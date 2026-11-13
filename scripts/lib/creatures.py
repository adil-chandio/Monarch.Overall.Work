"""
Animal silhouettes as single continuous bezier contours.

Rule this file exists to enforce: **one path, one contour, no blob stacking.** The
first attempt at this film assembled animals from ellipses and the result read as a
pile of circles at full resolution — correctly, because a body outline has a width
that changes smoothly and a circle does not.

Every shape below is defined in a unit box (x right, y down, both 0..1), drawn
facing right. `flip=True` mirrors it. Because they are paths and not images, they
scale to any size without softness and cost nothing to store.

The proportions are chosen to be identifiable in one glance at 400 px:
  - a whale is a long taper, a small eye, and one big jaw line
  - an orca is black with a white belly patch and a tall dorsal fin
  - a shark is a straight-backed torpedo with a triangular dorsal
If a viewer cannot name the animal at 400 px, the shape is wrong and should be
redrawn rather than decorated.
"""
from __future__ import annotations

import math

from .bezier import draw_path, stroke_path

# ---------------------------------------------------------------------------
# Livyatan — a raptorial sperm whale. Huge blunt head, one long lower jaw set
# with big teeth, small eye far back, narrow tail stock, flukes.
# ---------------------------------------------------------------------------
LIVYATAN = [
    ("M", 0.02, 0.52),
    # top of the head — blunt, squared, the sperm-whale signature
    ("C", 0.05, 0.30, 0.14, 0.20, 0.26, 0.19),
    # back running to the tail stock
    ("C", 0.44, 0.16, 0.62, 0.22, 0.76, 0.30),
    # tail stock, thin
    ("C", 0.82, 0.33, 0.84, 0.38, 0.845, 0.44),
    # fluke upper lobe
    ("C", 0.90, 0.34, 0.96, 0.26, 0.995, 0.22),
    ("C", 0.97, 0.40, 0.94, 0.46, 0.90, 0.50),
    # fluke lower lobe
    ("C", 0.94, 0.55, 0.97, 0.62, 0.995, 0.70),
    ("C", 0.95, 0.66, 0.90, 0.60, 0.845, 0.55),
    # underside back to the jaw hinge
    ("C", 0.80, 0.62, 0.72, 0.66, 0.62, 0.66),
    # lower jaw — long, straight, the weapon
    ("C", 0.44, 0.68, 0.24, 0.68, 0.09, 0.64),
    ("C", 0.04, 0.63, 0.01, 0.58, 0.02, 0.52),
    ("Z",),
]

# The mouth line: a thin opening between the snout and the jaw, drawn over the body.
LIVYATAN_JAW = [
    ("M", 0.035, 0.545),
    ("C", 0.14, 0.585, 0.26, 0.60, 0.38, 0.60),
    ("C", 0.30, 0.625, 0.16, 0.625, 0.045, 0.595),
]

# Eye position in unit-box terms, so it tracks the shape when scaled.
LIVYATAN_EYE = (0.335, 0.435)

# A single tooth, used along the jaw to build the "four dozen spears" line.
TOOTH = [
    ("M", 0.30, 0.00),
    ("C", 0.44, 0.28, 0.46, 0.62, 0.42, 1.00),
    ("C", 0.52, 0.62, 0.56, 0.28, 0.70, 0.00),
    ("Z",),
]

# ---------------------------------------------------------------------------
# Megalodon — a lamniform shark: pointed snout, straight back, big triangular
# dorsal, crescent tail, small second dorsal.
# ---------------------------------------------------------------------------
MEGALODON = [
    ("M", 0.015, 0.50),
    ("C", 0.06, 0.42, 0.14, 0.37, 0.24, 0.36),
    # straight back to the dorsal
    ("C", 0.38, 0.345, 0.50, 0.335, 0.585, 0.325),
    # dorsal fin up, back, and down
    ("C", 0.60, 0.16, 0.65, 0.08, 0.695, 0.04),
    ("C", 0.695, 0.16, 0.685, 0.26, 0.675, 0.345),
    # back to the caudal peduncle
    ("C", 0.74, 0.36, 0.80, 0.40, 0.845, 0.45),
    # tail: upper lobe long, lower lobe short — the lamnid crescent
    ("C", 0.90, 0.30, 0.955, 0.18, 0.995, 0.10),
    ("C", 0.975, 0.30, 0.955, 0.42, 0.925, 0.50),
    ("C", 0.955, 0.58, 0.965, 0.68, 0.955, 0.80),
    ("C", 0.92, 0.68, 0.885, 0.58, 0.845, 0.53),
    # belly forward to the snout
    ("C", 0.76, 0.60, 0.66, 0.64, 0.56, 0.645),
    # the mouth: a deep notch under the snout
    ("C", 0.44, 0.68, 0.36, 0.70, 0.30, 0.685),
    ("C", 0.22, 0.66, 0.14, 0.60, 0.015, 0.50),
    ("Z",),
]

