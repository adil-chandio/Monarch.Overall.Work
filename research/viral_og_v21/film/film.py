#!/usr/bin/env python3
"""
MONARCH film renderer — hybrid: analytic raymarched background + splat heroes.

Why: a point cloud cannot cover a 1080p frame solidly without hundreds of
thousands of taps per frame. So the set is real geometry:

  * cave tube and floor are an implicit surface  F(p) = min(r - R(z), y - yfloor)
    intersected by marching each pixel ray, then refined by bisection. Rock
    detail comes from bump-mapped fbm evaluated at the hit, which is where the
    eye looks for it, and costs one noise call instead of a displaced mesh.
  * the exterior is a procedurally lit sky plate, so rays that leave the mouth
    see weather instead of a void.
  * the bear, skulls and props are shaded splats, depth-tested against the
    background depth buffer, with adaptive soft taps so hero surfaces are solid.

Everything is numpy, everything is vectorised, everything is deterministic.
"""
from __future__ import annotations

import math

import numpy as np

from engine import (Cam, nrm, smoothstep, clamp01, fbm, vnoise, lerp, gauss,
                    box_blur, upsample, bloom, streak, chroma_ab, grain,
                    vignette, aces, srgb, to_u8, _disc_taps, shade_points)

# ============================================================== cave profile


def tube_R(z, length, radius, wob=1.0):
    V = np.clip(z / length + 0.5, -0.4, 1.6)
    wide = (1.0 + 0.30 * np.sin(V * math.pi * 2.2 + 0.5)
            + 0.16 * np.sin(V * math.pi * 5.7 + 1.7)
            + 0.10 * np.sin(V * math.pi * 11.3 + 4.2))
    flare = 1.0 + 0.55 * smoothstep(0.80, 1.02, V) ** 1.6
    flare = flare * (1.0 - 0.18 * smoothstep(0.955, 1.02, V))
    return radius * wide * flare * wob


def tube_F(p, length, radius, yfloor=-2.45):
    r = np.sqrt(p[..., 0] ** 2 + (p[..., 1] / 0.87) ** 2)
    ft = r - tube_R(p[..., 2], length, radius)
    ff = p[..., 1] - yfloor
    # outside the mouth the tube is gone
    open_ = p[..., 2] > length * 0.5
    ft = np.where(open_, -1e3, ft)
    # behind the closed end it is rock
    ft = np.where(p[..., 2] < -length * 0.5, 1e3, ft)
    return np.minimum(ft, ff)


def tube_grad(p, length, radius, eps=0.02):
    gx = (tube_F(p + np.array([eps, 0, 0], np.float32), length, radius)
          - tube_F(p - np.array([eps, 0, 0], np.float32), length, radius))
    gy = (tube_F(p + np.array([0, eps, 0], np.float32), length, radius)
          - tube_F(p - np.array([0, eps, 0], np.float32), length, radius))
    gz = (tube_F(p + np.array([0, 0, eps], np.float32), length, radius)
          - tube_F(p - np.array([0, 0, eps], np.float32), length, radius))
    return nrm(np.stack([gx, gy, gz], -1))


# ============================================================== sky


