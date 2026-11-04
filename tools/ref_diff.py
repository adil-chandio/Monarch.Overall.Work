#!/usr/bin/env python3
"""Numeric diff: is the rebuild actually the same as the reference?

Comparing two videos by eye is how "looks close enough" happens. This compares
two `report.json` files produced by `tools/analyse_ref.py` field by field and
prints PASS / FAIL against an explicit tolerance per row. A rebuild is only
"same" when this table says so.

Usage:
    python3 tools/ref_diff.py analysis/ref01/report.json analysis/v4-build/report.json
    python3 tools/ref_diff.py ref.json build.json --tol-cuts 0.033 --markdown out.md
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

# row -> (tolerance, unit, weight) — tolerance is absolute unless stated
TOLERANCES: dict[str, tuple[float, str, str]] = {
    "width": (0, "px", "hard"),
    "height": (0, "px", "hard"),
    "fps": (0.05, "fps", "hard"),
    "duration": (0.10, "s", "hard"),
    "cut_count": (1, "cuts", "soft"),
    "cuts_per_minute": (2.0, "/min", "soft"),
    "median_shot": (0.15, "s", "soft"),
    "hook_first_cut": (0.10, "s", "soft"),
    "hook_cuts_3s": (1, "cuts", "soft"),
    "hook_motion_1s": (0.030, "abs", "soft"),
    "motion_mean": (0.020, "abs", "soft"),
    "motion_peak": (0.30, "abs", "soft"),
    "static_share": (0.10, "abs", "soft"),
    "saturation": (0.08, "abs", "soft"),
    "luma": (12.0, "abs", "soft"),
    "dark_share": (0.12, "abs", "soft"),
    "bright_share": (0.08, "abs", "soft"),
    "edge_density": (0.45, "abs", "soft"),
    "palette_distance": (22.0, "rgb", "soft"),
    "rms_db": (2.0, "dB", "soft"),
    "flatness": (0.035, "abs", "soft"),
    "periodicity": (0.12, "abs", "soft"),
    "lufs": (1.0, "LUFS", "hard"),
    "true_peak": (1.0, "dBTP", "soft"),
    "lra": (2.0, "LU", "soft"),
}


def load(path: str) -> dict[str, Any]:
    with open(path) as fh:
        return json.load(fh)


def g(rep: dict[str, Any], *path: str, default=None):
    cur: Any = rep
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def palette_distance(a: list, b: list) -> float:
    """Mean nearest-neighbour distance between two palettes, weighted equally."""
    if not a or not b:
        return 999.0
    pa = [hex_rgb(s["hex"] if isinstance(s, dict) else s) for s in a]
    pb = [hex_rgb(s["hex"] if isinstance(s, dict) else s) for s in b]
    dists = []
    for p in pa:
        dists.append(min(sum((x - y) ** 2 for x, y in zip(p, q)) ** 0.5 for q in pb))
    for q in pb:
        dists.append(min(sum((x - y) ** 2 for x, y in zip(p, q)) ** 0.5 for p in pa))
    return sum(dists) / len(dists)


def pair_cuts(ref: list[float], got: list[float]) -> tuple[list[float], float]:
    """Match cuts by index; return per-cut deltas and the worst one."""
    n = min(len(ref), len(got))
    deltas = [abs(ref[i] - got[i]) for i in range(n)]
    return deltas, (max(deltas) if deltas else 999.0)


def rows(ref: dict[str, Any], got: dict[str, Any]) -> list[tuple[str, str, str, str, bool]]:
    out: list[tuple[str, str, str, str, bool]] = []

    def add(name: str, a, b, tol: float, unit: str, note: str = "") -> None:
        try:
            delta = abs(float(a) - float(b))
        except (TypeError, ValueError):
            out.append((name, str(a), str(b), "n/a", False))
            return
        ok = delta <= tol
        out.append((name, f"{a}{unit}", f"{b}{unit}", f"±{delta:.3f}", ok))

    tol = TOLERANCES
    add("width", g(ref, "file", "width"), g(got, "file", "width"), 0, "", "exact")
    add("height", g(ref, "file", "height"), g(got, "file", "height"), 0, "", "exact")
    add("fps", g(ref, "file", "fps"), g(got, "file", "fps"), *tol["fps"])
    add("duration", g(ref, "file", "duration"), g(got, "file", "duration"), *tol["duration"])
    add("cut_count", g(ref, "cut_count"), g(got, "cut_count"), *tol["cut_count"])
    add("cuts_per_minute", g(ref, "cuts_per_minute"), g(got, "cuts_per_minute"), *tol["cuts_per_minute"])
    add("median_shot", g(ref, "shot_len", "median"), g(got, "shot_len", "median"), *tol["median_shot"])
    add("hook_first_cut", g(ref, "hook", "first_cut"), g(got, "hook", "first_cut"), *tol["hook_first_cut"])
    add("hook_cuts_3s", g(ref, "hook", "cuts_in_first_3s"), g(got, "hook", "cuts_in_first_3s"), *tol["hook_cuts_3s"])
    add("hook_motion_1s", g(ref, "hook", "motion_first_1s"), g(got, "hook", "motion_first_1s"), *tol["hook_motion_1s"])
    add("motion_mean", g(ref, "motion", "mean"), g(got, "motion", "mean"), *tol["motion_mean"])
    add("motion_peak", g(ref, "motion", "peak"), g(got, "motion", "peak"), *tol["motion_peak"])
    add("static_share", g(ref, "motion", "quiet_share"), g(got, "motion", "quiet_share"), *tol["static_share"])
    add("saturation", g(ref, "colour", "mean_saturation"), g(got, "colour", "mean_saturation"), *tol["saturation"])
    add("luma", g(ref, "colour", "mean_luma"), g(got, "colour", "mean_luma"), *tol["luma"])
    add("dark_share", g(ref, "colour", "dark_share"), g(got, "colour", "dark_share"), *tol["dark_share"])
    add("bright_share", g(ref, "colour", "bright_share"), g(got, "colour", "bright_share"), *tol["bright_share"])
    add("edge_density", g(ref, "type_density", "mean"), g(got, "type_density", "mean"), *tol["edge_density"])

    pd = palette_distance(g(ref, "palette", default=[]) or [], g(got, "palette", default=[]) or [])
    out.append(("palette_distance", "—", "—", f"{pd:.1f} rgb", pd <= tol["palette_distance"][0]))

    add("rms_db", g(ref, "audio", "rms_db"), g(got, "audio", "rms_db"), *tol["rms_db"])
    # spectral flatness only exists when the deep pass ran; it is optional here
    fa, fb = g(ref, "audio", "flatness_mean"), g(got, "audio", "flatness_mean")
    if fa is not None and fb is not None:
        add("flatness", fa, fb, *tol["flatness"])
    pa, pb = g(ref, "audio", "envelope_periodicity"), g(got, "audio", "envelope_periodicity")
    if pa is not None and pb is not None:
        add("periodicity", pa, pb, *tol["periodicity"])
    add("lufs", g(ref, "loudness", "input_i"), g(got, "loudness", "input_i"), *tol["lufs"])
    add("true_peak", g(ref, "loudness", "input_tp"), g(got, "loudness", "input_tp"), *tol["true_peak"])
    add("lra", g(ref, "loudness", "input_lra"), g(got, "loudness", "input_lra"), *tol["lra"])

    # cut alignment is its own row because one bad cut ruins the illusion
    rc = [float(c["time"]) for c in g(ref, "cuts", default=[]) or []]
    gc = [float(c["time"]) for c in g(got, "cuts", default=[]) or []]
    deltas, worst = pair_cuts(rc, gc)
    if deltas:
        within = sum(1 for d in deltas if d <= 0.033)
        out.append((
            "cut_alignment",
            f"{len(rc)} cuts",
            f"{len(gc)} cuts",
            f"{within}/{len(deltas)} within 1 frame (worst {worst * 1000:.0f} ms)",
            within == len(deltas),
        ))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("reference")
    ap.add_argument("rebuild")
    ap.add_argument("--markdown", help="write the table to this .md file too")
    args = ap.parse_args()

    ref, got = load(args.reference), load(args.rebuild)
    table = rows(ref, got)
    passed = sum(1 for r in table if r[4])

    lines = [
        "| metric | reference | rebuild | delta | verdict |",
        "|---|---|---|---|---|",
    ]
    for name, a, b, delta, ok in table:
        lines.append(f"| {name} | {a} | {b} | {delta} | {'PASS' if ok else 'FAIL'} |")
    lines.append("")
    lines.append(f"**{passed}/{len(table)} rows pass.**")
    body = "\n".join(lines)
    print(body)

    if args.markdown:
        with open(args.markdown, "w") as fh:
            fh.write("# Reference diff\n\n")
            fh.write(f"- reference: `{args.reference}`\n- rebuild: `{args.rebuild}`\n\n")
            fh.write(body + "\n")
        print(f"\nwrote {args.markdown}")

    # the exit code is the gate: a rebuild that misses a hard row fails the build
    hard_fail = [r for r in table if not r[4] and r[0] in
                 {"width", "height", "fps", "duration", "lufs", "cut_alignment"}]
    sys.exit(1 if hard_fail else 0)


if __name__ == "__main__":
    main()
