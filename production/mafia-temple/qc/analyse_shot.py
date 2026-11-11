#!/usr/bin/env python3
"""Analyse a shot source and report what can be fixed, with measured evidence.

For one clip this decodes the frames, then measures:
  * flicker (per-frame luma curve; how much a deflicker pass can remove)
  * hand-held jitter (RMS residual after removing smooth travel)
  * softness (Laplacian energy before/after a real ESPCN 2x pass)
  * face/eye tracking hits for the close-up glow

Nothing here changes the media; it produces the numbers the render logs and the
report must quote. It does not measure likeness, anatomy or acting quality.

Usage:
  python analyse_shot.py --clips clips --json qc/shot_analysis.json \
      --superres /path/ESPCN_x2.pb --closeup wan4-face-a
"""
import argparse, json, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import film_tools as ft  # noqa: E402
import imageio_ffmpeg      # noqa: E402
import subprocess          # noqa: E402
import cv2                 # noqa: E402


def decode(path: Path):
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    probe = subprocess.run([ff, '-hide_banner', '-i', str(path)],
                           capture_output=True, text=True).stderr
    import re
    m = re.search(r'(\d{2,5})x(\d{2,5})', probe.split('Video:')[1]) if 'Video:' in probe else None
    if not m:
        raise SystemExit(f'cannot probe {path}')
    w, h = int(m.group(1)), int(m.group(2))
    raw = subprocess.run([ff, '-v', 'error', '-i', str(path), '-pix_fmt', 'bgr24',
                          '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    n = len(raw) // (w * h * 3)
    return np.frombuffer(raw[:n * w * h * 3], np.uint8).reshape(n, h, w, 3).copy()


def analyse(path: Path, sr_model: Path | None, closeup: bool):
    frames = decode(path)
    n = len(frames)
    gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]
    luma = np.array([g.mean() for g in gray], dtype=np.float64)
    gains = ft.deflicker_gains(luma)
    after = luma * gains
    out = {
        'file': path.name, 'frames': n, 'size': [frames.shape[2], frames.shape[1]],
        'luma_mean': round(float(luma.mean()), 3),
        'luma_step_max_before': round(float(np.abs(np.diff(luma)).max()), 3),
        'luma_step_max_after': round(float(np.abs(np.diff(after)).max()), 3),
        'flicker_reduction_pct': round(100 * (1 - np.abs(np.diff(after)).max() /
                                              max(np.abs(np.diff(luma)).max(), 1e-6)), 1),
    }
    # jitter
    step = max(1, n // 40)
    track = ft.track_shifts(gray[::step], work_width=320, radius=6)
    out['jitter_rms_px_before'] = round(ft.jitter_rms(track), 3)
    resid = ft.stabilise_residuals(track)
    out['jitter_rms_px_after'] = round(ft.jitter_rms(track - resid), 3)
    out['stabilise_applied'] = out['jitter_rms_px_before'] >= 0.45
    # sharpness / super-resolution
    mid = frames[n // 2]
    out['sharpness_before'] = round(float(cv2.Laplacian(
        cv2.cvtColor(mid, cv2.COLOR_BGR2GRAY).astype(np.float32), cv2.CV_32F).var()), 1)
    if sr_model and sr_model.exists():
        sr = ft.SuperRes(str(sr_model))
        crop = mid[: min(144, mid.shape[0]), : min(256, mid.shape[1])]
        up = sr(crop)
        big = cv2.resize(crop, (up.shape[1], up.shape[0]), interpolation=cv2.INTER_CUBIC)
        out['sharpness_cubic'] = round(float(cv2.Laplacian(
            cv2.cvtColor(big, cv2.COLOR_BGR2GRAY).astype(np.float32), cv2.CV_32F).var()), 1)
        out['sharpness_espcn'] = round(float(cv2.Laplacian(
            cv2.cvtColor(up, cv2.COLOR_BGR2GRAY).astype(np.float32), cv2.CV_32F).var()), 1)
        out['espcn_gain_vs_cubic_pct'] = round(
            100 * (out['sharpness_espcn'] / max(out['sharpness_cubic'], 1e-6) - 1), 1)
    if closeup:
        boxes = [ft.face_box(f) for f in frames]
        hits = sum(b is not None for b in boxes)
        pts = ft.smooth_points([ft.eye_points(f, b) for f, b in zip(frames, boxes)], 5)
        out['face_hits'] = hits
        out['eye_hits'] = sum(p is not None for p in pts)
        out['face_hit_pct'] = round(100 * hits / n, 1)
        if out['eye_hits']:
            drift = np.ptp(np.array([[p[0][0], p[1][0]] for p in pts if p], float), axis=0)
            out['eye_track_x_range_px'] = [round(float(v), 1) for v in drift]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--clips', type=Path, required=True)
    ap.add_argument('--json', type=Path, required=True)
    ap.add_argument('--superres', type=Path)
    ap.add_argument('--closeup', default='')
    a = ap.parse_args()
    rows = []
    for p in sorted(a.clips.glob('*.mp4')):
        r = analyse(p, a.superres, p.stem == a.closeup)
        rows.append(r)
        extra = ''
        if 'espcn_gain_vs_cubic_pct' in r:
            extra += f" espcn+{r['espcn_gain_vs_cubic_pct']}%"
        if r['face_hits'] if 'face_hits' in r else 0:
            extra += f" face {r['face_hit_pct']}% eyes {r['eye_hits']}"
        print(f"{r['file']:24s} flicker -{r['flicker_reduction_pct']:5.1f}%  "
              f"jitter {r['jitter_rms_px_before']:.2f}->{r['jitter_rms_px_after']:.2f}px{extra}", flush=True)
    a.json.parent.mkdir(parents=True, exist_ok=True)
    a.json.write_text(json.dumps({
        'tool': 'qc/analyse_shot.py',
        'note': 'Measured engineering deltas of the fix passes. Not creative acceptance.',
        'shots': rows}, indent=1))
    print(f'\nwrote {a.json}')


if __name__ == '__main__':
    main()
