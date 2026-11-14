"""Concatenate the rendered segments, mux the mix, and print a QC report."""
import subprocess, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
OUT = os.path.join(HERE, "out")


def run(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-2000:])
        sys.exit(1)
    return r


def probe(path):
    r = subprocess.run([FF, "-i", path], capture_output=True, text=True)
    return r.stderr


def main():
    parts = [p for p in ("A.mp4", "B.mp4") if os.path.exists(os.path.join(OUT, "parts", p))]
    lst = os.path.join(OUT, "parts", "list.txt")
    with open(lst, "w") as f:
        for p in parts:
            f.write("file '%s'\n" % os.path.join(OUT, "parts", p))
    vid = os.path.join(OUT, "video_silent.mp4")
    run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid])

    final = os.path.join(OUT, "Gatun_Locks_3D_1080x1920_30fps.mp4")
    run([FF, "-y", "-i", vid, "-i", os.path.join(HERE, "audio", "mix.wav"),
         "-c:v", "copy", "-c:a", "aac", "-b:a", "224k", "-ar", "48000",
         "-shortest", "-movflags", "+faststart", final])
    print("wrote", final, "%.1f MB" % (os.path.getsize(final) / 1e6))
    info = probe(final)
    for line in info.splitlines():
        if "Duration" in line or "Stream #" in line:
            print("  " + line.strip())


if __name__ == "__main__":
    main()
