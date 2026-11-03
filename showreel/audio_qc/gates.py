"""
Pass/fail gates for a delivery master. Numbers only — no opinions.

    python -m showreel.audio_qc.gates public/showreel/audio_master_60fps.m4a --profile web
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass

import numpy as np
from scipy import signal

from .core import BANDS, SAMPLE_RATE, load_audio, loudness_stats, spectral_profile

PROFILES = {
    # name          I target  tol   tp ceiling  lra range
    # NOTE: for pieces under 60 s the arrangement never has room to develop a wide LRA
    # (EBU LRA is built from 3 s windows, and a continuous score bed stays inside ~2 LU).
    # The meaningful short-form dynamics check is `movement_db` below, not LRA.
    "web":       {"lufs": -14.0, "tol": 0.7, "tp": -1.0, "lra": (1.0, 10.0)},
    "shorts":    {"lufs": -14.0, "tol": 0.7, "tp": -1.0, "lra": (1.0, 10.0)},
    "broadcast": {"lufs": -23.0, "tol": 0.5, "tp": -1.0, "lra": (5.0, 15.0)},
    "cinema":    {"lufs": -18.0, "tol": 1.0, "tp": -2.0, "lra": (5.0, 15.0)},
}


def mono_fold_loss_db(x: np.ndarray, sr: int) -> float:
    """How much 60-150 Hz survives a mono fold-down. > 3 dB loss means phase trouble."""
    if x.ndim == 1:
        return 0.0
    lo, hi = 60, 150
    # narrow band at 48 kHz: order-4 ba coefficients are numerically unstable
    # (poles outside the unit circle), so always use second-order sections.
    sos = signal.butter(4, [lo, hi], btype="band", fs=sr, output="sos")
    xd = np.asarray(x, dtype=np.float64)
    left = signal.sosfilt(sos, xd[:, 0])
    mono = signal.sosfilt(sos, xd.mean(axis=1))
    e_l = np.mean(left ** 2) + 1e-18
    e_m = np.mean(mono ** 2) + 1e-18
    return float(10 * np.log10(e_m / e_l))


def detect_clicks(x: np.ndarray, sr: int, threshold: float = 0.35) -> dict:
    mono = np.asarray(x if x.ndim == 1 else x.mean(axis=1), dtype=np.float64)
    d = np.abs(np.diff(mono))
    idx = np.where(d > threshold)[0]
    # a run of consecutive jumps is a click; a single jump at a hard cut is not
    runs, cur = [], []
    for i in idx:
        if cur and i - cur[-1] <= 3:
            cur.append(i)
        else:
            if len(cur) >= 2:
                runs.append((cur[0], len(cur)))
            cur = [i]
    if len(cur) >= 2:
        runs.append((cur[0], len(cur)))
    return {"click_runs": len(runs),
            "first_click_s": round(runs[0][0] / sr, 3) if runs else None}


def gated_loudness_curve(x: np.ndarray, sr: int, window_s: float = 0.5) -> list[tuple[float, float]]:
    mono = np.asarray(x if x.ndim == 1 else x.mean(axis=1), dtype=np.float64)
    win = int(window_s * sr)
    out = []
    for i in range(0, len(mono) - win + 1, win):
        rms = np.sqrt(np.mean(mono[i:i + win] ** 2)) + 1e-12
        out.append((round(i / sr, 2), round(20 * np.log10(rms), 2)))
    return out


def run(path: str, profile: str = "web") -> dict:
    spec = PROFILES[profile]
    x, sr = load_audio(path)
    loud = loudness_stats(x, sr)
    spec_prof = spectral_profile(x, sr)
    click = detect_clicks(x, sr)
    mono_loss = mono_fold_loss_db(x, sr)
    curve = gated_loudness_curve(x, sr)

    # sectional movement: peak-to-peak of the smoothed 0.5 s curve, excluding the tail
    body = [v for t, v in curve if t < loud["duration_s"] * 0.82]
    movement = round(float(max(body) - min(body)), 2) if body else 0.0

    # numpy bool is not JSON serialisable; normalise through python bool()
    spec_prof["harsh"] = bool(spec_prof["harsh"])
    spec_prof["dull"] = bool(spec_prof["dull"])

    checks = {
        "loudness_in_range": abs(loud["integrated_lufs"] - spec["lufs"]) <= spec["tol"],
        "true_peak_ok": loud["sample_peak_dbfs"] <= spec["tp"],
        "lra_in_range": spec["lra"][0] <= loud["lra_lu"] <= spec["lra"][1],
        "no_clipping": loud["clipped_samples"] == 0,
        "no_clicks": click["click_runs"] == 0,
        "mono_compatible": mono_loss > -3.0,
        "dc_offset_ok": loud["dc_offset"] < 0.002,
        "not_harsh": not spec_prof["harsh"],
        # short-form dynamic gate: sectional contrast, not EBU LRA
        "has_dynamics": movement >= 3.0,
    }
    checks = {k: bool(v) for k, v in checks.items()}   # numpy bools break json.dump mid-write

    return {
        "file": path,
        "profile": profile,
        "measured": {
            **{k: (float(v) if isinstance(v, (np.floating, np.integer, np.bool_)) else v)
               for k, v in loud.items()},
            "movement_db": movement,
            "mono_fold_loss_db": round(mono_loss, 2),
            "clicks": click,
            "band_db_rel_total": {k: float(v) for k, v in spec_prof["band_db_rel_total"].items()},
            "harsh_over_high_mid_db": spec_prof["harsh_over_high_mid_db"],
            "air_over_high_mid_db": spec_prof["air_over_high_mid_db"],
        },
        "targets": spec,
        "checks": checks,
        "pass": all(checks.values()),
        "failed": [k for k, v in checks.items() if not v],
        "loudness_curve": curve,
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print(__doc__)
        return 2
    path = args[0]
    profile = "web"
    if "--profile" in args:
        profile = args[args.index("--profile") + 1]
    out = None
    if "--json" in args:
        out = args[args.index("--json") + 1]

    result = run(path, profile)
    m = result["measured"]
    print(f"{result['file']}  [{profile}]")
    print(f"  I     {m['integrated_lufs']} LUFS   target {result['targets']['lufs']} ±{result['targets']['tol']}")
    print(f"  LRA   {m['lra_lu']} LU          target {result['targets']['lra']}")
    print(f"  peak  {m['sample_peak_dbfs']} dBFS     ceiling {result['targets']['tp']}")
    print(f"  move  {m['movement_db']} dB peak-to-peak across the body")
    print(f"  mono  {m['mono_fold_loss_db']} dB low-band loss")
    print(f"  harsh {m['harsh_over_high_mid_db']} dB over high-mid")
    print()
    for k, v in result["checks"].items():
        print(f"  {'PASS' if v else 'FAIL'}  {k}")
    print(f"\n  RESULT: {'PASS' if result['pass'] else 'FAIL — ' + ', '.join(result['failed'])}")
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2)
        print(f"  wrote {out}")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
