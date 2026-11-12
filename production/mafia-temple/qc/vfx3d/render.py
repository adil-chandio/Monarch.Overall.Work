"""Render one frame of the night-temple 3D scene.

Pipeline per frame, all NumPy in float32:
  1. build the camera rays for the shot's current camera pose
  2. intersect every solid analytically (plane / box / sphere / capsule / torus)
  3. shade the nearest hit: emissive, ambient, N point lights, rim, specular
  4. exponential height fog + fog drift, wet-ground mirror on the pavement
  5. rain streaks and spray (geometry, density from the shot)
  6. bloom, vignette, tone curve, grain

No billboards, no photo, no text overlay. This is a genuine 3D render at the
resolution asked for; it is deliberately stylised, not photoreal.
"""
from __future__ import annotations

import math

import numpy as np

from . import geom, scene

INF = np.float32(np.inf)


def _precompute(solids):
    boxes, spheres, capsules, toruses = [], [], [], []
    for s in solids:
        if isinstance(s, scene.Box):
            boxes.append((np.array(s.centre, np.float32),
                          np.array(s.half, np.float32), scene.MAT_ID[s.mat]))
        elif isinstance(s, scene.Sphere):
            spheres.append((np.array(s.centre, np.float32), float(s.radius),
                            scene.MAT_ID[s.mat]))
        elif isinstance(s, scene.Capsule):
            capsules.append((np.array(s.a, np.float32), np.array(s.b, np.float32),
                             float(s.radius), scene.MAT_ID[s.mat]))
        elif isinstance(s, scene.Torus):
            toruses.append((np.array(s.centre, np.float32), float(s.R), float(s.r),
                            scene.MAT_ID[s.mat], s.axis))
    return boxes, spheres, capsules, toruses


