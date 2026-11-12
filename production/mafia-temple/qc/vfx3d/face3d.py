"""The S6/S5 head, as a signed distance field with smooth blending.

Why a distance field and not a pile of ellipsoids: a hard union of ellipsoids
leaves a visible seam and bulge wherever two of them meet, which is exactly what
made the first three attempts at this face read as a balloon. A smooth-minimum
union melts the volumes into one continuous surface — the skin folds over the
cheekbone, the brow flows into the nose bridge — which is what makes a sculpt
look sculpted rather than assembled.

Everything here is a plain analytic distance function, so the marcher is a
straight loop with no acceleration structure. That is affordable because this
set is one object in front of a camera.

Region rules are by position, not by material id: the lips are where the mouth
is, the iris is where the iris is. That keeps the surface itself continuous while
still letting the shader colour the lip, the beard and the eye.

Honest scope: this is a stylised sculpt with correct volume and correct light
response. It is not a scan, not a likeness of any person, and there is no facial
rig, no pore detail and no subsurface scattering.
"""
from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------- primitives
def sd_sphere(p, c, r):
    return np.linalg.norm(p - np.asarray(c, np.float32), axis=-1) - r


def sd_ellipsoid(p, c, r):
    q = (p - np.asarray(c, np.float32)) / np.asarray(r, np.float32)
    k0 = np.linalg.norm(q, axis=-1)
    k1 = np.linalg.norm(q / np.asarray(r, np.float32), axis=-1)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)


def sd_capsule(p, a, b, r):
    a = np.asarray(a, np.float32)
    b = np.asarray(b, np.float32)
    pa = p - a
    ba = b - a
    h = np.clip((pa @ ba) / max(float(ba @ ba), 1e-9), 0, 1)
    return np.linalg.norm(pa - h[..., None] * ba, axis=-1) - r


def smin(a, b, k):
    """Polynomial smooth minimum: the join is filleted over roughly k metres."""
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


# ------------------------------------------------------------------ head sdf
# Local frame: +x right, +y up, +z forward (towards the camera), origin between
# the eyes. A 0.219 m head, so every number below is in metres.
EYE_Y = -0.012
EYE_X = 0.0292
EYE_Z = 0.0495
EYE_R = 0.0122


