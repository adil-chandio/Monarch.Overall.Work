#!/usr/bin/env python3
"""Compare two cuts of the same film on identical, decoded-pixel metrics.

This exists so a claim like "V8 is sharper and steadier than the earlier review
cut" is a measurement, not an opinion. Every number below is computed from the
decoded streams with the same code path for both files.

Reported per file:
  frames, resolution, duration, duplicated-frame count, black frames, mean
  Laplacian sharpness, per-frame luma curve flicker, stabilised jitter RMS,
  integrated loudness and true peak.

Usage:
  python qc/compare_cuts.py --a old.mp4 --b new.mp4 --json qc/out/compare.json
"""
from __future__ import annotations

import argparse, json, re, subprocess, sys
from pathlib import Path

import cv2
import numpy as np
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import film_tools as ft  # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()


def probe(path: Path):
    info = subprocess.run([FF, '-hide_banner', '-i', str(path)],
                          capture_output=True, text=True).stderr
    v = re.search(r'(\d{2,5})x(\d{2,5})', info.split('Video:')[1]) if 'Video:' in info else None
    dur = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', info)
    if not v or not dur:
        raise SystemExit(f'cannot probe {path}')
    seconds = int(dur.group(1)) * 3600 + int(dur.group(2)) * 60 + float(dur.group(3))
    fps = re.search(r'([\d.]+) fps', info)
    has_audio = 'Audio:' in info
    return {'width': int(v.group(1)), 'height': int(v.group(2)),
            'duration_seconds': round(seconds, 3),
            'fps': float(fps.group(1)) if fps else None, 'has_audio': has_audio}


