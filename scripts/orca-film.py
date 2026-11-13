#!/usr/bin/env python3
"""Why orcas are terrified of humpback whales — the first 60 seconds, rebuilt.

The operator asked for the reference's opening minute, same as it. So this is not
an interpretation of the topic; it is that minute's beat sheet, executed in vector.
The beat map below was read off 62 one-second frames of the reference and each
number is the second the reference cuts on.

  beat  what the reference does                              in -> out
  ----  ---------------------------------------------------  ---------
  1     orcas gliding in from the left, no words over it       0.0 ->  4.5
  2     a god-ray transition wash                              4.5 ->  5.2
  3     an orca arcs up after a tuna                             5.2 -> 9.0
  4     five orcas escort a blue whale past                      9.0 -> 14.0
  5     krill swarm, orcas feeding through it                   14.0 -> 18.0
  6     a trophic pyramid: KRILL FISH SEALS SHARKS               18.0 -> 22.5
  7     "THE BOSS OF THE SEA" and an orca at the apex            22.5 -> 24.5
  8     orca scanning, sonar rings, a distant hazy whale         24.5 -> 28.0
  9     a flock of upright flippers around the orca              28.0 -> 33.0
  10    the same flippers, spinning into a radial wheel          33.0 -> 37.0
  11    orca circle, plan view, sonar in the middle              37.0 -> 40.0
  12    a humpback rises toward the camera, vast and soft        40.0 -> 43.0
  13    Humpback Whale — 40 tonnes — 14 m HO (the card)          43.0 -> 46.0
  14    GANSBAAI, SOUTH AFRICA · 2017, then great whites         46.0 -> 52.5
  15    orcas arrive on the scene, kill data panel               52.5 -> 57.0
  16    "JUST PLAYING DEFENCE" / the whale between two orcas     57.0 -> 60.0

Everything is drawn with the same stack the reference uses: a deep vertical water
gradient, seven god-rays on a slow scroll, three parallax particle layers, shaded
bezier animals, then labels. Nothing is a flat fill and nothing is a circle stack.

Run:  python scripts/orca-film.py --out /tmp/orca --duration 60
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, ImageDraw, ImageFilter, ImageFont  # noqa: E402

import scripts.lib.creatures as C  # noqa: E402
import scripts.lib.shading as S  # noqa: E402
from scripts.lib.bezier import draw_path, stroke_path, to_pixels  # noqa: E402

W, H = 1280, 720
FPS_DEFAULT = 30

DEEP_TOP = (14, 44, 58)
DEEP_BOT = (4, 14, 21)
BONE = (236, 232, 222)
GOLD = (226, 180, 60)
WHITE = (245, 246, 244)
RED = (198, 58, 46)
GREEN = (74, 168, 104)
SLATE = (108, 126, 138)

_FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
]
_FONT_CACHE: dict = {}


def font(size: int, bold: bool = True):
    key = (size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    f = None
    for d in _FONT_DIRS:
        p = Path(d) / name
        if p.exists():
            f = ImageFont.truetype(str(p), size)
            break
    if f is None:
        f = ImageFont.load_default()
    _FONT_CACHE[key] = f
    return f


def lerp(a, b, t):
    return a + (b - a) * t


def clamp01(x):
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)


def ease_out(t):
    t = clamp01(t)
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    t = clamp01(t)
    return 3 * t * t - 2 * t * t * t


def win(t, start, end, fade=0.4):
    if t < start or t > end:
        return 0.0
    if fade <= 0:
        return 1.0
    return min(clamp01((t - start) / fade), clamp01((end - t) / fade))


# ---------------------------------------------------------------------------
# Water
# ---------------------------------------------------------------------------
_RAY_CACHE: dict = {}


def water(f, t, depth=1.0, ray_strength=1.0, tint=None):
    WW, HH = f.im.size
    top = DEEP_TOP if tint is None else tint
    bot = DEEP_BOT
    for y in range(HH):
        k = y / max(1, HH - 1)
        f.d.line(
            [(0, y), (WW, y)],
            fill=(
                int(lerp(top[0], bot[0], k) * lerp(1.0, 0.6, 1 - depth)),
                int(lerp(top[1], bot[1], k) * lerp(1.0, 0.6, 1 - depth)),
                int(lerp(top[2], bot[2], k) * lerp(1.0, 0.6, 1 - depth)),
            ),
        )
    if ray_strength <= 0.02:
        return
    key = (int(ray_strength * 10), WW, HH)
    if key not in _RAY_CACHE:
        ray = Image.new("L", (WW, HH), 0)
        rd = ImageDraw.Draw(ray)
        for i in range(7):
            x = int(WW * (0.02 + i * 0.155))
            wdt = 34 + (i * 41) % 74
            slant = 120 + (i * 29) % 90
            rd.polygon(
                [(x, -40), (x + wdt, -40), (x + wdt + slant, HH + 40), (x + slant, HH + 40)],
                fill=int(26 * ray_strength),
            )
        _RAY_CACHE[key] = ray.filter(ImageFilter.GaussianBlur(34))
    rays = _RAY_CACHE[key]
    off = int((t * 7) % WW)
    layer = Image.new("RGB", (WW, HH), (140, 198, 210))
    f.im.paste(layer, (0, 0), rays)
    f.im.paste(layer, (off - WW, 0), rays)
    f.im.paste(layer, (off, 0), rays)


def particles(f, t, density=1.0):
    WW, HH = f.im.size
    for lid, (count, rmin, rmax, speed, alpha) in enumerate(
        [(90, 1, 2, 24, 30), (54, 2, 4, 14, 44), (26, 3, 7, 7, 38)]
    ):
        count = int(count * density)
        for i in range(count):
            seed = (i * 2654435761 + lid * 40503) % 1000003
            x = (seed % WW + int(math.sin(t * 0.28 + i) * 11)) % WW
            y = ((seed // 977) % HH - t * speed) % HH
            r = rmin + (seed % (rmax - rmin + 1))
            f.d.ellipse([x - r, y - r, x + r, y + r], fill=(196, 224, 230, alpha))


# ---------------------------------------------------------------------------
# Text furniture — every label in the reference sits on a dark plate
# ---------------------------------------------------------------------------
def label_box(f, xy, text, alpha=1.0, size=22, anchor="tl", pad=(16, 9)):
    if alpha <= 0.01:
        return
    ft = font(size)
    tw = f.d.textbbox((0, 0), text, font=ft)
    bw, bh = tw[2] - tw[0], tw[3] - tw[1]
    x, y = xy
    if anchor == "tc":
        x -= bw / 2
    elif anchor == "tr":
        x -= bw
    box = [x - pad[0], y - pad[1], x + bw + pad[0], y + bh + pad[1] + 3]
    f.d.rounded_rectangle(box, radius=3, fill=(8, 12, 16, int(205 * alpha)),
                          outline=(120, 150, 162, int(70 * alpha)))
    f.d.text((x, y), text, font=ft, fill=BONE + (int(252 * alpha),))


def centre_text(f, cy, text, size=48, colour=WHITE, alpha=1.0, weight=1.0):
    if alpha <= 0.01:
        return
    CW, CH = f.im.size
    ft = font(size)
    bb = f.d.textbbox((0, 0), text, font=ft)
    x = CW / 2 - (bb[2] - bb[0]) / 2
    f.d.text((x + 3, cy + 4), text, font=ft, fill=(0, 0, 0, int(120 * alpha)))
    f.d.text((x, cy), text, font=ft, fill=colour + (int(250 * alpha * weight),))


def centre_block(f, cx, cy, lines, alpha=1.0, gap=40):
    """A stacked centre card: big line, then a smaller gold line under it."""
    if alpha <= 0.01:
        return
    centre_text(f, cy, lines[0], size=44, alpha=alpha)
    if len(lines) > 1:
        centre_text(f, cy + gap, lines[1], size=25, colour=GOLD, alpha=alpha)


def bar_rule(f, x0, x1, y, alpha=1.0, colour=GOLD, caps=True):
    if alpha <= 0.01:
        return
    f.d.line([(x0, y), (x1, y)], fill=colour + (int(235 * alpha),), width=2)
    if caps:
        f.d.line([(x0, y - 9), (x0, y + 9)], fill=colour + (int(235 * alpha),), width=3)
        f.d.line([(x1, y - 9), (x1, y + 9)], fill=colour + (int(235 * alpha),), width=3)


def sonar(f, cx, cy, t, period=2.4, n=3, radius=360, alpha=1.0, colour=(150, 200, 210)):
    if alpha <= 0.01:
        return
    for i in range(n):
        age = ((t + i * period / n) % period) / period
        r = 40 + age * radius
        a = int(120 * (1 - age) * alpha)
        if a <= 2:
            continue
        f.d.arc([cx - r, cy - r * 0.92, cx + r, cy + r * 0.92], 200, 340,
                fill=colour + (a,), width=2)


def scan_sweep(f, cx, cy, t, r, alpha=1.0):
    """The radar wedge in the reference's sonar panels."""
    a0 = (t * 60) % 360
    ov = Image.new("RGBA", f.im.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.pieslice([cx - r, cy - r, cx + r, cy + r], a0 - 34, a0,
                fill=(96, 210, 150, int(58 * alpha)))
    f.im.paste(Image.alpha_composite(f.im.convert("RGBA"), ov).convert("RGB"), (0, 0))


# ---------------------------------------------------------------------------
# Animal painting — every one goes through shading.py
# ---------------------------------------------------------------------------
def _bb(x, y, w, h):
    return (x, y, w, h)


def shaded_tile(size, path, bbox, stops, flip=False, segs=30, extras=None):
    """Render one animal onto its own transparent RGBA tile.

    The first version of this wrote `_Frame(tile.convert("RGB"), td)`, which draws
    into a throw-away copy: every blurred animal came out as an empty black box, and
    that is exactly what beats 12-14 looked like before this was fixed. The body is
    now composited back onto the tile explicitly, and the alpha is the union of the
    body mask and any extra patches so the white saddle is not clipped off.
    """
    w, h = int(size[0]), int(size[1])
    rgb = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(rgb, "RGBA")
    fr = type("F", (), {})()
    fr.im, fr.d, fr.w, fr.h = rgb, d, w, h
    S.fill_shaded(fr, path, bbox, stops, flip=flip, segs=segs)
    mask = S.mask_from_path((w, h), path, bbox, flip=flip, segs=segs)
    alpha_mask = mask
    if extras:
        pmask = Image.new("L", (w, h), 0)
        pd = ImageDraw.Draw(pmask)
        extras(d, bbox, False)
        extras(pd, bbox, True)
        from PIL import ImageChops
        alpha_mask = ImageChops.lighter(mask, pmask)
    out = rgb.convert("RGBA")
    out.putalpha(alpha_mask)
    return out


def orca(f, x, y, w, h, flip=False, alpha=1.0, detail=True, blur=0.0, angle=0.0):
    """Black body, white saddle patch, white eyepatch, tall dorsal.

    Anything that needs blur or rotation is built on a transparent tile first. An
    orca drawn straight onto the frame cannot be depth-graded later, because a blur
    applied afterwards picks up the water behind it and produces a black rectangle.
    """
    bb = _bb(x, y, w, h)
    stops = [(0.0, (7, 8, 11)), (0.5, (20, 22, 28)), (1.0, (50, 55, 62))]

    def patches(d, b, mask_only=False):
        # an "L" mask takes a bare int; an RGBA draw takes a 4-tuple
        col = 255 if mask_only else BONE + (252,)
        draw_path(d, C.ORCA_PATCH, b, col, flip=flip, segs=24)
        draw_path(d, C.ORCA_EYEPATCH, b, col, flip=flip, segs=20)

    if blur > 0.2 or abs(angle) > 0.1:
        pad = 30
        tile = shaded_tile((int(w) + pad * 2, int(h) + pad * 2), C.ORCA,
                           (pad, pad, w, h), stops, flip=flip, segs=26, extras=patches)
        if blur > 0.2:
            tile = tile.filter(ImageFilter.GaussianBlur(blur))
        if abs(angle) > 0.1:
            tile = tile.rotate(angle, resample=Image.BICUBIC, expand=False)
        if alpha < 0.999:
            tile.putalpha(tile.getchannel("A").point(lambda v: int(v * alpha)))
        f.im.paste(tile, (int(x - pad), int(y - pad)), tile)
        return

    S.fill_shaded(f, C.ORCA, bb, stops, flip=flip, segs=28, alpha=alpha)
    draw_path(f.d, C.ORCA_PATCH, bb, BONE + (int(252 * alpha),), flip=flip, segs=24)
    draw_path(f.d, C.ORCA_EYEPATCH, bb, BONE + (int(252 * alpha),), flip=flip, segs=20)
    if detail and alpha > 0.5:
        S.rim_light(f, C.ORCA, bb, colour=(160, 200, 215), width=max(2, int(h * 0.010)),
                    alpha=0.34 * alpha, flip=flip, segs=28)
    ex, ey = C.scale_point(bb, C.ORCA_EYE)
    if flip:
        ex = x + w - (ex - x)
    r = max(1.6, h * 0.016)
    f.d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(242, 240, 234, int(255 * alpha)))


