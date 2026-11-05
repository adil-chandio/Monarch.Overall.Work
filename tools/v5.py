#!/usr/bin/env python3
"""v5 — the reference's edit, our objects. No browser, no reference pixels.

REF-01 is a 23.27 s reel: TWENTY / BILLION type slams, a green macro, a bag on a stool
in a storm, a red "2008" portrait, and a loop of the same four motifs. The reference's
photographs are its own generated images; ours are different photographs of the same
ideas (bag on a stool, hands with money, a man in a red room). So this rebuild keeps the
*edit* — the timecodes, the transitions, the layout, the type system, the grade — and
puts our plates in the slots.

Everything is measured rather than eyeballed where a number exists:
  timecodes       analysis/v4-build/shots.json
  drift, grade    analysis/v4-build/shots_motion.json
  type 0.00-0.80  spec/typo-block.json  (fitted to the reference, see BUILD-LOG-01)

    python3 tools/v5.py --spec spec/v5-01.json --out public/demo/v5-30.mp4
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from ffbin import ffmpeg

W, H = 720, 1280
VENDOR = "showreel/v4/vendor"


# --------------------------------------------------------------------------- utils
def ease(u: float, kind: str = "out") -> float:
    u = min(max(u, 0.0), 1.0)
    if kind == "linear":
        return u
    if kind == "in":
        return u * u
    if kind == "out":
        return 1 - (1 - u) ** 2
    if kind == "back":
        c = 1.70158
        return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2
    return 0.5 - 0.5 * math.cos(math.pi * u)


def lerp(a, b, u):
    return a + (b - a) * u


def hex_rgb(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))       # -> RGB


# -------------------------------------------------------------------------- assets
_cache: dict[str, np.ndarray] = {}


def asset(path: str) -> np.ndarray:
    if path not in _cache:
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise SystemExit(f"missing asset {path}")
        if img.shape[2] == 3:
            img = np.dstack([img, np.full(img.shape[:2], 255, np.uint8)])
        _cache[path] = img
    return _cache[path]


def cut(a: np.ndarray) -> np.ndarray:
    """Trim an RGBA layer to its own ink box (so placement is about the object)."""
    ys, xs = np.where(a[..., 3] > 8)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def draw_layer(dst: np.ndarray, layer: np.ndarray, x: float, y: float, w: float,
               opacity: float = 1.0, rot: float = 0.0, skew: float = 0.0,
               blur: float = 0.0, h: float | None = None) -> None:
    """Composite an RGBA layer at a target size, optionally rotated/skewed.

    Compositing is in BGR float32 0..255, premultiplied by alpha, so no fringe appears
    when the layer is dimmed or moved over a bright plate.
    """
    if opacity <= 0.003 or w < 2:
        return
    lh, lw = layer.shape[:2]
    h = max(2, int(round(h if h is not None else lh * w / lw)))
    w = max(2, int(round(w)))
    if blur > 0.05:
        big = cv2.resize(layer, (w * 2, h * 2), interpolation=cv2.INTER_LANCZOS4)
        big = cv2.GaussianBlur(big, (0, 0), blur * 2)
        img = cv2.resize(big, (w, h), interpolation=cv2.INTER_AREA)
    else:
        img = cv2.resize(layer, (w, h), interpolation=cv2.INTER_LANCZOS4)
    if abs(rot) > 0.05 or abs(skew) > 0.005:
        M = np.float32([[math.cos(math.radians(rot)), -math.sin(math.radians(rot)),
                         h * skew], [math.sin(math.radians(rot)), math.cos(math.radians(rot)), 0]])
        # keep the whole rotated layer
        pad = int(math.ceil(abs(w * math.sin(math.radians(rot))) + abs(h * math.sin(math.radians(rot))) + abs(h * skew)))
        canvas = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.uint8)
        canvas[pad:pad + h, pad:pad + w] = img
        M[0, 2] += pad * 0.4
        M[1, 2] += pad * 0.4
        img = cv2.warpAffine(canvas, M, (w + 2 * pad, h + 2 * pad), flags=cv2.INTER_LANCZOS4,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        x -= pad * 0.4
        y -= pad * 0.4
        h, w = img.shape[:2]
    xi, yi = int(round(x)), int(round(y))
    x0, y0 = max(0, xi), max(0, yi)
    x1, y1 = min(W, xi + w), min(H, yi + h)
    if x1 <= x0 or y1 <= y0:
        return
    sub = img[y0 - yi:y1 - yi, x0 - xi:x1 - xi]
    a = (sub[..., 3].astype(np.float32) / 255.0 * opacity)[..., None]
    dst[y0:y1, x0:x1] = sub[..., :3].astype(np.float32) * a + dst[y0:y1, x0:x1] * (1 - a)



# ------------------------------------------------------------------- 3D camera
class Cam:
    """A pinhole camera over layers that sit at different depths.

    This is the whole difference between a flat cutout and a parallax shot. A layer at
    depth `z` is scaled by f/(f+z) and translated by the camera's own motion multiplied
    by the same factor, so a layer twice as far moves half as much and grows half as
    fast. The reference's red room does exactly this: the 2008 type slides across the
    man instead of riding with him, which is only possible if they are at two depths.
    """

    def __init__(self, f: float = 1500.0):
        self.f = f

    def project(self, z: float, cx: float, cy: float, cz: float) -> tuple[float, float, float]:
        k = self.f / max(1.0, self.f + z - cz)          # perspective scale for this depth
        k0 = self.f / max(1.0, self.f + z)              # how much camera motion it feels
        return k, -cx * k0, -cy * k0


CAM = Cam()


def place_px(dst: np.ndarray, img: np.ndarray, z: float, width: float, cx: float, cy: float,
             cz: float, opacity: float = 1.0, blur: float = 0.0,
             anchor: tuple[float, float] = (0.5, 0.5)) -> None:
    """Place a layer at a measured pixel width and let the camera scale it from there.

    Type is set by its ink width, so it must not be sized by `cover` -- cover answers
    "what fills the frame", which is the wrong question for a word.
    """
    k, dx, dy = CAM.project(z, cx, cy, cz)
    ih, iw = img.shape[:2]
    w = width * k
    h = ih * (w / iw)
    draw_layer(dst, img, (W - w) * anchor[0] + dx, (H - h) * anchor[1] + dy,
               w, opacity, 0.0, 0.0, blur, h=h)


def place(dst: np.ndarray, img: np.ndarray, z: float, cx: float, cy: float, cz: float,
          cover: float = 1.0, opacity: float = 1.0, blur: float = 0.0,
          anchor: tuple[float, float] = (0.5, 0.5)) -> None:
    """Composite one RGBA layer through the camera. `cover` is how it fills the frame at z=0."""
    k, dx, dy = CAM.project(z, cx, cy, cz)
    ih, iw = img.shape[:2]
    need = max(W / iw, H / ih) * cover
    w = iw * need * k
    h = ih * need * k
    draw_layer(dst, img, (W - w) * anchor[0] + dx, (H - h) * anchor[1] + dy,
               w, opacity, 0.0, 0.0, blur, h=h)


# -------------------------------------------------------------------------- colour
def rgb(r: float, g: float, b: float) -> np.ndarray:
    """RGB in, frame-order (BGR) out. Every colour in this file goes through here.

    Two channel swaps in a row happened because literals were written in RGB and used
    on a BGR canvas. One helper, one direction, plus a self-test in `prepare`.
    """
    return np.array([b, g, r], np.float32)


def colour_selftest() -> None:
    """Draw a known colour through the same path the scenes use and check it comes back."""
    canvas = np.zeros((8, 8, 3), np.float32)
    canvas[:] = rgb(255, 0, 0)
    b, g, r = canvas[4, 4]
    if not (r > 250 and g < 5 and b < 5):
        raise SystemExit(f"colour path is swapped: asked for red, got BGR {(b, g, r)}")

# ---------------------------------------------------------------------------- type
_fonts: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    if (name, size) not in _fonts:
        _fonts[(name, size)] = ImageFont.truetype(f"{VENDOR}/{name}", size)
    return _fonts[(name, size)]


_tglyph: dict[tuple[str, str], np.ndarray] = {}


def glyph(text: str, face: str = "ArchivoBlack-Regular.ttf") -> np.ndarray:
    """The word once at 4x, cropped to its ink box; resampled per use."""
    key = (text, face)
    if key not in _tglyph:
        img = Image.new("L", (3600, 900), 0)
        ImageDraw.Draw(img).text((60, 100), text, font=font(face, 420), fill=255)
        a = np.asarray(img)
        ys, xs = np.where(a > 8)
        _tglyph[key] = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return _tglyph[key]


def draw_text(dst: np.ndarray, text: str, x: float, y: float, w: float, colour,
              opacity: float = 1.0, rot: float = 0.0, skew: float = 0.0,
              blur: float = 0.0, face: str = "ArchivoBlack-Regular.ttf") -> None:
    """Set a word by its ink width, which is how the reference's type was measured."""
    if opacity <= 0.003:
        return
    g = glyph(text, face)
    rgba = np.dstack([np.full(g.shape, c, np.uint8) for c in colour[::-1]]
                     + [g]).astype(np.uint8)
    draw_layer(dst, rgba, x, y, w, opacity, rot, skew, blur)