def sky(cam, W, H, seed=7, snow=520, dusk=1.0):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = xx / W
    v = yy / H
    horizon = 0.52 + 0.06 * np.sin(u * 3.4 + 0.6)
    t = np.clip((v - horizon) / 0.60, 0, 1)
    top = np.array([0.035, 0.085, 0.210], np.float32) * dusk
    mid = np.array([0.150, 0.235, 0.380], np.float32) * dusk
    low = np.array([0.480, 0.400, 0.330], np.float32) * dusk
    img = lerp(mid[None, None, :], top[None, None, :], (t ** 0.85)[..., None])
    below = np.clip((horizon - v) / 0.09, 0, 1)[..., None]
    img = img * (1 - below) + low[None, None, :] * below * 0.60
    cl = fbm(u * 4.5 + 2.0, v * 8.0, 1.3, 4)
    img = img * (1.0 + 0.40 * (cl - 0.5)[..., None])
    # ridge line
    ridge = (horizon + 0.035
             + 0.028 * np.sin(u * 9.0 + 1.1)
             + 0.014 * np.sin(u * 23.0 + 0.3)
             + 0.040 * (fbm(u * 14.0, 2.2, 6.1, 4) - 0.5))
    m = (v > ridge)[..., None]
    land = np.array([0.020, 0.026, 0.034], np.float32)[None, None, :] * (
        0.75 + 0.70 * fbm(u * 26, v * 26, 3.0, 3)[..., None])
    img = img * (1 - m) + land * m
    # low glow at the ridge
    gy = ridge.mean() - 0.02
    r2 = ((u - 0.70) * 1.5) ** 2 + (v - gy) ** 2
    img = img + np.exp(-r2 / 0.008)[..., None] * np.array([0.55, 0.44, 0.34], np.float32) * 0.45
    if snow:
        n = snow
        sx = rng.random(n) * W
        sy = rng.random(n) * H
        sz = rng.random(n)
        rad = (0.6 + sz * 1.4).astype(np.int32)
        for i in range(n):
            y0 = int(max(0, sy[i] - rad[i])); y1 = int(min(H, sy[i] + rad[i] + 1))
            x0 = int(max(0, sx[i] - rad[i])); x1 = int(min(W, sx[i] + rad[i] + 1))
            if y1 <= y0 or x1 <= x0:
                continue
            img[y0:y1, x0:x1] += 0.50 * (0.35 + 0.65 * sz[i])
    return img.astype(np.float32)


# ============================================================== background march


