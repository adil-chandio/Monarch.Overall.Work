"""Render and encode the duel shot.

Same discipline as ``render_film``: frames stream to ffmpeg one at a time, because
a full cut in RAM is what killed an earlier pipeline and nothing here needs it.

    python -m showreel.stickman.duel_film [--preview] [--out PATH]
"""

from __future__ import annotations

import argparse
import os
import subprocess

import numpy as np

from .duel import Duel, FAR_LIP, GAP_DEPTH, NEAR_LIP
from .film import FPS, H, W, Performer
from .render import (air_and_grade, clip_to_gap, composite, dust_layer,
                     ground_shadow, ink, project_pose, rim_light)
from .spring import Dust
from .stage import Projector, World, paint


def ffmpeg_exe():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def two_figure_frame(duel, world, t):
    """One frame of the duel: backdrop, both shadows, both figures, grade."""
    hero, foe, cam = duel.state(t)
    proj = Projector(W, H, cam_x=cam["x"], cam_y=cam.get("rise", 0.0),
                     eye=cam["height"], zoom=cam["zoom"], tilt=cam["tilt"])
    proj._world = world

    frame = paint(world, proj)

    # Shadows first, and the far body's is weaker: it is further from the light and
    # its shadow is spread over more ground.
    if hero is not None:
        frame = ground_shadow(frame, hero, proj,
                              airborne=max(0.0, -(hero.pelvis[1] + 320.0)))
    if foe is not None:
        frame = ground_shadow(frame, foe, proj, airborne=0.0, strength=0.20)

    # Far body first. Draw order is depth order, and the silhouette is always the
    # further of the two -- it arrives from behind and never gets past the hero.
    if foe is not None:
        frame = composite(frame, ink(project_pose(foe, proj)))
    if hero is not None:
        rgba = ink(project_pose(hero, proj))
        if duel.in_void(t):
            # A body inside the hole is seen only through the hole's opening.
            rgba = clip_to_gap(rgba, world, proj)
        frame = composite(frame, rgba)

    frame = rim_light(frame, proj, world)
    return air_and_grade(frame, world, zoom=cam["zoom"], grain_seed=int(t * FPS))


def frames(duel, world, *, scale=1.0):
    n = int(round(duel.total * FPS))
    for i in range(n):
        frame = two_figure_frame(duel, world, (i + 1) / FPS)
        if scale != 1.0:
            from PIL import Image
            h = int(round(H * scale))
            w = int(round(W * scale))
            img = Image.fromarray((np.clip(frame, 0, 1) * 255).astype(np.uint8))
            frame = np.asarray(img.resize((w, h), Image.LANCZOS), np.float32) / 255.0
        yield (np.clip(frame, 0, 1) * 255.0).astype(np.uint8).tobytes()


def render(out_path, *, preview=False, crf=None, preset="medium"):
    perf = Performer()
    duel = Duel(perf)
    world = World("paper", seed=5, gaps=[(NEAR_LIP, FAR_LIP, GAP_DEPTH)])

    scale = 0.5 if preview else 1.0
    w, h = int(W * scale), int(H * scale)
    crf = crf if crf is not None else (27 if preview else 24)
    n_total = int(round(duel.total * FPS))

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
    step = max(1, n_total // 12)
    try:
        for i, buf in enumerate(frames(duel, world, scale=scale)):
            proc.stdin.write(buf)
            if i % step == 0:
                print(f"  {i:4d}/{n_total}", flush=True)
    finally:
        proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "replace")
        code = proc.wait()
    if code != 0:
        raise SystemExit(f"ffmpeg failed ({code}):\n{err}")
    return out_path, n_total


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="deliverables/monarch-duel-1080x1920.mp4")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--preset", default="veryslow")
    args = ap.parse_args(argv)
    out, n = render(args.out, preview=args.preview, preset=args.preset)
    print(f"wrote {out}  ({n} frames, {n / FPS:.2f} s)")


if __name__ == "__main__":
    main()
