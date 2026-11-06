#!/usr/bin/env python3
"""Narration, cleared sound, AAC calibration, mux and review for the NEW 24 s albatross Short."""
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

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "production/monarch-cam/short_dance"
WORK = ROOT / "production/monarch-cam/work/short_dance"
REVIEW = BASE / "review"
SOURCES = WORK / "sources"
OUT = ROOT / "deliverables/MONARCH_CAM_They_Dont_Flirt_They_Choreograph_24s_Short.mp4"
NATIVE_AUDIO = WORK / "usfws_clip_audio.wav"
SPEC = json.loads((BASE / "dance_short_spec.json").read_text())
MANIFEST = json.loads((BASE / "source_manifest_dance.json").read_text())
DURATION = float(SPEC["duration"])
SR = 48000
SAMPLES = int(DURATION * SR)
W, H, FPS = SPEC["width"], SPEC["height"], SPEC["fps"]
TARGET_I = -14.2
TARGET_TP = -2.2

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
    headers = {"User-Agent": "MonarchCamDanceShort/1.0 (CC0/public-domain production)"}
    paths = {}
    ledger = []
    allowed = set(MANIFEST["policy"]["allowed"])
    for asset in MANIFEST["assets"]:
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
    for index, item in enumerate(narration):
        clip = preview.decode_vo(WORK / f"{item['id']}.mp3").astype(np.float32)
        clip = sound.high_low_pass(clip, highpass=75)
        clip = sound.fade_edges(clip, 0.018, 0.018)
        start_sample = int(round(item["start"] * SR))
        slot_end = int(round(narration[index + 1]["start"] * SR)) if index + 1 < len(narration) else SAMPLES
        slot_samples = slot_end - start_sample
        allowed_samples = slot_samples - int(0.01 * SR)
        tempo = 1.0
        if len(clip) > allowed_samples:
            # Aim well below the slot guard: ffmpeg atempo can land slightly long
            # after resampling, so leave a 40 ms fitting margin before checking.
            target_samples = allowed_samples - int(0.04 * SR)
            tempo = len(clip) / target_samples
            if tempo > 1.15:
                raise RuntimeError(f"{item['id']} needs excessive tempo {tempo:.3f}")
            clip = preview.decode_vo(WORK / f"{item['id']}.mp3", atempo=tempo).astype(np.float32)
            clip = sound.fade_edges(sound.high_low_pass(clip, highpass=75), 0.018, 0.018)
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
            "placement": placement,
            "voice": SPEC["voice"], "text_sha256": hashlib.sha256(item["text"].encode()).hexdigest()
        })
    save_json(REVIEW / "voice_ledger.json", ledger)

    audio_spec = SPEC["audio"]
    music = fit_length(sound.decode(assets[audio_spec["music_asset"]], audio_spec["music_start"], DURATION, af="highpass=f=45,lowpass=f=12000"))
    music = sound.fade_edges(music, 0.35, 0.50)
    music, music_levels = sound.normalize_loudness(music, audio_spec["music_lufs"])
    music *= np.interp(np.arange(SAMPLES) / SR, audio_spec["music_envelope_t"], audio_spec["music_envelope_v"]).astype(np.float32)[:, None]

    ambience = fit_length(sound.decode(assets[audio_spec["ambience_asset"]], audio_spec["ambience_start"], DURATION, af="highpass=f=80,lowpass=f=6500"))
    ambience = sound.fade_edges(ambience, 0.35, 0.45)
    ambience, ambience_levels = sound.normalize_loudness(ambience, audio_spec["ambience_lufs"])
    ambience *= np.interp(np.arange(SAMPLES) / SR, audio_spec["ambience_envelope_t"], audio_spec["ambience_envelope_v"]).astype(np.float32)[:, None]

    sfx = np.zeros_like(voice)
    sfx_paths = {}
    sfx_selection_model_used = False
    for kind, definition in audio_spec["sfx"].items():
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
        if kind == "impact":
            clip = sound.high_low_pass(clip, 38, 7500)
        elif kind == "whoosh":
            clip = sound.high_low_pass(clip, 90, 6500)
        elif kind == "boing":
            clip = sound.high_low_pass(clip, 70, 5200)
        else:
            clip = sound.high_low_pass(clip, 240, 3600)
        clip = sound.fade_edges(clip, 0.006 if kind in ("tick", "boing") else 0.012, min(0.08, len(clip) / SR / 4))
        sf.write(path, clip, SR)
        sfx_paths[kind] = path
        save_json(REVIEW / f"sfx_{kind}_selection.json", selection)
        if "earshot_find" in selection:
            sfx_selection_model_used = True

    cue_ledger = []
    for cue in audio_spec["cues"]:
        clip, _ = sf.read(sfx_paths[cue["kind"]], dtype="float32", always_2d=True)
        placement = sound.add_at_peak(sfx, clip, cue["frame"] / SPEC["fps"], cue["peak_db"])
        cue_ledger.append({**cue, "time_s": cue["frame"] / SPEC["fps"], "source_file": Path(sfx_paths[cue["kind"]]).name, "placement": placement})
    save_json(REVIEW / "cue_ledger.json", cue_ledger)
    source_by_kind = {kind: definition["asset"] for kind, definition in audio_spec["sfx"].items()}
    save_json(REVIEW / "resolved_cues.json", {
        "fps": SPEC["fps"], "duration_seconds": DURATION,
        "picture_reference": str(OUT.relative_to(ROOT)),
        "picture_policy": "24-second retention-first native-vertical edit of public-domain USFWS Laysan albatross courtship dance; cues align only to visible cuts, dance-card steps, sync freeze, replay and loop accents.",
        "events": [{
            "id": f"dance:{cue['kind']}:{cue['frame']}",
            "frame": cue["frame"], "t": cue["time_s"], "kind": cue["kind"],
            "peak_dbfs": cue["peak_db"],
            "picture": cue["label"],
            "sound_need": "One restrained cleared graphic accent aligned to the visible cut or dance-card step; no unsupported wildlife event.",
            "source_asset": source_by_kind[cue["kind"]],
            "source_file": Path(sfx_paths[cue["kind"]]).name,
            "placement": cue["placement"],
            "supported_by_picture": True, "generated_audio": False
        } for cue in cue_ledger],
        "intentionally_silent": [{
            "frame": 360, "t": 12.0,
            "picture": "Wider colony context; no specific bird call is depicted.",
            "reason": "No generated bird vocalisation or invented event is added."
        }, {
            "frame": 549, "t": 18.3,
            "picture": "Loop returns to the opening pair.",
            "reason": "No bear, car, handle, door or attack sound is added."
        }]
    })

    duck = sound.asymmetric_duck(voice)
    ducked_music = music * duck[:, None]
    ducked_ambience = ambience * (0.72 + 0.28 * duck)[:, None]
    ducked_sfx = sfx * (0.55 + 0.45 * duck)[:, None]
    sfx = ducked_sfx
    for bus in (voice, ducked_music, ducked_ambience, sfx):
        bus[:int(0.05 * SR)] *= np.linspace(0, 1, int(0.05 * SR), dtype=np.float32)[:, None]
        bus[-int(0.45 * SR):] *= np.linspace(1, 0, int(0.45 * SR), dtype=np.float32)[:, None]
    mix = voice + ducked_music + ducked_ambience + sfx
    sf.write(WORK / "premaster.wav", mix, SR)
    for name, bus in [("voice", voice), ("music_ducked", ducked_music), ("ambience_ducked", ducked_ambience), ("sfx", sfx)]:
        sf.write(WORK / f"debug_{name}.wav", bus, SR)
    save_json(REVIEW / "source_mix_report.json", {
        "music": {**music_levels, "source": audio_spec["music_asset"], "source_start": audio_spec["music_start"]},
        "ambience": {**ambience_levels, "source": audio_spec["ambience_asset"], "source_start": audio_spec["ambience_start"], "native_clip_audio_used": True},
        "ducking": {"music_min_gain": 0.24, "ambience_min_gain": 0.7872, "sfx_min_gain": 0.658, "voice_preroll_ms": 120},
        "native_clip_audio_used": True,
        "generated_bird_vocalisations": False,
        "generated_bear_or_vehicle_foley": False,
        "sfx_selection_model_used": sfx_selection_model_used,
        "premaster_sample_peak_dbfs": round(float(20 * np.log10(np.max(np.abs(mix)) + 1e-12)), 4)
    })
    return mix, {"voice": voice, "music": ducked_music, "ambience": ducked_ambience, "sfx": sfx}


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
        "method": "V2-style two-pass loudnorm, conservative 192 kHz limiting and measured AAC-domain calibration; no gate bypass."
    })

    bed = stems["music"] + stems["ambience"] + stems["sfx"]
    scale = float(np.sum((final_mix - stems["voice"]) * bed) / (np.sum(bed * bed) + 1e-9))
    scale = float(np.clip(scale, 0.0, 4.0))
    stem_dir = REVIEW / "stems"
    stem_dir.mkdir(parents=True, exist_ok=True)
    sf.write(stem_dir / "01_voice.wav", stems["voice"], SR, subtype="PCM_24")
    sf.write(stem_dir / "02_music.wav", stems["music"] * scale, SR, subtype="PCM_24")
    sf.write(stem_dir / "03_ambience.wav", stems["ambience"] * scale, SR, subtype="PCM_24")
    sf.write(stem_dir / "04_sfx.wav", stems["sfx"] * scale, SR, subtype="PCM_24")
    reconstruction = stems["voice"] + scale * bed
    save_json(REVIEW / "stem_diagnostics.json", {
        "bed_scale": scale,
        "residual_dbfs": round(float(20 * np.log10(np.sqrt(np.mean((final_mix - reconstruction) ** 2)) + 1e-12)), 4),
        "note": "Reference stems are not a claimed bit-perfect unmastering of the delivered AAC."
    })
    return final_wav, final_aac, final_mix