def march_bg(cam, W, H, length, radius, yfloor=-2.45, tmax=46.0, steps=44):
    """Per-pixel ray march of the cave implicit surface. Returns hit data."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = cam.dir_of(xx.ravel(), yy.ravel())
    o = cam.pos[None, :]
    inside = tube_F(o, length, radius, yfloor) < 0
    t = np.full(d.shape[0], 0.12, np.float32)
    hit = np.zeros(d.shape[0], bool)
    sky_mask = np.zeros(d.shape[0], bool)
    # jittered start to avoid banding
    rng = np.random.default_rng(123)
    t = t + rng.random(d.shape[0]).astype(np.float32) * 0.05
    step = np.full(d.shape[0], 0.34, np.float32)
    cone_r = np.zeros(d.shape[0], np.float32)
    for i in range(steps):
        p = o + d * t[:, None]
        F = tube_F(p, length, radius, yfloor)
        # how wide is the bore here, and how far off-axis is the ray
        rr = np.sqrt(p[:, 0] ** 2 + (p[:, 1] / 0.87) ** 2)
        avail = np.maximum(tube_R(p[:, 2], length, radius) - rr, 0.0)
        cone_r = np.maximum(cone_r, np.where(hit, 0.0, avail * 0.55))
        out_now = (~hit) & (F > 0)
        if out_now.any():
            # bisect back to the surface
            lo = np.maximum(t - step, 0.0)
            hi = t.copy()
            for _ in range(6):
                mid = 0.5 * (lo + hi)
                pm = o + d * mid[:, None]
                inside_m = tube_F(pm, length, radius, yfloor) < 0
                lo = np.where(inside_m, mid, lo)
                hi = np.where(inside_m, hi, mid)
            t = np.where(out_now, lo, t)
            hit |= out_now
        past = (~hit) & (t > tmax)
        sky_mask |= past
        t = t + step
        if (hit | past).all():
            break
    # sky rays: give them a large depth
    t = np.where(hit, t, np.minimum(t, tmax))
    P = o + d * t[:, None]
    N = tube_grad(P, length, radius)
    depth = t
    return dict(P=P, N=N, depth=depth, hit=hit.reshape(H, W), cone_r=cone_r.reshape(H, W),
                sky=sky_mask.reshape(H, W), dirs=d, W=W, H=H,
                px=xx.reshape(-1), py=yy.reshape(-1))


# ============================================================== background shading


def tube_vis(P, Lpos, length, radius, yfloor=-2.45, steps=9, soft=0.22):
    """Fraction of the light at Lpos that reaches P through the tube."""
    P = np.asarray(P, np.float32)
    L = np.asarray(Lpos, np.float32)
    d = L[None, :] - P
    worst = np.full(len(P), 1e3, np.float32)
    for i in range(1, steps + 1):
        t = i / (steps + 1.0)
        p = P + d * t
        r = np.sqrt(p[:, 0] ** 2 + (p[:, 1] / 0.87) ** 2)
        Rz = tube_R(p[:, 2], length, radius)
        c = (Rz - r) / np.maximum(Rz, 1e-3)
        # floor clearance
        cf = (p[:, 1] - yfloor) / 2.5
        worst = np.minimum(worst, np.minimum(c, cf))
    # rays that pass out the mouth are unoccluded
    past = (P + d) [:, 2] > length * 0.5 - 0.5
    v = smoothstep(-soft, soft, worst)
    return np.where(past, np.maximum(v, 0.9), v).astype(np.float32)


def shade_bg(hg, cam, lights, length, radius, yfloor=-2.45, fog=0.030,
             fog_col=(0.008, 0.012, 0.020), amb=(0.006, 0.008, 0.013),
             bump=1.0, sky_img=None):
    P = hg["P"]
    N = hg["N"]
    d = hg["depth"]
    inside = hg["hit"].reshape(-1)
    isfloor = (P[:, 1] < yfloor + 0.05)
    # rock detail: bump map from fbm gradient in the surface's own scale
    s = 2.6
    e = 0.055
    n0 = fbm(P[:, 0] * s, P[:, 1] * s, P[:, 2] * s, 3)
    nx = fbm((P[:, 0] + e) * s, P[:, 1] * s, P[:, 2] * s, 3) - n0
    ny = fbm(P[:, 0] * s, (P[:, 1] + e) * s, P[:, 2] * s, 3) - n0
    nz = fbm(P[:, 0] * s, P[:, 1] * s, (P[:, 2] + e) * s, 3) - n0
    n1 = fbm(P[:, 0] * 11.0, P[:, 1] * 11.0, P[:, 2] * 11.0, 2)
    nx += (fbm((P[:, 0] + 0.02) * 11.0, P[:, 1] * 11.0, P[:, 2] * 11.0, 2) - n1) * 0.6
    ny += (fbm(P[:, 0] * 11.0, (P[:, 1] + 0.02) * 11.0, P[:, 2] * 11.0, 2) - n1) * 0.6
    nz += (fbm(P[:, 0] * 11.0, P[:, 1] * 11.0, (P[:, 2] + 0.02) * 11.0, 2) - n1) * 0.6
    G = np.stack([nx, ny, nz], 1) * (2.4 * bump)
    # project the gradient into the tangent plane
    G = G - (G * N).sum(1, keepdims=True) * N
    camd = np.linalg.norm(P - cam.pos[None, :], axis=1)
    G = G * np.exp(-camd / 7.0)[:, None]
    Nb = nrm(N - G)

    # albedo: stratified limestone, wet patches, gravel floor
    band = fbm(P[:, 0] * 0.62 + P[:, 2] * 0.24, P[:, 1] * 3.0, P[:, 2] * 0.62, 4)
    strata = np.sin(P[:, 1] * 6.5 + band * 6.5) * 0.5 + 0.5
    grime = fbm(P[:, 0] * 2.2, P[:, 1] * 2.2, P[:, 2] * 2.2, 3)
    spk = fbm(P[:, 0] * 22.0, P[:, 1] * 22.0, P[:, 2] * 22.0, 2)
    k = (0.62 + 0.62 * band) * (0.84 + 0.30 * grime) * (0.90 + 0.20 * strata) * (0.92 + 0.14 * spk)
    rock = np.array([0.300, 0.286, 0.258], np.float32)[None, :] * k[:, None]
    grav = smoothstep(0.35, 0.72, fbm(P[:, 0] * 4.2, 3.0, P[:, 2] * 4.2, 3))
    floorc = np.array([0.150, 0.140, 0.126], np.float32)[None, :] * (0.55 + 0.85 * band)[:, None]
    floorc = floorc * (0.72 + 0.55 * grav[:, None])
    alb = np.where(isfloor[:, None], floorc, rock)
    wet = smoothstep(0.60, 0.80, fbm(P[:, 0] * 1.15, P[:, 1] * 1.15, P[:, 2] * 1.15, 3)) * (~isfloor)
    alb = alb * (1.0 - 0.42 * wet[:, None])
    spec = 0.08 + 0.50 * wet

    V = cam.pos[None, :] - P
    vd = np.linalg.norm(V, axis=1) + 1e-6
    V = V / vd[:, None]
    ndv = np.clip((Nb * V).sum(1), 1e-3, 1.0)

    skyfill = tube_vis(P, np.array([0.0, 0.6, length * 0.5 + 0.5], np.float32), length, radius, yfloor)
    amb_l = (np.asarray(amb, np.float32)[None, :]
             * (0.35 + 0.12 * (Nb[:, 1:2] * 0.5 + 0.5) * 6.0))
    col = alb * (amb_l + skyfill[:, None] * np.array([0.030, 0.042, 0.070], np.float32)[None, :])
    for L in lights:
        lv = np.asarray(L["pos"], np.float32)[None, :] - P
        dist = np.linalg.norm(lv, axis=1) + 1e-6
        l = lv / dist[:, None]
        ndl = (Nb * l).sum(1)
        diff = np.clip((ndl + 0.28) / 1.28, 0, 1)
        if L.get("kind") == "portal":
            # aperture light: inverse square, with the singularity clamped near the mouth
            att = L["pow"] / (dist * dist + 2.2) * (1.0 - np.exp(-dist / 1.6))
        else:
            att = L["pow"] / (dist * dist + 0.40)
        if L.get("vis", True):
            att = att * tube_vis(P, L["pos"], length, radius, yfloor)
        if L.get("spot_dir") is not None:
            sd = nrm(np.asarray(L["spot_dir"], np.float32))
            att = att * smoothstep(L.get("spot_cos", 0.55), 1.0, (-l @ sd))
        col = col + alb * np.asarray(L["col"], np.float32)[None, :] * (diff * att)[:, None]
        h = nrm(l + V)
        ndh = np.clip((Nb * h).sum(1), 0, 1)
        a = 0.28 ** 2
        den = ndh * ndh * (a * a - 1) + 1
        D = a * a / (math.pi * den * den)
        Fs = 0.04 + 0.96 * (1 - ndv) ** 5
        sp = (D * Fs * spec)[:, None] * np.asarray(L["col"], np.float32)[None, :] * (np.clip(ndl, 0, 1) * att)[:, None]
        col = col + np.minimum(sp, 3.0)
        rim = (1 - ndv) ** 2.6 * clamp01(-ndl * 0.6 + 0.55) * att * 0.30
        col = col + rim[:, None] * np.asarray(L["col"], np.float32)[None, :] * (0.3 + 0.7 * alb)

    # depth fog into the cave
    fv = (1.0 - np.exp(-fog * np.maximum(vd - 1.0, 0.0)))
    col = col * (1 - fv[:, None]) + np.asarray(fog_col, np.float32)[None, :] * fv[:, None]

    img = col.reshape(hg["H"], hg["W"], 3)
    depth = hg["depth"].reshape(hg["H"], hg["W"])
    if sky_img is not None:
        m = hg["sky"]
        img[m] = sky_img[m]
        depth[m] = 1e3
    return img, depth


# ============================================================== splat heroes


def splat(nd, cam, W, H, zbuf, exposure_scale=1.0, max_taps=48, rad_scale=0.62, soft=0.42, cone=None):
    """Shaded splats with depth test. Returns colour, coverage, depth."""
    P = nd["P"]
    x, y, z = cam.view(P)
    ok = (z > 0.08)
    if ok.sum() < 4:
        return None
    x, y, z = x[ok], y[ok], z[ok]
    C = nd["_col"][ok]
    pxw = nd["PX"][ok]
    sx, sy, inv = cam.screen(x, y, z)
    rpx = np.clip(pxw * cam.f * inv * rad_scale, 0.65, 26.0)
    if cone is not None:
        iy = np.clip(np.floor(sy).astype(np.int32), 0, H - 1)
        ix = np.clip(np.floor(sx).astype(np.int32), 0, W - 1)
        cr = cone[iy, ix]
        rpx = rpx + cr * cam.f * inv * 0.28
    idx = np.arange(len(x))

    nb = W * H
    zmin = np.full(nb, 1e9, np.float32)
    flat0 = (np.floor(sy).astype(np.int32) * W + np.floor(sx).astype(np.int32))
    inb0 = (flat0 >= 0) & (flat0 < nb)
    np.minimum.at(zmin, np.where(inb0, flat0, 0), np.where(inb0, z, 1e9))

    taps_n = np.clip(np.rint(np.pi * rpx * rpx * 1.25), 1, max_taps).astype(np.int32)
    order = np.argsort(taps_n, kind="stable")
    acc = np.zeros((nb, 3), np.float32)
    wsum = np.zeros(nb, np.float32)
    dsum = np.zeros(nb, np.float32)
    esum = np.zeros(nb, np.float32)
    em = nd["EM"][ok]
    for nt in np.unique(taps_n):
        sel = order[taps_n[order] == nt]
        if sel.size == 0:
            continue
        T = _disc_taps(int(nt))[None, :, :] * (rpx[sel][:, None, None] * 0.92)
        tx = sx[sel][:, None] + T[..., 0]
        ty = sy[sel][:, None] + T[..., 1]
        ix = np.floor(tx).astype(np.int32)
        iy = np.floor(ty).astype(np.int32)
        inb = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
        fl = iy.astype(np.int64) * W + ix.astype(np.int64)
        fl = np.where(inb, fl, 0)
        zr = np.where(inb, z[sel][:, None], 1e9)
        inside = (zr <= zbuf.reshape(-1)[fl] * 1.001 + 1e-3)
        ddx = tx - np.floor(tx) - 0.5
        ddy = ty - np.floor(ty) - 0.5
        sw = np.exp(-(ddx * ddx + ddy * ddy) / soft).astype(np.float32)
        wgt = inside.astype(np.float32) * sw / (nt * 0.55)
        wf = wgt.ravel()
        acc[:, 0] += np.bincount(fl.ravel(), weights=(wf * np.repeat(C[sel, 0], nt) * 1.0), minlength=nb)[:nb].astype(np.float32)
        acc[:, 1] += np.bincount(fl.ravel(), weights=(wf * np.repeat(C[sel, 1], nt)), minlength=nb)[:nb].astype(np.float32)
        acc[:, 2] += np.bincount(fl.ravel(), weights=(wf * np.repeat(C[sel, 2], nt)), minlength=nb)[:nb].astype(np.float32)
        wsum += np.bincount(fl.ravel(), weights=wf, minlength=nb)[:nb].astype(np.float32)
        dsum += np.bincount(fl.ravel(), weights=wf * np.repeat(z[sel], nt), minlength=nb)[:nb].astype(np.float32)
        esum += np.bincount(fl.ravel(), weights=wf * np.repeat(em[sel], nt), minlength=nb)[:nb].astype(np.float32)
    ws = np.maximum(wsum, 1e-6)
    col = np.stack([acc[:, 0] / ws, acc[:, 1] / ws, acc[:, 2] / ws], 1)
    cov = (wsum / 0.85)
    depth = (dsum / ws)
    emit = esum / ws
    return dict(col=col.reshape(H, W, 3), cov=np.clip(cov, 0, 1).reshape(H, W),
                depth=depth.reshape(H, W), emit=emit.reshape(H, W),
                wsum=wsum.reshape(H, W))


# ============================================================== volumetrics


def volumetrics(cam, W, H, length, radius, lights, yfloor=-2.45, density=0.020,
                res=0.22, steps=26, height=4.2, ground=-2.45, col=(0.004, 0.007, 0.013)):
    sw = max(8, int(W * res)); sh = max(8, int(H * res))
    yy, xx = np.meshgrid((np.arange(sh) + 0.5) * (H / sh), (np.arange(sw) + 0.5) * (W / sw), indexing="ij")
    d = cam.dir_of(xx.ravel(), yy.ravel())
    o = cam.pos[None, :]
    tmax = 30.0
    dt = tmax / steps
    acc = np.zeros((d.shape[0], 3), np.float32)
    rng = np.random.default_rng(55)
    jit = rng.random(d.shape[0]).astype(np.float32) * dt
    for i in range(steps):
        t = 0.25 + i * dt + jit
        p = o + d * t[:, None]
        inside = tube_F(p, length, radius, yfloor) < 0
        hgt = np.exp(-np.maximum(p[:, 1] - ground, 0.0) / height)
        nz = fbm(p[:, 0] * 0.45, p[:, 1] * 0.45, p[:, 2] * 0.45, 3)
        ds = density * hgt * (0.30 + 1.05 * nz) * inside
        seg = np.zeros((d.shape[0], 3), np.float32)
        for L in lights:
            lv = np.asarray(L["pos"], np.float32)[None, :] - p
            dist = np.linalg.norm(lv, axis=1) + 1e-6
            l = lv / dist[:, None]
            cos = -(d * l).sum(1)
            g = 0.62
            hg = (1 - g * g) / (4 * math.pi * (1 + g * g - 2 * g * cos) ** 1.5) * 3.0
            att = L["pow"] / (dist * dist + 0.40)
            if L.get("spot_dir") is not None:
                sd = nrm(np.asarray(L["spot_dir"], np.float32))
                att = att * smoothstep(L.get("spot_cos", 0.55), 1.0, (-l @ sd))
            seg += (hg * att)[:, None] * np.asarray(L["col"], np.float32)[None, :]
        acc += seg * ds[:, None] * dt
    acc += np.asarray(col, np.float32)[None, :] * 0.4
    return upsample(acc.reshape(sh, sw, 3), H, W)


# ============================================================== grading


def auto_exposure(img, target=0.90, pct=99.6, mid_target=0.11, lo=0.05, hi=200.0):
    """Two-sided: pin the highlights AND protect the midtones.

    A cave must stay dark. So the exposure is the smaller of "let the mouth
    reach white" and "keep the average surface from washing out".
    """
    a = img.reshape(-1, 3).mean(1)
    a = a[np.isfinite(a)]
    if a.size == 0:
        return 1.0
    hi_v = float(np.percentile(a, pct))
    mid_v = float(np.percentile(a, 60))
    e_hi = target / hi_v if hi_v > 1e-6 else hi
    e_mid = mid_target / mid_v if mid_v > 1e-6 else hi
    return float(np.clip(min(e_hi, e_mid), lo, hi))


def grade(img, exposure=1.0, bloom_amt=0.20, streak_amt=0.14, ca=1.1, vig=0.36,
          grain_amt=0.011, seed=0, contrast=1.07, sat=1.06):
    x = aces(np.maximum(img, 0) * exposure)
    x = x + bloom(x, strength=bloom_amt)
    x = x + streak(x, strength=streak_amt)
    x = (x - 0.5) * contrast + 0.5
    lum = x.mean(2, keepdims=True)
    x = lum + (x - lum) * sat
    x = x + np.array([0.004, 0.006, 0.011], np.float32)[None, None, :] * (1 - clamp01(x))
    x = clamp01(x)
    x = chroma_ab(x, ca)
    x = x * vignette(*x.shape[:2], amount=vig)
    x = x + grain(x.shape[0], x.shape[1], seed, grain_amt)[..., None]
    return clamp01(x)