MEGALODON_EYE = (0.115, 0.455)

# Pectoral fin, drawn separately so it can sit under the body.
MEGALODON_FIN = [
    ("M", 0.30, 0.62),
    ("C", 0.26, 0.74, 0.22, 0.84, 0.17, 0.92),
    ("C", 0.30, 0.88, 0.40, 0.80, 0.46, 0.70),
    ("C", 0.42, 0.66, 0.36, 0.63, 0.30, 0.62),
    ("Z",),
]

# ---------------------------------------------------------------------------
# Orca — for the opening comparison shot. Black body, white belly patch,
# tall dorsal, white eye patch behind the eye.
# ---------------------------------------------------------------------------
ORCA = [
    ("M", 0.015, 0.52),
    ("C", 0.05, 0.40, 0.13, 0.33, 0.24, 0.32),
    ("C", 0.36, 0.31, 0.46, 0.30, 0.545, 0.295),
    # dorsal: tall, slightly swept back
    ("C", 0.565, 0.14, 0.615, 0.05, 0.655, 0.02),
    ("C", 0.655, 0.14, 0.645, 0.24, 0.635, 0.315),
    ("C", 0.72, 0.33, 0.79, 0.38, 0.85, 0.45),
    ("C", 0.90, 0.32, 0.955, 0.22, 0.995, 0.16),
    ("C", 0.975, 0.32, 0.955, 0.43, 0.925, 0.50),
    ("C", 0.955, 0.57, 0.965, 0.66, 0.955, 0.78),
    ("C", 0.92, 0.66, 0.885, 0.57, 0.85, 0.535),
    ("C", 0.76, 0.62, 0.66, 0.66, 0.56, 0.665),
    # jaw line
    ("C", 0.44, 0.69, 0.34, 0.70, 0.26, 0.665),
    ("C", 0.17, 0.63, 0.09, 0.58, 0.015, 0.52),
    ("Z",),
]

ORCA_PATCH = [
    ("M", 0.30, 0.545),
    ("C", 0.40, 0.545, 0.52, 0.575, 0.62, 0.625),
    ("C", 0.72, 0.665, 0.80, 0.60, 0.855, 0.535),
    ("C", 0.79, 0.62, 0.70, 0.68, 0.60, 0.69),
    ("C", 0.48, 0.70, 0.37, 0.66, 0.30, 0.60),
    ("Z",),
]

ORCA_EYEPATCH = [
    ("M", 0.225, 0.375),
    ("C", 0.275, 0.335, 0.345, 0.345, 0.375, 0.385),
    ("C", 0.365, 0.415, 0.305, 0.445, 0.258, 0.428),
    ("C", 0.235, 0.418, 0.222, 0.398, 0.225, 0.375),
    ("Z",),
]

ORCA_EYE = (0.248, 0.398)


# ---------------------------------------------------------------------------
# Public drawing helpers
# ---------------------------------------------------------------------------
def draw(f, path, bbox, fill, flip=False, shear=0.0):
    return draw_path(getattr(f, "d", f), path, bbox, fill, flip=flip, shear=shear)


def draw_stroke(f, path, bbox, fill, width=3, flip=False, shear=0.0):
    return stroke_path(getattr(f, "d", f), path, bbox, fill, width=width, flip=flip, shear=shear)


def eye(f, xy, r, colour=(10, 12, 14, 255)):
    x, y = xy
    f.d.ellipse([x - r, y - r, x + r, y + r], fill=colour)


def scale_point(bbox, unit):
    """Map a unit-box point to pixels inside `bbox`."""
    x0, y0, w, h = bbox
    return (x0 + unit[0] * w, y0 + unit[1] * h)


