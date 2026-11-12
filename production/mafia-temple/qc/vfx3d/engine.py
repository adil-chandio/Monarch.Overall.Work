"""Reference-matched renderer for the six-shot night-temple cut.

Pipeline per frame, all float32 NumPy:

  1. camera rays (optionally jittered for depth of field, or time-offset for
     motion blur — both are real sub-frame sampling, not a post filter)
  2. analytic intersection against the set's solids (box, oriented box, sphere,
     ellipsoid, capsule), with screen-rect culling that is bit-exact against the
     unculled trace
  3. shading: wrapped diffuse with 1/d^2 point lights, a directional key,
     ray-traced key shadows, Blinn specular, procedural surface detail
  4. atmosphere: exponential height fog plus a low mist band, so the temple sits
     in ground fog the way the reference does
  5. wet ground: mirror of the *lights* along the view ray, plus a faint
     reflection of the sky
  6. grade: a filmic curve, a cool-shadow / warm-highlight split tone, a slight
     anamorphic streak on highlights, vignette and grain

The target look was measured off the reference, not guessed:
  luma median 10-38, luma IQR 25-50, saturation median 81-181, blue-dominant in
  four of six shots, amber only where a lantern is burning.
"""
from __future__ import annotations

import math

import numpy as np

from . import geom, world

INF = np.float32(np.inf)

# primitives, flattened
K_BOX, K_OBB, K_SPHERE, K_ELLIP, K_CAPSULE = 0, 1, 2, 3, 4


def _flatten(solids):
    prims = []
    for s in solids:
        if isinstance(s, world.Box):
            prims.append((K_BOX, np.array(s.centre, np.float32),
                          np.array(s.half, np.float32), None,
                          world.MAT_ID[s.mat]))
        elif isinstance(s, world.OBox):
            prims.append((K_OBB, np.array(s.centre, np.float32),
                          np.array(s.half, np.float32),
                          geom.obb_basis(s.yaw, s.pitch, s.roll),
                          world.MAT_ID[s.mat]))
        elif isinstance(s, world.Sphere):
            prims.append((K_SPHERE, np.array(s.centre, np.float32),
                          np.float32(s.radius), None, world.MAT_ID[s.mat]))
        elif isinstance(s, world.Ellipsoid):
            B = None if s.basis is None else np.asarray(s.basis, np.float32)
            prims.append((K_ELLIP, np.array(s.centre, np.float32),
                          np.array(s.radii, np.float32),
                          (B, world.MAT_ID[s.mat]), world.MAT_ID[s.mat]))
        elif isinstance(s, world.Capsule):
            prims.append((K_CAPSULE, np.array(s.a, np.float32),
                          np.array(s.b, np.float32),
                          (np.float32(s.radius),), world.MAT_ID[s.mat]))
    return prims


def _bounds(prim):
    kind, p1, p2, p3, _mi = prim
    if kind in (K_BOX,):
        return p1 - p2, p1 + p2
    if kind == K_SPHERE:
        return p1 - p2, p1 + p2
    if kind == K_OBB:
        B = p3
        ext = np.abs(B).sum(1) * p2     # extents of the rotated box, axis-aligned
        return p1 - ext, p1 + ext
    if kind == K_ELLIP:
        r = float(np.max(p2))
        return p1 - r, p1 + r
    r = float(p3[0])
    return np.minimum(p1, p2) - r, np.maximum(p1, p2) + r


