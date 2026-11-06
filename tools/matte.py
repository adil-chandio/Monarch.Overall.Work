#!/usr/bin/env python3
"""Key our own plates into clean mattes — the green-screen pass, done properly.

Every subject we own sits on a flat, lit backdrop (the portrait on red, the bag on green,
the stool in a storm). Rather than trust whatever alpha came with a file, each subject is
re-keyed here:

  1. the backdrop is modelled per pixel by a smooth surface fitted to pixels that are both
     *smooth* (the screen is out of focus, the subject is not) and *chromatic* the way the
     screen is -- so the model follows the lighting falloff across the field;
  2. alpha = how far a pixel is from that model, measured in chroma so a shadow on the
     screen does not become part of the subject;
  3. **despill**: the subject's edge pixels are pulled back toward their own hue, which is
     what removes the colour fringe a naive key leaves on hair and leather;
  4. the matte is feathered a fraction of a pixel, never more.

    python3 tools/matte.py            # -> showreel/v4/assets/gen/matte-*.png
"""
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ffbin import ffmpeg

OUT = Path("showreel/v4/assets/gen")
DS = 2


def fit_screen(img: np.ndarray, screen_hue: str) -> tuple[np.ndarray, np.ndarray]:
    """Model the backdrop and return (model, candidate mask of screen pixels)."""
    small = cv2.resize(img, (img.shape[1] // DS, img.shape[0] // DS), cv2.INTER_AREA).astype(np.float32)
    h, w = small.shape[:2]
    g = small.mean(axis=2)
    mu = cv2.boxFilter(g, -1, (9, 9))
    sig = np.sqrt(np.clip(cv2.boxFilter(g * g, -1, (9, 9)) - mu * mu, 0, None))
    b, gg, r = [small[..., k] for k in range(3)]
    if screen_hue == "red":
        chroma = r - (gg + b) / 2
    elif screen_hue == "green":
        chroma = gg - (r + b) / 2
    else:
        chroma = np.zeros_like(g)
    cand = sig < 4.0
    if screen_hue in ("red", "green"):
        cand &= chroma > 18
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    X, Y = xx / w - 0.5, yy / h - 0.5
    basis = [(i, j) for i in range(4) for j in range(4 - i)]
    A = np.stack([(X ** i * Y ** j).ravel() for i, j in basis], 1)
    model = np.zeros_like(small)
    ok = cand.ravel()
    if ok.sum() < 500:
        raise SystemExit("no backdrop found — is this the right plate?")
    for c in range(3):
        coef, *_ = np.linalg.lstsq(A[ok], small[..., c].ravel()[ok], rcond=None)
        model[..., c] = (A @ coef).reshape(h, w)
    return model, cand


def key(img: np.ndarray, screen_hue: str = "red", tol: float = 16.0) -> np.ndarray:
    """RGBA matte of the subject on that backdrop."""
    small = cv2.resize(img, (img.shape[1] // DS, img.shape[0] // DS), cv2.INTER_AREA).astype(np.float32)
    model, _ = fit_screen(img, screen_hue)
    diff = small - model
    # chroma distance, plus a lightness term so a dark object is not called a shadow
    d = np.abs(diff).mean(axis=2)
    lum = np.abs(small.mean(axis=2) - model.mean(axis=2))
    raw = np.clip((np.maximum(d, lum * 0.6) - tol) / 24.0, 0, 1)
    m = (raw > 0.5).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    if n > 1:
        keep = np.zeros_like(m)
        for k in 1 + np.argsort(st[1:, 4])[::-1][:3]:
            if st[k, 4] > 0.004 * m.size:
                keep[lab == k] = 1
        m = keep
    # the matte follows the distance field, so edges land where the picture's do
    alpha_s = cv2.GaussianBlur(raw * (m > 0), (0, 0), 0.8)
    alpha = cv2.resize(alpha_s, (img.shape[1], img.shape[0]), cv2.INTER_LINEAR)
    alpha = np.clip((alpha - 0.18) / 0.64, 0, 1)
    rgb = img.astype(np.float32)
    # despill: at partial alpha, replace the backdrop's contribution with the subject's own
    a3 = alpha[..., None]
    unscreen = np.clip((rgb - model_up(model, img) * (1 - a3)) / np.maximum(a3, 1e-3), 0, 255)
    mix = np.clip((alpha - 0.05) * 3.2, 0, 1)[..., None]
    out_rgb = rgb * (1 - mix) + unscreen * mix
    return np.dstack([np.clip(out_rgb, 0, 255), alpha * 255]).astype(np.uint8)


def model_up(model_small: np.ndarray, img: np.ndarray) -> np.ndarray:
    return cv2.resize(model_small, (img.shape[1], img.shape[0]), cv2.INTER_CUBIC)


def show(name: str, rgba: np.ndarray) -> None:
    a = rgba[..., 3].astype(np.float32) / 255.0
    checker = (np.indices(a.shape).sum(axis=0) // 26 % 2 * 42 + 96).astype(np.float32)
    comp = rgba[..., :3].astype(np.float32) * a[..., None] + checker[..., None] * (1 - a[..., None])
    h = 420
    w = int(comp.shape[1] * h / comp.shape[0])
    cv2.imwrite(f"analysis/v4-build/key-{name}.png", cv2.resize(comp.astype(np.uint8), (w, h)))
    print(f"  {name:10s} {rgba.shape[1]}x{rgba.shape[0]}  coverage {a.mean():.2f}  "
          f"soft edge {float(((a > 0.05) & (a < 0.95)).mean()):.3f}")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [("hero", "showreel/v4/assets/plate-cta-hero.png", "red"),
            ("bag", "showreel/v4/assets/plate-bag-green.png", "green"),
            ("stool", "showreel/v4/assets/plate-bag-stool.png", "storm"),
            ("hands", "showreel/v4/assets/plate-hands-red.png", "red")]
    for name, src, hue in jobs:
        img = cv2.imread(src, cv2.IMREAD_UNCHANGED)[..., :3]
        rgba = key(img, hue)
        cv2.imwrite(str(OUT / f"matte-{name}.png"), rgba)
        show(name, rgba)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
