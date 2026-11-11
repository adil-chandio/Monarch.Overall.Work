"""Render and encode "POV: the stadium goes quiet".

    python -m showreel.stickman.pov_film [--out PATH] [--preview] [--preset S]
    python -m showreel.stickman.pov_film --stills 6      # contact sheet only

Frames stream into ffmpeg one at a time. A ninety-second cut held in RAM is 12 GB
of float32 and there is no reason to hold it.
"""

from __future__ import annotations

import argparse
import math
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .film import FPS, H, W
from .pov import Pov
from .render import (air_and_grade, composite, ground_shadow, ink, project_pose,
                     rim_light)
from .stage import Projector
from .stadium import paint as stadium_paint
from .stadium import z_of
from .stadium import tunnel as tunnel_matte


def ffmpeg_exe():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


# ------------------------------------------------------------------ elements

def ball_layer(frame, at, radius, proj, z=1.0):
    """The ball: a paper disc with an ink rim and one shadow arc.

    Drawn in projected space, so it shrinks with depth exactly like the goal it is
    heading for. A fixed-size ball would arrive at the net the same size it left
    the spot.
    """
    p = proj.point(at, z)
    r = float(radius) * proj.zoom / z
    if r < 0.8:
        return frame
    ss = 2
    img = Image.new("L", (int(W) * ss, int(H) * ss), 0)
    rim = Image.new("L", (int(W) * ss, int(H) * ss), 0)
    d = ImageDraw.Draw(img)
    dr = ImageDraw.Draw(rim)
    cx, cy = p[0] * ss, p[1] * ss
    rr = r * ss
    if not (-rr * 2 < cx < W * ss + rr * 2 and -rr * 2 < cy < H * ss + rr * 2):
        return frame
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=255)
    dr.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=255,
               width=max(1, int(rr * 0.16)))

    a = np.asarray(img.resize((W, H), Image.LANCZOS), np.float32) / 255.0
    b = np.asarray(rim.resize((W, H), Image.LANCZOS), np.float32) / 255.0
    paper = np.array([0.976, 0.965, 0.937], np.float32)
    inkc = np.array([0.055, 0.051, 0.067], np.float32)
    out = frame * (1.0 - a[..., None]) + paper * a[..., None]
    out = out * (1.0 - b[..., None]) + inkc * b[..., None]
    return out


def ball_shadow(frame, at, radius, proj, z=1.0):
    """A soft ellipse on the grass directly under the ball."""
    p = proj.point((at[0], 0.0), z)
    gy = float(proj.sy(0.0, z))
    if p[1] > gy + 40:
        return frame
    height = max(0.0, -at[1])
    k = float(np.clip(height / 400.0, 0.0, 1.0))
    r = float(radius) * proj.zoom / z * (1.1 + 1.2 * k)
    if r < 1.0:
        return frame
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    d.ellipse([p[0] - r * 1.6, gy - r * 0.35, p[0] + r * 1.6, gy + r * 0.55],
              fill=int(150 * (1.0 - 0.7 * k)))
    img = img.filter(ImageFilter.GaussianBlur(max(1.5, r * 0.5)))
    a = np.asarray(img, np.float32) / 255.0
    tint = np.array([0.10, 0.11, 0.09], np.float32)
    return frame * (1.0 - a[..., None]) + tint * a[..., None]

# --------------------------------------------------------------------- frames

# The set is painted at this fraction of the frame and scaled up. A backdrop made
# of soft gradients, a stand of small marks and a two-pixel net does not need a
# pixel for every pixel: at half resolution it is indistinguishable, and it costs
# a quarter as much. The figure and the ball are still rasterised at full size,
# which is where sharpness actually matters.
BACKDROP_SCALE = 0.5


