"""Shared 2D drawing core: masks, painted shading, cameras and film effects.

Everything is float32 RGB in 0..1 at master resolution. Layers are RGBA
filmstrips pre-rendered once at overscan size, then moved by a virtual camera.
That split is what makes a 60 second film render in minutes instead of hours.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

MASTER_W, MASTER_H = 1080, 1920
FPS = 24


# ----------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def smoother(x):
    x = clamp(x)
    return x * x * x * (x * (x * 6 - 15) + 10)


def ease_out(x, p=3.0):
    return 1 - (1 - clamp(x)) ** p


def ease_in(x, p=3.0):
    return clamp(x) ** p


def ramp(t, a, b):
    """0 before a, 1 after b, eased between."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return smooth((t - a) / (b - a))


def lerp(a, b, k):
    return a + (b - a) * k


def lerp3(a, b, k):
    return tuple(lerp(x, y, k) for x, y in zip(a, b))


def mix_pal(a, b, k):
    return tuple(lerp(x, y, k) for x, y in zip(a, b))


# --------------------------------------------------------------- utilities
def new_rgba(w=MASTER_W, h=MASTER_H):
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))


def mask_to_layer(mask, color, alpha=1.0):
    """Solid colour RGBA layer clipped by an 'L' mask."""
    layer = Image.new('RGBA', mask.size, color + (0,))
    layer.putalpha(mask.point(lambda v: int(v * alpha)))
    return layer


def vertical_gradient(size, stops):
    """stops: [(pos 0..1, (r,g,b)), ...] -> RGB float array, smooth in between."""
    h = size[1]
    ys = np.linspace(0, 1, h, dtype=np.float32)
    cols = np.zeros((h, 3), dtype=np.float32)
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        if p1 <= p0:
            continue
        k = np.clip((ys - p0) / (p1 - p0), 0, 1)
        k = k * k * (3 - 2 * k)
        for ci in range(3):
            cols[:, ci] = np.where((ys >= p0) & (ys <= p1),
                                   c0[ci] + (c1[ci] - c0[ci]) * k, cols[:, ci])
    cols[:] = np.where(ys[:, None] < stops[0][0], np.array(stops[0][1]), cols)
    cols[:] = np.where(ys[:, None] > stops[-1][0], np.array(stops[-1][1]), cols)
    return np.repeat(cols[:, None, :], size[0], axis=1)


def radial(size, centre, rx, ry, inner=(1, 1, 1), outer=(0, 0, 0), power=1.6):
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - centre[0]) / rx) ** 2 + ((yy - centre[1]) / ry) ** 2)
    k = np.clip(1.0 - d, 0, 1) ** power
    inner = np.array(inner, dtype=np.float32)
    outer = np.array(outer, dtype=np.float32)
    return outer + (inner - outer) * k[..., None]