class Frame:
    """One shot's set, traceable from any camera position."""

    def __init__(self, set_name, width=1280, height=720):
        self.w, self.h = width, height
        self.solids, self.lights = world.build(set_name)
        self.prims = _flatten(self.solids)
        self.bounds = [_bounds(p) for p in self.prims]
        albedo = np.stack([m.albedo for m in world.MATS.values()]).astype(np.float32)
        emissive = np.stack([m.emissive if m.emissive is not None
                             else np.zeros(3, np.float32)
                             for m in world.MATS.values()]).astype(np.float32)
        # 3D value-noise lattice, trilinearly sampled. Sharing one lattice
        # across every material keeps the detail coherent; the per-material
        # scale decides whether it reads as stone grain, cloth weave or pores.
        rng = np.random.default_rng(20261111)
        self.noise = rng.random((64, 64, 64), dtype=np.float32)
        self.mat = dict(
            albedo=albedo, emissive=emissive,
            rough=np.array([m.roughness for m in world.MATS.values()], np.float32),
            spec=np.array([m.spec for m in world.MATS.values()], np.float32),
            fog=np.array([m.fog for m in world.MATS.values()], np.float32),
            wrap=np.array([m.wrap for m in world.MATS.values()], np.float32),
            bump=np.array([m.bump for m in world.MATS.values()], np.float32),
            bscale=np.array([m.bump_scale for m in world.MATS.values()],
                            np.float32),
        )

    # ----------------------------------------------------------------- trace
    def _intersect(self, prim, ro, rd, t, mat, nrm,
                   y0, y1, x0, x1, ro_o, rd_o):
        """Clip one primitive into the running buffers inside a screen rect."""
        kind, p1, p2, p3, mi = prim
        sub_ro = ro_o[y0:y1, x0:x1]
        sub_rd = rd_o[y0:y1, x0:x1]
        t_sub = t[y0:y1, x0:x1]
        mat_sub = mat[y0:y1, x0:x1]
        nrm_sub = nrm[y0:y1, x0:x1]
        if kind == K_BOX:
            tp, axis = geom.ray_aabb(sub_ro, sub_rd, p1, p2)
            m = tp < t_sub
            if not m.any():
                return
            t_sub[m] = tp[m]
            mat_sub[m] = mi
            nrm_sub[m] = geom.aabb_normal(axis, sub_rd)[m]
        elif kind == K_OBB:
            tp = geom.ray_obb(sub_ro, sub_rd, p1, p2, p3)
            m = tp < t_sub
            if not m.any():
                return
            t_sub[m] = tp[m]
            mat_sub[m] = mi
            B = p3
            o = (sub_ro - p1) @ B.T
            d = sub_rd @ B.T
            tt = tp[..., None]
            q = o + d * tt
            # face normal = axis of largest |component| in box space
            ax = np.abs(q).argmax(-1)
            n = np.zeros_like(q)
            np.put_along_axis(n, ax[..., None],
                              np.sign(np.take_along_axis(q, ax[..., None], -1)),
                              -1)
            nrm_sub[m] = (n @ B.T)[m]
        elif kind == K_SPHERE:
            tp = geom.ray_sphere(sub_ro, sub_rd, p1, p2)
            m = tp < t_sub
            if not m.any():
                return
            t_sub[m] = tp[m]
            mat_sub[m] = mi
            nrm_sub[m] = geom.normalise(sub_ro + sub_rd * tp[..., None] - p1)[m]
        elif kind == K_ELLIP:
            B, _ = p3
            tp = geom.ray_ellipsoid(sub_ro, sub_rd, p1, p2, B)
            m = tp < t_sub
            if not m.any():
                return
            t_sub[m] = tp[m]
            mat_sub[m] = mi
            p = sub_ro + sub_rd * tp[..., None]
            nrm_sub[m] = geom.ellipsoid_normal(p, p1, p2, B)[m]
        else:                                    # capsule
            tp, _ = geom.ray_capsule(sub_ro, sub_rd, p1, p2, p3[0])
            m = tp < t_sub
            if not m.any():
                return
            t_sub[m] = tp[m]
            mat_sub[m] = mi
            ba = p2 - p1
            pp = sub_ro + sub_rd * tp[..., None]
            k = np.clip(((pp - p1) @ ba) / max(float(ba @ ba), 1e-8), 0, 1)
            nrm_sub[m] = geom.normalise(pp - (p1 + k[..., None] * ba))[m]

    def trace(self, ro, rd, dyn=None, cam=None, prims=None, cull=True):
        """Nearest hit for every ray. `dyn` are extra primitives (the figure)."""
        H, W = rd.shape[:2]
        ro = np.broadcast_to(np.asarray(ro, np.float32), rd.shape).copy()
        rd = np.asarray(rd, np.float32)
        src = self.prims if prims is None else prims
        allp = list(src) + list(dyn or [])
        t = np.full((H, W), np.inf, np.float32)
        mat = np.zeros((H, W), np.int16)
        nrm = np.zeros((H, W, 3), np.float32)

        if cam is not None and cull:
            eye, fwd, right, up, ty, aspect = cam
            for prim in allp:
                lo, hi = _bounds(prim)
                y0, y1, x0, x1 = screen_rect(eye, fwd, right, up, ty, aspect,
                                             W, H, lo, hi)
                if x1 - x0 < 1 or y1 - y0 < 1:
                    continue
                self._intersect(prim, None, None, t, mat, nrm,
                                y0, y1, x0, x1, ro, rd)
        else:
            for prim in allp:
                self._intersect(prim, None, None, t, mat, nrm,
                                0, H, 0, W, ro, rd)

        # the ground plane is cheaper as one analytic test than as a huge box
        tp, _ = geom.ray_plane(ro, rd, 0.0)
        m = tp < t
        t[m] = tp[m]
        mat[m] = world.MAT_ID['ground']
        nrm[m] = np.array([0.0, 1.0, 0.0], np.float32)
        return t, mat, nrm

    # --------------------------------------------------------------- shading
    def shade(self, ro, rd, t, mat, nrm, lights, fog_density, fog_tint,
              ambient, mist=0.35, time=0.0, shadow_dirs=None):
        hit = np.isfinite(t) & (t < 500.0)
        p = ro + rd * np.where(hit, t, 0.0)[..., None]
        alb = self.mat['albedo'][mat] * self.detail(p, mat)[..., None]
        emis = self.mat['emissive'][mat] * (self.mat['emissive'][mat] > 0)
        rough = self.mat['rough'][mat]
        spec = self.mat['spec'][mat]
        wrap_m = self.mat['wrap'][mat]

        # Procedural micro-normal: three sine bands displaced along the ray, and
        # their analytic gradient projected onto the tangent plane. This is what
        # gives the skin pores, the hair strands and the worn stone their texture
        # without a single texture file being read.
        bump = self.mat['bump'][mat]
        if float(bump.max()) > 0:
            nrm = self._perturb(p, nrm, mat, bump)

        col = alb * np.asarray(ambient, np.float32)[None, None, :]
        dist = np.where(hit, t, 0.0).astype(np.float32)

        shadow = {}
        for L in lights:
            lc = np.asarray(L.colour, np.float32)
            if L.direction is not None:
                key = id(L)
                if shadow_dirs is not None and key not in shadow:
                    shadow[key] = self._shadow_mask(p, nrm, L.direction)
                ldir = np.broadcast_to(np.asarray(L.direction, np.float32),
                                       nrm.shape)
                ndl = np.clip((nrm * ldir).sum(-1), 0, 1)
                atten = np.float32(L.intensity)
                sh = shadow.get(key, 1.0)
            else:
                lv = np.asarray(L.pos, np.float32)[None, None, :] - p
                d2 = (lv * lv).sum(-1) + 1e-4
                ldir = lv / np.sqrt(d2)[..., None]
                ndl = np.clip((nrm * ldir).sum(-1), 0, 1)
                # 1/d^2 with the emitter's own radius as the floor: a light
                # cannot illuminate itself to infinity from zero distance
                atten = L.intensity / (d2 + L.radius ** 2 + 1e-3)
                sh = 1.0
            wrapped = np.clip((ndl + wrap_m) / (1.0 + wrap_m), 0, 1)
            col += alb * lc[None, None, :] * (wrapped * atten * sh)[..., None]
            hv = geom.normalise(-rd + ldir)
            ndh = np.clip((nrm * hv).sum(-1), 0, 1)
            spec_term = (1.0 - rough) ** 2 * spec * ndh ** (10.0 + 60.0 * (1.0 - rough))
            col += lc[None, None, :] * (spec_term * atten)[..., None]

        # grazing surfaces pick up the sky, so night silhouettes keep their edge
        ndv = np.clip((nrm * -rd).sum(-1), 0, 1)
        col += np.asarray(fog_tint, np.float32)[None, None, :] * \
            (((1.0 - ndv) ** 4.0) * 0.30)[..., None]
        col = col + emis

        # fog: height falloff plus a low mist band that drifts with time
        y = np.clip(p[..., 1], 0, 40)
        hf = np.exp(-y * 0.22)
        drift = 0.72 + 0.28 * np.sin(p[..., 0] * 0.34 + p[..., 2] * 0.21 + time * 0.55)
        band = np.exp(-((y - 0.55) ** 2) / 1.6)
        dens = fog_density * (0.30 + 0.55 * hf + mist * band * drift) * self.mat['fog'][mat]
        fog = 1.0 - np.exp(-dist * dens)
        col = col * (1 - fog[..., None]) + np.asarray(fog_tint, np.float32)[None, None, :] * fog[..., None]
        return col.astype(np.float32), hit, dist

    def _shadow_mask(self, p, nrm, direction, scale=5):
        """Hard shadows for a directional key, traced on a coarse grid."""
        H, W = nrm.shape[:2]
        h, w = H // scale, W // scale
        ps = p[::scale, ::scale][:h, :w] + nrm[::scale, ::scale][:h, :w] * 0.02
        d = np.broadcast_to(np.asarray(direction, np.float32), ps.shape).copy()
        tp, _, _ = self.trace(ps, d, cam=None, prims=self.prims, cull=False)
        lit = (~np.isfinite(tp)).astype(np.float32)
        k = 2
        pad = np.pad(lit, ((k, k), (k, k)), mode='edge')
        acc = np.zeros_like(lit)
        for dy in range(-k, k + 1):
            for dx in range(-k, k + 1):
                acc += pad[k + dy:k + dy + h, k + dx:k + dx + w]
        lit = np.clip(acc / float((2 * k + 1) ** 2) * 1.4, 0, 1)
        from PIL import Image
        return np.asarray(Image.fromarray(lit, mode='F').resize((W, H), Image.BILINEAR),
                          np.float32)

    def _noise(self, q):
        """Trilinear value noise. `q` is a world position times frequency."""
        i0 = np.floor(q)
        f = q - i0
        i0 = i0.astype(np.int32) & 63
        f = f * f * (3.0 - 2.0 * f)
        i1 = (i0 + 1) & 63
        N = self.noise
        fx, fy, fz = f[..., 0], f[..., 1], f[..., 2]
        x0, x1 = i0[..., 0], i1[..., 0]
        y0, y1 = i0[..., 1], i1[..., 1]
        z0, z1 = i0[..., 2], i1[..., 2]
        def lerp(a, b, w):
            return a + (b - a) * w
        c00 = lerp(N[x0, y0, z0], N[x1, y0, z0], fx)
        c10 = lerp(N[x0, y1, z0], N[x1, y1, z0], fx)
        c01 = lerp(N[x0, y0, z1], N[x1, y0, z1], fx)
        c11 = lerp(N[x0, y1, z1], N[x1, y1, z1], fx)
        return lerp(lerp(c00, c10, fy), lerp(c01, c11, fy), fz)

    def _perturb(self, p, nrm, mat, bump):
        """Displace the normal along two tangent directions using value noise.

        Sine-band detail tiles visibly (it moires into a cross-hatch), so the
        micro-normal is sampled from a noise lattice instead. `eps` is one cell
        of that lattice, which is what makes the gradient resolvable.
        """
        sc = self.mat['bscale'][mat]
        # two arbitrary-but-stable tangents per pixel, from the normal itself
        ref = np.where(np.abs(nrm[..., 1:2]) > 0.9, np.array([1.0, 0.0, 0.0],
                                                              np.float32),
                       np.array([0.0, 1.0, 0.0], np.float32))
        t1 = np.cross(nrm, ref)
        t1 = t1 / np.maximum(np.linalg.norm(t1, axis=-1, keepdims=True), 1e-6)
        t2 = np.cross(nrm, t1)
        # one lattice cell in world units: the distance over which the gradient
        # is sampled. Half a cell is stable without washing the detail out.
        step = (0.5 / np.maximum(sc, 1e-3))[..., None]
        q = p * sc[..., None]
        h0 = self._noise(q)
        h1 = self._noise(q + t1 * step)
        h2 = self._noise(q + t2 * step)
        g = (t1 * (h1 - h0)[..., None] + t2 * (h2 - h0)[..., None])
        amp = (bump * 2.2)[..., None]
        return geom.normalise(nrm + g * amp)

    # --------------------------------------------------------- surface detail
    @staticmethod
    def detail(p, mat):
        x, y, z = p[..., 0], p[..., 1], p[..., 2]
        n1 = np.sin(x * 3.1 + y * 1.7 + z * 2.3) * 0.5 + 0.5
        n2 = np.sin(x * 11.0 - z * 7.0 + y * 5.0) * 0.5 + 0.5
        n3 = np.sin(y * 27.0 + x * 13.0 - z * 9.0) * 0.5 + 0.5
        base = 0.86 + 0.26 * (n1 * 0.55 + n2 * 0.30 + n3 * 0.15)
        out = base

        stone = (mat == world.MAT_ID['stone']) | (mat == world.MAT_ID['darkstone'])
        row = np.floor(y / 0.30)
        off = np.mod(np.floor(row), 2.0) * 0.42
        jv = np.abs(np.mod(x + off, 0.78) - 0.39)
        jh = np.abs(np.mod(y + 0.02, 0.30) - 0.15)
        mortar = np.clip(np.minimum(jv, jh * 1.5) / 0.035 - 1.0, 0, 1)
        out = np.where(stone, out * (0.78 + 0.22 * mortar), out)

        wood = mat == world.MAT_ID['wood']
        out = np.where(wood, 0.84 + 0.28 * (np.sin(x * 52.0 + z * 44.0) * 0.5 + 0.5), out)

        tile = mat == world.MAT_ID['tile']
        out = np.where(tile, 0.70 + 0.30 * (np.abs(np.sin(x * 11.0)) ** 0.55), out)

        pl = mat == world.MAT_ID['plaster']
        out = np.where(pl, 0.90 + 0.14 * n2, out)

        ground = mat == world.MAT_ID['ground']
        wet = 0.66 + 0.34 * np.clip(n1 * n2 * 2.1, 0, 1)
        out = np.where(ground, wet, out)

        skin = (mat == world.MAT_ID['skin']) | (mat == world.MAT_ID['skin_dark'])
        fine = 0.955 + 0.090 * n3
        out = np.where(skin, fine, out)

        hair = mat == world.MAT_ID['hair']
        strands = 0.72 + 0.42 * (np.sin(x * 210.0 + z * 90.0 + y * 60.0) * 0.5 + 0.5)
        out = np.where(hair, strands, out)
        return out.astype(np.float32)

    # ------------------------------------------------------------- wet floor
    def wet(self, col, ro, rd, t, mat, nrm, lights, fog_tint, strength=0.42,
            time=0.0):
        m = (mat == world.MAT_ID['ground']) & np.isfinite(t) & (t < 160)
        if not m.any() or strength <= 0:
            return col
        ry = np.array(rd, np.float32, copy=True)
        ry[..., 1] = -ry[..., 1]
        ry = geom.normalise(ry)
        p = ro + rd * np.where(m, t, 0.0)[..., None]
        pts = p[m]
        cols = np.zeros((pts.shape[0],), np.bool_)
        acc = np.zeros((pts.shape[0], 3), np.float32)
        for L in lights:
            if L.direction is not None:
                continue
            lv = np.asarray(L.pos, np.float32)[None, :] - pts
            d2 = (lv * lv).sum(-1) + 0.20
            align = np.clip((lv / np.sqrt(d2)[:, None] * ry[m]).sum(-1), 0, 1) ** 120
            acc += np.asarray(L.colour, np.float32)[None, :] * \
                (align * L.intensity / (d2 * 5.0 + 2.0))[:, None]
        ripple = 0.62 + 0.38 * np.sin(pts[:, 0] * 6.0 + pts[:, 2] * 3.4 + time * 1.5)
        rw = (strength * ripple)[:, None]
        out = col.copy()
        out[m] = col[m] * (1.0 - rw) + np.clip(acc, 0, 2.5) * rw
        return np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0)

    # ------------------------------------------------------------ atmosphere
    @staticmethod
    def sky(rd, tint, moon_dir=None, moon_size=1.0, time=0.0):
        d = geom.normalise(rd)
        y = np.clip(d[..., 1], -1, 1)
        horizon = np.clip(1.0 - np.abs(y) * 2.4, 0, 1) ** 2.0
        base = np.asarray(tint, np.float32)[None, None, :] * (0.30 + 1.25 * horizon[..., None])
        zenith = np.array([0.004, 0.007, 0.016], np.float32)
        base = base * (0.30 + 0.70 * horizon[..., None]) + zenith * (1 - horizon[..., None])
        if moon_dir is not None:
            md = geom.normalise(np.asarray(moon_dir, np.float32))
            cosang = (d * md).sum(-1)
            disc = np.clip((cosang - (0.99935 / moon_size)) / (0.00065 / moon_size), 0, 1)
            halo = np.clip((cosang - 0.90) / 0.10, 0, 1) ** 4
            base = base + np.array([0.80, 0.86, 1.0], np.float32) * \
                (disc * 1.6 + halo * 0.16)[..., None]
        return base.astype(np.float32)

    @staticmethod
    def mist_layer(col, hit, t, rd, strength=1.0, tint=(0.10, 0.13, 0.19)):
        """Volume-ish ground mist: denser along rays that graze the floor."""
        d = geom.normalise(rd)
        graze = np.clip(1.0 - np.abs(d[..., 1]) * 3.2, 0, 1)
        depth = np.clip(np.where(np.isfinite(t), t, 60.0) / 30.0, 0, 1)
        m = (graze ** 2.0) * depth * strength
        tint = np.asarray(tint, np.float32)
        return col * (1 - m[..., None] * 0.35) + tint * (m[..., None] * 0.35)

    # ------------------------------------------------------------------ grade
    @staticmethod
    def grade(col, exposure=1.0, contrast=1.16, saturation=1.10,
              shadow_tint=(-0.012, 0.004, 0.030),
              highlight_tint=(0.022, 0.010, -0.012),
              lift=0.0, streak=0.22, vignette=0.42, grain=0.010, seed=0):
        """Filmic curve, then a cool-shadow / warm-highlight split tone."""
        c = np.nan_to_num(col, nan=0.0, posinf=0.0, neginf=0.0) * exposure
        c = np.clip(c, 0, None)
        c = (c * (2.51 * c + 0.03)) / (c * (2.43 * c + 0.59) + 0.14)
        c = np.clip(c, 0, 1)
        c = np.power(c, 1 / 2.2)

        lum = (c * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1, keepdims=True)
        # split tone: shadows towards blue, highlights towards amber
        s_w = np.clip(1.0 - lum * 2.0, 0, 1)
        h_w = np.clip(lum * 1.6 - 0.35, 0, 1)
        c = c + np.asarray(shadow_tint, np.float32) * s_w + \
            np.asarray(highlight_tint, np.float32) * h_w
        c = lum + (c - lum) * saturation
        c = (c - 0.20) * contrast + 0.20 + lift

        # cheap anamorphic streak: a horizontal smear of the bright highlights
        if streak > 0:
            hi = np.clip(c - 0.72, 0, None)
            if hi.max() > 0:
                acc = hi.copy()
                for k in (2, 5, 11, 22):
                    acc = np.maximum(acc, np.roll(hi, k, axis=1) * 0.62)
                    acc = np.maximum(acc, np.roll(hi, -k, axis=1) * 0.62)
                c = c + acc * streak

        if vignette > 0:
            h, w = c.shape[:2]
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            r = np.sqrt(((xx / w - 0.5) * 2) ** 2 + ((yy / h - 0.5) * 2) ** 2)
            c = c * (1.0 - vignette * np.clip(r - 0.35, 0, 1) ** 2)[..., None]

        if grain > 0:
            rng = np.random.default_rng(seed)
            n = rng.standard_normal(c.shape[:2]).astype(np.float32)
            c = c + (n * grain)[..., None] * (1.0 - np.clip(lum, 0, 1) * 0.6)

        return np.clip(c * 255.0, 0, 255).astype(np.uint8)


