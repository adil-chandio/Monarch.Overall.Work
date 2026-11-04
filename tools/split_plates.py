"""Split the flat photographic plates into depth layers.

A flat plate can only scale or slide as one piece, which is why the rebuild's
plates measured 0.00 % scale movement while the reference's shots push +2.3 %/s.
To get two layers that can move at different rates — the actual parallax — a
plate has to be cut in two.

What is produced per plate (written to showreel/v4/assets/layers/):

  <name>-back.webp   the plate with the subject removed, inpainted from its own
                     surroundings, slightly softened: `far` reads as further away
  <name>-front.webp  the subject alone on transparent, tightened to its own
                     bounding box so CSS can place it where the composition wants
  <name>-mask.json   the bbox and the cover fraction, so the build can position
                     the layer without guessing

Method: GrabCut seeded by a rectangle, then the largest connected component, a
closing pass and a 3 px feather. The mask is deliberately conservative — a hard
subject edge that is slightly cut reads as a mistake, while 2-3 px of背景
bleeding into the front layer is invisible at 720 wide once it moves.

Usage: python3 tools/split_plates.py [name ...]
"""
import json
import pathlib
import sys

import cv2
import numpy as np

ASSETS = pathlib.Path("showreel/v4/assets")
OUT = ASSETS / "layers"

# rect = (x, y, w, h) as a fraction of the frame — the subject must sit inside it
PLATES = {
    "plate-bag-green": dict(rect=(0.14, 0.04, 0.66, 0.92), feather=3),
    "plate-cta-hero": dict(rect=(0.08, 0.03, 0.84, 0.95), feather=3),
    "plate-bag-stool": dict(rect=(0.24, 0.26, 0.52, 0.66), feather=3),
    "plate-hands-red": dict(rect=(0.02, 0.10, 0.96, 0.80), feather=3),
}


def largest_component(mask: np.ndarray) -> np.ndarray:
    n, lbl, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    if n <= 1:
        return mask
    keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    return (lbl == keep).astype(np.uint8)


def split(name: str, cfg: dict) -> dict:
    src = ASSETS / f"{name}.png"
    img = cv2.imread(str(src))
    if img is None:
        raise SystemExit(f"missing {src}")
    h, w = img.shape[:2]
    x, y, rw, rh = cfg["rect"]
    rect = (int(w * x), int(h * y), int(w * rw), int(h * rh))

    mask = np.zeros((h, w), np.uint8)
    bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(img, mask, rect, bgd, fgd, 6, cv2.GC_INIT_WITH_RECT)
    a = ((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD)).astype(np.uint8)
    a = largest_component(a)
    a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    a = cv2.morphologyEx(a, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    a = largest_component(a)

    # grow the alpha a touch so no light halo survives on a dark background
    a = cv2.dilate(a, np.ones((5, 5), np.uint8), iterations=1)
    alpha = cv2.GaussianBlur(a * 255, (0, 0), cfg.get("feather", 3))

    ys, xs = np.where(a > 0)
    if len(xs) == 0:
        raise SystemExit(f"{name}: empty mask — widen the rect")
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    pad = 6
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(w, x1 + pad), min(h, y1 + pad)

    # front: the subject, transparent outside it
    front = np.dstack([img, (alpha * 1.0).astype(np.uint8)])[y0:y1, x0:x1]

    # back: the plate with the subject inpainted out of its own surroundings
    hole = cv2.dilate(a, np.ones((9, 9), np.uint8), iterations=1)
    back = cv2.inpaint(img, hole * 255, 7, cv2.INPAINT_TELEA)
    # `far` gets a light defocus — depth cue, and it hides the inpaint seams
    k = cfg.get("back_blur", 9)
    back = cv2.GaussianBlur(back, (k, k), 0)

    OUT.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(OUT / f"{name}-front.png"), front)
    cv2.imwrite(str(OUT / f"{name}-back.png"), back)

    meta = {
        "plate": name,
        "size": [w, h],
        "front_box": [int(x0), int(y0), int(x1 - x0), int(y1 - y0)],
        "cover": round(float((a > 0).mean()), 4),
        "cover_of_subject": round(float((a > 0).sum() / max((x1 - x0) * (y1 - y0), 1)), 4),
    }
    (OUT / f"{name}-mask.json").write_text(json.dumps(meta, indent=1))
    return meta


if __name__ == "__main__":
    want = sys.argv[1:] or list(PLATES)
    for n in want:
        m = split(n, PLATES[n])
        print(f"{n:20s} front {m['front_box']}  subject {m['cover']*100:4.1f}% of frame")
