"""Render [t0, t1) straight into an H.264 segment.

Usage: python3 render_part.py t0 t1 out.mp4
Frames are a pure function of t, so independent workers can run in parallel.
"""
import sys, json, os, time, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import build_video as B

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"


def main():
    t0, t1, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
    caps = json.load(open(os.path.join(B.HERE, "audio", "align.json")))["captions"]
    st = B.build_static()
    n = int(round((t1 - t0) * B.FPS))
    p = subprocess.Popen([FF, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", "%dx%d" % (B.W, B.H), "-r", str(B.FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                          "-pix_fmt", "yuv420p", out],
                         stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t_start = time.time()
    for i in range(n):
        t = t0 + i / B.FPS
        p.stdin.write(B.render_frame(t, st, caps).tobytes())
        if i % 15 == 0:
            el = time.time() - t_start
            print("[%s] %d/%d  %.2fs/frame" % (os.path.basename(out), i, n, el / max(i, 1)), flush=True)
    p.stdin.close()
    p.wait()
    print("[%s] done in %.0fs" % (os.path.basename(out), time.time() - t_start), flush=True)


if __name__ == "__main__":
    main()
