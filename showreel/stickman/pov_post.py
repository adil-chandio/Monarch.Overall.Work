"""Lay the words over an already-rendered master, and nothing else.

The film is 2 160 frames at about a second a frame, so a change to the type is not
a reason to render it again. This pass decodes the master, composites the text
layers from ``pov_text``, and encodes the result -- roughly four minutes instead of
forty-five.

    python -m showreel.stickman.pov_post \\
        --src deliverables/monarch-pov-stadium-1080x1920.mp4 \\
        --out deliverables/monarch-pov-stadium-1080x1920.mp4 \\
        --preview deliverables/monarch-pov-stadium-preview.mp4

Two encodes, never three: the master is re-encoded once from the render, and the
preview is made from the texted master in the same run. Both are piped, so a
frame never exists as a file.
"""

from __future__ import annotations

import argparse
import math
import os
import subprocess
import sys

import imageio_ffmpeg
import numpy as np
from PIL import Image

from . import pov_text
from .film import FPS, H, W

# The replay is a replay: shot through a broadcast, so it loses a little colour and
# the corners come in. 49.0-58.0 in the cut.
REPLAY = (49.0, 58.0)
_VIG = None


def _vignette():
    """A radial falloff, built once. Cheap enough to apply per frame."""
    global _VIG
    if _VIG is None:
        y = np.linspace(-1.0, 1.0, H, dtype=np.float32)[:, None]
        x = np.linspace(-1.0, 1.0, W, dtype=np.float32)[None, :]
        r = np.sqrt(x * x + y * y) / math.sqrt(2.0)
        _VIG = (1.0 - 0.30 * r ** 2.0)[..., None]
    return _VIG


def replay_grade(frame):
    g = frame.mean(axis=2, keepdims=True)
    frame = frame * 0.88 + g * 0.12
    return frame * _vignette()

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

BASE = [
    "-hide_banner", "-loglevel", "error", "-y",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-an",
    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
    "-movflags", "+faststart",
]


def decoder(path):
    cmd = [FFMPEG, "-v", "error", "-i", path, "-f", "rawvideo",
           "-pix_fmt", "rgb24", "-"]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=W * H * 3 * 2)


def encoder(path, crf, preset, scale=None):
    vf = [] if scale is None else ["-vf", f"scale={scale[0]}:{scale[1]}:flags=lanczos"]
    cmd = [FFMPEG] + BASE + vf + [
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
        "-pix_fmt", "yuv420p", "-profile:v", "high", path]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE, bufsize=W * H * 3 * 2)


def texted(src, out, crf=20, preset="medium", limit=None, quiet=False):
    proc_a = decoder(src)
    proc_b = encoder(out, crf, preset)
    n = W * H * 3
    i = 0
    step = max(1, (limit or 2160) // 12)
    while True:
        if limit is not None and i >= limit:
            break
        buf = proc_a.stdout.read(n)
        if len(buf) < n:
            break
        frame = Image.frombytes("RGB", (W, H), buf)
        t = i / FPS
        if REPLAY[0] <= t < REPLAY[1]:
            frame = Image.fromarray(
                (np.clip(replay_grade(np.asarray(frame, np.float32) / 255.0),
                         0.0, 1.0) * 255).astype(np.uint8))
        if pov_text.active(t):
            frame = pov_text.overlay(frame, t)
        proc_b.stdin.write(frame.tobytes())
        i += 1
        if not quiet and i % step == 0:
            print(f"    {i:5d}/{limit or 2160}  {t:5.1f}s  frame", flush=True)
    proc_a.stdout.close()
    proc_a.wait()
    proc_b.stdin.close()
    proc_b.wait()
    return i


def shrink(src, out, w, h, crf=27, preset="medium"):
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", src,
           "-vf", f"scale={w}:{h}:flags=lanczos",
           "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-profile:v", "high",
           "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
           "-movflags", "+faststart", "-an", out]
    subprocess.run(cmd, check=True)


def mux(video, audio, out, loudness=-15.0):
    """Put the mix on the picture without touching a single video frame."""
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
           "-i", video, "-i", audio,
           "-map", "0:v:0", "-map", "1:a:0",
           "-c:v", "copy",
           "-af", f"loudnorm=I={loudness}:TP=-1.5:LRA=11",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-shortest", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pov_post")
    ap.add_argument("--src", required=True, help="rendered master, no text")
    ap.add_argument("--out", required=True, help="texted master")
    ap.add_argument("--preview", default=None, help="half-res mp4 from the texted master")
    ap.add_argument("--crf", type=float, default=20.0)
    ap.add_argument("--preset", default="medium")
    ap.add_argument("--limit", type=int, default=None, help="encode only N frames")
    ap.add_argument("--audio", default=None, help="wav mix to lay under the picture")
    a = ap.parse_args(argv)

    tmp = a.out + ".part.mp4"
    n = texted(a.src, tmp, a.crf, a.preset, a.limit)
    if a.audio:
        mux(tmp, a.audio, a.out)
        os.remove(tmp)
    else:
        os.replace(tmp, a.out)
    print(f"wrote {a.out}  ({n} frames, {n / FPS:.2f} s, "
          f"{os.path.getsize(a.out) / 1e6:.1f} MB)", flush=True)

    if a.preview:
        shrink(a.out, a.preview, W // 2, H // 2)
        print(f"wrote {a.preview}  ({os.path.getsize(a.preview) / 1e6:.1f} MB)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
