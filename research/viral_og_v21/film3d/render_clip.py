#!/usr/bin/env python3
"""Render a time range of the 60 s film as real 3D frames -> mp4."""
import sys, os, json, math, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import geo3d as G, render3d as R, film1min as F
from PIL import Image, ImageDraw, ImageFont

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"

def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

def draw_text(img, txt, pos="low"):
    if not txt: return img
    d = ImageDraw.Draw(img); H = img.height
    f = font(max(16, H // 22))
    tw = d.textlength(txt, font=f)
    y = {"low": H - int(H * 0.18), "mid": H // 2}[pos]
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        d.text(((img.width - tw) / 2 + ox, y + oy), txt, font=f, fill=(0, 0, 0))
    d.text(((img.width - tw) / 2, y), txt, font=f, fill=(235, 233, 229))
    return img

def main():
    t0 = float(sys.argv[1]); t1 = float(sys.argv[2])
    W = int(sys.argv[3]) if len(sys.argv) > 3 else 480
    H = int(W * 9 / 16)
    fps = 24
    out = sys.argv[4] if len(sys.argv) > 4 else "out/clip3d.mp4"
    step = int(sys.argv[5]) if len(sys.argv) > 5 else 2   # temporal supersample step
    os.makedirs("out", exist_ok=True)
    cave, shots = F.film()
    starts, acc = [], 0.0
    for s in shots:
        starts.append(acc); acc += s.dur
    n = int(round((t1 - t0) * fps))
    p = subprocess.Popen([FF, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for i in range(n):
        T = t0 + i / fps
        k = max(j for j, st in enumerate(starts) if st <= T + 1e-6)
        local = T - starts[k]
        s = shots[k]
        eye, tgt, fov, lts, act = s.sample(local)
        cam = R.Cam(W, H, eye, tgt, fov=fov)
        lights = [R.Light(a, b, c, kind=d) for (a, b, c, d) in lts]
        hg = R.march_set(cam, cave, W, H, steps=34)
        bg, depth = R.shade_set(hg, cam, cave, lights)
        img = bg
        if act.get("kind") == "skull":
            rk = G.rocks((0, -0.12, 0.0), n=380, radius=0.30)
            cr = R.shade_points(rk, cam, lights, cave, amb=0.01)
            spr = R.splat(rk, cam, W, H, depth, cr)
            img = img * (1 - spr["cov"][..., None]) + spr["col"] * spr["cov"][..., None]
            nd = G.skull(scale=act.get("scale", 1.0), density=0.8)
            nd["P"] = nd["P"] + np.asarray(act["pos"], np.float32)
            if act.get("rot"):
                nd["P"] = G.rotY(nd["P"], act["rot"])
                nd["N"] = G.rotY(nd["N"], act["rot"], (0, 0, 0))
            cl = R.shade_points(nd, cam, lights, cave, amb=0.01)
            sp = R.splat(nd, cam, W, H, depth, cl)
            img = img * (1 - sp["cov"][..., None]) + sp["col"] * sp["cov"][..., None]
        elif act.get("kind") == "bear":
            nd = G.bear(T, pose=act.get("pose", 0), walk=act.get("walk", 0),
                        phase=act.get("phase", 0), head_yaw=act.get("yaw", 0),
                        breathe=act.get("breath", 0), density=0.9)
            nd["P"] = nd["P"] + np.asarray(act["pos"], np.float32)
            cl = R.shade_points(nd, cam, lights, cave, amb=0.02)
            sp = R.splat(nd, cam, W, H, depth, cl)
            img = img * (1 - sp["cov"][..., None]) + sp["col"] * sp["cov"][..., None]
        vol = R.volumetrics(cam, cave, lights, W, H, density=0.020, res=0.32)
        fin = R.finish(img + vol * 1.5, seed=i)
        fr = Image.fromarray((fin * 255).astype(np.uint8))
        fr = draw_text(fr, s.text, s.texpos)
        p.stdin.write(fr.tobytes())
        if i % 24 == 0:
            print("frame", i, "/", n, flush=True)
    p.stdin.close(); p.wait()
    print("wrote", out)

if __name__ == "__main__":
    main()