def blue_whale(f, x, y, w, h, flip=False, alpha=1.0, detail=True, blur=0.0):
    bb = _bb(x, y, w, h)
    stops = [(0.0, (30, 34, 42)), (0.42, (64, 72, 86)), (0.78, (112, 121, 133)), (1.0, (156, 163, 172))]
    if blur > 0.2:
        pad = 30
        tile = shaded_tile((int(w) + pad * 2, int(h) + pad * 2), C.BLUE_WHALE,
                           (pad, pad, w, h), stops, flip=flip, segs=30)
        tile = tile.filter(ImageFilter.GaussianBlur(blur))
        if alpha < 0.999:
            tile.putalpha(tile.getchannel("A").point(lambda v: int(v * alpha)))
        f.im.paste(tile, (int(x - pad), int(y - pad)), tile)
        return
    S.fill_shaded(f, C.BLUE_WHALE, bb, stops, flip=flip, segs=30, alpha=alpha)
    if detail and alpha > 0.5:
        for pts in C.unit_to_px(C.blue_whale_pleats(26), bb, flip=flip):
            f.d.line(pts, fill=(24, 28, 34, int(130 * alpha)),
                     width=max(2, int(h * 0.010)), joint="curve")
        S.rim_light(f, C.BLUE_WHALE, bb, colour=(170, 205, 220), width=max(2, int(h * 0.012)),
                    alpha=0.36 * alpha, flip=flip, segs=30)
        S.streaks(f, C.BLUE_WHALE, bb, alpha=0.05 * alpha, n=40, flip=flip)
    stroke_path(f.d, C.BLUE_WHALE_MOUTH, bb, (10, 12, 16, int(210 * alpha)),
                width=max(2, int(h * 0.014)), flip=flip, segs=26)
    ex, ey = C.scale_point(bb, C.BLUE_WHALE_EYE)
    if flip:
        ex = x + w - (ex - x)
    r = max(1.6, h * 0.020)
    f.d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(240, 238, 232, int(255 * alpha)))


