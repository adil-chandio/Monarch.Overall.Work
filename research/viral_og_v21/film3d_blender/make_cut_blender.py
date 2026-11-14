#!/usr/bin/env python3
"""Cut the new Blender bear shot into the 60 s episode master.

v3 of the 60 s cut has seven shots (S1..S7). Three of them are the animal itself:
S3 (the bear appears in the cave mouth), S4 (it comes up and fills the doorway)
and S6 (the walk). Those three were raymarched "blobs"; the Blender shot in
shots/out/ is the same animal built as real geometry. This script swaps them,
keeps the original audio bed and VO, and writes a new master — it never touches
the v3 files.

    python3 make_cut_blender.py                 # build out/final_v4/... from what exists
    python3 make_cut_blender.py --dry-run       # print the plan only

What it does per segment:
  * survives: stream-copy the v3 segment (no re-encode, no quality loss)
  * replaced: re-time the Blender render to the segment's exact duration and
    resolution, then concat
Audio comes from the v3 master's own mix (out/mix60.wav) so the VO, score and
footstep cues stay frame-locked to the picture.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILM3D = os.path.abspath(os.path.join(HERE, "..", "film3d"))
V3 = os.path.join(FILM3D, "out", "v3")
AUDIO = os.path.join(FILM3D, "out", "mix60.wav")
OUT = os.path.join(HERE, "out", "final_v4")
FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"

# shot name -> the Blender render that replaces it (None = keep the v3 file)
WALK = os.path.join(HERE, "shots", "out", "bear_walk_10s.mp4")
FACE = os.path.join(HERE, "shots", "out", "bear_face_9s.mp4")
# shot -> (file, in-point in the source, zoom). S3 and S4 are both the animal but not
# the same take: S3 is the wide walk (it appears), S4 is the face beat (it comes up and
# fills the doorway), S6 is the walk again from a later in-point. Using one render
# three times would read as a repeated shot.
REPLACE = {
    "S3": (WALK, 0.0, 1.00),
    "S4": (FACE, 0.0, 1.00),
    "S6": (WALK, 1.8, 1.00),
}
MASTER = "EP01_BEAR_1min_3D_v4_640x360_MASTER.mp4"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# The Blender render is a clean plate: no type on it, exactly as the brief requires
# (only narration-synced captions, nothing else burnt in). So the two captions that
# belong on these shots are drawn here, at cut time, in the same style/position as
# the v3 renderer: centred, low, near-white, one-pixel dark outline.
CAPTIONS = {
    # shot -> (caption, burn-in start s, burn-in end s)
    "S3": ("PLACED.", 0.4, 9.4),
    "S4": ("ONE DOOR", 0.8, 8.4),
    "S6": ("", 0.0, 0.0),
}
CAPTION_Y = 0.82          # same as render_clip.draw_text's "low"
CAPTION_PT = 29           # 640x360: matches H//22 with the 16 pt floor


def probe(path):
    r = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True)
    txt = r.stderr
    dur = None
    for line in txt.splitlines():
        if "Duration:" in line:
            hh, mm, ss = line.split("Duration:")[1].split(",")[0].strip().split(":")
            dur = int(hh) * 3600 + int(mm) * 60 + float(ss)
        if "Video:" in line and "fps" in line:
            pass
    return dur


def run(cmd, what):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAILED: {what}\n{r.stderr[-2500:]}", file=sys.stderr)
        raise SystemExit(r.returncode)
    return r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--crf", type=int, default=16)
    a = ap.parse_args()

    order = [f"S{i}" for i in range(1, 8)]
    plan = []
    for name in order:
        src = os.path.join(V3, f"seg_{name}.mp4")
        if not os.path.exists(src):
            print(f"missing {src}", file=sys.stderr)
            return 2
        dur = probe(src)
        plan.append((name, src, dur, REPLACE.get(name)))

    print(f"{'shot':5} {'dur':>6}  source")
    for name, src, dur, rep in plan:
        print(f"{name:5} {dur:6.2f}  {os.path.basename(src)}" + (f"   <- {rep}" if rep else ""))
    total = sum(p[2] for p in plan)
    print(f"total {total:.2f}s")

    if a.dry_run:
        return 0

    os.makedirs(OUT, exist_ok=True)
    pieces = []
    for name, src, dur, rep in plan:
        dst = os.path.join(OUT, f"seg_{name}.mp4")
        if rep is None:
            subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error",
                            "-i", src, "-c", "copy", dst], check=True)
        else:
            blend, ss, zoom = rep
            if not os.path.exists(blend):
                print(f"missing blender render {blend}", file=sys.stderr)
                return 2
            print(f"retiming {os.path.basename(blend)} in={ss:.1f}s zoom={zoom:.2f} -> {name} ({dur:.2f}s)")
            src, ss, zoom = rep
            vf = ["fps=24"]
            if zoom > 1.0:
                cw, ch = 640 / zoom, 360 / zoom
                vf.append(f"crop={cw:.0f}:{ch:.0f}:(iw-{cw:.0f})/2:(ih-{ch:.0f})/2")
            vf.append("scale=640:360:flags=lanczos")
            cap, c0, c1 = CAPTIONS.get(name, ("", 0, 0))
            if cap:
                esc = cap.replace(":", "\\:").replace("'", "").replace("%", "\\%")
                vf.append(
                    f"drawtext=fontfile={FONT}:text='{esc}':fontsize={CAPTION_PT}"
                    f":fontcolor=0xEBE9E5:borderw=1.2:bordercolor=black"
                    f":x=(w-text_w)/2:y=h*{CAPTION_Y}"
                    f":enable='between(t,{c0},{c1})'")
                print(f"  caption on {name}: {cap!r} {c0}-{c1}s")
            vf.append("format=yuv420p")
            # -t is applied in output time, so an in-point cannot shorten the result;
            # force exactly dur*24 frames instead of trusting a duration bound
            frames = int(round(dur * 24))
            run([FF, "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{ss:.3f}",
                 "-i", blend,
                 "-vf", ",".join(vf), "-frames:v", str(frames),
                 "-r", "24", "-c:v", "libx264", "-preset", "medium", "-crf", str(a.crf),
                 "-pix_fmt", "yuv420p", dst], f"retime {name}")
        got = probe(dst)
        if got is None or abs(got - dur) > 0.05:
            print(f"WARNING {name}: asked {dur:.2f}s, got {got}s "
                  f"(source tail too short for in-point)")
        pieces.append(dst)

    lst = os.path.join(OUT, "concat.txt")
    with open(lst, "w") as f:
        for p in pieces:
            f.write(f"file '{p}'\n")
    video = os.path.join(OUT, "video_only.mp4")
    run([FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", lst, "-c", "copy", video], "concat")

    master = os.path.join(OUT, MASTER)
    run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", video, "-i", AUDIO,
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", "-movflags", "+faststart", master], "mux audio")

    print(f"\nwrote {master}")
    print(f"bytes {os.path.getsize(master)}  duration {probe(master):.2f}s")
    with open(os.path.join(OUT, "assembly.json"), "w") as f:
        json.dump({"shots": [{"name": n, "v3": os.path.relpath(s, FILM3D), "dur": d,
                              "replaced_by": (os.path.relpath(r[0], HERE) if r else None),
                              "in_point": (r[1] if r else None), "zoom": (r[2] if r else None)} for n, s, d, r in plan],
                   "master": os.path.basename(master)}, f, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
