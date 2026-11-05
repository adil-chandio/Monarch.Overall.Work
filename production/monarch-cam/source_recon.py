#!/usr/bin/env python3
"""Retrieve the explicit public-domain NPS bear/car asset and build review contact sheets.

The sandbox cannot reach NPS directly, so this script also runs in the reproducible
GitHub Actions source-recon job. It never selects footage by title alone: the contact
sheets are for visual shot verification before the 30-second edit.
"""
from __future__ import annotations

import html
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time

import requests
from PIL import Image, ImageDraw, ImageFont

NPS_URL = "https://www.nps.gov/media/video/view.htm?id=07B1F1A5-E8DC-0BCE-DAFAE3F9B356AA73"
MIRROR_URL = "https://www.youtube.com/watch?v=6blQ31cJ25k"
OUT = Path(os.environ.get("RECON_OUT", "production/monarch-cam/work/recon")).resolve()
MEDIA = OUT / "media"
SHEETS = OUT / "contact-sheets"
FRAMES = OUT / "frames"
for directory in (OUT, MEDIA, SHEETS, FRAMES):
    directory.mkdir(parents=True, exist_ok=True)


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, text=True, **kwargs)


def media_urls(text: str) -> list[str]:
    decoded = html.unescape(text).replace("\\/", "/")
    candidates = re.findall(r"https?://[^\s\"'<>\\]+", decoded)
    answer: list[str] = []
    for url in candidates:
        url = url.rstrip("),;]")
        if any(token in url.lower() for token in (".mp4", ".m3u8", ".webm")):
            if url not in answer:
                answer.append(url)
    return answer


def retrieve() -> tuple[Path, str]:
    headers = {"User-Agent": "MonarchCamResearch/1.0 (+public-domain NPS media review)"}
    response = requests.get(NPS_URL, headers=headers, timeout=60)
    response.raise_for_status()
    (OUT / "nps-source-page.html").write_bytes(response.content)
    urls = media_urls(response.text)
    (OUT / "detected-media-urls.json").write_text(json.dumps(urls, indent=2), encoding="utf-8")
    print("Detected media URLs:", json.dumps(urls, indent=2), flush=True)

    expected = MEDIA / "nps_bears_in_cars.mp4"
    direct: list[Path] = []
    route = ""

    # Prefer the highest explicitly advertised NPS rendition. yt-dlp's generic page
    # extraction otherwise chooses 640x360 even when the 854x480 master is present.
    ordered = sorted(
        urls,
        key=lambda u: ("854x480" not in u, "AD_" in u, ".mp4" not in u.lower(), len(u)),
    )
    for index, url in enumerate(ordered):
        candidate = MEDIA / f"nps_url_{index}.mp4"
        got = run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning",
            "-i", url, "-c", "copy", str(candidate),
        ])
        if got.returncode == 0 and candidate.exists() and candidate.stat().st_size > 100_000:
            direct = [candidate]
            route = url
            break

    if not direct:
        template = str(MEDIA / "nps_direct.%(ext)s")
        run([
            sys.executable, "-m", "yt_dlp", "--no-playlist", "--no-part",
            "-f", "best[height<=480]/best", "--merge-output-format", "mp4",
            "-o", template, NPS_URL,
        ])
        direct = sorted(
            p for p in MEDIA.glob("nps_direct.*")
            if p.suffix.lower() in {".mp4", ".webm", ".mkv", ".mov"} and p.stat().st_size > 100_000
        )
        route = "NPS direct page"
    if not direct:
        # Last-resort retrieval of the same 7:04 public-domain NPS compilation. The mirror's
        # own branding/intro/outro is not approved for the edit; visual review must isolate
        # the underlying NPS footage. The NPS source/rights page is archived separately.
        route = "Public-domain NPS compilation mirror; NPS-only interior shots required"
        run([
            sys.executable, "-m", "yt_dlp", "--no-playlist", "--no-part",
            "-f", "bv*[height<=480]+ba/b[height<=480]/best[height<=480]/best",
            "--merge-output-format", "mp4", "-o", str(expected), MIRROR_URL,
        ], check=True)
        direct = [expected]
    if not direct:
        raise RuntimeError("No usable NPS media file was retrieved")

    source = direct[0]
    if source.suffix.lower() == ".mp4":
        if source != expected:
            source.replace(expected)
            source = expected
    else:
        converted = expected
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-i", str(source),
             "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-c:a", "aac", "-b:a", "160k",
             str(converted)], check=True)
        source = converted
    (OUT / "retrieval-route.txt").write_text(route + "\n", encoding="utf-8")
    return source, route