# ---------------------------------------------------------------------------
# DETAIL SETS — the paths a viewer actually recognises the animal by.
# Each is a list of polylines in UNIT-BOX coordinates, so they scale with the body.
# The reference's humpback is identifiable from three things at a glance: the
# throat pleats, the knobbly flipper, and the baleen comb. Without them a whale is
# just a grey lozenge, which is the failure the operator spotted immediately.
# ---------------------------------------------------------------------------
def _unit_line(x0, y0, x1, y1, n=6, bow=0.0):
    """A slightly bowed line, because a dead-straight pleat looks like a ruler mark."""
    pts = []
    for i in range(n + 1):
        k = i / n
        x = x0 + (x1 - x0) * k
        y = y0 + (y1 - y0) * k + math.sin(k * math.pi) * bow
        pts.append((x, y))
    return pts


def humpback_pleats(n=14):
    """Throat grooves running from under the jaw back along the belly."""
    out = []
    for i in range(n):
        f0 = i / (n - 1)
        x = 0.045 + f0 * 0.34
        y0 = 0.70 - f0 * 0.16
        out.append(_unit_line(x, y0, x + 0.055, y0 + 0.115, n=5, bow=-0.012))
    return out


def flipper_knobs(n=9):
    """The tubercles on a humpback pectoral flipper — the giveaway detail."""
    out = []
    for i in range(n):
        f0 = (i + 0.5) / n
        x = 0.26 + f0 * 0.16
        y = 0.86 - f0 * 0.34
        out.append([(x - 0.008, y), (x + 0.008, y)])
    return out


def baleen_comb(n=22):
    """Vertical baleen plates in the mouth — gold in the reference, and gold here."""
    out = []
    for i in range(n):
        f0 = i / (n - 1)
        x = 0.055 + f0 * 0.19
        y_top = 0.585 - f0 * 0.02
        out.append([(x, y_top), (x + 0.002, y_top + 0.075)])
    return out


def shark_gill_slits(n=5):
    out = []
    for i in range(n):
        x = 0.23 + i * 0.022
        out.append([(x, 0.42 + i * 0.004), (x + 0.006, 0.52 + i * 0.004)])
    return out


def whale_belly_lines(n=10):
    """Generic ventral creases, for the sperm whale / Livyatan."""
    out = []
    for i in range(n):
        f0 = i / (n - 1)
        x = 0.06 + f0 * 0.30
        y = 0.625 - f0 * 0.03
        out.append(_unit_line(x, y, x + 0.10, y + 0.012, n=4, bow=0.006))
    return out


def unit_to_px(lines, bbox, flip=False):
    """Map a detail set onto the canvas using the same transform as the body."""
    x0, y0, w, h = bbox
    out = []
    for ln in lines:
        pts = []
        for (ux, uy) in ln:
            ux2 = (1 - ux) if flip else ux
            # clamp: a detail that runs slightly past the unit box must not produce
            # an inverted ellipse box when the caller's bbox starts off-screen
            ux2 = max(0.0, min(1.0, ux2))
            uy = max(0.0, min(1.0, uy))
            pts.append((x0 + ux2 * w, y0 + uy * h))
        out.append(pts)
    return out


# A humpback: the body the reference actually shows. Same box, fuller profile,
# throat expanded, and a clearly separate long pectoral flipper.
HUMPBACK = [
    ("M", 0.010, 0.42),
    # head, blunt and slightly down-turned
    ("C", 0.045, 0.30, 0.115, 0.24, 0.205, 0.235),
    ("C", 0.30, 0.225, 0.40, 0.225, 0.50, 0.25),
    ("C", 0.60, 0.275, 0.66, 0.31, 0.72, 0.35),
    ("C", 0.78, 0.38, 0.82, 0.42, 0.855, 0.475),
    # fluke
    ("C", 0.895, 0.395, 0.945, 0.335, 0.985, 0.30),
    ("C", 0.965, 0.42, 0.945, 0.475, 0.905, 0.515),
    ("C", 0.945, 0.555, 0.962, 0.615, 0.975, 0.685),
    ("C", 0.935, 0.655, 0.895, 0.60, 0.855, 0.555),
    # belly, expanding into the throat
    ("C", 0.80, 0.63, 0.70, 0.70, 0.58, 0.72),
    ("C", 0.44, 0.745, 0.28, 0.735, 0.16, 0.70),
    ("C", 0.085, 0.675, 0.035, 0.61, 0.018, 0.53),
    ("C", 0.012, 0.49, 0.008, 0.45, 0.010, 0.42),
    ("Z",),
]