def soft_ellipse(size, centre, rx, ry, softness=0.55):
    """Antialiased elliptical falloff mask in 0..1."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - centre[0]) / max(rx, 1e-3)) ** 2 + ((yy - centre[1]) / max(ry, 1e-3)) ** 2)
    edge = np.clip((1.0 - d) / max(softness, 1e-3), 0, 1)
    return edge * edge * (3 - 2 * edge)


def gauss(arr, radius):
    if radius <= 0:
        return arr
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    im = im.filter(ImageFilter.GaussianBlur(radius))
    return np.asarray(im).astype(np.float32) / 255.0


def to_pil(arr):
    return Image.fromarray((np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8))


def from_pil(im):
    if im.mode == 'RGBA':
        arr = np.asarray(im).astype(np.float32) / 255.0
        alpha = arr[..., 3:4]
        return arr[..., :3] * alpha + 0 * alpha, alpha
    return np.asarray(im.convert('RGB')).astype(np.float32) / 255.0, None


# ------------------------------------------------------------ painted body
def paint_shape(draw_fn, size, base, **kw):
    """Draw a silhouette with draw_fn(draw) on an 'L' mask, then light it."""
    mask = Image.new('L', size, 0)
    draw_fn(ImageDraw.Draw(mask))
    return paint_mask(mask, base, **kw)


def paint_mask(mask, base, light=(-0.6, -0.8), key=1.0, shade=0.42,
               rim=None, rim_strength=0.0, rim_soft=6, texture=None,
               ambient=0.30):
    """Light an existing 'L' mask.

    The shading is a ramp along the light direction plus a rim band on the lit
    edge, which is what makes flat vector shapes read as modelled forms.
    """
    w, h = mask.size
    m = np.asarray(mask).astype(np.float32) / 255.0

    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    lx, ly = light
    n = math.hypot(lx, ly) or 1.0
    lx, ly = lx / n, ly / n
    # coordinate along the light axis, normalised to the mask's own extent
    ys, xs = np.nonzero(m > 0.02)
    if len(xs) < 8:
        return np.zeros((h, w, 3), np.float32), m
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    nx = ((xx - x0) / max(x1 - x0, 1)) * 2 - 1
    ny = ((yy - y0) / max(y1 - y0, 1)) * 2 - 1
    along = clamp_axis((nx * lx + ny * ly) * 0.5 + 0.5, 0, 1)
    lit = (1.0 - shade) + shade * along

    base_arr = np.array(base, dtype=np.float32)
    rgb = base_arr[None, None, :] * (ambient + key * lit)[..., None]

    if texture is not None:
        rgb = rgb * (1.0 + texture)

    if rim is not None and rim_strength > 0:
        eroded = Image.fromarray((m * 255).astype(np.uint8)).filter(
            ImageFilter.MinFilter(3))
        inner = np.asarray(eroded).astype(np.float32) / 255.0
        band = np.clip(m - inner, 0, 1)
        band = np.asarray(Image.fromarray((band * 255).astype(np.uint8))
                          .filter(ImageFilter.GaussianBlur(rim_soft))).astype(np.float32) / 255.0
        side = clamp_axis((nx * lx + ny * ly) * 0.5 + 0.5, 0, 1) ** 1.5
        rgb = rgb + np.array(rim, np.float32)[None, None, :] * (band * side * rim_strength)[..., None]

    return rgb * m[..., None], m


def clamp_axis(a, lo, hi):
    return np.clip(a, lo, hi)


def paste_rgb(canvas, rgb, mask, xy=(0, 0), alpha=1.0):
    """Composite an RGB+mask pair onto a float canvas."""
    x, y = int(xy[0]), int(xy[1])
    h, w = mask.shape
    H, W = canvas.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return canvas
    sx0, sy0 = x0 - x, y0 - y
    sub_m = mask[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)] * alpha
    sub_c = rgb[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)]
    region = canvas[y0:y1, x0:x1]
    canvas[y0:y1, x0:x1] = region * (1 - sub_m[..., None]) + sub_c * sub_m[..., None]
    return canvas


# ------------------------------------------------------------------ camera
class Camera:
    """Virtual camera over pre-rendered overscan layers.

    pan/zoom are the *subject plane* values; each layer's depth decides how much
    of that movement it receives, which is all parallax really is.
    """

    def __init__(self, w=MASTER_W, h=MASTER_H):
        self.w, self.h = w, h
        self.x = 0.0          # pan in master pixels at subject depth
        self.y = 0.0
        self.zoom = 1.0
        self.rot = 0.0        # degrees, tiny
        self.shake = 0.0
        self.t = 0.0

    def at(self, t, x=0.0, y=0.0, zoom=1.0, rot=0.0, shake=0.0):
        self.t = t
        self.x, self.y, self.zoom, self.rot = x, y, zoom, rot
        self.shake = shake
        return self

    def offset(self, depth):
        """Screen offset for a layer at `depth` (0 = far, 1 = subject)."""
        sx = sy = 0.0
        if self.shake:
            t = self.t
            sx += self.shake * (math.sin(t * 37.1) * .5 + math.sin(t * 61.7 + 1.3) * .3)
            sy += self.shake * (math.sin(t * 29.3 + .7) * .5 + math.sin(t * 53.9) * .3)
        return -self.x * depth + sx, -self.y * depth + sy

    def scale(self, depth):
        return 1.0 + (self.zoom - 1.0) * depth

    def transform(self, im, depth, extra_zoom=1.0, dx=0.0, dy=0.0):
        """Return the layer cropped to frame, as an RGBA image."""
        s = self.scale(depth) * extra_zoom
        ox, oy = self.offset(depth)
        ox += dx
        oy += dy
        # place layer centre, scaled, into the frame
        cw, ch = im.size
        nw, nh = max(1, int(round(cw * s))), max(1, int(round(ch * s)))
        if (nw, nh) != (cw, ch):
            im = im.resize((nw, nh), Image.BILINEAR)
        cx = (nw - self.w) / 2.0 + ox
        cy = (nh - self.h) / 2.0 + oy
        box = (int(round(cx)), int(round(cy)), int(round(cx)) + self.w, int(round(cy)) + self.h)
        out = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))
        out.paste(im, (-int(round(cx)), -int(round(cy))))
        if abs(self.rot) > 0.001:
            out = out.rotate(self.rot, resample=Image.BICUBIC, center=(self.w / 2, self.h / 2))
        return out


def over(base, layer_rgba):
    """Alpha-composite PIL RGBA over float canvas, returning float canvas."""
    arr = np.asarray(layer_rgba).astype(np.float32) / 255.0
    a = arr[..., 3:4]
    return base * (1 - a) + arr[..., :3] * a


# ----------------------------------------------------------- film effects
def _half(img, f=2):
    h, w = img.shape[:2]
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    im = im.resize((max(1, w // f), max(1, h // f)), Image.BILINEAR)
    return np.asarray(im).astype(np.float32) / 255.0


def _full(small, size):
    im = Image.fromarray((np.clip(small, 0, 1) * 255).astype(np.uint8))
    return np.asarray(im.resize(size, Image.BILINEAR)).astype(np.float32) / 255.0


def bloom(img, threshold=0.62, radius=(18, 42, 90), strength=(0.55, 0.34, 0.20), fast=3):
    h, w = img.shape[:2]
    small = _half(img, fast)
    bright = np.clip((small - threshold) / max(1e-3, 1 - threshold), 0, 1) ** 1.4
    acc = np.zeros_like(bright)
    for r, s in zip(radius, strength):
        acc += gauss(bright, max(1.0, r / fast)) * s
    acc = _full(np.clip(acc, 0, 1), (w, h))
    return 1.0 - (1.0 - np.clip(img, 0, 1)) * (1.0 - np.clip(acc, 0, 1))


def halation(img, amount=0.12, fast=4):
    """Red-leaning glow, the thing film does around hot highlights."""
    h, w = img.shape[:2]
    small = _half(img, fast)
    lum = small.max(axis=2)
    hot = np.clip((lum - 0.78) / 0.22, 0, 1) ** 1.2
    glow = _full(gauss(hot, max(1.0, 26 / fast)) * amount, (w, h))
    out = img.copy()
    out[..., 0] += glow * 1.00
    out[..., 1] += glow * 0.55
    out[..., 2] += glow * 0.32
    return out


def light_shaft(img, origin, angle_deg, length, width, color, power=0.55, t=0.0):
    h, w = img.shape[:2]
    f = 4
    sw, sh = max(1, w // f), max(1, h // f)
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    yy *= f
    xx *= f
    dx, dy = xx - origin[0], yy - origin[1]
    a = math.radians(angle_deg)
    ux, uy = math.sin(a), math.cos(a)
    along = dx * ux + dy * uy
    across = -dx * uy + dy * ux
    spread = width * (0.55 + 0.9 * np.clip(along / max(length, 1), 0, 1))
    fall = np.clip(1.0 - along / max(length, 1), 0, 1) ** 1.5
    band = np.exp(-(across / np.maximum(spread, 1e-3)) ** 2)
    m = band * fall
    m = m * (0.92 + 0.08 * math.sin(t * 1.7))
    m = _full(m, (w, h))
    return img + np.array(color, np.float32)[None, None, :] * (m * power)[..., None]


def depth_blur(img, focus_band, amount):
    """Blur everything outside a horizontal band; stand-in for a real lens."""
    if amount <= 0.2:
        return img
    y0, y1 = focus_band
    blurred = gauss(img, amount)
    h = img.shape[0]
    ys = np.arange(h, dtype=np.float32)
    m = np.clip(np.minimum((ys - y0) / max(1, 90), (y1 - ys) / max(1, 90)) * -1 + 1, 0, 1)
    m = (m * m * (3 - 2 * m))[:, None, None]
    return img * m + blurred * (1 - m)


def vignette(img, power=0.55, size=1.22):
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (xx - w / 2) / (w / 2)
    ny = (yy - h / 2) / (h / 2)
    d = np.sqrt(nx ** 2 + (ny * 0.72) ** 2) / size
    v = np.clip(1 - power * np.clip(d, 0, 1.6) ** 2.1, 0, 1)
    return img * v[..., None]


_GRAIN_CACHE = {}


def grain(img, amount=0.022, seed=0):
    h, w = img.shape[:2]
    key = (w, h, seed % 24)
    n = _GRAIN_CACHE.get(key)
    if n is None:
        rng = np.random.default_rng(seed % 24)
        n0 = rng.normal(0, 1, (h // 2 + 1, w // 2 + 1)).astype(np.float32)
        n = np.repeat(np.repeat(n0, 2, axis=0), 2, axis=1)[:h, :w]
        _GRAIN_CACHE[key] = n
    lum = img.mean(axis=2, keepdims=True)
    # grain is strongest in the mids, weakest in the blacks
    wgt = 0.35 + 0.65 * (1 - np.abs(lum * 2 - 1))
    return img + (n[..., None] * wgt * amount)


def grade(img, lift=(0.0, 0.0, 0.0), gamma=(1.0, 1.0, 1.0), gain=(1.0, 1.0, 1.0),
          contrast=1.0, sat=1.0, tint=None, tint_amount=0.0):
    out = np.clip(img, 0, 1)
    out = np.clip(out * np.array(gain, np.float32), 0, 4)
    out = out ** np.array(gamma, np.float32)
    out = out + np.array(lift, np.float32)
    if contrast != 1.0:
        out = (out - 0.5) * contrast + 0.5
    if sat != 1.0:
        lum = out @ np.array([0.299, 0.587, 0.114], np.float32)
        out = lum[..., None] + (out - lum[..., None]) * sat
    if tint is not None and tint_amount > 0:
        lum = out.mean(axis=2, keepdims=True)
        out = out * (1 - tint_amount) + (lum * 2.0) * np.array(tint, np.float32)[None, None, :] * tint_amount
    return np.clip(out, 0, 1)


# ------------------------------------------------------------- text plates
def draw_text_layer(size, text, font_path, font_size, colour=(255, 255, 255),
                    sub_colour=(20, 20, 24), stroke=3, max_width=None, extra=None):
    """Burned-in caption with a soft drop shadow, animated separately."""
    from PIL import ImageFont
    w, h = size
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, font_size)
    words = text.split()
    lines, cur = [], ''
    for word in words:
        trial = (cur + ' ' + word).strip()
        if max_width and d.textlength(trial, font=font) > max_width and cur:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    lh = int(font_size * 1.20)
    y = int(h * 0.795) - lh * (len(lines) - 1)
    for line in lines:
        tw = d.textlength(line, font=font)
        x = (w - tw) / 2
        d.text((x, y), line, font=font, fill=sub_colour + (150,),
               stroke_width=stroke + 3, stroke_fill=(0, 0, 0, 120))
        d.text((x, y), line, font=font, fill=colour + (255,),
               stroke_width=stroke, stroke_fill=sub_colour + (235,))
        y += lh
    if extra:
        f2 = ImageFont.truetype(font_path, int(font_size * 0.30))
        tw = d.textlength(extra, font=f2)
        d.text(((w - tw) / 2, 60), extra, font=f2, fill=(255, 255, 255, 190))
    return img
