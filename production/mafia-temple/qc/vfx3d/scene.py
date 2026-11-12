"""Night-temple scene graph: real solids, lights and a rigged low-poly figure.

Everything here is explicit geometry. The figure is built from capsules driven by
a small hand-authored skeleton with forward kinematics — so the walk/run come
from joint angles over time, not from moving a photo. That is the difference
between this and the earlier cuts.

Scale: 1 unit = 1 metre. Ground at y=0. The temple faces +z (towards camera).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from . import geom


@dataclass
class Material:
    name: str
    albedo: np.ndarray
    roughness: float = 0.6
    spec: float = 0.15
    emissive: np.ndarray | None = None
    fog: float = 1.0


def _c(r, g, b):
    return np.array([r, g, b], np.float32)


# ------------------------------------------------------------------ materials
MATS = {
    'ground':  Material('ground',  _c(0.030, 0.034, 0.042), 0.28, 0.30, fog=1.10),
    'stone':   Material('stone',   _c(0.062, 0.066, 0.075), 0.74, 0.10),
    'darkstone': Material('darkstone', _c(0.030, 0.035, 0.043), 0.84, 0.07),
    'wood':    Material('wood',    _c(0.075, 0.045, 0.032), 0.72, 0.10),
    'tile':    Material('tile',    _c(0.020, 0.025, 0.033), 0.46, 0.36),
    'paper':   Material('paper',   _c(0.150, 0.120, 0.078), 0.95, 0.02,
                        emissive=_c(0.085, 0.052, 0.022)),
    'lantern': Material('lantern', _c(0.900, 0.420, 0.130), 1.00, 0.00,
                        emissive=_c(1.55, 0.62, 0.20)),
    'cloth':   Material('cloth',   _c(0.130, 0.135, 0.155), 0.66, 0.22),
    'skin':    Material('skin',    _c(0.185, 0.125, 0.092), 0.62, 0.14),
    'hair':    Material('hair',    _c(0.022, 0.020, 0.020), 0.55, 0.22),
    'shirt':   Material('shirt',   _c(0.165, 0.160, 0.155), 0.78, 0.08),
}
MAT_LIST = list(MATS)
MAT_ID = {n: i for i, n in enumerate(MAT_LIST)}


@dataclass
class Box:
    centre: tuple
    half: tuple
    mat: str
    rot_z: float = 0.0          # optional yaw, baked at build time
    shape: str = 'box'
    extra: dict = field(default_factory=dict)


@dataclass
class Sphere:
    centre: tuple
    radius: float
    mat: str
    shape: str = 'sphere'


@dataclass
class Capsule:
    a: tuple
    b: tuple
    radius: float
    mat: str
    shape: str = 'capsule'


@dataclass
class Torus:
    centre: tuple
    R: float
    r: float
    mat: str
    axis: str = 'y'
    shape: str = 'torus'


@dataclass
class Light:
    """A point light, or a directional one when `detail` is a unit vector.

    Directional lights carry no distance falloff — that is what the moon is.
    Point lights use 1/d^2; giving them a physical falloff is the difference
    between a night scene and a washed-out grey room.
    """
    pos: tuple
    colour: tuple
    intensity: float
    radius: float = 0.0
    direction: tuple = None


# ------------------------------------------------------------------ the world
def build_world(with_figure=True):
    """Return (solids, lights) for the night temple.

    Axes: +x right, +y up, +z towards the audience. The hall faces +z; a torii
    gate stands on the approach and the camera cranes in along it.

    The set is deliberately compact (hall 12 m wide, 12 m from gate to hall)
    so that a 20-knots-of-wind crane shot can hold both the gate and the hall
    in one 44-degree frame. Wide sets are what made the first drafts read as
    empty fields with a shed in them.

        hall plinth   x +-5.8, z -10.6 .. -0.6, floor y 0.55
        columns       5 at x = -5.4..5.4 step 2.7, z = -0.9
        roof          eaves y 4.55 -> 6.05, overhang x +-7.6
        torii         x = +-3.7 at z = +4.0, top y 6.2
        lanterns      x = +-2.9 at z = +2.6 and -0.2
    """
    solids: list = []
    lights: list = []

    # ---- plinth with a dark floor, then the approach steps
    solids.append(Box((0, 0.275, -5.6), (6.0, 0.275, 5.0), 'stone'))
    solids.append(Box((0, 0.565, -5.6), (5.7, 0.03, 4.7), 'tile'))
    for y, z, w in ((0.08, 0.30, 3.0), (0.16, 0.05, 3.2), (0.24, -0.20, 3.4),
                    (0.32, -0.45, 3.6)):
        solids.append(Box((0, y, z), (w, 0.04, 0.14), 'stone'))

    # ---- front colonnade
    for i in range(5):
        x = -5.4 + i * 2.7
        solids.append(Box((x, 2.55, -0.9), (0.20, 1.98, 0.20), 'wood'))
        solids.append(Box((x, 0.64, -0.9), (0.30, 0.09, 0.30), 'darkstone'))
    solids.append(Box((0, 4.42, -0.9), (5.7, 0.16, 0.26), 'wood'))
    solids.append(Box((0, 3.40, -0.9), (5.7, 0.10, 0.20), 'wood'))

    # ---- side and back walls
    for x in (-5.85, 5.85):
        solids.append(Box((x, 2.55, -5.8), (0.18, 1.98, 4.9), 'darkstone'))
    solids.append(Box((0, 2.55, -10.6), (5.9, 1.98, 0.20), 'darkstone'))

    # ---- shoji screens: lit paper between the columns
    for i in range(4):
        x = -5.4 + i * 2.7 + 1.35
        for yy in (1.75, 3.05):
            solids.append(Box((x, yy, -1.6), (0.86, 0.54, 0.04), 'paper'))
        solids.append(Box((x, 2.42, -1.6), (0.88, 0.02, 0.06), 'wood'))
        solids.append(Box((x, 2.42, -1.6), (0.02, 1.35, 0.06), 'wood'))
    solids.append(Box((0, 2.30, -10.4), (2.2, 1.6, 0.05), 'paper'))

    # ---- roof: 24 eaves from the veranda line up to the ridge
    N = 24
    for i in range(N):
        f = i / (N - 1)
        y = 4.55 + f * 1.55
        hw = 7.7 - f * 5.2
        hz = 6.4 - f * 4.2
        solids.append(Box((0, y, -5.6), (hw, 0.06, hz), 'tile'))
    solids.append(Box((0, 4.47, -5.6), (7.7, 0.07, 6.4), 'darkstone'))
    # exposed rafters, and the ridge with its end ornaments
    for i in range(13):
        x = -6.9 + i * 1.15
        solids.append(Box((x, 4.36, -3.0), (0.045, 0.045, 3.4), 'wood'))
    solids.append(Box((0, 6.15, -5.6), (1.6, 0.12, 0.9), 'darkstone'))
    for x in (-1.6, 1.6):
        solids.append(Sphere((x, 6.16, -5.6), 0.17, 'darkstone'))

    # ---- torii gate
    for x in (-3.7, 3.7):
        solids.append(Box((x, 2.55, 4.0), (0.24, 2.35, 0.24), 'wood'))
        solids.append(Box((x, 0.20, 4.0), (0.34, 0.20, 0.34), 'darkstone'))
    solids.append(Box((0, 5.00, 4.0), (4.4, 0.15, 0.28), 'wood'))    # nuki
    solids.append(Box((0, 5.65, 4.0), (5.3, 0.17, 0.44), 'tile'))    # kasagi
    solids.append(Box((0, 5.42, 4.0), (4.9, 0.09, 0.34), 'wood'))    # shimaki

    # ---- lanterns hanging off the gate
    for x in (-2.2, 2.2):
        solids.append(Sphere((x, 4.25, 3.85), 0.19, 'lantern'))
        solids.append(Box((x, 4.52, 3.85), (0.015, 0.22, 0.015), 'darkstone'))
        lights.append(Light((x, 4.25, 3.85), (1.0, 0.56, 0.20), 12.0, 0.10))

    # ---- stone lanterns flanking the approach
    for z in (2.6, -0.2):
        for x in (-2.9, 2.9):
            solids.append(Box((x, 0.52, z), (0.14, 0.52, 0.14), 'stone'))
            solids.append(Box((x, 1.14, z), (0.30, 0.09, 0.30), 'stone'))
            solids.append(Box((x, 1.38, z), (0.19, 0.15, 0.19), 'lantern'))
            solids.append(Box((x, 1.60, z), (0.30, 0.05, 0.30), 'stone'))
            lights.append(Light((x, 1.38, z), (1.0, 0.54, 0.19), 7.0, 0.12))

    # ---- lanterns under the hall eave, in front of the columns
    for x in (-3.6, 0.0, 3.6):
        solids.append(Sphere((x, 3.55, -1.4), 0.21, 'lantern'))
        solids.append(Box((x, 3.86, -1.4), (0.015, 0.24, 0.015), 'darkstone'))
        lights.append(Light((x, 3.55, -1.4), (1.0, 0.60, 0.24), 11.0, 0.10))

    # ---- warm light inside, spilling through the shoji
    for x in (-3.4, 0.0, 3.4):
        lights.append(Light((x, 2.4, -3.4), (1.0, 0.62, 0.30), 8.0, 0.7))
    lights.append(Light((0, 2.3, -9.6), (1.0, 0.66, 0.34), 14.0, 0.8))

    # ---- approach: paving, gravel borders, low walls
    for i in range(9):
        z = 10.0 - i * 1.20
        solids.append(Box((0, 0.028, z), (1.45, 0.028, 0.50), 'stone'))
    for x in (-2.4, 2.4):
        solids.append(Box((x, 0.012, 4.0), (0.9, 0.012, 8.4), 'darkstone'))
    for x in (-4.9, 4.9):
        solids.append(Box((x, 0.48, 2.6), (0.18, 0.48, 7.6), 'darkstone'))
        solids.append(Box((x, 0.98, 2.6), (0.26, 0.07, 7.6), 'tile'))

    # ---- the moon: directional, one shared shadow direction for the set
    # NB: a tuple, not a numpy array — a numpy "unit vector" dataclass default is
    # the exact bug that made this the brightest object in every frame earlier.
    md = (0.46, -0.60, -0.66)
    n = math.sqrt(sum(v * v for v in md))
    md = tuple(v / n for v in md)
    lights.append(Light((0, 0, 0), (0.55, 0.68, 1.00), 1.65, 0.0, direction=md))

    if with_figure:
        solids.extend(figure_solids(pose_at(0.0, root=(0.0, 2.0))))
    return solids, lights


# ------------------------------------------------------------------ the figure
# A tiny hand-authored skeleton. Joint positions are computed by forward
# kinematics from a few angles, then capsules are emitted. No image, no mocap,
# no pre-baked mesh — so the silhouette is honest low-poly 3D.
SEGMENTS = [
    # (name, parent, length, radius, material)
    ('pelvis',  None,     0.00, 0.145, 'cloth'),
    ('spine',   'pelvis', 0.34, 0.150, 'cloth'),
    ('chest',   'spine',  0.26, 0.165, 'cloth'),
    ('neck',    'chest',  0.09, 0.062, 'skin'),
    ('head',    'neck',   0.19, 0.098, 'skin'),
    ('thighL',  'pelvis', 0.44, 0.085, 'cloth'),
    ('shinL',   'thighL', 0.42, 0.062, 'cloth'),
    ('thighR',  'pelvis', 0.44, 0.085, 'cloth'),
    ('shinR',   'thighR', 0.42, 0.062, 'cloth'),
    ('upperArmL', 'chest', 0.28, 0.058, 'cloth'),
    ('foreArmL',  'upperArmL', 0.26, 0.045, 'cloth'),
    ('upperArmR', 'chest', 0.28, 0.058, 'cloth'),
    ('foreArmR',  'upperArmR', 0.26, 0.045, 'cloth'),
]


def gait_angles(t, speed=1.0, run=False):
    """Joint angles for a walk or run cycle at phase time t (seconds).

    Frequencies are ~1.9 steps/s walking and ~3.0 steps/s running; stride
    length follows from hip amplitude. This is procedural animation, not
    reference-matched performance.
    """
    w = (2 * math.pi) * (1.6 if run else 1.05) * speed
    p = t * w
    hip = 0.62 if run else 0.40
    knee = 1.15 if run else 0.70
    arm = 0.75 if run else 0.42
    lean = 0.16 if run else 0.045
    # left and right are half a cycle apart
    thL = hip * math.sin(p)
    thR = hip * math.sin(p + math.pi)
    knL = knee * max(0.0, -math.sin(p - 0.9)) + 0.08
    knR = knee * max(0.0, -math.sin(p + math.pi - 0.9)) + 0.08
    aL = arm * math.sin(p + math.pi)
    aR = arm * math.sin(p)
    bob = (0.030 if run else 0.016) * math.cos(2 * p)
    return dict(thighL=thL, thighR=thR, kneeL=knL, kneeR=knR,
                armL=aL, armR=aR, lean=lean, bob=bob,
                elbow=0.55 if run else 0.25)


def pose_at(t, height=0.0, yaw=0.0, run=False, head_turn=0.0, root=(0.0, 0.0)):
    """World-space capsule list for the figure at time t."""
    a = gait_angles(t, run=run)
    hip_y = 0.90 + a['bob'] + height
    base = np.array([root[0], hip_y, root[1]], np.float64)

    def rot2(v, ang):
        c, s = math.cos(ang), math.sin(ang)
        return np.array([v[0] * c - v[1] * s, v[0] * s + v[1] * c])

    # forward is +z in local space; lean tilts the torso towards +z
    lean = a['lean']
    pelvis = base
    spine = pelvis + np.array([0, 0.30 * math.cos(lean), 0.30 * math.sin(lean)])
    chest = spine + np.array([0, 0.26 * math.cos(lean), 0.26 * math.sin(lean)])
    neck = chest + np.array([0, 0.10, 0.02])
    head = neck + np.array([0, 0.17, 0.01 + 0.02 * head_turn])
    head = head + np.array([0.05 * head_turn, 0, 0])

    segs = [('pelvis', pelvis, spine, 0.145, 'cloth'),
            ('spine', spine, chest, 0.150, 'cloth'),
            ('neck', chest, neck, 0.058, 'skin'),
            ('head', neck, head, 0.098, 'skin')]

    # legs: rotate in the sagittal plane around x, thigh then shin
    for side, th, kn in (('L', a['thighL'], a['kneeL']), ('R', a['thighR'], a['kneeR'])):
        sx = 0.105 if side == 'L' else -0.105
        hip = pelvis + np.array([sx, -0.04, 0.0])
        knee = hip + np.array([0, -0.44 * math.cos(th), 0.44 * math.sin(th)])
        ank = knee + np.array([0, -0.42 * math.cos(th - kn), 0.42 * math.sin(th - kn)])
        segs.append((f'thigh{side}', hip, knee, 0.088, 'cloth'))
        segs.append((f'shin{side}', knee, ank, 0.062, 'cloth'))
        # shoe: a short foot forward from the ankle
        foot = ank + np.array([0, -0.035, 0.12])
        segs.append((f'foot{side}', ank, foot, 0.052, 'cloth'))

    # arms swing opposite the legs
    for side, ar in (('L', a['armL']), ('R', a['armR'])):
        sx = 0.20 if side == 'L' else -0.20
        sh = chest + np.array([sx, -0.02, 0.0])
        el = sh + np.array([0, -0.28 * math.cos(ar), 0.28 * math.sin(ar)])
        wr = el + np.array([0, -0.26 * math.cos(ar + a['elbow']),
                            0.26 * math.sin(ar + a['elbow'])])
        segs.append((f'upperArm{side}', sh, el, 0.060, 'cloth'))
        segs.append((f'foreArm{side}', el, wr, 0.046, 'cloth'))

    if yaw:
        c, s = math.cos(yaw), math.sin(yaw)
        M = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        pivot = np.array([base[0], 0.0, base[2]])
        segs = [(n, (a0 - pivot) @ M.T + pivot, (a1 - pivot) @ M.T + pivot, r, m)
                for n, a0, a1, r, m in segs]
    return segs


def figure_solids(segs):
    return [Capsule(tuple(a), tuple(b), r, m) for _n, a, b, r, m in segs]


def head_lights(segs):
    """Cold red eye lights emitted from the head capsule during the reveal."""
    for n, a, b, r, m in segs:
        if n == 'head':
            fwd = (b - a)
            fwd = fwd / max(np.linalg.norm(fwd), 1e-6)
            mid = b - fwd * 0.035
            side = np.array([1.0, 0, 0]) * 0.035
            return [(tuple(mid + side), (1.0, 0.10, 0.06), 5.0, 0.02),
                    (tuple(mid - side), (1.0, 0.10, 0.06), 5.0, 0.02)]
    return []