# --------------------------------------------------------------------------- plate
_plate_cache: dict = {}


def plate_surface(coef, basis) -> np.ndarray:
    key = (tuple(np.round(coef, 4)), len(basis))
    if key not in _plate_cache:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
        X, Y = xx / W - 0.5, yy / H - 0.5
        lum = sum(c * (X ** i) * (Y ** j) for c, (i, j) in zip(coef, basis))
        _plate_cache[key] = np.dstack([lum] * 3).astype(np.float32)
    return _plate_cache[key].copy()


def plate_colour(rgb) -> np.ndarray:
    return np.full((H, W, 3), rgb[::-1], np.float32)


def plate_gradient(stops: list[tuple[float, tuple[int, int, int], float, float]],
                   base: tuple[int, int, int]) -> np.ndarray:
    """A soft lit field: elliptical radial stops, measured centres and radii."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    out = np.zeros((H, W, 3), np.float32)
    for cy, cx, r, colour in stops:
        d = np.sqrt(((xx - cx * W) / (r * W)) ** 2 + ((yy - cy * H) / (r * W)) ** 2)
        k = np.clip(1 - d, 0, 1) ** 0.7
        out += np.array(colour[::-1], np.float32) * k[..., None]
    return out + plate_colour(base) * np.clip(1 - out.max(axis=2) / 255.0, 0, 1)[..., None]


def plate_image(path: str, zoom: float = 1.0, dx: float = 0.0, dy: float = 0.0,
                crop_y: float = 0.5) -> np.ndarray:
    img = asset(path)[..., :3].astype(np.float32)
    ih, iw = img.shape[:2]
    s = max(W / iw, H / ih) * zoom
    nw, nh = int(round(iw * s)), int(round(ih * s))
    img = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LANCZOS4)
    x0 = int(round((nw - W) / 2 + dx))
    y0 = int(round((nh - H) * crop_y + dy))
    x0 = max(0, min(nw - W, x0)); y0 = max(0, min(nh - H, y0))
    return img[y0:y0 + H, x0:x0 + W].copy()


def vignette(frame: np.ndarray, strength: float = 0.35, power: float = 2.2) -> None:
    key = (round(strength, 3), round(power, 2))
    if key not in _plate_cache:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 1.414
        _plate_cache[key] = (1 - strength * np.clip(d, 0, 1) ** power)[..., None]
    frame *= _plate_cache[key]


def grain(frame: np.ndarray, sigma: float, seed: int) -> None:
    if sigma <= 0:
        return
    rng = np.random.default_rng(seed)
    frame += rng.normal(0, sigma, (H, W, 1)).astype(np.float32)


# --------------------------------------------------------------------------- scenes
GREEN = (125, 187, 11)          # #7dbb0b, measured off the reference's field
RED = (162, 26, 27)             # #a21a1b, the 2008 plate
INK_RED = (157, 9, 10)          # #9d090a, HE SAID / NO
GLASS = (239, 231, 214)         # #efe7d6, the subscribe pill
BAG = "showreel/v4/assets/layers/plate-bag-green-front.png"


def scene_s1(f, t, u):
    """0.00-0.53  TWENTY on a lit card, rising. Plate is the fitted surface."""
    f[:] = plate_surface(S["plate_coef"], S["plate_basis"])
    draw_text(f, "TWENTY", 118, lerp(672, 626, ease(u, "out")), 452, GREEN,
              opacity=min(1.0, 0.25 + u * 1.4), blur=lerp(4.0, 0.0, ease(u, "out")))
    vignette(f, 0.30)


def scene_s2(f, t, u):
    """0.53-0.83  the slam: TWENTY small, BILLION large, on near-black."""
    f[:] = plate_gradient([(0.55, 0.5, 0.95, (38, 38, 38))], (11, 11, 11))
    draw_text(f, "TWENTY", 34, 690, 196, GREEN)
    draw_text(f, "BILLION", 176, lerp(512, 552, ease(u, "out")), 470, GREEN,
              skew=0.02, blur=lerp(6.0, 0.0, ease(u, "out")))
    vignette(f, 0.55)


def scene_s3(f, t, u):
    """0.80-1.33  the green field: BILLION above the bag, both flying in."""
    f[:] = plate_gradient([(0.46, 0.5, 0.86, (108, 152, 52))], (92, 138, 24))
    k = ease(u, "out")
    draw_layer(f, TBAG, lerp(178, 152, k), lerp(392, 424, k), lerp(344, 424, k),
               opacity=min(1.0, 0.35 + u * 1.7), blur=lerp(10.0, 0.0, k), rot=-4 + 4 * k)
    f[:] = np.clip(f * 0.72, 0, 255)                 # grade: the reference's field is deep
    draw_text(f, "BILLION", lerp(150, 112, k), lerp(170, 196, k), lerp(340, 430, k), (24, 32, 4),
              opacity=min(1.0, 0.2 + u * 1.8), rot=-4.0, blur=lerp(8.0, 0.0, k))
    vignette(f, 0.26)


def scene_s4(f, t, u):
    """1.33-3.13  the bag on a stool in a storm, HE, then NO."""
    f[:] = plate_image("showreel/v4/assets/plate-bag-stool.png", zoom=1.04,
                       dx=lerp(10, -6, u), dy=lerp(-8, 8, u), crop_y=0.46)
    f[:] = np.clip(f * 1.22 + 16, 0, 255)            # the reference's storm is a bright grey
    ka = ease(min(1.0, max(0.0, (t - 1.88) / 0.20)), "out")
    draw_text(f, "HE", 150, 150, 200, INK_RED, opacity=ka, blur=lerp(5.0, 0.0, ka))
    a = ease(min(1.0, max(0.0, (t - 2.04) / 0.14)), "out")
    if a > 0:
        sc = lerp(1.42, 1.0, a)
        draw_text(f, "NO", 128 + (1 - sc) * 170, 268 + (1 - sc) * 88, 386 * sc, INK_RED,
                  opacity=a, blur=lerp(8.0, 0.0, a))
    vignette(f, 0.30)


def feather_edges(img: np.ndarray, px: int = 46, bottom: int = 120) -> np.ndarray:
    """Soften a cutout's own border so the cut is never the thing you see.

    A cutout that ends mid-frame reads as a sticker; the reference's figure is lit into
    the room, so the transition has to be gradual. The bottom gets a longer ramp because
    that is where a subject is normally lost in shadow.
    """
    out = img.copy()
    a = out[..., 3].astype(np.float32)
    ramp = np.linspace(0, 1, px)[:, None]
    a[:px] *= ramp
    a[-bottom:] *= np.linspace(1, 0, bottom)[:, None] ** 1.4
    ramp2 = np.linspace(0, 1, px)[None, :]
    a[:, :px] *= ramp2
    a[:, -px:] *= ramp2[:, ::-1]
    out[..., 3] = np.clip(a, 0, 255).astype(np.uint8)
    return out


def red_field(dst: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """The room: a deep red wall, lit from the upper left, darkening toward the floor."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - 0.16 * W) / (0.92 * W)) ** 2 + ((yy - 0.16 * H) / (0.80 * H)) ** 2)
    lit = np.clip(1 - d, 0, 1) ** 1.15
    dark = rgb(34, 4, 6)                       # the wall away from the light
    bright = rgb(150, 26, 26)                  # the wall where the light rakes it
    field = dark + (bright - dark) * lit[..., None]
    field *= (1 - 0.55 * np.clip((yy / H - 0.62) / 0.38, 0, 1) ** 1.3)[..., None]
    dst[:] = np.clip(field * strength, 0, 255)


