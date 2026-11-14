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


def visibility(P, L, cave, steps=7):
    """Can the light actually reach this surface point through the tube?"""
    d = L.pos[None, :] - P
    worst = np.full(len(P), 1e3, np.float32)
    rr = None
    for i in range(1, steps + 1):
        q = P + d * (i / (steps + 1.0))
        th = np.arctan2(q[:, 1] / 0.80, q[:, 0])
        wob = (1.0 + 0.20 * np.sin(3.0 * th + 0.7) + 0.12 * np.sin(5.0 * th + 2.1)
               + 0.06 * np.sin(9.0 * th + 4.4))
        r = np.sqrt(q[:, 0] ** 2 + (q[:, 1] / 0.80) ** 2)
        Rz = cave.radius_at(q[:, 2]) * wob
        worst = np.minimum(worst, np.minimum((Rz - r) / np.maximum(Rz, 1e-3),
                                            (q[:, 1] - cave.floor_y) / 2.4))
    return smoothstep(-0.10, 0.22, worst).astype(np.float32)


# ---------------------------------------------------------------- set


def march_set(cam, cave, W, H, tmax=44.0, steps=40):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = cam.rays(xx.ravel(), yy.ravel())
    o = cam.eye[None, :]
    rng = np.random.default_rng(int(cam.eye[0] * 977) & 0xffff)
    t = 0.25 + rng.random(d.shape[0]).astype(np.float32) * 0.03
    hit = np.zeros(d.shape[0], bool)
    beyond = np.zeros(d.shape[0], bool)
    step = 0.42
    for _ in range(steps):
        p = o + d * t[:, None]
        s = cave.sdf(p)
        now = (~hit) & (~beyond) & (s > 0)
        if now.any():
            lo = np.maximum(t - step, 0.02)
            hi = t.copy()
            for _ in range(5):
                mid = 0.5 * (lo + hi)
                ins = cave.sdf(o + d * mid[:, None]) < 0
                lo = np.where(ins, mid, lo)
                hi = np.where(ins, hi, mid)
            t = np.where(now, lo, t)
            hit |= now
        t += step
        far = (~hit) & (t > tmax)
        beyond |= far
        if (hit | beyond).all():
            break
    P = o + d * t[:, None]
    N = cave.normal(P)
    return dict(P=P.astype(np.float32), N=N.astype(np.float32), t=t.astype(np.float32),
                hit=hit.reshape(H, W), d=d, xx=xx.ravel(), yy=yy.ravel(), W=W, H=H)


def shade_set(hit, cam, cave, lights, exposure=1.0, fog=0.028):
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
    return img * exposure, depth


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


def splat(nd, cam, W, H, zbuf, col, max_taps=40, rad=0.60):
    x, y, z = cam.view(nd["P"])
    ok = z > 0.12
    if ok.sum() < 4:
        return None
    x, y, z = x[ok], y[ok], z[ok]
    col = col[ok]
    sx, sy, inv = cam.to_screen(x, y, z)
    rpx = np.clip(nd["PX"][ok] * cam.f * inv * rad, 0.7, 22.0)
    nb = W * H
    zmin = np.full(nb, 1e9, np.float32)
    f0 = np.floor(sy).astype(np.int32) * W + np.floor(sx).astype(np.int32)
    inb = (f0 >= 0) & (f0 < nb)
    np.minimum.at(zmin, np.where(inb, f0, 0), np.where(inb, z, 1e9))
    nt = np.clip(np.rint(np.pi * rpx * rpx * 1.3), 1, max_taps).astype(np.int32)
    order = np.argsort(nt, kind="stable")
    acc = np.zeros((nb, 3), np.float32)
    wsum = np.zeros(nb, np.float32)
    dsum = np.zeros(nb, np.float32)
    for n in np.unique(nt):
        sel = order[nt[order] == n]
        if sel.size == 0:
            continue
        T = _taps(int(n))[None, :, :] * (rpx[sel][:, None, None] * 0.95)
        tx = sx[sel][:, None] + T[..., 0]
        ty = sy[sel][:, None] + T[..., 1]
        ix = np.floor(tx).astype(np.int32)
        iy = np.floor(ty).astype(np.int32)
        inb2 = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
        fl = np.where(inb2, iy.astype(np.int64) * W + ix.astype(np.int64), 0)
        zr = np.where(inb2, z[sel][:, None], 1e9)
        keep = zr <= zbuf.reshape(-1)[fl] * 1.002 + 2e-3
        ddx = tx - np.floor(tx) - 0.5
        ddy = ty - np.floor(ty) - 0.5
        sw = np.exp(-(ddx * ddx + ddy * ddy) / 0.44).astype(np.float32)
        wgt = (keep.astype(np.float32) * sw / (n * 0.5)).ravel()
        for c in range(3):
            acc[:, c] += np.bincount(fl.ravel(), weights=wgt * np.repeat(col[sel, c], int(n)),
                                     minlength=nb)[:nb].astype(np.float32)
        wsum += np.bincount(fl.ravel(), weights=wgt, minlength=nb)[:nb].astype(np.float32)
        dsum += np.bincount(fl.ravel(), weights=wgt * np.repeat(z[sel], int(n)),
                            minlength=nb)[:nb].astype(np.float32)
    ws = np.maximum(wsum, 1e-6)
    cov = np.clip(wsum / 0.80, 0, 1)
    return dict(col=np.stack([acc[:, 0] / ws, acc[:, 1] / ws, acc[:, 2] / ws], 1).reshape(H, W, 3),
                cov=cov.reshape(H, W), depth=(dsum / ws).reshape(H, W))


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
    acc += np.asarray(base, np.float32)[None, :]
    vol = acc.reshape(sh, sw, 3)
    yi = (np.arange(H) + .5) * (sh / H) - .5
    xi = (np.arange(W) + .5) * (sw / W) - .5
    y0 = np.clip(np.floor(yi).astype(np.int32), 0, sh - 1); y1 = np.clip(y0 + 1, 0, sh - 1)
    x0 = np.clip(np.floor(xi).astype(np.int32), 0, sw - 1); x1 = np.clip(x0 + 1, 0, sw - 1)
    fy = np.clip(yi - y0, 0, 1)[:, None, None]; fx = np.clip(xi - x0, 0, 1)[None, :, None]
    return (vol[y0][:, x0] * (1 - fx) * (1 - fy) + vol[y0][:, x1] * fx * (1 - fy)
            + vol[y1][:, x0] * (1 - fx) * fy + vol[y1][:, x1] * fx * fy).astype(np.float32)


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
    hv = float(np.percentile(a, pct)); mv = float(np.percentile(a, 62))
    e1 = hi / hv if hv > 1e-7 else 40.0
    e2 = mid / mv if mv > 1e-7 else 40.0
    return float(np.clip(min(e1, e2), 0.4, 90.0))


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
