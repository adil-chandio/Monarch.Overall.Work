#!/usr/bin/env python3
"""Frame-locked, rights-aware shared SFX catalog/render/mix/mux helper.

The tool does not infer semantics from an arbitrary picture. A video workflow supplies
an event sheet whose frames are grounded in its shot plan/render timeline; this script
resolves each sound cue from the shared catalog, renders a stereo SFX stem, and writes
an auditable placement report.
"""
from __future__ import annotations

import argparse
import array
import json
import math
import re
import shutil
import subprocess
import sys
import wave
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "production/audio-library/catalog.json"
DEFAULT_SR = 48_000
AUDIO_SUFFIXES = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".mp4", ".mov", ".webm", ".mkv"}
UNCLEARED = {"unknown", "unverified", "user_provided_unverified", "unverified_user_provided", "pending"}
CLEARED = {"verified_public_domain", "verified_cc0", "verified_cc_by_with_required_attribution", "owned_or_original", "licensed"}


def find_ffmpeg() -> str:
    bundled = ROOT / "node_modules/@ffmpeg-installer/linux-x64/ffmpeg"
    if bundled.exists():
        return str(bundled)
    found = shutil.which("ffmpeg")
    if found:
        return found
    raise RuntimeError("FFmpeg is required (install it or add it to PATH).")


