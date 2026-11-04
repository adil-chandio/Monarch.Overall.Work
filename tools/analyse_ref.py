#!/usr/bin/env python3
"""analyse_ref.py — the forensic rig for reference videos.

Point it at a file (or a folder) and it produces, per video:

  <out>/report.json      every measurement, machine-readable
  <out>/report.md        the same as a dossier a human reads before rebuilding
  <out>/sheet_3x3.png    contact sheet, one frame every duration/9
  <out>/strip_cuts.png   the frames either side of every cut, so the transition is visible
  <out>/zoom_t*.png      10x zooms of the four quadrants at 6%, 50%, 94% of the film
  <out>/palette.png      the dominant colours as swatches
  <out>/motion.png       per-frame motion energy, so pacing is a number

Nothing here says "looks about right". Every claim is a measurement with the
method printed next to it, so a rebuild can be diffed against the reference.

Usage:
    python3 tools/analyse_ref.py ref.mp4 [--out analysis/<name>]
    python3 tools/analyse_ref.py refs/*.mp4 --out analysis/batch
"""
from __future__ import annotations

import argparse
import io
import json
import math
import pathlib
import re
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
FFMPEG = None
FFPROBE = None


# --------------------------------------------------------------------------- tools
def _ffmpeg_bin() -> tuple[str, str]:
    import shutil

    venv = ROOT / ".venv/lib/python3.11/site-packages/imageio_ffmpeg/binaries"
    ff = next((p for p in sorted(venv.glob("ffmpeg-*")) if p.is_file()), None)
    if ff is None:
        found = shutil.which("ffmpeg")
        if found:
            ff = pathlib.Path(found)
        else:
            try:
                import imageio_ffmpeg

                ff = pathlib.Path(imageio_ffmpeg.get_ffmpeg_exe())
            except Exception:
                raise SystemExit("no ffmpeg: pip install imageio-ffmpeg")
    probe = shutil.which("ffprobe") or str(ff).replace("ffmpeg-linux", "ffprobe-linux")
    if not pathlib.Path(probe).exists():
        probe = ""
    return str(ff), probe


