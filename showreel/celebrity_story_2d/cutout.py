"""Turn a flat chroma-green character plate into an animated cut-out.

Keeps a soft alpha matte (with spill suppression on the edge), then deforms the
figure with a small skeleton: bend, lean, head tilt, and limb rotation. That is
how 2D cut-out animation actually works, and it keeps the painted art intact
instead of redrawing it.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageFilter

import core2d as C


def key_green(path, key=(8, 169, 67), tol=0.16, feather=2.0):
    """Return (rgb float, alpha float) with green removed and despilled."""
    im = Image.open(path).convert('RGB')
    a = np.asarray(im).astype(np.float32) / 255.0
    k = np.array([key[0], key[1], key[2]], np.float32) / 255.0

    # chroma distance in a green-dominant projection, tolerant of shading
    g = a[..., 1]
    rb = (a[..., 0] + a[..., 2]) * 0.5
    excess = g - rb                       # green screen: high, figure: ~0
    alpha = 1.0 - np.clip((excess - tol) / 0.20, 0, 1)
    alpha[g < 0.10] = np.maximum(alpha[g < 0.10], 0.0)
    # keep dark hair/shoes that are low-chroma but not green
    alpha = np.where((np.abs(excess) < tol) & (g > rb + tol), 0.0, alpha)

    m = Image.fromarray((alpha * 255).astype(np.uint8))
    if feather > 0:
        m = m.filter(ImageFilter.GaussianBlur(feather))
    alpha = np.asarray(m).astype(np.float32) / 255.0
    # harden the interior so the figure stays opaque
    alpha = np.clip(alpha * 1.35, 0, 1)

    # despill: clamp green toward the red/blue average anywhere it exceeds it,
    # weighted by how close the pixel is to the matte edge (where spill lives)
    edge = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(2.5))).astype(np.float32) / 255.0
    band = np.clip(np.abs(alpha - edge) * 2.2 + 0.25, 0, 1)
    excess2 = np.clip(g - rb, 0, 1) * band
    rgb = a.copy()
    rgb[..., 1] = g - excess2 * 1.35
    # last line of defence: force the outermost 1px inward, where the fringe lives
    hard = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8))
                      .filter(ImageFilter.MinFilter(3))).astype(np.float32) / 255.0
    fringe = np.clip(alpha - hard, 0, 1)
    rgb[..., 1] = rgb[..., 1] * (1 - fringe * 0.55) + rb * fringe * 0.55
    alpha = np.clip(alpha - fringe * 0.45, 0, 1)
    return np.clip(rgb, 0, 1), alpha


def trim(rgb, alpha, pad=8):
    ys, xs = np.nonzero(alpha > 0.03)
    if len(xs) == 0:
        raise ValueError('empty matte')
    x0, x1 = max(0, xs.min() - pad), min(alpha.shape[1], xs.max() + pad)
    y0, y1 = max(0, ys.min() - pad), min(alpha.shape[0], ys.max() + pad)
    return rgb[y0:y1, x0:x1], alpha[y0:y1, x0:x1]


def to_layer(rgb, alpha):
    """(rgb, alpha) -> straight-alpha RGBA PIL image."""
    rgba = np.dstack([np.clip(rgb, 0, 1), np.clip(alpha, 0, 1)])
    return Image.fromarray((rgba * 255 + .5).astype(np.uint8), 'RGBA')


def place(canvas, layer, x, y, scale=1.0, rot=0.0, flip=False, alpha=1.0,
          squash=(1.0, 1.0)):
    """Draw an RGBA cut-out onto a float canvas with its *feet* at (x, y)."""
    im = layer
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    w, h = im.size
    nw, nh = max(1, int(round(w * scale * squash[0]))), max(1, int(round(h * scale * squash[1])))
    if (nw, nh) != (w, h):
        im = im.resize((nw, nh), Image.LANCZOS)
    if abs(rot) > 0.01:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    arr = np.asarray(im).astype(np.float32) / 255.0
    a = arr[..., 3:4] * alpha
    return C.paste_rgb(canvas, arr[..., :3] * alpha, a[..., 0], xy=(x - im.size[0] / 2, y - im.size[1]))


def silhouette_blur(rgb, alpha, radius, tint=(0, 0, 0), amount=1.0):
    """Out-of-focus copy of a cut-out, for foreground bokeh and depth racks."""
    a = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(radius))).astype(np.float32) / 255.0 * amount
    rgb_b = C.gauss(rgb, radius)
    tintarr = np.array(tint, np.float32)
    mix = 0.55
    rgb_b = rgb_b * (1 - mix) + tintarr[None, None, :] * mix
    return rgb_b, a


def shadow_under(canvas, x, y, rx, ry, strength=0.55, softness=1.1):
    h, w = canvas.shape[:2]
    m = C.soft_ellipse((w, h), (x, y), rx, ry, softness=softness)
    return canvas * (1 - (m * strength)[..., None])


def limb_swing(rgb, alpha, pivot, angle, region, power=1.6):
    """Shear a region around a pivot: cheap but effective limb motion for cut-outs."""
    if abs(angle) < 0.05:
        return rgb, alpha
    h, w = alpha.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    px, py = pivot
    rx, ry = region
    d = np.sqrt(((xx - px) / max(rx, 1)) ** 2 + ((yy - py) / max(ry, 1)) ** 2)
    wgt = np.clip(1.0 - d, 0, 1) ** power
    a = math.radians(angle)
    sx, sy = xx - px, yy - py
    mx = px + sx * math.cos(a) - sy * math.sin(a)
    my = py + sx * math.sin(a) + sy * math.cos(a)
    mx = xx + (mx - xx) * wgt
    my = yy + (my - yy) * wgt
    rgba = np.dstack([rgb, alpha])
    out = np.zeros_like(rgba)
    xi = np.clip(mx.round().astype(np.int32), 0, w - 1)
    yi = np.clip(my.round().astype(np.int32), 0, h - 1)
    out[yi, xi] = rgba
    # fill pinholes
    holes = out[..., 3] < 0.02
    filled = np.stack([C.gauss(out[..., i], 1.2) for i in range(4)], -1)
    out = np.where(holes[..., None], filled, out)
    return out[..., :3], out[..., 3]