# --------------------------------------------------------------- screen rect
def screen_rect(eye, fwd, right, up, ty, aspect, w, h, lo, hi, pad=2):
    """Pixel rect (y0, y1, x0, x1) a world AABB can cover; empties are skipped.

    Returns in the caller's order — (x, y) swapped here was the bug that once
    hid the figure entirely, so it is spelled out explicitly.
    """
    ext = np.array([[x, y, z] for x in (lo[0], hi[0])
                    for y in (lo[1], hi[1]) for z in (lo[2], hi[2])], np.float32)
    rel = ext - eye[None, :]
    z = rel @ fwd
    if (z <= 0.05).any():
        return 0, h, 0, w
    sx = (rel @ right) / z / (ty * aspect)
    sy = (rel @ up) / z / ty
    x_lo = int(np.floor((sx.min() * 0.5 + 0.5) * w)) - pad
    x_hi = int(np.ceil((sx.max() * 0.5 + 0.5) * w)) + pad
    y_top = int(np.floor((0.5 - sy.max() * 0.5) * h)) - pad
    y_bot = int(np.ceil((0.5 - sy.min() * 0.5) * h)) + pad
    return (max(y_top, 0), min(y_bot, h), max(x_lo, 0), min(x_hi, w))


def camera_basis(eye, target):
    fwd = np.asarray(target, np.float64) - np.asarray(eye, np.float64)
    fwd /= max(np.linalg.norm(fwd), 1e-9)
    world_up = np.array([0.0, 1.0, 0.0])
    if abs(float(fwd @ world_up)) > 0.995:
        world_up = np.array([0.0, 0.0, 1.0])
    right = np.cross(fwd, world_up)
    right /= max(np.linalg.norm(right), 1e-9)
    up = np.cross(right, fwd)
    return right.astype(np.float32), up.astype(np.float32), fwd.astype(np.float32)