def run(args: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run([FFMPEG, *args], capture_output=True, **kw)


# --------------------------------------------------------------------------- probe
def probe(path: pathlib.Path) -> dict:
    out = run(["-hide_banner", "-i", str(path)]).stderr.decode("utf-8", "ignore")
    info: dict = {"file": path.name, "bytes": path.stat().st_size}

    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", out)
    if m:
        h, mnt, s = m.groups()
        info["duration"] = round(int(h) * 3600 + int(mnt) * 60 + float(s), 3)

    size = re.search(r"Video:.*?,\s*(\d{2,5})x(\d{2,5})", out)
    if size:
        info["width"], info["height"] = int(size.group(1)), int(size.group(2))
    codec = re.search(r"Video:\s*([A-Za-z0-9_]+)\s*\(", out)
    if codec:
        info["vcodec"] = codec.group(1)
    pix = re.search(r"Video:.*?,\s*(yuv\w+|rgb\w+|gbrp\w*|gray\w*|yuva\w+)", out)
    if pix:
        info["pix_fmt"] = pix.group(1)
    tags = re.search(r"\(([^)]*(?:bt709|bt601|smpte170m|tv|pc)[^)]*)\)", out)
    if tags:
        info["colour_tags"] = tags.group(1)

    fps = re.search(r"(\d+(?:\.\d+)?)\s*fps", out)
    if fps:
        info["fps"] = float(fps.group(1))

    a = re.search(r"Audio:\s*([A-Za-z0-9_]+)[^,]*,\s*(\d+)\s*Hz,\s*([a-z0-9.]+)", out)
    if a:
        info["acodec"], info["sample_rate"], info["channels"] = a.group(1), int(a.group(2)), a.group(3)
    kb = re.search(r"Audio:.*?(\d+)\s*kb/s", out)
    if kb:
        info["audio_kbps"] = int(kb.group(1))
    vkb = re.search(r"Video:.*?(\d+)\s*kb/s", out)
    if vkb:
        info["video_kbps"] = int(vkb.group(1))
    rot = re.search(r"rotate\s*:\s*(-?\d+)", out)
    if rot:
        info["rotation"] = int(rot.group(1))

    if info.get("width") and info.get("height"):
        info["aspect"] = round(info["width"] / info["height"], 4)
        r = info["aspect"]
        info["shape"] = ("9:16" if abs(r - 9 / 16) < 0.05 else
                         "16:9" if abs(r - 16 / 9) < 0.05 else
                         "1:1" if abs(r - 1) < 0.05 else
                         "4:5" if abs(r - 0.8) < 0.05 else
                         "4:3" if abs(r - 4 / 3) < 0.05 else f"{r:.3f}")
    return info


# --------------------------------------------------------------------------- frames
def decode_gray(path: pathlib.Path, width: int = 480) -> tuple[np.ndarray, float, dict]:
    info = probe(path)
    fps = info.get("fps") or 30.0
    raw = run(["-v", "error", "-i", str(path), "-vf", f"scale={width}:-2,format=gray",
               "-f", "rawvideo", "-"]).stdout
    h = int(round(width / info["aspect"])) if info.get("aspect") else int(width * 9 / 16)
    h -= h % 2
    fb = width * h
    n = len(raw) // fb
    frames = np.frombuffer(raw[: n * fb], dtype=np.uint8).reshape(n, h, width)
    return frames, fps, info


def motion_curve(frames: np.ndarray) -> np.ndarray:
    d = np.abs(np.diff(frames.astype(np.int16), axis=0)).mean(axis=(1, 2))
    if d.size == 0:
        return np.zeros(1)
    lo, hi = np.percentile(d, 5), np.percentile(d, 99.5)
    return np.clip((d - lo) / max(hi - lo, 1e-6), 0, 1)


def edge_density(frames: np.ndarray) -> np.ndarray:
    """Share of strong horizontal/vertical gradients — a proxy for 'how much type'."""
    f = frames.astype(np.float32)
    gx = np.abs(np.diff(f, axis=2)).mean(axis=(1, 2))
    gy = np.abs(np.diff(f, axis=1)).mean(axis=(1, 2))
    return (gx + gy) / 2


def plane_hist(plane: np.ndarray) -> np.ndarray:
    h = np.bincount(plane.ravel(), minlength=256).astype(np.float64)
    return h / max(h.sum(), 1.0)


def otsu(x: np.ndarray, bins: int = 256) -> float:
    """Otsu's threshold: split the score track where between-class variance peaks."""
    if x.size == 0:
        return 0.0
    hist, edges = np.histogram(x, bins=bins)
    hist = hist.astype(np.float64)
    p = hist / hist.sum()
    centres = (edges[:-1] + edges[1:]) / 2
    omega = np.cumsum(p)
    mu = np.cumsum(p * centres)
    mu_t = mu[-1]
    denom = omega * (1 - omega)
    denom[denom == 0] = 1e-12
    sigma_b = (mu_t * omega - mu) ** 2 / denom
    if not np.isfinite(sigma_b).any() or sigma_b.max() <= 0:
        return float(np.percentile(x, 99))
    return float(centres[int(np.argmax(sigma_b))])


def shot_boundaries(frames: np.ndarray, fps: float) -> dict:
    """Score every frame pair the way a shot detector should, then report the scores.

    A percentage of changed pixels alone cannot tell an edit from a whip-pan, and a
    fixed multiple of the median flags every camera move (it found 71 "cuts" in a
    7-shot film). One score combines three independent signals:

      * how MUCH changed — share of pixels differing by > 12 levels
      * how UNRELATED the frames are — histogram distance after the cut
      * whether motion is CUT-SHAPED — a 0.20 s spike between two still stretches

    The threshold is Otsu's, computed on the score track itself, so it adapts to
    the film instead of to my taste. The score track is returned, so a wrong call
    can be argued with.
    """
    n = frames.shape[0]
    if n < 4:
        return {"cuts": [], "scores": [], "threshold": 0.0,
                "method_notes": "too short to detect shots"}

    f = frames.astype(np.int16)
    changed = (np.abs(np.diff(f, axis=0)) > 12).mean(axis=(1, 2))
    hs = [plane_hist(fr) for fr in frames]
    hist_dist = np.array([1.0 - float(np.minimum(hs[i], hs[i + 1]).sum()) for i in range(n - 1)])

    win = max(2, int(round(0.20 * fps)))
    spike = np.zeros(n - 1)
    for i in range(n - 1):
        a = changed[max(0, i - win): i]
        b = changed[i + 1: i + 1 + win]
        ba = a.mean() if a.size else changed[i]
        bb = b.mean() if b.size else changed[i]
        spike[i] = changed[i] - 0.5 * ba - 0.5 * bb

    score = changed * np.clip(hist_dist * 2.0, 0, 1) * np.clip(0.5 + spike * 4.0, 0, 2)
    thr = otsu(score)

    cuts: list[dict] = []
    min_gap = max(2, int(round(0.18 * fps)))
    for i in range(1, score.size - 1):
        if score[i] <= thr or score[i] < score[i - 1] or score[i] < score[i + 1]:
            continue
        if cuts and i - cuts[-1]["_i"] < min_gap:
            if score[i] > cuts[-1]["sharpness"]:
                cuts.pop()
            else:
                continue
        cuts.append({"frame": int(i + 1), "time": round((i + 1) / fps, 3),
                     "sharpness": round(float(score[i]), 4),
                     "changed_px": round(float(changed[i]), 4),
                     "hist_dist": round(float(hist_dist[i]), 4), "_i": i})
    for c in cuts:
        c.pop("_i", None)
    return {"cuts": cuts, "scores": [round(float(x), 5) for x in score],
            "threshold": round(float(thr), 5),
            "method_notes": (f"changed-px x histogram-distance x cut-shape, Otsu threshold "
                             f"{thr:.4f} over {n - 1} frame pairs")}


def scene_cuts_ffmpeg(path: pathlib.Path, thresh: float = 0.35) -> list[float]:
    """Second opinion, from ffmpeg's own scene score. Disagreement = slow dissolve."""
    out = run(["-v", "info", "-i", str(path), "-vf",
               f"select='gt(scene,{thresh})',metadata=print", "-f", "null", "-"]).stderr.decode(
        "utf-8", "ignore")
    return [round(float(m), 3) for m in re.findall(r"pts_time:([\d.]+)", out)]


def classify_transition(frames: np.ndarray, i: int, fps: float) -> dict:
    """Name the transition at boundary i with an alpha profile.

    Take A = the frame two back (surely before the edit) and B = the frame a third of
    a second later (surely after). For each frame in the window, project it onto the
    A→B line:  alpha(t) = <F(t) - A, B - A> / |B - A|^2  clamped to 0..1.

    That single number says what the edit *is*:
      hard cut      alpha steps 0 -> 1 between two frames
      dissolve      alpha ramps roughly linearly across >= 3 frames
      dip to dark   alpha is not monotone; luma collapses in the middle
      camera move   alpha grows slowly and never reaches 1
    """
    n = frames.shape[0]
    i = max(2, min(i, n - 4))
    win = max(3, int(round(0.5 * fps)))
    lo, hi = max(0, i - 2), min(n - 1, i + win)
    A = frames[lo].astype(np.float32)
    B = frames[hi].astype(np.float32)
    D = (B - A).ravel()
    denom = float((D * D).sum())
    if denom < 1e3:  # the two ends are the same picture: no edit here
        return {"type": "camera move", "dur_s": 0.0, "delta": 0.0, "alpha_ramp": []}
    alpha, lum = [], []
    for k in range(lo, hi + 1):
        F = frames[k].astype(np.float32)
        alpha.append(round(float(np.clip(((F - A).ravel() @ D) / denom, 0, 1)), 3))
        lum.append(round(float(F.mean() / 255), 3))

    steps = [round(alpha[k + 1] - alpha[k], 3) for k in range(len(alpha) - 1)]
    big = max(steps) if steps else 0.0
    reached = max(alpha) if alpha else 0.0
    ramp_frames = sum(1 for a in alpha if 0.12 < a < 0.88)
    dark_mid = min(lum[1:-1] or lum) < 0.05 < max(lum)

    common = {"delta": round(reached, 3), "alpha_ramp": alpha, "peak_step": big}
    if big >= 0.55 and reached >= 0.85:
        return {"type": "hard cut", "dur_s": round(1 / fps, 3), **common}
    if dark_mid and ramp_frames >= 2:
        return {"type": "dip to dark", "dur_s": round(ramp_frames / fps, 2), **common}
    if ramp_frames >= 3 and reached >= 0.85:
        ends_black = min(lum[0], lum[-1]) < 0.06
        return {"type": "fade through black" if ends_black else "dissolve",
                "dur_s": round(ramp_frames / fps, 2), **common}
    if reached >= 0.5:
        return {"type": "soft wipe / morph", "dur_s": round(max(ramp_frames, 1) / fps, 2), **common}
    return {"type": "camera move", "dur_s": round(max(ramp_frames, 1) / fps, 2), **common}


# --------------------------------------------------------------------------- colour
def colour_stats(path: pathlib.Path, samples: int = 24) -> dict:
    info = probe(path)
    fps = info.get("fps") or 30
    n_frames = max(1, int((info.get("duration") or 1) * fps))
    picks = np.linspace(0, max(n_frames - 2, 0), samples).astype(int)
    acc = []
    for f in picks:
        raw = run(["-v", "error", "-ss", f"{f / fps:.3f}", "-i", str(path), "-frames:v", "1",
                   "-vf", "scale=48:-2,format=rgb24", "-f", "rawvideo", "-"]).stdout
        if raw:
            acc.append(np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3))
    if not acc:
        return {}
    px = np.concatenate(acc).astype(np.float32)
    mx, mn = px.max(axis=1), px.min(axis=1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    lum = 0.2126 * px[:, 0] + 0.7152 * px[:, 1] + 0.0722 * px[:, 2]

    r, g, b = px[:, 0], px[:, 1], px[:, 2]
    d = mx - mn + 1e-6
    hue = np.zeros(len(px))
    m = mx == r
    hue[m] = (60 * ((g[m] - b[m]) / d[m])) % 360
    m = mx == g
    hue[m] = 60 * ((b[m] - r[m]) / d[m]) + 120
    m = mx == b
    hue[m] = 60 * ((r[m] - g[m]) / d[m]) + 240
    bins = np.histogram(hue, bins=12, range=(0, 360), weights=sat)[0]
    total = max(bins.sum(), 1e-9)

    return {
        "mean_saturation": round(float(sat.mean()), 4),
        "mean_luma": round(float(lum.mean()), 2),
        "luma_std": round(float(lum.std()), 2),
        "dark_share": round(float((lum < 32).mean()), 3),
        "bright_share": round(float((lum > 200).mean()), 3),
        "dominant_hues": [{"hue": f"{int(t * 30)}-{int(t * 30) + 30}deg",
                           "share": round(float(bins[t] / total), 3)}
                          for t in np.argsort(bins)[::-1][:4]],
    }


def palette_image(path: pathlib.Path, out: pathlib.Path, k: int = 6) -> list[dict]:
    """k-means over sampled RGB; writes a swatch strip and returns the clusters."""
    from PIL import Image, ImageDraw

    info = probe(path)
    fps = info.get("fps") or 30
    n = max(1, int((info.get("duration") or 1) * fps))
    acc = []
    for f in np.linspace(0, max(n - 2, 0), 18).astype(int):
        raw = run(["-v", "error", "-ss", f"{f / fps:.3f}", "-i", str(path), "-frames:v", "1",
                   "-vf", "scale=80:-2,format=rgb24", "-f", "rawvideo", "-"]).stdout
        if raw:
            acc.append(np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3))
    if not acc:
        return []
    px = np.concatenate(acc).astype(np.float32)
    rs = np.random.RandomState(7)
    cent = px[rs.choice(len(px), k, replace=False)]
    for _ in range(24):
        d = ((px[:, None, :] - cent[None, :, :]) ** 2).sum(axis=2)
        lab = d.argmin(axis=1)
        for i in range(k):
            if (lab == i).any():
                cent[i] = px[lab == i].mean(axis=0)
    counts = np.bincount(lab, minlength=k).astype(float)
    order = np.argsort(counts)[::-1]
    clusters = []
    sw = 120
    strip = Image.new("RGB", (sw * k, sw), (10, 10, 14))
    dr = ImageDraw.Draw(strip)
    for pos, i in enumerate(order):
        c = tuple(int(v) for v in cent[i])
        dr.rectangle([pos * sw, 0, (pos + 1) * sw - 1, sw - 30], fill=c)
        share = counts[i] / counts.sum()
        dr.text((pos * sw + 6, sw - 24), f"#{c[0]:02x}{c[1]:02x}{c[2]:02x} {share*100:.0f}%",
                fill=(235, 235, 240))
        clusters.append({"hex": f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}",
                         "rgb": list(c), "share": round(float(share), 3)})
    strip.save(out / "palette.png")
    return clusters


