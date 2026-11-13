#!/usr/bin/env python3
"""The cue sheet: every SFX and music move, placed on a shot boundary."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shots import SHOTS

CHORD = {          # one chord per chapter, minor and cold
    0: [55.00, 82.41, 110.00],      # Am
    1: [55.00, 82.41, 130.81],      # Am(+C)
    2: [49.00, 73.42, 110.00],      # Gm-ish
    3: [43.65, 65.41, 98.00],       # Fm
    4: [41.20, 61.74, 92.50],       # Em low
    5: [43.65, 65.41, 87.31],       # Fm
    6: [49.00, 73.42, 98.00],       # G
    7: [55.00, 82.41, 110.00],
    8: [49.00, 73.42, 116.54],
    9: [41.20, 61.74, 82.41],
    10: [43.65, 65.41, 87.31],
    11: [55.00, 82.41, 110.00],
}

def timeline():
    t = 0.0
    rows = []
    for s in SHOTS:
        rows.append(dict(id=s["id"], ch=s["ch"], start=round(t, 3), dur=s["sec"]))
        t += s["sec"]
    return rows, round(t, 3)

def cues(rows):
    """Every cut gets a transition; only the specified beats get a boom."""
    out = []
    for i, r in enumerate(rows):
        # cut into this shot
        if i > 0:
            out.append(dict(t=max(0.0, r["start"] - 0.16), kind="whoosh",
                            gain=0.30 if r["ch"] < 6 else 0.22,
                            note="cut"))
        if r["id"] in ("S01", "S04", "S13", "S23", "S25", "S34", "S40", "S43", "S50"):
            out.append(dict(t=r["start"] + 0.10, kind="boom", gain=0.55, note="beat"))
        if r["id"] in ("S04", "S23", "S34", "S40", "S43"):
            out.append(dict(t=max(0.0, r["start"] - 2.2), kind="riser",
                            gain=0.26, note="approach"))
        if r["ch"] in (0, 4, 6, 8) and r["id"].endswith(("01", "03", "05")):
            out.append(dict(t=r["start"] + 0.2, kind="tick", gain=0.10, note="text card"))
    return out
