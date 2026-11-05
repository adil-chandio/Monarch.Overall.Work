#!/usr/bin/env python3
"""Measure our film against the reference: where the ink sits, and how well the frames align.

The rule for this build is "measure the reference, never copy it". This tool is the
measuring half: it reads the reference and our render at the same timestamp, finds the
type by its measured ink colour in both, and reports the difference in ink box, then fits
an affine between the two frames and reports its scale, rotation and residual.

    python3 tools/match_ref.py --ours /tmp/v6a --spec spec/v5-02.json
    python3 tools/match_ref.py --ours public/demo/v6-01.mp4
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ffbin import ffmpeg                                     # noqa: E402

REF = "analysis/attachment-filename-How-to-Edit-VIRAL-RE/reference.mp4"

# ink colours measured off the reference, in BGR (that is what cv2 reads)
INK = {
    "green": np.array([11, 187, 125], np.float32),           # #7dbb0b
    "red": np.array([27, 9, 157], np.float32),               # #9d090a
    "white": np.array([216, 214, 206], np.float32),
}

# which ink to look for in which shot -- the *same* rule for the reference and for ours,
# which is the only way the two boxes mean the same thing
# rule, and the band of the frame the word lives in (fraction of height): a word is only
# comparable when both frames are read inside the same band
LOOK = {
    "s1": ("green_bright", 0.30, 0.80, 0), "s2": ("green_bright", 0.25, 0.75, 0),
    "s3": ("green_dark", 0.02, 0.42, 0), "s4": ("red_ink", 0.02, 0.45, 0),
    "s7": ("green_bright", 0.30, 0.80, 0), "s8": ("green_bright", 0.25, 0.80, 0),
    "s10": ("green_dark", 0.02, 0.45, 0), "s11": ("red_ink", 0.02, 0.45, 0),
    "s12": ("white_ink", 0.02, 0.28, 0), "s13": ("white_ink", 0.02, 0.26, 0),
}


def frame_from_video(path: str, t: float) -> np.ndarray:
    p = subprocess.run([ffmpeg(), "-v", "error", "-ss", f"{t:.3f}", "-i", path,
                        "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                       capture_output=True)
    img = cv2.imdecode(np.frombuffer(p.stdout, np.uint8), cv2.IMREAD_COLOR)
    return img


def frame_from_stills(folder: str, t: float, fps: int = 30) -> np.ndarray:
    i = int(round(t * fps))
    return cv2.imread(f"{folder}/f{i:04d}.png", cv2.IMREAD_COLOR)


def ink_box(img: np.ndarray, key: str, tol: float = 58.0, nth: int = 0,
            y0: float = 0.0, y1: float = 1.0):
    """The ink's bounding box, by the rule the shot's ink needs.

    A green headline on a white card is the green itself; the same headline on the green
    field is the *dark* ink printed on it, so the two have to be found by different rules
    or the field measures as if it were type. `nth` picks the nth-largest blob, so a shot
    with two words can be read word by word.
    """
    f = img.astype(np.float32)
    b, g, r = f[..., 0], f[..., 1], f[..., 2]
    luma = 0.114 * b + 0.587 * g + 0.299 * r
    sat = f.max(axis=2) - f.min(axis=2)
    if key == "green_bright":
        m = (np.linalg.norm(f - INK["green"][None, None, :], axis=2) < tol).astype(np.uint8)
    elif key == "green_dark":
        m = ((luma < 78) & (g > r * 1.05) & (sat < 90)).astype(np.uint8)
    elif key == "red_ink":
        m = (np.linalg.norm(f - INK["red"][None, None, :], axis=2) < 70).astype(np.uint8)
    elif key == "white_ink":
        m = ((luma > 176) & (sat < 42)).astype(np.uint8)
    else:
        raise SystemExit(f"unknown ink rule {key}")
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    # merge the letters into a word, not into the field: wide, short kernel
    m = cv2.dilate(m, np.ones((31, 9), np.uint8))
    m[int(img.shape[0] * y1):] = 0
    m[:int(img.shape[0] * y0)] = 0
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
    if n <= 1:
        return None
    order = np.argsort(-st[1:, 4]) + 1
    order = [k for k in order if st[k, 4] >= 900]
    if nth >= len(order):
        return None
    k = order[nth]
    x, y, w, h, area = st[k]
    return dict(x=int(x), y=int(y), w=int(w), h=int(h), cx=float(cen[k][0]), cy=float(cen[k][1]),
                area=int(area), nblobs=len(order))


def align(a: np.ndarray, b: np.ndarray):
    """An affine between two frames on blurred gradients, so colour does not matter."""
    def prep(x):
        y = cv2.cvtColor(cv2.GaussianBlur(x, (9, 9), 0), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
        gx = cv2.Sobel(y, cv2.CV_32F, 1, 0, ksize=5)
        gy = cv2.Sobel(y, cv2.CV_32F, 0, 1, ksize=5)
        e = cv2.magnitude(gx, gy)
        e = cv2.GaussianBlur(e, (5, 5), 0)
        return cv2.normalize(e, None, 0, 1, cv2.NORM_MINMAX)
    ea, eb = prep(a), prep(b)
    warp = np.eye(2, 3, dtype=np.float32)
    try:
        crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 120, 1e-5)
        cc, warp = cv2.findTransformECC(ea, eb, warp.copy(), cv2.MOTION_AFFINE, crit, None, 5)
    except cv2.error as e:
        return None
    a_, b_, tx = warp[0]
    c_, d_, ty = warp[1]
    scale = float(np.sqrt(a_ * a_ + c_ * c_))
    rot = float(np.degrees(np.arctan2(c_, a_)))
    res = float(np.mean(np.abs(ea - cv2.warpAffine(eb, warp, (ea.shape[1], ea.shape[0]),
                                                   flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP))))
    return dict(cc=float(cc), scale=scale, rot=rot, tx=float(tx), ty=float(ty), residual=res)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ours", required=True, help="mp4 or a folder of stills")
    ap.add_argument("--spec", default="spec/v5-02.json")
    ap.add_argument("--shots", default=None)
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text())
    only = set(a.shots.split(",")) if a.shots else None
    stills = Path(a.ours).is_dir()
    print(f"  {'shot':5s} {'t':>6s}  {'ink':6s} | ref box            | ours box           | "
          f"dx  dy  dw  dh | align scale rot  res")
    rows = []
    for s in spec["shots"]:
        sid = s["id"]
        if only and sid not in only:
            continue
        if sid not in LOOK:
            continue
        t = (s["start"] + s["end"]) / 2
        ref = frame_from_video(REF, t)
        ours = frame_from_stills(a.ours, t) if stills else frame_from_video(a.ours, t)
        if ref is None or ours is None:
            print(f"  {sid:5s} missing frame")
            continue
        if ref.shape != ours.shape:
            ours = cv2.resize(ours, (ref.shape[1], ref.shape[0]))
        rule, y0, y1, nth = LOOK[sid]
        rb = ink_box(ref, rule, y0=y0, y1=y1, nth=nth)
        ob = ink_box(ours, rule, y0=y0, y1=y1, nth=nth)
        al = align(ref, ours)
        if rb and ob:
            dtxt = (f"{rb['x']:4d},{rb['y']:4d},{rb['w']:3d},{rb['h']:3d} | "
                    f"{ob['x']:4d},{ob['y']:4d},{ob['w']:3d},{ob['h']:3d} | "
                    f"{ob['x'] - rb['x']:+4d}{ob['y'] - rb['y']:+4d}"
                    f"{ob['w'] - rb['w']:+4d}{ob['h'] - rb['h']:+4d}")
            err = abs(ob["cx"] - rb["cx"]) / ref.shape[1] + abs(ob["w"] - rb["w"]) / rb["w"]
        elif rb:
            dtxt = f"{rb['x']:4d},{rb['y']:4d},{rb['w']:3d},{rb['h']:3d} | {'-- ink not found --':18s} |"
            err = 9.0
        else:
            dtxt = "no ink in reference or ours (skipped)"
            err = 9.0
        al_txt = (f"{al['scale']:.3f} {al['rot']:+.1f} {al['residual']:.3f}" if al else "  --")
        print(f"  {sid:5s} {t:6.2f}  {rule:12s} | {dtxt} {al_txt}")
        rows.append(dict(shot=sid, t=t, ref=rb, ours=ob, align=al, err=err))
    ok = [r for r in rows if r["ref"] and r["ours"]]
    if ok:
        print(f"\n  mean ink error over {len(ok)} shots: "
              f"{np.mean([r['err'] for r in ok]):.3f}  (lower is better, 0 is exact)")
        worst = sorted(ok, key=lambda r: -r["err"])[:3]
        for r in worst:
            print(f"    worst: {r['shot']} err {r['err']:.3f}  ref {r['ref']['w']}px wide, "
                  f"ours {r['ours']['w']}px")
    Path("analysis/v4-build/match-report.json").write_text(json.dumps(rows, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
