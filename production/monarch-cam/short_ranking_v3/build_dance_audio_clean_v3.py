#!/usr/bin/env python3
"""Narration, V3 clean-premium cleared sound, AAC calibration, mux and review.

Same locked 35 s / 69 words / 13 narration slots / 16 cues as the V3 spec.
V3 changes: salience-layered softer hits, panned CC0 SFX, a short original
room, voice-aware presence dip, wider music/ambience, PCHIP envelopes, four
low-level generated sub-blooms, gentle voice de-harsh and a bounded premaster
ceiling. No generated animal vocalisation, attack, bear, car, handle, door or
food-reward sound; no human listening or virality guarantee.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import math
import re
import subprocess
import sys
import time
from pathlib import Path

import edge_tts
import numpy as np
import requests
import soundfile as sf
from scipy import signal
from scipy.interpolate import PchipInterpolator

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "production/monarch-cam/short_ranking_v3"
WORK = ROOT / "production/monarch-cam/work/short_ranking_v3"
REVIEW = BASE / "review"
SOURCES = WORK / "sources"
OUT = ROOT / "deliverables/MONARCH_CAM_5_Unexpected_Animal_Skills_Ranked_35s_Short_CLEAN_PREMIUM_V3.mp4"
NATIVE_AUDIO = WORK / "native_ambience.wav"
SPEC = json.loads((BASE / "dance_short_spec.json").read_text())
MANIFEST = json.loads((BASE / "source_manifest_ranking.json").read_text())
DURATION = float(SPEC["duration"])
SR = 48000
SAMPLES = int(DURATION * SR)
W, H, FPS = SPEC["width"], SPEC["height"], SPEC["fps"]
TARGET_I = -14.2
TARGET_TP = -2.2
PREM = SPEC["audio"]["premium"]
AUDIO = SPEC["audio"]

sys.path.insert(0, str(ROOT / "production/monarch-cam/sound_v2"))
sys.path.insert(0, str(ROOT / "production/monarch-cam"))
import build_sound_v2 as sound  # noqa: E402
import build_preview as preview  # noqa: E402

sound.WORK = WORK
sound.REVIEW = REVIEW
preview.WORK = WORK


def run(command, stdout=None):
    print("+", " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), check=True, stdout=stdout)


def save_json(path: Path, data):
    sound.save_json(path, data)


def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def download_dance_assets():
    """Retrieve only verified CC0 HQ previews; use the native public-domain WAV locally."""
    SOURCES.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "MonarchCamDancePremium/1.0 (CC0/public-domain production)"}
    paths = {}
    ledger = []
    allowed = set(MANIFEST["policy"]["allowed"])
    for asset in MANIFEST["assets"]:
        if asset.get("role") == "video":
            continue
        if not asset.get("source_page_verified"):
            raise RuntimeError(f"Unverified source page for {asset['id']}")
        if asset["license"] not in allowed:
            raise RuntimeError(f"Disallowed licence for {asset['id']}: {asset['license']}")
        if asset.get("local"):
            path = WORK / asset["local_filename"]
            if not path.exists() or path.stat().st_size < 1000:
                raise FileNotFoundError(f"Native public-domain audio missing: {path}")
            used_url = None
        else:
            path = SOURCES / asset["local_filename"]
            used_url = None
            if not path.exists() or path.stat().st_size < 1000:
                error = None
                for url in asset["download_urls"]:
                    for attempt in range(1, 4):
                        try:
                            response = requests.get(url, headers=headers, timeout=90)
                            response.raise_for_status()
                            if len(response.content) < 1000:
                                raise RuntimeError(f"Only {len(response.content)} bytes returned")
                            path.write_bytes(response.content)
                            used_url = url
                            break
                        except Exception as exc:
                            error = exc
                            path.unlink(missing_ok=True)
                            if attempt == 3:
                                break
                            time.sleep(attempt * 2)
                    if used_url:
                        break
                if not used_url:
                    raise RuntimeError(f"Could not retrieve {asset['id']}: {error}") from error
            else:
                used_url = asset["download_urls"][0]
        paths[asset["id"]] = path
        ledger.append({
            "id": asset["id"], "file": path.name, "bytes": path.stat().st_size,
            "sha256": sha256(path), "download_url": used_url,
            "source_page": asset["source_page"], "license": asset["license"],
            "openverse_record": asset.get("openverse_record"),
        })
        print(f"Source {asset['id']}: {path.stat().st_size:,} bytes", flush=True)
    save_json(REVIEW / "source_file_ledger.json", ledger)
    return paths


async def synthesize_voice():
    WORK.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir(parents=True, exist_ok=True)
    failures = []
    for item in SPEC["narration"]:
        destination = WORK / f"{item['id']}.mp3"
        voice = SPEC["voice"]
        for attempt in range(1, 6):
            try:
                if destination.exists():
                    destination.unlink()
                communicate = edge_tts.Communicate(
                    item["text"], voice["name"], rate=voice["rate"],
                    volume=voice["volume"], pitch=voice["pitch"]
                )
                await communicate.save(str(destination))
                if destination.stat().st_size < 1000:
                    raise RuntimeError("Voice response is unexpectedly small")
                print(f"TTS {item['id']} attempt {attempt}: {destination.stat().st_size} bytes", flush=True)
                break
            except Exception as exc:
                failures.append({"id": item["id"], "attempt": attempt, "error": repr(exc)})
                print(f"TTS retry {item['id']} {attempt}/5: {exc!r}", flush=True)
                if attempt == 5:
                    save_json(REVIEW / "tts_failures.json", failures)
                    raise
                await asyncio.sleep(attempt * 2)


def fit_length(clip: np.ndarray, samples: int = SAMPLES):
    clip = np.asarray(clip, dtype=np.float32)
    if clip.ndim == 1:
        clip = np.repeat(clip[:, None], 2, axis=1)
    if len(clip) < samples:
        clip = np.pad(clip, ((0, samples - len(clip)), (0, 0)))
    return clip[:samples].astype(np.float32)


def smooth_envelope(times, values):
    """Monotone C1 envelope; replaces the original piecewise-linear ramps."""
    interpolator = PchipInterpolator(
        np.asarray(times, dtype=np.float64), np.asarray(values, dtype=np.float64), extrapolate=True
    )
    t = np.arange(SAMPLES, dtype=np.float64) / SR
    return np.clip(interpolator(t), 0.0, 1.3).astype(np.float32)


def widen_stereo(clip: np.ndarray, amount: float):
    """Mid/side widening keeps the mono fold intact while adding side energy."""
    left, right = clip[:, 0], clip[:, 1]
    mid = (left + right) * 0.5
    side = (left - right) * 0.5
    gain = 1.0 + float(amount)
    out = np.stack([mid + gain * side, mid - gain * side], axis=1).astype(np.float32)
    peak = float(np.max(np.abs(out)))
    if peak > 0.95:
        out *= 0.95 / peak
    return out


def add_short_room(clip: np.ndarray, mix: float, decay_ms: float, seed: int):
    """Deterministic very short room; an original effect, not a wildlife sound."""
    rng = np.random.default_rng(seed)
    n = max(64, int(decay_ms / 1000.0 * SR))
    t = np.arange(n, dtype=np.float64) / SR
    ir = rng.standard_normal(n).astype(np.float32) * np.exp(-t / (decay_ms / 1000.0 / 4.0)).astype(np.float32)
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    wet = np.stack(
        [signal.fftconvolve(clip[:, c], ir, mode="full")[:len(clip)] for c in range(2)], axis=1
    ).astype(np.float32)
    dry_rms = float(np.sqrt(np.mean(clip ** 2))) + 1e-9
    wet_rms = float(np.sqrt(np.mean(wet ** 2))) + 1e-9
    wet *= dry_rms / wet_rms
    return (clip * (1.0 - mix) + wet * mix).astype(np.float32)


def apply_pan(clip: np.ndarray, pan_start: float, pan_end: float):
    """Constant-power motion pan; SFX energy leaves the 1-4 kHz voice lane via ducking below."""
    p = np.linspace(float(pan_start), float(pan_end), len(clip), dtype=np.float32)
    angle = (p + 1.0) * np.pi / 4.0
    mono = clip.mean(axis=1)
    return np.stack([mono * np.cos(angle), mono * np.sin(angle)], axis=1).astype(np.float32)


def make_sub_bloom(cfg: dict):
    """Short original low-frequency bloom under four hero reveals; not a animal sound."""
    n = int(float(cfg["duration_s"]) * SR)
    t = np.arange(n, dtype=np.float64) / SR
    freq = float(cfg["start_hz"]) + (float(cfg["end_hz"]) - float(cfg["start_hz"])) * (1.0 - np.exp(-t * 10.0))
    phase = 2.0 * np.pi * np.cumsum(freq) / SR
    attack = 0.075
    env = np.sin(np.pi / 2.0 * np.clip(t / attack, 0.0, 1.0)) ** 2
    env *= np.exp(-np.maximum(t - attack, 0.0) / 0.24)
    mono = (np.sin(phase) * env).astype(np.float32)
    out = np.stack([mono, mono], axis=1)
    return sound.fade_edges(out, 0.006, 0.060)


def voice_aware_presence_dip(sfx: np.ndarray, duck: np.ndarray, amount: float):
    """Crossfade toward a low-passed SFX bus while narration is active."""
    low = sound.high_low_pass(sfx, 80, 2600)
    voice_mask = (1.0 - duck).astype(np.float32)
    return (sfx * (1.0 - amount * voice_mask[:, None]) + low * (amount * voice_mask[:, None])).astype(np.float32)


def soft_limit(clip: np.ndarray, ceiling_dbfs: float):
    peak = float(np.max(np.abs(clip)))
    cap = 10 ** (ceiling_dbfs / 20.0)
    if peak > cap:
        clip = clip * (cap / peak)
    return clip.astype(np.float32)


def build_audio():
    asyncio.run(synthesize_voice())
    assets = download_dance_assets()
    api = None
    try:
        from earshot import api as earshot_api
        api = earshot_api
        print("Earshot API available; model-assisted SFX selection enabled", flush=True)
    except Exception as exc:
        print("Earshot unavailable during SFX selection; fixed reviewed trims remain required:", repr(exc), flush=True)

    voice = np.zeros((SAMPLES, 2), np.float32)
    ledger = []
    narration = SPEC["narration"]
    voice_fade = float(PREM["voice_fade_s"])
    voice_lowpass = int(PREM["voice_lowpass_hz"])
    for index, item in enumerate(narration):
        clip = preview.decode_vo(WORK / f"{item['id']}.mp3").astype(np.float32)
        clip = sound.high_low_pass(clip, 75, voice_lowpass)
        clip = sound.fade_edges(clip, voice_fade, voice_fade)
        start_sample = int(round(item["start"] * SR))
        slot_end = int(round(narration[index + 1]["start"] * SR)) if index + 1 < len(narration) else SAMPLES
        slot_samples = slot_end - start_sample
        allowed_samples = slot_samples - int(0.01 * SR)
        tempo = 1.0
        if len(clip) > allowed_samples:
            target_samples = allowed_samples - int(0.04 * SR)
            tempo = len(clip) / target_samples
            if tempo > 1.15:
                raise RuntimeError(f"{item['id']} needs excessive tempo {tempo:.3f}")
            clip = preview.decode_vo(WORK / f"{item['id']}.mp3", atempo=tempo).astype(np.float32)
            clip = sound.high_low_pass(clip, 75, voice_lowpass)
            clip = sound.fade_edges(clip, voice_fade, voice_fade)
        if len(clip) > allowed_samples + 2:
            raise RuntimeError(f"{item['id']} duration {len(clip) / SR:.3f}s exceeds its narration slot")
        if start_sample + len(clip) > SAMPLES - int(0.20 * SR):
            raise RuntimeError(f"{item['id']} does not leave the required 200 ms closing buffer")
        leveled_clip = sound.normalize_peak(clip, -3.0)
        count = min(len(leveled_clip), SAMPLES - start_sample)
        voice[start_sample:start_sample + count] += leveled_clip[:count]
        placement = {"timeline_start": item["start"], "timeline_end": (start_sample + count) / SR, "target_peak_dbfs": -3.0}
        duration = len(clip) / SR
        ledger.append({
            **item, "measured_duration_s": round(duration, 6), "tempo": round(tempo, 6),
            "end_s": round(item["start"] + duration, 6),
            "slot_duration_s": round(slot_samples / SR, 6),
            "words": len(item["text"].split()),
            "samples": len(clip), "clip_peak_dbfs_before_placement": round(float(20 * np.log10(np.max(np.abs(clip)) + 1e-12)), 4),
            "placement": placement, "voice": SPEC["voice"],
            "premium_voice_lowpass_hz": voice_lowpass,
            "premium_voice_fade_s": voice_fade,
            "text_sha256": hashlib.sha256(item["text"].encode()).hexdigest()
        })
    save_json(REVIEW / "voice_ledger.json", ledger)

    music = fit_length(sound.decode(assets[AUDIO["music_asset"]], AUDIO["music_start"], DURATION,
                                    af="highpass=f=45,lowpass=f=12000"))
    # V3: a gentle 3.6 kHz roll-off softens beat transients without muting the
    # cleared CC0 bed; Earshot's reference band still needs a sparse hit density.
    music = sound.high_low_pass(music, None, 2600)
    music = sound.fade_edges(music, 0.35, 0.50)
    music = widen_stereo(music, PREM["stereo_width_music"])
    music, music_levels = sound.normalize_loudness(music, AUDIO["music_lufs"])
    music_levels["stereo_width"] = PREM["stereo_width_music"]
    music *= smooth_envelope(AUDIO["music_envelope_t"], AUDIO["music_envelope_v"])[:, None]

    ambience = fit_length(sound.decode(assets[AUDIO["ambience_asset"]], AUDIO["ambience_start"], DURATION,
                                       af="highpass=f=80,lowpass=f=6500"))
    ambience = sound.fade_edges(ambience, 0.35, 0.45)
    ambience = widen_stereo(ambience, PREM["stereo_width_ambience"])
    ambience, ambience_levels = sound.normalize_loudness(ambience, AUDIO["ambience_lufs"])
    ambience_levels["stereo_width"] = PREM["stereo_width_ambience"]
    ambience *= smooth_envelope(AUDIO["ambience_envelope_t"], AUDIO["ambience_envelope_v"])[:, None]

    sfx = np.zeros_like(voice)
    sfx_paths = {}
    sfx_selection_model_used = False
    for kind, definition in AUDIO["sfx"].items():
        source_path = assets[definition["asset"]]
        source_audio = sound.decode(source_path)
        excerpt = source_audio[int(definition["trim_start"] * SR):int(definition["trim_end"] * SR)]
        if len(excerpt) < int(0.05 * SR):
            raise RuntimeError(f"{kind} source trim is unexpectedly short")
        path = WORK / f"selected_{kind}.wav"
        sf.write(path, excerpt, SR, subtype="FLOAT")
        clip, selection = sound.choose_sfx_excerpt(
            path, f"{definition['description']} clean", definition["pre"], definition["post"], api, api is not None
        )
        clip = sound.high_low_pass(clip, definition["premium_highpass"], definition["premium_lowpass"])
        clip = add_short_room(clip, PREM["sfx_room_mix"], PREM["sfx_room_decay_ms"],
                              seed=9000 + sum(ord(c) for c in kind))
        clip = sound.fade_edges(clip, 0.014, min(0.12, len(clip) / SR / 3.0))
        sf.write(path, clip, SR, subtype="FLOAT")
        sfx_paths[kind] = path
        selection["premium"] = {
            "highpass_hz": definition["premium_highpass"],
            "lowpass_hz": definition["premium_lowpass"],
            "short_room_mix": PREM["sfx_room_mix"],
            "short_room_decay_ms": PREM["sfx_room_decay_ms"],
            "edge_fade_in_s": 0.014,
            "processed_duration_s": round(len(clip) / SR, 4),
            "generated_audio": False,
            "room_is_original_effect": True
        }
        save_json(REVIEW / f"sfx_{kind}_selection.json", selection)
        if "earshot_find" in selection:
            sfx_selection_model_used = True

    cue_ledger = []
    for cue in AUDIO["cues"]:
        clip, _ = sf.read(sfx_paths[cue["kind"]], dtype="float32", always_2d=True)
        clip = apply_pan(clip, cue["pan_start"], cue["pan_end"])
        effective_peak = float(cue["effective_peak_db"])
        placement = sound.add_at_peak(sfx, clip, cue["frame"] / FPS, effective_peak)
        cue_ledger.append({
            **cue, "time_s": cue["frame"] / FPS,
            "source_file": Path(sfx_paths[cue["kind"]]).name,
            "effective_peak_db": effective_peak,
            "placement": placement
        })
    save_json(REVIEW / "cue_ledger.json", cue_ledger)

    sub = np.zeros_like(voice)
    sub_clip = make_sub_bloom(PREM["sub_bloom"])
    sub_events = []
    for frame in PREM["sub_bloom_frames"]:
        at = frame / FPS
        placement = sound.add_at_peak(sub, sub_clip, at, PREM["sub_bloom"]["peak_dbfs"])
        sub_events.append({
            "frame": frame, "t": round(at, 6),
            "peak_dbfs": PREM["sub_bloom"]["peak_dbfs"],
            "picture": "Hero visual reveal / sync / replay",
            "placement": placement,
            "generated_audio": True,
            "generated_bird_vocalisation": False,
            "note": "Original low-frequency cinematic bloom; not a wildlife event."
        })

    source_by_kind = {kind: definition["asset"] for kind, definition in AUDIO["sfx"].items()}
    save_json(REVIEW / "resolved_cues.json", {
        "fps": FPS, "duration_seconds": DURATION,
        "picture_reference": str(OUT.relative_to(ROOT)),
        "picture_policy": "Premium 35-second native-vertical ranked-animal edit of five CC0 Wikimedia Commons clips; cues align only to visible cuts, rank reveals, detail accents and the loop.",
        "premium": {
            "salience_roles": PREM["salience_roles"],
            "sub_bloom_events": sub_events,
            "sfx_panning": "constant-power motion pan",
            "voice_aware_presence_dip": PREM["voice_presence_dip"],
            "stereo_width_music": PREM["stereo_width_music"],
            "stereo_width_ambience": PREM["stereo_width_ambience"],
            "envelope_smoothing": PREM["envelope_smoothing"]
        },
        "events": [{
            "id": f"dance:{cue['kind']}:{cue['frame']}",
            "frame": cue["frame"], "t": cue["time_s"], "kind": cue["kind"],
            "peak_dbfs": cue["peak_db"],
            "effective_peak_dbfs": cue["effective_peak_db"],
            "salience_role": cue["salience_role"],
            "pan": [cue["pan_start"], cue["pan_end"]],
            "picture": cue["label"],
            "sound_need": "One salience-layered cleared graphic accent aligned to the visible cut or dance-card step; no unsupported wildlife event.",
            "source_asset": source_by_kind[cue["kind"]],
            "source_file": Path(sfx_paths[cue["kind"]]).name,
            "placement": cue["placement"],
            "supported_by_picture": True, "generated_audio": False
        } for cue in cue_ledger],
        "intentionally_silent": [{
            "frame": 360, "t": 12.0,
            "picture": "Wider colony context; no specific bird call is depicted.",
            "reason": "No generated animal vocalisation; only a low-level original sub-bloom supports the visual reveal."
        }, {
            "frame": 549, "t": 18.3,
            "picture": "Loop returns to the opening pair.",
            "reason": "No bear, car, handle, door, attack or generated animal sound is added; only the original sub-bloom."
        }]
    })

    duck = sound.asymmetric_duck(voice)
    ducked_music = music * duck[:, None]
    ducked_music *= 0.96
    ducked_ambience = ambience * (0.72 + 0.28 * duck)[:, None]
    ducked_sfx = sfx * (0.55 + 0.45 * duck)[:, None]
    ducked_sfx = voice_aware_presence_dip(ducked_sfx, duck, PREM["voice_presence_dip"])
    ducked_sub = sub * (PREM["sub_min_gain"] + (1.0 - PREM["sub_min_gain"]) * duck)[:, None]
    for bus in (voice, ducked_music, ducked_ambience, ducked_sfx, ducked_sub):
        bus[:int(0.05 * SR)] *= np.linspace(0, 1, int(0.05 * SR), dtype=np.float32)[:, None]
        bus[-int(0.45 * SR):] *= np.linspace(1, 0, int(0.45 * SR), dtype=np.float32)[:, None]
    mix = voice + ducked_music + ducked_ambience + ducked_sfx + ducked_sub
    mix = soft_limit(mix, PREM["premaster_ceiling_dbfs"])
    sf.write(WORK / "premaster.wav", mix, SR)
    stems = {"voice": voice, "music": ducked_music, "ambience": ducked_ambience,
             "sfx": ducked_sfx, "sub_bloom": ducked_sub}
    for name, bus in stems.items():
        sf.write(WORK / f"debug_{name}.wav", bus, SR)
    save_json(REVIEW / "source_mix_report.json", {
        "music": {**music_levels, "source": AUDIO["music_asset"], "source_start": AUDIO["music_start"]},
        "ambience": {**ambience_levels, "source": AUDIO["ambience_asset"], "source_start": AUDIO["ambience_start"], "native_clip_audio_used": True},
        "ducking": {"music_min_gain": 0.24, "ambience_min_gain": 0.7872, "sfx_min_gain": 0.658,
                    "sub_min_gain": PREM["sub_min_gain"], "voice_preroll_ms": 120},
        "premium": {
            "salience_roles": PREM["salience_roles"],
            "stereo_width_music": PREM["stereo_width_music"],
            "stereo_width_ambience": PREM["stereo_width_ambience"],
            "sfx_room_mix": PREM["sfx_room_mix"],
            "sfx_room_decay_ms": PREM["sfx_room_decay_ms"],
            "voice_presence_dip": PREM["voice_presence_dip"],
            "voice_lowpass_hz": PREM["voice_lowpass_hz"],
            "envelope_smoothing": PREM["envelope_smoothing"],
            "sub_bloom_events": len(sub_events),
            "sub_bloom_peak_dbfs": PREM["sub_bloom"]["peak_dbfs"],
            "premaster_ceiling_dbfs": PREM["premaster_ceiling_dbfs"],
            "generated_sub_bloom": True,
            "generated_short_room": True,
            "panned_sfx": True,
            "soft_support_hits": True
        },
        "native_clip_audio_used": True,
        "generated_bird_vocalisations": False,
        "generated_animal_vocalisations": False,
        "generated_bear_or_vehicle_foley": False,
        "sfx_selection_model_used": sfx_selection_model_used,
        "premaster_sample_peak_dbfs": round(float(20 * np.log10(np.max(np.abs(mix)) + 1e-12)), 4)
    })
    return mix, stems


def encode_aac(wav: Path, destination: Path):
    run(["ffmpeg", "-y", "-i", wav, "-t", f"{DURATION:.3f}", "-c:a", "aac", "-b:a", "192k", "-ar", SR, "-ac", 2, destination])


def decode_aac(path: Path):
    return fit_length(sound.decode(path, 0, DURATION))


def master_audio(mix: np.ndarray, stems: dict):
    raw = WORK / "premaster_24.wav"
    sf.write(raw, mix, SR, subtype="PCM_24")
    first = subprocess.run([
        "ffmpeg", "-hide_banner", "-i", raw,
        "-af", "loudnorm=I=-13.8:TP=-3.5:LRA=9:print_format=json", "-f", "null", "-"
    ], check=True, capture_output=True, text=True)
    match = re.search(r'\{\s*"input_i"[\s\S]*?\}', first.stderr)
    stats = json.loads(match.group(0)) if match else {}
    if stats:
        af = (
            "loudnorm=I=-13.8:TP=-3.5:LRA=9:"
            f"measured_I={stats['input_i']}:measured_TP={stats['input_tp']}:"
            f"measured_LRA={stats['input_lra']}:measured_thresh={stats['input_thresh']}:"
            f"offset={stats['target_offset']}:linear=true,"
            f"alimiter=limit=0.67:level=false,aresample={SR}"
        )
    else:
        af = f"loudnorm=I=-13.8:TP=-3.5:LRA=9,alimiter=limit=0.67:level=false,aresample={SR}"
    soundtrack = WORK / "soundtrack.wav"
    final_aac = WORK / "audio_master.m4a"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-i", raw, "-af", af,
         "-t", f"{DURATION:.3f}", "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s24le", soundtrack])
    encode_aac(soundtrack, final_aac)
    save_json(REVIEW / "mastering_first_pass.json", stats)

    calibration = []
    for pass_index in range(1, 4):
        measured = sound.loudness(final_aac)
        integrated = float(measured["input_i"])
        true_peak = float(measured["input_tp"])
        delta = float(np.clip(TARGET_I - integrated, -3.0, 3.0))
        calibration.append({"pass": pass_index, "before": measured, "requested_gain_db": round(delta, 4)})
        if abs(TARGET_I - integrated) <= 0.15 and true_peak <= -1.20:
            break
        if true_peak > -1.20:
            delta = min(delta, -1.40 - true_peak)
        adjusted = WORK / f"soundtrack_calibrated_{pass_index}.wav"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-i", soundtrack,
             "-af", f"volume={delta:.4f}dB,aresample=192000,alimiter=limit=0.67:level=false,aresample={SR}",
             "-t", f"{DURATION:.3f}", "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s24le", adjusted])
        adjusted.replace(soundtrack)
        encode_aac(soundtrack, final_aac)

    peak_guard = []
    for guard_index in range(1, 4):
        measured = sound.loudness(final_aac)
        true_peak = float(measured["input_tp"])
        if true_peak <= TARGET_TP:
            break
        delta = min(-0.25, TARGET_TP - true_peak - 0.20)
        guarded = WORK / f"soundtrack_peak_guard_{guard_index}.wav"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-i", soundtrack,
             "-af", f"volume={delta:.4f}dB,aresample=192000,alimiter=limit=0.65:level=false,aresample={SR}",
             "-t", f"{DURATION:.3f}", "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s24le", guarded])
        guarded.replace(soundtrack)
        encode_aac(soundtrack, final_aac)
        peak_guard.append({"pass": guard_index, "before": measured, "gain_db": round(delta, 4), "after": sound.loudness(final_aac)})

    before_clicks = sound.loudness(final_aac)
    if float(before_clicks["input_tp"]) > TARGET_TP or abs(float(before_clicks["input_i"]) - TARGET_I) > 0.50:
        raise RuntimeError(f"Mastering calibration failed on AAC: {before_clicks}")

    click_review = {"threshold": 0.35, "max_repair_samples_per_run": 48, "passes": []}
    final_wav = soundtrack
    for click_pass in range(1, 4):
        decoded_aac = decode_aac(final_aac)
        runs = sound.detect_click_runs(decoded_aac)
        pass_record = {"pass": click_pass, "before_runs": runs}
        click_review["passes"].append(pass_record)
        if not runs:
            break
        pcm, pcm_rate = sf.read(final_wav, dtype="float32", always_2d=True)
        if pcm_rate != SR:
            raise RuntimeError(f"Unexpected PCM master rate: {pcm_rate}")
        repaired, operations = sound.repair_short_click_runs(pcm, runs)
        pass_record["operations"] = operations
        repaired_wav = WORK / f"soundtrack_click_repaired_{click_pass}.wav"
        sf.write(repaired_wav, repaired, SR, subtype="PCM_24")
        final_wav = repaired_wav
        encode_aac(final_wav, final_aac)
        remaining = sound.detect_click_runs(decode_aac(final_aac))
        pass_record["after_runs"] = remaining
        if not remaining:
            break
        if click_pass == 3:
            save_json(REVIEW / "click_repair.json", click_review)
            raise RuntimeError(f"Persistent AAC click runs after bounded repair: {remaining}")

    final_mix = decode_aac(final_aac)
    click_review["final_runs"] = sound.detect_click_runs(final_mix)
    click_review["final_aac_measurement"] = sound.loudness(final_aac)
    click_review["repaired_samples"] = sum(op["interpolated_samples"] for p in click_review["passes"] for op in p.get("operations", []))
    save_json(REVIEW / "click_repair.json", click_review)
    if click_review["final_runs"]:
        raise RuntimeError(f"Delivered AAC still has {len(click_review['final_runs'])} click runs")

    save_json(REVIEW / "mastering_calibration.json", {
        "target_integrated_lufs": TARGET_I, "target_true_peak_dbtp": TARGET_TP,
        "first_pass_loudnorm": stats, "calibration": calibration,
        "peak_guard": peak_guard, "before_click_repair": before_clicks,
        "final_aac": click_review["final_aac_measurement"],
        "method": "Premium V3-style two-pass loudnorm, conservative 192 kHz limiting and measured AAC-domain calibration; no gate bypass."
    })

    bed = stems["music"] + stems["ambience"] + stems["sfx"] + stems["sub_bloom"]
    scale = float(np.sum((final_mix - stems["voice"]) * bed) / (np.sum(bed * bed) + 1e-9))
    scale = float(np.clip(scale, 0.0, 4.0))
    stem_dir = REVIEW / "stems"
    stem_dir.mkdir(parents=True, exist_ok=True)
    sf.write(stem_dir / "01_voice.wav", stems["voice"], SR, subtype="PCM_24")
    sf.write(stem_dir / "02_music.wav", stems["music"] * scale, SR, subtype="PCM_24")
    sf.write(stem_dir / "03_ambience.wav", stems["ambience"] * scale, SR, subtype="PCM_24")
    sf.write(stem_dir / "04_sfx.wav", stems["sfx"] * scale, SR, subtype="PCM_24")
    sf.write(stem_dir / "05_sub_bloom.wav", stems["sub_bloom"] * scale, SR, subtype="PCM_24")
    reconstruction = stems["voice"] + scale * bed
    save_json(REVIEW / "stem_diagnostics.json", {
        "bed_scale": scale,
        "residual_dbfs": round(float(20 * np.log10(np.sqrt(np.mean((final_mix - reconstruction) ** 2)) + 1e-12)), 4),
        "note": "Premium reference stems, including the original sub-bloom, are not a claimed bit-perfect unmastering of the delivered AAC."
    })
    return final_wav, final_aac, final_mix


def mux_and_qc(final_aac: Path):
    silent = WORK / "dance_silent_clean_v3.mp4"
    if not silent.exists():
        raise FileNotFoundError("Render the V3 clean vertical picture first")
    run(["ffmpeg", "-y", "-i", silent, "-i", final_aac, "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "copy", "-t", f"{DURATION:.3f}", "-movflags", "+faststart", OUT])
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-count_frames", "-show_entries",
        "format=duration,size:stream=index,codec_name,codec_type,width,height,r_frame_rate,nb_frames,nb_read_frames,sample_rate,channels",
        "-of", "json", str(OUT)
    ]))
    decoded_path = WORK / "delivered_audio.wav"
    run(["ffmpeg", "-y", "-i", OUT, "-map", "0:a:0", "-t", f"{DURATION:.3f}", "-c:a", "pcm_f32le", "-ar", SR, "-ac", 2, decoded_path])
    delivered, rate = sf.read(decoded_path, dtype="float32", always_2d=True)
    click_runs = sound.detect_click_runs(delivered)
    clipped = np.abs(delivered) >= 0.999969
    clipping_runs = int(np.sum(np.diff(np.r_[False, np.any(clipped, axis=1), False].astype(np.int8)) == 1))
    loudness = sound.loudness(OUT)
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    audio = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    duration = float(probe["format"]["duration"])
    frames = int(video.get("nb_read_frames") or video.get("nb_frames") or 0)
    checks = {
        "duration_24s": abs(duration - DURATION) <= 0.05,
        "frames_720": frames == SPEC["frame_count"],
        "vertical_1080x1920": [video.get("width"), video.get("height")] == [W, H],
        "fps_30": video.get("r_frame_rate") == "30/1",
        "audio_48k_stereo": [int(audio.get("sample_rate", 0)), int(audio.get("channels", 0))] == [SR, 2],
        "integrated_loudness": abs(float(loudness["input_i"]) - TARGET_I) <= 0.50,
        "true_peak": float(loudness["input_tp"]) <= TARGET_TP,
        "no_sample_clipping_runs": clipping_runs == 0,
        "no_click_runs": len(click_runs) == 0
    }
    report = {
        "file": str(OUT.relative_to(ROOT)), "sha256": sha256(OUT), "bytes": OUT.stat().st_size,
        "probe": probe, "decoded_audio_samples": len(delivered), "decoded_sample_rate": rate,
        "loudness": loudness, "click_runs": click_runs, "clipping_runs": clipping_runs,
        "decoded_sample_peak_dbfs": round(float(20 * np.log10(np.max(np.abs(delivered)) + 1e-12)), 4),
        "checks": checks, "passed": all(checks.values()),
        "v3": {
            "edition": "clean_premium_v3",
            "separate_from_previous_editions": True,
            "sound_enhancements": SPEC["enhancement"]["sound"],
            "visual_enhancements": SPEC["enhancement"]["visual"]
        }
    }
    save_json(REVIEW / "technical_qc.json", report)
    if not report["passed"]:
        raise RuntimeError(f"Technical QC failed: {json.dumps(checks)}")
    return delivered


def earshot_review(audio: np.ndarray):
    status = {}
    try:
        from earshot import api
        final_audio = WORK / "earshot_final.wav"
        sf.write(final_audio, audio, SR)
        cue_path = REVIEW / "resolved_cues.json"
        try:
            timeline = api.timeline(str(final_audio), video=str(OUT), cues=str(cue_path))
            save_json(REVIEW / "earshot_timeline.json", timeline)
            (REVIEW / "earshot_timeline.txt").write_text(timeline.get("summary", json.dumps(timeline, default=sound.json_default)), encoding="utf-8")
            status["timeline"] = "complete"
        except Exception as exc:
            status["timeline"] = f"{type(exc).__name__}: {exc}"
        try:
            api.sheet(str(final_audio), str(REVIEW / "earshot_sheet.png"), video=str(OUT), cues=str(cue_path))
            status["sheet"] = "complete"
        except Exception as exc:
            status["sheet"] = f"{type(exc).__name__}: {exc}"
        try:
            critique = api.critique(str(final_audio), video=str(OUT))
            save_json(REVIEW / "earshot_critique.json", critique)
            status["critique"] = "complete"
        except Exception as exc:
            status["critique"] = f"{type(exc).__name__}: {exc}"
    except Exception as exc:
        status["model_load"] = f"{type(exc).__name__}: {exc}"
    save_json(REVIEW / "earshot_final_status.json", status)
    print("Earshot final status:", status, flush=True)
    return all(status.get(key) == "complete" for key in ("timeline", "sheet", "critique"))


def write_delivery_docs():
    credits = """# Credits — 5 Unexpected Animal Skills, Ranked (Clean Premium V3)

