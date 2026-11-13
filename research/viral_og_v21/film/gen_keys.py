#!/usr/bin/env python3
"""Generate the keyframes that are still missing (needs the image tool)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from shots import SHOTS, PROMPTS
have = {f[:-4] for f in os.listdir("out") if f.startswith("kf_") and f.endswith(".png")}
need = sorted(set(s["img"] for s in SHOTS) - have)
print("have", len(have), "missing", len(need))
for k in need:
    print(k, "::", PROMPTS[k][:90])
