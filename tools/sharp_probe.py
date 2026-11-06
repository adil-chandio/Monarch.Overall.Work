"""Measure what the browser did to a plate, compared with the plate itself.

The plates are the reference's own frames, so their detail is not negotiable. This
compares a source image against the frame the renderer produced from it, over a
region with fine detail, and reports the ratio.

Two numbers came out of this question already and they disagreed with the guess:
the same PNG through the same x264 settings came back at 307.7/307.7 (the encode is
lossless), while the frame the browser screenshotted measured 136 (it is not). This
tool exists so that the browser half can be measured on its own and in one run,
instead of through a full checkpoint cycle.

Pure Python on a raw grey buffer — no numpy, because every dependency this job has
cost it a run.

  python3 tools/sharp_probe.py --a plate.png --b frame.png [--box 300,760,620,1120]
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ffbin import ffmpeg

W, H = 720, 1280


def grey(path: str) -> bytes:
    return subprocess.run([ffmpeg(), "-v", "error", "-i", path, "-vf", f"scale={W}:{H}",
                           "-pix_fmt", "gray", "-f", "rawvideo", "-"],
                          capture_output=True).stdout


def acutance(raw: bytes, x0: int, y0: int, x1: int, y1: int) -> float:
    """Variance of the 4-neighbour Laplacian over a crop — the usual sharpness proxy."""
    total, total_sq, n = 0.0, 0.0, 0
    for y in range(max(1, y0), min(H - 1, y1)):
        row, up, down = y * W, (y - 1) * W, (y + 1) * W
        for x in range(max(1, x0), min(W - 1, x1)):
            v = 4 * raw[row + x] - raw[row + x - 1] - raw[row + x + 1] - raw[up + x] - raw[down + x]
            total += v
            total_sq += v * v
            n += 1
    if not n:
        return 0.0
    mean = total / n
    return total_sq / n - mean * mean


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="the source image")
    ap.add_argument("--b", required=True, help="the frame produced from it")
    ap.add_argument("--box", default="300,760,620,1120", help="x0,y0,x1,y1")
    ap.add_argument("--min-ratio", type=float, default=0.85)
    args = ap.parse_args()

    x0, y0, x1, y1 = (int(v) for v in args.box.split(","))
    a, b = grey(args.a), grey(args.b)
    if min(len(a), len(b)) < W * H:
        print(f"SHARPNESS PROBE: cannot read one of the images ({len(a)}/{len(b)} bytes)")
        return 1
    va, vb = acutance(a, x0, y0, x1, y1), acutance(b, x0, y0, x1, y1)
    ratio = vb / va if va else 0.0
    print(f"  source {Path(args.a).name:28s} acutance {va:8.1f}")
    print(f"  frame  {Path(args.b).name:28s} acutance {vb:8.1f}   ratio {ratio:.2f}")
    if ratio < args.min_ratio:
        print(f"SHARPNESS PROBE: FAIL — the render kept only {ratio * 100:.0f} % of the plate's detail")
        return 1
    print("SHARPNESS PROBE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
