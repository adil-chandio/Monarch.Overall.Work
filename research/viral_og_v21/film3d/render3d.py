#!/usr/bin/env python3
"""
Frame renderer. Every frame is computed: ray-marched set, shaded characters,
volumetric single scatter, lens and film post. No sampled frames.

Pipeline per frame
  1  camera: position, target, fov, roll, aperture from an anim curve
  2  set   : ray-march the implicit cave, refine by bisection, analytic normal,
             albedo from 3D noise evaluated at the hit point
  3  chars : shade point clouds with the full light rig, depth-test against the
             set's depth buffer, splat with adaptive soft taps
  4  volume: ray-march density with HG phase through the same lights
  5  post  : exposure, ACES, bloom, anamorphic streak, CA, vignette, grain
"""
from __future__ import annotations

import math

import numpy as np

from geo3d import Cave, nrm, fbm, smoothstep


# ---------------------------------------------------------------- camera


class Cam:
    def __init__(self, W, H, eye, target, up=(0, 1, 0), fov=42.0, roll=0.0):
        self.W, self.H = int(W), int(H)
        self.eye = np.asarray(eye, np.float32)
        f = nrm(np.asarray(target, np.float32) - self.eye)
        u = np.asarray(up, np.float32)
        if abs(float(f @ u)) > 0.999:
            u = np.array([0, 0, 1], np.float32)
        r = nrm(np.cross(f, u))
        u2 = np.cross(r, f)
        if roll:
            c, s = math.cos(roll), math.sin(roll)
            r, u2 = r * c + u2 * s, -r * s + u2 * c
        self.R, self.U, self.F = r.astype(np.float32), u2.astype(np.float32), f.astype(np.float32)
        self.f = 0.5 * self.W / math.tan(math.radians(fov) * 0.5)
        self.cx, self.cy = self.W * 0.5, self.H * 0.5

    def view(self, P):
        d = P - self.eye
        return d @ self.R, d @ self.U, d @ self.F

    def to_screen(self, x, y, z):
        inv = 1.0 / np.maximum(z, 1e-4)
        return self.cx + self.f * x * inv, self.cy - self.f * y * inv, inv

    def rays(self, sx, sy):
        x = (sx - self.cx) / self.f
        y = -(sy - self.cy) / self.f
        return nrm(self.R[None, :] * x[:, None] + self.U[None, :] * y[:, None] + self.F[None, :])


# ---------------------------------------------------------------- lights


class Light:
    def __init__(self, pos, col, power, kind="point", spot_dir=None, spot_cos=0.0):
        self.pos = np.asarray(pos, np.float32)
        self.col = np.asarray(col, np.float32)
        self.power = float(power)
        self.kind = kind
        self.spot_dir = None if spot_dir is None else nrm(np.asarray(spot_dir, np.float32))
        self.spot_cos = spot_cos

    def attenuation(self, P):
        d = self.pos[None, :] - P
        dist = np.linalg.norm(d, axis=1) + 1e-6
        if self.kind == "portal":
            a = self.power / (dist * dist + 2.0) * (1.0 - np.exp(-dist / 1.4))
        else:
            a = self.power / (dist * dist + 0.30)
        if self.spot_dir is not None:
            l = d / dist[:, None]
            a = a * smoothstep(self.spot_cos, 1.0, -(l @ self.spot_dir))
        return a, d / dist[:, None], dist


def visibility(P, L, cave, steps=10):
    """Soft shadow along the segment P -> light, using the cave's own SDF.

    Paths are 1 m or less, so a handful of taps is enough; the penumbra comes
    from how far the worst tap sits inside the rock, not from a binary test.
    """
    seg = L.pos[None, :] - P
    worst = np.full(len(P), -1e3, np.float32)
    for i in range(1, steps + 1):
        q = P + seg * (i / (steps + 1.0))
        worst = np.maximum(worst, cave.sdf(q))
    return (1.0 - smoothstep(-0.015, 0.075, worst)).astype(np.float32)