def red_room(f, t, u, push: float, cx: float, cy: float, cz: float) -> None:
    """The reference's red room as three planes at three depths.

    y<0   the year sits *behind* the subject, so the camera slides it across him instead
          of carrying it with him. That relative motion is the whole tell of parallax.
    z=900 the figure is a real cutout with its own alpha.
    z=1500 red haze in front separates the planes to the eye.
    Then the floor is taken down to shadow, which is where a subject is normally lost and
    which is also what hides a cutout's lower edge.
    """
    red_field(f)
    place_px(f, T2008, -520.0, 372 * push, cx * 0.42, cy * 0.42, cz, opacity=0.33,
             blur=1.1, anchor=(0.5, 0.055))
    place(f, THERO, 900.0, cx, cy, cz, cover=1.0 * push, opacity=1.0,
          anchor=(0.5, 0.52), blur=0.2)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    haze = np.zeros((H, W, 4), np.uint8)
    g = np.clip(1 - np.sqrt(((xx - 0.28 * W) / (1.0 * W)) ** 2 + ((yy - 0.30 * H) / (0.95 * H)) ** 2), 0, 1) ** 1.6
    haze[..., 3] = (g * 64).astype(np.uint8)
    place(f, haze, 1500.0, cx * 1.5, cy * 1.5, cz, cover=1.05, opacity=0.5)
    shadow = np.clip((yy / H - 0.80) / 0.20, 0, 1)[..., None] ** 1.5
    f[:] = f * (1 - 0.92 * shadow)


