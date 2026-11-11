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


def _ellipse_mask(H, W, centre, rx, ry, soft=0.75):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - centre[0]) / max(rx, 1e-3)) ** 2 +
                ((yy - centre[1]) / max(ry, 1e-3)) ** 2)
    e = np.clip((1.0 - d) / max(soft, 1e-3), 0, 1)
    return e * e * (3 - 2 * e)


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


def warp_block(rgb, alpha, dx, dy, blur=36.0, power=1.0):
    """Coherent body sway: lean the figure from the feet, weighted by its field."""
    if abs(dx) < 0.02 and abs(dy) < 0.02:
        return rgb, alpha
    h, w = alpha.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    f = _field(alpha, blur)
    wgt = np.clip(f * power, 0, 1)
    lean = (h - yy) / max(h, 1)          # pivot at the feet
    sx = np.clip(xx + dx * wgt * lean, 0, w - 1).astype(np.int32)
    sy = np.clip(yy + dy * wgt, 0, h - 1).astype(np.int32)
    return rgb[sy, sx], alpha[sy, sx]


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
FRAC_MOUTH = (128.0 - 11.0) / 142.0  # 0.824
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


# ---------------------------------------------------------------- lip sync
_TALK_CACHE = {}


def _shift(cel, dx, dy):
    """Translate a cel in its own canvas, growing it so nothing is cropped."""
    pad_l = max(0, int(round(-dx))) + 2
    pad_r = max(0, int(round(dx))) + 2
    pad_t = max(0, int(round(-dy))) + 2
    pad_b = max(0, int(round(dy))) + 2
    W = cel.w + pad_l + pad_r
    H = cel.h + pad_t + pad_b
    r = np.zeros((H, W, 3), np.float32)
    a = np.zeros((H, W), np.float32)
    x0 = pad_l + int(round(dx))
    y0 = pad_t + int(round(dy))
    r[y0:y0 + cel.h, x0:x0 + cel.w] = cel.rgb
    a[y0:y0 + cel.h, x0:x0 + cel.w] = cel.alpha
    return Cel(cel.name, r, a)


def _scaled(cel, sc, tag):
    """Resize a cel under a distinct name, so face metrics stay truthful."""
    nw = max(1, int(round(cel.w * sc)))
    nh = max(1, int(round(cel.h * sc)))
    rgb, alpha = resize_float(cel.rgb, cel.alpha, (nw, nh))
    return Cel(f'{cel.name}@{tag}', rgb, alpha)


def _ncc(a, b):
    a = a - a.mean()
    b = b - b.mean()
    den = np.sqrt((a * a).sum()) * np.sqrt((b * b).sum()) + 1e-6
    return float((a * b).sum() / den)


def _chin_refine(open_cel, base_cel, span=6):
    """Slide the open drawing onto the base chin; the beard is identical."""
    bs = face_metrics(base_cel)
    fw = max(8.0, bs['face_w'])
    x0 = int(bs['cx'] - fw * 0.28)
    x1 = int(bs['cx'] + fw * 0.28)
    y0 = int(bs['mouth_y'] + fw * 0.22)
    y1 = int(bs['mouth_y'] + fw * 0.46)
    ref = base_cel.rgb[y0:y1, x0:x1].mean(axis=2)
    if ref.size < 80:
        return 0, 0
    best = (-2.0, 0, 0)
    for dy in range(-span, span + 1):
        for dx in range(-span, span + 1):
            yy0, xx0 = y0 + dy, x0 + dx
            cand = open_cel.rgb[yy0:yy0 + (y1 - y0), xx0:xx0 + (x1 - x0)].mean(axis=2)
            if cand.shape != ref.shape:
                continue
            v = _ncc(ref, cand)
            if v > best[0]:
                best = (v, dy, dx)
    return best[1], best[2]


