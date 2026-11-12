#!/usr/bin/env python3
"""Render MONARCH — night temple, reference-matched 3D cut.

Six shots, cut for cut against `monarch-mafia-temple-20s.mp4`:

    S1 street      0- 96 f   Edo alley, walking man, lanterns, wet stone, neon towers
    S2 facade     96-216 f   temple front, toro, cedar forest, mist
    S3 aerial    216-312 f   the whole complex from above, lantern-lit axis
    S4 run       312-384 f   lateral tracking pan, running man, vermilion hall
    S5 face-3/4  384-432 f   chest-up three-quarter portrait, warm interior
    S6 face      432-480 f   chest-up front portrait, red irises, cool temple behind

Cut points are frame-exact, measured from the reference by histogram distance:
96, 216, 312, 384, 432.

Cameras are locked in five of the six shots, as in the reference (phase
correlation put the reference at 0.00-0.22 px/frame except S4). S4 is a
tracking pan at the measured 4.4 px/frame, rebuilt as a real sub-frame camera
move so the motion blur is in the geometry as well as the man.

Grading is calibrated, not guessed: each shot carries the luma and saturation
measured off the reference, and `--calibrate` solves exposure and saturation to
land on them.

Honest scope. Everything is ray-traced or rasterised geometry — no plates, no
billboards. The sets are procedural primitives. The figure is a procedural
14-segment skeleton. The close-up face is a real scanned head mesh (Lee
Perry-Smith, CC BY 3.0) re-lit in this world, with procedural hair; it is one
fixed mesh, so it has no expression rig and no second face. It is not a likeness
of any person in the reference video.

Usage:
  python qc/vfx3d/film3d.py --stills S1,S6
  python qc/vfx3d/film3d.py --probe
  python qc/vfx3d/film3d.py --calibrate
  python qc/vfx3d/film3d.py --frames-dir render-3d/frames --slice "2:5"
  python qc/vfx3d/film3d.py --frames-dir render-3d/frames --encode-only \
      --audio render-3d/sound.wav --out render-3d/monarch-temple-3d.mp4
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from vfx3d import engine, geom, head_mesh, world  # noqa: E402

FPS = 24
W_DEFAULT, H_DEFAULT = 1280, 720
TOTAL = 480

# Grade targets, measured off the reference per shot:
#   luma = median luma, sat = median HSV saturation, (b, a) = blue / amber share
TARGETS = {
    'S1': dict(luma=21.1, sat=134.0),
    'S2': dict(luma=17.0, sat=138.0),
    'S3': dict(luma=27.3, sat=161.0),
    'S4': dict(luma=38.1, sat=81.0),
    'S5': dict(luma=11.0, sat=181.0),
    'S6': dict(luma=18.7, sat=98.0),
}

SHOTS = [
    dict(name='S1-street', start=0, end=96, set='street',
         eye=(0.15, 1.50, 10.6), target=(0.0, 1.36, -8.0), fov=46.0,
         ambient=(0.010, 0.013, 0.021), fog=0.030, mist=0.45, wet=0.72,
         fog_tint=(0.030, 0.043, 0.072), samples=2,
         grade=dict(exposure=1.35, contrast=1.26, saturation=1.30, lift=0.0,
                    streak=0.24, vignette=0.46, bloom=0.55),
         figure=dict(root=(-0.10, 4.2), phase0=0.0, walk=1.35, run=False,
                     yaw=0.0, travel=0.0, back=True)),

    dict(name='S2-facade', start=96, end=216, set='temple',
         eye=(0.0, 2.10, 18.0), target=(0.0, 4.00, -1.0), fov=36.0,
         ambient=(0.009, 0.012, 0.019), fog=0.026, mist=0.55, wet=0.45,
         fog_tint=(0.028, 0.040, 0.068), samples=2,
         grade=dict(exposure=1.20, contrast=1.24, saturation=1.30, lift=0.002,
                    streak=0.22, vignette=0.50, bloom=0.50)),

    dict(name='S3-aerial', start=216, end=312, set='aerial',
         eye=(7.0, 19.0, 26.0), target=(0.0, 2.0, -4.0), fov=44.0,
         ambient=(0.011, 0.014, 0.022), fog=0.013, mist=0.30, wet=0.26,
         fog_tint=(0.032, 0.045, 0.074), samples=2,
         grade=dict(exposure=1.10, contrast=1.26, saturation=1.42, lift=0.004,
                    streak=0.22, vignette=0.42, bloom=0.55)),

    dict(name='S4-run', start=312, end=384, set='runhall',
         eye=(-0.90, 1.46, 7.10), target=(-0.90, 1.30, 0.0), fov=36.0,
         dolly_per_frame=(0.0144, 0.0, 0.0),   # 4.4 px/frame at 720p
         blur_taps=4, shutter=0.5, samples=1,
         ambient=(0.013, 0.016, 0.022), fog=0.022, mist=0.58, wet=0.55,
         fog_tint=(0.044, 0.046, 0.058), samples_note='motion blur only',
         grade=dict(exposure=1.05, contrast=1.16, saturation=1.10, lift=0.006,
                    streak=0.18, vignette=0.46, bloom=0.45),
         figure=dict(root=(0.30, 4.30), phase0=0.35, walk=2.75, run=True,
                     yaw=math.pi / 2, travel=-0.55, back=False)),

    dict(name='S5-face3q', start=384, end=432, set='face3q',
         eye=(0.135, 0.004, 0.400), target=(0.0, -0.012, 0.0), fov=28.0,
         samples=2, grade=dict(exposure=1.0, contrast=1.16, saturation=1.05,
                               streak=0.12, vignette=0.52, bloom=0.35)),

    dict(name='S6-face', start=432, end=480, set='face',
         eye=(0.010, 0.002, 0.430), target=(0.0, -0.014, 0.0), fov=27.0,
         samples=2, grade=dict(exposure=1.0, contrast=1.18, saturation=1.02,
                               streak=0.14, vignette=0.52, bloom=0.40)),
]

# The face lights, measured against the reference frame at 19 s: a soft key from
# camera-left, two cold rims from behind, almost nothing from the front.
FACE_LIGHTS = {
    'S6': [
        world.Light((-0.40, 0.170, 0.470), (1.0, 0.74, 0.52), 0.055, 0.03),
        world.Light((0.50, -0.020, 0.380), (0.46, 0.56, 0.90), 0.016, 0.05),
        world.Light((0.17, 0.250, -0.400), (0.62, 0.78, 1.0), 0.120, 0.04),
        world.Light((-0.30, 0.090, -0.420), (0.55, 0.72, 1.0), 0.070, 0.05),
    ],
    # S5 is lit warm from in front-left, from the shoji screens behind the camera
    'S5': [
        world.Light((-0.34, 0.130, 0.420), (1.0, 0.62, 0.30), 0.075, 0.04),
        world.Light((0.42, 0.020, 0.330), (0.86, 0.58, 0.30), 0.026, 0.06),
        world.Light((0.10, 0.230, -0.380), (0.72, 0.62, 0.44), 0.040, 0.05),
        world.Light((0.34, -0.060, -0.300), (0.30, 0.34, 0.46), 0.030, 0.06),
    ],
}


# ------------------------------------------------------------------ geometry
def shot_for_frame(f):
    for s in SHOTS:
        if s['start'] <= f < s['end']:
            return s
    return SHOTS[-1]


def camera_for(shot, frame_in_shot):
    """Camera for one frame: locked, unless the shot declares a pan rate."""
    eye = np.asarray(shot['eye'], np.float64)
    target = np.asarray(shot['target'], np.float64)
    dolly = shot.get('dolly_per_frame')
    if dolly:
        off = np.asarray(dolly, np.float64) * frame_in_shot
        return ((eye + off).astype(np.float32),
                (target + off).astype(np.float32))
    rate = shot.get('pan_deg_per_s', 0.0)
    if not rate:
        return eye.astype(np.float32), target.astype(np.float32)
    ang = math.radians(rate) * (frame_in_shot / FPS)
    c, s = math.cos(ang), math.sin(ang)
    d = target - eye
    d = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]) @ d
    return eye.astype(np.float32), (eye + d).astype(np.float32)


def figure_solids_at(shot, t):
    """The man, at time t seconds into the shot. None if the shot has no man."""
    fg = shot.get('figure')
    if not fg:
        return None
    root = (fg['root'][0] + fg['travel'] * t, fg['root'][1])
    phase = fg['phase0'] + t * fg['walk']
    pose = world.pose_at(phase, root=root, yaw=fg['yaw'], run=fg['run'])
    solids = world.figure_solids(pose)
    if not fg.get('back'):
        solids.extend(world.head_solids(pose['head_centre'],
                                        yaw=pose['head_yaw']))
    return engine._flatten(solids)


# --------------------------------------------------------------------- shots
class FaceShot:
    """The close-up: scanned head + procedural hair, over a live set.

    The set behind the head is the same ray-traced temple as S2, thrown far out
    of focus, so the background is real geometry with a real depth of field
    instead of a gradient.
    """

    def __init__(self, set_name='face', width=W_DEFAULT, height=H_DEFAULT):
        self.head = head_mesh.HeadMesh()
        self.hair_prims = engine._flatten(head_mesh.hair_solids())
        self.frame = engine.Frame(set_name, 8, 8)      # materials + background
        self.set_name = set_name
        self.width, self.height = width, height
        self._bg_cache = {}

    def background(self, shot, eye, target, w, h, scale=2):
        eye, target = shot['_bgeye'], shot['_bgtarget']
        """The set behind the head, rendered at reduced resolution.

        It is far out of focus, so rendering it at 1/scale and upsampling is
        both correct for the look and much cheaper than a full-res trace.
        """
        key = (shot['name'],)
        if key in self._bg_cache:
            return self._bg_cache[key]
        bw, bh = max(w // scale, 16), max(h // scale, 16)
        bg = engine.Frame(shot['_bgset'], bw, bh)
        grade = dict(shot['grade'])
        grade['exposure'] = grade['exposure'] * 0.16
        grade['grain'] = 0.004
        grade['contrast'] = 1.10
        grade['bloom'] = 0.30
        sh = engine.Shot(shot['name'] + '-bg', eye, target, shot['fov'],
                         ambient=shot['_bgamb'], fog=shot['_bgfog'],
                         fog_tint=shot['_bgtint'], mist=shot['_bgmist'],
                         wet=0.0, grade=grade)
        img = engine.render(bg, sh, bw, bh, samples=1, seed=3)
        from PIL import Image
        img = np.asarray(Image.fromarray(img).resize((w, h), Image.BICUBIC),
                         np.float32) / 255.0
        self._bg_cache[key] = img
        return img


def render_face_shot(face, shot, f, w, h):
    """One frame of S5 or S6."""
    t = f / FPS
    fi = f - shot['start']
    eye, target = camera_for(shot, fi)
    # the head turns through the shot, as in the reference
    if shot['name'] == 'S5-face3q':
        yaw = -0.52 + 0.02 * fi / FPS
        glow = 0.0
        tint = (1.0, 0.96, 0.92)
    else:
        yaw = 0.0
        glow = 0.55 + 0.35 * min(1.0, fi / 20.0)
        tint = (0.90, 0.90, 0.98)

    bg = face.background(shot, eye, target, w, h, scale=3)
    lights = FACE_LIGHTS[shot['name'].split('-')[0]]
    img, alpha, depth = head_mesh.render_head(
        face.head, eye, target, w, h, shot['fov'], lights,
        ambient=shot['_faceamb'], fog_tint=shot['_bgtint'], yaw=yaw,
        iris_glow=glow, skin_tint=tint, rough=0.50,
        dof_focus=float(np.linalg.norm(np.asarray(eye) - np.asarray(target))),
        dof_amount=0.9 if shot['name'] == 'S6-face' else 0.6, flare=0.10)
    img, alpha, depth = head_mesh.composite_hair_raytraced(
        img, alpha, depth, face.hair_prims, face.frame, eye, target, w, h,
        shot['fov'], lights, ambient=(0.004, 0.005, 0.008),
        fog_tint=shot['_bgtint'])

    out = bg * (1.0 - alpha[..., None]) + img
    out = np.clip(out, 0, None)
    return engine.Frame.grade(out, seed=f * 7 + 1, **shot['grade'])


# ------------------------------------------------------------------ rendering
def render_one(cache, shot, f, w, h):
    if shot['set'] in ('face', 'face3q'):
        face = cache.get('face')
        if face is None:
            face = FaceShot('face', w, h)
            cache['face'] = face
        return render_face_shot(face, shot, f, w, h)

    fr = cache.get(shot['name'])
    if fr is None:
        fr = engine.Frame(shot['set'], w, h)
        cache[shot['name']] = fr
    fi = f - shot['start']
    t = f / FPS
    eye, target = camera_for(shot, fi)

    dyn = None
    dyn_fn = None
    eye_fn = None
    target_fn = None
    if shot.get('figure'):
        dyn = figure_solids_at(shot, fi / FPS)
        dyn_fn = lambda tt, s=shot: figure_solids_at(        # noqa: E731
            s, tt - s['start'] / FPS)
    if shot.get('dolly_per_frame') or shot.get('pan_deg_per_s'):
        # the motion-blur taps are given ABSOLUTE time; camera_for wants time
        # into the shot, so subtract the shot's start or the dolly runs away
        eye_fn = lambda tt, s=shot: camera_for(                    # noqa: E731
            s, (tt - s['start'] / FPS) * FPS)[0]
        target_fn = lambda tt, s=shot: camera_for(                 # noqa: E731
            s, (tt - s['start'] / FPS) * FPS)[1]

    sh = engine.Shot(shot['name'], eye, target, shot['fov'],
                     ambient=shot['ambient'], fog=shot['fog'],
                     fog_tint=shot['fog_tint'], mist=shot['mist'],
                     grade=shot['grade'], wet=shot['wet'],
                     shutter=shot.get('shutter', 0.0),
                     mist_layer=1.0)
    return engine.render(fr, sh, w, h, time=t, dyn=dyn, dyn_fn=dyn_fn,
                         eye_fn=eye_fn, target_fn=target_fn,
                         samples=shot.get('samples', 2),
                         blur_taps=shot.get('blur_taps', 0),
                         seed=f * 7 + 1)


def measure(img):
    """The same measurements the reference targets were taken with."""
    c = img.astype(np.float32)
    g = (c * np.array([0.114, 0.587, 0.299], np.float32)).sum(-1)
    mx = c.max(-1)
    mn = c.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1.0) * 255.0
    return dict(luma=float(np.median(g)), sat=float(np.median(sat)))


def calibrate(w=320, h=180):
    """Solve exposure and saturation per shot so the measurement hits the target.

    Two passes: render a probe frame, measure, then correct exposure by the
    inverse of the luma ratio and saturation by the ratio of the residual. The
    correction is stored in `render-3d/calib.json` and applied at render time.
    """
    out = {}
    cache = {}
    for shot in SHOTS:
        key = shot['name'].split('-')[0]
        f = (shot['start'] + shot['end']) // 2
        img = render_one(cache, shot, f, w, h)
        m = measure(img)
        tgt = TARGETS[key]
        ex = shot['grade']['exposure']
        sat = shot['grade']['saturation']
        # luma is roughly gamma-linear in exposure at these levels
        ex2 = ex * (tgt['luma'] / max(m['luma'], 1e-3)) ** 0.55
        sat2 = sat * (tgt['sat'] / max(m['sat'], 1e-3)) ** 0.75
        out[key] = dict(exposure=round(float(np.clip(ex2, 0.2, 4.0)), 3),
                        saturation=round(float(np.clip(sat2, 0.3, 2.4)), 3),
                        measured=m, target=tgt)
        print(f"{shot['name']:12s} measured luma {m['luma']:5.1f} sat {m['sat']:5.1f}"
              f"  -> target {tgt['luma']:5.1f} / {tgt['sat']:5.1f}"
              f"  exposure {ex:.2f}->{ex2:.2f}  sat {sat:.2f}->{sat2:.2f}",
              flush=True)
    Path('render-3d').mkdir(exist_ok=True)
    Path('render-3d/calib.json').write_text(json.dumps(out, indent=1))
    print('wrote render-3d/calib.json')
    return out


def apply_calib(path='render-3d/calib.json'):
    p = Path(path)
    if not p.exists():
        return
    calib = json.loads(p.read_text())
    for shot in SHOTS:
        key = shot['name'].split('-')[0]
        if key in calib:
            shot['grade']['exposure'] = calib[key]['exposure']
            shot['grade']['saturation'] = calib[key]['saturation']


# ------------------------------------------------------------------ encoding
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


# -------------------------------------------------------------- face-set prep
def prep_face_sets():
    """Background parameters for the two face shots.

    S5 looks into a warm, low room: shoji screens lit from behind, so the
    background is amber and close. S6 looks out over the temple: cold, deep and
    dark, with the stone lanterns catching the rim of the face.
    """
    for shot in SHOTS:
        if shot['set'] == 'face3q':
            shot['_bgset'] = 'courtyard'
            shot['_bgamb'] = (0.0075, 0.0050, 0.0028)
            shot['_bgfog'] = 0.085
            shot['_bgtint'] = (0.050, 0.031, 0.016)
            shot['_bgmist'] = 0.25
            shot['_faceamb'] = (0.020, 0.013, 0.008)
            shot['_bgeye'] = (0.30, 1.55, 5.60)
            shot['_bgtarget'] = (0.10, 1.52, 0.0)
        elif shot['set'] == 'face':
            shot['_bgset'] = 'temple'
            shot['_bgamb'] = (0.0022, 0.0028, 0.0044)
            shot['_bgfog'] = 0.075
            shot['_bgtint'] = (0.016, 0.023, 0.040)
            shot['_bgmist'] = 0.35
            shot['_faceamb'] = (0.007, 0.008, 0.012)
            shot['_bgeye'] = (0.10, 1.68, 7.40)
            shot['_bgtarget'] = (0.0, 1.95, -3.0)


def main():
    prepare = prep_face_sets()
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='render-3d/monarch-temple-3d.mp4')
    ap.add_argument('--width', type=int, default=W_DEFAULT)
    ap.add_argument('--height', type=int, default=H_DEFAULT)
    ap.add_argument('--frames-dir', default='render-3d/frames')
    ap.add_argument('--range', default='')
    ap.add_argument('--slice', default='', help='K:N - render slice K of N')
    ap.add_argument('--encode-only', action='store_true')
    ap.add_argument('--audio', default='')
    ap.add_argument('--crf', type=int, default=17)
    ap.add_argument('--preset', default='medium')
    ap.add_argument('--stills', default='')
    ap.add_argument('--probe', action='store_true')
    ap.add_argument('--calibrate', action='store_true')
    ap.add_argument('--log', default='render-3d/render_log.json')
    args = ap.parse_args()

    apply_calib()

    if args.encode_only:
        encode(args.frames_dir, args.out, args.audio, args.width, args.height,
               args.crf, args.preset)
        print('encoded', args.out)
        return

    if args.calibrate:
        calibrate()
        return

    width, height = args.width, args.height

    if args.probe:
        cache = {}
        for shot in SHOTS:
            f = (shot['start'] + shot['end']) // 2
            t0 = time.time()
            img = render_one(cache, shot, f, width, height)
            dt = time.time() - t0
            m = measure(img)
            print(f"{shot['name']:12s} frame {f:3d}  {dt:5.1f}s  "
                  f"luma {m['luma']:5.1f}  sat {m['sat']:5.1f}", flush=True)
        return

    if args.stills:
        want = {s.strip() for s in args.stills.split(',') if s.strip()}
        outp = Path('render-3d/stills')
        outp.mkdir(parents=True, exist_ok=True)
        from PIL import Image
        cache = {}
        for shot in SHOTS:
            key = shot['name'].split('-')[0]
            if shot['name'] not in want and key not in want:
                continue
            f = (shot['start'] + shot['end']) // 2
            t0 = time.time()
            img = render_one(cache, shot, f, width, height)
            Image.fromarray(img).save(outp / f"{shot['name']}.png")
            print(f"{shot['name']:12s} frame {f:3d} {time.time()-t0:5.1f}s "
                  f"luma {measure(img)['luma']:.1f}", flush=True)
        return

    frames_dir = Path(args.frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)
    if args.range:
        a, b = (int(x) for x in args.range.split(':'))
        todo = list(range(a, min(b, TOTAL)))
    elif args.slice:
        k, n = (int(x) for x in args.slice.split(':'))
        per = TOTAL // n
        todo = list(range((k - 1) * per, k * per if k < n else TOTAL))
    else:
        todo = list(range(TOTAL))

    cache = {}
    t_start = time.time()
    done = []
    from PIL import Image
    for f in todo:
        shot = shot_for_frame(f)
        img = render_one(cache, shot, f, width, height)
        Image.fromarray(img).save(frames_dir / f'f{f:05d}.png')
        done.append(f)
        if len(done) % 4 == 0 or f == todo[-1]:
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