def scene_s5(f, t, u):
    """3.13-9.17  the red room: 2008, the figure, and a camera that pushes in."""
    p = ease(u, "linear")
    red_room(f, t, u, push=1.0 + 0.045 * p, cx=-10 + 22 * p, cy=-6 + 14 * p, cz=26 * p)
    vignette(f, 0.40)


def scene_s6(f, t, u):
    """9.17-11.73  same room, tighter, eyes hot, subscribe and like."""
    p = ease(u, "linear")
    red_room(f, t, u, push=1.10 + 0.05 * p, cx=18 - 26 * p, cy=10 - 18 * p, cz=40 * p)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for cx in (0.452, 0.556):
        dd = np.sqrt(((xx - cx * W) / (0.040 * W)) ** 2 + ((yy - 0.432 * H) / (0.013 * H)) ** 2)
        hot = np.clip(1 - dd, 0, 1) ** 1.3
        f[:] = f + np.array([34, 34, 255], np.float32) * hot[..., None] * 0.9
    a = ease(min(1.0, max(0.0, (t - 9.55) / 0.30)), "out")
    draw_pill(f, 168, lerp(824, 786, a), a)
    vignette(f, 0.44)


def draw_pill(f, x, y, a, scale=1.0):
    if a <= 0.01:
        return
    w, h = int(186 * scale), int(88 * scale)
    canvas = np.zeros((h, w, 4), np.uint8)
    cv2.rectangle(canvas, (0, 0), (w - 1, h - 1), (*GLASS[::-1], 255), -1, cv2.LINE_AA)
    canvas = cv2.GaussianBlur(canvas, (0, 0), 0.6)
    draw_layer(f, canvas, x, y, w, opacity=a * 0.94)
    draw_text(f, "SUBSCRIBE", x + 16 * scale, y + 12 * scale, 152 * scale, (30, 26, 20),
              opacity=a, face="Poppins-SemiBold.ttf")