HUMPBACK_FLIPPER = [
    ("M", 0.245, 0.60),
    ("C", 0.235, 0.72, 0.215, 0.84, 0.175, 0.95),
    ("C", 0.255, 0.905, 0.315, 0.82, 0.355, 0.715),
    ("C", 0.335, 0.655, 0.29, 0.615, 0.245, 0.60),
    ("Z",),
]

HUMPBACK_MOUTH = [
    ("M", 0.018, 0.50),
    ("C", 0.075, 0.545, 0.135, 0.565, 0.195, 0.562),
    ("C", 0.145, 0.585, 0.075, 0.575, 0.020, 0.545),
]

HUMPBACK_EYE = (0.075, 0.455)


# ---------------------------------------------------------------------------
# Blue whale — the animal the orcas are afraid of. Long, flat-backed, small dorsal
# set far back, wide flat rostrum. The reference draws it almost as a slab, and
# that is right: a blue whale has no waist.
# ---------------------------------------------------------------------------
BLUE_WHALE = [
    ("M", 0.008, 0.520),
    ("C", 0.030, 0.430, 0.085, 0.372, 0.160, 0.352),
    ("C", 0.300, 0.318, 0.470, 0.315, 0.620, 0.330),
    ("C", 0.700, 0.338, 0.760, 0.352, 0.800, 0.368),
    ("C", 0.826, 0.352, 0.846, 0.320, 0.862, 0.300),
    ("C", 0.872, 0.318, 0.878, 0.352, 0.876, 0.386),
    ("C", 0.912, 0.400, 0.948, 0.412, 0.978, 0.434),
    ("C", 0.960, 0.470, 0.938, 0.500, 0.906, 0.514),
    ("C", 0.880, 0.560, 0.862, 0.600, 0.836, 0.628),
    ("C", 0.780, 0.640, 0.700, 0.648, 0.610, 0.650),
    ("C", 0.470, 0.655, 0.320, 0.652, 0.210, 0.634),
    ("C", 0.140, 0.622, 0.075, 0.586, 0.008, 0.520),
    ("Z",),
]

BLUE_WHALE_EYE = (0.118, 0.452)
BLUE_WHALE_MOUTH = [
    ("M", 0.012, 0.545),
    ("C", 0.060, 0.556, 0.110, 0.566, 0.166, 0.570),
    ("C", 0.226, 0.574, 0.288, 0.572, 0.340, 0.566),
]

# Tall, upright pectoral fin. Used for the "humpback rising" beat, where the fin
# is the subject rather than a detail on a body.
WHALE_FIN_UP = [
    ("M", 0.470, 0.930),
    ("C", 0.420, 0.800, 0.400, 0.660, 0.408, 0.540),
    ("C", 0.412, 0.420, 0.452, 0.300, 0.494, 0.210),
    ("C", 0.520, 0.140, 0.552, 0.070, 0.578, 0.020),
    ("C", 0.606, 0.090, 0.618, 0.190, 0.618, 0.290),
    ("C", 0.618, 0.420, 0.604, 0.560, 0.576, 0.680),
    ("C", 0.566, 0.770, 0.552, 0.860, 0.536, 0.930),
    ("Z",),
]


# ---------------------------------------------------------------------------
# Great white shark. Distinct from the Megalodon silhouette above: narrower
# snout, lunate tail, a second small dorsal, and a much sharper pectoral.
# ---------------------------------------------------------------------------
GREAT_WHITE = [
    ("M", 0.985, 0.545),
    ("C", 0.930, 0.500, 0.880, 0.470, 0.830, 0.452),
    ("C", 0.790, 0.398, 0.762, 0.338, 0.740, 0.300),
    ("C", 0.716, 0.346, 0.700, 0.398, 0.686, 0.436),
    ("C", 0.600, 0.420, 0.520, 0.418, 0.440, 0.428),
    ("C", 0.400, 0.398, 0.372, 0.368, 0.348, 0.348),
    ("C", 0.352, 0.398, 0.360, 0.440, 0.366, 0.468),
    ("C", 0.330, 0.478, 0.296, 0.490, 0.268, 0.500),
    ("C", 0.250, 0.560, 0.240, 0.600, 0.226, 0.628),
    ("C", 0.200, 0.600, 0.176, 0.578, 0.156, 0.570),
    ("C", 0.170, 0.606, 0.176, 0.636, 0.178, 0.658),
    ("C", 0.160, 0.668, 0.132, 0.660, 0.108, 0.642),
    ("C", 0.094, 0.700, 0.076, 0.752, 0.052, 0.792),
    ("C", 0.030, 0.740, 0.014, 0.690, 0.006, 0.646),
    ("C", 0.004, 0.606, 0.004, 0.572, 0.008, 0.548),
    ("C", 0.250, 0.560, 0.560, 0.556, 0.760, 0.552),
    ("C", 0.850, 0.550, 0.930, 0.550, 0.985, 0.545),
    ("Z",),
]

