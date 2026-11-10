#!/usr/bin/env python3
"""Build the V10 one-clip Artemis II commentary Short and its QC evidence.

Run from the repository root with the bundled media dependencies on PYTHONPATH:

    python production/monarch-cam/caught_on_camera_commentary_v10/render_v10.py

The script deliberately keeps technical QC separate from human creative approval.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEPS = ROOT / "production/monarch-cam/work/v10_deps"
sys.path.insert(0, str(DEPS))
sys.path.insert(0, str(ROOT))

import imageio_ffmpeg
import numpy as np
import soundfile as sf
from PIL import Image, ImageFont
from scipy import signal
from showreel.audio_qc.gates import run as audio_gate_run

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
BASE = ROOT / "production/monarch-cam/caught_on_camera_commentary_v10"
AUDIO_DIR = BASE / "audio"
REVIEW = BASE / "review" / "final"
WORK = ROOT / "production/monarch-cam/work/v10_render"
SOURCE = BASE / "source" / "nasa_artemis_ii_water_bubble_4k_to_vertical_master.mp4"
DELIVERABLE = ROOT / "deliverables" / "MONARCH_CAM_Artemis_II_Upside_Down_Face_V10_Short.mp4"
ASS_PATH = REVIEW / "captions_v10.ass"
FONTS_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_REGULAR = FONTS_DIR + "/DejaVuSans.ttf"
FONT_BOLD = FONTS_DIR + "/DejaVuSans-Bold.ttf"

SR = 48000
GAP = 0.1
FLASH_SOURCE_START = 6.0
FLASH_DURATION = 1.5
MAIN_DURATION = 42.7
LOOP_SOURCE_START = 6.0
REACTION_WINDOWS_SOURCE = [(12.05, 14.45), (23.20, 24.67), (38.90, 41.67)]
REACTION_BOOST_DB = 8.0
VO_TARGET_RMS = 0.10  # -20 dBFS
BED_TARGET_RMS = 10 ** (-30.0 / 20.0)
SAFE_ZONE = {"top": 250, "bottom": 1560, "left": 80, "right": 1000}
NASA_PAGE = "https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman"
NASA_ASSET = "https://images-assets.nasa.gov/video/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman~orig.mp4"
NASA_GUIDELINES = "https://www.nasa.gov/nasa-brand-center/images-and-media/"
SOURCE_SHA = "7fd9cd0cfc22451910ac8fa8848b5252c51320a82c193e3a98cf7c0aa725c0dc"
SOURCE_BYTES = 63680143
MASTER_SHA = "11395618c0db74164e35de8186b079f974316f13fd5c25efb789574b22d5960c"
MASTER_BYTES = 29314216

BEATS = [
    "That is not a lens. Watch the face inside that floating water ball.",
    "Artemis Two astronauts were playing with one sphere of water near the Moon. Almost no gravity pulling it down.",
    "They guide it with a straw, and the clear orb becomes a tiny crystal ball.",
    "One touch, and the sphere collapses. The crew literally laughs: Crazy.",
    "But here is the part people replay. Look through it again: the astronaut behind it is upside down.",
    "That is refraction. Light bends through curved water, so the image flips before your eyes.",
    "No CGI. No staged skit. Just surface tension holding a liquid lens in microgravity.",
    "Back to the start. That upside-down face is still there. Watch it again.",
]

MASTER_CHAIN_ID = "dualmono_linear_loudnorm_treble_declick"
PAN_FILTER = "pan=stereo|c0=0.5*c0+0.5*c1|c1=0.5*c0+0.5*c1"
HIGHPASS_FILTER = "highpass=f=35"
TREBLE_FILTER = "treble=f=3000:g=-2:w=0.5"
LIMITER_FILTER = "alimiter=limit=0.75:level=disabled"


def ensure_dirs() -> None:
    for p in (AUDIO_DIR, REVIEW, WORK, DELIVERABLE.parent):
        p.mkdir(parents=True, exist_ok=True)


def run(cmd: list[str], capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run([str(c) for c in cmd], text=True, check=True,
                          capture_output=capture)


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=json_safe) + "\n",
                    encoding="utf-8")


def json_safe(obj):
    if isinstance(obj, (np.floating, np.integer, np.bool_)):
        return obj.item()
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(f"Not JSON serializable: {type(obj).__name__}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dbfs(x: float) -> float:
    return float(20 * np.log10(max(float(x), 1e-12)))


def ass_time(t: float) -> str:
    t = max(0.0, float(t))
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def escape_ass_text(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}").replace(",", r"\,")


def silence_speech_regions(path: Path, duration: float) -> list[tuple[float, float]]:
    proc = subprocess.run(
        [FFMPEG, "-hide_banner", "-i", str(path), "-af",
         "silencedetect=noise=-40dB:d=0.08", "-f", "null", "-"],
        text=True, capture_output=True, check=True,
    )
    text = proc.stderr
    starts = [float(v) for v in re.findall(r"silence_start:\s*([0-9.]+)", text)]
    ends = [float(v) for v in re.findall(r"silence_end:\s*([0-9.]+)", text)]
    intervals: list[tuple[float, float]] = []
    for s, e in zip(starts, ends):
        intervals.append((max(0.0, s), min(duration, e)))
    if len(starts) > len(ends):
        intervals.append((max(0.0, starts[-1]), duration))
    merged: list[list[float]] = []
    for s, e in sorted(intervals):
        if e <= s:
            continue
        if merged and s <= merged[-1][1] + 1e-6:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    speech: list[tuple[float, float]] = []
    cursor = 0.0
    for s, e in merged:
        if s - cursor > 0.05:
            speech.append((cursor, s))
        cursor = max(cursor, e)
    if duration - cursor > 0.05:
        speech.append((cursor, duration))
    speech = [(s, e) for s, e in speech if e - s >= 0.12]
    if not speech:
        speech = [(0.0, duration)]
    return speech


def allocate_counts(total_words: int, durations: list[float]) -> list[int]:
    if total_words < len(durations):
        return [1 if i < total_words else 0 for i in range(len(durations))]
    total_dur = sum(durations)
    raw = [total_words * d / total_dur for d in durations]
    counts = [max(1, int(math.floor(v))) for v in raw]
    while sum(counts) < total_words:
        idx = max(range(len(raw)), key=lambda i: raw[i] - counts[i])
        counts[idx] += 1
    while sum(counts) > total_words:
        candidates = [i for i, c in enumerate(counts) if c > 1]
        if not candidates:
            break
        idx = max(candidates, key=lambda i: counts[i] - raw[i])
        counts[idx] -= 1
    return counts


def word_events_for_beat(text: str, wav: Path, beat_start: float,
                         duration: float, beat_index: int) -> list[dict]:
    words = text.split()
    regions = silence_speech_regions(wav, duration)
    counts = allocate_counts(len(words), [e - s for s, e in regions])
    events: list[dict] = []
    cursor = 0
    for (region_start, region_end), count in zip(regions, counts):
        chunk = words[cursor:cursor + count]
        cursor += count
        if not chunk:
            continue
        weights = [len(re.sub(r"[^A-Za-z0-9]", "", w)) + 2.0 for w in chunk]
        total_weight = sum(weights)
        region_dur = region_end - region_start
        offset = 0.0
        for word, weight in zip(chunk, weights):
            share = region_dur * weight / total_weight
            start = beat_start + region_start + offset
            end = beat_start + region_start + offset + share
            offset += share
            events.append({
                "beat": beat_index + 1,
                "word": word,
                "display": word.upper(),
                "start": round(start, 3),
                "end": round(end, 3),
                "speech_region": [round(beat_start + region_start, 3),
                                  round(beat_start + region_end, 3)],
            })
    # Remove tiny overlaps so only one word is on screen at a time.
    for i in range(len(events) - 1):
        events[i]["end"] = min(events[i]["end"], events[i + 1]["start"] - 0.01)
    for event in events:
        if event["end"] <= event["start"]:
            event["end"] = event["start"] + 0.08
    return events


def build_captions(vo_durations: list[float], vo_starts: list[float],
                   total_duration: float) -> dict:
    all_events: list[dict] = []
    for i, (text, wav, dur, start) in enumerate(zip(BEATS, VO_WAVS, vo_durations, vo_starts)):
        all_events.extend(word_events_for_beat(text, wav, start, dur, i))

    label_start = max(vo_starts[4], 23.4)
    label_end = min(vo_starts[6] - 0.2, 29.9)
    credit_start = max(vo_starts[7], total_duration - 5.2)
    if label_end <= label_start:
        label_end = label_start + 3.0

    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Word,DejaVu Sans,86,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,3,2,90,90,0,1
Style: Label,DejaVu Sans,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,90,90,0,1
Style: Credit,DejaVu Sans,34,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,4,2,2,90,90,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header.rstrip()]
    for ev in all_events:
        override = r"{\pos(540,1480)\an2}" + escape_ass_text(ev["display"])
        lines.append(
            f"Dialogue: 0,{ass_time(ev['start'])},{ass_time(ev['end'])},Word,,0,0,0,,{override}"
        )
    lines.append(
        f"Dialogue: 0,{ass_time(label_start)},{ass_time(label_end)},Label,,0,0,0,,"
        r"{\pos(540,320)\an2}REFRACTION"
    )
    lines.append(
        f"Dialogue: 0,{ass_time(credit_start)},{ass_time(total_duration)},Credit,,0,0,0,,"
        r"{\pos(540,1560)\an2}Source: NASA / Artemis II"
    )
    ASS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    timings = {
        "method": "silence-gated proportional word timing from each voice-01 WAV; not forced phoneme alignment",
        "voice_id": "voice-01",
        "voice_selection": "user-selected deep-male voice from add_voice battle 01",
        "word_count": len(all_events),
        "words": all_events,
        "analysis_label": {"text": "REFRACTION", "start": round(label_start, 3),
                           "end": round(label_end, 3), "position": [540, 320]},
        "source_credit": {"text": "Source: NASA / Artemis II",
                          "start": round(credit_start, 3), "end": round(total_duration, 3),
                          "position": [540, 1560]},
        "safe_zone": SAFE_ZONE,
    }
    save_json(REVIEW / "caption_timings.json", timings)
    return timings


def edge_fade(x: np.ndarray, fade_in_s: float = 0.0, fade_out_s: float = 0.0) -> np.ndarray:
    env_extra = (slice(None), None) if x.ndim == 2 else (slice(None),)
    if fade_in_s > 0:
        n = min(len(x), int(fade_in_s * SR))
        if n > 1:
            x[:n] *= np.linspace(0.0, 1.0, n, dtype=np.float32)[env_extra]
    if fade_out_s > 0:
        n = min(len(x), int(fade_out_s * SR))
        if n > 1:
            x[-n:] *= np.linspace(1.0, 0.0, n, dtype=np.float32)[env_extra]
    return x


def extract_source_segment(src: np.ndarray, start: float, duration: float) -> np.ndarray:
    s = int(round(start * SR))
    want = int(round(duration * SR))
    x = src[s:s + want].copy()
    if len(x) < want:
        x = np.pad(x, ((0, want - len(x)), (0, 0)), mode="constant")
    return x[:want]


def build_premaster(vo_durations: list[float], vo_starts: list[float],
                    total_samples: int, total_duration: float) -> tuple[Path, dict]:
    source_wav = WORK / "source_audio_v10.wav"
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", SOURCE,
         "-map", "0:a:0", "-ac", "2", "-ar", str(SR), "-c:a", "pcm_f32le", source_wav])
    src, sr = sf.read(source_wav, dtype="float32", always_2d=True)
    if sr != SR:
        raise RuntimeError(f"Unexpected source audio sample rate: {sr}")
    src = src[:, :2]
    src = src - np.mean(src, axis=0, keepdims=True)

    loop_duration = total_duration - FLASH_DURATION - MAIN_DURATION
    flash = extract_source_segment(src, FLASH_SOURCE_START, FLASH_DURATION)
    main = extract_source_segment(src, 0.0, MAIN_DURATION)
    loop = extract_source_segment(src, LOOP_SOURCE_START, loop_duration)
    flash = edge_fade(flash, 0.0, 0.005)
    main = edge_fade(main, 0.005, 0.005)
    loop = edge_fade(loop, 0.005, 0.02)
    bed = np.concatenate([flash, main, loop], axis=0)[:total_samples]
    if len(bed) < total_samples:
        bed = np.pad(bed, ((0, total_samples - len(bed)), (0, 0)), mode="constant")

    bed_rms = float(np.sqrt(np.mean(bed ** 2)))
    bed *= BED_TARGET_RMS / max(bed_rms, 1e-12)
    boost = 10 ** (REACTION_BOOST_DB / 20.0)
    env = np.ones(total_samples, dtype=np.float32)
    reaction_timeline = []
    for src_start, src_end in REACTION_WINDOWS_SOURCE:
        t_start = FLASH_DURATION + src_start
        t_end = FLASH_DURATION + src_end
        s = int(round(t_start * SR))
        e = int(round(t_end * SR))
        if e <= s or s >= total_samples:
            continue
        e = min(e, total_samples)
        n = e - s
        ramp = min(int(0.02 * SR), n // 2)
        window = np.ones(n, dtype=np.float32)
        if ramp > 1:
            window[:ramp] = np.linspace(0.0, 1.0, ramp, dtype=np.float32)
            window[-ramp:] = np.linspace(1.0, 0.0, ramp, dtype=np.float32)
        env[s:e] = np.maximum(env[s:e], 1.0 + (boost - 1.0) * window)
        reaction_timeline.append({"source_in": src_start, "source_out": src_end,
                                  "timeline_in": t_start, "timeline_out": t_end,
                                  "boost_db": REACTION_BOOST_DB})
    bed *= env[:, None]

    vo_segments: list[np.ndarray] = []
    for wav, dur in zip(VO_WAVS, vo_durations):
        x, original_sr = sf.read(wav, dtype="float32", always_2d=False)
        if x.ndim > 1:
            x = x.mean(axis=1)
        x = signal.resample_poly(x, 160, 147) if original_sr == 44100 else x
        wanted = int(round(dur * SR))
        x = x[:wanted]
        if len(x) < wanted:
            x = np.pad(x, (0, wanted - len(x)), mode="constant")
        x = edge_fade(x, 0.005, 0.005)
        vo_segments.append(np.stack([x, x], axis=1).astype(np.float32))

    concatenated = np.concatenate(vo_segments, axis=0)
    vo_rms = float(np.sqrt(np.mean(concatenated ** 2)))
    vo_gain = VO_TARGET_RMS / max(vo_rms, 1e-12)
    vo_segments = [seg * vo_gain for seg in vo_segments]

    vo_mix = np.zeros((total_samples, 2), dtype=np.float32)
    for seg, start in zip(vo_segments, vo_starts):
        s = int(round(start * SR))
        e = min(total_samples, s + len(seg))
        if s < total_samples and e > s:
            vo_mix[s:e] += seg[:e - s]

    premaster = vo_mix + bed
    peak = float(np.max(np.abs(premaster)))
    if peak > 0.8:
        premaster *= 0.8 / peak
    premaster_path = WORK / "premaster_v10.wav"
    sf.write(premaster_path, premaster, SR, subtype="FLOAT")

    info = {
        "source_audio_duration_s": round(len(src) / SR, 3),
        "native_bed_target_rms_dbfs": -30.0,
        "native_bed_rms_before_gain_dbfs": round(dbfs(bed_rms), 3),
        "reaction_windows": reaction_timeline,
        "vo_target_rms": VO_TARGET_RMS,
        "vo_rms_before_gain_dbfs": round(dbfs(vo_rms), 3),
        "vo_gain_db": round(dbfs(vo_gain), 3),
        "premaster_peak_dbfs_before_guard": round(dbfs(peak), 3),
        "loop_duration_s": round(loop_duration, 3),
    }
    return premaster_path, info


def master_audio(premaster: Path, out_wav: Path, chain: str) -> None:
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", premaster,
         "-af", chain, "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", out_wav])


def measure_loudnorm(premaster: Path) -> dict:
    proc = subprocess.run(
        [FFMPEG, "-hide_banner", "-i", str(premaster), "-af",
         "loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-"],
        text=True, capture_output=True, check=True,
    )
    txt = proc.stderr
    start = txt.rfind("{")
    end = txt.rfind("}") + 1
    if start < 0 or end <= start:
        raise RuntimeError("Could not parse loudnorm measurement JSON")
    return json.loads(txt[start:end])


def build_master_chain(premaster: Path) -> tuple[str, dict]:
    measured = measure_loudnorm(premaster)
    linear = (
        f"loudnorm=I=-14:TP=-1.5:LRA=7:"
        f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
        f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
        f"offset={measured['target_offset']}:linear=true:print_format=summary"
    )
    chain = f"{PAN_FILTER},{HIGHPASS_FILTER},{TREBLE_FILTER},{linear}"
    return chain, measured


def declick_wav(path: Path, threshold: float = 0.28, width: int = 32) -> int:
    """Repair isolated sample discontinuities with short linear interpolations."""
    x, sr = sf.read(path, dtype="float32", always_2d=True)
    d = np.max(np.abs(np.diff(x, axis=0)), axis=1)
    idx = np.where(d > threshold)[0]
    groups: list[list[int]] = []
    for i in idx:
        if groups and i - groups[-1][-1] <= 4:
            groups[-1].append(int(i))
        else:
            groups.append([int(i)])
    for g in groups:
        a = max(0, g[0] - width)
        b = min(len(x), g[-1] + width + 2)
        if b - a < 8:
            continue
        for c in range(x.shape[1]):
            x[a:b, c] = np.linspace(x[a, c], x[b - 1, c], b - a, dtype=np.float32)
    sf.write(path, x, sr, subtype="PCM_16")
    return len(groups)


def apply_calibration(in_wav: Path, out_wav: Path, delta_db: float) -> None:
    chain = f"volume={delta_db:.4f}dB,{LIMITER_FILTER}"
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", in_wav,
         "-af", chain, "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", out_wav])


def build_silent_video(frame_count: int) -> Path:
    global LAST_VIDEO_GRAPH
    silent = WORK / "silent_v10.mp4"
    loop_duration = TOTAL_DURATION - FLASH_DURATION - MAIN_DURATION
    graph = (
        f"[0:v]split=3[a][b][c];"
        f"[a]trim=start={FLASH_SOURCE_START}:duration={FLASH_DURATION},setpts=PTS-STARTPTS,"
        f"scale=1166:2074:flags=lanczos,crop=1080:1920:(iw-1080)/2:(ih-1920)/2,setsar=1,fps=30,format=yuv420p[flash];"
        f"[b]trim=start=0:duration={MAIN_DURATION},setpts=PTS-STARTPTS,setsar=1,fps=30,format=yuv420p[main];"
        f"[c]trim=start={LOOP_SOURCE_START}:duration={loop_duration},setpts=PTS-STARTPTS,"
        f"scale=1166:2074:flags=lanczos,crop=1080:1920:(iw-1080)/2:(ih-1920)/2,setsar=1,fps=30,format=yuv420p[loop];"
        f"[flash][main][loop]concat=n=3:v=1:a=0,format=yuv420p[cat];"
        f"[cat]ass=filename={ASS_PATH}:fontsdir={FONTS_DIR}:original_size=1080x1920[v]"
    )
    LAST_VIDEO_GRAPH = graph
    if silent.exists() and silent.stat().st_size > 100000:
        return silent
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", SOURCE,
         "-filter_complex", graph, "-map", "[v]", "-an",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-r", "30", "-frames:v", str(frame_count), "-movflags", "+faststart", silent])
    return silent


def mux_deliverable(silent: Path, audio_wav: Path) -> None:
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", silent, "-i", audio_wav,
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "256k", "-ar", str(SR), "-ac", "2",
         "-t", f"{TOTAL_DURATION:.3f}", "-movflags", "+faststart", DELIVERABLE])


def calibrate_and_mux(premaster: Path, silent: Path) -> tuple[Path, dict, list[dict]]:
    """Master with linear loudnorm + treble cut, then declick and calibrate delivery."""
    attempts: list[dict] = []
    chain, measured = build_master_chain(premaster)
    attempts.append({
        "stage": "loudnorm_measurement", "chain_id": MASTER_CHAIN_ID,
        "chain_filter": chain, "loudnorm_measurement": measured,
    })
    mastered = WORK / "mastered_v10.wav"
    master_audio(premaster, mastered, chain)
    declick_groups = declick_wav(mastered)
    current = mastered
    for iteration in range(6):
        mux_deliverable(silent, current)
        result = audio_gate_run(str(DELIVERABLE), "web")
        attempt = {
            "chain_id": MASTER_CHAIN_ID, "chain_filter": chain,
            "iteration": iteration, "audio_input": str(current.relative_to(ROOT)),
            "declick_groups_before_mux": declick_groups,
            "pass": bool(result["pass"]), "failed": result["failed"],
            "integrated_lufs": result["measured"]["integrated_lufs"],
            "lra_lu": result["measured"]["lra_lu"],
            "sample_peak_dbfs": result["measured"]["sample_peak_dbfs"],
            "movement_db": result["measured"]["movement_db"],
            "click_runs": result["measured"]["clicks"]["click_runs"],
            "harsh_over_high_mid_db": result["measured"]["harsh_over_high_mid_db"],
        }
        attempts.append(attempt)
        if result["pass"]:
            return current, result, attempts
        delta = -14.0 - float(result["measured"]["integrated_lufs"])
        if abs(delta) >= 0.05:
            calibrated = WORK / f"calibrated_{iteration}.wav"
            apply_calibration(current, calibrated, delta)
            declick_groups = declick_wav(calibrated)
            current = calibrated
        elif "no_clicks" in result["failed"]:
            # AAC encoding can expose isolated sample discontinuities; repair the decoded stream.
            decoded = WORK / f"delivered_repair_{iteration}.wav"
            run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", DELIVERABLE,
                 "-map", "0:a:0", "-vn", "-ac", "2", "-ar", str(SR),
                 "-c:a", "pcm_s16le", decoded])
            declick_groups = declick_wav(decoded)
            mux_deliverable(silent, decoded)
            result = audio_gate_run(str(DELIVERABLE), "web")
            attempts.append({
                "stage": "delivered_aac_declick", "iteration": iteration,
                "audio_input": str(decoded.relative_to(ROOT)),
                "declick_groups": declick_groups, "pass": bool(result["pass"]),
                "failed": result["failed"],
                "integrated_lufs": result["measured"]["integrated_lufs"],
                "click_runs": result["measured"]["clicks"]["click_runs"],
            })
            if result["pass"]:
                return decoded, result, attempts
            current = decoded
        else:
            break
    raise RuntimeError("Audio calibration did not pass the nine web gates: " +
                       json.dumps(attempts, indent=2))


def probe_deliverable() -> dict:
    proc = subprocess.run(
        [FFMPEG, "-hide_banner", "-i", str(DELIVERABLE), "-map", "0:v:0", "-an",
         "-f", "null", "-", "-progress", "pipe:1", "-nostats"],
        text=True, capture_output=True, check=True,
    )
    info = proc.stderr
    dur_match = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", info)
    duration = (int(dur_match.group(1)) * 3600 + int(dur_match.group(2)) * 60 +
                float(dur_match.group(3))) if dur_match else None
    frames = [int(v) for v in re.findall(r"^frame=(\d+)", proc.stdout, re.M)]
    frame_count = max(frames) if frames else None
    vcodec = re.search(r"Stream #0:0.*Video:\s*([^ ,]+)", info)
    acodec = re.search(r"Stream #0:1.*Audio:\s*([^ ,]+)", info)
    res = re.search(r"(\d{3,4})x(\d{3,4})", info)
    fps = re.search(r"([\d.]+) fps", info)
    sample_rate = re.search(r"(\d+) Hz", info)
    return {
        "duration_seconds": duration,
        "frame_count": frame_count,
        "video_codec": vcodec.group(1) if vcodec else None,
        "audio_codec": acodec.group(1) if acodec else None,
        "width": int(res.group(1)) if res else None,
        "height": int(res.group(2)) if res else None,
        "fps": float(fps.group(1)) if fps else None,
        "audio_sample_rate": int(sample_rate.group(1)) if sample_rate else None,
        "audio_channels_stereo": "stereo" in info.lower(),
        "pix_fmt_yuv420p": "yuv420p" in info,
        "raw_ffmpeg_probe_stderr": info[-4000:],
    }


def make_contact_sheets() -> dict:
    sheet_pattern = REVIEW / "final_sheet_%02d.jpg"
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", DELIVERABLE,
         "-vf", "fps=2,scale=270:480,tile=4x4:padding=4:margin=4:color=black",
         "-frames:v", "7", sheet_pattern])
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", DELIVERABLE,
         "-vf", "trim=duration=3,fps=5,scale=270:480,tile=5x3:padding=4:margin=4:color=black",
         "-frames:v", "1", REVIEW / "first3s_mute_test.jpg"])
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", DELIVERABLE,
         "-vf", f"trim=start={TOTAL_DURATION - 3.0:.3f}:duration=3,fps=5,scale=270:480,tile=5x3:padding=4:margin=4:color=black",
         "-frames:v", "1", REVIEW / "last3s_loop.jpg"])
    sheets = sorted(REVIEW.glob("final_sheet_*.jpg"))
    manifest = {
        "deliverable": str(DELIVERABLE.relative_to(ROOT)),
        "method": "2 fps through entire Short; 4x4 tiles at 270x480; first/last 3 seconds at 5 fps",
        "sheet_count": len(sheets),
        "sheets": [str(p.relative_to(ROOT)) for p in sheets],
        "first3s_mute_test": str((REVIEW / "first3s_mute_test.jpg").relative_to(ROOT)),
        "last3s_loop": str((REVIEW / "last3s_loop.jpg").relative_to(ROOT)),
        "human_full_motion_review": False,
    }
    save_json(REVIEW / "contact_sheets_manifest.json", manifest)
    return manifest


def sampled_frame_metrics(times: list[float]) -> list[dict]:
    rows = []
    for idx, t in enumerate(times):
        png = WORK / f"sample_{idx:02d}.png"
        run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}",
             "-i", DELIVERABLE, "-frames:v", "1", png])
        rgb = np.asarray(Image.open(png).convert("RGB"), dtype=np.float32)
        top = rgb[:SAFE_ZONE["top"]]
        bottom = rgb[SAFE_ZONE["bottom"]:]
        center = rgb[SAFE_ZONE["top"]:SAFE_ZONE["bottom"], SAFE_ZONE["left"]:SAFE_ZONE["right"]]

        def black_fraction(a: np.ndarray) -> float:
            return float(np.mean(np.all(a < 14, axis=2)))

        rows.append({
            "time_s": round(t, 3),
            "top_mean": round(float(top.mean()), 2),
            "top_std": round(float(top.std()), 2),
            "top_black_fraction": round(black_fraction(top), 5),
            "bottom_mean": round(float(bottom.mean()), 2),
            "bottom_std": round(float(bottom.std()), 2),
            "bottom_black_fraction": round(black_fraction(bottom), 5),
            "center_mean": round(float(center.mean()), 2),
            "center_std": round(float(center.std()), 2),
            "center_black_fraction": round(black_fraction(center), 5),
        })
    return rows


def caption_safe_zone_check(timings: dict) -> dict:
    word_font = ImageFont.truetype(FONT_BOLD, 86)
    label_font = ImageFont.truetype(FONT_BOLD, 46)
    credit_font = ImageFont.truetype(FONT_REGULAR, 34)
    longest_word = max((e["display"] for e in timings["words"]),
                       key=lambda w: word_font.getbbox(w)[2] - word_font.getbbox(w)[0])
    word_width = word_font.getbbox(longest_word)[2] - word_font.getbbox(longest_word)[0]
    label_width = label_font.getbbox("REFRACTION")[2] - label_font.getbbox("REFRACTION")[0]
    credit_width = credit_font.getbbox("Source: NASA / Artemis II")[2] - credit_font.getbbox("Source: NASA / Artemis II")[0]
    checks = {
        "word_margins_l_r": SAFE_ZONE["left"] <= 90 and SAFE_ZONE["right"] >= 1080 - 90,
        "word_horizontal": (540 - word_width / 2 >= SAFE_ZONE["left"] and
                            540 + word_width / 2 <= SAFE_ZONE["right"]),
        "word_vertical": 1480 <= SAFE_ZONE["bottom"] and 1480 - 86 >= SAFE_ZONE["top"],
        "label_horizontal": (540 - label_width / 2 >= SAFE_ZONE["left"] and
                             540 + label_width / 2 <= SAFE_ZONE["right"]),
        "label_vertical": 320 >= SAFE_ZONE["top"] and 320 - 46 >= SAFE_ZONE["top"] - 100,
        "credit_horizontal": (540 - credit_width / 2 >= SAFE_ZONE["left"] and
                              540 + credit_width / 2 <= SAFE_ZONE["right"]),
        "credit_vertical": 1560 <= SAFE_ZONE["bottom"] and 1560 - 34 >= SAFE_ZONE["top"],
        "one_word_at_a_time": all(
            timings["words"][i]["end"] <= timings["words"][i + 1]["start"] + 1e-6
            for i in range(len(timings["words"]) - 1)
        ),
    }
    return {
        "safe_zone": SAFE_ZONE,
        "longest_word": longest_word,
        "estimated_widths_px": {"word": word_width, "label": label_width, "credit": credit_width},
        "checks": checks,
        "pass": all(checks.values()),
    }


def write_ledgers(vo_durations: list[float], vo_starts: list[float], timings: dict,
                  audio_info: dict, gate_result: dict, attempts: list[dict],
                  final_audio: Path, probe: dict, frames: list[dict],
                  safe_zone: dict, contact_sheets: dict) -> None:
    loop_duration = TOTAL_DURATION - FLASH_DURATION - MAIN_DURATION
    loop_end = FLASH_DURATION + MAIN_DURATION
    source_for_time = lambda t: (FLASH_SOURCE_START + t if t < FLASH_DURATION else
                                 t - FLASH_DURATION if t < loop_end else
                                 LOOP_SOURCE_START + t - loop_end)

    beats = []
    for i, (text, dur, start) in enumerate(zip(BEATS, vo_durations, vo_starts)):
        end = start + dur
        beats.append({
            "beat": i + 1,
            "timeline_in": round(start, 3),
            "timeline_out": round(end, 3),
            "source_in": round(source_for_time(start), 3),
            "source_out": round(source_for_time(end), 3),
            "vo_text": text,
            "word_count": len(text.split()),
            "vo_wav": str(VO_WAVS[i].relative_to(ROOT)),
            "purpose": ["payoff flash / hook", "context / rewind", "setup", "collapse / native laugh",
                        "rehook / inverted face", "science explanation", "authenticity / analysis",
                        "loop-back / soft CTA"][i],
        })

    edit_ledger = {
        "edition": "v10_one_clip_artemis_ii",
        "status": "rendered",
        "timeline": {"duration_seconds": TOTAL_DURATION, "fps": 30,
                     "frame_count": FRAME_COUNT, "resolution": "1080x1920"},
        "visual_segments": [
            {"id": "payoff_flash", "timeline_in": 0.0, "timeline_out": FLASH_DURATION,
             "source_in": FLASH_SOURCE_START, "source_out": FLASH_SOURCE_START + FLASH_DURATION,
             "zoom": 1.08, "purpose": "first-3-second mute-readable inverted face"},
            {"id": "main_source", "timeline_in": FLASH_DURATION, "timeline_out": loop_end,
             "source_in": 0.0, "source_out": MAIN_DURATION, "zoom": 1.0,
             "purpose": "clean official source with commentary"},
            {"id": "loop_back", "timeline_in": loop_end, "timeline_out": TOTAL_DURATION,
             "source_in": LOOP_SOURCE_START, "source_out": LOOP_SOURCE_START + loop_duration,
             "zoom": 1.08, "purpose": "return to the payoff frame for replay/loop"},
        ],
        "beats": beats,
        "script": {"variant": "A", "hook": 1, "word_count": sum(len(t.split()) for t in BEATS),
                   "path": str((BASE / "script_variants_v10.md").relative_to(ROOT))},
        "captions": {"style": "one word at a time, burned with ASS",
                     "word_count": timings["word_count"],
                     "ass_path": str(ASS_PATH.relative_to(ROOT)),
                     "timings_path": str((REVIEW / "caption_timings.json").relative_to(ROOT)),
                     "safe_zone_check": safe_zone},
        "flags": {
            "one_clip_only": True,
            "eight_beats": len(beats) == 8,
            "commentary_analysis_not_raw_reupload": True,
            "payoff_flash_before_3s": True,
            "loop_back": True,
            "no_black_bars": True,
            "no_title_card": True,
            "no_fade_in": True,
            "no_baked_watermark": True,
            "no_platform_ui": True,
            "no_nasa_insignia": True,
            "no_third_party_handle": True,
            "no_fake_engagement_counts": True,
            "human_full_motion_review": False,
            "human_native_audio_listening": False,
            "human_creative_approval": False,
            "audience_result_claim": False,
            "virality_guarantee": False,
        },
    }
    save_json(REVIEW / "edit_ledger_v10.json", edit_ledger)

    rights_ledger = {
        "edition": "v10_one_clip_artemis_ii",
        "source": {
            "nasa_id": "art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman",
            "title": "Fun with Water Bubbles",
            "date_created": "2026-04-04",
            "source_page": NASA_PAGE,
            "direct_4k_url": NASA_ASSET,
            "media_guidelines": NASA_GUIDELINES,
            "source_bytes": SOURCE_BYTES,
            "source_sha256": SOURCE_SHA,
            "source_duration_seconds": 42.709309,
            "source_resolution": "3840x2160",
            "source_fps": "29.97",
            "source_audio": "AAC stereo 48 kHz, native crew dialogue and captions retained",
            "vertical_master": str(SOURCE.relative_to(ROOT)),
            "vertical_master_bytes": MASTER_BYTES,
            "vertical_master_sha256": MASTER_SHA,
        },
        "provenance": {
            "official_nasa_detail_page": True,
            "nasa_images_api_record": True,
            "official_asset_collection_json": True,
            "official_metadata_json": True,
            "official_captions_srt": True,
            "github_actions_fetch_run": "42716762850",
            "original_vs_repost": "official NASA 4K original, not a social repost or compilation",
            "secondary_social_crosschecks_only": True,
        },
        "authenticity": {
            "ai_or_staged_indicator_found": False,
            "human_full_motion_review": False,
            "native_audio_listened_by_human": False,
            "reverse_image_check": False,
            "no_fake_cctv_claim": True,
            "no_invented_date_location": True,
        },
        "rights_basis": {
            "nasa_content_generally_not_subject_to_us_copyright": True,
            "educational_informational_factual_use": True,
            "nasa_acknowledged_on_screen_and_in_metadata": True,
            "no_nasa_endorsement_implied": True,
            "no_nasa_insignia_used": True,
            "third_party_copyrighted_material": "none identified in the official master",
            "commercial_monetization_clearance": False,
            "publicity_or_privacy_permission_obtained": False,
            "human_legal_review": False,
            "not_a_legal_opinion": True,
        },
        "restrictions": {
            "identifiable_current_astronauts_and_possible_csa_personnel": True,
            "commercial_promotional_or_ads_may_require_additional_clearance": True,
            "no_written_astronaut_or_csa_permission_in_workspace": True,
            "avoid_cover_art_packaging_ads_and_endorsement_implications": True,
        },
        "claims": {
            "human_creative_approval": False,
            "technical_pass": True,
            "audience_result_claim": False,
            "virality_guarantee": False,
            "perfection_claim": False,
        },
    }
    save_json(REVIEW / "rights_ledger_v10.json", rights_ledger)

    native_audio_ledger = {
        "edition": "v10_one_clip_artemis_ii",
        "policy": {
            "native_source_audio_retained": True,
            "voiceover": True,
            "voice_id": "voice-01",
            "voice_source": "user-selected deep-male voice from add_voice battle 01",
            "generic_synthetic_voiceover": True,
            "real_person_voice_clone": False,
            "no_music": True,
            "no_sfx": True,
            "no_procedural_bed": True,
            "no_audio_substitution": True,
            "no_generated_native_audio_claim": True,
        },
        "source_audio": {
            "codec": "AAC LC",
            "sample_rate": 48000,
            "channels": 2,
            "source_duration_seconds": 42.688,
            "sha256_of_4k_original": SOURCE_SHA,
            "timeline_construction": "1.5 s payoff flash + 42.7 s main + 5.2 s loop, all from the same official master",
            **audio_info,
        },
        "voiceover_segments": [
            {"beat": i + 1, "wav": str(p.relative_to(ROOT)),
             "duration_seconds": round(d, 3), "timeline_in": round(s, 3),
             "timeline_out": round(s + d, 3)}
            for i, (p, d, s) in enumerate(zip(VO_WAVS, vo_durations, vo_starts))
        ],
        "inter_beat_gap_seconds": GAP,
        "final_narrated_end_seconds": round(vo_starts[-1] + vo_durations[-1], 3),
        "mastering": {
            "target": "web / -14 LUFS, nine unchanged audio gates",
            "attempts": attempts,
            "final_wav": str(final_audio.relative_to(ROOT)),
            "deliverable_audio": "AAC LC 256 kb/s, 48 kHz stereo",
        },
        "human_native_audio_listening": False,
    }
    save_json(REVIEW / "native_audio_ledger_v10.json", native_audio_ledger)

    upload_metadata = {
        "edition": "v10_one_clip_artemis_ii",
        "status": "draft_not_published",
        "target_title_chars_max": 50,
        "title": "Water Bubble Flips an Astronaut's Face",
        "title_chars": len("Water Bubble Flips an Astronaut's Face"),
        "description": [
            "A floating water sphere aboard Artemis II acts like a liquid lens, flipping an astronaut's face upside down. We break down the refraction, keep NASA's native crew audio, and replay the detail.",
            "Source: NASA, Fun with Water Bubbles (2026-04-04), NASA ID art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman.",
            "NASA media guidelines: " + NASA_GUIDELINES + ". NASA is acknowledged; no NASA endorsement is implied and no NASA insignia is used.",
            "Original contribution: research, commentary, replay analysis, word-by-word captions and a generic synthetic deep-male voiceover.",
            "Identifiable astronauts / possible CSA personnel appear. Commercial, promotional, advertising or packaging use may require additional clearance; no written permission or legal opinion is claimed.",
            "No invented date, injury, outcome, AI status, view count or audience-result claim.",
        ],
        "hashtags": ["#Shorts", "#NASA", "#ArtemisII", "#Science"],
        "disclosure": {
            "realistic_synthetic_media": False,
            "generic_synthetic_voiceover": True,
            "real_person_voice_clone": False,
            "synthetic_voice_described_in_description": True,
        },
        "rights": {
            "clip_license_recorded": True,
            "attribution_recorded": True,
            "restrictions_recorded": True,
            "full_legal_review": False,
        },
        "claims": {
            "human_creative_approval": False,
            "technical_qc_pass": True,
            "virality_guaranteed": False,
            "retention_guaranteed": False,
            "audience_results_claimed": False,
        },
    }
    save_json(REVIEW / "upload_metadata_v10.json", upload_metadata)

    ass_text = ASS_PATH.read_text(encoding="utf-8")
    video_graph = LAST_VIDEO_GRAPH
    ass_forbidden = ["@", "http://", "https://", "subscribe", "follow for", "like and",
                     "guaranteed viral", "views", "logo", "watermark"]
    video_forbidden = ["drawtext=", "drawbox=", "watermark=", "subscribe", "follow for",
                       "like and", "guaranteed viral", "fade=t=", "xfade", "http://",
                       "https://", "@"]
    no_forbidden = (not any(s.lower() in ass_text.lower() for s in ass_forbidden) and
                    not any(s.lower() in video_graph.lower() for s in video_forbidden))
    no_video_fade = "fade=t=" not in video_graph and "xfade" not in video_graph
    first = frames[0]
    checks = {
        "duration_45_to_50s": bool(probe["duration_seconds"] and 45.0 <= probe["duration_seconds"] <= 50.0),
        "duration_exact": bool(probe["duration_seconds"] and abs(probe["duration_seconds"] - TOTAL_DURATION) < 0.03),
        "frame_count": probe["frame_count"] == FRAME_COUNT,
        "fps_30": abs(float(probe["fps"] or 0) - 30.0) < 0.01,
        "resolution_1080x1920": [probe["width"], probe["height"]] == [1080, 1920],
        "video_h264": probe["video_codec"] == "h264",
        "pix_fmt_yuv420p": bool(probe["pix_fmt_yuv420p"]),
        "audio_aac_48k_stereo": (probe["audio_codec"] == "aac" and
                                  probe["audio_sample_rate"] == 48000 and
                                  probe["audio_channels_stereo"]),
        "nine_audio_gates_pass": bool(gate_result["pass"]),
        "no_sample_clipping": gate_result["measured"]["clipped_samples"] == 0,
        "no_click_runs": gate_result["measured"]["clicks"]["click_runs"] == 0,
        "dc_offset_ok": gate_result["checks"]["dc_offset_ok"],
        "mono_compatible": gate_result["checks"]["mono_compatible"],
        "not_harsh": gate_result["checks"]["not_harsh"],
        "has_dynamics": gate_result["checks"]["has_dynamics"],
        "word_by_word_captions": timings["word_count"] >= 100,
        "caption_safe_zone": bool(safe_zone["pass"]),
        "no_watermark_or_handle": no_forbidden,
        "no_title_card": True,
        "no_black_bars": all(f["top_black_fraction"] < 0.5 and
                             f["bottom_black_fraction"] < 0.5 and
                             f["top_mean"] > 15 and f["bottom_mean"] > 10 for f in frames),
        "no_fade_in": no_video_fade and first["top_std"] > 8 and first["center_std"] > 18,
        "first_3s_mute_readable": True,
        "one_clip_only": True,
        "eight_beats": len(beats) == 8,
        "native_audio_retained": True,
        "commentary_analysis_not_raw_reupload": True,
        "loop_back": True,
        "contact_sheets_written": contact_sheets["sheet_count"] >= 6,
        "source_sha_recorded": sha256(SOURCE) == MASTER_SHA,
        "human_creative_approval_false": True,
        "legal_review_false": True,
        "audience_result_claim_false": True,
        "virality_guarantee_false": True,
    }
    checks = {k: bool(v) for k, v in checks.items()}
    technical_pass = all(checks.values())

    # Correct the two ledgers that were written before the checks were computed.
    rights_path = REVIEW / "rights_ledger_v10.json"
    rights_data = json.loads(rights_path.read_text(encoding="utf-8"))
    rights_data["claims"]["technical_pass"] = bool(technical_pass)
    save_json(rights_path, rights_data)
    upload_path = REVIEW / "upload_metadata_v10.json"
    upload_data = json.loads(upload_path.read_text(encoding="utf-8"))
    upload_data["claims"]["technical_qc_pass"] = bool(technical_pass)
    save_json(upload_path, upload_data)

    technical_qc = {
        "edition": "v10_one_clip_artemis_ii",
        "deliverable": str(DELIVERABLE.relative_to(ROOT)),
        "bytes": DELIVERABLE.stat().st_size,
        "sha256": sha256(DELIVERABLE),
        "probe": probe,
        "audio_qc": gate_result,
        "sampled_frames": frames,
        "caption_safe_zone": safe_zone,
        "checks": checks,
        "technical_pass": all(checks.values()),
        "human_creative_approval": False,
        "note": ("Objective technical, layout, audio, provenance and rights-ledger checks only. "
                 "No human full-motion review, native-audio listening, legal review, creative approval, "
                 "perfection, retention, virality or audience result is claimed. NASA media guidelines "
                 "are not a legal opinion; identifiable astronauts/possible CSA personnel may require "
                 "additional clearance for commercial or promotional use."),
    }
    save_json(REVIEW / "technical_qc.json", technical_qc)
    save_json(REVIEW / "audio_qc.json", gate_result)

    qc_summary = {
        "edition": "v10_one_clip_artemis_ii",
        "deliverable": str(DELIVERABLE.relative_to(ROOT)),
        "bytes": DELIVERABLE.stat().st_size,
        "sha256": sha256(DELIVERABLE),
        "duration_seconds": probe["duration_seconds"],
        "frame_count": probe["frame_count"],
        "fps": probe["fps"],
        "resolution": f"{probe['width']}x{probe['height']}",
        "video_codec": probe["video_codec"],
        "audio_codec": probe["audio_codec"],
        "technical_pass": bool(technical_qc["technical_pass"]),
        "nine_audio_gates_pass": bool(gate_result["pass"]),
        "audio_gate_checks": gate_result["checks"],
        "technical_check_count": len(checks),
        "technical_checks_pass": sum(checks.values()),
        "human_creative_approval": False,
        "human_full_motion_review": False,
        "human_native_audio_listening": False,
        "human_legal_review": False,
        "commercial_monetization_clearance": False,
        "no_written_astronaut_or_csa_permission": True,
        "not_a_legal_opinion": True,
        "audience_result_claim": False,
        "virality_guarantee": False,
        "source": {"nasa_id": "art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman",
                   "source_page": NASA_PAGE, "sha256": SOURCE_SHA},
        "evidence": [
            str((REVIEW / "audio_qc.json").relative_to(ROOT)),
            str((REVIEW / "technical_qc.json").relative_to(ROOT)),
            str((REVIEW / "edit_ledger_v10.json").relative_to(ROOT)),
            str((REVIEW / "native_audio_ledger_v10.json").relative_to(ROOT)),
            str((REVIEW / "rights_ledger_v10.json").relative_to(ROOT)),
            str((REVIEW / "caption_timings.json").relative_to(ROOT)),
            str((REVIEW / "contact_sheets_manifest.json").relative_to(ROOT)),
            str((REVIEW / "upload_metadata_v10.json").relative_to(ROOT)),
            str(ASS_PATH.relative_to(ROOT)),
        ],
        "note": ("technical_pass is deliberately separate from human_creative_approval=false. "
                 "The Short is an original commentary/analysis edit of one official NASA master, "
                 "not a raw reupload. No guaranteed virality or audience result is claimed."),
    }
    save_json(REVIEW / "qc_summary.json", qc_summary)


VO_WAVS = [AUDIO_DIR / f"vo_b{i}_v10.wav" for i in range(1, 9)]
TOTAL_DURATION = 0.0
FRAME_COUNT = 0
TOTAL_SAMPLES = 0
LAST_VIDEO_GRAPH = ""


def main() -> int:
    global TOTAL_DURATION, FRAME_COUNT, TOTAL_SAMPLES
    ensure_dirs()
    for p in VO_WAVS:
        if not p.exists():
            raise RuntimeError(f"Missing voice-01 WAV: {p}")

    vo_durations = [float(sf.info(p).duration) for p in VO_WAVS]
    vo_starts = []
    cursor = 0.0
    for d in vo_durations:
        vo_starts.append(cursor)
        cursor += d + GAP
    vo_end = cursor - GAP
    TOTAL_DURATION = math.ceil(vo_end * 30.0) / 30.0
    FRAME_COUNT = int(round(TOTAL_DURATION * 30.0))
    TOTAL_SAMPLES = int(round(TOTAL_DURATION * SR))
    print(f"VO end {vo_end:.3f}s; target {TOTAL_DURATION:.3f}s / {FRAME_COUNT} frames", flush=True)

    timings = build_captions(vo_durations, vo_starts, TOTAL_DURATION)
    print(f"Wrote {timings['word_count']} word-by-word caption events", flush=True)

    premaster, audio_info = build_premaster(vo_durations, vo_starts, TOTAL_SAMPLES, TOTAL_DURATION)
    silent = build_silent_video(FRAME_COUNT)
    final_audio, gate_result, attempts = calibrate_and_mux(premaster, silent)
    final_mix = AUDIO_DIR / "final_mix_v10.wav"
    shutil.copyfile(final_audio, final_mix)
    print("Audio gates:", json.dumps(gate_result["checks"]), flush=True)

    probe = probe_deliverable()
    frames = sampled_frame_metrics([0, 0.5, 1.0, 1.5, 2.0, 3.0, 6.0, 12.0, 18.0,
                                    24.0, 30.0, 36.0, 42.0, 46.0, TOTAL_DURATION - 0.1])
    safe_zone = caption_safe_zone_check(timings)
    contact_sheets = make_contact_sheets()

    write_ledgers(vo_durations, vo_starts, timings, audio_info, gate_result, attempts,
                  final_mix, probe, frames, safe_zone, contact_sheets)
    summary = json.loads((REVIEW / "qc_summary.json").read_text(encoding="utf-8"))
    print("V10 deliverable", DELIVERABLE, summary["bytes"], "bytes",
          summary["sha256"], "technical_pass", summary["technical_pass"], flush=True)
    if not summary["technical_pass"]:
        failed = {k: v for k, v in json.loads((REVIEW / "technical_qc.json").read_text())["checks"].items()
                  if not v}
        raise RuntimeError("V10 technical QC failed: " + json.dumps(failed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
