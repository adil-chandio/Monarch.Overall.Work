"""Thumbnail forensics: what the winners' faces, colours and text actually do.

YouTube serves every thumbnail at five sizes. Fetching `hqdefault` (480x360) and
`maxresdefault` (1280x720) is a public HTTP GET, so this works with no key and no API.

What is measured, and what each measurement is for:

  face_share        fraction of skin-tone-ish pixels in the upper half. Crude, but across
                    a channel's winners it tracks "there is a human in this thumbnail".
  accent            the dominant non-neutral colour + its share. Winners are usually
                    one-hue, not five.
  contrast          luminance spread. A thumbnail's job is to survive a crowded feed.
  text_likeness     edge density in the two horizontal bands where burned-in text lives,
                    and a proxy text height instead of pretending to OCR.
  face_ratio        share of the last N thumbnails that contain a face. A channel-level
                    consistency signal: consistency beats novelty in a feed.

Not OCR, not face recognition, not a classification model. Every number here is an
image statistic with a stated purpose, because a black box would just give us another
opinion to argue with.
"""
from __future__ import annotations

import io
import statistics

import numpy as np

from . import http

SIZES = ("maxresdefault", "sddefault", "hqdefault")


def fetch(video_id: str) -> tuple[np.ndarray | None, str]:
    """Return (RGB float array or None, which size worked)."""
    for size in SIZES:
        try:
            raw = http.get(f"https://i.ytimg.com/vi/{video_id}/{size}.jpg", ttl=86400 * 14)
        except Exception:
            continue
        try:
            from PIL import Image
            im = Image.open(io.BytesIO(raw)).convert("RGB")
            if min(im.size) < 200:
                continue
            return np.asarray(im, dtype=np.float32) / 255.0, size
        except Exception:
            continue
    return None, ""


def _luma(a: np.ndarray) -> np.ndarray:
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def _skin_mask(a: np.ndarray) -> np.ndarray:
    """Wide, deliberately permissive skin-tone band — with the neutral-grey trap closed.

    A pure CbCr skin test passes any mid-grey (r=g=b gives cb=cr=128), which made a bone
    background read as 65% "face". So saturation is required too, plus a low luma floor
    that still catches very dark portraits. This measures *presence of a human*, never
    identity; a false positive on sand-coloured b-roll costs a little accuracy, while a
    real face model would cost privacy and licensing.
    """
    r, g, b = a[..., 0] * 255, a[..., 1] * 255, a[..., 2] * 255
    cb = 128 - 0.168736 * r - 0.331264 * g + 0.5 * b
    cr = 128 + 0.5 * r - 0.418688 * g - 0.081312 * b
    y = _luma(a)
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = (mx - mn) / (mx + 1e-6)
    warm = r >= g * 0.92                                     # skin is red >= green
    return (
        (cb > 74) & (cb < 133) & (cr > 136) & (cr < 176)
        & (sat > 0.22) & (sat < 0.75)
        & (y > 0.06) & warm
    )


def analyse(a: np.ndarray, size: str = "") -> dict:
    h, w = a.shape[:2]
    y = _luma(a)
    top = a[: h // 2]
    skin_top = float(_skin_mask(top).mean())
    skin_all = float(_skin_mask(a).mean())

    # colour: ignore near-neutral pixels, then measure concentration of the rest
    mx = a.max(axis=2)
    mn = a.min(axis=2)
    sat = (mx - mn) / (mx + 1e-6)
    vivid = sat > 0.30
    accent_share = float(vivid.mean())
    dominant = None
    if vivid.sum() > 50:
        px = (a[vivid] * 255).astype(np.int32)
        q = (px // 32)
        keys, counts = np.unique(q, axis=0, return_counts=True)
        pick = keys[counts.argmax()]
        sel = px[(q == pick).all(axis=1)]
        if len(sel):
            rgb = sel.mean(axis=0).astype(int)
            dominant = {"hex": "#%02x%02x%02x" % tuple(rgb), "share": round(float(counts.max() / len(px)), 3)}
            accent_share = float(counts.max() / len(px))

    # text-likeness: horizontal edge energy in the bands where burned-in text sits
    gy, gx = np.gradient(y)
    edge = np.abs(gy) + np.abs(gx)
    bands = {
        "upper": edge[int(h * 0.62):int(h * 0.82)],
        "lower": edge[int(h * 0.82):int(h * 0.98)],
        "centre": edge[int(h * 0.30):int(h * 0.60)],
    }
    textness = {k: round(float(v.mean()) * 100, 2) for k, v in bands.items()}
    rows_with_text = int((np.abs(gy[int(h * 0.62):int(h * 0.98)]).mean(axis=1) > np.abs(gy).mean() * 1.15).sum())

    return {
        "size": size, "w": w, "h": h,
        "face_share": round(skin_all, 3),
        "face_present": bool(skin_top > 0.012),
        "face_upper_half": round(skin_top, 3),
        "contrast": round(float(y.std()), 3),
        "brightness": round(float(y.mean()), 3),
        "accent_share": round(accent_share, 3),
        "dominant": dominant,
        "text_edge_energy": textness,
        "text_row_span": rows_with_text,
        "busy": round(float(edge.mean()) * 100, 2),
    }


def channel_fingerprint(video_ids: list[str], sample: int = 24) -> dict:
    """Aggregate the last N thumbnails into a channel-level style profile."""
    out = []
    for vid in video_ids[:sample]:
        arr, size = fetch(vid)
        if arr is None:
            continue
        rec = analyse(arr, size)
        rec["id"] = vid
        out.append(rec)
    if not out:
        return {"status": "unavailable", "detail": "could not fetch any thumbnails (network or size)"}
    # threshold is not 0: a heavily graded portrait (red rim light, tight mask) lands
    # around 1.5-5 % of the frame, so 0.012 is "a human is present", not "a tan wall"
    faces = [r["face_upper_half"] > 0.012 for r in out]
    hues = [r["dominant"]["hex"] for r in out if r.get("dominant")]
    return {
        "status": "ok", "n": len(out),
        "face_rate": round(sum(faces) / len(out), 2),
        "avg_contrast": round(statistics.mean(r["contrast"] for r in out), 3),
        "avg_busy": round(statistics.mean(r["busy"] for r in out), 2),
        "text_band_energy": round(statistics.mean(r["text_edge_energy"]["lower"] for r in out), 2),
        "top_hexes": sorted({h: hues.count(h) for h in hues}.items(), key=lambda kv: -kv[1])[:5],
        "samples": out[:6],
        "reading": (
            "face-led channel: people are the product" if sum(faces) / len(out) > 0.5
            else "graphic-led channel: the idea is the product"
        ),
    }