def scene_s7(f, t, u):
    """11.73-12.20  the loop head: TWENTY again, fast, brighter."""
    f[:] = plate_surface(S["plate_coef"], S["plate_basis"]) * 1.05
    draw_text(f, "TWENTY", 118, lerp(700, 632, ease(u, "out")), 470, GREEN,
              opacity=min(1.0, 0.2 + u * 2.0), blur=lerp(7.0, 0.0, ease(u, "out")))
    vignette(f, 0.28)


def scene_s8(f, t, u):
    """12.20-12.50  BILLION alone on black, skewed."""
    f[:] = plate_gradient([(0.5, 0.5, 0.9, (28, 28, 28))], (9, 9, 9))
    draw_text(f, "BILLION", 40, 600, 560, GREEN, opacity=1.0, skew=0.03,
              blur=lerp(5.0, 0.0, ease(u, "out")))
    vignette(f, 0.5)


def scene_s9(f, t, u):
    """12.50-12.70  green macro hold."""
    f[:] = plate_gradient([(0.5, 0.5, 0.9, (108, 152, 52))], (92, 138, 24))
    draw_layer(f, TBAG, 40, 300, 640, opacity=1.0, blur=2.0)
    f[:] = np.clip(f * 0.72, 0, 255)
    vignette(f, 0.3)


