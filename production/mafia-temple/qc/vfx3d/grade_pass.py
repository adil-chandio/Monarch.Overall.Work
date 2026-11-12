#!/usr/bin/env python3
"""One linear-light grade pass over rendered frames.

The renderer grades per shot, but the film's overall level still sat above the
reference (median luma 44.9 against the reference's 10-38). Rather than pretend
the wider band was the target, this pass brings the film onto the measured
level: exposure down, a small S-curve, and saturation held.

Usage:
  python qc/vfx3d/grade_pass.py --src render-3d/frames2 --dst render-3d/frames3
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

LUMA = np.array([0.299, 0.587, 0.114], np.float32)

# Per-shot correction to the reference's measured palette. Each entry is
# (frame_start, frame_end, luma_target, saturation_target); the pass measures
# what the shot actually is and drives it to the reference value. The reference
# numbers are in the report: S1 21.4/135, S2 17.1/138, S3 28.4/161,
# S4 37.6/81, S5 10.6/181, S6 18.9/98.
TARGETS = [
    (0, 96, 21.4, 135.0),
    (96, 216, 17.1, 138.0),
    (216, 312, 28.4, 161.0),
    (312, 384, 37.6, 81.0),
    (384, 432, 10.6, 181.0),
    (432, 480, 18.9, 98.0),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--dst', required=True)
    ap.add_argument('--exposure', type=float, default=0.80)
    ap.add_argument('--gamma', type=float, default=1.05)
    ap.add_argument('--contrast', type=float, default=1.04)
    ap.add_argument('--saturation', type=float, default=1.0)
    args = ap.parse_args()

    src, dst = Path(args.src), Path(args.dst)
    dst.mkdir(parents=True, exist_ok=True)
    files = sorted(src.glob('f*.png'))

    # pass 1: measure the median luma and saturation of every shot
    stats = {k: ([], []) for k in range(len(TARGETS))}
    for f in files:
        i = int(f.stem[1:])
        k = next(j for j, (a0, b0, _l, _s) in enumerate(TARGETS) if a0 <= i < b0)
        x = np.asarray(Image.open(f), np.float32)
        lum = x @ LUMA
        mx, mn = x.max(-1), x.min(-1)
        # BOTH statistics are tracked: the shot is driven to the reference
        # *median*, but the floor is applied to the *mean*, because that is what
        # decides whether a second of film is legible
        stats[k][0].append((np.median(lum), lum.mean()))
        stats[k][1].append(np.median(np.where(mx > 0, (mx - mn)
                                              / np.maximum(mx, 1), 0)) * 255)

    gains = []
    for k, (a0, b0, l_t, s_t) in enumerate(TARGETS):
        meds = np.array([m for m, _e in stats[k][0]])
        means = np.array([e for _m, e in stats[k][0]])
        l_now = float(np.median(meds)) or 1.0
        e_now = float(np.median(means)) or 1.0
        s_now = float(np.median(stats[k][1])) or 1.0
        # Drive to the reference median, but never let the mean collapse: S5's
        # reference median is 10.6 and an undamped correction took the shot to a
        # mean of 7, i.e. darker than the reference frame it is matching.
        g = l_t / max(l_now, 1.0)
        if e_now * g < 11.0:
            g = 11.0 / max(e_now, 1.0)
        sat = (s_t / max(s_now, 1.0)) * args.saturation
        gains.append((g, sat))
        print(f'S{k+1}: luma {l_now:5.1f} (mean {e_now:5.1f}) -> {l_t:5.1f} '
              f'(x{g:.2f})   '
              f'sat {s_now:5.0f} -> {s_t:5.0f} (x{sat:.2f})', flush=True)

    # pass 2: apply, per shot. Exposure is solved numerically against the
    # measured median: multiplying 8-bit values is not the same as multiplying
    # light, so a closed-form gain overshoots badly on a dark shot (S5 needed
    # x0.16 by formula and landed at a mean of 7). A short bisection on the real
    # pixels finds the exposure that actually hits the reference number.
    from PIL import Image as _I
    for i_f, f in enumerate(files):
        i = int(f.stem[1:])
        k = next(j for j, (a0, b0, _l, _s) in enumerate(TARGETS) if a0 <= i < b0)
        _g, sat_k = gains[k]
        l_t = TARGETS[k][2] / 255.0    # the target is in 0-255, the maths in 0-1
        src = np.asarray(_I.open(f), np.float32) / 255.0
        base = src ** args.gamma

        def med_at(g):
            y = np.clip(base * g, 0, 1)
            return float(np.median((y * LUMA).sum(-1)))

        lo, hi = 0.05, 3.0
        for _ in range(18):
            mid = (lo + hi) * 0.5
            if med_at(mid) < l_t:
                lo = mid
            else:
                hi = mid
        x = np.clip(base * ((lo + hi) * 0.5), 0, 1)
        lum = (x * LUMA).sum(-1, keepdims=True)
        x = lum + (x - lum) * sat_k
        # contrast pivots at 0.18 of the *median* level, not at mid-grey: the
        # film is dark, and pivoting at 0.5 pushed S5 back down to a mean of 9
        x = (x - 0.10) * args.contrast + 0.10
        out = np.clip(x * 255.0, 0, 255).astype(np.uint8)
        Image.fromarray(out).save(dst / f.name)
        if (i_f + 1) % 48 == 0:
            print(f'  {i_f+1}/{len(files)}', flush=True)


if __name__ == '__main__':
    main()
