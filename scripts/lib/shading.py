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


# ---------------------------------------------------------------------------
# Depth of field
# ---------------------------------------------------------------------------
def paste_dof(f, layer, xy, blur=0.0, alpha=1.0, haze=None):
    """Paste an RGBA layer with optional blur and aerial haze.

    In the reference nothing is uniformly sharp: the animal that is meant to be far
    away is both blurred and pushed toward the water colour. A blur alone still
    reads as a sharp sticker you cannot focus on; haze alone leaves hard edges.
    Together they read as distance.
    """
    im = layer
    if blur > 0.2:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    if haze is not None:
        hz = Image.new("RGBA", im.size, haze + (int(255 * alpha),))
        im = Image.alpha_composite(im, hz)
        alpha = 1.0
    if alpha < 0.999:
        a = im.getchannel("A").point(lambda v: int(v * alpha))
        im = im.copy()
        im.putalpha(a)
    f.im.paste(im, (int(xy[0]), int(xy[1])), im)


def animal_layer(size, path, bbox, stops, flip=False, segs=30, glow=None):
    """Render one shaded animal onto its own transparent tile.

    Drawing straight onto the frame makes blurring a distant animal impossible,
    because the blur would pick up the water behind it. Every animal that has to be
    depth-graded is built here first.
    """
    tile = Image.new("RGBA", size, (0, 0, 0, 0))
    if glow:
        pass
    g = Image.new("RGBA", size, (0, 0, 0, 0))
    class _F:  # minimal frame so fill_shaded can draw into the tile
        pass
    fr = _F()
    fr.im = tile.convert("RGB")
    fr.d = ImageDraw.Draw(fr.im, "RGBA")
    fr.w, fr.h = size
    fill_shaded(fr, path, bbox, stops, flip=flip, segs=segs)
    mask = mask_from_path(size, path, bbox, flip=flip, segs=segs)
    out = fr.im.convert("RGBA")
    out.putalpha(mask)
    return out
