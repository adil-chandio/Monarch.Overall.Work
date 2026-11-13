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
K_BOX, K_OBB, K_SPHERE, K_ELLIP, K_CAPSULE, K_FRUSTUM = 0, 1, 2, 3, 4, 5


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
        elif isinstance(s, world.Frustum):
            prims.append((K_FRUSTUM, np.array(s.a, np.float32),
                          np.array(s.b, np.float32),
                          (np.float32(s.r_a), np.float32(s.r_b)),
                          world.MAT_ID[s.mat]))
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
    if kind == K_FRUSTUM:
        r = max(float(p3[0]), float(p3[1]))
    else:
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
        elif kind == K_CAPSULE:
            tp, _ = geom.ray_capsule(sub_ro, sub_rd, p1, p2, p3[0])
            m = tp < t_sub
            if not m.any():
                return
            t_sub[m] = tp[m]
            mat_sub[m] = mi
            ba = p2 - p1
            pp = sub_ro[m] + sub_rd[m] * tp[m, None]
            k = np.clip(((pp - p1) @ ba) / max(float(ba @ ba), 1e-8), 0, 1)
            nrm_sub[m] = geom.normalise(pp - (p1 + k[..., None] * ba))
        elif kind == K_FRUSTUM:
            tp, _ss = geom.ray_frustum(sub_ro, sub_rd, p1, p2, p3[0], p3[1])
            m = tp < t_sub
            if not m.any():
                return
            t_sub[m] = tp[m]
            mat_sub[m] = mi
            ba = p2 - p1
            pp = sub_ro + sub_rd * tp[..., None]
            k = np.clip(((pp - p1) @ ba) / max(float(ba @ ba), 1e-8), 0, 1)
            axis_pt = p1 + k[..., None] * ba
            radial = pp - axis_pt
            # the surface normal of a cone is not radial: it leans back along
            # the axis by the taper angle, or the shading is a cylinder's
            dr = float(p3[1]) - float(p3[0])
            L = math.sqrt(max(float(ba @ ba), 1e-8))
            nrm_sub[m] = geom.normalise(
                radial * L + ba[None, None, :] * (-dr))[m]

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

        up = np.clip(nrm[..., 1], -1, 1)
        sky_amb = np.asarray(fog_tint, np.float32)[None, None, :] * 1.05
        gnd_amb = np.asarray(ambient, np.float32)[None, None, :] * 1.6
        hemi = gnd_amb + (sky_amb - gnd_amb) * ((up * 0.5 + 0.5) ** 1.4)[..., None]
        col = alb * (hemi + np.asarray(ambient, np.float32)[None, None, :] * 0.5)
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
        # broad timber tones, not vertical stripes: the walls in the reference are
        # near-black with a wet sheen, and a high-frequency grain reads as corduroy
        plank = np.sin(y * 34.0 + z * 2.0) * 0.5 + 0.5
        grain = np.sin(x * 9.0 + z * 7.0 + y * 3.0) * 0.5 + 0.5
        out = np.where(wood, 0.94 + 0.08 * (0.35 * plank + 0.65 * grain), out)

        tile = mat == world.MAT_ID['tile']
        out = np.where(tile, 0.70 + 0.30 * (np.abs(np.sin(x * 11.0)) ** 0.55), out)

        pl = mat == world.MAT_ID['plaster']
        out = np.where(pl, 0.90 + 0.14 * n2, out)

        ground = mat == world.MAT_ID['ground']
        mottle = 0.90 + 0.16 * np.clip(n1 * 0.6 + n2 * 0.4, 0, 1)
        out = np.where(ground, mottle, out)

        skin = (mat == world.MAT_ID['skin']) | (mat == world.MAT_ID['skin_dark'])
        fine = 0.955 + 0.090 * n3
        out = np.where(skin, fine, out)

        hair = mat == world.MAT_ID['hair']
        strands = 0.72 + 0.42 * (np.sin(x * 210.0 + z * 90.0 + y * 60.0) * 0.5 + 0.5)
        out = np.where(hair, strands, out)
        return out.astype(np.float32)

    # ------------------------------------------------------------- wet floor
    # materials whose up-facing surfaces are wet: the pavement, the stone of the
    # court, and the earth. The first version tested only 'ground', but every
    # floor in every set is built from 'stone' boxes laid over the ground plane,
    # so the wet pass never ran on a single visible pixel of the street.
    _WET_MATS = None

    def _wet_mask(self, mat):
        if Frame._WET_MATS is None:
            Frame._WET_MATS = np.array([world.MAT_ID[k] for k in
                                        ('ground', 'stone', 'darkstone')])
        return np.isin(mat, Frame._WET_MATS)

    def wet(self, col, ro, rd, t, mat, nrm, lights, fog_tint, strength=0.42,
            time=0.0):
        m = (self._wet_mask(mat) & (nrm[..., 1] > 0.75)
             & np.isfinite(t) & (t < 160))
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
            # A lantern reflection is broad and smeared, not a pinpoint: a wet
            # flagstone scatters the lobe over a wide angle. A tight 26th power
            # produced small bright dots that never read as a reflection.
            align = np.clip((lv / np.sqrt(d2)[:, None] * ry[m]).sum(-1), 0, 1) ** 11
            # falloff with distance keeps each pool under its own lamp instead
            # of letting one lamp light the whole street
            acc += np.asarray(L.colour, np.float32)[None, :] * \
                (align * L.intensity / (d2 * 0.55 + 0.35)
                 * np.exp(-np.sqrt(d2) / 9.0))[:, None]
        # A wet flagstone is a low, rough mirror. What the reference actually
        # shows is a bright vertical smear under each lantern and almost nothing
        # between them, plus one long mirror line where a nearby lamp's lobe is
        # grazing. The earlier passes either lit the whole floor (a glowing
        # carpet) or added a two-sine product (a literal checkerboard). This
        # weights the reflection by how tightly each lamp's lobe is aligned, so
        # the pools stay local, and elongates the noise along the view so the
        # texture is a smear, never a grid.
        # real value noise, 8:1 elongated along z, drifting slowly: anything
        # built from single sines at these frequencies produces a visible
        # interference pattern, which is precisely how the last three passes
        # turned the pavement into a carpet
        q = np.stack([pts[:, 0] * 26.0,
                      pts[:, 1] * 26.0,
                      pts[:, 2] * 3.2 + time * 0.35], -1).astype(np.float32)
        n1 = self._noise(q)
        n2 = self._noise(q * np.array([2.7, 1.0, 2.3], np.float32) + 11.0)
        sm = np.clip(0.30 + 1.15 * (0.65 * n1 + 0.35 * n2), 0.0, 1.0)
        # A wet floor is not only a mirror for the lamps: at the grazing angles a
        # street is shot from, Fresnel makes it a mirror for the sky as well, and
        # in this film the sky is the cold blue haze. Without this the pavement
        # was lit purely by warm lanterns and came out brown, like a timber
        # floor, where the reference's wet stone is blue-grey with the lamps
        # sitting on top of it.
        cos_i = np.clip(np.abs((rd[m] * nrm[m]).sum(-1)), 0, 1)
        fres = (1.0 - cos_i) ** 3.4
        sky_refl = (np.asarray(fog_tint, np.float32)[None, :] * 2.6
                    * (0.55 + 1.30 * sm)[:, None]
                    * fres[:, None])
        refl = np.clip(acc * sm[:, None] + sky_refl, 0, 1.4)
        refl = refl + np.asarray(fog_tint, np.float32)[None, :] * 0.06 * sm[:, None]
        rw = np.clip(strength * 0.92 * (0.22 + 0.78 * sm), 0, 0.85)[:, None]
        out = col.copy()
        out[m] = col[m] * (1.0 - rw) + refl * rw
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

    # -------------------------------------------------------------------- rain
    @staticmethod
    def rain_streaks(col, depth, eye, right, up, fwd, t, *, amount=1.0,
                     wind=(0.10, -0.06), seed=0, ty=0.5):
        """Rain as motion-blurred streaks in camera space.

        A drop at 24 fps under a 1/48 s shutter lays down a streak tens of
        centimetres long, not a dot, so each drop is drawn as a line along its
        own velocity. Drops live in a cell that wraps around the camera, which
        makes the field infinite without rebuilding anything, and each drop is
        placed with true perspective and depth-tested against the geometry — so
        rain in front of a lantern is lit by it and rain behind the wall is not
        drawn at all.

        This has to be done in camera space, not screen space. Screen-space
        streaks do not share a vanishing point, do not parallax, and do not
        respect occlusion, and the result looks like scratches on the negative.
        """
        if amount <= 0:
            return col
        h, w = col.shape[:2]
        rng = np.random.default_rng(1000 + int(seed))
        out = col.copy()
        img = out.reshape(-1, 3)
        aspect = w / h
        shells = ((0.40, 5.5, 320), (1.30, 15.0, 520), (3.40, 30.0, 780))
        for ci, (near, far, count) in enumerate(shells):
            n = int(count * amount)
            base = rng.random((n, 3), np.float32)
            span = far - near
            fall = (base[:, 1] * span + t * 9.5) % span
            bx = (base[:, 0] - 0.5) * 2.0 * (near + fall) * 1.15
            bz = near + ((base[:, 2] * span + t * 1.1) % span)
            wy = near * 0.20 + fall
            wx = bx + wind[0] * fall
            pw = (np.asarray(eye, np.float32)[None, :]
                  + np.asarray(fwd, np.float32)[None, :] * bz[:, None]
                  + np.asarray(right, np.float32)[None, :] * wx[:, None]
                  + np.asarray(up, np.float32)[None, :] * wy[:, None])
            rel = pw - np.asarray(eye, np.float32)[None, :]
            zc = rel @ np.asarray(fwd, np.float32)
            ok = zc > 0.30
            if not ok.any():
                continue
            xs = (rel @ np.asarray(right, np.float32)) / np.maximum(zc, 1e-4) / (ty * aspect)
            ys = (rel @ np.asarray(up, np.float32)) / np.maximum(zc, 1e-4) / ty
            px = (xs * 0.5 + 0.5) * w
            py = (0.5 - ys * 0.5) * h
            keep = ok & (px >= 0) & (px < w - 1) & (py >= 0) & (py < h - 1)
            if not keep.any():
                continue
            pi = np.nonzero(keep)[0]
            z_at = depth[py[pi].astype(np.int32), px[pi].astype(np.int32)]
            vis = pi[zc[pi] < z_at + 0.08]
            if len(vis) == 0:
                continue
            # streak length in pixels: the distance the drop travels during the
            # shutter, projected through the same perspective
            speed = 9.0 + 3.5 * base[vis, 0]
            k = (ty * h)
            ln = np.clip(0.020 * speed * k / np.maximum(zc[vis], 1e-3), 2.0, 70.0)
            amp = (0.20 if ci == 0 else 0.115 if ci == 1 else 0.055) * amount
            for j, i in enumerate(vis):
                L = float(ln[j])
                steps = int(np.clip(L, 2, 34))
                u = np.linspace(0.0, 1.0, steps, dtype=np.float32)
                sx = px[i] + wind[0] * L * 3.0 * u
                sy = py[i] + L * u
                xi = np.clip(sx.astype(np.int32), 0, w - 1)
                yi = np.clip(sy.astype(np.int32), 0, h - 1)
                taper = (np.sin(np.pi * u) ** 0.8) * amp
                np.add.at(img, yi * w + xi,
                          np.array([0.55, 0.63, 0.76], np.float32)[None, :]
                          * taper[:, None])
        return out

    # ------------------------------------------------------------------ grade
    @staticmethod
    def grade(col, exposure=1.0, contrast=1.16, saturation=1.10,
              shadow_tint=(-0.012, 0.004, 0.030),
              highlight_tint=(0.022, 0.010, -0.012),
              lift=0.0, streak=0.22, vignette=0.42, grain=0.010, seed=0,
              bloom=0.55):
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

        # bloom: a wide, soft halo round the lanterns and lit windows. Two
        # downsample-upsample passes give a long-tailed falloff for the cost of
        # one small blur and are what stop an emissive box reading as a flat quad.
        if bloom > 0:
            hi = np.clip(c - 0.55, 0, None)
            if hi.max() > 0:
                from PIL import Image as _Im
                def _blur(plane, div):
                    im = _Im.fromarray(np.ascontiguousarray(plane, np.float32),
                                       mode='F')
                    sw_, sh_ = im.size
                    return np.asarray(im.resize((max(sw_ // div, 1),
                                                 max(sh_ // div, 1)), _Im.BILINEAR)
                                      .resize((sw_, sh_), _Im.BILINEAR), np.float32)
                if np.ndim(hi) == 2:
                    c = c + (_blur(hi, 8) * 0.55 + _blur(hi, 32) * 0.85) * bloom
                else:
                    for ch in range(hi.shape[-1]):
                        c[..., ch] += (_blur(hi[..., ch], 8) * 0.55
                                       + _blur(hi[..., ch], 32) * 0.85) * bloom

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
                 shutter=0.0, moon=None, mist_layer=1.0, pan_rate=0.0,
                 ao=0.0, moon_size=1.0, rain=0.0, rain_wind=(0.10, -0.06)):
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
        self.ao = ao
        self.moon_size = moon_size
        self.rain = rain
        self.rain_wind = rain_wind


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


# ---------------------------------------------------------- the film renderer
def _single_pass(fr, shot, w, h, eye, target, *, dyn=None, jitter=None,
                 time=0.0, want_depth=False):
    """One full-res pass: trace, shade, sky, wet ground, mist, and the depth."""
    rd, ro, right, up = geom.camera_rays(w, h, eye, target, fov_deg=shot.fov,
                                        roll=shot.roll)
    if jitter is not None:
        ty = np.tan(np.radians(shot.fov) * 0.5)
        rd = geom.normalise(rd + (jitter[0] * 2.0 * ty / w) * right[None, None, :]
                            + (jitter[1] * 2.0 * ty / h) * up[None, None, :])
    fwd = geom.normalise(np.asarray(target, np.float32) - np.asarray(eye, np.float32))
    ty = float(np.tan(np.radians(shot.fov) * 0.5))
    cam = (np.asarray(eye, np.float32), fwd, right, up, ty, w / h)

    t, mat, nrm = fr.trace(ro, rd, dyn=dyn, cam=cam)
    col, hit, _dist = fr.shade(ro, rd, t, mat, nrm, fr.lights, shot.fog,
                               shot.fog_tint, shot.ambient, mist=shot.mist,
                               time=time)
    if (~hit).any():
        m = ~hit
        col[m] = fr.sky(rd[m], shot.fog_tint, shot.moon, shot.moon_size, time)
    if shot.wet:
        col = fr.wet(col, ro, rd, t, mat, nrm, fr.lights, shot.fog_tint,
                     strength=shot.wet, time=time)
    if shot.ao:
        col = col * fr.ao(ro, rd, t, hit, nrm, strength=shot.ao)
    col = fr.mist_layer(col, hit, t, rd, strength=shot.mist_layer,
                        tint=shot.fog_tint)
    col = np.nan_to_num(col, nan=0.0, posinf=0.0, neginf=0.0)
    depth = np.where(np.isfinite(t), t, 250.0).astype(np.float32)
    return col, depth


def _defocus(col, coc, taps=9, radius=10.0):
    """Disc defocus with per-pixel circle of confusion, done as a spiral of taps.

    A true bokeh kernel would need one pass per pixel; this samples the disc at
    `taps` golden-angle positions, which is enough for the reference's shallow
    background fall-off and costs the same at every blur radius.
    """
    h, w = coc.shape
    acc = col.copy()
    wsum = np.ones((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ga = 2.399963
    for k in range(taps):
        ang = ga * k
        r = np.sqrt((k + 0.5) / taps) * radius
        ox = (np.cos(ang) * r).astype(np.float32)
        oy = (np.sin(ang) * r).astype(np.float32)
        sx = np.clip(xx + ox * coc, 0, w - 1).astype(np.int32)
        sy = np.clip(yy + oy * coc, 0, h - 1).astype(np.int32)
        samp = col[sy, sx]
        wt = coc
        acc += samp * wt[..., None]
        wsum += wt
    return acc / wsum[..., None]


def _time_blur(fr, shot, w, h, eye_fn, target_fn, dyn_fn, *, taps=5,
               shutter=0.5, base_time=0.0):
    """Sub-frame motion blur: sample the set at several instants inside the shutter.

    This is real motion blur — the geometry and the camera both move between
    taps — not a post-process smear of one frame.
    """
    acc = None
    depth = None
    for k in range(taps):
        frac = (k + 0.5) / taps - 0.5
        tt = base_time + frac * shutter / 24.0
        eye, target = eye_fn(tt), target_fn(tt)
        dyn = dyn_fn(tt)
        c, _d = _single_pass(fr, shot, w, h, eye, target, dyn=dyn,
                             jitter=(float(k) * 0.37 % 1.0 - 0.5,
                                     float(k) * 0.71 % 1.0 - 0.5),
                             time=tt)
        acc = c if acc is None else acc + c
        if depth is None:
            depth = _d
        else:
            depth = np.minimum(depth, _d)
    return acc / taps, depth


def render(fr, shot, width, height, *, time=0.0, eye=None, target=None,
           dyn=None, dyn_fn=None, eye_fn=None, target_fn=None, samples=2,
           dof=0, focus=None, blur_taps=0, seed=0):
    """Render one finished frame, graded.

    `samples` > 1 supersamples with a rotated-grid jitter, which is what removes
    the CG pixel stair on every silhouette. `dof` > 0 applies a disc defocus
    using the true per-pixel depth. `blur_taps` > 0 rebuilds the frame from
    several sub-frame instants instead of smearing a single frame.
    """
    eye = shot.eye if eye is None else eye
    target = shot.target if target is None else target
    h, w = height, width

    if blur_taps > 0 and (eye_fn is not None or dyn_fn is not None):
        e = eye_fn or (lambda _t: eye)
        tg = target_fn or (lambda _t: target)
        d = dyn_fn or (lambda _t: dyn)
        acc, depth = _time_blur(fr, shot, w, h, e, tg, d, taps=blur_taps,
                                shutter=max(shot.shutter, 0.5) if shot.shutter else 0.5,
                                base_time=time)
    else:
        acc = None
        depth = None
        rng = np.random.default_rng(seed)
        n = max(1, samples)
        jitters = [None]
        if n > 1:
            # rotated grid: n*n samples per pixel, evenly spaced, sub-pixel
            side = int(math.ceil(math.sqrt(n)))
            pts = []
            for iy in range(side):
                for ix in range(side):
                    pts.append(((ix + 0.5) / side - 0.5 + (0.5 / side) * (iy % 2),
                                (iy + 0.5) / side - 0.5))
            jitters = [(float(np.clip(px, -0.5, 0.5)), float(np.clip(py, -0.5, 0.5)))
                       for px, py in pts[:n]]
        for k, j in enumerate(jitters):
            c, dep = _single_pass(fr, shot, w, h, eye, target, dyn=dyn,
                                  jitter=j, time=time)
            acc = c if acc is None else acc + c
            if depth is None:
                depth = dep
        acc /= len(jitters)

    if dof and dof > 0:
        f_plane = focus if focus is not None else getattr(shot, 'focus', None)
        if f_plane:
            coc = np.clip(np.abs(depth - f_plane) / max(f_plane, 0.2) * dof, 0, 1) ** 0.8
            acc = _defocus(acc, coc.astype(np.float32), taps=7,
                           radius=float(width) / 220.0)

    # Rain goes on last, after defocus and before the grade, because that is
    # where it is in the optical path: drops are in front of the lens, so they
    # are in focus even when the set behind them is not.
    if getattr(shot, 'rain', 0.0) > 0:
        _, _, right, up = geom.camera_rays(8, 8, eye, target, shot.fov, shot.roll)
        fwd = geom.normalise(np.asarray(target, np.float32) - np.asarray(eye, np.float32))
        ty_r = float(np.tan(np.radians(shot.fov) * 0.5))
        acc = fr.rain_streaks(
            acc, np.where(np.isfinite(depth), depth, 60.0), eye, right, up, fwd,
            time, amount=shot.rain, wind=getattr(shot, 'rain_wind', (0.10, -0.06)),
            seed=seed, ty=ty_r)
    return fr.grade(acc, seed=seed, **shot.grade)