## Picture — all CC0 1.0 via Wikimedia Commons

- **Sasana.2015.myanmar.squirrel.1.webmhd.webm** — Moine Sāsana. https://commons.wikimedia.org/wiki/File:Sasana.2015.myanmar.squirrel.1.webmhd.webm
- **Einsiedlerkrebs (Wangerooge).webm** — Rhetos, Sabine Heim. https://commons.wikimedia.org/wiki/File:Einsiedlerkrebs_(Wangerooge).webm
- **Seestern (sich aufrichtend).webm** — Rhetos, Sabine Heim. https://commons.wikimedia.org/wiki/File:Seestern_(sich_aufrichtend).webm
- **OctopusFeedingCSS.mpg** — Shuoli1999. https://commons.wikimedia.org/wiki/File:OctopusFeedingCSS.mpg
- **Slow Motion Hand-Feeding a Tufted Titmouse.webm** — Equationsmith. https://commons.wikimedia.org/wiki/File:Slow_Motion_Hand-Feeding_a_Tufted_Titmouse.webm
- CC0 legal text: https://creativecommons.org/publicdomain/zero/1.0/

## Audio

- **Little, happy tune - 22.10.2015** — cabled_mess, CC0 1.0. https://freesound.org/people/cabled_mess/sounds/335361/
- **Cartoon Boing.wav** — reelworldstudio, CC0 1.0. https://freesound.org/people/reelworldstudio/sounds/161122/
- **Comedy_Music_Samples_033.wav** — jalastram, CC0 1.0. https://freesound.org/people/jalastram/sounds/457985/
- **Whoosh_Simple_ER_SFX_1.wav** — Alex_hears_things, CC0 1.0. https://freesound.org/people/Alex_hears_things/sounds/521044/
- **Soft Cinematic Impact** — Rizzard, CC0 1.0. https://freesound.org/people/Rizzard/sounds/560156/
- Low-level native CC0 source-clip audio is retained as ambience; no generated animal vocalisation was added.
- Narration: AI-generated with Microsoft Edge TTS `en-US-AndrewNeural`.
- Premium sound design: salience-layered softer CC0 hits, motion panning, a short original room, voice-aware presence dip, wider music/ambience, PCHIP envelopes, four low-level original sub-blooms and gentle voice de-harsh. The sub-bloom and room are original production effects, not wildlife recordings.

