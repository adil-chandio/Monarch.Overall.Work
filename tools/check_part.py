"""Check a checkpoint render on its own terms.

tools/check_render.py validates a finished film against the whole composition —
701 frames and the full scene table — which a part render is not. This checks the
part: the frame count it claims, that no frame is black, that the first frame is
painted, and that it lines up frame-for-frame with the reference cut that was made
to match it. A silent one-frame offset between the two files would make every later
comparison meaningless, so it is checked here rather than assumed.
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ffbin import ffmpeg

W, H = 480, 854
FF = ffmpeg()


def track(path: str) -> tuple[int, list[float]]:
    """Frame count and per-frame mean luma.

    Plain Python on purpose. This runs in a CI job whose only other job is to render
    and publish, and a dependency there has twice cost more than the check is worth:
    numpy from pip stalled for eight minutes with no output, and numpy from apt timed
    the step out at six. Summing a bytes slice is done in C and is fast enough.
    """
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-vf", f"scale={W}:{H}",
                          "-pix_fmt", "gray", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    size = W * H
    n = len(raw) // size
    lum = [sum(raw[i * size:(i + 1) * size]) / size for i in range(n)]
    return n, lum


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", default="public/demo/v4-30-silent.mp4")
    ap.add_argument("--reference", default="public/demo/ref30.mp4")
    ap.add_argument("--frames", type=int, default=210)
    args = ap.parse_args()

    problems = []
    print(f"{'file':34s} {'frames':>6s} {'frame0':>7s} {'black':>5s} {'mean':>6s}")
    lens = {}
    for label, path in (("checkpoint", args.video), ("reference", args.reference)):
        if not Path(path).is_file():
            problems.append(f"{path} is missing")
            continue
        n, lum = track(path)
        black = [i for i, v in enumerate(lum) if v < 6]
        lens[label] = n
        print(f"{Path(path).name:34s} {n:6d} {lum[0]:7.1f} {len(black):5d} {sum(lum) / len(lum):6.1f}")
        if black:
            problems.append(f"{label}: {len(black)} black frame(s), first at {black[0] / 30:.2f}s")
        if lum[0] < 12:
            problems.append(f"{label}: frame 0 is {lum[0]:.1f} luma — the picture is not painted")
        if label == "checkpoint" and n != args.frames:
            problems.append(f"checkpoint has {n} frames, expected {args.frames}")

    if len(lens) == 2 and lens["checkpoint"] != lens["reference"]:
        problems.append(
            f"checkpoint is {lens['checkpoint']} frames and the reference cut is "
            f"{lens['reference']} — they do not line up, so a comparison between them is void")

    print()
    if problems:
        print("CHECKPOINT CHECK: FAIL")
        for p in problems:
            print("  ✗ " + p)
        return 1
    print(f"CHECKPOINT CHECK: PASS — {args.frames} frames, no black frames, lined up with the reference")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