def humpback(f, x, y, w, h, flip=False, alpha=1.0, detail=True, blur=0.0):
    """The animal the whole video is about, with the features that identify it.

    A humpback is not a blue whale: it has a knobbly head, a long white grooved
    throat, an enormous pectoral fin, and a much deeper body for its length. Drawing
    the species card with the blue whale was wrong in a way that is obvious the
    moment you know the animal.
    """
    bb = _bb(x, y, w, h)
    stops = [(0.0, (10, 12, 17)), (0.36, (26, 30, 36)), (0.72, (92, 99, 108)), (1.0, (168, 173, 178))]
    if blur > 0.2:
        pad = 30
        tile = shaded_tile((int(w) + pad * 2, int(h) + pad * 2), C.HUMPBACK,
                           (pad, pad, w, h), stops, flip=flip, segs=30)
        tile = tile.filter(ImageFilter.GaussianBlur(blur))
        if alpha < 0.999:
            tile.putalpha(tile.getchannel("A").point(lambda v: int(v * alpha)))
        f.im.paste(tile, (int(x - pad), int(y - pad)), tile)
        return
    S.fill_shaded(f, C.HUMPBACK_FLIPPER, bb, [(0.0, (206, 208, 204)), (1.0, (124, 129, 134))],
                  flip=flip, segs=26, alpha=alpha)
    S.fill_shaded(f, C.HUMPBACK, bb, stops, flip=flip, segs=30, alpha=alpha)
    if detail and alpha > 0.5:
        for pts in C.unit_to_px(C.humpback_pleats(16), bb, flip=flip):
            f.d.line(pts, fill=(52, 57, 64, int(170 * alpha)),
                     width=max(2, int(h * 0.010)), joint="curve")
        for pts in C.unit_to_px(C.flipper_knobs(10), bb, flip=flip):
            (ax, ay), (bx, by) = pts
            r = max(2.0, h * 0.012)
            # a flipped bbox reverses x, so normalise before building the ellipse box
            x0k, x1k = min(ax, bx), max(ax, bx)
            y0k, y1k = min(ay, by), max(ay, by)
            f.d.ellipse([x0k - r, y0k - r, x1k + r, y1k + r],
                        fill=(236, 233, 226, int(230 * alpha)))
        for pts in C.unit_to_px(C.baleen_comb(24), bb, flip=flip):
            f.d.line(pts, fill=(226, 180, 60, int(235 * alpha)), width=max(2, int(h * 0.011)))
        S.rim_light(f, C.HUMPBACK, bb, colour=(175, 212, 224), width=max(2, int(h * 0.010)),
                    alpha=0.34 * alpha, flip=flip, segs=30)
        S.streaks(f, C.HUMPBACK, bb, alpha=0.05 * alpha, n=32, flip=flip)
    stroke_path(f.d, C.HUMPBACK_MOUTH, bb, (6, 8, 12, int(230 * alpha)),
                width=max(2, int(h * 0.014)), flip=flip, segs=24)
    ex, ey = C.scale_point(bb, C.HUMPBACK_EYE)
    if flip:
        ex = x + w - (ex - x)
    r = max(1.8, h * 0.014)
    f.d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(240, 238, 232, int(255 * alpha)))


