#!/usr/bin/env python3
"""
MONARCH — cave bear film engine (numpy only).

Real 3D: perspective projection with a physical film-back, per-point deferred
shading, single-sample scatter + push-pull depth fill, 2.5D volumetric light
shafts from mist point clouds, bloom/streak/CA/vignette/grain/ACES.

Design constraint: 2 cores, 3 GB. So: points, not triangles; vectorised, not
per-pixel loops; scatter at full res, fill holes with a depth pyramid.
"""
from __future__ import annotations

import math

import numpy as np

# --------------------------------------------------------------------- scalar helpers


def nrm(v):
    v = np.asarray(v, np.float32)
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, 1e-8)


def look_at(eye, target, up=(0.0, 1.0, 0.0)):
    eye = np.asarray(eye, np.float32)
    target = np.asarray(target, np.float32)
    f = nrm(target - eye)
    up = np.asarray(up, np.float32)
    if abs(float(np.dot(f, up))) > 0.999:
        up = np.array([0.0, 0.0, 1.0], np.float32)
    r = nrm(np.cross(f, up))
    u = np.cross(r, f)
    return r, u, f


def smoothstep(a, b, x):
    t = np.clip((np.asarray(x, np.float32) - a) / (b - a if b != a else 1e-8), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def clamp01(x):
    return np.clip(x, 0.0, 1.0)


# --------------------------------------------------------------------- noise

_rng0 = np.random.default_rng(20261105)
_PG = _rng0.random((64, 64, 64), dtype=np.float32)


def vnoise(x, y, z):
    x = np.asarray(x, np.float32)
    y = np.asarray(y, np.float32)
    z = np.asarray(z, np.float32)
    xf0 = np.floor(x)
    yf0 = np.floor(y)
    zf0 = np.floor(z)
    xi = xf0.astype(np.int32) & 63
    yi = yf0.astype(np.int32) & 63
    zi = zf0.astype(np.int32) & 63
    fx = x - xf0
    fy = y - yf0
    fz = z - zf0
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    fz = fz * fz * (3 - 2 * fz)
    x1 = (xi + 1) & 63
    y1 = (yi + 1) & 63
    z1 = (zi + 1) & 63
    c000 = _PG[xi, yi, zi]
    c100 = _PG[x1, yi, zi]
    c010 = _PG[xi, y1, zi]
    c110 = _PG[x1, y1, zi]
    c001 = _PG[xi, yi, z1]
    c101 = _PG[x1, yi, z1]
    c011 = _PG[xi, y1, z1]
    c111 = _PG[x1, y1, z1]
    c00 = c000 + (c100 - c000) * fx
    c10 = c010 + (c110 - c010) * fx
    c01 = c001 + (c101 - c001) * fx
    c11 = c011 + (c111 - c011) * fx
    c0 = c00 + (c10 - c00) * fy
    c1 = c01 + (c11 - c01) * fy
    return c0 + (c1 - c0) * fz


def fbm(x, y, z, oct=4, gain=0.5, lac=2.03):
    tot = np.zeros_like(np.asarray(x, np.float32))
    amp, fr = 1.0, 1.0
    for _ in range(oct):
        tot = tot + amp * vnoise(x * fr, y * fr, z * fr)
        amp *= gain
        fr *= lac
    return tot


# --------------------------------------------------------------------- node container


def node(P, N, C, S=0.05, R=0.8, PX=0.02, AO=None, EM=0.0, tag=""):
    P = np.asarray(P, np.float32)
    n = P.shape[0]
    N = np.asarray(N, np.float32)
    if N.ndim == 1:
        N = np.repeat(N[None, :], n, 0)
    C = np.asarray(C, np.float32)
    if C.ndim == 1:
        C = np.repeat(C[None, :], n, 0)
    d = {
        "P": P, "N": N, "C": C,
        "S": (np.full(n, S, np.float32) if np.isscalar(S) else np.asarray(S, np.float32)),
        "R": (np.full(n, R, np.float32) if np.isscalar(R) else np.asarray(R, np.float32)),
        "PX": (np.full(n, PX, np.float32) if np.isscalar(PX) else np.asarray(PX, np.float32)),
        "AO": (np.ones(n, np.float32) if AO is None else np.asarray(AO, np.float32)),
        "EM": (np.full(n, float(EM), np.float32) if np.isscalar(EM) else np.asarray(EM, np.float32)),
        "tag": tag,
    }
    return d


def merge(nodes):
    keys = ("P", "N", "C", "S", "R", "PX", "AO", "EM")
    out = {k: np.concatenate([n[k] for n in nodes], 0) for k in keys}
    out["tag"] = "merged"
    return out


def offset(P, d):
    return P + np.asarray(d, np.float32)


def rotY(P, a, pivot=(0, 0, 0)):
    p = np.asarray(pivot, np.float32)
    q = P - p
    c, s = math.cos(a), math.sin(a)
    x = q[:, 0] * c + q[:, 2] * s
    z = -q[:, 0] * s + q[:, 2] * c
    return np.stack([x, q[:, 1], z], 1) + p


def rotX(P, a, pivot=(0, 0, 0)):
    p = np.asarray(pivot, np.float32)
    q = P - p
    c, s = math.cos(a), math.sin(a)
    y = q[:, 1] * c - q[:, 2] * s
    z = q[:, 1] * s + q[:, 2] * c
    return np.stack([q[:, 0], y, z], 1) + p


def rotZ(P, a, pivot=(0, 0, 0)):
    p = np.asarray(pivot, np.float32)
    q = P - p
    c, s = math.cos(a), math.sin(a)
    x = q[:, 0] * c - q[:, 1] * s
    y = q[:, 0] * s + q[:, 1] * c
    return np.stack([x, y, q[:, 2]], 1) + p


def tangent_frame(N):
    """Build two tangents for a normal buffer (for surface detail)."""
    up = np.where(np.abs(N[:, 1:2]) > 0.9, np.array([[0, 0, 1]], np.float32),
                  np.array([[0, 1, 0]], np.float32))
    t = nrm(np.cross(up, N))
    b = np.cross(N, t)
    return t, b


# --------------------------------------------------------------------- camera


class Cam:
    def __init__(self, W, H, pos, target, up=(0, 1, 0), fov=48.0, roll=0.0, shift=(0.0, 0.0)):
        self.W, self.H = int(W), int(H)
        self.pos = np.asarray(pos, np.float32)
        self.R, self.U, self.F = look_at(pos, target, up)
        if roll:
            c, s = math.cos(roll), math.sin(roll)
            R2 = self.R * c + self.U * s
            U2 = -self.R * s + self.U * c
            self.R, self.U = R2.astype(np.float32), U2.astype(np.float32)
        self.f = 0.5 * self.W / math.tan(math.radians(fov) * 0.5)
        self.cx = self.W * 0.5 + shift[0] * self.W
        self.cy = self.H * 0.5 + shift[1] * self.H

    def view(self, P):
        d = P - self.pos
        return d @ self.R, d @ self.U, d @ self.F

    def screen(self, x, y, z):
        inv = 1.0 / np.maximum(z, 1e-4)
        return self.cx + self.f * x * inv, self.cy - self.f * y * inv, inv

    def dir_of(self, sx, sy):
        x = (np.asarray(sx, np.float32) - self.cx) / self.f
        y = -(np.asarray(sy, np.float32) - self.cy) / self.f
        return nrm(self.R[None, :] * x[:, None] + self.U[None, :] * y[:, None] + self.F[None, :])


# --------------------------------------------------------------------- shading


def shade_points(nd, cam, lights, amb=(0.010, 0.013, 0.019), amb_up=0.05,
                 fog=0.045, fog_col=(0.008, 0.011, 0.018), rim_amt=0.55, vis=None):
    """
    Per-point deferred shading -> (rgb (N,3), dist (N,), emit (N,)).
    lights: list of dict(pos=vec3, col=vec3, pow=float, radius=float,
                         spot_dir=vec3|None, spot_cos=float)
    """
    P = nd["P"]
    N = nd["N"]
    C = nd["C"]
    V = cam.pos[None, :] - P
    vd = np.linalg.norm(V, axis=1) + 1e-6
    V = V / vd[:, None]

    col = np.zeros_like(C)
    # ambient (hemisphere + cavity)
    ambv = np.asarray(amb, np.float32)[None, :]
    up = (N[:, 1:2] * 0.5 + 0.5)
    col += C * ambv * (0.5 + amb_up * up * 8.0) * nd["AO"][:, None]

    for li, L in enumerate(lights):
        vis_l = None if vis is None else vis[li]
        lv = np.asarray(L["pos"], np.float32)[None, :] - P
        dist = np.linalg.norm(lv, axis=1) + 1e-6
        l = lv / dist[:, None]
        ndl = (N * l).sum(1)
        # soft wrapped diffuse: rock/skin read better with a wrap term
        diff = np.clip((ndl + 0.30) / 1.30, 0.0, 1.0)
        att = L["pow"] / (dist * dist + 0.35)
        if vis_l is not None:
            att = att * vis_l
        if L.get("spot_dir") is not None:
            sd = nrm(np.asarray(L["spot_dir"], np.float32))
            cosang = (-l @ sd)
            att = att * smoothstep(L.get("spot_cos", 0.5), 1.0, cosang)
        key = att * diff
        col += C * np.asarray(L["col"], np.float32)[None, :] * key[:, None]

        # GGX specular
        h = nrm(l + V)
        ndh = np.clip((N * h).sum(1), 0.0, 1.0)
        ndv = np.clip((N * V).sum(1), 1e-3, 1.0)
        a = np.maximum(nd["R"], 0.03) ** 2
        den = ndh * ndh * (a * a - 1.0) + 1.0
        D = a * a / (math.pi * den * den + 1e-8)
        k = a * 0.5
        G = (ndv / (ndv * (1 - k) + k)) * (np.clip(ndl, 0, 1) / (np.clip(ndl, 0, 1) * (1 - k) + k))
        F = 0.05 + 0.95 * (1.0 - ndv) ** 5
        sp = (D * G * F * nd["S"])[:, None] * np.asarray(L["col"], np.float32)[None, :] * (np.clip(ndl, 0, 1) * att)[:, None]
        col += np.minimum(sp, 6.0)

        # rim: backlight wraps the silhouette
        rim = (np.clip(1.0 - ndv, 0, 1) ** 2.4) * clamp01(-ndl * 0.6 + 0.55) * att * rim_amt
        col += rim[:, None] * np.asarray(L["col"], np.float32)[None, :] * (0.35 + 0.65 * C)

    col += C * nd["EM"][:, None]
    # aerial perspective
    fv = (1.0 - np.exp(-fog * np.maximum(vd - 1.2, 0.0)))
    col = col * (1.0 - fv[:, None]) + np.asarray(fog_col, np.float32)[None, :] * fv[:, None] * 1.0
    return col, vd, nd["EM"]


# --------------------------------------------------------------------- raster


def _bincount_acc(idx, w, n, shape):
    return np.bincount(idx, weights=w, minlength=n).astype(np.float32).reshape(shape)


_SPLASH_CACHE = {}


def _disc_taps(n):
    """Sunflower disc of n unit-radius offsets (constant flux per splat)."""
    if n in _SPLASH_CACHE:
        return _SPLASH_CACHE[n]
    if n <= 1:
        out = np.zeros((1, 2), np.float32)
    else:
        k = np.arange(n, dtype=np.float32) + 0.5
        r = np.sqrt(k / n)
        a = k * 2.39996323
        out = np.stack([np.cos(a) * r, np.sin(a) * r], 1).astype(np.float32)
    _SPLASH_CACHE[n] = out
    return out


def render_buffer(nd, cam, lights, W, H, znear=0.10, bg=None, exposure_scale=1.0, **shade_kw):
    """Disc-splat raster with per-point adaptive radius, single-sample resolve.

    Each point is splatted over a disc whose radius is its projected world
    size, with a constant sample count per splat so flux is right; the depth
    test keeps the nearest surface; holes are filled by progressive blur.
    """
    col, dist, emit = shade_points(nd, cam, lights, **shade_kw)
    x, y, z = cam.view(nd["P"])
    ok = z > znear
    if ok.sum() < 10:
        return np.zeros((H, W, 3), np.float32), None, None
    x, y, z = x[ok].astype(np.float32), y[ok].astype(np.float32), z[ok].astype(np.float32)
    col, dist, emit = col[ok], dist[ok], emit[ok]
    px_world = nd["PX"][ok] if "PX" in nd else np.full(len(x), 0.02, np.float32)
    sx, sy, inv = cam.screen(x, y, z)
    rpx = np.clip(px_world * cam.f * inv * 0.62, 0.70, 7.0)

    # bucket by tap count; taps scale with the splat area
    nb = W * H
    zmin = np.full(nb, 1e9, np.float32)
    step = max(1, len(x) // 340000)
    for k in range(0, len(x), step):
        sl = slice(k, min(k + step, len(x)))
        zz = z[sl]
        pp = np.floor(sy[sl]).astype(np.int32) * W + np.floor(sx[sl]).astype(np.int32)
        pp = np.where((pp >= 0) & (pp < nb), pp, 0)
        np.minimum.at(zmin, pp, zz)
    # visible-own pass
    zz_all = np.empty(len(x), np.float32)

    ntaps = np.clip(np.rint(np.pi * rpx * rpx * 1.15), 1, 26).astype(np.int32)
    order = np.argsort(ntaps, kind="stable")
    acc = np.zeros((nb, 3), np.float32)
    wsum = np.zeros(nb, np.float32)
    dsum = np.zeros(nb, np.float32)
    esum = np.zeros(nb, np.float32)
    for n_t in np.unique(ntaps):
        idxs = order[ntaps[order] == n_t]
        if len(idxs) == 0:
            continue
        taps = _disc_taps(int(n_t))[None, :, :] * (rpx[idxs][:, None, None] * 0.55)
        tx = sx[idxs][:, None] + taps[..., 0]
        ty = sy[idxs][:, None] + taps[..., 1]
        pxx = np.floor(tx).astype(np.int32)
        pyy = np.floor(ty).astype(np.int32)
        inb = (pxx >= 0) & (pxx < W) & (pyy >= 0) & (pyy < H)
        flat = (pyy.astype(np.int64) * W + pxx.astype(np.int64))
        flat = np.where(inb, flat, 0)
        zr = np.where(inb, z[idxs][:, None], 1e9)
        own = (zr <= zmin[flat] * 1.02 + 2e-3).astype(np.float32)
        ddx = (tx - np.floor(tx) - 0.5)
        ddy = (ty - np.floor(ty) - 0.5)
        soft = np.exp(-(ddx * ddx + ddy * ddy) / 0.42).astype(np.float32)
        wgt = own * soft / (n_t * 0.7)
        for c in range(3):
            acc[:, c] += np.bincount(flat.ravel(), weights=(wgt * col[idxs][:, c][:, None]).ravel(), minlength=nb).astype(np.float32)
        wsum += np.bincount(flat.ravel(), weights=wgt.ravel(), minlength=nb).astype(np.float32)
        dsum += np.bincount(flat.ravel(), weights=(wgt * dist[idxs][:, None]).ravel(), minlength=nb).astype(np.float32)
        esum += np.bincount(flat.ravel(), weights=(wgt * emit[idxs][:, None]).ravel(), minlength=nb).astype(np.float32)

    ws = np.maximum(wsum, 1e-6)
    out = np.empty((H, W, 6), np.float32)
    out[..., 0] = (acc[:, 0] / ws).reshape(H, W)
    out[..., 1] = (acc[:, 1] / ws).reshape(H, W)
    out[..., 2] = (acc[:, 2] / ws).reshape(H, W)
    out[..., 3] = (dsum / ws).reshape(H, W)
    out[..., 4] = wsum.reshape(H, W)
    out[..., 5] = (esum / ws).reshape(H, W)
    mask = (wsum > 1e-5).reshape(H, W)
    if bg is None:
        bgc = np.array([0.008, 0.010, 0.015], np.float32)
    else:
        bgc = np.asarray(bg, np.float32)
    if bg is not None and np.asarray(bg).ndim == 3:
        plate = np.asarray(bg, np.float32)
        hole = (~mask).astype(np.float32)[..., None]
        hole = gauss(hole[..., :3], 1)
        filled = push_pull(out, mask, np.array([0.0, 0.0, 0.0], np.float32))
        comp = filled[..., :3] * (1 - hole[..., :3] if hole.shape[-1] == 3 else 1 - hole) + plate * hole[..., :3]
        # also darken the plate by depth so the mouth doesn't cut out
        return comp, filled[..., 3], filled[..., 5]
    filled = push_pull(out, mask, bgc)
    filled[..., 4] = mask.astype(np.float32)
    return filled[..., :3], filled[..., 3], filled[..., 5]


def _dilate(src, mask, iters=24):
    """Nearest-known-pixel fill by repeated 8-neighbour max-propagation."""
    val = src.copy()
    known = mask.copy()
    for _ in range(iters):
        if known.all():
            break
        v = val.copy()
        k = known.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            vs = np.roll(np.roll(v, dy, axis=0), dx, axis=1)
            ks = np.roll(np.roll(k, dy, axis=0), dx, axis=1)
            take = (~known) & ks
            val[take] = vs[take]
            known = known | take
    return val, known


def _down(x, f):
    H, W = x.shape[:2]
    Hh, Ww = (H // f) * f, (W // f) * f
    y = x[:Hh, :Ww]
    if y.ndim == 2:
        return y.reshape(Hh // f, f, Ww // f, f).mean(axis=(1, 3))
    return y.reshape(Hh // f, f, Ww // f, f, y.shape[2]).mean(axis=(1, 3))


def push_pull(buf, mask, bgc, f=4, iters=40):
    """Fast hole fill: propagate at 1/f resolution, upsample, composite.

    The unfilled region is almost always soft background, so doing the
    propagation coarse costs nothing visually and saves an order of magnitude.
    """
    out = buf.copy()
    m = mask.astype(np.float32)
    if m.all():
        return out
    rgb = buf[..., :3]
    # weighted downsample (only known pixels contribute)
    wr = _down(rgb * m[..., None], f)
    wm = _down(m, f)
    small = np.where(wm[..., None] > 1e-4, wr / np.maximum(wm, 1e-4)[..., None], 0.0)
    known = wm > 1e-4
    val = small.copy()
    for _ in range(iters):
        if known.all():
            break
        v = val.copy()
        k = known.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            vs = np.roll(np.roll(v, dy, axis=0), dx, axis=1)
            ks = np.roll(np.roll(k, dy, axis=0), dx, axis=1)
            take = (~known) & ks
            val[take] = vs[take]
            known = known | take
    if not known.all():
        val[~known] = np.asarray(bgc, np.float32)[None, :]
    val = gauss(val, 3)
    up = upsample(val, buf.shape[0], buf.shape[1])
    mix = ~mask
    out[..., 0][mix] = up[..., 0][mix]
    out[..., 1][mix] = up[..., 1][mix]
    out[..., 2][mix] = up[..., 2][mix]
    out[..., 3][mix] = 60.0
    out[..., 5][mix] = 0.0
    return out


# --------------------------------------------------------------------- volumetrics


def volumetric(cam, W, H, fog_cfg, lights, res=(0.25, 0.25)):
    """
    Raymarched single-scatter through an exponential fog with point lights.
    Rendered at 1/4 res and upsampled — this is the shaft/god-ray layer.
    fog_cfg: dict(density=..., height=..., col=(...), ground_y=..., amb=...)
    """
    sw = max(8, int(W * res[0]))
    sh = max(8, int(H * res[1]))
    yy, xx = np.meshgrid((np.arange(sh) + 0.5) * (H / sh), (np.arange(sw) + 0.5) * (W / sw), indexing="ij")
    d = cam.dir_of(xx.ravel(), yy.ravel())
    t = np.linspace(0.4, 26.0, 30, dtype=np.float32)
    acc = np.zeros((d.shape[0], 3), np.float32)
    dens_cfg = fog_cfg
    for i in range(len(t)):
        p = cam.pos[None, :] + d * t[i]
        # height-dependent density + 3D noise for wispy shafts
        hgt = np.exp(-np.maximum(p[:, 1] - dens_cfg.get("ground_y", -1.5), 0) / dens_cfg.get("height", 3.0))
        nz = fbm(p[:, 0] * 0.55, p[:, 1] * 0.55, p[:, 2] * 0.55, 3)
        dens = dens_cfg["density"] * hgt * (0.35 + 0.9 * nz)
        seg = np.zeros((d.shape[0], 3), np.float32)
        for L in lights:
            lv = np.asarray(L["pos"], np.float32)[None, :] - p
            dist = np.linalg.norm(lv, axis=1) + 1e-6
            l = lv / dist[:, None]
            # HG phase
            cos = -(d * l).sum(1)
            g = 0.55
            hg = (1 - g * g) / (4 * math.pi * (1 + g * g - 2 * g * cos) ** 1.5)
            att = L["pow"] / (dist * dist + 0.25)
            if L.get("spot_dir") is not None:
                sd = nrm(np.asarray(L["spot_dir"], np.float32))
                att = att * smoothstep(L.get("spot_cos", 0.5), 1.0, -l @ sd)
            seg += (hg * att)[:, None] * np.asarray(L["col"], np.float32)[None, :]
        acc += seg * dens[:, None] * (t[1] - t[0])
    acc += np.asarray(dens_cfg.get("col", (0.004, 0.006, 0.010)), np.float32)[None, :] * 0.6
    vol = acc.reshape(sh, sw, 3)
    return upsample(vol, H, W)


def upsample(img, H, W):
    h, w = img.shape[:2]
    yi = (np.arange(H, dtype=np.float32) + 0.5) * (h / H) - 0.5
    xi = (np.arange(W, dtype=np.float32) + 0.5) * (w / W) - 0.5
    y0 = np.clip(np.floor(yi).astype(np.int32), 0, h - 1)
    x0 = np.clip(np.floor(xi).astype(np.int32), 0, w - 1)
    y1 = np.clip(y0 + 1, 0, h - 1)
    x1 = np.clip(x0 + 1, 0, w - 1)
    fy = np.clip(yi - y0, 0, 1)[:, None]
    fx = np.clip(xi - x0, 0, 1)[None, :]
    a = img[y0][:, x0]
    b = img[y0][:, x1]
    c = img[y1][:, x0]
    d = img[y1][:, x1]
    if img.ndim == 3:
        fy = fy[..., None]
        fx = fx[..., None]
    return (a * (1 - fx) * (1 - fy) + b * fx * (1 - fy) + c * (1 - fx) * fy + d * fx * fy).astype(np.float32)


# --------------------------------------------------------------------- post


def aces(x):
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    return clamp01((x * (a * x + b)) / (x * (c * x + d) + e))


def box_blur(img, r, axis):
    if r < 1:
        return img
    r = int(r)
    k = 2 * r + 1
    if axis == 0:
        p = np.pad(img, ((r, r), (0, 0)) + ((0, 0),) * (img.ndim - 2), mode="edge")
        cs = np.cumsum(p, axis=0, dtype=np.float32)
        cs = np.concatenate([np.zeros_like(cs[:1]), cs], 0)
        return (cs[k:] - cs[:-k]) / k
    p = np.pad(img, ((0, 0), (r, r)) + ((0, 0),) * (img.ndim - 2), mode="edge")
    cs = np.cumsum(p, axis=1, dtype=np.float32)
    cs = np.concatenate([np.zeros_like(cs[:, :1]), cs], 1)
    return (cs[:, k:] - cs[:, :-k]) / k


def gauss(img, r):
    if r < 1:
        return img
    o = img
    for _ in range(3):
        o = box_blur(o, max(1, r // 2), 0)
        o = box_blur(o, max(1, r // 2), 1)
    return o


def bloom(img, thresh=0.78, strength=0.30, radii=(4, 12, 30)):
    br = np.maximum(img - thresh, 0.0)
    acc = np.zeros_like(img)
    tot = 0.0
    for i, r in enumerate(radii):
        w = 1.0 / (i + 1)
        acc += gauss(br, r) * w
        tot += w
    return acc / max(tot, 1e-6) * strength


def streak(img, thresh=1.1, strength=0.55, length=90, tilt=0.0):
    """Anamorphic streak: horizontal (optionally tilted) light smear."""
    br = np.maximum(img - thresh, 0.0)
    lum = br.mean(2, keepdims=True)
    br = br * (lum > 0)
    if abs(tilt) > 1e-3:
        pass
    k = np.zeros((1, length * 2 + 1, 1), np.float32)
    xs = np.arange(-length, length + 1, dtype=np.float32)
    k[0, :, 0] = np.exp(-(xs ** 2) / (2 * (length * 0.32) ** 2)).astype(np.float32)
    k /= k.sum()
    pad = np.pad(br, ((0, 0), (length, length), (0, 0)), mode="edge")
    out = np.zeros_like(br)
    for c in range(3):
        out[..., c] = np.convolve(pad[..., c].ravel(), k.ravel(), "same").reshape(br.shape[0], -1)[:, :br.shape[1]]
    return out * strength


def chroma_ab(img, amt=1.2):
    if amt <= 0:
        return img
    H, W = img.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    s = 1.0 + amt * 0.004 * d * d
    out = img.copy()
    for c, k in enumerate((s * 1.0, s, s * 0.998)):
        xs = np.clip((xx - W / 2) * k + W / 2, 0, W - 1).astype(np.int32)
        ys = np.clip((yy - H / 2) * k + H / 2, 0, H - 1).astype(np.int32)
        out[..., c] = img[ys, xs, c]
    return out


_grain_cache = {}


def grain(H, W, seed, amount=0.014, size=1.6):
    key = (H, W, size)
    if key not in _grain_cache:
        rng = np.random.default_rng(9182)
        base = rng.normal(0, 1, (H // 2 + 2, W // 2 + 2)).astype(np.float32)
        big = upsample(base[..., None], H, W)[..., 0]
        _grain_cache[key] = big
    rng = np.random.default_rng(seed)
    off = rng.integers(0, 64)
    g = np.roll(_grain_cache[key], off * 3, axis=1)
    g = np.roll(g, off * 2, axis=0)
    return g * amount


def vignette(H, W, amount=0.30):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    v = 1.0 - amount * clamp01(r - 0.35) ** 1.6
    return v[..., None]


def filmic(x, exposure=1.0, shoulder=0.62):
    """Linear -> display: exposure, ACES-ish tonemap, gentle filmic shoulder."""
    x = np.maximum(x, 0.0) * exposure
    return aces(x)


def finish(img, frame_seed=0, exposure=1.0, bloom_amt=0.22, streak_amt=0.16,
           ca=1.2, vig=0.34, grain_amt=0.012, contrast=1.05, lift=(0.004, 0.006, 0.010)):
    x = filmic(img, exposure)
    x = x + bloom(x, strength=bloom_amt)
    x = x + streak(x, strength=streak_amt)
    # contrast + film lift/saturation
    x = (x - 0.5) * contrast + 0.5
    x = x + np.asarray(lift, np.float32)[None, None, :] * (1.0 - x)
    lum = x.mean(2, keepdims=True)
    x = lum + (x - lum) * 1.08
    x = clamp01(x)
    x = chroma_ab(x, ca)
    x = x * vignette(*x.shape[:2], amount=vig)
    x = x + grain(x.shape[0], x.shape[1], frame_seed, grain_amt)[..., None]
    return clamp01(x)


def srgb(x):
    x = clamp01(x)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def to_u8(img_linear_or_display, display=True):
    v = clamp01(img_linear_or_display)
    if display:
        v = srgb(v)
    return (v * 255.0 + 0.5).astype(np.uint8)
