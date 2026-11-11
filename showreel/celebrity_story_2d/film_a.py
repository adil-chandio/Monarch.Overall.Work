"""Celebrity morning — painted 2D animation, 60 s portrait film.

Shot list and frame renderer. Everything below is data: which plate, where the
camera goes, which cels are on screen, when they hand off, what the light does
and what the caption says. The renderer resolves that into frames.

    python film_a.py --out /tmp/silent.mp4            # whole film
    python film_a.py --t0 34 --t1 40 --out /tmp/x.mp4 # one beat
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

import anim2d as A
import scene2d as SC
import voice2d as V

P = Path(__file__).resolve().parent
FPS = 24
END = 60.0
TOTAL_FRAMES = int(round(END * FPS))

# narration cues, from script.json (same timings the 3D v6 cut used)
CUES = V.script()
CUE = [c['start'] for c in CUES]

# which drawing supplies lip sync for which base drawing
TALK_BASE = {
    'idle0': 'idle0', 'walk0': 'walk0', 'walk1': 'walk1',
    'sidle0': 'sidle0', 'swalk0': 'swalk0', 'stalk0': 'sidle0',
    'talk0': 'idle0',
}

_OPEN, _VIS = None, None


def lipsync():
    global _OPEN, _VIS
    if _OPEN is None:
        _OPEN, _VIS = V.build_track(CUES, TOTAL_FRAMES, FPS)
    return _OPEN, _VIS


def shot(t0, t1, plate, view, tracks, cap=None, grade=None, lights=None,
         cam=None, flash=None):
    return dict(t0=t0, t1=t1, plate=plate, view=view, tracks=tracks, cap=cap,
                grade=grade or {}, lights=lights or [], cam=cam or {},
                flash=flash)


def shots(cels):
    S_ = []

    def add(*a, **k):
        S_.append(shot(*a, **k))

    # 1 dawn, lying awake.  Slow push-in on the bed.
    add(0.0, 5.4, 'bg_bedroom.png', (0.46, 0.50, 1.02),
        [dict(cel='idle0', x=0.52, y=0.975, h=0.62, flip=True,
              keys=[(0.0, 'idle0'), (5.4, 'idle0')], mouth=True)],
        cap='At five forty in the morning, the city is still asleep. '
            'His phone is already awake.',
        grade=dict(lift=(.010, .012, .026), contrast=1.06, sat=.92, bloom=.30,
                   halation=.10, gain=(1.02, 1.01, 1.00)),
        lights=[dict(origin=(560, 220), angle=-8, length=2200, width=300,
                     colour=(.86, .90, 1.0), power=.16)],
        cam=dict(x0=-.004, x1=.006, y0=.004, y1=-.006, z0=1.0, z1=1.10, hand=1.0))

    # 2 phone insert: the screen is the light source
    add(5.4, 8.6, 'bg_bedroom.png', (0.40, 0.62, 1.52),
        [dict(cel='idle0', x=0.50, y=0.985, h=0.72,
              keys=[(5.4, 'idle0'), (8.6, 'idle0')], mouth=True)],
        cap='Three missed calls. Two shoot days. One hour before the car arrives.',
        grade=dict(lift=(.006, .008, .020), contrast=1.10, sat=.90, bloom=.40,
                   halation=.14),
        lights=[dict(origin=(520, 1180), angle=2, length=1500, width=260,
                     colour=(.80, .88, 1.0), power=.22)],
        cam=dict(x0=.004, x1=-.004, y0=-.002, y1=.004, z0=1.22, z1=1.30, hand=.7))

    # 3 the calls, close on him sitting up
    add(8.6, 11.91, 'bg_bedroom.png', (0.50, 0.44, 1.30),
        [dict(cel='idle0', x=0.52, y=0.985, h=0.80,
              keys=[(8.6, 'idle0'), (11.91, 'idle0')], mouth=True)],
        cap='Three missed calls. Two shoot days. One hour before the car arrives.',
        grade=dict(lift=(.008, .010, .022), contrast=1.06, sat=.94, bloom=.26,
                   halation=.10),
        cam=dict(x0=-.006, x1=.004, y0=.0, y1=-.004, z0=1.04, z1=1.12, hand=.8))

    # 4 kitchen: coffee first
    add(11.91, 14.6, 'bg_kitchen.png', (0.52, 0.52, 1.06),
        [dict(cel='idle0', x=0.46, y=0.980, h=0.74,
              keys=[(11.91, 'idle0'), (14.6, 'idle0')], mouth=True)],
        cap='So he does what he always does. Coffee first. '
            'Everything else can wait a minute.',
        grade=dict(lift=(.014, .014, .020), contrast=1.04, sat=.96, bloom=.30,
                   halation=.12, gain=(1.02, 1.015, 1.0)),
        lights=[dict(origin=(760, 260), angle=32, length=2000, width=320,
                     colour=(1.0, .93, .80), power=.20)],
        cam=dict(x0=.004, x1=-.006, y0=-.004, y1=.002, z0=1.02, z1=1.10, hand=.9))

    # 5 the mug insert
    add(14.6, 17.24, 'bg_kitchen.png', (0.34, 0.46, 1.62),
        [], cap='So he does what he always does. Coffee first. '
                'Everything else can wait a minute.',
        grade=dict(lift=(.016, .015, .018), contrast=1.05, sat=.94, bloom=.34,
                   halation=.14),
        cam=dict(x0=-.006, x1=.006, y0=.004, y1=-.004, z0=1.10, z1=1.18, hand=.6))

    # 6 the window, first look outside — suit is on now
    add(17.24, 20.2, 'bg_street.png', (0.54, 0.40, 1.30),
        [dict(cel='sidle0', x=0.50, y=0.975, h=0.66, flip=True,
              keys=[(17.24, 'sidle0'), (20.2, 'sidle0')], mouth=True)],
        cap='By eight, the street outside his building has changed. '
            'They know the car. They know the windows.',
        grade=dict(lift=(.012, .014, .024), contrast=1.06, sat=.92, bloom=.28,
                   halation=.10,
                   gain=(1.0, 1.0, 1.0)),
        cam=dict(x0=.004, x1=-.006, y0=.002, y1=-.004, z0=1.02, z1=1.12, hand=1.0))

    # 6b the empty street: the pause before the door
    add(20.2, 22.95, 'bg_street.png', (0.50, 0.52, 1.16),
        [], cap='By eight, the street outside his building has changed. '
                'They know the car. They know the windows.',
        grade=dict(lift=(.012, .014, .024), contrast=1.06, sat=.92, bloom=.26,
                   halation=.10),
        cam=dict(x0=-.006, x1=.008, y0=.004, y1=-.006, z0=1.14, z1=1.04, hand=1.0))

    # 7 the street, walking into it
    walk = [(22.95, 'swalk0')]
    t = 22.95
    step = 3.0 / FPS
    i = 0
    while t < 29.4:
        t += step
        walk.append((round(t, 3), 'swalk0' if i % 2 == 0 else 'sidle0'))
        i += 1
    walk.append((29.81, 'stalk0'))
    add(22.95, 29.81, 'bg_street.png', (0.50, 0.56, 1.24),
        [dict(cel='swalk0', x=0.46, y=0.972, h=0.60, keys=walk, mouth=True)],
        cap='The door opens, and the noise hits him all at once. '
            'His name, from every direction.',
        grade=dict(lift=(.014, .016, .026), contrast=1.08, sat=.92, bloom=.30,
                   halation=.12),
        lights=[dict(origin=(880, 300), angle=28, length=2200, width=340,
                     colour=(1.0, .94, .84), power=.14)],
        flash=(22.95, 29.81),
        cam=dict(x0=.004, x1=-.006, y0=.004, y1=-.004, z0=1.08, z1=1.02, hand=1.1))

    # 8 the press line
    press = [(29.81, 'stalk0'), (31.0, 'sidle0'), (32.2, 'stalk0'),
             (33.4, 'sidle0'), (34.79, 'stalk0')]
    add(29.81, 34.79, 'bg_barrier.png', (0.56, 0.46, 1.22),
        [dict(cel='stalk0', x=0.54, y=0.970, h=0.62, flip=True, keys=press,
              mouth=True)],
        cap='Then the flashes start, and the smile is not fake. '
            'It is just practiced.',
        grade=dict(lift=(.018, .018, .024), contrast=1.10, sat=.94, bloom=.36,
                   halation=.16),
        lights=[dict(origin=(300, 260), angle=-34, length=2100, width=300,
                     colour=(1.0, .90, .74), power=.18)],
        flash=(29.9, 34.5),
        cam=dict(x0=-.004, x1=.006, y0=.002, y1=-.004, z0=1.04, z1=1.12, hand=1.0))

    # 9 the girl behind the barrier
    add(34.79, 40.12, 'bg_barrier.png', (0.40, 0.56, 1.30),
        [dict(cel='girl0', x=0.33, y=0.975, h=0.47,
              keys=[(34.79, 'girl0'), (40.12, 'girl0')]),
         dict(cel='sidle0', x=0.70, y=0.968, h=0.62, flip=True,
              keys=[(34.79, 'sidle0'), (37.6, 'stalk0'), (40.12, 'sidle0')],
              mouth=True)],
        cap='One girl at the barrier is not holding a phone. She is shaking. '
            'He stops walking.',
        grade=dict(lift=(.016, .015, .020), contrast=1.04, sat=.94, bloom=.28,
                   halation=.12),
        cam=dict(x0=.004, x1=-.006, y0=-.002, y1=.004, z0=1.02, z1=1.12, hand=.9))

    # 10 the reach
    add(40.12, 46.31, 'bg_barrier.png', (0.60, 0.54, 1.40),
        [dict(cel='girl0', x=0.34, y=0.978, h=0.49,
              keys=[(40.12, 'girl0'), (46.31, 'girl0')]),
         dict(cel='sidle0', x=0.72, y=0.970, h=0.64, flip=True,
              keys=[(40.12, 'sidle0'), (41.9, 'sidle0'), (43.4, 'stalk0'),
                    (46.31, 'stalk0')], mouth=True)],
        cap='He reaches over the barrier, and for a second he is not a headline. '
            'He is just someone who listened.',
        grade=dict(lift=(.018, .016, .020), contrast=1.06, sat=.94, bloom=.34,
                   halation=.16),
        lights=[dict(origin=(880, 300), angle=26, length=2000, width=300,
                     colour=(1.0, .88, .70), power=.16)],
        cam=dict(x0=.008, x1=-.004, y0=-.004, y1=.004, z0=1.02, z1=1.14, hand=.8))

    # 11 the car
    add(46.31, 50.54, 'bg_street.png', (0.54, 0.58, 1.26),
        [dict(cel='sidle0', x=0.46, y=0.968, h=0.58,
              keys=[(46.31, 'sidle0'), (50.54, 'sidle0')], mouth=True)],
        cap='Then the car door closes, and the street goes quiet again.',
        grade=dict(lift=(.014, .018, .028), contrast=1.06, sat=.86, bloom=.24,
                   halation=.10),
        cam=dict(x0=-.010, x1=-.002, y0=.0, y1=-.008, z0=1.06, z1=1.20, hand=.7))

    # 12 night, at the glass
    add(50.54, 55.6, 'bg_night.png', (0.50, 0.50, 1.04),
        [dict(cel='sidle0', x=0.42, y=0.972, h=0.60, flip=True,
              keys=[(50.54, 'sidle0'), (55.6, 'sidle0')], mouth=True)],
        cap='Hours later, the apartment is dark. He stands at the glass, '
            'the phone face down behind him. Nobody is watching.',
        grade=dict(lift=(.004, .006, .014), contrast=1.14, sat=.92, bloom=.30,
                   halation=.10),
        cam=dict(x0=-.006, x1=.004, y0=.004, y1=-.004, z0=1.0, z1=1.10, hand=.6))

    # 13 the empty room
    add(55.6, END, 'bg_night.png', (0.46, 0.46, 1.30),
        [dict(cel='sidle0', x=0.56, y=0.950, h=0.48, flip=True,
              keys=[(55.6, 'sidle0'), (END, 'sidle0')], mouth=True)],
        cap='Hours later, the apartment is dark. He stands at the glass, '
            'the phone face down behind him. Nobody is watching.',
        grade=dict(lift=(.004, .005, .012), contrast=1.16, sat=.90, bloom=.28,
                   halation=.10),
        cam=dict(x0=.004, x1=-.010, y0=-.004, y1=.006, z0=1.22, z1=1.08, hand=.5))

    return S_


# ------------------------------------------------------------------ renderer
def resolve(keys, t):
    if t <= keys[0][0]:
        return keys[0][1], keys[0][1], 0.0
    if t >= keys[-1][0]:
        return keys[-1][1], keys[-1][1], 0.0
    for i in range(len(keys) - 1):
        if keys[i][0] <= t < keys[i + 1][0]:
            span = max(1e-3, keys[i + 1][0] - keys[i][0])
            return keys[i][1], keys[i + 1][1], (t - keys[i][0]) / span
    return keys[-1][1], keys[-1][1], 0.0


def _flash_value(flash, t):
    a, b = flash
    if not (a <= t <= b):
        return 0.0
    ph = (t - a) % 0.5
    if ph < 0.055:
        return (1 - ph / 0.055) ** 2 * 0.52
    return 0.0


def _caption_alpha(cap, t0, t1, t):
    # appears a fifth of a second after the shot starts, gone before it ends
    in_a = min(1.0, max(0.0, (t - t0 - 0.20) / 0.35))
    out_a = min(1.0, max(0.0, (t1 - 0.14 - t) / 0.30))
    return min(in_a, out_a)


def render_frames(shots_, cels, t0=None, t1=None, out_path=None, scale=1.0):
    import imageio_ffmpeg
    tw, th = int(SC.W * scale), int(SC.H * scale)
    proc = None
    if out_path:
        ff = imageio_ffmpeg.get_ffmpeg_exe()
        proc = subprocess.Popen(
            [ff, '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
             '-s', f'{tw}x{th}', '-r', str(FPS), '-i', '-',
             '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
             '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out_path],
            stdin=subprocess.PIPE)

    openness, visemes = lipsync()
    plates = {}
    n = 0
    for sh in shots_:
        f0 = int(round(sh['t0'] * FPS))
        f1 = int(round(sh['t1'] * FPS))
        if sh['plate'] not in plates:
            plates[sh['plate']] = SC.plate(sh['plate'])
        bg = plates[sh['plate']]
        for fi in range(f0, f1):
            t = fi / FPS
            if t >= END:
                continue
            if t0 is not None and t < t0:
                continue
            if t1 is not None and t >= t1:
                continue

            img = SC.view_of(bg, sh['cam'], t, sh['t0'], sh['t1'], sh['view'])

            for tr in sh['tracks']:
                a_name, b_name, k = resolve(tr['keys'], t)
                ca = cels.get(a_name)
                if ca is None:
                    continue
                cb = cels.get(b_name) or ca

                mouth = None
                if tr.get('mouth'):
                    speak = (0.06 <= openness[fi] <= 1.0 and t >= CUES[0]['start'])
                    if speak:
                        mouth = (visemes[fi], min(1.0, 0.30 + 0.85 * openness[fi]))

                rgb, alpha = SC.pose_frame(ca, cb, k, t, talk=None, mouth=mouth,
                                           seed=(fi * 0.017) % 6.283)
                img = A.place_cel(img, rgb, alpha, tr['x'] * SC.W,
                                  tr['y'] * SC.H, tr['h'] * SC.H,
                                  flip=tr.get('flip', False),
                                  pivot=(ca.pivot if k < 0.5 else cb.pivot) * (alpha.shape[1] / ca.w),
                                  shadow=0.30)

            if sh.get('flash'):
                fl = _flash_value(sh['flash'], t)
                if fl > 0:
                    img = SC.flash(img, fl)

            for li in sh['lights']:
                img = SC.light_shaft(img, li['origin'], li['angle'], li['length'],
                                     li['width'], li['colour'], li['power'], t)

            img = SC.apply_grade(img, sh['grade'])
            img = SC.vignette(img, sh['grade'].get('vignette', 0.52))
            img = SC.grain(img, 0.018, seed=fi % 24)

            cap_a = _caption_alpha(sh['cap'], sh['t0'], sh['t1'], t)
            if cap_a > 0:
                img = SC.draw_caption(img, sh['cap'], cap_a)

            frame = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
            if scale != 1.0:
                frame = np.asarray(Image.fromarray(frame).resize((tw, th), Image.LANCZOS))
            if proc:
                proc.stdin.write(frame.tobytes())
            n += 1
            if n % 24 == 0:
                print(f'  {n} frames (t={t:.1f}s)', flush=True)

    if proc:
        proc.stdin.close()
        proc.wait()
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--t0', type=float, default=None)
    ap.add_argument('--t1', type=float, default=None)
    ap.add_argument('--scale', type=float, default=1.0)
    ap.add_argument('--out', default=None)
    args = ap.parse_args()

    cels = SC.load_library()
    A.calibrate(cels)
    print('cels', sorted(cels), flush=True)
    sh = shots(cels)
    n = render_frames(sh, cels, args.t0, args.t1, args.out, args.scale)
    print(f'frames {n} -> {args.out}')


if __name__ == '__main__':
    main()
