"""
Shaded vector shapes — the thing that separates "clip art" from the reference.

The reference's animals are not flat silhouettes. Measured at full resolution: the
humpback's back is near-black at the top, its belly is mid-grey, the dorsal ridge
carries a highlight, and the baleen is a separate gold comb. The orca has a
gradient down its flank. That shading is why it reads as a lit object.

This module gives every path three extra tools:

  fill_shaded()  a vertical (or angled) gradient clipped to the path's own mask,
                 so a single bezier contour can be lit top-to-bottom.
  rim_light()    a soft bright edge along the top of the shape, which is what sells
                 "there is a light source above and behind".
  streaks()      low-contrast horizontal marks inside the mask, for hide texture.

Everything is drawn through an 8-bit mask built from the same flattened contour, so
a detail can never spill outside the animal it belongs to.
"""
from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageFilter

from .bezier import flatten, to_pixels


def mask_from_path(size, path, bbox, flip=False, shear=0.0, segs=30, blur=0):
    w, h = size
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    pts = to_pixels(flatten(path, segs), bbox, flip=flip, shear=shear)
    if len(pts) >= 3:
        d.polygon(pts, fill=255)
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    return m


def _grad_image(size, stops, angle=90):
    """stops: [(pos 0..1, (r,g,b)), ...]. angle 90 = top to bottom."""
    w, h = size
    img = Image.new("RGB", (1, max(2, h)))
    d = ImageDraw.Draw(img)
    stops = sorted(stops, key=lambda s: s[0])
    for y in range(img.height):
        t = y / (img.height - 1)
        # find the surrounding stops
        lo = stops[0]
        hi = stops[-1]
        for i in range(len(stops) - 1):
            if stops[i][0] <= t <= stops[i + 1][0]:
                lo, hi = stops[i], stops[i + 1]
                break
        span = max(1e-6, hi[0] - lo[0])
        k = (t - lo[0]) / span
        col = tuple(int(lo[1][c] + (hi[1][c] - lo[1][c]) * k) for c in range(3))
        d.point((0, y), fill=col)
    return img.resize((w, h), Image.BILINEAR)


def fill_shaded(f, path, bbox, stops, flip=False, shear=0.0, segs=30, alpha=1.0):
    """Fill `path` with a vertical gradient. This is the single change that made the
    biggest difference to how the animals read."""
    if alpha <= 0:
        return
    w, h = f.im.size
    mask = mask_from_path((w, h), path, bbox, flip=flip, shear=shear, segs=segs)
    grad = _grad_image((w, h), stops)
    if alpha < 1:
        mask = mask.point(lambda v: int(v * alpha))
    f.im.paste(grad, (0, 0), mask)


def rim_light(f, path, bbox, colour=(190, 220, 230), width=3, alpha=0.45,
              flip=False, shear=0.0, segs=30, blur=2):
    """A soft bright edge just inside the top of the shape.

    Implemented as: mask, shifted down a few px, subtracted — that leaves a crescent
    along the upper contour, which is exactly where a rim light lands.
    """
    if alpha <= 0:
        return
    w, h = f.im.size
    m = mask_from_path((w, h), path, bbox, flip=flip, shear=shear, segs=segs)
    m2 = Image.new("L", (w, h), 0)
    m2.paste(m, (0, max(1, width * 2)))
    rim = Image.eval(Image.merge("L", [m]), lambda v: v)
    from PIL import ImageChops
    rim = ImageChops.subtract(m, m2)
    rim = rim.filter(ImageFilter.GaussianBlur(blur))
    rim = rim.point(lambda v: int(v * alpha))
    col = Image.new("RGB", (w, h), colour)
    f.im.paste(col, (0, 0), rim)


def streaks(f, path, bbox, colour=(150, 175, 185), alpha=0.10, n=26, seed=7,
            flip=False, shear=0.0, segs=30):
    """Horizontal hide marks inside the shape. Low contrast on purpose — the reference
    uses the same trick and it reads as skin rather than as pattern."""
    w, h = f.im.size
    mask = mask_from_path((w, h), path, bbox, flip=flip, shear=shear, segs=segs)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, bw, bh = bbox
    r = seed
    for i in range(n):
        r = (r * 1103515245 + 12345) & 0x7FFFFFFF
        yy = y0 + ((r >> 8) % 1000) / 1000 * bh
        ln = bw * (0.10 + ((r >> 3) % 100) / 100 * 0.35)
        sx = x0 + ((r >> 5) % 1000) / 1000 * (bw - ln)
        d.line([(sx, yy), (sx + ln, yy - 1)], fill=colour + (int(255 * alpha),), width=2)
    layer.putalpha(Image.composite(layer.split()[3], Image.new("L", (w, h), 0), mask))
    f.im.paste(layer.convert("RGB"), (0, 0), layer)


def detail_strokes(f, strokes, colour, width, alpha=1.0):
    """Draw a list of polylines (already in pixels). Used for pleats, teeth rows and
    the knobs along a flipper — the details that make the animal identifiable."""
    if alpha <= 0:
        return
    col = tuple(colour) + (int(255 * alpha),)
    for s in strokes:
        if len(s) >= 2:
            f.d.line(s, fill=col, width=width, joint="curve")
