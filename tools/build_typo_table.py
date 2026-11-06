#!/usr/bin/env python3
"""Measure the 0.00-0.80 s block and write the renderer's table. No search, no guessing.

For every frame this reads four things off the reference and converts them to numbers
the renderer can use directly:

  box       the word's green-excess bounding box -> x, y, width, height
  penumbra  a fixed 2.5 px soft edge, measured on the settled frames (f10-f12), where
            the word is not moving and any softness is the picture's own
  ink       the 97th percentile of green-excess inside the box -> opacity
  dimmer    the plate's centre luma over its own value at f0 -> `dark`

Height that exceeds the glyph's natural height at that width is vertical motion smear,
which is drawn as a vertical stretch, not as a blur, so the box stays where the
reference puts it. The word's font is Montserrat Black, the closest of fourteen faces
tested; that, and only that, is where this block can differ from the reference.

    python3 tools/build_typo_table.py     # -> spec/typo-block.json
"""
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import typo_core as core
from ffbin import ffmpeg

REF = "analysis/attachment-filename-How-to-Edit-VIRAL-RE/reference.mp4"
N = 24            # 0.00-0.80 s: past this the green field has begun to dissolve in
PENUMBRA = 2.5    # settled px, measured on f10-f12
PEAK = [1.0]      # the settled ink peak, set from f10 before any alpha is computed
SETTLED = (slice(608, 686), slice(134, 584))   # where the word sits once it has landed


def ref_frames(n: int) -> list[np.ndarray]:
    b = subprocess.run([ffmpeg(), "-v", "error", "-i", REF, "-frames:v", str(n),
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    arr = np.frombuffer(b, np.uint8).reshape(-1, core.H, core.W, 3)
    return list(arr)


def excess(im: np.ndarray) -> np.ndarray:
    f = im.astype(np.float32)
    b, g, r = [f[..., k] for k in range(3)]
    return np.clip((g - (r + b) / 2) / 60.0, 0, 1.2)


def main() -> int:
    ref = ref_frames(N)
    plate = np.median(np.stack([im.astype(np.float32).mean(axis=2) for im in ref[:4]]), axis=0)
    centre0 = float(plate[600:680, 320:400].mean())
    basis = [(i, j) for i in range(5) for j in range(5 - i)]
    ds = 4                                    # the surface is smooth; fit it decimated
    hh, ww = plate.shape[0] // ds, plate.shape[1] // ds
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float64)
    X, Y = xx / (ww - 1) - 0.5, yy / (hh - 1) - 0.5
    A = np.stack([(X ** i * Y ** j).ravel() for i, j in basis], 1)

    def fit(f: np.ndarray):
        small_f = cv2.resize(f.astype(np.float32), (ww, hh), cv2.INTER_AREA).astype(np.float64)
        c, *_ = np.linalg.lstsq(A, small_f.ravel(), rcond=None)
        return c, float((small_f.ravel() - A @ c).std())

    coef, rms = fit(plate)
    true_ratio = core.glyph().height / core.glyph().width
    print(f"  plate polynomial deg4, {len(basis)} terms, rms {rms:.2f}/255, centre {centre0:.1f}; "
          f"glyph aspect {1 / true_ratio:.3f} h/w")

    e10 = excess(ref[10])
    PEAK[0] = max(1e-3, float(np.percentile(e10[SETTLED], 97)))
    print(f"  settled ink peak {PEAK[0]:.3f} (frame 10)")
    rows = []
    for i, im in enumerate(ref):
        e = excess(im)
        ys, xs = np.where(e > 0.45)
        dark = 1.0
        if im.astype(np.float32).mean(axis=2)[600:680, 320:400].mean() < centre0 * 0.97:
            dark = round(float(im.astype(np.float32).mean(axis=2)[600:680, 320:400].mean()
                               / centre0), 3)
        frame_coef, frame_rms = fit(im.astype(np.float32).mean(axis=2))
        if len(xs) < 60:
            rows.append(dict(frame=i, alpha=0.0, dark=dark,
                             plate_coef=np.round(frame_coef, 4).tolist()))
            print(f"  f{i:02d}  (plate only)")
            continue
        x, y, w, h = int(xs.min()), int(ys.min()), int(xs.max() - xs.min()), int(ys.max() - ys.min())
        # Ink opacity. Once the word has stopped travelling (f13 on) its box is a smear,
        # so the opacity is read where the word actually is -- the settled box -- against
        # its own settled peak. That is the fade the reference draws as a ghost.
        natural = w * true_ratio
        settled = SETTLED
        # Only a word that is already sitting at its final place can be read there; a
        # word still travelling has an empty box there, which is not a fade.
        if h > natural * 1.15 and abs(y - 608) < 26:
            alpha = float(np.clip(np.percentile(e[settled], 97) / PEAK[0], 0.0, 1.0))
        else:
            alpha = float(np.clip(np.percentile(e[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 97)
                                  / PEAK[0], 0.05, 1.0))
        squash = max(0.4, min(2.8, (h - 2 * PENUMBRA) / natural))
        rows.append(dict(frame=i, x=x, y=y, scale=round(w / core.SETTLE_W, 3),
                         squash=round(squash, 3), sigma=PENUMBRA, alpha=round(alpha, 2),
                         ink=1.0, dark=dark,
                         plate_coef=np.round(frame_coef, 4).tolist(), plate_rms=round(frame_rms, 2)))
        print(f"  f{i:02d} box {w:3d}x{h:3d} at {x:3d},{y:3d} -> scale {w / core.SETTLE_W:.3f} "
              f"natural h {natural:5.1f} squash {squash:4.2f} alpha {alpha:.2f} dark {dark:.2f}")

    for r in rows:
        r["plate_basis"] = [[i, j] for i, j in basis]
    Path("spec").mkdir(exist_ok=True)
    Path("spec/typo-block.json").write_text(json.dumps(
        {"plate": {"coef": np.round(coef, 5).tolist(), "basis": [[i, j] for i, j in basis]},
         "frames": rows}, indent=1))
    print(f"  {len(rows)} frames -> spec/typo-block.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
