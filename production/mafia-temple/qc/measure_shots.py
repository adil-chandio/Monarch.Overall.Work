#!/usr/bin/env python3
"""Measure every generated clip instead of describing it in prose.

Per clip this reports frame count, resolution, real motion energy (mean absolute
frame difference), frozen runs, temporal luma flicker, sharpness (Laplacian
variance) and black/low-detail frames. These are engineering measurements of the
decoded pixels; they are NOT creative acceptance, likeness proof or a claim that
the motion is anatomically correct.

Usage:  python measure_shots.py --clips <dir> --output <json>
"""
import argparse, json, re, subprocess
from pathlib import Path
import cv2
import numpy as np
import imageio_ffmpeg


def decode(path):
    """Decode every frame of a clip as RGB uint8 via the bundled ffmpeg."""
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    probe = subprocess.run(
        [ff, '-hide_banner', '-i', str(path)],
        capture_output=True, text=True).stderr
    w = h = None
    for token in probe.replace(',', ' ').split():
        # ffmpeg prints e.g. "yuv420p(progressive), 768x448, 391 kb/s"
        if re.fullmatch(r'\d{2,5}x\d{2,5}', token):
            a, b = token.split('x')
            w, h = int(a), int(b)
            break
    if not w:
        raise SystemExit(f'cannot probe {path}')
    raw = subprocess.run(
        [ff, '-v', 'error', '-i', str(path), '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'],
        capture_output=True, check=True).stdout
    n = len(raw) // (w * h * 3)
    return np.frombuffer(raw[:n * w * h * 3], np.uint8).reshape(n, h, w, 3), w, h


def runs(flags):
    """Return [(start, length)] of consecutive True values."""
    out, start = [], None
    for i, f in enumerate(flags):
        if f and start is None:
            start = i
        elif not f and start is not None:
            out.append((start, i - start)); start = None
    if start is not None:
        out.append((start, len(flags) - start))
    return out


def measure(path):
    frames, w, h = decode(path)
    n = len(frames)
    gray = np.stack([cv2.cvtColor(f, cv2.COLOR_RGB2GRAY) for f in frames]).astype(np.float32)
    diff = np.abs(np.diff(gray, axis=0))
    mad = diff.reshape(n - 1, -1).mean(1)
    # A frozen frame pair is one where almost nothing moved at all.
    frozen = mad < 0.25
    luma = gray.reshape(n, -1).mean(1)
    sharp = np.array([cv2.Laplacian(g, cv2.CV_32F).var() for g in gray])
    return {
        'file': path.name,
        'width': w, 'height': h, 'frames': n, 'fps': 24,
        'seconds': round(n / 24, 3),
        'motion_mad_mean': round(float(mad.mean()), 4),
        'motion_mad_min': round(float(mad.min()), 4),
        'motion_mad_p05': round(float(np.percentile(mad, 5)), 4),
        'motion_mad_max': round(float(mad.max()), 4),
        'frozen_pairs': int(frozen.sum()),
        'frozen_runs': runs(frozen.tolist())[:8],
        'frozen_run_max': max([r[1] for r in runs(frozen.tolist())] or [0]),
        'luma_mean': round(float(luma.mean()), 2),
        'luma_std_over_time': round(float(luma.std()), 3),
        'luma_flicker_max_step': round(float(np.abs(np.diff(luma)).max()), 3),
        'sharpness_mean': round(float(sharp.mean()), 2),
        'sharpness_min': round(float(sharp.min()), 2),
        'dark_frames': int((luma < 6).sum()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--clips', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--glob', default='*.mp4')
    a = ap.parse_args()
    files = sorted(a.clips.glob(a.glob))
    rows = []
    for f in files:
        try:
            rows.append(measure(f))
            r = rows[-1]
            print(f"{r['file']:24s} {r['width']}x{r['height']} {r['frames']:4d}f "
                  f"mad={r['motion_mad_mean']:.3f} frozen={r['frozen_pairs']:3d}/{max(r['frozen_run_max'],0):3d} "
                  f"sharp={r['sharpness_mean']:7.1f} flicker={r['luma_flicker_max_step']:.2f}", flush=True)
        except Exception as e:  # a broken clip must be reported, not hidden
            rows.append({'file': f.name, 'error': str(e)[:200]})
            print(f'{f.name}: ERROR {str(e)[:90]}', flush=True)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps({
        'tool': 'qc/measure_shots.py',
        'note': 'Decoded-pixel engineering metrics only. Not creative acceptance.',
        'clips': rows}, indent=1))
    print(f'\nwrote {a.output} ({len(rows)} clips)')


if __name__ == '__main__':
    main()