def head_distance(p, yaw=0.0, gaze=0.0):
    """Distance to the head surface, in metres. Negative inside."""
    if yaw or gaze:
        c, s = np.cos(-(yaw + gaze * 0.30)), np.sin(-(yaw + gaze * 0.30))
        x = p[..., 0] * c - p[..., 2] * s
        z = p[..., 0] * s + p[..., 2] * c
        p = np.stack([x, p[..., 1], z], -1)

    # ---- cranium: skull, forehead and the temples, blended into one mass
    d = sd_ellipsoid(p, (0.0, 0.030, -0.014), (0.0705, 0.0710, 0.0770))
    d = smin(d, sd_ellipsoid(p, (0.0, 0.040, 0.006), (0.0640, 0.0440, 0.0620)),
             0.030)
    for sx in (-1, 1):
        d = smin(d, sd_ellipsoid(p, (sx * 0.0520, 0.012, -0.014),
                                 (0.0210, 0.0430, 0.0500)), 0.030)

    # ---- mid-face: one mass, then the brow, cheeks and temples folded into it
    d = smin(d, sd_ellipsoid(p, (0.0, -0.0300, -0.0060),
                             (0.0560, 0.0430, 0.0560)), 0.045)
    for sx in (-1, 1):
        d = smin(d, sd_ellipsoid(p, (sx * 0.0270, 0.0030, 0.0430),
                                 (0.0330, 0.0105, 0.0200)), 0.022)
        d = smin(d, sd_ellipsoid(p, (sx * 0.0390, -0.0390, 0.0300),
                                 (0.0280, 0.0210, 0.0290)), 0.030)
        d = smin(d, sd_ellipsoid(p, (sx * 0.0430, -0.0300, 0.0200),
                                 (0.0210, 0.0180, 0.0250)), 0.030)
        d = smin(d, sd_ellipsoid(p, (sx * 0.0560, -0.0080, 0.0060),
                                 (0.0150, 0.0250, 0.0300)), 0.028)
    d = smin(d, sd_ellipsoid(p, (0.0, 0.0010, 0.0450), (0.0165, 0.0110, 0.0180)),
             0.020)

    # ---- nose: bridge and tip and wings, all one blend so there is no seam
    d = smin(d, sd_capsule(p, (0.0, 0.0070, 0.0505), (0.0, -0.0400, 0.0665),
                           0.0104), 0.018)
    d = smin(d, sd_ellipsoid(p, (0.0, -0.0495, 0.0690),
                             (0.0155, 0.0135, 0.0140)), 0.016)
    for sx in (-1, 1):
        d = smin(d, sd_ellipsoid(p, (sx * 0.0150, -0.0540, 0.0610),
                                 (0.0074, 0.0062, 0.0074)), 0.010)

    # ---- jaw, chin and the rami running up to the ears
    d = smin(d, sd_ellipsoid(p, (0.0, -0.0660, 0.0280),
                             (0.0510, 0.0330, 0.0480)), 0.032)
    d = smin(d, sd_ellipsoid(p, (0.0, -0.0905, 0.0440),
                             (0.0270, 0.0195, 0.0245)), 0.022)
    # the cheek-to-jaw hollow, filled so the face is not a wedge
    for sx in (-1, 1):
        d = smin(d, sd_ellipsoid(p, (sx * 0.0340, -0.0560, 0.0330),
                                 (0.0250, 0.0250, 0.0270)), 0.026)
    for sx in (-1, 1):
        d = smin(d, sd_ellipsoid(p, (sx * 0.0455, -0.0550, -0.0100),
                                 (0.0115, 0.0290, 0.0250)), 0.024)

    # ---- lips: shallow pads, so the mouth is a crease and not a shelf
    d = smin(d, sd_ellipsoid(p, (0.0, -0.0762, 0.0600),
                             (0.0198, 0.0052, 0.0056)), 0.008)
    d = smin(d, sd_ellipsoid(p, (0.0, -0.0845, 0.0596),
                             (0.0190, 0.0064, 0.0058)), 0.008)
    # the mouth line itself is a cut, not a groove
    d = smax(d, -sd_ellipsoid(p, (0.0, -0.0805, 0.0700),
                              (0.0205, 0.0012, 0.0060)), 0.004)

    # ---- eye sockets: subtracted, so the eyeball sits in a real hollow
    for sx in (-1, 1):
        # the cut has to stop short of the eyeball's front pole, or it removes
        # the eye as well as the socket and the face reads as a skull
        d = smax(d, -sd_ellipsoid(p, (sx * EYE_X, EYE_Y, 0.0320),
                                  (0.0230, 0.0175, 0.0140)), 0.010)

    # ---- ears
    for sx in (-1, 1):
        d = smin(d, sd_ellipsoid(p, (sx * 0.0668, -0.0140, -0.0180),
                                 (0.0042, 0.0160, 0.0112)), 0.012)

    # ---- neck
    d = smin(d, sd_capsule(p, (0.0, -0.1080, -0.0080), (0.0, -0.1520, -0.0180),
                           0.0400), 0.030)
    return d


def hair_distance(p, yaw=0.0):
    """The hair volume, kept separate so the shader can colour the strands."""
    if yaw:
        c, s = np.cos(-yaw), np.sin(-yaw)
        x = p[..., 0] * c - p[..., 2] * s
        z = p[..., 0] * s + p[..., 2] * c
        p = np.stack([x, p[..., 1], z], -1)
    d = sd_ellipsoid(p, (0.0, 0.0400, -0.0300), (0.0805, 0.0735, 0.0860))
    d = smin(d, sd_ellipsoid(p, (0.0, -0.0120, -0.0620),
                             (0.0745, 0.0815, 0.0480)), 0.030)
    d = smin(d, sd_ellipsoid(p, (0.0, 0.0200, -0.0100),
                             (0.0800, 0.0640, 0.0700)), 0.030)
    # hairline: layered locks with different tilt, so the edge is ragged
    d = smin(d, sd_ellipsoid(p, (0.0, 0.0640, 0.0200),
                             (0.0700, 0.0180, 0.0450)), 0.020)
    d = smin(d, sd_ellipsoid(p, (-0.029, 0.0610, 0.0400),
                             (0.0335, 0.0135, 0.0300)), 0.012)
    d = smin(d, sd_ellipsoid(p, (0.032, 0.0665, 0.0340),
                             (0.0305, 0.0130, 0.0285)), 0.012)
    d = smin(d, sd_ellipsoid(p, (0.007, 0.0740, 0.0120),
                             (0.0395, 0.0135, 0.0335)), 0.012)
    d = smin(d, sd_ellipsoid(p, (0.0, 0.0570, 0.0460),
                             (0.0520, 0.0135, 0.0240)), 0.010)
    # Carve the face out of the hair volume. Without this the cap and the side
    # masses bulge forward past the brow and swallow the whole face — which is
    # exactly what the first render of this field showed: a bob with no features.
    face_win = sd_ellipsoid(p, (0.0, -0.0300, 0.0900),
                            (0.0790, 0.0980, 0.1200))
    d = smax(d, -face_win, 0.006)
    # side sweeps: the long hair that falls past the ear, longer on one side by
    # design so the silhouette is not a symmetric helmet
    for sx, k in ((-1, 1.00), (1, 1.14)):
        d = smin(d, sd_ellipsoid(p, (sx * 0.0600 * k, 0.0180, 0.0010),
                                 (0.0225 * k, 0.0480, 0.0560)), 0.024)
        d = smin(d, sd_ellipsoid(p, (sx * 0.0620 * k, -0.0280, -0.0330),
                                 (0.0215, 0.0620, 0.0700)), 0.024)
        d = smin(d, sd_ellipsoid(p, (sx * 0.0640 * k, 0.0430, -0.0060),
                                 (0.0180, 0.0300, 0.0410)), 0.018)
    return d


