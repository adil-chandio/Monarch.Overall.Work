"""Is the reference actually moving in depth, or is it one flat plate with a push?

This is the measurement that decides how the rebuild must be built, so it is done
on the reference itself rather than guessed from how the shot "feels".

Method
------
Between consecutive frames, sparse Lucas-Kanade flow is fitted with a similarity
transform (scale, rotation, translation) — separately, in a grid of image regions.
A flat plate under a camera push gives *the same* scale in every region: the whole
frame breathes together and there is no depth. Any real parallax makes the regions
disagree — the background scales less than the foreground, because it is further
from the camera — and the disagreement is the parallax coefficient.

Reported per shot:
  scale     median per-frame scale change (1.004 = 0.4 % growth per frame)
  parallax  max_region_scale / min_region_scale over the shot's sampled frames
            1.00 = perfectly flat, no depth separation at all
  residual  flow left after removing the global similarity fit, in pixels —
            independent motion (a subject that moves on its own, drifting type)
  layers    how many distinct scale bands the regions fall into
"""
import subprocess
import sys

import cv2
import numpy as np

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
W, H = 720, 1280


def frames(path, t0, t1):
    out = subprocess.run(
        [FF, "-v", "error", "-ss", f"{t0}", "-to", f"{t1}", "-i", path,
         "-pix_fmt", "gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    n = len(out) // (W * H)
    return np.frombuffer(out[: n * W * H], dtype=np.uint8).reshape(n, H, W)


def similarity(prev, cur, mask=None):
    """Least-squares similarity (uniform scale + rotation + translation)."""
    p0 = cv2.goodFeaturesToTrack(prev, maxCorners=1400, qualityLevel=0.01,
                                 minDistance=7, blockSize=9, mask=mask)
    if p0 is None or len(p0) < 12:
        return None
    p1, st, _ = cv2.calcOpticalFlowPyrLK(prev, cur, p0, None,
                                         winSize=(21, 21), maxLevel=3)
    if p1 is None:
        return None
    ok = st.ravel() == 1
    a, b = p0[ok].reshape(-1, 2), p1[ok].reshape(-1, 2)
    if len(a) < 12:
        return None
    m, inl = cv2.estimateAffinePartial2D(a, b, method=cv2.RANSAC,
                                         ransacReprojThreshold=1.5)
    if m is None:
        return None
    s = float(np.hypot(m[0, 0], m[1, 0]))          # uniform scale
    r = float(np.degrees(np.arctan2(m[1, 0], m[0, 0])))
    res = b - (a @ m[:, :2].T + m[:, 2])
    return dict(scale=s, rot=r, tx=float(m[0, 2]), ty=float(m[1, 2]),
                residual=float(np.abs(res).mean()), n=int(ok.sum()),
                inliers=int(inl.sum()) if inl is not None else 0)


def regions(gh=3, gw=2, pad=0.12):
    out = []
    for iy in range(gh):
        for ix in range(gw):
            y0 = int(H * (iy / gh + pad / gh))
            y1 = int(H * ((iy + 1) / gh - pad / gh))
            x0 = int(W * (ix / gw + pad / gw))
            x1 = int(W * ((ix + 1) / gw - pad / gw))
            out.append((f"r{iy}{ix}", slice(y0, y1), slice(x0, x1)))
    return out


def probe(path, t0, t1, label=""):
    f = frames(path, t0, t1)
    if len(f) < 3:
        print(f"{label}: too few frames")
        return
    regs = regions()
    reg_scales = {name: [] for name, _, _ in regs}
    gscale, gres, grot = [], [], []
    for i in range(1, len(f)):
        g = similarity(f[i - 1], f[i])
        if g:
            gscale.append(g["scale"])
            gres.append(g["residual"])
            grot.append(g["rot"])
        for name, ys, xs in regs:
            m = np.zeros((H, W), np.uint8)
            m[ys, xs] = 255
            r = similarity(f[i - 1], f[i], mask=m)
            if r:
                reg_scales[name].append(r["scale"])

    allr = [x for v in reg_scales.values() for x in v]
    print(f"\n{label}  [{t0}-{t1}s, {len(f)} frames]")
    if not gscale:
        print("  no trackable motion")
        return
    med = float(np.median(gscale))
    print(f"  global scale/frame : {med:.5f}   ({(med-1)*100:+.3f} % per frame"
          f" = {(med**30-1)*100:+.1f} % per second)")
    print(f"  rotation/frame     : {np.median(grot):+.4f} deg")
    print(f"  residual flow      : {np.median(gres):.2f} px  (independent motion)")
    per = {k: float(np.median(v)) if v else float("nan") for k, v in reg_scales.items()}
    lo, hi = min(per.values()), max(per.values())
    print(f"  region scales      : " + "  ".join(f"{k} {v:.5f}" for k, v in per.items()))
    if lo == lo and lo > 0:
        print(f"  PARALLAX ratio     : {hi/lo:.4f}   "
              f"({'flat — no depth' if hi/lo < 1.02 else 'depth separation present'})")


if __name__ == "__main__":
    REF = "analysis/attachment-filename-How-to-Edit-VIRAL-RE/reference.mp4"
    V4 = "public/demo/v4.mp4"
    probe(REF, 3.20, 5.20, "REF  shot 6 (3.13-9.13)  the 2008 red plate")
    probe(REF, 15.00, 17.00, "REF  shot 14 (14.80-23.30) the CTA")
    probe(REF, 9.20, 11.60, "REF  shot 7 (9.13-11.70) main shot")
    probe(REF, 1.35, 3.10, "REF  shot 5 (1.30-3.13) match-move")
    probe(V4, 3.20, 5.20, "V4   shot 6 (same window)")
    probe(V4, 15.00, 17.00, "V4   shot 14 (same window)")
