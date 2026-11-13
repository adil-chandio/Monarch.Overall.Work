#!/usr/bin/env python3
"""Livyatan — "The Whale That Fought Megalodon". Flat-vector documentary short.

Built to match the reference video's *style*, which was measured frame by frame in
docs/research/competitor-apexmorph/. That style is not 3D and it is not simple:
every shot has depth haze, volumetric god-rays, floating matter, a slowly drifting
subject, a labelled call-out, and a flat-vector animal that is identifiable at
400 px because it is one continuous bezier contour — not a stack of circles.

The five things this file reproduces from the reference, in order of how much they
matter to the look:

  1. **Depth-aware water.** A vertical gradient plus soft god-ray shafts drawn with
     additive blending, plus three parallax layers of floating matter. Flat colour
     alone reads as a PowerPoint slide; the haze is what makes it read as water.
  2. **Subjects that drift, never sit still.** Every animal moves at 6-18 px/s with
     a slow vertical bob, and is mirrored before being drawn so motion reads.
  3. **Label boxes, not bare text.** A dark rounded plate with a soft border, exactly
     like `BALEEN — LIKE A GIANT SIEVE` in the reference.
  4. **Gold measurement bars.** `~5.5 M` sits on a gold rule. Numbers are gold,
     labels are white, and nothing is centred by eye.
  5. **Sonar arcs.** Thin radius-chasing arcs propagate away from a moving subject —
     the sound-made-visible device.

Everything is a pure function of `t`; no keyframe store. 3000 frames render in
minutes on one core, which is the point.

Usage:
    python scripts/livyatan-film.py --out /tmp/liv --fps 30
    python scripts/livyatan-film.py --out /tmp/liv --still 12.5
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:  # pragma: no cover
    sys.exit("needs Pillow")

import scripts.lib.creatures as C
from scripts.lib.bezier import draw_path, stroke_path

W, H = 1280, 720
FPS_DEFAULT = 30

# -- palette ----------------------------------------------------------------
DEEP_TOP = (16, 46, 60)
DEEP_BOT = (5, 16, 24)
INK = (16, 18, 22)
WHALE = (26, 28, 34)
SHARK = (52, 58, 66)
BONE = (236, 232, 222)
GOLD = (226, 180, 60)
TEAL = (108, 190, 200)
WHITE = (245, 246, 244)

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
_FC = {}


def font(size: int):
    if size in _FC:
        return _FC[size]
    for p in FONT_PATHS:
        if Path(p).exists():
            _FC[size] = ImageFont.truetype(p, size)
            return _FC[size]
    _FC[size] = ImageFont.load_default()
    return _FC[size]


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


def win(t, start, end, fade=0.35):
    span = max(0.05, end - start)
    fade = min(fade, span * 0.3)
    if t < start - fade or t > end + fade:
        return 0.0
    return min(smoothstep(start - fade, start, t), 1 - smoothstep(end, end + fade, t))


# ---------------------------------------------------------------------------
# The water. This is the single biggest difference between "vector graphics" and
# "underwater footage", so it is built in four separate passes.
# ---------------------------------------------------------------------------
_RAY_CACHE: dict = {}


def water(f, t, depth=1.0, ray_strength=1.0):
    """Vertical gradient + god-rays + three matter layers.

    Gradient first: 720 line draws is cheap and gives an exactly flat wash with no
    banding, unlike a resized 2x2 image.
    """
    top = tuple(int(c * lerp(1.0, 0.55, 1 - depth)) for c in DEEP_TOP)
    bot = tuple(int(c * lerp(1.0, 0.45, 1 - depth)) for c in DEEP_BOT)
    for y in range(H):
        k = y / H
        f.d.line([(0, y), (W, y)],
                 fill=(int(lerp(top[0], bot[0], k)),
                       int(lerp(top[1], bot[1], k)),
                       int(lerp(top[2], bot[2], k))))

    # god-rays: a cached mask of soft wedges, scrolled horizontally so they appear
    # to move with the water rather than with the camera.
    key = (int(depth * 10), int(ray_strength * 10))
    if key not in _RAY_CACHE:
        ray = Image.new("L", (W, H), 0)
        rd = ImageDraw.Draw(ray)
        for i in range(7):
            x = int(W * (0.06 + i * 0.145))
            wdt = 26 + (i * 37) % 60
            slant = 90 + (i * 23) % 70
            rd.polygon([(x, -40), (x + wdt, -40),
                        (x + wdt + slant, H + 40), (x + slant, H + 40)],
                       fill=int(26 * ray_strength))
        ray = ray.filter(ImageFilter.GaussianBlur(26))
        _RAY_CACHE[key] = ray
    rays = _RAY_CACHE[key]
    off = int((t * 9) % W)
    layer = Image.new("RGB", (W, H), (150, 205, 215))
    f.im.paste(layer, (0, 0), rays.rotate(0))  # paste twice, wrapped, for a seamless scroll
    f.im.paste(layer, (off - W, 0), rays)
    f.im.paste(layer, (off, 0), rays)

    # matter: three parallax layers. Near layer is bigger and faster, far layer is
    # a fine dust that barely moves. This is what gives the frame depth.
    for layer_id, (count, rmin, rmax, speed, alpha) in enumerate(
        [(70, 1, 2, 26, 34), (46, 2, 4, 15, 46), (22, 3, 7, 8, 40)]
    ):
        for i in range(count):
            seed = (i * 2654435761 + layer_id * 40503) % 1000003
            x = (seed % W + int(math.sin(t * 0.3 + i) * 12)) % W
            y = ((seed // 977) % H - t * speed) % H
            r = rmin + (i % (rmax - rmin + 1))
            f.d.ellipse([x - r, y - r, x + r, y + r],
                        fill=(198, 226, 232, alpha))


# ---------------------------------------------------------------------------
# Devices
# ---------------------------------------------------------------------------
def label_box(f, xy, text, alpha=1.0, size=22, anchor="la"):
    """Device: the dark rounded plate behind a label, as in `BALEEN — LIKE A GIANT
    SIEVE`. Bare text floats; a plate looks authored."""
    if alpha <= 0:
        return
    ft = font(size)
    bb = f.d.textbbox((0, 0), text, font=ft)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    padx, pady = 16, 9
    x, y = xy
    if anchor == "ma":
        x -= tw / 2 + padx
    box = [x, y, x + tw + padx * 2, y + th + pady * 2]
    f.d.rounded_rectangle(box, radius=6,
                          fill=(6, 10, 14, int(190 * alpha)),
                          outline=(120, 150, 160, int(90 * alpha)), width=1)
    f.d.text((x + padx, y + pady - 2), text, font=ft,
             fill=(240, 242, 238, int(250 * alpha)))


def gold_rule(f, x0, x1, y, text, alpha=1.0, size=30):
    """Device: the measurement bar. `~5.5 M` sits on a gold line, never floating."""
    if alpha <= 0:
        return
    f.d.line([(x0, y), (x1, y)], fill=GOLD + (int(220 * alpha),), width=2)
    for xx in (x0, x1):
        f.d.line([(xx, y - 8), (xx, y + 8)], fill=GOLD + (int(220 * alpha),), width=2)
    ft = font(size)
    bb = f.d.textbbox((0, 0), text, font=ft)
    tw = bb[2] - bb[0]
    f.d.text(((x0 + x1) / 2 - tw / 2, y - 46), text, font=ft,
             fill=GOLD + (int(250 * alpha),))


def sonar(f, cx, cy, t, period=2.2, n=3, radius=340, alpha=1.0):
    """Device: sound made visible — radius-chasing arcs, the reference's sonar."""
    for i in range(n):
        ph = ((t / period) + i / n) % 1.0
        r = 40 + ease_out(ph) * radius
        a = int(120 * alpha * (1 - ph) ** 1.4)
        if a <= 0:
            continue
        f.d.arc([cx - r, cy - r * 0.42, cx + r, cy + r * 0.42],
                start=200, end=340, fill=TEAL + (a,), width=2)
        f.d.arc([cx - r, cy - r * 0.42, cx + r, cy + r * 0.42],
                start=20, end=160, fill=TEAL + (int(a * 0.6),), width=2)