def scene_s10(f, t, u):
    """12.70-13.00  the bag in green, close."""
    f[:] = plate_gradient([(0.46, 0.5, 0.85, (108, 152, 52))], (92, 138, 24))
    draw_layer(f, TBAG, 116, 396, 512, opacity=1.0, blur=1.0)
    f[:] = np.clip(f * 0.72, 0, 255)
    draw_text(f, "BILLION", 110, 240, 452, (28, 34, 6), opacity=1.0, rot=-3.0)
    vignette(f, 0.3)


def scene_s11(f, t, u):
    """13.00-14.83  the stool, HE then NO, on a bright grey storm."""
    f[:] = plate_image("showreel/v4/assets/plate-bag-stool.png", zoom=1.06, crop_y=0.46,
                       dy=lerp(-6, 6, u))
    g = min(1.0, max(0.0, (t - 13.20) / 0.45))
    if g > 0:
        lum = f.mean(axis=2, keepdims=True)
        f[:] = f * (1 - g * 0.85) + (lum * 0.9 + 16) * (g * 0.85)
    draw_text(f, "HE", 150, 210, 300, INK_RED, opacity=ease(min(1.0, (t - 13.15) / 0.2), "out"))
    a = ease(min(1.0, max(0.0, (t - 13.55) / 0.22)), "back")
    draw_text(f, "NO", 92, 300, 420 * (1.3 - 0.3 * a), INK_RED, opacity=min(1.0, a * 1.6),
              blur=lerp(6.0, 0.0, a))
    vignette(f, 0.34)


def scene_s12(f, t, u):
    """14.83-20.63  the red room, longer: 2008, the portrait, the push."""
    f[:] = plate_colour(RED)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - 0.2 * W) / (0.8 * W)) ** 2 + ((yy - 0.24 * H) / (0.6 * H)) ** 2)
    f[:] = np.clip(f * (1 - 0.55 * np.clip(1 - d, 0, 1) ** 1.2)[..., None] + (8, 3, 48), 0, 255)
    draw_text(f, "2008", 146, 236, 424, (218, 216, 218), opacity=0.62)
    draw_layer(f, THERO, lerp(158, 134, u), lerp(400, 372, u), lerp(486, 536, u), opacity=1.0)
    g = lerp(0.10, 0.34, ease(u, "linear"))
    f[:] = f * (1 - g) + plate_colour(RED) * g
    vignette(f, 0.44)