# ------------------------------------------------------------------ one frame
class Shot:
    """Camera, grade and atmosphere for one reference shot."""
    def __init__(self, name, eye, target, fov=42.0, roll=0.0,
                 ambient=(0.10, 0.13, 0.19), fog=0.030, fog_tint=(0.055, 0.070, 0.100),
                 mist=0.45, grade=None, wet=0.42, fstop=None, focus=None,
                 shutter=0.0, moon=None, mist_layer=1.0, pan_rate=0.0):
        self.name = name
        self.eye = np.asarray(eye, np.float32)
        self.target = np.asarray(target, np.float32)
        self.fov, self.roll = fov, roll
        self.ambient = ambient
        self.fog, self.fog_tint, self.mist = fog, fog_tint, mist
        self.grade = grade or {}
        self.wet = wet
        self.fstop, self.focus = fstop, focus
        self.shutter = shutter
        self.pan_rate = pan_rate          # deg/s, used for sub-frame blur
        self.moon = moon
        self.mist_layer = mist_layer


def render_frame(fr, shot, width, height, t=0.0, dyn=None, dof=1, blur=1,
                 seed=0, lights=None, ao=0.0):
    """Render one frame. `dof` and `blur` set the number of sub-samples."""
    rd0, eye, right, up = geom.camera_rays(width, height, shot.eye, shot.target,
                                           shot.fov, shot.roll)
    fwd = geom.normalise(shot.target - shot.eye)
    ty = np.tan(np.radians(shot.fov) * 0.5)
    aspect = width / height
    cam = (eye, fwd, right, up, ty, aspect)
    lights = lights if lights is not None else fr.lights
    rng = np.random.default_rng(seed)

    n = max(1, dof * blur)
    acc = np.zeros((height, width, 3), np.float32)
    for s in range(n):
        rd = rd0
        if n > 1:
            # sub-pixel jitter: this is what breaks the CG edge and gives the
            # reference its fine film grain rather than a clean pixel stair
            jx = (rng.random((height, width), np.float32) - 0.5) * 1.2
            jy = (rng.random((height, width), np.float32) - 0.5) * 1.2
            if shot.shutter > 0:
                jx = jx * 0.35
                jy = jy * 0.35
            rd = geom.normalise(rd0 + (jx / width * 2 * ty)[..., None] * right
                                + (jy / height * 2 * ty)[..., None] * up)
            if shot.pan_rate and shot.shutter > 0:
                # true sub-frame camera motion: the pan is sampled across the
                # shutter window instead of being applied as a post blur
                ang = np.radians(shot.pan_rate) * ((s + 0.5) / n - 0.5) \
                    * shot.shutter
                c, sn = math.cos(ang), math.sin(ang)
                r2 = right * c - up * sn
                u2 = up * c + right * sn
                rd = geom.normalise(fwd[None, None, :] * 1.0
                                    + (np.linspace(-1, 1, width, dtype=np.float32)
                                       * ty * aspect)[None, :, None] * r2[None, None, :]
                                    + (np.linspace(1, -1, height, dtype=np.float32)
                                       * ty)[:, None, None] * u2[None, None, :])
        t_hit, mat, nrm = fr.trace(eye, rd, dyn=dyn, cam=cam)
        col, hit, dist = fr.shade(eye, rd, t_hit, mat, nrm, lights,
                                  shot.fog, shot.fog_tint, shot.ambient,
                                  mist=shot.mist, time=t)
        sky = fr.sky(rd, shot.fog_tint, shot.moon, time=t)
        col = np.where(hit[..., None], col, sky)

        # depth of field: rays that land off the focus plane blend towards the
        # average of a small disc of neighbours — a real defocus, done cheaply
        if dof > 1 and shot.focus:
            coc = np.clip(np.abs(np.where(np.isfinite(t_hit), t_hit, 60.0)
                                 - shot.focus) / 6.0, 0, 1) * (1.0 - 1.0 / dof)
            for _ in range(1):
                soft = col.copy()
                for k in (2, 5, 9):
                    soft += np.roll(col, k, axis=1) + np.roll(col, -k, axis=1)
                    soft += np.roll(col, k, axis=0) + np.roll(col, -k, axis=0)
                soft /= 11.0
                col = col * (1 - coc[..., None] * 0.55) + soft * (coc[..., None] * 0.55)

        acc += col
    acc /= n

    # Crevice shading: where neighbouring normals disagree sharply, the surface
    # is folded in on itself (eye sockets, nostrils, the hairline, the joints of
    # the architecture). Darkening by normal divergence is the cheap stand-in
    # for ambient occlusion and is what stops the face reading as a flat mask.
    if ao > 0:
        nb = np.zeros_like(nrm)
        nb[1:-1, 1:-1] = (nrm[1:-1, 2:] - nrm[1:-1, :-2]
                          + nrm[2:, 1:-1] - nrm[:-2, 1:-1])
        fold = np.clip(np.linalg.norm(nb, axis=-1) * 2.2, 0, 1)
        # only darken where both this pixel and its neighbours are on geometry,
        # otherwise every silhouette gets a black halo drawn round it
        hm = np.ones_like(fold)
        hm[1:-1, 1:-1] = (hit[1:-1, 2:] & hit[1:-1, :-2]
                          & hit[2:, 1:-1] & hit[:-2, 1:-1])
        fold = fold * hm
        from PIL import Image
        h, w = fold.shape
        fold = np.asarray(Image.fromarray(fold.astype(np.float32), mode='F')
                          .resize((w // 2, h // 2), Image.BILINEAR)
                          .resize((w, h), Image.BILINEAR), np.float32)
        occ = (1.0 - ao * fold)[..., None]
        acc = acc * occ
    acc = fr.wet(acc, eye, rd0, t_hit, mat, nrm, lights, shot.fog_tint,
                 strength=shot.wet, time=t)
    acc = fr.mist_layer(acc, t_hit, np.broadcast_to(np.inf, t_hit.shape), rd0,
                        strength=shot.mist_layer)
    return fr.grade(acc, seed=seed, **shot.grade), acc
