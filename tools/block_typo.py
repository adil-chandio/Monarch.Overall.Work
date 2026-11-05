#!/usr/bin/env python3
"""Render 0.00-0.80 s from the measured table: a plate, a font, and 24 rows of numbers.

Every parameter comes from tools/build_typo_table.py, which measures the reference
once. This file never opens the reference; it only draws.

    python3 tools/block_typo.py --out public/demo/block-typo.mp4
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import typo_core as core
from ffbin import ffmpeg


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default="spec/typo-block.json")
    ap.add_argument("--out", default="public/demo/block-typo.mp4")
    ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args()

    spec = core.load(a.spec)
    rows = spec["frames"]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    enc = subprocess.Popen([ffmpeg(), "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{core.W}x{core.H}", "-r", str(a.fps), "-i", "-",
                            "-c:v", "libx264", "-crf", "15", "-preset", "slow",
                            "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out],
                           stdin=subprocess.PIPE)
    for p in rows:
        rgb = core.render(p)
        enc.stdin.write(rgb[..., ::-1].tobytes())          # RGB -> BGR for x264's yuv420
    enc.stdin.close()
    enc.wait()
    print(f"  {len(rows)} frames -> {a.out} ({Path(a.out).stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
