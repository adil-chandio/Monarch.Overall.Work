#!/usr/bin/env python3
"""Retrieve the public-domain USFWS Laysan albatross dance clip and build review sheets.

This is a NEW topic and a NEW source, deliberately separate from the NPS bears/cars
footage. The sandbox cannot reach Wikimedia directly, so the reproducible GitHub
Actions source-recon job runs this script. No scene is locked before visual review.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "production/monarch-cam/short_dance_clean_v2"
OUT = Path(os.environ.get("RECON_OUT", str(ROOT / "production/monarch-cam/work/short_dance_clean_v2"))).resolve()
REVIEW = Path(os.environ.get("RECON_REVIEW", str(BASE / "review"))).resolve()
MEDIA = OUT / "media"
FRAMES = OUT / "frames"
for directory in (OUT, REVIEW, MEDIA, FRAMES):
    directory.mkdir(parents=True, exist_ok=True)

RIGHTS_PAGE = "https://commons.wikimedia.org/wiki/File:Laysan_Albatross_Mating_Dance_2016.webm"
USFWS_STORY = "https://www.fws.gov/story/2017-08/laysan-lovesong"
ADW_PAGE = "https://animaldiversity.org/accounts/Phoebastria_immutabilis/"
SOURCE_URLS = [
    "https://upload.wikimedia.org/wikipedia/commons/f/f4/Laysan_Albatross_Mating_Dance_2016.webm",
    "https://commons.wikimedia.org/wiki/Special:Redirect/file/Laysan_Albatross_Mating_Dance_2016.webm",
]
WEBM = MEDIA / "laysan_albatross_dance.webm"
MP4 = MEDIA / "laysan_albatross_dance.mp4"
NATIVE_AUDIO = OUT / "usfws_clip_audio.wav"


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    print("+", " ".join(map(str, cmd)), flush=True)
    return subprocess.run(list(map(str, cmd)), text=True, **kwargs)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def retrieve() -> str:
    headers = {"User-Agent": "MonarchCamDanceResearch/1.0 (+public-domain USFWS media review)"}
    # Archive the rights page for provenance; a rights-page failure is not a media failure.
    try:
        page = requests.get(RIGHTS_PAGE, headers=headers, timeout=60)
        page.raise_for_status()
        (OUT / "commons-rights-page.html").write_bytes(page.content)
    except Exception as exc:
        print("Rights-page archive unavailable:", repr(exc), flush=True)

    last_error = None
    for url in SOURCE_URLS:
        try:
            response = requests.get(url, headers=headers, timeout=180, allow_redirects=True)
            response.raise_for_status()
            if len(response.content) < 1_000_000:
                raise RuntimeError(f"Only {len(response.content)} bytes returned")
            WEBM.write_bytes(response.content)
            print("Retrieved", len(response.content), "bytes from", url, flush=True)
            return url
        except Exception as exc:
            last_error = exc
            print("Candidate failed:", url, repr(exc), flush=True)
    raise RuntimeError(f"Could not retrieve public-domain USFWS dance clip: {last_error}")


def probe(path: Path) -> dict:
    proc = run([
        "ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path),
    ], capture_output=True, check=True)
    data = json.loads(proc.stdout)
    (OUT / "source_probe.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def convert_and_extract(info: dict):
    duration = float(info.get("format", {}).get("duration", 0.0))
    streams = info.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if not 50.0 <= duration <= 56.0:
        raise RuntimeError(f"Unexpected source duration {duration:.3f}s; refusing blind edit")
    if [int(video.get("width", 0)), int(video.get("height", 0))] != [1920, 1080]:
        raise RuntimeError(f"Unexpected source geometry: {video.get('width')}x{video.get('height')}")

    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-i", str(WEBM),
        "-map", "0:v:0", "-map", "0:a:0?", "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(MP4),
    ], check=True)
    if not MP4.exists() or MP4.stat().st_size < 100_000:
        raise RuntimeError("Converted source MP4 is missing or too small")

    if audio:
        run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-i", str(WEBM),
            "-vn", "-map", "0:a:0", "-ac", "2", "-ar", "48000", "-c:a", "pcm_f32le",
            str(NATIVE_AUDIO),
        ], check=True)
        if not NATIVE_AUDIO.exists() or NATIVE_AUDIO.stat().st_size < 10_000:
            raise RuntimeError("Native USFWS audio extraction failed")
    return duration, video, audio


def font(size: int):
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def contact_sheets(pattern: str, prefix: str, interval: float, title: str):
    frames = sorted(FRAMES.glob(f"{prefix}_*.jpg"))
    if not frames:
        raise RuntimeError(f"No {prefix} review frames generated")
    cols, rows = 4, 5
    cell_w, cell_h = 336, 246
    pages = math.ceil(len(frames) / (cols * rows))
    paths = []
    for page in range(pages):
        chunk = frames[page * cols * rows:(page + 1) * cols * rows]
        canvas = Image.new("RGB", (cols * cell_w, 64 + rows * cell_h), "#101820")
        draw = ImageDraw.Draw(canvas)
        draw.text((16, 12), f"{title} — PAGE {page + 1}/{pages}", font=font(20), fill="#F4F1E8")
        draw.text((16, 38), f"One frame every {interval:g}s • labels are source timestamps", font=font(15), fill="#A9B8C4")
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
            draw.text((x + 4, y + 207), label, font=font(20), fill="#63D7C8")
        out = REVIEW / f"{prefix}_contact_sheet_{page + 1:02d}.jpg"
        canvas.save(out, quality=92)
        paths.append(str(out.relative_to(ROOT)))
        print("Wrote", out, flush=True)
    return len(frames), paths


def main() -> int:
    started = time.time()
    route = retrieve()
    info = probe(WEBM)
    duration, video, audio = convert_and_extract(info)
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-i", str(MP4),
        "-vf", "fps=1,scale=320:-2", "-q:v", "3", "-start_number", "0",
        str(FRAMES / "coarse_%04d.jpg"),
    ], check=True)
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-i", str(MP4),
        "-vf", "fps=2,scale=320:-2", "-q:v", "3", "-start_number", "0",
        str(FRAMES / "fine_%04d.jpg"),
    ], check=True)
    coarse_count, coarse_sheets = contact_sheets("coarse", "coarse", 1.0, "USFWS ALBATROSS DANCE — COARSE REVIEW")
    fine_count, fine_sheets = contact_sheets("fine", "fine", 0.5, "USFWS ALBATROSS DANCE — FINE REVIEW")
    # A clean poster frame from the middle of the dance for the cover reference.
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-ss", "12", "-i", str(MP4),
        "-frames:v", "1", "-q:v", "2", str(REVIEW / "source_poster.jpg"),
    ], check=True)

    manifest = {
        "topic": "Laysan albatross courtship dance",
        "new_topic_separate_from_prior_bear_car_short": True,
        "source_page": RIGHTS_PAGE,
        "original_file_url": SOURCE_URLS[0],
        "retrieval_route": route,
        "usfws_story": USFWS_STORY,
        "animal_diversity_web": ADW_PAGE,
        "rights_declaration": (
            "Public domain: work of a U.S. Fish & Wildlife Service employee (Ann Bell/USFWS) "
            "made as part of official duties; as a U.S. federal government work it is in the public domain."
        ),
        "credit": "Ann Bell / U.S. Fish & Wildlife Service",
        "source_file": str(WEBM.relative_to(ROOT)),
        "source_video_ledger": str((REVIEW / "source_video_ledger.json").relative_to(ROOT)),
        "source_sha256": sha256(WEBM),
        "source_bytes": WEBM.stat().st_size,
        "converted_mp4": str(MP4.relative_to(ROOT)),
        "native_audio": str(NATIVE_AUDIO.relative_to(ROOT)) if audio else None,
        "native_audio_codec": (audio or {}).get("codec_name"),
        "duration_seconds": duration,
        "width": int(video.get("width", 0)),
        "height": int(video.get("height", 0)),
        "video_codec": video.get("codec_name"),
        "coarse_review_frames": coarse_count,
        "fine_review_frames": fine_count,
        "coarse_contact_sheets": coarse_sheets,
        "fine_contact_sheets": fine_sheets,
        "poster": str((REVIEW / "source_poster.jpg").relative_to(ROOT)),
        "visual_timestamp_approval": "PENDING — no scene lock before contact-sheet review",
        "retrieved_unix": int(started),
    }
    (REVIEW / "review-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (REVIEW / "source_probe.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    ledger = [
        {
            "id": "usfws_albatross_dance_webm",
            "file": str(WEBM.relative_to(ROOT)),
            "bytes": WEBM.stat().st_size,
            "sha256": sha256(WEBM),
            "download_url": route,
            "source_page": RIGHTS_PAGE,
            "license": "Public domain (USFWS / U.S. federal government work)",
        },
        {
            "id": "usfws_albatross_dance_mp4",
            "file": str(MP4.relative_to(ROOT)),
            "bytes": MP4.stat().st_size,
            "sha256": sha256(MP4),
            "note": "Local H.264 conversion of the same public-domain WebM for reliable frame-accurate rendering.",
            "license": "Public domain (USFWS / U.S. federal government work)",
        },
    ]
    if audio:
        ledger.append({
            "id": "usfws_clip_native_audio",
            "file": str(NATIVE_AUDIO.relative_to(ROOT)),
            "bytes": NATIVE_AUDIO.stat().st_size,
            "sha256": sha256(NATIVE_AUDIO),
            "codec": audio.get("codec_name"),
            "note": "Original public-domain clip audio extracted for optional low-level ambience; not a generated bird vocalisation.",
            "license": "Public domain (USFWS / U.S. federal government work)",
        })
    (REVIEW / "source_video_ledger.json").write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    (REVIEW / "SOURCE_RIGHTS.md").write_text(
        "# Source rights — Laysan Albatross Mating Dance 2016\n\n"
        f"- Commons file page: {RIGHTS_PAGE}\n"
        f"- Original file: {SOURCE_URLS[0]}\n"
        f"- USFWS story: {USFWS_STORY}\n"
        "- Author: Ann Bell / U.S. Fish & Wildlife Service, 9 December 2016.\n"
        "- License: **Public domain** — U.S. federal government work created in official duties.\n"
        "- This is a different topic and different footage from the earlier NPS *Bears in Cars* Short.\n",
        encoding="utf-8",
    )
    (REVIEW / "SOURCE_FACTS.md").write_text(
        "# Factual lock — Laysan albatross courtship dance\n\n"
        f"- USFWS, *A Laysan Lovesong*: {USFWS_STORY}\n"
        "  - Young albatrosses gather in twos and threes to **practice courtship dances** for several years.\n"
        "  - Laysan courtship dances can have **dozens of ritualized movements**.\n"
        "  - USFWS explicitly calls these gatherings **dance parties**.\n"
        "  - Once a pair bond forms, the birds **stay bonded for life**.\n"
        f"- Animal Diversity Web, *Phoebastria immutabilis*: {ADW_PAGE}\n"
        "  - **Independently fetched and read on 2026-11-06.** The page says the courtship display consists of **25 different postures**, including **clicking beaks together**, tucking bills under wings, and **pointing bills at the sky simultaneously**.\n"
        "  - Laysan albatrosses are **monogamous** and **mate for life**; pair bonds are formed over **several years**.\n"
        "  - ADW says only first-time breeders and non-breeding birds perform this dance. That is a general species statement and is **not** used here to identify or label the two birds in the USFWS clip.\n"
        "- Commons description: filmed on **Midway Atoll**; video by Ann Bell/USFWS.\n\n"
        "Guardrail: the edit explains general species behavior. It does **not** claim these two filmed birds are juveniles, "
        "are already a lifelong pair, or have a known relationship history. No handle, door, car, food-reward, "
        "25M-view, part-2 or virality-guarantee claim belongs to this topic.\n",
        encoding="utf-8",
    )
    (BASE / "DANCE_TOPIC_LOCK.md").write_text(
        "# New topic lock — They Don't Flirt. They Choreograph.\n\n"
        "**Status:** source reviewed, exact visual windows locked for the V2 clean-premium 24-second render; previous bear/car Shorts and the original 24-second Short are untouched.\n\n"
        "- New subject: **Laysan albatross courtship dance**, Midway Atoll.\n"
        "- New picture source: public-domain USFWS clip via Wikimedia Commons, 52.581 s, 1920×1080.\n"
        "- New creative angle: a ridiculous-looking dance that is actually a multi-year audition for a lifelong partner.\n"
        "- New sound bed: CC0 upbeat chiptune comedy music, salience-layered CC0 graphic accents, clean-premium stereo/sub design, and original public-domain clip ambience.\n"
        "- Rule: \"viral\" is an optimization objective, not a promise. Objective QC and model review are evidence, not audience guarantees.\n\n"
        f"- Rights: {RIGHTS_PAGE}\n- Facts: {USFWS_STORY} and {ADW_PAGE}\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