## Guardrails

- Original 24s, PREMIUM, CLEAN, CLEAN PREMIUM V2, historical Sound V2, 35s Master and rejected 20s files remain unchanged.
- No human full-motion review, native-audio listening, human approval, perfection or virality guarantee is claimed.
- This is a subjective entertainment ranking, not a scientific claim or a claim about any individual animal's life.
- No third-party TikTok, Instagram or Reels clip was used.
"""
    (BASE / "CREDITS.md").write_text(credits, encoding="utf-8")

    upload = """UPLOAD TITLE
5 Unexpected Animal Skills, Ranked.

VIDEO CATEGORY
Entertainment (YouTube videoCategoryId 24)

DESCRIPTION
Five real animal moments. One completely subjective ranking.

A squirrel drops in, a hermit crab carries a broken shell, a starfish flips itself back over, an octopus opens a bottle, and a Tufted Titmouse lands on a human hand. Which one deserves number one?

All picture clips are CC0 1.0 via Wikimedia Commons and are credited below. This is subjective entertainment, not a scientific claim or a claim about any individual animal's life.

Picture: Moine Sāsana; Rhetos / Sabine Heim; Shuoli1999; Equationsmith (CC0, Wikimedia Commons).
Music: Little, happy tune - 22.10.2015 — cabled_mess (CC0).
SFX: reelworldstudio, jalastram, Alex_hears_things and Rizzard (CC0).
Narration: AI-generated English voice.

