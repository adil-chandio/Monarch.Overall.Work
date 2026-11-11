"""A shot: painted pose, a moving camera, motivated light, and air.

The rig proved that a single drawing can be made to breathe, but not that it
can act. So the acting here comes from painted poses — the extremes are drawn,
never deformed — and everything between them is *filmmaking*:

  * the camera moves, so the frame is never the same twice
  * the shot has a focal length, so a dolly actually changes perspective
  * light is motivated and flickers, so the drawing sits in a place
  * air — haze, grain, vignette, a shallow depth of field — puts the character
    behind a lens instead of on top of a background

A pose holds for as long as the acting needs and cuts to the next one. That is
a cut, not a morph: real drawn animation cuts between held poses all the time,
and a cut never ghosts.
"""
from __future__ import annotations

import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import poselib as PL
import skeleton as K

W, H = 1080, 1920          # portrait delivery
OVERSCAN = 1.22            # the plate is bigger than the frame, so a dolly has room


# ------------------------------------------------------------------ the plate
def plate(name, overscan=OVERSCAN):
    """A background plate at overscan size, as float RGB."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', name)
    im = Image.open(path).convert('RGB')
    tw, th = int(W * overscan), int(H * overscan)
    s = max(tw / im.size[0], th / im.size[1])
    im = im.resize((int(round(im.size[0] * s)), int(round(im.size[1] * s))), Image.LANCZOS)
    x0 = (im.size[0] - tw) // 2
    y0 = (im.size[1] - th) // 2
    im = im.crop((x0, y0, x0 + tw, y0 + th))
    return np.asarray(im, np.float32) / 255.0


def camera(bg, t, t0, t1, cam, view=(0.5, 0.5)):
    """Crop a camera window out of the plate.

    The window is smaller when the lens is longer, which is what makes a push
    in read as a push in rather than as a zoom of the picture: the plate is
    re-sampled from a smaller region each frame.
    """
    u = 0.0 if t1 <= t0 else min(1.0, max(0.0, (t - t0) / (t1 - t0)))
    e = u * u * u * (u * (u * 6 - 15) + 10)          # smootherstep: no snap at ends
    x = cam.get('x0', 0.0) + (cam.get('x1', 0.0) - cam.get('x0', 0.0)) * e
    y = cam.get('y0', 0.0) + (cam.get('y1', 0.0) - cam.get('y0', 0.0)) * e
    z = cam.get('z0', 1.0) + (cam.get('z1', 1.0) - cam.get('z0', 1.0)) * e

    hand = cam.get('hand', 0.0)
    if hand:
        x += hand * (math.sin(t * 0.71) * 0.0018 + math.sin(t * 1.63 + 0.7) * 0.0009)
        y += hand * (math.sin(t * 0.53 + 1.1) * 0.0026 + math.sin(t * 1.97) * 0.0010)
        z *= 1.0 + hand * math.sin(t * 0.41) * 0.0012

    z = max(0.4, z)
    cw, ch = int(round(W / z)), int(round(H / z))
    sw, sh = bg.shape[1], bg.shape[0]
    cx = sw / 2.0 + x * (sw - cw) / 2.0
    cy = sh / 2.0 + y * (sh - ch) / 2.0
    x0 = int(round(min(max(0, cx - cw / 2), sw - cw)))
    y0 = int(round(min(max(0, cy - ch / 2), sh - ch)))
    ch = min(ch, sh); cw = min(cw, sw)
    crop = bg[y0:y0 + ch, x0:x0 + cw]
    im = Image.fromarray((np.clip(crop, 0, 1) * 255).astype(np.uint8))
    im = im.resize((W, H), Image.BICUBIC)
    return np.asarray(im, np.float32) / 255.0


# -------------------------------------------------------------- the character
def plate_pose(poses, name, height_frac=0.66, feet=(0.5, 0.965)):
    """Place a painted pose in the frame at a given size."""
    p = poses[name]
    fh = int(H * height_frac)
    scale = fh / p.alpha.shape[0]
    nw = max(1, int(round(p.alpha.shape[1] * scale)))
    rgb = np.asarray(Image.fromarray((p.rgb * 255).astype(np.uint8)).resize((nw, fh), Image.LANCZOS),
                     np.float32) / 255.0
    a = np.asarray(Image.fromarray((p.alpha * 255).astype(np.uint8)).resize((nw, fh), Image.LANCZOS),
                   np.float32) / 255.0
    # the figure in the cel does not fill its box; find where its feet are
    ys, _ = np.nonzero(a > 0.5)
    bottom = ys.max() if ys.size else fh - 1
    top = ys.min() if ys.size else 0
    canvas = np.zeros((H, W, 3), np.float32)
    acanvas = np.zeros((H, W), np.float32)
    x0 = int(round(feet[0] * W - nw / 2))
    y1 = int(round(feet[1] * H))
    y0 = y1 - int((bottom - top)) - 1
    y0 = max(0, y0)
    x0 = max(0, min(W - nw, x0))
    hh = min(fh, H - y0)
    ww = min(nw, W - x0)
    canvas[y0:y0 + hh, x0:x0 + ww] = rgb[:hh, :ww]
    acanvas[y0:y0 + hh, x0:x0 + ww] = a[:hh, :ww]
    return canvas, acanvas


def light(rgb, t, kind='window', power=1.0, origin=(0.25, 0.0), angle=26.0):
    """Motivated light: a soft shaft, a rim, and a slow flicker.

    A character pasted on a plate has no relationship to the light in it. This
    gives the drawing one: a shaft from the direction the plate's own light
    comes from, a rim on the lit side, and a flicker slow enough to read as air
    moving, not as a strobing effect.
    """
    h, w = rgb.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)

    flick = 0.94 + 0.06 * math.sin(t * 2.1) * math.sin(t * 0.77 + 1.3)
    out = rgb * (0.97 + 0.05 * (1.0 - yy / h))[..., None]  # falloff into the floor

    if kind in ('window', 'practical'):
        ox, oy = origin[0] * w, origin[1] * h
        a = math.radians(angle)
        d = (xx - ox) * math.cos(a) + (yy - oy) * math.sin(a)
        axis = np.exp(-((d / (0.30 * w)) ** 2))
        out = out + axis[..., None] * np.array([1.00, 0.94, 0.82], np.float32) * 0.16 * power * flick
        # rim on the lit edge
        rim = np.clip(1.0 - np.abs(d) / (0.06 * w), 0, 1) ** 2
        out = out + rim[..., None] * np.array([1.0, 0.92, 0.78], np.float32) * 0.14 * power

    return np.clip(out, 0, 1)


def air(rgb, depth=0.30, haze=(0.72, 0.78, 0.86)):
    """Haze that grows with distance, so the plate has a far end."""
    h, w = rgb.shape[:2]
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    k = (depth * (1.0 - yy) ** 2)[..., None]
    return np.clip(rgb * (1 - k) + np.array(haze, np.float32) * k, 0, 1)


def depth_of_field(rgb, amount=0.6, bg_amount=1.0):
    """Blur the plate behind the character: the lens has one plane in focus."""
    im = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))
    b = im.filter(ImageFilter.GaussianBlur(radius=3.2 * amount))
    return np.asarray(b, np.float32) / 255.0


def vignette(rgb, power=0.55):
    h, w = rgb.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = w / 2, h / 2
    r = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2) / math.sqrt(2)
    v = np.clip(1.0 - power * (r ** 2.2), 0, 1)[..., None]
    return np.clip(rgb * v, 0, 1)


def grain(rgb, t, amount=0.022, seed=7):
    h, w = rgb.shape[:2]
    rng = np.random.default_rng(seed + int(t * 1000))
    n = rng.normal(0, 1, (h, w, 1)).astype(np.float32)
    n = np.repeat(n, 3, axis=2) * amount
    # grain is strongest in the midtones, as on film
    lum = rgb.mean(2, keepdims=True)
    wgt = 4 * lum * (1 - lum)
    return np.clip(rgb + n * wgt, 0, 1)


def grade(rgb, lift=(0.012, 0.016, 0.028), gain=(1.03, 1.00, 0.96), contrast=1.07):
    out = rgb * np.array(gain, np.float32) + np.array(lift, np.float32)
    out = (out - 0.5) * contrast + 0.5
    return np.clip(out, 0, 1)


# ------------------------------------------------------------------ the shots
SHOTS = [
    # (name, plate, pose, seconds, camera, light, height, feet)
    ('establish', 'bg_street.png', None, 3.4,
     dict(x0=0.05, x1=0.0, y0=0.02, y1=0.0, z0=1.00, z1=1.10, hand=1.0),
     dict(kind='window', origin=(0.28, 0.0), angle=24.0, power=0.9), 0.0, (0.5, 0.96)),
    ('arrive', 'bg_street.png', 'profile', 2.6,
     dict(x0=0.0, x1=0.02, y0=0.0, y1=0.0, z0=1.12, z1=1.04, hand=0.7),
     dict(kind='window', origin=(0.30, 0.0), angle=22.0, power=1.0), 0.74, (0.47, 0.975)),
    ('turn', 'bg_street.png', 'three_q', 2.2,
     dict(x0=0.0, x1=0.0, y0=0.0, y1=-0.01, z0=1.04, z1=1.14, hand=0.5),
     dict(kind='window', origin=(0.26, 0.0), angle=20.0, power=1.05), 0.80, (0.51, 0.978)),
    ('greet', 'bg_street.png', 'raise', 2.8,
     dict(x0=0.0, x1=0.01, y0=-0.01, y1=0.0, z0=1.14, z1=1.09, hand=0.6),
     dict(kind='window', origin=(0.24, 0.0), angle=19.0, power=1.1), 0.82, (0.53, 0.978)),
    ('walkoff', 'bg_street.png', 'walk', 2.4,
     dict(x0=0.0, x1=-0.03, y0=0.0, y1=0.01, z0=1.09, z1=1.00, hand=0.8),
     dict(kind='window', origin=(0.27, 0.0), angle=23.0, power=0.95), 0.76, (0.49, 0.980)),
]


def shot_frames(shot, poses, plates, fps=24):
    """Yield one finished frame at a time.

    Holding a whole cut in memory does not work at 1080x1920: five shots is
    several gigabytes of float32 and the process is killed before the encoder
    sees anything.
    """
    name, bgname, pose, secs, cam, lit, height, feet = shot
    bg = plates[bgname]
    n = int(round(secs * fps))
    for i in range(n):
        yield frame_at(shot, poses, bg, i / fps)


def frame_at(shot, poses, bg, t):
    name, bgname, pose, secs, cam, lit, height, feet = shot
    frame = camera(bg, t, 0.0, secs, cam)
    frame = depth_of_field(frame, 0.55)
    frame = air(frame, 0.26)
    if pose:
        frgb, fa = plate_pose(poses, pose, height, feet)
        sy, sx = int(feet[1] * H), int(feet[0] * W)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        sh = np.exp(-(((xx - sx) / (0.105 * W)) ** 2 + ((yy - sy) / (0.017 * H)) ** 2))
        core = np.exp(-(((xx - sx) / (0.050 * W)) ** 2 + ((yy - sy) / (0.008 * H)) ** 2))
        frame = frame * (1 - 0.34 * sh[..., None] - 0.30 * core[..., None])
        a = fa[..., None]
        frame = frgb * a + frame * (1 - a)
    frame = light(frame, t, lit['kind'], lit['power'], lit['origin'], lit['angle'])
    frame = vignette(frame, 0.42)
    frame = grade(frame)
    frame = grain(frame, t)
    return frame


def stream_cut(path, poses, plates, shots=SHOTS, fps=24):
    """Encode straight to disk, one frame at a time."""
    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    w, h = W // 2 * 2, H // 2 * 2
    p = subprocess.Popen([exe, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                          '-s', f'{w}x{h}', '-r', str(fps), '-i', '-',
                          '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17',
                          '-preset', 'slow', '-movflags', '+faststart', path],
                         stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    n = 0
    for shot in shots:
        for f in shot_frames(shot, poses, plates, fps):
            p.stdin.write((np.clip(f[:h, :w], 0, 1) * 255).astype(np.uint8).tobytes())
            n += 1
    p.stdin.close()
    p.wait()
    return path, n


def write_mp4(frames, path, fps=24):
    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    h, w = frames[0].shape[0] // 2 * 2, frames[0].shape[1] // 2 * 2
    p = subprocess.Popen([exe, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                          '-s', f'{w}x{h}', '-r', str(fps), '-i', '-',
                          '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17',
                          '-preset', 'slow', '-movflags', '+faststart', path],
                         stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    for f in frames:
        a = (np.clip(f[:h, :w], 0, 1) * 255).astype(np.uint8)
        p.stdin.write(a.tobytes())
    p.stdin.close()
    p.wait()
    return path


if __name__ == '__main__':
    poses = PL.load_poses()
    plates = {n: plate(n) for n in {s[1] for s in SHOTS}}
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'scene.mp4')
    path, n = stream_cut(path, poses, plates)
    print('wrote', path, n, 'frames')
