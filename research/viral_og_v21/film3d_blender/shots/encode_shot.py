#!/usr/bin/env python3
"""Encode a rendered PNG sequence from the Blender shots into an H.264 mp4.

The shot scripts render stills (PNG) so a render can be resumed or inspected frame
by frame; this turns whatever is on disk into something playable.

    python3 shots/encode_shot.py out/walk_preview_0099.mp4 --fps 8
    python3 shots/encode_shot.py out/bear_walk_10s.mp4 --fps 24 --pattern walk_final_

Notes:
  * --fps is the playback rate, which is NOT the scene rate if you rendered with
    --step: rendering every 3rd frame of a 24 fps scene means each stored frame
    covers 3/24 s, i.e. play the sequence back at 8 fps to keep real time.
  * uses the imageio-ffmpeg binary already present in this image (no apt, no sudo).
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mp4", help="output file (relative to this file's directory is fine)")
    ap.add_argument("--pattern", default="walk_", help="filename prefix, e.g. walk_preview_")
    ap.add_argument("--fps", type=float, default=24.0, help="playback rate of the stored frames")
    ap.add_argument("--dir", default=os.path.join(HERE, "out"), help="where the PNGs live")
    ap.add_argument("--crf", type=int, default=18)
    a = ap.parse_args()

    frames = sorted(glob.glob(os.path.join(a.dir, f"{a.pattern}[0-9][0-9][0-9][0-9].png")))
    if not frames:
        print(f"no frames matching {a.pattern}*.png in {a.dir}", file=sys.stderr)
        return 2
    # render.filepath writes frame numbers with the scene's padding; keep only the
    # contiguous run ending at the last frame so an older partial pass is not mixed in
    nums = [int(re.search(r"(\d{4})\.png$", f).group(1)) for f in frames]
    step = min((b - a2 for a2, b in zip(nums, nums[1:]) if b - a2 > 0), default=1)
    keep = []
    expect = nums[-1]
    for f, n in zip(reversed(frames), reversed(nums)):
        if n != expect:
            break
        keep.append(f)
        expect -= step
    keep.reverse()

    os.makedirs(os.path.dirname(os.path.abspath(a.mp4)) or ".", exist_ok=True)
    tmp = os.path.join(a.dir, "_seq")
    os.makedirs(tmp, exist_ok=True)
    for f in glob.glob(os.path.join(tmp, "*.png")):
        os.unlink(f)
    for i, f in enumerate(keep):
        os.link(os.path.abspath(f), os.path.join(tmp, f"{i:05d}.png"))

    cmd = [FF, "-y", "-framerate", str(a.fps), "-i", os.path.join(tmp, "%05d.png"),
           "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264",
           "-pix_fmt", "yuv420p", "-crf", str(a.crf), "-movflags", "+faststart", a.mp4]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:], file=sys.stderr)
        return r.returncode
    dur = len(keep) / a.fps
    print(f"wrote {a.mp4}  frames={len(keep)}  fps={a.fps}  dur={dur:.2f}s  "
          f"bytes={os.path.getsize(a.mp4)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