GREAT_WHITE_EYE = (0.951, 0.522)

# ---------------------------------------------------------------------------
# Krill — a single body plus a fan of legs and antennae. Drawn as one path so the
# swarm in the reference reads as thousands of small soft shapes.
# ---------------------------------------------------------------------------
KRILL = [
    ("M", 0.060, 0.500),
    ("C", 0.120, 0.420, 0.240, 0.380, 0.400, 0.378),
    ("C", 0.560, 0.376, 0.700, 0.402, 0.800, 0.440),
    ("C", 0.870, 0.466, 0.920, 0.492, 0.950, 0.510),
    ("C", 0.920, 0.536, 0.870, 0.556, 0.800, 0.570),
    ("C", 0.700, 0.600, 0.560, 0.612, 0.400, 0.606),
    ("C", 0.240, 0.600, 0.120, 0.572, 0.060, 0.500),
    ("Z",),
]


# ---------------------------------------------------------------------------
# Detail sets for the animals above
# ---------------------------------------------------------------------------
def blue_whale_pleats(n=26, x0=0.045, x1=0.46, y0=0.560):
    """Long parallel grooves down the throat, the blue whale's defining texture."""
    lines = []
    for i in range(n):
        k = i / max(1, n - 1)
        y = y0 + k * 0.070
        lines.append([(x0 + k * 0.030, y), (x1 - k * 0.045, y + k * 0.012)])
    return lines


def shark_teeth_row(n=14, x0=0.760, x1=0.960, y=0.578):
    """A tight row of small triangles along the jaw."""
    out = []
    for i in range(n):
        k = i / max(1, n - 1)
        x = x0 + k * (x1 - x0)
        h = 0.016
        out.append([(x, y), (x + 0.006, y + h), (x + 0.012, y)])
    return out


def great_white_gills(n=5, x=0.760, y=0.470, step=0.020, h=0.070):
    return [[(x + i * step, y), (x + i * step - 0.004, y + h)] for i in range(n)]


def checks():
    """Every path must close and stay inside the unit box."""
    import math as _m
    for name in ("BLUE_WHALE", "WHALE_FIN_UP", "GREAT_WHITE", "KRILL"):
        p = globals()[name]
        assert p[-1][0] == "Z", name + " does not close"
        for op in p:
            for v in op[1:]:
                assert 0.0 <= v <= 1.0, (name, op)
    for fn in (blue_whale_pleats(), shark_teeth_row(), great_white_gills()):
        for line in fn:
            for (x, y) in line:
                assert 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0, (fn, x, y)
    return True


# ---------------------------------------------------------------------------
# Profile builder
# ---------------------------------------------------------------------------
def _catmull(points, closed=False):
    """Smooth C-segment path through `points` (Catmull-Rom -> cubic Bezier).

    Hand-writing control points for a 200-pixel-wide animal is how you end up with
    a shark whose tail is three unrelated polygons; specifying the outline as a
    top edge and a bottom edge and letting this smooth them is both faster to
    author and impossible to break.
    """
    pts = [(float(x), float(y)) for x, y in points]
    n = len(pts)
    if n < 3:
        return [("M", *pts[0]), ("L", *pts[-1]), ("Z",)]
    out = [("M", *pts[0])]
    for i in range(n - 1):
        p0 = pts[i - 1] if i > 0 else (2 * pts[0][0] - pts[1][0], 2 * pts[0][1] - pts[1][1])
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < n else (2 * pts[-1][0] - pts[-2][0], 2 * pts[-1][1] - pts[-2][1])
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        out.append(("C", c1[0], c1[1], c2[0], c2[1], p2[0], p2[1]))
    out.append(("Z",))
    return out


