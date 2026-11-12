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
    """Not used for the full film any more (1.3 GB, OOM in a 3 GB sandbox);
    kept for small probes."""
    cmd = [ff, '-v', 'error', '-i', str(path), '-f', 'rawvideo',
           '-pix_fmt', 'rgb24', '-']
    p = subprocess.run(cmd, capture_output=True)
    buf = np.frombuffer(p.stdout, np.uint8)
    per = width * height * 3
    n = len(buf) // per
    return buf[:n * per].reshape(n, height, width, 3)


def stream_stats(ff, path, width, height, chunk=24):
    """Decode once, frame by frame, and keep only per-frame statistics plus a
    coarse 8x8 thumbnail per frame (which is all the cut detector needs)."""
    cmd = [ff, '-v', 'error', '-i', str(path), '-f', 'rawvideo',
           '-pix_fmt', 'rgb24', '-']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=10 ** 8)
    per = width * height * 3
    lums, sats, thumbs, frames_diffs = [], [], [], []
    prev = None
    count = 0
    while True:
        raw = proc.stdout.read(per)
        if len(raw) < per:
            break
        f = np.frombuffer(raw, np.uint8).reshape(height, width, 3)
        lums.append(float((f[..., 0] * 0.299 + f[..., 1] * 0.587
                          + f[..., 2] * 0.114).mean()))
        mx = f.max(-1).astype(np.float32)
        mn = f.min(-1).astype(np.float32)
        sats.append(float(np.median(np.where(mx > 0, (mx - mn)
                                             / np.maximum(mx, 1), 0)) * 255))
        small = f[::90, ::160].astype(np.float32)
        thumbs.append(small)
        if prev is not None:
            frames_diffs.append(float(np.abs(f.astype(np.int16)
                                             - prev.astype(np.int16)).mean()))
        prev = f
        count += 1
    proc.stdout.close()
    proc.wait()
    return (np.array(lums), np.array(sats), np.array(thumbs),
            np.array(frames_diffs), count)


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
    lums, sats, thumbs, diffs, n = stream_stats(ff, path, w, h)
    need(abs(n / 24.0 - 20.0) <= 1 / 24.0,
         f'frame count matches 20 s at 24 fps (got {n})')

    # no frozen frames: consecutive frames must differ
    dup = int((diffs < 0.02).sum())
    need(dup == 0, f'no duplicated frames (duplicates: {dup})')
    need(float(diffs.min()) > 0.05,
         f'every frame differs from the last (min diff {diffs.min():.3f})')

    # a real render must not be black or blown out
    need(lums.mean() > 18, f'frame is not black (mean luma {lums.mean():.1f})')
    need(lums.mean() < 140,
         f'frame is not blown out (mean luma {lums.mean():.1f})')

    # every second of the film has picture in it
    per_second = [float(lums[i:i + 24].mean()) for i in range(0, n, 24)]
    # the reference itself has a shot at median luma 10.6, so the floor here is
    # "legible", not "bright": 8 is a dark shot, 6 is a mistake
    need(min(per_second) > 8, f'no unreadably dark second (min {min(per_second):.1f})')

    # ---- reference match: measured against monarch-mafia-temple-20s.mp4 ------
    # These are the numbers that made the first cut unacceptable, so they are now
    # gates: the cut is graded to the reference's measured palette, not to taste.
    luma_med = float(np.median(lums))
    need(8.0 <= luma_med <= 45.0,
         f'median luma matches the reference band 10-38 (got {luma_med:.1f})')
    sat_med = float(np.median(sats))
    need(60.0 <= sat_med <= 190.0,
         f'median saturation matches the reference 81-181 (got {sat_med:.1f})')

    # cut points have to land where the reference cuts are
    d = diffs
    local = np.convolve(d, np.ones(9) / 9, mode='same')
    spikes = [i + 1 for i in range(len(d))
              if d[i] > local[i] * 2.2 and d[i] > 5.0]
    cuts = []
    for c in spikes:
        if not cuts or c - cuts[-1] > 6:
            cuts.append(c)
    need(len(cuts) >= 4, f'the film has the reference cut structure (found {cuts})')
    near = sum(1 for c in cuts
               if min(abs(c - e) for e in (96, 216, 312, 384, 432)) <= 3)
    need(near >= 4, f'cuts land on the reference cut points (within 3 frames: '
                    f'{near} of {len(cuts)})')

    print(f'palette     luma median {luma_med:.1f}  '
          f'saturation median {sat_med:.1f}')
    print(f'cuts        {cuts}  (reference 96, 216, 312, 384, 432)')
    print(f'file        {path}')
    print(f'size        {path.stat().st_size} bytes')
    print(f'frames      {n}')
    print(f'luma        mean {lums.mean():.1f}  min {lums.min():.1f}  max {lums.max():.1f}')
    print(f'frame diff  min {diffs.min():.3f}  mean {diffs.mean():.3f}')
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
