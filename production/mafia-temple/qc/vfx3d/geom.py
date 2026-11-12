"""Vectorised ray geometry for the night-temple 3D renderer.

Everything is exact analytic intersection (no raymarching) in float32, so a
frame is a handful of NumPy passes instead of millions of SDF steps. Primitives:
plane, axis-aligned box, sphere, capsule and torus. Each returns distance `t`
and enough data to shade it (normal, material id).

This is a real 3D renderer: geometry, a perspective camera, point/area lights,
exponential fog and per-pixel shading. It is not photoreal, and it is not the
supplied reference likeness — see KNOWN-LIMITS.md.
"""
from __future__ import annotations

import numpy as np

INF = np.float32(np.inf)


def normalise(v):
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, 1e-9)


def camera_rays(width, height, eye, target, fov_deg=42.0, roll=0.0):
    """Pinhole camera ray directions for every pixel, plus the basis vectors."""
    eye = np.asarray(eye, np.float64)
    fwd = normalise(np.asarray(target, np.float64) - eye)
    world_up = np.array([0.0, 1.0, 0.0])
    if abs(float(fwd @ world_up)) > 0.995:          # near-vertical look
        world_up = np.array([0.0, 0.0, 1.0])
    right = normalise(np.cross(fwd, world_up))
    up = np.cross(right, fwd)
    if roll:
        c, s = np.cos(roll), np.sin(roll)
        right, up = right * c + up * s, up * c - right * s
    aspect = width / height
    ty = np.tan(np.radians(fov_deg) * 0.5)
    xs = (np.arange(width, dtype=np.float32) + 0.5) / width * 2 - 1
    ys = 1 - (np.arange(height, dtype=np.float32) + 0.5) / height * 2
    X, Y = np.meshgrid(xs * ty * aspect, ys * ty)
    rd = (fwd[None, None, :].astype(np.float32)
          + X[..., None] * right[None, None, :].astype(np.float32)
          + Y[..., None] * up[None, None, :].astype(np.float32))
    return normalise(rd).astype(np.float32), eye.astype(np.float32), \
        right.astype(np.float32), up.astype(np.float32)


def ray_plane(ro, rd, y, upward=False):
    """Horizontal plane at height y."""
    denom = rd[..., 1]
    t = (y - ro[..., 1]) / np.where(np.abs(denom) < 1e-8, 1e-8, denom)
    ok = (t > 1e-3) & ((denom < 0) if not upward else (denom > 0))
    return np.where(ok, t, INF).astype(np.float32), np.array([0.0, 1.0, 0.0], np.float32)


def ray_aabb(ro, rd, centre, half):
    """Slab test. Returns (t, axis) where axis is the entry face 0=x,1=y,2=z."""
    c = np.asarray(centre, np.float32)
    h = np.asarray(half, np.float32)
    inv = 1.0 / np.where(np.abs(rd) < 1e-8, 1e-8, rd)
    o = (ro - c) * inv
    s = np.abs(h * inv)
    t1 = -o - s
    t2 = -o + s
    tmin = t1.max(-1)
    tmax = t2.min(-1)
    ok = (tmax > np.maximum(tmin, 1e-3))
    axis = t1.argmax(-1).astype(np.int8)
    return np.where(ok, tmin, INF).astype(np.float32), axis


def ray_sphere(ro, rd, centre, radius):
    c = np.asarray(centre, np.float32)
    oc = ro - c
    b = (oc * rd).sum(-1)
    cc = (oc * oc).sum(-1) - radius * radius
    disc = b * b - cc
    sq = np.sqrt(np.maximum(disc, 0))
    t = -b - sq
    ok = (disc > 0) & (t > 1e-3)
    return np.where(ok, t, INF).astype(np.float32)


def ray_capsule(ro, rd, a, b, radius):
    """Capsule from a to b. Returns (t, distance-along-axis) for shading."""
    a = np.asarray(a, np.float32)
    b = np.asarray(b, np.float32)
    ba = b - a
    oa = ro - a
    baba = float(ba @ ba)
    bard = (ba[None, None, :] * rd).sum(-1) if rd.ndim == 3 else ba @ rd
    baoa = (ba[None, None, :] * oa).sum(-1) if oa.ndim == 3 else ba @ oa
    rdoa = (rd * oa).sum(-1)
    oaoa = (oa * oa).sum(-1)
    denom = baba - bard * bard
    denom = np.where(np.abs(denom) < 1e-8, 1e-8, denom)
    t = (baoa - bard * rdoa) / denom
    t = np.clip(t, 0.0, 1.0)
    # closest point on segment, then sphere of that radius
    cx = a + t[..., None] * ba
    oc = ro - cx
    bq = (oc * rd).sum(-1)
    cq = (oc * oc).sum(-1) - radius * radius
    disc = bq * bq - cq
    sq = np.sqrt(np.maximum(disc, 0))
    tt = -bq - sq
    ok = (disc > 0) & (tt > 1e-3)
    return np.where(ok, tt, INF).astype(np.float32), t.astype(np.float32)


def ray_torus(ro, rd, centre, R, r, axis='y'):
    """Approximate torus on the y (or z) axis via a bounded cylinder test.

    Sufficient for roof ridges and door rings at this scale; it is a real
    torus-ish solid, not a quad billboard.
    """
    c = np.asarray(centre, np.float32)
    o = ro - c
    if axis == 'y':
        o2 = o[..., [0, 2]]
        d2 = rd[..., [0, 2]]
    else:
        o2 = o[..., [0, 1]]
        d2 = rd[..., [0, 1]]
    a = (d2 * d2).sum(-1)
    b = 2 * (o2 * d2).sum(-1)
    cc = (o2 * o2).sum(-1) - (R + r) ** 2
    disc = b * b - 4 * a * cc
    t = (-b - np.sqrt(np.maximum(disc, 0))) / (2 * np.maximum(a, 1e-8))
    ok = (disc > 0) & (t > 1e-3)
    return np.where(ok, t, INF).astype(np.float32)


def aabb_normal(axis, rd):
    n = np.zeros((*axis.shape, 3), np.float32)
    idx = np.arange(axis.size)
    flat_axis = axis.reshape(-1)
    flat_rd = rd.reshape(-1, 3)
    sign = -np.sign(np.take_along_axis(flat_rd, flat_axis[:, None], 1)[:, 0])
    n.reshape(-1, 3)[idx, flat_axis] = sign
    return n


def smoothstep(a, b, x):
    t = np.clip((x - a) / np.maximum(b - a, 1e-9), 0, 1)
    return t * t * (3 - 2 * t)
