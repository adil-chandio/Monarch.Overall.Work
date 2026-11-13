#!/usr/bin/env python3
"""Build `sfx/` as data, exactly as `skills/monarch-video-lab/sfx-library` defines it.

That skill is blunt about the failure it exists to prevent: "a sound effect is only
reusable if you can prove where it came from and what it measures", and cues must
not be "re-invented per project". The orca film synthesised nine voices; this writes
them to the house library with the required manifest row for each, so the next film
can `sfx.by_tag("whoosh")` instead of writing a fourth whoosh.

Every measured field is measured. Nothing is guessed: a field that cannot be
computed is written as null.

  python scripts/build-sfx-library.py --out sfx
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import wave
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

SR = 48000

# family, material, variant, generator-name
CATALOGUE = [
    ("ui", "thock", "warm", "film_tick"),
    ("transition", "whoosh", "silk", "silk_whoosh"),
    ("transition", "riser", "spectral", "spectral_riser"),
    ("impact", "boom", "sub", "cinema_sub_boom"),
    ("musical", "sting", "glass", "glass_sting"),
    ("ambience", "shimmer", "krill", "krill_shimmer"),
    ("ambience", "bubble", "rise", "bubble_rise"),
    ("musical", "ping", "sonar", "sonar_ping"),
    ("natural", "moan", "humpback", "whale_moan"),
]

TAGS = {
    "film_tick": ["ui", "warm", "wood", "no-high-click"],
    "silk_whoosh": ["transition", "water", "airy", "formant"],
    "spectral_riser": ["transition", "tension", "build", "sweep"],
    "cinema_sub_boom": ["impact", "sub", "cinema", "low"],
    "glass_sting": ["musical", "in-key-D", "glass", "soft-attack"],
    "krill_shimmer": ["ambience", "texture", "biological", "wide"],
    "bubble_rise": ["ambience", "water", "biological", "sparse"],
    "sonar_ping": ["musical", "clean", "signal", "sci"],
    "whale_moan": ["natural", "biological", "low", "long"],
}


def load_generators():
    """Import the film's audio script and rebuild each voice at unity gain."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("oa", REPO / "scripts" / "orca3d-audio.py")
    oa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oa)
    DSL = oa.DSL

    def glass_sting():
        return DSL.synth_felt_glass_pluck(62, 0.7, 1.0)

    return {
        "film_tick": lambda: oa.film_tick(1.0),
        "silk_whoosh": lambda: DSL.silk_whoosh(0.46, -0.4, 0.4, 1.0).mean(axis=1),
        "spectral_riser": lambda: oa.spectral_riser(1.5, 1.0),
        "cinema_sub_boom": lambda: np.asarray(DSL.cinema_sub_boom(1.25, 36.71, 1.0)).mean(axis=1),
        "glass_sting": glass_sting,
        "krill_shimmer": lambda: oa.krill_shimmer(3.2, 1.0),
        "bubble_rise": lambda: oa.bubble_rise(1.6, 1.0),
        "sonar_ping": lambda: oa.sonar_ping(1.25, 1180.0, 1.0),
        "whale_moan": lambda: oa.whale_moan(2.9, 470.0, 232.0, 1.0),
    }


def write_wav(path: Path, x: np.ndarray):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def band_energy(x: np.ndarray) -> dict:
    spec = np.abs(np.fft.rfft(x)) ** 2
    f = np.fft.rfftfreq(len(x), 1.0 / SR)
    tot = float(np.sum(spec)) + 1e-20
    return {
        "low": round(float(np.sum(spec[f < 250])) / tot, 4),
        "mid": round(float(np.sum(spec[(f >= 250) & (f < 2500)])) / tot, 4),
        "high": round(float(np.sum(spec[f >= 2500])) / tot, 4),
    }


def measure(x: np.ndarray) -> dict:
    peak = float(np.max(np.abs(x))) + 1e-12
    env = np.abs(x)
    thr = peak * 0.1
    # attack: time from first 10%-of-peak sample to the peak
    i_pk = int(np.argmax(env))
    before = np.where(env[: i_pk + 1] >= thr)[0]
    i_at = int(before[0]) if len(before) else 0
    attack_ms = round((i_pk - i_at) / SR * 1000.0, 2)
    # tail: last sample above 1% of peak, measured from the peak
    tail_idx = np.where(env >= peak * 0.01)[0]
    tail_ms = round((int(tail_idx[-1]) - i_pk) / SR * 1000.0, 1) if len(tail_idx) else 0.0
    # spectral centre: amplitude-weighted mean frequency
    mag = np.abs(np.fft.rfft(x))
    f = np.fft.rfftfreq(len(x), 1.0 / SR)
    centre = float(np.sum(mag * f) / (np.sum(mag) + 1e-20))
    # harsh: is 2.5-5k more than 2 dB above 1k?
    def band_db(lo, hi):
        sel = (f >= lo) & (f < hi)
        return 20 * math.log10(np.sqrt(np.mean(mag[sel] ** 2)) + 1e-12)
    harsh = bool(band_db(2500, 5000) - band_db(900, 1100) > 2.0)
    return {
        "duration_s": round(len(x) / SR, 3),
        "peak_dbfs": round(20 * math.log10(peak), 2),
        "attack_ms": attack_ms,
        "tail_ms": tail_ms,
        "spectral_centre_hz": round(centre),
        "band_energy": band_energy(x),
        "harsh": harsh,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="sfx")
    a = ap.parse_args()
    out = Path(a.out)
    gens = load_generators()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = []

    for n, (family, material, variant, gen) in enumerate(CATALOGUE, start=1):
        x = np.asarray(gens[gen](), dtype=np.float64)
        if x.ndim > 1:
            x = x.mean(axis=1)
        name = f"{family}-{material}-{variant}-{n:03d}"
        rel = f"{family}/{name}.wav"
        path = out / rel
        write_wav(path, x)
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        row = {
            "id": f"sfx-{name}",
            "file": rel,
            "source": "synth",
            "url": "",
            "author": "Monarch.Overall.Work",
            "license": "own",
            "license_url": "",
            "sha256": sha,
            "downloaded_at": now,
            "duration_s": None, "sample_rate": SR, "channels": 1,
            "peak_dbfs": None, "attack_ms": None, "tail_ms": None,
            "spectral_centre_hz": None, "band_energy": None,
            "harsh": None,
            "tags": TAGS[gen],
            "changes": f"synthesised by scripts/orca3d-audio.py::{gen}()",
            "generator": f"scripts/orca3d-audio.py::{gen}",
        }
        row.update(measure(x))
        manifest.append(row)
        print(f"  {rel:44s} {row['duration_s']:5.2f}s  "
              f"atk {row['attack_ms']:6.2f}ms  tail {row['tail_ms']:7.1f}ms  "
              f"harsh={row['harsh']}")

    (out / "manifest.json").write_text(json.dumps(
        {"schema": "monarch-sfx-manifest/1", "generated_at": now,
         "sample_rate": SR, "entries": manifest}, indent=2) + "\n")

    bad = [m for m in manifest if m["harsh"]]
    print(f"\n{len(manifest)} entries -> {out/'manifest.json'}")
    if bad:
        print("  WARNING: harsh entries (2.5-5k > +2 dB over 1k): "
              + ", ".join(m["id"] for m in bad))
    return 0


if __name__ == "__main__":
    sys.exit(main())
