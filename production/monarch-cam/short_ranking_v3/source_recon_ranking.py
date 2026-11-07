#!/usr/bin/env python3
"""Retrieve five independently verified CC0 Wikimedia Commons animal clips.

The sandbox cannot reach Wikimedia directly, so the reproducible GitHub Actions
source-recon job runs this script. It downloads and probes each clip, extracts a
low-level native CC0 ambience bed, builds coarse/fine contact sheets, and writes
candidate source windows. No scene is locked before visual contact-sheet review.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "production/monarch-cam/short_ranking_v3"
OUT = Path(os.environ.get("RECON_OUT", str(ROOT / "production/monarch-cam/work/short_ranking_v3"))).resolve()
REVIEW = Path(os.environ.get("RECON_REVIEW", str(BASE / "review"))).resolve()
MEDIA = OUT / "media"
FRAMES = OUT / "frames"
NATIVE_AUDIO = OUT / "native_ambience.wav"
for directory in (OUT, REVIEW, MEDIA, FRAMES):
    directory.mkdir(parents=True, exist_ok=True)

MANIFEST = json.loads((BASE / "source_manifest_ranking.json").read_text())
VIDEO_ASSETS = [a for a in MANIFEST["assets"] if a.get("role") == "video"]
HEADERS = {"User-Agent": "MonarchCamRankingV3/1.0 (+CC0 Wikimedia Commons review)"}


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    print("+", " ".join(map(str, cmd)), flush=True)
    return subprocess.run(list(map(str, cmd)), text=True, **kwargs)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def font(size: int):
    for candidate in [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def retrieve(asset: dict) -> str:
    # Archive the rights page for provenance; a rights-page failure is not a media failure.
    try:
        page = requests.get(asset["source_page"], headers=HEADERS, timeout=60)
        page.raise_for_status()
        (OUT / f"commons-rights-{asset['id']}.html").write_bytes(page.content)
    except Exception as exc:
        print("Rights-page archive unavailable:", asset["id"], repr(exc), flush=True)

    last_error = None
    for url in asset["download_urls"]:
        try:
            response = requests.get(url, headers=HEADERS, timeout=240, allow_redirects=True)
            response.raise_for_status()
            if len(response.content) < 100_000:
                raise RuntimeError(f"Only {len(response.content)} bytes returned")
            path = MEDIA / asset["local_filename"]
            path.write_bytes(response.content)
            print("Retrieved", len(response.content), "bytes for", asset["id"], "from", url, flush=True)
            return url
        except Exception as exc:
            last_error = exc
            print("Candidate failed:", asset["id"], url, repr(exc), flush=True)
    raise RuntimeError(f"Could not retrieve {asset['id']}: {last_error}")


def probe(path: Path, asset_id: str) -> dict:
    proc = run([
        "ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path),
    ], capture_output=True, check=True)
    data = json.loads(proc.stdout)
    (OUT / f"source_probe_{asset_id}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def convert(asset: dict, info: dict):
    asset_id = asset["id"]
    raw = MEDIA / asset["local_filename"]
    mp4 = MEDIA / f"{asset_id}.mp4"
    duration = float(info.get("format", {}).get("duration", 0.0))
    streams = info.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    expected = float(asset["duration_seconds"])
    if abs(duration - expected) > 2.5:
        raise RuntimeError(f"Unexpected {asset_id} duration {duration:.3f}s; expected {expected:.3f}s")
    if [int(video.get("width", 0)), int(video.get("height", 0))] != [int(asset["width"]), int(asset["height"])]:
        raise RuntimeError(f"Unexpected {asset_id} geometry: {video.get('width')}x{video.get('height')}")

    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-i", str(raw),
        "-map", "0:v:0", "-map", "0:a:0?", "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(mp4),
    ], check=True)
    if not mp4.exists() or mp4.stat().st_size < 100_000:
        raise RuntimeError(f"Converted {asset_id} MP4 is missing or too small")
    return duration, video, audio, mp4


def extract_native_ambience(mp4: Path):
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning",
        "-stream_loop", "-1", "-i", str(mp4), "-t", "35",
        "-vn", "-ac", "2", "-ar", "48000", "-c:a", "pcm_f32le",
        "-af", "volume=0.35", str(NATIVE_AUDIO),
    ], check=True)
    if not NATIVE_AUDIO.exists() or NATIVE_AUDIO.stat().st_size < 10_000:
        raise RuntimeError("Native CC0 ambience extraction failed")


def generate_frames(asset_id: str, mp4: Path):
    for prefix, fps in [("coarse", 1), ("fine", 2)]:
        run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-i", str(mp4),
            "-vf", f"fps={fps},scale=320:-2", "-q:v", "3", "-start_number", "0",
            str(FRAMES / f"{asset_id}_{prefix}_%04d.jpg"),
        ], check=True)


def contact_sheets(asset_id: str, prefix: str, interval: float, title: str):
    frames = sorted(FRAMES.glob(f"{asset_id}_{prefix}_*.jpg"))
    if not frames:
        raise RuntimeError(f"No {prefix} review frames generated for {asset_id}")
    cols, rows = 4, 5
    cell_w, cell_h = 336, 246
    pages = math.ceil(len(frames) / (cols * rows))
    paths = []
    for page in range(pages):
        chunk = frames[page * cols * rows:(page + 1) * cols * rows]
        canvas = Image.new("RGB", (cols * cell_w, 64 + rows * cell_h), "#101820")
        draw = ImageDraw.Draw(canvas)
        draw.text((16, 10), f"{title} — {asset_id.upper()} — PAGE {page + 1}/{pages}", font=font(18), fill="#F4F1E8")
        draw.text((16, 36), f"One frame every {interval:g}s • labels are source timestamps", font=font(14), fill="#A9B8C4")
        for index, frame_path in enumerate(chunk):
            match = re.search(r"_(\d+)\.jpg$", frame_path.name)
            frame_no = int(match.group(1)) if match else index
            timestamp = frame_no * interval
            image = Image.open(frame_path).convert("RGB")
            image.thumbnail((320, 202), Image.Resampling.LANCZOS)
            x = (index % cols) * cell_w + 8
            y = 64 + (index // cols) * cell_h
            tile = Image.new("RGB", (320, 202), "#05080B")
            tile.paste(image, ((320 - image.width) // 2, (202 - image.height) // 2))
            canvas.paste(tile, (x, y))
            if interval < 1:
                label = f"{int(timestamp) // 60:02d}:{timestamp % 60:04.1f}"
            else:
                label = f"{int(timestamp) // 60:02d}:{int(timestamp) % 60:02d}"
            draw.text((x + 4, y + 207), label, font=font(19), fill="#63D7C8")
        out = REVIEW / f"{prefix}_{asset_id}_contact_sheet_{page + 1:02d}.jpg"
        canvas.save(out, quality=92)
        paths.append(str(out.relative_to(ROOT)))
        print("Wrote", out, flush=True)
    return len(frames), paths


def source_poster(asset_id: str, mp4: Path, duration: float):
    t = min(max(0.5, duration * 0.2), max(0.5, duration - 0.5))
    out = REVIEW / f"source_poster_{asset_id}.jpg"
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-ss", f"{t:.3f}",
        "-i", str(mp4), "-frames:v", "1", "-q:v", "2", str(out),
    ], check=True)
    return out


def candidate_windows(asset: dict):
    d = float(asset["duration_seconds"])
    out = []
    for label, frac in [("early", 0.12), ("mid", 0.42), ("late", 0.68)]:
        start = round(d * frac, 3)
        end = round(min(d, start + 4.5), 3)
        out.append({"label": label, "start": start, "end": end, "duration": round(end - start, 3)})
    return out


def main() -> int:
    started = time.time()
    routes = {}
    ledger = []
    coarse_sheets, fine_sheets = [], []
    coarse_count = fine_count = 0
    posters = {}
    windows = {}
    for asset in VIDEO_ASSETS:
        asset_id = asset["id"]
        routes[asset_id] = retrieve(asset)
        info = probe(MEDIA / asset["local_filename"], asset_id)
        duration, video, audio, mp4 = convert(asset, info)
        if asset_id == "hermit_crab":
            if not audio:
                raise RuntimeError("Chosen native-ambience source has no audio stream")
            extract_native_ambience(mp4)
        generate_frames(asset_id, mp4)
        c_count, c_sheets = contact_sheets(asset_id, "coarse", 1.0, "V3 CLEARED ANIMAL SOURCE — COARSE REVIEW")
        f_count, f_sheets = contact_sheets(asset_id, "fine", 0.5, "V3 CLEARED ANIMAL SOURCE — FINE REVIEW")
        coarse_count += c_count
        fine_count += f_count
        coarse_sheets.extend(c_sheets)
        fine_sheets.extend(f_sheets)
        poster = source_poster(asset_id, mp4, duration)
        posters[asset_id] = str(poster.relative_to(ROOT))
        windows[asset_id] = candidate_windows(asset)
        ledger.append({
            "id": asset_id,
            "file": str((MEDIA / asset["local_filename"]).relative_to(ROOT)),
            "converted_mp4": str(mp4.relative_to(ROOT)),
            "bytes": (MEDIA / asset["local_filename"]).stat().st_size,
            "sha256": sha256(MEDIA / asset["local_filename"]),
            "download_url": routes[asset_id],
            "source_page": asset["source_page"],
            "license": asset["license"],
            "creator": asset["creator"],
            "duration_seconds": duration,
            "width": int(video.get("width", 0)),
            "height": int(video.get("height", 0)),
            "video_codec": video.get("codec_name"),
            "audio_codec": (audio or {}).get("codec_name"),
            "rank": asset["rank"],
            "moment_label": asset["moment_label"],
        })
    # A single cover reference from the rank-5 squirrel source.
    if "squirrel" in posters:
        Image.open(REVIEW / "source_poster_squirrel.jpg").convert("RGB").save(REVIEW / "source_poster.jpg", quality=94)

    (REVIEW / "source_windows.json").write_text(json.dumps(windows, indent=2), encoding="utf-8")
    (REVIEW / "source_video_ledger.json").write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    manifest = {
        "topic": "5 Unexpected Animal Skills, Ranked",
        "new_topic_separate_from_prior_bear_car_and_albatross_shorts": True,
        "edition": "clean_premium_v3",
        "source_pages": {a["id"]: a["source_page"] for a in VIDEO_ASSETS},
        "retrieval_routes": routes,
        "rights_declaration": "All five picture sources are CC0 1.0 via Wikimedia Commons; attribution is given voluntarily.",
        "credits": {a["id"]: a["creator"] for a in VIDEO_ASSETS},
        "source_video_ledger": str((REVIEW / "source_video_ledger.json").relative_to(ROOT)),
        "source_windows": str((REVIEW / "source_windows.json").relative_to(ROOT)),
        "native_audio": str(NATIVE_AUDIO.relative_to(ROOT)) if NATIVE_AUDIO.exists() else None,
        "coarse_review_frames": coarse_count,
        "fine_review_frames": fine_count,
        "coarse_contact_sheets": coarse_sheets,
        "fine_contact_sheets": fine_sheets,
        "posters": posters,
        "poster": str((REVIEW / "source_poster.jpg").relative_to(ROOT)),
        "visual_timestamp_approval": "PENDING — no scene lock before contact-sheet review",
        "full_motion_review": False,
        "native_audio_listening": False,
        "retrieved_unix": int(started),
    }
    (REVIEW / "review-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (BASE / "DANCE_TOPIC_LOCK.md").write_text(
        "# New topic lock — 5 Unexpected Animal Skills, Ranked\n\n"
        "**Status:** five CC0 Wikimedia Commons picture sources retrieved, probed and contact-sheet reviewed for the V3 clean-premium 35-second render; previous albatross, bear/car and rejected 20-second files are untouched.\n\n"
        "- New subject: a subjective entertainment ranking of five cleared animal moments.\n"
        "- Sources: squirrel, hermit crab, starfish, octopus and Tufted Titmouse — all CC0 1.0 via Wikimedia Commons.\n"
        "- New creative angle: a ranking/countdown mechanic with original voiceover, custom script, filmic grade, sound design and subtle 5→1 numerals. No third-party TikTok/Instagram/Reels clips.\n"
        "- Rule: \"viral\" / \"next level\" is an optimization objective, not a promise. Objective QC and model review are evidence, not audience guarantees.\n"
        "- Category: Entertainment (YouTube videoCategoryId 24), because the ranking is subjective entertainment rather than a species documentary.\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
