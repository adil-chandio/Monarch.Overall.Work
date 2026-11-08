#!/usr/bin/env python3
"""Make frame 0 of a render the frame the composition actually authored.

The headless renderer captures frame 0 before the browser has composited the CSS
background plates, so the first frame of the master came out pure black (mean
0,0,0) while every measurement — which starts at 0.03 s — looked fine. Rather
than paper over it in the encode, the frame is rebuilt from the same composition
by rendering frame 1's time and then shifting the cut by one frame is wrong too:
frame 0 must be t=0, not t=1/30.

So: extract what the composition shows at t=0 from frames 1..3 is not possible
either. The honest fix is at the source (a warm-up pass in the renderer); this
script is the verification that it worked, plus a hard failure if it did not.

Usage:
    python3 tools/force_first_frame.py public/demo/v4.mp4
"""

from __future__ import annotations

import json
import subprocess
import sys

import numpy as np


def ffmpeg() -> str:
    import shutil

    return shutil.which("ffmpeg") or __import__("imageio_ffmpeg").get_ffmpeg_exe()


def first_frames(path: str, n: int = 3) -> np.ndarray:
    w, h = 90, 160
    raw = subprocess.run(
        [ffmpeg(), "-nostdin", "-v", "error", "-i", path,
         "-frames:v", str(n), "-vf", f"scale={w}:-2", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True,
    ).stdout
    return np.frombuffer(raw[: n * 3 * w * h], np.uint8).reshape(n, h, w, 3).astype(float)


def main() -> None:
    path = sys.argv[1]
    fr = first_frames(path)
    means = [float(f.reshape(-1, 3).mean()) for f in fr]
    print("first frames mean luma:", [round(m, 1) for m in means])
    if means[0] < 2.0:
        print("FAIL: frame 0 is black — the renderer's warm pass did not take")
        sys.exit(1)
    print("PASS: frame 0 is authored")
    json.dump({"first_frame_means": means}, sys.stdout)


if __name__ == "__main__":
    main()
