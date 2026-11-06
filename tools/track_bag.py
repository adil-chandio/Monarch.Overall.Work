#!/usr/bin/env python3
"""Where is the bag, and how big, in each frame of the reference's green scene?

The bag is a layer we hold with a real alpha, so tracking is a search over the two
things a composite needs: scale and place. Matching is done on gradient magnitude, which
ignores colour and brightness -- the scene drains from green to grey mid-shot, and a
colour match would lose the bag halfway through.

    python3 tools/track_bag.py            # -> analysis/v4-build/bag-track.json
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
LAYER = "showreel/v4/assets/layers/plate-bag-green-front.png"
FIRST, LAST = 40, 94            # 1.33 s .. 3.13 s
DS = 2                          # match at half resolution, report at full


def edges(img: np.ndarray) -> np.ndarray:
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, 3)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, 3)
    m = np.sqrt(gx * gx + gy * gy)
    return cv2.GaussianBlur(m, (0, 0), 1.0)


def main() -> int:
    b = subprocess.run([ffmpeg(), "-v", "error", "-i", REF, "-frames:v", str(LAST + 1),
                        "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    frames = np.frombuffer(b, np.uint8).reshape(-1, 1280, 720, 3)
    lay = cv2.imread(LAYER, cv2.IMREAD_UNCHANGED)
    alpha = lay[..., 3].astype(np.float32) / 255.0
    ys, xs = np.where(alpha > 0.35)
    lay = lay[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    lh, lw = lay.shape[:2]
    print(f"  layer {lw}x{lh}")

    rows = []
    for i in range(FIRST, LAST + 1):
        target = cv2.resize(edges(frames[i]), (720 // DS, 1280 // DS))
        best = (-9, None)
        for s in np.arange(0.55, 1.45, 0.05):
            t = cv2.resize(lay, (max(8, int(lw * s / DS)), max(8, int(lh * s / DS))))
            th, tw = t.shape[:2]
            if th >= target.shape[0] or tw >= target.shape[1]:
                continue
            te = edges(t)
            r = cv2.matchTemplate(target, te, cv2.TM_CCOEFF_NORMED)
            _, mx, _, loc = cv2.minMaxLoc(r)
            if mx > best[0]:
                best = (mx, (round(float(s), 3), loc[0] * DS, loc[1] * DS))
        # refine scale around the winner
        s0, x0, y0 = best[1]
        for s in np.arange(max(0.4, s0 - 0.05), s0 + 0.05, 0.0125):
            t = cv2.resize(lay, (max(8, int(lw * s / DS)), max(8, int(lh * s / DS))))
            th, tw = t.shape[:2]
            if th >= target.shape[0] or tw >= target.shape[1]:
                continue
            r = cv2.matchTemplate(target, edges(t), cv2.TM_CCOEFF_NORMED)
            _, mx, _, loc = cv2.minMaxLoc(r)
            if mx > best[0]:
                best = (mx, (round(float(s), 4), loc[0] * DS, loc[1] * DS))
        score, (s, x, y) = best
        rows.append(dict(frame=i, t=round(i / 30, 4), score=round(float(score), 3),
                         scale=s, x=int(x), y=int(y),
                         w=int(round(lw * s)), h=int(round(lh * s))))
        print(f"  f{i:02d} t={i / 30:5.2f} score {score:5.3f} scale {s:.3f} at {x:4d},{y:4d} "
              f"({rows[-1]['w']}x{rows[-1]['h']})")

    Path("analysis/v4-build").mkdir(parents=True, exist_ok=True)
    Path("analysis/v4-build/bag-track.json").write_text(json.dumps(rows, indent=1))
    good = [r["score"] for r in rows]
    print(f"\n  mean score {np.mean(good):.3f}  min {np.min(good):.3f}  frames {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