# ---------------------------------------------------------------- set


def march_set(cam, cave, W, H, tmax=46.0, steps=52):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = cam.rays(xx.ravel(), yy.ravel())
    o = cam.eye[None, :]
    rng = np.random.default_rng(int(cam.eye[0] * 977) & 0xffff)
    t = 0.20 + rng.random(d.shape[0]).astype(np.float32) * 0.06
    hit = np.zeros(d.shape[0], bool)
    beyond = np.zeros(d.shape[0], bool)
    for _ in range(steps):
        p = o + d * t[:, None]
        s = cave.sdf(p)
        now = (~hit) & (~beyond) & (s > 0)
        if now.any():
            lo = np.maximum(t - s, 0.02)
            hi = t.copy()
            for _ in range(6):
                mid = 0.5 * (lo + hi)
                ins = cave.sdf(o + d * mid[:, None]) < 0
                lo = np.where(ins, mid, lo)
                hi = np.where(ins, hi, mid)
            t = np.where(now, lo, t)
            hit |= now
        # sphere tracing: advance by the (clamped) distance to the surface, so a
        # 30 m bore is crossed in tens of samples instead of ~100
        st = np.clip(np.abs(s) * 0.92, 0.10, 2.6) * (~hit) * (~beyond)
        t += st
        far = (~hit) & (t > tmax)
        beyond |= far
        if (hit | beyond).all():
            break
    P = o + d * t[:, None]
    N = cave.normal(P)
    return dict(P=P.astype(np.float32), N=N.astype(np.float32), t=t.astype(np.float32),
                hit=hit.reshape(H, W), d=d, xx=xx.ravel(), yy=yy.ravel(), W=W, H=H)