def mux_and_qc(final_aac: Path):
    silent = WORK / "dance_silent.mp4"
    if not silent.exists():
        raise FileNotFoundError("Render the vertical picture first")
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
        "checks": checks, "passed": all(checks.values())
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
    credits = """# Credits — They Don't Flirt. They Choreograph.

## Footage

- **Laysan Albatross Mating Dance 2016**, Midway Atoll, Ann Bell / U.S. Fish & Wildlife Service. Public domain.
- Rights page: https://commons.wikimedia.org/wiki/File:Laysan_Albatross_Mating_Dance_2016.webm
- Original 24-second retention-first vertical edit, narration, dance-card animation, mirror-split freeze and sound design: Monarch Cam production.
- Exact timeline/source ranges: `review/visual_edit_ledger.json`.

## Audio

- **Little, happy tune - 22.10.2015** — cabled_mess, CC0 1.0. Source: https://freesound.org/people/cabled_mess/sounds/335361/
- **Cartoon Boing.wav** — reelworldstudio, CC0 1.0. Source: https://freesound.org/people/reelworldstudio/sounds/161122/
- **Comedy_Music_Samples_033.wav** — jalastram, CC0 1.0. Source: https://freesound.org/people/jalastram/sounds/457985/
- **Whoosh_Simple_ER_SFX_1.wav** — Alex_hears_things, CC0 1.0. Source: https://freesound.org/people/Alex_hears_things/sounds/521044/
- **Soft Cinematic Impact** — Rizzard, CC0 1.0. Source: https://freesound.org/people/Rizzard/sounds/560156/
- CC0 legal text: https://creativecommons.org/publicdomain/zero/1.0/
- Original public-domain USFWS clip audio retained at low level as ambience; not represented as generated bird sound.
- Narration: AI-generated with Microsoft Edge TTS `en-US-AndrewNeural`.
- No generated bird vocalisation, attack, bear, car, handle, door or food-reward sound was added.
- This is a separate new-topic Short; the 35-second Master, 20-second follow-up and Sound V2 remain unchanged.
"""
    (BASE / "CREDITS.md").write_text(credits, encoding="utf-8")

    upload = """UPLOAD TITLE
They Don't Flirt. They Choreograph.

DESCRIPTION
This isn't a fight. It's a dance audition for a lifelong partner.

Laysan albatrosses bow, clack bills and point at the sky. Young birds practice these dozens of ritualized moves for years before forming a pair bond that lasts for life. Yes, USFWS literally calls them dance parties.

Public-domain footage by Ann Bell / U.S. Fish & Wildlife Service, filmed on Midway Atoll. This is a general species explanation, not a claim about these two birds' history.

Footage: Laysan Albatross Mating Dance 2016, USFWS (public domain).
Music: Little, happy tune - 22.10.2015 — cabled_mess (CC0).
SFX: reelworldstudio, jalastram, Alex_hears_things and Rizzard (CC0).
Narration: AI-generated English voice.

#Shorts #Birds #Wildlife

UPLOAD NOTES
- Native 1080x1920 vertical Short; 24.000 seconds / 720 frames.
- Keep hashtags in the description, not in the title field.
- Use review/cover.jpg as the 0.07s hook-frame cover reference.
- Pin the prepared comment and clarify that this is general species behavior, not these two birds' history.
- Do not add a bear, car, handle, door, food-reward, 25M-view, part-2 or viral claim.
- Compare 24h / 3d / 7d stayed-to-watch, engaged views, average percentage viewed, loops, likes, comments, shares and subscribers gained; no viral result is guaranteed.
"""
    (REVIEW / "UPLOAD_METADATA_DANCE.txt").write_text(upload, encoding="utf-8")

    metadata = """# Upload Metadata — They Don't Flirt. They Choreograph.

**Primary title:** `They Don't Flirt. They Choreograph.`

**Clean title only — no hashtags in the title field.**

**Description:** see `UPLOAD_METADATA_DANCE.txt` and `DANCE_PLAN_AND_METADATA.md`.

**First three hashtags:** `#Shorts #Birds #Wildlife` — in the description, not the title.

**Tags:** Laysan albatross, albatross dance, courtship dance, funny birds, bird dance, Midway Atoll, USFWS, public domain footage, wildlife short, bird behavior, nature comedy, albatross, Monarch Cam, dance party.

**Cover text:** `THIS IS A JOB INTERVIEW.` / optional A/B `WOULD YOU PASS?`

**Pinned comment:** `Which move is your favorite: the bow, the bill clack, or the sky point?`

**Clarifying comment:** `This is general Laysan albatross courtship behavior. The clip doesn't tell us these two birds' individual history or whether they are already a pair.`

**Rejected:** bear/car/handle/door claims, 25M-view claim, "part 2" promise, any claim about these two birds' relationship history, or pre-upload "viral" claim.
"""
    (REVIEW / "DANCE_UPLOAD_METADATA.md").write_text(metadata, encoding="utf-8")

    script_lines = [f"{item['start']:05.2f}s | {item['text']}" for item in SPEC["narration"]]
    (REVIEW / "FINAL_NARRATION_DANCE.txt").write_text("\n".join(script_lines) + "\n", encoding="utf-8")


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
