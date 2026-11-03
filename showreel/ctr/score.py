"""Explainable thumbnail scoring.

No black boxes: every number is a measurement with a documented ideal band, and the
weights are printed alongside the score so a client can argue with them.

The single most predictive metric here is `mobile_survival`: a thumbnail is judged at
~168x94 px in a phone feed, so we downsample to exactly that, blow it back up, and
correlate with the original. If the shape does not survive that round trip, the idea is
too detailed to work, no matter how good it looks at full size.
"""
from __future__ import annotations

import numpy as np
from PIL import Image

FEED_W, FEED_H = 168, 94          # YouTube mobile feed thumbnail
SAFE = 0.05                       # title-safe margin
BADGE_ZONE = (0.80, 1.0, 0.86, 1.0)   # bottom-right: duration overlay

WEIGHTS = {
    "mobile_survival": 0.30,
    "contrast": 0.20,
    "focal_gravity": 0.20,
    "palette_discipline": 0.15,
    "accent_presence": 0.15,
}


def _luma(im: Image.Image) -> np.ndarray:
    a = np.asarray(im.convert("RGB"), dtype=np.float64) / 255.0
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def _resize(a: np.ndarray, size) -> np.ndarray:
    return np.asarray(Image.fromarray(a).resize(size, Image.LANCZOS), dtype=np.float64)


def _corr(a: np.ndarray, b: np.ndarray) -> float:
    a = a.ravel() - a.mean()
    b = b.ravel() - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d else 0.0


def _band(value: float, lo: float, hi: float, soft: float) -> float:
    """1.0 inside [lo, hi], falling to 0 over `soft` outside it."""
    if lo <= value <= hi:
        return 1.0
    d = lo - value if value < lo else value - hi
    return max(0.0, 1.0 - d / soft)


def metrics(im: Image.Image) -> dict:
    w, h = im.size
    g = _luma(im)

    # 1. feed survival — downsample to the real feed size and correlate back
    small = _resize(g, (FEED_W, FEED_H))
    back = _resize(small, (w, h))
    survival = _corr(g, back)

    # 2. contrast — normalised RMS luminance spread
    contrast = float(g.std() * 2.2)          # 0.45 std ~= full marks

    # 3. focal gravity — where the detail lives. Good thumbs load the centre-left
    #    (text) and centre-right (face) and keep the outer frame quiet.
    gy, gx = np.gradient(g)
    edge = np.hypot(gx, gy)
    cw = edge[int(h * 0.12):int(h * 0.88), int(w * 0.05):int(w * 0.95)]
    border = edge.sum() - cw.sum()
    focal = float(cw.sum() / (edge.sum() + 1e-9))

    # 4. palette discipline — how many distinct hues fight for attention
    rgb = np.asarray(im.convert("RGB"), dtype=np.float64) / 255.0
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    sat = (mx - mn) / (mx + 1e-6)
    vivid = sat > 0.35
    if vivid.sum() > 0:
        hue = _hue(rgb)[vivid]
        hist, _ = np.histogram(hue, bins=18, range=(0, 360))
        p = hist / hist.sum()
        p = p[p > 0]
        entropy = float(-(p * np.log2(p)).sum() / np.log2(18))     # 0..1
    else:
        entropy = 0.0
    accent = float(vivid.mean())                                    # share of vivid pixels

    # 5. legibility of the badge zone — keep it clean for the duration overlay
    x0, x1, y0, y1 = BADGE_ZONE
    badge_var = float(g[int(h * y0):int(h * y1), int(w * x0):int(w * x1)].std())

    return {
        "mobile_survival": survival,
        "contrast": contrast,
        "focal_gravity": focal,
        "palette_entropy": entropy,
        "accent_presence": accent,
        "badge_zone_busy": badge_var,
    }


def _hue(rgb: np.ndarray) -> np.ndarray:
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4))
    return (h * 60.0) % 360.0


def score_image(im: Image.Image) -> dict:
    m = metrics(im)
    sub = {
        "mobile_survival": 100 * _band(m["mobile_survival"], 0.86, 1.0, 0.22),
        "contrast":        100 * min(1.0, m["contrast"] / 0.45),
        "focal_gravity":   100 * _band(m["focal_gravity"], 0.55, 0.85, 0.30),
        "palette_discipline": 100 * _band(m["palette_entropy"], 0.0, 0.55, 0.45),
        "accent_presence": 100 * _band(m["accent_presence"], 0.02, 0.22, 0.12),
    }
    total = sum(WEIGHTS[k] * v for k, v in sub.items())
    fails = []
    if m["mobile_survival"] < 0.70:
        fails.append("does not survive the 168x94 feed downsample")
    if m["badge_zone_busy"] > 0.34:
        fails.append("bottom-right is busy; the duration overlay will collide")
    return {
        "score": round(total, 1),
        "grade": _grade(total),
        "subscores": {k: round(v, 1) for k, v in sub.items()},
        "raw": {k: round(v, 4) for k, v in m.items()},
        "hard_fails": fails,
    }


def _grade(s: float) -> str:
    return "A" if s >= 85 else "B" if s >= 72 else "C" if s >= 58 else "D"


def rank(items: dict) -> list:
    """items: {name: PIL.Image} -> ranked list of (name, report)."""
    rows = [(n, score_image(im)) for n, im in items.items()]
    return sorted(rows, key=lambda r: -r[1]["score"])
