#!/usr/bin/env python3
"""Build Monarch Cam's 30-second real-footage opening proof.

Inputs are the explicit public-domain NPS asset retrieved by source_recon.py and the
editorial spec in preview_spec.json. Output is exactly 900 frames at 1920x1080/30 fps
with original neural narration, restrained graphics, procedural sound and measured
loudness. No synthetic wildlife imagery is generated.
"""
from __future__ import annotations

import asyncio
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import cv2
import edge_tts
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import signal
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SPEC = json.loads((ROOT / "preview_spec.json").read_text(encoding="utf-8"))
WORK = ROOT / "work/preview"
OUT = REPO / "deliverables/MONARCH_CAM_Bear_Opening_30s_Preview.mp4"
REVIEW = ROOT / "preview"
FONTS = REPO / "public/showreel/fonts"
W, H, FPS = SPEC["width"], SPEC["height"], SPEC["fps"]
DURATION = float(SPEC["duration_seconds"])
TOTAL_FRAMES = int(round(DURATION * FPS))
SR = 48000
SOURCE = ROOT / SPEC["source"]["file"]
FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
AMBER = (229, 179, 65, 255)
WHITE = (245, 243, 236, 255)
MUTED = (174, 185, 192, 255)

for directory in (WORK, REVIEW, OUT.parent):
    directory.mkdir(parents=True, exist_ok=True)


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    print("+", " ".join(cmd), flush=True)
    kwargs.setdefault("text", True)
    return subprocess.run(cmd, **kwargs)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size=size)


def empty_layer() -> Image.Image:
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def static_layer() -> np.ndarray:
    layer = empty_layer()
    d = ImageDraw.Draw(layer)
    mono = font("IBMPlexMono-400.ttf", 23)
    bold = font("Manrope-800.ttf", 25)
    d.rounded_rectangle((70, 50, 88, 68), radius=4, fill=AMBER)
    d.text((103, 43), "MONARCH CAM", font=bold, fill=WHITE)
    label = "NPS ARCHIVE  /  YOSEMITE"
    box = d.textbbox((0, 0), label, font=mono)
    d.text((W - 70 - (box[2] - box[0]), 48), label, font=mono, fill=MUTED)
    d.line((70, 91, W - 70, 91), fill=(255, 255, 255, 35), width=1)
    return np.asarray(layer).astype(np.float32) / 255.0


def kicker_layer(text: str) -> np.ndarray:
    layer = empty_layer()
    d = ImageDraw.Draw(layer)
    mono = font("IBMPlexMono-400.ttf", 24)
    d.rectangle((78, 132, 84, 168), fill=AMBER)
    d.text((103, 133), text, font=mono, fill=WHITE)
    return np.asarray(layer).astype(np.float32) / 255.0


def headline_layer(kicker: str, headline: str, layout: str) -> np.ndarray:
    layer = empty_layer()
    d = ImageDraw.Draw(layer)
    mono = font("IBMPlexMono-400.ttf", 25)
    big = font("Manrope-800.ttf", 82 if layout == "question" else 88)
    x, y = 100, 198
    d.text((x, y), kicker, font=mono, fill=AMBER)
    d.multiline_text(
        (x, y + 64), headline, font=big, fill=WHITE, spacing=9,
        stroke_width=3, stroke_fill=(0, 0, 0, 150),
    )
    d.rectangle((x, y + 322, x + 150, y + 330), fill=AMBER)
    return np.asarray(layer).astype(np.float32) / 255.0