def decode(path: Path, w: int, h: int):
    raw = subprocess.run([FF, '-v', 'error', '-i', str(path), '-pix_fmt', 'bgr24',
                          '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    n = len(raw) // (w * h * 3)
    return np.frombuffer(raw[:n * w * h * 3], np.uint8).reshape(n, h, w, 3)


def loudness(path: Path):
    out = subprocess.run([FF, '-hide_banner', '-nostats', '-i', str(path),
                          '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    integ = re.findall(r'I:\s+(-?\d+\.\d+) LUFS', out)
    peak = re.findall(r'Peak:\s+(-?\d+\.\d+) dBFS', out)
    return (float(integ[-1]) if integ else None, float(peak[-1]) if peak else None)


def measure(path: Path):
    info = probe(path)
    frames = decode(path, info['width'], info['height'])
    n = len(frames)
    # decimate for speed on long files but keep the temporal structure
    step = max(1, n // 240)
    sel = frames[::step]
    raw_gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in sel]
    # Film grain and h264 noise register as fake sub-pixel "shake"; blur only for
    # the motion track so it measures camera movement, not compression texture.
    gray = [cv2.GaussianBlur(g, (5, 5), 1.2) for g in raw_gray]
    luma = np.array([g.mean() for g in gray])
    diff = np.array([float(np.abs(gray[i + 1].astype(np.int16) -
                                 gray[i].astype(np.int16)).mean()) for i in range(len(gray) - 1)])
    sharp = np.array([cv2.Laplacian(g.astype(np.float32), cv2.CV_32F).var() for g in raw_gray])
    track = ft.track_shifts(gray, work_width=320, radius=5) if len(gray) > 3 else np.zeros((1, 2))
    # A shot with a real camera move has a large monotonic track; its "jitter"
    # number is dominated by that travel and must not be reported as shake.
    travel = float(np.abs(track).max())
    per_frame_travel = travel / max(len(track) - 1, 1)
    lufs, peak = loudness(path) if info['has_audio'] else (None, None)
    return {
        **info, 'frames': n,
        'duplicated_frame_pairs': int((diff < 0.02).sum()),
        'frozen_pair_pct': round(100 * float((diff < 0.02).mean()), 2) if len(diff) else 0.0,
        'black_frames': int((luma < 6).sum()),
        # Laplacian variance on unblurred luma. This is high-frequency energy: an
        # upscale pass can raise it without adding real resolution, so it is
        # reported as texture, never as proof of detail beyond the source.
        'high_freq_energy_mean': round(float(sharp.mean()), 1),
        'flicker_max_luma_step': round(float(np.abs(np.diff(luma)).max()), 3) if len(luma) > 1 else 0.0,
        'jitter_rms_px': round(ft.jitter_rms(track), 3),
        'max_track_travel_px': round(travel, 1),
        'travel_dominates_jitter': bool(per_frame_travel > 1.5),
        'integrated_lufs': lufs, 'true_peak_dbfs': peak,
    }


def info_frames(path: Path) -> int:
    info = probe(path)
    return max(1, int(round(info['duration_seconds'] * (info['fps'] or 24))))


def shot_track(path: Path, info: dict, lo: int, hi: int, step: int):
    """Blurred motion track for one shot only, so cuts do not fake jitter."""
    w, h = info['width'], info['height']
    cmd = [FF, '-v', 'error', '-i', str(path), '-vf',
           f"select='between(n\\,{lo}\\,{hi - 1})',setpts=N/FRAME_RATE/TB",
           '-pix_fmt', 'bgr24', '-f', 'rawvideo', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = len(raw) // (w * h * 3)
    if n < 4:
        return np.zeros((1, 2))
    arr = np.frombuffer(raw[:n * w * h * 3], np.uint8).reshape(n, h, w, 3)
    keep = arr[::step] if step > 1 else arr
    gray = [cv2.GaussianBlur(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (5, 5), 1.2) for f in keep]
    return ft.track_shifts(gray, work_width=320, radius=5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--a', required=True, type=Path)
    ap.add_argument('--b', required=True, type=Path)
    ap.add_argument('--json', type=Path)
    args = ap.parse_args()
    a, b = measure(args.a), measure(args.b)
    per_shot = {}
    try:
        sys.path.insert(0, str(HERE))
        import render_film_v8 as rv
        a_info, b_info = probe(args.a), probe(args.b)
        for shot in rv.SHOTS:
            lo, hi = shot.start, min(shot.end, 480)
            row = {}
            for tag, path, info in (('a', args.a, a_info), ('b', args.b, b_info)):
                step = max(1, info_frames(path) // 240)
                track = shot_track(path, info, lo, hi, step)
                row[tag] = {'jitter_rms_px': round(ft.jitter_rms(track), 3),
                            'max_travel_px': round(float(np.abs(track).max()), 1)}
            travel = row['a']['max_travel_px']
            row['travel_dominates'] = bool(travel > 40)
            row['note'] = ('camera travel dominates; jitter not separable here'
                           if row['travel_dominates'] else 'comparable')
            per_shot[shot.name] = row
    except Exception as exc:  # never fail the whole report on the optional part
        per_shot = {'error': str(exc)[:200]}
    deltas = {}
    for key in ('high_freq_energy_mean', 'jitter_rms_px', 'flicker_max_luma_step',
                'frozen_pair_pct', 'duplicated_frame_pairs'):
        if a.get(key) is not None and b.get(key) is not None:
            deltas[key] = round(b[key] - a[key], 3)
    out = {'a': {'file': str(args.a), **a}, 'b': {'file': str(args.b), **b},
           'delta_b_minus_a': deltas, 'per_shot': per_shot,
           'note': ('Decoded-pixel engineering metrics, not creative acceptance. '
                    'high_freq_energy is texture, not proof of resolution beyond the source. '
                    'Per-shot jitter is only meaningful where camera travel does not dominate.')}
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(out, indent=1))
    for k in ('width', 'height', 'frames', 'duration_seconds', 'high_freq_energy_mean',
              'flicker_max_luma_step', 'jitter_rms_px', 'duplicated_frame_pairs',
              'integrated_lufs', 'true_peak_dbfs'):
        print(f'{k:24s} A={a.get(k)!s:>10}   B={b.get(k)!s:>10}')
    print('\ndelta (B-A):', deltas)
    if isinstance(per_shot, dict) and 'error' not in per_shot:
        print('\nper shot jitter RMS (px):')
        for name, row in per_shot.items():
            flag = ' *travel dominates' if row['travel_dominates'] else ''
            print(f"  {name:12s} A={row['a']['jitter_rms_px']:5.2f}  "
                  f"B={row['b']['jitter_rms_px']:5.2f}{flag}")
    if args.json:
        print('wrote', args.json)


if __name__ == '__main__':
    main()