def shade_set(hit, cam, cave, lights, exposure=1.0, fog=0.013):
    P, N, t = hit["P"], hit["N"], hit["t"]
    isfloor = P[:, 1] < cave.floor_y + 0.06

    # surface detail by bump: gradient of 3D noise in the tangent plane
    s = 3.1
    e = 0.04
    n0 = fbm(P[:, 0] * s, P[:, 1] * s, P[:, 2] * s, 3)
    gx = fbm((P[:, 0] + e) * s, P[:, 1] * s, P[:, 2] * s, 3) - n0
    gy = fbm(P[:, 0] * s, (P[:, 1] + e) * s, P[:, 2] * s, 3) - n0
    gz = fbm(P[:, 0] * s, P[:, 1] * s, (P[:, 2] + e) * s, 3) - n0
    n1 = fbm(P[:, 0] * 13, P[:, 1] * 13, P[:, 2] * 13, 2)
    gx += (fbm((P[:, 0] + 0.06) * 13, P[:, 1] * 13, P[:, 2] * 13, 2) - n1) * 0.18
    gy += (fbm(P[:, 0] * 13, (P[:, 1] + 0.06) * 13, P[:, 2] * 13, 2) - n1) * 0.18
    gz += (fbm(P[:, 0] * 13, P[:, 1] * 13, (P[:, 2] + 0.06) * 13, 2) - n1) * 0.18
    G = np.stack([gx, gy, gz], 1) * 1.5
    G -= (G * N).sum(1, keepdims=True) * N
    Nd = nrm(N - G)

    band = fbm(P[:, 0] * 0.55 + P[:, 2] * 0.22, P[:, 1] * 3.1, P[:, 2] * 0.55, 4)
    strata = np.sin(P[:, 1] * 7.2 + band * 6.0) * 0.5 + 0.5
    grime = fbm(P[:, 0] * 2.3, P[:, 1] * 2.3, P[:, 2] * 2.3, 3)
    spec = fbm(P[:, 0] * 24, P[:, 1] * 24, P[:, 2] * 24, 2)
    k = (0.62 + 0.60 * band) * (0.84 + 0.30 * grime) * (0.90 + 0.20 * strata) * (0.93 + 0.14 * spec)
    rock = np.array([0.285, 0.272, 0.246], np.float32)[None, :] * k[:, None]
    grav = smoothstep(0.35, 0.72, fbm(P[:, 0] * 4.5, 3.0, P[:, 2] * 4.5, 3))
    fl = np.array([0.150, 0.140, 0.126], np.float32)[None, :] * (0.55 + 0.85 * band)[:, None]
    fl = fl * (0.72 + 0.55 * grav[:, None])
    alb = np.where(isfloor[:, None], fl, rock)
    wet = smoothstep(0.60, 0.80, fbm(P[:, 0] * 1.1, P[:, 1] * 1.1, P[:, 2] * 1.1, 3)) * (~isfloor)
    alb = alb * (1.0 - 0.40 * wet[:, None])
    specamt = 0.07 + 0.55 * wet

    V = cam.eye[None, :] - P
    vd = np.linalg.norm(V, axis=1) + 1e-6
    V = V / vd[:, None]
    ndv = np.clip((Nd * V).sum(1), 1e-3, 1.0)

    # ambient: dark room + a cold sky fill from the mouth direction
    skyv = visibility(P, Light([0, 0.6, cave.mouth_z + 0.5], (0, 0, 0), 1.0), cave)
    col = alb * (skyv[:, None] * np.array([0.018, 0.028, 0.052], np.float32)[None, :]
                 + np.array([0.004, 0.005, 0.008], np.float32)[None, :])

    for L in lights:
        att, l, dist = L.attenuation(P)
        vis = visibility(P, L, cave)
        att = att * vis
        ndl = (Nd * l).sum(1)
        diff = np.clip((ndl + 0.22) / 1.22, 0, 1)
        col += alb * L.col[None, :] * (diff * att)[:, None]
        h = nrm(l + V)
        ndh = np.clip((Nd * h).sum(1), 0, 1)
        a = 0.30 ** 2
        den = ndh * ndh * (a * a - 1) + 1
        D = a * a / (math.pi * den * den + 1e-9)
        Fs = 0.04 + 0.96 * (1 - ndv) ** 5
        sp = (D * Fs * specamt)[:, None] * L.col[None, :] * (np.clip(ndl, 0, 1) * att)[:, None]
        col += np.minimum(sp, 2.5)
        rim = (1 - ndv) ** 2.2 * np.clip(-ndl * 0.6 + 0.60, 0, 1) * att * 0.40
        col += rim[:, None] * L.col[None, :] * (0.35 + 0.65 * alb)

    fv = 1.0 - np.exp(-fog * np.maximum(vd - 1.0, 0.0))
    col = col * (1 - fv[:, None]) + np.array([0.006, 0.009, 0.016], np.float32)[None, :] * fv[:, None]
    img = col.reshape(hit["H"], hit["W"], 3).astype(np.float32)
    depth = np.where(hit["hit"], hit["t"].reshape(hit["H"], hit["W"]), 1e4).astype(np.float32)
    trans = (1.0 - fv).reshape(hit["H"], hit["W"]).astype(np.float32)
    trans = trans * hit["hit"].astype(np.float32) ** 1  # sky (no hit) = open mouth, still fogged by volume only
    return img * exposure, depth, trans


# ---------------------------------------------------------------- characters


