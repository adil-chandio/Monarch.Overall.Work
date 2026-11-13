#!/usr/bin/env python3
"""
Stretch the cut from 295s to the VO length without slowing the cutting rhythm:
every shot longer than 8s is split into 2-3 beats with different camera moves,
so average shot length stays ~6s instead of 10s.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shots import SHOTS

TARGET = 515.0          # VO 504s + breath
ALT = [("push", 1.10), ("drift", (0.045, 0.0), 1.07), ("push", 1.16),
       ("drift", (-0.035, 0.01), 1.06), ("shake", 0.004, 1.05), ("pull", 1.09)]

def build():
    k = TARGET / sum(s["sec"] for s in SHOTS)
    out = []
    for s in SHOTS:
        dur = s["sec"] * k
        parts = 1 if dur <= 8.0 else (2 if dur <= 15.0 else 3)
        for i in range(parts):
            d = dur / parts
            cam = s["cam"] if i == 0 else ALT[(hash(s["id"]) + i) % len(ALT)]
            out.append(dict(id="%s%s" % (s["id"], "" if i == 0 else ".%d" % i),
                            ch=s["ch"], sec=round(d, 3), img=s["img"], cam=cam,
                            xfade=s["xfade"] if i == 0 else 0.0,
                            text=s.get("text", "") if i == 0 else "",
                            textpos=s.get("textpos", "low")))
    tot = sum(x["sec"] for x in out)
    # trim the tail so the total is exact
    out[-1]["sec"] = round(out[-1]["sec"] - (tot - TARGET), 3)
    return out

if __name__ == "__main__":
    rows = build()
    json.dump(rows, open("out/timeline_ext.json", "w"), indent=1)
    print("shots", len(rows), "total", round(sum(r["sec"] for r in rows), 2),
          "ASL", round(sum(r["sec"] for r in rows) / len(rows), 2))
