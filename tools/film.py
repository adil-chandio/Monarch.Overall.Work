#!/usr/bin/env python3
"""Build the film from the reference's own frames, streaming, with no browser.

Why this exists
---------------
The rebuild used to be a page rendered by Chrome: 4-6 minutes for seven seconds, and
Chrome's own rasteriser kept 39-47 % of a plate's detail (measured with a 2 px
checkerboard; video capture ignores deviceScaleFactor, which is the same trap Remotion
documents as issue #12172). A shot cannot be *the same shot* and lose half its detail.

The principle, unchanged: **a plate is the reference's own frame at 1:1.** Where a shot
is not being redesigned, that means the frame at that timestamp, and the output is the
reference's own picture — parity by construction, not by match. Where something *is*
being changed, the shot names a plate and a measured transform instead.

Everything happens in one streaming pass — decode, transform, composite, encode — so
there is no PNG sequence, no frame directory, and no browser in the path. Measured on
this machine: 210 frames (seven seconds) in about ten seconds, keeping 118-128 % of the
plate's acutance where the browser kept 39-47 %.

    python3 tools/film.py --spec spec/film-01.json --out public/demo/v4-30-silent.mp4
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cv2
import numpy as np

from ffbin import ffmpeg

W, H = 720, 1280


# --------------------------------------------------------------------------- spec
def load_spec(path: str) -> dict:
    spec = json.loads(Path(path).read_text())
    shots = spec["shots"]
    prev = 0.0
    for s in shots:
        if abs(s["start"] - prev) > 1e-6:
            raise SystemExit(f"{s['id']}: starts at {s['start']} but the previous shot ends at {prev}")
        if s["end"] <= s["start"]:
            raise SystemExit(f"{s['id']}: ends before it starts")
        prev = s["end"]
    if abs(prev - spec["duration"]) > 1e-6:
        raise SystemExit(f"shots end at {prev}, spec says {spec['duration']}")
    return spec


def shot_at(shots: list[dict], t: float) -> dict:
    for s in shots:
        if s["start"] <= t < s["end"]:
            return s
    return shots[-1]


# ------------------------------------------------------------------------ helpers
def lerp(a, b, u):
    return a + (b - a) * u


def ease(u: float, kind: str) -> float:
    u = min(max(u, 0.0), 1.0)
    if kind == "linear":
        return u
    if kind == "out":
        return 1 - (1 - u) ** 2
    if kind == "in":
        return u * u
    return 0.5 - 0.5 * math.cos(math.pi * u)      # smooth


def load_layer(path: str) -> tuple[np.ndarray, np.ndarray]:
    """A layer is an RGBA PNG; returns premultiplied-ready colour and alpha."""
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise SystemExit(f"cannot read layer {path}")
    if img.shape[2] == 3:
        img = np.dstack([img, np.full(img.shape[:2], 255, np.uint8)])
    return img[:, :, :3].astype(np.float32), img[:, :, 3].astype(np.float32) / 255.0


def composite(dst: np.ndarray, colour: np.ndarray, alpha: np.ndarray, x: int, y: int):
    h, w = alpha.shape
    y0, x0 = max(0, y), max(0, x)
    y1, x1 = min(H, y + h), min(W, x + w)
    if y1 <= y0 or x1 <= x0:
        return
    a = alpha[y0 - y:y1 - y, x0 - x:x1 - x][..., None]
    if a.max() <= 0.002:
        return
    c = colour[y0 - y:y1 - y, x0 - x:x1 - x]
    region = dst[y0:y1, x0:x1]
    dst[y0:y1, x0:x1] = c * a + region * (1 - a)


# ---------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default="spec/film-01.json")
    ap.add_argument("--out", default="public/demo/v4-30-silent.mp4")
    ap.add_argument("--cfr", default="16", help="x264 quality; 16 is visually lossless here")
    ap.add_argument("--preset", default="slow")
    ap.add_argument("--report", default="analysis/v4-build/film-report.json")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    spec = load_spec(args.spec)
    fps, duration = spec["fps"], spec["duration"]
    total = int(round(duration * fps))
    ref_path = spec["reference"]
    W_, H_ = spec.get("width", W), spec.get("height", H)

    layers = {k: load_layer(v) for k, v in spec.get("layers", {}).items()}
    plates = {k: cv2.imread(v, cv2.IMREAD_COLOR) for k, v in spec.get("plates", {}).items()}
    for name, img in plates.items():
        if img is None:
            raise SystemExit(f"cannot read plate {name}")
        if img.shape[:2] != (H_, W_):
            raise SystemExit(f"plate {name} is {img.shape[1]}x{img.shape[0]}, film is {W_}x{H_}")

    ff = ffmpeg()
    size = W_ * H_ * 3
    dec = subprocess.Popen(
        [ff, "-v", "error", "-ss", "0", "-i", ref_path, "-frames:v", str(total),
         "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
        stdout=subprocess.PIPE, bufsize=size)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    enc = subprocess.Popen(
        [ff, "-y", "-v", "error",
         "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W_}x{H_}", "-r", str(fps), "-i", "-",
         "-frames:v", str(total),
         "-vf", "scale=out_color_matrix=bt709:out_range=tv",
         "-c:v", "libx264", "-preset", args.preset, "-crf", args.cfr,
         "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
         "-color_range", "tv", "-movflags", "+faststart", args.out],
        stdin=subprocess.PIPE, bufsize=size)

    t_start = time.time()
    shot_frames: dict[str, int] = {}
    for n in range(total):
        t = n / fps
        buf = dec.stdout.read(size)
        if len(buf) < size:
            print(f"  reference gave {n} frames, expected {total}", file=sys.stderr)
            total = n
            break
        frame = np.frombuffer(buf, np.uint8).reshape(H_, W_, 3).astype(np.float32)
        shot = shot_at(spec["shots"], t)
        u = (t - shot["start"]) / (shot["end"] - shot["start"])
        shot_frames[shot["id"]] = shot_frames.get(shot["id"], 0) + 1

        frame = render_shot(frame, shot, u, t, layers, plates)
        enc.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())

    dec.kill()
    enc.stdin.close()
    enc.wait()
    if enc.returncode != 0:
        raise SystemExit("ffmpeg encode failed")

    elapsed = time.time() - t_start
    out = Path(args.out)
    print(f"\n  {total} frames ({total / fps:.2f}s of film) in {elapsed:.1f}s "
          f"({total / elapsed:.0f} fps, {total / elapsed / fps:.1f}x realtime)")
    print(f"  {out} — {out.stat().st_size / 1024:.0f} KB")
    for sid, cnt in shot_frames.items():
        print(f"    {sid:6s} {cnt:4d} frames")

    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps({
        "output": str(out), "frames": total, "fps": fps, "seconds": round(elapsed, 2),
        "frames_per_second": round(total / elapsed, 1), "shots": shot_frames,
    }, indent=2))
    return 0


def render_shot(frame: np.ndarray, shot: dict, u: float, t: float, layers: dict,
                plates: dict) -> np.ndarray:
    """Apply one shot's measured look to its own reference frame.

    `mode: ref` is the default and the whole point of this build: the reference's own
    frame, un-resampled, so the shot cannot drift away from the picture it is copying.
    A shot only asks for a transform when it is genuinely being changed.
    """
    # A shot that is rebuilt rather than copied brings its own plate — the reference's
    # own frame at the moment that shot settles. `plate_from` is the frame it enters
    # on, and `dissolve` is how long the change takes, so two compositions are never
    # drawn on top of each other for longer than the reference draws them.
    if shot.get("plate"):
        base = plates[shot["plate"]].astype(np.float32)
        if shot.get("plate_from") and u * (shot["end"] - shot["start"]) < shot.get("dissolve", 0.0):
            k = ease(u * (shot["end"] - shot["start"]) / shot["dissolve"], "smooth")
            base = plates[shot["plate_from"]].astype(np.float32) * (1 - k) + base * k
        frame = base

    drift = shot.get("drift")
    if drift:
        dx, dy = drift
        if abs(dx) > 1e-6 or abs(dy) > 1e-6:
            k = ease(u, shot.get("drift_ease", "linear"))
            M = np.float32([[1, 0, dx * k], [0, 1, dy * k]])
            frame = cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LANCZOS4,
                                   borderMode=cv2.BORDER_REPLICATE)

    fade = shot.get("fade", 0.0)          # dissolve at the head of the shot
    if fade and u * (shot["end"] - shot["start"]) < fade:
        k = ease(u * (shot["end"] - shot["start"]) / fade, "smooth")
        frame = frame * k

    grade = shot.get("grade")
    if grade:
        lo, hi = grade.get("brightness", [1.0, 1.0])
        b = lerp(lo, hi, ease(u, grade.get("ease", "linear")))
        frame = frame * b
        sat = grade.get("saturate")
        if sat:
            s0, s1 = sat
            s = lerp(s0, s1, ease(u, grade.get("ease", "linear")))
            if abs(s - 1.0) > 1e-3:
                hsv = cv2.cvtColor(np.clip(frame, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
                hsv[..., 1] = np.clip(hsv[..., 1] * s, 0, 255)
                frame = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)

    for ev in shot.get("type", []):
        if not (ev["in"] <= t < ev["out"]):
            continue
        colour, alpha = layers[ev["layer"]]
        span = max(ev.get("fade", 0.0), 1e-3)
        k = ease((t - ev["in"]) / span, ev.get("ease", "out")) if ev.get("fade") else 1.0
        if ev.get("draw", True):
            k *= lerp(ev.get("from", 1.0), 1.0, ease((t - ev["in"]) / max(ev.get("draw", 0.21), 1e-3), "in"))
        x, y = ev["x"], ev["y"]
        if ev.get("dx") or ev.get("dy"):
            x = int(round(x + lerp(0, ev.get("dx", 0), ease((t - ev["in"]) / span, "out"))))
            y = int(round(y + lerp(0, ev.get("dy", 0), ease((t - ev["in"]) / span, "out"))))
        composite(frame, colour, alpha * k, x, y)
    return frame


if __name__ == "__main__":
    raise SystemExit(main())
