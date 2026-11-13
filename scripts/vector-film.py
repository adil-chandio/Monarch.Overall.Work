#!/usr/bin/env python3
"""Flat-vector motion graphics — the ApexMorph grammar, applied to Extinct Life.

Why this exists, in one paragraph: the competitor study found that a 2.1M-view
documentary is not 3D. It is flat shapes that slide, scale and fade, held together
by nine repeated devices (stamps, counting grids, animating numbers, pinned labels,
scale reveals, fake UIs, visible sound, held question cards, fake rewind). This
renders that grammar from a script and a timed SRT, with no render farm and no GPU.

Deliberate constraints, each with a reason:

  * Flat colour only. No gradients beyond one flat vertical wash, no textures, no
    lighting. That is what makes silhouette animation read at phone size and it is
    why the competitor can afford 10 minutes.
  * Every device is a function of `t` — a pure function of time. No state machine,
    no keyframe store, no dependencies. A frame can be rendered alone, in any order,
    which is the difference between a 3-minute render and a 3-hour one.
  * No asset files. Every animal is drawn from a small set of bezier/polygon
    primitives in this file. Nothing to lose, nothing to relink, nothing to license.

Usage:
    python scripts/vector-film.py --srt <file.srt> --out <dir> [--fps 30] [--w 1280 --h 720]
    python scripts/vector-film.py --srt <file.srt> --frames 0:900 --out <dir>

Writes PNG frames. Encoding is a separate step (see --encode).
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    sys.exit("needs Pillow: python -m pip install pillow")

# ---------------------------------------------------------------------------
# The palette. Taken from the competitor's video, not invented: deep teal water,
# near-black figures, one warm accent for stamps, one gold for numbers.
# ---------------------------------------------------------------------------
WATER_TOP = (18, 44, 58)
WATER_BOT = (8, 26, 36)
INK = (10, 14, 18)
BONE = (232, 228, 218)
WHITE = (245, 245, 242)
ACCENT = (198, 58, 46)      # the stamp red
GOLD = (232, 186, 62)       # the counting numbers
TEAL = (86, 168, 178)
GREY = (140, 150, 156)


def lerp(a, b, t):
    return a + (b - a) * t


def clamp01(x):
    return 0.0 if x < 0 else (1.0 if x > 1 else x)


def ease_out(t):
    t = clamp01(t)
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    t = clamp01(t)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def smoothstep(a, b, x):
    if b == a:
        return 0.0
    t = clamp01((x - a) / (b - a))
    return t * t * (3 - 2 * t)


def window(t, start, end, fade=0.28):
    """1.0 inside [start, end], easing to 0 outside. The single primitive every
    device uses, so nothing ever pops in or out without a fade.

    The fade is clamped to a quarter of the cue: an unclamped fade on a 0.9 s cue
    makes the two ramps overlap and the result never reaches 1.0, so the beat is
    half-drawn for its whole life. That bug shipped once and made the last ten
    seconds of the film render as an empty background.
    """
    span = max(0.05, end - start)
    fade = min(fade, span * 0.25)
    if t < start - fade or t > end + fade:
        return 0.0
    return min(smoothstep(start - fade, start, t), 1 - smoothstep(end, end + fade, t))


# ---------------------------------------------------------------------------
# Fonts. DejaVu ships with most Linux images and is the closest thing to the
# competitor's condensed sans that is guaranteed present. Missing fonts must not
# crash a render, so every lookup falls back to the PIL default.
# ---------------------------------------------------------------------------
_FONT_CACHE: dict = {}
_FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
]


def font(size: int, bold: bool = True):
    key = (size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    for p in _FONT_PATHS:
        if Path(p).exists():
            try:
                _FONT_CACHE[key] = ImageFont.truetype(p, size)
                return _FONT_CACHE[key]
            except OSError:
                continue
    _FONT_CACHE[key] = ImageFont.load_default()
    return _FONT_CACHE[key]


class Frame:
    """One canvas plus the primitives every device needs."""

    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.im = Image.new("RGB", (w, h), WATER_TOP)
        self.d = ImageDraw.Draw(self.im, "RGBA")

    def water(self, t: float, dark: float = 1.0):
        """A flat vertical wash plus slow drifting motes. No gradient maths beyond
        a row loop — 720 rows is trivial and keeps the fill exactly flat."""
        top = tuple(int(c * dark) for c in WATER_TOP)
        bot = tuple(int(c * dark) for c in WATER_BOT)
        for y in range(self.h):
            f = y / self.h
            self.d.line([(0, y), (self.w, y)],
                        fill=(int(lerp(top[0], bot[0], f)),
                              int(lerp(top[1], bot[1], f)),
                              int(lerp(top[2], bot[2], f))))
        # motes: a deterministic scatter, drifting up. sin() keeps it frame-pure.
        n = 90
        for i in range(n):
            seed = i * 2654435761 % 1000003
            x = seed % self.w
            base = (seed // 7) % self.h
            y = (base - t * 14) % self.h
            r = 1 + (i % 3)
            a = 26 + (i % 5) * 8
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=(150, 200, 210, a))

    # -- text ------------------------------------------------------------
    def text(self, xy, s, size=34, fill=WHITE, alpha=1.0, anchor="la", spacing=6):
        if alpha <= 0:
            return
        f = font(size)
        col = tuple(fill) + (int(255 * clamp01(alpha)),)
        # shadow first: flat type on a dark plate needs one or it disappears
        self.d.text((xy[0] + 2, xy[1] + 3), s, font=f, fill=(0, 0, 0, int(120 * clamp01(alpha))), anchor=anchor)
        self.d.text(xy, s, font=f, fill=col, anchor=anchor)

    def centred(self, y, s, size=48, fill=WHITE, alpha=1.0):
        self.text((self.w // 2, y), s, size=size, fill=fill, alpha=alpha, anchor="ma")

    # -- the stamp -------------------------------------------------------
    def stamp(self, y, s, t_in, t, size=54, colour=ACCENT, hold_after=True):
        """Device 1. A bordered box with slight rotation. Appears with a 0.25 s
        scale punch, never a fade-only. This is the channel's signature and the
        reason eleven of them read as authorship rather than repetition."""
        p = ease_out((t - t_in) / 0.25)
        if p <= 0:
            return
        f = font(size)
        box = self.d.textbbox((0, 0), s, font=f)
        tw, th = box[2] - box[0], box[3] - box[1]
        padx, pady = 26, 16
        bw, bh = tw + padx * 2, th + pady * 2
        cx, cy = self.w // 2, y
        ang = -2.2
        # draw on a small canvas and rotate, so the border tilts with the text
        pad = 12
        card = Image.new("RGBA", (bw + pad * 2, bh + pad * 2), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        cd.rectangle([pad, pad, pad + bw, pad + bh], fill=tuple(colour) + (235,))
        cd.rectangle([pad, pad, pad + bw, pad + bh], outline=(255, 255, 255, 210), width=3)
        cd.text((pad + bw // 2, pad + bh // 2), s, font=f, fill=(255, 255, 255, 255), anchor="mm")
        sc = 0.86 + 0.14 * p
        card = card.resize((max(1, int(card.width * sc)), max(1, int(card.height * sc))), Image.LANCZOS)
        card = card.rotate(ang, expand=True, resample=Image.BICUBIC)
        alpha = int(255 * clamp01(p))
        if alpha < 255:
            a = card.split()[3].point(lambda v: int(v * alpha / 255))
            card.putalpha(a)
        self.im.paste(card, (cx - card.width // 2, int(cy - card.height // 2)), card)

    # -- device 2: the counting grid -------------------------------------
    def counting_grid(self, x, y, cell, cols, rows, filled, t_reveal, t, colour=GOLD):
        for i in range(cols * rows):
            if t < t_reveal + i * 0.055:
                continue
            c, r = i % cols, i // cols
            px, py = x + c * cell, y + r * cell
            on = i < filled
            if on:
                self.d.rectangle([px, py, px + cell - 3, py + cell - 3], fill=tuple(colour) + (230,))
            else:
                self.d.rectangle([px, py, px + cell - 3, py + cell - 3], outline=(120, 140, 150, 150), width=2)

    # -- device 3: the animating number ---------------------------------
    def counter(self, cx, cy, value, size=96, colour=GOLD, suffix="", label=None):
        s = f"{value}{suffix}"
        self.text((cx, cy), s, size=size, fill=colour, anchor="mm")
        if label:
            self.text((cx, cy + size * 0.72), label, size=int(size * 0.24),
                      fill=(215, 222, 226), anchor="ma")

    # -- device 4: pinned label ------------------------------------------
    def pin(self, xy, s, alpha=1.0, size=24):
        if alpha <= 0:
            return
        f = font(size)
        box = self.d.textbbox((0, 0), s, font=f)
        tw, th = box[2] - box[0], box[3] - box[1]
        a = int(210 * alpha)
        self.d.rectangle([xy[0] - tw / 2 - 8, xy[1] - th / 2 - 5,
                          xy[0] + tw / 2 + 8, xy[1] + th / 2 + 5], fill=(8, 12, 16, a))
        self.text((xy[0], xy[1]), s, size=size, fill=BONE, alpha=alpha, anchor="mm")

    # -- device 5: scale reveal ------------------------------------------
    def human_for_scale(self, x, y, h=70, alpha=1.0):
        a = int(240 * alpha)
        self.d.ellipse([x - h * .09, y - h, x + h * .09, y - h + h * .18], fill=BONE + (a,))
        self.d.polygon([(x, y - h * .78), (x + h * .16, y), (x - h * .16, y)], fill=BONE + (a,))

    # -- device 8: the held question card --------------------------------
    def question_card(self, t, t_in, t_out, question, answer=None, answer_at=None):
        k = window(t, t_in, t_out, fade=0.35)
        if k <= 0:
            return
        dark = Image.new("RGBA", (self.w, self.h), (0, 0, 0, int(150 * k)))
        self.im.paste(Image.alpha_composite(self.im.convert("RGBA"), dark).convert("RGB"), (0, 0))
        self.centred(self.h // 2 - 40, question, size=52, fill=WHITE, alpha=k)
        if answer and answer_at is not None:
            self.centred(self.h // 2 + 46, answer, size=40, fill=GOLD,
                         alpha=window(t, answer_at, t_out, 0.3))

    # -- device 7: visible sound -----------------------------------------
    def rings(self, cx, cy, t, period=1.6, n=4, radius=260, alpha=0.7):
        for i in range(n):
            phase = ((t / period) + i / n) % 1.0
            r = 20 + phase * radius
            a = int(150 * alpha * (1 - phase))
            self.d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(170, 215, 225, a), width=3)
            self.d.ellipse([cx - r * .66, cy - r * .66, cx + r * .66, cy + r * .66],
                           outline=(170, 215, 225, int(a * .55)), width=2)


# ---------------------------------------------------------------------------
# Animal silhouettes. Flat, unshaded, dot eye — the competitor's whole visual
# economy. Each takes (frame, cx, cy, size, flip, alpha) so it can drift or scale.
# ---------------------------------------------------------------------------
def cat_nibble(f: Frame, cx, cy, s, alpha=1.0, flip=False):
    """Homotherium cub: crouched, oversized front paws, small round ears, heavy neck.

    Proportions come from the 2024 Scientific Reports description (small ears,
    robust neck, broad forelimbs) and not from any artwork. Drawn as five filled
    shapes plus two dots — the competitor's economy is that a silhouette is
    legible at phone size precisely because it has no detail to blur.
    """
    if alpha <= 0:
        return
    a = int(255 * alpha)
    x = -1 if flip else 1

    def P(px, py):
        return (cx + px * s, cy + py * s)

    # tail, behind everything
    f.d.polygon([P(-0.50 * x, 0.02), P(-0.72 * x, -0.10), P(-0.74 * x, -0.02),
                 P(-0.50 * x, 0.14)], fill=BONE + (a,))
    # hind quarters — a low haunch, not a lumpy blob
    l, r = sorted((cx - 0.56 * s * x, cx - 0.10 * s * x))
    f.d.ellipse([l, cy - 0.10 * s, r, cy + 0.30 * s], fill=BONE + (a,))
    # barrel of the body
    l, r = sorted((cx - 0.40 * s * x, cx + 0.30 * s * x))
    f.d.ellipse([l, cy - 0.16 * s, r, cy + 0.22 * s], fill=BONE + (a,))
    # heavy neck + chest, the described feature
    hcx = cx + 0.10 * s * x
    f.d.ellipse([hcx - 0.22 * s, cy - 0.16 * s, hcx + 0.22 * s, cy + 0.24 * s], fill=BONE + (a,))
    # head — pulled in so the neck reads as one mass, not a separate ball
    hx = cx + 0.44 * s * x
    f.d.ellipse([hx - 0.21 * s, cy - 0.36 * s, hx + 0.17 * s, cy + 0.02 * s], fill=BONE + (a,))
    # muzzle
    f.d.polygon([(hx + 0.02 * s * x, cy - 0.15 * s), (hx + 0.22 * s * x, cy - 0.09 * s),
                 (hx + 0.22 * s * x, cy + 0.03 * s), (hx, cy + 0.05 * s)],
                fill=BONE + (a,))
    f.d.polygon([(cx + 0.10 * s * x, cy - 0.20 * s), (hx - 0.10 * s * x, cy - 0.24 * s),
                 (hx - 0.10 * s * x, cy + 0.06 * s), (cx + 0.10 * s * x, cy + 0.16 * s)],
                fill=BONE + (a,))
    # small round ears, set low on the skull
    for dx in (-0.09, 0.01):
        ex = hx + dx * s * x
        f.d.ellipse([ex - 0.062 * s, cy - 0.42 * s, ex + 0.062 * s, cy - 0.30 * s], fill=BONE + (a,))
    # broad front paws — both visible, the second described feature
    for dx in (0.10, 0.26):
        px = cx + dx * s * x
        f.d.ellipse([px - 0.085 * s, cy + 0.20 * s, px + 0.085 * s, cy + 0.32 * s], fill=BONE + (a,))
    # the dot eye. One dot is the whole face.
    f.d.ellipse([hx + 0.10 * s * x - 0.026 * s, cy - 0.25 * s,
                 hx + 0.10 * s * x + 0.026 * s, cy - 0.20 * s], fill=INK + (255,))
    # nose
    f.d.ellipse([hx + 0.23 * s * x - 0.020 * s, cy - 0.07 * s,
                 hx + 0.23 * s * x + 0.020 * s, cy - 0.03 * s], fill=INK + (int(220 * alpha),))


def lion_cub(f: Frame, cx, cy, s, alpha=1.0, flip=False):
    """The comparison animal. Deliberately plainer: bigger round ears, thin neck."""
    if alpha <= 0:
        return
    a = int(255 * alpha)
    x = -1 if flip else 1
    f.d.polygon([
        (cx - 0.52 * s * x, cy + 0.18 * s), (cx - 0.26 * s * x, cy - 0.06 * s),
        (cx + 0.10 * s * x, cy - 0.10 * s), (cx + 0.36 * s * x, cy + 0.02 * s),
        (cx + 0.48 * s * x, cy + 0.20 * s), (cx - 0.34 * s * x, cy + 0.24 * s),
    ], fill=GREY + (a,))
    f.d.ellipse([cx + 0.40 * s * x - 0.22 * s, cy - 0.32 * s,
                 cx + 0.40 * s * x + 0.22 * s, cy + 0.04 * s], fill=GREY + (a,))
    for dx in (-0.06, 0.18):
        ex = cx + (0.40 + dx) * s * x
        f.d.ellipse([ex - 0.08 * s, cy - 0.40 * s, ex + 0.08 * s, cy - 0.26 * s], fill=GREY + (a,))
    f.d.ellipse([cx + 0.50 * s * x - 0.022 * s, cy - 0.17 * s,
                 cx + 0.50 * s * x + 0.022 * s, cy - 0.12 * s], fill=INK + (255,))


def skull(f: Frame, cx, cy, s, alpha=1.0):
    """A skull plate seen from the side: cranium, muzzle, the saber canines.
    This is the CT section of the story, drawn rather than scanned."""
    if alpha <= 0:
        return
    a = int(240 * alpha)
    f.d.ellipse([cx - 0.30 * s, cy - 0.28 * s, cx + 0.14 * s, cy + 0.16 * s], fill=BONE + (a,))
    f.d.polygon([(cx + 0.02 * s, cy - 0.06 * s), (cx + 0.46 * s, cy - 0.10 * s),
                 (cx + 0.46 * s, cy + 0.06 * s), (cx + 0.04 * s, cy + 0.10 * s)], fill=BONE + (a,))
    f.d.ellipse([cx - 0.06 * s, cy - 0.02 * s, cx + 0.10 * s, cy + 0.12 * s], fill=INK + (int(190 * alpha),))
    for dx in (0.30, 0.40):
        f.d.polygon([(cx + dx * s, cy + 0.04 * s), (cx + (dx + 0.035) * s, cy + 0.30 * s),
                     (cx + (dx + 0.075) * s, cy + 0.05 * s)], fill=BONE + (a,))


# ---------------------------------------------------------------------------
# The film. Each beat is a function of time; the SRT window decides when it runs.
# ---------------------------------------------------------------------------
def build_beats(cues):
    """Map narration cue windows onto the nine devices. Kept as data so a later
    edit changes a number here, not the drawing code."""
    def at(i, lo=0.0, hi=1.0):
        if i >= len(cues):
            return (0.0, 0.0)
        a, b = cues[i][0], cues[i][1]
        return (a + (b - a) * lo, a + (b - a) * hi)

    return [
        # (name, start, end, drawer)
        ("hook-card", *at(0, 0.0, 0.55), draw_hook_card),
        ("age-counter", *at(0, 0.35, 1.0), draw_age_counter),
        ("fur-reveal", *at(1), draw_fur_reveal),
        ("permafrost", *at(2), draw_permafrost),
        ("not-alive", *at(3), draw_not_alive),
        ("ct-scan", *at(4), draw_ct_scan),
        ("species", *at(5), draw_species),
        ("three-weeks", *at(6), draw_three_weeks),
        ("comparison", *at(7), draw_comparison),
        ("preserved", *at(8), draw_preserved),
        ("incomplete", *at(9), draw_incomplete),
        ("not-resurrected", *at(10), draw_not_resurrected),
        # the closing card owns everything after the last cue. Without this the
        # film ends on whatever the previous beat left behind.
        ("closing", cues[-1][0], cues[-1][0] + 4.5, draw_closing),
    ]


def draw_hook_card(f: Frame, t0, t1, t):
    k = window(t, t0, t1, 0.4)
    if k <= 0:
        return
    f.water(t, dark=0.85)
    cat_nibble(f, f.w * 0.5, f.h * 0.58, 420 * (1 + 0.015 * math.sin(t * 2)), alpha=k)
    f.centred(f.h * 0.20, "THIS SABER-TOOTHED CUB", size=46, fill=WHITE, alpha=k)


def draw_age_counter(f: Frame, t0, t1, t):
    k = window(t, t0, t1, 0.35)
    if k <= 0:
        return
    f.water(t, dark=0.62)
    p = ease_out((t - t0) / max(0.4, (t1 - t0) * 0.7))
    val = int(lerp(0, 35000, p))
    f.counter(f.w // 2, f.h * 0.40, f"{val:,}", size=118, colour=GOLD, label="YEARS OLD")
    # the cub sits low and full-ink: a half-transparent silhouette reads as a
    # watermark, which is the opposite of what a hero subject should do
    cat_nibble(f, f.w * 0.5, f.h * 0.80, 300, alpha=k)


def draw_fur_reveal(f: Frame, t0, t1, t):
    k = window(t, t0, t1, 0.35)
    if k <= 0:
        return
    f.water(t, dark=0.75)
    f.centred(f.h * 0.30, "AND ITS FUR", size=54, fill=WHITE, alpha=k)
    f.stamp(f.h * 0.44, "IS STILL HERE", t0 + 0.25, t, size=50)
    # fur strokes: short deterministic hairs over the body region
    rnd = 1337
    for i in range(140):
        rnd = (rnd * 1103515245 + 12345) & 0x7FFFFFFF
        x = f.w * 0.30 + (rnd % 1000) / 1000 * f.w * 0.40
        rnd = (rnd * 1103515245 + 12345) & 0x7FFFFFFF
        y = f.h * 0.60 + (rnd % 700) / 1000 * f.h * 0.24
        a = int(70 * k)
        f.d.line([(x, y), (x + 6 * math.sin(i), y + 10)], fill=(200, 180, 150, a), width=1)


def draw_permafrost(f: Frame, t0, t1, t):
    k = window(t, t0, t1, 0.3)
    if k <= 0:
        return
    f.water(t, dark=0.5)
    # a flat ice shelf: one polygon, one highlight line
    y = f.h * 0.66
    f.d.polygon([(0, y), (f.w, y - 20), (f.w, f.h), (0, f.h)], fill=(176, 198, 208, int(255 * k)))
    f.d.line([(0, y), (f.w, y - 20)], fill=(225, 240, 246, int(230 * k)), width=4)
    f.pin((f.w * 0.5, f.h * 0.30), "SIBERIAN PERMAFROST", alpha=k, size=30)
    cat_nibble(f, f.w * 0.5, y - 40, 150, alpha=k * 0.85)


def draw_not_alive(f: Frame, t0, t1, t):
    k = window(t, t0, t1, 0.3)
    if k <= 0:
        return
    f.water(t, dark=0.9)
    f.centred(f.h * 0.34, "PRESERVED REMAINS", size=52, fill=WHITE, alpha=k)
    f.stamp(f.h * 0.52, "NOT A LIVING ANIMAL", t0 + 0.2, t, size=38)


def draw_ct_scan(f: Frame, t0, t1, t):
    k = window(t, t0, t1, 0.3)
    if k <= 0:
        return
    f.water(t, dark=0.8)
    # the scan line sweeps the skull — device 7 applied to investigation itself
    sweep = (t - t0) / max(0.6, t1 - t0)
    skull(f, f.w * 0.42, f.h * 0.52, 300, alpha=k)
    x = f.w * 0.42 - 170 + 340 * clamp01(sweep)
    f.d.rectangle([x - 3, f.h * 0.26, x + 3, f.h * 0.78], fill=TEAL + (int(150 * k),))
    f.text((f.w * 0.72, f.h * 0.30), "CT IMAGING", size=34, fill=TEAL, alpha=k)
    f.pin((f.w * 0.72, f.h * 0.40), "SKULL + TEETH", alpha=k * 0.9, size=22)


def draw_species(f: Frame, t0, t1, t):
    k = window(t, t0, t1, 0.3)
    if k <= 0:
        return
    f.water(t, dark=0.85)
    f.centred(f.h * 0.26, "HOMOTHERIUM", size=62, fill=WHITE, alpha=k)
    f.centred(f.h * 0.38, "AN EXTINCT SABER-TOOTHED CAT", size=30, fill=GREY, alpha=k)
    cat_nibble(f, f.w * 0.5, f.h * 0.64, 380, alpha=k)


def draw_three_weeks(f: Frame, t0, t1, t):
    k = window(t, t0, t1, 0.3)
    if k <= 0:
        return
    f.water(t, dark=0.9)
    p = ease_out((t - t0) / max(0.4, (t1 - t0) * 0.6))
    f.counter(f.w // 2, f.h * 0.42, int(lerp(0, 3, p)), size=170, colour=GOLD,
              suffix="", label="WEEKS OLD — FROM TOOTH ERUPTION")
    cat_nibble(f, f.w * 0.5, f.h * 0.80, 210, alpha=k * 0.9)


def draw_comparison(f: Frame, t0, t1, t):
    k = window(t, t0, t1, 0.3)
    if k <= 0:
        return
    f.water(t, dark=0.8)
    # Device 5: two animals at true relative scale, labelled
    cat_nibble(f, f.w * 0.30, f.h * 0.52, 300, alpha=k)
    lion_cub(f, f.w * 0.70, f.h * 0.52, 300, alpha=k * 0.9, flip=True)
    f.pin((f.w * 0.30, f.h * 0.76), "HOMOTHERIUM CUB", alpha=k)
    f.pin((f.w * 0.70, f.h * 0.76), "LION CUB, SAME AGE", alpha=k)
    f.centred(f.h * 0.16, "SAMPLED AGAINST A LION CUB", size=32, fill=GREY, alpha=k)


def draw_preserved(f: Frame, t0, t1, t):
    k = window(t, t0, t1, 0.3)
    if k <= 0:
        return
    f.water(t, dark=0.85)
    f.centred(f.h * 0.20, "WHAT A SKELETON CANNOT SHOW", size=36, fill=GREY, alpha=k)
    items = ["SMALLER EARS", "POWERFUL NECK", "BROADER FRONT PAWS"]
    for i, s in enumerate(items):
        a = window(t, t0 + i * 0.55, t1, 0.22)
        y = f.h * 0.36 + i * 0.16 * f.h
        if a > 0:
            # tick first, then the words — the checklist reveal from the video
            f.d.line([(f.w * 0.24, y + 10), (f.w * 0.26, y + 20), (f.w * 0.30, y - 2)],
                     fill=TEAL + (int(240 * a),), width=5)
            f.text((f.w * 0.34, y), s, size=38, fill=WHITE, alpha=a)


def draw_incomplete(f: Frame, t0, t1, t):
    k = window(t, t0, t1, 0.3)
    if k <= 0:
        return
    f.water(t, dark=0.9)
    f.centred(f.h * 0.30, "THE MUMMY IS INCOMPLETE", size=44, fill=WHITE, alpha=k)
    # a partial outline: head and chest present, the rest dashed away
    cat_nibble(f, f.w * 0.44, f.h * 0.60, 280, alpha=k * 0.75)
    for i in range(14):
        x = f.w * 0.60 + i * 16
        if (i % 2) == 0:
            f.d.rectangle([x, f.h * 0.55, x + 9, f.h * 0.57], fill=GREY + (int(160 * k),))
    f.pin((f.w * 0.72, f.h * 0.72), "HIND LIMBS INCOMPLETE", alpha=k * 0.9, size=20)


def draw_not_resurrected(f: Frame, t0, t1, t):
    k = window(t, t0, t1, 0.3)
    if k <= 0:
        return
    f.water(t, dark=0.9)
    f.stamp(f.h * 0.40, "NOT A RESURRECTED PREDATOR", t0 + 0.15, t, size=40, colour=ACCENT)


def draw_closing(f: Frame, t0, t1, t):
    k = window(t, t0, t1, 0.5)
    if k <= 0:
        return
    f.water(t, dark=0.8)
    cat_nibble(f, f.w * 0.5, f.h * 0.50, 300, alpha=k * 0.9)
    f.centred(f.h * 0.74, "A TINY SURVIVOR OF DEEP TIME", size=38, fill=WHITE, alpha=k)
    f.centred(f.h * 0.82, "EXTINCT LIFE", size=26, fill=GOLD, alpha=k)


# ---------------------------------------------------------------------------
def parse_srt(path: Path):
    txt = path.read_text(encoding="utf-8", errors="replace").replace("\r", "")
    out = []
    for block in re.split(r"\n\s*\n", txt.strip()):
        lines = [l for l in block.split("\n") if l.strip()]
        if len(lines) < 2:
            continue
        m = re.search(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", block)
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        start = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        end = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        out.append((start, end))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--srt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--w", type=int, default=1280)
    ap.add_argument("--h", type=int, default=720)
    ap.add_argument("--duration", type=float, default=None)
    ap.add_argument("--frames", default=None, help="lo:hi, for a shard")
    ap.add_argument("--still", type=float, default=None, help="render one second, for checking")
    args = ap.parse_args()

    cues = parse_srt(Path(args.srt))
    if not cues:
        sys.exit(f"no cues parsed from {args.srt}")
    beats = build_beats(cues)
    duration = args.duration or (cues[-1][1] + 2.0)
    total = int(duration * args.fps)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.still is not None:
        f = Frame(args.w, args.h)
        f.water(args.still)
        for name, s, e, fn in beats:
            if s - 0.5 <= args.still <= e + 0.5:
                fn(f, s, e, args.still)
        p = out / f"still-{args.still:06.2f}.png"
        f.im.save(p)
        print(p)
        return 0

    lo, hi = 0, total
    if args.frames:
        a, b = args.frames.split(":")
        lo, hi = int(a), int(b)

    for i in range(lo, min(hi, total)):
        t = i / args.fps
        f = Frame(args.w, args.h)
        f.water(t)
        for name, s, e, fn in beats:
            if s - 0.6 <= t <= e + 0.6:
                fn(f, s, e, t)
        f.im.save(out / f"f_{i:05d}.png")
        if i % 60 == 0:
            print(f"frame {i}/{total}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
