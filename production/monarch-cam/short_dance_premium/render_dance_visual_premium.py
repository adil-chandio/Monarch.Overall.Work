#!/usr/bin/env python3
"""Render the PREMIUM 24-second albatross-dance vertical Short (picture only).

Same locked 24 s / 720 frames / 13 scenes / 16 cues as the delivered original,
with a cinematic split-tone grade, larger rounded action window, subtle grain and
vignette, kinetic caption, macro detail inset, audition progress, loop crossfade
and exact-text thumbnails. No change to narration, source windows or duration.
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "production/monarch-cam/short_dance_premium"
WORK = ROOT / "production/monarch-cam/work/short_dance_premium"
REVIEW = BASE / "review"
SOURCE = WORK / "media" / "laysan_albatross_dance.mp4"
OUT = WORK / "dance_silent_premium.mp4"
SPEC = json.loads((BASE / "dance_short_spec.json").read_text())
W, H, FPS = SPEC["width"], SPEC["height"], SPEC["fps"]
DURATION = float(SPEC["duration"])
N_FRAMES = int(SPEC["frame_count"])
VIS = SPEC["visual"]["premium"]
ACTION_X, ACTION_Y, ACTION_W, ACTION_H = VIS["action_window"]
RADIUS = int(VIS["action_corner_radius"])
FONT_DIR = ROOT / "public/showreel/fonts"
SYSTEM_FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FONT_FILES = {
    "Montserrat-Bold": [FONT_DIR / "Manrope-800.ttf", FONT_DIR / "Anton-Regular.ttf"],
    "DejaVuSansMono": [FONT_DIR / "IBMPlexMono-400.ttf", SYSTEM_FONT_DIR / "DejaVuSansMono.ttf"],
    "DejaVuSans": [FONT_DIR / "Manrope-700.ttf", SYSTEM_FONT_DIR / "DejaVuSans.ttf"],
    "DejaVuSans-Bold": [SYSTEM_FONT_DIR / "DejaVuSans-Bold.ttf", FONT_DIR / "Manrope-800.ttf"],
}
BG = (7, 13, 22)
WHITE = (247, 247, 242)
MUTED = (177, 190, 198)
TEAL = (99, 215, 200)
CORAL = (255, 138, 101)
CARD = (8, 16, 26, 238)
ACCENT_FRAMES = set(SPEC.get("pattern_interrupts", []))
INSET_X, INSET_Y, INSET_W, INSET_H = VIS["detail_inset"]

# Cached premium finishing layers: one allocation each, not per frame.
ROUNDED_MASK = Image.new("L", (ACTION_W, ACTION_H), 0)
ImageDraw.Draw(ROUNDED_MASK).rounded_rectangle(
    (0, 0, ACTION_W - 1, ACTION_H - 1), radius=RADIUS, fill=255
)
SHADOW = Image.new("RGBA", (ACTION_W + 40, ACTION_H + 40), (0, 0, 0, 0))
ImageDraw.Draw(SHADOW, "RGBA").rounded_rectangle(
    (20, 20, ACTION_W + 20, ACTION_H + 20), radius=RADIUS, fill=(0, 0, 0, 155)
)
SHADOW = SHADOW.filter(ImageFilter.GaussianBlur(18))
CIRCLE_MASK = Image.new("L", (INSET_W, INSET_H), 0)
ImageDraw.Draw(CIRCLE_MASK).ellipse((0, 0, INSET_W - 1, INSET_H - 1), fill=255)
GRAIN_TILE = np.random.default_rng(20261107).standard_normal((256, 256)).astype(np.float32)
_yy, _xx = np.ogrid[:ACTION_H, :ACTION_W]
_cx, _cy = ACTION_W / 2.0, ACTION_H / 2.0
_r = np.sqrt(((_xx - _cx) / _cx) ** 2 + ((_yy - _cy) / _cy) ** 2) / np.sqrt(2.0)
VIGNETTE = (1.0 - float(VIS["vignette_strength"]) * np.clip(_r, 0.0, 1.0) ** 2).astype(np.float32)


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def font(name: str, size: int):
    candidates = FONT_FILES.get(name, [FONT_DIR / f"{name}.ttf", SYSTEM_FONT_DIR / f"{name}.ttf"])
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    raise FileNotFoundError(f"No usable font for {name}; checked {[str(x) for x in candidates]}")


def fit_font(draw: ImageDraw.ImageDraw, text: str, name: str, start: int, max_width: int, minimum: int = 34, spacing: int = 10):
    for size in range(start, minimum - 1, -2):
        candidate = font(name, size)
        box = draw.multiline_textbbox((0, 0), text, font=candidate, spacing=spacing, align="center")
        if box[2] - box[0] <= max_width:
            return candidate
    return font(name, minimum)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, face, max_width: int):
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and draw.textlength(candidate, font=face) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return "\n".join(lines)


def smoothstep(p: float):
    p = float(np.clip(p, 0.0, 1.0))
    return p * p * (3.0 - 2.0 * p)


def source_content(frame: np.ndarray):
    """The USFWS source is 16:9; keep the full frame, no 4:3 pillar-bar crop."""
    return frame


def grade(frame: np.ndarray):
    """Gentle base lift for the blurred vertical background."""
    lut = np.clip((np.arange(256) / 255.0) ** 0.92 * 255, 0, 255).astype(np.uint8)
    lifted = cv2.LUT(frame, lut)
    return cv2.convertScaleAbs(lifted, alpha=1.035, beta=-3)


def cinema_grade(frame: np.ndarray):
    """Restrained split-tone S-curve plus a shape-aware vignette."""
    x = frame.astype(np.float32) / 255.0
    x = np.clip((x - 0.5) * 1.07 + 0.5, 0.0, 1.0)
    luma = x.mean(axis=2)
    shadows = np.clip((0.42 - luma) / 0.42, 0.0, 1.0)
    highlights = np.clip((luma - 0.62) / 0.38, 0.0, 1.0)
    # BGR: cool the shadows slightly, warm the highlights slightly.
    x[..., 0] += 0.018 * shadows - 0.010 * highlights
    x[..., 1] += 0.008 * shadows + 0.004 * highlights
    x[..., 2] += 0.006 * shadows + 0.022 * highlights
    x = np.clip(x, 0.0, 1.0)
    h, w = x.shape[:2]
    yy, xx = np.ogrid[:h, :w]
    cx, cy = w / 2.0, h / 2.0
    r = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2) / np.sqrt(2.0)
    vignette = (1.0 - float(VIS["vignette_strength"]) * np.clip(r, 0.0, 1.0) ** 2).astype(np.float32)
    x *= vignette[..., None]
    return (np.clip(x, 0.0, 1.0) * 255.0).astype(np.uint8)


def add_grain(main: np.ndarray, frame_index: int):
    g = np.roll(GRAIN_TILE, (frame_index % 256, (frame_index * 7) % 256), axis=(0, 1))
    g = cv2.resize(g, (ACTION_W, ACTION_H), interpolation=cv2.INTER_LINEAR)
    return np.clip(main.astype(np.float32) + g * float(VIS["grain_amplitude"]), 0, 255).astype(np.uint8)


def crop_action(content: np.ndarray, zoom: float, focus: float):
    h, w = content.shape[:2]
    cw, ch = max(160, int(w / zoom)), max(120, int(h / zoom))
    cx = float(np.clip(focus, 0.0, 1.0)) * w
    cy = h * 0.50
    x0 = int(np.clip(round(cx - cw / 2), 0, w - cw))
    y0 = int(np.clip(round(cy - ch / 2), 0, h - ch))
    return content[y0:y0 + ch, x0:x0 + cw]


def vertical_background(content: np.ndarray, focus: float):
    scale = H / content.shape[0]
    enlarged = cv2.resize(content, (int(round(content.shape[1] * scale)), H), interpolation=cv2.INTER_CUBIC)
    center = int(round(float(focus) * enlarged.shape[1]))
    left = int(np.clip(center - W // 2, 0, enlarged.shape[1] - W))
    bg = enlarged[:, left:left + W]
    bg = cv2.GaussianBlur(bg, (0, 0), 32)
    bg = np.clip(bg.astype(np.float32) * 0.40, 0, 255).astype(np.uint8)
    bg = np.clip(bg.astype(np.float32) + np.array([4.0, 2.0, -2.0], np.float32), 0, 255).astype(np.uint8)
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    edge = 0.60 + 0.40 * np.minimum(1.0, np.minimum(yy / 0.23, (1.0 - yy) / 0.24))
    return np.clip(bg.astype(np.float32) * edge, 0, 255).astype(np.uint8)


def draw_brand(draw: ImageDraw.ImageDraw):
    draw.ellipse((52, 56, 60, 64), fill=TEAL)
    draw.text((72, 48), "MONARCH CAM", font=font("Montserrat-Bold", 29), fill=WHITE, stroke_width=1, stroke_fill=(0, 0, 0))
    label = "REAL USFWS FOOTAGE / MIDWAY ATOLL"
    face = font("DejaVuSansMono", 21)
    width = draw.textlength(label, font=face)
    draw.text((W - 64 - width, 55), label, font=face, fill=MUTED)


def draw_top(base: Image.Image, text: str, scene_index: int):
    draw = ImageDraw.Draw(base, "RGBA")
    kicker = f"FIELD NOTE {scene_index + 1:02d} / {len(SPEC['scenes']):02d}"
    draw.text((64, 112), kicker, font=font("DejaVuSansMono", 20), fill=(*TEAL, 210))
    draw.line((64, 142, W - 64, 142), fill=(255, 255, 255, 26), width=2)
    face = fit_font(draw, text, "Montserrat-Bold", 82, 950, 44, 8)
    lines = text.split("\n")
    spacing = 8
    box = draw.multiline_textbbox((0, 0), text, font=face, spacing=spacing, align="center")
    y = 158 - box[1]
    for index, line in enumerate(lines):
        line_box = draw.textbbox((0, 0), line, font=face)
        line_w = line_box[2] - line_box[0]
        x = (W - line_w) / 2
        color = CORAL if index == len(lines) - 1 else WHITE
        draw.text((x + 3, y + 4), line, font=face, fill=(0, 0, 0, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
        draw.text((x, y), line, font=face, fill=(*color, 255), stroke_width=1, stroke_fill=(0, 0, 0, 255))
        y += (line_box[3] - line_box[1]) + spacing + 12
    draw.line((W / 2 - 70, 262, W / 2 + 70, 262), fill=(*CORAL, 170), width=3)


def active_caption(t: float):
    narration = SPEC["narration"]
    for i, item in enumerate(narration):
        end = narration[i + 1]["start"] - 0.06 if i + 1 < len(narration) else DURATION
        if item["start"] <= t < end:
            return {"text": item["caption"], "start": item["start"], "end": end, "index": i}
    return None


def draw_caption(base: Image.Image, info: dict | None, t: float):
    if not info:
        return
    draw = ImageDraw.Draw(base, "RGBA")
    age = max(0.0, t - info["start"])
    fade = smoothstep(age / 0.14)
    alpha = int(230 * fade)
    if alpha <= 0:
        return
    y0 = int(VIS["caption_y"] + (1.0 - fade) * 16)
    chosen, wrapped = None, None
    for size in range(64, 43, -2):
        candidate = font("Montserrat-Bold", size)
        candidate_wrapped = wrap_text(draw, info["text"], candidate, 920)
        if len(candidate_wrapped.split("\n")) <= 2:
            chosen, wrapped = candidate, candidate_wrapped
            break
    if chosen is None:
        chosen = font("Montserrat-Bold", 44)
        wrapped = wrap_text(draw, info["text"], chosen, 920)
    box = draw.multiline_textbbox((0, 0), wrapped, font=chosen, spacing=12, align="center", stroke_width=1)
    tw, th = box[2] - box[0], box[3] - box[1]
    x = (W - tw) / 2
    draw.text((80, y0 - 46), f"NARRATION / {info['index'] + 1:02d}", font=font("DejaVuSansMono", 19), fill=(*TEAL, int(200 * fade)))
    draw.line((80, y0 - 16, W - 80, y0 - 16), fill=(*TEAL, int(55 * fade)), width=2)
    draw.rounded_rectangle((x - 30, y0 - 22, x + tw + 30, y0 + th + 34), radius=22,
                           fill=(2, 6, 11, alpha), outline=(*TEAL, int(90 * fade)), width=2)
    draw.multiline_text((x + 2, y0 + 3), wrapped, font=chosen, fill=(0, 0, 0, alpha), spacing=12,
                        align="center", stroke_width=2, stroke_fill=(0, 0, 0, alpha))
    draw.multiline_text((x, y0), wrapped, font=chosen, fill=(*WHITE, alpha), spacing=12,
                        align="center", stroke_width=1, stroke_fill=(0, 0, 0, alpha))


def draw_dance_card(base: Image.Image, t: float):
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    draw.rounded_rectangle((48, 250, 1032, 326), radius=18, fill=CARD, outline=(*TEAL, 150), width=2)
    draw.text((72, 264), "DANCE CARD", font=font("DejaVuSansMono", 20), fill=MUTED)
    active = sum(1 for step in SPEC["dance_steps"] if t + 1e-6 >= step["time"])
    chips = [(260, "01 BOW"), (520, "02 CLACK"), (780, "03 SKY")]
    for index, (x, label) in enumerate(chips):
        is_active = index + 1 == active
        fill = (*TEAL, 70) if is_active else (255, 255, 255, 12)
        outline = (*TEAL, 230) if is_active else (255, 255, 255, 40)
        draw.rounded_rectangle((x, 258, x + 220, 308), radius=14, fill=fill, outline=outline, width=2)
        color = TEAL if is_active else MUTED
        draw.text((x + 18, 270), label, font=font("DejaVuSansMono", 22), fill=(*color, 255))
        if is_active:
            draw.ellipse((x + 196, 266, x + 208, 278), fill=(*CORAL, 230))
    progress = float(np.clip((t - 5.9) / (10.4 - 5.9), 0.0, 1.0))
    draw.rounded_rectangle((72, 314, 1008, 319), radius=3, fill=(255, 255, 255, 22))
    draw.rounded_rectangle((72, 314, 72 + 936 * progress, 319), radius=3, fill=(*TEAL, 220))
    base.alpha_composite(overlay)


def draw_badge(base: Image.Image, text: str):
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    face = font("Montserrat-Bold", 44)
    width = draw.textlength(text, font=face)
    x0, x1 = (W - width) / 2 - 42, (W + width) / 2 + 42
    draw.rounded_rectangle((x0 - 6, 1104, x1 + 6, 1190), radius=26, fill=(*CORAL, 45))
    draw.rounded_rectangle((x0, 1110, x1, 1184), radius=20, fill=(8, 16, 26, 230), outline=(*CORAL, 230), width=3)
    draw.text(((W - width) / 2 + 2, 1127), text, font=face, fill=(0, 0, 0, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
    draw.text(((W - width) / 2, 1125), text, font=face, fill=(*CORAL, 255))
    base.alpha_composite(overlay)


def paste_action(base: Image.Image, main: np.ndarray, frame_index: int, scene_index: int):
    base.alpha_composite(SHADOW, dest=(ACTION_X - 20, ACTION_Y - 20))
    action = Image.fromarray(cv2.cvtColor(main, cv2.COLOR_BGR2RGB)).convert("RGBA")
    base.paste(action, (ACTION_X, ACTION_Y), ROUNDED_MASK)
    draw = ImageDraw.Draw(base, "RGBA")
    draw.rounded_rectangle((ACTION_X, ACTION_Y, ACTION_X + ACTION_W, ACTION_Y + ACTION_H),
                           radius=RADIUS, outline=(*TEAL, 145), width=2)
    # Fine corner brackets and a restrained footage label.
    c = 34
    for x0, y0, dx, dy in [
        (ACTION_X + 14, ACTION_Y + 14, 1, 1),
        (ACTION_X + ACTION_W - 14, ACTION_Y + 14, -1, 1),
        (ACTION_X + 14, ACTION_Y + ACTION_H - 14, 1, -1),
        (ACTION_X + ACTION_W - 14, ACTION_Y + ACTION_H - 14, -1, -1),
    ]:
        draw.line((x0, y0, x0 + c * dx, y0), fill=(*TEAL, 190), width=3)
        draw.line((x0, y0, x0, y0 + c * dy), fill=(*TEAL, 190), width=3)
    draw.rounded_rectangle((ACTION_X + 18, ACTION_Y + 18, ACTION_X + 270, ACTION_Y + 60), radius=9, fill=(4, 8, 12, 215))
    draw.text((ACTION_X + 30, ACTION_Y + 28), "REAL USFWS FOOTAGE", font=font("DejaVuSansMono", 18), fill=(*MUTED, 255))
    draw.text((ACTION_X + 24, ACTION_Y + ACTION_H - 38), f"TC {frame_index / FPS:05.2f} / NOTE {scene_index + 1:02d}",
              font=font("DejaVuSansMono", 17), fill=(*MUTED, 210))
    if frame_index in ACCENT_FRAMES:
        draw.rounded_rectangle((ACTION_X + 6, ACTION_Y + 6, ACTION_X + ACTION_W - 6, ACTION_Y + ACTION_H - 6),
                               radius=RADIUS, outline=(*CORAL, 185), width=5)
        draw.line((ACTION_X + 40, ACTION_Y + 40, ACTION_X + ACTION_W - 40, ACTION_Y + 40),
                  fill=(*TEAL, 135), width=3)


def draw_detail_inset(base: Image.Image, content: np.ndarray, focus: float):
    detail = crop_action(content, 1.85, min(0.78, max(0.22, focus + 0.12)))
    detail = cv2.resize(detail, (INSET_W, INSET_H), interpolation=cv2.INTER_CUBIC)
    detail = cinema_grade(detail)
    detail = np.clip(detail.astype(np.float32) * 0.92, 0, 255).astype(np.uint8)
    img = Image.fromarray(cv2.cvtColor(detail, cv2.COLOR_BGR2RGB)).convert("RGBA")
    img.putalpha(CIRCLE_MASK)
    base.alpha_composite(img, (INSET_X, INSET_Y))
    draw = ImageDraw.Draw(base, "RGBA")
    draw.ellipse((INSET_X, INSET_Y, INSET_X + INSET_W, INSET_Y + INSET_H), outline=(*TEAL, 195), width=3)
    draw.text((INSET_X, INSET_Y + INSET_H + 10), "MACRO / DETAIL", font=font("DejaVuSansMono", 18), fill=(*MUTED, 255))


def draw_progress(base: Image.Image, t: float, scene_index: int):
    draw = ImageDraw.Draw(base, "RGBA")
    y = int(VIS["progress_y"])
    draw.line((80, y, 1000, y), fill=(65, 78, 88, 255), width=3)
    progress = float(np.clip(t / DURATION, 0.0, 1.0))
    draw.line((80, y, 80 + 920 * progress, y), fill=(*TEAL, 255), width=5)
    for i, scene in enumerate(SPEC["scenes"]):
        x = 80 + 920 * (scene["start"] / DURATION)
        color = (*TEAL, 255) if i == scene_index else (80, 92, 102, 255)
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=color)
    face = font("DejaVuSansMono", 20)
    draw.text((80, y + 18), f"AUDITION / NOTE {scene_index + 1:02d}", font=face, fill=(*MUTED, 255))
    right = f"{t:05.2f} / {DURATION:05.2f}"
    draw.text((1000 - draw.textlength(right, font=face), y + 18), right, font=face, fill=(*MUTED, 255))


def draw_footer(draw: ImageDraw.ImageDraw):
    tag = "WATCH  /  LAUGH  /  LEARN"
    face = font("DejaVuSansMono", 23)
    width = draw.textlength(tag, font=face)
    draw.text(((W - width) / 2, 1860), tag, font=face, fill=MUTED)


def make_exact_thumbnails(hook_bgr: np.ndarray):
    base = Image.fromarray(cv2.cvtColor(hook_bgr, cv2.COLOR_BGR2RGB)).convert("RGBA")
    cv2.imwrite(str(REVIEW / "cover_hook.jpg"), hook_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
    outputs = []

    def render_text(text: str, filename: str):
        img = base.copy()
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay, "RGBA")
        draw.rectangle((0, 0, W, 520), fill=(2, 8, 14, 176))
        draw.line((80, 500, 1000, 500), fill=(*TEAL, 190), width=3)
        draw.text((64, 48), "MONARCH CAM", font=font("Montserrat-Bold", 29), fill=(*WHITE, 255))
        draw.text((64, 112), "LAYSAN ALBATROSS / DANCE AUDITION", font=font("DejaVuSansMono", 20), fill=(*TEAL, 220))
        face = fit_font(draw, text, "Montserrat-Bold", 92, 940, 50, 8)
        box = draw.multiline_textbbox((0, 0), text, font=face, spacing=8, align="center")
        tw, th = box[2] - box[0], box[3] - box[1]
        x, y = (W - tw) / 2, 180 - box[1]
        draw.multiline_text((x + 3, y + 4), text, font=face, fill=(0, 0, 0, 255), spacing=8,
                            align="center", stroke_width=2, stroke_fill=(0, 0, 0, 255))
        draw.multiline_text((x, y), text, font=face, fill=(*CORAL, 255), spacing=8,
                            align="center", stroke_width=1, stroke_fill=(0, 0, 0, 255))
        img.alpha_composite(overlay)
        path = REVIEW / filename
        img.convert("RGB").save(path, quality=95)
        outputs.append({"file": path.name, "text": text, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "bytes": path.stat().st_size})

    render_text(VIS["exact_cover_text"], "cover.jpg")
    render_text(VIS["exact_cover_ab_text"], "cover_WOULD_YOU_PASS.jpg")
    save_json(REVIEW / "exact_thumbnail_manifest.json", {
        "hook_frame_reference": "cover_hook.jpg",
        "hook_frame_text": "NOT A FIGHT.",
        "primary": VIS["exact_cover_text"],
        "ab": VIS["exact_cover_ab_text"],
        "outputs": outputs,
        "note": "Exact-text thumbnails are generated from the 0.07 s hook frame; no separate human thumbnail review occurred."
    })


def render():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Retrieve the cleared USFWS source first: {SOURCE}")
    WORK.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium",
        "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT)
    ]
    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    ledger = []
    sampled_luma = []
    hook_captured = False
    hook_frame = None
    global_first_content = None
    for scene_index, scene in enumerate(SPEC["scenes"]):
        start_frame = int(round(scene["start"] * FPS))
        end_frame = int(round(scene["end"] * FPS))
        cap = cv2.VideoCapture(str(SOURCE))
        source_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        scene_rate = float(scene.get("rate", 1.0))
        source_start_frame = int(round(scene["source_start"] * source_fps))
        cap.set(cv2.CAP_PROP_POS_FRAMES, source_start_frame)
        ok, first = cap.read()
        if not ok:
            raise RuntimeError(f"Cannot read {scene['id']} at {scene['source_start']}s")
        first_content = grade(source_content(first))
        if global_first_content is None:
            global_first_content = first_content.copy()
        background = vertical_background(first_content, scene.get("focus", 0.5))
        layout = scene.get("layout", "footage")
        raw = first
        current_source_offset = 0
        for frame_index in range(start_frame, end_frame):
            local_index = frame_index - start_frame
            t = frame_index / FPS
            desired_source_offset = int(round(local_index * scene_rate))
            if desired_source_offset != current_source_offset:
                step = desired_source_offset - current_source_offset
                if step < 0 or step > 8:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, source_start_frame + desired_source_offset)
                    ok, candidate = cap.read()
                    raw = candidate if ok else first
                else:
                    for _ in range(step):
                        ok, candidate = cap.read()
                        raw = candidate if ok else first
                current_source_offset = desired_source_offset
            content = grade(source_content(raw))
            if scene.get("loop_to_start_last") and global_first_content is not None:
                remaining = (end_frame - frame_index) / FPS
                if remaining <= scene["loop_to_start_last"]:
                    blend = smoothstep(1.0 - remaining / scene["loop_to_start_last"])
                    content = cv2.addWeighted(content, 1.0 - blend, global_first_content, blend, 0)
            progress = local_index / max(1, end_frame - start_frame - 1)
            ep = smoothstep(progress)
            zoom = scene.get("zoom_start", 1.18) * (1 - ep) + scene.get("zoom_end", 1.32) * ep
            drift = 0.018 * math.sin(2 * math.pi * (t / DURATION) * 1.5 + scene_index)
            focus_eff = float(np.clip(scene.get("focus", 0.5) + drift, 0.0, 1.0))
            action = crop_action(content, zoom, focus_eff)
            main = cv2.resize(action, (ACTION_W, ACTION_H), interpolation=cv2.INTER_CUBIC)
            main = np.clip(main.astype(np.float32) * 1.22 - cv2.GaussianBlur(main, (0, 0), 1.0).astype(np.float32) * 0.22,
                           0, 255).astype(np.uint8)
            if layout == "mirror_split":
                mirrored = cv2.flip(main, 1)
                main = cv2.addWeighted(main, 0.5, mirrored, 0.5, 0)
            main = cinema_grade(main)
            if layout == "mirror_split":
                cv2.line(main, (ACTION_W // 2, 0), (ACTION_W // 2, ACTION_H), TEAL, 3, cv2.LINE_AA)
            main = add_grain(main, frame_index)

            base = Image.fromarray(cv2.cvtColor(background, cv2.COLOR_BGR2RGB)).convert("RGBA")
            paste_action(base, main, frame_index, scene_index)
            draw_detail_inset(base, content, focus_eff)
            if scene.get("card_step"):
                draw_dance_card(base, t)
            if scene.get("badge"):
                draw_badge(base, scene["badge"])
            draw_top(base, scene["top"], scene_index)
            draw_caption(base, active_caption(t), t)
            draw_progress(base, t, scene_index)
            flat = ImageDraw.Draw(base)
            draw_brand(flat)
            draw_footer(flat)
            final = cv2.cvtColor(np.asarray(base.convert("RGB")), cv2.COLOR_RGB2BGR)
            proc.stdin.write(final.tobytes())
            if not hook_captured and frame_index >= 2:
                hook_frame = final.copy()
                hook_captured = True
            if frame_index % 60 == 0:
                sampled_luma.append({"frame": frame_index, "time": round(t, 3),
                                     "mean_luma": round(float(cv2.cvtColor(final, cv2.COLOR_BGR2GRAY).mean()), 3)})
        cap.release()
        ledger.append({
            "id": scene["id"], "timeline_frames": [start_frame, end_frame],
            "timeline_in": round(start_frame / FPS, 6), "timeline_out": round(end_frame / FPS, 6),
            "source_in": scene["source_start"],
            "source_out_approx": round(scene["source_start"] + ((end_frame - start_frame) / FPS) * scene.get("rate", 1.0), 6),
            "rate": scene.get("rate", 1.0), "layout": layout,
            "top": scene["top"], "loop_to_start_last": scene.get("loop_to_start_last", 0),
            "premium_action_window": [ACTION_X, ACTION_Y, ACTION_W, ACTION_H],
            "premium_zoom_easing": "smoothstep", "premium_focus_drift": 0.018
        })
        print(f"Rendered premium {scene['id']} / frames {start_frame}:{end_frame}", flush=True)
    proc.stdin.close()
    code = proc.wait()
    if code:
        raise RuntimeError(f"ffmpeg visual encoder failed: {code}")
    if hook_frame is None:
        raise RuntimeError("Hook frame was not captured")
    save_json(REVIEW / "visual_edit_ledger.json", {
        "source": str(SOURCE.relative_to(ROOT)), "scenes": ledger,
        "premium": {"action_window": [ACTION_X, ACTION_Y, ACTION_W, ACTION_H],
                    "cinema_grade": True, "grain": True, "vignette": True,
                    "detail_inset": [INSET_X, INSET_Y, INSET_W, INSET_H],
                    "loop_crossfade_s": VIS["loop_crossfade_s"]}
    })
    save_json(REVIEW / "visual_sample_qc.json", {
        "expected_frames": N_FRAMES, "sampled_luma": sampled_luma,
        "minimum_sampled_luma": min(x["mean_luma"] for x in sampled_luma),
        "note": "Samples guard against an unintended black render; final stream/frame validation is in technical_qc.json."
    })
    make_exact_thumbnails(hook_frame)
    make_contact_sheet()
    save_json(REVIEW / "visual_premium_qc.json", {
        "cinema_grade": True,
        "split_tone": True,
        "vignette": True,
        "subtle_grain": True,
        "larger_rounded_action_window": True,
        "macro_detail_inset": True,
        "kinetic_caption": True,
        "audition_progress": True,
        "seamless_loop_crossfade": True,
        "exact_text_thumbnails": True,
        "action_window": [ACTION_X, ACTION_Y, ACTION_W, ACTION_H],
        "grain_amplitude": VIS["grain_amplitude"],
        "vignette_strength": VIS["vignette_strength"],
        "loop_crossfade_s": VIS["loop_crossfade_s"],
        "thumbnail_manifest": "review/exact_thumbnail_manifest.json",
        "note": "Frame-by-frame picture enhancements are objective render facts, not human approval or an audience guarantee."
    })
    print(f"Saved premium picture {OUT}", flush=True)


def make_contact_sheet():
    cap = cv2.VideoCapture(str(OUT))
    times = [0.07, 1.45, 2.95, 4.45, 5.95, 7.35, 8.85, 10.45, 12.05, 13.55, 15.15, 16.85, 18.35, 22.0]
    cell_w, cell_h, gap = 270, 480, 14
    sheet = Image.new("RGB", (4 * cell_w + 5 * gap, 4 * (cell_h + 42) + 5 * gap), BG)
    draw = ImageDraw.Draw(sheet)
    for index, t in enumerate(times):
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            continue
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize((cell_w, cell_h), Image.Resampling.LANCZOS)
        col, row = index % 4, index // 4
        x = gap + col * (cell_w + gap)
        y = gap + row * (cell_h + 42 + gap)
        sheet.paste(image, (x, y))
        scene_id = SPEC["scenes"][min(len(SPEC["scenes"]) - 1, next((j for j, s in enumerate(SPEC["scenes"]) if t < s["end"]), len(SPEC["scenes"]) - 1))]["id"]
        label = f"{t:05.2f}s / {scene_id}"
        draw.text((x, y + cell_h + 8), label[:39], font=font("DejaVuSansMono", 14), fill=WHITE)
        cv2.imwrite(str(REVIEW / f"frame_{index + 1:02d}_{t:05.2f}s.jpg"), frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
    cap.release()
    sheet.save(REVIEW / "vertical_contact_sheet.jpg", quality=94)


if __name__ == "__main__":
    render()
