"""Cel animation primitives for the painted 2D cut.

A cel is a painted character on a flat grey field. It is keyed off that field,
trimmed, normalised to a common height and kept as float RGB + alpha. Poses are
blended with a *weighted displacement* warp: the alpha of both cels is smoothed
into a shape field and each output pixel samples a weighted average of the two
source images. That produces the soft in-between you get from a real assistant
penciller, without the double-limb ghosting a plain cross-dissolve gives.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageFilter

TARGET_H = 1000


# ------------------------------------------------------------------ matting
def cut_grey(path, tol=10.0, feather=1.1):
    """Key a character off a flat grey (#808080) field.

    The field is measured from the plate corners, then a soft chroma/luma
    distance key is built. Grey is desaturated *and* mid-luma, so distance is
    measured against the exact background colour, not just saturation.
    """
    im = Image.open(path).convert('RGB')
    a = np.asarray(im).astype(np.float32) / 255.0
    h, w = a.shape[:2]
    border = np.concatenate([a[0:4].reshape(-1, 3), a[-4:].reshape(-1, 3),
                             a[:, 0:4].reshape(-1, 3), a[:, -4:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    dist = np.sqrt(((a - bg[None, None, :]) ** 2).sum(axis=2))
    alpha = np.clip((dist - tol / 255.0) / 0.055, 0, 1)
    # a soft floor cut kills the faint plate noise in the flat field
    alpha[dist < tol / 255.0 * 1.4] = 0.0
    if feather:
        m = Image.fromarray((alpha * 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(feather))
        alpha = np.asarray(m).astype(np.float32) / 255.0
    # harden the interior, keep the edge soft
    alpha = np.clip(alpha * 1.22, 0, 1)
    # decontaminate: pull edge pixels toward the interior colour
    inner = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).filter(
        ImageFilter.MinFilter(5))).astype(np.float32) / 255.0
    band = np.clip(alpha - inner, 0, 1)[..., None]
    rgb = a * (1 - band * 0.55) + bg[None, None, :] * (band * 0.55)
    rgb = np.clip(rgb, 0, 1)
    return rgb.astype(np.float32), alpha.astype(np.float32)


def cut_green(path, tol=0.16, feather=1.1):
    """Key a character off a chroma-green field (the committed cel sheets)."""
    im = Image.open(path).convert('RGB')
    a = np.asarray(im).astype(np.float32) / 255.0
    g = a[..., 1]
    rb = (a[..., 0] + a[..., 2]) * 0.5
    excess = g - rb
    alpha = np.clip(1.0 - (excess - tol) / 0.20, 0, 1)
    if feather:
        m = Image.fromarray((alpha * 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(feather))
        alpha = np.asarray(m).astype(np.float32) / 255.0
    alpha = np.clip(alpha * 1.3, 0, 1)
    edge = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(2.5))).astype(np.float32) / 255.0
    band = np.clip(np.abs(alpha - edge) * 2.2 + 0.25, 0, 1)
    rgb = a.copy()
    rgb[..., 1] = g - np.clip(excess, 0, 1) * band * 1.35
    hard = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).filter(
        ImageFilter.MinFilter(3))).astype(np.float32) / 255.0
    fringe = np.clip(alpha - hard, 0, 1)
    rgb[..., 1] = rgb[..., 1] * (1 - fringe * 0.55) + rb * fringe * 0.55
    alpha = np.clip(alpha - fringe * 0.45, 0, 1)
    return np.clip(rgb, 0, 1).astype(np.float32), alpha.astype(np.float32)


def trim(rgb, alpha, pad=6):
    ys, xs = np.nonzero(alpha > 0.03)
    if len(xs) == 0:
        raise ValueError('empty matte')
    x0, x1 = max(0, xs.min() - pad), min(alpha.shape[1], xs.max() + pad + 1)
    y0, y1 = max(0, ys.min() - pad), min(alpha.shape[0], ys.max() + pad + 1)
    return rgb[y0:y1, x0:x1], alpha[y0:y1, x0:x1]


def resize_float(rgb, alpha, size):
    r = np.asarray(Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))
                   .resize(size, Image.LANCZOS)).astype(np.float32) / 255.0
    a = np.asarray(Image.fromarray((np.clip(alpha, 0, 1) * 255).astype(np.uint8))
                   .resize(size, Image.LANCZOS)).astype(np.float32) / 255.0
    return r, a


# ---------------------------------------------------------------------- cel
class Cel:
    """A painted character pose, normalised so all poses share one height."""

    __slots__ = ('name', 'rgb', 'alpha', 'h', 'w', 'pivot', 'head_box')

    def __init__(self, name, rgb, alpha, head=None):
        self.name = name
        self.rgb = rgb
        self.alpha = alpha
        self.h, self.w = alpha.shape
        # the head is the top ~19% of the figure; its centre is the pivot every
        # pose is aligned on, so a swinging arm or leg never shifts the body
        band = alpha[:max(4, int(self.h * 0.19))]
        ys, xs = np.nonzero(band > 0.5)
        if len(xs):
            self.pivot = float((xs.min() + xs.max()) / 2.0)
            self.head_box = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
        else:
            self.pivot = self.w / 2.0
            self.head_box = (0, 0, self.w, int(self.h * 0.19))

    def __repr__(self):
        return f'<Cel {self.name} {self.w}x{self.h}>'


def normalise(rgb, alpha, target_h=TARGET_H):
    h, w = alpha.shape
    s = target_h / float(h)
    return resize_float(rgb, alpha, (max(1, int(round(w * s))), target_h))


def load_cel(path, name, target_h=TARGET_H, key='grey'):
    rgb, alpha = (cut_grey if key == 'grey' else cut_green)(path)
    rgb, alpha = trim(rgb, alpha)
    rgb, alpha = normalise(rgb, alpha, target_h)
    return Cel(name, rgb, alpha)


# -------------------------------------------------------------------- warp
def _field(alpha, blur=9.0):
    """Smooth alpha -> shape field used as a warp weight."""
    a = Image.fromarray((np.clip(alpha, 0, 1) * 255).astype(np.uint8))
    a = a.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(a).astype(np.float32) / 255.0


def canvas_for(cela, celb):
    h = max(cela.h, celb.h)
    w = max(cela.w, celb.w) + 8
    return h, w


def _paste_centre(src_rgb, src_a, H, W, dy=0):
    """Place a cel in a common canvas, feet on the bottom edge, centred."""
    out_r = np.zeros((H, W, 3), np.float32)
    out_a = np.zeros((H, W), np.float32)
    h, w = src_a.shape
    x = (W - w) // 2
    y = H - h + dy
    x0, y0 = max(0, x), max(0, y)
    out_r[y0:y0 + h, x0:x0 + w] = src_rgb[:H - y0, :W - x0]
    out_a[y0:y0 + h, x0:x0 + w] = src_a[:H - y0, :W - x0]
    return out_r, out_a


def warp_between(rgb_a, alpha_a, rgb_b, alpha_b, k):
    """Pose-to-pose morph by weighted displacement, k in 0..1."""
    if k <= 0.001:
        return rgb_a, alpha_a
    if k >= 0.999:
        return rgb_b, alpha_b
    H, W = max(alpha_a.shape[0], alpha_b.shape[0]), max(alpha_a.shape[1], alpha_b.shape[1]) + 10
    ra, aa = _paste_centre(rgb_a, alpha_a, H, W)
    rb, ab = _paste_centre(rgb_b, alpha_b, H, W)
    fa = _field(aa)
    fb = _field(ab)
    kk = k * k * (3 - 2 * k)
    wa = np.clip(fa * (1 - kk), 0, 1)
    wb = np.clip(fb * kk, 0, 1)
    tot = wa + wb
    m = tot > 1e-3
    wa_m = np.where(m, wa / np.maximum(tot, 1e-3), 0.5)
    wb_m = 1.0 - wa_m
    # sample both sources with the same sub-pixel offsets: gentle arc, no slide
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    shift = 3.0 * math.sin(math.pi * kk)
    xa = np.clip(xx - shift * wa_m, 0, W - 1).astype(np.int32)
    xb = np.clip(xx + shift * wb_m, 0, W - 1).astype(np.int32)
    ya = np.clip(yy + 1.5 * kk * wa_m, 0, H - 1).astype(np.int32)
    yb = np.clip(yy - 1.5 * kk * wb_m, 0, H - 1).astype(np.int32)
    sa_r = ra[ya, xa]
    sa_a = aa[ya, xa]
    sb_r = rb[yb, xb]
    sb_a = ab[yb, xb]
    out_rgb = sa_r * wa_m[..., None] + sb_r * wb_m[..., None]
    out_a = sa_a * wa_m + sb_a * wb_m
    return out_rgb, out_a


def _align_on(cel, W, H):
    """Place a cel in a common canvas, anchored on its head pivot and feet."""
    out_r = np.zeros((H, W, 3), np.float32)
    out_a = np.zeros((H, W), np.float32)
    h, w = cel.alpha.shape
    x = int(round(W / 2.0 - cel.pivot))
    y = H - h
    x0 = max(0, x)
    x1 = min(W, x + w)
    src_x0 = x0 - x
    out_r[y:, x0:x1] = cel.rgb[:, src_x0:src_x0 + (x1 - x0)]
    out_a[y:, x0:x1] = cel.alpha[:, src_x0:src_x0 + (x1 - x0)]
    return out_r, out_a


_FACE_CACHE = {}

# Proportions read off the reference drawing (hero_casual, 1000 px tall):
#   head top 11, eye line 91, mouth line 131, face width 104, head height 142
HW_RATIO = 142.0 / 104.0        # head height / head width
FRAC_EYE = (91.0 - 11.0) / 142.0    # 0.563
FRAC_MOUTH = (131.0 - 11.0) / 142.0  # 0.845
FACE_W_RATIO = 104.0 / 100.0

# Landmarks read off the reference drawing on a printed grid, expressed as
# ratios of the head-box width. The head box itself comes from the alpha
# silhouette in the top tenth of the figure, which no arm swing can affect.
#   head top   11 px
#   eye line   91 px   -> (91 - 11) / 119 = 0.672 head-widths below the top
#   mouth line 131 px  -> (131 - 11) / 119 = 1.008
#   face width 100 px  -> 0.840 head-widths
RATIO_EYE = 0.755
RATIO_MOUTH = 1.075
RATIO_FACE_W = 0.800


def head_box(cel):
    """Head-only bounding box, taken from a narrow band at the very top.

    The band has to be narrow: at ten percent of the figure the shoulders of a
    three-quarter pose are already inside it, and the head measures far too
    wide.
    """
    h, w = cel.alpha.shape
    band = cel.alpha[:max(5, int(h * 0.045))]
    ys, xs = np.nonzero(band > 0.5)
    if len(xs) < 10:
        return (0, 0, w, max(1, int(h * 0.10)))
    return (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))


def face_metrics(cel):
    """Landmarks for a cel, in that cel's own pixel space."""
    m = _FACE_CACHE.get(cel.name)
    if m is not None:
        return m
    x0, y0, x1, y1 = head_box(cel)
    hw = float(max(8, x1 - x0))
    # head height comes from the head *width* (stable) rather than the band,
    # whose height is an artefact of where the band was cut
    hh = hw * HW_RATIO
    # landmarks as fractions of head height, measured on the reference drawing
    m = dict(
        cx=(x0 + x1) / 2.0,
        eye_y=y0 + hh * FRAC_EYE,
        mouth_y=y0 + hh * FRAC_MOUTH,
        face_w=hw * FACE_W_RATIO,
        top=float(y0),
        head_w=hw,
        head_h=hh,
    )
    _FACE_CACHE[cel.name] = m
    return m


def calibrate(cels):
    _FACE_CACHE.clear()
    for c in cels.values():
        face_metrics(c)
    return _FACE_CACHE


# ------------------------------------------------------------------ mouths
# A drawn mouth chart in *face-width* units: (width, height, teeth, round, lift)
MOUTH_CHART = {
    'none': (0.000, 0.000, 0.00, 0.0, 0.00),
    'M':    (0.300, 0.016, 0.00, 0.0, 0.02),   # closed
    'MBP':  (0.280, 0.010, 0.00, 0.0, 0.00),   # pressed
    'A':    (0.300, 0.150, 0.30, 0.35, 0.00),  # "ah"
    'E':    (0.345, 0.095, 0.55, 0.10, 0.08),  # "eh"
    'I':    (0.300, 0.065, 0.55, 0.00, 0.10),  # "ee"
    'O':    (0.232, 0.135, 0.06, 0.85, 0.00),  # "oh"
    'U':    (0.182, 0.082, 0.05, 0.80, 0.00),  # "oo"
    'F':    (0.272, 0.044, 0.70, 0.00, 0.05),  # "f/v"
    'L':    (0.254, 0.100, 0.35, 0.20, 0.03),  # "l/th"
}


class A_CEL_PROXY:
    def __init__(self, rgb, alpha):
        self.rgb = rgb
        self.alpha = alpha


def _lip_colour(cel_rgb, cel_alpha, m):
    """Sample the lip skin just below the mouth so the chart matches the art."""
    h, w = cel_alpha.shape
    y = int(min(h - 1, max(0, m['mouth_y'] + m['face_w'] * 0.11)))
    x0 = int(max(0, m['cx'] - m['face_w'] * 0.20))
    x1 = int(min(w, m['cx'] + m['face_w'] * 0.20))
    if x1 <= x0:
        return np.array([0.55, 0.33, 0.29], np.float32)
    patch = cel_rgb[max(0, y - 2):y + 3, x0:x1]
    a = cel_alpha[max(0, y - 2):y + 3, x0:x1]
    if patch.size == 0 or a.mean() < 0.5:
        return np.array([0.55, 0.33, 0.29], np.float32)
    return patch.reshape(-1, 3).mean(0).astype(np.float32)


def draw_mouth(cel_rgb, cel_alpha, m, viseme, amount=1.0, lip=None):
    """Draw one viseme from the mouth chart onto the cel's face, in place."""
    key = viseme if viseme in MOUTH_CHART else 'A'
    fw = max(6.0, m['face_w'])
    bw_u, bh_u, teeth, rnd, _lift = MOUTH_CHART[key]
    amount = max(0.0, min(1.0, amount))
    if key == 'none' or bw_u <= 0.0 or amount <= 0.02:
        return cel_rgb, cel_alpha

    h, w = cel_alpha.shape
    cx, cy = float(m['cx']), float(m['mouth_y'])
    bw = max(2.0, bw_u * fw * (0.72 + 0.28 * amount))
    bh = max(1.2, bh_u * fw * amount)
    if lip is None:
        lip = _lip_colour(cel_rgb, cel_alpha, m)
    lipc = np.clip(np.asarray(lip, np.float32) * 0.86, 0, 1)

    R = int(bw * 0.75) + 10
    sx0, sx1 = max(0, int(cx - R)), min(w, int(cx + R))
    sy0, sy1 = max(0, int(cy - bh * 1.6 - 6)), min(h, int(cy + bh * 1.6 + 6))
    if sx1 - sx0 < 5 or sy1 - sy0 < 4:
        return cel_rgb, cel_alpha

    hh, ww = sy1 - sy0, sx1 - sx0
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    px = xx + sx0 - cx
    py = yy + sy0 - cy
    u = px / (bw * 0.5)
    v = py / max(bh * 0.5, 0.6)

    # --- closed / pressed: draw only a soft seam, never a fill -------------
    if bh < fw * 0.022:
        seam_w = max(0.9, fw * 0.008)
        band = np.exp(-(py / seam_w) ** 2)
        band *= np.clip(1.0 - np.abs(u) / 1.02, 0, 1) ** 0.7
        band *= amount
        target = lipc * 0.45
        region = cel_rgb[sy0:sy1, sx0:sx1]
        cel_rgb[sy0:sy1, sx0:sx1] = region * (1 - band[..., None] * 0.8) + \
            target.reshape(1, 1, 3) * (band[..., None] * 0.8)
        return cel_rgb, cel_alpha

    # --- open: lens (wide vowels) or ellipse (round vowels) ----------------
    if rnd > 0.45:
        d = u ** 2 + v ** 2
    else:
        # flatter lid on top, deeper floor: the shape of a speaking mouth
        vv = np.where(v < 0, v * 0.86, v)
        d = np.abs(u) ** 1.7 + np.abs(vv) ** 1.55
    shape = np.clip((1.0 - d) / 0.30, 0, 1)
    shape = shape * shape * (3 - 2 * shape)

    depth = np.clip(1.0 - np.sqrt(np.maximum(0.0, u ** 2 * 0.7 + v ** 2)), 0, 1)
    interior = np.array([0.105, 0.042, 0.048], np.float32)
    interior = interior + depth[..., None] * np.array([0.075, 0.018, 0.025], np.float32)
    tongue = (np.clip((v - 0.18) / 0.72, 0, 1) ** 1.6) * (np.abs(u) < 0.58)
    interior = interior * (1 - tongue[..., None] * 0.40) + \
        np.array([0.46, 0.16, 0.16], np.float32) * (tongue[..., None] * 0.40)
    if teeth > 0.01:
        band = np.clip((0.10 - v) / 0.34, 0, 1) * np.clip((v + 0.55) / 0.30, 0, 1)
        band *= (np.abs(u) < 0.84) * teeth
        interior = interior * (1 - band[..., None] * 0.92) + \
            np.array([0.90, 0.87, 0.82], np.float32) * (band[..., None] * 0.92)

    # lip rim, feathered outward from the opening
    r_sq = np.sqrt(np.maximum(0.0, u ** 2 + v ** 2))
    rim = np.clip(1.0 - np.abs(r_sq - 1.18) / 0.36, 0, 1) * 0.42

    region = cel_rgb[sy0:sy1, sx0:sx1]
    face = np.clip(cel_alpha[sy0:sy1, sx0:sx1] * 1.6, 0, 1)
    a_open = shape * face
    out = region * (1 - a_open[..., None]) + interior * a_open[..., None]
    rim = rim * (1 - shape) * face
    out = out * (1 - rim[..., None]) + lipc.reshape(1, 1, 3) * rim[..., None]
    cel_rgb[sy0:sy1, sx0:sx1] = np.clip(out, 0, 1)
    return cel_rgb, cel_alpha


class A_CEL_PROXY:
    """Tiny shim so _lip_colour can read a cel without the Cel class."""

    def __init__(self, rgb, alpha):
        self.rgb = rgb
        self.alpha = alpha


def warp_block(rgb, alpha, dx, dy, blur=40.0, power=1.0):
    """Coherent body sway: shift the figure, weight by its own smoothed field."""
    if abs(dx) < 0.02 and abs(dy) < 0.02:
        return rgb, alpha
    h, w = alpha.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    f = _field(alpha, blur)
    wgt = np.clip(f * power, 0, 1)
    # pivot near the feet so the body leans rather than slides
    lean = (h - yy) / max(h, 1)
    sx = np.clip(xx + dx * wgt * lean, 0, w - 1).astype(np.int32)
    sy = np.clip(yy + dy * wgt, 0, h - 1).astype(np.int32)
    out_r = rgb[sy, sx]
    out_a = alpha[sy, sx]
    return out_r, out_a


# ---------------------------------------------------------------- composite
def place_cel(canvas, rgb, alpha, cx, foot_y, height, flip=False, tint=None,
              opacity=1.0, shadow=0.0, pivot=None):
    """Composite a cel so its head sits on cx and its feet on foot_y."""
    H, W = canvas.shape[:2]
    sc = height / float(alpha.shape[0])
    nw, nh = max(1, int(round(alpha.shape[1] * sc))), max(1, int(round(height)))
    if pivot is None:
        pivot = alpha.shape[1] / 2.0
    pivot = pivot * sc
    r, a = resize_float(rgb, alpha, (nw, nh))
    if flip:
        r = r[:, ::-1]
        a = a[:, ::-1]
        pivot = nw - pivot
    if tint is not None:
        r = r * np.array(tint, np.float32)[None, None, :]
    a = a * opacity
    x = int(round(cx - pivot))
    y = int(round(foot_y - nh))
    if shadow > 0:
        ry = max(4.0, nh * 0.022)
        rx = max(6.0, nw * 0.30)
        mask = _ellipse_mask(H, W, (cx, foot_y - ry * 0.25), rx, ry)
        canvas *= (1.0 - mask[..., None] * shadow)
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + nw), min(H, y + nh)
    if x1 <= x0 or y1 <= y0:
        return canvas
    sx0, sy0 = x0 - x, y0 - y
    sub_a = a[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)]
    sub_r = r[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)]
    region = canvas[y0:y1, x0:x1]
    canvas[y0:y1, x0:x1] = region * (1 - sub_a[..., None]) + sub_r * sub_a[..., None]
    return canvas


