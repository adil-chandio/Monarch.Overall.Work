#!/usr/bin/env python3
"""Contact sheet of full-quality frames at given times (same code path as the renderer)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import render_clip as RC, film1min as F

W = int(os.environ.get("PW", 640)); H = W * 9 // 16
times = [float(x) for x in sys.argv[1:]] or [2, 12, 21, 31, 41, 50, 57]
cave, shots = F.film()
starts, acc = [], 0.0
for s in shots:
    starts.append(acc); acc += s.dur
cols = min(4, len(times)); rows = (len(times) + cols - 1) // cols
sheet = Image.new("RGB", (W * cols, H * rows))
for i, t in enumerate(times):
    fr, k, s = RC.build_frame(t, W, H, cave, shots, starts, seed=i)
    sheet.paste(fr, ((i % cols) * W, (i // cols) * H))
    print("t", t, "shot", k + 1, s.name, flush=True)
sheet.save("sheet_preview.png")
print("wrote sheet_preview.png")
