#!/usr/bin/env python3
"""How far is the build from the reference, shot by shot, in numbers.

The gate is visual parity, so it has to be measured rather than argued about. For each
shot window this reports:

  mean|diff|   absolute pixel difference from the reference frame at the same instant
  SSIM         structural similarity, 1.0 = the same picture
  edges        a sharpness ratio (>1 means this build is sharper than the reference)
  black/dup    frames that are black, or identical to the frame before them

Unlike the old numeric diff, this walks a *window* rather than sampling one frame per
shot, because a shot can be right at its start and wrong by its end.

    python3 tools/match_ref.py --video public/demo/v4-30-silent.mp4
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cv2
import numpy as np

from ffbin import ffmpeg

W, H = 720, 1280
N = W * H * 3


def stream(path: str, frames: int) -> list[np.ndarray]:
    dec = subprocess.Popen([ffmpeg(), "-v", "error", "-i", path, "-frames:v", str(frames),
                            "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                           stdout=subprocess.PIPE, bufsize=N)
    out = []
    for _ in range(frames):
        b = dec.stdout.read(N)
        if len(b) < N:
            break
        out.append(np.frombuffer(b, np.uint8).reshape(H, W, 3))
    dec.kill()
    return out


def ssim(a: np.ndarray, b: np.ndarray) -> float:
    """Global SSIM on greyscale, on a decimated image — fast, and enough to rank shots."""
    ga = cv2.cvtColor(cv2.resize(a, (180, 320)), cv2.COLOR_BGR2GRAY).astype(np.float64)
    gb = cv2.cvtColor(cv2.resize(b, (180, 320)), cv2.COLOR_BGR2GRAY).astype(np.float64)
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    mu_a, mu_b = ga.mean(), gb.mean()
    va, vb = ga.var(), gb.var()
    cov = ((ga - mu_a) * (gb - mu_b)).mean()
    return ((2 * mu_a * mu_b + c1) * (2 * cov + c2)) / ((mu_a ** 2 + mu_b ** 2 + c1) * (va + vb + c2))


def acutance(a: np.ndarray) -> float:
    g = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(g, cv2.CV_32F).var())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", default="public/demo/v4-30-silent.mp4")
    ap.add_argument("--reference", default="analysis/attachment-filename-How-to-Edit-VIRAL-RE/reference.mp4")
    ap.add_argument("--spec", default="spec/film-01.json")
    ap.add_argument("--json", default="analysis/v4-build/match.json")
    ap.add_argument("--min-ssim", type=float, default=0.98)
    args = ap.parse_args()

    spec = json.loads(Path(args.spec).read_text())
    fps = spec["fps"]
    total = int(round(spec["duration"] * fps))
    ours, ref = stream(args.video, total), stream(args.reference, total)
    if len(ours) != len(ref):
        print(f"  frame counts differ: build {len(ours)}, reference {len(ref)}")

    print(f"{'shot':6s} {'frames':>6s} {'mean|diff|':>10s} {'SSIM':>7s} {'edges vs REF':>13s}  verdict")
    rows, worst = [], 1.0
    shot_of = {}
    for s in spec["shots"]:
        for f in range(int(round(s["start"] * fps)), int(round(s["end"] * fps))):
            shot_of[f] = s["id"]
    for s in spec["shots"]:
        i0, i1 = int(round(s["start"] * fps)), min(len(ours), int(round(s["end"] * fps)))
        if i1 <= i0:
            continue
        diffs, ss, eo, er, black, dup = [], [], [], [], 0, 0
        prev = None
        for i in range(i0, i1):
            diffs.append(float(np.abs(ours[i].astype(np.int16) - ref[i].astype(np.int16)).mean()))
            ss.append(ssim(ours[i], ref[i]))
            eo.append(acutance(ours[i])); er.append(acutance(ref[i]))
            if ours[i].mean() < 6:
                black += 1
            if prev is not None and np.array_equal(ours[i], prev):
                dup += 1
            prev = ours[i]
        s_mean = float(np.mean(ss))
        worst = min(worst, s_mean)
        verdict = "ok" if s_mean >= args.min_ssim else "BELOW GATE"
        if black:
            verdict += f", {black} black"
        if dup:
            verdict += f", {dup} frozen"
        print(f"{s['id']:6s} {i1 - i0:6d} {np.mean(diffs):10.2f} {s_mean:7.4f} "
              f"{np.mean(eo) / max(np.mean(er), 1e-6):13.2f}  {verdict}")
        rows.append({"shot": s["id"], "frames": i1 - i0,
                     "mean_abs_diff": round(float(np.mean(diffs)), 2),
                     "ssim": round(s_mean, 4),
                     "edges_vs_ref": round(float(np.mean(eo) / max(np.mean(er), 1e-6)), 3),
                     "black": black, "frozen": dup})

    print(f"\n  worst shot SSIM {worst:.4f}   (gate {args.min_ssim})")
    Path(args.json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json).write_text(json.dumps({"worst_ssim": round(worst, 4), "shots": rows}, indent=2))
    return 0 if worst >= args.min_ssim else 1


if __name__ == "__main__":
    raise SystemExit(main())
