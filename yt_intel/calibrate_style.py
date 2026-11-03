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
    print("A threshold that wins here is necessary, not sufficient — graded footage needs its own pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
