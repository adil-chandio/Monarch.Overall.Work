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


def _cap(p, c, r):
    """Conservative bound for an ellipsoid at (c, r): cheap, never underestimates."""
    return ellipsoid(p, (c[0], c[1], c[2]), (r[0] * 1.02, r[1] * 1.02, r[2] * 1.02))


def smax(a, b, k):
    return -smin(-a, -b, k)


def ellipsoid(p, c, r):
    """Approximate SDF of an axis-aligned ellipsoid (good enough for sphere tracing).

    Written out with a single squared-norm pass: it is called thousands of times
    per frame, and this is the hot inner loop of the whole renderer.
    """
    qx = (p[..., 0] - c[0]) * (1.0 / r[0])
    qy = (p[..., 1] - c[1]) * (1.0 / r[1])
    qz = (p[..., 2] - c[2]) * (1.0 / r[2])
    k0 = np.sqrt(qx * qx + qy * qy + qz * qz) + 1e-9
    k1 = np.sqrt((qx / r[0]) ** 2 + (qy / r[1]) ** 2 + (qz / r[2]) ** 2) + 1e-9
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
    ("torso",   (0.00, 1.02, 0.02), (0.46, 0.50, 0.80)),
    ("hump",    (0.00, 1.44, 0.34), (0.34, 0.26, 0.40)),   # the shoulder hump: the giveaway
    ("rump",    (0.00, 0.96, -0.56), (0.40, 0.44, 0.40)),
    ("chest",   (0.00, 0.90, 0.62), (0.50, 0.46, 0.38)),
    ("shldrL",  (0.34, 1.20, 0.46), (0.20, 0.30, 0.30)),
    ("shldrR",  (-0.34, 1.20, 0.46), (0.20, 0.30, 0.30)),
    ("brisket", (0.00, 0.62, 0.68), (0.30, 0.26, 0.28)),   # deep chest between the forelegs
    ("neck",    (0.00, 1.06, 0.92), (0.32, 0.32, 0.30)),
    ("nape",    (0.00, 1.26, 0.84), (0.20, 0.14, 0.22)),
    ("brow",    (0.00, 1.18, 1.14), (0.22, 0.10, 0.13)),   # low forehead ridge
    ("head",    (0.00, 1.02, 1.16), (0.215, 0.215, 0.235)),
    ("cheekL",  (0.14, 0.96, 1.16), (0.10, 0.11, 0.13)),
    ("cheekR",  (-0.14, 0.96, 1.16), (0.10, 0.11, 0.13)),
    ("snout",   (0.00, 0.94, 1.36), (0.115, 0.098, 0.15)),  # short, blunt
    ("nose",    (0.00, 0.925, 1.48), (0.062, 0.052, 0.042)),
    ("earL",    (0.185, 1.20, 1.06), (0.055, 0.062, 0.032)),  # small, low, round
    ("earR",    (-0.185, 1.20, 1.06), (0.055, 0.062, 0.032)),
    ("tail",    (0.00, 1.00, -0.92), (0.045, 0.060, 0.045)),
]
LEGS = [  # name, hip pivot, hip centre, radii, paw centre, paw radii, phase
    ("hipL", (0.36, 0.86, 0.50), (0.36, 0.50, 0.54), (0.145, 0.40, 0.160), (0.36, 0.115, 0.62), (0.140, 0.105, 0.200), 0.0),
    ("hipR", (-0.36, 0.86, 0.50), (-0.36, 0.50, 0.54), (0.145, 0.40, 0.160), (-0.36, 0.115, 0.62), (0.140, 0.105, 0.200), math.pi),
    ("shL",  (0.36, 0.86, -0.58), (0.36, 0.50, -0.60), (0.150, 0.40, 0.170), (0.36, 0.115, -0.56), (0.140, 0.105, 0.190), math.pi),
    ("shR",  (-0.36, 0.86, -0.58), (-0.36, 0.50, -0.60), (0.150, 0.40, 0.170), (-0.36, 0.115, -0.56), (0.140, 0.105, 0.190), 0.0),
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
                far = (np.abs(q[..., 0] - c[0]) > r[0] * 4.0) | \
                      (np.abs(q[..., 1] - c[1]) > r[1] * 4.0) | \
                      (np.abs(q[..., 2] - c[2]) > r[2] * 4.0)
                e = np.where(far, 9.0, ellipsoid(q, c, r))
                d = smin(d, e, 0.13)
            else:
                c, r, ang, piv, axis, *w = part
                qq = _rot(q, piv, axis, ang)
                e = ellipsoid(qq, c, r)
                if w:  # arms only fade in with the rear
                    e = e + (1.0 - w[0]) * 0.6
                d = smin(d, e, 0.05)
        # fur: displace the surface with noise so the silhouette is not a tube
        if self.fur > 0:
            n = fbm(q[..., 0] * 16.0, q[..., 1] * 16.0, q[..., 2] * 16.0, 2) - 0.5
            n2 = vnoise(q[..., 0] * 41.0, q[..., 1] * 41.0, q[..., 2] * 41.0) - 0.5
            d = d - self.fur * (0.013 * n + 0.006 * n2)
            d = d + self.fur * 0.014        # keeps the body from inflating
        return d


# ------------------------------------------------------------------ skull

SKULL_PARTS = [
    ((0.000, 0.000, -0.055), (0.110, 0.092, 0.112)),      # braincase
    ((0.000, 0.052, -0.090), (0.078, 0.044, 0.070)),      # occiput
    ((0.000, 0.064, -0.010), (0.014, 0.040, 0.118)),      # sagittal crest
    ((0.000, 0.004, 0.072), (0.086, 0.056, 0.076)),       # frontal / brow
    ((0.000, -0.028, 0.186), (0.047, 0.040, 0.118)),      # muzzle
    ((0.000, -0.030, 0.258), (0.034, 0.031, 0.036)),      # premaxilla
    ((0.076, -0.018, 0.088), (0.020, 0.025, 0.074)),      # zygomatic arch L
    ((-0.076, -0.018, 0.088), (0.020, 0.025, 0.074)),     # zygomatic arch R
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
            # a part only affects samples inside (roughly) its own shell; skipping the
            # far ones is exact for the same reason smin with a big b is a no-op
            far = (np.abs(q[..., 0] - c[0]) > r[0] * 3.2) | \
                  (np.abs(q[..., 1] - c[1]) > r[1] * 3.2) | \
                  (np.abs(q[..., 2] - c[2]) > r[2] * 3.2)
            e = np.where(far, 9.0, ellipsoid(q, c, r))
            d = smin(d, e, 0.020)
        # eye sockets, nasal aperture, foramen magnum: carved out of the bone
        for sx in (-1, 1):
            # orbit, then the gap under the cheekbone that reads as an arch
            d = smax(d, -ellipsoid(q, (0.058 * sx, 0.010, 0.092), (0.036, 0.034, 0.034)), 0.006)
            d = smax(d, -ellipsoid(q, (0.070 * sx, -0.048, 0.080), (0.026, 0.016, 0.050)), 0.008)
        d = smax(d, -ellipsoid(q, (0.0, -0.024, 0.286), (0.017, 0.024, 0.022)), 0.006)   # nasal aperture
        d = smax(d, -ellipsoid(q, (0.0, -0.014, -0.168), (0.028, 0.026, 0.022)), 0.006)  # foramen magnum
        # teeth: two rows along the maxilla
        for sx in (-1, 1):
            for k in range(8):
                tz = 0.086 + k * 0.0205
                tx = sx * (0.040 - 0.0038 * k)
                ty = -0.060 - 0.007 * math.sin(k / 7.0 * math.pi)
                d = smin(d, ellipsoid(q, (tx, ty, tz), (0.0105, 0.020, 0.0085)), 0.003)
        # canines: the pair that makes a bear skull unmistakable
        for sx in (-1, 1):
            d = smin(d, ellipsoid(q, (sx * 0.042, -0.070, 0.246), (0.0105, 0.026, 0.0105)), 0.003)
        # the post-orbital constriction: a narrow waist behind the eyes
        d = smax(d, -ellipsoid(q, (0.0, 0.030, 0.020), (0.052, 0.030, 0.030)), 0.020)
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


class Fire:
    """The humans' fire: a low ring of stones and the burning wood inside it.

    This is what lights the cave. Every warm light in the film is anchored here,
    so the shadows all agree with each other.
    """

    def __init__(self, base=(0.0, -1.35, 0.0), ring=0.42):
        self.b = np.asarray(base, np.float32)
        self.ring = float(ring)
        self.centre = self.b + np.array([0.0, 0.22, 0.0], np.float32)
        self.radius = float(ring) + 0.55

    def sdf(self, p):
        q = p - self.b[None, :]
        # stone ring: a torus flattened into the floor
        rxz = np.sqrt(q[..., 0] ** 2 + q[..., 2] ** 2)
        d = np.sqrt((rxz - self.ring) ** 2 + (q[..., 1] - 0.05) ** 2) - 0.085
        # crossed logs
        for ax in (0.0, 1.0):
            c, sn = math.cos(ax * 1.9), math.sin(ax * 1.9)
            qq = np.stack([q[..., 0] * c - q[..., 2] * sn, q[..., 1] - 0.07, q[..., 0] * sn + q[..., 2] * c], -1)
            d = smin(d, np.linalg.norm(qq / np.array([0.40, 0.045, 0.045], np.float32), axis=-1) * 0.045 - 0.045, 0.03)
        return d


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
        bb = np.array([0.0, -0.30, 0.0], np.float32)
        pa = q - a
        ba = bb - a
        h = np.clip((pa @ ba) / (ba @ ba), 0.0, 1.0)
        d = np.linalg.norm(pa - h[..., None] * ba, axis=-1) - 0.026
        d = smin(d, ellipsoid(q, (0.0, 0.036, 0.0), (0.042, 0.055, 0.042)), 0.02)
        # a rag wrap, so it reads as something a hand made
        d = smin(d, ellipsoid(q, (0.0, -0.16, 0.0), (0.036, 0.090, 0.036)), 0.03)
        return d
