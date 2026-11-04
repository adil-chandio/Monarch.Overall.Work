"""Build s5's plate and its two type layers from the reference itself.

Three things were measured about this shot, and they overlap, which is why taking
any single frame as the plate kept going wrong:

  * the colour sweep (green field -> grey) runs 1.9 s to 2.9 s
  * HE SAID arrives around 2.2 s, NO slams 2.35 s -> 2.9 s
  * the camera is still moving through all of it

So there is no frame in this shot that is both the final colour and free of type.
The plate is therefore the last frame with no type in it (2.10 s), the colour change
is reproduced in the page as a saturate() animation (the measured end state is
neutral, 129.8/129.7/129.9 — the sweep is almost pure loss of saturation), and the
type arrives as two layers unmixed against the 2.05 s frame, which has neither.

Run: python3 tools/s5_assets.py
"""
import io
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cv2
import numpy as np
from PIL import Image

from ffbin import ffmpeg

REF = "analysis/attachment-filename-How-to-Edit-VIRAL-RE/reference.mp4"
OUT = Path("showreel/v4/assets/ref")
PLATE_T, CLEAN_T, FULL_T = 2.10, 2.05, 2.95
FF = ffmpeg()


def grab(t: float) -> np.ndarray:
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t:.3f}", "-i", REF,
                          "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True).stdout
    return np.asarray(Image.open(io.BytesIO(raw)).convert("RGB")).astype(np.float32)


def unmix(name: str, sel: np.ndarray, full: np.ndarray, base: np.ndarray) -> list[int]:
    """Recover C and alpha from full = C*a + base*(1-a), given where the type is.

    Two frames of the same shot, one with the element and one without, so the
    difference is the element. Keying by colour instead leaves a pale fringe on
    every glyph edge; solving for C does not.
    """
    d = np.abs(full - base).max(axis=2)
    al = np.where(sel, np.clip(d / 210.0, 0, 1), 0).astype(np.float32)
    solid = (al > 0.30).astype(np.uint8)
    n, lbl, st, _ = cv2.connectedComponentsWithStats(solid, 8)
    keep = np.zeros_like(solid)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] > 1500:
            keep[lbl == i] = 1
    al = cv2.GaussianBlur((keep * 255).astype(np.uint8), (0, 0), 1.0).astype(np.float32) / 255
    a = np.clip(al, 1e-3, 1)[..., None]
    c = np.clip((full - (1 - a) * base) / a, 0, 255)
    ys, xs = np.where(al > 0.05)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    x0, y0 = max(0, x0 - 6), max(0, y0 - 6)
    rgba = np.dstack([c, al * 255]).astype(np.uint8)[y0:y1, x0:x1]
    cv2.imwrite(str(OUT / f"{name}.png"), cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA))
    box = [int(x0), int(y0), int(x1 - x0), int(y1 - y0)]
    json.dump({"box": box}, open(OUT / f"{name}.json", "w"))
    print(f"  {name:14s} {box}")
    return box


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    plate, full, clean = grab(PLATE_T), grab(FULL_T), grab(CLEAN_T)

    for name, f in (("plate 2.10", plate), ("full 2.95", full)):
        r, g, b = f[:, :, 0], f[:, :, 1], f[:, :, 2]
        red = (r > 80) & (r - g > 35) & (r - b > 35)
        print(f"  {name}: {int(red.sum())} red pixels")

    cv2.imwrite(str(OUT / "s5-plate.png"), cv2.cvtColor(plate.astype(np.uint8), cv2.COLOR_RGB2BGR))
    print(f"  s5-plate.png   the reference at {PLATE_T}s — no type in it")

    r, g, b = full[:, :, 0], full[:, :, 1], full[:, :, 2]
    red = (r > 80) & (r - g > 35) & (r - b > 35)
    ys, _ = np.where(red)
    band = int(ys.min() + (ys.max() - ys.min()) * 0.46)

    up = np.zeros_like(red); up[:band, :] = True; up &= red
    lo = np.zeros_like(red); lo[band:, :] = True; lo &= red
    unmix("s5-he-layer", up, full, clean)
    unmix("s5-no", lo, full, clean)

    # the measured colour endpoints, so the page animates to something real
    swept = plate.mean(axis=(0, 1)).round(1)
    ended = full.mean(axis=(0, 1)).round(1)
    print(f"  frame mean, {PLATE_T}s {swept[0]}/{swept[1]}/{swept[2]} -> {FULL_T}s {ended[0]}/{ended[1]}/{ended[2]}")
    print(f"  animation window: {PLATE_T}s -> {FULL_T}s, saturate 1 -> 0")


if __name__ == "__main__":
    main()
