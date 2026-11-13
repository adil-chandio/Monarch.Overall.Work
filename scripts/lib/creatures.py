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
