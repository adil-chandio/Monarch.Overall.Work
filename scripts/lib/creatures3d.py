#!/usr/bin/env python3
"""3D meshes for the sea animals — built from cross-sections, not from primitives.

Every body is a spine of elliptical rings. That gives three things a flat silhouette
cannot: a rounded flank that catches light, a belly that is genuinely separable from
the back for shading, and a mesh the camera can orbit.

Anatomy note. The humpback's profile below is a real whale profile: blunt knobbly
rostrum, deep throat, a dorsal that is a small hook a third of the way forward of
the fluke, and a peduncle that narrows hard. Both pectoral fins are separate meshes
so they can animate independently.

  humpback(length_m=14)
  orca(length_m=8)
  blue_whale(length_m=28)
  great_white(length_m=6)
  flipper(length_m=5, side='R')

All meshes are in metres, head toward +z, +y up, centred on the origin.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scripts.lib.tri3d import Mesh, ellipse_ring, mirror_x, tube  # noqa: E402


def _profiles(points, n=20):
    """points: [(z, cy, rx, ry)] -> list of rings."""
    rings = []
    for (z, cy, rx, ry) in points:
        rings.append(ellipse_ring((0.0, cy, z), max(1e-4, rx), max(1e-4, ry), n))
    return rings


def _fluke(width, length, thick=0.05, y=0.0, z=0.0):
    """A horizontal tail fluke: two lobes, thin, with a notch."""
    w, l, t = width, length, thick
    v = []
    for s in (-1, 1):
        v += [
            (s * 0.02, y, z),
            (s * w * 0.55, y + 0.02, z - l * 0.55),
            (s * w * 1.00, y - 0.01, z - l * 1.00),
            (s * w * 0.42, y + 0.01, z - l * 0.62),
            (s * w * 0.06, y, z - l * 0.18),
        ]
    top = [(p[0], p[1] + t, p[2]) for p in v]
    bot = [(p[0], p[1] - t, p[2]) for p in v]
    verts = np.array(top + bot, dtype=np.float32)
    n = len(v)
    tris = []
    for i in range(n - 1):
        tris += [(i, i + 1, n + i), (i + 1, n + i + 1, n + i)]
    # close the two halves across the midline
    tris += [(0, n, n + 4), (0, n + 4, 4)]
    tris += [(3, n + 3, 4), (4, n + 3, n + 4)]
    return Mesh(verts, tris, (70, 76, 84), "skin")


# Head toward +z. A humpback: blunt rostrum, deep throat, the body's widest point
# at about 40 % of its length, a hard taper into a thin peduncle.
#   0.10 L : flank max          0.42 L : dorsal
#   the throat hangs below the axis, which is what makes the profile read as a
#   rorqual rather than a fish.
HUMPBACK_PROFILE = [
    # z,    cy,    rx,    ry
    # A rorqual head is BLUNT: the rostrum stays wide almost to the tip, then the
    # section collapses over the last 30 cm. Tapering it evenly from the flank makes
    # a teardrop, which is what the first two attempts looked like.
    (3.50, -0.06, 0.12, 0.10),
    (3.44, -0.06, 0.30, 0.24),
    (3.33, -0.06, 0.44, 0.35),
    (3.16, -0.08, 0.56, 0.45),
    (2.92, -0.11, 0.68, 0.56),
    (2.60, -0.15, 0.80, 0.68),
    (2.20, -0.18, 0.92, 0.80),
    (1.75, -0.20, 1.02, 0.90),
    (1.25, -0.18, 1.08, 0.94),
    (0.70, -0.13, 1.06, 0.90),
    (0.10, -0.06, 0.98, 0.82),
    (-0.50, 0.01, 0.86, 0.70),
    (-1.10, 0.06, 0.72, 0.56),
    (-1.65, 0.08, 0.56, 0.42),
    (-2.15, 0.08, 0.41, 0.30),
    (-2.55, 0.06, 0.29, 0.21),
    (-2.82, 0.05, 0.20, 0.15),
    (-2.97, 0.04, 0.14, 0.11),
    (-3.05, 0.03, 0.10, 0.08),
]


def _attach(mesh, x, y, z, yaw=0.0, pitch=0.0, roll=0.0):
    from scripts.lib.tri3d import rotation_x, rotation_y, rotation_z
    m = rotation_y(yaw) @ rotation_x(pitch) @ rotation_z(roll)
    out = mesh.copy()
    out.v = mesh.v @ m.T + np.array([x, y, z], dtype=np.float32)
    return out


def _ventral_pleats(profiles, s, from_k=0.02, to_k=0.40, n_groove=20,
                    width=0.040):
    """Throat grooves: the defining feature of a rorqual, and it was missing.

    A humpback's throat inflates with every mouthful, and the pleats are the folds
    that let it stretch to several times its resting girth. Seen from below - the
    angle this film looks at a rising whale - they are the thing that says
    "humpback" rather than "generic whale".

    The grooves are strips that run ALONG the body, so each one is a ribbon of
    quads connecting consecutive sections. v3.0 emitted one flat quad per section
    instead, i.e. twenty little cross-section plates buried inside the throat,
    which is why they never appeared in a single frame.
    """
    from scripts.lib.tri3d import Mesh
    i0 = int(len(profiles) * from_k)
    i1 = int(len(profiles) * to_k)
    rows = profiles[i0:i1 + 1]
    if len(rows) < 3:
        return None
    vs, ts = [], []
    for g in range(n_groove):
        # -pi/2 is straight down the throat; fan out across the belly only. Spreading
        # the arc across the whole section put them on the back, inside the body.
        th = -math.pi * 0.5 + (math.pi * 0.66) * ((g / max(1, n_groove - 1)) - 0.5)
        strip = []
        for j, (z, cy, rx, ry) in enumerate(rows):
            life = math.sin(math.pi * (j / max(1, len(rows) - 1))) ** 0.55
            if life < 0.06:
                strip.append(None)
                continue
            wv = width * s * life * (1.0 + 0.45 * (g % 2))
            # +y is dorsal in this rig (the dorsal fin sits at +y), so the ventral
            # surface is cy + sin(th)*ry: at th = -pi/2 that is cy - ry, the throat.
            # Getting this sign backwards laid all twenty grooves along the animal's
            # back, inside the body, which is why three renders showed no pleats.
            cx = math.cos(th) * rx * 1.004
            cyy = cy + math.sin(th) * ry * 1.004
            # offset a hair along the surface normal so it is never co-planar
            nx = math.cos(th) * 0.020 * s
            ny = math.sin(th) * 0.020 * s
            strip.append((cx + nx, cyy + ny, z * s))
        # stitch consecutive live sections into a ribbon. The width axis is the local
        # tangent around the section, so the groove stays the same width all the way
        # down the throat instead of twisting with the profile.
        prev = None
        for j, pt in enumerate(strip):
            if pt is None:
                prev = None
                continue
            z, cy, rx, ry = rows[j]
            life = math.sin(math.pi * (j / max(1, len(rows) - 1))) ** 0.55
            wv = (width * 0.5) * s * life * (1.0 + 0.45 * (g % 2))
            # tangential direction in the section plane
            tx, ty = math.sin(th) * 1.0, math.cos(th) * 1.0
            a = (pt[0] - tx * wv, pt[1] - ty * wv, pt[2])
            b = (pt[0] + tx * wv, pt[1] + ty * wv, pt[2])
            if prev is not None:
                base = len(vs)
                vs.extend([prev[0], prev[1], b, a])
                ts.extend([[base, base + 1, base + 2], [base, base + 2, base + 3]])
            prev = (a, b)
    if not vs:
        return None
    # NOT material="patch": the patch shader is deliberately a diffuse scatterer
    # (that is what makes an orca's saddle legible at distance), so a dark
    # patch-coloured ribbon washed out to the body's own value and the grooves
    # vanished. A groove is a crease - it has to read as a dark line.
    m = Mesh(np.asarray(vs, dtype=np.float32), np.asarray(ts, dtype=np.int32),
             colour=(4, 6, 9), material="slab")
    m.two_sided = True
    return m


def humpback(length_m=14.0, colour=(150, 152, 148), n=22):
    """The whole animal: body tube, fluke, two pectoral fins, dorsal, jawline carved
    with a dark material band so the mouth reads without a texture map."""
    s = length_m / 14.0
    pts = [(z * s, cy * s, rx * s, ry * s) for (z, cy, rx, ry) in HUMPBACK_PROFILE]
    # flatten the back and deepen the throat: a humpback is not a cigar
    shaped = []
    for (z, cy, rx, ry) in pts:
        shaped.append((z, cy, rx, ry))
    body = tube(_profiles(shaped, n), colour, "skin")

    fluke = _fluke(width=2.20 * s, length=1.30 * s, thick=0.075 * s, z=-3.02 * s)
    fluke.colour = np.asarray(colour, dtype=np.float32) / 255.0
    dorsal = _dorsal(0.55 * s, 0.42 * s, z=-0.25 * s, y=0.86 * s)
    finr = _pec_fin(3.6 * s, 1.45 * s, thick=0.13 * s)
    finl = mirror_x(finr)

    # pectoral fins sit just behind and below the head, sweeping back
    m = np.eye(4, dtype=np.float32)
    # the fin root sits INSIDE the flank so there is no gap at the shoulder
    finr = _attach(finr, 1.00 * s, -0.50 * s, 1.55 * s, yaw=-14, pitch=-8, roll=-34)
    finl = _attach(finl, -1.00 * s, -0.50 * s, 1.55 * s, yaw=14, pitch=-8, roll=34)

    parts = [body, fluke, dorsal, finr, finl]
    mouth = mouth_band([(z / s, cy / s, rx / s, ry / s) for (z, cy, rx, ry) in shaped],
                       from_k=0.02, to_k=0.30)
    if mouth is not None:
        mouth.v = mouth.v * s
        parts.append(mouth)
    for sx in (-1, 1):
        e = eye_sphere(0.11 * s)
        e = _attach(e, sx * 0.66 * s, -0.30 * s, 2.72 * s)
        parts.append(e)
    pleats = _ventral_pleats(shaped, 1.0)   # shaped is already in metres
    if pleats is not None:
        parts.append(pleats)
    vs, ts, off = [], [], 0
    for p in parts:
        vs.append(p.v)
        ts.append(p.t + off)
        off += len(p.v)
    out = Mesh(np.concatenate(vs), np.concatenate(ts), colour, "whale")
    return out


def _dorsal(h, base, z, y, thick=0.09):
    v = np.array([
        (0, y, z - base * 0.5), (0, y + h, z + h * 0.25), (0, y, z + base * 0.7),
        (0, y - 0.04, z + base * 0.7), (0, y - 0.04, z - base * 0.5),
    ], dtype=np.float32)
    t = [(0, 1, 2), (0, 2, 4), (2, 1, 3), (1, 0, 3), (0, 4, 3), (1, 3, 4), (2, 3, 4)]
    return Mesh(v, t, (60, 65, 72))


def _pec_fin(length, width, thick=0.10, n=8, colour=(196, 198, 196), material="skin"):
    """A humpback pectoral fin, extending along -Y with its chord along X.

    The cross-section MUST be in the X-Z plane. An earlier version used
    ellipse_ring(), which puts the section in X-Y -- the same axis the fin runs
    along -- so the fin collapsed into a sliver whenever it was seen edge-on and
    the animal ended up looking like it had legs.
    """
    rings = []
    for i in range(n + 1):
        k = i / n
        # wide at the root, a bulge near 35 %, then a blunt tip; the small sine term
        # gives the knobbly leading edge
        w = width * (1.0 - 0.50 * k ** 1.8) * (0.74 + 0.26 * math.sin(math.pi * k) ** 0.5)
        w *= 1.0 + 0.05 * math.sin(k * 19.0)
        th = thick * (1.0 - 0.70 * k) + 0.02
        y = -k * length
        ring = []
        for m in range(14):
            a = 2 * math.pi * m / 14
            ring.append((math.cos(a) * w * 0.5, y, math.sin(a) * th))
        rings.append(ring)
    return tube(rings, colour, material)


def mouth_band(profile, length_scale=1.0, from_k=0.02, to_k=0.30, width=0.05):
    """A thin dark strip following the jawline, pushed 4 % outside the hull.

    Long before this there was a texture-less whale with no mouth at all, which
    reads as a submarine. A ribbon along the lower flank is enough.
    """
    pts = []
    n = len(profile)
    for i in range(n):
        k = i / (n - 1)
        if k < from_k or k > to_k:
            continue
        pts.append(profile[i])
    vs, ts = [], []
    for (z, cy, rx, ry) in pts:
        y = cy - ry * 0.45
        for sx in (-1, 1):
            x = sx * rx * 1.04
            vs.append((x, y - width, z))
            vs.append((x, y + width, z))
    for i in range(len(pts) - 1):
        a, b = i * 4, (i + 1) * 4
        ts += [(a, b, b + 2), (a, b + 2, a + 2)]
        ts += [(a + 1, a + 3, b + 3), (a + 1, b + 3, b + 1)]
    if not ts:
        return None
    return Mesh(np.array(vs, dtype=np.float32), np.array(ts, dtype=np.int32),
                (26, 30, 36), "mouth")


def eye_sphere(radius, colour=(226, 228, 224)):
    rings = []
    for i in range(7):
        phi = math.pi * (i + 0.5) / 7
        r = radius * math.sin(phi)
        y = radius * math.cos(phi)
        rings.append([(math.cos(2 * math.pi * j / 10) * r, y,
                       math.sin(2 * math.pi * j / 10) * r) for j in range(10)])
    return tube(rings, colour, "eye")


ORCA_PROFILE = [
    (2.60, 0.02, 0.03, 0.03),
    (2.45, 0.02, 0.16, 0.13),
    (2.20, 0.00, 0.36, 0.28),
    (1.85, -0.02, 0.56, 0.44),
    (1.45, -0.03, 0.72, 0.58),
    (1.00, -0.02, 0.82, 0.68),
    (0.50, 0.00, 0.86, 0.72),
    (0.00, 0.01, 0.84, 0.70),
    (-0.55, 0.02, 0.76, 0.62),
    (-1.10, 0.02, 0.64, 0.50),
    (-1.60, 0.02, 0.48, 0.36),
    (-2.05, 0.01, 0.32, 0.23),
    (-2.35, 0.00, 0.20, 0.14),
    (-2.52, 0.00, 0.12, 0.09),
]


def orca(length_m=8.0, colour=(22, 24, 29), n=22):
    s = length_m / 5.2
    pts = [(z * s, cy * s, rx * s, ry * s) for (z, cy, rx, ry) in ORCA_PROFILE]
    body = tube(_profiles(pts, n), colour, "skin")
    fluke = _fluke(1.05 * s, 0.62 * s, 0.035 * s, z=-2.50 * s)
    fluke.colour = np.asarray(colour, dtype=np.float32) / 255.0
    dorsal = _tall_dorsal(0.85 * s, 0.34 * s, z=0.15 * s, y=0.52 * s)
    dorsal.colour = np.asarray(colour, dtype=np.float32) / 255.0
    # An orca's pectoral is a near-flat black blade. Shaded as glossy skin it does
    # nothing but catch a rim highlight along its whole span, so it renders as a
    # white pole twice the width of the animal - which is what the pec-slap beat
    # showed. "slab" is the matte, non-specular path: it stays black, as it should.
    finr = _pec_fin(1.10 * s, 0.62 * s, thick=0.09 * s, n=7, colour=colour, material="fin")
    finl = mirror_x(finr)
    finr = _attach(finr, 0.50 * s, -0.30 * s, 0.80 * s, yaw=-16, pitch=-10, roll=-30)
    finl = _attach(finl, -0.50 * s, -0.30 * s, 0.80 * s, yaw=16, pitch=-10, roll=30)
    parts = [body, fluke, dorsal, finr, finl]
    vs, ts, off = [], [], 0
    for p in parts:
        vs.append(p.v)
        ts.append(p.t + off)
        off += len(p.v)
    base = Mesh(np.concatenate(vs), np.concatenate(ts), colour, "orca")
    # patches travel with the body but keep their own two-sided material
    base.patches = orca_patches(length_m)
    return base


def orca_patches(length_m=8.0, n_ang=14):
    """The three markings that make an orca read as an orca, as offset shells.

    The first version painted a band from z=+1.05*s to z=-1.45*s across TWO separate
    angle ranges - 2.15..3.95 rad and -0.99..0.81 rad. Those two ranges together
    cover most of the circumference, so the animal came out as a white barrel with a
    black nose, which is a panda with a dorsal fin. Real markings are narrow:

      * an eye patch: a small oval above and behind the eye, one per flank
      * a saddle: a grey blaze *behind* the dorsal fin, low on the back
      * a chin/belly: white from the jaw back along the underside only

    Everything below is expressed in the profile's own coordinates (z toward the
    head is positive, angle pi/2 is up), so it stays attached when the body bends.
    """
    s_ = length_m / 5.2
    prof = [(z * s_, cy * s_, rx * s_, ry * s_) for (z, cy, rx, ry) in ORCA_PROFILE]
    vs, ts = [], []

    def add_shell(z0, z1, a0, a1, grow=1.03, taper=0.0):
        base = len(vs)
        pts = [p for p in prof if z0 <= p[0] <= z1]
        if len(pts) < 2:
            return
        nn = n_ang
        for k, (z, cy, rx, ry) in enumerate(pts):
            # taper the angle span toward the ends so the patch has a soft edge
            # instead of a rectangle cut out of the hull
            f = 1.0
            if taper > 0.0:
                u = k / max(1, len(pts) - 1)
                f = math.sin(math.pi * u) ** (taper * 0.5) * 0.85 + 0.15
            mid = 0.5 * (a0 + a1)
            half = 0.5 * (a1 - a0) * f
            for j in range(nn):
                a = mid - half + 2 * half * j / (nn - 1)
                vs.append((math.cos(a) * rx * grow, cy + math.sin(a) * ry * grow, z))
        rows = len(pts)
        for i in range(rows - 1):
            for j in range(nn - 1):
                a = base + i * nn + j
                b = a + nn
                ts.append((a, b, b + 1))
                ts.append((a, b + 1, a + 1))

    # --- eye patch: small oval, above and slightly behind the eye, both flanks ---
    # The eye sits near z=+1.9*s, about 40 degrees up from the waterline.
    for side in (1, -1):
        base = len(vs)
        rows, cols = 7, 7
        cz, ca = 1.78 * s_, 0.62          # centre: behind the snout, high on the flank
        for i in range(rows):
            for j in range(cols):
                u = i / (rows - 1) - 0.5      # along the body
                v = j / (cols - 1) - 0.5      # around the body
                rr = (u / 0.5) ** 2 + (v / 0.5) ** 2
                if rr > 1.0:
                    k = 1.0 / math.sqrt(rr)
                    u *= k * 0.98
                    v *= k * 0.98
                z = cz + u * 0.62 * s_
                ang = ca + v * 0.66 * (1 if side > 0 else 1)
                # sample the local hull radius at this z
                rx = ry = 0.0
                cy = 0.0
                for (pz, pcy, prx, pry) in prof:
                    if pz <= z:
                        rx, ry, cy = prx, pry, pcy
                        break
                if rx == 0.0:
                    rx, ry, cy = prof[-1][2], prof[-1][3], prof[-1][1]
                g = 1.028
                x = math.cos(ang) * rx * g
                y = cy + math.sin(ang) * ry * g
                if side < 0:
                    x = -x
                vs.append((x, y, z))
        for i in range(rows - 1):
            for j in range(cols - 1):
                a = base + i * cols + j
                b = a + cols
                ts.append((a, b, b + 1))
                ts.append((a, b + 1, a + 1))

    # --- saddle: a grey blaze behind the dorsal fin, only on the upper back ---
    add_shell(-0.30 * s_, -1.25 * s_, 0.72, 2.42, grow=1.022, taper=1.4)

    # --- chin / belly: white underside from the jaw back, never up the flank ---
    add_shell(-0.05 * s_, 2.18 * s_, -2.55, -0.62, grow=1.024, taper=1.0)

    out = Mesh(np.array(vs, dtype=np.float32), np.array(ts, dtype=np.int32),
               (238, 236, 230), "patch")
    out.two_sided = True
    return out


def _tall_dorsal(h, base, z, y, thick=0.10):
    th = thick
    """The orca's blade: tall, swept back, thin edges."""
    v = np.array([
        (0, y, z - base * 0.55), (0, y + h * 0.98, z + h * 0.30),
        (0, y + h * 0.55, z + h * 0.44), (0, y, z + base * 0.75),
        (0, y - 0.05, z + base * 0.75), (0, y - 0.05, z - base * 0.55),
        (th * 0.35, y, z - base * 0.55), (th * 0.25, y + h * 0.98, z + h * 0.30),
        (th * 0.30, y, z + base * 0.75),
    ], dtype=np.float32)
    t = [(0, 1, 2), (0, 2, 3), (0, 3, 6), (6, 3, 8), (8, 3, 2), (2, 7, 8),
         (2, 1, 7), (1, 6, 7), (6, 0, 5), (6, 8, 2), (5, 4, 8), (5, 8, 6)]
    return Mesh(v, t, (18, 20, 24))


