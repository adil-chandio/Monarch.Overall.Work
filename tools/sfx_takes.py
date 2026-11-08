#!/usr/bin/env python3
"""Render earshot's forge bank into audio/takes/ with its sync metadata.

earshot is not on PyPI under this name (that package is somebody else's VAD binding), so it
is run from its source tree:

    git clone https://github.com/Leonxlnx/earshot /tmp/esrc/earshot-main   # or the tarball
    PYTHONPATH=/tmp/esrc/earshot-main python3 tools/sfx_takes.py

For each sound id it writes <id with / -> _>.wav at 48 kHz plus audio/takes/meta.json, which
carries the onset / peak / end times the mixer aligns cues to. Deterministic: same seed,
same wav.
"""
import json
import sys
from pathlib import Path

import numpy as np

SRC = "/tmp/esrc/earshot-main"
OUT = Path("audio/takes")
SEED = 11

# the roles the film needs: cuts, type, landings, air, tonal beats
WANT = [
    "cut_hit/punch", "cut_hit/kick", "whoosh_fast/crisp", "whoosh_big/thump",
    "pro_pop_in/round", "knock/wood", "riser/dark", "reverse_swell/dark",
    "mallet/glock", "notify/mid_tine", "shutter/dslr", "typing_key/clicky",
    "ui_pop/soft", "sub_drop/punch", "pro_hover_tick/ping", "swish/bright",
]


def main() -> int:
    sys.path.insert(0, SRC)
    try:
        import soundfile as sf
        from earshot.forge import bank
    except ImportError as e:
        print(f"  need soundfile and earshot on PYTHONPATH ({e})")
        return 2
    print(f"  bank: {len(bank.ids())} sounds")
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {}
    for sid in WANT:
        x, info = bank.render(sid, seed=SEED)
        name = sid.replace("/", "_")
        sf.write(OUT / f"{name}.wav", np.asarray(x), 48000)
        meta[name] = {k: float(info[k]) for k in ("onset_s", "peak_s", "end_s", "dur_s",
                                                 "peak_db", "lufs_m_max")}
        print(f"  {sid:22s} {info['dur_s']:.2f}s  {info['lufs_m_max']:6.1f} LUFS")
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(f"  {len(meta)} takes -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
