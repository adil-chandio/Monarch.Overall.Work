"""Cut the reference down to the same first 30 % so the checkpoint can be judged
against it, like for like, and encode it with the same settings as the rebuild.

The checkpoint is not a different film — it is the first 7.01 s of both — so this
takes the first 0.30 of the reference's duration and writes it to
public/demo/ref30.mp4 with the rebuild's own encoder settings, otherwise a
sharpness or loudness difference between the two files would be an encoder
artefact masquerading as a match/mismatch.
"""
import subprocess
import sys

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
REF = "analysis/attachment-filename-How-to-Edit-VIRAL-RE/reference.mp4"
OUT = "public/demo/ref30.mp4"
PART = float(sys.argv[1]) if len(sys.argv) > 1 else 0.30

dur = 23.35
upto = round(dur * PART, 3)
subprocess.run([FF, "-v", "error", "-y", "-i", REF, "-t", str(upto), "-an",
                "-c:v", "libx264", "-preset", "slow", "-crf", "20",
                "-maxrate", "1600k", "-bufsize", "3200k", "-pix_fmt", "yuv420p",
                OUT], check=True)
print(f"wrote {OUT} — first {PART*100:.0f} % of the reference ({upto}s)")