def model_layer(kicker: str, steps: list[str], reveal: int) -> np.ndarray:
    layer = empty_layer()
    d = ImageDraw.Draw(layer)
    mono = font("IBMPlexMono-400.ttf", 24)
    number = font("Manrope-800.ttf", 30)
    body = font("Manrope-800.ttf", 43)
    d.text((100, 172), kicker, font=mono, fill=AMBER)
    d.text((100, 215), "HOW THE LESSON STICKS", font=font("Manrope-800.ttf", 49), fill=WHITE)
    start_y = 335
    for index, text in enumerate(steps[:reveal]):
        y = start_y + index * 142
        if index < len(steps[:reveal]) - 1:
            d.line((127, y + 66, 127, y + 139), fill=(229, 179, 65, 170), width=4)
        d.ellipse((98, y, 156, y + 58), fill=(16, 24, 30, 230), outline=AMBER, width=3)
        n = str(index + 1)
        bb = d.textbbox((0, 0), n, font=number)
        d.text((127 - (bb[2] - bb[0]) / 2, y + 8), n, font=number, fill=AMBER)
        d.text((184, y + 5), text, font=body, fill=WHITE, stroke_width=2, stroke_fill=(0, 0, 0, 130))
    if reveal == len(steps):
        d.rounded_rectangle((100, 802, 835, 867), radius=8, fill=(12, 18, 22, 205))
        d.text((125, 817), "REWARD  →  MEMORY  →  REPEAT", font=mono, fill=AMBER)
    return np.asarray(layer).astype(np.float32) / 255.0


def caption_layer(text: str) -> np.ndarray:
    layer = empty_layer()
    d = ImageDraw.Draw(layer)
    body = font("Manrope-700.ttf", 43)
    lines = text.splitlines()
    heights = []
    for line in lines:
        bb = d.textbbox((0, 0), line, font=body, stroke_width=2)
        heights.append(bb[3] - bb[1])
    total_h = sum(heights) + max(0, len(lines) - 1) * 12
    y = H - 78 - total_h
    for index, line in enumerate(lines):
        bb = d.textbbox((0, 0), line, font=body, stroke_width=2)
        width = bb[2] - bb[0]
        d.text(
            ((W - width) / 2, y), line, font=body, fill=WHITE,
            stroke_width=3, stroke_fill=(0, 0, 0, 225),
        )
        y += heights[index] + 12
    return np.asarray(layer).astype(np.float32) / 255.0


def apply_layer(frame: np.ndarray, layer: np.ndarray, opacity: float = 1.0) -> None:
    if opacity <= 0:
        return
    alpha = np.clip(layer[:, :, 3:4] * opacity, 0.0, 1.0)
    frame *= 1.0 - alpha
    # PIL text layers are RGBA while the video canvas is OpenCV BGR.
    frame += layer[:, :, :3][:, :, ::-1] * 255.0 * alpha


def smooth_fade(t: float, start: float, end: float, fade: float = 0.22) -> float:
    return max(0.0, min(1.0, (t - start) / fade, (end - t) / fade))


def scene_at(t: float) -> dict:
    for scene in SPEC["scenes"]:
        if scene["start"] <= t < scene["end"]:
            return scene
    return SPEC["scenes"][-1]


