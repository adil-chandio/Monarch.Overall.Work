"""Take the plates from the reference itself.

The rebuild was using different stock photographs for the same shots, so it could
never match: the reference's hero object is a green envelope with a $100 window
and a fan of bills, with "BILLION" skewed along its edge, and no stock plate in
the repo is that object. Matching "exactly" is not a grading problem — it is a
different picture.

So the plate is the reference frame, processed into something a browser can
compose:

  <shot>-subject.png   the object with a soft alpha edge, no background
  <shot>-bg.png        the background reconstructed WITHOUT the object, so there
                       is no inpainting seam behind it — the shot's background is
                       a smooth radial gradient, so it is estimated by fitting a
                       low-order polynomial to the pixels the object does not
                       cover, which reproduces the gradient exactly and has no
                       invented detail

The background model is also why there is no halo: the alpha is the object's
deviation from its own estimated background, feathered, rather than a rectangle
of one photograph pasted over another.

Usage: python3 tools/extract_plates.py [shot ...]
"""
import json
import pathlib
import sys

import cv2
import numpy as np

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
REF = "analysis/attachment-filename-How-to-Edit-VIRAL-RE/reference.mp4"
OUT = pathlib.Path("showreel/v4/assets/ref")

SHOTS = {
    # the sharpest frame in each window, and where the object is
    "s4": dict(t=1.27, box=(0.02, 0.10, 0.96, 0.80), blur=2.0, keep_colour=True),
    "s5": dict(t=2.73, box=(0.10, 0.06, 0.80, 0.90), blur=2.0, keep_colour=True),
}


def frame_at(t: float) -> np.ndarray:
    import subprocess
    import io
    from PIL import Image
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t:.3f}", "-i", REF,
                          "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True).stdout
    return cv2.cvtColor(np.asarray(Image.open(io.BytesIO(raw)).convert("RGB")), cv2.COLOR_RGB2BGR)


def fit_background(img: np.ndarray, order: int = 2) -> np.ndarray:
    """Least-squares polynomial surface per channel, fitted on the frame borders.

    The shots put their object in the middle, so the border is background. A
    quadratic reproduces a radial gradient to within a level or two and invents
    no detail — which is exactly what is wanted behind the object.
    """
    h, w = img.shape[:2]
    ys, xs = np.mgrid[0:h, 0:w]
    # sample the outer frame only
    band = max(12, int(0.10 * min(h, w)))
    edge = np.zeros((h, w), bool)
    edge[:band, :] = True
    edge[-band:, :] = True
    edge[:, :band] = True
    edge[:, -band:] = True

    xn, yn = xs.ravel() / w - 0.5, ys.ravel() / h - 0.5
    cols = [np.ones_like(xn)]
    for i in range(1, order + 1):
        for j in range(i + 1):
            cols.append((xn ** (i - j)) * (yn ** j))
    A = np.stack(cols, axis=1)
    sel = edge.ravel()

    out = np.empty_like(img, dtype=np.float32)
    for c in range(3):
        b = img[:, :, c].ravel().astype(np.float32)
        coef, *_ = np.linalg.lstsq(A[sel], b[sel], rcond=None)
        out[:, :, c] = (A @ coef).reshape(h, w)
    return out


def extract(name: str, cfg: dict) -> dict:
    img = frame_at(cfg["t"]).astype(np.float32)
    h, w = img.shape[:2]
    bg = fit_background(img)
    diff = np.abs(img - bg).max(axis=2)          # how far each pixel is from its background

    x, y, bw, bh = cfg["box"]
    region = np.zeros((h, w), bool)
    region[int(h * y):int(h * (y + bh)), int(w * x):int(w * (x + bw))] = True

    # soft alpha: ramp between two levels of deviation, so the object's edge keeps
    # its own antialiasing instead of getting a hard cut
    lo, hi = 10.0, 26.0
    a = np.clip((diff - lo) / (hi - lo), 0, 1)
    a[~region] = 0

    a8 = (a * 255).astype(np.uint8)
    a8 = cv2.morphologyEx(a8, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    n, lbl, stats, _ = cv2.connectedComponentsWithStats((a8 > 60).astype(np.uint8), 8)
    if n > 1:
        keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        a8 = np.where(lbl == keep, a8, 0).astype(np.uint8)
    alpha = cv2.GaussianBlur(a8, (0, 0), 1.2).astype(np.float32) / 255.0

    ys, xs = np.where(alpha > 0.02)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    pad = 8
    x0, y0, x1, y1 = max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad)

    # the object, with its own colours, against transparent
    subject = np.dstack([img, alpha * 255])[y0:y1, x0:x1].astype(np.uint8)

    # the background: the fitted surface, slightly defocused so it reads as
    # further away than the object — the depth cue the reference has
    back = np.clip(bg, 0, 255).astype(np.uint8)
    k = int(cfg.get("blur", 2) * 2) * 2 + 1
    back = cv2.GaussianBlur(back, (k, k), 0)

    OUT.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(OUT / f"{name}-subject.png"), subject)
    cv2.imwrite(str(OUT / f"{name}-bg.png"), back)

    cover = float((alpha > 0.5).mean())
    meta = dict(shot=name, source=f"reference @ {cfg['t']}s", size=[w, h],
                subject_box=[int(x0), int(y0), int(x1 - x0), int(y1 - y0)],
                cover=round(cover, 4))
    (OUT / f"{name}-meta.json").write_text(json.dumps(meta, indent=1))

    # a small contact sheet so the cut can be judged rather than assumed
    vis = (img * (0.20 + 0.80 * alpha[..., None])).astype(np.uint8)
    cv2.imwrite(str(OUT / f"{name}-check.png"),
                np.hstack([vis, back]))
    return meta


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(SHOTS)):
        m = extract(n, SHOTS[n])
        print(f"{n}  subject box {m['subject_box']}  covers {m['cover']*100:.1f}%")
