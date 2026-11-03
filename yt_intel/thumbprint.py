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
    # Vivid, not merely dark, and grouped by HUE. The first version quantised RGB into
    # 32-step cubes and took the biggest cube — on twelve real thumbnails that returned
    # `#0c1213` ten times over, because "darkest corner of the frame" wins that vote in
    # almost every thumbnail ever made. A one-hue accent is what the docstring promises, so
    # the grouping is hue-based and pixels below 0.22 luma are excluded: near-black carries no
    # hue information worth voting on.
    vivid = (sat > 0.30) & (_luma(a) > 0.22)
    accent_share = float(vivid.mean())
    dominant = None
    if vivid.sum() > 50:
        px = (a[vivid] * 255).astype(np.int32)
        r, g, b = px[:, 0], px[:, 1], px[:, 2]
        mxv = px.max(axis=1)
        mnv = px.min(axis=1)
        d = (mxv - mnv).astype(np.float64)
        d[d == 0] = 1.0
        hue = np.zeros(len(px))
        red = mxv == r
        green = (mxv == g) & ~red
        blue = (mxv == b) & ~red & ~green
        hue[red] = (60 * ((g[red] - b[red]) / d[red])) % 360
        hue[green] = 60 * ((b[green] - r[green]) / d[green]) + 120
        hue[blue] = 60 * ((r[blue] - g[blue]) / d[blue]) + 240
        bins = (hue // 15).astype(np.int32) % 24
        names, counts = np.unique(bins, return_counts=True)
        # require a real cluster: one 15-degree sliver of a random gradient is not an accent
        if counts.max() >= max(50, 0.04 * len(px)):
            pick = names[counts.argmax()]
            sel = px[bins == pick]
            rgb = sel.mean(axis=0).astype(int)
            dominant = {
                "hex": "#%02x%02x%02x" % tuple(rgb),
                "share": round(float(counts.max() / len(px)), 3),
                "hue_deg": int(pick * 15 + 7),
            }
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


FAMILY_NAMES = ("red", "amber", "green", "teal", "blue", "magenta")


def _hue_families(hues: list[int]) -> list:
    """Count thumbnails per 60-degree hue family. Sums to at most len(hues)."""
    buckets = [0] * 6
    for h in hues:
        buckets[(h % 360) // 60] += 1
    named = [(FAMILY_NAMES[i], n) for i, n in enumerate(buckets) if n]
    return sorted(named, key=lambda kv: (-kv[1], kv[0]))


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
    fam = [r["dominant"]["hue_deg"] for r in out if r.get("dominant")]
    hexes = [r["dominant"]["hex"] for r in out if r.get("dominant")]
    return {
        "status": "ok", "n": len(out),
        "face_rate": round(sum(faces) / len(out), 2),
        "avg_contrast": round(statistics.mean(r["contrast"] for r in out), 3),
        "avg_busy": round(statistics.mean(r["busy"] for r in out), 2),
        "text_band_energy": round(statistics.mean(r["text_edge_energy"]["lower"] for r in out), 2),
        # family = 60-degree bucket, named. Two thumbnails at #018afb and #0b7fd0 are the
        # same brand colour; counting exact hexes reported twelve accents with a count of one
        # each, which reads as "no house colour" for a channel that plainly has one.
        #
        # Keyed by BUCKET, not by the observed hue: the first version keyed by hue and counted
        # by bucket, so 22 degrees and 7 degrees appeared as two separate families with 6 each
        # out of 12 thumbnails — a total of 22 over a sample of 12.
        "hue_families": _hue_families(fam),
        "top_hexes": sorted({h: hexes.count(h) for h in hexes}.items(), key=lambda kv: -kv[1])[:5],
        "samples": out[:6],
        "reading": _reading(sum(faces) / len(out), _hue_families(fam), len(out)),
    }


def _reading(face_rate: float, families: list, n: int) -> str:
    """One sentence that a producer can act on. States the sample in the sentence itself."""
    face = ("face-led: people are the product" if face_rate > 0.5
            else "graphic-led: the idea is the product")
    if families and families[0][1] >= 0.4 * n:
        house = f"house colour is {families[0][0]} ({families[0][1]}/{n} thumbnails)"
    elif families:
        house = f"no single house colour — {families[0][0]} leads at only {families[0][1]}/{n}"
    else:
        house = "no measurable accent colour"
    return f"{face}; {house}"