def probe(source: Path) -> dict:
    proc = run([
        "ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(source),
    ], capture_output=True, check=True)
    data = json.loads(proc.stdout)
    (OUT / "source-probe.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def contact_sheets(source: Path, duration: float) -> int:
    # One frame every five seconds; pages cover two minutes each and stay visually readable.
    pattern = str(FRAMES / "frame_%04d.jpg")
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning", "-i", str(source),
        "-vf", "fps=1/5,scale=320:-2", "-q:v", "3", pattern,
    ], check=True)
    frames = sorted(FRAMES.glob("frame_*.jpg"))
    if not frames:
        raise RuntimeError("No review frames generated")
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, 20)
    small = ImageFont.truetype(font_path, 15)
    cols, rows = 4, 6
    cell_w, cell_h = 336, 246
    pages = math.ceil(len(frames) / (cols * rows))
    for page in range(pages):
        chunk = frames[page * cols * rows:(page + 1) * cols * rows]
        canvas = Image.new("RGB", (cols * cell_w, 64 + rows * cell_h), "#101419")
        draw = ImageDraw.Draw(canvas)
        draw.text((16, 13), f"NPS BEARS IN CARS — REVIEW PAGE {page + 1}/{pages}", font=font, fill="#F4F1E8")
        draw.text((16, 40), "One frame every 5 seconds • labels are approximate source timestamps", font=small, fill="#A9B4BF")
        for index, frame_path in enumerate(chunk):
            frame_no = page * cols * rows + index
            timestamp = frame_no * 5
            image = Image.open(frame_path).convert("RGB")
            image.thumbnail((320, 202), Image.Resampling.LANCZOS)
            x = (index % cols) * cell_w + 8
            y = 64 + (index // cols) * cell_h
            tile = Image.new("RGB", (320, 202), "#050607")
            tile.paste(image, ((320 - image.width) // 2, (202 - image.height) // 2))
            canvas.paste(tile, (x, y))
            draw.text((x + 4, y + 207), f"{timestamp // 60:02d}:{timestamp % 60:02d}", font=font, fill="#F2C14E")
        out = SHEETS / f"review_{page + 1:02d}.jpg"
        canvas.save(out, quality=93)
        print("Wrote", out, flush=True)
    return len(frames)


def main() -> int:
    started = time.time()
    source, route = retrieve()
    info = probe(source)
    duration = float(info.get("format", {}).get("duration", 0.0))
    if not 400 <= duration <= 450:
        raise RuntimeError(f"Unexpected source duration {duration:.3f}s; refusing blind edit")
    count = contact_sheets(source, duration)
    metadata = {
        "nps_rights_page": NPS_URL,
        "rights_declaration": "Stock footage of bears in cars in Yosemite National Park. All footage is in the public domain and may be used for any purpose.",
        "credit": "National Park Service",
        "retrieval_route": route,
        "source_file": source.name,
        "duration_seconds": duration,
        "review_frames": count,
        "review_interval_seconds": 5,
        "visual_timestamp_approval": "PENDING — no opening/title lock before frame review",
        "retrieved_unix": int(started),
    }
    (OUT / "review-manifest.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
