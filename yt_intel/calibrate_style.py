"""Generate films with a known number of hard cuts, for calibrating style.py.

Why synthetic: the cut detector's threshold was tuned on one 36-second film and has been
quoted ever since. A threshold needs ground truth to be defensible, and no reference clip in
this repo has a verified shot list. A concat of solid-colour shots does: N shots = N-1
internal cuts, exactly, with no dissolves, no flashes and no camera motion to confuse it.

Run:  python -m yt_intel.calibrate_style [--keep]
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile

import numpy as np

from . import style

DEFAULT_SIZE = "640x360"
DEFAULT_FPS = 25
COLORS = ["red", "blue", "white", "black", "green", "yellow", "purple", "orange"]

# shots are durations in seconds; the expected cut count is len(shots) - 1
CASES = {
    "hardcuts": [2, 1, 3, 1.5, 2, 1, 4, 2],   # 7 cuts, ~16.5 s
    "longtake": [8],                            # 0 cuts
    "fastcuts": [0.5] * 20,                     # 19 cuts in 10 s = 114 cpm
    "slowfilm": [6, 6, 6, 6],                   # 3 cuts, 24 s = 7.5 cpm
}


def _ffmpeg() -> str:
    return style._ffmpeg()


def make(path: str, shots: list[float], size: str = DEFAULT_SIZE, fps: int = DEFAULT_FPS) -> int:
    """Concatenate solid-colour shots. Returns the number of internal cuts."""
    ff = _ffmpeg()
    tmpdir = tempfile.mkdtemp(prefix="ytstyle-")
    parts = []
    for i, secs in enumerate(shots):
        p = os.path.join(tmpdir, f"part{i}.mp4")
        subprocess.run(
            [ff, "-y", "-v", "error", "-f", "lavfi", "-i",
             f"color=c={COLORS[i % len(COLORS)]}:s={size}:d={secs}:r={fps}",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", p],
            check=True, capture_output=True,
        )
        parts.append(p)
    lst = os.path.join(tmpdir, "list.txt")
    with open(lst, "w") as f:
        f.write("".join(f"file '{p}'\n" for p in parts))
    subprocess.run([ff, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", path], check=True, capture_output=True)
    return len(shots) - 1


def graded_fixture(source: str, starts: list[float], seg: float = 2.0) -> tuple[str, list[float]]:
    """Six segments of a *real graded film*, concatenated with hard cuts.

    This exists because synthetic fixtures lied to us. Solid-colour shots said 0.14 was exact;
    on six real segments of our own master, 0.14 found 4 of 5 cuts and the old 0.22 found none.
    A fixture built from the footage we actually ship is the only one that can catch that.

    Returns (path, cut_times). The cuts are at seg, 2*seg, ... — exact by construction.
    """
    ff = _ffmpeg()
    tmpdir = tempfile.mkdtemp(prefix="ytgraded-")
    parts = []
    for i, start in enumerate(starts):
        p = os.path.join(tmpdir, f"part{i}.mp4")
        subprocess.run(
            [ff, "-y", "-v", "error", "-ss", str(start), "-i", source, "-t", str(seg),
             "-vf", "scale=480:270", "-r", "25", "-c:v", "libx264", "-pix_fmt", "yuv420p", p],
            check=True, capture_output=True,
        )
        parts.append(p)
    lst = os.path.join(tmpdir, "list.txt")
    with open(lst, "w") as f:
        f.write("".join(f"file '{p}'\n" for p in parts))
    out = os.path.join(tmpdir, "graded.mp4")
    subprocess.run([ff, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", out], check=True, capture_output=True)
    return out, [seg * (i + 1) for i in range(len(parts) - 1)]


def score(truth: list[float], detected: list[float], tol: float = 0.35) -> tuple[int, int]:
    """(hits, false_positives). A detection matches at most one truth value."""
    used, hit = set(), 0
    for t in truth:
        for i, x in enumerate(detected):
            if i in used:
                continue
            if abs(x - t) <= tol:
                used.add(i)
                hit += 1
                break
    return hit, len(detected) - hit


def sweep(thresholds: list[float] | None = None) -> dict:
    """Detect cuts on every synthetic case at every threshold. Returns accuracy per threshold."""
    thresholds = thresholds or [0.10, 0.14, 0.18, 0.22, 0.28, 0.34, 0.40]
    tmpdir = tempfile.mkdtemp(prefix="ytcal-")
    films = {}
    for name, shots in CASES.items():
        p = os.path.join(tmpdir, f"{name}.mp4")
        made = make(p, shots)
        films[name] = {"path": p, "expected": made, "shots": len(shots)}

    table = {}
    for th in thresholds:
        rows = {}
        exact = 0
        total_err = 0
        for name, f in films.items():
            res = style.analyse(f["path"], cut_threshold=th)
            got = res.get("cuts", 0)
            err = abs(got - f["expected"])
            rows[name] = {"expected": f["expected"], "got": got, "error": err}
            total_err += err
            if err == 0:
                exact += 1
        table[th] = {"cases": rows, "exact": exact, "total_abs_error": total_err}

    best = min(table, key=lambda t: (table[t]["total_abs_error"], abs(t - 0.22)))
    return {"thresholds": table, "best": best, "films": {k: v["expected"] for k, v in films.items()}}


GRADED_STARTS = [1.0, 5.0, 9.0, 15.0, 20.5, 25.0]
DEFAULT_GRADED = "deliverables/MON-DEMO26_Proof_Over_Promises_v3_1080p60_Master.mp4"


def sweep_graded(source: str = DEFAULT_GRADED, thresholds: list[float] | None = None) -> dict | None:
    """The same sweep on real graded footage. Returns None when the source is not present."""
    if not os.path.exists(source):
        return None
    thresholds = thresholds or [0.06, 0.08, 0.10, 0.12, 0.14, 0.18, 0.22]
    film, truth = graded_fixture(source, GRADED_STARTS)
    table = {}
    for th in thresholds:
        res = style.analyse(film, cut_threshold=th)
        # analyse() reports counts, so recover times the same way the analyser does
        prev, times, diffs = None, [], []
        for _, a, t in style.frames(film, fps=4.0):
            if prev is not None:
                diffs.append(float(np.abs(a - prev).mean()))
                times.append(t)
            prev = a
        det = [times[i] for i, d in enumerate(diffs) if d >= th]
        hit, false = score(truth, det)
        table[th] = {"hits": hit, "of": len(truth), "false": false, "cpm": res.get("cuts_per_minute")}
    best = max(table, key=lambda t: (table[t]["hits"] - table[t]["false"] * 0.25, -t))
    return {"thresholds": table, "best": best, "cuts": len(truth), "film": film}


def main(argv: list[str]) -> int:
    res = sweep()
    print("synthetic cut-detection calibration\n")
    print(f"{'threshold':>9}  {'exact':>5}  {'abs err':>7}  per-case (expected/got)")
    for th, row in res["thresholds"].items():
        cells = " ".join(f"{k}={v['expected']}/{v['got']}" for k, v in row["cases"].items())
        mark = "  <- best" if th == res["best"] else ""
        print(f"{th:>9.2f}  {row['exact']}/4  {row['total_abs_error']:>7}  {cells}{mark}")
    print(f"\nbest threshold on this rig: {res['best']:.2f}")
    print("caveat: solid-colour concat is the easiest possible case (no motion, no dissolves).")
    print("A threshold that wins here is necessary, not sufficient — see the graded sweep below.")

    graded = sweep_graded()
    if graded is None:
        print(f"\ngraded sweep: source not found ({DEFAULT_GRADED}) — skipped")
        return 0
    print(f"\nreal graded footage — {graded['cuts']} known hard cuts from our own master\n")
    print(f"{'threshold':>9}  {'hits':>7}  {'false':>6}  {'cpm':>6}")
    for th, row in graded["thresholds"].items():
        mark = "  <- best" if th == graded["best"] else ""
        print(f"{th:>9.2f}  {row['hits']:>2}/{row['of']}     {row['false']:>6}  {row['cpm']:>6}{mark}")
    print(f"\nbest on graded footage: {graded['best']:.2f} (shipped value: {style.CUT_THRESHOLD:.2f})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