BLUE_PROFILE = [
    (13.0, 0.1, 0.10, 0.10),
    (12.2, 0.1, 0.55, 0.50),
    (11.0, 0.05, 1.05, 0.95),
    (9.0, -0.10, 1.75, 1.55),
    (6.5, -0.25, 2.35, 2.05),
    (3.5, -0.30, 2.60, 2.30),
    (0.0, -0.25, 2.45, 2.15),
    (-3.5, -0.10, 2.05, 1.75),
    (-7.0, 0.05, 1.55, 1.25),
    (-10.0, 0.10, 1.00, 0.78),
    (-12.0, 0.10, 0.60, 0.45),
    (-13.0, 0.05, 0.34, 0.26),
    (-13.6, 0.00, 0.20, 0.15),
]


def blue_whale(length_m=28.0, colour=(96, 106, 120), n=24):
    s = length_m / 28.0
    pts = [(z * s, cy * s, rx * s, ry * s) for (z, cy, rx, ry) in BLUE_PROFILE]
    body = tube(_profiles(pts, n), colour, "skin")
    fluke = _fluke(4.4 * s, 2.2 * s, 0.10 * s, z=-13.55 * s)
    fluke.colour = np.asarray(colour, dtype=np.float32) / 255.0
    dorsal = _dorsal(0.55 * s, 1.5 * s, z=-11.0 * s, y=0.75 * s)
    finr = _pec_fin(2.8 * s, 1.1 * s, thick=0.12 * s, n=8)
    finl = mirror_x(finr)
    finr = _attach(finr, 1.85 * s, -1.05 * s, 4.4 * s, yaw=-12, pitch=-12, roll=-38)
    finl = _attach(finl, -1.85 * s, -1.05 * s, 4.4 * s, yaw=12, pitch=-12, roll=38)
    vs, ts, off = [], [], 0
    for p in [body, fluke, dorsal, finr, finl]:
        vs.append(p.v)
        ts.append(p.t + off)
        off += len(p.v)
    return Mesh(np.concatenate(vs), np.concatenate(ts), colour, "whale")


