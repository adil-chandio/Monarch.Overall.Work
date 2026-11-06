#!/usr/bin/env python3
"""The typographic renderer for 0.00-1.00 s: a plate, a font, and a table of numbers.

This module knows nothing about the reference file. It draws a bright band and sets
one word, driven by a per-frame parameter table (tools/../spec/typo-block.json):

    y       the word's top edge, in pixels
    scale   width multiplier against the settled 448 px
    squash  height multiplier, for the vertical travel
    sigma   motion-blur sigma in *settled* pixels
    alpha   ink opacity (a word arriving out of a bright plate fades as well as moves)
    ink     how far its colour has travelled from the plate to #7dbb0b
    dark    the whole-frame dimmer, 1.0 = plate at full brightness

`tune_typo.py` fills the table by minimising the difference against the reference
frame by frame; `block_typo.py` renders with it. Nothing is hand-keyed.
"""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 720, 1280
FONT = "showreel/v4/vendor/ArchivoBlack-Regular.ttf"   # IoU 0.747 on the settled word,
                                                      # the best of 58 faces tested
WORD = "TWENTY"
SETTLE_W, SETTLE_H = 448, 80
INK = np.array([125, 187, 11], np.float32)

_GLYPH = None
BLOOM = [0.0]        # swept against the reference: bloom made it very slightly worse
INK_SCALE = [0.95]   # same sweep: 0.95 ink is the best fit


def glyph() -> Image.Image:
    """The word once, at 4x, cropped to its ink box — resampled per frame, never per call."""
    global _GLYPH
    if _GLYPH is None:
        img = Image.new("L", (3200, 900), 0)
        ImageDraw.Draw(img).text((60, 100), WORD, font=ImageFont.truetype(FONT, 420), fill=255)
        _GLYPH = img.crop(img.getbbox())
    return _GLYPH


_PLATE = None


def surface(coef, basis) -> np.ndarray:
    """One frame's background from its own 15 fitted coefficients."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    X, Y = xx / W - 0.5, yy / H - 0.5
    lum = sum(c * (X ** i) * (Y ** j) for c, (i, j) in zip(coef, basis))
    return np.dstack([lum] * 3).astype(np.float32)


def plate(spec=None) -> np.ndarray:
    """The lit background: a 15-term polynomial surface fitted to the measured plate.

    The reference's plate is a soft lit card with a bright band low-centre and a dark
    vignette. A sampled grid showed its own cells; the surface has no cells, and it is
    still made of measured numbers rather than a formula somebody invented.
    """
    global _PLATE
    if spec is not None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
        X, Y = xx / W - 0.5, yy / H - 0.5
        coef = np.asarray(spec["coef"], np.float64)
        lum = sum(c * (X ** i) * (Y ** j) for c, (i, j) in zip(coef, spec["basis"]))
        _PLATE = np.dstack([lum] * 3).astype(np.float32)
    return _PLATE.copy()


def _draw(base: np.ndarray, x: int, y: int) -> None:
    """Add `base` (0..1) into `base`'s canvas at (x, y), clipped at the frame edge."""
    h, w = base.shape
    y0, y1 = max(0, y), min(H, y + h)
    x0, x1 = max(0, x), min(W, x + w)
    if x1 <= x0 or y1 <= y0:
        return
    return y0, y1, x0, x1


def _mask(p: dict) -> tuple[np.ndarray, np.ndarray]:
    """The word's coverage and its bloom, both full-frame, both 0..1.

    Two ways a frame of this block carries the word, and they are different physics:

      travelling (squash > 1.12)  the shutter is open while it moves, so the frame is the
                                  word averaged along its path -- never a stretched glyph,
                                  which would ink the whole span at full weight
      sitting                     one sharp glyph with a soft edge and a wide low bloom,
                                  because the reference's lettering reads as light
    """
    g = glyph()
    alpha = float(p.get("alpha", 1.0))
    tw = max(8, int(round(SETTLE_W * p.get("scale", 1.0))))
    base_h = max(8, int(round(g.height * tw / g.width)))
    x = int(round(p.get("x", (W - tw) // 2)))
    y = int(round(p.get("y", 0)))
    sq = float(p.get("squash", 1.0))

    a = np.zeros((H, W), np.float32)
    if sq > 1.12:
        travel = (sq - 1.0) * base_h
        k = max(3, min(16, int(round(travel / 2.5))))
        g1 = np.asarray(g.resize((tw, base_h), Image.LANCZOS), np.float32) / 255.0
        for j in range(k):
            yy = int(round(y + travel * j / (k - 1)))
            box = _draw(g1, x, yy)
            if box:
                y0, y1, x0, x1 = box
                a[y0:y1, x0:x1] += g1[y0 - yy:y1 - yy, x0 - x:x1 - x] / k
        halo = cv2.GaussianBlur(a, (0, 0), 5.0) * (0.22 * BLOOM[0])
    else:
        ss = 2
        big = g.resize((tw * ss, base_h * ss), Image.LANCZOS)
        sigma = float(p.get("sigma", 0.0)) * ss
        if sigma > 0.05:
            big = big.filter(ImageFilter.GaussianBlur(sigma))
        g1 = np.asarray(big.resize((tw, base_h), Image.LANCZOS), np.float32) / 255.0
        box = _draw(g1, x, y)
        if box:
            y0, y1, x0, x1 = box
            a[y0:y1, x0:x1] = g1[y0 - y:y1 - y, x0 - x:x1 - x]
        halo = cv2.GaussianBlur(a, (0, 0), max(2.5, tw / 55.0)) * (0.30 * BLOOM[0])
    return a * alpha, halo * alpha


def render(p: dict) -> np.ndarray:
    """One frame, RGB uint8, from one row of the table."""
    rgb = surface(p["plate_coef"], p["plate_basis"]) if p.get("plate_coef") else plate()
    if p.get("alpha", 0) > 0.002 and p.get("x") is not None:
        cov, halo = _mask(p)
        ink = np.clip(INK * INK_SCALE[0], 0, 255)[None, None, :]
        rgb = rgb * (1 - halo[..., None]) + ink * halo[..., None]
        rgb = rgb * (1 - cov[..., None]) + ink * cov[..., None]
    return np.clip(rgb, 0, 255).astype(np.uint8)


def load(path: str = "spec/typo-block.json") -> dict:
    d = json.loads(Path(path).read_text())
    plate(d["plate"])
    return d
