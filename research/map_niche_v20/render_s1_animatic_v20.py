#!/usr/bin/env python3
"""S1 style-frame animatic — "The US Town You Can Only Reach Through Canada".

What this is: a 58-second, 9:16, frame-rendered *style test* for Shorts S1 of the V20 map
series. It exists to lock composition, pacing, on-screen text size and the map look BEFORE
anyone spends animation hours. Every frame is drawn programmatically (PIL), so nothing here
is footage from anyone else, and nothing here is a finished animation.

What this is NOT: not a finished video, not a 3D render, not geographically precise
cartography (shapes are schematic blocks, not Natural Earth geometry), no narration, no music.
VO is carried by burned-in caption text standing in for the voice track.

Run:  python3 render_s1_animatic_v20.py [--fps 12]
Out:  s1_animatic_v20.mp4 (+ poster.png, frames/ if --keep-frames)
"""
from __future__ import annotations

import argparse
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 540, 960          # 9:16 style test (scaled-up render would be 1080x1920)
SAFE_TOP, SAFE_BOTTOM = 0.16, 0.22

INK = (17, 26, 40)
DEEP = (12, 20, 33)
LAND = (214, 202, 182)
LAND_DK = (188, 175, 154)
WATER = (38, 92, 140)
WATER_DK = (28, 74, 116)
RED = (224, 71, 60)
WHITE = (255, 255, 255)
GREY = (176, 184, 196)
GREEN = (74, 122, 92)


def font(size, bold=True):
    for p in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


F_HOOK = font(44)
F_BIG = font(74)
F_MID = font(52)
F_CAP = font(34)
F_SM = font(26)
F_TINY = font(20)


def fit(draw, text, start, maxw, min_size=28):
    """Shrink until the line fits the safe width, so headlines never clip."""
    size = start
    while size > min_size and draw.textlength(text, font=font(size)) > maxw:
        size -= 2
    return font(size)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return a + (b - a) * t


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def caption(img, draw, text, y=None, size=F_CAP, color=WHITE, box=True, alpha=1.0):
    """Sound-off caption block inside the safe zone."""
    y = y if y is not None else int(H * (1 - SAFE_BOTTOM)) - 150
    lines = wrap(draw, text, size, W - 72)
    lh = size.size + 10
    h = lh * len(lines)
    if box:
        draw.rounded_rectangle([28, y - 14, W - 28, y + h + 12], 18, fill=(0, 0, 0))
    for i, ln in enumerate(lines):
        tw = draw.textlength(ln, font=size)
        draw.text(((W - tw) / 2, y + i * lh), ln, font=size, fill=color)


def corner_label(draw, text, size=F_TINY):
    """Watermark for this layout test only - sits in the very bottom margin."""
    tw = draw.textlength(text, font=size)
    draw.text(((W - tw) / 2, H - 26), text, font=size, fill=(120, 128, 142))


def bg(img, top=INK, bottom=DEEP):
    d = ImageDraw.Draw(img)
    for i in range(H):
        t = i / H
        d.line([(0, i), (W, i)],
               fill=tuple(int(lerp(top[c], bottom[c], t)) for c in range(3)))


def map_block(d, yline, land_h=0.20, scale=1.0, peninsula=True, water_bottom=0.72):
    """Schematic map: header band + Canada land + water + border line + optional peninsula.

    Layout is deliberately stacked for 9:16 so on-screen text never sits on busy pixels.
    """
    y = int(yline)
    wb = int(H * water_bottom)
    d.rectangle([0, 0, W, y - int(H * land_h * scale)], fill=INK)          # header band
    d.rectangle([0, y - int(H * land_h * scale), W, y], fill=LAND)         # Canada land
    d.rectangle([0, y - 4, W, y + 2], fill=LAND_DK)
    d.rectangle([0, y, W, wb], fill=WATER)                                 # water
    for i in range(int(y) + 2, wb):                                        # subtle depth
        t = (i - y) / max(1, wb - y)
        d.line([(0, i), (W, i)], fill=tuple(int(lerp(WATER[c], WATER_DK[c], t * 0.5)) for c in range(3)))
    pts = [(0, y), (90, y - 5), (180, y + 3), (270, y - 4), (360, y + 2), (450, y - 3), (W, y + 1)]
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=WHITE, width=7)
        d.line([(pts[i][0], pts[i][1] + 22), (pts[i + 1][0], pts[i + 1][1] + 22)],
               fill=(232, 228, 214), width=4)
    if peninsula:
        poly = [(W * 0.52, y + 8), (W * 0.80, y + 4), (W * 0.82, y + 112),
                (W * 0.66, y + 128), (W * 0.52, y + 92)]
        d.polygon(poly, fill=GREEN, outline=WHITE)
        d.line([(W * 0.80, y + 4), (W * 0.82, y + 150)], fill=RED, width=6)


