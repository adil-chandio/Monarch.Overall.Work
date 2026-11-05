#!/usr/bin/env python3
"""Separate the bag from its green screen by texture, not by colour.

The screen is a smooth lit field; the bag is leather and paper, so it is *rough* even
where its hue matches the screen's. So:

  1. candidates = pixels that are smooth (local sigma < 3) AND strongly green. Those can
     only be screen.
  2. a quadratic surface is fitted to the candidates in all three channels, which models
     the lighting falloff across the field.
  3. whatever is far from that surface is subject. Two dilations close the paper's
     holes, and the largest component is kept.

    python3 tools/mask_green_scene.py            # visual check -> analysis/v4-build/
"""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ffbin import ffmpeg

REF = "analysis/attachment-filename-How-to-Edit-VIRAL-RE/reference.mp4"
DS = 4


def subject_mask(im: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    small = cv2.resize(im, (720 // DS, 1280 // DS), cv2.INTER_AREA).astype(np.float32)
    h, w = small.shape[:2]
    g = small.mean(axis=2)
    loc = cv2.boxFilter(g * g, -1, (9, 9)) - cv2.boxFilter(g, -1, (9, 9)) ** 2
    sigma = np.sqrt(np.clip(loc, 0, None))
    b, gg, r = [small[..., k] for k in range(3)]
    green = gg - (r + b) / 2
    cand = (sigma < 3.0) & (green > 22) & (gg > 40)
    if cand.sum() < 3000:
        cand = (sigma < 6.0) & (green > 15)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    X, Y = xx / w - 0.5, yy / h - 0.5
    basis = [(i, j) for i in range(3) for j in range(3 - i)]
    A = np.stack([(X ** i * Y ** j).ravel() for i, j in basis], 1)
    model = np.zeros_like(small)
    for c in range(3):
        coef, *_ = np.linalg.lstsq(A[cand.ravel()], small[..., c].ravel()[cand.ravel()], rcond=None)
        model[..., c] = (A @ coef).reshape(h, w)
    d = np.abs(small - model).max(axis=2)
    m = (d > 20).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    if n > 1:
        k = 1 + int(np.argmax(st[1:, 4]))
        keep = (lab == k).astype(np.uint8)
    else:
        keep = m
    full = cv2.resize(keep, (720, 1280), cv2.INTER_LINEAR)
    return (full > 0.5).astype(np.uint8), small


def main() -> int:
    b = subprocess.run([ffmpeg(), "-v", "error", "-i", REF, "-frames:v", "95",
                        "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    F = np.frombuffer(b, np.uint8).reshape(-1, 1280, 720, 3)
    rows = []
    for i in (42, 46, 50, 55, 60, 65, 70, 80, 90, 93):
        m, _ = subject_mask(F[i])
        ys, xs = np.where(m > 0)
        if len(xs) == 0:
            continue
        rows.append(dict(frame=i, t=round(i / 30, 3), x=int(xs.min()), y=int(ys.min()),
                         w=int(xs.max() - xs.min()), h=int(ys.max() - ys.min()),
                         fill=round(float(m.sum()) / (720 * 1280), 3)))
        print(rows[-1])
        vis = F[i].copy()
        vis[m > 0] = (vis[m > 0] * 0.35 + np.array([40, 40, 255]) * 0.65).astype(np.uint8)
        cv2.imwrite(f"analysis/v4-build/mask-{i:03d}.png", cv2.resize(vis, (360, 640)))
    Path("analysis/v4-build/mask-samples.json").write_text(json.dumps(rows, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
