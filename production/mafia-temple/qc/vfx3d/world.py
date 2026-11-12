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
    'ground':   Material('ground',   _c(0.012, 0.015, 0.021), 0.16, 0.62, fog=1.20,
                         bump=0.25, bump_scale=70.0),
    'stone':    Material('stone',    _c(0.034, 0.037, 0.045), 0.66, 0.22,
                         bump=0.45, bump_scale=90.0),
    'darkstone': Material('darkstone', _c(0.020, 0.024, 0.030), 0.86, 0.07),
    'moss':     Material('moss',     _c(0.030, 0.042, 0.028), 0.92, 0.03),
    'wood':     Material('wood',     _c(0.026, 0.017, 0.013), 0.80, 0.07),
    'vermilion': Material('vermilion', _c(0.072, 0.020, 0.013), 0.80, 0.06),
    'tile_ridge': Material('tile_ridge', _c(0.145, 0.170, 0.210), 0.24, 0.66),
    'tile':     Material('tile',     _c(0.115, 0.135, 0.170), 0.26, 0.58),
    'plaster':  Material('plaster',  _c(0.040, 0.039, 0.038), 0.92, 0.04),
    'paper_dim': Material('paper_dim', _c(0.045, 0.030, 0.017), 0.95, 0.02,
                          emissive=_c(0.030, 0.013, 0.004)),
    'paper':    Material('paper',    _c(0.075, 0.052, 0.030), 0.95, 0.02,
                         emissive=_c(0.030, 0.014, 0.005)),
    'lantern':  Material('lantern',  _c(1.000, 0.480, 0.150), 1.00, 0.00,
                         emissive=_c(0.86, 0.300, 0.070)),
    'lantern_dim': Material('lantern_dim', _c(0.30, 0.115, 0.030), 1.00, 0.00,
                            emissive=_c(0.145, 0.040, 0.008)),
    'lantern_rib': Material('lantern_rib', _c(0.135, 0.048, 0.016), 0.90, 0.05,
                            emissive=_c(0.055, 0.014, 0.003)),
    'neon':     Material('neon',     _c(0.400, 0.700, 1.000), 1.00, 0.00,
                         emissive=_c(0.16, 0.30, 0.46)),
    'neon_red': Material('neon_red', _c(1.000, 0.200, 0.120), 1.00, 0.00,
                         emissive=_c(0.46, 0.055, 0.032)),
    'glass':    Material('glass',    _c(0.020, 0.030, 0.045), 0.10, 0.55),
    'foliage':  Material('foliage',  _c(0.014, 0.026, 0.020), 0.95, 0.02,
                         bump=0.75, bump_scale=150.0),
    # figure
    'cloth':    Material('cloth',    _c(0.0115, 0.0125, 0.0160), 0.62, 0.22, wrap=0.05,
                         bump=0.30, bump_scale=260.0),
    'shirt':    Material('shirt',    _c(0.0160, 0.0170, 0.0205), 0.74, 0.14, wrap=0.05,
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
    'lip':      Material('lip',      _c(0.098, 0.048, 0.042), 0.52, 0.22, wrap=0.08,
                         bump=0.10, bump_scale=700.0),
    'eye_white': Material('eye_white', _c(0.240, 0.225, 0.215), 0.35, 0.30),
    'iris':     Material('iris',     _c(0.140, 0.030, 0.016), 0.25, 0.55,
                         emissive=_c(0.280, 0.014, 0.005)),
    'pupil':    Material('pupil',    _c(0.006, 0.006, 0.006), 0.20, 0.10),
    'eye_glow': Material('eye_glow', _c(1.000, 0.120, 0.080), 1.00, 0.00,
                         emissive=_c(0.62, 0.030, 0.010)),
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
def _lantern(solids, lights, x, y, z, power=1.5, h=0.0, warm=(1.0, 0.52, 0.17),
             scale=1.0):
    """A chochin: a ribbed paper lantern hanging from a short cord.

    The body is an ellipsoid, because a lantern is a rounded volume and a box
    reads as a glowing cube at any angle. Three proud ribs and two dark caps give
    it the silhouette of the reference's paper lanterns.
    """
    sc = scale
    cy = y + h
    solids.append(Ellipsoid((x, cy, z), (0.105 * sc, 0.150 * sc, 0.105 * sc),
                            'lantern'))
    for k in (-0.55, 0.0, 0.55):
        solids.append(Ellipsoid((x, cy + k * 0.150 * sc, z),
                                (0.108 * sc, 0.006 * sc, 0.108 * sc),
                                'lantern_rib'))
    solids.append(Ellipsoid((x, cy + 0.150 * sc, z),
                            (0.036 * sc, 0.016 * sc, 0.036 * sc), 'darkstone'))
    solids.append(Ellipsoid((x, cy - 0.152 * sc, z),
                            (0.030 * sc, 0.014 * sc, 0.030 * sc), 'darkstone'))
    solids.append(Box((x, cy + 0.235 * sc, z), (0.008, 0.085 * sc, 0.008),
                      'darkstone'))
    lights.append(Light((x, cy, z), warm, power, 0.13 * sc))


def _stone_lantern(solids, lights, x, z, scale=1.0, light=True):
    """Toro: mossy base, shaft, fire box, flared cap."""
    s = scale
    solids.append(Box((x, 0.10 * s, z), (0.30 * s, 0.10 * s, 0.30 * s), 'moss'))
    solids.append(Box((x, 0.55 * s, z), (0.10 * s, 0.35 * s, 0.10 * s), 'stone'))
    solids.append(Box((x, 0.95 * s, z), (0.26 * s, 0.06 * s, 0.26 * s), 'stone'))
    # fire box: a small cell, lit only through two pierced windows
    solids.append(Box((x, 1.15 * s, z), (0.115 * s, 0.105 * s, 0.115 * s),
                      'darkstone'))
    solids.append(Box((x, 1.15 * s, z + 0.118 * s), (0.070 * s, 0.062 * s, 0.006),
                      'lantern_dim'))
    solids.append(Box((x, 1.15 * s, z - 0.118 * s), (0.070 * s, 0.062 * s, 0.006),
                      'lantern_dim'))
    for k in (-1, 1):
        solids.append(Box((x + k * 0.118 * s, 1.15 * s, z),
                          (0.006, 0.062 * s, 0.070 * s), 'lantern_dim'))
    solids.append(Box((x, 1.26 * s, z), (0.185 * s, 0.030 * s, 0.185 * s), 'stone'))
    # flared cap: four sloped faces, which is what makes a toro read as a roof
    for k in (-1, 1):
        solids.append(OBox((x, 1.325 * s, z + k * 0.075 * s),
                           (0.200 * s, 0.028 * s, 0.115 * s), 0.0, k * 0.34, 0.0,
                           'stone'))
        solids.append(OBox((x + k * 0.075 * s, 1.325 * s, z),
                           (0.115 * s, 0.028 * s, 0.200 * s), 0.0, 0.0, -k * 0.34,
                           'stone'))
    solids.append(Ellipsoid((x, 1.40 * s, z), (0.045 * s, 0.045 * s, 0.045 * s),
                            'stone'))
    if light:
        lights.append(Light((x, 1.15 * s, z), (1.0, 0.46, 0.14), 0.55 * s,
                            0.10))


# --------------------------------------------------------------- the figure
# A 15-segment forward-kinematic skeleton. Joint angles are procedural; the
# silhouette comes from capsules plus an ellipsoid skull, so it is real 3D
# volume rather than a cut-out.
SEGMENTS = [
    ('pelvis', None, 0.00, 0.150, 'cloth'),
    ('spine', 'pelvis', 0.30, 0.155, 'cloth'),
    ('chest', 'spine', 0.26, 0.175, 'shirt'),
    ('neck', 'chest', 0.09, 0.058, 'skin'),
    ('head', 'neck', 0.185, 0.070, 'skin'),
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
            ('head', head_c, head_top, 0.070, 'skin')]

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
    """The man: capsules for the body, plus a hair cap on the head.

    A capsule head with no hair reads as a bald mannequin at any distance, and
    this figure is on screen at 4-8 m in S1 and S4.
    """
    out = [Capsule(tuple(a), tuple(b), r, m) for _n, a, b, r, m in pose['segs']]
    hc = np.asarray(pose['head_centre'], np.float64)
    # the capsule runs from head_centre up to head_top (0.185 m), so the skull's
    # centre is about 9 cm above head_centre; a hair mass centred on head_centre
    # itself ends up round the neck
    hc = hc + np.array([0.0, 0.092, 0.0])
    R = geom.obb_basis(yaw=pose['head_yaw'])
    # pose['head_centre'] is the BASE of the head capsule, so the skull's centre
    # is about 8 cm above it. Offsetting the hair from the base left the skin
    # capsule poking out of the top of the hair like a bald crown.
    for c, r, mat in (((0.0, 0.020, -0.006), (0.082, 0.070, 0.088), 'hair'),
                      ((0.0, -0.004, -0.014), (0.078, 0.052, 0.082), 'hair'),
                      ((0.0, 0.038, -0.008), (0.064, 0.042, 0.072), 'hair')):
        out.append(Ellipsoid(tuple((hc + R @ np.asarray(c)).tolist()), r, mat, R))
    return out


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
    """A face assembled from anatomical masses, not a texture.

    Local frame: +x right, +y up, +z forward (towards camera in S6), origin
    between the eyes. Measured proportions for a 0.219 m head:

        crown        +0.102      brow ridge  +0.004   front z 0.062
        eye line     -0.012      eyeball     z 0.050 (front 0.062)
        nose base    -0.052      nose tip    z 0.079
        mouth line   -0.082      chin        -0.117, front z 0.056

    There is deliberately no single "face plate" ellipsoid. A face reads as a
    face because the eye area is *recessed*: the brow, the cheek mounds and the
    nose bridge are separate volumes whose fronts sit 8-17 mm in front of the
    eyeballs, while the mid-face between them stays back. One big ellipsoid in
    front of the eyes hides them completely, which is what the first pass did.

    Stylised sculpt — real silhouette, real light response, real parallax — not a
    scan, not a likeness of any person, and with no facial rig behind it.
    """
    cx, cy, cz = centre
    R = geom.obb_basis(yaw=yaw + gaze * 0.30)

    def P(v):
        return (np.asarray([cx, cy, cz], np.float64)
                + R @ np.asarray(v, np.float64)).tolist()

    out = []

    def E(pos, radii, mat, basis=None):
        out.append(Ellipsoid(P(pos), radii, mat, R if basis is None else basis))

    # ---------------------------------------------------------------- cranium
    E((0.0, 0.030, -0.014), (0.0705, 0.0710, 0.0770), 'skin')
    E((0.0, 0.040, 0.006), (0.0640, 0.0440, 0.0620), 'skin')      # forehead
    for sx in (-1, 1):
        E((sx * 0.0520, 0.012, -0.014), (0.0210, 0.0430, 0.0500), 'skin')

    # ------------------------------------------------------- mid-face, kept back
    E((0.0, -0.0300, -0.0060), (0.0560, 0.0430, 0.0560), 'skin')
    # brow: one ridge per side, fronts at z 0.062, angled down to the glabella
    for sx in (-1, 1):
        E((sx * 0.0270, 0.0030, 0.0430), (0.0330, 0.0105, 0.0200), 'skin')
        E((sx * 0.0265, 0.0105, 0.0460), (0.0250, 0.0032, 0.0048), 'hair')
    E((0.0, 0.0010, 0.0450), (0.0165, 0.0110, 0.0180), 'skin')    # glabella
    # cheek mounds: front at z 0.058, below and outside the eyes
    for sx in (-1, 1):
        E((sx * 0.0390, -0.0390, 0.0300), (0.0280, 0.0210, 0.0290), 'skin')
        E((sx * 0.0430, -0.0300, 0.0200), (0.0210, 0.0180, 0.0250), 'skin')
    # temples, so the brow does not hang in the air
    for sx in (-1, 1):
        E((sx * 0.0560, -0.0080, 0.0060), (0.0150, 0.0250, 0.0300), 'skin')

    # ---------------------------------------------------------------- eye area
    for sx in (-1, 1):
        ex = sx * 0.0292
        # shallow dark socket behind the eyeball; the brow and cheeks do the
        # recessing, this only stops the gap reading as a lit hole
        E((ex, -0.0120, 0.0300), (0.0215, 0.0175, 0.0190), 'skin_dark')
        E((ex, -0.0120, 0.0495), (0.0122, 0.0122, 0.0122), 'eye_white')
        E((ex, -0.0123, 0.0600), (0.0076, 0.0076, 0.0026), 'iris')
        E((ex, -0.0123, 0.0622), (0.0030, 0.0030, 0.0016), 'pupil')
        E((ex, -0.0123, 0.0628), (0.0024, 0.0024, 0.0012), 'eye_glow')
        # lids: thin shells wrapping the top and bottom of the eyeball
        E((ex + sx * 0.0006, -0.0035, 0.0495), (0.0138, 0.0056, 0.0118), 'skin')
        E((ex, -0.0222, 0.0488), (0.0128, 0.0036, 0.0106), 'skin')
        E((sx * 0.0428, -0.0120, 0.0395), (0.0044, 0.0112, 0.0112), 'skin')

    # ------------------------------------------------------------------- nose
    # bridge stands 15 mm proud of the mid-face, tip at z 0.079
    out.append(Capsule(P((0.0, 0.0070, 0.0520)), P((0.0, -0.0400, 0.0660)),
                       0.0098, 'skin'))
    E((0.0, -0.0500, 0.0680), (0.0135, 0.0120, 0.0128), 'skin')
    for sx in (-1, 1):
        E((sx * 0.0150, -0.0540, 0.0620), (0.0074, 0.0062, 0.0076), 'skin')
        E((sx * 0.0082, -0.0578, 0.0658), (0.0030, 0.0024, 0.0026), 'pupil')

    # ------------------------------------------------------- jaw and lower face
    E((0.0, -0.0700, 0.0260), (0.0455, 0.0310, 0.0450), 'skin')
    E((0.0, -0.0955, 0.0420), (0.0230, 0.0195, 0.0225), 'skin')    # chin pad
    E((0.0, -0.0790, 0.0480), (0.0290, 0.0210, 0.0270), 'skin')    # chin front
    for sx in (-1, 1):
        E((sx * 0.0455, -0.0550, -0.0100), (0.0115, 0.0290, 0.0250), 'skin')

    # ------------------------------------------------------------------ mouth
    mo = -jaw_open * 0.006
    E((0.0, -0.0762 + mo, 0.0600), (0.0198, 0.0052, 0.0056), 'lip')
    E((0.0, -0.0845 + mo, 0.0596), (0.0190, 0.0064, 0.0058), 'lip')
    E((0.0, -0.0805 + mo, 0.0632), (0.0196, 0.0009, 0.0020), 'skin_dark')
    for sx in (-1, 1):
        E((sx * 0.0208, -0.0805 + mo, 0.0570), (0.0036, 0.0040, 0.0036), 'lip')

    # ------------------------------------------- stubble, moustache and goatee
    # thin and close to the skin: a beard is shadow, not a mask
    E((0.0, -0.0712, 0.0640), (0.0175, 0.0026, 0.0028), 'stubble')
    for sx in (-1, 1):
        E((sx * 0.0125, -0.0725, 0.0620), (0.0092, 0.0022, 0.0024), 'stubble')
    E((0.0, -0.1040, 0.0455), (0.0115, 0.0100, 0.0058), 'stubble')
    E((0.0, -0.0945, 0.0520), (0.0165, 0.0105, 0.0048), 'stubble')
    for sx in (-1, 1):
        E((sx * 0.0330, -0.0755, 0.0240), (0.0180, 0.0195, 0.0235), 'stubble')
        E((sx * 0.0450, -0.0580, 0.0140), (0.0128, 0.0150, 0.0195), 'stubble')

    # ------------------------------------------------------------------- ears
    for sx in (-1, 1):
        E((sx * 0.0668, -0.0140, -0.0180), (0.0042, 0.0160, 0.0112), 'skin')
        E((sx * 0.0660, -0.0140, -0.0180), (0.0022, 0.0108, 0.0076), 'skin_dark')

    # ------------------------------------------------------------------- hair
    E((0.0, 0.0380, -0.0300), (0.0765, 0.0700, 0.0820), 'hair')      # cap
    E((0.0, -0.0120, -0.0580), (0.0705, 0.0800, 0.0440), 'hair')     # nape
    # hairline: five overlapping masses with different tilt, so the edge is a
    # ragged line and not a band across the forehead
    E((0.0, 0.0655, 0.0250), (0.0680, 0.0150, 0.0400), 'hair')
    E((-0.028, 0.0615, 0.0400), (0.0330, 0.0130, 0.0290), 'hair')
    E((0.031, 0.0665, 0.0360), (0.0300, 0.0125, 0.0275), 'hair')
    E((0.006, 0.0730, 0.0180), (0.0390, 0.0130, 0.0330), 'hair')
    E((0.0, 0.0560, 0.0480), (0.0510, 0.0130, 0.0230), 'hair')       # fringe sweep
    for sx, k in ((-1, 1.00), (1, 1.11)):
        E((sx * 0.0560 * k, 0.0240, 0.0010), (0.0270 * k, 0.0400, 0.0520), 'hair')
        E((sx * 0.0600 * k, -0.0190, -0.0300), (0.0245, 0.0620, 0.0680), 'hair')
        E((sx * 0.0355 * k, 0.0620, 0.0230), (0.0315, 0.0155, 0.0250), 'hair')
        E((sx * 0.0625 * k, 0.0410, -0.0040), (0.0195, 0.0300, 0.0400), 'hair')

    # ------------------------------------------------------- neck and shoulders
    out.append(Capsule(P((0.0, -0.1080, -0.0080)), P((0.0, -0.1520, -0.0180)),
                       0.0400, 'skin_dark'))
    E((0.0, -0.1700, -0.0220), (0.0620, 0.0170, 0.0600), 'cloth')
    for sx in (-1, 1):
        E((sx * 0.0900, -0.2000, -0.0940), (0.1030, 0.0520, 0.0780), 'cloth')
    E((0.0, -0.2240, -0.1000), (0.1860, 0.0740, 0.0880), 'cloth')
    E((0.0, -0.2900, -0.1040), (0.2050, 0.0870, 0.0930), 'cloth')
    return out


def head_eye_lights(centre, yaw=0.0, gaze=0.0, power=0.0028):
    """Two red point lights at the irises, so the glow lights the socket."""
    cx, cy, cz = centre
    R = geom.obb_basis(yaw=yaw + gaze)
    lights = []
    for sx in (-1, 1):
        p = np.asarray([cx, cy, cz]) + R @ np.asarray([sx * 0.0315, -0.0123,
                                                       0.0655])
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
    """S1: a narrow Edo alley opening onto a neon megacity, at night, wet.

    Composition is taken from the reference frame at 0.8 s: the alley walls are
    low enough that the eaves and the sky slot are visible, the far end opens out
    rather than closing, and the towers sit deep in haze so they read as
    silhouettes with lit windows, not as a wall of stripes.
    """
    solids, lights = [], []
    HALF = 3.05                      # alley half-width in metres
    WALL_H = 3.15                    # eave height; the sky slot above is visible

    # ---- ground: wet flagstone. Courses run across the alley, one every 0.9 m.
    for i in range(34):
        z = 14.0 - i * 0.9
        solids.append(Box((0.0, 0.010, z), (HALF + 0.4, 0.010, 0.40), 'stone'))

    # ---- alley walls: timber ground floor, plaster above, tile eaves
    for side in (-1, 1):
        x = side * HALF
        for i in range(15):
            z = 12.0 - i * 2.2
            solids.append(Box((x, WALL_H * 0.5, z), (0.18, WALL_H * 0.5, 1.05),
                              'wood'))
            # dark plaster above the timber, under the eave
            solids.append(Box((x + side * 0.10, WALL_H + 0.30, z),
                              (0.10, 0.30, 1.05), 'plaster'))
            # lattice window on every third bay, lit faintly from inside
            if i % 3 == 1:
                solids.append(Box((x - side * 0.16, 1.55, z), (0.04, 0.55, 0.42),
                                  'paper'))
                lights.append(Light((x - side * 0.55, 1.55, z),
                                    (1.0, 0.62, 0.30), 0.55, 0.25))
            if i % 3 == 0:
                # a slatted wooden screen on the opposite beat, so the rhythm is
                # not a metronome
                for k in range(4):
                    solids.append(Box((x - side * 0.15, 1.35 + k * 0.16, z),
                                      (0.03, 0.05, 0.40), 'wood'))
            # eave: projects inward and is the dark band at the top of frame
            solids.append(OBox((x - side * 0.52, WALL_H + 0.62, z),
                               (0.62, 0.07, 1.12), 0.0, side * 0.30, 0.0, 'tile'))
            solids.append(Box((x - side * 0.24, WALL_H + 0.30, z),
                              (0.06, 0.12, 1.10), 'darkstone'))

        # paper lanterns hung off the eaves: the reference's dominant warm accent
        for i, z in enumerate((10.0, 5.0, 0.2, -4.6)):
            _lantern(solids, lights, x - side * 0.72, 2.35, z, power=5.5)

    # ---- far end: the alley continues into a lit cross-street
    solids.append(Box((0.0, 1.75, -18.2), (HALF + 1.2, 1.75, 0.35), 'wood'))
    solids.append(Box((0.0, 1.55, -17.7), (1.05, 0.85, 0.05), 'paper'))
    lights.append(Light((0.0, 1.55, -17.2), (1.0, 0.55, 0.24), 6.0, 0.6))
    # hanging signs and a red lantern cluster at the crossing
    for sx, yy in ((1.35, 2.6), (-1.5, 2.9)):
        solids.append(Box((sx, yy, -16.9), (0.13, 0.55, 0.05), 'paper'))
        lights.append(Light((sx, yy, -16.5), (1.0, 0.50, 0.22), 2.2, 0.3))

    # ---- the megacity: block towers deep in haze, only windows read
    rng = np.random.default_rng(21)
    for i in range(16):
        bx = -34.0 + i * 4.4 + rng.uniform(-1.2, 1.2)
        bz = -72.0 - rng.uniform(0.0, 34.0)
        hw = rng.uniform(1.6, 3.4)
        hh = rng.uniform(14.0, 46.0)
        solids.append(Box((bx, hh * 0.5, bz), (hw, hh * 0.5, rng.uniform(1.8, 3.4)),
                          'glass'))
        # window rows: small emissive slats, never a full-height stripe
        rows = int(hh / 2.6)
        for k in range(rows):
            if rng.random() < 0.45:
                continue
            wy = 2.2 + k * 2.6
            ww = hw * rng.uniform(0.35, 0.75)
            solids.append(Box((bx + rng.uniform(-0.4, 0.4), wy,
                               bz + rng.uniform(1.8, 3.4)),
                              (ww, 0.055, 0.04),
                              'neon' if rng.random() < 0.62 else 'paper'))
        lights.append(Light((bx, hh * 0.55, bz + 8.0), (0.34, 0.58, 1.0),
                            46.0, 0.0))
    # one red broadcast mast, the strongest coloured light in the distance
    solids.append(Box((2.2, 26.0, -86.0), (0.20, 26.0, 0.20), 'glass'))
    solids.append(Box((2.2, 34.0, -85.8), (0.30, 0.30, 0.10), 'neon_red'))
    lights.append(Light((2.2, 34.0, -85.0), (1.0, 0.16, 0.10), 120.0, 0.0))
    # the cloud ceiling the reference glows against
    lights.append(Light((0.0, 30.0, -40.0), (0.26, 0.38, 0.62), 70.0, 6.0))
    return solids, lights


def build_temple():
    """S2: the temple facade, straight on. Deep eaves, timber posts, toro, mist.

    Composition is read off the reference frame at 6.3 s: the roof fills the top
    half with a shallow eave that kinks into a steep pitch, the eave line curves
    up at both ends, the veranda railing runs the full width, and mossy stone
    lanterns stand in the near foreground either side.
    """
    solids, lights = [], []

    # ---------------------------------------------------------- approach stair
    for i in range(9):
        z = 6.6 - i * 0.42
        y = 0.055 + i * 0.062
        hw = 2.30 - i * 0.05
        solids.append(Box((0.0, y, z), (hw, 0.031, 0.21), 'stone'))
        solids.append(Box((0.0, y + 0.031, z - 0.20), (hw, 0.006, 0.012),
                          'tile_ridge'))
    for sx in (-1, 1):
        solids.append(OBox((sx * 2.55, 0.34, 4.9), (0.22, 0.30, 2.1),
                           0.0, 0.0, sx * 0.10, 'stone'))

    # ------------------------------------------------------------------ plinth
    solids.append(Box((0.0, 0.52, -1.2), (5.9, 0.30, 4.2), 'stone'))
    solids.append(Box((0.0, 0.84, -1.2), (5.6, 0.03, 3.9), 'tile_ridge'))
    # veranda railing across the front
    solids.append(Box((0.0, 1.04, 2.30), (3.3, 0.045, 0.05), 'wood'))
    solids.append(Box((0.0, 0.88, 2.30), (3.3, 0.030, 0.04), 'wood'))
    for i in range(14):
        solids.append(Box((-3.15 + i * 0.485, 0.96, 2.30), (0.028, 0.09, 0.035),
                          'wood'))

    # ------------------------------------------------------------------- posts
    for i in range(6):
        x = -4.6 + i * 1.84
        for zz in (1.55, -2.60):
            solids.append(Box((x, 2.62, zz), (0.185, 1.80, 0.185), 'wood'))
            solids.append(Box((x, 4.42, zz), (0.235, 0.075, 0.235), 'darkstone'))
        # bracket set: three stacked blocks stepping outboard
        for k in range(3):
            solids.append(Box((x, 4.02 + k * 0.12, 1.55),
                              (0.20 + k * 0.10, 0.045, 0.20 + k * 0.10),
                              'wood'))
    # tie beams and the lattice transom between the posts
    solids.append(Box((0.0, 4.50, 1.55), (5.4, 0.16, 0.24), 'wood'))
    solids.append(Box((0.0, 3.30, 1.55), (5.4, 0.085, 0.19), 'wood'))
    solids.append(Box((0.0, 4.12, 1.55), (5.4, 0.06, 0.17), 'wood'))
    for i in range(11):
        solids.append(Box((-4.5 + i * 0.9, 3.80, 1.55), (0.042, 0.36, 0.10),
                          'wood'))

    # ------------------------------------------------------- the doorway, lit
    solids.append(Box((0.0, 1.62, 0.40), (1.10, 1.15, 0.06), 'paper'))
    for i in range(5):
        solids.append(Box((-0.95 + i * 0.475, 2.72, 0.46), (0.21, 0.30, 0.03),
                          'paper'))
    for sx in (-1.30, 1.30):
        solids.append(Box((sx, 1.62, 0.40), (0.09, 1.15, 0.09), 'wood'))

    # ---------------------------------------------------------- side wings
    for side in (-1, 1):
        solids.append(Box((side * 7.4, 2.30, -1.2), (1.55, 1.55, 3.6), 'wood'))
        for i in range(7):
            f = i / 6.0
            solids.append(Box((side * 7.4, 4.10 + f * 1.55, -1.2),
                              (1.85 - f * 0.55, 0.045, 3.9 - f * 1.25), 'tile'))
            solids.append(Box((side * 7.4, 4.10 + f * 1.55, -1.2 + 2.65 - f * 0.85),
                              (1.85 - f * 0.55, 0.026, 0.05), 'tile_ridge'))
        # a lit window on each wing, so the flanks are not dead black
        solids.append(Box((side * 5.95, 2.15, 0.4), (0.05, 0.42, 0.62), 'paper'))
        lights.append(Light((side * 5.4, 2.15, 0.4), (1.0, 0.58, 0.26), 2.2, 0.3))

    # ------------------------------------------------------------------ roof
    # Two pitches: a shallow eave out to the drip line, then a steep upper slope,
    # with the eave line curving up at the corners. Courses every 0.30 m carry a
    # row of half-round tiles; that corduroy is the reference roof's texture.
    COURSES = 22
    for i in range(COURSES):
        f = i / (COURSES - 1)
        # eave (f<0.45) is shallow, upper pitch steeper
        if f < 0.45:
            t = f / 0.45
            y = 4.32 + t * 0.72
            hz = 5.55 - t * 1.35
            hx = 8.55 - t * 0.35
        else:
            t = (f - 0.45) / 0.55
            y = 5.04 + t ** 1.25 * 3.35
            hz = 4.20 - t * 3.05
            hx = 8.20 - t * 5.15
        solids.append(Box((0.0, y, -1.2), (hx, 0.042, hz), 'tile'))
        # raised lip at the drip edge of each course
        solids.append(Box((0.0, y + 0.050, -1.2 + hz - 0.055),
                          (hx, 0.026, 0.05), 'tile_ridge'))
        # half-round tiles down the slope, at the course spacing, 3 per metre
        cols = max(int(hx * 2 * 0.60), 5)
        for k in range(cols):
            tx = -hx + (k + 0.5) * (2 * hx / cols)
            solids.append(Box((tx, y + 0.048, -1.2),
                              (0.058, 0.026, hz), 'tile_ridge'))
    # the continuous shell under the courses. Without it the shrinking courses
    # read as steps; with it they read as tiles on a slope.
    for i in range(30):
        f = i / 29.0
        if f < 0.45:
            t = f / 0.45
            y = 4.30 + t * 0.72
            hz = 5.60 - t * 1.35
            hx = 8.60 - t * 0.35
        else:
            t = (f - 0.45) / 0.55
            y = 5.02 + t ** 1.25 * 3.35
            hz = 4.25 - t * 3.05
            hx = 8.25 - t * 5.15
        solids.append(Box((0.0, y - 0.030, -1.2), (hx + 0.02, 0.032, hz + 0.02),
                          'tile'))
    # the eave edge itself: a fascia board and a drip gutter
    solids.append(Box((0.0, 4.30, 4.34), (8.60, 0.075, 0.06), 'darkstone'))
    solids.append(Box((0.0, 4.22, 4.30), (8.65, 0.035, 0.09), 'wood'))
    # upturned corners: the ends of the eave lift
    for sx in (-1, 1):
        for k in range(4):
            solids.append(OBox((sx * (8.0 + k * 0.26), 4.34 + k * 0.115, 4.20),
                               (0.30, 0.048, 0.55 - k * 0.08),
                               0.0, 0.0, sx * (0.16 + k * 0.11), 'tile_ridge'))
        # barge board up the gable, and the ornamental end of the ridge
        for k in range(6):
            f = k / 5.0
            solids.append(OBox((sx * (5.05 - f * 2.45), 5.10 + f * 3.25, -1.2),
                               (0.09, 0.10, 4.25 - f * 3.05), 0.0, 0.0,
                               -sx * 0.62, 'darkstone'))
    # gable wall and ridge
    for k in range(8):
        f = k / 7.0
        solids.append(Box((0.0, 5.05 + f * 3.30, -1.2), (0.12, 0.25,
                                                         4.15 - f * 2.95),
                          'plaster'))
    solids.append(Box((0.0, 8.48, -1.2), (2.65, 0.145, 1.35), 'darkstone'))
    solids.append(Box((0.0, 8.64, -1.2), (2.80, 0.075, 1.45), 'tile_ridge'))
    for sx in (-1, 1):
        solids.append(Ellipsoid((sx * 2.80, 8.72, -1.2), (0.17, 0.22, 0.24),
                                'darkstone'))
    # exposed rafters under the eave, catching the lantern light
    for i in range(34):
        x = -8.3 + i * 0.505
        solids.append(Box((x, 4.14, 3.05), (0.042, 0.052, 1.30), 'wood'))

    # ------------------------------------------------------- lanterns and toro
    for sx in (-1.62, 1.62):
        _lantern(solids, lights, sx, 3.42, 2.05, power=3.2, scale=0.92,
                 warm=(1.0, 0.55, 0.20))
        solids.append(Box((sx, 3.62, 2.05), (0.012, 0.11, 0.012), 'darkstone'))
    for sx in (-1.30, 1.30):
        lights.append(Light((sx, 1.62, 0.30), (1.0, 0.58, 0.26), 3.4, 0.55))
    lights.append(Light((0.0, 2.30, 0.20), (1.0, 0.54, 0.22), 5.0, 0.8))
    # eight toro flanking the approach, biggest nearest camera
    for i, z in enumerate((6.2, 8.4, 10.6, 12.8)):
        s = 1.02 + i * 0.075
        for sx in (-3.35 - i * 0.42, 3.35 + i * 0.42):
            _stone_lantern(solids, lights, sx, z, scale=s)

    # ---------------------------------------------------------- forest and sky
    _cedar_forest(solids, lights, -17.0, 17.0, -20.0, -5.0, n=30, seed=5)
    _cedar_forest(solids, lights, -22.0, -9.5, -5.0, 12.0, n=16, seed=6)
    _cedar_forest(solids, lights, 9.5, 22.0, -5.0, 12.0, n=16, seed=7)
    # framing: two big cedars close to the lens crop the frame in
    for sx, zz, rr in ((-1, 12.0, 0.66), (1, 9.4, 0.58), (-1, 16.5, 0.90),
                       (1, 17.0, 0.78)):
        solids.append(Box((sx * 9.0, 7.0, zz), (rr, 7.0, rr), 'wood'))
        for k in range(3):
            solids.append(Ellipsoid((sx * 9.0, 9.2 + k * 2.3, zz),
                                    (rr * 4.0, 2.1, rr * 4.0), 'foliage'))
    # weak moon high behind the roof, rimming the tiles and the ridge
    lights.append(Light((0.0, 27.0, -16.0), (0.34, 0.46, 0.72), 90.0, 0.0))
    return solids, lights


def build_aerial():
    """S3: the whole complex from the sky — halls, gate, path, lanterns, mist.

    Read off the reference at 10.5 s: a high three-quarter view looking down the
    axis, the main hall at the top of frame behind a broad paved court, two
    side halls, a torii and a gate at the bottom, lantern fires strung along the
    path, forest pressing in on all four sides and mist lying in the courtyard.
    """
    solids, lights = [], []

    def hip_roof(cx, cz, hx, hz, y0, height, mat='tile', ridge_mat='tile_ridge',
                 steps=12):
        """A hipped roof: courses shrinking in both axes to a short ridge."""
        for i in range(steps):
            f = i / (steps - 1)
            y = y0 + f * height
            sx = hx * (1.0 - f ** 1.1 * 0.72)
            sz = hz * (1.0 - f ** 1.1 * 0.55)
            solids.append(Box((cx, y, cz), (sx, 0.045, sz), mat))
            solids.append(Box((cx, y + 0.052, cz + sz - 0.05), (sx, 0.026, 0.05),
                              ridge_mat))
            cols = max(int(sx * 2 * 0.55), 4)
            for k in range(cols):
                solids.append(Box((cx - sx + (k + 0.5) * (2 * sx / cols),
                                   y + 0.050, cz),
                                  (0.055, 0.024, sz), ridge_mat))
        solids.append(Box((cx, y0 + height + 0.04, cz), (hx * 0.30, 0.09,
                                                          hz * 0.46), 'darkstone'))

    # ---- the court and the processional way
    solids.append(Box((0.0, 0.010, 0.0), (24.0, 0.010, 26.0), 'stone'))
    for i in range(20):
        z = 24.0 - i * 1.55
        solids.append(Box((0.0, 0.030, z), (1.55, 0.026, 0.68), 'stone'))
        solids.append(Box((0.0, 0.052, z), (1.42, 0.008, 0.62), 'tile_ridge'))
    # low walls outlining the court
    for sx in (-12.6, 12.6):
        for i in range(12):
            solids.append(Box((sx, 0.62, 13.0 - i * 2.4), (0.16, 0.62, 1.15),
                              'wood'))

    # ---- main hall, top of frame
    solids.append(Box((0.0, 0.55, -12.0), (7.0, 0.55, 4.4), 'stone'))
    for i in range(5):
        solids.append(Box((0.0, 0.10 + i * 0.09, -7.0 + i * 0.36),
                          (3.0, 0.045, 0.19), 'stone'))
    for i in range(7):
        x = -5.8 + i * 1.94
        solids.append(Box((x, 2.10, -8.6), (0.17, 1.55, 0.17), 'wood'))
        solids.append(Box((x, 2.10, -15.2), (0.17, 1.55, 0.17), 'wood'))
    solids.append(Box((0.0, 3.72, -8.6), (6.4, 0.15, 0.21), 'wood'))
    solids.append(Box((0.0, 3.72, -15.2), (6.4, 0.15, 0.21), 'wood'))
    solids.append(Box((0.0, 1.55, -15.0), (5.2, 0.95, 0.06), 'paper'))
    for sx in (-2.4, 0.0, 2.4):
        lights.append(Light((sx, 2.2, -14.6), (1.0, 0.58, 0.26), 7.0, 0.9))
    hip_roof(0.0, -11.9, 8.6, 5.0, 3.95, 4.6, steps=16)

    # ---- two side halls
    for side in (-1, 1):
        cx = side * 9.2
        solids.append(Box((cx, 0.42, -9.0), (3.6, 0.42, 3.4), 'stone'))
        for i in range(5):
            x = cx - 3.0 + i * 1.5
            solids.append(Box((x, 1.75, -6.4), (0.15, 1.25, 0.15), 'wood'))
        solids.append(Box((cx, 1.45, -6.4), (3.4, 0.70, 0.05), 'paper'))
        solids.append(Box((cx, 2.92, -6.4), (3.6, 0.13, 0.19), 'wood'))
        lights.append(Light((cx, 1.9, -6.0), (1.0, 0.56, 0.24), 4.5, 0.7))
        hip_roof(cx, -9.0, 4.6, 4.0, 3.15, 2.7, steps=10)
        # a smaller pavilion further back on each side
        hip_roof(cx * 0.72, -17.5, 2.8, 2.6, 2.35, 2.2, steps=8)
        solids.append(Box((cx * 0.72, 1.15, -17.5), (2.4, 1.15, 2.2), 'wood'))

    # ---- the gate at the bottom of the axis, and the torii in the near court
    for sx in (-4.2, 4.2):
        solids.append(Box((sx, 2.1, 20.0), (0.30, 2.1, 0.30), 'wood'))
    solids.append(Box((0.0, 4.10, 20.0), (4.8, 0.22, 0.38), 'wood'))
    hip_roof(0.0, 20.0, 5.0, 1.5, 4.30, 1.9, steps=7)
    for sx in (-3.0, 3.0):
        solids.append(Box((sx, 2.55, 14.4), (0.24, 2.55, 0.24), 'vermilion'))
        solids.append(Box((sx, 2.55, 11.6), (0.24, 2.55, 0.24), 'vermilion'))
    solids.append(OBox((0.0, 5.05, 13.0), (4.0, 0.16, 0.30), 0.0, 0.10, 0.0,
                       'vermilion'))
    solids.append(Box((0.0, 5.55, 13.0), (4.4, 0.16, 0.42), 'darkstone'))

    # ---- lantern fires along the axis and round the halls
    for z in (18.0, 12.0, 6.0, 0.0, -5.0):
        for sx in (-3.4, 3.4):
            _stone_lantern(solids, lights, sx, z, scale=1.25)
    for sx in (-7.0, 7.0, -11.4, 11.4):
        _stone_lantern(solids, lights, sx, -3.0, scale=1.30)
    for z in (9.0, -1.0):
        for sx in (-6.2, 6.2):
            _stone_lantern(solids, lights, sx, z, scale=1.15)
    # wall-mounted lanterns on the hall fronts
    for sx in (-5.4, -1.8, 1.8, 5.4):
        _lantern(solids, lights, sx, 3.05, -8.3, power=2.4, scale=0.8)

    # ---- forest, the frame and the bottom of the valley
    _cedar_forest(solids, lights, -34.0, -14.0, -30.0, 30.0, n=40, seed=91)
    _cedar_forest(solids, lights, 14.0, 34.0, -30.0, 30.0, n=40, seed=92)
    _cedar_forest(solids, lights, -14.0, 14.0, -34.0, -19.0, n=26, seed=93)
    _cedar_forest(solids, lights, -14.0, 14.0, 24.0, 34.0, n=22, seed=94)
    # the valley falling away at the bottom of frame, mist catching in it
    solids.append(Box((0.0, -3.5, 40.0), (60.0, 3.5, 12.0), 'foliage'))
    lights.append(Light((0.0, 34.0, 10.0), (0.32, 0.44, 0.68), 55.0, 0.0))
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
    solids.append(Box((0.0, 2.0, -7.2), (5.4, 1.4, 0.06), 'wood'))
    for sx in (-3.0, 0.0, 3.0):
        lights.append(Light((sx, 1.7, -6.6), (1.0, 0.50, 0.20), 2.6, 0.5))
    # the two hanging lanterns that give the reference its warm pools
    for sx in (-2.4, 2.4):
        _lantern(solids, lights, sx, 2.5, -6.4, power=2.2)
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
    """S6 background only: the temple behind the head, far out of focus.

    The head itself is the scanned mesh in `head_mesh.py`; this set exists so the
    portrait has real geometry behind it — pillars, the plinth edge, a lantern —
    rather than a gradient.
    """
    solids, lights = [], []
    for sx in (-2.2, 2.2):
        solids.append(Box((sx, 2.2, -4.4), (0.26, 2.2, 0.26), 'vermilion'))
    solids.append(Box((0.0, 4.35, -4.4), (2.5, 0.16, 0.26), 'vermilion'))
    solids.append(Box((0.0, 0.30, -3.2), (3.2, 0.30, 0.9), 'stone'))
    for i in range(5):
        solids.append(Box((0.0, 0.08 + i * 0.10, -2.4 + i * 0.30),
                          (1.9, 0.05, 0.16), 'stone'))
    # a toro and a lantern, far behind: the two warm points in the reference
    _stone_lantern(solids, lights, -1.55, -2.0, scale=1.6)
    _lantern(solids, lights, 1.35, 2.35, -3.0, power=3.0, scale=0.9)
    for sx in (-0.9, 0.9):
        solids.append(Box((sx, 1.9, -5.6), (0.9, 1.9, 0.10), 'wood'))
    lights.append(Light((0.0, 3.2, -6.0), (1.0, 0.48, 0.20), 12.0, 0.9))
    lights.append(Light((0.0, 16.0, 2.0), (0.26, 0.34, 0.52), 22.0, 0.0))
    return solids, lights


def build_runhall():
    """S4: the front of a long vermilion hall, seen from the side.

    The reference shot is a lateral tracking pan across a temple veranda: the
    hall runs left to right across the frame at a slight angle, its steps come
    down into the foreground where the man runs, and two lanterns give the only
    warm light. Building the hall along the x axis is what makes a pan along x
    read as a pan across a facade.
    """
    solids, lights = [], []
    # wet flagstone court, extending well past the frame in both directions
    for i in range(30):
        z = 12.0 - i * 1.0
        solids.append(Box((0.0, 0.010, z), (22.0, 0.010, 0.45), 'stone'))
    # the hall: plinth, veranda, six bays of posts, deep eave
    solids.append(Box((0.0, 0.52, -3.4), (17.0, 0.52, 3.4), 'darkstone'))
    solids.append(Box((0.0, 1.06, -3.4), (16.6, 0.03, 3.1), 'tile_ridge'))
    # steps down into the court, running the whole length
    for i in range(5):
        solids.append(Box((0.0, 0.09 + i * 0.10, 0.55 - i * 0.30),
                          (16.2, 0.052, 0.16), 'stone'))
    for i in range(15):
        x = -15.4 + i * 2.2
        for zz in (0.0, -3.0, -6.0):
            solids.append(Box((x, 2.55, zz), (0.19, 1.80, 0.19), 'vermilion'))
        solids.append(Box((x, 4.32, 0.0), (0.21, 0.16, 0.24), 'darkstone'))
    # beams
    for zz in (0.0, -3.0, -6.0):
        solids.append(Box((0.0, 4.34, zz), (15.6, 0.17, 0.22), 'vermilion'))
    solids.append(Box((0.0, 3.30, 0.0), (15.6, 0.09, 0.18), 'wood'))
    # screens behind the posts, lit from inside
    for i in range(14):
        x = -14.3 + i * 2.2
        solids.append(Box((x, 2.30, -5.95), (0.92, 1.20, 0.05), 'paper_dim'))
        # a wooden lattice over each screen, so it is not a lit slab
        for k in range(5):
            solids.append(Box((x - 0.62 + k * 0.31, 2.30, -5.88),
                              (0.022, 1.20, 0.02), 'wood'))
        for k in range(4):
            solids.append(Box((x, 1.55 + k * 0.48, -5.88), (0.92, 0.018, 0.02),
                              'wood'))
    for x in (-9.0, -3.0, 3.0, 9.0):
        lights.append(Light((x, 2.1, -4.0), (1.0, 0.52, 0.22), 16.0, 1.1))
    # roof: courses running the length of the hall, with the eave overhead
    for i in range(10):
        f = i / 9.0
        solids.append(Box((0.0, 4.60 + f * 1.55, -3.4 + f * 1.7),
                          (16.4 - f * 1.2, 0.05, 3.9 - f * 1.5), 'tile'))
        solids.append(Box((0.0, 4.60 + f * 1.55, -3.4 + f * 1.7 + (3.9 - f * 1.5) - 0.05),
                          (16.4 - f * 1.2, 0.03, 0.06), 'tile_ridge'))
    # two lanterns: the reference has one on a post at the near end and one
    # lower, on the ground, throwing a pool of amber
    _stone_lantern(solids, lights, -1.55, 5.05, scale=1.30)
    lights.append(Light((-1.52, 1.50, 5.02), (1.0, 0.50, 0.16), 6.0, 0.26))
    _lantern(solids, lights, 1.15, 1.15, 3.55, power=9.0, scale=1.15)
    solids.append(Box((1.15, 0.55, 3.55), (0.058, 0.62, 0.058), 'darkstone'))
    _lantern(solids, lights, -4.1, 3.30, 2.7, power=7.0, scale=0.95)
    # mist that pools against the steps
    lights.append(Light((0.0, 16.0, 8.0), (0.30, 0.40, 0.60), 90.0, 0.0))
    return solids, lights


BUILDERS = {
    'street': build_street,
    'temple': build_temple,
    'aerial': build_aerial,
    'courtyard': build_courtyard,
    'runhall': build_runhall,
    'face': build_face,
}


def build(name):
    return BUILDERS[name]()
