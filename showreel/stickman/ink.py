"""Ink: turning a polyline into a mark that looks like it was drawn.

The previous renderer drew every segment as a constant-width capsule. That is
correct in the same way a wireframe is correct: the geometry is right and it
still looks like software. Three things separate an inked line from a stroke:

  pressure   a pen is heavier where it slows down, which on a limb is the joint
             and not the middle
  taper      a stroke thins as the nib lifts, so the ends are never blunt
  grain      ink sits unevenly on paper; a perfectly uniform edge reads as vector

This renderer draws each stroke as a polygon whose two edges are offset by a
width profile sampled along the stroke, plus a soft round cap at each end. It is
antialiased by drawing at 2x and averaging down. The result is still pure
geometry -- no bitmap is ever pasted -- but it stops looking like a schematic.
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SS = 2  # supersample factor


def _profile(n, *, w0, w1, wmid=None, peak=0.55):
    """Width at ``n`` samples along a stroke.

    A cubic ease from w0 at the start to w1 at the end, with a bulge of
    ``wmid`` extra width around ``peak`` of the way along. Real ink is heaviest
    where the hand pressed hardest, which is rarely the very end.
    """
    t = np.linspace(0.0, 1.0, n)
    base = w0 + (w1 - w0) * (t ** 1.25)
    if wmid:
        bulge = np.exp(-((t - peak) ** 2) / (2.0 * 0.16 ** 2))
        base = base + wmid * bulge
    return base


def stroke(draw, p0, p1, width, value, *, taper_start=0.55, taper_end=0.55,
           bulge=0.10, samples=14, cap=True):
    """Draw one tapered, slightly barrel-shaped stroke onto a mask image."""
    p0 = np.asarray(p0, float)
    p1 = np.asarray(p1, float)
    d = p1 - p0
    length = float(np.hypot(d[0], d[1]))
    if length < 1e-4:
        r = width * 0.5
        draw.ellipse([p0[0] - r, p0[1] - r, p0[0] + r, p0[1] + r], fill=value)
        return

    u = d / length
    n = np.array([-u[1], u[0]])
    t = np.linspace(0.0, 1.0, samples)
    pts = p0[None, :] + d[None, :] * t[:, None]

    # Width in pixels: taper both ends, bulge in the middle.
    w = _profile(samples, w0=width * taper_start, w1=width * taper_end,
                 wmid=width * bulge)
    left = pts + n[None, :] * (w * 0.5)[:, None]
    right = pts - n[None, :] * (w * 0.5)[:, None]

    poly = np.concatenate([left, right[::-1]], axis=0)
    draw.polygon([tuple(q) for q in poly], fill=value)

    if cap:
        for p, r in ((pts[0], w[0] * 0.5), (pts[-1], w[-1] * 0.5)):
            draw.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=value)


def ring(draw, centre, radius, thickness, value, *, samples=72):
    """An annulus, drawn as a true ring rather than a disc with a hole.

    The head in a stick figure is a circle, and how that circle is drawn is half
    the character. A constant-thickness annulus reads mechanical; this one is
    slightly heavier at the bottom, where a hand naturally presses.
    """
    cx, cy = centre
    outer, inner = [], []
    for i in range(samples + 1):
        a = 2.0 * math.pi * i / samples
        # Heavier at the bottom of the ring (a = pi/2 in screen space).
        press = 1.0 + 0.16 * math.sin(a)
        ro = radius + thickness * 0.5 * press
        ri = radius - thickness * 0.5 * press
        outer.append((cx + math.cos(a) * ro, cy + math.sin(a) * ro))
        inner.append((cx + math.cos(a) * ri, cy + math.sin(a) * ri))
    draw.polygon([tuple(q) for q in outer + inner[::-1]], fill=value)


def disc(draw, centre, radius, value, *, squash_y=1.0):
    cx, cy = centre
    draw.ellipse([cx - radius, cy - radius * squash_y,
                  cx + radius, cy + radius * squash_y], fill=value)


def paper_grain(size, *, seed=0, amount=0.5):
    """A soft fibrous mask used to break up the ink edges.

    Multiplied into the ink's alpha at low strength, this makes an edge wander by
    a fraction of a pixel the way ink bleeds into paper. It is generated, not
    sampled from a texture file, so there is still no pasted imagery anywhere.
    """
    rng = np.random.default_rng(seed)
    h, w = size[1], size[0]
    n = rng.standard_normal((h, w)).astype(np.float32)
    img = Image.fromarray(((n * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8))
    img = img.filter(ImageFilter.GaussianBlur(1.1))
    a = np.asarray(img, np.float32) / 255.0
    lo, hi = a.min(), a.max()
    a = (a - lo) / max(hi - lo, 1e-6)
    return 1.0 - amount * 0.25 * (a - 0.5)
