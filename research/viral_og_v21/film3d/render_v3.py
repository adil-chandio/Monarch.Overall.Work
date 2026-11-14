#!/usr/bin/env python3
"""Render the 60 s bear cut, v3, as real 3D frames — one file per shot, resumable.

Usage:
    python3 render_v3.py            # render every shot that is missing, then concat
    python3 render_v3.py --concat   # only concat + mux audio from what exists

Each shot goes to out/v3/seg_<name>.mp4. If a shot file already exists it is
skipped, so a crash or a kill only costs the shot that was running.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np                      # noqa: E402
import render_clip as RC                # noqa: E402
import film1min as F                    # noqa: E402

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
FPS = 24
W, H = 640, 360
# The cave tube is marched at 60% and bilinearly upsampled. Measured: ~5 s/frame
# instead of ~11 s/frame, with no visible difference at this delivery size.
SET_SCALE = 0.60
OUT = os.path.join(HERE, "out", "v3")
AUDIO = os.path.join(HERE, "out", "mix60.wav")
MASTER = os.path.join(OUT, "EP01_BEAR_1min_3D_v3_640x360_MASTER.mp4")


def shots_with_starts():
    cave, shots = F.film()
    starts, acc = [], 0.0
    for s in shots:
        starts.append(acc)
        acc += s.dur
    return cave, shots, starts


def render_shot(cave, shots, starts, k):
    s = shots[k]
    t0 = starts[k]
    path = os.path.join(OUT, f"seg_{s.name}.mp4")
    part = path + ".part"          # only a finished shot gets its real name
    n = int(round(s.dur * FPS))
    p = subprocess.Popen([FF, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "16",
                          "-pix_fmt", "yuv420p", "-f", "mp4", part],
                         stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    t_start = time.time()
    for i in range(n):
        T = t0 + i / FPS
        fr, _, _ = RC.build_frame(T, W, H, cave, shots, starts, seed=i, set_scale=SET_SCALE)
        p.stdin.write(fr.convert("RGB").tobytes())
        if i % 12 == 0:
            el = time.time() - t_start
            print(f"{s.name} frame {i}/{n}  {el / (i + 1):.2f}s/f  "
                  f"eta {(el / (i + 1)) * (n - i - 1) / 60:.1f} min", flush=True)
    p.stdin.close()
    err = p.stderr.read().decode("utf-8", "replace")
    if p.wait() != 0:
        print(f"{s.name}: ffmpeg failed\n{err[-2000:]}", flush=True)
        return
    os.replace(part, path)
    print(f"{s.name} done in {(time.time() - t_start) / 60:.1f} min -> {path}", flush=True)


def concat():
    parts = [os.path.join(OUT, f"seg_{s.name}.mp4") for s in shots_with_starts()[1]]
    missing = [p for p in parts if not os.path.exists(p)]
    if missing:
        print("missing shots, not concatenating:", missing)
        return None
    lst = os.path.join(OUT, "concat_v3.txt")
    with open(lst, "w") as f:
        for p in parts:
            f.write(f"file '{os.path.basename(p)}'\n")
    video = os.path.join(OUT, "v3_video_only.mp4")
    subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", video], check=True)
    subprocess.run([FF, "-y", "-i", video, "-i", AUDIO,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", MASTER], check=True)
    print("master ->", MASTER, flush=True)
    return MASTER


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--concat" not in sys.argv:
        cave, shots, starts = shots_with_starts()
        for k, s in enumerate(shots):
            path = os.path.join(OUT, f"seg_{s.name}.mp4")
            if os.path.exists(path) and os.path.getsize(path) > 50000:
                print(f"{s.name}: already rendered, skipping", flush=True)
                continue
            render_shot(cave, shots, starts, k)
    concat()


if __name__ == "__main__":
    main()