def shade_points(nd, cam, lights, cave, amb=0.0):
    P, N, C = nd["P"], nd["N"], nd["C"]
    V = cam.eye[None, :] - P
    vd = np.linalg.norm(V, axis=1) + 1e-6
    V = V / vd[:, None]
    ndv = np.clip((N * V).sum(1), 1e-3, 1.0)
    col = C * amb
    for L in lights:
        att, l, dist = L.attenuation(P)
        if amb > 0 or True:
            vis = visibility(P, L, cave)
            att = att * vis
        ndl = (N * l).sum(1)
        diff = np.clip((ndl + 0.25) / 1.25, 0, 1)
        col = col + C * L.col[None, :] * (diff * att)[:, None]
        h = nrm(l + V)
        ndh = np.clip((N * h).sum(1), 0, 1)
        a = np.maximum(nd["R"], 0.03) ** 2
        den = ndh * ndh * (a * a - 1) + 1
        D = a * a / (math.pi * den * den + 1e-9)
        k = a * 0.5
        Gg = (ndv / (ndv * (1 - k) + k)) * (np.clip(ndl, 0, 1) / (np.clip(ndl, 0, 1) * (1 - k) + k))
        Fs = 0.05 + 0.95 * (1 - ndv) ** 5
        sp = (D * Gg * Fs * nd["S"])[:, None] * L.col[None, :] * (np.clip(ndl, 0, 1) * att)[:, None]
        col = col + np.minimum(sp, 8.0)
        rim = (np.clip(1 - ndv, 0, 1) ** 1.9) * np.clip(-ndl * 0.55 + 0.62, 0, 1) * att * 1.15
        col = col + rim[:, None] * L.col[None, :] * (0.4 + 0.6 * C)
    col = col + C * nd["EM"][:, None]
    fv = 1.0 - np.exp(-0.024 * np.maximum(vd - 1.0, 0.0))
    col = col * (1 - fv[:, None]) + np.array([0.006, 0.009, 0.016], np.float32)[None, :] * fv[:, None]
    return col.astype(np.float32)


_TAP_CACHE = {}


def _taps(n):
    if n in _TAP_CACHE:
        return _TAP_CACHE[n]
    k = np.arange(n, dtype=np.float32) + 0.5
    r = np.sqrt(k / n)
    a = k * 2.39996323
    out = np.stack([np.cos(a) * r, np.sin(a) * r], 1).astype(np.float32) if n > 1 else np.zeros((1, 2), np.float32)
    _TAP_CACHE[n] = out
    return out