def profile(top, bottom):
    """Close a top profile and a bottom profile into one smooth silhouette."""
    top = [(max(0.0, min(1.0, x)), max(0.0, min(1.0, y))) for x, y in top]
    bottom = [(max(0.0, min(1.0, x)), max(0.0, min(1.0, y))) for x, y in bottom]
    return _catmull(top + bottom, closed=True)


# Blue whale: head at the left, blunt rostrum, flat back, 4 % dorsal set far aft.
BLUE_WHALE = profile(
    [(0.030, 0.470), (0.050, 0.395), (0.110, 0.342), (0.220, 0.318), (0.360, 0.310),
     (0.500, 0.312), (0.620, 0.322), (0.720, 0.336), (0.790, 0.350),
     # dorsal
     (0.812, 0.322), (0.828, 0.306), (0.842, 0.318), (0.852, 0.352),
     # peduncle
     (0.900, 0.368), (0.940, 0.392), (0.966, 0.418),
     (0.995, 0.372), (0.995, 0.470), (0.966, 0.470)],
    [(0.030, 0.470), (0.042, 0.545), (0.090, 0.596), (0.180, 0.626), (0.320, 0.642),
     (0.470, 0.648), (0.610, 0.644), (0.730, 0.628), (0.830, 0.596),
     (0.890, 0.556), (0.930, 0.520), (0.966, 0.500), (0.995, 0.580), (0.995, 0.470)],
)

BLUE_WHALE_EYE = (0.100, 0.452)
BLUE_WHALE_MOUTH = [
    ("M", 0.034, 0.500),
    ("C", 0.090, 0.516, 0.160, 0.526, 0.240, 0.528),
    ("C", 0.300, 0.529, 0.360, 0.526, 0.410, 0.520),
]

# Great white: pointed snout right, lunate caudal fin, small second dorsal.
GREAT_WHITE = profile(
    [(0.995, 0.560), (0.930, 0.520), (0.860, 0.492), (0.800, 0.470),
     # first dorsal
     (0.762, 0.430), (0.740, 0.330), (0.722, 0.398), (0.700, 0.452),
     # second dorsal
     (0.610, 0.436), (0.596, 0.398), (0.582, 0.432),
     # caudal upper lobe
     (0.520, 0.420), (0.400, 0.412), (0.300, 0.418), (0.230, 0.430),
     (0.180, 0.400), (0.140, 0.352), (0.118, 0.330),
     (0.128, 0.420), (0.146, 0.500), (0.150, 0.560)],
    [(0.995, 0.560), (0.955, 0.588), (0.900, 0.606), (0.840, 0.618),
     # pectoral
     (0.800, 0.660), (0.760, 0.720), (0.740, 0.760),
     (0.716, 0.700), (0.700, 0.648), (0.680, 0.628),
     (0.600, 0.628), (0.500, 0.632), (0.380, 0.640), (0.280, 0.652),
     (0.220, 0.672), (0.180, 0.700), (0.150, 0.700),
     (0.134, 0.648), (0.128, 0.600), (0.150, 0.560)],
)

GREAT_WHITE_EYE = (0.944, 0.536)

# Humpback pectoral fin, the animal's signature. Long, narrow at the root,
# widest at about a third of its length, tapering to a rounded knobbly tip.
# Both edges must actually diverge or the closed path self-intersects and PIL
# fills it as a needle, which is what the first version looked like.
WHALE_FIN_UP = profile(
    [(0.500, 0.020), (0.556, 0.110), (0.590, 0.230), (0.606, 0.360),
     (0.604, 0.480), (0.586, 0.600), (0.562, 0.700), (0.544, 0.790), (0.530, 0.860),
     (0.520, 0.930)],
    [(0.500, 0.020), (0.452, 0.120), (0.414, 0.250), (0.396, 0.390),
     (0.398, 0.510), (0.416, 0.630), (0.446, 0.730), (0.474, 0.810), (0.500, 0.870),
     (0.520, 0.930)],
)

KRILL = profile(
    [(0.030, 0.470), (0.090, 0.402), (0.200, 0.372), (0.340, 0.366),
     (0.480, 0.376), (0.620, 0.404), (0.740, 0.442), (0.830, 0.478), (0.900, 0.492)],
    [(0.030, 0.470), (0.080, 0.530), (0.180, 0.572), (0.320, 0.590),
     (0.470, 0.592), (0.610, 0.578), (0.730, 0.548), (0.820, 0.514), (0.900, 0.492)],
)
