"""
A tiny bezier path engine, so silhouettes are continuous curves and not a pile of
ellipses.

Why this file exists: the first attempt at this film drew animals by stacking
circles and polygons. The operator looked at one full-resolution frame and said it
looked like a pile of circles — which was exactly right. Filled ellipses cannot
make a body outline, because a body outline is one continuous contour whose width
changes smoothly.

So: cubic bezier segments, flattened at sub-pixel density, filled as a single
polygon. That is how every vector tool does it, and it is 120 lines, so there is
no reason to approximate it with blobs.

Coordinates are in a unit box: x and y both 0..1 relative to the shape's bounding
box. A shape is placed with `draw_path(im, d, path, bbox, fill)`.
"""
from __future__ import annotations

import math


def _cubic(p0, p1, p2, p3, n):
    out = []
    for i in range(1, n + 1):
        t = i / n
        u = 1 - t
        x = u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0]
        y = u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1]
        out.append((x, y))
    return out


def flatten(path, segments_per_curve: int = 28):
    """Turn a path into a dense point list.

    `path` is a list of tuples:
        ("M", x, y)                  move to
        ("L", x, y)                  line to
        ("C", cx1, cy1, cx2, cy2, x, y)   cubic bezier to
        ("Q", cx, cy, x, y)          quadratic, converted to cubic
        ("Z",)                       close

    Every curve is flattened to `segments_per_curve` points. 28 is chosen so that
    at a 1000 px bounding box one segment is under 1.3 px — below the threshold
    where a flattening artefact is visible, and still fast enough to render 3000
    frames.
    """
    pts: list[tuple[float, float]] = []
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    for cmd in path:
        op = cmd[0]
        if op == "M":
            cur = (cmd[1], cmd[2])
            start = cur
            pts.append(cur)
        elif op == "L":
            cur = (cmd[1], cmd[2])
            pts.append(cur)
        elif op == "C":
            p1, p2, p3 = (cmd[1], cmd[2]), (cmd[3], cmd[4]), (cmd[5], cmd[6])
            pts.extend(_cubic(cur, p1, p2, p3, segments_per_curve))
            cur = p3
        elif op == "Q":
            # quadratic -> cubic: c1 = p0 + 2/3(q-p0), c2 = p3 + 2/3(q-p3)
            q, p3 = (cmd[1], cmd[2]), (cmd[3], cmd[4])
            c1 = (cur[0] + 2 / 3 * (q[0] - cur[0]), cur[1] + 2 / 3 * (q[1] - cur[1]))
            c2 = (p3[0] + 2 / 3 * (q[0] - p3[0]), p3[1] + 2 / 3 * (q[1] - p3[1]))
            pts.extend(_cubic(cur, c1, c2, p3, segments_per_curve))
            cur = p3
        elif op == "Z":
            pts.append(start)
            cur = start
    return pts


def to_pixels(pts, bbox, flip=False, shear=0.0):
    """Map unit-box points onto the canvas.

    `shear` is a small horizontal offset per unit of y, in unit-box terms. A whale
    body is not a rectangle: its tail sits higher than its jaw, and a shear of
    -0.04 to +0.04 is enough to give a silhouette the lean that reads as motion.
    """
    x0, y0, w, h = bbox
    out = []
    for px, py in pts:
        ux = (1 - px) if flip else px
        ux += shear * py
        out.append((x0 + ux * w, y0 + py * h))
    return out


def draw_path(d, path, bbox, fill, flip=False, shear=0.0, segs=28):
    pts = to_pixels(flatten(path, segs), bbox, flip=flip, shear=shear)
    if len(pts) >= 3:
        d.polygon(pts, fill=fill)
    return pts


def stroke_path(d, path, bbox, fill, width=3, flip=False, shear=0.0, segs=28):
    pts = to_pixels(flatten(path, segs), bbox, flip=flip, shear=shear)
    if len(pts) >= 2:
        d.line(pts, fill=fill, width=width, joint="curve")
    return pts


def bbox_of(path, bbox, flip=False, shear=0.0, segs=28):
    pts = to_pixels(flatten(path, segs), bbox, flip=flip, shear=shear)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)