def _ellipse_mask(H, W, centre, rx, ry, soft=0.75):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - centre[0]) / max(rx, 1e-3)) ** 2 +
                ((yy - centre[1]) / max(ry, 1e-3)) ** 2)
    e = np.clip((1.0 - d) / max(soft, 1e-3), 0, 1)
    return e * e * (3 - 2 * e)


# ------------------------------------------------------------------ mouths
def mouth_overlay(rgb, alpha, box, shape, amount):
    """Draw a moving mouth inside a box of the face.

    `box` is (x0, y0, x1, y1) in the cel's own pixel space. `shape` is one of
    'closed', 'half', 'open', 'wide'. Everything is drawn in float RGB and
    feathered so it reads as paint, not as a sticker.
    """
    if amount <= 0.01 or shape == 'closed':
        return rgb, alpha
    h, w = alpha.shape
    x0, y0, x1, y1 = [int(v) for v in box]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)
    if x1 - x0 < 4 or y1 - y0 < 3:
        return rgb, alpha
    bw, bh = x1 - x0, y1 - y0
    yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32)
    u = (xx - bw / 2.0) / (bw / 2.0)
    v = (yy - bh / 2.0) / (bh / 2.0)
    opening = {'half': 0.45, 'open': 0.85, 'wide': 1.15}.get(shape, 0.5)
    # lip line bow: an ellipse squashed to the opening width
    ry = opening * 0.95
    rx = 0.92
    d = (u / rx) ** 2 + (v / max(ry, 1e-3)) ** 2
    inside = np.clip((1.0 - d) / 0.40, 0, 1)
    inside = inside * inside * (3 - 2 * inside)
    # the dark interior, warmer toward the lower lip
    inner = np.zeros((bh, bw, 3), np.float32)
    inner[...] = np.array([0.22, 0.075, 0.075], np.float32)
    inner += (np.clip(v, 0, 1)[..., None] * np.array([0.13, 0.03, 0.03], np.float32))
    # teeth along the top of the opening
    teeth = np.clip((0.10 - v) / 0.30, 0, 1) * np.clip(inside * 1.2, 0, 1)
    teeth *= (np.abs(u) < 0.78)
    inner = inner * (1 - teeth[..., None] * 0.86) + \
        np.array([0.92, 0.89, 0.84], np.float32) * (teeth[..., None] * 0.86)
    m = inside * amount
    # restrict to the face: only touch pixels the cel already covers
    face = alpha[y0:y1, x0:x1]
    m = m * np.clip(face * 1.6, 0, 1)
    region = rgb[y0:y1, x0:x1]
    region[:] = region * (1 - m[..., None]) + inner * m[..., None]
    return rgb, alpha