def render_video() -> Path:
    static = static_layer()
    kickers = {s["id"]: kicker_layer(s.get("kicker", "")) for s in SPEC["scenes"] if s["layout"] == "footage"}
    headlines = {
        s["id"]: headline_layer(s["kicker"], s["headline"], s["layout"])
        for s in SPEC["scenes"] if s["layout"] in {"question", "answer"}
    }
    models = {
        (s["id"], reveal): model_layer(s["kicker"], s["steps"], reveal)
        for s in SPEC["scenes"] if s["layout"] == "model" for reveal in (0, 1, 2, 3)
    }
    captions = {n["id"]: caption_layer(n["caption"]) for n in SPEC["narration"] if n["caption"]}

    # Reusable optical treatments; no random flicker or AI-generated detail.
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = (xx - W / 2) / (W / 2)
    ny = (yy - H / 2) / (H / 2)
    vignette = np.clip(1.0 - 0.12 * (nx * nx + ny * ny), 0.76, 1.0)[:, :, None]
    top_gradient = np.ones((H, 1), dtype=np.float32)
    top_gradient[:125, 0] = np.linspace(0.60, 1.0, 125)
    bottom_gradient = np.ones((H, 1), dtype=np.float32)
    bottom_gradient[H - 285:, 0] = np.linspace(1.0, 0.36, 285)
    left_gradient = np.ones((1, W), dtype=np.float32)
    left_gradient[0, :1030] = np.linspace(0.35, 1.0, 1030)

    silent = WORK / "video_silent.mp4"
    proc = subprocess.Popen([
        FFMPEG, "-y", "-hide_banner", "-loglevel", "warning",
        "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(silent),
    ], stdin=subprocess.PIPE)
    assert proc.stdin is not None

    current_id = None
    cap = None
    source = None
    next_source_time = 0.0
    source_frame_step = 1.0 / 29.97
    qc_frames: dict[int, np.ndarray] = {}
    wanted = {int(round(t * FPS)) for t in (0.5, 3.0, 6.0, 12.0, 18.0, 24.0, 27.0, 29.5)}
    prev_small = None
    diffs: list[float] = []
    dark_frames = 0

    for frame_index in range(TOTAL_FRAMES):
        t = frame_index / FPS
        scene = scene_at(t)
        if scene["id"] != current_id:
            if cap is not None:
                cap.release()
            cap = cv2.VideoCapture(str(SOURCE))
            cap.set(cv2.CAP_PROP_POS_MSEC, float(scene["source_start"]) * 1000.0)
            source_fps = float(cap.get(cv2.CAP_PROP_FPS) or 29.97)
            source_frame_step = 1.0 / source_fps
            source = None
            next_source_time = float(scene["source_start"])
            current_id = scene["id"]
        target_source_time = float(scene["source_start"]) + (t - float(scene["start"])) * float(scene.get("source_rate", 1.0))
        if source is None:
            ok, source = cap.read()
            if not ok or source is None:
                raise RuntimeError(f"Cannot seek source in scene {scene['id']} at {target_source_time:.3f}s")
            next_source_time = float(scene["source_start"]) + source_frame_step
        # Constant-frame-rate resampling keeps normal shots near real time and permits the
        # closing real close-up to play gently slower without manufacturing any motion.
        while next_source_time < target_source_time - source_frame_step * 0.25:
            ok, following = cap.read()
            if not ok or following is None:
                break
            source = following
            next_source_time += source_frame_step
        frame = cv2.resize(source, (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
        # Mild archival cleanup only. The animal/action is not altered.
        blur = cv2.GaussianBlur(frame, (0, 0), 1.0)
        frame = cv2.addWeighted(frame, 1.18, blur, -0.18, 0)
        frame = (frame - 127.5) * 1.055 + 132.0
        frame *= vignette
        layout = scene["layout"]
        if layout in {"question", "answer"}:
            frame *= 0.53
        elif layout == "model":
            frame *= left_gradient[:, :, None]
        frame *= top_gradient[:, :, None]
        frame *= bottom_gradient[:, :, None]

        if layout == "footage":
            apply_layer(frame, static)
            apply_layer(frame, kickers[scene["id"]], smooth_fade(t, scene["start"], scene["end"], 0.35))
        elif layout in {"question", "answer"}:
            apply_layer(frame, static)
            apply_layer(frame, headlines[scene["id"]], smooth_fade(t, scene["start"], scene["end"], 0.38))
        elif layout == "model":
            apply_layer(frame, static)
            reveal = 0 if t < 23.55 else (1 if t < 24.85 else (2 if t < 26.15 else 3))
            apply_layer(frame, models[(scene["id"], reveal)], 1.0)

        for narration in SPEC["narration"]:
            if narration["caption"] and narration["start"] <= t < narration["latest_end"]:
                apply_layer(frame, captions[narration["id"]], smooth_fade(t, narration["start"], narration["latest_end"], 0.16))

        frame = np.clip(frame, 0, 255).astype(np.uint8)
        if frame_index in wanted:
            qc_frames[frame_index] = frame.copy()
        if frame_index == int(round(18.0 * FPS)):
            Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).save(REVIEW / "poster.jpg", quality=94)
        small = cv2.resize(frame, (96, 54), interpolation=cv2.INTER_AREA)
        if float(small.mean()) < 3.0:
            dark_frames += 1
        if prev_small is not None:
            diffs.append(float(np.abs(small.astype(np.float32) - prev_small.astype(np.float32)).mean()))
        prev_small = small
        proc.stdin.write(frame.tobytes())
        if frame_index % 90 == 0:
            print(f"Rendered {frame_index}/{TOTAL_FRAMES} frames", flush=True)

    cap.release()
    proc.stdin.close()
    code = proc.wait()
    if code != 0:
        raise RuntimeError(f"ffmpeg video encoder exited {code}")

    # Eight representative frames for human visual QC.
    thumbs = []
    for index in sorted(qc_frames):
        rgb = cv2.cvtColor(qc_frames[index], cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb).resize((480, 270), Image.Resampling.LANCZOS)
        thumbs.append((index, image))
    sheet = Image.new("RGB", (4 * 496, 2 * 314 + 54), "#101419")
    d = ImageDraw.Draw(sheet)
    label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
    d.text((14, 14), "MONARCH CAM — 30 SECOND PREVIEW / VISUAL QC", font=label_font, fill="#F4F1E8")
    for pos, (index, image) in enumerate(thumbs):
        x = (pos % 4) * 496 + 8
        y = 54 + (pos // 4) * 314
        sheet.paste(image, (x, y))
        d.text((x + 3, y + 278), f"{index / FPS:05.2f}s", font=label_font, fill="#F2C14E")
    sheet.save(REVIEW / "visual_qc.jpg", quality=94)
    stats = {
        "frames": TOTAL_FRAMES,
        "duration_seconds": DURATION,
        "dark_frames": dark_frames,
        "mean_frame_difference": round(float(np.mean(diffs)), 4),
        "near_static_transitions": sum(v < 0.02 for v in diffs),
        "visual_review": "See visual_qc.jpg; final human review required",
    }
    (REVIEW / "visual_metrics.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    return silent


async def synthesize() -> None:
    voice = SPEC["voice"]
    for narration in SPEC["narration"]:
        target = WORK / f"{narration['id']}.mp3"
        if target.exists() and target.stat().st_size > 1000:
            continue
        communicate = edge_tts.Communicate(narration["text"], voice["name"], rate=voice["rate"])
        await communicate.save(str(target))
        print("Synthesized", narration["id"], flush=True)


def decode_vo(path: Path, atempo: float = 1.0) -> np.ndarray:
    af = (
        "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.025,"
        "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.06,areverse,"
        f"atempo={atempo:.5f},aresample={SR}"
    )
    proc = run([
        FFMPEG, "-y", "-hide_banner", "-loglevel", "warning", "-i", str(path),
        "-af", af, "-ac", "2", "-f", "f32le", "pipe:1",
    ], capture_output=True, check=True, text=False)
    if not proc.stdout:
        # Very quiet or unusual narration can be over-trimmed by FFmpeg; retain the full
        # voice rather than silently producing an empty narration bus.
        proc = run([
            FFMPEG, "-y", "-hide_banner", "-loglevel", "warning", "-i", str(path),
            "-af", f"atempo={atempo:.5f},aresample={SR}", "-ac", "2", "-f", "f32le", "pipe:1",
        ], capture_output=True, check=True, text=False)
    if not proc.stdout:
        raise RuntimeError(f"Narration decode produced no samples: {path}")
    return np.frombuffer(proc.stdout, dtype=np.float32).reshape(-1, 2).copy()


def mix_into(bus: np.ndarray, clip: np.ndarray, start_s: float, gain: float = 1.0) -> None:
    start = int(round(start_s * SR))
    count = min(len(clip), len(bus) - start)
    if count > 0:
        bus[start:start + count] += clip[:count] * gain


def whoosh(duration: float = 0.45) -> np.ndarray:
    n = int(duration * SR)
    rng = np.random.default_rng(510)
    noise = rng.standard_normal(n)
    sos = signal.butter(2, [180, 2400], btype="bandpass", fs=SR, output="sos")
    filtered = signal.sosfilt(sos, noise)
    env = np.sin(np.linspace(0, np.pi, n)) ** 1.8
    mono = filtered * env * 0.025
    pan = np.linspace(0.2, 0.8, n)
    return np.stack([mono * np.cos(pan * np.pi / 2), mono * np.sin(pan * np.pi / 2)], axis=1)


def sub_hit(duration: float = 0.75) -> np.ndarray:
    t = np.arange(int(duration * SR), dtype=np.float64) / SR
    freq = 35 + 52 * np.exp(-t * 10)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    mono = np.sin(phase) * np.exp(-t * 5.2) * 0.10
    return np.stack([mono, mono], axis=1)


def loudnorm_file(raw_path: Path, output: Path) -> None:
    first = run([
        FFMPEG, "-y", "-hide_banner", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", str(raw_path),
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-",
    ], capture_output=True, check=True)
    match = re.search(r'\{\s*"input_i"[\s\S]*?\}', first.stderr)
    stats = json.loads(match.group(0)) if match else {}
    if stats:
        af = (
            "loudnorm=I=-14:TP=-1.5:LRA=11:"
            f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
            f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
            f"offset={stats['target_offset']}:linear=true,aresample={SR},alimiter=limit=0.82:level=false"
        )
    else:
        af = f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample={SR},alimiter=limit=0.82:level=false"
    run([
        FFMPEG, "-y", "-hide_banner", "-loglevel", "warning",
        "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", str(raw_path),
        "-af", af, "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), str(output),
    ], check=True)


def render_audio() -> tuple[Path, list[dict]]:
    samples = int(round(DURATION * SR))
    voice_bus = np.zeros((samples, 2), dtype=np.float32)
    background = np.zeros_like(voice_bus)
    report: list[dict] = []
    for narration in SPEC["narration"]:
        path = WORK / f"{narration['id']}.mp3"
        clip = decode_vo(path)
        allowed = float(narration["latest_end"]) - float(narration["start"]) - 0.06
        duration = len(clip) / SR
        tempo = max(1.0, duration / allowed)
        if tempo > 1.001:
            if tempo > 1.12:
                raise RuntimeError(f"{narration['id']} needs excessive tempo {tempo:.3f}")
            clip = decode_vo(path, tempo)
            duration = len(clip) / SR
        if duration > allowed + 0.08:
            raise RuntimeError(f"{narration['id']} overruns: {duration:.3f}s > {allowed:.3f}s")
        # Gentle voice cleanup and consistent short fades before the final master loudnorm.
        clip = signal.sosfilt(signal.butter(2, 75, btype="highpass", fs=SR, output="sos"), clip, axis=0).astype(np.float32)
        fade = min(int(0.018 * SR), len(clip) // 4)
        clip[:fade] *= np.linspace(0, 1, fade)[:, None]
        clip[-fade:] *= np.linspace(1, 0, fade)[:, None]
        mix_into(voice_bus, clip, float(narration["start"]), 0.96)
        report.append({"id": narration["id"], "start": narration["start"], "duration": round(duration, 3), "tempo": round(tempo, 4)})

    t = np.arange(samples, dtype=np.float64) / SR
    drone_l = np.sin(2 * np.pi * 55 * t) + 0.38 * np.sin(2 * np.pi * 82.41 * t + 0.3)
    drone_r = np.sin(2 * np.pi * 55.08 * t + 0.1) + 0.38 * np.sin(2 * np.pi * 82.47 * t + 0.6)
    section = np.interp(t, [0, 10.8, 11.7, 16.4, 17.1, 22.7, 23.2, 29.3, 30], [0.30, 0.30, 0.55, 0.55, 0.90, 0.90, 0.48, 0.48, 0.15])
    drone = np.stack([drone_l, drone_r], axis=1) * section[:, None] * 0.018
    background += drone.astype(np.float32)

    # Very low, band-limited original night air prevents near-digital-silence between
    # narration beats. It is ducked under the voice and contains no fake wildlife/foley.
    rng = np.random.default_rng(20261105)
    air = np.empty((samples, 2), dtype=np.float32)
    air_sos = signal.butter(2, [120, 1800], btype="bandpass", fs=SR, output="sos")
    for channel in range(2):
        noise = signal.sosfilt(air_sos, rng.standard_normal(samples))
        noise /= float(np.sqrt(np.mean(noise * noise)) + 1e-12)
        air[:, channel] = noise.astype(np.float32)
    air_section = np.interp(t, [0, 11.7, 17.1, 23.2, 30], [1.0, 0.92, 0.86, 0.94, 0.80])
    background += (air * air_section[:, None] * 0.012).astype(np.float32)

    mix_into(background, whoosh(), 11.42, 0.85)
    mix_into(background, whoosh(), 22.93, 0.75)
    mix_into(background, sub_hit(), 17.08, 0.70)

    vo_env = np.abs(voice_bus).mean(axis=1)
    win = int(0.055 * SR)
    smooth = np.convolve(vo_env, np.ones(win) / win, mode="same")
    duck = np.clip(1.0 - smooth * 7.0, 0.24, 1.0).astype(np.float32)
    background *= duck[:, None]
    mix = voice_bus + background
    mix[: int(0.12 * SR)] *= np.linspace(0, 1, int(0.12 * SR))[:, None]
    mix[-int(0.42 * SR):] *= np.linspace(1, 0, int(0.42 * SR))[:, None]
    mix = np.nan_to_num(mix).astype(np.float32)
    raw = WORK / "mix_raw.f32"
    raw.write_bytes(mix.tobytes())
    master = WORK / "audio_master.m4a"
    loudnorm_file(raw, master)
    raw.unlink(missing_ok=True)
    (REVIEW / "narration_timing.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return master, report


def mux_and_probe(video: Path, audio: Path) -> dict:
    run([
        FFMPEG, "-y", "-hide_banner", "-loglevel", "warning", "-i", str(video), "-i", str(audio),
        "-c:v", "copy", "-c:a", "copy", "-t", f"{DURATION:.3f}", "-movflags", "+faststart", str(OUT),
    ], check=True)
    proc = run([
        "ffprobe", "-v", "error", "-count_frames", "-show_entries",
        "format=duration,size:stream=index,codec_name,codec_type,width,height,r_frame_rate,nb_read_frames,sample_rate,channels",
        "-of", "json", str(OUT),
    ], capture_output=True, check=True)
    data = json.loads(proc.stdout)
    (REVIEW / "delivery_probe.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    video_stream = next(s for s in data["streams"] if s["codec_type"] == "video")
    assert video_stream["width"] == W and video_stream["height"] == H
    assert video_stream["r_frame_rate"] == "30/1"
    assert int(video_stream["nb_read_frames"]) == TOTAL_FRAMES
    assert abs(float(data["format"]["duration"]) - DURATION) < 0.05
    return data


def main() -> int:
    args = set(sys.argv[1:])
    audio_only = "--audio-only" in args
    video_only = "--video-only" in args
    if audio_only and video_only:
        raise ValueError("Choose only one of --audio-only / --video-only")
    if not SOURCE.exists():
        raise FileNotFoundError(f"Retrieve NPS source first: {SOURCE}")
    if video_only:
        audio = WORK / "audio_master.m4a"
        if not audio.exists():
            raise FileNotFoundError("Render and verify the audio master before --video-only")
    else:
        asyncio.run(synthesize())
        audio, _ = render_audio()
    if audio_only:
        print(json.dumps({"audio_master": str(audio)}, indent=2), flush=True)
        return 0
    video = render_video()
    probe = mux_and_probe(video, audio)
    print(json.dumps({"output": str(OUT), "probe": probe}, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
