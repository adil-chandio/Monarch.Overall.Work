"""Production-style forensics: how a video is *built*, not what it says.

Titles and thumbnails are the packaging. This module measures the film:

  shot_lengths      cuts detected from frame-to-frame difference; median + p10/p90
  cuts_per_minute   edit rhythm (a Short cuts 4-8x more often than a video essay)
  motion_profile    normalised inter-frame energy over time — where it breathes, where it spikes
  palette           mean saturation, contrast and the dominant hues across the film
  overlay_density   edge energy in the lower third over time — burned-in captions/graphics
  hook_cut_rate     cuts in the first 3 s (the number most people never measure)

It reads a local file. For a YouTube video, download a low-res copy first
(`yt-dlp -f "bv*[height<=480]+ba/b[height<=480]" <url>`) — this tool does not download
anything itself, deliberately: style analysis needs 20 MB, not 2 GB, and hotlinking other
people's video is not something a studio tool should do.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import numpy as np


def _ffmpeg() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        from shutil import which
        exe = which("ffmpeg")
        if not exe:
            raise RuntimeError("ffmpeg not found: pip install imageio-ffmpeg")
        return exe


def frames(path: str, fps: float = 4.0, width: int = 160):
    """Yield (index, RGB float array, t) at a low frame rate. Small on purpose."""
    h = int(width * 9 / 16)
    cmd = [_ffmpeg(), "-v", "error", "-i", path, "-vf", f"fps={fps},scale={width}:{h}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    size = width * h * 3
    i = 0
    try:
        while True:
            buf = proc.stdout.read(size)
            if len(buf) < size:
                break
            arr = np.frombuffer(buf, dtype=np.uint8).reshape(h, width, 3).astype(np.float32) / 255.0
            yield i, arr, i / fps
            i += 1
    finally:
        proc.stdout.close()
        proc.wait()


def duration(path: str) -> float:
    out = subprocess.run([_ffmpeg(), "-i", path], capture_output=True, text=True).stderr
    for line in out.splitlines():
        if "Duration:" in line:
            hms = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = hms.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 0.0


# Threshold history, in the order the evidence arrived — this is the useful part:
#
#   0.22  shipped for months. Tuned on one 36 s film. On synthetic hard-cut fixtures it found
#         6 of 7 and 15 of 19 cuts.
#   0.14  what synthetic fixtures said was exact (4/4 cases).
#   0.14  what real graded footage said was still broken: on six real segments of our own
#         master, concatenated with five known hard cuts, it found 4 of 5.
#   0.10  finds 5 of 5 on the same fixture with 2 false positives; 0.22 found 0 of 5.
#
# The synthetic answer (0.14) was closer to the truth than 0.22 and still wrong, because
# solid-colour shots are the easiest case that exists. Graded footage is the case that matters.
#
# The deeper finding: on this film a real cut can have a *lower* frame delta (0.074) than a
# whip-pan or a flash that is not a cut (peak 0.406). No single absolute threshold separates
# them, so the number below is a best-effort line and `adaptive_cuts` reports a second opinion
# beside it. Two detectors that disagree is information; one detector is a guess with a decimal.
CUT_THRESHOLD = 0.10


def adaptive_cuts(times: list[float], diffs, k: float = 3.0, window: int = 6,
                  floor: float = 0.035) -> list[float]:
    """Cuts as local spikes rather than absolute values.

    A hard cut is a discontinuity *for that part of that film*: a quiet conversation edited at
    0.05 and an action sequence edited at 0.15 both cut, and neither is the other's threshold.
    This walks the delta series, compares each frame to the median of its neighbourhood, and
    keeps peaks that clear both that neighbourhood and an absolute floor.

    It is not the primary detector — on our own graded fixture it found 4 of 5 known cuts while
    a flat 0.10 found 5 of 5. It is here as a second opinion so that a video where the two
    methods disagree loudly is visibly uncertain instead of confidently wrong.
    """
    import numpy as _np
    d = _np.asarray(diffs, dtype=float)
    n = len(d)
    if n == 0:
        return []
    out = []
    for i in range(n):
        lo, hi = max(0, i - window), min(n, i + window + 1)
        local = float(_np.median(d[lo:hi])) + 1e-4
        if d[i] < max(floor, k * local):
            continue
        if i > 0 and d[i] < d[i - 1]:
            continue
        if i < n - 1 and d[i] < d[i + 1]:
            continue
        out.append(times[i])
    return out


def _agreement(primary: list[float], second: list[float], tol: float = 0.35) -> dict:
    """How much the two detectors agree. Shown, never used to silently pick a winner."""
    matched = sum(1 for a in primary if any(abs(a - b) <= tol for b in second))
    return {
        "matched": matched,
        "primary_only": len(primary) - matched,
        "second_only": len(second) - matched,
        "verdict": ("both methods agree" if matched and len(primary) - matched <= 1 and len(second) - matched <= 1
                    else "the two methods disagree — treat cuts_per_minute as a range, not a number"
                    if primary or second else "neither method found a cut"),
    }


def analyse(path: str, fps: float = 4.0, cut_threshold: float | None = None) -> dict:
    """cut_threshold is on normalised RGB distance between consecutive sampled frames.

    Default comes from `CUT_THRESHOLD`, which is calibrated but not universal: solid-colour
    concat is the easiest case (no motion, no dissolves). Graded footage with fast pans needs
    its own pass — `calibrate_style.sweep()` shows how, and the numbers here are a starting
    point, never a certificate.
    """
    if cut_threshold is None:
        cut_threshold = CUT_THRESHOLD
    prev = None
    diffs, motion, sat, contrast, lower_edges, times = [], [], [], [], [], []
    h = w = 0
    for i, a, t in frames(path, fps=fps):
        h, w = a.shape[:2]
        if prev is not None:
            d = float(np.abs(a - prev).mean())
            diffs.append(d)
            motion.append(d)
            times.append(t)
        mx, mn = a.max(axis=2), a.min(axis=2)
        sat.append(float(((mx - mn) / (mx + 1e-6)).mean()))
        y = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
        contrast.append(float(y.std()))
        gy, gx = np.gradient(y)
        band = np.abs(gy[int(h * 0.72):int(h * 0.98)]) + np.abs(gx[int(h * 0.72):int(h * 0.98)])
        lower_edges.append(float(band.mean()))
        prev = a

    if not diffs:
        return {"status": "no_frames", "path": path}

    diffs_a = np.array(diffs)
    cuts = np.where(diffs_a >= cut_threshold)[0]
    cut_times = [times[i] for i in cuts]
    # Second opinion, reported not merged: a cut is also plausibly a spike against its own
    # neighbourhood. When the two disagree by a wide margin the honest output is the
    # disagreement, because on graded footage neither method is reliably right on its own.
    adaptive = adaptive_cuts(times, diffs_a)
    shot_bounds = [0.0] + cut_times + [duration(path) or times[-1]]
    lengths = [round(b - a, 2) for a, b in zip(shot_bounds, shot_bounds[1:]) if b - a > 0.05]
    dur = duration(path) or times[-1]
    first3 = [t for t in cut_times if t <= 3.0]

    return {
        "status": "ok", "path": os.path.basename(path), "duration_s": round(dur, 2),
        "sample_fps": fps,
        "cuts": len(cut_times),
        "cuts_per_minute": round(len(cut_times) / (dur / 60), 2) if dur else None,
        "hook_cuts_first_3s": len(first3),
        "adaptive_cuts": len(adaptive),
        "cut_agreement": _agreement(cut_times, adaptive),
        "shot_median_s": round(float(np.median(lengths)), 2) if lengths else None,
        "shot_p10_s": round(float(np.percentile(lengths, 10)), 2) if lengths else None,
        "shot_p90_s": round(float(np.percentile(lengths, 90)), 2) if lengths else None,
        "longest_shot_s": round(max(lengths), 2) if lengths else None,
        "motion_mean": round(float(np.mean(motion)), 4),
        "motion_peak": round(float(np.max(motion)), 4),
        "motion_quiet_share": round(float((diffs_a < 0.05).mean()), 3),
        "saturation_mean": round(float(np.mean(sat)), 3),
        "contrast_mean": round(float(np.mean(contrast)), 3),
        "overlay_density_mean": round(float(np.mean(lower_edges)), 4),
        "overlay_density_peak": round(float(np.max(lower_edges)), 4),
        "pacing_verdict": _pacing(len(cut_times), dur),
    }


def _pacing(cuts: int, dur: float) -> str:
    if not dur:
        return "unknown"
    cpm = cuts / (dur / 60)
    if cpm >= 24:
        return "maximalist — short-form native, high retention risk if the content is thin"
    if cpm >= 12:
        return "punchy — YouTube editorial standard"
    if cpm >= 5:
        return "measured — essay/documentary rhythm"
    return "slow — only survives on authority or genuinely beautiful footage"


def compare(a: dict, b: dict) -> dict:
    """How does our film differ from theirs? This is the reference-match, for editing."""
    keys = ["cuts_per_minute", "shot_median_s", "hook_cuts_first_3s", "motion_mean",
            "saturation_mean", "contrast_mean", "overlay_density_mean"]
    out = {}
    for k in keys:
        av, bv = a.get(k), b.get(k)
        if av is None or bv is None:
            continue
        out[k] = {"ours": av, "theirs": bv, "delta": round((av - bv), 3),
                  "ratio": round(av / bv, 2) if bv else None}
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    path = argv[1]
    res = analyse(path)
    if "--json" in argv:
        out = argv[argv.index("--json") + 1]
        with open(out, "w") as f:
            json.dump(res, f, indent=2)
        print(f"wrote {out}")
        return 0
    if res.get("status") != "ok":
        print(json.dumps(res, indent=2))
        return 1
    print(f"\nPRODUCTION STYLE · {res['path']}  ({res['duration_s']}s)")
    print(f"  cuts            {res['cuts']}  ({res['cuts_per_minute']}/min)")
    print(f"  hook cuts 0-3s  {res['hook_cuts_first_3s']}")
    print(f"  shot length     median {res['shot_median_s']}s · p10 {res['shot_p10_s']} · p90 {res['shot_p90_s']} · longest {res['longest_shot_s']}")
    print(f"  motion          mean {res['motion_mean']} · peak {res['motion_peak']} · quiet {res['motion_quiet_share']:.0%}")
    print(f"  look            saturation {res['saturation_mean']} · contrast {res['contrast_mean']}")
    print(f"  lower-third     edge density mean {res['overlay_density_mean']} · peak {res['overlay_density_peak']}")
    print(f"  pacing          {res['pacing_verdict']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