def _nudge(frame, dx, dy):
    """Translate a frame by whole pixels, extending its edges.

    Camera shake, not camera damage: rolling the array would have wrapped the
    bright near touchline round into the dark stand, which reads as a glitch.
    """
    if dx == 0 and dy == 0:
        return frame
    f = frame
    if dy > 0:
        f = np.concatenate([np.repeat(f[:1], dy, axis=0), f[:-dy]], axis=0)
    elif dy < 0:
        f = np.concatenate([f[-dy:], np.repeat(f[-1:], -dy, axis=0)], axis=0)
    if dx > 0:
        f = np.concatenate([np.repeat(f[:, :1], dx, axis=1), f[:, :-dx]], axis=1)
    elif dx < 0:
        f = np.concatenate([f[:, -dx:], np.repeat(f[:, -1:], -dx, axis=1)], axis=1)
    return f


def frame_at(pov, t):
    """One complete frame of the film at story time ``t``."""
    s = pov.state(t)
    if s.get("blank"):
        return np.zeros((H, W, 3), np.float32)
    c = s["cam"]
    proj = Projector(W, H, cam_x=c["x"], cam_y=c["rise"], eye=c["eye"],
                     zoom=c["zoom"], tilt=c["tilt"])
    bw, bh = int(W * BACKDROP_SCALE), int(H * BACKDROP_SCALE)
    # Rendering the set smaller is only the same picture if the camera is also
    # described in the smaller frame. `eye` is a fraction of H, so halving H halves
    # the camera's height in world units; `zoom` is pixels per world unit at depth
    # one, so halving the frame halves that too. Getting either wrong moves the
    # horizon, and the first version of this had the pitch painted 400 px from
    # where the hero's feet actually were.
    k = BACKDROP_SCALE
    proj_low = Projector(bw, bh, cam_x=c["x"], cam_y=c["rise"],
                         eye=c["eye"] / k, zoom=c["zoom"] * k, tilt=c["tilt"])

    stad = s["stadium"]
    stad.set_palette(s["palette"])

    # The net keeps moving for a second and a half after the ball arrives, driven
    # by the same clock the ball is on -- so in the replay, where that clock runs at
    # a fifth of speed, the net wobbles slowly too, because it is the same event.
    wobble = 0.0
    se = s.get("strike_e")
    if se is not None:
        wt = se - pov.FLIGHT
        if 0.0 <= wt < 1.8:
            wobble = 260.0 * math.exp(-2.1 * wt) * math.sin(23.0 * wt)

    frame = stadium_paint(stad, proj_low, churn=s["churn"], wobble=wobble)
    if (bw, bh) != (W, H):
        frame = np.asarray(
            Image.fromarray((np.clip(frame, 0, 1) * 255).astype(np.uint8))
                 .resize((W, H), Image.BILINEAR),
            np.float32) / 255.0

    hz = s["hero_z"]
    z_goal = z_of(s["goal_d"])

    # Shadows first: they are on the ground, everything else is above it.
    if s["hero"] is not None:
        frame = ground_shadow(frame, s["hero"], proj, airborne=0.0, strength=0.30)
    if s["ball"] is not None:
        b = s["ball"]
        frame = ball_shadow(frame, b["at"], b["r"], proj, z=b["z"])

    # The keeper stands on the goal line, so he is drawn at the goal's depth and
    # at the goal's lateral position -- the same two numbers the set used.
    if s["keeper"] is not None:
        frame = composite(frame, ink(project_pose(s["keeper"], proj, z=z_goal),
                                     colour=(0.055, 0.060, 0.085)))

    if s["hero"] is not None:
        ps = project_pose(s["hero"], proj, z=hz)
        frame = composite(frame, ink(ps, face=s["face"],
                                     paper=tuple(stad.pal["line"])))

    if s["ball"] is not None:
        b = s["ball"]
        frame = ball_layer(frame, b["at"], b["r"], proj, z=b["z"])

    # The tunnel goes on last because it is between the lens and everything else.
    frame = tunnel_matte(frame, proj, openness=s["tunnel"])

    frame = rim_light(frame, proj, stad, strength=0.34)
    frame = air_and_grade(frame, stad, zoom=c["zoom"], grain_seed=int(t * FPS))

    # Contact: two frames of white over an almost-black stadium, and a camera that
    # rings for a third of a second afterwards.
    flash = float(s.get("flash") or 0.0)
    if flash > 0.0:
        frame = frame + (1.0 - frame) * min(1.0, flash) * 0.92
    dx, dy = s.get("shake") or (0.0, 0.0)
    frame = _nudge(frame, int(round(dx)), int(round(dy)))
    return np.clip(frame, 0.0, 1.0)


