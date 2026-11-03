#!/usr/bin/env python3
"""Prove the film-analysis rig works on the runner, on every run.

`style.py` has been used by hand — on our own master, on synthetic films with known shot
lists — but never by CI. So nobody would notice if a runner lacked ffmpeg, or if numpy
changed an API under it, until the first time someone actually needed a reference match.

This builds a four-shot film inside the job (4 shots = exactly 3 cuts, known by
construction), analyses it, and fails if the detector disagrees. It costs ~2 seconds and a
few hundred kilobytes of /tmp, and it turns "the analysis code exists" into "the analysis
code runs here today".

Usage: python scripts/film-selftest.py [--keep]
Exit:  0 when the detected cut count matches, 1 when it does not (or ffmpeg is missing).
"""
from __future__ import annotations

import shutil
import sys
import tempfile


def main(argv: list[str]) -> int:
    sys.path.insert(0, ".")
    from yt_intel import calibrate_style, style

    tmp = tempfile.mkdtemp(prefix="filmselftest-")
    try:
        shots = [1.5, 2.0, 1.0, 2.5]          # 4 shots, 3 internal cuts, 7 s
        film = f"{tmp}/selftest.mp4"
        try:
            calibrate_style.make(film, shots)
        except Exception as e:                  # ffmpeg missing or codec unavailable
            print(f"film self-test: could not build the fixture — {type(e).__name__}: {e}")
            print("  the analysis path is untested on this machine; that is a failure, not a skip")
            return 1

        res = style.analyse(film)
        expected = len(shots) - 1
        got = res.get("cuts")
        dur = res.get("duration_s")
        print(f"film self-test: {len(shots)} shots / {expected} cuts expected · "
              f"detected {got} · {res.get('cuts_per_minute')}/min · {dur}s · "
              f"pacing: {str(res.get('pacing_verdict'))[:40]}")
        if got != expected:
            print(f"  MISMATCH: expected {expected} cuts, got {got}. "
                  f"threshold is {style.CUT_THRESHOLD} — this is the calibration drifting, "
                  f"or a codec/ffmpeg difference worth knowing about.")
            return 1
        if res.get("pacing_verdict") in (None, "unknown"):
            print("  pacing verdict missing: duration was not read, so cuts/min is not comparable")
            return 1
        print("  ok — fixture, detector and pacing all agree on this runner")
        return 0
    finally:
        if "--keep" in argv:
            print(f"  kept: {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
