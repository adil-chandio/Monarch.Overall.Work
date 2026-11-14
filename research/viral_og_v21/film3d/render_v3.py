#!/usr/bin/env python3
"""Render the 60 s bear cut, v3, as real 3D frames.

Two segments in parallel (this box has 2 cores), each piped straight into x264.
Usage:  python3 render_v3.py <t0> <t1> <W> <out.mp4>
"""
import sys, os, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import render_clip as RC
import film1min as F

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
FPS = 24


def main():
    t0, t1 = float(sys.argv[1]), float(sys.argv[2])
    W = int(sys.argv[3]) if len(sys.argv) > 3 else 640
    H = W * 9 // 16
    out = sys.argv[4] if len(sys.argv) > 4 else "out/v3_seg.mp4"
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    cave, shots = F.film()
    starts, acc = [], 0.0
    for s in shots:
        starts.append(acc); acc += s.dur
    n = int(round((t1 - t0) * FPS))
    p = subprocess.Popen([FF, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "16",
                          "-pix_fmt", "yuv420p", out],
                         stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t_start = time.time()
    for i in range(n):
        T = t0 + i / FPS
        fr, k, s = RC.build_frame(T, W, H, cave, shots, starts, seed=i)
        p.stdin.write(fr.convert("RGB").tobytes())
        if i % 24 == 0:
            el = time.time() - t_start
            eta = el / (i + 1) * (n - i - 1)
            print(f"[{out}] frame {i}/{n}  {el/(i+1):.2f}s/f  eta {eta/60:.1f} min  shot {s.name}",
                  flush=True)
    p.stdin.close()
    p.wait()
    print(f"[{out}] done in {(time.time()-t_start)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
