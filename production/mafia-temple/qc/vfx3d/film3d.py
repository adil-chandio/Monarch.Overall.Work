#!/usr/bin/env python3
"""Render MONARCH — night temple, reference-matched 3D cut.

Six shots, cut for cut against `monarch-mafia-temple-20s.mp4`:

    S1 street     0-96    f   Edo alley, lanterns, wet stone, neon towers
    S2 temple    96-216   f   facade, stone toro, cedar forest, mist
    S3 aerial    216-312  f   the whole complex from above
    S4 run-wide  312-384  f   lateral pan, running man, vermilion hall
    S5 run-close 384-432  f   tighter run, rim light, heavy mist
    S6 face      432-480  f   chest-up portrait, red irises

The cameras are LOCKED except S4, whose pan is measured from the reference at
-4.75 px/frame at 720p (0.22 deg/frame), i.e. 0.56 deg/s.

Honest scope: 1 unit = 1 m, 24 fps, 1280x720, 480 frames = 20.000 s. Everything
is ray-traced geometry — no plates, no billboards, no photo warping. The figure
is a procedural 15-segment skeleton; the face is a sculpt built from volumes. It
is a stylised render: it is not a likeness of any person and it has no facial rig.

Usage:
  python qc/vfx3d/film3d.py --out render-3d/monarch-temple-3d.mp4 --stills S6
  python qc/vfx3d/film3d.py --frames-dir render-3d/frames --slice "2:5"
  python qc/vfx3d/film3d.py --frames-dir render-3d/frames --encode-only \
      --audio render-3d/sound.wav --out render-3d/monarch-temple-3d.mp4
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from vfx3d import engine, world  # noqa: E402

FPS = 24
W_DEFAULT, H_DEFAULT = 1280, 720

# ---------------------------------------------------------------- the 6 shots
# Grade numbers are per shot, aimed at the per-shot palette measured off the
# reference (luma median 10-38, saturation median 81-181, blue or amber cast).
SHOTS = [
    dict(name='S1-street', start=0, end=96, set='street',
         eye=(0.35, 1.62, 9.4), target=(-0.10, 1.50, -6.0), fov=44.0,
         ambient=(0.020, 0.026, 0.040), fog=0.030, mist=0.40, wet=0.72,
         grade=dict(exposure=0.92, contrast=1.20, saturation=1.16, lift=0.0,
                    streak=0.26, vignette=0.46),
         figure=dict(root=(-0.55, 2.6), walk=-0.9, run=False, yaw=0.0,
                     frames=96, travel=-0.021, height=0.0)),
    dict(name='S2-temple', start=96, end=216, set='temple',
         eye=(0.0, 1.28, 12.6), target=(0.0, 3.05, -1.0), fov=43.0,
         ambient=(0.017, 0.022, 0.034), fog=0.028, mist=0.55, wet=0.40,
         grade=dict(exposure=0.88, contrast=1.22, saturation=1.14, lift=0.004,
                    streak=0.24, vignette=0.50)),
    dict(name='S3-aerial', start=216, end=312, set='aerial',
         eye=(13.0, 24.0, 33.0), target=(-1.0, 0.0, -3.0), fov=44.0,
         ambient=(0.021, 0.027, 0.042), fog=0.009, mist=0.34, wet=0.0,
         grade=dict(exposure=1.02, contrast=1.20, saturation=1.20, lift=0.006,
                    streak=0.26, vignette=0.40)),
    dict(name='S4-run-wide', start=312, end=384, set='courtyard',
         eye=(0.0, 1.46, 10.4), target=(0.0, 1.16, -1.0), fov=36.0,
         pan_deg_per_s=4.9, ambient=(0.024, 0.030, 0.042), fog=0.038,
         mist=0.58, wet=0.52,
         grade=dict(exposure=1.05, contrast=1.14, saturation=1.02, lift=0.008,
                    streak=0.20, vignette=0.44),
         figure=dict(root=(-3.4, 1.0), walk=1.9, run=True, yaw=0.0,
                     frames=72, travel=0.105, height=0.0)),
    dict(name='S5-run-close', start=384, end=432, set='courtyard',
         eye=(1.35, 1.32, 4.35), target=(-0.7, 1.16, -0.7), fov=35.0,
         pan_deg_per_s=0.15, ambient=(0.013, 0.017, 0.028), fog=0.046,
         mist=0.70, wet=0.60,
         grade=dict(exposure=0.92, contrast=1.24, saturation=1.28, lift=0.0,
                    streak=0.30, vignette=0.54),
         figure=dict(root=(-0.9, 1.4), walk=2.1, run=True, yaw=0.0,
                     frames=48, travel=0.090, height=0.0)),
    dict(name='S6-face', start=432, end=480, set='face',
         eye=(0.07, 1.622, 1.06), target=(0.0, 1.596, 0.0), fov=24.0,
         ambient=(0.012, 0.013, 0.019), fog=0.012, mist=0.0, wet=0.0,
         dof=2, focus=1.08, ao=0.75,
         grade=dict(exposure=1.0, contrast=1.22, saturation=1.10, lift=0.0,
                    streak=0.18, vignette=0.52,
                    shadow_tint=(0.004, 0.004, 0.020),
                    highlight_tint=(0.020, 0.010, -0.006))),
]

TOTAL = SHOTS[-1]['end']


def figure_solids_for(shot, frame_in_shot, t):
    """The walking/running man for this frame, or None if the shot has no figure."""
    fg = shot.get('figure')
    if not fg:
        return None
    # continuity: where the figure stands at this instant
    root = (fg['root'][0] + fg['travel'] * frame_in_shot, fg['root'][1])
    phase = (frame_in_shot / FPS) * fg['walk']
    pose = world.pose_at(phase, root=root, yaw=fg.get('yaw', 0.0),
                         run=fg.get('run', False))
    solids = world.figure_solids(pose)
    # head: real face volumes on the walking figure too, not a capsule
    solids.extend(world.head_solids(pose['head_centre'],
                                    yaw=pose['head_yaw'], gaze=0.0))
    return solids


def shot_for_frame(f, shots=SHOTS):
    for s in shots:
        if s['start'] <= f < s['end']:
            return s
    return shots[-1]


def camera_for(shot, frame_in_shot):
    """Camera for one frame. Locked unless the shot declares a pan."""
    eye = np.asarray(shot['eye'], np.float64)
    target = np.asarray(shot['target'], np.float64)
    rate = shot.get('pan_deg_per_s', 0.0)
    if rate:
        ang = math.radians(rate) * (frame_in_shot / FPS)
        c, s = math.cos(ang), math.sin(ang)
        d = target - eye
        # yaw the target around the eye's vertical axis
        d = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]) @ d
        target = eye + d
    return eye, target


def render_one(fr, shot, width, height, f, t):
    eye, target = camera_for(shot, f - shot['start'])
    s = engine.Shot(shot['name'], eye=eye, target=target, fov=shot['fov'],
                    ambient=shot['ambient'], fog=shot['fog'],
                    fog_tint=shot.get('fog_tint', (0.030, 0.042, 0.068)),
                    mist=shot.get('mist', 0.45), grade=shot['grade'],
                    wet=shot.get('wet', 0.0),
                    focus=shot.get('focus'), shutter=shot.get('shutter', 0.0),
                    mist_layer=shot.get('mist_layer', 1.0))
    dyn = figure_solids_for(shot, f - shot['start'], t)
    prims = engine._flatten(dyn) if dyn else None
    img, _ = engine.render_frame(fr, s, width, height, t=t, dyn=prims,
                                 dof=shot.get('dof', 1),
                                 ao=shot.get('ao', 0.0),
                                 seed=f * 7 + 1)
    return img


# ------------------------------------------------------------------- encoding
def encode(frames_dir, out, audio='', width=W_DEFAULT, height=H_DEFAULT,
           crf=17, preset='medium'):
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, '-y', '-hide_banner', '-loglevel', 'error',
           '-framerate', str(FPS), '-start_number', '0',
           '-i', str(Path(frames_dir) / 'f%05d.png')]
    if audio:
        cmd += ['-i', str(audio)]
    cmd += ['-fps_mode', 'cfr', '-vf', 'scale=%d:%d:flags=lanczos' % (width, height),
            '-c:v', 'libx264', '-preset', preset, '-crf', str(crf),
            '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-tune', 'film',
            '-movflags', '+faststart']
    if audio:
        cmd += ['-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest']
    cmd += [str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit('encode failed: ' + r.stderr[-2000:])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--width', type=int, default=W_DEFAULT)
    ap.add_argument('--height', type=int, default=H_DEFAULT)
    ap.add_argument('--frames-dir', default='render-3d/frames')
    ap.add_argument('--range', default='')
    ap.add_argument('--slice', default='', help='K:N — render slice K of N')
    ap.add_argument('--encode-only', action='store_true')
    ap.add_argument('--audio', default='')
    ap.add_argument('--crf', type=int, default=17)
    ap.add_argument('--preset', default='medium')
    ap.add_argument('--stills', default='', help='comma list of shot names')
    ap.add_argument('--log', default='render-3d/render_log.json')
    args = ap.parse_args()

    if args.encode_only:
        encode(args.frames_dir, args.out, args.audio, args.width, args.height,
               args.crf, args.preset)
        print('encoded', args.out)
        return

    width, height = args.width, args.height
    if args.stills:
        want = {s.strip() for s in args.stills.split(',') if s.strip()}
        shots = [s for s in SHOTS if s['name'] in want or
                 s['name'].split('-')[0] in want]
        for s in shots:
            fr = engine.Frame(s['set'], width, height)
            mid = (s['start'] + s['end']) // 2
            t0 = time.time()
            img = render_one(fr, s, width, height, mid, mid / FPS)
            outp = Path('render-3d/stills')
            outp.mkdir(parents=True, exist_ok=True)
            import cv2
            cv2.imwrite(str(outp / f'{s["name"]}.png'),
                        img[..., ::-1])       # BGR for cv2
            print(f'{s["name"]:12s} frame {mid:3d} {time.time()-t0:5.1f}s')
        return

    frames_dir = Path(args.frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)
    if args.range:
        a, b = (int(x) for x in args.range.split(':'))
        todo = list(range(a, min(b, TOTAL)))
    elif args.slice:
        k, n = (int(x) for x in args.slice.split(':'))
        # snap to shot boundaries so no shot is split across processes
        per = TOTAL // n
        todo = list(range((k - 1) * per, k * per if k < n else TOTAL))
    else:
        todo = list(range(TOTAL))

    cache = {}
    t_start = time.time()
    done = []
    for f in todo:
        s = shot_for_frame(f)
        if s['name'] not in cache:
            cache = {s['name']: engine.Frame(s['set'], width, height)}
        img = render_one(cache[s['name']], s, width, height, f, f / FPS)
        # imageio-free PNG write keeps memory flat: one frame at a time
        from PIL import Image
        Image.fromarray(img[..., ::-1]).save(frames_dir / f'f{f:05d}.png')
        done.append(f)
        if len(done) % 8 == 0 or f == todo[-1]:
            el = time.time() - t_start
            per_f = el / max(len(done), 1)
            print(f'{f:4d}/{TOTAL}  {el:6.1f}s  {per_f:5.2f}s/f  '
                  f'eta {(len(todo)-len(done))*per_f/60:5.1f} min', flush=True)

    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    Path(args.log).write_text(json.dumps(dict(
        frames=done, width=width, height=height, fps=FPS,
        seconds=time.time() - t_start,
        shots=[dict(name=s['name'], start=s['start'], end=s['end'])
               for s in SHOTS]), indent=1))

    if not args.slice and not args.range:
        encode(frames_dir, args.out, args.audio, width, height, args.crf,
               args.preset)
        print('wrote', args.out)


if __name__ == '__main__':
    main()