GW_PROFILE = [
    (2.30, 0.06, 0.02, 0.02),
    (2.15, 0.05, 0.10, 0.07),
    (1.90, 0.02, 0.22, 0.15),
    (1.55, 0.00, 0.34, 0.25),
    (1.10, -0.01, 0.44, 0.34),
    (0.60, 0.00, 0.48, 0.40),
    (0.10, 0.01, 0.46, 0.39),
    (-0.40, 0.02, 0.40, 0.33),
    (-0.90, 0.02, 0.32, 0.26),
    (-1.35, 0.01, 0.22, 0.18),
    (-1.75, 0.00, 0.14, 0.11),
    (-1.95, 0.00, 0.09, 0.07),
]


def great_white(length_m=6.0, colour=(92, 100, 110), n=20):
    s = length_m / 4.3
    pts = [(z * s, cy * s, rx * s, ry * s) for (z, cy, rx, ry) in GW_PROFILE]
    body = tube(_profiles(pts, n), colour, "skin")
    # lunate caudal: the top lobe is long, bottom lobe short
    v = np.array([
        (0, 0, 0), (0, 0.55, -0.45), (0, 0.75, -0.75), (0, 0.30, -0.42),
        (0, 0, -0.30), (0, -0.32, -0.42), (0, -0.45, -0.62),
        (0.05, 0, 0), (0.05, 0.55, -0.45), (0.05, 0.30, -0.42),
        (0.05, 0, -0.30), (0.05, -0.32, -0.42),
    ], dtype=np.float32) * s
    t = [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 6), (0, 6, 5),
         (7, 8, 9), (7, 9, 10), (7, 10, 11),
         (0, 7, 1), (7, 8, 1), (1, 8, 2), (8, 9, 2), (2, 9, 3), (9, 10, 3),
         (3, 10, 4), (10, 11, 4), (4, 11, 6), (11, 5, 6)]
    caudal = Mesh(v, t, (78, 86, 96))
    caudal.v[:, 2] -= 1.85 * s
    dorsal = _dorsal(0.52 * s, 0.40 * s, z=0.05 * s, y=0.44 * s)
    finr = _pec_fin(0.95 * s, 0.58 * s, thick=0.06 * s, n=6)
    finl = mirror_x(finr)
    finr = _attach(finr, 0.34 * s, -0.16 * s, 0.45 * s, yaw=-30, pitch=-14, roll=-44)
    finl = _attach(finl, -0.34 * s, -0.16 * s, 0.45 * s, yaw=30, pitch=-14, roll=44)
    vs, ts, off = [], [], 0
    for p in [body, caudal, dorsal, finr, finl]:
        vs.append(p.v)
        ts.append(p.t + off)
        off += len(p.v)
    return Mesh(np.concatenate(vs), np.concatenate(ts), colour, "shark")


