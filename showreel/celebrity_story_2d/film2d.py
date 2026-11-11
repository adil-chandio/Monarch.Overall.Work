"""2D film assembly: painted plates + cut-out animation + camera + film finish.

One function per act builds a Scene; the renderer walks the global shot list,
composites layers with parallax, applies the photographic finishing chain and
pipes raw frames straight into ffmpeg.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

import core2d as C
import cutout as K

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = '/home/user/assets2d'
CACHE = os.environ.get('C2D_CACHE', '/tmp/c2d_cache')
W, H = 1080, 1920
OVERS_W, OVERS_H = 1320, 2350
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FPS = 24


# ------------------------------------------------------------------ loading
def _sharp(im, amount=1.25):
    return im.filter(ImageFilter.UnsharpMask(radius=2.0, percent=int(amount * 100), threshold=2))


def background(name):
    os.makedirs(CACHE, exist_ok=True)
    key = os.path.join(CACHE, f'bg_{name}_{OVERS_W}.jpg')
    if os.path.exists(key):
        return np.asarray(Image.open(key)).astype(np.float32) / 255.0
    im = Image.open(os.path.join(ASSETS, name)).convert('RGB')
    scale = max(OVERS_W / im.width, OVERS_H / im.height)
    im = im.resize((int(im.width * scale) + 1, int(im.height * scale) + 1), Image.LANCZOS)
    im = _sharp(im, 0.9)
    l, t = (im.width - OVERS_W) // 2, (im.height - OVERS_H) // 2
    im = im.crop((l, t, l + OVERS_W, t + OVERS_H))
    im.save(key, quality=94)
    return np.asarray(im).astype(np.float32) / 255.0


def figure(name):
    """Load (and cache) a keyed cut-out as a PIL RGBA image."""
    os.makedirs(CACHE, exist_ok=True)
    key = os.path.join(CACHE, f'cut_{name}.png')
    if not os.path.exists(key):
        rgb, a = K.key_green(os.path.join(ASSETS, name))
        rgb, a = K.trim(rgb, a)
        K.to_layer(rgb, a).save(key)
    return Image.open(key).convert('RGBA')


def phone_layer(size=(420, 620)):
    """A phone seen from the side, screen up, still glowing."""
    from PIL import ImageDraw
    im = Image.new('RGBA', size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    w, h = size
    d.rounded_rectangle([20, 40, w - 20, h - 60], radius=44, fill=(16, 18, 24, 255))
    d.rounded_rectangle([34, 56, w - 34, h - 76], radius=34, fill=(8, 10, 16, 255))
    # screen glow: missed calls
    glow = Image.new('RGBA', size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.rounded_rectangle([48, 74, w - 48, h - 94], radius=28, fill=(96, 150, 235, 235))
    for i in range(3):
        y = 150 + i * 118
        gd.rounded_rectangle([86, y, w - 86, y + 86], radius=14, fill=(140, 180, 245, 200))
        gd.ellipse([102, y + 20, 140, y + 58], fill=(220, 236, 255, 235))
        gd.rounded_rectangle([156, y + 24, w - 120, y + 40], radius=8, fill=(210, 230, 255, 225))
        gd.rounded_rectangle([156, y + 50, w - 170, y + 64], radius=7, fill=(180, 208, 246, 190))
    glow = glow.filter(ImageFilter.GaussianBlur(9))
    im = Image.alpha_composite(im, glow)
    im = Image.alpha_composite(im, glow)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([20, 40, w - 20, h - 60], radius=44, outline=(120, 128, 144, 255), width=5)
    return im


def mug_layer(size=(360, 420)):
    """A dark stoneware mug with a rising steam wisp."""
    from PIL import ImageDraw
    im = Image.new('RGBA', size, (0, 0, 0, 0))
    w, h = size
    d = ImageDraw.Draw(im)
    body = [70, 130, w - 90, h - 60]
    d.rounded_rectangle(body, radius=26, fill=(52, 44, 42, 255))
    d.rounded_rectangle([70, 130, 82, h - 70], radius=8, fill=(84, 72, 66, 255))
    d.ellipse([70, 108, w - 90, 158], fill=(38, 32, 30, 255))
    d.ellipse([84, 116, w - 104, 148], fill=(96, 62, 44, 255))
    d.arc([w - 118, 168, w - 34, 300], 290, 110, fill=(52, 44, 42, 255), width=22)
    d.rounded_rectangle([70, h - 82, w - 90, h - 58], radius=14, fill=(40, 34, 32, 255))
    steam = Image.new('RGBA', size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(steam)
    for i in range(3):
        x = 140 + i * 34
        sd.arc([x - 26, 30, x + 26, 96], 200, 340, fill=(255, 255, 255, 90), width=9)
        sd.arc([x - 18, 0, x + 18, 62], 20, 160, fill=(255, 255, 255, 70), width=7)
    steam = steam.filter(ImageFilter.GaussianBlur(6))
    im = Image.alpha_composite(im, steam)
    return im


def sheet_figures(name):
    """Split a multi-figure green plate into separate cut-outs by column gaps."""
    rgb, a = K.key_green(os.path.join(ASSETS, name))
    rgb, a = K.trim(rgb, a)
    cols = (a > .35).sum(axis=0)
    xs = np.nonzero(cols > 3)[0]
    if len(xs) == 0:
        return []
    groups, start, prev = [], xs[0], xs[0]
    for x in xs[1:]:
        if x - prev > 40:
            groups.append((start, prev))
            start = x
        prev = x
    groups.append((start, prev))
    out = []
    for x0, x1 in groups:
        sub_rgb = rgb[:, x0:x1 + 1]
        sub_a = a[:, x0:x1 + 1]
        ys = np.nonzero((sub_a > .35).any(axis=1))[0]
        sub_rgb = sub_rgb[ys.min():ys.max() + 1]
        sub_a = sub_a[ys.min():ys.max() + 1]
        out.append(K.to_layer(sub_rgb, sub_a))
    return out


# ------------------------------------------------------------------- scene
class Scene:
    """A stack of layers at depths, plus the light and camera for this shot."""

    def __init__(self, bg_name, t0, t1, view=(0.5, 0.5, 1.0)):
        self.bg = background(bg_name)
        self.view = view          # (cx, cy, zoom) in plate UV space
        self.t0, self.t1 = t0, t1
        self.figures = []      # (PIL layer, spec dict)
        self.fg = []           # foreground blurred elements
        self.lights = []
        self.grade = dict()
        self.caption = None
        self.flash = 0.0

    def add(self, layer, xf, yf, hf, flip=False, alpha=1.0, depth=1.0,
            rot=0.0, motion=None, blur=0.0, tint=None, shadow=None):
        """Place a cut-out by frame fractions.

        xf, yf: feet position as a fraction of frame width/height.
        hf:     figure height as a fraction of frame height.
        """
        scale = (hf * H) / layer.size[1]
        self.figures.append(dict(layer=layer, x=xf * W, y=yf * H, scale=scale, flip=flip,
                                 alpha=alpha, depth=depth, rot=rot, motion=motion or {},
                                 blur=blur, tint=tint, shadow=shadow))
        return self.figures[-1]


def draw_character(canvas, spec, t, cam):
    """Composite one animated cut-out with its own motion and a contact shadow."""
    m = spec['motion']
    k = C.clamp((t - m.get('t0', 0.0)) / max(1e-3, m.get('dur', 1.0)))
    x = spec['x'] + m.get('dx', 0.0) * C.smooth(k)
    y = spec['y'] + m.get('dy', 0.0) * C.smooth(k)
    breathe = math.sin(t * m.get('breath_rate', 1.4) + m.get('seed', 0.0)) * m.get('breath_amp', 2.0)
    sway = math.sin(t * m.get('sway_rate', .55) + m.get('seed', 0.0) * 2) * m.get('sway_amp', 0.0)
    bob = -abs(math.sin(t * m.get('step_rate', 0.0))) * m.get('step_amp', 0.0)
    scale = spec['scale'] * (1.0 + m.get('grow', 0.0) * C.smooth(k))
    rot = spec['rot'] + sway

    layer = spec['layer']
    if spec['blur'] > 0.2:
        arr = np.asarray(layer).astype(np.float32) / 255.0
        r = C.gauss(arr[..., :3], spec['blur'])
        aa = C.gauss(arr[..., 3], spec['blur'])
        if spec['tint']:
            r = r * .55 + np.array(spec['tint'], np.float32) * .45
        layer = Image.fromarray((np.dstack([np.clip(r, 0, 1), np.clip(aa, 0, 1)]) * 255)
                                .astype(np.uint8), 'RGBA')

    # contact shadow first, so the figure never floats
    if spec['shadow']:
        strength, rx, ry = spec['shadow']
        canvas = K.shadow_under(canvas, x, y, rx * spec['scale'], ry * spec['scale'], strength)

    depth = spec['depth']
    # parallax is a nudge, not a re-layout: a few tens of pixels at most
    px = (cam.x_at(depth) - cam.x_at(0.0)) * 0.22
    py = (cam.y_at(depth) - cam.y_at(0.0)) * 0.22
    canvas = K.place(canvas, layer, x + px, y + py + breathe + bob,
                     scale=scale, rot=rot, flip=spec['flip'],
                     alpha=spec['alpha'] * spec.get('fade', 1.0))
    return canvas


def finish(img, scene, t, cam):
    """Everything after compositing: light, bloom, grade, gate weave."""
    # volumetric shafts from the scene's key window
    for light in scene.lights:
        img = C.light_shaft(img, light['origin'], light['angle'], light['length'],
                            light['width'], light['colour'], light['power'], t)
    img = C.bloom(img, threshold=.60, radius=(16, 40, 88), strength=(.50, .30, .17))
    img = C.halation(img, .10)
    g = scene.grade
    img = C.grade(img, lift=g.get('lift', (0, 0, 0)), gamma=g.get('gamma', (1, 1, 1)),
                  gain=g.get('gain', (1, 1, 1)), contrast=g.get('contrast', 1.0),
                  sat=g.get('sat', 1.0), tint=g.get('tint'), tint_amount=g.get('tint_amount', 0))
    img = C.vignette(img, power=g.get('vignette', .50), size=g.get('vignette_size', 1.30))
    img = C.grain(img, amount=.020, seed=int(t * 1000) % 65536)
    return np.clip(img, 0, 1)


_SCRIPT = {}


def caption_window(idx):
    """Captions follow the voice: in a beat after the line starts, out before it ends."""
    if idx not in _SCRIPT:
        for c in load_script():
            _SCRIPT.setdefault(len(_SCRIPT), c)
    cues = load_script()
    c = cues[idx]
    t0 = c['start'] + 0.18
    t1 = c['start'] + c['duration'] + 0.10
    return t0, t1


def caption_alpha(t, idx, hold=0.12):
    t0, t1 = caption_window(idx)
    a_in = C.ramp(t, t0, t0 + 0.30)
    a_out = 1.0 - C.ramp(t, t1 - 0.16, t1 + hold)
    return a_in * a_out


def caption_layer(text, size=(W, H), scale=1.0, sub='FICTIONAL'):
    if not text:
        return None
    return C.draw_text_layer(size, text, FONT, int(58 * scale), max_width=int(880 * scale),
                             extra=sub)


def compose(scene, t, cam, caption_img=None, cap_alpha=0.0):
    w, h = W, H
    # background with its own parallax + a slow drift for life
    cam.setup(t)
    bg = scene.bg
    bh, bw = bg.shape[:2]
    # plate framing: view centre in UV, zoomed so the plate covers the frame
    vx, vy, vz = scene.view
    cover = max(bw / w, bh / h)
    s = cover * vz * cam.zoom_at(0.0)
    cw, ch = w / s, h / s
    cx = np.clip(vx * bw - cw / 2 + cam.x_at(0.0) * 0.35, 0, bw - cw)
    cy = np.clip(vy * bh - ch / 2 + cam.y_at(0.0) * 0.35, 0, bh - ch)
    crop = bg[int(cy):int(cy) + int(ch), int(cx):int(cx) + int(cw)]
    canvas = np.asarray(Image.fromarray((crop * 255).astype(np.uint8))
                        .resize((w, h), Image.BICUBIC)).astype(np.float32) / 255.0

    for spec in scene.figures:
        canvas = draw_character(canvas, spec, t, cam)
    canvas = finish(canvas, scene, t, cam)
    # scrim under the captions: a soft dark band, the way subtitles are burned
    band = np.clip((np.arange(H, dtype=np.float32) / H - 0.755) / 0.06, 0, 1)
    scrim = (band * 0.42 * cap_alpha)[:, None, None]
    canvas = canvas * (1 - scrim)
    if caption_img is not None and cap_alpha > 0:
        if isinstance(caption_img, np.ndarray):
            arr = caption_img
        else:
            arr = np.asarray(caption_img).astype(np.float32) / 255.0
            caption_img = arr
            if 'caption_cache' not in scene.__dict__:
                scene.__dict__['caption_cache'] = arr
        a = arr[..., 3:4] * cap_alpha
        canvas = canvas * (1 - a) + arr[..., :3] * a
    return canvas


class Cam:
    """Camera moves defined per shot; parallax comes from layer depth."""

    def __init__(self):
        self.t = 0.0
        self.k = 0.0
        self.x0 = self.x1 = 0.0
        self.y0 = self.y1 = 0.0
        self.z0 = self.z1 = 1.0
        self.handheld = 0.0
        self.shake = 0.0
    def setup(self, t, t0=0.0, t1=1.0, x=(0, 0), y=(0, 0), zoom=(1.0, 1.0),
              handheld=1.0, shake=0.0, ease=None):
        self.t = t
        self.k = (ease or C.smoother)((t - t0) / max(1e-3, t1 - t0))
        self.x0, self.x1 = x
        self.y0, self.y1 = y
        self.z0, self.z1 = zoom
        self.handheld = handheld
        self.shake = shake

    def x_at(self, depth):
        d = 0.35 + 0.65 * depth
        jitter = self.handheld * (math.sin(self.t * 0.63) * 4.5 + math.sin(self.t * 1.47 + 1.1) * 2.2)
        s = self.shake * (math.sin(self.t * 33.7) * .6 + math.sin(self.t * 57.1 + 2) * .35)
        return (self.x0 + (self.x1 - self.x0) * self.k) * d + jitter + s

    def y_at(self, depth):
        d = 0.35 + 0.65 * depth
        jitter = self.handheld * (math.sin(self.t * .51 + .4) * 5.0 + math.sin(self.t * 1.19) * 2.4)
        s = self.shake * (math.sin(self.t * 41.3 + 1) * .6 + math.sin(self.t * 63.7) * .35)
        return (self.y0 + (self.y1 - self.y0) * self.k) * d + jitter + s

    def zoom_at(self, depth):
        z = self.z0 + (self.z1 - self.z0) * self.k
        return 1.0 + (z - 1.0) * (0.45 + 0.55 * depth)

    def parallax(self, depth):
        return (self.x_at(depth) * depth, self.y_at(depth) * depth, 1.0)


# -------------------------------------------------------------------- shots
def load_script():
    with open(os.path.join(ROOT, 'script.json')) as f:
        return json.load(f)


# ------------------------------------------------------------------ render
def build_shots():
    import acts
    return acts.build()


def render_stream(out_path, only_t0=None, only_t1=None, scale=1.0, fps=FPS):
    import imageio_ffmpeg
    shots = build_shots()
    script = load_script()
    tw, th = int(W * scale), int(H * scale)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{tw}x{th}', '-r', str(fps), '-i', '-',
           '-c:v', 'libx264', '-preset', 'slow', '-crf', '17',
           '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    caps, n = {}, 0
    for sh in shots:
        sc = sh['scene']
        f0, f1 = int(round(sc.t0 * fps)), int(round(sc.t1 * fps))
        idx = sh['cap']
        if idx is not None and idx not in caps:
            caps[idx] = np.asarray(caption_layer(script[idx]['text'])).astype(np.float32) / 255.0
        for fi in range(f0, f1):
            t = fi / fps
            if only_t0 is not None and t < only_t0:
                continue
            if only_t1 is not None and t >= only_t1:
                continue
            cam = Cam()
            cam.setup(t, sc.t0, sc.t1, **sh['cam'])
            a = caption_alpha(t, idx)
            img = compose(sc, t, cam, caps.get(idx), a)
            if scale != 1.0:
                img = np.asarray(Image.fromarray((img * 255).astype(np.uint8))
                                 .resize((tw, th), Image.LANCZOS)).astype(np.float32) / 255.0
            proc.stdin.write((np.clip(img, 0, 1) * 255).astype(np.uint8).tobytes())
            n += 1
            if n % 96 == 0:
                print(f'  {n} frames, t={t:.1f}s', flush=True)
    proc.stdin.close()
    proc.wait()
    print('frames', n, '->', out_path)
    return n


def render(out_path, only_t0=None, only_t1=None, preview_every=None, scale=1.0):
    shots = build_shots()
    tw, th = int(W * scale), int(H * scale)
    caps = {}
    script = load_script()

    frames = []
    for sh in shots:
        f0 = int(round(sh['t0'] * FPS))
        f1 = int(round(sh['t1'] * FPS))
        for fi in range(f0, f1):
            t = fi / FPS
            if only_t0 is not None and t < only_t0:
                continue
            if only_t1 is not None and t >= only_t1:
                continue
            cam = Cam()
            cam.setup(t, sh['t0'], sh['t1'], **sh['cam'])
            if sh['caption_idx'] is not None and sh['caption_idx'] not in caps:
                caps[sh['caption_idx']] = caption_layer(script[sh['caption_idx']]['text'])
            cap = caps.get(sh['caption_idx'])
            a = C.ramp(t, sh['t0'] + 0.10, sh['t0'] + 0.45)
            img = compose(sh['scene'], t, cam, cap, a)
            if scale != 1.0:
                img = np.asarray(Image.fromarray((img * 255).astype(np.uint8))
                                 .resize((tw, th), Image.LANCZOS)).astype(np.float32) / 255.0
            frames.append((img * 255).astype(np.uint8))
            if preview_every and len(frames) % preview_every == 0:
                print(f'  frame {len(frames)} t={t:.2f}', flush=True)
    return frames


def encode(frames, out_path, fps=FPS):
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    h, w = frames[0].shape[:2]
    cmd = [ff, '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{w}x{h}', '-r', str(fps), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
           '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fr in frames:
        p.stdin.write(fr.tobytes())
    p.stdin.close()
    p.wait()
    return out_path


def render_film(out_path, scale=1.0):
    return render_stream(out_path, scale=scale)


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--t0', type=float, default=None)
    ap.add_argument('--t1', type=float, default=None)
    ap.add_argument('--scale', type=float, default=1.0)
    ap.add_argument('--out', default='/tmp/shot.mp4')
    ap.add_argument('--still', default=None)
    args = ap.parse_args()
    if args.still:
        fr = render(args.out, args.t0, args.t1, preview_every=24, scale=args.scale)
        for i in (0, len(fr) // 3, len(fr) // 2, len(fr) - 1):
            Image.fromarray(fr[i]).save(args.still.replace('.jpg', f'_{i:04d}.jpg'), quality=92)
    else:
        render_stream(args.out, args.t0, args.t1, scale=args.scale)
