"""Render the stickman cut and encode it.

Frames are never held in memory: a generator yields one finished frame at a time
and ffmpeg consumes it on stdin. A full-length 1080x1920 cut in RAM is what
killed the previous render, and there is no version of this that needs to.

    python -m showreel.stickman.render_film [--out PATH] [--preview]
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

import numpy as np

from .film import FPS, H, W, Performer, build_shots
from .render import render_time
from .stage import World


def ffmpeg_exe():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def frames(shots, perf, world, *, scale=1.0):
    """Yield every frame of the film as raw RGB bytes."""
    total = sum(s.duration for s in shots)
    n = int(round(total * FPS))
    for i in range(n):
        t = i / FPS
        frame = render_time(shots, perf, world, t)
        if scale != 1.0:
            from PIL import Image
            h = int(round(H * scale))
            w = int(round(W * scale))
            img = Image.fromarray((np.clip(frame, 0, 1) * 255).astype(np.uint8))
            frame = np.asarray(img.resize((w, h), Image.LANCZOS), np.float32) / 255.0
        yield (np.clip(frame, 0, 1) * 255.0).astype(np.uint8).tobytes()


def render(out_path, *, preview=False, crf=None, preset="medium"):
    perf = Performer()
    shots = build_shots(perf)
    world = World("paper", seed=5)

    scale = 0.5 if preview else 1.0
    w = int(W * scale)
    h = int(H * scale)
    crf = crf if crf is not None else (27 if preview else 19)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    cmd = [
        ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-",
        "-an",
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
        "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-movflags", "+faststart",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        out_path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE)
    total = sum(s.duration for s in shots)
    n_total = int(round(total * FPS))
    step = max(1, n_total // 20)
    try:
        for i, buf in enumerate(frames(shots, perf, world, scale=scale)):
            proc.stdin.write(buf)
            if i % step == 0:
                print(f"  {i:4d}/{n_total} frames", flush=True)
    finally:
        proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "replace")
        code = proc.wait()
    if code != 0:
        raise SystemExit(f"ffmpeg failed ({code}):\n{err}")
    return out_path, n_total


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="deliverables/monarch-stickman-1080x1920.mp4")
    ap.add_argument("--preview", action="store_true")
    args = ap.parse_args(argv)
    out, n = render(args.out, preview=args.preview)
    print(f"wrote {out}  ({n} frames, {n / FPS:.2f} s)")


if __name__ == "__main__":
    main()