def hex_pin(d, x, y, label="US", color=RED):
    d.ellipse([x - 46, y - 46, x + 46, y + 46], outline=color, width=6)
    tw = d.textlength(label, font=F_SM)
    d.text((x - tw / 2, y - 14), label, font=F_SM, fill=WHITE)


def route(d, pts, progress, color=RED):
    n = len(pts) - 1
    draw_to = progress * n
    for i in range(n):
        if draw_to <= i:
            break
        a, b = pts[i], pts[i + 1]
        t = min(1.0, draw_to - i)
        d.line([a, (lerp(a[0], b[0], t), lerp(a[1], b[1], t))], fill=color, width=8)
    # moving dot
    idx = min(n - 1, int(draw_to))
    t = min(1.0, draw_to - idx)
    a, b = pts[idx], pts[idx + 1]
    cx, cy = lerp(a[0], b[0], t), lerp(a[1], b[1], t)
    d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=WHITE)


# ---------------------------------------------------------------- beats
# (start, end, caption, scene)  -- 58s total, cut for sound-off viewing
BEATS = [
    (0.0, 3.0, "This is Point Roberts.", "map_full"),
    (3.0, 7.0, "It's in the United States.", "pin"),
    (7.0, 12.0, "You cannot drive to it from the United States.", "isolate"),
    (12.0, 20.0, "In 1846 they drew the US-Canada border straight through this peninsula.", "line_split"),
    (20.0, 28.0, "Everything below the line became America. Everything above stayed Canada.", "split_colour"),
    (28.0, 36.0, "So the American part became an island — made of a line, not water.", "island"),
    (36.0, 44.0, "About 1,000 people live there. School means 4 border crossings a day.", "route"),
    (44.0, 50.0, "Dentist. Hardware store. Hospital. All of it means leaving the country.", "icons"),
    (50.0, 58.0, "Nobody fought a war over this. Someone just drew a line.", "card"),
]
TOTAL = BEATS[-1][1]


