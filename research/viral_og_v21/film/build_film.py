#!/usr/bin/env python3
"""
Assemble EP01. Renders every shot's camera move, concatenates, grades, and
muxes the sound bed. Missing keyframes fall back to the nearest hero plate so
the cut is always complete; regenerate the plate and re-run to upgrade it.
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shots import SHOTS

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
OUT = "out"
SEG = os.path.join(OUT, "segs")

# fallback map: if a plate is not generated yet, use the closest available beat
FALLBACK = {
    "kf_AC": "kf_Y", "kf_AA": "kf_Z", "kf_AB": "kf_X", "kf_AD": "kf_X",
    "kf_AE": "kf_O", "kf_AF": "kf_O", "kf_AG": "kf_P", "kf_AH": "kf_S",
    "kf_AI": "kf_C", "kf_AJ": "kf_A",
}

def have(k):
    return os.path.exists(os.path.join(OUT, k + ".png"))

def pick(k):
    if have(k):
        return k
    f = FALLBACK.get(k)
    while f and not have(f):
        f = FALLBACK.get(f)
    return f if f else next(s for s in
                            ("kf_A", "kf_C", "kf_B", "kf_H", "kf_M")
                            if have(s))

def main():
    os.makedirs(SEG, exist_ok=True)
    missing = sorted({s["img"] for s in SHOTS if not have(s["img"])})
    print("plates missing:", len(missing), missing[:12], "...")
    segs = []
    total = 0.0
    for s in SHOTS:
        k = pick(s["img"])
        out = os.path.join(SEG, s["id"] + ".mp4")
        segs.append(out)
        total += s["sec"]
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            continue
        subprocess.run([sys.executable, "render_key.py",
                        "--key", k, "--shot", s["id"],
                        "--cam", json.dumps(s["cam"]),
                        "--sec", str(s["sec"]), "--fps", "30",
                        "--text", s.get("text", ""),
                        "--textpos", s.get("textpos", "low"),
                        "--out", out], check=True)
        print("  ", s["id"], k, s["sec"], "s")
    lst = os.path.join(SEG, "list.txt")
    open(lst, "w").write("".join("file '%s'\n" % os.path.abspath(p) for p in segs))
    pic = os.path.join(OUT, "picture_239.mp4")
    subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", pic], check=True)
    print("picture", round(total, 1), "s")
    return total

if __name__ == "__main__":
    main()
