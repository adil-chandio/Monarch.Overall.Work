#!/usr/bin/env python3
"""Render ONE keyframe's camera move into an intermediate mp4 segment."""
import argparse, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W_SRC, H_SRC = 1920, 804          # 2.39:1 canvas inside a 1920x1080 frame

def font(size, bold=True):
    p = ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
         else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

def prep(path):
    im = Image.open(path).convert("RGB")
    # cover-fit into the 2.39 band
    s = max(W_SRC / im.width, H_SRC / im.height)
    im = im.resize((max(W_SRC, int(im.width * s + 0.5)), max(H_SRC, int(im.height * s + 0.5))), Image.LANCZOS)
    x = (im.width - W_SRC) // 2
    y = (im.height - H_SRC) // 2
    return im.crop((x, y, x + W_SRC, y + H_SRC))

def crop_zoom(im, zoom, dx, dy):
    w = int(W_SRC / zoom); h = int(H_SRC / zoom)
    cx = W_SRC / 2 + dx * W_SRC
    cy = H_SRC / 2 + dy * H_SRC
    x0 = int(np.clip(cx - w / 2, 0, W_SRC - w))
    y0 = int(np.clip(cy - h / 2, 0, H_SRC - h))
    return im.crop((x0, y0, x0 + w, y0 + h)).resize((W_SRC, H_SRC), Image.BICUBIC)

def draw_text(img, text, pos):
    if not text:
        return img
    d = ImageDraw.Draw(img)
    fs = 46
    f = font(fs)
    tw = d.textlength(text, font=f)
    x = (W_SRC - tw) / 2
    y = {"low": H_SRC - 130, "mid": H_SRC / 2 - 20, "high": 90}[pos]
    for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2)):
        d.text((x + ox, y + oy), text, font=f, fill=(0, 0, 0))
    d.text((x, y), text, font=f, fill=(238, 236, 232))
    return img

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", required=True)
    ap.add_argument("--shot", required=True)
    ap.add_argument("--cam", required=True)          # json
    ap.add_argument("--sec", type=float, default=6.0)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--text", default="")
    ap.add_argument("--textpos", default="low")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    import json
    cam = json.loads(a.cam)
    src = prep(f"out/{a.key}.png")
    n = max(1, int(round(a.sec * a.fps)))
    w, h = W_SRC, H_SRC
    import subprocess
    FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
    p = subprocess.Popen([FF, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{w}x{h}", "-r", str(a.fps), "-i", "-",
                          "-c:v", "libx264", "-preset", "ultrafast", "-crf", "12",
                          "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for i in range(n):
        t = i / max(n - 1, 1)
        kind = cam[0]
        if kind == "push":
            z = 1.0 + (cam[1] - 1.0) * (t ** 0.85)
            dx, dy = 0.0, 0.0
        elif kind == "pull":
            z = cam[1] - (cam[1] - 1.0) * (t ** 0.85)
            dx, dy = 0.0, 0.0
        elif kind == "drift":
            dx, dy = cam[1][0] * t, cam[1][1] * t
            z = 1.0 + (cam[2] - 1.0) * t
        elif kind == "shake":
            amp, z0 = cam[1], cam[2]
            z = z0 + (z0 * 0.03) * t
            dx = amp * math.sin(t * 41.0) * math.sin(t * 7.3)
            dy = amp * math.cos(t * 33.0 + 1.1) * math.sin(t * 5.1)
        else:
            z, dx, dy = 1.0, 0.0, 0.0
        fr = crop_zoom(src, z, dx, dy)
        fr = draw_text(fr, a.text, a.textpos)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    main()
