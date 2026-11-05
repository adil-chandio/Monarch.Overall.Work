#!/usr/bin/env python3
"""Narration, licensed sound, AAC calibration, mux and review for the 35 s Short."""
from __future__ import annotations

import asyncio
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import edge_tts
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "production/monarch-cam/short_35"
WORK = ROOT / "production/monarch-cam/work/short_35"
REVIEW = BASE / "review"
OUT = ROOT / "deliverables/MONARCH_CAM_This_Bear_Window_35s_Short.mp4"
SPEC = json.loads((BASE / "short_spec.json").read_text())
DURATION = float(SPEC["duration"])
SR = 48000
SAMPLES = int(DURATION * SR)
TARGET_I = -14.1
TARGET_TP = -2.2

sys.path.insert(0, str(ROOT / "production/monarch-cam/sound_v2"))
sys.path.insert(0, str(ROOT / "production/monarch-cam"))
import build_sound_v2 as sound  # noqa: E402
import build_preview as preview  # noqa: E402

# Asset provenance stays in the verified V2 manifest; review outputs belong to this Short.
sound.WORK = WORK
sound.REVIEW = REVIEW


def run(command, stdout=None):
    print("+", " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), check=True, stdout=stdout)


def save_json(path: Path, data):
    sound.save_json(path, data)


def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    if len(clip) < samples:
        clip = np.pad(clip, ((0, samples - len(clip)), (0, 0)))
    return clip[:samples].astype(np.float32)


def build_audio():
    asyncio.run(synthesize_voice())
    assets = sound.download_assets()
    api = None
    try:
        from earshot import api as earshot_api
        earshot_api.load("onnx")
        api = earshot_api
    except Exception as exc:
        print("Earshot unavailable during SFX selection; fixed reviewed trims remain required:", repr(exc), flush=True)
    voice = np.zeros(SAMPLES, np.float32)
    ledger = []
    narration = SPEC["narration"]
    for index, item in enumerate(narration):
        clip = preview.decode_vo(WORK / f"{item['id']}.mp3").astype(np.float32)
        clip = sound.high_low_pass(clip, highpass=75)
        clip = sound.fade_edges(clip, 0.018, 0.018)
        start_sample = int(round(item["start"] * SR))
        slot_end = int(round(narration[index + 1]["start"] * SR)) if index + 1 < len(narration) else SAMPLES
        slot_samples = slot_end - start_sample
        allowed_samples = slot_samples - int(0.06 * SR)
        tempo = 1.0
        if len(clip) > allowed_samples:
            tempo = len(clip) / allowed_samples
            if tempo > 1.12:
                raise RuntimeError(f"{item['id']} needs excessive tempo {tempo:.3f}")
            clip = preview.decode_vo(WORK / f"{item['id']}.mp3", tempo=tempo).astype(np.float32)
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
    music = sound.fade_edges(music, 0.60, 0.90)
    music, music_levels = sound.normalize_loudness(music, audio_spec["music_lufs"])
    # Musical contrast follows information reveals rather than arbitrary cuts.
    env_t = np.array([0, 2.15, 7.25, 11.35, 16.25, 19.35, 25.20, 30.35, 34.5, 35.0])
    env_v = np.array([0.56, 0.70, 0.83, 0.92, 0.70, 1.00, 0.84, 0.74, 0.40, 0.25])
    music *= np.interp(np.arange(SAMPLES) / SR, env_t, env_v).astype(np.float32)[:, None]

    ambience = fit_length(sound.decode(assets[audio_spec["ambience_asset"]], audio_spec["ambience_start"], DURATION, af="highpass=f=80,lowpass=f=6500"))
    ambience = sound.fade_edges(ambience, 0.60, 0.70)
    ambience, ambience_levels = sound.normalize_loudness(ambience, audio_spec["ambience_lufs"])
    ambience *= np.interp(
        np.arange(SAMPLES) / SR,
        [0, 2.15, 7.25, 11.35, 16.25, 19.35, 25.20, 30.35, 35],
        [0.65, 0.9, 0.95, 1.0, 0.55, 0.9, 1.0, 0.8, 0.25]
    ).astype(np.float32)[:, None]

    sfx = np.zeros_like(voice)
    sfx_paths = {}
    for kind, definition in audio_spec["sfx"].items():
        source = assets[definition["asset"]]
        path = WORK / f"selected_{kind}.wav"
        sf.write(path, source[int(definition["trim_start"] * SR):int(definition["trim_end"] * SR)], SR)
        clip, selection = sound.choose_sfx_excerpt(
            path, f"{definition['description']} clean", definition["pre"], definition["post"], api, api is not None
        )
        if kind == "impact":
            clip = sound.high_low_pass(clip, 38, 7500)
        elif kind == "whoosh":
            clip = sound.high_low_pass(clip, 90, 6500)
        else:
            clip = sound.high_low_pass(clip, 240, 3600)
        clip = sound.fade_edges(clip, 0.006 if kind == "tick" else 0.012, min(0.08, len(clip) / SR / 4))
        sf.write(path, clip, SR)
        sfx_paths[kind] = path
        save_json(REVIEW / f"sfx_{kind}_selection.json", selection)

    cue_ledger = []
    for cue in audio_spec["cues"]:
        clip, _ = sf.read(sfx_paths[cue["kind"]], dtype="float32", always_2d=True)
        placement = sound.add_at_peak(sfx, clip, cue["frame"] / SPEC["fps"], cue["peak_db"])
        cue_ledger.append({**cue, "time_s": cue["frame"] / SPEC["fps"], "source_file": Path(sfx_paths[cue["kind"]]).name, "placement": placement})
    save_json(REVIEW / "cue_ledger.json", cue_ledger)
    save_json(REVIEW / "resolved_cues.json", {
        "fps": SPEC["fps"], "events": [
            {"t": cue["time_s"], "frame": cue["frame"], "kind": cue["kind"], "peak_dbfs": cue["peak_db"], "label": cue["label"], "supported_by_picture": True, "generated_audio": False}
            for cue in cue_ledger
        ],
        "intentionally_silent": ["No invented food-reward sound", "No handle, door, attack or bear-vocalisation cue"]
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
        "ambience": {**ambience_levels, "source": audio_spec["ambience_asset"], "source_start": audio_spec["ambience_start"], "native_camera_audio": False},
        "ducking": {"music_min_gain": 0.24, "ambience_min_gain": 0.7872, "sfx_min_gain": 0.658, "voice_preroll_ms": 120},
        "generated_bear_or_vehicle_foley": False,
        "premaster_sample_peak_dbfs": round(float(20 * np.log10(np.max(np.abs(mix)) + 1e-12)), 4)
    })
    return mix, {"voice": voice, "music": ducked_music, "ambience": ducked_ambience, "sfx": sfx}


def encode_aac(wav: Path, destination: Path):
    run(["ffmpeg", "-y", "-i", wav, "-t", f"{DURATION:.3f}", "-c:a", "aac", "-b:a", "192k", "-ar", SR, "-ac", 2, destination])


def decode_aac(path: Path):
    return sound.decode(path, 0, DURATION)


def master_audio(mix: np.ndarray, stems: dict):
    """Calibrate on decoded AAC, never trust only the WAV limiter reading."""
    pre = WORK / "premaster_target.wav"
    normalized_mix, normalization_report = sound.normalize_loudness(mix, -13.8)
    sf.write(pre, normalized_mix, SR, subtype="PCM_24")
    limited = WORK / "premaster_limited.wav"
    run(["ffmpeg", "-y", "-i", pre, "-af", "aresample=192000,alimiter=limit=0.67:level=false,aresample=48000", "-t", f"{DURATION:.3f}", limited])
    first_aac = WORK / "master_first_pass.m4a"
    encode_aac(limited, first_aac)
    first_mix = decode_aac(first_aac)
    pre_loudness = sound.loudness(first_aac)

    calibration_gain = TARGET_I - float(pre_loudness["input_i"])
    calibrated = WORK / "master_calibrated.wav"
    run(["ffmpeg", "-y", "-i", limited, "-af", f"volume={calibration_gain:.6f}dB,aresample=192000,alimiter=limit=0.67:level=false,aresample=48000", "-t", f"{DURATION:.3f}", calibrated])
    second_aac = WORK / "master_second_pass.m4a"
    encode_aac(calibrated, second_aac)
    second_loudness = sound.loudness(second_aac)

    # A small post-codec residual correction was necessary on the previous deliverable too.
    residual_gain = TARGET_I - float(second_loudness["input_i"])
    final_wav = WORK / "final_mix.wav"
    run(["ffmpeg", "-y", "-i", calibrated, "-af", f"volume={residual_gain:.6f}dB", "-t", f"{DURATION:.3f}", final_wav])
    final_aac = WORK / "final_audio.m4a"
    encode_aac(final_wav, final_aac)
    delivered_loudness = sound.loudness(final_aac)

    # Guard true peak after the residual codec correction; loudness tolerance is rechecked below.
    if float(delivered_loudness["input_tp"]) > TARGET_TP - 0.01:
        peak_guard = WORK / "final_peak_guard.wav"
        run(["ffmpeg", "-y", "-i", final_wav, "-af", "aresample=192000,alimiter=limit=0.65:level=false,aresample=48000", "-t", f"{DURATION:.3f}", peak_guard])
        final_wav = peak_guard
        encode_aac(final_wav, final_aac)
        delivered_loudness = sound.loudness(final_aac)

    final_mix = decode_aac(final_aac)
    repair_report = {"threshold": 0.35, "max_repair_samples_per_run": 48, "passes": []}
    for click_pass in range(1, 4):
        runs = sound.detect_click_runs(final_mix)
        pass_record = {"pass": click_pass, "before_runs": runs}
        repair_report["passes"].append(pass_record)
        if not runs:
            break
        pcm, pcm_rate = sf.read(final_wav, dtype="float32", always_2d=True)
        if pcm_rate != SR:
            raise RuntimeError(f"Unexpected PCM master rate: {pcm_rate}")
        repaired, repairs = sound.repair_short_click_runs(pcm, runs)
        pass_record["operations"] = repairs
        repaired_wav = WORK / f"final_mix_click_repaired_{click_pass}.wav"
        sf.write(repaired_wav, repaired, SR, subtype="PCM_24")
        final_wav = repaired_wav
        encode_aac(final_wav, final_aac)
        final_mix = decode_aac(final_aac)
        pass_record["after_runs"] = sound.detect_click_runs(final_mix)
        if not pass_record["after_runs"]:
            break
        if click_pass == 3:
            save_json(REVIEW / "click_repair.json", repair_report)
            raise RuntimeError(f"Persistent AAC click runs after bounded repair: {pass_record['after_runs']}")
    repair_report["final_runs"] = sound.detect_click_runs(final_mix)
    repair_report["repaired_samples"] = sum(op["interpolated_samples"] for p in repair_report["passes"] for op in p.get("operations", []))
    save_json(REVIEW / "click_repair.json", repair_report)

    calibration = {
        "target_integrated_lufs": TARGET_I, "target_true_peak_dbtp": TARGET_TP,
        "premaster_normalization": normalization_report,
        "first_pass_aac": pre_loudness, "calibration_gain_db": calibration_gain,
        "second_pass_aac": second_loudness, "residual_gain_db": residual_gain,
        "delivered_aac_before_final_click_check": delivered_loudness,
        "final_aac": sound.loudness(final_aac),
        "method": "Conservative limiting followed by measured AAC-domain integrated-loudness correction; no gate bypass."
    }
    save_json(REVIEW / "mastering_calibration.json", calibration)

    # Reference stems use a bounded residual fit and retain voice as the reference track.
    bed = stems["music"] + stems["ambience"] + stems["sfx"]
    scale = float(np.sum((final_mix - stems["voice"]) * bed) / (np.sum(bed * bed) + 1e-9))
    scale = float(np.clip(scale, 0.0, 4.0))
    stem_dir = REVIEW / "stems"
    stem_dir.mkdir(parents=True, exist_ok=True)
    sf.write(stem_dir / "01_voice.wav", stems["voice"], SR)
    sf.write(stem_dir / "02_music.wav", stems["music"] * scale, SR)
    sf.write(stem_dir / "03_ambience.wav", stems["ambience"] * scale, SR)
    sf.write(stem_dir / "04_sfx.wav", stems["sfx"] * scale, SR)
    reconstruction = stems["voice"] + scale * bed
    save_json(REVIEW / "stem_diagnostics.json", {
        "bed_scale": scale,
        "residual_dbfs": round(float(20 * np.log10(np.sqrt(np.mean((final_mix - reconstruction) ** 2)) + 1e-12)), 4),
        "note": "Reference stems are not a claimed bit-perfect unmastering of the delivered AAC."
    })
    return final_wav, final_aac, final_mix


def mux_and_qc(final_aac: Path):
    silent = WORK / "short_35_silent.mp4"
    if not silent.exists():
        raise FileNotFoundError("Render the vertical picture first")
    run([
        "ffmpeg", "-y", "-i", silent, "-i", final_aac, "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "copy", "-t", f"{DURATION:.3f}", "-movflags", "+faststart", OUT
    ])
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=index,codec_name,codec_type,width,height,r_frame_rate,nb_frames,sample_rate,channels",
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
    frames = int(video.get("nb_frames", 0))
    checks = {
        "duration_35s": abs(duration - DURATION) <= 0.05,
        "frames_1050": frames == SPEC["frame_count"],
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
        api.load("onnx")
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
    credits = """# Credits — This Bear Didn’t Need the Door

## Footage

- **Bears in Cars**, Yosemite National Park, National Park Service. Public domain.
- Rights declaration: https://www.nps.gov/media/video/view.htm?id=07B1F1A5-E8DC-0BCE-DAFAE3F9B356AA73
- Original vertical edit, narration, explanatory animation and sound design: Monarch Cam production.
- Exact timeline/source ranges: `review/visual_edit_ledger.json`.

## Audio

- **Emotional Spiritual Soundtrack - Respect** — MusicByMisterbates / Misterbates, CC0 1.0. Source: https://freesound.org/people/MusicByMisterbates/sounds/603711/
- **Forest Night Ambience…** — neverak, CC0 1.0. Real nocturnal field recording. Source: https://freesound.org/people/neverak/sounds/708611/
- **Whoosh_Simple_ER_SFX_1.wav** — Alex_hears_things, CC0 1.0. Source: https://freesound.org/people/Alex_hears_things/sounds/521044/
- **Soft Cinematic Impact** — Rizzard, CC0 1.0. Source: https://freesound.org/people/Rizzard/sounds/560156/
- CC0 legal text: https://creativecommons.org/publicdomain/zero/1.0/
- Narration: AI-generated with Microsoft Edge TTS `en-US-AndrewNeural`.
- Source camera audio was not available; added ambience is not represented as native NPS production sound.
- No generated bear roar, handle-pull, door or attack sound was added.
"""
    (BASE / "CREDITS.md").write_text(credits, encoding="utf-8")
    description = """UPLOAD TITLE
This Bear Didn’t Need the Door

DESCRIPTION
He came through the window—but the important lesson is how cars can become associated with food.

Real public-domain NPS footage from Yosemite, with original Monarch Cam narration and a visual explanation of food conditioning. Secure food and lock vehicles in bear country.

Footage: Bears in Cars, National Park Service (public domain).
Music: Emotional Spiritual Soundtrack - Respect — MusicByMisterbates (CC0).
Ambience: Forest Night Ambience — neverak (CC0).
SFX: Alex_hears_things and Rizzard (CC0).
Narration: AI-generated English voice.

#Shorts #Bears #Wildlife

UPLOAD NOTES
- Native 1080x1920 vertical Short; 35.000 seconds.
- Use review/cover.jpg as the cover reference where custom selection is available.
- Do not add a nonexistent full-episode/related-video link.
- Evaluate stayed to watch, engaged views, average view duration, percentage viewed, loops and subscribers gained after publication; no viral result is guaranteed.
"""
    (REVIEW / "UPLOAD_METADATA.txt").write_text(description, encoding="utf-8")
    script_lines = [f"{item['start']:05.2f}s | {item['text']}" for item in SPEC["narration"]]
    (REVIEW / "FINAL_NARRATION.txt").write_text("\n".join(script_lines) + "\n", encoding="utf-8")


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
