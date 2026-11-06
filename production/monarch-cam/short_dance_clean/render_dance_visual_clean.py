#!/usr/bin/env python3
"""Render the CLEAN-PREMIUM 24-second albatross-dance vertical Short (picture only).

Same locked 24 s / 720 frames / 13 scenes / 16 cues / 59 words as the delivered
original and PREMIUM editions. The picture policy here is deliberately clean:
only minimal lower-third narration captions, a coherent deep-navy / ivory /
muted-teal palette, no top headlines, badges, dance cards, progress bars,
footers, macro inset, source labels, brand watermark, corner brackets or
2-frame cut flashes. The measured premium soundtrack is unchanged.
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
BASE = ROOT / "production/monarch-cam/short_dance_clean"
WORK = ROOT / "production/monarch-cam/work/short_dance_clean"
REVIEW = BASE / "review"
SOURCE = WORK / "media" / "laysan_albatross_dance.mp4"
OUT = WORK / "dance_silent_clean.mp4"
SPEC = json.loads((BASE / "dance_short_spec.json").read_text())
W, H, FPS = SPEC["width"], SPEC["height"], SPEC["fps"]
DURATION = float(SPEC["duration"])
N_FRAMES = int(SPEC["frame_count"])
CLEAN = SPEC["visual"]["clean"]
ACTION_X, ACTION_Y, ACTION_W, ACTION_H = CLEAN["action_window"]
RADIUS = int(CLEAN["action_corner_radius"])

FONT_DIR = ROOT / "public/showreel/fonts"
SYSTEM_FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
FONT_FILES = {
    "Montserrat-Bold": [FONT_DIR / "Manrope-800.ttf", FONT_DIR / "Anton-Regular.ttf"],
    "DejaVuSansMono": [FONT_DIR / "IBMPlexMono-400.ttf", SYSTEM_FONT_DIR / "DejaVuSansMono.ttf"],
    "DejaVuSans": [FONT_DIR / "Manrope-700.ttf", SYSTEM_FONT_DIR / "DejaVuSans.ttf"],
}

# Premium, restrained palette (RGB for PIL / BGR noted separately for OpenCV).
BG = (7, 13, 22)
BG_BGR = (22, 13, 7)
TEXT = (244, 241, 232)
ACCENT = (111, 207, 192)
CTA = (255, 138, 101)
GRAIN_TILE = np.random.default_rng(20261107).standard_normal((256, 256)).astype(np.float32)

# Cached finishing layers: allocated once, not per frame.
ROUNDED_MASK = Image.new("L", (ACTION_W, ACTION_H), 0)
ImageDraw.Draw(ROUNDED_MASK).rounded_rectangle(
    (0, 0, ACTION_W - 1, ACTION_H - 1), radius=RADIUS, fill=255
)
SHADOW = Image.new("RGBA", (ACTION_W + 40, ACTION_H + 40), (0, 0, 0, 0))
ImageDraw.Draw(SHADOW, "RGBA").rounded_rectangle(
    (20, 20, ACTION_W + 20, ACTION_H + 20), radius=RADIUS, fill=(0, 0, 0, 120)
)
SHADOW = SHADOW.filter(ImageFilter.GaussianBlur(20))

# A very soft bottom gradient keeps the minimal caption readable without a box.
_grad = np.zeros((H, W, 4), dtype=np.uint8)
_start = int(CLEAN["caption_y"] - 170)
_ys = np.arange(_start, H, dtype=np.float32)
_alpha = np.clip(((_ys - _start) / max(1, H - _start)) ** 1.6 * 118, 0, 150).astype(np.uint8)
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
    lut = np.clip((np.arange(256) / 255.0) ** 0.94 * 255, 0, 255).astype(np.uint8)
    lifted = cv2.LUT(frame, lut)
    return cv2.convertScaleAbs(lifted, alpha=1.025, beta=-2)


def cinema_grade(frame: np.ndarray):
    """Restrained, professional split-tone S-curve plus a soft vignette."""
    x = frame.astype(np.float32) / 255.0
    x = np.clip((x - 0.5) * 1.045 + 0.5, 0.0, 1.0)
    luma = x.mean(axis=2)
    shadows = np.clip((0.42 - luma) / 0.42, 0.0, 1.0)
    highlights = np.clip((luma - 0.62) / 0.38, 0.0, 1.0)
    # BGR: cool the shadows a touch, warm the highlights a touch.
    x[..., 0] += 0.008 * shadows - 0.004 * highlights
    x[..., 1] += 0.004 * shadows + 0.002 * highlights
    x[..., 2] += 0.003 * shadows + 0.010 * highlights
    x = np.clip(x, 0.0, 1.0)
    h, w = x.shape[:2]
    yy, xx = np.ogrid[:h, :w]
    cx, cy = w / 2.0, h / 2.0
    r = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2) / np.sqrt(2.0)
    vignette = (1.0 - float(CLEAN["vignette_strength"]) * np.clip(r, 0.0, 1.0) ** 2).astype(np.float32)
    x *= vignette[..., None]
    return (np.clip(x, 0.0, 1.0) * 255.0).astype(np.uint8)


def add_grain(main: np.ndarray, frame_index: int):
    g = np.roll(GRAIN_TILE, (frame_index % 256, (frame_index * 7) % 256), axis=(0, 1))
    g = cv2.resize(g, (ACTION_W, ACTION_H), interpolation=cv2.INTER_LINEAR)
    return np.clip(main.astype(np.float32) + g[..., None] * float(CLEAN["grain_amplitude"]), 0, 255).astype(np.uint8)


def crop_action(content: np.ndarray, zoom: float, focus: float):
    h, w = content.shape[:2]
    cw, ch = max(160, int(w / zoom)), max(120, int(h / zoom))
    cx = float(np.clip(focus, 0.0, 1.0)) * w
    cy = h * 0.50
    x0 = int(np.clip(round(cx - cw / 2), 0, w - cw))
    y0 = int(np.clip(round(cy - ch / 2), 0, h - ch))
    return content[y0:y0 + ch, x0:x0 + cw]


def vertical_background(content: np.ndarray, focus: float):
    """Deep-navy tinted, softly blurred full-bleed background."""
    scale = H / content.shape[0]
    enlarged = cv2.resize(content, (int(round(content.shape[1] * scale)), H), interpolation=cv2.INTER_CUBIC)
    center = int(round(float(focus) * enlarged.shape[1]))
    left = int(np.clip(center - W // 2, 0, enlarged.shape[1] - W))
    bg = enlarged[:, left:left + W]
    bg = cv2.GaussianBlur(bg, (0, 0), 38)
    tint = np.array(BG_BGR, np.float32)
    bg = np.clip(bg.astype(np.float32) * 0.30 + tint * 0.70, 0, 255).astype(np.uint8)
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    edge = 0.72 + 0.28 * np.minimum(1.0, np.minimum(yy / 0.24, (1.0 - yy) / 0.26))
    return np.clip(bg.astype(np.float32) * edge, 0, 255).astype(np.uint8)


def paste_action(base: Image.Image, main: np.ndarray):
    """One clean rounded 16:9 window: no border brackets, labels or flashes."""
    base.alpha_composite(SHADOW, dest=(ACTION_X - 20, ACTION_Y - 20))
    action = Image.fromarray(cv2.cvtColor(main, cv2.COLOR_BGR2RGB)).convert("RGBA")
    base.paste(action, (ACTION_X, ACTION_Y), ROUNDED_MASK)
    draw = ImageDraw.Draw(base, "RGBA")
    draw.rounded_rectangle(
        (ACTION_X, ACTION_Y, ACTION_X + ACTION_W, ACTION_Y + ACTION_H),
        radius=RADIUS, outline=(*TEXT, 26), width=1,
    )


def active_caption(t: float):
    narration = SPEC["narration"]
    for i, item in enumerate(narration):
        end = narration[i + 1]["start"] - 0.06 if i + 1 < len(narration) else DURATION
        if item["start"] <= t < end:
            return {"text": item["caption"], "start": item["start"], "end": end, "index": i}
    return None


def draw_caption(base: Image.Image, info: dict | None, t: float):
    """The only in-picture text: one minimal, elegant lower-third caption."""
    if not info:
        return
    base.alpha_composite(BOTTOM_GRADIENT)
    draw = ImageDraw.Draw(base, "RGBA")
    age = max(0.0, t - info["start"])
    fade = smoothstep(age / 0.18)
    alpha = int(238 * fade)
    if alpha <= 0:
        return
    y0 = int(CLEAN["caption_y"] + (1.0 - fade) * 14)
    chosen, wrapped = None, None
    for size in range(int(CLEAN["caption_font_max"]), int(CLEAN["caption_font_min"]) - 1, -2):
        candidate = font("DejaVuSans", size)
        candidate_wrapped = wrap_text(draw, info["text"], candidate, int(CLEAN["caption_max_width"]))
        if len(candidate_wrapped.split("\n")) <= 2:
            chosen, wrapped = candidate, candidate_wrapped
            break
    if chosen is None:
        chosen = font("DejaVuSans", int(CLEAN["caption_font_min"]))
        wrapped = wrap_text(draw, info["text"], chosen, int(CLEAN["caption_max_width"]))
    box = draw.multiline_textbbox((0, 0), wrapped, font=chosen, spacing=10, align="center", stroke_width=1)
    tw, th = box[2] - box[0], box[3] - box[1]
    x = (W - tw) / 2
    is_final = info["index"] == len(SPEC["narration"]) - 1
    color = CTA if is_final else TEXT
    shadow_alpha = int(alpha * 0.72)
    draw.multiline_text(
        (x + 2, y0 + 2), wrapped, font=chosen, fill=(0, 0, 0, shadow_alpha),
        spacing=10, align="center", stroke_width=2, stroke_fill=(0, 0, 0, shadow_alpha),
    )
    draw.multiline_text(
        (x, y0), wrapped, font=chosen, fill=(*color, alpha),
        spacing=10, align="center", stroke_width=1, stroke_fill=(0, 0, 0, shadow_alpha),
    )
    # A single restrained accent rule; no box, kicker or progress element.
    rule_w = 96
    draw.rounded_rectangle(
        (W / 2 - rule_w / 2, y0 + th + 24, W / 2 + rule_w / 2, y0 + th + 27),
        radius=2, fill=(*ACCENT, int(120 * fade)),
    )


def make_exact_thumbnails(hook_bgr: np.ndarray):
    """Clean exact-text thumbnails: one headline, no extra branding or labels."""
    cv2.imwrite(str(REVIEW / "cover_hook.jpg"), hook_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
    base = Image.fromarray(cv2.cvtColor(hook_bgr, cv2.COLOR_BGR2RGB)).convert("RGBA")
    outputs = []

    def render_text(text: str, filename: str, color):
        img = base.copy()
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay, "RGBA")
        # Soft top scrim only; no logos, subheads or field-note labels.
        draw.rectangle((0, 0, W, 620), fill=(2, 8, 14, 158))
        draw.line((80, 570, 1000, 570), fill=(*ACCENT, 130), width=2)
        face = fit_font(draw, text, "Montserrat-Bold", 88, 940, 46, 8)
        box = draw.multiline_textbbox((0, 0), text, font=face, spacing=8, align="center")
        tw, th = box[2] - box[0], box[3] - box[1]
        x, y = (W - tw) / 2, 210 - box[1]
        draw.multiline_text(
            (x + 3, y + 4), text, font=face, fill=(0, 0, 0, 255), spacing=8,
            align="center", stroke_width=2, stroke_fill=(0, 0, 0, 255),
        )
        draw.multiline_text(
            (x, y), text, font=face, fill=(*color, 255), spacing=8,
            align="center", stroke_width=1, stroke_fill=(0, 0, 0, 255),
        )
        img.alpha_composite(overlay)
        path = REVIEW / filename
        img.convert("RGB").save(path, quality=95)
        outputs.append({
            "file": path.name, "text": text,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size,
        })

    render_text(CLEAN["exact_cover_text"], "cover.jpg", TEXT)
    render_text(CLEAN["exact_cover_ab_text"], "cover_WOULD_YOU_PASS.jpg", CTA)
    save_json(REVIEW / "exact_thumbnail_manifest.json", {
        "hook_frame_reference": "cover_hook.jpg",
        "hook_frame_text": None,
        "primary": CLEAN["exact_cover_text"],
        "ab": CLEAN["exact_cover_ab_text"],
        "outputs": outputs,
        "note": "Clean exact-text thumbnails generated from the 0.07 s hook frame. The in-video hook frame itself has no extra headline. No separate human thumbnail review occurred.",
    })


def make_contact_sheet():
    cap = cv2.VideoCapture(str(OUT))
    times = [0.07, 1.45, 2.95, 4.45, 5.95, 7.35, 8.85, 10.45, 12.05, 13.55, 15.15, 16.85, 18.35, 22.0]
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
            zoom = scene.get("zoom_start", 1.10) * (1 - ep) + scene.get("zoom_end", 1.18) * ep
            drift = 0.010 * math.sin(2 * math.pi * (t / DURATION) * 1.5 + scene_index)
            focus_eff = float(np.clip(scene.get("focus", 0.5) + drift, 0.0, 1.0))
            action = crop_action(content, zoom, focus_eff)
            main = cv2.resize(action, (ACTION_W, ACTION_H), interpolation=cv2.INTER_CUBIC)
            main = np.clip(
                main.astype(np.float32) * 1.10
                - cv2.GaussianBlur(main, (0, 0), 1.0).astype(np.float32) * 0.10,
                0, 255,
            ).astype(np.uint8)
            if layout == "mirror_split":
                mirrored = cv2.flip(main, 1)
                main = cv2.addWeighted(main, 0.5, mirrored, 0.5, 0)
                cv2.line(main, (ACTION_W // 2, 0), (ACTION_W // 2, ACTION_H),
                         (205, 210, 208), 1, cv2.LINE_AA)
            main = cinema_grade(main)
            main = add_grain(main, frame_index)

            base = Image.fromarray(cv2.cvtColor(background, cv2.COLOR_BGR2RGB)).convert("RGBA")
            paste_action(base, main)
            draw_caption(base, active_caption(t), t)
            final = cv2.cvtColor(np.asarray(base.convert("RGB")), cv2.COLOR_RGB2BGR)
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
        ledger.append({
            "id": scene["id"], "timeline_frames": [start_frame, end_frame],
            "timeline_in": round(start_frame / FPS, 6), "timeline_out": round(end_frame / FPS, 6),
            "source_in": scene["source_start"],
            "source_out_approx": round(
                scene["source_start"] + ((end_frame - start_frame) / FPS) * scene.get("rate", 1.0), 6
            ),
            "rate": scene.get("rate", 1.0), "layout": layout,
            "top": scene["top"], "loop_to_start_last": scene.get("loop_to_start_last", 0),
            "clean_action_window": [ACTION_X, ACTION_Y, ACTION_W, ACTION_H],
            "clean_text_policy": CLEAN["text_policy"],
        })
        print(f"Rendered clean {scene['id']} / frames {start_frame}:{end_frame}", flush=True)
    proc.stdin.close()
    code = proc.wait()
    if code:
        raise RuntimeError(f"ffmpeg visual encoder failed: {code}")
    if hook_frame is None:
        raise RuntimeError("Hook frame was not captured")

    save_json(REVIEW / "visual_edit_ledger.json", {
        "source": str(SOURCE.relative_to(ROOT)), "scenes": ledger,
        "clean": {
            "text_policy": CLEAN["text_policy"],
            "action_window": [ACTION_X, ACTION_Y, ACTION_W, ACTION_H],
            "palette": CLEAN["palette"],
            "cinema_grade": True,
            "grain": True,
            "vignette": True,
            "loop_crossfade_s": CLEAN["loop_crossfade_s"],
        },
    })
    save_json(REVIEW / "visual_sample_qc.json", {
        "expected_frames": N_FRAMES, "sampled_luma": sampled_luma,
        "minimum_sampled_luma": min(x["mean_luma"] for x in sampled_luma),
        "note": "Samples guard against an unintended black render; final stream/frame validation is in technical_qc.json.",
    })
    make_exact_thumbnails(hook_frame)
    make_contact_sheet()
    save_json(REVIEW / "visual_clean_qc.json", {
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
        "action_window": [ACTION_X, ACTION_Y, ACTION_W, ACTION_H],
        "grain_amplitude": CLEAN["grain_amplitude"],
        "vignette_strength": CLEAN["vignette_strength"],
        "loop_crossfade_s": CLEAN["loop_crossfade_s"],
        "thumbnail_manifest": "review/exact_thumbnail_manifest.json",
        "note": "Clean visual policy: only minimal lower-third captions. Objective render facts, not human approval or an audience guarantee.",
    })
    print(f"Saved clean picture {OUT}", flush=True)


if __name__ == "__main__":
    render()
