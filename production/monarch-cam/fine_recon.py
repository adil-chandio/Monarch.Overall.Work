#!/usr/bin/env python3
"""Build fine-grained visual reviews around candidate NPS opening/action shots."""
from __future__ import annotations

import json
import math
from pathlib import Path
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "work/recon/media/nps_bears_in_cars.mp4"
OUT = ROOT / "review"
RANGES = [
    {"name": "opening", "start": 0, "end": 40, "step": 1},
    {"name": "later_action", "start": 260, "end": 366, "step": 2},
]
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def make_range(spec: dict) -> list[str]:
    work = ROOT / "work" / f"fine_{spec['name']}"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning",
        "-ss", str(spec["start"]), "-t", str(spec["end"] - spec["start"]),
        "-i", str(SOURCE), "-vf", f"fps=1/{spec['step']},scale=440:-2",
        "-q:v", "2", str(work / "frame_%04d.jpg"),
    ])
    frames = sorted(work.glob("frame_*.jpg"))
    font = ImageFont.truetype(FONT_PATH, 19)
    small = ImageFont.truetype(FONT_PATH, 14)
    cols, rows = 4, 5
    cell_w, cell_h = 456, 310
    outputs: list[str] = []
    pages = math.ceil(len(frames) / (cols * rows))
    for page in range(pages):
        chunk = frames[page * cols * rows:(page + 1) * cols * rows]
        canvas = Image.new("RGB", (cols * cell_w, 64 + rows * cell_h), "#101419")
        draw = ImageDraw.Draw(canvas)
        title = f"NPS FINE REVIEW — {spec['name'].upper()} — PAGE {page + 1}/{pages}"
        draw.text((14, 12), title, font=font, fill="#F4F1E8")
        draw.text((14, 40), f"Source {spec['start']}–{spec['end']}s • one frame every {spec['step']}s", font=small, fill="#A9B4BF")
        for index, frame_path in enumerate(chunk):
            frame_no = page * cols * rows + index
            timestamp = spec["start"] + frame_no * spec["step"]
            image = Image.open(frame_path).convert("RGB")
            image.thumbnail((440, 264), Image.Resampling.LANCZOS)
            x = (index % cols) * cell_w + 8
            y = 64 + (index // cols) * cell_h
            tile = Image.new("RGB", (440, 264), "#050607")
            tile.paste(image, ((440 - image.width) // 2, (264 - image.height) // 2))
            canvas.paste(tile, (x, y))
            draw.text((x + 4, y + 270), f"{timestamp // 60:02d}:{timestamp % 60:02d}", font=font, fill="#F2C14E")
        name = f"fine_{spec['name']}_{page + 1:02d}.jpg"
        canvas.save(OUT / name, quality=94)
        outputs.append(name)
    return outputs


def main() -> int:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    OUT.mkdir(parents=True, exist_ok=True)
    outputs: list[str] = []
    for spec in RANGES:
        outputs.extend(make_range(spec))
    # Full-resolution candidate frames for title/thumbnail and text-safe-area review.
    for timestamp in (0, 3, 15, 20, 50, 65, 275, 290, 350, 355):
        run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning",
            "-ss", str(timestamp), "-i", str(SOURCE), "-frames:v", "1", "-q:v", "2",
            str(OUT / f"source_{timestamp:03d}.jpg"),
        ])
    (OUT / "fine-review-files.json").write_text(json.dumps(outputs, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