def splat(nd, cam, W, H, zbuf, col=None, max_taps=24, rad=2.2):
    """Deferred point splatting.

    Points are only used to (a) win the depth test and (b) hand over a surface
    normal, albedo and material for each pixel. Shading then happens per pixel
    in screen space, so a cloud of points reads as one solid surface instead of
    a heap of overlapping blobs. Returns None when nothing is visible.
    """
    x, y, z = cam.view(nd["P"])
    ok = z > 0.10
    if ok.sum() < 4:
        return None
    P, N = nd["P"][ok], nd["N"][ok]
    x, y, z = x[ok], y[ok], z[ok]
    sx, sy, inv = cam.to_screen(x, y, z)
    rpx = np.clip(nd["PX"][ok] * cam.f * inv * rad, 1.1, 26.0)
    nb = W * H

    # ---- pass 1: nearest depth per pixel
    zmin = np.full(nb, 1e9, np.float32)
    for k in range(2):
        n = 1 if k == 0 else 5
        T = _taps(n) * (rpx[:, None] * (0.55 if k == 0 else 0.95))[:, None, :]
        tx = sx[:, None] + T[..., 0]
        ty = sy[:, None] + T[..., 1]
        ix = np.floor(tx).astype(np.int32); iy = np.floor(ty).astype(np.int32)
        inb = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
        fl = np.where(inb, iy.astype(np.int64) * W + ix.astype(np.int64), 0)
        zz = np.where(inb, z[:, None], 1e9)
        np.minimum.at(zmin, fl.ravel(), zz.ravel())
    zmin = np.minimum(zmin, zbuf.reshape(-1))          # geometry in front wins

    # ---- pass 2: gather material for the pixels the nearest points own
    hit = np.zeros(nb, bool)
    accN = np.zeros((nb, 3), np.float32)
    accC = np.zeros((nb, 3), np.float32)
    accM = np.zeros((nb, 4), np.float32)
    cnt = np.zeros(nb, np.float32)
    for k in range(2):
        n = 1 if k == 0 else 5
        T = _taps(n) * (rpx[:, None] * (0.55 if k == 0 else 0.95))[:, None, :]
        tx = sx[:, None] + T[..., 0]
        ty = sy[:, None] + T[..., 1]
        ix = np.floor(tx).astype(np.int32); iy = np.floor(ty).astype(np.int32)
        inb = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
        fl = np.where(inb, iy.astype(np.int64) * W + ix.astype(np.int64), 0)
        keep = inb & (z[:, None] <= zmin[fl] * 1.004 + 1e-3)
        w = keep.astype(np.float32)
        for c in range(3):
            accN[:, c] += np.bincount(fl.ravel(), weights=(N[:, c][:, None] * w).ravel(), minlength=nb)[:nb]
            accC[:, c] += np.bincount(fl.ravel(), weights=(nd["C"][ok][:, c][:, None] * w).ravel(), minlength=nb)[:nb]
        for j, key in enumerate(("S", "R", "PX", "EM")):
            accM[:, j] += np.bincount(fl.ravel(), weights=(nd[key][ok][:, None] * w).ravel(), minlength=nb)[:nb]
        cnt += np.bincount(fl.ravel(), weights=w.ravel(), minlength=nb)[:nb]
        hit |= np.bincount(fl.ravel(), weights=w.ravel(), minlength=nb)[:nb] > 0

    if not hit.any():
        return None
    idx = np.nonzero(hit)[0]
    c = np.maximum(cnt[idx], 1e-6)[:, None]
    Np = nrm(accN[idx] / c)
    d = cam.rays((idx % W).astype(np.float32) + 0.5, (idx // W).astype(np.float32) + 0.5)
    Pp = cam.eye[None, :] + d * zmin[idx][:, None]
    return dict(idx=idx, P=Pp.astype(np.float32), N=Np.astype(np.float32),
                C=(accC[idx] / c).astype(np.float32),
                S=(accM[idx, 0] / c[:, 0]).astype(np.float32),
                R=(accM[idx, 1] / c[:, 0]).astype(np.float32),
                PX=(accM[idx, 2] / c[:, 0]).astype(np.float32),
                EM=(accM[idx, 3] / c[:, 0]).astype(np.float32))


def composite(img, g, cam, lights, cave, amb=0.02):
    """Shade a gathered surface per pixel and over it on the plate."""
    if g is None:
        return img
    col = shade_points(g, cam, lights, cave, amb=amb)
    flat = img.reshape(-1, 3)
    flat[g["idx"]] = col
    return flat.reshape(img.shape)


# ---------------------------------------------------------------- solid objects


def march_objects(cam, objs, W, H, zbuf, steps=38):
    """Raymarch solid SDF props/characters, keeping whatever is nearest.

    Each object is culled by its bounding sphere and only traced where it can
    beat the geometry that is already there, so the cost stays on the pixels the
    animal actually covers.
    """
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = cam.rays(xx.ravel(), yy.ravel())
    o = cam.eye[None, :]
    best_t = zbuf.reshape(-1).astype(np.float32).copy()
    best_o = np.full(d.shape[0], -1, np.int16)
    for oi, ob in enumerate(objs):
        c = np.asarray(ob.centre, np.float32)
        R = float(ob.radius)
        oc = o - c[None, :]
        b = (d * oc).sum(1)
        cc = (oc * oc).sum(1) - R * R
        disc = b * b - cc
        m = disc > 0
        if not m.any():
            continue
        sq = np.sqrt(np.maximum(disc, 0))
        t0 = np.maximum(-b - sq, 0.02)
        t1 = -b + sq
        m = m & (t0 < best_t) & (t1 > 0.02)
        idx = np.nonzero(m)[0]
        if idx.size == 0:
            continue
        t = t0[idx].copy()
        live = np.ones(idx.size, bool)
        hit = np.zeros(idx.size, bool)
        for _ in range(steps):
            sel = np.nonzero(live)[0]
            if sel.size == 0:
                break
            p = o + d[idx[sel]] * t[sel][:, None]
            s = ob.sdf(p)
            got = s < 1.2e-3
            if got.any():
                g = sel[got]
                lo = np.maximum(t[g] - np.abs(s[got]) - 1e-3, 0.01)
                hi = t[g].copy()
                for _k in range(5):
                    mid = 0.5 * (lo + hi)
                    ins = ob.sdf(o + d[idx[g]] * mid[:, None]) < 0
                    lo = np.where(ins, mid, lo)
                    hi = np.where(ins, hi, mid)
                t[g] = lo
                hit[g] = True
                live[g] = False
            t[sel] = t[sel] + np.clip(np.abs(s) * 0.85, 8e-4, 0.30)
            live &= t < np.minimum(best_t[idx], t1[idx])
        if hit.any():
            gi = idx[hit]
            best_t[gi] = t[hit]
            best_o[gi] = oi
    mask = best_o >= 0
    if not mask.any():
        return None
    gi = np.nonzero(mask)[0]
    P = (o + d[gi] * best_t[gi][:, None]).astype(np.float32)
    N = np.zeros_like(P)
    for oi, ob in enumerate(objs):
        sel = best_o[gi] == oi
        if sel.any():
            N[sel] = _sdf_normal(ob.sdf, P[sel])
    return dict(idx=gi, P=P, N=N, obj=best_o[gi])


def _sdf_normal(fn, P, e=6e-4):
    gx = fn(P + np.array([e, 0, 0], np.float32)) - fn(P - np.array([e, 0, 0], np.float32))
    gy = fn(P + np.array([0, e, 0], np.float32)) - fn(P - np.array([0, e, 0], np.float32))
    gz = fn(P + np.array([0, 0, e], np.float32)) - fn(P - np.array([0, 0, e], np.float32))
    return nrm(-np.stack([gx, gy, gz], -1))


def sdf_ao(fn, P, N, radii=(0.045, 0.11, 0.24)):
    """Contact darkening from five taps along the normal: creases, sockets, gaps."""
    occ = np.zeros(len(P), np.float32)
    for i, r in enumerate(radii):
        h = r * (0.55 + 0.45 * (i / max(len(radii) - 1, 1)))
        s = fn(P + N * h)
        occ += np.clip((h - s) / h, 0.0, 1.0) * (1.0 / (i + 1.4))
    return np.clip(1.0 - occ * 0.85, 0.0, 1.0).astype(np.float32)


def shade_surface(P, N, mat, cam, lights, cave, ao):
    """Cook-Torrance-ish shading for one surface, with cave occlusion + AO."""
    C = mat["C"]
    V = cam.eye[None, :] - P
    vd = np.linalg.norm(V, axis=1) + 1e-6
    V = V / vd[:, None]
    ndv = np.clip((N * V).sum(1), 1e-3, 1.0)
    col = C * (mat.get("amb", 0.02) * ao)[:, None]
    for L in lights:
        att, l, dist = L.attenuation(P)
        att = att * visibility(P, L, cave)
        ndl = (N * l).sum(1)
        wrap = np.clip((ndl + 0.03) / 1.03, 0, 1)
        col = col + C * L.col[None, :] * (wrap * att)[:, None]
        h = nrm(l + V)
        ndh = np.clip((N * h).sum(1), 0, 1)
        a = np.maximum(mat["R"], 0.03) ** 2
        den = ndh * ndh * (a * a - 1) + 1
        D = a * a / (math.pi * den * den + 1e-9)
        Fs = 0.04 + 0.96 * (1 - ndv) ** 5
        sp = (D * Fs * mat["S"])[:, None] * L.col[None, :] * (np.clip(ndl, 0, 1) * att)[:, None]
        col = col + np.minimum(sp, 6.0)
        rim = (np.clip(1 - ndv, 0, 1) ** 2.0) * np.clip(-ndl * 0.5 + 0.6, 0, 1) * att * mat.get("rim", 0.45)
        col = col + rim[:, None] * L.col[None, :] * (0.35 + 0.65 * C)
    em = mat.get("EM")
    if em is not None:
        em = np.asarray(em, np.float32)
        col = col + C * (em[:, None] if em.ndim else em) * 6.0
    fv = 1.0 - np.exp(-0.013 * np.maximum(vd - 1.0, 0.0))
    col = col * (1 - fv[:, None]) + np.array([0.006, 0.009, 0.016], np.float32)[None, :] * fv[:, None]
    return col.astype(np.float32)


# ---------------------------------------------------------------- volumetrics


def volumetrics(cam, cave, lights, W, H, density=0.016, res=0.30, steps=24,
                height=4.0, hg_g=0.62, base=(0.004, 0.007, 0.013)):
    sw, sh = max(8, int(W * res)), max(8, int(H * res))
    yy, xx = np.meshgrid((np.arange(sh) + .5) * (H / sh), (np.arange(sw) + .5) * (W / sw), indexing="ij")
    d = cam.rays(xx.ravel(), yy.ravel())
    o = cam.eye[None, :]
    rng = np.random.default_rng(7)
    dt = 30.0 / steps
    jit = rng.random(d.shape[0]).astype(np.float32) * dt
    acc = np.zeros((d.shape[0], 3), np.float32)
    tau = np.zeros(d.shape[0], np.float32)
    for i in range(steps):
        t = 0.3 + i * dt + jit
        p = o + d * t[:, None]
        inside = cave.sdf(p) < 0
        hgt = np.exp(-np.maximum(p[:, 1] - cave.floor_y, 0) / height)
        nz = fbm(p[:, 0] * 0.5, p[:, 1] * 0.5, p[:, 2] * 0.5, 3)
        dens = density * hgt * (0.25 + 1.1 * nz) * inside
        seg = np.zeros((d.shape[0], 3), np.float32)
        for L in lights:
            att, l, dist = L.attenuation(p)
            cos = -(d * l).sum(1)
            hg = (1 - hg_g ** 2) / (4 * math.pi * (1 + hg_g ** 2 - 2 * hg_g * cos) ** 1.5) * 3.2
            seg += (hg * att)[:, None] * L.col[None, :]
        acc += seg * dens[:, None] * dt
        tau += dens * dt * 0.55
    acc += np.asarray(base, np.float32)[None, :]
    tr = np.exp(-tau)
    vol = acc.reshape(sh, sw, 3)
    trv = tr.reshape(sh, sw)
    yi = (np.arange(H) + .5) * (sh / H) - .5
    xi = (np.arange(W) + .5) * (sw / W) - .5
    y0 = np.clip(np.floor(yi).astype(np.int32), 0, sh - 1); y1 = np.clip(y0 + 1, 0, sh - 1)
    x0 = np.clip(np.floor(xi).astype(np.int32), 0, sw - 1); x1 = np.clip(x0 + 1, 0, sw - 1)
    fy3 = np.clip(yi - y0, 0, 1)[:, None, None]; fx3 = np.clip(xi - x0, 0, 1)[None, :, None]
    fy = np.clip(yi - y0, 0, 1)[:, None]; fx = np.clip(xi - x0, 0, 1)[None, :]
    vos = (vol[y0][:, x0] * (1 - fx3) * (1 - fy3) + vol[y0][:, x1] * fx3 * (1 - fy3)
           + vol[y1][:, x0] * (1 - fx3) * fy3 + vol[y1][:, x1] * fx3 * fy3).astype(np.float32)
    trs = (trv[y0][:, x0] * (1 - fx) * (1 - fy) + trv[y0][:, x1] * fx * (1 - fy)
           + trv[y1][:, x0] * (1 - fx) * fy + trv[y1][:, x1] * fx * fy).astype(np.float32)
    return vos, trs


# ---------------------------------------------------------------- post


def aces(x):
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    return np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)


def box(img, r, ax):
    if r < 1:
        return img
    r = int(r); k = 2 * r + 1
    if ax == 0:
        p = np.pad(img, ((r, r), (0, 0), (0, 0)), mode="edge")
        cs = np.cumsum(p, 0, dtype=np.float32)
        cs = np.concatenate([np.zeros_like(cs[:1]), cs], 0)
        return (cs[k:] - cs[:-k]) / k
    p = np.pad(img, ((0, 0), (r, r), (0, 0)), mode="edge")
    cs = np.cumsum(p, 1, dtype=np.float32)
    cs = np.concatenate([np.zeros_like(cs[:, :1]), cs], 1)
    return (cs[:, k:] - cs[:, :-k]) / k


def blur(img, r):
    if r < 1:
        return img
    o = img
    for _ in range(2):
        o = box(o, max(1, r), 0)
        o = box(o, max(1, r), 1)
    return o


def bloom(img, th=0.62, k=0.30, radii=(4, 11, 26)):
    br = np.maximum(img - th, 0)
    acc = np.zeros_like(img); tot = 0.0
    for i, r in enumerate(radii):
        w = 1.0 / (i + 1); acc += blur(br, r) * w; tot += w
    return acc / tot * k


def streak(img, th=0.9, k=0.22, length=70):
    br = np.maximum(img - th, 0)
    xs = np.arange(-length, length + 1, dtype=np.float32)
    ker = np.exp(-(xs ** 2) / (2 * (length * 0.30) ** 2)); ker /= ker.sum()
    pad = np.pad(br, ((0, 0), (length, length), (0, 0)), mode="edge")
    out = np.zeros_like(br)
    for c in range(3):
        out[..., c] = np.convolve(pad[..., c].ravel(), ker, "same").reshape(br.shape[0], -1)[:, :br.shape[1]]
    return out * k


def ca(img, amt=1.0):
    H, W = img.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    s = 1.0 + amt * 0.0032 * d * d
    out = img.copy()
    for c in range(3):
        xs = np.clip((xx - W / 2) * s + W / 2, 0, W - 1).astype(np.int32)
        ys = np.clip((yy - H / 2) * s + H / 2, 0, H - 1).astype(np.int32)
        out[..., c] = img[ys, xs, c]
    return out


_gc = {}


def grain(H, W, seed, amt=0.010):
    key = (H, W)
    if key not in _gc:
        r = np.random.default_rng(5)
        g = r.normal(0, 1, (H // 2 + 2, W // 2 + 2)).astype(np.float32)
        g = np.repeat(np.repeat(g, 2, 0), 2, 1)[:H, :W]
        _gc[key] = g
    r = np.random.default_rng(seed)
    g = np.roll(_gc[key], int(r.integers(0, 60)), axis=1)
    return g * amt


def vignette(H, W, k=0.32):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2)
    return (1 - k * np.clip(r - 0.35, 0, 1) ** 1.5)[..., None]


def auto_exposure(img, hi=0.90, mid=0.105, pct=99.6):
    a = img.reshape(-1, 3).mean(1)
    a = a[np.isfinite(a)]
    lum = np.maximum(a, 1e-6)
    logavg = float(np.exp(np.mean(np.log(lum + 1e-4))))
    e = 0.16 / max(logavg, 1e-5)
    return float(np.clip(e, 0.30, 60.0))


def finish(img, seed=0, exposure=None, bloom_k=0.26, streak_k=0.18,
           ca_amt=1.0, vig_k=0.32, grain_amt=0.009, contrast=1.05, sat=1.05):
    e = auto_exposure(img) if exposure is None else exposure
    x = aces(np.maximum(img, 0) * e)
    x = x + bloom(x, k=bloom_k)
    x = x + streak(x, k=streak_k)
    x = (x - 0.5) * contrast + 0.5
    lum = x.mean(2, keepdims=True)
    x = lum + (x - lum) * sat
    x = x + np.array([0.003, 0.005, 0.010], np.float32)[None, None, :] * (1 - np.clip(x, 0, 1))
    x = np.clip(x, 0, 1)
    x = ca(x, ca_amt)
    x = x * vignette(*x.shape[:2], k=vig_k)
    x = np.clip(x + grain(x.shape[0], x.shape[1], seed, grain_amt)[..., None], 0, 1)
    return x