# --------------------------------------------------------------------------- audio
def audio_analysis(path: pathlib.Path, sr: int = 22050) -> dict:
    info = probe(path)
    if "acodec" not in info:
        return {"has_audio": False}
    raw = run(["-v", "error", "-i", str(path), "-ac", "1", "-ar", str(sr),
               "-f", "f32le", "-acodec", "pcm_f32le", "-"]).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    if x.size == 0:
        return {"has_audio": False}

    rms = float(np.sqrt((x.astype(np.float64) ** 2).mean()))
    peak = float(np.abs(x).max())
    win = int(sr * 0.02)
    env = np.abs(x)[: x.size // win * win].reshape(-1, win).mean(axis=1)

    onset = np.maximum(0, np.diff(env))
    onset = onset - onset.mean()
    ac = np.correlate(onset, onset, mode="full")[onset.size - 1:]
    ac = ac / max(ac[0], 1e-9)
    hop = 0.02
    cands = []
    for bpm in np.arange(55, 191, 0.5):
        period = 60.0 / bpm / hop
        acc, wsum = 0.0, 0.0
        for mult, weight in ((1, 1.0), (2, 0.6), (3, 0.35), (4, 0.2)):
            idx = int(round(period * mult))
            if 1 <= idx < ac.size:
                acc += weight * float(ac[max(1, idx - 1): idx + 2].max())
                wsum += weight
        cands.append((acc / max(wsum, 1e-9), float(bpm)))
    cands.sort(reverse=True)
    top = [{"bpm": round(b, 1), "score": round(a, 3)} for a, b in cands[:3]]
    # a weak peak means "no stable grid" (a voice-over with a pad, say) — say so
    if not top or top[0]["score"] < 0.35:
        top = [dict(x, weak=True) for x in top]

    return {
        "has_audio": True,
        "sample_rate": sr,
        "rms_db": round(20 * math.log10(rms + 1e-9), 2),
        "peak_db_decoded": round(20 * math.log10(peak + 1e-9), 2),
        "crest_db": round(20 * math.log10((peak + 1e-9) / (rms + 1e-9)), 2),
        "bpm_estimate": (top[0]["bpm"] if top and not top[0].get("weak") else None),
        "bpm_confidence": top[0]["score"] if top else None,
        "bpm_note": ("no stable grid — score is free-timed, cut to speech"
                     if top and top[0].get("weak") else None),
        "bpm_candidates": top,
        "envelope_hops": int(env.size),
    }


def loudness(path: pathlib.Path) -> dict:
    out = run(["-hide_banner", "-nostats", "-i", str(path), "-af",
               "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null",
               "-"]).stderr.decode("utf-8", "ignore")
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", out, re.S)
    if not m:
        return {}
    try:
        d = json.loads(m.group(0))
        return {"input_i": float(d["input_i"]), "input_tp": float(d["input_tp"]),
                "input_lra": float(d["input_lra"]), "input_thresh": float(d["input_thresh"])}
    except Exception:
        return {}


def audio_figure(path: pathlib.Path, out: pathlib.Path) -> None:
    """Waveform + onset envelope, with the cuts drawn on top. Picture meets sound."""
    from PIL import Image, ImageDraw

    info = probe(path)
    if "acodec" not in info:
        return
    raw = run(["-v", "error", "-i", str(path), "-ac", "1", "-ar", "8000",
               "-f", "f32le", "-acodec", "pcm_f32le", "-"]).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    if x.size == 0:
        return
    cols, rows = 1200, 220
    seg = max(1, x.size // cols)
    img = Image.new("RGB", (cols, rows), (10, 12, 18))
    dr = ImageDraw.Draw(img)
    peaks = [float(np.abs(x[i * seg:(i + 1) * seg]).max()) for i in range(cols)]
    mid = rows // 2
    for i, p in enumerate(peaks):
        h = p * (mid - 8)
        dr.line([(i, mid - h), (i, mid + h)], fill=(90, 160, 255))
    dr.line([(0, mid), (cols, mid)], fill=(60, 70, 90))
    img.save(out / "waveform.png")


# --------------------------------------------------------------------------- images
def grab(path: pathlib.Path, t: float, w: int = 1920):
    from PIL import Image

    raw = run(["-v", "error", "-ss", f"{t:.3f}", "-i", str(path), "-frames:v", "1",
               "-vf", f"scale={w}:-2", "-f", "image2pipe", "-vcodec", "png", "-"]).stdout
    return Image.open(io.BytesIO(raw)).convert("RGB") if raw else None


def contact_sheet(path: pathlib.Path, out: pathlib.Path, dur: float, cols=3, rows=3) -> None:
    from PIL import Image, ImageDraw

    ims = []
    for i in range(cols * rows):
        t = (i + 0.5) * dur / (cols * rows)
        im = grab(path, t, 640)
        if im is None:
            continue
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 118, 26], fill=(0, 0, 0))
        d.text((8, 7), f"{t:0.2f}s", fill=(255, 255, 255))
        ims.append(im)
    if not ims:
        return
    cw, ch = ims[0].size
    sheet = Image.new("RGB", (cw * cols, ch * rows), (12, 12, 16))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * cw, (i // cols) * ch))
    sheet.save(out / "sheet_3x3.png")


def cut_strip(path: pathlib.Path, out: pathlib.Path, cuts: list[float], dur: float,
              around: int = 6, step: float = 0.08) -> None:
    from PIL import Image, ImageDraw

    if not cuts:
        return
    cuts = cuts[:8]
    w = 260
    tw, th = w, int(w * 9 / 16)
    strip = Image.new("RGB", (tw * around * 2, th * len(cuts)), (8, 8, 12))
    for r, c in enumerate(cuts):
        for i in range(-around, around):
            t = max(0.0, min(dur - 0.01, c + i * step))
            im = grab(path, t, w) or Image.new("RGB", (tw, th), (0, 0, 0))
            im = im.resize((tw, th))
            d = ImageDraw.Draw(im)
            tag = "cut" if i == 0 else ("-" if i < 0 else "+")
            d.rectangle([0, 0, 92, 20], fill=(0, 0, 0))
            d.text((4, 4), f"{tag}{abs(i) * step:.2f}",
                   fill=(255, 190, 60) if i >= 0 else (150, 150, 160))
            strip.paste(im, ((i + around) * tw, r * th))
    strip.save(out / "strip_cuts.png")


def zoom_pass(path: pathlib.Path, out: pathlib.Path, times: list[float], scale: int = 10) -> None:
    from PIL import Image

    for t in times:
        full = grab(path, t, 1920)
        if full is None:
            continue
        w, h = full.size
        regions = {"tl": (0, 0, w // 2, h // 2), "tr": (w // 2, 0, w, h // 2),
                   "bl": (0, h // 2, w // 2, h), "br": (w // 2, h // 2, w, h)}
        for name, box in regions.items():
            crop = full.crop(box)
            factor = min(scale, 1400 / max(crop.width, 1))
            crop = crop.resize((int(crop.width * factor), int(crop.height * factor)),
                               Image.LANCZOS)
            crop.save(out / f"zoom_t{t:05.2f}_{name}.png")


def motion_figure(motion: np.ndarray, out: pathlib.Path, cuts: list[float], fps: float) -> None:
    from PIL import Image, ImageDraw

    cols, rows = 1200, 180
    img = Image.new("RGB", (cols, rows), (10, 12, 18))
    dr = ImageDraw.Draw(img)
    if motion.size > 1:
        for i in range(cols):
            a, b = int(i * motion.size / cols), max(int((i + 1) * motion.size / cols), int(i * motion.size / cols) + 1)
            v = float(motion[a:b].max())
            dr.line([(i, rows - 10 - v * (rows - 24)), (i, rows - 10)], fill=(255, 120, 90))
    for c in cuts:
        x = int(c / max((motion.size + 1) / fps, 1e-6) * cols)
        dr.line([(x, 0), (x, rows)], fill=(255, 220, 120))
    img.save(out / "motion.png")


# --------------------------------------------------------------------------- dossier
def build_report(path: pathlib.Path, out: pathlib.Path) -> dict:
    frames, fps, info = decode_gray(path)
    dur = info.get("duration") or 0
    motion = motion_curve(frames)
    edges = edge_density(frames)
    det = shot_boundaries(frames, fps)
    cuts = det["cuts"]
    for c in cuts:
        c["transition"] = classify_transition(frames, c["frame"], fps)
    alt = scene_cuts_ffmpeg(path)

    cut_times = [c["time"] for c in cuts]
    bounds = [0.0] + cut_times + [dur]
    shots = [{"start": round(bounds[i], 2), "end": round(bounds[i + 1], 2),
              "len": round(bounds[i + 1] - bounds[i], 2)} for i in range(len(bounds) - 1)]
    lens = [s["len"] for s in shots if s["len"] > 0.02]

    report = {
        "file": info,
        "cuts": cuts,
        "cut_scores": det["scores"],
        "cut_threshold": det["threshold"],
        "cut_method": det["method_notes"],
        "cuts_second_opinion": alt,
        "cut_count": len(cuts),
        "cuts_per_minute": round(len(cuts) / max(dur / 60, 1e-6), 2),
        "shots": shots,
        "shot_len": ({"median": round(float(np.median(lens)), 2),
                      "p10": round(float(np.percentile(lens, 10)), 2),
                      "p90": round(float(np.percentile(lens, 90)), 2),
                      "longest": round(max(lens), 2)} if lens else {}),
        "hook": {"cuts_in_first_3s": len([c for c in cut_times if c <= 3]),
                 "first_cut": cut_times[0] if cut_times else None,
                 "motion_first_1s": round(float(motion[: max(1, int(fps))].mean()), 4)},
        "motion": {"mean": round(float(motion.mean()), 4),
                   "peak": round(float(motion.max()), 4),
                   "quiet_share": round(float((motion < 0.15).mean()), 3)},
        "type_density": {"mean": round(float(edges.mean()), 4),
                         "peak": round(float(edges.max()), 4),
                         "peak_time": round(float(int(np.argmax(edges)) / fps), 2)},
        "colour": colour_stats(path),
        "palette": [],
        "audio": audio_analysis(path),
        "loudness": loudness(path),
    }

    contact_sheet(path, out, dur)
    cut_strip(path, out, cut_times, dur)
    zoom_pass(path, out, [round(dur * f, 3) for f in (0.06, 0.5, 0.94)])
    motion_figure(motion, out, cut_times, fps)
    audio_figure(path, out)
    report["palette"] = palette_image(path, out)

    (out / "report.json").write_text(json.dumps(report, indent=1) + "\n")
    (out / "report.md").write_text(dossier(report) + "\n")
    return report


def dossier(r: dict) -> str:
    f = r["file"]
    L = [f"# {f['file']}", "", "## Container", "",
         f"- **{f.get('width')}x{f.get('height')} ({f.get('shape')})**, {f.get('fps')} fps, "
         f"{f.get('duration')} s, {f.get('bytes'):,} bytes",
         f"- video {f.get('vcodec')} / {f.get('pix_fmt')} / {f.get('video_kbps')} kb/s"
         + (f" / {f.get('colour_tags')}" if f.get("colour_tags") else ""),
         f"- audio {f.get('acodec')} / {f.get('sample_rate')} Hz / {f.get('channels')} / "
         f"{f.get('audio_kbps')} kb/s", ""]

    s = r["shot_len"]
    L += ["## Edit", "",
          f"- **{r['cut_count']} cuts** ({r['cuts_per_minute']}/min); ffmpeg scene-score second "
          f"opinion: {len(r['cuts_second_opinion'])}",
          f"- shot length median **{s.get('median')} s** (p10 {s.get('p10')}, p90 {s.get('p90')}, "
          f"longest {s.get('longest')})",
          f"- hook: {r['hook']['cuts_in_first_3s']} cut(s) in 3 s, first cut {r['hook']['first_cut']}, "
          f"first-second motion {r['hook']['motion_first_1s']}",
          f"- detector: {r.get('cut_method')}", ""]
    if r["cuts"]:
        L += ["| # | time | transition | dur | sharpness | changed px |",
              "|---|---|---|---|---|---|"]
        for i, c in enumerate(r["cuts"], 1):
            tr = c.get("transition") or {}
            L.append(f"| {i} | {c['time']}s | {tr.get('type', '?')} | {tr.get('dur_s')}s | "
                     f"{c['sharpness']} | {c['changed_px']} |")
        L.append("")

    c = r.get("colour") or {}
    L += ["## Look", "",
          f"- saturation {c.get('mean_saturation')} · luma {c.get('mean_luma')} "
          f"(σ {c.get('luma_std')}) · dark {(c.get('dark_share') or 0) * 100:.0f}% · "
          f"blown {(c.get('bright_share') or 0) * 100:.0f}%",
          f"- motion mean {r['motion']['mean']} / peak {r['motion']['peak']} · static "
          f"{(r['motion']['quiet_share']) * 100:.0f}% of frames",
          f"- edge density (type proxy) mean {r['type_density']['mean']}, peak "
          f"{r['type_density']['peak']} at {r['type_density']['peak_time']}s"]
    if c.get("dominant_hues"):
        L.append("- dominant hue bands: " + ", ".join(
            f"{h['hue']} {h['share'] * 100:.0f}%" for h in c["dominant_hues"]))
    if r.get("palette"):
        L.append("- palette: " + ", ".join(f"`{p['hex']}` {p['share'] * 100:.0f}%"
                                           for p in r["palette"]))
    L.append("")

    a = r.get("audio") or {}
    if a.get("has_audio"):
        L += ["## Sound", "",
              f"- RMS {a.get('rms_db')} dBFS · decoded peak {a.get('peak_db_decoded')} dBFS · "
              f"crest {a.get('crest_db')} dB",
              (f"- tempo **{a.get('bpm_estimate')} BPM** (confidence {a.get('bpm_confidence')}); "
               f"runners-up " + ", ".join(f"{x['bpm']} ({x['score']})"
                                          for x in (a.get("bpm_candidates") or [])[1:])
               if a.get("bpm_estimate") else
               f"- **no stable tempo grid** (best candidate {a.get('bpm_candidates')[0]['bpm']} "
               f"BPM at score {a.get('bpm_confidence')}) — so: cut to speech, not to a beat"), ""]
    lp = r.get("loudness") or {}
    if lp:
        L += ["## Loudness — rebuild to this", "",
              f"- integrated **{lp.get('input_i')} LUFS** · true peak {lp.get('input_tp')} dBTP · "
              f"LRA {lp.get('input_lra')}", ""]
    L += ["## Artifacts", "",
          "- `sheet_3x3.png` — nine frames, the arc at a glance",
          "- `strip_cuts.png` — frames either side of each cut (±0.48 s): the transition itself",
          "- `zoom_t*.png` — 10x zooms of the four quadrants at 6%, 50%, 94%",
          "- `palette.png`, `waveform.png`, `motion.png` — colour, sound, pacing as pictures",
          "- `report.json` — every number above, for diffing the rebuild", ""]
    return "\n".join(L)


def main() -> int:
    global FFMPEG, FFPROBE
    ap = argparse.ArgumentParser()
    ap.add_argument("videos", nargs="+")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    FFMPEG, FFPROBE = _ffmpeg_bin()

    for v in args.videos:
        p = pathlib.Path(v).expanduser().resolve()
        if not p.exists():
            print(f"missing: {p}", file=sys.stderr)
            continue
        out = pathlib.Path(args.out) if args.out else ROOT / "analysis" / p.stem
        out.mkdir(parents=True, exist_ok=True)
        print(f"\n=== {p.name}")
        r = build_report(p, out)
        s = r["shot_len"]
        print(f"  {r['file'].get('width')}x{r['file'].get('height')} "
              f"{r['file'].get('fps')}fps {r['file'].get('duration')}s "
              f"({r['file'].get('shape')})")
        print(f"  cuts {r['cut_count']} ({r['cuts_per_minute']}/min) · median shot "
              f"{s.get('median')}s · bpm {r['audio'].get('bpm_estimate')} · "
              f"{r['loudness'].get('input_i')} LUFS")
        print(f"  -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
