"""Scene layer for the painted 2D cut: plates, camera, light, grade, captions.

The camera is virtual: every plate is cached once at overscan size and each
frame crops a moving window out of it. Characters are composited as keyed cels
into the same float canvas, so light, grain and grade hit picture and figure
together — the reason this reads as one painted world instead of cut-outs on a
background.
"""
from __future__ import annotations

import math
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import anim2d as A
import core2d as C

P = Path(__file__).resolve().parent
ASSETS = P / 'assets'
FRAMES = ASSETS / 'frames'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

W, H = 1080, 1920
FPS = 24
OVERSCAN = 1.46

_PLATES = {}
_CELS = {}


# ------------------------------------------------------------------ plates
def plate(name):
    """Load a background plate at overscan size, as float RGB."""
    if name in _PLATES:
        return _PLATES[name]
    path = ASSETS / name
    im = Image.open(path).convert('RGB')
    tw, th = int(W * OVERSCAN), int(H * OVERSCAN)
    # cover the frame: scale to fill, then centre-crop to the overscan box
    s = max(tw / im.size[0], th / im.size[1])
    nw, nh = int(round(im.size[0] * s)), int(round(im.size[1] * s))
    im = im.resize((nw, nh), Image.LANCZOS)
    x0 = (nw - tw) // 2
    y0 = (nh - th) // 2
    im = im.crop((x0, y0, x0 + tw, y0 + th))
    arr = np.asarray(im).astype(np.float32) / 255.0
    _PLATES[name] = arr
    return arr


def _smoother(x):
    x = min(1.0, max(0.0, x))
    return x * x * x * (x * (x * 6 - 15) + 10)


def view_of(bg, cam, t, t0, t1, view=None):
    """Crop the moving camera window out of the overscan plate."""
    u = 0.0 if t1 <= t0 else (t - t0) / (t1 - t0)
    e = _smoother(u)
    if view is None:
        view = (0.5, 0.5, 1.0)
    vx, vy, vz = view
    cam = cam or {}

    x0 = cam.get('x0', 0.0); x1 = cam.get('x1', 0.0)
    y0 = cam.get('y0', 0.0); y1 = cam.get('y1', 0.0)
    z0 = cam.get('z0', 1.0); z1 = cam.get('z1', 1.0)
    hand = cam.get('hand', 0.0)

    px = x0 + (x1 - x0) * e
    py = y0 + (y1 - y0) * e
    pz = z0 + (z1 - z0) * e

    if hand:
        px += hand * (math.sin(t * 0.83) * 0.0022 + math.sin(t * 1.71 + 1.1) * 0.0011)
        py += hand * (math.sin(t * 0.61 + 0.4) * 0.0030 + math.sin(t * 2.13) * 0.0012)
        pz *= 1.0 + hand * math.sin(t * 0.37) * 0.0016

    z = max(0.35, pz * vz)
    cw, ch = W / z, H / z
    sw, sh = bg.shape[1], bg.shape[0]
    # the window is placed inside the overscan slack
    slack_x = (sw - cw) / 2.0
    slack_y = (sh - ch) / 2.0
    cx = sw / 2.0 + px * slack_x
    cy = sh / 2.0 + py * slack_y
    x0i = int(round(min(max(0, cx - cw / 2), sw - cw)))
    y0i = int(round(min(max(0, cy - ch / 2), sh - ch)))
    x1i = int(round(min(sw, x0i + cw)))
    y1i = int(round(min(sh, y0i + ch)))
    crop = bg[y0i:y1i, x0i:x1i]
    im = Image.fromarray((np.clip(crop, 0, 1) * 255).astype(np.uint8))
    im = im.resize((W, H), Image.BILINEAR)
    return np.asarray(im).astype(np.float32) / 255.0


# -------------------------------------------------------------------- cels
MOUTH_PAIRS = {}


def register_mouths(pairs):
    for closed_name, open_name in pairs:
        if closed_name in _CELS and open_name in _CELS:
            MOUTH_PAIRS[closed_name] = open_name


def load_library(target_h=1000):
    """Key every cel sheet in assets/frames into the shared library."""
    specs = [
        ('idle0', 'hero_casual.png', 'green'),
        ('walk0', 'casual_walk_a.png', 'green'),
        ('walk1', 'casual_walk_b.png', 'green'),
        ('talk0', 'casual_talk.png', 'green'),
        ('sidle0', 'hero_suit.png', 'green'),
        ('swalk0', 'hero_walk.png', 'green'),
        ('swalk1', 'suit_walk_b.png', 'green'),
        ('stalk0', 'suit_talk.png', 'green'),
        ('sreach0', 'suit_reach.png', 'green'),
        ('girl0', 'girl.png', 'green'),
        ('extra0', 'extras.png', 'green'),
    ]
    for name, fn, key in specs:
        path = FRAMES / fn
        if not path.exists():
            path = ASSETS / fn
        if not path.exists():
            continue
        if name in _CELS:
            continue
        rgb, alpha = (A.cut_green if key == 'green' else A.cut_grey)(str(path))
        rgb, alpha = A.trim(rgb, alpha)
        rgb, alpha = A.normalise(rgb, alpha, target_h)
        _CELS[name] = A.Cel(name, rgb, alpha)
    register_mouths([('idle0', 'talk0'), ('sidle0', 'stalk0'),
                     ('walk0', 'talk0'), ('walk1', 'talk0'),
                     ('swalk0', 'stalk0'), ('sreach0', 'stalk0')])
    return _CELS


