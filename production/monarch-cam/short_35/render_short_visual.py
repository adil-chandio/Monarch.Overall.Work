#!/usr/bin/env python3
"""Render the original 35-second native-vertical Monarch Cam Short (picture only)."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "production/monarch-cam/short_35"
WORK = ROOT / "production/monarch-cam/work/short_35"
REVIEW = BASE / "review"
SOURCE = ROOT / "production/monarch-cam/work/recon/media/nps_bears_in_cars.mp4"
OUT = WORK / "short_35_silent.mp4"
SPEC = json.loads((BASE / "short_spec.json").read_text())
W, H, FPS = SPEC["width"], SPEC["height"], SPEC["fps"]
DURATION = float(SPEC["duration"])
N_FRAMES = int(SPEC["frame_count"])
FONT_DIR = ROOT / "deliverables/monarch-cam/fonts"
BG = (7, 13, 22)
WHITE = (247, 247, 242)
MUTED = (177, 190, 198)
AMBER = (245, 184, 76)
CARD = (8, 16, 26, 238)


def font(name: str, size: int):
    return ImageFont.truetype(str(FONT_DIR / f"{name}.ttf"), size)


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


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


def source_content(frame: np.ndarray):
    """Remove the archival encode's pillar bars without stretching the 4:3 picture."""
    h, w = frame.shape[:2]
    content_w = min(w, int(round(h * 4 / 3)))
    left = max(0, (w - content_w) // 2)
    return frame[:, left:left + content_w]


def grade(frame: np.ndarray):
    # Lift archival night mid-tones while retaining real blacks and highlights.
    lut = np.clip((np.arange(256) / 255.0) ** 0.85 * 255, 0, 255).astype(np.uint8)
    lifted = cv2.LUT(frame, lut)
    return cv2.convertScaleAbs(lifted, alpha=1.025, beta=-2)


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
    bg = np.clip(bg.astype(np.float32) * 0.34, 0, 255).astype(np.uint8)
    # Quiet the caption/brand regions without introducing a synthetic picture.
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    edge = 0.60 + 0.40 * np.minimum(1.0, np.minimum(yy / 0.23, (1.0 - yy) / 0.24))
    bg = np.clip(bg.astype(np.float32) * edge, 0, 255).astype(np.uint8)
    return bg


def draw_brand(draw: ImageDraw.ImageDraw):
    draw.text((64, 48), "MONARCH CAM", font=font("Montserrat-Bold", 29), fill=WHITE, stroke_width=1, stroke_fill=(0, 0, 0))
    label = "REAL NPS FOOTAGE / YOSEMITE"
    face = font("DejaVuSansMono", 21)
    width = draw.textlength(label, font=face)
    draw.text((W - 64 - width, 55), label, font=face, fill=MUTED)


def draw_top(base: Image.Image, text: str):
    draw = ImageDraw.Draw(base)
    face = fit_font(draw, text, "Montserrat-Bold", 82, 900, 46, 8)
    lines = text.split("\n")
    spacing = 8
    box = draw.multiline_textbbox((0, 0), text, font=face, spacing=spacing, align="center")
    height = box[3] - box[1]
    y = 164 - box[1]
    for index, line in enumerate(lines):
        line_box = draw.textbbox((0, 0), line, font=face)
        line_w = line_box[2] - line_box[0]
        x = (W - line_w) / 2
        color = AMBER if index == len(lines) - 1 else WHITE
        draw.text((x + 3, y + 4), line, font=face, fill=(0, 0, 0), stroke_width=2, stroke_fill=(0, 0, 0))
        draw.text((x, y), line, font=face, fill=color, stroke_width=1, stroke_fill=(0, 0, 0))
        y += (line_box[3] - line_box[1]) + spacing + 14


def active_caption(t: float):
    narration = SPEC["narration"]
    for i, item in enumerate(narration):
        end = narration[i + 1]["start"] - 0.10 if i + 1 < len(narration) else 34.65
        if item["start"] <= t < end:
            return item["caption"]
    return None


def draw_caption(base: Image.Image, text: str | None):
    if not text:
        return
    draw = ImageDraw.Draw(base, "RGBA")
    chosen, wrapped = None, None
    for size in range(52, 39, -2):
        candidate = font("Montserrat-Bold", size)
        candidate_wrapped = wrap_text(draw, text, candidate, 860)
        if len(candidate_wrapped.split("\n")) <= 2:
            chosen, wrapped = candidate, candidate_wrapped
            break
    if chosen is None:
        chosen = font("Montserrat-Bold", 40)
        wrapped = wrap_text(draw, text, chosen, 860)
    box = draw.multiline_textbbox((0, 0), wrapped, font=chosen, spacing=12, align="center", stroke_width=1)
    tw, th = box[2] - box[0], box[3] - box[1]
    x = (W - tw) / 2
    y = 1300
    draw.rounded_rectangle((x - 28, y - 22, x + tw + 28, y + th + 30), radius=20, fill=(2, 6, 11, 206), outline=(255, 255, 255, 24), width=1)
    draw.multiline_text((x + 2, y + 3), wrapped, font=chosen, fill=(0, 0, 0, 255), spacing=12, align="center", stroke_width=2, stroke_fill=(0, 0, 0, 255))
    draw.multiline_text((x, y), wrapped, font=chosen, fill=WHITE, spacing=12, align="center", stroke_width=1, stroke_fill=(0, 0, 0))


def draw_footer(draw: ImageDraw.ImageDraw, scene_index: int):
    tag = "OBSERVE  /  UNDERSTAND"
    face = font("DejaVuSansMono", 23)
    width = draw.textlength(tag, font=face)
    draw.text(((W - width) / 2, 1695), tag, font=face, fill=MUTED)
    count = len(SPEC["scenes"])
    gap, radius = 35, 5
    total = (count - 1) * gap
    x0 = W / 2 - total / 2
    for i in range(count):
        color = AMBER if i == scene_index else (75, 86, 96)
        x = x0 + i * gap
        draw.ellipse((x - radius, 1800 - radius, x + radius, 1800 + radius), fill=color)


def draw_diagram(base: Image.Image, t: float):
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    draw.rounded_rectangle((58, 360, 1022, 1240), radius=34, fill=CARD, outline=(245, 184, 76, 155), width=2)
    draw.text((96, 402), "ONE SEARCH CAN BECOME A SHORTCUT", font=font("DejaVuSansMono", 25), fill=MUTED)
    row_y = [520, 750, 980]
    for index, (step, y) in enumerate(zip(SPEC["diagram_steps"], row_y)):
        if t + 1e-6 < step["time"]:
            continue
        local = max(0.0, min(1.0, (t - step["time"]) / 0.24))
        slide = int(round((1.0 - local) * 22))
        alpha = int(round(255 * local))
        number_face = font("DejaVuSansMono", 34)
        title_face = font("Montserrat-Bold", 67 if len(step["title"]) < 12 else 59)
        subtitle_face = font("DejaVuSans", 31)
        draw.text((98, y + 22 + slide), step["number"], font=number_face, fill=(*AMBER, alpha))
        draw.text((188, y + slide), step["title"], font=title_face, fill=(*WHITE, alpha), stroke_width=1, stroke_fill=(0, 0, 0, alpha))
        draw.text((192, y + 91 + slide), step["subtitle"], font=subtitle_face, fill=(*MUTED, alpha))
        if index < 2:
            draw.text((119, y + 150), "↓", font=font("DejaVuSans-Bold", 38), fill=(*AMBER, int(alpha * 0.72)))
    base.alpha_composite(overlay)


def render():
    if not SOURCE.exists():
        raise FileNotFoundError(f"Retrieve the cleared NPS source first: {SOURCE}")
    WORK.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium",
        "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT)
    ]
    proc = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    ledger = []
    sampled_luma = []
    cover_saved = False
    for scene_index, scene in enumerate(SPEC["scenes"]):
        start_frame = int(round(scene["start"] * FPS))
        end_frame = int(round(scene["end"] * FPS))
        cap = cv2.VideoCapture(str(SOURCE))
        source_fps = cap.get(cv2.CAP_PROP_FPS) or 29.97
        cap.set(cv2.CAP_PROP_FPS, source_fps * scene.get("rate", 1.0))
        cap.set(cv2.CAP_PROP_POS_MSEC, scene["source_start"] * 1000)
        ok, first = cap.read()
        if not ok:
            raise RuntimeError(f"Cannot read {scene['id']} at {scene['source_start']}s")
        first_content = grade(source_content(first))
        background = vertical_background(first_content, scene.get("focus", 0.5))
        layout = scene.get("layout", "footage")
        for frame_index in range(start_frame, end_frame):
            local_index = frame_index - start_frame
            local_t = local_index / FPS
            t = frame_index / FPS
            if local_index == 0:
                raw = first
            else:
                ok, raw = cap.read()
                if not ok:
                    raw = first
            content = grade(source_content(raw))
            if scene.get("loop_to_start_last") and (end_frame - frame_index) / FPS <= scene["loop_to_start_last"]:
                content = first_content.copy()
            progress = local_index / max(1, end_frame - start_frame - 1)
            zoom = scene.get("zoom_start", 1.05) * (1 - progress) + scene.get("zoom_end", 1.12) * progress
            frame = background.copy()
            if layout == "footage":
                action = crop_action(content, zoom, scene.get("focus", 0.5))
                main = cv2.resize(action, (1000, 750), interpolation=cv2.INTER_CUBIC)
                main = np.clip(main.astype(np.float32) * 1.30 - cv2.GaussianBlur(main, (0, 0), 1.0).astype(np.float32) * 0.30, 0, 255).astype(np.uint8)
                frame[390:1140, 40:1040] = main
                cv2.rectangle(frame, (39, 389), (1041, 1141), (100, 165, 205), 2, cv2.LINE_AA)
                # A small factual source label sits on the footage, not over the animal's face.
                cv2.rectangle(frame, (58, 408), (286, 450), (4, 8, 12), -1)
                cv2.putText(frame, "REAL NPS FOOTAGE", (70, 436), cv2.FONT_HERSHEY_SIMPLEX, 0.54, (198, 210, 216), 1, cv2.LINE_AA)
            base = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGBA")
            if layout == "diagram":
                draw_diagram(base, t)
            draw_top(base, scene["top"])
            draw_caption(base, active_caption(t))
            footer_draw = ImageDraw.Draw(base)
            draw_brand(footer_draw)
            draw_footer(footer_draw, scene_index)
            final = cv2.cvtColor(np.asarray(base.convert("RGB")), cv2.COLOR_RGB2BGR)
            proc.stdin.write(final.tobytes())
            if not cover_saved:
                cv2.imwrite(str(REVIEW / "cover.jpg"), final, [cv2.IMWRITE_JPEG_QUALITY, 95])
                cover_saved = True
            if frame_index % 90 == 0:
                sampled_luma.append({"frame": frame_index, "time": round(t, 3), "mean_luma": round(float(cv2.cvtColor(final, cv2.COLOR_BGR2GRAY).mean()), 3)})
        cap.release()
        ledger.append({
            "id": scene["id"], "timeline_frames": [start_frame, end_frame],
            "timeline_in": round(start_frame / FPS, 6), "timeline_out": round(end_frame / FPS, 6),
            "source_in": scene["source_start"],
            "source_out_approx": round(scene["source_start"] + ((end_frame - start_frame) / FPS) * scene.get("rate", 1.0), 6),
            "rate": scene.get("rate", 1.0), "layout": layout,
            "top": scene["top"], "loop_to_start_last": scene.get("loop_to_start_last", 0)
        })
        print(f"Rendered {scene['id']} / frames {start_frame}:{end_frame}", flush=True)
    proc.stdin.close()
    code = proc.wait()
    if code:
        raise RuntimeError(f"ffmpeg visual encoder failed: {code}")
    save_json(REVIEW / "visual_edit_ledger.json", {"source": str(SOURCE.relative_to(ROOT)), "scenes": ledger})
    save_json(REVIEW / "visual_sample_qc.json", {
        "expected_frames": N_FRAMES, "sampled_luma": sampled_luma,
        "minimum_sampled_luma": min(x["mean_luma"] for x in sampled_luma),
        "note": "Samples guard against an unintended black render; final stream/frame validation is in technical_qc.json."
    })
    make_contact_sheet()
    print(f"Saved {OUT}", flush=True)


def make_contact_sheet():
    cap = cv2.VideoCapture(str(OUT))
    times = [0.07, 2.20, 4.40, 7.30, 11.40, 16.30, 17.00, 17.70, 19.40, 25.30, 30.40, 34.70]
    cell_w, cell_h, gap = 270, 480, 14
    sheet = Image.new("RGB", (4 * cell_w + 5 * gap, 3 * (cell_h + 42) + 4 * gap), BG)
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
        label = f"{t:05.2f}s / {SPEC['scenes'][min(len(SPEC['scenes']) - 1, next((j for j, s in enumerate(SPEC['scenes']) if t < s['end']), len(SPEC['scenes']) - 1))]['id']}"
        draw.text((x, y + cell_h + 8), label[:39], font=font("DejaVuSansMono", 14), fill=WHITE)
        cv2.imwrite(str(REVIEW / f"frame_{index + 1:02d}_{t:05.2f}s.jpg"), frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
    cap.release()
    sheet.save(REVIEW / "vertical_contact_sheet.jpg", quality=94)


if __name__ == "__main__":
    render()