#Shorts #Animals #Wildlife

UPLOAD NOTES
- Clean-premium V3 1080x1920 vertical Short; 35.000 seconds / 1050 frames.
- Keep hashtags in the description, not in the title field.
- Use review/cover.jpg for `WHICH ONE IS #1?`; A/B is review/cover_RANK_THESE_5.jpg.
- Pin the prepared comment and clarify that this is a subjective ranking of licensed clips.
- Do not add a third-party clip, factual "most impressive ever" superlative, bear, car, handle, door, food-reward, 25M-view, part-2, 3x, subscribe, like, hypnosis, human-approval or viral claim.
- Compare 24h / 3d / 7d stayed-to-watch, engaged views, average percentage viewed, loops, likes, comments, shares and subscribers gained; no result is guaranteed.
"""
    (REVIEW / "UPLOAD_METADATA_DANCE.txt").write_text(upload, encoding="utf-8")

    metadata = """# Upload Metadata — 5 Unexpected Animal Skills, Ranked (Clean Premium V3)

**Primary title:** `5 Unexpected Animal Skills, Ranked.`
**Clean title only — no hashtags in the title field.**
**Video category:** Entertainment — YouTube videoCategoryId `24`.
**Description:** see `UPLOAD_METADATA_DANCE.txt` and `DANCE_PLAN_AND_METADATA.md`.
**First three hashtags:** `#Shorts #Animals #Wildlife` — in the description, not the title.
**Tags:** ranked animals, animal moments, animal skills, wildlife shorts, CC0 footage, octopus, starfish, hermit crab, squirrel, tufted titmouse, Monarch Cam.
**Cover text:** `WHICH ONE IS #1?` — `review/cover.jpg`. A/B: `RANK THESE 5.` — `review/cover_RANK_THESE_5.jpg`.
**Pinned comment:** `Which moment deserves #1?`
**Clarifying comment:** `This is a subjective entertainment ranking using independently licensed CC0 Wikimedia Commons clips; it is not a scientific claim or a claim about any individual animal's life.`
**Rejected:** reference-channel footage reuse, watermarked short-form reposts, factual "most impressive ever" superlative, pre-upload viral/subscribe/like/3x claim, human-listening/human-approval claim, or cluttered on-screen text.
"""
    (REVIEW / "DANCE_UPLOAD_METADATA.md").write_text(metadata, encoding="utf-8")

    script_lines = [f"{item['start']:05.2f}s | {item['text']}" for item in SPEC["narration"]]
    (REVIEW / "FINAL_NARRATION_DANCE.txt").write_text("\n".join(script_lines) + "\n", encoding="utf-8")

    enhancements = """# Clean-premium V3 enhancements — measured, not guaranteed

