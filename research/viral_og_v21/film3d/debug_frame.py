#!/usr/bin/env python3
"""Diagnose one frame: is geometry visible? what are light levels? where is auto-exposure landing?"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import geo3d as G, render3d as R, film1min as F
from PIL import Image

t = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0
W = int(sys.argv[2]) if len(sys.argv) > 2 else 480
H = int(W * 9 / 16)
cave, shots = F.film()
starts, acc = [], 0.0
for s in shots:
    starts.append(acc); acc += s.dur
k = max(j for j, st in enumerate(starts) if st <= t + 1e-6)
s = shots[k]; local = t - starts[k]
eye, tgt, fov, lts, act = s.sample(local)
print("shot", k + 1, "local", round(local, 2), "eye", np.round(eye, 2), "tgt", np.round(tgt, 2), "fov", fov)
for (a, b, c, d) in lts:
    print("  light", d, "pos", np.round(a, 2), "col", np.round(b, 3), "power", c)
cam = R.Cam(W, H, eye, tgt, fov=fov)
lights = [R.Light(a, b, c, kind=d) for (a, b, c, d) in lts]
hg = R.march_set(cam, cave, W, H, steps=34)
print("hit %%", round(100 * hg["hit"].mean(), 1), "t range", float(hg["t"].min()), float(hg["t"].max()))
print("eye inside cave sdf:", float(cave.sdf(cam.eye[None, :])[0]))
bg, depth, tr = R.shade_set(hg, cam, cave, lights)
print("bg raw  p50 %.4f p99 %.4f max %.3f" % (np.percentile(bg, 50), np.percentile(bg, 99), bg.max()))
vol, vt = R.volumetrics(cam, cave, lights, W, H, density=0.0075, res=0.34)
print("vol raw p50 %.4f p99 %.4f max %.3f" % (np.percentile(vol, 50), np.percentile(vol, 99), vol.max()))
comp = bg * vt[..., None] + vol
print("comp    p50 %.4f p99 %.4f max %.3f" % (np.percentile(comp, 50), np.percentile(comp, 99), comp.max()))
print("auto exposure would be:", R.auto_exposure(comp))
# geometry only, exposure 1
for ex in (1.0, 3.0, 8.0):
    Image.fromarray((np.clip(comp * ex, 0, 1) * 255).astype(np.uint8)).save(f"dbg_t{int(t)}_e{int(ex)}.png")
Image.fromarray((np.clip(bg * 8, 0, 1) * 255).astype(np.uint8)).save(f"dbg_t{int(t)}_geo.png")
Image.fromarray((np.clip(vol * 8, 0, 1) * 255).astype(np.uint8)).save(f"dbg_t{int(t)}_vol.png")
print("saved dbg_*.png")