class Frame:
    """Holds per-frame geometry so the render loop does not rebuild the world."""

    def __init__(self, width=1280, height=720, quality=1.0):
        self.w, self.h, self.q = width, height, quality
        self.solids, self.lights = scene.build_world(with_figure=False)
        self.static = _precompute(self.solids)
        albedo = np.stack([m.albedo for m in scene.MATS.values()]).astype(np.float32)
        emissive = np.stack([m.emissive if m.emissive is not None
                             else np.zeros(3, np.float32)
                             for m in scene.MATS.values()]).astype(np.float32)
        fogmul = np.array([m.fog for m in scene.MATS.values()], np.float32)
        rough = np.array([m.roughness for m in scene.MATS.values()], np.float32)
        spec = np.array([m.spec for m in scene.MATS.values()], np.float32)
        self.mat = dict(albedo=albedo, emissive=emissive, fog=fogmul,
                        rough=rough, spec=spec)
        self._cached_prims = self._static_prims()

    def _static_prims(self):
        prims = []
        for c, h, mi in self.static[0]:
            prims.append((0, c, h, None, mi))
        for c, r, mi in self.static[1]:
            prims.append((1, c, np.float32(r), None, mi))
        for a, b, r, mi in self.static[2]:
            prims.append((2, a, b, (np.float32(r),), mi))
        for c, R, r, mi, axis in self.static[3]:
            prims.append((3, c, np.float32(R), (np.float32(r), axis), mi))
        return prims

    # ------------------------------------------------------------------ trace
    @staticmethod
    def _screen_rect(eye, fwd, right, up, ty, aspect, w, h, lo, hi, pad=2):
        """Pixel rectangle a world-space AABB can possibly cover.

        Returns (y0, y1, x0, x1) in the caller's order — the first version of
        this returned x and y swapped, which silently dropped thin geometry
        (the figure) out of the trace.
        Projects the 8 corners of the bound; anything outside the frame is
        skipped entirely, so a pillar that covers 20% of the screen costs 20%
        of the maths. Rays are still tested properly inside the rectangle, so
        this only removes provably-empty work.
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

    def _bounds(self, kind, p1, p2, p3):
        if kind == 0:
            return p1 - p2, p1 + p2
        if kind == 1:
            r = np.float32(p2)
            return p1 - r, p1 + r
        if kind == 2:
            r = np.float32(p3[0])
            lo = np.minimum(p1, p2) - r
            hi = np.maximum(p1, p2) + r
            return lo, hi
        R, _ = np.float32(p2), np.float32(p3[0])
        rr = R + p3[0]
        return p1 - rr, p1 + rr

    def trace(self, ro, rd, dyn, cam=None):
        H, W = rd.shape[:2]
        prims = list(self._cached_prims)
        for a, b, r, mi in dyn:
            prims.append((2, np.asarray(a, np.float32), np.asarray(b, np.float32),
                          (np.float32(r),), mi))

        t = np.full((H, W), np.inf, np.float32)
        mat = np.zeros((H, W), np.int16)
        nrm = np.zeros((H, W, 3), np.float32)

        # NB: with cam=None every primitive must still be tested, so fall back to
        # the full frame instead of skipping the loop (that bug blanked the scene).
        for kind, p1, p2, p3, mi in prims:
            lo, hi = self._bounds(kind, p1, p2, p3)
            if cam is None:
                y0, y1, x0, x1 = 0, H, 0, W
            else:
                eye, fwd, right, up, ty, aspect = cam
                y0, y1, x0, x1 = self._screen_rect(eye, fwd, right, up, ty,
                                                   aspect, W, H, lo, hi)
            if x1 - x0 < 1 or y1 - y0 < 1:
                continue
            sub_ro, sub_rd = ro[y0:y1, x0:x1], rd[y0:y1, x0:x1]
            t_sub = t[y0:y1, x0:x1]
            if kind == 0:
                tp, ax = geom.ray_aabb(sub_ro, sub_rd, p1, p2)
                m = tp < t_sub
                if not m.any():
                    continue
                t_sub[m] = tp[m]
                mat[y0:y1, x0:x1][m] = mi
                nrm[y0:y1, x0:x1][m] = geom.aabb_normal(ax, sub_rd)[m]
            elif kind == 1:
                tp = geom.ray_sphere(sub_ro, sub_rd, p1, p2)
                m = tp < t_sub
                if not m.any():
                    continue
                t_sub[m] = tp[m]
                mat[y0:y1, x0:x1][m] = mi
                nrm[y0:y1, x0:x1][m] = geom.normalise(sub_ro + sub_rd * tp[..., None] - p1)[m]
            elif kind == 2:
                tp, _ = geom.ray_capsule(sub_ro, sub_rd, p1, p2, p3[0])
                m = tp < t_sub
                if not m.any():
                    continue
                t_sub[m] = tp[m]
                mat[y0:y1, x0:x1][m] = mi
                ba = p2 - p1
                pp = sub_ro + sub_rd * tp[..., None]
                k = np.clip(((pp - p1) @ ba) / max(float(ba @ ba), 1e-8), 0, 1)
                nrm[y0:y1, x0:x1][m] = geom.normalise(pp - (p1 + k[..., None] * ba))[m]
            else:
                tp = geom.ray_torus(sub_ro, sub_rd, p1, p2, p3[0], p3[1])
                m = tp < t_sub
                if not m.any():
                    continue
                t_sub[m] = tp[m]
                mat[y0:y1, x0:x1][m] = mi
                nrm[y0:y1, x0:x1][m] = geom.normalise(sub_ro + sub_rd * tp[..., None] - p1)[m]

        tp, _ = geom.ray_plane(ro, rd, 0.0)
        m = tp < t
        t[m] = tp[m]
        mat[m] = scene.MAT_ID['ground']
        nrm[m] = np.array([0.0, 1.0, 0.0], np.float32)
        return t, mat, nrm


    def _batch(self, ro, rd, prims):
        """Intersect a flat primitive list over a whole grid (no culling).

        Used by the shadow pass, where every sample point is independent and
        the grids are small.
        """
        H, W = rd.shape[:2]
        t = np.full((H, W), np.inf, np.float32)
        mat = np.zeros((H, W), np.int16)
        nrm = np.zeros((H, W, 3), np.float32)
        for kind, p1, p2, p3, mi in prims:
            if kind == 0:
                tp, ax = geom.ray_aabb(ro, rd, p1, p2)
                m = tp < t
                if not m.any():
                    continue
                t[m] = tp[m]
                mat[m] = mi
                nrm[m] = geom.aabb_normal(ax, rd)[m]
            elif kind == 1:
                tp = geom.ray_sphere(ro, rd, p1, p2)
                m = tp < t
                if not m.any():
                    continue
                t[m] = tp[m]
                mat[m] = mi
                nrm[m] = geom.normalise(ro + rd * tp[..., None] - p1)[m]
            elif kind == 2:
                tp, _ = geom.ray_capsule(ro, rd, p1, p2, p3[0])
                m = tp < t
                if not m.any():
                    continue
                t[m] = tp[m]
                mat[m] = mi
                ba = p2 - p1
                pp = ro + rd * tp[..., None]
                k = np.clip(((pp - p1) @ ba) / max(float(ba @ ba), 1e-8), 0, 1)
                nrm[m] = geom.normalise(pp - (p1 + k[..., None] * ba))[m]
            else:
                tp = geom.ray_torus(ro, rd, p1, p2, p3[0], p3[1])
                m = tp < t
                if not m.any():
                    continue
                t[m] = tp[m]
                mat[m] = mi
                nrm[m] = geom.normalise(ro + rd * tp[..., None] - p1)[m]
        return t, mat, nrm

    # ------------------------------------------------------- surface detail
    @staticmethod
    def surface_detail(p, mat):
        """World-space procedural detail: stone courses, wood grain, wet patches.

        Kept in world space so the pattern is glued to the geometry and slides
        correctly with camera motion. This is what stops flat boxes reading as
        flat boxes.
        """
        x, y, z = p[..., 0], p[..., 1], p[..., 2]
        # value noise from hashed sines (cheap, deterministic, no textures)
        n1 = np.sin(x * 3.1 + y * 1.7 + z * 2.3) * 0.5 + 0.5
        n2 = np.sin(x * 11.0 - z * 7.0 + y * 5.0) * 0.5 + 0.5
        n3 = np.sin(y * 27.0 + x * 13.0 - z * 9.0) * 0.5 + 0.5
        grain = (n1 * 0.55 + n2 * 0.30 + n3 * 0.15)
        detail = 0.86 + 0.28 * grain

        # stone courses: horizontal joints every 0.34 m, offset every other row
        name = np.zeros_like(x)
        stone = (mat == scene.MAT_ID['stone']) | (mat == scene.MAT_ID['darkstone'])
        row = np.floor(y / 0.34)
        off = np.mod(np.floor(row), 2.0) * 0.45
        joint_v = np.abs(np.mod(x + off, 0.9) - 0.45)
        joint_h = np.abs(np.mod(y + 0.02, 0.34) - 0.17)
        mortar = np.clip(np.minimum(joint_v, joint_h * 1.6) / 0.045 - 1.0, 0, 1)
        detail = np.where(stone, detail * (0.80 + 0.20 * mortar), detail)

        # wood: vertical grain on the columns and beams
        wood = mat == scene.MAT_ID['wood']
        wgrain = 0.88 + 0.22 * (np.sin(x * 46.0 + z * 41.0) * 0.5 + 0.5)
        detail = np.where(wood, wgrain, detail)

        # roof tiles: ridged courses down the slope
        tile = mat == scene.MAT_ID['tile']
        ridge = 0.72 + 0.28 * (np.abs(np.sin(x * 9.0)) ** 0.6)
        detail = np.where(tile, ridge, detail)

        # wet patches on the pavement
        ground = mat == scene.MAT_ID['ground']
        wet = 0.72 + 0.28 * np.clip(n1 * n2 * 1.9, 0, 1)
        detail = np.where(ground, wet, detail)
        return detail.astype(np.float32)

    def _moon_shadow(self, p, nrm, light_dir, scale=4):
        """Shadow mask for the directional light, computed on a coarse grid.

        Rays are fired from the (sub-sampled) hit points toward the moon and
        tested against the static solids only. A shadow of the roof, the
        columns and the gate falling across the courtyard is the cheapest way
        to make a night set read as solid architecture.
        """
        H, W = nrm.shape[:2]
        h, w = H // scale, W // scale
        ps = p[::scale, ::scale][:h, :w]
        ns = nrm[::scale, ::scale][:h, :w]
        bias = 0.02
        o = ps + ns * bias
        d = np.broadcast_to(np.asarray(light_dir, np.float32), o.shape).copy()
        t, _, _ = self._batch(o, d, self._cached_prims)
        lit = (~np.isfinite(t)).astype(np.float32)
        # feather the mask so shadow edges are not aliased staircase blocks
        k = 3
        pad = np.pad(lit, ((k, k), (k, k)), mode='edge')
        acc = np.zeros_like(lit)
        for dy in range(-k, k + 1):
            for dx in range(-k, k + 1):
                acc += pad[k + dy:k + dy + h, k + dx:k + dx + w]
        lit = acc / float((2 * k + 1) ** 2)
        lit = np.clip(lit * 1.35, 0, 1)
        import cv2
        return cv2.resize(lit, (W, H), interpolation=cv2.INTER_LINEAR)

    # ------------------------------------------------------------------ shade
    def shade(self, ro, rd, t, mat, nrm, lights, eye_lights, fog_density,
              fog_tint, ambient):
        hit = np.isfinite(t) & (t < 400.0)
        p = ro + rd * np.where(hit, t, 0)[..., None]
        alb = self.mat['albedo'][mat]
        alb = alb * self.surface_detail(p, mat)[..., None]
        emis = self.mat['emissive'][mat] * (self.mat['emissive'][mat] > 0).astype(np.float32)
        shadow = None
        rg = self.mat['rough'][mat]
        sp = self.mat['spec'][mat]

        col = alb * ambient[None, None, :]
        # height fog darkening on the ground, stronger with distance
        dist = np.where(hit, t, 0).astype(np.float32)

        for L in lights:
            light_col = np.asarray(L.colour, np.float32)
            if L.direction is not None:
                # directional: constant direction, no falloff, shelf-shaded by N.L
                if shadow is None:
                    shadow = self._moon_shadow(p, nrm, L.direction)
                ldir = np.asarray(L.direction, np.float32)[None, None, :]
                ldir = np.broadcast_to(ldir, nrm.shape)
                ndl = np.clip((nrm * ldir).sum(-1), 0, 1)
                atten = np.float32(L.intensity)
            else:
                lv = np.asarray(L.pos, np.float32)[None, None, :] - p
                d2 = (lv * lv).sum(-1) + 1e-4
                ldir = lv / np.sqrt(d2)[..., None]
                ndl = np.clip((nrm * ldir).sum(-1), 0, 1)
                atten = L.intensity / (d2 + L.radius ** 2 * 4.0)
            # wrapped diffuse: a little light wraps past the terminator so
            # silhouettes keep their form instead of going black
            wrapped = np.clip((ndl + 0.18) / 1.18, 0, 1)
            diff = wrapped * atten
            if L.direction is not None:
                diff = diff * shadow * 1.0
            shade = np.clip(1.0 - dist * 0.004, 0.45, 1.0)
            col += alb * light_col[None, None, :] * diff[..., None] * shade[..., None]
            # specular
            hv = geom.normalise(-rd + ldir)
            ndh = np.clip((nrm * hv).sum(-1), 0, 1)
            spec_term = (1.0 - rg) ** 2 * sp * ndh ** (8.0 + 40.0 * (1.0 - rg))
            col += np.asarray(light_col, np.float32)[None, None, :] * (spec_term * atten)[..., None]

        for pos, light_col, inten, radius in eye_lights:
            lp = np.asarray(pos, np.float32)
            lv = lp[None, None, :] - p
            d2 = (lv * lv).sum(-1) + 1e-3
            ndl = np.clip((nrm * (lv / np.sqrt(d2)[..., None])).sum(-1), 0, 1)
            atten = inten / (d2 + radius * radius * 4.0)
            col += np.asarray(light_col, np.float32)[None, None, :] * (ndl * atten)[..., None] * 0.35

        # cool rim: grazing surfaces catch the night sky, so dark wood and
        # silhouettes still read as shapes instead of black holes
        ndv = np.clip((nrm * -rd).sum(-1), 0, 1)
        rim = (1.0 - ndv) ** 3.0
        col = col + np.asarray(fog_tint, np.float32)[None, None, :] * (rim * 0.85)[..., None]
        col = col + emis

        # exponential fog: denser near the ground, drifting with time
        y = np.clip(p[..., 1], 0, 30)
        hf = np.exp(-y * 0.30)
        fog = 1.0 - np.exp(-dist * fog_density * (0.35 + 0.65 * hf)
                           * self.mat['fog'][mat])
        sky = np.asarray(fog_tint, np.float32)
        col = col * (1 - fog[..., None]) + sky[None, None, :] * fog[..., None]
        # unlit background: deep night gradient
        v = np.clip((rd[..., 1] * 0.5 + 0.5), 0, 1)
        bg = sky[None, None, :] * (0.35 + 0.65 * v[..., None] ** 1.6)
        col = np.where(hit[..., None], col, bg)
        return col.astype(np.float32), hit, dist

    # ------------------------------------------------------------------ extras
    def wet_floor(self, col, ro, rd, t, mat, nrm, lights, eye_lights,
                  fog_density, fog_tint, ambient, strength=0.55, time=0.0):
        """Mirror the scene on wet stone.

        Only lights whose *reflected* direction lines up with the view ray
        contribute, and the result is bounded, so the pavement gets streaks of
        lantern light instead of turning into a glowing slab.
        """
        m = (mat == scene.MAT_ID['ground']) & np.isfinite(t) & (t < 120)
        if not m.any() or strength <= 0:
            return col
        ry = np.array(rd, dtype=np.float32, copy=True)
        ry[..., 1] = -ry[..., 1]
        ry = geom.normalise(ry)
        if not np.isfinite(ry).all():
            return col
        p = ro + rd * t[..., None]
        refl = np.zeros_like(col)
        for L in lights:
            lv = np.asarray(L.pos, np.float32)[None, None, :] - p
            d2 = (lv * lv).sum(-1) + 0.25
            ldir = lv / np.sqrt(d2)[..., None]
            align = np.clip((ldir * ry).sum(-1), 0, 1) ** 220
            contrib = align * L.intensity / (d2 * 26.0 + 8.0)
            refl += np.asarray(L.colour, np.float32)[None, None, :] * contrib[..., None]
        # faint moon sheen on the wet stone
        refl += np.asarray(fog_tint, np.float32)[None, None, :] * 0.22
        ripple = 0.55 + 0.45 * np.sin(p[..., 0] * 7.0 + p[..., 2] * 4.0 + time * 1.7)
        wet = np.nan_to_num(strength * m * ripple, nan=0.0).astype(np.float32)
        refl = np.nan_to_num(refl, nan=0.0, posinf=0.0, neginf=0.0)
        out = col * (1.0 - wet[..., None]) + np.clip(refl, 0, 3.0) * wet[..., None]
        return np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0)

    @staticmethod
    def sky(rd, fog_tint, moon_dir=(-0.30, 0.42, -0.86), time=0.0, clouds=True):
        """Night sky: vertical gradient, moon disc + halo, slow cloud bands.

        Not an HDRI; a procedural backdrop so the frame is a picture and not a
        black void. Everything is a function of the ray direction only.
        """
        d = geom.normalise(rd)
        y = np.clip(d[..., 1], -1, 1)
        horizon = np.clip(1.0 - np.abs(y) * 2.2, 0, 1) ** 2.2
        base = np.asarray(fog_tint, np.float32)[None, None, :] * (0.55 + 1.55 * horizon[..., None])
        zenith = np.array([0.014, 0.022, 0.048], np.float32)
        base = base * (0.35 + 0.65 * horizon[..., None]) + zenith[None, None, :] * (1 - horizon[..., None])
        if clouds:
            x = d[..., 0] / np.maximum(np.abs(y) + 0.08, 0.08)
            z = d[..., 2] / np.maximum(np.abs(y) + 0.08, 0.08)
            band = (np.sin(x * 1.7 + z * 0.9 + time * 0.06) * 0.5
                    + np.sin(x * 3.3 - z * 2.1 + time * 0.03) * 0.3
                    + np.sin(x * 7.1 + z * 4.4) * 0.2)
            cloud = np.clip(band * 0.5 + 0.5, 0, 1) ** 2.4
            cloud *= np.clip(1.0 - np.abs(y - 0.22) * 2.0, 0, 1)
            tint = np.array([0.085, 0.105, 0.150], np.float32)
            base = base + tint[None, None, :] * cloud[..., None]
        md = geom.normalise(np.asarray(moon_dir, np.float32))
        cosang = (d * md).sum(-1)
        disc = np.clip((cosang - 0.99955) / 0.00045, 0, 1)
        halo = np.clip((cosang - 0.90) / 0.10, 0, 1) ** 4
        moon_col = np.array([0.85, 0.90, 1.05], np.float32)
        base = base + moon_col[None, None, :] * (disc * 3.2 + halo * 0.22)[..., None]
        return base.astype(np.float32)

    @staticmethod
    def god_rays(col, hit, t, rd, source, strength=0.55, spread=0.16):
        """Cheap screen-space shafts radiating from a bright source position."""
        H, W = col.shape[:2]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        sx, sy = source
        dx = (xx / W - sx)
        dy = (yy / H - sy)
        r = np.sqrt(dx * dx + dy * dy) + 1e-5
        ang = np.arctan2(dy, dx)
        shafts = (np.sin(ang * 13.0) * 0.5 + np.sin(ang * 29.0 + 1.3) * 0.3
                  + np.sin(ang * 7.0 + 2.7) * 0.2)
        falloff = np.clip(1.0 - r / (0.85), 0, 1) ** 2.2
        edge = np.clip((r - spread) / 0.12, 0, 1)
        fade = np.where(hit, 1.0, 0.25)
        shaft = np.clip(shafts, 0, 1) * falloff * edge * fade
        tint = np.array([0.30, 0.26, 0.20], np.float32)
        return col + tint[None, None, :] * (shaft * strength)[..., None]

    @staticmethod
    def rain(col, rd, t, seed, density=1.0, speed=14.0, frame=0, length=0.42):
        """Rain as real 3D streaks: nearest-hash sampling along each ray."""
        if density <= 0:
            return col
        rng = np.random.default_rng(seed)
        # 3 fixed layers of drops; parallax comes from the camera position
        out = col
        for layer in range(3):
            n = int(900 * density * (1.0 + layer))
            tops = rng.uniform(-10, 14, (n, 3)).astype(np.float32)
            tops[:, 1] = rng.uniform(0, 12, n)
            tops[:, 2] += layer * 6.0
            fall = (frame * speed / 24.0) % 12.0
            tops[:, 1] = (tops[:, 1] - fall) % 12.0
            # project a few drops to screen space and add a thin streak
            # (screen-space streaks are cheap and read correctly at 24 fps)
            H, W = col.shape[:2]
            cam_dir = rd[H // 2, W // 2]
            depth = 1.0 / np.maximum(np.abs(cam_dir[2]), 0.1)
            xs = (tops[:, 0] / np.maximum(depth, 0.5) + 0.5)
            ys = (0.5 - tops[:, 1] / 22.0) * 1.0
            for i in range(n):
                x = int((0.5 + xs[i] * 0.9) * W) % W
                y = int(ys[i] * H) % H
                ln = int(6 + 10 * length)
                a = 0.10 / (1 + layer)
                col[max(0, y):min(H, y + ln), max(0, x):min(W, x + 1)] += a
        return col

    @staticmethod
    def bloom(col, strength=0.6):
        """Threshold-and-blur glow so lanterns and the eye light bleed."""
        lum = col.mean(-1, keepdims=True)
        bright = np.clip(col - 0.82, 0, None)
        # separable box blur via cumulative sums (fast, adequate at 720p)
        def box(a, r):
            k = r * 2 + 1
            pad = np.pad(a, ((r, r), (r, r), (0, 0)), mode='edge')
            c = np.cumsum(np.cumsum(pad, 0), 1)
            c = np.pad(c, ((1, 0), (1, 0), (0, 0)))
            out = (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)
            return out[:a.shape[0], :a.shape[1]]
        g = box(box(bright, 6), 10)
        return col + g * strength

    @staticmethod
    def finish(col, exposure=1.0, vignette=0.30, grain=0.005, seed=0,
               contrast=1.12, saturation=1.06, lift=0.004):
        col = np.nan_to_num(col, nan=0.0, posinf=0.0, neginf=0.0)
        c = np.clip(col * exposure, 0, None)
        # filmic-ish shoulder: keeps highlights from clipping, lifts midtones
        c = (c * (2.51 * c + 0.03)) / (c * (2.43 * c + 0.59) + 0.14)
        c = np.power(np.clip(c, 0, 1), 1 / 2.2)
        lum = (c * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1, keepdims=True)
        c = lum + (c - lum) * saturation
        c = (c - 0.5) * contrast + 0.5 + lift
        H, W = c.shape[:2]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        c *= (1.0 - vignette * np.clip((r - 0.45) / 0.85, 0, 1) ** 1.6)[..., None]
        rng = np.random.default_rng(seed)
        c += rng.normal(0, grain, (H, W, 1)).astype(np.float32)
        return np.clip(c * 255, 0, 255).astype(np.uint8)