def counter(f, cx, cy, value, size=110, colour=GOLD, label=None, alpha=1.0):
    ft = font(size)
    s = str(value)
    bb = f.d.textbbox((0, 0), s, font=ft)
    tw = bb[2] - bb[0]
    f.d.text((cx - tw / 2 + 3, cy - size * 0.5 + 4), s, font=ft, fill=(0, 0, 0, int(120 * alpha)))
    f.d.text((cx - tw / 2, cy - size * 0.5), s, font=ft, fill=colour + (int(255 * alpha),))
    if label:
        lf = font(max(16, int(size * 0.22)))
        bb = f.d.textbbox((0, 0), label, font=lf)
        f.d.text((cx - (bb[2] - bb[0]) / 2, cy + size * 0.52), label, font=lf,
                 fill=(214, 222, 224, int(235 * alpha)))


def stamp(f, cy, text, t_in, t, size=46, colour=(198, 58, 46), alpha=1.0):
    p = ease_out((t - t_in) / 0.22)
    if p <= 0 or alpha <= 0:
        return
    ft = font(size)
    bb = f.d.textbbox((0, 0), text, font=ft)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    padx, pady = 26, 15
    bw, bh = tw + padx * 2, th + pady * 2
    pad = 14
    card = Image.new("RGBA", (bw + pad * 2, bh + pad * 2), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rectangle([pad, pad, pad + bw, pad + bh], fill=tuple(colour) + (235,))
    cd.rectangle([pad, pad, pad + bw, pad + bh], outline=(255, 255, 255, 215), width=3)
    cd.text((pad + bw / 2, pad + bh / 2), text, font=ft, fill=(255, 255, 255, 255), anchor="mm")
    sc = 0.88 + 0.12 * p
    card = card.resize((max(1, int(card.width * sc)), max(1, int(card.height * sc))), Image.LANCZOS)
    card = card.rotate(-2.0, expand=True, resample=Image.BICUBIC)
    a = int(255 * p * alpha)
    if a < 255:
        card.putalpha(card.split()[3].point(lambda v: int(v * a / 255)))
    f.im.paste(card, (W // 2 - card.width // 2, int(cy - card.height / 2)), card)


# ---------------------------------------------------------------------------
# The film. Each beat is (start, end, drawer). Timing follows the narration.
# ---------------------------------------------------------------------------
def beats():
    # Timed against the generated narration (65.81 s total):
    #   "Meet Livyatan..."              0.0 -> 20.9
    #   "Megalodon had rows..."        20.9 -> 39.5
    #   "Megalodon teeth have been..." 39.5 -> 65.8
    return [
        (0.0, 3.2, b_hook),
        (3.2, 7.0, b_sperm),
        (7.0, 11.2, b_two_giants),
        (11.2, 14.6, b_nine_million),
        (14.6, 18.0, b_head),
        (18.0, 21.2, b_teeth),
        (21.2, 26.0, b_four_dozen),
        (26.0, 30.4, b_not_biggest),
        (30.4, 35.0, b_blue_whale),
        (35.0, 39.6, b_real_question),
        (39.6, 45.0, b_bite_marks),
        (45.0, 51.0, b_not_complete),
        (51.0, 56.0, b_no_fight),
        (56.0, 60.4, b_shared_water),
        (60.4, 64.2, b_not_monster),
        (64.2, 67.5, b_title_close),
    ]


def _subject(f, shape_fn, x, y, w, h, t, flip=False, colour=None, speed=12.0, bob=5.0, alpha=1.0):
    """Draw an animal that drifts. The bob keeps even a 'held' shot alive, which is
    what the reference does in every single shot."""
    xx = x + math.sin(t * 0.4) * speed
    yy = y + math.sin(t * 0.9 + 1.1) * bob
    shape_fn(f, xx, yy, w, h, flip=flip, colour=colour, alpha=alpha)


def _whale(f, x, y, w, h, flip=False, colour=None, alpha=1.0):
    col = tuple(colour or WHALE) + (int(255 * alpha),)
    C.draw_path(f.d, C.LIVYATAN, (x, y, w, h), col, flip=flip, segs=30)
    stroke_path(f.d, C.LIVYATAN_JAW, (x, y, w, h), (8, 10, 14, int(210 * alpha)),
                width=max(2, int(h * 0.028)), flip=flip, segs=24)
    ex, ey = C.scale_point((x, y, w, h), C.LIVYATAN_EYE)
    if flip:
        ex = x + w - (ex - x)
    r = max(2.0, h * 0.032)
    f.d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(240, 238, 232, int(255 * alpha)))


def _meg(f, x, y, w, h, flip=False, colour=None, alpha=1.0):
    col = tuple(colour or SHARK) + (int(255 * alpha),)
    fin = tuple(max(0, c - 10) for c in (colour or SHARK)) + (int(255 * alpha),)
    C.draw_path(f.d, C.MEGALODON_FIN, (x, y, w, h), fin, flip=flip, segs=24)
    C.draw_path(f.d, C.MEGALODON, (x, y, w, h), col, flip=flip, segs=30)
    ex, ey = C.scale_point((x, y, w, h), C.MEGALODON_EYE)
    if flip:
        ex = x + w - (ex - x)
    r = max(2.0, h * 0.026)
    f.d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(240, 238, 232, int(255 * alpha)))


def _orca(f, x, y, w, h, flip=False, alpha=1.0):
    C.draw_path(f.d, C.ORCA, (x, y, w, h), (18, 20, 24, int(255 * alpha)), flip=flip, segs=30)
    C.draw_path(f.d, C.ORCA_PATCH, (x, y, w, h), BONE + (int(250 * alpha),), flip=flip, segs=26)
    C.draw_path(f.d, C.ORCA_EYEPATCH, (x, y, w, h), BONE + (int(250 * alpha),), flip=flip, segs=20)


# -- beats -------------------------------------------------------------------
def b_hook(f, t, t0, t1):
    k = win(t, t0, t1, 0.5)
    if k <= 0:
        return
    water(f, t, depth=0.85)
    # two subjects in one frame at true relative size, like the reference's
    # orca / blue-whale shot — depth comes from one being hazier than the other
    _subject(f, lambda ff, x, y, w, h, flip=False, colour=None, alpha=1.0: _meg(
        ff, x, y, w, h, flip=True, colour=(70, 78, 86), alpha=0.55 * k), 640, 300, 470, 190, t, speed=6)
    _subject(f, lambda ff, x, y, w, h, flip=False, colour=None, alpha=1.0: _whale(
        ff, x, y, w, h, flip=False, colour=(20, 22, 27), alpha=k), 300, 380, 700, 300, t, speed=10)
    sonar(f, 760, 360, t, alpha=k * 0.7)


def b_sperm(f, t, t0, t1):
    k = win(t, t0, t1, 0.45)
    if k <= 0:
        return
    water(f, t, depth=0.75)
    _subject(f, lambda ff, x, y, w, h, flip=False, colour=None, alpha=1.0: _whale(
        ff, x, y, w, h, colour=(22, 24, 29), alpha=k), 250, 250, 820, 340, t, speed=14)
    label_box(f, (70, 620), "LIVYATAN — A RAPTORIAL SPERM WHALE", alpha=k, size=24)


def b_two_giants(f, t, t0, t1):
    k = win(t, t0, t1, 0.45)
    if k <= 0:
        return
    water(f, t, depth=0.9)
    _subject(f, lambda ff, x, y, w, h, flip=False, colour=None, alpha=1.0: _whale(
        ff, x, y, w, h, colour=(24, 26, 31), alpha=k), 120, 200, 640, 260, t, speed=9)
    _subject(f, lambda ff, x, y, w, h, flip=False, colour=None, alpha=1.0: _meg(
        ff, x, y, w, h, flip=True, colour=(62, 70, 78), alpha=k), 760, 420, 430, 175, t, speed=13)
    label_box(f, (760, 330), "MEGALODON", alpha=k * 0.95, size=22)
    label_box(f, (120, 150), "LIVYATAN", alpha=k * 0.95, size=22)


def b_nine_million(f, t, t0, t1):
    k = win(t, t0, t1, 0.4)
    if k <= 0:
        return
    water(f, t, depth=0.95, ray_strength=0.7)
    p = ease_in_out((t - t0) / max(0.4, (t1 - t0) * 0.85))
    counter(f, W // 2, H * 0.42, f"{lerp(0, 9, p):.1f}", size=132,
            label="MILLION YEARS AGO", alpha=k)


def b_head(f, t, t0, t1):
    k = win(t, t0, t1, 0.4)
    if k <= 0:
        return
    water(f, t, depth=0.7)
    # the head fills the frame — the reference's baleen close-up does the same
    _whale(f, -120, 120, 1300, 540, colour=(20, 22, 27), alpha=k)
    label_box(f, (70, 96), "ONE HEAD, ONE WEAPON", alpha=k, size=24)


def b_teeth(f, t, t0, t1):
    k = win(t, t0, t1, 0.4)
    if k <= 0:
        return
    water(f, t, depth=1.0, ray_strength=0.4)
    # jaw band across frame, teeth as repeated path shapes along it
    f.d.polygon([(0, 420), (W, 380), (W, 470), (0, 520)], fill=(24, 26, 31, int(255 * k)))
    n = 13
    for i in range(n):
        x = 40 + i * (W - 80) / (n - 1)
        y = 470 - i * 2.4
        th = 150 + (i * 37) % 60
        C.draw_path(f.d, C.TOOTH, (x - 26, y, 52, th), (238, 234, 224, int(252 * k)), segs=18)
    p = ease_in_out((t - t0) / max(0.4, (t1 - t0) * 0.85))
    counter(f, W // 2, H * 0.20, f"{int(lerp(0, 40, p))}", size=118, label="CM EACH", alpha=k)


def b_four_dozen(f, t, t0, t1):
    k = win(t, t0, t1, 0.4)
    if k <= 0:
        return
    water(f, t, depth=0.85, ray_strength=0.6)
    _whale(f, 60, 300, 560, 230, colour=(22, 24, 29), alpha=k)
    _meg(f, 700, 330, 500, 205, flip=True, colour=(58, 66, 74), alpha=k)
    label_box(f, (60, 560), "FOUR DOZEN TEETH", alpha=k, size=24)
    stamp(f, 150, "NOT ROWS — SPEARS", t0 + 0.3, t, size=38, alpha=k)


def b_not_biggest(f, t, t0, t1):
    k = win(t, t0, t1, 0.4)
    if k <= 0:
        return
    water(f, t, depth=0.9)
    _whale(f, 120, 240, 700, 300, colour=(22, 24, 29), alpha=k)
    a = win(t, t0 + 0.5, t1, 0.3)
    gold_rule(f, 160, 800, 190, "~17 M", alpha=a * k, size=34)


def b_blue_whale(f, t, t0, t1):
    k = win(t, t0, t1, 0.4)
    if k <= 0:
        return
    water(f, t, depth=0.8)
    # a blue whale is the same silhouette scaled up — the honest way to show "twice"
    small = (240, 430, 520, 220)
    big = (170, 210, 1120, 470)
    _whale(f, *small, colour=(70, 78, 88), alpha=k * 0.6)
    _whale(f, *big, colour=(20, 22, 27), alpha=k * 0.35)
    label_box(f, (240, 470), "LIVYATAN · 17 M", alpha=k, size=22)
    label_box(f, (170, 170), "BLUE WHALE · 30 M+", alpha=k, size=22)


def b_real_question(f, t, t0, t1):
    k = win(t, t0, t1, 0.5)
    if k <= 0:
        return
    water(f, t, depth=1.0, ray_strength=0.5)
    dark = Image.new("RGBA", (W, H), (0, 0, 0, int(150 * k)))
    f.im.paste(Image.alpha_composite(f.im.convert("RGBA"), dark).convert("RGB"), (0, 0))
    ft = font(50)
    s = "WHAT WAS IT HUNTING?"
    bb = f.d.textbbox((0, 0), s, font=ft)
    f.d.text((W / 2 - (bb[2] - bb[0]) / 2 + 3, H * 0.40 + 4), s, font=ft, fill=(0, 0, 0, int(120 * k)))
    f.d.text((W / 2 - (bb[2] - bb[0]) / 2, H * 0.40), s, font=ft, fill=WHITE + (int(250 * k),))
    a = win(t, t0 + 0.9, t1, 0.3)
    label_box(f, (W // 2 - 190, H * 0.58), "THE ANSWER IS NOT SIZE", alpha=a * k, size=26)


def b_bite_marks(f, t, t0, t1):
    k = win(t, t0, t1, 0.4)
    if k <= 0:
        return
    water(f, t, depth=0.95, ray_strength=0.5)
    _meg(f, 180, 260, 900, 370, colour=(52, 58, 66), alpha=k)
    for i in range(9):
        a = win(t, t0 + 0.35 + i * 0.13, t1, 0.2) * k
        if a <= 0:
            continue
        x = 330 + i * 62
        y = 470 + (i % 3) * 7
        f.d.arc([x - 26, y - 18, x + 26, y + 18], start=200, end=340,
                fill=(220, 96, 78, int(230 * a)), width=5)
    label_box(f, (150, 130), "TOOTH DAMAGE ON MEGALODON FOSSILS", alpha=k, size=22)


def b_not_complete(f, t, t0, t1):
    k = win(t, t0, t1, 0.4)
    if k <= 0:
        return
    water(f, t, depth=1.0, ray_strength=0.45)
    _whale(f, 90, 260, 560, 230, colour=(26, 28, 34), alpha=k * 0.85)
    _meg(f, 700, 300, 500, 205, flip=True, colour=(52, 58, 66), alpha=k * 0.85)
    # the gap between them, drawn as an explicit absence
    for i in range(11):
        x = 620 + i * 7
        if i % 2 == 0:
            f.d.rectangle([x, 400, x + 4, 404], fill=(140, 150, 156, int(160 * k)))
    stamp(f, 560, "NO ONE HAS FOUND THEM TOGETHER", t0 + 0.25, t, size=32, alpha=k)


def b_no_fight(f, t, t0, t1):
    k = win(t, t0, t1, 0.45)
    if k <= 0:
        return
    water(f, t, depth=0.9, ray_strength=0.6)
    ft = font(46)
    s = "WE CANNOT SAY THEY FOUGHT"
    bb = f.d.textbbox((0, 0), s, font=ft)
    f.d.text((W / 2 - (bb[2] - bb[0]) / 2, H * 0.30), s, font=ft, fill=WHITE + (int(245 * k),))
    a = win(t, t0 + 0.8, t1, 0.3)
    ft2 = font(34)
    s2 = "WE CAN SAY THEY SHARED THE WATER"
    bb2 = f.d.textbbox((0, 0), s2, font=ft2)
    f.d.text((W / 2 - (bb2[2] - bb2[0]) / 2, H * 0.44), s2, font=ft2,
             fill=GOLD + (int(240 * a * k),))


def b_shared_water(f, t, t0, t1):
    k = win(t, t0, t1, 0.45)
    if k <= 0:
        return
    water(f, t, depth=0.7)
    _whale(f, 90, 210, 640, 265, colour=(22, 24, 29), alpha=k)
    _meg(f, 700, 430, 470, 190, flip=True, colour=(56, 64, 72), alpha=k)
    sonar(f, 400, 350, t, alpha=k * 0.8)
    label_box(f, (90, 540), "A FEW MILLION YEARS · THE SAME OCEAN", alpha=k, size=22)


def b_not_monster(f, t, t0, t1):
    k = win(t, t0, t1, 0.45)
    if k <= 0:
        return
    water(f, t, depth=1.0, ray_strength=0.4)
    ft = font(44)
    s = "NOT A MONSTER"
    bb = f.d.textbbox((0, 0), s, font=ft)
    f.d.text((W / 2 - (bb[2] - bb[0]) / 2, H * 0.34), s, font=ft, fill=WHITE + (int(245 * k),))
    a = win(t, t0 + 0.7, t1, 0.3)
    label_box(f, (W // 2 - 240, H * 0.50), "AN ANIMAL THAT WAS REALLY THERE", alpha=a * k, size=28)


def b_title_close(f, t, t0, t1):
    k = win(t, t0, t1, 0.55)
    if k <= 0:
        return
    water(f, t, depth=0.65)
    _whale(f, 190, 300, 900, 370, colour=(20, 22, 26), alpha=k * 0.9)
    ft = font(58)
    s = "LIVYATAN"
    bb = f.d.textbbox((0, 0), s, font=ft)
    f.d.text((W / 2 - (bb[2] - bb[0]) / 2 + 3, H * 0.14 + 4), s, font=ft, fill=(0, 0, 0, int(130 * k)))
    f.d.text((W / 2 - (bb[2] - bb[0]) / 2, H * 0.14), s, font=ft, fill=WHITE + (int(250 * k),))
    ft2 = font(24)
    s2 = "EXTINCT LIFE"
    bb2 = f.d.textbbox((0, 0), s2, font=ft2)
    f.d.text((W / 2 - (bb2[2] - bb2[0]) / 2, H * 0.26), s2, font=ft2, fill=GOLD + (int(240 * k),))


# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=FPS_DEFAULT)
    ap.add_argument("--still", type=float, default=None)
    ap.add_argument("--frames", default=None)
    ap.add_argument("--duration", type=float, default=88.0)
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    bs = beats()
    total = int(a.duration * a.fps)

    def render(t):
        f = type("F", (), {})()
        f.im = Image.new("RGB", (W, H), DEEP_TOP)
        f.d = ImageDraw.Draw(f.im, "RGBA")
        f.w, f.h = W, H
        for (s, e, fn) in bs:
            if s - 0.7 <= t <= e + 0.7:
                fn(f, t, s, e)
        return f.im

    if a.still is not None:
        p = out / f"still-{a.still:06.2f}.png"
        render(a.still).save(p)
        print(p)
        return 0

    lo, hi = 0, total
    if a.frames:
        x, y = a.frames.split(":")
        lo, hi = int(x), int(y)
    for i in range(lo, min(hi, total)):
        render(i / a.fps).save(out / f"f_{i:05d}.png")
        if i % 120 == 0:
            print(f"frame {i}/{total}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
