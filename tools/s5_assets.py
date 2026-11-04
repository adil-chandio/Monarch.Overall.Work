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
ENTRY_T, PLATE_T, CLEAN_T, FULL_T = 1.45, 1.85, 2.05, 2.95
FF = ffmpeg()


def grab(t: float) -> np.ndarray:
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t:.3f}", "-i", REF,
                          "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True).stdout
    return np.asarray(Image.open(io.BytesIO(raw)).convert("RGB")).astype(np.float32)


def cut_out(name: str, sel: np.ndarray, full: np.ndarray) -> list[int]:
    """Cut the element out of the reference's own final frame.

    Solving for alpha against an earlier frame was wrong in a way that looked like
    a bug and was not: the type in the reference is opaque, so the difference
    between the two frames is not the element's alpha, it is the element's colour
    over whatever the background changed by. Dividing by that difference gave a
    partial alpha, the plate showed through the letters, and the threshold that
    cleaned it up drew a straight line across them.

    The element is opaque, so the layer is the final frame's own pixels, masked by
    the glyph shape and feathered by a pixel or two to sit on the plate.
    """
    shape = cv2.dilate(sel.astype(np.uint8), np.ones((5, 5), np.uint8))
    al = cv2.GaussianBlur(shape.astype(np.float32), (0, 0), 1.6)
    al = np.clip(al / max(al.max(), 1e-6), 0, 1) * (shape > 0)

    ys, xs = np.where(al > 0.02)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    x0, y0 = max(0, x0 - 3), max(0, y0 - 3)

    colour = full[y0:y1, x0:x1]
    alpha = al[y0:y1, x0:x1]
    rgba = np.dstack([colour, alpha * 255]).astype(np.uint8)
    cv2.imwrite(str(OUT / f"{name}.png"), cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA))
    box = [int(x0), int(y0), int(x1 - x0), int(y1 - y0)]
    json.dump({"box": box}, open(OUT / f"{name}.json", "w"))
    print(f"  {name:14s} {box}")
    return box


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    plate, full, clean = grab(PLATE_T), grab(FULL_T), grab(CLEAN_T)

    # The shot enters with BILLION over the field and the bag further from the lens;
    # both are gone by 1.85. Neither state can be faked from the other, so the scene
    # holds the entry frame and dissolves to the settled one — the word leaves the
    # way the reference's does, in one move, rather than being invented.
    entry = grab(ENTRY_T)
    cv2.imwrite(str(OUT / "s5plate-entry.png"), cv2.cvtColor(entry, cv2.COLOR_RGB2BGR))
    print(f"  s5plate-entry.png the reference at {ENTRY_T}s — BILLION still over the field")

    for name, f in (("plate 2.05", plate), ("full 2.95", full)):
        r, g, b = f[:, :, 0], f[:, :, 1], f[:, :, 2]
        red = (r > 80) & (r - g > 35) & (r - b > 35)
        print(f"  {name}: {int(red.sum())} red pixels")

    cv2.imwrite(str(OUT / "s5plate-base.png"), cv2.cvtColor(plate.astype(np.uint8), cv2.COLOR_RGB2BGR))
    print(f"  s5plate-base.png  the reference at {PLATE_T}s — the last frame of the shot with no type in it")

    # What the plate cannot supply is the END of the colour's life: by 2.25 s the
    # reference has drained the green from the field as well as the bag. That last
    # stretch is a saturation and nothing else, so it can be applied to the plate
    # itself. The plate has to be 1.85 s and not 1.37 s, because BILLION is over the
    # field at 1.37 — a plate taken there carries the word, and inpainting it out
    # smears the bills, so the plate is the last frame of the shot that has no type.
    drained = cv2.cvtColor(plate.astype(np.uint8), cv2.COLOR_RGB2HSV)
    drained[..., 1] = (drained[..., 1].astype(np.float32) * 0.02).astype(np.uint8)
    cv2.imwrite(str(OUT / "s5-plate.png"),
                cv2.cvtColor(cv2.cvtColor(drained, cv2.COLOR_HSV2RGB), cv2.COLOR_RGB2BGR))
    print("  s5-plate.png      the same frame with the colour drained — the end of the sweep")

    # Split the two elements where the reference actually separates them: by the
    # empty rows between them. Splitting at a fraction of the type's total height
    # put the boundary inside NO (its rows run 352-575 while 46 % of the span is
    # 396), so the top strip of NO was cut into HE SAID's layer — which then moved
    # with HE SAID's own camera offset and left a dark band across the top of NO.
    r, g, b = full[:, :, 0], full[:, :, 1], full[:, :, 2]
    red = (r > 80) & (r - g > 35) & (r - b > 35)
    rows = red.sum(axis=1)
    filled = [i for i in range(len(rows)) if rows[i] > 200]
    groups, start, prev = [], filled[0], filled[0]
    for i in filled[1:]:
        if i - prev > 4:
            groups.append((start, prev))
            start = i
        prev = i
    groups.append((start, prev))
    print(f"  type rows: {groups}")
    if len(groups) < 2:
        raise SystemExit("expected two type elements, found one — check the reference window")
    he_rows, no_rows = groups[0], tuple([groups[1][0], groups[-1][1]])

    up = np.zeros_like(red); up[he_rows[0]:he_rows[1] + 1, :] = True; up &= red
    lo = np.zeros_like(red); lo[no_rows[0]:no_rows[1] + 1, :] = True; lo &= red
    cut_out("s5-he-layer", up, full)
    cut_out("s5-no", lo, full)

    # the measured colour endpoints, so the page animates to something real
    swept = plate.mean(axis=(0, 1)).round(0)
    ended = full.mean(axis=(0, 1)).round(0)
    print(f"  frame mean, {PLATE_T}s {swept[0]}/{swept[1]}/{swept[2]} -> {FULL_T}s {ended[0]}/{ended[1]}/{ended[2]}")
    print("  the plate is the shot as it ENTERS the frame; the drained copy is the end state")


if __name__ == "__main__":
    main()