def coat_distance(p):
    """The jacket: shoulders and chest, so the head is not floating."""
    d = sd_ellipsoid(p, (0.0, -0.2240, -0.1000), (0.1860, 0.0740, 0.0880))
    d = smin(d, sd_ellipsoid(p, (0.0, -0.2900, -0.1040),
                             (0.2050, 0.0870, 0.0930)), 0.040)
    for sx in (-1, 1):
        d = smin(d, sd_ellipsoid(p, (sx * 0.0900, -0.2000, -0.0940),
                                 (0.1030, 0.0520, 0.0780)), 0.030)
    d = smin(d, sd_ellipsoid(p, (0.0, -0.1700, -0.0220),
                             (0.0620, 0.0170, 0.0600)), 0.020)   # collar
    # a shirt collar opening: a shallow V cut into the jacket front
    d = smax(d, -np.abs(sd_ellipsoid(p, (0.0, -0.1680, 0.0100),
                                     (0.0300, 0.0180, 0.0320))), 0.008)
    return d


def eye_points(sx):
    """Centre of one eyeball in head-local space."""
    return np.array([sx * EYE_X, EYE_Y, EYE_Z], np.float32)


def scene_distance(p, yaw=0.0, gaze=0.0, with_hair=True, with_coat=True):
    """Distance to the nearest part of the head, hair, coat and eyes."""
    d = head_distance(p, yaw, gaze)
    if with_hair:
        d = smin(d, hair_distance(p, yaw), 0.008)
    if with_coat:
        d = smin(d, coat_distance(p), 0.020)
    for sx in (-1, 1):
        d = smin(d, sd_sphere(p, eye_points(sx), EYE_R), 0.0015)
    return d


# ------------------------------------------------------------------ marcher
def march(ro, rd, *, max_dist=3.0, steps=96, eps=0.00035, yaw=0.0, gaze=0.0,
          t_min=0.002):
    """Sphere-trace the head. Returns (t, hit_mask).

    A conservative step (0.9 x the distance) keeps the march stable at the
    blends between masses, where the field is a little less than a true distance.
    """
    n = ro.shape[0]
    t = np.full(n, t_min, np.float32)
    alive = np.ones(n, bool)
    for _ in range(steps):
        p = ro + rd * t[..., None]
        d = scene_distance(p, yaw, gaze)
        hit = d < eps
        alive &= ~hit
        if not alive.any():
            break
        t = np.where(alive, t + np.maximum(d * 0.9, eps * 1.5), t)
        over = t > max_dist
        alive &= ~over
        if not alive.any():
            break
    hit = scene_distance(ro + rd * t[..., None], yaw, gaze) < eps * 2.0
    hit &= t < max_dist
    return t.astype(np.float32), hit


def normal(p, yaw=0.0, gaze=0.0, h=0.00035):
    """Tetrahedral gradient of the field: the surface normal, no smoothing."""
    k = np.array([[1, -1, -1], [-1, -1, 1], [-1, 1, -1], [1, 1, 1]], np.float32)
    n = np.zeros_like(p)
    for i in range(4):
        n += k[i] * scene_distance(p + k[i] * h, yaw, gaze)[..., None]
    return n / np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-9)


