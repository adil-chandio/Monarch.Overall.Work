"""Proof shot: a few seconds of acting from the single painted cel.

This is the honest ceiling test. It drives one standing drawing with the
armature and records what it can and cannot do, so the next step is a decision
about art rather than a guess.

Everything here is a function of the timestamp: breath, a weight shift, a
head turn, and an arm that lifts with an overshoot and settles.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import character as C
import motion as M
import scene2d as SC
import subprocess
from PIL import Image


def to_frame(rgb, alpha, bg=(238, 238, 238)):
    im = Image.fromarray(np.dstack([(np.clip(rgb, 0, 1) * 255).astype(np.uint8),
                                    (np.clip(alpha, 0, 1) * 255).astype(np.uint8)]),
                         'RGBA')
    back = Image.new('RGBA', im.size, bg + (255,))
    back.alpha_composite(im)
    return back.convert('RGB')


def sheet(frames, path, cols=6):
    w, h = frames[0].size
    rows = (len(frames) + cols - 1) // cols
    out = Image.new('RGB', (cols * w, rows * h), (238, 238, 238))
    for i, f in enumerate(frames):
        out.paste(f, ((i % cols) * w, (i // cols) * h))
    out.save(path)
    return path


def write_mp4(frames, path, fps=24):
    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    w, h = frames[0].size
    w -= w % 2
    h -= h % 2
    p = subprocess.Popen([exe, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                          '-s', f'{w}x{h}', '-r', str(fps), '-i', '-',
                          '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                          '-crf', '16', '-movflags', '+faststart', path],
                         stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    for f in frames:
        a = np.asarray(f.convert('RGB'), np.uint8)
        if a.shape[1] != w or a.shape[0] != h:
            a = np.asarray(Image.fromarray(a).resize((w, h), Image.LANCZOS), np.uint8)
        p.stdin.write(a.tobytes())
    p.stdin.close()
    p.wait()
    return path


def acting(t):
    """6 s: breathe, shift weight, turn the head, lift the near arm."""
    b = M.breathe(t, rate=0.20)
    body = {
        'spine': -1.1 * (b - 0.5),
        'chest': -1.6 * (b - 0.5),
        'neck': 1.2 * (b - 0.5),
    }
    # weight shifts onto the other foot over the shot
    s = math.sin(t * 0.22 * math.tau)
    body['pelvis'] = 1.8 * s
    body['hip_l'] = -1.6 * s
    body['hip_r'] = -1.6 * s
    body['spine'] += -1.0 * s

    # head turns to look off-camera, a beat after the body
    turn = M.ease_in_out((t - 1.6) / 1.1) - M.ease_in_out((t - 4.4) / 1.0)
    body['neck'] = 4.0 * turn
    body['head'] = 3.0 * turn

    # the near arm lifts in the middle of the shot, overshoots, and settles
    lift = 0.0
    if t > 1.9:
        lift = M.ease_out_back(min(1.0, (t - 1.9) / 0.95)) * 13.0
    if t > 3.9:
        lift = 13.0 * (1.0 - M.ease_in_out(min(1.0, (t - 3.9) / 1.1)))
    wobble = M.settle(t, 2.85, 1.1, 1.4)
    body['shoulder_l'] = -lift * 0.42 + wobble * 0.3
    body['elbow_l'] = -lift * 0.62
    body['wrist_l'] = -lift * 0.10 + wobble
    body['hand_l'] = wobble * 1.6
    # the far arm counter-swings a little
    body['shoulder_r'] = lift * 0.10
    body['elbow_r'] = -2.0 + lift * 0.05

    root = (1.9 * s, -1.4 * (b - 0.5))
    return body, root


if __name__ == '__main__':
    lib = SC.load_library()
    cel = lib['sidle0']
    ch = C.Character(cel.rgb, cel.alpha)
    fps, secs = 24, 6.0
    n = int(fps * secs)
    frames = []
    for i in range(n):
        t = i / fps
        pose, root = acting(t)
        rgb, a = ch.render(ch.posed(pose, root))
        frames.append(to_frame(rgb, a).resize((ch.w // 2, ch.h // 2)))
    os.makedirs('/tmp/shots', exist_ok=True)
    write_mp4(frames, '/tmp/shots/acting.mp4', fps=fps)
    sheet(frames[::12], '/tmp/shots/acting_sheet.png', cols=6)
    print('rendered', len(frames), 'frames')
