"""Fail the render if a scene's own content is cut off while that scene is playing.

Two renders shipped with the first character of every headline sliced off, because the camera
drifted past the anchor. I missed it twice in a contact sheet, so it is a check now.

The first version of this check was wrong in the other direction: it flagged content at the
left edge during a whip, which is exactly what an outgoing scene is supposed to do. Content is
only required to be inside the frame while its scene is on its anchor — so the check renders the
actual compositions (not a decoded encode) at times inside every beat and ignores the seams.

Usage: python showreel/qc_framing.py
"""
from __future__ import annotations

import sys

from PIL import Image, ImageDraw
import numpy as np

import os
import sys as _s
_s.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from showreel import viral_short as V

MARGIN = 8          # px of background required at each edge
THRESHOLD = 60      # luma above this is content, not the gradient


def check() -> int:
    """Compose each scene alone, on its anchor, and measure its own bounding box.

    Checking a full frame cannot work: during every seam the outgoing scene is legitimately
    hanging off the left edge and the incoming one off the right. What must hold is that a
    scene, played on its own anchor, sits inside the margins.
    """
    from PIL import Image
    D = V.load()
    failures = []
    checked = 0
    for i, (s0, s1) in enumerate(V.BEATS):
        cam = V.ANCHORS[i] - V.LEFT_MARGIN
        for frac in (0.15, 0.5, 0.85):
            t = s0 + (s1 - s0) * frac
            img = Image.new("RGB", (V.W, V.H), V.BG1)
            d = ImageDraw.Draw(img)
            V.SCENES[i](d, cam, t, D)
            a = np.asarray(img).astype(np.int16).mean(axis=2)
            mask = a > 70 + 10          # above the flat background fill
            if not mask.any():
                continue
            cols = np.where(mask.any(axis=0))[0]
            rows = np.where(mask.any(axis=1))[0]
            checked += 1
            if (cols.min() < MARGIN or cols.max() > V.W - MARGIN
                    or rows.min() < MARGIN or rows.max() > V.H - MARGIN):
                failures.append((i, round(t, 2), int(cols.min()), int(cols.max()),
                                 int(rows.min()), int(rows.max())))

    if failures:
        print(f"FRAMING FAIL — {len(failures)} of {checked} compositions touch an edge")
        for f in failures:
            print(f"  scene {f[0]} t={f[1]:>5}s  cols {f[2]}-{f[3]}  rows {f[4]}-{f[5]}")
        return 1
    print(f"framing ok — {checked} compositions, none touching an edge")
    return 0


if __name__ == "__main__":
    sys.exit(check())
