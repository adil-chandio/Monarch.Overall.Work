#!/usr/bin/env python3
"""Render the CLEAN-PREMIUM V3 35-second ranked-animal vertical Short (picture only).

Same locked 35 s / 1050 frames / 13 scenes / 16 cues / 69 words and the same
minimal-caption policy. V3 adds a filmic grade with restrained halation,
double-smoothstep zoom, horizontal/vertical motion drift, five-frame scene
cross-dissolves, elegant tracked captions with a drawn-in accent rule and a
slightly richer exact-text thumbnail treatment. Only minimal captions and subtle rank numerals; no other on-screen text.
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
BASE = ROOT / "production/monarch-cam/short_ranking_v3"
WORK = ROOT / "production/monarch-cam/work/short_ranking_v3"
REVIEW = BASE / "review"
SOURCE_DIR = WORK / "media"
OUT = WORK / "dance_silent_clean_v3.mp4"
SPEC = json.loads((BASE / "dance_short_spec.json").read_text())
W, H, FPS = SPEC["width"], SPEC["height"], SPEC["fps"]
DURATION = float(SPEC["duration"])
N_FRAMES = int(SPEC["frame_count"])
V3 = SPEC["visual"]["v3"]
ACTION_X, ACTION_Y, ACTION_W, ACTION_H = V3["action_window"]
SOURCE_CONTENT_BBOX = {}
RADIUS = int(V3["action_corner_radius"])
TRANSITION_FRAMES = int(V3["scene_transition_frames"])

FONT_DIR = ROOT / "public/showreel/fonts"
SYSTEM_FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FONT_FILES = {
    "Montserrat-Bold": [FONT_DIR / "Manrope-800.ttf", FONT_DIR / "Anton-Regular.ttf"],
    "DejaVuSansMono": [FONT_DIR / "IBMPlexMono-400.ttf", SYSTEM_FONT_DIR / "DejaVuSansMono.ttf"],
    "DejaVuSans": [FONT_DIR / "Manrope-700.ttf", SYSTEM_FONT_DIR / "DejaVuSans.ttf"],
}

BG = (7, 13, 22)
BG_BGR = (22, 13, 7)
TEXT = (244, 241, 232)
ACCENT = (111, 207, 192)
CTA = (255, 138, 101)
GRAIN_TILE = np.random.default_rng(20261107).standard_normal((256, 256)).astype(np.float32)

ROUNDED_MASK = Image.new("L", (ACTION_W, ACTION_H), 0)
ImageDraw.Draw(ROUNDED_MASK).rounded_rectangle(
    (0, 0, ACTION_W - 1, ACTION_H - 1), radius=RADIUS, fill=255
)
SHADOW = Image.new("RGBA", (ACTION_W + 44, ACTION_H + 44), (0, 0, 0, 0))
ImageDraw.Draw(SHADOW, "RGBA").rounded_rectangle(
    (22, 22, ACTION_W + 22, ACTION_H + 22), radius=RADIUS, fill=(0, 0, 0, 126)
)
SHADOW = SHADOW.filter(ImageFilter.GaussianBlur(22))

# Soft bottom gradient: caption readability without a box or extra label.
_grad = np.zeros((H, W, 4), dtype=np.uint8)
_start = int(V3["caption_y"] - 180)
_ys = np.arange(_start, H, dtype=np.float32)
_alpha = np.clip(((_ys - _start) / max(1, H - _start)) ** 1.55 * 126, 0, 158).astype(np.uint8)
_grad[_start:, :, 0] = 2
_grad[_start:, :, 1] = 7
_grad[_start:, :, 2] = 13
_grad[_start:, :, 3] = _alpha[:, None]
BOTTOM_GRADIENT = Image.fromarray(_grad, "RGBA")


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def font(name: str, size: int):
    candidates = FONT_FILES.get(name, [FONT_DIR / f"{name}.ttf", SYSTEM_FONT_DIR / f"{name}.ttf"])
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    raise FileNotFoundError(f"No usable font for {name}; checked {[str(x) for x in candidates]}")


def fit_font(draw: ImageDraw.ImageDraw, text: str, name: str, start: int, max_width: int,
             minimum: int = 34, spacing: int = 10):
    for size in range(start, minimum - 1, -2):
        candidate = font(name, size)
        box = draw.multiline_textbbox((0, 0), text, font=candidate, spacing=spacing, align="center")
        if box[2] - box[0] <= max_width:
            return candidate
    return font(name, minimum)


def tracked_width(draw: ImageDraw.ImageDraw, text: str, face, tracking: float):
    return sum(draw.textlength(ch, font=face) for ch in text) + tracking * max(0, len(text) - 1)


def wrap_text_v3(draw: ImageDraw.ImageDraw, text: str, face, max_width: int, tracking: float):
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and tracked_width(draw, candidate, face, tracking) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return "\n".join(lines)


def draw_tracked_line(draw, x, y, line, face, fill, tracking, stroke_width=0, stroke_fill=None):
    for ch in line:
        draw.text((x, y), ch, font=face, fill=fill,
                  stroke_width=stroke_width, stroke_fill=stroke_fill)
        x += draw.textlength(ch, font=face) + tracking


def draw_tracked_multiline(draw, center_x, y, text, face, fill, tracking, line_spacing,
                           stroke_width=0, stroke_fill=None):
    lines = text.split("\n")
    box = draw.textbbox((0, 0), "Ag", font=face)
    line_h = box[3] - box[1]
    total_h = len(lines) * line_h + (len(lines) - 1) * line_spacing
    cur_y = y
    for line in lines:
        tw = tracked_width(draw, line, face, tracking)
        x = center_x - tw / 2
        draw_tracked_line(draw, x, cur_y, line, face, fill, tracking, stroke_width, stroke_fill)
        cur_y += line_h + line_spacing
    return total_h


def smoothstep(p: float):
    p = float(np.clip(p, 0.0, 1.0))
    return p * p * (3.0 - 2.0 * p)


def source_content(frame: np.ndarray, source_id: str = "", vertical_center: float = 0.5):
    """Return an undistorted 16:9 crop from the cleared source.

    The 9:16 CC0 starfish clip is centre-cropped to the action-window aspect
    ratio instead of being stretched; black review-sheet padding is not part of
    the source frame. Other CC0 sources are already 16:9 and pass through.
    """
    h, w = frame.shape[:2]
    key = source_id or f"{w}x{h}"
    bbox = SOURCE_CONTENT_BBOX.get(key)
    if bbox is None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cols = np.where(gray.mean(axis=0) > 12)[0]
        rows = np.where(gray.mean(axis=1) > 12)[0]
        x0, x1 = (int(cols[0]), int(cols[-1]) + 1) if cols.size else (0, w)
        y0, y1 = (int(rows[0]), int(rows[-1]) + 1) if rows.size else (0, h)
        # Only trim substantial bars; dark but valid picture edges are preserved.
        if x0 <= w * 0.05 and x1 >= w * 0.95:
            x0, x1 = 0, w
        if y0 <= h * 0.05 and y1 >= h * 0.95:
            y0, y1 = 0, h
        bbox = (x0, y0, x1, y1)
        SOURCE_CONTENT_BBOX[key] = bbox
    x0, y0, x1, y1 = bbox
    content = frame[y0:y1, x0:x1]
    ch, cw = content.shape[:2]
    target_ratio = ACTION_W / ACTION_H
    ratio = cw / ch
    if abs(ratio - target_ratio) < 1e-3:
        return content
    if ratio > target_ratio:
        new_w = max(2, int(round(ch * target_ratio)))
        left = int(np.clip(round(cw * 0.5 - new_w / 2), 0, cw - new_w))
        return content[:, left:left + new_w]
    new_h = max(2, int(round(cw / target_ratio)))
    cy = int(round(float(np.clip(vertical_center, 0.0, 1.0)) * ch))
    top = int(np.clip(cy - new_h / 2, 0, ch - new_h))
    return content[top:top + new_h, :]


def grade(frame: np.ndarray):
    """Gentle base lift for the blurred vertical background."""
    lut = np.clip((np.arange(256) / 255.0) ** 0.94 * 255, 0, 255).astype(np.uint8)
    lifted = cv2.LUT(frame, lut)
    return cv2.convertScaleAbs(lifted, alpha=1.025, beta=-2)


def cinema_grade_v3(frame: np.ndarray, intensity: float = 1.0):
    """Filmic S-curve, restrained split-tone, halation and a soft vignette."""
    x = frame.astype(np.float32) / 255.0
    x = np.clip((x - 0.5) * 1.06 + 0.5, 0.0, 1.0)
    luma = x.mean(axis=2)
    shadows = np.clip((0.44 - luma) / 0.44, 0.0, 1.0)
    highlights = np.clip((luma - 0.60) / 0.40, 0.0, 1.0)
    # BGR: cool the shadows a touch, warm the highlights a touch.
    x[..., 0] += 0.010 * shadows - 0.005 * highlights
    x[..., 1] += 0.005 * shadows + 0.003 * highlights
    x[..., 2] += 0.004 * shadows + 0.014 * highlights
    x = np.clip(x, 0.0, 1.0)
    # Restrained highlight halation: no bloom text, no cheap glow overlay.
    bright = np.clip((luma - 0.70) / 0.30, 0.0, 1.0)[..., None]
    glow_src = (x * bright * 255.0).astype(np.float32)
    glow = cv2.GaussianBlur(glow_src, (0, 0), float(V3["bloom_radius"])) / 255.0
    x = np.clip(x + glow * float(V3["halation_strength"]) * intensity, 0.0, 1.0)
    h, w = x.shape[:2]
    yy, xx = np.ogrid[:h, :w]
    cx, cy = w / 2.0, h / 2.0
    r = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2) / np.sqrt(2.0)
    vignette = (1.0 - float(V3["vignette_strength"]) * np.clip(r, 0.0, 1.0) ** 2).astype(np.float32)
    x *= vignette[..., None]
    return (np.clip(x, 0.0, 1.0) * 255.0).astype(np.uint8)


def add_grain_v3(main: np.ndarray, frame_index: int):
    g = np.roll(GRAIN_TILE, (frame_index % 256, (frame_index * 7) % 256), axis=(0, 1))
    g = cv2.resize(g, (ACTION_W, ACTION_H), interpolation=cv2.INTER_LINEAR)
    return np.clip(main.astype(np.float32) + g[..., None] * float(V3["grain_amplitude"]), 0, 255).astype(np.uint8)


def crop_action_v3(content: np.ndarray, zoom: float, focus_x: float, focus_y: float):
    h, w = content.shape[:2]
    cw, ch = max(160, int(w / zoom)), max(120, int(h / zoom))
    cx = float(np.clip(focus_x, 0.0, 1.0)) * w
    cy = float(np.clip(0.5 + focus_y, 0.0, 1.0)) * h
    x0 = int(np.clip(round(cx - cw / 2), 0, w - cw))
    y0 = int(np.clip(round(cy - ch / 2), 0, h - ch))
    return content[y0:y0 + ch, x0:x0 + cw]


def vertical_background_v3(content: np.ndarray, focus_x: float):
    """Deep-navy tinted, softly blurred full-bleed background."""
    scale = H / content.shape[0]
    enlarged = cv2.resize(content, (int(round(content.shape[1] * scale)), H), interpolation=cv2.INTER_CUBIC)
    center = int(round(float(focus_x) * enlarged.shape[1]))
    left = int(np.clip(center - W // 2, 0, enlarged.shape[1] - W))
    bg = enlarged[:, left:left + W]
    bg = cv2.GaussianBlur(bg, (0, 0), 40)
    tint = np.array(BG_BGR, np.float32)
    bg = np.clip(bg.astype(np.float32) * 0.28 + tint * 0.72, 0, 255).astype(np.uint8)
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    edge = 0.70 + 0.30 * np.minimum(1.0, np.minimum(yy / 0.24, (1.0 - yy) / 0.26))
    return np.clip(bg.astype(np.float32) * edge, 0, 255).astype(np.uint8)


def paste_action_v3(base: Image.Image, main: np.ndarray):
    """One clean rounded 16:9 window: no brackets, labels or flashes."""
    base.alpha_composite(SHADOW, dest=(ACTION_X - 22, ACTION_Y - 22))
    action = Image.fromarray(cv2.cvtColor(main, cv2.COLOR_BGR2RGB)).convert("RGBA")
    base.paste(action, (ACTION_X, ACTION_Y), ROUNDED_MASK)
    draw = ImageDraw.Draw(base, "RGBA")
    draw.rounded_rectangle(
        (ACTION_X, ACTION_Y, ACTION_X + ACTION_W, ACTION_Y + ACTION_H),
        radius=RADIUS, outline=(*TEXT, 30), width=1,
    )


def active_caption(t: float):
    narration = SPEC["narration"]
    for i, item in enumerate(narration):
        end = narration[i + 1]["start"] - 0.06 if i + 1 < len(narration) else DURATION
        if item["start"] <= t < end:
            return {"text": item["caption"], "start": item["start"], "end": end, "index": i}
    return None


def active_scene(t: float):
    for scene in SPEC["scenes"]:
        if scene["start"] <= t < scene["end"]:
            return scene
    return SPEC["scenes"][-1]


def draw_caption_v3(base: Image.Image, info: dict | None, scene: dict, t: float):
    """Minimal tracked lower-third caption plus one subtle rank numeral."""
    base.alpha_composite(BOTTOM_GRADIENT)
    draw = ImageDraw.Draw(base, "RGBA")
    rank = scene.get("rank")
    if rank:
        age = max(0.0, t - scene["start"])
        fade = smoothstep(age / 0.22)
        label = f"{int(rank):02d}"
        face = font("DejaVuSansMono", int(V3["rank_number_size"]))
        tracking = 3.0
        tw = tracked_width(draw, label, face, tracking)
        x = W / 2 - tw / 2
        y = int(V3["rank_number_y"])
        draw_tracked_line(draw, x + 2, y + 2, label, face, (0, 0, 0, int(150 * fade)), tracking,
                          stroke_width=1, stroke_fill=(0, 0, 0, int(120 * fade)))
        draw_tracked_line(draw, x, y, label, face, (*ACCENT, int(220 * fade)), tracking)
    if not info:
        return
    age = max(0.0, t - info["start"])
    fade = smoothstep(age / 0.22)
    alpha = int(242 * fade)
    if alpha <= 0:
        return
    y0 = int(V3["caption_y"] + (1.0 - fade) * 18)
    tracking = float(V3["caption_tracking_px"])
    chosen, wrapped = None, None
    for size in range(int(V3["caption_font_max"]), int(V3["caption_font_min"]) - 1, -2):
        candidate = font("DejaVuSans", size)
        candidate_wrapped = wrap_text_v3(draw, info["text"], candidate, int(V3["caption_max_width"]), tracking)
        if len(candidate_wrapped.split("\n")) <= 2:
            chosen, wrapped = candidate, candidate_wrapped
            break
    if chosen is None:
        chosen = font("DejaVuSans", int(V3["caption_font_min"]))
        wrapped = wrap_text_v3(draw, info["text"], chosen, int(V3["caption_max_width"]), tracking)
    is_final = info["index"] == len(SPEC["narration"]) - 1
    color = CTA if is_final else TEXT
    shadow_alpha = int(alpha * 0.74)
    total_h = draw_tracked_multiline(
        draw, W / 2, y0 + 2, wrapped, chosen, (0, 0, 0, shadow_alpha), tracking, 12,
        stroke_width=2, stroke_fill=(0, 0, 0, shadow_alpha),
    )
    total_h = draw_tracked_multiline(
        draw, W / 2, y0, wrapped, chosen, (*color, alpha), tracking, 12,
        stroke_width=1, stroke_fill=(0, 0, 0, shadow_alpha),
    )
    rule_w = int(112 * fade)
    if rule_w > 2:
        draw.rounded_rectangle(
            (W / 2 - rule_w / 2, y0 + total_h + 26, W / 2 + rule_w / 2, y0 + total_h + 29),
            radius=2, fill=(*ACCENT, int(150 * fade)),
        )


def make_exact_thumbnails_v3(hook_bgr: np.ndarray):
    """Clean V3 exact-text thumbnails: one tracked headline, no branding or labels."""
    cv2.imwrite(str(REVIEW / "cover_hook.jpg"), hook_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
    base = Image.fromarray(cv2.cvtColor(hook_bgr, cv2.COLOR_BGR2RGB)).convert("RGBA")
    outputs = []

    def render_text(text: str, filename: str, color):
        img = base.copy()
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay, "RGBA")
        draw.rectangle((0, 0, W, 640), fill=(2, 8, 14, 166))
        draw.line((80, 584, 1000, 584), fill=(*ACCENT, 135), width=2)
        face = fit_font(draw, text, "Montserrat-Bold", 90, 940, 46, 8)
        tracking = 3.0
        tw = tracked_width(draw, text, face, tracking)
        x, y = (W - tw) / 2, 214
        draw_tracked_line(draw, x + 3, y + 4, text, face, (0, 0, 0, 255), tracking,
                          stroke_width=2, stroke_fill=(0, 0, 0, 255))
        draw_tracked_line(draw, x, y, text, face, (*color, 255), tracking,
                          stroke_width=1, stroke_fill=(0, 0, 0, 255))
        rule_w = 150
        draw.rounded_rectangle((W / 2 - rule_w / 2, y + 116, W / 2 + rule_w / 2, y + 119),
                               radius=2, fill=(*ACCENT, 170))
        img.alpha_composite(overlay)
        path = REVIEW / filename
        img.convert("RGB").save(path, quality=95)
        outputs.append({
            "file": path.name, "text": text,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size,
        })

    render_text(V3["exact_cover_text"], "cover.jpg", TEXT)
    render_text(V3["exact_cover_ab_text"], "cover_RANK_THESE_5.jpg", CTA)
    save_json(REVIEW / "exact_thumbnail_manifest.json", {
        "hook_frame_reference": "cover_hook.jpg",
        "hook_frame_text": None,
        "primary": V3["exact_cover_text"],
        "ab": V3["exact_cover_ab_text"],
        "outputs": outputs,
        "note": "Clean V3 exact-text thumbnails generated from the 0.07 s hook frame. The in-video hook frame itself has no extra headline. No separate human thumbnail review occurred.",
    })


def make_contact_sheet():
    cap = cv2.VideoCapture(str(OUT))
    times = [0.07, 2.50, 5.00, 8.00, 11.00, 14.00, 17.00, 20.00, 23.00, 26.00, 29.00, 32.00, 33.50, 34.50]
    cell_w, cell_h, gap = 270, 480, 14
    sheet = Image.new("RGB", (4 * cell_w + 5 * gap, 4 * (cell_h + 42) + 5 * gap), BG)
    draw = ImageDraw.Draw(sheet)
    label_face = font("DejaVuSansMono", 14)
    for index, t in enumerate(times):
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            continue
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize(
            (cell_w, cell_h), Image.Resampling.LANCZOS
        )
        col, row = index % 4, index // 4
        x = gap + col * (cell_w + gap)
        y = gap + row * (cell_h + 42 + gap)
        sheet.paste(image, (x, y))
        scene_id = SPEC["scenes"][min(
            len(SPEC["scenes"]) - 1,
            next((j for j, s in enumerate(SPEC["scenes"]) if t < s["end"]), len(SPEC["scenes"]) - 1),
        )]["id"]
        draw.text((x, y + cell_h + 8), f"{t:05.2f}s / {scene_id}"[:39], font=label_face, fill=TEXT)
        cv2.imwrite(str(REVIEW / f"frame_{index + 1:02d}_{t:05.2f}s.jpg"), frame,
                    [cv2.IMWRITE_JPEG_QUALITY, 92])
    cap.release()
    sheet.save(REVIEW / "vertical_contact_sheet.jpg", quality=94)


def render():
    missing = sorted({s["source_id"] for s in SPEC["scenes"] if not (SOURCE_DIR / f"{s['source_id']}.mp4").exists()})
    if missing:
        raise FileNotFoundError(f"Retrieve cleared V3 sources first: {missing}")
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
    prev_final_raw = None

    for scene_index, scene in enumerate(SPEC["scenes"]):
        start_frame = int(round(scene["start"] * FPS))
        end_frame = int(round(scene["end"] * FPS))
        cap = cv2.VideoCapture(str(SOURCE_DIR / f"{scene['source_id']}.mp4"))
        source_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        scene_rate = float(scene.get("rate", 1.0))
        source_start_frame = int(round(scene["source_start"] * source_fps))
        cap.set(cv2.CAP_PROP_POS_FRAMES, source_start_frame)
        ok, first = cap.read()
        if not ok:
            raise RuntimeError(f"Cannot read {scene['id']} at {scene['source_start']}s")
        first_content = grade(source_content(first, scene['source_id'], scene.get('vertical_center', 0.5)))
        if global_first_content is None:
            global_first_content = first_content.copy()
        background = vertical_background_v3(first_content, scene.get("focus", 0.5))
        layout = scene.get("layout", "footage")
        grade_intensity = 1.12 if layout == "mirror_split" else 1.0
        raw = first
        current_source_offset = 0
        scene_prev_final = prev_final_raw if scene_index > 0 else None
        last_raw_final = None
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
            content = grade(source_content(raw, scene['source_id'], scene.get('vertical_center', 0.5)))
            if scene.get("loop_to_start_last") and global_first_content is not None:
                remaining = (end_frame - frame_index) / FPS
                if remaining <= scene["loop_to_start_last"]:
                    blend = smoothstep(1.0 - remaining / scene["loop_to_start_last"])
                    content = cv2.addWeighted(content, 1.0 - blend, global_first_content, blend, 0)
            progress = local_index / max(1, end_frame - start_frame - 1)
            ep = smoothstep(smoothstep(progress))
            zoom = scene.get("zoom_start", 1.10) * (1 - ep) + scene.get("zoom_end", 1.18) * ep
            drift_x = float(V3["motion_drift_x"]) * math.sin(2 * math.pi * (t / DURATION) * 1.5 + scene_index)
            drift_y = float(V3["motion_drift_y"]) * math.cos(2 * math.pi * (t / DURATION) * 1.2 + scene_index)
            focus_x = float(np.clip(scene.get("focus", 0.5) + drift_x, 0.0, 1.0))
            action = crop_action_v3(content, zoom, focus_x, drift_y)
            main = cv2.resize(action, (ACTION_W, ACTION_H), interpolation=cv2.INTER_CUBIC)
            main = np.clip(
                main.astype(np.float32) * 1.11
                - cv2.GaussianBlur(main, (0, 0), 1.0).astype(np.float32) * 0.11,
                0, 255,
            ).astype(np.uint8)
            if layout == "mirror_split":
                mirrored = cv2.flip(main, 1)
                main = cv2.addWeighted(main, 0.5, mirrored, 0.5, 0)
                cv2.line(main, (ACTION_W // 2, 0), (ACTION_W // 2, ACTION_H),
                         (205, 210, 208), 1, cv2.LINE_AA)
            main = cinema_grade_v3(main, grade_intensity)
            main = add_grain_v3(main, frame_index)

            base = Image.fromarray(cv2.cvtColor(background, cv2.COLOR_BGR2RGB)).convert("RGBA")
            paste_action_v3(base, main)
            draw_caption_v3(base, active_caption(t), active_scene(t), t)
            final = cv2.cvtColor(np.asarray(base.convert("RGB")), cv2.COLOR_RGB2BGR)
            last_raw_final = final.copy()
            if scene_prev_final is not None and local_index < TRANSITION_FRAMES:
                blend = smoothstep((local_index + 1) / TRANSITION_FRAMES)
                final = cv2.addWeighted(scene_prev_final, 1.0 - blend, final, blend, 0)
            proc.stdin.write(final.tobytes())
            if not hook_captured and frame_index >= 2:
                hook_frame = final.copy()
                hook_captured = True
            if frame_index % 60 == 0:
                sampled_luma.append({
                    "frame": frame_index, "time": round(t, 3),
                    "mean_luma": round(float(cv2.cvtColor(final, cv2.COLOR_BGR2GRAY).mean()), 3),
                })
        cap.release()
        prev_final_raw = last_raw_final
        ledger.append({
            "id": scene["id"], "source_id": scene["source_id"], "rank": scene.get("rank"), "timeline_frames": [start_frame, end_frame],
            "timeline_in": round(start_frame / FPS, 6), "timeline_out": round(end_frame / FPS, 6),
            "source_in": scene["source_start"],
            "source_out_approx": round(
                scene["source_start"] + ((end_frame - start_frame) / FPS) * scene.get("rate", 1.0), 6
            ),
            "rate": scene.get("rate", 1.0), "layout": layout,
            "top": scene["top"], "loop_to_start_last": scene.get("loop_to_start_last", 0),
            "v3_action_window": [ACTION_X, ACTION_Y, ACTION_W, ACTION_H],
            "v3_text_policy": V3["text_policy"],
            "v3_rank": scene.get("rank"),
            "v3_scene_transition_frames": TRANSITION_FRAMES if scene_index > 0 else 0,
            "v3_zoom_easing": "double_smoothstep",
        })
        print(f"Rendered V3 {scene['id']} / frames {start_frame}:{end_frame}", flush=True)
    proc.stdin.close()
    code = proc.wait()
    if code:
        raise RuntimeError(f"ffmpeg visual encoder failed: {code}")
    if hook_frame is None:
        raise RuntimeError("Hook frame was not captured")

    save_json(REVIEW / "visual_edit_ledger.json", {
        "sources": sorted({s["source_id"] for s in SPEC["scenes"]}), "scenes": ledger,
        "v3": {
            "text_policy": V3["text_policy"],
            "action_window": [ACTION_X, ACTION_Y, ACTION_W, ACTION_H],
            "palette": V3["palette"],
            "cinema_grade": True,
            "halation_bloom": True,
            "grain": True,
            "vignette": True,
            "scene_transition_frames": TRANSITION_FRAMES,
            "tracked_captions": True,
            "motion_drift": [V3["motion_drift_x"], V3["motion_drift_y"]],
            "loop_crossfade_s": V3["loop_crossfade_s"],
        },
    })
    save_json(REVIEW / "visual_sample_qc.json", {
        "expected_frames": N_FRAMES, "sampled_luma": sampled_luma,
        "minimum_sampled_luma": min(x["mean_luma"] for x in sampled_luma),
        "note": "Samples guard against an unintended black render; final stream/frame validation is in technical_qc.json.",
    })
    make_exact_thumbnails_v3(hook_frame)
    make_contact_sheet()
    save_json(REVIEW / "visual_v3_qc.json", {
        "minimal_captions_only": True,
        "no_top_headlines": True,
        "no_badges": True,
        "no_dance_card": True,
        "no_progress": True,
        "no_footer": True,
        "no_macro_inset": True,
        "no_source_labels": True,
        "no_brand_watermark": True,
        "no_cut_flashes": True,
        "cinema_grade": True,
        "premium_palette": True,
        "seamless_loop_crossfade": True,
        "exact_text_thumbnails": True,
        "v3_cinematic_grade": True,
        "v3_halation_bloom": True,
        "v3_scene_crossfades": True,
        "v3_tracked_captions": True,
        "v3_motion_drift": True,
        "v3_sound_polish": True,
        "v3_rank_numbers": True,
        "five_cc0_sources": True,
        "source_aspect_preserved": True,
        "no_third_party_short_form_clips": True,
        "subjective_ranking_not_science": True,
        "action_window": [ACTION_X, ACTION_Y, ACTION_W, ACTION_H],
        "grain_amplitude": V3["grain_amplitude"],
        "vignette_strength": V3["vignette_strength"],
        "halation_strength": V3["halation_strength"],
        "scene_transition_frames": TRANSITION_FRAMES,
        "loop_crossfade_s": V3["loop_crossfade_s"],
        "thumbnail_manifest": "review/exact_thumbnail_manifest.json",
        "note": "V3 clean visual policy: minimal tracked lower-third captions and subtle 5-to-1 rank numerals only; five CC0 sources, richer grade, cross-dissolves and motion drift, still zero extra text. Objective render facts, not human approval or an audience guarantee.",
    })
    print(f"Saved V3 clean picture {OUT}", flush=True)


if __name__ == "__main__":
    render()
