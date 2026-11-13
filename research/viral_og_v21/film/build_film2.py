#!/usr/bin/env python3
"""Render the extended cut (97 shots) and concat."""
import json, os, subprocess, sys
FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
FALLBACK = {"kf_AC":"kf_Y","kf_AA":"kf_Z","kf_AB":"kf_X","kf_AD":"kf_X",
            "kf_AE":"kf_O","kf_AF":"kf_O","kf_AG":"kf_P","kf_AH":"kf_S",
            "kf_AI":"kf_C","kf_AJ":"kf_A"}
have=lambda k: os.path.exists(os.path.join("out",k+".png"))
def pick(k):
    if have(k): return k
    f=FALLBACK.get(k)
    while f and not have(f): f=FALLBACK.get(f)
    return f if f else next(s for s in ("kf_A","kf_C","kf_B","kf_H","kf_M") if have(s))
rows=json.load(open("out/timeline_ext.json"))
SEG="out/segs2"; os.makedirs(SEG,exist_ok=True)
segs=[]
for i,r in enumerate(rows):
    out=os.path.join(SEG,"%03d_%s.mp4"%(i,r["id"]))
    segs.append(out)
    if os.path.exists(out) and os.path.getsize(out)>1000: continue
    subprocess.run([sys.executable,"render_key.py","--key",pick(r["img"]),"--shot",r["id"],
                    "--cam",json.dumps(r["cam"]),"--sec",str(r["sec"]),"--fps","30",
                    "--text",r.get("text",""),"--textpos",r.get("textpos","low"),
                    "--out",out],check=True)
lst=os.path.join(SEG,"list.txt")
open(lst,"w").write("".join("file '%s'\n"%os.path.abspath(p) for p in segs))
subprocess.run([FF,"-y","-f","concat","-safe","0","-i",lst,"-c","copy","out/picture_full.mp4"],check=True)
print("done")
