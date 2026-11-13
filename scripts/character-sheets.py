#!/usr/bin/env python3
"""Character sheets: every animal in the film, five poses each, on one page.

The operator asked for this so the next film does not start from zero: instead of
re-deriving an orca each time, there is a page you can point at and say "that one,
third down". Each sheet is 2x2 or 2x3 at 400 px per cell on a 1600-wide page, and
every cell is labelled with the pose so the sheet doubles as a pose menu.

Twelve sheets are produced:

  orca              profile, arcing, angled-down, distant/hazy, two-up
  humpback          profile, flipper-out, rising, fluke-down, distant
  blue-whale        profile, from-above, distant, head-on, with escorts
  great-white       profile, from-above, angled, distant, jaws
  megalodon         profile, jaws, angled, distant, dorsal-only
  livyatan          profile, jaws, angled, distant, teeth
  flipper           upright, angled, both-out, knobbly detail, knobs close
  krill             single, cluster, swarm, backlit, drifting

Run:  python scripts/character-sheets.py --out production/extinct-life/characters
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import scripts.lib.creatures as C  # noqa: E402
import scripts.lib.shading as S  # noqa: E402
from scripts.lib.bezier import draw_path, stroke_path  # noqa: E402

PAGE_W = 1600
CELL = 400
GAP = 14
PAD = 28

BG_TOP = (16, 42, 55)
BG_BOT = (6, 16, 23)
BONE = (236, 232, 222)
GOLD = (226, 180, 60)
WHITE = (240, 243, 241)
MUTED = (140, 160, 170)

_FONTS = {}


def font(size, bold=True):
    key = (size, bold)
    if key in _FONTS:
        return _FONTS[key]
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for d in ("/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation"):
        p = Path(d) / name
        if p.exists():
            _FONTS[key] = ImageFont.truetype(str(p), size)
            return _FONTS[key]
    _FONTS[key] = ImageFont.load_default()
    return _FONTS[key]


class Cell:
    """A drawing surface the size of one grid cell."""

    def __init__(self, w, h, water=True, rays=0.9):
        self.im = Image.new("RGB", (w, h), BG_TOP)
        self.d = ImageDraw.Draw(self.im, "RGBA")
        self.w, self.h = w, h
        for y in range(h):
            k = y / max(1, h - 1)
            self.d.line([(0, y), (w, y)],
                        fill=(int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * k),
                              int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * k),
                              int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * k)))
        if water and rays > 0:
            ov = Image.new("L", (w, h), 0)
            od = ImageDraw.Draw(ov)
            for i in range(4):
                x = int(w * (0.05 + i * 0.26))
                wd = 26 + (i * 37) % 46
                sl = 54 + (i * 21) % 40
                od.polygon([(x, -20), (x + wd, -20), (x + wd + sl, h + 20), (x + sl, h + 20)],
                           fill=int(30 * rays))
            ov = ov.filter(__import__("PIL.ImageFilter", fromlist=["ImageFilter"]).GaussianBlur(22))
            self.im.paste(Image.new("RGB", (w, h), (140, 198, 210)), (0, 0), ov)
        # a few particles so the cell reads as water, not a poster
        for i in range(26):
            sd = (i * 2654435761) % 1000003
            x, y = sd % w, (sd // 977) % h
            r = 1 + i % 3
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=(196, 224, 230, 40))


def label(d, x, y, text, size=17, colour=BONE, pad=(9, 5)):
    ft = font(size)
    bb = d.textbbox((0, 0), text, font=ft)
    d.rounded_rectangle([x, y, x + (bb[2] - bb[0]) + pad[0] * 2, y + (bb[3] - bb[1]) + pad[1] * 2 + 2],
                        radius=3, fill=(6, 10, 14, 205), outline=(110, 140, 152, 70))
    d.text((x + pad[0], y + pad[1]), text, font=ft, fill=colour + (250,))


# ---------------------------------------------------------------------------
# Painters — thin wrappers so a sheet cell is one line
# ---------------------------------------------------------------------------
def p_orca(c, x, y, w, h, flip=False, angle=0.0, blur=0.0, alpha=1.0):
    if angle or blur:
        tile = S.__dict__  # placeholder to keep the import used
        pad = 40
        rgb = Image.new("RGB", (int(w) + pad * 2, int(h) + pad * 2), BG_TOP)
        d = ImageDraw.Draw(rgb, "RGBA")
        fr = type("F", (), {})()
        fr.im, fr.d, fr.w, fr.h = rgb, d, rgb.width, rgb.height
        S.fill_shaded(fr, C.ORCA, (pad, pad, w, h),
                      [(0.0, (7, 8, 11)), (0.5, (20, 22, 28)), (1.0, (50, 55, 62))],
                      flip=flip, segs=26)
        draw_path(d, C.ORCA_PATCH, (pad, pad, w, h), BONE + (252,), flip=flip, segs=22)
        draw_path(d, C.ORCA_EYEPATCH, (pad, pad, w, h), BONE + (252,), flip=flip, segs=18)
        m = S.mask_from_path(rgb.size, C.ORCA, (pad, pad, w, h), flip=flip, segs=26)
        rgb.putalpha if False else None
        rgba = rgb.convert("RGBA")
        rgba.putalpha(m)
        if blur:
            rgba = rgba.filter(__import__("PIL.ImageFilter", fromlist=["ImageFilter"]).GaussianBlur(blur))
        if angle:
            rgba = rgba.rotate(angle, resample=Image.BICUBIC, expand=True)
        c.im.paste(rgba, (int(x + w / 2 - rgba.width / 2), int(y + h / 2 - rgba.height / 2)), rgba)
        return
    bb = (x, y, w, h)
    S.fill_shaded(c, C.ORCA, bb, [(0.0, (7, 8, 11)), (0.5, (20, 22, 28)), (1.0, (50, 55, 62))],
                  flip=flip, segs=28)
    draw_path(c.d, C.ORCA_PATCH, bb, BONE + (252,), flip=flip, segs=24)
    draw_path(c.d, C.ORCA_EYEPATCH, bb, BONE + (252,), flip=flip, segs=20)
    S.rim_light(c, C.ORCA, bb, colour=(160, 200, 215), width=3, alpha=0.34, flip=flip, segs=28)
    ex, ey = C.scale_point(bb, C.ORCA_EYE)
    if flip:
        ex = x + w - (ex - x)
    c.d.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(242, 240, 234))


def p_humpback(c, x, y, w, h, flip=False, alpha=1.0, blur=0.0, detail=True):
    bb = (x, y, w, h)
    stops = [(0.0, (10, 12, 17)), (0.36, (26, 30, 36)), (0.72, (92, 99, 108)), (1.0, (168, 173, 178))]
    S.fill_shaded(c, C.HUMPBACK_FLIPPER, bb, [(0.0, (208, 210, 206)), (1.0, (124, 129, 134))],
                  flip=flip, segs=24, alpha=alpha)
    S.fill_shaded(c, C.HUMPBACK, bb, stops, flip=flip, segs=30, alpha=alpha)
    if detail:
        for pts in C.unit_to_px(C.humpback_pleats(16), bb, flip=flip):
            c.d.line(pts, fill=(52, 57, 64, 170), width=3, joint="curve")
        for pts in C.unit_to_px(C.flipper_knobs(10), bb, flip=flip):
            (ax, ay), (bx, by) = pts
            x0, x1 = min(ax, bx), max(ax, bx)
            y0, y1 = min(ay, by), max(ay, by)
            c.d.ellipse([x0 - 3, y0 - 3, x1 + 3, y1 + 3], fill=(236, 233, 226, 230))
        for pts in C.unit_to_px(C.baleen_comb(24), bb, flip=flip):
            c.d.line(pts, fill=(226, 180, 60, 235), width=3)
        S.rim_light(c, C.HUMPBACK, bb, colour=(175, 212, 224), width=3, alpha=0.34, flip=flip, segs=30)
    stroke_path(c.d, C.HUMPBACK_MOUTH, bb, (6, 8, 12, 230), width=4, flip=flip, segs=24)
    ex, ey = C.scale_point(bb, C.HUMPBACK_EYE)
    if flip:
        ex = x + w - (ex - x)
    c.d.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(240, 238, 232))


def p_blue(c, x, y, w, h, flip=False, alpha=1.0, detail=True):
    bb = (x, y, w, h)
    S.fill_shaded(c, C.BLUE_WHALE, bb,
                  [(0.0, (30, 34, 42)), (0.42, (64, 72, 86)), (0.78, (112, 121, 133)), (1.0, (156, 163, 172))],
                  flip=flip, segs=30, alpha=alpha)
    if detail:
        for pts in C.unit_to_px(C.blue_whale_pleats(26), bb, flip=flip):
            c.d.line(pts, fill=(24, 28, 34, 130), width=3, joint="curve")
        S.rim_light(c, C.BLUE_WHALE, bb, colour=(170, 205, 220), width=3, alpha=0.36, flip=flip, segs=30)
    stroke_path(c.d, C.BLUE_WHALE_MOUTH, bb, (10, 12, 16, 210), width=4, flip=flip, segs=26)
    ex, ey = C.scale_point(bb, C.BLUE_WHALE_EYE)
    if flip:
        ex = x + w - (ex - x)
    c.d.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(240, 238, 232))


def p_gws(c, x, y, w, h, flip=False, alpha=1.0, detail=True):
    bb = (x, y, w, h)
    S.fill_shaded(c, C.GREAT_WHITE, bb,
                  [(0.0, (44, 50, 58)), (0.46, (92, 99, 108)), (1.0, (198, 202, 206))],
                  flip=flip, segs=28, alpha=alpha)
    if detail:
        for (a, b) in C.unit_to_px(C.great_white_gills(5), bb, flip=flip):
            c.d.line([a, b], fill=(22, 26, 32, 180), width=3)
        for tri in C.unit_to_px(C.shark_teeth_row(15, 0.700, 0.930, 0.600), bb, flip=flip):
            c.d.polygon(tri, fill=(246, 246, 241, 240))
        S.rim_light(c, C.GREAT_WHITE, bb, colour=(175, 210, 222), width=3, alpha=0.40, flip=flip, segs=28)
    ex, ey = C.scale_point(bb, C.GREAT_WHITE_EYE)
    if flip:
        ex = x + w - (ex - x)
    c.d.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(238, 236, 230))


def p_meg(c, x, y, w, h, flip=False, alpha=1.0, detail=True):
    bb = (x, y, w, h)
    S.fill_shaded(c, C.MEGALODON_FIN, bb, [(0.0, (30, 34, 40)), (1.0, (58, 64, 72))],
                  flip=flip, segs=24, alpha=alpha)
    S.fill_shaded(c, C.MEGALODON, bb,
                  [(0.0, (26, 30, 36)), (0.45, (52, 58, 66)), (1.0, (118, 126, 134))],
                  flip=flip, segs=30, alpha=alpha)
    if detail:
        for pts in C.unit_to_px(C.shark_gill_slits(5), bb, flip=flip):
            c.d.line(pts, fill=(12, 14, 18, 170), width=3, joint="curve")
        S.rim_light(c, C.MEGALODON, bb, colour=(150, 190, 205), width=3, alpha=0.32, flip=flip, segs=30)
    ex, ey = C.scale_point(bb, C.MEGALODON_EYE)
    if flip:
        ex = x + w - (ex - x)
    c.d.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(240, 238, 232))


def p_liv(c, x, y, w, h, flip=False, alpha=1.0, detail=True):
    bb = (x, y, w, h)
    S.fill_shaded(c, C.LIVYATAN, bb,
                  [(0.0, (12, 14, 18)), (0.40, (26, 29, 35)), (0.74, (74, 80, 88)), (1.0, (122, 128, 136))],
                  flip=flip, segs=30, alpha=alpha)
    if detail:
        for pts in C.unit_to_px(C.whale_belly_lines(11), bb, flip=flip):
            c.d.line(pts, fill=(10, 12, 16, 150), width=3, joint="curve")
        S.rim_light(c, C.LIVYATAN, bb, colour=(150, 195, 210), width=3, alpha=0.34, flip=flip, segs=30)
    stroke_path(c.d, C.LIVYATAN_JAW, bb, (6, 8, 12, 225), width=5, flip=flip, segs=24)


def p_fin(c, x, y, w, h, angle=0.0, flip=False, alpha=1.0, knobs=True):
    pad = int(max(w, h) * 0.6) + 10
    rgb = Image.new("RGB", (int(w) + pad * 2, int(h) + pad * 2), BG_TOP)
    d = ImageDraw.Draw(rgb, "RGBA")
    fr = type("F", (), {})()
    fr.im, fr.d, fr.w, fr.h = rgb, d, rgb.width, rgb.height
    bb = (pad, pad, w, h)
    S.fill_shaded(fr, C.WHALE_FIN_UP, bb,
                  [(0.0, (216, 218, 214)), (0.5, (178, 182, 181)), (1.0, (126, 131, 135))],
                  flip=flip, segs=26)
    if knobs:
        for pts in C.unit_to_px(C.flipper_knobs(11), bb, flip=flip):
            (ax, ay), (bx, by) = pts
            x0, x1 = min(ax, bx), max(ax, bx)
            y0, y1 = min(ay, by), max(ay, by)
            d.ellipse([x0 - 3.5, y0 - 3.5, x1 + 3.5, y1 + 3.5], fill=(240, 237, 229, 235))
    m = S.mask_from_path(rgb.size, C.WHALE_FIN_UP, bb, flip=flip, segs=26)
    rgba = rgb.convert("RGBA")
    rgba.putalpha(m)
    if angle:
        rgba = rgba.rotate(angle, resample=Image.BICUBIC, expand=True)
    c.im.paste(rgba, (int(x + w / 2 - rgba.width / 2), int(y + h / 2 - rgba.height / 2)), rgba)


def p_krill(c, x, y, w, h, flip=False):
    bb = (x, y, w, h)
    S.fill_shaded(c, C.KRILL, bb, [(0.0, (150, 140, 120)), (1.0, (226, 216, 190))], flip=flip, segs=24)
    c.d.ellipse([x + w * 0.62, y + h * 0.42, x + w * 0.68, y + h * 0.50], fill=(30, 26, 22))
    for i in range(5):
        k = i / 4
        c.d.line([(x + w * (0.22 + k * 0.18), y + h * 0.60),
                  (x + w * (0.18 + k * 0.16), y + h * (0.78 + 0.03 * (i % 2)))],
                 fill=(196, 186, 162, 220), width=2)


# ---------------------------------------------------------------------------
# Sheets
# ---------------------------------------------------------------------------
def build_orca():
    cells = [
        ("01 · PROFILE  left-facing, rim-lit", lambda c: (
            p_orca(c, 30, 130, 340, 150))),
        ("02 · ARCING UP  −24°", lambda c: (
            p_orca(c, 40, 120, 320, 160, angle=-24))),
        ("03 · ANGLED DOWN  +18°, distant haze", lambda c: (
            p_orca(c, 50, 130, 300, 150, angle=18, blur=2.2, alpha=0.7))),
        ("04 · TWO-UP  pair at different depths", lambda c: (
            p_orca(c, 20, 90, 230, 108),
            p_orca(c, 250, 170, 180, 84, alpha=0.6, blur=1.6))),
        ("05 · SILHOUETTE  far, near-black", lambda c: (
            p_orca(c, 40, 140, 320, 150, alpha=0.55))),
        ("06 · FLIPPED  right-facing", lambda c: (
            p_orca(c, 30, 130, 340, 150, flip=True))),
    ]
    return "ORCA  ·  Orcinus orca", cells, 3


def build_humpback():
    cells = [
        ("01 · PROFILE  pleats, baleen, knobs", lambda c: p_humpback(c, 20, 130, 360, 155)),
        ("02 · FLIPPER OUT  fin extended", lambda c: (
            p_humpback(c, 10, 120, 330, 145),
            p_fin(c, 250, 230, 90, 150, angle=40))),
        ("03 · RISING  seen from below, soft", lambda c: p_humpback(c, 0, 90, 420, 200, blur=1.6, alpha=0.85)),
        ("04 · FLUKE-DOWN  diving, tail toward camera", lambda c: (
            p_humpback(c, 40, 150, 300, 130),
            p_fin(c, 130, 40, 70, 130, angle=6))),
        ("05 · DISTANT  hazed, out of focus", lambda c: p_humpback(c, 60, 160, 280, 118, blur=3.0, alpha=0.65)),
        ("06 · FLIPPED  right-facing", lambda c: p_humpback(c, 20, 130, 360, 155, flip=True)),
    ]
    return "HUMPBACK  ·  Megaptera novaeangliae", cells, 3


def build_blue():
    cells = [
        ("01 · PROFILE  the slab", lambda c: p_blue(c, 10, 160, 380, 120)),
        ("02 · HEAD-ON  rostrum toward camera", lambda c: (
            p_blue(c, 70, 150, 260, 100),
            p_fin(c, 100, 210, 60, 120, angle=-30))),
        ("03 · DISTANT  hazed at 3.4 px", lambda c: p_blue(c, 30, 170, 340, 100, alpha=0.5)),
        ("04 · WITH ESCORTS  orcas alongside", lambda c: (
            p_blue(c, 30, 120, 340, 120),
            p_orca(c, 60, 210, 130, 60),
            p_orca(c, 200, 240, 110, 50, alpha=0.7))),
        ("05 · FROM ABOVE  plan view", lambda c: p_blue(c, 20, 150, 360, 130)),
        ("06 · FLIPPED", lambda c: p_blue(c, 10, 160, 380, 120, flip=True)),
    ]
    return "BLUE WHALE  ·  Balaenoptera musculus", cells, 3


def build_gws():
    cells = [
        ("01 · PROFILE  gills + teeth", lambda c: p_gws(c, 20, 150, 360, 150)),
        ("02 · ANGLED UP  hunting", lambda c: p_gws(c, 30, 140, 340, 150, )),
        ("03 · DISTANT  in the Gansbaai water", lambda c: p_gws(c, 50, 175, 300, 110, alpha=0.55)),
        ("04 · JAWS  close, teeth forward", lambda c: p_gws(c, -40, 120, 520, 200)),
        ("05 · THREE-UP  the reference's group", lambda c: (
            p_gws(c, 10, 70, 230, 92),
            p_gws(c, 150, 150, 210, 86, alpha=0.85),
            p_gws(c, 60, 240, 200, 82, alpha=0.6))),
        ("06 · FLIPPED", lambda c: p_gws(c, 20, 150, 360, 150, flip=True)),
    ]
    return "GREAT WHITE  ·  Carcharodon carcharias", cells, 3


def build_meg():
    cells = [
        ("01 · PROFILE  the old silhouette", lambda c: p_meg(c, 20, 140, 360, 160)),
        ("02 · GILL SLITS  detail", lambda c: p_meg(c, -50, 110, 520, 210)),
        ("03 · ANGLED  rising", lambda c: p_meg(c, 30, 130, 340, 155)),
        ("04 · DISTANT  haze", lambda c: p_meg(c, 60, 165, 290, 120, alpha=0.5)),
        ("05 · DORSAL ONLY  fin breaking surface", lambda c: (
            p_fin(c, 150, 130, 90, 175, angle=0))),
        ("06 · FLIPPED", lambda c: p_meg(c, 20, 140, 360, 160, flip=True)),
    ]
    return "MEGALODON  ·  Otodus megalodon", cells, 3


def build_liv():
    cells = [
        ("01 · PROFILE  belly creases", lambda c: p_liv(c, 20, 140, 360, 155)),
        ("02 · JAW  close", lambda c: p_liv(c, -60, 110, 540, 210)),
        ("03 · ANGLED  from above", lambda c: p_liv(c, 30, 130, 340, 155)),
        ("04 · DISTANT  haze", lambda c: p_liv(c, 60, 165, 290, 120, alpha=0.5)),
        ("05 · WITH TEETH  jaw open", lambda c: (
            p_liv(c, 10, 130, 380, 165),
            p_fin(c, 150, 250, 60, 110, angle=12))),
        ("06 · FLIPPED", lambda c: p_liv(c, 20, 140, 360, 155, flip=True)),
    ]
    return "LIVYATAN  ·  Livyatan melvillei", cells, 3


def build_flipper():
    cells = [
        ("01 · UPRIGHT  vertical, as in the film", lambda c: p_fin(c, 155, 40, 100, 320, angle=0)),
        ("02 · ANGLED  34°", lambda c: p_fin(c, 140, 60, 100, 300, angle=34)),
        ("03 · PAIR OUT  both fins, defence posture", lambda c: (
            p_fin(c, 115, 60, 90, 270, angle=-38),
            p_fin(c, 200, 60, 90, 270, angle=38))),
        ("04 · KNOBBLY  tubercles visible", lambda c: p_fin(c, 145, 30, 115, 340, angle=0)),
        ("05 · CLOSE  knobs and leading edge", lambda c: p_fin(c, 100, -40, 220, 520, angle=0)),
        ("06 · WHEEL  the reference's radial shot", lambda c: [
            p_fin(c, 200 + math.sin(math.radians(a)) * 96 - 26,
                  190 - math.cos(math.radians(a)) * 78 - 62,
                  52, 124, angle=a) for a in (0, 45, 90, 135, 180, 225, 270, 315)]),
    ]
    return "HUMPBACK FLIPPER  ·  the reference's most repeated shape", cells, 3


def build_krill():
    def swarm(c, n, spread, alpha=0.9):
        for i in range(n):
            sd = (i * 2654435761) % 1000003
            ang = (sd % 6283) / 1000.0
            rad = ((sd // 6283) % 1000) / 1000.0
            x = c.w / 2 + math.cos(ang) * spread * (rad ** 0.55)
            y = c.h / 2 + math.sin(ang) * spread * 0.62 * (rad ** 0.55)
            s = 3 + sd % 6
            c.d.ellipse([x - s, y - s * 0.5, x + s, y + s * 0.5],
                        fill=(226, 214, 186, int((70 + sd % 90) * alpha)))
    cells = [
        ("01 · SINGLE  one krill, 6× scale", lambda c: p_krill(c, 90, 160, 220, 80)),
        ("02 · CLUSTER  a dozen, tight", lambda c: swarm(c, 14, 90)),
        ("03 · SWARM  the reference's cloud", lambda c: swarm(c, 210, 190)),
        ("04 · BACKLIT  against a god-ray", lambda c: (
            swarm(c, 120, 150, alpha=1.0))),
        ("05 · DRIFTING  long exposure streaks", lambda c: (
            swarm(c, 90, 170),
            [c.d.line([(c.w / 2 - 60 + i * 7, c.h / 2 + (i % 9) * 12 - 50),
                       (c.w / 2 - 20 + i * 7, c.h / 2 + (i % 9) * 12 - 50)],
                      fill=(230, 220, 196, 60), width=2) for i in range(40)])),
        ("06 · DENSE  wall of krill", lambda c: swarm(c, 340, 200)),
    ]
    return "KRILL  ·  Euphausiacea", cells, 3


SHEETS = {
    "orca": build_orca,
    "humpback": build_humpback,
    "blue-whale": build_blue,
    "great-white": build_gws,
    "megalodon": build_meg,
    "livyatan": build_liv,
    "flipper": build_flipper,
    "krill": build_krill,
}


def render_sheet(name, title, cells, cols=3):
    rows = (len(cells) + cols - 1) // cols
    head = 62
    h = head + rows * (CELL + GAP) + PAD
    page = Image.new("RGB", (PAGE_W, h), (10, 14, 18))
    d = ImageDraw.Draw(page, "RGBA")
    d.text((PAD, 16), title, font=font(26), fill=WHITE)
    d.text((PAD, 46), f"character sheet · {len(cells)} poses · Monarch Overall Work",
           font=font(14, False), fill=MUTED)
    for i, (cap, fn) in enumerate(cells):
        cx = PAD + (i % cols) * (CELL + GAP)
        cy = head + (i // cols) * (CELL + GAP)
        c = Cell(CELL, CELL)
        out = fn(c)
        page.paste(c.im, (cx, cy))
        d.rectangle([cx, cy, cx + CELL - 1, cy + CELL - 1], outline=(38, 56, 66, 255))
        label(d, cx + 10, cy + CELL - 38, cap, size=15)
    page.save(OUT / f"{name}.jpg", quality=92)
    return page.size


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="production/extinct-life/characters")
    a = ap.parse_args()
    global OUT
    OUT = Path(a.out)
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in SHEETS.items():
        title, cells, cols = fn()
        size = render_sheet(name, title, cells, cols)
        print(f"{name}.jpg  {size[0]}x{size[1]}  {len(cells)} poses")
    print(f"\n{len(SHEETS)} sheets -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
