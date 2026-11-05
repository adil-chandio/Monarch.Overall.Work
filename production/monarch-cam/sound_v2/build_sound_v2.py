#!/usr/bin/env python3
"""Rebuild only the Monarch Cam opening's soundtrack from licensed source audio.

The approved V1 H.264 stream is copied without modification. The old procedural
background is never decoded or reused. Narration is regenerated from the approved
script with the existing bounded-retry Edge TTS route, then combined with CC0 music,
real forest ambience and professionally produced CC0 transition/graphic SFX.

Earshot assists with music-section ranking, SFX trim selection and final timeline /
scorecard review. All creative placements come from the picture-derived cues.json.
No sound is synthesized by this script and no unsupported wildlife/vehicle event is
added. Run showreel.audio_qc.gates on the returned MP4 as the final measured gate.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time

import numpy as np
import requests
import soundfile as sf
from scipy import signal, ndimage

ROOT = Path(__file__).resolve().parent
PRODUCTION = ROOT.parent
REPO = PRODUCTION.parents[1]
sys.path.insert(0, str(PRODUCTION))
import build_preview as preview  # noqa: E402  (reuse approved narration only)

MANIFEST = json.loads((ROOT / "source_manifest.json").read_text(encoding="utf-8"))
CUES = json.loads((ROOT / "cues.json").read_text(encoding="utf-8"))
WORK = PRODUCTION / "work/sound_v2"
SOURCES = WORK / "sources"
CANDIDATES = WORK / "music_candidates"
REVIEW = ROOT / "review"
OUT = REPO / "deliverables/MONARCH_CAM_Bear_Opening_30s_Sound_V2.mp4"
V1 = REPO / "deliverables/MONARCH_CAM_Bear_Opening_30s_Preview.mp4"
SR = 48000
DURATION = 30.0
FPS = 30
SAMPLES = int(round(DURATION * SR))
MUSIC_QUERY = (
    "restrained mysterious orchestral wildlife documentary underscore, slow ambient "
    "strings and piano, instrumental, gentle steady pacing"
)


def json_default(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return str(value)
    return str(value)


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=json_default), encoding="utf-8")


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    return subprocess.run([str(x) for x in cmd], **kwargs)


def ffmpeg(*args: str, capture: bool = False) -> subprocess.CompletedProcess:
    return run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", *args,
    ], capture_output=capture, check=True, text=capture)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download_assets() -> dict[str, Path]:
    SOURCES.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    ledger = []
    headers = {"User-Agent": "MonarchCamSoundV2/1.0 (licensed-audio-production)"}
    for asset in MANIFEST["assets"]:
        if asset["license"] != "CC0-1.0" or not asset.get("source_page_verified"):
            raise RuntimeError(f"Unverified or disallowed asset: {asset['id']}")
        path = SOURCES / asset["local_filename"]
        paths[asset["id"]] = path
        if not path.exists() or path.stat().st_size < 1000:
            error = None
            for attempt in range(1, 5):
                try:
                    response = requests.get(asset["download_url"], headers=headers, timeout=90)
                    response.raise_for_status()
                    if len(response.content) < 1000:
                        raise RuntimeError(f"Only {len(response.content)} bytes returned")
                    path.write_bytes(response.content)
                    break
                except Exception as exc:  # bounded retrieval retry, no fallback source substitution
                    error = exc
                    path.unlink(missing_ok=True)
                    if attempt == 4:
                        raise RuntimeError(f"Could not retrieve {asset['id']}: {error}") from error
                    time.sleep(attempt * 2)
        ledger.append({
            "id": asset["id"], "file": path.name, "bytes": path.stat().st_size,
            "sha256": sha256(path), "download_url": asset["download_url"],
            "source_page": asset["source_page"], "license": asset["license"],
        })
        print(f"Source {asset['id']}: {path.stat().st_size:,} bytes", flush=True)
    save_json(REVIEW / "source_file_ledger.json", ledger)
    return paths


def decode(path: Path, start: float = 0.0, duration: float | None = None,
           af: str | None = None, channels: int = 2) -> np.ndarray:
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-i", str(path)]
    if start > 0:
        cmd += ["-ss", f"{start:.6f}"]
    if duration is not None:
        cmd += ["-t", f"{duration:.6f}"]
    filters = []
    if af:
        filters.append(af)
    filters += [f"aresample={SR}"]
    cmd += ["-af", ",".join(filters), "-ac", str(channels), "-f", "f32le", "pipe:1"]
    proc = run(cmd, capture_output=True, check=True)
    if not proc.stdout:
        raise RuntimeError(f"No audio decoded from {path}")
    return np.frombuffer(proc.stdout, dtype=np.float32).reshape(-1, channels).copy()


def fit_stereo(clip: np.ndarray) -> np.ndarray:
    if clip.ndim == 1:
        return np.repeat(clip[:, None], 2, axis=1)
    return clip


def fade_edges(clip: np.ndarray, fade_in: float = 0.012, fade_out: float = 0.09) -> np.ndarray:
    out = clip.copy()
    fi = min(int(round(fade_in * SR)), len(out) // 3)
    fo = min(int(round(fade_out * SR)), len(out) // 3)
    if fi:
        out[:fi] *= np.sin(np.linspace(0, np.pi / 2, fi))[:, None]
    if fo:
        out[-fo:] *= np.cos(np.linspace(0, np.pi / 2, fo))[:, None]
    return out


def normalize_peak(clip: np.ndarray, peak_dbfs: float) -> np.ndarray:
    peak = float(np.max(np.abs(clip))) if len(clip) else 0.0
    if peak < 1e-9:
        raise RuntimeError("Cannot normalize a silent SFX excerpt")
    return clip * (10 ** (peak_dbfs / 20) / peak)


def normalize_loudness(clip: np.ndarray, target_lufs: float) -> tuple[np.ndarray, dict]:
    import pyloudnorm as pyln
    meter = pyln.Meter(SR)
    measured = float(meter.integrated_loudness(clip))
    if not math.isfinite(measured):
        raise RuntimeError("Non-finite source loudness")
    gain_db = float(np.clip(target_lufs - measured, -24.0, 24.0))
    gained = clip * (10 ** (gain_db / 20))
    # A source with an exceptional transient must not defeat the background-bus level.
    peak = float(np.max(np.abs(gained)))
    peak_cap_db = -8.0
    extra = 0.0
    if peak > 10 ** (peak_cap_db / 20):
        extra = peak_cap_db - 20 * math.log10(peak)
        gained *= 10 ** (extra / 20)
    return gained.astype(np.float32), {
        "input_lufs": round(measured, 3), "target_lufs_before_peak_cap": target_lufs,
        "gain_db": round(gain_db, 3), "peak_cap_adjustment_db": round(extra, 3),
        "output_lufs": round(float(meter.integrated_loudness(gained)), 3),
        "sample_peak_dbfs": round(20 * math.log10(max(float(np.max(np.abs(gained))), 1e-12)), 3),
    }


def trim_candidate(source: Path, start: float, target: Path) -> None:
    ffmpeg("-i", str(source), "-ss", f"{start:.6f}", "-t", "30.000",
           "-af", f"aresample={SR}", "-ac", "2", "-c:a", "pcm_s16le", str(target))


def select_music(paths: dict[str, Path], use_earshot: bool) -> tuple[dict, dict, object]:
    CANDIDATES.mkdir(parents=True, exist_ok=True)
    candidate_specs = []
    for asset_id, starts in {
        "music_dark": [0.0, 18.0, 36.0, 51.322],
        "music_backup": [0.0, 45.0, 90.0, 150.0],
    }.items():
        for start in starts:
            name = f"{asset_id}_{start:06.1f}.wav".replace(".", "p", 1)
            path = CANDIDATES / name
            trim_candidate(paths[asset_id], start, path)
            candidate_specs.append({"asset_id": asset_id, "source_start": start, "path": path})
    report = {
        "query": MUSIC_QUERY,
        "method": "Earshot CLAP ranking plus AudioSet vocal screening when available",
        "candidates": [{"asset_id": c["asset_id"], "source_start": c["source_start"], "file": c["path"].name}
                       for c in candidate_specs],
    }
    api = None
    selected = None
    if use_earshot:
        try:
            from earshot import api as earshot_api
            api = earshot_api
            ranking = api.rank([str(c["path"]) for c in candidate_specs], MUSIC_QUERY)
            report["ranking"] = ranking
            screened = []
            by_path = {str(c["path"]): c for c in candidate_specs}
            for ranked in ranking.get("results", []):
                candidate = by_path.get(ranked["path"])
                if candidate is None:
                    continue
                description = api.describe(ranked["path"])
                vocal_labels = {
                    "Speech", "Male speech, man speaking", "Female speech, woman speaking",
                    "Conversation", "Narration, monologue", "Singing", "Choir", "Vocal music",
                }
                vocal_probability = max(
                    [float(x["p"]) for x in description.get("audioset", []) if x["label"] in vocal_labels] or [0.0]
                )
                row = {"candidate": candidate["asset_id"], "source_start": candidate["source_start"],
                       "rank": ranked, "vocal_probability": vocal_probability,
                       "description_summary": description.get("summary")}
                screened.append(row)
                # Prefer the model's order, but do not knowingly choose a section with a
                # substantial vocal/speech label. Instrumental false positives stay reviewable.
                if selected is None and vocal_probability < 0.30:
                    selected = candidate
                    report["selected_description"] = description
            report["vocal_screen"] = screened
            if selected is None and ranking.get("results"):
                selected = by_path[str(ranking["results"][0]["path"])]
                report["selection_warning"] = "All candidates met the vocal-review threshold; inspect selected_description before publication."
        except Exception as exc:
            report["earshot_error"] = f"{type(exc).__name__}: {exc}"
            print("Earshot music review unavailable; using declared deterministic fallback.", flush=True)
            api = None
    if selected is None:
        selected = next(c for c in candidate_specs if c["asset_id"] == "music_dark" and c["source_start"] == 18.0)
        report["fallback"] = "Dark orchestral candidate at 18.0 s; fixed in advance, not a random selection."
    asset = next(a for a in MANIFEST["assets"] if a["id"] == selected["asset_id"])
    report["selected"] = {"asset_id": asset["id"], "title": asset["title"], "creator": asset["creator"],
                          "source_start": selected["source_start"], "duration": DURATION,
                          "source_page": asset["source_page"], "license": asset["license"]}
    save_json(REVIEW / "music_selection.json", report)
    return {"asset": asset, "start": selected["source_start"], "candidate_path": selected["path"]}, report, api


def peak_time(clip: np.ndarray) -> float:
    mono = np.max(np.abs(clip), axis=1)
    win = max(1, int(round(0.010 * SR)))
    envelope = np.convolve(mono, np.ones(win) / win, mode="same")
    return float(np.argmax(envelope) / SR)


def fallback_active_excerpt(path: Path, pre: float, post: float) -> tuple[np.ndarray, dict]:
    full = decode(path)
    peak = peak_time(full)
    start = max(0.0, peak - pre)
    end = min(len(full) / SR, peak + post)
    clip = full[int(start * SR):int(end * SR)].copy()
    return clip, {"start": round(start, 4), "end": round(end, 4), "method": "measured global peak fallback"}


def choose_sfx_excerpt(path: Path, query: str, pre: float, post: float,
                       api: object, use_earshot: bool) -> tuple[np.ndarray, dict]:
    report = {"query": query}
    chosen = None
    if use_earshot and api is not None:
        try:
            found = api.find(str(path), query, top=6, kind="event")
            report["earshot_find"] = found
            segments = found.get("segments", [])
            # Prefer clean edges and a useful one-shot duration while retaining Earshot's rank.
            viable = [s for s in segments if 0.12 <= s["duration"] <= 4.0]
            clean = [s for s in viable if not s.get("cut")]
            chosen = (clean or viable or [None])[0]
        except Exception as exc:
            report["earshot_error"] = f"{type(exc).__name__}: {exc}"
    if chosen is not None:
        start = max(0.0, float(chosen["start"]))
        end = max(start + 0.05, float(chosen["end"]))
        clip = decode(path, start=start, duration=end - start)
        report["selected_source_range"] = {"start": start, "end": end, "earshot": chosen}
    else:
        clip, fallback = fallback_active_excerpt(path, pre, post)
        start, end = fallback["start"], fallback["end"]
        report["selected_source_range"] = fallback
    # Bound the designed gesture around its own measured peak even when the model
    # returned a long take. Short edge fades avoid cut clicks; no audio is synthesized.
    local_peak = peak_time(clip)
    trim_start = max(0.0, local_peak - pre)
    trim_end = min(len(clip) / SR, local_peak + post)
    clip = clip[int(trim_start * SR):int(trim_end * SR)].copy()
    clip = fade_edges(clip, 0.012 if pre < 0.1 else 0.035, 0.16 if post > 0.5 else 0.07)
    report["processed_excerpt"] = {
        "source_start": round(start + trim_start, 4), "source_end": round(start + trim_end, 4),
        "duration": round(len(clip) / SR, 4), "local_peak_seconds": round(peak_time(clip), 4),
        "edge_fades": True, "generated_audio": False,
    }
    return clip, report


def high_low_pass(clip: np.ndarray, highpass: float | None = None, lowpass: float | None = None) -> np.ndarray:
    out = clip
    if highpass:
        out = signal.sosfilt(signal.butter(2, highpass, btype="highpass", fs=SR, output="sos"), out, axis=0)
    if lowpass:
        out = signal.sosfilt(signal.butter(2, lowpass, btype="lowpass", fs=SR, output="sos"), out, axis=0)
    return out.astype(np.float32)


def add_at_peak(bus: np.ndarray, clip: np.ndarray, at: float, peak_dbfs: float) -> dict:
    clip = normalize_peak(clip, peak_dbfs)
    local_peak = peak_time(clip)
    start = int(round((at - local_peak) * SR))
    source_start = 0
    if start < 0:
        source_start = -start
        start = 0
    count = min(len(clip) - source_start, len(bus) - start)
    if count <= 0:
        raise RuntimeError(f"Cue at {at} does not fit timeline")
    bus[start:start + count] += clip[source_start:source_start + count]
    return {"timeline_peak": round(at, 6), "timeline_start": round(start / SR, 6),
            "source_peak_seconds": round(local_peak, 6), "target_peak_dbfs": peak_dbfs,
            "timeline_end": round((start + count) / SR, 6)}


def asymmetric_duck(voice: np.ndarray) -> np.ndarray:
    env = np.max(np.abs(voice), axis=1)
    win = int(round(0.050 * SR))
    env = ndimage.uniform_filter1d(env, size=win, mode="nearest")
    # Begin opening space just before the phrase and recover slowly after it. A pair
    # of bounded shifts gives pre-roll without an expensive 5,760-sample maximum filter.
    early = int(round(0.060 * SR))
    look_1 = np.roll(env, -early)
    look_2 = np.roll(env, -early * 2)
    look_1[-early:] = 0.0
    look_2[-early * 2:] = 0.0
    env = np.maximum.reduce([env, look_1, look_2])
    target = np.clip(1.0 - env * 7.0, 0.24, 1.0).astype(np.float32)
    out = np.empty_like(target)
    value = 1.0
    attack = 1.0 - math.exp(-1.0 / (0.012 * SR))
    release = 1.0 - math.exp(-1.0 / (0.260 * SR))
    for i, desired in enumerate(target):
        coefficient = attack if desired < value else release
        value += coefficient * (float(desired) - value)
        out[i] = value
    return out


def build_voice() -> tuple[np.ndarray, list[dict]]:
    asyncio.run(preview.synthesize())
    voice = np.zeros((SAMPLES, 2), dtype=np.float32)
    report = []
    for narration in preview.SPEC["narration"]:
        path = preview.WORK / f"{narration['id']}.mp3"
        clip = preview.decode_vo(path)
        allowed = float(narration["latest_end"]) - float(narration["start"]) - 0.06
        duration = len(clip) / SR
        tempo = max(1.0, duration / allowed)
        if tempo > 1.001:
            if tempo > 1.12:
                raise RuntimeError(f"{narration['id']} needs excessive tempo {tempo:.3f}")
            clip = preview.decode_vo(path, tempo)
            duration = len(clip) / SR
        if duration > allowed + 0.08:
            raise RuntimeError(f"{narration['id']} overruns its approved slot")
        clip = high_low_pass(clip, highpass=75)
        clip = fade_edges(clip, 0.018, 0.018)
        start = int(round(float(narration["start"]) * SR))
        count = min(len(clip), len(voice) - start)
        voice[start:start + count] += clip[:count] * 0.96
        report.append({"id": narration["id"], "start": narration["start"],
                       "duration": round(duration, 3), "tempo": round(tempo, 4),
                       "voice": preview.SPEC["voice"]["name"], "text_unchanged": True})
    save_json(REVIEW / "narration_timing.json", report)
    return voice, report


def make_stems(paths: dict[str, Path], music: dict, api: object,
               use_earshot: bool) -> tuple[dict[str, np.ndarray], dict]:
    voice, voice_report = build_voice()
    t = np.arange(SAMPLES, dtype=np.float64) / SR

    music_clip = decode(paths[music["asset"]["id"]], start=float(music["start"]), duration=DURATION,
                        af="highpass=f=45,lowpass=f=12000")
    if len(music_clip) < SAMPLES:
        music_clip = np.pad(music_clip, ((0, SAMPLES - len(music_clip)), (0, 0)))
    music_clip = music_clip[:SAMPLES]
    music_clip = fade_edges(music_clip, 0.80, 1.15)
    music_clip, music_levels = normalize_loudness(music_clip, -25.0)
    section = np.interp(t, [0.0, 5.7, 11.7, 17.1, 23.2, 28.6, 30.0],
                        [0.74, 0.74, 0.88, 1.0, 0.76, 0.62, 0.40]).astype(np.float32)
    # Linear interpolation already provides slow ramps; avoid a very wide per-sample
    # Gaussian kernel on the 1.44-million-sample timeline.

    ambience_start = 18.0
    ambience = decode(paths["forest_night"], start=ambience_start, duration=DURATION,
                      af="highpass=f=85,lowpass=f=6500")
    ambience = ambience[:SAMPLES]
    if len(ambience) < SAMPLES:
        ambience = np.pad(ambience, ((0, SAMPLES - len(ambience)), (0, 0)))
    ambience = fade_edges(ambience, 0.90, 0.90)
    ambience, ambience_levels = normalize_loudness(ambience, -42.0)

    whoosh, whoosh_report = choose_sfx_excerpt(
        paths["soft_whoosh"], "a single soft airy whoosh for a documentary title transition",
        0.48, 0.90, api, use_earshot,
    )
    whoosh = high_low_pass(whoosh, highpass=90, lowpass=6500)
    impact, impact_report = choose_sfx_excerpt(
        paths["soft_impact"], "a single soft deep cinematic impact with a smooth decay",
        0.10, 1.65, api, use_earshot,
    )
    impact = high_low_pass(impact, highpass=38, lowpass=7500)

    # Model ticks are short, high-passed excerpts of the same licensed impact take.
    # Reusing one material gives the diagram a consistent sonic identity without a new boom.
    ip = int(round(peak_time(impact) * SR))
    tick = impact[max(0, ip - int(0.025 * SR)):min(len(impact), ip + int(0.24 * SR))].copy()
    tick = high_low_pass(tick, highpass=240, lowpass=3600)
    tick = fade_edges(tick, 0.005, 0.070)

    sfx = np.zeros_like(voice)
    resolved = {"fps": FPS, "events": [], "intentionally_silent": CUES["intentionally_silent"]}
    for cue in CUES["events"]:
        kind = cue["kind"]
        clip = whoosh if kind == "soft_whoosh" else tick if kind == "model_tick" else impact
        placement = add_at_peak(sfx, clip, float(cue["t"]), float(cue["peak_dbfs"]))
        source_id = "soft_whoosh" if kind == "soft_whoosh" else "soft_impact"
        resolved["events"].append({**cue, "source_asset": source_id, "placement": placement,
                                   "supported_by_picture": True, "generated_audio": False})
    save_json(REVIEW / "resolved_cues.json", resolved)

    duck = asymmetric_duck(voice)
    music_ducked = music_clip * (section * duck)[:, None]
    ambience_ducked = ambience * (0.72 + 0.28 * duck)[:, None]
    sfx_ducked = sfx * (0.55 + 0.45 * duck)[:, None]
    mix = voice + music_ducked + ambience_ducked + sfx_ducked
    mix[:int(0.08 * SR)] *= np.linspace(0, 1, int(0.08 * SR))[:, None]
    mix[-int(0.60 * SR):] *= np.cos(np.linspace(0, np.pi / 2, int(0.60 * SR)))[:, None]
    mix = np.nan_to_num(mix).astype(np.float32)
    report = {
        "old_procedural_background_reused": False,
        "narration": voice_report,
        "music": {**music_levels, "source": music["asset"]["id"], "source_start": music["start"],
                  "section_automation": "slow scene arc; sidechain range down to -12.4 dB"},
        "ambience": {**ambience_levels, "source": "forest_night", "source_start": ambience_start,
                     "note": "Real licensed sound-design ambience, not represented as original NPS camera audio."},
        "whoosh_trim": whoosh_report, "impact_trim": impact_report,
        "model_tick": {"source": "soft_impact", "duration": round(len(tick) / SR, 4),
                       "processing": "240 Hz high-pass, 3.6 kHz low-pass, edge fades"},
        "ducking": {"voice_envelope_ms": 50, "pre_roll_ms": 120, "attack_ms": 12, "release_ms": 260,
                    "music_min_gain": 0.24, "ambience_min_gain": 0.7872, "sfx_min_gain": 0.658},
        "premaster_sample_peak_dbfs": round(20 * math.log10(max(float(np.max(np.abs(mix))), 1e-12)), 3),
    }
    return {"voice": voice, "music": music_ducked, "ambience": ambience_ducked,
            "sfx": sfx_ducked, "mix": mix}, report


def write_stems(stems: dict[str, np.ndarray]) -> None:
    stem_dir = REVIEW / "stems_premaster"
    stem_dir.mkdir(parents=True, exist_ok=True)
    for name, clip in stems.items():
        sf.write(stem_dir / f"{name}.wav", clip, SR, subtype="PCM_24")
    sf.write(WORK / "mix_raw.wav", stems["mix"], SR, subtype="PCM_24")


def master_audio() -> tuple[Path, Path, dict]:
    raw = WORK / "mix_raw.wav"
    first = run([
        "ffmpeg", "-hide_banner", "-i", str(raw),
        "-af", "loudnorm=I=-14:TP=-1.8:LRA=9:print_format=json", "-f", "null", "-",
    ], capture_output=True, check=True, text=True)
    match = re.search(r'\{\s*"input_i"[\s\S]*?\}', first.stderr)
    stats = json.loads(match.group(0)) if match else {}
    if stats:
        af = (
            "loudnorm=I=-14:TP=-1.8:LRA=9:"
            f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
            f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
            f"offset={stats['target_offset']}:linear=true,aresample={SR},alimiter=limit=0.79:level=false"
        )
    else:
        af = f"loudnorm=I=-14:TP=-1.8:LRA=9,aresample={SR},alimiter=limit=0.79:level=false"
    soundtrack = REVIEW / "MONARCH_CAM_Sound_V2_soundtrack.wav"
    master_m4a = WORK / "audio_master.m4a"
    ffmpeg("-i", str(raw), "-af", af, "-t", "30.000", "-ar", str(SR), "-ac", "2",
           "-c:a", "pcm_s24le", str(soundtrack))
    ffmpeg("-i", str(soundtrack), "-t", "30.000", "-c:a", "aac", "-b:a", "192k",
           "-ar", str(SR), "-ac", "2", str(master_m4a))
    save_json(REVIEW / "master_first_pass.json", stats)
    return soundtrack, master_m4a, stats


def mux(soundtrack: Path) -> None:
    if not V1.exists():
        raise FileNotFoundError(f"Approved picture missing: {V1}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg("-i", str(V1), "-i", str(soundtrack), "-map", "0:v:0", "-map", "1:a:0",
           "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2",
           "-t", "30.000", "-movflags", "+faststart", str(OUT))


def loudness(path: Path) -> dict:
    proc = run([
        "ffmpeg", "-hide_banner", "-i", str(path), "-map", "0:a:0",
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-",
    ], capture_output=True, check=True, text=True)
    match = re.search(r'\{\s*"input_i"[\s\S]*?\}', proc.stderr)
    if not match:
        raise RuntimeError("Could not parse final loudness")
    return json.loads(match.group(0))


def video_stream_hash(path: Path) -> str:
    proc = run([
        "ffmpeg", "-hide_banner", "-loglevel", "warning", "-i", str(path),
        "-map", "0:v:0", "-c", "copy", "-f", "streamhash", "-hash", "sha256", "-",
    ], capture_output=True, check=True, text=True)
    return proc.stdout.strip().split("=")[-1]


def technical_qc() -> dict:
    probe_proc = run([
        "ffprobe", "-v", "error", "-count_frames", "-show_entries",
        "format=duration,size:stream=index,codec_name,codec_type,width,height,r_frame_rate,nb_read_frames,sample_rate,channels",
        "-of", "json", str(OUT),
    ], capture_output=True, check=True, text=True)
    probe = json.loads(probe_proc.stdout)
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    audio = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    decoded = decode(OUT)
    sample_peak = float(np.max(np.abs(decoded)))
    clipped = int(np.sum(np.abs(decoded) >= 0.999))
    jumps = np.abs(np.diff(decoded, axis=0))
    extreme_jumps = int(np.sum(jumps > 0.90))
    loud = loudness(OUT)
    v1_hash = video_stream_hash(V1)
    v2_hash = video_stream_hash(OUT)
    duration = float(probe["format"]["duration"])
    integrated = float(loud["input_i"])
    true_peak = float(loud["input_tp"])
    gates = {
        "duration_30_seconds": abs(duration - 30.0) < 0.05,
        "900_frames": int(video["nb_read_frames"]) == 900,
        "1920x1080_30fps": video["width"] == 1920 and video["height"] == 1080 and video["r_frame_rate"] == "30/1",
        "stereo_48khz": int(audio["sample_rate"]) == SR and int(audio["channels"]) == 2,
        "picture_stream_identical": v1_hash == v2_hash,
        "loudness_minus_14_plusminus_0_75": abs(integrated + 14.0) <= 0.75,
        "aac_true_peak_at_or_below_minus_1": true_peak <= -1.0,
        "no_clipped_samples": clipped == 0,
        "no_extreme_sample_discontinuities": extreme_jumps == 0,
    }
    result = {
        "deliverable": str(OUT.relative_to(REPO)), "bytes": OUT.stat().st_size, "sha256": sha256(OUT),
        "probe": probe, "final_aac_loudness": loud,
        "sample_peak_dbfs": round(20 * math.log10(max(sample_peak, 1e-12)), 4),
        "clipped_samples": clipped, "extreme_sample_jumps": extreme_jumps,
        "v1_video_stream_sha256": v1_hash, "v2_video_stream_sha256": v2_hash,
        "old_audio_decoded_or_reused": False, "gates": gates,
        "pass": all(gates.values()),
        "subjective_note": "Measured gates cannot guarantee every listener's preference; human listening remains the final creative review.",
    }
    save_json(REVIEW / "technical_qc.json", result)
    if not result["pass"]:
        raise RuntimeError("Technical QC failed: " + ", ".join(k for k, v in gates.items() if not v))
    return result


def final_earshot_review(api: object, soundtrack: Path) -> None:
    if api is None:
        save_json(REVIEW / "earshot_final_status.json", {
            "status": "not_run", "reason": "Earshot was unavailable during selection; see music_selection.json."
        })
        return
    status = {}
    cue_path = REVIEW / "resolved_cues.json"
    try:
        timeline = api.timeline(str(soundtrack), video=str(OUT), cues=str(cue_path))
        save_json(REVIEW / "earshot_timeline.json", timeline)
        (REVIEW / "earshot_timeline.txt").write_text(timeline.get("summary", json.dumps(timeline, default=json_default)),
                                                    encoding="utf-8")
        status["timeline"] = "complete"
    except Exception as exc:
        status["timeline"] = f"{type(exc).__name__}: {exc}"
    try:
        api.sheet(str(soundtrack), str(REVIEW / "earshot_sheet.png"), video=str(OUT), cues=str(cue_path))
        status["sheet"] = "complete"
    except Exception as exc:
        status["sheet"] = f"{type(exc).__name__}: {exc}"
    try:
        critique = api.critique(str(soundtrack), video=str(OUT))
        save_json(REVIEW / "earshot_critique.json", critique)
        status["critique"] = "complete"
    except Exception as exc:
        status["critique"] = f"{type(exc).__name__}: {exc}"
    save_json(REVIEW / "earshot_final_status.json", status)


def write_credits(music: dict, mix_report: dict) -> None:
    used = [music["asset"]] + [a for a in MANIFEST["assets"] if a["id"] in {"forest_night", "soft_whoosh", "soft_impact"}]
    lines = [
        "# MONARCH CAM — Bear Opening Sound V2 Credits", "",
        "All third-party audio below is marked **CC0 1.0** on its original Freesound source page.",
        "Each page explicitly permits copying, modification, distribution and commercial performance without permission outreach.",
        "The recordings were trimmed, faded, equalised, level-automated and mixed for this 30-second edit.", "",
    ]
    for asset in used:
        lines += [
            f"## {asset['role']}: {asset['title']}", "",
            f"- Creator: **{asset['creator']}**",
            f"- Source: {asset['source_page']}",
            f"- Openverse record: {asset['openverse_record']}",
            f"- Licence: **CC0 1.0** — {asset['license_url']}",
        ]
        if asset["id"] == music["asset"]["id"]:
            lines.append(f"- Use in this edit: 30.000-second excerpt beginning at {float(music['start']):.3f} seconds; level automation, EQ and fades.")
        elif asset["id"] == "forest_night":
            lines.append("- Use in this edit: 30.000-second ambience excerpt beginning at 18.000 seconds; quiet background level, EQ and fades.")
            lines.append("- This is licensed sound-design ambience, not original NPS location/camera audio.")
        elif asset["id"] == "soft_whoosh":
            rng = mix_report["whoosh_trim"]["processed_excerpt"]
            lines.append(f"- Use in this edit: excerpt {rng['source_start']:.3f}–{rng['source_end']:.3f} seconds; question/answer graphic transitions.")
        elif asset["id"] == "soft_impact":
            rng = mix_report["impact_trim"]["processed_excerpt"]
            lines.append(f"- Use in this edit: excerpt {rng['source_start']:.3f}–{rng['source_end']:.3f} seconds; opening/question/model graphic accents.")
        lines.append("")
    lines += [
        "## Other production elements", "",
        "- Picture: approved National Park Service public-domain footage plus the existing project typography and diagrams; the V1 video stream is copied unchanged.",
        "- Narration: the approved project script, freshly synthesized with Edge TTS `en-US-AndrewNeural`; no old background track is reused.",
        "- No handle pull, door movement, bear roar or other unsupported event sound was added.", "",
        "Licence records support the selected use, but no source can guarantee a platform's automated Content ID outcome.",
    ]
    (ROOT / "CREDITS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    desc = ["Audio sources (CC0 1.0; edited for this video):"]
    for asset in used:
        credit = asset.get("source_credit_request") or f"{asset['title']} — {asset['creator']}"
        desc.append(f"{credit}\n{asset['source_page']}\nLicence: {asset['license_url']}")
    desc.append("Forest ambience is licensed sound-design ambience, not original NPS camera audio. Picture: National Park Service public-domain footage; project narration, typography and edit.")
    (REVIEW / "YOUTUBE_DESCRIPTION_CREDITS.txt").write_text("\n\n".join(desc) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-earshot", action="store_true", help="Use deterministic source trims; final model review is skipped")
    args = parser.parse_args()
    for directory in (WORK, REVIEW, OUT.parent):
        directory.mkdir(parents=True, exist_ok=True)
    use_earshot = not args.skip_earshot
    paths = download_assets()
    music, _, api = select_music(paths, use_earshot)
    stems, mix_report = make_stems(paths, music, api, use_earshot)
    write_stems(stems)
    save_json(REVIEW / "mix_report.json", mix_report)
    soundtrack, _, _ = master_audio()
    mux(soundtrack)
    technical = technical_qc()
    write_credits(music, mix_report)
    final_earshot_review(api if use_earshot else None, soundtrack)
    print(json.dumps({
        "output": str(OUT), "bytes": OUT.stat().st_size, "technical_pass": technical["pass"],
        "music": music["asset"]["title"], "music_start": music["start"],
    }, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