def register_onto(src, dst):
    """Open-mouth drawing resampled onto `dst`'s exact canvas, head-matched."""
    ms, md = face_metrics(src), face_metrics(dst)
    sc = md['head_w'] / max(1e-3, ms['head_w'])
    out = src
    if abs(sc - 1.0) > 0.004:
        out = _scaled(src, sc, 'reg')
    om = face_metrics(out)
    # where the source head lands on the destination canvas
    dx = int(round(md['cx'] - om['cx']))
    dy = int(round(md['eye_y'] - om['eye_y']))
    H, W = dst.h, dst.w
    r = np.zeros((H, W, 3), np.float32)
    a = np.zeros((H, W), np.float32)
    sx0 = max(0, -dx)
    sy0 = max(0, -dy)
    dx0 = max(0, dx)
    dy0 = max(0, dy)
    cw = min(out.w - sx0, W - dx0)
    ch = min(out.h - sy0, H - dy0)
    if cw > 0 and ch > 0:
        r[dy0:dy0 + ch, dx0:dx0 + cw] = out.rgb[sy0:sy0 + ch, sx0:sx0 + cw]
        a[dy0:dy0 + ch, dx0:dx0 + cw] = out.alpha[sy0:sy0 + ch, sx0:sx0 + cw]
    reg = Cel(f'{dst.name}+{src.name}', r, a)
    _FACE_CACHE[reg.name] = dict(md)
    return reg


def _crop_to(cel, dst):
    """Crop/pad a cel back to the destination canvas."""
    r = np.zeros((dst.h, dst.w, 3), np.float32)
    a = np.zeros((dst.h, dst.w), np.float32)
    ch = min(dst.h, cel.h)
    cw = min(dst.w, cel.w)
    r[:ch, :cw] = cel.rgb[:ch, :cw]
    a[:ch, :cw] = cel.alpha[:ch, :cw]
    out = Cel(cel.name + '|c', r, a)
    _FACE_CACHE[out.name] = _FACE_CACHE.get(cel.name)
    return out


def talking_head(base, open_cel):
    key = (base.name, open_cel.name)
    hit = _TALK_CACHE.get(key)
    if hit is None:
        hit = register_onto(open_cel, base)
        _TALK_CACHE[key] = hit
    return hit


def speak_mix(rgb, alpha, base_cel, open_cel, amount):
    """Lip sync as drawn animation: swap to the open-mouth chart, mouth only."""
    amount = max(0.0, min(1.0, amount))
    if amount <= 0.02 or open_cel is None:
        return rgb, alpha
    t = talking_head(base_cel, open_cel)
    m = face_metrics(base_cel)
    h, w = alpha.shape
    if (t.h, t.w) != (h, w):
        return rgb, alpha

    fw = max(6.0, m['face_w'])
    cx = float(m['cx'])
    cy = float(m['mouth_y']) + fw * 0.14
    rx, ry = fw * 0.50, fw * 0.26
    # never reach the eyes: the patch starts below the nose
    top = int(max(m['eye_y'] + fw * 0.44, cy - ry * 2.0))
    y0, y1 = int(max(0, top)), int(min(h, cy + ry * 1.9))
    x0, x1 = int(max(0, cx - rx * 1.9)), int(min(w, cx + rx * 1.9))
    if y1 - y0 < 6 or x1 - x0 < 6:
        return rgb, alpha

    hh, ww = y1 - y0, x1 - x0
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    d = np.sqrt(((xx + x0 - cx) / rx) ** 2 + ((yy + y0 - cy) / ry) ** 2)
    e = np.clip((1.0 - d) / 0.55, 0, 1)
    mask = (e * e * (3 - 2 * e)) * amount
    mask = mask * np.clip(alpha[y0:y1, x0:x1] * 1.5, 0, 1) * \
        np.clip(t.alpha[y0:y1, x0:x1] * 1.5, 0, 1)

    out_r = rgb.copy()
    region = out_r[y0:y1, x0:x1]
    out_r[y0:y1, x0:x1] = region * (1 - mask[..., None]) + \
        t.rgb[y0:y1, x0:x1] * mask[..., None]
    return out_r, alpha.copy()


class A_CEL_PROXY:
    def __init__(self, rgb, alpha):
        self.rgb = rgb
        self.alpha = alpha


