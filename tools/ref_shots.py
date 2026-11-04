#!/usr/bin/env python3
"""Per-shot contact cards: one frame at the midpoint of every shot.

`analyse_ref.py` answers "where are the cuts and what do they look like". This
answers the next question a rebuild needs: *what exactly is on screen in each
shot, and for how long* — so a shot list can be written straight off the image.

Usage:
    python3 tools/ref_shots.py <video> --analysis analysis/<name> [--cols 4]

Writes `<analysis>/shots.png` (+ `shots.json` with the shot list) and prints a
markdown shot table.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Any

from PIL import Image, ImageDraw, ImageFont

CARD_W = 300


def ffmpeg_bin() -> str:
    """System ffmpeg if present, else the static build bundled with imageio."""
    forced = os.environ.get("FFMPEG_BIN")
    if forced:
        return forced
    from shutil import which

    found = which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # pragma: no cover - last resort
        return "ffmpeg"


def ffprobe_bin() -> str:
    from shutil import which

    found = which("ffprobe")
    if found:
        return found
    return ""  # static build has no ffprobe; probe() falls back to ffmpeg


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(" ".join(cmd) + "\n" + proc.stderr[-2000:] + "\n")
        raise SystemExit(f"command failed: {cmd[0]}")


def probe(path: str) -> dict[str, Any]:
    probe_bin = ffprobe_bin()
    if probe_bin:
        out = subprocess.run(
            [probe_bin, "-v", "error", "-print_format", "json",
             "-show_format", "-show_streams", path],
            capture_output=True,
            text=True,
        )
        if out.returncode == 0:
            return json.loads(out.stdout)
        sys.stderr.write(f"ffprobe failed, using ffmpeg: {out.stderr[-400:]}\n")
    # static-ffmpeg fallback: parse "Duration: 00:00:23.35" and the video stream line
    txt = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", path],
                         capture_output=True, text=True).stderr
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", txt)
    if not m:
        raise SystemExit("cannot read duration")
    h, mm, ss = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return {"format": {"duration": h * 3600 + mm * 60 + ss}}


def grab(path: str, t: float, dest: str, width: int) -> bool:
    run(
        [
            ffmpeg_bin(), "-nostdin", "-v", "error", "-y",
            "-ss", f"{max(t, 0.0):.3f}", "-i", path,
            "-frames:v", "1", "-vf", f"scale={width}:-2:flags=lanczos",
            dest,
        ]
    )
    return os.path.exists(dest) and os.path.getsize(dest) > 0


def font(size: int) -> ImageFont.ImageFont:
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ):
        if os.path.exists(candidate):
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def build_shots(report: dict[str, Any], duration: float) -> list[dict[str, Any]]:
    """Turn the cut list into shots with start/end/midpoint."""
    cuts = sorted(float(c["time"]) for c in report.get("cuts", []))
    edges = [0.0] + cuts + [duration]
    shots = []
    for i in range(len(edges) - 1):
        start, end = edges[i], edges[i + 1]
        if end - start < 0.12:  # a transition pair, not a shot
            continue
        shots.append(
            {
                "index": len(shots) + 1,
                "start": round(start, 3),
                "end": round(end, 3),
                "dur": round(end - start, 3),
                "mid": round((start + end) / 2.0, 3),
                "transition_in": next(
                    (c.get("transition") for c in report.get("cuts", [])
                     if abs(float(c["time"]) - start) < 0.05),
                    "—" if i == 0 else "cut",
                ),
            }
        )
    return shots


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--analysis", required=True, help="dir holding report.json")
    ap.add_argument("--cols", type=int, default=4)
    args = ap.parse_args()

    report_path = os.path.join(args.analysis, "report.json")
    with open(report_path) as fh:
        report = json.load(fh)

    info = probe(args.video)
    duration = float(info["format"]["duration"])
    shots = build_shots(report, duration)

    tmp = os.path.join(args.analysis, "_shots")
    os.makedirs(tmp, exist_ok=True)
    cards = []
    for shot in shots:
        dest = os.path.join(tmp, f"shot_{shot['index']:02d}.png")
        if not grab(args.video, shot["mid"], dest, CARD_W):
            continue
        shot["card"] = os.path.basename(dest)
        cards.append((shot, Image.open(dest).convert("RGB")))

    if not cards:
        raise SystemExit("no frames grabbed")

    cw, ch = cards[0][1].size
    pad, label_h = 10, 52
    cols = max(1, min(args.cols, len(cards)))
    rows = (len(cards) + cols - 1) // cols
    W = cols * (cw + pad) + pad
    H = rows * (ch + label_h + pad) + pad
    sheet = Image.new("RGB", (W, H), (16, 16, 18))
    draw = ImageDraw.Draw(sheet)
    small, big = font(15), font(21)

    for i, (shot, img) in enumerate(cards):
        cx = pad + (i % cols) * (cw + pad)
        cy = pad + (i // cols) * (ch + label_h + pad)
        sheet.paste(img, (cx, cy))
        draw.rectangle([cx, cy + ch, cx + cw, cy + ch + label_h], fill=(16, 16, 18))
        draw.text((cx + 2, cy + ch + 4), f"{shot['index']:02d}  {shot['start']:05.2f}s", font=big, fill=(255, 255, 255))
        draw.text(
            (cx + 2, cy + ch + 30),
            f"hold {shot['dur']:.2f}s · in: {shot['transition_in']}",
            font=small,
            fill=(160, 165, 175),
        )

    out_png = os.path.join(args.analysis, "shots.png")
    sheet.save(out_png, optimize=True)
    with open(os.path.join(args.analysis, "shots.json"), "w") as fh:
        json.dump(shots, fh, indent=2)

    print(f"shots: {len(shots)}  →  {out_png}\n")
    print("| # | start | hold | in |")
    print("|---|---|---|---|")
    for shot in shots:
        print(f"| {shot['index']} | {shot['start']:.2f}s | {shot['dur']:.2f}s | {shot['transition_in']} |")


if __name__ == "__main__":
    main()