def ao(p, n, yaw=0.0, gaze=0.0, taps=5, strength=1.0):
    """Field-based ambient occlusion: five short probes along the normal."""
    occ = np.zeros(p.shape[:-1], np.float32)
    for i in range(taps):
        h = 0.004 + 0.011 * i
        d = scene_distance(p + n * h, yaw, gaze)
        occ += np.clip((h - d) / h, 0, 1)
    return np.clip(1.0 - occ / taps * strength * 1.35, 0.0, 1.0)


# ------------------------------------------------------------------- the grid
class Field:
    """The head field baked to a grid, so a march costs lookups, not ellipsoids.

    Evaluating forty blended ellipsoids per march step is far too slow for a
    720p frame; baking the field once at 2.5 mm and trilinearly interpolating
    drops the cost by more than an order of magnitude and the interpolation
    error is well under a pixel at this scale.
    """

    def __init__(self, yaw=0.0, gaze=0.0, res=0.0025,
                 lo=(-0.125, -0.205, -0.150), hi=(0.125, 0.125, 0.135)):
        self.yaw, self.gaze = yaw, gaze
        self.lo = np.asarray(lo, np.float32)
        self.hi = np.asarray(hi, np.float32)
        self.res = float(res)
        dims = np.maximum(np.ceil((self.hi - self.lo) / res).astype(int) + 1, 2)
        self.dims = tuple(int(v) for v in dims)
        xs = self.lo[0] + np.arange(self.dims[0], dtype=np.float32) * res
        ys = self.lo[1] + np.arange(self.dims[1], dtype=np.float32) * res
        zs = self.lo[2] + np.arange(self.dims[2], dtype=np.float32) * res
        g = np.empty(self.dims, np.float32)
        # fill one y-slab at a time: a (nx, nz) block of points per slab keeps the
        # working set small enough that the bake fits in a modest sandbox
        for j, y in enumerate(ys):
            X, Z = np.meshgrid(xs, zs)
            pts = np.stack([X.ravel(),
                            np.full(X.size, y, np.float32),
                            Z.ravel()], -1).astype(np.float32)
            g[:, j, :] = scene_distance(pts, yaw, gaze).reshape(len(zs), len(xs)).T
        self.grid = g

    def sample(self, p):
        q = (p - self.lo) / self.res
        q = np.clip(q, 0, np.asarray(self.dims, np.float32) - 1.001)
        i0 = q.astype(np.int32)
        f = q - i0
        x, y, z = i0[:, 0], i0[:, 1], i0[:, 2]
        fx, fy, fz = f[:, 0], f[:, 1], f[:, 2]
        g = self.grid
        c000 = g[x, y, z]; c100 = g[x + 1, y, z]
        c010 = g[x, y + 1, z]; c110 = g[x + 1, y + 1, z]
        c001 = g[x, y, z + 1]; c101 = g[x + 1, y, z + 1]
        c011 = g[x, y + 1, z + 1]; c111 = g[x + 1, y + 1, z + 1]
        c00 = c000 + (c100 - c000) * fx
        c10 = c010 + (c110 - c010) * fx
        c01 = c001 + (c101 - c001) * fx
        c11 = c011 + (c111 - c011) * fx
        c0 = c00 + (c10 - c00) * fy
        c1 = c01 + (c11 - c01) * fy
        return c0 + (c1 - c0) * fz

    def normal(self, p, h=0.0012):
        k = np.array([[1, -1, -1], [-1, -1, 1], [-1, 1, -1], [1, 1, 1]], np.float32)
        n = np.zeros_like(p)
        for i in range(4):
            n += k[i] * self.sample(p + k[i] * h)[..., None]
        return n / np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-9)

    def march(self, ro, rd, max_dist=0.9, steps=64, eps=0.0006):
        n = ro.shape[0]
        t = np.full(n, 0.004, np.float32)
        alive = np.ones(n, bool)
        for _ in range(steps):
            d = self.sample(ro + rd * t[..., None])
            hit = (d < eps) & alive
            alive &= ~hit
            if not alive.any():
                break
            t = np.where(alive, t + np.maximum(d * 0.85, eps), t)
            alive &= t < max_dist
            if not alive.any():
                break
        hit = (self.sample(ro + rd * t[..., None]) < eps * 2.5) & (t < max_dist)
        return t, hit

    def ao(self, p, nrm, taps=5, strength=1.0):
        occ = np.zeros(p.shape[0], np.float32)
        for i in range(taps):
            h = 0.004 + 0.013 * i
            occ += np.clip((h - self.sample(p + nrm * h)) / h, 0, 1)
        return np.clip(1.0 - occ / taps * strength * 1.6, 0.0, 1.0)