def cels():
    return _CELS


# ------------------------------------------------------------------ figure
def cels_get(name):
    return _CELS.get(name)


def pose_frame(cel_a, cel_b, k, t, talk=None, mouth=None, seed=0.0):
    """Resolve one frame of a pose pair, plus breathing and lip sync."""
    # Pose changes are cuts, not dissolves. Two separately drawn poses share
    # no pixel correspondence — arms and legs sit in different places — so
    # blending them pastes a second figure on screen. Drawn animation flips
    # the drawing instead, and only the small idle motion is continuous.
    if k < 0.5:
        rgb, alpha = cel_a.rgb, cel_a.alpha
        kk = 0.0
    else:
        rgb, alpha = cel_b.rgb, cel_b.alpha
        kk = 1.0


    # lip sync: cut between the closed and open lip chart on the voice envelope
    if mouth is not None:
        viseme, amount = mouth
        ref = cel_b if kk > 0.5 else cel_a
        open_name = MOUTH_PAIRS.get(ref.name)
        open_cel = _CELS.get(open_name) if open_name else None
        if open_cel is not None:
            # drawn animation changes drawings; it does not dissolve them.
            # the envelope picks the chart, with a one-frame edge so a fast
            # syllable does not strobe.
            rgb, alpha = A.speak_mix(rgb, alpha, ref, open_cel,
                                     1.0 if amount >= 0.34 else 0.0)

    # breathing: a small vertical breath, strongest in the chest
    breath = math.sin(t * 1.31 + seed) * 1.7
    sway = math.sin(t * 0.47 + seed * 0.7) * 1.4
    rgb, alpha = A.warp_block(rgb, alpha, sway, breath, blur=36.0)
    return rgb, alpha


# ------------------------------------------------------------------ effects
def light_shaft(img, origin, angle_deg, length, width, colour, power=0.4, t=0.0):
    return C.light_shaft(img, origin, angle_deg, length, width, colour, power, t)


def flash(img, amount):
    return 1.0 - (1.0 - img) * (1.0 - amount)


def vignette(img, power=0.55):
    return C.vignette(img, power=power, size=1.18)


def grain(img, amount=0.020, seed=0):
    return C.grain(img, amount, seed)


def apply_grade(img, g):
    """Grade + bloom + halation. Copies the dict so shots cannot be mutated."""
    g = dict(g or {})
    if g.get('bloom', 0) > 0:
        img = C.bloom(img, threshold=g.get('bloom_th', 0.66),
                      strength=(0.42 * g['bloom'], 0.26 * g['bloom'], 0.15 * g['bloom']))
    if g.get('halation', 0) > 0:
        img = C.halation(img, amount=g['halation'])
    img = C.grade(img,
                  lift=g.get('lift', (0, 0, 0)),
                  gamma=g.get('gamma', (1, 1, 1)),
                  gain=g.get('gain', (1, 1, 1)),
                  contrast=g.get('contrast', 1.0),
                  sat=g.get('sat', 1.0))
    return img


# ---------------------------------------------------------------- captions
_CAP_CACHE = {}


def caption_layer(text, size=(W, H), font_size=52):
    key = (text, font_size)
    if key in _CAP_CACHE:
        return _CAP_CACHE[key]
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, font_size)
    max_w = int(W * 0.82)
    words = text.split()
    lines, cur = [], ''
    for word in words:
        trial = (cur + ' ' + word).strip()
        if d.textlength(trial, font=font) > max_w and cur:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    lh = int(font_size * 1.30)
    total = lh * len(lines)
    y = int(H * 0.80) - total // 2
    for line in lines:
        tw = d.textlength(line, font=font)
        x = (W - tw) / 2
        d.text((x, y), line, font=font, fill=(0, 0, 0, 150),
               stroke_width=7, stroke_fill=(0, 0, 0, 130))
        d.text((x, y), line, font=font, fill=(255, 255, 255, 246),
               stroke_width=3, stroke_fill=(18, 18, 22, 225))
        y += lh
    arr = np.asarray(img).astype(np.float32) / 255.0
    _CAP_CACHE[key] = (arr[..., :3], arr[..., 3])
    return _CAP_CACHE[key]


def draw_caption(img, text, alpha):
    if alpha <= 0.01 or not text:
        return img
    rgb, a = caption_layer(text)
    m = a * alpha
    return img * (1 - m[..., None]) + rgb * m[..., None]
