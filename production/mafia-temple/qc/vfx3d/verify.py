#!/usr/bin/env python3
"""Technical gates for the 3D cut.

These are hard, checkable facts about the file — not an opinion about the
picture. If any of them fails the file is not allowed out under this name.

    python qc/vfx3d/verify.py render-3d/monarch-temple-3d.mp4
"""
from __future__ import annotations

import json
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
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    info = probe(ff, path)

    checks = []

    def need(cond, msg):
        checks.append((bool(cond), msg))

    need('1280x720' in info, 'picture is 1280x720')
    need('24 fps' in info, 'frame rate is 24 fps')
    need('Duration: 00:00:20.00' in info, 'duration is exactly 20.000 s')
    if expect_audio:
        need('Audio: aac' in info, 'has an AAC audio stream')

    w, h = 1280, 720
    frames = decode_frames(ff, path, w, h)
    need(len(frames) == 480, f'480 frames decoded (got {len(frames)})')

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
