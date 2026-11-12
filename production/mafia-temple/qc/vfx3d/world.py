"""Reference-matched night-temple world: six sets, one hit.

Every solid here is explicit geometry that the ray tracer intersects. Nothing is
a billboard or a photo plate.

The six sets follow the reference cut frame for frame:

    set 'street'    S1  Edo-era alley, lanterns, wet flagstones, neon towers
    set 'temple'    S2  temple facade, eight stone lanterns, mist, cedar forest
    set 'aerial'    S3  whole temple complex from the sky, torii, path, lanterns
    set 'courtyard' S4/S5  open courtyard, vermilion hall steps, running figure
    set 'face'      S6  the head itself, built from ellipsoids and oriented boxes

Scale: 1 unit = 1 metre, ground at y=0. Sets are built lazily per shot so the
primitive list stays short and the trace stays fast.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

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
    # subsurface-ish wrap for skin: light bleeds past the terminator
    wrap: float = 0.18
    # how strongly procedural micro-detail perturbs the normal (0 = smooth)
    bump: float = 0.0
    # spatial frequency of that detail, in cycles per metre
    bump_scale: float = 60.0


def _c(r, g, b):
    return np.array([r, g, b], np.float32)


# ------------------------------------------------------------------ materials
# Values sampled against the reference: cool blue shadows, near-black stone,
# amber only where a lantern is actually burning.
MATS = {
    'ground':   Material('ground',   _c(0.020, 0.024, 0.032), 0.22, 0.34, fog=1.20,
                         bump=0.25, bump_scale=70.0),
    'stone':    Material('stone',    _c(0.048, 0.052, 0.062), 0.74, 0.14,
                         bump=0.45, bump_scale=90.0),
    'darkstone': Material('darkstone', _c(0.020, 0.024, 0.030), 0.86, 0.07),
    'moss':     Material('moss',     _c(0.030, 0.042, 0.028), 0.92, 0.03),
    'wood':     Material('wood',     _c(0.055, 0.032, 0.022), 0.74, 0.09),
    'vermilion': Material('vermilion', _c(0.210, 0.055, 0.030), 0.68, 0.14),
    'tile':     Material('tile',     _c(0.026, 0.032, 0.042), 0.40, 0.40),
    'plaster':  Material('plaster',  _c(0.055, 0.052, 0.048), 0.90, 0.05),
    'paper':    Material('paper',    _c(0.075, 0.052, 0.030), 0.95, 0.02,
                         emissive=_c(0.030, 0.014, 0.005)),
    'lantern':  Material('lantern',  _c(1.000, 0.480, 0.150), 1.00, 0.00,
                         emissive=_c(0.62, 0.235, 0.062)),
    'neon':     Material('neon',     _c(0.400, 0.700, 1.000), 1.00, 0.00,
                         emissive=_c(0.16, 0.30, 0.46)),
    'neon_red': Material('neon_red', _c(1.000, 0.200, 0.120), 1.00, 0.00,
                         emissive=_c(0.46, 0.055, 0.032)),
    'glass':    Material('glass',    _c(0.020, 0.030, 0.045), 0.10, 0.55),
    'foliage':  Material('foliage',  _c(0.014, 0.026, 0.020), 0.95, 0.02,
                         bump=0.75, bump_scale=150.0),
    # figure
    'cloth':    Material('cloth',    _c(0.020, 0.022, 0.028), 0.70, 0.16, wrap=0.05,
                         bump=0.30, bump_scale=260.0),
    'shirt':    Material('shirt',    _c(0.032, 0.034, 0.040), 0.78, 0.10, wrap=0.05,
                         bump=0.28, bump_scale=260.0),
    # skin: the reference face, warm-lit, with real wrap so it is not a mask
    'skin':     Material('skin',     _c(0.268, 0.176, 0.132), 0.64, 0.12, wrap=0.07,
                         bump=0.10, bump_scale=900.0),
    'skin_dark': Material('skin_dark', _c(0.110, 0.070, 0.054), 0.70, 0.08, wrap=0.05,
                         bump=0.08, bump_scale=900.0),
    'hair':     Material('hair',     _c(0.014, 0.012, 0.012), 0.66, 0.07, wrap=0.04,
                         bump=0.55, bump_scale=420.0),
    'stubble':  Material('stubble',  _c(0.028, 0.022, 0.019), 0.80, 0.06, wrap=0.05,
                         bump=0.30, bump_scale=1500.0),
    'lip':      Material('lip',      _c(0.128, 0.058, 0.046), 0.46, 0.30, wrap=0.08,
                         bump=0.10, bump_scale=700.0),
    'eye_white': Material('eye_white', _c(0.240, 0.225, 0.215), 0.35, 0.30),
    'iris':     Material('iris',     _c(0.140, 0.030, 0.016), 0.25, 0.55,
                         emissive=_c(0.280, 0.014, 0.005)),
    'pupil':    Material('pupil',    _c(0.006, 0.006, 0.006), 0.20, 0.10),
    'eye_glow': Material('eye_glow', _c(1.000, 0.120, 0.080), 1.00, 0.00,
                         emissive=_c(0.95, 0.045, 0.014)),
}
MAT_LIST = list(MATS)
MAT_ID = {n: i for i, n in enumerate(MAT_LIST)}


# -------------------------------------------------------------------- solids
@dataclass
class Box:
    centre: tuple
    half: tuple
    mat: str


@dataclass
class OBox:
    """Oriented box: centre, half extents, and yaw/pitch/roll in radians."""
    centre: tuple
    half: tuple
    yaw: float
    pitch: float
    roll: float
    mat: str


@dataclass
class Sphere:
    centre: tuple
    radius: float
    mat: str


@dataclass
class Ellipsoid:
    centre: tuple
    radii: tuple
    mat: str
    basis: np.ndarray | None = None


@dataclass
class Capsule:
    a: tuple
    b: tuple
    radius: float
    mat: str


@dataclass
class Light:
    pos: tuple
    colour: tuple
    intensity: float
    radius: float = 0.0
    direction: tuple = None


# ------------------------------------------------------------------- helpers
def _lantern(solids, lights, x, y, z, power=1.5, h=0.0, warm=(1.0, 0.52, 0.17)):
    """A paper lantern: a glowing box plus a small post and a cap."""
    solids.append(Box((x, y + h, z), (0.11, 0.15, 0.11), 'lantern'))
    solids.append(Box((x, y + h + 0.175, z), (0.13, 0.02, 0.13), 'darkstone'))
    solids.append(Box((x, y + h - 0.175, z), (0.13, 0.02, 0.13), 'darkstone'))
    lights.append(Light((x, y + h, z), warm, power, 0.16))


def _stone_lantern(solids, lights, x, z, scale=1.0, light=True):
    """Toro: mossy base, shaft, fire box, flared cap."""
    s = scale
    solids.append(Box((x, 0.10 * s, z), (0.30 * s, 0.10 * s, 0.30 * s), 'moss'))
    solids.append(Box((x, 0.55 * s, z), (0.10 * s, 0.35 * s, 0.10 * s), 'stone'))
    solids.append(Box((x, 0.95 * s, z), (0.26 * s, 0.06 * s, 0.26 * s), 'stone'))
    solids.append(Box((x, 1.15 * s, z), (0.17 * s, 0.14 * s, 0.17 * s), 'lantern'))
    solids.append(Box((x, 1.32 * s, z), (0.30 * s, 0.05 * s, 0.30 * s), 'stone'))
    solids.append(OBox((x, 1.42 * s, z), (0.30 * s, 0.06 * s, 0.30 * s),
                       0.0, 0.0, 0.0, 'stone'))
    if light:
        lights.append(Light((x, 1.15 * s, z), (1.0, 0.48, 0.15), 1.5 * s, 0.14))


# --------------------------------------------------------------- the figure
# A 15-segment forward-kinematic skeleton. Joint angles are procedural; the
# silhouette comes from capsules plus an ellipsoid skull, so it is real 3D
# volume rather than a cut-out.
SEGMENTS = [
    ('pelvis', None, 0.00, 0.150, 'cloth'),
    ('spine', 'pelvis', 0.30, 0.155, 'cloth'),
    ('chest', 'spine', 0.26, 0.175, 'shirt'),
    ('neck', 'chest', 0.09, 0.058, 'skin'),
    ('head', 'neck', 0.20, 0.098, 'skin'),
    ('thighL', 'pelvis', 0.46, 0.090, 'cloth'),
    ('shinL', 'thighL', 0.44, 0.064, 'cloth'),
    ('thighR', 'pelvis', 0.46, 0.090, 'cloth'),
    ('shinR', 'thighR', 0.44, 0.064, 'cloth'),
    ('upperArmL', 'chest', 0.30, 0.060, 'shirt'),
    ('foreArmL', 'upperArmL', 0.27, 0.046, 'shirt'),
    ('upperArmR', 'chest', 0.30, 0.060, 'shirt'),
    ('foreArmR', 'upperArmR', 0.27, 0.046, 'shirt'),
]


def gait_angles(t, speed=1.0, run=False):
    """Joint angles for the run/walk cycle.

    Run cadence is 2.7 strides/s with a forward lean, because the reference run
    is a sprint, not a jog. This is procedural animation, not performance capture.
    """
    w = (2 * math.pi) * ((1.35 if run else 0.95) * speed)
    p = t * w
    hip = 0.95 if run else 0.45
    knee = 1.75 if run else 0.75
    arm = 1.15 if run else 0.45
    lean = 0.34 if run else 0.06
    thL = hip * math.sin(p)
    thR = hip * math.sin(p + math.pi)
    knL = knee * max(0.0, -math.sin(p - 0.7)) + 0.10
    knR = knee * max(0.0, -math.sin(p + math.pi - 0.7)) + 0.10
    aL = arm * math.sin(p + math.pi)
    aR = arm * math.sin(p)
    bob = (0.055 if run else 0.020) * math.cos(2 * p)
    return dict(thighL=thL, thighR=thR, kneeL=knL, kneeR=knR,
                armL=aL, armR=aR, lean=lean, bob=bob,
                elbow=0.95 if run else 0.30)


def pose_at(t, root=(0.0, 0.0), yaw=0.0, run=False, lean_extra=0.0,
            head_turn=0.0, height=0.0, arms=None):
    """World-space capsule list plus the head frame for the figure."""
    a = gait_angles(t, run=run)
    hip_y = 0.92 + a['bob'] + height
    base = np.array([root[0], hip_y, root[1]], np.float64)
    lean = a['lean'] + lean_extra

    pelvis = base
    spine = pelvis + np.array([0, 0.30 * math.cos(lean), 0.30 * math.sin(lean)])
    chest = spine + np.array([0, 0.26 * math.cos(lean), 0.26 * math.sin(lean)])
    neck = chest + np.array([0, 0.11, 0.015 * math.sin(lean)])
    head_c = neck + np.array([0, 0.13, 0.012])
    head_top = neck + np.array([0, 0.27, 0.012])

    segs = [('pelvis', pelvis, spine, 0.150, 'cloth'),
            ('spine', spine, chest, 0.155, 'cloth'),
            ('chest', chest, neck, 0.175, 'shirt'),
            ('neck', neck, head_c, 0.058, 'skin'),
            ('head', head_c, head_top, 0.098, 'skin')]

    for side, th, kn in (('L', a['thighL'], a['kneeL']),
                         ('R', a['thighR'], a['kneeR'])):
        sx = 0.105 if side == 'L' else -0.105
        hip = pelvis + np.array([sx, -0.04, 0.0])
        knee = hip + np.array([0, -0.46 * math.cos(th), 0.46 * math.sin(th)])
        ank = knee + np.array([0, -0.44 * math.cos(th - kn), 0.44 * math.sin(th - kn)])
        segs.append((f'thigh{side}', hip, knee, 0.090, 'cloth'))
        segs.append((f'shin{side}', knee, ank, 0.064, 'cloth'))
        foot = ank + np.array([0, -0.035, 0.13])
        segs.append((f'foot{side}', ank, foot, 0.054, 'cloth'))

    arm_l = a['armL'] if arms is None else arms[0]
    arm_r = a['armR'] if arms is None else arms[1]
    for side, ar in (('L', arm_l), ('R', arm_r)):
        sx = 0.205 if side == 'L' else -0.205
        sh = chest + np.array([sx, -0.02, 0.0])
        el = sh + np.array([0, -0.30 * math.cos(ar), 0.30 * math.sin(ar)])
        wr = el + np.array([0, -0.27 * math.cos(ar + a['elbow']),
                            0.27 * math.sin(ar + a['elbow'])])
        segs.append((f'upperArm{side}', sh, el, 0.060, 'shirt'))
        segs.append((f'foreArm{side}', el, wr, 0.046, 'shirt'))

    if yaw or head_turn:
        c, s = math.cos(yaw), math.sin(yaw)
        M = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        pivot = np.array([base[0], 0.0, base[2]])
        segs = [(n, (a0 - pivot) @ M.T + pivot, (a1 - pivot) @ M.T + pivot, r, m)
                for n, a0, a1, r, m in segs]
        head_c = (head_c - pivot) @ M.T + pivot

    head_yaw = yaw + head_turn
    return dict(segs=segs, head_centre=tuple(head_c), head_yaw=head_yaw,
                neck=tuple(neck), torso_up=tuple(neck - pelvis))


def figure_solids(pose):
    return [Capsule(tuple(a), tuple(b), r, m) for _n, a, b, r, m in pose['segs']]


# ---------------------------------------------------------------- the head
# Local frame for every feature below: +x right, +y up, +z forward (towards the
# camera in S6). The skull and the face mass are ellipsoids; brow, lids, lips and
# ears are oriented boxes; the nose is a capsule plus a tip. The eye is three
# nested spheres (white, iris, pupil) with an emissive core for the red glow.
#
# This is a stylised sculpt built from volumes — correct silhouette, correct
# light response, real parallax when the camera moves — but it is not a scan,
# not a likeness of any person, and it has no facial rig or skin shader.
HEAD_Y = 1.615


def head_solids(centre, yaw=0.0, gaze=0.0, jaw_open=0.0):
    """A face built from volumes, not a texture.

    Local frame: +x right, +y up, +z forward (towards camera in S6). Everything
    is an ellipsoid, a lens-flat ellipsoid or a capsule. No boxes on the face: a
    box brow reads as Lego, an ellipsoid brow reads as bone.

    Stylised sculpt — real silhouette, real light response, real parallax — not a
    scan, not a likeness, and with no facial rig behind it.
    """
    cx, cy, cz = centre
    R = geom.obb_basis(yaw=yaw + gaze * 0.30)

    def P(v):
        return (np.asarray([cx, cy, cz], np.float64)
                + R @ np.asarray(v, np.float64)).tolist()

    out = []

    def E(pos, radii, mat, basis=None):
        out.append(Ellipsoid(P(pos), radii, mat, R if basis is None else basis))

    # ------------------------------------------------------------------ skull
    E((0.0, 0.004, -0.012), (0.066, 0.080, 0.077), 'skin')
    E((0.0, -0.020, 0.024), (0.061, 0.078, 0.060), 'skin')       # face plane
    E((0.0, -0.058, 0.014), (0.0425, 0.040, 0.044), 'skin')      # jaw
    E((0.0, -0.086, 0.044), (0.019, 0.016, 0.019), 'skin')       # chin
    E((0.0, -0.090, 0.052), (0.013, 0.011, 0.011), 'skin')       # chin point
    for sx in (-1, 1):
        E((sx * 0.040, -0.026, 0.034), (0.021, 0.013, 0.018), 'skin')   # cheekbone
        E((sx * 0.0330, 0.0298, 0.0620), (0.0242, 0.0072, 0.0098), 'skin')  # brow
        E((sx * 0.0325, 0.0345, 0.0662), (0.0215, 0.0028, 0.0036), 'hair')  # brow hair
    # ------------------------------------------------------------------- eyes
    for sx in (-1, 1):
        ex = sx * 0.0305
        E((ex, 0.012, 0.054), (0.026, 0.019, 0.025), 'skin_dark')   # socket
        E((ex, 0.012, 0.0705), (0.0122, 0.0122, 0.0122), 'eye_white')
        # iris, pupil, core: lens-flat discs sitting on the eyeball
        E((ex, 0.012, 0.0810), (0.0074, 0.0074, 0.0030), 'iris')
        E((ex, 0.012, 0.0832), (0.0029, 0.0029, 0.0016), 'pupil')
        E((ex, 0.012, 0.0839), (0.0026, 0.0026, 0.0015), 'eye_glow')
        # lids, the upper one overhanging the eyeball
        E((ex, 0.0215, 0.0703), (0.0154, 0.0062, 0.0108), 'skin')
        E((ex, 0.0015, 0.0700), (0.0140, 0.0042, 0.0098), 'skin')
    # ------------------------------------------------------------------- nose
    out.append(Capsule(P((0.0, 0.0175, 0.0685)), P((0.0, -0.0025, 0.0805)),
                       0.0088, 'skin'))
    E((0.0, -0.0115, 0.0842), (0.0122, 0.0102, 0.0114), 'skin')
    for sx in (-1, 1):
        E((sx * 0.0122, -0.0155, 0.0798), (0.0062, 0.0050, 0.0058), 'skin')
        E((sx * 0.0068, -0.0185, 0.0822), (0.0030, 0.0020, 0.0022), 'pupil')
    # ------------------------------------------------------------------ mouth
    # A mouth reads from the seam and the colour of the lips, not from volume.
    mo = -jaw_open * 0.006
    E((0.0, -0.0572 + mo, 0.0810), (0.0186, 0.0098, 0.0030), 'lip')
    E((0.0, -0.0570 + mo, 0.0834), (0.0178, 0.0009, 0.0020), 'skin_dark')
    for sx in (-1, 1):
        E((sx * 0.0046, -0.0408, 0.0818), (0.0032, 0.0080, 0.0030), 'skin')
    E((0.0, -0.0440, 0.0836), (0.0198, 0.0028, 0.0026), 'hair')   # moustache
    E((0.0, -0.0800, 0.0540), (0.0112, 0.0098, 0.0060), 'stubble')  # goatee
    for sx in (-1, 1):
        E((sx * 0.0290, -0.0645, 0.0330), (0.0165, 0.0170, 0.0210), 'stubble')
    # ------------------------------------------------------------------- ears
    for sx in (-1, 1):
        E((sx * 0.0655, -0.008, -0.006), (0.0048, 0.0150, 0.0105), 'skin')
        E((sx * 0.0652, -0.008, -0.006), (0.0022, 0.0105, 0.0072), 'skin_dark')
    # ------------------------------------------------------------------- hair
    E((0.0, 0.024, -0.026), (0.0755, 0.0720, 0.0800), 'hair')     # cap
    E((0.0, 0.0520, 0.0300), (0.0690, 0.0230, 0.0470), 'hair')    # hairline
    E((0.0, -0.010, -0.052), (0.0690, 0.0760, 0.0430), 'hair')    # nape
    # asymmetric by design: a perfectly mirrored hair volume reads as a helmet
    E((0.0, 0.0480, 0.0430), (0.0600, 0.0190, 0.0270), 'hair')    # fringe sweep
    for sx, k in ((-1, 1.00), (1, 1.12)):
        E((sx * 0.0530 * k, 0.0280, 0.0120), (0.0280 * k, 0.0360, 0.0490), 'hair')
        E((sx * 0.0570 * k, -0.0060, -0.0260), (0.0260, 0.0640, 0.0670), 'hair')
        E((sx * 0.0320 * k, 0.0500, 0.0270), (0.0310, 0.0180, 0.0240), 'hair')
        E((sx * 0.0590 * k, 0.0380, 0.0020), (0.0190, 0.0290, 0.0390), 'hair')
        E((sx * 0.0400 * k, 0.0570, 0.0080), (0.0230, 0.0150, 0.0330), 'hair')
    E((0.0, -0.008, -0.060), (0.062, 0.066, 0.042), 'hair')
    # ------------------------------------------------------ neck, collar, chest
    out.append(Capsule(P((0.0, -0.100, -0.012)), P((0.0, -0.126, -0.016)),
                       0.0400, 'skin_dark'))
    out.append(Capsule(P((0.0, -0.124, -0.016)), P((0.0, -0.148, -0.020)),
                       0.0470, 'skin_dark'))
    E((0.0, -0.162, -0.020), (0.062, 0.018, 0.060), 'cloth')      # collar
    # shoulders: one shoulder volume each, set back and slightly down, so the
    # line falls away from the neck the way a jacket does
    for sx in (-1, 1):
        E((sx * 0.085, -0.192, -0.090), (0.100, 0.050, 0.075), 'cloth')
    E((0.0, -0.214, -0.096), (0.180, 0.072, 0.085), 'cloth')      # chest
    E((0.0, -0.278, -0.100), (0.200, 0.085, 0.090), 'cloth')      # lower chest
    return out


def head_eye_lights(centre, yaw=0.0, gaze=0.0, power=0.0028):
    """Two red point lights at the irises, so the glow lights the socket."""
    cx, cy, cz = centre
    R = geom.obb_basis(yaw=yaw + gaze)
    lights = []
    for sx in (-1, 1):
        p = np.asarray([cx, cy, cz]) + R @ np.asarray([sx * 0.032, 0.015,
                                                       0.094])
        lights.append(Light(tuple(p.tolist()), (1.0, 0.10, 0.055), power, 0.012))
    return lights


# ------------------------------------------------------------------- the sets
def _cedar_forest(solids, lights, x0, x1, z0, z1, n=26, seed=3):
    """Dark conifer silhouettes: trunks and three tiers of foliage each."""
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = rng.uniform(x0, x1)
        z = rng.uniform(z0, z1)
        h = rng.uniform(11.0, 19.0)
        r = rng.uniform(0.09, 0.15)
        solids.append(Box((x, h * 0.40, z), (r, h * 0.40, r), 'wood'))
        base = h * 0.20
        for k in range(6):
            f = k / 5
            yy = h * 0.20 + (h * 0.72) * f
            rr = (2.6 - 2.15 * f) * (0.8 + rng.uniform(-0.12, 0.12))
            solids.append(Ellipsoid((x, yy, z), (rr, h * 0.105, rr), 'foliage'))


def build_street():
    """S1: Edo alley receding to neon towers. Wet flagstones, lanterns, no moon."""
    solids, lights = [], []
    # ground flagstones running away from camera, with gaps between courses
    for i in range(46):
        z = 9.0 - i * 1.25
        solids.append(Box((0.0, 0.012, z), (4.6, 0.012, 0.55), 'stone'))
    # building walls both sides: dark timber, regular bays, paper screens
    for side in (-1, 1):
        x = side * 5.2
        for i in range(11):
            z = 6.0 - i * 2.6
            solids.append(Box((x, 3.2, z), (0.30, 3.2, 1.25), 'wood'))
            solids.append(Box((x - side * 0.28, 2.55, z), (0.05, 0.95, 0.85),
                              'plaster'))
            if i % 3 == 0:
                solids.append(Box((x - side * 0.30, 2.35, z - 0.55),
                                  (0.03, 0.62, 0.30), 'paper'))
            # eaves over the alley
            solids.append(OBox((x - side * 0.55, 6.55, z), (1.15, 0.09, 1.30),
                               0.0, side * 0.22, 0.0, 'tile'))
        # hanging paper lanterns under the eaves: every other bay, so the alley
        # reads as a street with lights in it rather than a lit runway
        for i in range(0, 5, 2):
            z = 5.2 - i * 4.2
            _lantern(solids, lights, x - side * 0.85, 3.35, z, power=1.1)
    # far end: a lit shopfront and the neon city wall behind it
    solids.append(Box((0.0, 2.0, -17.0), (5.0, 2.0, 0.5), 'wood'))
    solids.append(Box((0.0, 1.9, -16.4), (1.6, 0.9, 0.06), 'paper'))
    for i in range(7):
        bx = -9.0 + i * 3.0
        h = 16.0 + (i % 3) * 5.0
        solids.append(Box((bx, h * 0.5, -30.0 - (i % 2) * 4.0),
                          (1.5, h * 0.5, 1.5), 'glass'))
        # window grid lit from inside, low intensity blue
        for k in range(4):
            solids.append(Box((bx, 3.5 + k * 3.0, -28.4), (1.1, 0.10, 0.06),
                              'neon'))
        lights.append(Light((bx, 8.0, -26.0), (0.35, 0.60, 1.0), 18.0, 0.0))
    # two red vertical signs, the only warm accent at the far end
    for sx in (-2.6, 2.4):
        solids.append(Box((sx, 4.2, -15.6), (0.14, 1.1, 0.06), 'neon_red'))
        lights.append(Light((sx, 4.2, -15.2), (1.0, 0.18, 0.12), 9.0, 0.0))
    # cold night sky bounce from above (no moon in this shot)
    lights.append(Light((0.0, 22.0, -6.0), (0.34, 0.46, 0.70), 14.0, 0.0))
    return solids, lights


def build_temple():
    """S2: the temple facade, straight on. Deep eaves, wooden posts, toro, mist."""
    solids, lights = [], []
    # stone steps up to the plinth
    for i in range(4):
        solids.append(Box((0.0, 0.06 + i * 0.12, 3.4 - i * 0.42),
                          (3.2 - i * 0.10, 0.06, 0.22), 'stone'))
    solids.append(Box((0.0, 0.55, -1.2), (5.6, 0.28, 4.0), 'stone'))
    solids.append(Box((0.0, 0.84, -1.2), (5.3, 0.02, 3.7), 'tile'))
    # twelve posts: the reference facade is a forest of timber
    for i in range(6):
        x = -4.4 + i * 1.76
        solids.append(Box((x, 2.60, 0.6), (0.17, 1.76, 0.17), 'wood'))
        solids.append(Box((x, 3.95, 0.6), (0.21, 0.06, 0.21), 'darkstone'))
        solids.append(Box((x, 2.60, -2.4), (0.17, 1.76, 0.17), 'wood'))
    # tie beams and a lattice transom
    solids.append(Box((0.0, 4.28, 0.6), (5.0, 0.14, 0.22), 'wood'))
    solids.append(Box((0.0, 3.10, 0.6), (5.0, 0.09, 0.18), 'wood'))
    for i in range(9):
        solids.append(Box((-4.2 + i * 1.05, 3.70, 0.6), (0.045, 0.42, 0.10),
                          'wood'))
    # the inner doorway, lit warm, with a hanging curtain
    solids.append(Box((0.0, 1.35, -0.4), (1.05, 1.05, 0.05), 'paper'))
    for i in range(5):
        solids.append(Box((-0.9 + i * 0.45, 2.55, -0.35), (0.20, 0.55, 0.02),
                          'paper'))
    # side wings, lower roofs
    for side in (-1, 1):
        solids.append(Box((side * 5.4, 2.2, -1.0), (0.9, 1.6, 3.2), 'wood'))
        for i in range(6):
            solids.append(OBox((side * 5.9, 4.35 + i * 0.16, -1.0),
                               (1.9 - i * 0.12, 0.06, 3.6 - i * 0.2),
                               0.0, side * 0.28, 0.0, 'tile'))
    # main roof: layered eave boards sweeping to a ridge
    N = 26
    for i in range(N):
        f = i / (N - 1)
        solids.append(Box((0.0, 4.55 + f * 2.35, -1.0),
                          (8.0 - f * 4.6, 0.05, 5.2 - f * 3.4), 'tile'))
    # exposed rafters under the eave: the fine structure in the reference
    for i in range(21):
        x = -7.4 + i * 0.74
        solids.append(OBox((x, 4.40, 2.1), (0.04, 0.04, 2.6), 0.0, 0.05, 0.0,
                          'wood'))
    # ridge ornaments and the two lanterns either side of the door
    solids.append(Box((0.0, 6.95, -1.0), (1.4, 0.12, 0.8), 'darkstone'))
    for sx in (-1.5, 1.5):
        solids.append(Sphere((sx, 7.02, -1.0), 0.20, 'darkstone'))
    for sx in (-1.9, 1.9):
        _lantern(solids, lights, sx, 3.35, 1.0, power=13.0)
    # eight toro down both sides of the approach
    for i, z in enumerate((3.2, 5.4, 7.6, 9.8)):
        for sx in (-3.6 - i * 0.5, 3.6 + i * 0.5):
            _stone_lantern(solids, lights, sx, z, scale=1.0 + i * 0.08)
    # warm spill from inside the hall
    for sx in (-1.6, 0.0, 1.6):
        lights.append(Light((sx, 2.2, -0.6), (1.0, 0.58, 0.26), 6.0, 0.55))
    # cedar forest behind and either side
    _cedar_forest(solids, lights, -16.0, 16.0, -18.0, -4.0, n=30, seed=5)
    _cedar_forest(solids, lights, -20.0, -9.0, -4.0, 8.0, n=14, seed=6)
    _cedar_forest(solids, lights, 9.0, 20.0, -4.0, 8.0, n=14, seed=7)
    # weak moon high behind the roof, rims the tiles
    lights.append(Light((0.0, 26.0, -14.0), (0.30, 0.42, 0.66), 60.0, 0.0))
    return solids, lights


def build_aerial():
    """S3: the whole complex from above — two halls, gate, path, lanterns."""
    solids, lights = [], []
    # courtyard: wet flagstone, dark
    solids.append(Box((0.0, 0.01, 0.0), (26.0, 0.01, 26.0), 'stone'))
    # processional path
    for i in range(16):
        solids.append(Box((0.0, 0.03, 22.0 - i * 1.5), (1.5, 0.03, 0.65), 'stone'))
    # main hall
    solids.append(Box((0.0, 0.42, -8.0), (6.2, 0.42, 4.6), 'stone'))
    for i in range(6):
        f = i / 5
        solids.append(Box((0.0, 0.95 + f * 1.9, -8.0),
                          (7.2 - f * 2.4, 0.06, 5.4 - f * 1.8), 'tile'))
    for i in range(5):
        x = -4.4 + i * 2.2
        solids.append(Box((x, 1.4, -4.6), (0.16, 0.95, 0.16), 'wood'))
    solids.append(Box((0.0, 1.15, -4.6), (2.0, 0.75, 0.05), 'paper'))
    # secondary halls left and right with their own tiled roofs
    for side in (-1, 1):
        solids.append(Box((side * 9.5, 0.35, -6.0), (3.2, 0.35, 3.0), 'stone'))
        for i in range(5):
            f = i / 4
            solids.append(Box((side * 9.5, 0.85 + f * 1.0, -6.0),
                              (3.6 - f * 1.4, 0.05, 3.4 - f * 1.2), 'tile'))
        solids.append(Box((side * 9.5, 0.85, -4.4), (1.2, 0.35, 0.05), 'paper'))
    # torii on the path
    for sx in (-2.6, 2.6):
        solids.append(Box((sx, 2.4, 12.0), (0.20, 2.4, 0.20), 'vermilion'))
    solids.append(Box((0.0, 4.55, 12.0), (3.4, 0.16, 0.26), 'vermilion'))
    solids.append(Box((0.0, 4.95, 12.0), (4.0, 0.15, 0.38), 'tile'))
    # lanterns along the path and around the halls
    for z in (16.0, 10.0, 4.0, -1.0):
        for sx in (-3.2, 3.2):
            _stone_lantern(solids, lights, sx, z, scale=1.0)
    for sx in (-6.0, 6.0, -9.5, 9.5):
        _stone_lantern(solids, lights, sx, -2.0, scale=1.1)
    # forest ring
    _cedar_forest(solids, lights, -30.0, -14.0, -26.0, 26.0, n=26, seed=11)
    _cedar_forest(solids, lights, 14.0, 30.0, -26.0, 26.0, n=26, seed=12)
    _cedar_forest(solids, lights, -14.0, 14.0, -30.0, -14.0, n=22, seed=13)
    lights.append(Light((0.0, 30.0, 6.0), (0.34, 0.46, 0.70), 40.0, 0.0))
    return solids, lights


def build_courtyard():
    """S4/S5: open courtyard in front of a vermilion hall, mist and lanterns."""
    solids, lights = [], []
    for i in range(24):
        z = 10.0 - i * 1.15
        solids.append(Box((0.0, 0.012, z), (9.0, 0.012, 0.52), 'stone'))
    # vermilion hall: raised floor, steps, posts, deep red beams
    solids.append(Box((0.0, 0.55, -5.0), (8.0, 0.55, 4.0), 'darkstone'))
    for i in range(5):
        solids.append(Box((0.0, 0.10 + i * 0.11, -0.6 + i * 0.34),
                          (3.0, 0.055, 0.18), 'stone'))
    for i in range(7):
        x = -6.6 + i * 2.2
        solids.append(Box((x, 2.35, -2.2), (0.19, 1.80, 0.19), 'vermilion'))
        solids.append(Box((x, 2.35, -7.4), (0.19, 1.80, 0.19), 'vermilion'))
    solids.append(Box((0.0, 4.20, -2.2), (7.0, 0.17, 0.24), 'vermilion'))
    solids.append(Box((0.0, 4.20, -7.4), (7.0, 0.17, 0.24), 'vermilion'))
    solids.append(Box((0.0, 4.20, -4.8), (0.22, 0.17, 2.8), 'vermilion'))
    # roof over the hall
    for i in range(14):
        f = i / 13
        solids.append(Box((0.0, 4.55 + f * 1.75, -4.8),
                          (8.4 - f * 3.0, 0.05, 5.0 - f * 2.2), 'tile'))
    # a lit interior behind the posts
    solids.append(Box((0.0, 2.0, -7.2), (5.4, 1.4, 0.06), 'paper'))
    for sx in (-3.0, 0.0, 3.0):
        lights.append(Light((sx, 2.0, -7.0), (1.0, 0.56, 0.24), 14.0, 0.7))
    # stone lanterns: the two big ones in the reference foreground
    for sx, z, s in ((-4.6, 3.6, 1.35), (4.6, 1.2, 1.15), (-5.2, -0.4, 1.0),
                     (5.4, 3.2, 1.0)):
        _stone_lantern(solids, lights, sx, z, scale=s, light=True)
    # low wall and mist-catching ground detail
    for sx in (-8.4, 8.4):
        solids.append(Box((sx, 0.55, 0.0), (0.20, 0.55, 9.0), 'darkstone'))
    lights.append(Light((0.0, 20.0, 4.0), (0.30, 0.42, 0.65), 34.0, 0.0))
    # Two cold rims from high behind the courtyard: they trace the shoulder and
    # the back of the head on the running figure, which is what makes the
    # reference S5 read as a silhouette with an edge rather than a black shape.
    for sx in (-3.6, 3.4):
        lights.append(Light((sx, 3.9, -2.6), (0.52, 0.66, 1.0), 46.0, 0.35))
    return solids, lights


def build_face():
    """S6: the head, close, with the temple far behind as bokeh-friendly depth."""
    centre = (0.0, 1.62, 0.0)
    solids = head_solids(centre, yaw=0.0, gaze=0.0)
    lights = []
    # Low warm key from the left: enough to model the cheek, nose and brow,
    # not enough to flatten the face. The reference face is mostly in shadow.
    lights.append(Light((-0.42, 1.70, 0.86), (1.0, 0.74, 0.50), 1.75, 0.12))
    # Two cold rims from behind, the strongest light on the subject: they trace
    # the cheekbone, jaw and hair and separate the head from the dark room.
    lights.append(Light((-0.74, 1.86, -0.70), (0.58, 0.74, 1.0), 1.10, 0.06))
    lights.append(Light((0.78, 1.78, -0.62), (0.62, 0.78, 1.0), 0.85, 0.06))
    # a whisper of cool fill on the shadow side so it does not go pure black
    lights.append(Light((0.55, 1.58, 0.90), (0.52, 0.56, 0.80), 0.055, 0.40))
    # the eyes themselves
    lights.extend(head_eye_lights(centre))
    # background: pillars and steps, out of focus depth cues
    for sx in (-1.9, 1.9):
        solids.append(Box((sx, 2.0, -4.6), (0.26, 2.0, 0.26), 'vermilion'))
    solids.append(Box((0.0, 4.1, -4.6), (2.4, 0.16, 0.26), 'vermilion'))
    solids.append(Box((0.0, 0.30, -3.6), (3.0, 0.30, 0.7), 'stone'))
    for i in range(4):
        solids.append(Box((0.0, 0.08 + i * 0.10, -2.8 + i * 0.36),
                          (1.8, 0.05, 0.18), 'stone'))
    lights.append(Light((0.0, 1.30, -4.6), (1.0, 0.44, 0.17), 2.2, 0.5))
    return solids, lights


BUILDERS = {
    'street': build_street,
    'temple': build_temple,
    'aerial': build_aerial,
    'courtyard': build_courtyard,
    'face': build_face,
}


def build(name):
    return BUILDERS[name]()
