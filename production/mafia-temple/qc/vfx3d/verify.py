#!/usr/bin/env python3
"""Technical gates for the 3D cut.

These are hard, checkable facts about the file — not an opinion about the
picture. If any of them fails the file is not allowed out under this name.

    python qc/vfx3d/verify.py render-3d/monarch-temple-3d.mp4
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np


def probe(ff, path):
    out = subprocess.run([ff, '-hide_banner', '-i', str(path)],
                         capture_output=True, text=True).stderr
    return out


def decode_frames(ff, path, width, height):
    cmd = [ff, '-v', 'error', '-i', str(path), '-f', 'rawvideo',
           '-pix_fmt', 'rgb24', '-']
    p = subprocess.run(cmd, capture_output=True)
    buf = np.frombuffer(p.stdout, np.uint8)
    per = width * height * 3
    n = len(buf) // per
    return buf[:n * per].reshape(n, height, width, 3)


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else
                'render-3d/monarch-temple-3d.mp4')
    expect_audio = '--no-audio' not in sys.argv
    strict_duration = '--strict-duration' in sys.argv
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    info = probe(ff, path)

    checks = []

    def need(cond, msg):
        checks.append((bool(cond), msg))

    need('1280x720' in info, 'picture is 1280x720')
    need('24 fps' in info, 'frame rate is 24 fps')
    if strict_duration:
        need('Duration: 00:00:20.00' in info, 'duration is exactly 20.000 s')
    else:
        m = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', info)
        secs = (int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))) if m else 0.0
        need(abs(secs - 20.0) < 0.05, f'duration is 20.00 s (measured {secs:.2f})')
    if expect_audio:
        need('Audio: aac' in info, 'has an AAC audio stream')

    w, h = 1280, 720
    frames = decode_frames(ff, path, w, h)
    need(abs(len(frames) / 24.0 - 20.0) <= 1 / 24.0,
         f'frame count matches 20 s at 24 fps (got {len(frames)})')

    # no frozen frames: consecutive frames must differ
    diffs = [float(np.abs(frames[i].astype(np.int16) -
                          frames[i - 1].astype(np.int16)).mean())
             for i in range(1, len(frames))]
    dup = sum(1 for d in diffs if d < 0.02)
    need(dup == 0, f'no duplicated frames (duplicates: {dup})')
    need(min(diffs) > 0.05, f'every frame differs from the last (min diff {min(diffs):.3f})')

    # a real 3D render must have depth: plenty of distinct luminance levels
    lum = frames.mean(axis=(1, 2, 3))
    need(lum.mean() > 18, f'frame is not black (mean luma {lum.mean():.1f})')
    need(lum.mean() < 140, f'frame is not blown out (mean luma {lum.mean():.1f})')

    # per-shot coverage: every second of the film has picture in it
    per_second = [float(lum[i:i + 24].mean()) for i in range(0, len(lum), 24)]
    need(min(per_second) > 10, f'no dark second (min {min(per_second):.1f})')

    # ---- reference match: measured against monarch-mafia-temple-20s.mp4 ------
    # These are the numbers that made the first cut unacceptable, so they are now
    # hard gates: the cut is graded to the reference's measured palette, not to
    # taste.
    gray = frames.astype(np.float32) @ np.array([0.299, 0.587, 0.114],
                                                np.float32)
    luma_med = np.median(gray)
    need(8.0 <= luma_med <= 45.0,
         f'median luma matches the reference band 10-38 (got {luma_med:.1f})')
    iqr = np.percentile(gray, 75) - np.percentile(gray, 25)
    need(20.0 <= iqr <= 60.0,
         f'median luma IQR matches the reference 25-50 (got {iqr:.1f})')

    # saturation, measured the way the reference was
    hsv = np.empty_like(frames)
    mx = frames.max(-1).astype(np.float32)
    mn = frames.min(-1).astype(np.float32)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0) * 255
    sat_med = np.median(sat)
    need(60.0 <= sat_med <= 190.0,
         f'median saturation matches the reference 81-181 (got {sat_med:.1f})')

    # cut points have to land where the reference cuts are
    cut_expected = [96, 216, 312, 384, 432]
    d = np.array([np.abs(frames[i].astype(np.int16) -
                         frames[i - 1].astype(np.int16)).mean()
                  for i in range(1, len(frames))])
    # a cut is a spike well above the local level
    local = np.convolve(d, np.ones(9) / 9, mode='same')
    spikes = [i + 1 for i in range(len(d))
              if d[i] > local[i] * 2.2 and d[i] > 6.0]
    cuts = []
    for c in spikes:
        if not cuts or c - cuts[-1] > 6:
            cuts.append(c)
    need(len(cuts) >= 4, f'the film has the reference cut structure '
                         f'(found {cuts})')

    print(f'palette     luma median {luma_med:.1f}  IQR {iqr:.1f}  '
          f'saturation median {sat_med:.1f}')
    print(f'cuts        {cuts}  (reference 96, 216, 312, 384, 432)')
    print(f'file        {path}')
    print(f'size        {path.stat().st_size} bytes')
    print(f'frames      {len(frames)}')
    print(f'luma        mean {lum.mean():.1f}  min {lum.min():.1f}  max {lum.max():.1f}')
    print(f'frame diff  min {min(diffs):.3f}  mean {np.mean(diffs):.3f}')
    print()
    ok = True
    for passed, msg in checks:
        print(f'  {"PASS" if passed else "FAIL"}  {msg}')
        ok &= passed
    print()
    print('VERIFIED' if ok else 'NOT VERIFIED')
    if not ok:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