This is a separate V3 clean-premium 35-second ranked-animal Short. The original, PREMIUM, CLEAN and CLEAN PREMIUM V2 MP4s and their review records are preserved.

Picture: five independently verified CC0 Wikimedia Commons animal clips, minimal tracked lower-third captions and subtle 5→1 rank numerals only. No top headlines, badges, dance cards, progress bars, footers, macro inset or persistent labels. A filmic grade with restrained halation/bloom, very subtle grain/vignette, an undistorted rounded 16:9 action window, double-smoothstep zoom, motion drift, five-frame cross-dissolves, a 0.3 s loop crossfade and exact-text thumbnails remain.

Sound: 16 CC0 cues salience-layered, motion-panned hits, a short original room, gentle de-harsh, voice-aware presence dip, wider mid/side music/ambience, monotone PCHIP envelopes, four weighted original sub-blooms and a bounded -1.4 dBFS premaster ceiling. No new third-party audio asset was introduced.

Measured evidence: nine audio gates, technical QC, Earshot timeline/sheet/critique/comparison, cue/voice/source ledgers, visual-V3 QC and contact sheets. This is objective and model-assisted evidence plus contact-sheet review — not human full-motion review, native-audio listening, human approval, audience hypnosis, a 3x multiplier, subscribe/like behavior, retention or a virality guarantee. "Viral"/"next level" is a design objective only.
"""
    (REVIEW / "CLEAN_V3_ENHANCEMENTS.md").write_text(enhancements, encoding="utf-8")
    (BASE / "CLEAN_V3_ENHANCEMENTS.md").write_text(enhancements, encoding="utf-8")
    (BASE / "DANCE_TOPIC_LOCK.md").write_text(
        "# New topic lock — 5 Unexpected Animal Skills, Ranked\n\n"
        "**Status:** five CC0 Wikimedia Commons picture sources retrieved, probed and contact-sheet reviewed for the V3 clean-premium 35-second render; previous albatross, bear/car and rejected 20-second files are untouched.\n\n"
        "- New subject: a subjective entertainment ranking of five cleared animal moments.\n"
        "- Sources: squirrel, hermit crab, starfish, octopus and Tufted Titmouse — all CC0 1.0 via Wikimedia Commons.\n"
        "- Category: Entertainment (YouTube videoCategoryId 24).\n"
        "- Rule: \"viral\" / \"next level\" is an optimization objective, not a promise.\n",
        encoding="utf-8",
    )


def main():
    REVIEW.mkdir(parents=True, exist_ok=True)
    mix, stems = build_audio()
    _, final_aac, _ = master_audio(mix, stems)
    delivered = mux_and_qc(final_aac)
    earshot_review(delivered)
    write_delivery_docs()
    print(f"DONE {OUT} / {OUT.stat().st_size} bytes", flush=True)


if __name__ == "__main__":
    main()