def frame(t):
    img = Image.new("RGB", (W, H), INK)
    bg(img)
    d = ImageDraw.Draw(img)
    beat = next((b for b in BEATS if b[0] <= t < b[1]), BEATS[-1])
    s, e, cap, scene = beat
    p = ease((t - s) / max(0.001, (e - s)))

    yline = int(H * 0.42)
    LH = 0.20          # land band height (fraction of H) - keeps the map under the headline
    SAFE = W - 80

    if scene == "map_full":
        map_block(d, yline, land_h=LH, peninsula=False)
        corner_label(d, "STYLE TEST  ·  9:16  ·  58s  ·  not final art")
        d.text((40, int(H * 0.045)), "POINT", font=fit(d, "POINT", 76, SAFE), fill=WHITE)
        d.text((40, int(H * 0.045) + 84), "ROBERTS", font=fit(d, "ROBERTS", 76, SAFE), fill=RED)
        d.text((42, int(H * 0.14) + 190), "WASHINGTON, USA", font=F_TINY, fill=GREY)

    elif scene == "pin":
        map_block(d, yline, land_h=LH)
        hex_pin(d, int(W * 0.62), yline + 96)
        d.text((40, int(H * 0.045)), "THE US", font=fit(d, "THE US", 70, SAFE), fill=WHITE)
        d.text((42, yline + 200), "CANADA ABOVE THE LINE", font=F_TINY, fill=(240, 236, 226))

    elif scene == "isolate":
        map_block(d, yline, land_h=LH)
        bx, by = int(W * 0.80), yline + 78
        k = int(30 * (0.5 + 0.5 * math.sin(t * 6)))
        d.line([(bx - k, by - k), (bx + k, by + k)], fill=RED, width=9)
        d.line([(bx - k, by + k), (bx + k, by - k)], fill=RED, width=9)
        d.text((36, int(H * 0.045)), "NO ROAD IN", font=fit(d, "NO ROAD IN", 70, SAFE), fill=WHITE)
        d.text((38, int(H * 0.045) + 82), "FROM THE US", font=F_MID, fill=RED)

    elif scene == "line_split":
        map_block(d, yline, land_h=LH, peninsula=True)
        x = int(lerp(0, W, p))
        d.line([(0, yline), (x, yline)], fill=RED, width=12)
        d.text((36, int(H * 0.045)), "1846", font=fit(d, "1846", 76, SAFE), fill=WHITE)
        d.text((38, int(H * 0.045) + 86), "THE 49TH PARALLEL", font=F_SM, fill=GREY)

    elif scene == "split_colour":
        map_block(d, yline, land_h=LH, peninsula=True)
        d.rectangle([0, yline - int(H * LH), W, yline], fill=(122, 96, 76))
        d.rectangle([0, yline + 2, W, int(H * 0.62)], fill=(24, 62, 100))
        poly = [(W * 0.52, yline + 8), (W * 0.80, yline + 4), (W * 0.82, yline + 112),
                (W * 0.66, yline + 128), (W * 0.52, yline + 92)]
        d.polygon(poly, fill=GREEN, outline=WHITE)
        d.text((36, yline - 70), "CANADA", font=F_SM, fill=(245, 240, 230))
        d.text((36, yline + 210), "UNITED STATES", font=F_SM, fill=WHITE)

    elif scene == "island":
        map_block(d, yline, land_h=LH)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 130))
        od = ImageDraw.Draw(ov)
        poly = [(W * 0.52, yline + 8), (W * 0.80, yline + 4), (W * 0.82, yline + 112),
                (W * 0.66, yline + 128), (W * 0.52, yline + 92)]
        od.polygon(poly, fill=(0, 0, 0, 0))
        img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"), (0, 0))
        d = ImageDraw.Draw(img)
        d.polygon(poly, outline=RED, width=4)
        d.text((36, int(H * 0.045)), "AN ISLAND", font=fit(d, "AN ISLAND", 74, SAFE), fill=WHITE)
        d.text((38, int(H * 0.045) + 84), "MADE OF A LINE", font=F_SM, fill=RED)

    elif scene == "route":
        map_block(d, yline, land_h=LH)
        pts = [(int(W * 0.60), yline + 90), (int(W * 0.60), yline - 46),
               (int(W * 0.86), yline - 46), (int(W * 0.88), yline + 70)]
        route(d, pts, p)
        d.text((32, int(H * 0.045)), "4 CROSSINGS", font=fit(d, "4 CROSSINGS", 72, SAFE), fill=WHITE)
        d.text((34, int(H * 0.045) + 80), "ONE SCHOOL DAY", font=F_SM, fill=RED)

    elif scene == "icons":
        items = ["DENTIST", "HARDWARE", "HOSPITAL"]
        y0, step, hgt = 262, 96, 76
        tw = d.textlength("PASSPORT", font=F_TINY)
        for i, name in enumerate(items):
            k = ease(p * 3 - i)
            if k <= 0:
                continue
            top = y0 + i * step
            d.rounded_rectangle([40, top, W - 40, top + hgt], 14,
                                fill=(28, 40, 58), outline=(62, 76, 98))
            room = (W - 40) - 64 - tw - 34          # left pad, right pad, gap
            d.text((64, top + 24), name, font=fit(d, name, 32, room), fill=WHITE)
            d.text((W - 64 - tw, top + 28), "PASSPORT", font=F_TINY, fill=(255, 128, 118))
        d.text((40, int(H * 0.11)), "ALL OF IT", font=fit(d, "ALL OF IT", 68, SAFE), fill=WHITE)
        d.text((42, int(H * 0.11) + 84), "MEANS LEAVING THE COUNTRY", font=F_TINY, fill=(255, 128, 118))

    else:  # card
        d.rectangle([0, int(H * 0.33), W, int(H * 0.33) + 6], fill=RED)
        d.text((40, int(H * 0.14)), "LINES", font=fit(d, "LINES", 78, SAFE), fill=WHITE)
        d.text((40, int(H * 0.14) + 92), "ON A MAP", font=fit(d, "ON A MAP", 78, SAFE), fill=RED)
        d.text((42, int(H * 0.14) + 196), "EP 01  ·  one map every two weeks", font=F_TINY, fill=GREY)

    caption(img, d, cap)
    # progress bar (layout only, not part of the final video)
    d.rectangle([0, H - 8, int(W * (t / TOTAL)), H - 4], fill=(72, 82, 98))
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fps", type=int, default=12)
    ap.add_argument("--keep-frames", action="store_true")
    a = ap.parse_args()

    out = Path(__file__).parent / "s1_animatic_v20.mp4"
    frames = Path(__file__).parent / "frames_s1"
    if frames.exists():
        shutil.rmtree(frames)
    frames.mkdir()

    n = int(TOTAL * a.fps)
    for i in range(n):
        frame(i / a.fps).save(frames / f"f{i:04d}.png")
    frame(1.0).save(Path(__file__).parent / "s1_poster.png")

    try:
        sys.path.insert(0, "/home/user/.docvenv/lib/python3.11/site-packages")
        import imageio_ffmpeg
        ff = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        ff = shutil.which("ffmpeg")
    if not ff:
        raise SystemExit("no ffmpeg available; frames kept in frames_s1/")

    subprocess.run([ff, "-y", "-loglevel", "error", "-framerate", str(a.fps),
                    "-i", str(frames / "f%04d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                    str(out)], check=True)
    print(f"wrote {out} ({out.stat().st_size/1e6:.2f} MB, {n} frames @ {a.fps}fps, {TOTAL}s)")
    if not a.keep_frames:
        shutil.rmtree(frames)


if __name__ == "__main__":
    main()