def relpath(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Cannot read JSON {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"Expected a JSON object in {path}")
    return data


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def seconds_to_frame(seconds: float, fps: float) -> int:
    if fps <= 0:
        raise ValueError("fps must be positive")
    return int(math.floor(float(seconds) * fps + 0.5))


def _tokens(value: Any) -> set[str]:
    if value is None:
        return set()
    items = value if isinstance(value, list) else [value]
    result: set[str] = set()
    for item in items:
        text = str(item).lower().replace("-", "_")
        result.update(part for part in re.split(r"[^a-z0-9]+", text) if part)
        result.add(text)
    return result


def flatten_catalog(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    sources = catalog.get("sources")
    if not isinstance(sources, list):
        raise RuntimeError("Catalog must contain a 'sources' list")
    cues = []
    for source in sources:
        if not isinstance(source, dict) or not source.get("id") or not source.get("path"):
            raise RuntimeError("Every catalog source needs id and path")
        for cue in source.get("cues", []):
            cues.append({**cue, "source_id": source["id"], "source_path": source["path"],
                         "rights_status": source.get("rights_status", "unknown"),
                         "use_scope": source.get("use_scope", "restricted"),
                         "provenance": source.get("provenance", ""), "source_duration": source.get("duration_seconds")})
    return cues


def resolve_cue(event: dict[str, Any], cues: list[dict[str, Any]]) -> dict[str, Any]:
    cue_id = event.get("cue_id") or event.get("cue") or event.get("asset_id")
    if cue_id:
        matches = [cue for cue in cues if cue.get("id") == cue_id]
        if not matches:
            raise RuntimeError(f"Cue '{cue_id}' is not in the shared SFX catalog")
        return matches[0]
    wanted = _tokens(event.get("tags", [])) | _tokens(event.get("effect")) | _tokens(event.get("kind"))
    wanted |= _tokens(event.get("vibe", []))
    ranked = []
    for cue in cues:
        available = _tokens(cue.get("tags", [])) | _tokens(cue.get("vibe", []))
        overlap = wanted & available
        if not overlap:
            continue
        score = len(overlap) / max(1, len(wanted))
        if event.get("source_id") and event["source_id"] == cue["source_id"]:
            score += 0.25
        ranked.append((score, cue.get("id", ""), cue))
    if not ranked:
        desc = event.get("effect") or event.get("kind") or event.get("tags")
        raise RuntimeError(f"No reviewed SFX catalog cue matches event {desc!r}; add/tag a cue rather than guessing")
    ranked.sort(key=lambda row: (-row[0], row[1]))
    return ranked[0][2]


def ensure_rights(cue: dict[str, Any], private_review: bool) -> None:
    status = str(cue.get("rights_status", "unknown")).lower()
    if status in UNCLEARED:
        if not private_review or cue.get("use_scope") != "private_review_only":
            raise RuntimeError(f"Cue {cue['id']} is {status}; only a private draft with --private-review may use it")
    elif status not in CLEARED:
        raise RuntimeError(f"Cue {cue['id']} has unsupported rights status {status!r}; public delivery is blocked")


def normalise_events(doc: dict[str, Any], catalog: dict[str, Any], cues: list[dict[str, Any]]) -> tuple[float, float, list[dict[str, Any]]]:
    fps = float(doc.get("fps", catalog.get("default_fps", 30)))
    duration = float(doc.get("duration_seconds", doc.get("duration", 0)))
    if fps <= 0 or duration <= 0:
        raise RuntimeError("Cue sheet requires positive fps and duration_seconds")
    total_frames = int(math.ceil(duration * fps))
    silent_spans = []
    for index, span in enumerate(doc.get("intentional_silence", []), 1):
        start, end = int(span.get("start_frame", -1)), int(span.get("end_frame", -1))
        if start < 0 or end <= start or end > total_frames:
            raise RuntimeError(f"Intentional-silence span {index} has invalid frame bounds")
        silent_spans.append((start, end))
    raw_events = doc.get("events", doc.get("placements"))
    if not isinstance(raw_events, list) or not raw_events:
        raise RuntimeError("Cue sheet needs a non-empty events or placements list")
    resolved = []
    for index, event in enumerate(raw_events, 1):
        if not isinstance(event, dict):
            raise RuntimeError(f"Event {index} is not a JSON object")
        if "frame" in event:
            frame = int(event["frame"])
            if "time" in event or "time_seconds" in event:
                t = float(event.get("time_seconds", event.get("time")))
                if abs(seconds_to_frame(t, fps) - frame) > 0:
                    raise RuntimeError(f"Event {index} has inconsistent frame/time ({frame}, {t})")
        elif "time_seconds" in event or "time" in event:
            t = float(event.get("time_seconds", event.get("time")))
            frame = seconds_to_frame(t, fps)
        else:
            raise RuntimeError(f"Event {index} requires a video frame (or time_seconds)")
        if frame < 0 or frame >= total_frames:
            raise RuntimeError(f"Event {index} frame {frame} is outside 0..{total_frames - 1}")
        cue = resolve_cue(event, cues)
        start = float(event.get("trim_start_seconds", cue.get("start_seconds", 0)))
        length = float(event.get("duration_seconds", cue.get("duration_seconds", 0)))
        if start < 0 or length <= 0:
            raise RuntimeError(f"Event {index} has invalid source trim")
        if cue.get("source_duration") is not None and start + length > float(cue["source_duration"]) + 1e-6:
            raise RuntimeError(f"Event {index} trim exceeds source {cue['source_id']}")
        event_end = frame + int(math.ceil(length * fps))
        if any(frame < silence_end and event_end > silence_start for silence_start, silence_end in silent_spans):
            raise RuntimeError(f"Event {index} overlaps a declared intentional-silence span")
        gain = float(event["gain"]) if "gain" in event else 10 ** (float(event.get("gain_db", -18)) / 20)
        if not math.isfinite(gain) or gain < 0 or gain > 1.5:
            raise RuntimeError(f"Event {index} gain must be between 0 and 1.5 linear")
        pan = float(event.get("pan", 0))
        if not -1 <= pan <= 1:
            raise RuntimeError(f"Event {index} pan must be between -1 and 1")
        resolved.append({
            **event, "frame": frame, "time_seconds": frame / fps,
            "cue_id": cue["id"], "source_id": cue["source_id"], "source_path": cue["source_path"],
            "rights_status": cue["rights_status"], "use_scope": cue["use_scope"],
            "source_start_seconds": start, "duration_seconds": length,
            "gain_linear": gain, "pan": pan,
        })
    return fps, duration, sorted(resolved, key=lambda row: (row["frame"], row["cue_id"]))


def decode_stereo(path: Path, sr: int, ffmpeg: str) -> array.array:
    if not path.exists():
        raise RuntimeError(f"SFX source is missing: {path}")
    proc = subprocess.run([
        ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(path), "-map", "0:a:0",
        "-vn", "-ar", str(sr), "-ac", "2", "-f", "f32le", "pipe:1",
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode:
        raise RuntimeError(f"Could not decode audio from {path}: {proc.stderr.decode(errors='replace')[-1000:]}")
    if not proc.stdout or len(proc.stdout) % 8:
        raise RuntimeError(f"Unexpected stereo float PCM from {path}")
    samples = array.array("f")
    samples.frombytes(proc.stdout)
    if sys.byteorder != "little":
        samples.byteswap()
    return samples


def render(args: argparse.Namespace) -> int:
    catalog = read_json(args.catalog)
    events_doc = read_json(args.events)
    cues = flatten_catalog(catalog)
    fps, duration, events = normalise_events(events_doc, catalog, cues)
    for event in events:
        # SFX demo reels are unverified unless explicitly cleared in the manifest.
        cue = next(c for c in cues if c["id"] == event["cue_id"])
        ensure_rights(cue, args.private_review)
    sr = int(catalog.get("default_sample_rate_hz", DEFAULT_SR))
    if sr != DEFAULT_SR:
        raise RuntimeError(f"This renderer currently requires {DEFAULT_SR} Hz, catalog requested {sr}")
    ffmpeg = find_ffmpeg()
    source_cache: dict[str, array.array] = {}
    total_samples = int(math.ceil(duration * sr))
    mix = array.array("f", [0.0]) * (total_samples * 2)
    resolved_report = []
    for event in events:
        source_path = (ROOT / event["source_path"]).resolve() if not Path(event["source_path"]).is_absolute() else Path(event["source_path"])
        key = str(source_path)
        if key not in source_cache:
            source_cache[key] = decode_stereo(source_path, sr, ffmpeg)
        source = source_cache[key]
        src_at = int(round(event["source_start_seconds"] * sr)) * 2
        requested = int(round(event["duration_seconds"] * sr))
        if src_at + requested * 2 > len(source):
            raise RuntimeError(f"Cue {event['cue_id']} excerpt extends beyond decoded source {event['source_id']}")
        rate = float(event.get("playback_rate", 1.0))
        if not 0.7 <= rate <= 1.3:
            raise RuntimeError(f"Cue {event['cue_id']} playback_rate outside safe 0.7..1.3")
        out_at = int(round(event["frame"] * sr / fps))
        wanted = min(int(requested / rate), int(float(event.get("render_duration_seconds", event["duration_seconds"])) * sr))
        wanted = min(wanted, total_samples - out_at)
        if wanted <= 0:
            raise RuntimeError(f"Cue {event['cue_id']} has no renderable samples")
        attack_n = max(1, int(round(float(event.get("fade_in_ms", 5)) * sr / 1000)))
        release_n = max(1, int(round(float(event.get("fade_out_ms", 55)) * sr / 1000)))
        pan = event["pan"]
        left_gain = math.sqrt((1 - pan) / 2) * math.sqrt(2) * event["gain_linear"]
        right_gain = math.sqrt((1 + pan) / 2) * math.sqrt(2) * event["gain_linear"]
        for j in range(wanted):
            env = min(1.0, j / attack_n, (wanted - 1 - j) / release_n)
            si = src_at + int(j * rate) * 2
            di = (out_at + j) * 2
            mix[di] += source[si] * event["gain_linear"] * env * left_gain / max(event["gain_linear"], 1e-12)
            mix[di + 1] += source[si + 1] * event["gain_linear"] * env * right_gain / max(event["gain_linear"], 1e-12)
        resolved_report.append({
            "frame": event["frame"], "time_seconds": event["time_seconds"], "sample_start": out_at,
            "cue_id": event["cue_id"], "source_id": event["source_id"], "source_path": event["source_path"],
            "rights_status": event["rights_status"], "visual_action": event.get("visual_action", event.get("picture", "")),
            "gain_linear": event["gain_linear"], "duration_seconds": wanted / sr,
        })
    peak = max((abs(x) for x in mix), default=0.0)
    peak_before_limit = peak
    if peak > 0.92:
        scale = 0.92 / peak
        for i in range(len(mix)):
            mix[i] *= scale
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    pcm = array.array("h")
    for value in mix:
        pcm.append(int(max(-0.92, min(0.92, value)) * 32767))
    with wave.open(str(out), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sr)
        wav.writeframes(pcm.tobytes())
    report_path = Path(args.report) if args.report else out.with_suffix(".resolved-cues.json")
    write_json(report_path, {
        "renderer": "tools/sfx_sync.py", "fps": fps, "duration_seconds": duration,
        "sample_rate_hz": sr, "total_cues": len(resolved_report),
        "private_review_only": bool(args.private_review), "peak_before_safety_limit": peak_before_limit,
        "safety_ceiling": 0.92, "output_wav": relpath(out), "events": resolved_report,
    })
    print(f"Rendered {len(events)} frame-locked SFX cues → {out}")
    if any(e["rights_status"] in UNCLEARED for e in events):
        print("RIGHTS WARNING: contains unverified user-provided sources; private review only, do not publish.", file=sys.stderr)
    print(f"Resolved cue report → {report_path}")
    return 0


def scan(args: argparse.Namespace) -> int:
    ffmpeg = find_ffmpeg()
    root = Path(args.root)
    if not root.is_absolute():
        root = ROOT / root
    if not root.exists():
        raise RuntimeError(f"Scan root does not exist: {root}")
    found = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in AUDIO_SUFFIXES):
        proc = subprocess.run([ffmpeg, "-hide_banner", "-i", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=False)
        text = proc.stderr.decode(errors="replace")
        duration_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", text)
        duration = None
        if duration_match:
            h, m, s = duration_match.groups()
            duration = int(h) * 3600 + int(m) * 60 + float(s)
        has_audio = bool(re.search(r"Audio:\s*", text))
        found.append({
            "path": relpath(path), "size_bytes": path.stat().st_size,
            "duration_seconds": duration, "has_audio_stream": has_audio,
            "rights_status": "unknown", "eligible_for_public_use": False,
            "next_step": "Listen/review, tag the useful excerpt, and establish rights before adding it to catalog.json.",
        })
    output = Path(args.output)
    write_json(output, {"scan_root": relpath(root), "candidates": found})
    print(f"Found {len(found)} candidate files under {root}; none were auto-cleared or added to the approved catalog.")
    print(f"Inventory → {output}")
    return 0


def mix(args: argparse.Namespace) -> int:
    ffmpeg = find_ffmpeg()
    voice = Path(args.voice)
    sfx = Path(args.sfx)
    if not voice.exists() or not sfx.exists():
        raise RuntimeError("Both --voice and --sfx files must exist")
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(voice), "-i", str(sfx)]
    if args.music:
        music = Path(args.music)
        if not music.exists():
            raise RuntimeError(f"Music stem is missing: {music}")
        command += ["-i", str(music)]
    filters = [
        "[0:a]aresample=48000,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,asplit=2[voice][key]",
        "[1:a]aresample=48000,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[sfx0]",
        "[sfx0][key]sidechaincompress=threshold=0.055:ratio=1.6:attack=18:release=220[sfx]",
    ]
    inputs = "[voice][sfx]"
    n_inputs = 2
    if args.music:
        filters += [
            "[2:a]aresample=48000,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,volume=0.35[music0]",
            "[music0][key]sidechaincompress=threshold=0.07:ratio=2:attack=35:release=280[music]",
        ]
        inputs += "[music]"
        n_inputs = 3
    filters.append(f"{inputs}amix=inputs={n_inputs}:duration=first:dropout_transition=0,loudnorm=I={args.lufs}:TP={args.true_peak}:LRA=7,alimiter=limit=0.84:level=disabled,aresample=48000[aout]")
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    command += ["-filter_complex", ";".join(filters), "-map", "[aout]", "-c:a", "pcm_s24le", "-ar", "48000", "-ac", "2", str(out)]
    subprocess.run(command, check=True)
    print(f"Voice-driven SFX mix → {out}; source video audio is not an input to this step.")
    return 0


def mux(args: argparse.Namespace) -> int:
    ffmpeg = find_ffmpeg()
    video, audio, out = Path(args.video), Path(args.audio), Path(args.output)
    if not video.exists() or not audio.exists():
        raise RuntimeError("Both --video and --audio files must exist")
    out.parent.mkdir(parents=True, exist_ok=True)
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(video), "-i", str(audio),
               "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
               "-ar", "48000", "-ac", "2", "-shortest", "-movflags", "+faststart", str(out)]
    subprocess.run(command, check=True)
    print(f"Muxed video with mastered audio only → {out}; original video audio was dropped by explicit stream mapping.")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    q = sub.add_parser("scan", help="Inventory local audio/video sources without approving them")
    q.add_argument("--root", required=True, help="Folder to scan, e.g. production/audio-library/inbox")
    q.add_argument("--output", required=True, help="JSON candidate inventory")
    q.set_defaults(func=scan)
    q = sub.add_parser("render", help="Render an SFX-only WAV from a frame-based cue sheet")
    q.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    q.add_argument("--events", type=Path, required=True, help="Project cue sheet JSON")
    q.add_argument("--output", required=True, help="SFX-only WAV output")
    q.add_argument("--report", help="Resolved cue report path")
    q.add_argument("--private-review", action="store_true", help="Permit user-provided but unverified assets for private draft only")
    q.set_defaults(func=render)
    q = sub.add_parser("mix", help="Mix VO with the SFX stem (optionally music), ducking effects under speech")
    q.add_argument("--voice", required=True)
    q.add_argument("--sfx", required=True)
    q.add_argument("--music")
    q.add_argument("--output", required=True)
    q.add_argument("--lufs", type=float, default=-14.0)
    q.add_argument("--true-peak", type=float, default=-1.5)
    q.set_defaults(func=mix)
    q = sub.add_parser("mux", help="Mux mastered audio while explicitly stripping source-video audio")
    q.add_argument("--video", required=True)
    q.add_argument("--audio", required=True)
    q.add_argument("--output", required=True)
    q.set_defaults(func=mux)
    return p


def main() -> int:
    args = parser().parse_args()
    try:
        return args.func(args)
    except (RuntimeError, OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"sfx_sync: ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