def frames(pov, *, preview=False):
    n = int(round(pov_total() * FPS))
    for i in range(n):
        f = frame_at(pov, (i + 1) / FPS)
        if preview:
            img = Image.fromarray((f * 255).astype(np.uint8))
            img = img.resize((W // 2, H // 2), Image.LANCZOS)
            f = np.asarray(img, np.float32) / 255.0
        yield (f * 255).astype(np.uint8).tobytes()


def pov_total():
    from .pov import TOTAL
    return TOTAL


# --------------------------------------------------------------------- render

def render(out_path, *, preview=False, crf=None, preset="medium", limit=None):
    pov = Pov()
    scale = 0.5 if preview else 1.0
    w, h = int(W * scale), int(H * scale)
    crf = crf if crf is not None else (27 if preview else 24)
    n_total = int(round(pov_total() * FPS))
    if limit:
        n_total = min(n_total, limit)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    cmd = [
        ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-", "-an",
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
        "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        out_path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE)
    step = max(1, n_total // 20)
    try:
        for i, buf in enumerate(frames(pov, preview=preview)):
            if i >= n_total:
                break
            proc.stdin.write(buf)
            if i % step == 0:
                print(f"  {i:5d}/{n_total}  {i / FPS:5.1f}s", flush=True)
    finally:
        proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "replace")
        code = proc.wait()
    if code != 0:
        raise SystemExit(f"ffmpeg failed ({code}):\n{err}")
    return out_path, n_total


# --------------------------------------------------------------------- stills

def stills(out="pov_sheet.png", times=None, cols=4, scale=0.30):
    pov = Pov()
    if times is None:
        times = [3.0, 9.0, 16.0, 22.0, 30.0, 38.0, 48.0, 56.0, 64.0, 69.0, 78.0, 86.0]
    tw, th = int(W * scale), int(H * scale)
    rows = (len(times) + cols - 1) // cols
    sheet = Image.new("RGB", (tw * cols, th * rows), (0, 0, 0))
    for i, t in enumerate(times):
        f = frame_at(pov, t)
        img = Image.fromarray((f * 255).astype(np.uint8)).resize((tw, th), Image.LANCZOS)
        d = ImageDraw.Draw(img)
        d.text((6, 6), f"{t:.1f}s", fill=(255, 255, 255))
        sheet.paste(img, ((i % cols) * tw, (i // cols) * th))
        print(f"  still {t:.1f}s", flush=True)
    sheet.save(out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="deliverables/monarch-pov-stadium-1080x1920.mp4")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--preset", default="veryslow")
    ap.add_argument("--crf", type=int, default=None)
    ap.add_argument("--limit", type=int, default=None, help="stop after N frames")
    ap.add_argument("--stills", type=int, default=0, metavar="N",
                    help="render N stills as a contact sheet instead of a film")
    ap.add_argument("--sheet-out", default="pov_sheet.png")
    args = ap.parse_args(argv)

    if args.stills:
        print("wrote", stills(args.sheet_out))
        return

    out, n = render(args.out, preview=args.preview, crf=args.crf,
                    preset=args.preset, limit=args.limit)
    print(f"wrote {out}  ({n} frames, {n / FPS:.2f} s)")


if __name__ == "__main__":
    main()