def flipper(length_m=5.0, colour=(198, 200, 197)):
    """A standalone pectoral fin, root at the origin, tip toward -y."""
    return _pec_fin(length_m, length_m * 0.26, thick=0.10, n=10)


def krill_cluster(count=260, radius=2.6, seed=4):
    """A school of krill as one draw call: tiny ellipsoids in a cloud."""
    rng = np.random.default_rng(seed)
    vs, ts, off = [], [], 0
    for i in range(count):
        p = rng.normal(size=3) * 0.5
        p = p / (np.linalg.norm(p) + 1e-6) * radius * rng.random() ** 0.6
        s = 0.02 + rng.random() * 0.035
        rings = [ellipse_ring((p[0], p[1] + dy, p[2] + dz), s, s * 0.55, 6)
                 for dy, dz in ((-0.5 * s, 0), (0.5 * s, 0))]
        m = tube(rings, (210, 200, 178), cap=True)
        vs.append(m.v)
        ts.append(m.t + off)
        off += len(m.v)
    return Mesh(np.concatenate(vs), np.concatenate(ts), (210, 200, 178), "krill")


if __name__ == "__main__":
    for name, fn in (("humpback", humpback), ("orca", orca), ("blue", blue_whale),
                     ("great_white", great_white), ("krill", krill_cluster)):
        m = fn()
        lo, hi = m.bounds()
        print(f"{name:12s} verts {len(m.v):6d}  tris {len(m.t):6d}  "
              f"size {(hi - lo).round(2)}")