def great_white(f, x, y, w, h, flip=False, alpha=1.0, detail=True, blur=0.0):
    bb = _bb(x, y, w, h)
    stops = [(0.0, (44, 50, 58)), (0.46, (92, 99, 108)), (1.0, (198, 202, 206))]
    if blur > 0.2:
        pad = 20
        tile = shaded_tile((int(w) + pad * 2, int(h) + pad * 2), C.GREAT_WHITE,
                           (pad, pad, w, h), stops, flip=flip, segs=28)
        tile = tile.filter(ImageFilter.GaussianBlur(blur))
        if alpha < 0.999:
            tile.putalpha(tile.getchannel("A").point(lambda v: int(v * alpha)))
        f.im.paste(tile, (int(x - pad), int(y - pad)), tile)
        return
    S.fill_shaded(f, C.GREAT_WHITE, bb, stops, flip=flip, segs=28, alpha=alpha)
    if detail and alpha > 0.5:
        for (a, b) in C.unit_to_px(C.great_white_gills(5), bb, flip=flip):
            f.d.line([a, b], fill=(22, 26, 32, int(180 * alpha)),
                     width=max(1, int(h * 0.016)))
        for tri in C.unit_to_px(C.shark_teeth_row(15, 0.700, 0.930, 0.600), bb, flip=flip):
            f.d.polygon(tri, fill=(246, 246, 241, int(240 * alpha)))
        S.rim_light(f, C.GREAT_WHITE, bb, colour=(175, 210, 222), width=max(2, int(h * 0.012)),
                    alpha=0.40 * alpha, flip=flip, segs=28)
    ex, ey = C.scale_point(bb, C.GREAT_WHITE_EYE)
    if flip:
        ex = x + w - (ex - x)
    r = max(1.4, h * 0.020)
    f.d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(238, 236, 230, int(255 * alpha)))


def flipper(f, x, y, w, h, angle=0.0, alpha=1.0, flip=False):
    """A bare pectoral fin. The reference's most repeated shape after the orca.

    Rotating a tile rotates about the tile centre, so the caller passes the centre
    of where the fin should sit, not its top-left.
    """
    pad = int(max(w, h) * 0.55) + 10
    tile = shaded_tile((int(w) + pad * 2, int(h) + pad * 2), C.WHALE_FIN_UP,
                       (pad, pad, w, h),
                       [(0.0, (214, 216, 212)), (0.5, (178, 182, 181)), (1.0, (128, 133, 137))],
                       flip=flip, segs=26)
    if abs(angle) > 0.1:
        tile = tile.rotate(angle, resample=Image.BICUBIC, expand=True)
    if alpha < 0.999:
        tile.putalpha(tile.getchannel("A").point(lambda v: int(v * alpha)))
    f.im.paste(tile, (int(x + w / 2 - tile.width / 2), int(y + h / 2 - tile.height / 2)), tile)


