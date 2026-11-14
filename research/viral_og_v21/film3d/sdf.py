#!/usr/bin/env python3
"""
Solid geometry for the characters and props, as signed distance fields.

Point clouds were the wrong tool: separate ellipsoid shells leave gaps, read as
bubbles and have no continuous surface normal. A smooth-union SDF gives one
watertight body, correct normals everywhere and real occlusion against the cave,
because the same ray that misses the cave wall can then hit the animal.

Convention, same as geo3d.Cave: sdf > 0 is solid, sdf < 0 is air.
"""
from __future__ import annotations

import math

import numpy as np

from geo3d import fbm, smoothstep, vnoise

__all__ = ["smin", "smax", "ellipsoid", "Bear", "Skull", "Boulder", "Torch"]


def smin(a, b, k):
    """Polynomial smooth minimum: blends two surfaces without a crease."""
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b * (1 - h) + a * h - k * h * (1 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


def ellipsoid(p, c, r):
    """Approximate SDF of an axis-aligned ellipsoid (good enough for sphere tracing)."""
    q = (p - np.asarray(c, np.float32)) / np.asarray(r, np.float32)
    k0 = np.linalg.norm(q, axis=-1)
    q2 = q / np.asarray(r, np.float32)
    k1 = np.linalg.norm(q2, axis=-1) + 1e-8
    return k0 * (k0 - 1.0) / k1


def _rot(p, c, axis, ang):
    """Rotate points *back* around c (so a rotated part can be tested in place)."""
    if ang == 0.0:
        return p
    q = p - np.asarray(c, np.float32)
    ca, sa = math.cos(-ang), math.sin(-ang)
    if axis == "x":
        y = q[..., 1] * ca - q[..., 2] * sa
        z = q[..., 1] * sa + q[..., 2] * ca
        return np.stack([q[..., 0], y, z], -1) + np.asarray(c, np.float32)
    x = q[..., 0] * ca + q[..., 2] * sa
    z = -q[..., 0] * sa + q[..., 2] * ca
    return np.stack([x, q[..., 1], z], -1) + np.asarray(c, np.float32)


# ------------------------------------------------------------------ bear

# part, centre, radii  (metres, origin at the feet, nose towards +z)
BEAR = [
    ("torso",  (0.00, 1.06, 0.05), (0.44, 0.47, 0.86)),
    ("hump",   (0.00, 1.42, 0.44), (0.29, 0.21, 0.33)),
    ("rump",   (0.00, 0.99, -0.58), (0.37, 0.41, 0.38)),
    ("chest",  (0.00, 0.96, 0.72), (0.37, 0.41, 0.35)),
    ("neck",   (0.00, 1.03, 0.96), (0.26, 0.26, 0.26)),
    ("head",   (0.00, 0.99, 1.23), (0.235, 0.215, 0.26)),
    ("snout",  (0.00, 0.93, 1.46), (0.125, 0.110, 0.20)),
    ("nose",   (0.00, 0.92, 1.63), (0.070, 0.060, 0.050)),
    ("earL",   (0.155, 1.16, 1.17), (0.065, 0.070, 0.040)),
    ("earR",   (-0.155, 1.16, 1.17), (0.065, 0.070, 0.040)),
    ("tail",   (0.00, 1.02, -0.90), (0.050, 0.070, 0.050)),
]
LEGS = [  # name, hip pivot, hip centre, radii, paw centre, paw radii, phase
    ("hipL", (0.32, 0.86, 0.52), (0.32, 0.50, 0.56), (0.150, 0.40, 0.185), (0.32, 0.115, 0.66), (0.145, 0.105, 0.215), 0.0),
    ("hipR", (-0.32, 0.86, 0.52), (-0.32, 0.50, 0.56), (0.150, 0.40, 0.185), (-0.32, 0.115, 0.66), (0.145, 0.105, 0.215), math.pi),
    ("shL",  (0.30, 0.86, -0.50), (0.30, 0.50, -0.50), (0.160, 0.40, 0.200), (0.30, 0.115, -0.40), (0.150, 0.105, 0.210), math.pi),
    ("shR",  (-0.30, 0.86, -0.50), (-0.30, 0.50, -0.50), (0.160, 0.40, 0.200), (-0.30, 0.115, -0.40), (0.150, 0.105, 0.210), 0.0),
]

# rearing pose targets for the body parts (legs stay planted)
REAR = {
    "torso": ((0.00, 1.15, 0.00), (0.52, 0.70, 0.58)),
    "hump":  ((0.00, 1.66, 0.06), (0.34, 0.26, 0.28)),
    "rump":  ((0.00, 0.86, -0.26), (0.40, 0.40, 0.34)),
    "chest": ((0.00, 1.52, 0.24), (0.42, 0.42, 0.34)),
    "neck":  ((0.00, 1.86, 0.30), (0.28, 0.28, 0.28)),
    "head":  ((0.00, 2.02, 0.42), (0.235, 0.215, 0.26)),
    "snout": ((0.00, 1.96, 0.64), (0.125, 0.110, 0.20)),
    "nose":  ((0.00, 1.95, 0.81), (0.070, 0.060, 0.050)),
    "earL":  ((0.155, 2.19, 0.36), (0.065, 0.070, 0.040)),
    "earR":  ((-0.155, 2.19, 0.36), (0.065, 0.070, 0.040)),
    "tail":  ((0.00, 0.52, -0.44), (0.050, 0.070, 0.050)),
}
REAR_ARMS = [
    ("armL", (0.40, 1.58, 0.20), (0.40, 1.58, 0.20), (0.130, 0.30, 0.140), (0.44, 1.10, 0.34), (0.110, 0.110, 0.130)),
    ("armR", (-0.40, 1.58, 0.20), (-0.40, 1.58, 0.20), (0.130, 0.30, 0.140), (-0.44, 1.10, 0.34), (0.110, 0.110, 0.130)),
]


class Bear:
    """One watertight animal, posed by moving the field's parts, not the pixels."""

    radius = 1.45

    def __init__(self, pos=(0.0, 0.0, 0.0), yaw=0.0, fur=1.0, pose=0.0, walk=0.0,
                 phase=0.0, breathe=0.0):
        self.pos = np.asarray(pos, np.float32)
        self.yaw = float(yaw)
        self.fur = float(fur)
        # pose and gait are bound to the field, otherwise the renderer would trace
        # the same default stance in every shot
        self.pose, self.walk, self.phase, self.breathe = float(pose), float(walk), float(phase), float(breathe)
        # bounding sphere has to live in world space, or the ray cull clips the body
        self.centre = self.pos + np.array([0.0, 1.15, 0.35], np.float32)

    def _parts(self, pose, walk, phase, breathe):
        u = float(np.clip(pose, 0, 1))
        u = u * u * (3 - 2 * u)
        out = []
        for name, c, r in BEAR:
            c2, r2 = c, r
            if name in REAR:
                cr, rr = REAR[name]
                c2 = tuple(c[i] + (cr[i] - c[i]) * u for i in range(3))
                r2 = tuple(r[i] + (rr[i] - r[i]) * u for i in range(3))
            if breathe and name in ("torso", "chest", "hump"):
                r2 = tuple(r2[i] * (1.0 + 0.012 * breathe) for i in range(3))
            out.append((c2, r2, 1.0))
        # legs: rotate the whole limb about its hip by the gait angle
        for name, pivot, hc, hr, pc, pr, ph in LEGS:
            ang = math.sin(phase + ph) * 0.42 * walk
            out.append((hc, hr, ang, pivot, "x"))
            out.append((pc, pr, ang, pivot, "x"))
        if u > 0.02:
            for name, pivot, hc, hr, pc, pr in REAR_ARMS:
                a = (u) * 0.55 * math.sin(phase * 0.5 + (0.4 if name == "armL" else -0.4))
                out.append((hc, hr, a, pivot, "x", u))
                out.append((pc, pr, a, pivot, "x", u))
        return out

    def sdf(self, p, pose=None, walk=None, phase=None, breathe=None):
        pose = self.pose if pose is None else pose
        walk = self.walk if walk is None else walk
        phase = self.phase if phase is None else phase
        breathe = self.breathe if breathe is None else breathe
        q = p - self.pos[None, :]
        if self.yaw:
            q = _rot(q, (0, 0, 0), "y", -self.yaw) if False else q
        # yaw about the animal's own origin
        ca, sa = math.cos(-self.yaw), math.sin(-self.yaw)
        q = np.stack([q[..., 0] * ca + q[..., 2] * sa, q[..., 1], -q[..., 0] * sa + q[..., 2] * ca], -1)
        d = np.full(q.shape[:-1], 1e3, np.float32)
        for part in self._parts(pose, walk, phase, breathe):
            if len(part) == 3:
                c, r, _ = part
                d = smin(d, ellipsoid(q, c, r), 0.13)
            else:
                c, r, ang, piv, axis, *w = part
                qq = _rot(q, piv, axis, ang)
                e = ellipsoid(qq, c, r)
                if w:  # arms only fade in with the rear
                    e = e + (1.0 - w[0]) * 0.6
                d = smin(d, e, 0.09)
        # fur: displace the surface with noise so the silhouette is not a tube
        if self.fur > 0:
            n = fbm(q[..., 0] * 16.0, q[..., 1] * 16.0, q[..., 2] * 16.0, 2) - 0.5
            n2 = vnoise(q[..., 0] * 41.0, q[..., 1] * 41.0, q[..., 2] * 41.0) - 0.5
            d = d - self.fur * (0.010 * n + 0.0045 * n2)
            d = d + self.fur * 0.014        # keeps the body from inflating
        return d


# ------------------------------------------------------------------ skull

SKULL_PARTS = [
    ((0.000, 0.000, -0.020), (0.112, 0.098, 0.132)),   # cranium
    ((0.000, 0.034, -0.060), (0.070, 0.052, 0.095)),   # occiput / crest mass
    ((0.000, 0.058, 0.010), (0.026, 0.030, 0.118)),    # sagittal crest
    ((0.000, -0.004, 0.130), (0.068, 0.056, 0.098)),   # muzzle root
    ((0.000, -0.012, 0.205), (0.045, 0.039, 0.058)),   # muzzle
    ((0.076, -0.016, 0.078), (0.026, 0.038, 0.068)),   # zygomatic L
    ((-0.076, -0.016, 0.078), (0.026, 0.038, 0.068)),  # zygomatic R
    ((0.000, 0.040, 0.070), (0.086, 0.026, 0.060)),    # forehead plate
]


class Skull:
    radius = 0.34

    def __init__(self, origin=(0.0, 0.0, 0.0), yaw=0.0, scale=1.0):
        self.o = np.asarray(origin, np.float32)
        self.centre = self.o
        self.yaw = float(yaw)
        self.s = float(scale)

    def sdf(self, p):
        q = (p - self.o[None, :]) / self.s
        ca, sa = math.cos(-self.yaw), math.sin(-self.yaw)
        q = np.stack([q[..., 0] * ca + q[..., 2] * sa, q[..., 1], -q[..., 0] * sa + q[..., 2] * ca], -1)
        d = np.full(q.shape[:-1], 1e3, np.float32)
        for c, r in SKULL_PARTS:
            d = smin(d, ellipsoid(q, c, r), 0.030)
        # eye sockets, nasal aperture, foramen magnum: carved out of the bone
        for sx in (-1, 1):
            d = smax(d, -ellipsoid(q, (0.058 * sx, 0.020, 0.150), (0.030, 0.030, 0.032)), 0.012)
        d = smax(d, -ellipsoid(q, (0.0, -0.004, 0.246), (0.020, 0.032, 0.030)), 0.010)
        d = smax(d, -ellipsoid(q, (0.0, -0.030, -0.150), (0.030, 0.030, 0.026)), 0.010)
        # teeth: two rows along the maxilla
        for sx in (-1, 1):
            for k in range(8):
                tz = 0.086 + k * 0.0205
                tx = sx * (0.040 - 0.0038 * k)
                ty = -0.044 - 0.006 * math.sin(k / 7.0 * math.pi)
                d = smin(d, ellipsoid(q, (tx, ty, tz), (0.0095, 0.017, 0.0080)), 0.004)
        # bone grain
        d = d - 0.0016 * (fbm(q[..., 0] * 34, q[..., 1] * 34, q[..., 2] * 34, 2) - 0.5)
        return d * self.s


# ------------------------------------------------------------------ props


class Boulder:
    """The slab the skull sits on: a squat, noise-broken dome."""

    def __init__(self, centre=(0.0, -1.35, 0.0), radii=(0.42, 0.30, 0.42)):
        self.c = np.asarray(centre, np.float32)
        self.r = np.asarray(radii, np.float32)
        self.centre = self.c
        self.radius = float(np.max(radii) * 1.4)

    def sdf(self, p):
        q = p - self.c[None, :]
        q = np.stack([q[..., 0], np.abs(q[..., 1]), q[..., 2]], -1)     # dome: mirror the lower half away
        d = ellipsoid(q, (0, 0, 0), self.r)
        n = fbm(q[..., 0] * 7.0, q[..., 1] * 7.0, q[..., 2] * 7.0, 3) - 0.5
        n2 = fbm(q[..., 0] * 19.0, q[..., 1] * 19.0, q[..., 2] * 19.0, 2) - 0.5
        return d - (0.045 * n + 0.016 * n2) + 0.02


class Torch:
    """The hand torch: a tapered handle with a charred head."""

    def __init__(self, base=(0.0, 0.0, 0.0), tilt=0.35):
        self.b = np.asarray(base, np.float32)
        self.centre = self.b
        self.tilt = float(tilt)
        self.radius = 0.45

    def sdf(self, p):
        q = p - self.b[None, :]
        q = _rot(q, (0, 0, 0), "x", -self.tilt)
        # capsule along -y
        a = np.array([0.0, 0.0, 0.0], np.float32)
        bb = np.array([0.0, -0.26, 0.0], np.float32)
        pa = q - a
        ba = bb - a
        h = np.clip((pa @ ba) / (ba @ ba), 0.0, 1.0)
        d = np.linalg.norm(pa - h[..., None] * ba, axis=-1) - 0.014
        d = smin(d, ellipsoid(q, (0.0, 0.030, 0.0), (0.028, 0.040, 0.028)), 0.02)
        return d
