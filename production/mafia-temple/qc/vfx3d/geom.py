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


def ray_frustum(ro, rd, a, b, r_a, r_b):
    """Cone frustum from a (radius r_a) to b (radius r_b).

    Same algebra as the capsule, but the radius is interpolated along the axis
    instead of being constant, so a limb can taper. Returns (t, s) where s is
    0..1 along the axis for shading.
    """
    a = np.asarray(a, np.float32)
    b = np.asarray(b, np.float32)
    ba = b - a
    oa = ro - a
    baba = max(float(ba @ ba), 1e-8)
    if rd.ndim == 3:
        bard = (ba[None, None, :] * rd).sum(-1)
        baoa = (ba[None, None, :] * oa).sum(-1)
    else:
        bard = ba @ rd
        baoa = ba @ oa
    rdoa = (rd * oa).sum(-1)
    oaoa = (oa * oa).sum(-1)
    s = np.clip((baoa - bard * rdoa) / np.maximum(baba - bard * bard, 1e-8), 0.0, 1.0)
    # radius at the closest point, then a sphere test against it
    rad = r_a + (r_b - r_a) * s
    cx = a + s[..., None] * ba
    oc = ro - cx
    bq = (oc * rd).sum(-1)
    cq = (oc * oc).sum(-1) - rad * rad
    disc = bq * bq - cq
    sq = np.sqrt(np.maximum(disc, 0))
    tt = -bq - sq
    ok = (disc > 0) & (tt > 1e-3)
    return np.where(ok, tt, INF).astype(np.float32), s.astype(np.float32)


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


# --------------------------------------------------------------------- extras
def ray_obb(ro, rd, centre, half, basis):
    """Ray vs oriented box. `basis` is a 3x3 matrix whose COLUMNS are the box axes.

    A box rotated in its own frame, so beams, eaves and the head can be tilted
    without approximating them with a bigger axis-aligned box.
    """
    c = np.asarray(centre, np.float32)
    h = np.asarray(half, np.float32)
    B = np.asarray(basis, np.float32)
    o = (ro - c) @ B                      # world -> box frame (B orthonormal)
    d = rd @ B
    inv = 1.0 / np.where(np.abs(d) < 1e-8, 1e-8, d)
    t1 = (-h - o) * inv
    t2 = (h - o) * inv
    tmin = np.maximum(np.minimum(t1, t2).max(-1), 0.0)
    tmax = np.minimum(np.maximum(t1, t2).min(-1), np.inf)
    hit = (tmax >= tmin) & (tmin > 1e-3)
    return np.where(hit, tmin, INF).astype(np.float32)


def obb_basis(yaw=0.0, pitch=0.0, roll=0.0):
    """Orthonormal basis for a box rotated by yaw (y), pitch (x), roll (z)."""
    cy, sy = np.cos(yaw), np.sin(yaw)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cr, sr = np.cos(roll), np.sin(roll)
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], np.float32)
    Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]], np.float32)
    Rz = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]], np.float32)
    return (Ry @ Rx @ Rz).astype(np.float32)


def ray_ellipsoid(ro, rd, centre, radii, basis=None):
    """Ray vs ellipsoid (optionally rotated). Used for the head/skull volume."""
    c = np.asarray(centre, np.float32)
    r = np.asarray(radii, np.float32)
    o = ro - c
    d = rd
    if basis is not None:
        B = np.asarray(basis, np.float32)
        o = o @ B
        d = d @ B
    o = o / r
    d = d / r
    a = (d * d).sum(-1)
    b = (o * d).sum(-1)
    cc = (o * o).sum(-1) - 1.0
    disc = b * b - a * cc
    sq = np.sqrt(np.maximum(disc, 0))
    t = (-b - sq) / np.maximum(a, 1e-9)
    ok = (disc > 0) & (t > 1e-3)
    return np.where(ok, t, INF).astype(np.float32)


def ellipsoid_normal(p, centre, radii, basis=None):
    """Outward normal of the same ellipsoid at world point p."""
    c = np.asarray(centre, np.float32)
    r = np.asarray(radii, np.float32)
    q = (p - c) / r
    n = q / r
    if basis is not None:
        n = n @ np.asarray(basis, np.float32).T
    return normalise(n)


def orbit_eye(target, distance, yaw_deg, pitch_deg, roll_deg=0.0):
    """Camera position orbiting a target: used for locked-off shot placement."""
    t = np.asarray(target, np.float64)
    y = np.radians(yaw_deg)
    p = np.radians(pitch_deg)
    off = np.array([np.sin(y) * np.cos(p), np.sin(p), np.cos(y) * np.cos(p)])
    return (t + off * distance).astype(np.float32)
