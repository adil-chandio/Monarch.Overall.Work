#!/usr/bin/env python3
"""Microscope pass: what moves *inside* each shot, and what the sound is doing.

`analyse_ref.py` finds the cuts and grades the transitions. This goes one level
deeper, which is what a rebuild actually needs:

  --strip t0 t1 step    a dense frame grid over a range (to read a type animation)
  --motion              per-shot drift: translation (phase correlation), brightness
                        ramp, and whether the frame is actually locked off
  --audio               transient table (are there whooshes on the cuts?) plus
                        spectral flatness (is that a music bed or just voice?)

Everything is measured, nothing is guessed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


# ---------------------------------------------------------------- ffmpeg glue
def ffmpeg_bin() -> str:
    forced = os.environ.get("FFMPEG_BIN")
    if forced:
        return forced
    found = shutil.which("ffmpeg")
    if found:
        return found
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def duration_of(path: str) -> float:
    txt = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", txt)
    if not m:
        raise SystemExit("cannot read duration")
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def frames(path: str, fps: float, w: int) -> tuple[np.ndarray, float]:
    """Decode the whole file to a float32 grey cube (T,H,W) at `fps` and `w`."""
    cmd = [ffmpeg_bin(), "-nostdin", "-v", "error", "-i", path,
           "-vf", f"fps={fps},scale={w}:-2:flags=area", "-f", "rawvideo",
           "-pix_fmt", "gray", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    probe = subprocess.run(
        [ffmpeg_bin(), "-nostdin", "-v", "error", "-i", path,
         "-vf", f"fps={fps},scale={w}:-2:flags=area", "-frames:v", "1",
         "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        capture_output=True).stdout
    h = len(probe) // w
    if h == 0:
        raise SystemExit("could not size the decoded frame")
    n = len(raw) // (w * h)
    return np.frombuffer(raw[: n * w * h], np.uint8).reshape(n, h, w).astype(np.float32), h


def colour_frames(path: str, fps: float, w: int) -> np.ndarray:
    cmd = [ffmpeg_bin(), "-nostdin", "-v", "error", "-i", path,
           "-vf", f"fps={fps},scale={w}:-2:flags=area", "-f", "rawvideo",
           "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    one = subprocess.run(
        [ffmpeg_bin(), "-nostdin", "-v", "error", "-i", path,
         "-vf", f"fps={fps},scale={w}:-2:flags=area", "-frames:v", "1",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    h = len(one) // (3 * w)
    n = len(raw) // (3 * w * h)
    return np.frombuffer(raw[: n * 3 * w * h], np.uint8).reshape(n, h, w, 3)


def pcm(path: str, rate: int = 48000) -> np.ndarray:
    raw = subprocess.run(
        [ffmpeg_bin(), "-nostdin", "-v", "error", "-i", path,
         "-ac", "1", "-ar", str(rate), "-f", "f32le", "-"],
        capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


# ------------------------------------------------------------------ analysis
def phase_shift(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """Translation between two grey frames, by phase correlation (pixels)."""
    wa = np.hanning(a.shape[0])[:, None] * np.hanning(a.shape[1])[None, :]
    fa = np.fft.rfft2((a - a.mean()) * wa)
    fb = np.fft.rfft2((b - b.mean()) * wa)
    r = fb * np.conj(fa)
    r /= np.abs(r) + 1e-9
    c = np.fft.irfft2(r, s=a.shape)
    peak = np.unravel_index(np.argmax(c), c.shape)
    dy = peak[0] - (a.shape[0] if peak[0] < a.shape[0] // 2 else 0)
    dy = peak[0] if peak[0] < a.shape[0] // 2 else peak[0] - a.shape[0]
    dx = peak[1] if peak[1] < a.shape[1] // 2 else peak[1] - a.shape[1]
    return float(dx), float(dy)


def shot_stats(path: str, report_path: str) -> list[dict[str, Any]]:
    with open(report_path) as fh:
        report = json.load(fh)
    dur = float(report["file"]["duration"])
    cuts = sorted(float(c["time"]) for c in report.get("cuts", []))
    edges = [0.0] + cuts + [dur]

    fps = 15.0
    grey, _ = frames(path, fps, 180)
    rgb = colour_frames(path, fps, 180)

    out = []
    for i in range(len(edges) - 1):
        s, e = edges[i], edges[i + 1]
        if e - s < 0.15:
            continue
        f0, f1 = int(s * fps), max(int(s * fps) + 1, int(e * fps) - 1)
        f1 = min(f1, len(grey) - 1)
        if f1 <= f0:
            continue
        seg = grey[f0:f1 + 1]
        d = np.abs(np.diff(seg, axis=0))
        motion = float(d.mean())
        # is the content sliding? compare the shot's own first/last frame
        dx, dy = phase_shift(seg[0], seg[-1])
        # brightness ramp (fades, glows, exposure moves)
        brightness = seg.mean(axis=(1, 2))
        ramp = float(brightness[-1] - brightness[0])
        # background colour: the most common colour of the outer 8% border
        card = rgb[f0:f1 + 1]
        border = np.concatenate([
            card[:, :12].reshape(-1, 3), card[:, -12:].reshape(-1, 3),
            card[:, :, :12].reshape(-1, 3), card[:, :, -12:].reshape(-1, 3),
        ])
        q = (border // 24 * 24).astype(np.int32)
        keys, counts = np.unique(q, axis=0, return_counts=True)
        bg = keys[int(np.argmax(counts))]
        out.append({
            "shot": len(out) + 1,
            "start": round(s, 3),
            "dur": round(e - s, 3),
            "motion_per_frame": round(motion, 4),
            "drift_px": [round(dx, 1), round(dy, 1)],
            "drift_pct_w": round(abs(dx) / 180 * 100, 2),
            "brightness": round(float(seg.mean()), 1),
            "brightness_ramp": round(ramp, 2),
            "bg": "#%02x%02x%02x" % tuple(int(v) for v in bg),
        })
    return out


def audio_stats(path: str, cuts: list[float]) -> dict[str, Any]:
    sr = 48000
    a = pcm(path, sr)
    if a.size == 0:
        return {"has_audio": False}
    hop = sr // 100  # 10 ms
    n = a.size // hop
    env = np.array([np.sqrt(np.mean(a[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)])
    db = 20 * np.log10(env + 1e-12)

    # transient table: 10 ms frame louder than both neighbours by >3 dB
    transient = []
    for i in range(1, n - 1):
        if db[i] > db[i - 1] + 3 and db[i] >= db[i + 1]:
            transient.append((i / 100.0, float(db[i])))
    transient.sort(key=lambda t: -t[1])
    transient = sorted(transient[:40])

    near_cuts = []
    for c in cuts:
        best = min(transient, key=lambda t: abs(t[0] - c)) if transient else None
        if best and abs(best[0] - c) <= 0.12:
            near_cuts.append({"cut": round(c, 3), "transient": round(best[0], 3),
                              "delta_ms": round((best[0] - c) * 1000),
                              "db": round(best[1], 1)})

    # spectral flatness per 0.5 s window: ~0 = tonal/music, ~1 = noise
    win = sr // 2
    flat = []
    for i in range(0, max(1, a.size - win), win):
        spec = np.abs(np.fft.rfft(a[i:i + win] * np.hanning(win))) + 1e-12
        flat.append(float(np.exp(np.mean(np.log(spec))) / np.mean(spec)))
    flat = np.array(flat)

    # harmonic-to-percussive-ish split: how periodic is the envelope?
    env_c = env - env.mean()
    ac = np.correlate(env_c, env_c, "full")[n - 1:]
    ac /= ac[0] + 1e-12
    lo, hi = int(60 / 191 * 100), int(60 / 55 * 100)  # lags for 55-191 BPM
    lag = lo + int(np.argmax(ac[lo:hi])) if hi < n else 0
    periodicity = float(ac[lag]) if lag else 0.0

    return {
        "has_audio": True,
        "rms_db": round(float(20 * np.log10(np.sqrt(np.mean(a ** 2)) + 1e-12)), 2),
        "peak_db": round(float(20 * np.log10(np.abs(a).max() + 1e-12)), 2),
        "flatness_mean": round(float(flat.mean()), 3),
        "flatness_p10": round(float(np.percentile(flat, 10)), 3),
        "flatness_p90": round(float(np.percentile(flat, 90)), 3),
        "quietest_half_second_db": round(float(np.percentile(flat, 5)), 3),
        "envelope_periodicity": round(periodicity, 3),
        "period_bpm": round(6000.0 / lag, 1) if lag else None,
        "transient_count": len(transient),
        "loudest_transients": [{"t": round(t, 2), "db": round(dbv, 1)} for t, dbv in
                               sorted(transient, key=lambda x: -x[1])[:12]],
        "transients_on_cuts": near_cuts,
        "envelope_p10_db": round(float(np.percentile(db, 10)), 1),
        "envelope_p50_db": round(float(np.percentile(db, 50)), 1),
        "envelope_p90_db": round(float(np.percentile(db, 90)), 1),
    }


def strip(path: str, t0: float, t1: float, step: float, out: str, width: int = 260) -> str:
    tmp = tempfile.mkdtemp(prefix="strip_")
    cmd = [ffmpeg_bin(), "-nostdin", "-v", "error", "-y",
           "-ss", f"{t0:.3f}", "-i", path, "-t", f"{t1 - t0:.3f}",
           "-vf", f"fps=1/{step},scale={width}:-2:flags=lanczos",
           os.path.join(tmp, "f_%03d.png")]
    subprocess.run(cmd, check=True, capture_output=True)
    files = sorted(os.listdir(tmp))
    imgs = [Image.open(os.path.join(tmp, f)).convert("RGB") for f in files]
    if not imgs:
        raise SystemExit("no frames")
    cw, ch = imgs[0].size
    cols = 8
    rows = (len(imgs) + cols - 1) // cols
    lab = 26
    sheet = Image.new("RGB", (cols * (cw + 6) + 6, rows * (ch + lab + 6) + 6), (14, 14, 16))
    d = ImageDraw.Draw(sheet)
    try:
        fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
    except Exception:
        fnt = ImageFont.load_default()
    for i, im in enumerate(imgs):
        x = 6 + (i % cols) * (cw + 6)
        y = 6 + (i // cols) * (ch + lab + 6)
        sheet.paste(im, (x, y))
        d.text((x + 2, y + ch + 2), f"{t0 + i * step:5.2f}s", font=fnt, fill=(255, 255, 255))
    sheet.save(out, optimize=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--report", help="report.json from analyse_ref.py")
    ap.add_argument("--out", default="analysis")
    ap.add_argument("--strip", nargs=3, metavar=("T0", "T1", "STEP"))
    ap.add_argument("--motion", action="store_true")
    ap.add_argument("--audio", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    if args.strip:
        t0, t1, step = (float(v) for v in args.strip)
        out = os.path.join(args.out, f"strip_{t0:.2f}-{t1:.2f}.png")
        print(strip(args.video, t0, t1, step, out))

    if args.motion:
        report = args.report or os.path.join(args.out, "report.json")
        stats = shot_stats(args.video, report)
        with open(os.path.join(args.out, "shots_motion.json"), "w") as fh:
            json.dump(stats, fh, indent=2)
        print("| shot | start | dur | motion/frame | drift px | %W | luma | ramp | bg |")
        print("|---|---|---|---|---|---|---|---|---|")
        for s in stats:
            print(f"| {s['shot']} | {s['start']:.2f} | {s['dur']:.2f} | {s['motion_per_frame']:.4f} "
                  f"| {s['drift_px']} | {s['drift_pct_w']} | {s['brightness']} | {s['brightness_ramp']} | {s['bg']} |")

    if args.audio:
        report = args.report or os.path.join(args.out, "report.json")
        cuts = []
        if os.path.exists(report):
            with open(report) as fh:
                cuts = [float(c["time"]) for c in json.load(fh).get("cuts", [])]
        info = audio_stats(args.video, cuts)
        with open(os.path.join(args.out, "audio_deep.json"), "w") as fh:
            json.dump(info, fh, indent=2)
        print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
