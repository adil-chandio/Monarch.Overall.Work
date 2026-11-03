"""
Reference matching: measure a reference track and your own, then say exactly which
band and which section is off, and by how much.

Output is deliberately numeric. No adjectives, no "feels warmer".
"""
from __future__ import annotations

import json
from typing import Iterable

import numpy as np

from .core import analyse, BANDS, band_energy_curve, load_audio, onset_density, spectral_profile


def _resample_curve(curve: list[float], n: int) -> np.ndarray:
    arr = np.asarray(curve, dtype=float)
    if arr.size == n:
        return arr
    if arr.size < 2:
        return np.full(n, arr.mean() if arr.size else -100.0)
    xp = np.linspace(0, 1, arr.size)
    x = np.linspace(0, 1, n)
    return np.interp(x, xp, arr)


def compare_tracks(reference_path: str, candidate_path: str, sections: int = 8) -> dict:
    """Compare two files. Bands are compared on a normalised time grid, per section."""
    ref, cand = analyse(reference_path), analyse(candidate_path)

    r_bands = ref["bands"]
    c_bands = cand["bands"]

    section_deltas = {}
    worst = []
    for name, lo, hi in BANDS:
        r = _resample_curve(r_bands[name], 100)
        c = _resample_curve(c_bands[name], 100)
        # normalise each band curve to its own mean so we compare *movement*, not level
        r_n = r - r.mean()
        c_n = c - c.mean()
        # pad so sections divide evenly
        k = 100 // sections
        r_s = r_n[:k * sections].reshape(sections, k).mean(axis=1)
        c_s = c_n[:k * sections].reshape(sections, k).mean(axis=1)
        delta = c_s - r_s
        section_deltas[name] = [round(float(v), 2) for v in delta]
        worst.append({
            "band": name,
            "range_hz": f"{lo}-{hi}",
            "mean_delta_db": round(float(delta.mean()), 2),
            "worst_section": int(np.argmax(np.abs(delta))) + 1,
            "worst_delta_db": round(float(delta[np.argmax(np.abs(delta))]), 2),
        })

    worst.sort(key=lambda d: -abs(d["worst_delta_db"]))

    r_onsets = np.asarray(ref["onsets"]["onsets_per_s"], dtype=float)
    c_onsets = np.asarray(cand["onsets"]["onsets_per_s"], dtype=float)
    r_dens = float(r_onsets.mean()) if r_onsets.size else 0.0
    c_dens = float(c_onsets.mean()) if c_onsets.size else 0.0

    r_spec, c_spec = ref["spectrum"]["band_db_rel_total"], cand["spectrum"]["band_db_rel_total"]
    spec_delta = {k: round(c_spec[k] - r_spec[k], 2) for k in r_spec}

    r_l, c_l = ref["loudness"], cand["loudness"]
    return {
        "reference": {"file": ref["path"], **r_l, "harsh": ref["spectrum"]["harsh"],
                      "onsets_per_s": round(r_dens, 2)},
        "candidate": {"file": cand["path"], **c_l, "harsh": cand["spectrum"]["harsh"],
                      "onsets_per_s": round(c_dens, 2)},
        "loudness_gap_lu": round(c_l["integrated_lufs"] - r_l["integrated_lufs"], 2),
        "lra_gap_lu": round(c_l["lra_lu"] - r_l["lra_lu"], 2),
        "density_gap_onsets": round(c_dens - r_dens, 2),
        "spectrum_delta_db": spec_delta,
        "sections": sections,
        "band_section_deltas_db": section_deltas,
        "worst_bands": worst,
    }


def match_report(reference_path: str, candidate_path: str, sections: int = 8) -> str:
    """Human-readable verdict with a concrete, prioritised fix list."""
    r = compare_tracks(reference_path, candidate_path, sections)
    lines = [
        f"REFERENCE : {r['reference']['file']}  "
        f"{r['reference']['integrated_lufs']} LUFS / LRA {r['reference']['lra_lu']} / "
        f"{r['reference']['onsets_per_s']} onsets/s",
        f"CANDIDATE : {r['candidate']['file']}  "
        f"{r['candidate']['integrated_lufs']} LUFS / LRA {r['candidate']['lra_lu']} / "
        f"{r['candidate']['onsets_per_s']} onsets/s",
        "",
        f"LOUDNESS GAP : {r['loudness_gap_lu']:+.2f} LU   (negative = ours is quieter)",
        f"DYNAMICS GAP : {r['lra_gap_lu']:+.2f} LU       (negative = ours is flatter)",
        f"DENSITY GAP  : {r['density_gap_onsets']:+.2f} onsets/s  (negative = ours is emptier)",
        "",
        "SPECTRUM (ours minus reference, dB, relative to total energy):",
    ]
    for k, v in r["spectrum_delta_db"].items():
        flag = "  <-- fix" if abs(v) >= 2.5 else ""
        lines.append(f"  {k:>9}: {v:+.2f}{flag}")

    lines += ["", "WORST BANDS (by movement mismatch, per section):"]
    for w in r["worst_bands"][:4]:
        lines.append(
            f"  {w['band']:>9} ({w['range_hz']} Hz): mean {w['mean_delta_db']:+.2f} dB, "
            f"worst at section {w['worst_section']} ({w['worst_delta_db']:+.2f} dB)"
        )

    lines += ["", "SECTION MOVEMENT (ours minus reference, dB, per band):"]
    header = "section".ljust(9) + "".join(f"{n[:8]:>9}" for n, _, _ in BANDS)
    lines.append(header)
    for i in range(r["sections"]):
        row = f"{i + 1:<9}" + "".join(
            f"{r['band_section_deltas_db'][n][i]:>9.2f}" for n, _, _ in BANDS
        )
        lines.append(row)

    fixes = []
    if r["loudness_gap_lu"] < -1.5:
        fixes.append(f"raise integrated loudness by {abs(r['loudness_gap_lu']):.1f} LU (loudnorm I)")
    if r["lra_gap_lu"] < -2:
        fixes.append("our mix is flatter than the reference — open the arrangement dynamics (stems in/out, not volume)")
    if r["density_gap_onsets"] < -1.5:
        fixes.append(f"add {abs(r['density_gap_onsets']):.1f} events/second — the arrangement is too sparse")
    for band, delta in r["spectrum_delta_db"].items():
        if abs(delta) >= 3.0:
            direction = "cut" if delta > 0 else "lift"
            fixes.append(f"{direction} {band} by about {abs(delta) - 1:.1f} dB at the stem level")
    if r["candidate"]["harsh"] and not r["reference"]["harsh"]:
        fixes.append("our 2.5-5 kHz is hotter than the reference's — thin the pluck/exciter stack")

    lines += ["", "FIX LIST (in order):"]
    lines += [f"  {i + 1}. {f}" for i, f in enumerate(fixes)] or ["  none — within tolerance"]

    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    import sys
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) < 2:
        print("usage: python -m showreel.audio_qc.compare <reference> <candidate> [--json out.json] [--sections N]")
        return 2
    sections = 8
    if "--sections" in args:
        i = args.index("--sections")
        sections = int(args[i + 1])
        del args[i:i + 2]
    json_out = None
    if "--json" in args:
        i = args.index("--json")
        json_out = args[i + 1]
        del args[i:i + 2]
    report = match_report(args[0], args[1], sections)
    print(report)
    if json_out:
        with open(json_out, "w", encoding="utf-8") as fh:
            json.dump(compare_tracks(args[0], args[1], sections), fh, indent=2)
        print(f"\nwrote {json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