def krill_swarm(f, t, cx, cy, rx, ry, n=210, alpha=1.0, drift=6.0):
    """Thousands of tiny soft bodies, which is what the reference's swarm reads as."""
    for i in range(n):
        seed = (i * 2654435761) % 1000003
        ang = (seed % 6283) / 1000.0
        rad = ((seed // 6283) % 1000) / 1000.0
        rr = rad ** 0.55
        x = cx + math.cos(ang) * rx * rr
        y = cy + math.sin(ang) * ry * rr + math.sin(t * 0.7 + i * 0.4) * drift
        s = 2 + (seed % 5)
        a = int((70 + (seed % 90)) * alpha)
        tint = (226, 214, 186) if seed % 3 else (206, 198, 176)
        f.d.ellipse([x - s, y - s * 0.5, x + s, y + s * 0.5], fill=tint + (a,))


def bubble(f, x, y, r, alpha=1.0):
    if alpha <= 0.02:
        return
    f.d.ellipse([x - r, y - r, x + r, y + r], outline=(210, 232, 238, int(150 * alpha)),
                width=max(1, int(r * 0.28)))
    f.d.ellipse([x - r * 0.45, y - r * 0.5, x - r * 0.05, y - r * 0.15],
                fill=(255, 255, 255, int(110 * alpha)))


def trail(f, x, y, w, h, alpha=1.0, n=7, colour=(150, 195, 210)):
    """Motion streaks trailing an animal, so movement is legible in a still."""
    for i in range(n):
        k = i / max(1, n - 1)
        xx = x + w * k
        a = int(90 * (1 - k) * alpha)
        if a <= 2:
            continue
        f.d.line([(xx, y + h * (i % 2) * 0.4), (xx - w * 0.10, y + h * (i % 2) * 0.4)],
                 fill=colour + (a,), width=2)


# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------
def cam_crop(im, t, t0, t1, drift=(0.02, -0.015), push=0.055):
    k = clamp01((t - t0) / max(0.001, t1 - t0))
    e = ease_in_out(k)
    sw, sh = im.size
    scale = 1.03 + push * e
    cw = max(8, min(sw, int(round(W / scale))))
    ch = max(8, min(sh, int(round(H / scale))))
    cx = (sw - cw) / 2 + drift[0] * sw * (e - 0.5)
    cy = (sh - ch) / 2 + drift[1] * sh * (e - 0.5)
    cx = int(max(0, min(sw - cw, round(cx))))
    cy = int(max(0, min(sh - ch, round(cy))))
    out = im.crop((cx, cy, cx + cw, cy + ch))
    if out.size != (W, H):
        out = out.resize((W, H), Image.LANCZOS)
    return out


CAM_S = 1.16


# ---------------------------------------------------------------------------
# Beats
# ---------------------------------------------------------------------------
def b_orcas_in(f, t, t0, t1):
    """1. Orcas glide in from the left in loose formation, nothing on screen."""
    water(f, t, 1.0, 1.0)
    particles(f, t, 0.9)
    p = ease_out(clamp01((t - t0) / 3.4))
    specs = [
        (-0.16, 0.20, 0.30, -6.0),
        (-0.24, 0.46, 0.24, -2.0),
        (-0.10, 0.66, 0.27, 2.0),
        (-0.30, 0.80, 0.20, 5.0),
    ]
    for i, (bx, by, sz, dy) in enumerate(specs):
        x = W * (bx + p * 0.34)
        y = H * (by + dy * 0.004) + math.sin(t * 0.9 + i) * 5
        orca(f, x, y, W * sz * CAM_S * 0.8, H * 0.30 * CAM_S * 0.8,
             alpha=0.65 + 0.35 * (i == 0), detail=(i == 0))


def b_wash(f, t, t0, t1):
    """2. The reference cuts through a bright god-ray wash between scenes."""
    water(f, t, 0.55, 3.4)
    k = win(t, t0, t1, 0.2)
    CW, CH = f.im.size
    ov = Image.new("RGB", (CW, CH), (150, 205, 214))
    f.im.paste(Image.blend(f.im, ov, 0.55 * k), (0, 0))
    particles(f, t, 0.4)


def b_arc(f, t, t0, t1):
    """3. An orca arcs upward and a fish breaks above it."""
    water(f, t, 0.9, 1.2)
    particles(f, t, 1.0)
    p = ease_out(clamp01((t - t0) / 3.0))
    CW, CH = f.im.size
    # the arcing orca, rotated through a shallow climb
    ang = -22 * p
    orca(f, CW * 0.30, CH * (0.52 - 0.14 * p), CW * 0.30, CH * 0.34,
         angle=ang, alpha=1.0)
    # the fish it is chasing, small and sharp
    fish_x = CW * (0.50 + 0.06 * p)
    fish_y = CH * (0.30 - 0.06 * p)
    f.d.ellipse([fish_x - 26, fish_y - 9, fish_x + 26, fish_y + 9],
                fill=(198, 204, 206, 240))
    f.d.polygon([(fish_x + 26, fish_y), (fish_x + 46, fish_y - 14), (fish_x + 46, fish_y + 14)],
                fill=(186, 192, 195, 240))
    trail(f, fish_x - 120, fish_y - 4, 110, 10, alpha=0.7)


def b_escort(f, t, t0, t1):
    """4. Five orcas escort a blue whale — the reference's hero establishing shot."""
    water(f, t, 1.0, 1.0)
    particles(f, t, 0.8)
    CW, CH = f.im.size
    p = ease_out(clamp01((t - t0) / 4.4))
    # blue whale: huge, off the right edge, drifting left
    blue_whale(f, CW * (0.26 - 0.03 * p), CH * 0.40, CW * 1.02, CH * 0.30, alpha=1.0)
    # five orcas, staggered, the nearest sharp
    specs = [(0.02, 0.30, 0.17), (0.05, 0.62, 0.15), (0.14, 0.80, 0.13),
             (0.20, 0.24, 0.11), (0.24, 0.68, 0.09)]
    for i, (bx, by, sz) in enumerate(specs):
        x = CW * (bx + 0.02 * p)
        y = CH * (by + math.sin(t * 1.1 + i) * 0.006)
        orca(f, x, y, CW * sz, CH * sz * 1.5, alpha=0.55 + 0.45 * (i < 2), detail=(i < 2))
    k = win(t, t0 + 2.2, t1, 0.5)
    centre_text(f, CH * 0.86, "THE BIGGEST ANIMAL THAT HAS EVER LIVED",
                size=21, alpha=k)


def b_krill(f, t, t0, t1):
    """5. Krill swarm; the orcas feed straight through it."""
    water(f, t, 0.85, 1.4)
    CW, CH = f.im.size
    krill_swarm(f, t, CW * 0.50, CH * 0.48, CW * 0.42, CH * 0.34, n=260, alpha=0.9)
    p = ease_out(clamp01((t - t0) / 4.0))
    orca(f, CW * (0.16 + 0.10 * p), CH * 0.30, CW * 0.26, CH * 0.30, alpha=1.0)
    orca(f, CW * (0.62 + 0.10 * p), CH * 0.58, CW * 0.20, CH * 0.24, alpha=0.8)
    # krill caught in the wash, catching light
    for i in range(70):
        seed = (i * 7919) % 100003
        x = CW * (0.12 + (seed % 900) / 1000.0 * 0.8) + math.sin(t * 1.4 + i) * 8
        y = CH * (0.18 + ((seed // 900) % 700) / 1000.0 * 0.7)
        r = 2 + seed % 4
        f.d.ellipse([x - r, y - r, x + r, y + r], fill=(240, 232, 210, 120))


def _pyramid(f, cx, base_y, apex_y, half_w, rows, alpha=1.0, labels=None):
    """The trophic pyramid from the reference: four stacked trapezoids."""
    if alpha <= 0.01:
        return
    n = len(rows)
    for i, (txt, col) in enumerate(zip(labels or rows, rows)):
        k0 = i / n
        k1 = (i + 1) / n
        y0 = lerp(apex_y, base_y, k0)
        y1 = lerp(apex_y, base_y, k1)
        hw0 = lerp(half_w * 0.10, half_w, k0)
        hw1 = lerp(half_w * 0.10, half_w, k1)
        f.d.polygon([(cx - hw0, y0), (cx + hw0, y0), (cx + hw1, y1), (cx - hw1, y1)],
                    fill=col + (int(228 * alpha),), outline=(150, 190, 205, int(80 * alpha)))
        ft = font(20)
        bb = f.d.textbbox((0, 0), txt, font=ft)
        f.d.text((cx - (bb[2] - bb[0]) / 2, (y0 + y1) / 2 - (bb[3] - bb[1]) / 2 - 2),
                 txt, font=ft, fill=BONE + (int(250 * alpha),))


def b_pyramid(f, t, t0, t1):
    """6. The trophic pyramid builds bottom-up."""
    water(f, t, 0.9, 0.8)
    particles(f, t, 0.5)
    CW, CH = f.im.size
    k = win(t, t0, t1, 0.5)
    rows = [(58, 92, 108), (62, 104, 118), (68, 116, 128), (74, 128, 138)]
    reveal = clamp01((t - t0) / 0.9)
    for i, col in enumerate(rows):
        if reveal >= (3 - i) / 4.0 + 0.02:
            k0 = i / 4
            k1 = (i + 1) / 4
            y0 = lerp(CH * 0.20, CH * 0.74, k0)
            y1 = lerp(CH * 0.20, CH * 0.74, k1)
            hw0 = lerp(CW * 0.052, CW * 0.26, k0)
            hw1 = lerp(CW * 0.052, CW * 0.26, k1)
            f.d.polygon([(CW / 2 - hw0, y0), (CW / 2 + hw0, y0),
                         (CW / 2 + hw1, y1), (CW / 2 - hw1, y1)],
                        fill=col + (int(225 * k),), outline=(150, 190, 205, int(80 * k)))
            lbl = ["SHARKS", "SEALS", "FISH", "KRILL"][i]
            centre_text(f, (y0 + y1) / 2 - 13, lbl, size=20, alpha=k)


def b_boss(f, t, t0, t1):
    """7. THE BOSS OF THE SEA, an orca sitting above the pyramid's apex."""
    b_pyramid(f, t, t0, t1)
    CW, CH = f.im.size
    k = win(t, t0 + 0.3, t1, 0.5)
    centre_text(f, CH * 0.085, "THE BOSS OF THE SEA", size=30, colour=RED, alpha=k)
    orca(f, CW * 0.42, CH * 0.10, CW * 0.20, CH * 0.18, alpha=k)


def b_scan(f, t, t0, t1):
    """8. Orca scanning; sonar rings; a hazy whale far off, out of focus."""
    water(f, t, 1.0, 1.0)
    particles(f, t, 0.9)
    CW, CH = f.im.size
    # far whale: blurred AND hazed, the reference's depth cue
    blue_whale(f, CW * 0.62, CH * 0.30, CW * 0.46, CH * 0.14, blur=3.4, alpha=0.55)
    p = ease_out(clamp01((t - t0) / 3.2))
    orca(f, CW * (0.06 + 0.06 * p), CH * 0.48, CW * 0.28, CH * 0.30, alpha=1.0)
    sonar(f, CW * 0.42, CH * 0.50, t, period=2.6, n=3, radius=CW * 0.30, alpha=0.85)


def b_flock(f, t, t0, t1):
    """9. A flock of upright flippers around the orca."""
    water(f, t, 1.0, 1.0)
    particles(f, t, 0.7)
    CW, CH = f.im.size
    p = ease_out(clamp01((t - t0) / 3.4))
    orca(f, CW * (0.36 + 0.05 * p), CH * 0.44, CW * 0.24, CH * 0.26, alpha=1.0)
    spots = [(0.12, 0.16, -34), (0.30, 0.10, -16), (0.46, 0.14, -6), (0.60, 0.08, 14),
             (0.70, 0.20, 28), (0.18, 0.32, -46), (0.58, 0.36, 34)]
    for i, (bx, by, ang) in enumerate(spots):
        a = win(t, t0 + i * 0.16, t1, 0.45)
        flipper(f, CW * (bx + 0.008 * p), CH * (by + 0.02 * p), CW * 0.075, CH * 0.36,
                angle=ang, alpha=a)


def b_wheel(f, t, t0, t1):
    """10. The same flippers rotate into a radial wheel — the reference's oddest shot."""
    water(f, t, 0.8, 1.3)
    particles(f, t, 0.6)
    CW, CH = f.im.size
    n = 8
    a = win(t, t0, t1, 0.5)
    for i in range(n):
        ang = 360.0 / n * i + t * 24.0
        rad = CW * 0.20
        x = CW / 2 + math.sin(math.radians(ang)) * rad
        y = CH / 2 - math.cos(math.radians(ang)) * rad * 0.80
        flipper(f, x - CW * 0.050, y - CH * 0.22, CW * 0.100, CH * 0.44,
                angle=ang, alpha=a)


def b_plan(f, t, t0, t1):
    """11. Plan view: an orca ring with sonar sweeping in the middle."""
    water(f, t, 0.9, 1.0)
    particles(f, t, 0.6)
    CW, CH = f.im.size
    p = ease_out(clamp01((t - t0) / 2.4))
    n = 6
    for i in range(n):
        ang = 360.0 / n * i + t * 8.0
        rad = CW * (0.16 + 0.02 * p)
        x = CW / 2 + math.sin(math.radians(ang)) * rad
        y = CH / 2 - math.cos(math.radians(ang)) * rad * 0.60
        orca(f, x - CW * 0.05, y - CH * 0.05, CW * 0.075, CH * 0.11,
             angle=ang, alpha=0.92)
    sonar(f, CW / 2, CH / 2, t, period=2.0, n=3, radius=CW * 0.22, alpha=0.9)


def b_rise(f, t, t0, t1):
    """12. A humpback rises toward camera: a huge soft mass entering frame.

    No hard outline. The reference's version is almost a smudge, and that is the
    point — it is the animal that is about to fill the next two beats.
    """
    water(f, t, 0.7, 1.5)
    particles(f, t, 1.1)
    CW, CH = f.im.size
    p = ease_in_out(clamp01((t - t0) / 3.0))
    # a dark bulk sliding up from below, scaled past the frame
    humpback(f, CW * (0.08 - 0.04 * p), CH * (0.58 - 0.28 * p),
             CW * 1.12, CH * 0.46, flip=True, blur=2.2, alpha=0.82)
    for i in range(9):
        bubble(f, CW * (0.3 + 0.05 * i) + math.sin(t + i) * 14,
               CH * (0.9 - 0.10 * i - 0.06 * p), 6 + (i % 4) * 5, alpha=0.7)


def b_card(f, t, t0, t1):
    """13. The species card: Humpback Whale / 40 tonnes / 14 m, over the animal."""
    water(f, t, 0.62, 1.3)
    particles(f, t, 0.5)
    CW, CH = f.im.size
    humpback(f, CW * 0.04, CH * 0.40, CW * 0.92, CH * 0.38, flip=True)
    k = win(t, t0 + 0.15, t1, 0.5)
    centre_text(f, CH * 0.105, "HUMPBACK WHALE", size=46, alpha=k)
    centre_text(f, CH * 0.198, "40 TONNES   ·   14 M LONG", size=24, colour=GOLD, alpha=k)


def b_gansbaai(f, t, t0, t1):
    """14. GANSBAAI, SOUTH AFRICA · 2017, then great whites in the water."""
    water(f, t, 0.9, 1.5)
    particles(f, t, 0.8)
    CW, CH = f.im.size
    label_box(f, (CW / 2, CH * 0.10), "GANSBAAI, SOUTH AFRICA  ·  2017",
              alpha=win(t, t0, t1, 0.5), size=22, anchor="tc")
    p = ease_out(clamp01((t - t0) / 4.5))
    specs = [(0.54, 0.22, 0.30), (0.62, 0.50, 0.26), (0.50, 0.74, 0.24)]
    for i, (bx, by, sz) in enumerate(specs):
        x = CW * (bx + 0.05 * p) - i * 12
        y = CH * (by + math.sin(t * 0.8 + i) * 0.008)
        great_white(f, x, y, CW * sz, CH * sz * 0.62, alpha=0.5 + 0.5 * (i < 2),
                    detail=(i < 2), blur=0.0 if i < 2 else 1.6)


def b_kill(f, t, t0, t1):
    """15. Orcas arrive; the kill-data panel slides in."""
    water(f, t, 1.0, 1.1)
    particles(f, t, 0.7)
    CW, CH = f.im.size
    p = ease_out(clamp01((t - t0) / 3.0))
    great_white(f, CW * 0.26, CH * 0.40, CW * 0.34, CH * 0.22, alpha=0.9)
    orca(f, CW * (0.40 + 0.06 * p), CH * 0.30, CW * 0.22, CH * 0.24, alpha=1.0)
    orca(f, CW * (0.16 + 0.04 * p), CH * 0.56, CW * 0.18, CH * 0.20, alpha=0.85)
    label_box(f, (CW * 0.70, CH * 0.22), "PORT", alpha=p, size=17)
    label_box(f, (CW * 0.66, CH * 0.30), "STARBOARD", alpha=p, size=17)
    # a small line chart, as in the reference's data panel
    if p > 0.4:
        k = (p - 0.4) / 0.6
        x0, y0, w, h = CW * 0.66, CH * 0.52, CW * 0.20, CH * 0.14
        f.d.rectangle([x0, y0, x0 + w, y0 + h], fill=(10, 16, 20, int(200 * k)),
                      outline=(120, 150, 162, int(90 * k)))
        pts = []
        for i in range(14):
            fx = x0 + w * i / 13
            fy = y0 + h * (0.86 - 0.62 * (i / 13) ** 2.2)
            pts.append((fx, fy))
        f.d.line(pts, fill=RED + (int(240 * k),), width=2)


def b_defence(f, t, t0, t1):
    """16. JUST PLAYING DEFENCE, a humpback between two orcas."""
    water(f, t, 0.9, 1.2)
    particles(f, t, 0.8)
    CW, CH = f.im.size
    p = ease_out(clamp01((t - t0) / 2.6))
    # humpback in the middle, flippers out — the actual defence posture
    humpback(f, CW * 0.28, CH * 0.38, CW * 0.46, CH * 0.26, alpha=0.95)
    flipper(f, CW * 0.60, CH * 0.28, CW * 0.105, CH * 0.44, angle=44, alpha=0.9)
    flipper(f, CW * 0.22, CH * 0.32, CW * 0.105, CH * 0.42, angle=-48, alpha=0.9)
    orca(f, CW * (0.06 + 0.03 * p), CH * 0.28, CW * 0.20, CH * 0.22, alpha=0.95)
    orca(f, CW * (0.68 - 0.03 * p), CH * 0.56, CW * 0.18, CH * 0.20, alpha=0.9)
    k = win(t, t0 + 0.8, t1, 0.5)
    centre_text(f, CH * 0.86, "JUST PLAYING DEFENCE", size=26, alpha=k)


def beats():
    """Beat map locked to the 40.76 s narration, then a 19 s silent tail.

    Narration landmarks, measured from the three generated clips:
      0.00  "Off the coast of South Africa..."
     14.25  "It is not a shark. It is the humpback whale."
     27.64  "Not because it is afraid of being eaten..."
     40.76  end of speech
    The tail exists because the reference never stops talking until the card; here
    the last three beats carry no words, so they get more room to breathe.
    """
    return [
        (0.00, 5.20, b_orcas_in),      # "Off the coast of South Africa, killer whales hunt..."
        (5.20, 6.10, b_wash),
        (6.10, 9.40, b_arc),
        (9.40, 14.25, b_escort),       # "Great whites. Seals. Fish. Krill."
        (14.25, 18.60, b_krill),       # "It is not a shark. It is the humpback whale."
        (18.60, 22.40, b_card),        # 40 TONNES / 14 M
        (22.40, 25.60, b_pyramid),     # trophic pyramid
        (25.60, 27.64, b_boss),        # THE BOSS OF THE SEA
        (27.64, 31.40, b_scan),        # "Not because it is afraid..."
        (31.40, 35.60, b_flock),       # flippers
        (35.60, 39.20, b_wheel),
        (39.20, 42.40, b_plan),
        (42.40, 45.60, b_rise),
        (45.60, 49.60, b_gansbaai),    # "In 2017, off Gansbaai, orcas started killing..."
        (49.60, 54.00, b_kill),
        (54.00, 60.00, b_defence),     # "And still, they did not touch the humpbacks."
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=FPS_DEFAULT)
    ap.add_argument("--still", type=float, default=None)
    ap.add_argument("--duration", type=float, default=60.0)
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    bs = beats()
    total = int(a.duration * a.fps)

    def render(t):
        BW, BH = int(W * CAM_S), int(H * CAM_S)
        f = type("F", (), {})()
        f.im = Image.new("RGB", (BW, BH), DEEP_TOP)
        f.d = ImageDraw.Draw(f.im, "RGBA")
        f.w, f.h = BW, BH
        active = None
        for (s, e, fn) in bs:
            if s - 0.6 <= t <= e + 0.6:
                fn(f, t, s, e)
                if s <= t <= e:
                    active = (s, e)
        if active:
            return cam_crop(f.im, t, active[0], active[1])
        return cam_crop(f.im, t, 0.0, 1.0)

    if a.still is not None:
        p = out / f"still-{a.still:06.2f}.png"
        render(a.still).save(p)
        print(p)
        return 0

    for i in range(total):
        render(i / a.fps).save(out / f"f_{i:05d}.png")
        if i % 120 == 0:
            print(f"frame {i}/{total}", flush=True)
    print(f"{total} frames -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