def scene_s13(f, t, u):
    """20.63-23.27  the CTA: red reveal, the figure, a flash, the glass card.

    The reveal itself is the camera pulling back through the planes: at the head the
    figure is large and the wall is close behind him, and by the end there is room for
    the card. That is a dolly, not a cross-fade between two layouts.
    """
    p = ease(u, "out")
    red_room(f, t, u, push=1.22 - 0.16 * p, cx=-18 + 26 * p, cy=14 - 20 * p, cz=-60 + 44 * p)
    if 20.80 <= t < 20.86:                      # the reference's one-frame flash
        f[:] = np.minimum(f * 1.85 + 66, 255)
    a = ease(min(1.0, max(0.0, (t - 21.10) / 0.45)), "out")
    if a > 0:
        cardh, cardw = int(300 * lerp(0.88, 1.0, a)), int(560 * lerp(0.88, 1.0, a))
        card = np.zeros((cardh, cardw, 4), np.uint8)
        cv2.rectangle(card, (12, 12), (cardw - 13, cardh - 13), (*GLASS[::-1], 236), -1, cv2.LINE_AA)
        card = cv2.GaussianBlur(card, (0, 0), 1.2)
        card[..., 3] = (card[..., 3] * a).astype(np.uint8)
        draw_layer(f, card, (W - cardw) // 2, 790 - cardh // 2, cardw, opacity=a * 0.96)
        sub = "SUBSCRIBE  •  LIKE"
        draw_text(f, sub, (W - 380) // 2, 790 - cardh // 2 + 66, 380, (26, 20, 16), opacity=a,
                  face="Poppins-SemiBold.ttf")
    vignette(f, 0.48)


# ---------------------------------------------------------------------------- spec
S: dict = {}
TBAG: np.ndarray | None = None
TSTOOL: np.ndarray | None = None
THERO: np.ndarray | None = None
T2008: np.ndarray | None = None
THAND: np.ndarray | None = None


def load_spec(path: str) -> dict:
    spec = json.loads(Path(path).read_text())
    prev = 0.0
    for s in spec["shots"]:
        if abs(s["start"] - prev) > 1e-6:
            raise SystemExit(f"{s['id']}: starts at {s['start']}, previous shot ends at {prev}")
        if s["end"] <= s["start"]:
            raise SystemExit(f"{s['id']}: ends before it starts")
        prev = s["end"]
    if abs(prev - spec["duration"]) > 1e-6:
        raise SystemExit(f"shots end at {prev}, spec says {spec['duration']}")
    return spec


def prepare(spec: dict) -> None:
    """Cut our object layers out of our own plates, once, before any frame is drawn."""
    global S, TBAG, TSTOOL, THERO, THAND, T2008
    S = spec
    TBAG = cut(asset(BAG))
    # the bag on the stool: the plate's own subject, taken by its difference from the
    # storm behind it (the storm is grey and softly graded, the bag is not)
    pl = asset("showreel/v4/assets/plate-bag-stool.png")
    rgb = pl[..., :3].astype(np.float32)
    g = cv2.cvtColor(pl[..., :3], cv2.COLOR_BGR2GRAY).astype(np.float32)
    mu = cv2.boxFilter(g, -1, (13, 13))
    var = cv2.boxFilter(g * g, -1, (13, 13)) - mu * mu
    tex = np.sqrt(np.clip(var, 0, None))
    sat = rgb.max(axis=2) - rgb.min(axis=2)
    m = ((tex > 9) | (sat > 34)).astype(np.uint8)
    m[:240] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((41, 41), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((17, 17), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    k = 1 + int(np.argmax(st[1:, 4]))
    keep = (lab == k).astype(np.uint8)
    alpha = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 1.6)
    alpha = np.clip((alpha - 0.3) / 0.5, 0, 1)
    TSTOOL = cut(np.dstack([pl[..., :3], (alpha * 255).astype(np.uint8)]))
    # the portrait: our cta plate's front layer, already cut by its own alpha
    THERO = feather_edges(cut(asset("showreel/v4/assets/layers/plate-cta-hero-front.png")),
                          px=44, bottom=250)
    THAND = cut(asset("showreel/v4/assets/layers/plate-hands-red-front.png"))
    g = glyph("2008")
    grey = 214
    rgba = np.dstack([np.full(g.shape, grey, np.uint8)] * 3 + [(g * 0.92).astype(np.uint8)])
    T2008 = rgba


def render_frame(i: int, spec: dict, fps: int) -> np.ndarray:
    t = i / fps
    shot = next((s for s in spec["shots"] if s["start"] <= t < s["end"]), spec["shots"][-1])
    u = (t - shot["start"]) / (shot["end"] - shot["start"])
    f = np.zeros((H, W, 3), np.float32)
    globals()[f"scene_{shot['fn']}"](f, t, u)
    if shot.get("grain", 1.4) > 0:
        grain(f, shot["grain"], i * 7919 + 13)
    if shot.get("dissolve_in", 0) > 0:
        k = ease(min(1.0, (t - shot["start"]) / shot["dissolve_in"]), "smooth")
        prev_i = max(0, int(round(shot["start"] * fps)) - 1)
        prev = render_prev(prev_i, spec, fps)
        f = prev * (1 - k) + f * k
    return np.clip(f, 0, 255).astype(np.uint8)


_prev_cache: dict[int, np.ndarray] = {}


def render_prev(i: int, spec: dict, fps: int) -> np.ndarray:
    """One cached frame of the shot that ends where this one starts (for dissolves)."""
    if i not in _prev_cache:
        _prev_cache.clear()
        _prev_cache[i] = render_frame(i, spec, fps).astype(np.float32)
    return _prev_cache[i]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default="spec/v5-01.json")
    ap.add_argument("--out", default="public/demo/v5-30.mp4")
    ap.add_argument("--cfr", default="16")
    ap.add_argument("--from", dest="start", type=float, default=0.0)
    ap.add_argument("--to", dest="stop", type=float, default=None)
    ap.add_argument("--only", default=None, help="comma-separated shot ids")
    ap.add_argument("--stills", default=None, help="write PNG stills instead of a video")
    a = ap.parse_args()

    spec = load_spec(a.spec)
    t0 = time.time()
    prepare(spec)
    colour_selftest()
    print(f"  prepare {time.time() - t0:.2f}s   bag {TBAG.shape[1]}x{TBAG.shape[0]}  "
          f"stool {TSTOOL.shape[1]}x{TSTOOL.shape[0]}  portrait {THERO.shape[1]}x{THERO.shape[0]}")

    fps = spec["fps"]
    stop = spec["duration"] if a.stop is None else a.stop
    frames = [i for i in range(int(round(spec["duration"] * fps)))
              if a.start <= i / fps < stop]
    if a.only:
        want = {x.strip() for x in a.only.split(",")}
        frames = [i for i in frames
                  if next((s["id"] for s in spec["shots"] if s["start"] <= i / fps < s["end"]),
                          None) in want]

    if a.stills:
        Path(a.stills).mkdir(parents=True, exist_ok=True)
        for i in frames:
            cv2.imwrite(f"{a.stills}/f{i:04d}.png", render_frame(i, spec, fps))
        print(f"  {len(frames)} stills -> {a.stills}  ({time.time() - t0:.1f}s)")
        return 0

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    enc = subprocess.Popen([ffmpeg(), "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                            "-c:v", "libx264", "-crf", a.cfr, "-preset", "medium",
                            "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out],
                           stdin=subprocess.PIPE)
    for i in frames:
        enc.stdin.write(render_frame(i, spec, fps).tobytes())
    enc.stdin.close()
    enc.wait()
    dt = time.time() - t0
    print(f"  {len(frames)} frames in {dt:.1f}s ({len(frames) / dt:.1f} fps) -> {a.out} "
          f"({Path(a.out).stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
