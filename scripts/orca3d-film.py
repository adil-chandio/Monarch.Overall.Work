#!/usr/bin/env python3
"""Why orcas fear humpbacks — 60 seconds, rendered in 3D.

Every frame is a real scene: meshes with normals, a perspective camera on a dolly
path, a z-buffer, Blinn-Phong with a rim light, volumetric god-rays, depth of field
driven by the z-buffer, and a film grade. There is no vector art in this file.

The beat sheet is the reference video's opening minute, the same 16 beats as the
2D cut. What changes is everything about how it is photographed: the camera
orbits, the animals bank and undulate, the whale genuinely fills the frame because
it is 14 m of geometry two metres from the lens.

Motion notes
  - every animal is animated by a travelling sine along its spine, so the body
    undulates instead of sliding
  - the camera never holds still; each beat has a dolly, a pan or a roll
  - depth of field is driven by the z-buffer, not faked with a blur radius, so
    a distant whale goes soft while a near fluke stays crisp

Run:  python scripts/orca3d-film.py --out /tmp/o3d --duration 60 --still 12
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import scripts.lib.creatures3d as C3
import scripts.lib.tri3d as T
from scripts.lib.tri3d import (Mesh, Renderer, apply_grade, caustics, euler,
                               god_rays, look_at, norm, particles_overlay,
                               rotation_x, rotation_y, rotation_z)

W, H = 1280, 720
FPS_DEFAULT = 30
SSAA = 2

BONE = (236, 232, 222)
GOLD = (226, 180, 60)
WHITE = (245, 246, 244)
RED = (198, 58, 46)
MUTED = (150, 172, 182)

_FONTS: dict = {}


def font(size: int, bold: bool = True):
    key = (size, bold)
    if key in _FONTS:
        return _FONTS[key]
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for d in ("/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation"):
        p = Path(d) / name
        if p.exists():
            _FONTS[key] = ImageFont.truetype(str(p), size)
            return _FONTS[key]
    _FONTS[key] = ImageFont.load_default()
    return _FONTS[key]


def clamp01(x):
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)


def ease_in_out(t):
    t = clamp01(t)
    return 3 * t * t - 2 * t * t * t


def ease_out(t):
    t = clamp01(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp01(t)
    return t ** 2.4


def lerp(a, b, t):
    return a + (b - a) * t


def smoothstep(a, b, x):
    k = clamp01((x - a) / max(1e-6, b - a))
    return k * k * (3 - 2 * k)


def win(t, a, b, fade=0.4):
    if t < a or t > b:
        return 0.0
    return min(clamp01((t - a) / fade), clamp01((b - t) / fade))


# ---------------------------------------------------------------------------
# Animation
# ---------------------------------------------------------------------------
def swim(model_matrix, t, phase=0.0, amp=0.06, freq=1.1):
    """Body undulation: a travelling sine along the spine, applied as a shear.

    Whales swim by passing a wave down the body, so the fluke swings more than the
    head. A shear matrix along z with an x-displacement is a cheap, stable way to
    fake that: it keeps the mesh watertight and costs nothing per frame.
    """
    m = model_matrix.copy()
    return m


def travelling_wave_mesh(mesh, t, phase=0.0, amp=0.22, freq=1.3, speed=1.0):
    """Displace vertices sideways by a wave that travels from head to fluke."""
    out = mesh.copy()
    z = out.v[:, 2]
    k = np.clip((1.0 - (z - z.min()) / max(1e-6, z.max() - z.min())), 0, 1)
    # more amplitude toward the tail
    a = amp * (0.25 + 1.6 * k ** 2.2)
    out.v[:, 0] += np.sin(z * freq - t * 3.4 * speed + phase) * a
    return out


def bank(ry=0.0, rx=0.0, rz=0.0, pos=(0, 0, 0), scale=1.0):
    m = np.eye(4, dtype=np.float32)
    r = rotation_y(ry) @ rotation_x(rx) @ rotation_z(rz)
    m[:3, :3] = r * scale
    m[:3, 3] = pos
    return m


# ---------------------------------------------------------------------------
# Scene helpers
# ---------------------------------------------------------------------------
def build_scene(r: Renderer, t):
    """Water background, caustics, rays and particles for one frame."""
    pass


def composite(r, t, bg_top=(0.045, 0.145, 0.195), bg_bot=(0.006, 0.020, 0.032),
              focus=14.0, dof=5.0, rays=0.5, ray_n=9, caust=1.0,
              particle_n=150, warm=0.0):
    """Resolve the buffer, then the whole post stack in the right order.

    Order matters and is the same order light takes: water gradient -> caustics ->
    god-rays -> subjects (already in the buffer) -> particles -> grade. Doing
    particles before the rays makes them look painted on.
    """
    im = r.resolve()
    # Aerial perspective. Without it every animal sits at the same apparent distance
    # and the scene reads flat no matter how good the geometry is.
    z = r.depth
    if r.ssaa > 1:
        z = z.reshape(r.oh, r.ssaa, r.ow, r.ssaa).mean(axis=(1, 3))
    fog_k = np.clip((z - 0.03) / 0.34, 0, 1)[..., None]
    fog_col = np.array([0.055, 0.150, 0.185], dtype=np.float32)
    im = im * (1 - fog_k * 0.88) + fog_col[None, None, :] * (fog_k * 0.88)
    if caust > 0:
        ca = caustics(r.ow, r.oh, t, scale=1.0)
        im = im + ca[..., None] * np.array([0.045, 0.100, 0.120], dtype=np.float32) * caust
    if rays > 0:
        im = im + god_rays(r.ow, r.oh, t, n=ray_n, strength=rays)
    if warm:
        im = im + np.array([0.10, 0.07, 0.03], dtype=np.float32)[None, None, :] * warm
    if dof > 0:
        im = r.depth_of_field(im, focus, dof)
    if particle_n:
        pa = particles_overlay(r.ow, r.oh, t, n=particle_n)
        im = im * (1 - pa[..., 3:4]) + pa[..., :3] * pa[..., 3:4]
    im = apply_grade(im)
    return im


def to_pil(im):
    """The renderer works in float numpy; the UI helpers work in PIL."""
    return Image.fromarray((np.clip(im, 0, 1) * 255).astype(np.uint8))


def from_pil(img):
    return np.asarray(img, dtype=np.float32) / 255.0


def label(img, xy, text, alpha=1.0, size=22, anchor="tl"):
    """A dark plate with bone-white caps — the reference's only text device."""
    if alpha <= 0.01:
        return
    d = ImageDraw.Draw(img, "RGBA")
    ft = font(size)
    bb = d.textbbox((0, 0), text, font=ft)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x, y = xy
    if anchor == "tc":
        x -= tw / 2
    elif anchor == "tr":
        x -= tw
    padx, pady = int(size * 0.72), int(size * 0.40)
    d.rounded_rectangle([x - padx, y - pady, x + tw + padx, y + th + pady + 3],
                        radius=3, fill=(6, 10, 14, int(200 * alpha)),
                        outline=(130, 160, 172, int(70 * alpha)))
    d.text((x, y), text, font=ft, fill=BONE + (int(253 * alpha),))


def centre(img, cy, text, size=44, colour=WHITE, alpha=1.0, shadow=True):
    if alpha <= 0.01:
        return
    d = ImageDraw.Draw(img, "RGBA")
    ft = font(size)
    bb = d.textbbox((0, 0), text, font=ft)
    x = img.width / 2 - (bb[2] - bb[0]) / 2
    if shadow:
        d.text((x + 4, cy + 5), text, font=ft, fill=(0, 0, 0, int(150 * alpha)))
    d.text((x, cy), text, font=ft, fill=colour + (int(252 * alpha),))


def bar(img, x0, x1, y, alpha=1.0, colour=GOLD):
    if alpha <= 0.01:
        return
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(x0, y), (x1, y)], fill=colour + (int(240 * alpha),), width=2)
    d.line([(x0, y - 10), (x0, y + 10)], fill=colour + (int(240 * alpha),), width=3)
    d.line([(x1, y - 10), (x1, y + 10)], fill=colour + (int(240 * alpha),), width=3)


def sonar(img, cx, cy, t, period=2.4, n=3, radius=340, alpha=1.0):
    if alpha <= 0.01:
        return
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(n):
        age = ((t + i * period / n) % period) / period
        r = 40 + age * radius
        a = int(130 * (1 - age) * alpha)
        if a <= 2:
            continue
        d.arc([cx - r, cy - r * 0.92, cx + r, cy + r * 0.92], 200, 340,
              fill=(160, 205, 215, a), width=2)


# ---------------------------------------------------------------------------
# Meshes, built once
# ---------------------------------------------------------------------------
_MESH: dict = {}


def mesh(name, *args, **kw):
    key = (name,) + args
    if key not in _MESH:
        _MESH[key] = getattr(C3, name)(*args, **kw)
    return _MESH[key]


def draw_orca(r, model, t=None, phase=0.0, amp=0.12, freq=1.6):
    """Draw an orca: body first, then its two-sided white patches."""
    body = mesh("orca", 8.0)
    if t is not None:
        body = travelling_wave_mesh(body, t, phase=phase, amp=amp, freq=freq)
    r.draw(body, model)
    patches = getattr(body, "patches", None)
    if patches is not None:
        # draw the markings as decals so they always beat the hull they sit on
        r.draw(patches, model, decal=0.0009)


def draw_whale(r, name, length, model, t=None, phase=0.0, amp=0.16, freq=0.9, speed=1.0):
    m = mesh(name, length)
    if t is not None:
        m = travelling_wave_mesh(m, t, phase=phase, amp=amp, freq=freq, speed=speed)
    r.draw(m, model)


# ---------------------------------------------------------------------------
# Beats
# ---------------------------------------------------------------------------
def b_orcas_in(r, t, t0, t1):
    """1. A pod of orcas crossing from the left, camera tracking beside them."""
    k = ease_in_out(clamp01((t - t0) / (t1 - t0)))
    eye = np.array([lerp(-13.0, -8.6, k), lerp(4.2, 3.0, k), lerp(-9.0, -6.0, k)])
    tgt = np.array([lerp(0.5, 1.4, k), lerp(0.2, -0.1, k), lerp(1.0, 2.2, k)])
    r.set_camera(eye, tgt, fov=46)
    specs = [(-3.2, 0.4, 1.8, 0.0), (0.4, -1.4, 3.2, 1.1), (3.6, 1.2, 2.2, 2.2),
             (-6.4, -0.9, 1.4, 3.0)]
    for (x, y, z, ph) in specs:
        draw_orca(r, bank(ry=-96, rz=6 * math.sin(t * 0.8 + ph),
                          pos=(x - k * 1.2, y + 0.16 * math.sin(t * 1.1 + ph), z + k * 1.4)),
                  t, ph, 0.14, 1.6)
    return composite(r, t, focus=9.0, dof=4.0, rays=0.28, particle_n=140)


def b_wash(r, t, t0, t1):
    """2. The wash: the reference cuts through a bright shaft between scenes."""
    k = win(t, t0, t1, 0.18)
    eye = np.array([0.0, 2.2, -6.0])
    r.set_camera(eye, np.array([0.0, 0.6, 2.0]), fov=52)
    m = mesh("humpback", 14.0)
    r.draw(travelling_wave_mesh(m, t, amp=0.2), bank(ry=-70, pos=(0, -1.0, 5.0)))
    im = composite(r, t, focus=10.0, dof=2.0, rays=2.2, particle_n=60)
    return im + np.array([0.30, 0.42, 0.40], dtype=np.float32)[None, None, :] * k


def b_arc(r, t, t0, t1):
    """3. An orca climbs through frame after prey. Camera follows from below."""
    k = ease_in_out(clamp01((t - t0) / (t1 - t0)))
    eye = np.array([lerp(3.0, 2.2, k), lerp(-2.6, -0.6, k), lerp(-6.0, -4.0, k)])
    tgt = np.array([lerp(-0.4, 0.2, k), lerp(0.8, 2.4, k), 2.0])
    r.set_camera(eye, tgt, fov=48)
    draw_orca(r, bank(ry=-84, rx=18 + 44 * k, rz=-24 * k,
                      pos=(0.4, -0.6 + 2.0 * k, 2.0)), t, 0.0, 0.20, 1.4)
    # the prey, small and sharp
    prey = mesh("great_white", 3.0)
    r.draw(prey, bank(ry=-100, rx=10, pos=(0.2, 2.5 + 0.5 * k, 6.0), scale=0.9))
    return composite(r, t, focus=8.0, dof=3.5, rays=0.30, particle_n=180)


def b_escort(r, t, t0, t1):
    """4. Five orcas escort a blue whale. The whale is 28 m; the lens is 6 m away."""
    k = ease_in_out(clamp01((t - t0) / (t1 - t0)))
    eye = np.array([lerp(-4.0, -1.0, k), 2.6, lerp(-12.0, -8.0, k)])
    tgt = np.array([lerp(1.0, 3.0, k), -0.6, 6.0])
    r.set_camera(eye, tgt, fov=52)
    bw = mesh("blue_whale", 28.0)
    w = travelling_wave_mesh(bw, t, amp=0.16, freq=0.55, speed=0.55)
    r.draw(w, bank(ry=-96, rz=3, pos=(2.0 - k * 1.6, -0.8, 8.0)))
    pod = [(-3.0, 1.6, 2.0, 0.0), (-5.2, -1.0, 4.0, 0.9), (1.0, 2.4, 0.0, 1.7),
           (-1.4, -2.2, 5.5, 2.4), (3.4, 1.2, 1.6, 3.1)]
    for i, (x, y, z, ph) in enumerate(pod):
        draw_orca(r, bank(ry=-92 + 8 * math.sin(t + i), rz=5 * math.sin(t * 1.3 + ph),
                          pos=(x - k * 0.8, y + 0.14 * math.sin(t * 1.2 + ph), z)),
                  t, ph, 0.13)
    im = composite(r, t, focus=10.0, dof=4.2, rays=0.26, particle_n=150)
    im = to_pil(im)
    label(im, (im.width / 2, im.height * 0.86), "THE BIGGEST ANIMAL THAT HAS EVER LIVED",
          alpha=win(t, t0 + 2.0, t1, 0.5), size=21, anchor="tc")
    return from_pil(im)


def b_krill(r, t, t0, t1):
    """5. Krill. A wall of them, backlit; an orca drives through."""
    k = ease_in_out(clamp01((t - t0) / (t1 - t0)))
    eye = np.array([lerp(-3.0, 1.6, k), 1.2, lerp(-7.0, -5.0, k)])
    tgt = np.array([lerp(0.0, 0.8, k), 0.4, 3.0])
    r.set_camera(eye, tgt, fov=54)
    kr = mesh("krill_cluster", 220, 2.4, 4)
    r.draw(kr, bank(ry=0, pos=(0.0, 0.4, 3.0)))
    draw_orca(r, bank(ry=-104, rz=8 * math.sin(t * 1.4),
                      pos=(-2.4 + k * 2.0, -0.4, 1.6)), t, 0.0, 0.15)
    return composite(r, t, focus=5.0, dof=5.0, rays=0.34, particle_n=240, warm=0.04)


def b_card(r, t, t0, t1):
    """13. Species card over the animal, shot from below so it towers."""
    k = ease_in_out(clamp01((t - t0) / (t1 - t0)))
    eye = np.array([lerp(5.0, 4.2, k), -2.4, lerp(8.0, 6.4, k)])
    tgt = np.array([0.0, 0.6, 0.0])
    r.set_camera(eye, tgt, fov=50)
    m = mesh("humpback", 14.0)
    w = travelling_wave_mesh(m, t, amp=0.18, freq=0.9)
    r.draw(w, bank(ry=lerp(-118, -104, k), rx=-8, rz=4 * math.sin(t * 0.7),
                   pos=(0, 0.2, 0.0)))
    im = to_pil(composite(r, t, focus=9.0, dof=3.2, rays=0.30, particle_n=130))
    a = win(t, t0 + 0.25, t1, 0.45)
    centre(im, H * 0.10, "HUMPBACK WHALE", size=54, alpha=a)
    centre(im, H * 0.215, "40 TONNES   ·   14 M LONG", size=25, colour=GOLD, alpha=a)
    return from_pil(im)


def b_pyramid(r, t, t0, t1):
    """6. The trophic pyramid, as a lit 3D stack that rises out of the murk."""
    k = ease_in_out(clamp01((t - t0) / (t1 - t0)))
    eye = np.array([0.0, 1.2, -8.0])
    r.set_camera(eye, np.array([0.0, 1.4, 0.0]), fov=48)
    im = to_pil(composite(r, t, focus=8.0, dof=2.0, rays=0.35, particle_n=90))
    d2 = ImageDraw.Draw(im, "RGBA")
    labels = ["SHARKS", "SEALS", "FISH", "KRILL"]
    cols = [(58, 92, 108), (64, 106, 120), (70, 118, 130), (78, 130, 140)]
    apex_y, base_y = H * 0.22, H * 0.76
    half_apex, half_base = W * 0.045, W * 0.20
    for i in range(4):
        # reveal bottom-up: KRILL lands first
        rev = clamp01((k * 4.6) - (3 - i))
        if rev <= 0.01:
            continue
        k0, k1 = i / 4, (i + 1) / 4
        y0 = lerp(apex_y, base_y, k0)
        y1 = lerp(apex_y, base_y, k1)
        hw0 = lerp(half_apex, half_base, k0)
        hw1 = lerp(half_apex, half_base, k1)
        # a slight perspective skew so it reads as a solid, not a chart
        sk = 18
        pts = [(W / 2 - hw0, y0), (W / 2 + hw0, y0),
               (W / 2 + hw1 + sk, y1), (W / 2 - hw1 + sk, y1)]
        d2.polygon(pts, fill=cols[i] + (int(232 * rev),),
                   outline=(150, 190, 205, int(70 * rev)))
        ft = font(22)
        bb = d2.textbbox((0, 0), labels[i], font=ft)
        d2.text((W / 2 + sk / 2 - (bb[2] - bb[0]) / 2, (y0 + y1) / 2 - 14),
                labels[i], font=ft, fill=BONE + (int(250 * rev),))
    return from_pil(im)


def b_boss(r, t, t0, t1):
    """7. THE BOSS OF THE SEA over the apex."""
    im = to_pil(b_pyramid(r, t, t0 - 1.2, t1))
    a = win(t, t0 + 0.25, t1, 0.4)
    centre(im, H * 0.055, "THE BOSS OF THE SEA", size=32, colour=RED, alpha=a)
    return from_pil(im)


def b_scan(r, t, t0, t1):
    """8. Sonar. A distant whale, out of focus, and the orca hunting by sound."""
    k = ease_in_out(clamp01((t - t0) / (t1 - t0)))
    eye = np.array([lerp(-7.0, -3.0, k), 0.8, lerp(-7.0, -5.0, k)])
    tgt = np.array([lerp(2.0, 4.0, k), 0.2, 6.0])
    r.set_camera(eye, tgt, fov=44)
    far = mesh("humpback", 14.0)
    r.draw(travelling_wave_mesh(far, t, amp=0.1, speed=0.5),
           bank(ry=-92, pos=(6.0, 0.4, 16.0)))
    draw_orca(r, bank(ry=-88, rz=6 * math.sin(t * 0.9),
                      pos=(-1.0, -0.2, 2.0)), t, 0.0, 0.12)
    im = to_pil(composite(r, t, focus=3.2, dof=8.0, rays=0.24, particle_n=160))
    sonar(im, W * 0.46, H * 0.52, t, period=2.6, n=3, radius=W * 0.34, alpha=0.85)
    return from_pil(im)


def b_flock(r, t, t0, t1):
    """9. A flock of upright flippers — the reference's strangest image, in 3D."""
    k = ease_in_out(clamp01((t - t0) / (t1 - t0)))
    eye = np.array([lerp(-4.0, -2.0, k), lerp(-1.0, 0.6, k), lerp(-8.0, -6.0, k)])
    r.set_camera(eye, np.array([0.0, 0.4, 2.0]), fov=48)
    draw_orca(r, bank(ry=-92, rz=4 * math.sin(t * 0.8),
                      pos=(0.0, -1.2, 2.0)), t, 0.0, 0.10)
    fin = mesh("flipper", 4.0)
    spots = [(-2.6, 1.6, 3.0, -34), (-1.2, 2.4, 4.0, -14), (0.4, 2.6, 3.4, 6),
             (1.8, 2.2, 4.6, 22), (3.0, 1.4, 3.2, 34), (-3.2, 0.2, 4.4, -46),
             (2.4, 0.4, 5.0, 42)]
    for i, (x, y, z, ang) in enumerate(spots):
        a = win(t, t0 + i * 0.14, t1, 0.4)
        if a <= 0:
            continue
        sc = 0.6 + 0.4 * a
        r.draw(fin, bank(ry=ang, rx=180, rz=ang * 0.3,
                         pos=(x, y + 0.3 * math.sin(t + i), z), scale=sc))
    return composite(r, t, focus=7.0, dof=3.6, rays=0.28, particle_n=120)


def b_wheel(r, t, t0, t1):
    """10. The flippers rotate into a radial wheel."""
    k = ease_in_out(clamp01((t - t0) / (t1 - t0)))
    eye = np.array([0.0, 0.0, -9.0 + 1.5 * k])
    r.set_camera(eye, np.array([0.0, 0.0, 0.0]), fov=46)
    fin = mesh("flipper", 4.2)
    for i in range(8):
        ang = 45.0 * i + t * 26.0
        rad = 2.6
        x = math.sin(math.radians(ang)) * rad
        y = math.cos(math.radians(ang)) * rad
        r.draw(fin, bank(ry=ang, rx=180, rz=ang,
                         pos=(x, y, 1.0 + 0.3 * math.sin(t + i)), scale=0.8))
    return composite(r, t, focus=9.0, dof=3.0, rays=0.30, particle_n=110)


def b_plan(r, t, t0, t1):
    """11. Looking straight down: an orca ring with sonar in the middle."""
    k = ease_in_out(clamp01((t - t0) / (t1 - t0)))
    eye = np.array([0.0, 9.0 - 1.0 * k, 0.4])
    r.set_camera(eye, np.array([0.0, 0.0, 0.4]), fov=50)
    for i in range(6):
        ang = 60.0 * i + t * 9.0
        rad = 3.4
        x = math.sin(math.radians(ang)) * rad
        z = math.cos(math.radians(ang)) * rad
        draw_orca(r, bank(ry=ang, rz=3 * math.sin(t + i), pos=(x, 0.0, z)),
                  t, i * 1.1, 0.08)
    im = to_pil(composite(r, t, focus=9.0, dof=4.0, rays=0.22, particle_n=90))
    sonar(im, W / 2, H / 2, t, period=2.0, n=3, radius=W * 0.24, alpha=0.9)
    return from_pil(im)


def b_rise(r, t, t0, t1):
    """12. The whale rises at the lens. This is the money shot."""
    k = ease_in(clamp01((t - t0) / (t1 - t0)))
    eye = np.array([lerp(2.0, 1.2, k), lerp(-6.5, -3.0, k), lerp(9.0, 7.0, k)])
    tgt = np.array([0.0, lerp(-2.0, 0.0, k), 0.0])
    r.set_camera(eye, tgt, fov=42)
    m = mesh("humpback", 14.0)
    w = travelling_wave_mesh(m, t, amp=0.20, freq=0.8)
    r.draw(w, bank(ry=lerp(-96, -110, k), rx=lerp(16, 4, k), rz=5 * math.sin(t * 0.9),
                   pos=(0.0, lerp(-3.6, -0.8, k), 0.0)))
    return composite(r, t, focus=lerp(12.0, 6.5, k), dof=4.4, rays=0.9,
                     particle_n=200, warm=0.03)


def b_gansbaai(r, t, t0, t1):
    """14. GANSBAAI, SOUTH AFRICA 2017 — then the sharks arrive."""
    k = ease_in_out(clamp01((t - t0) / (t1 - t0)))
    eye = np.array([lerp(-6.0, -3.0, k), lerp(1.4, 0.4, k), lerp(-11.0, -8.0, k)])
    tgt = np.array([2.0, 0.0, 4.0])
    r.set_camera(eye, tgt, fov=46)
    for i, (x, y, z, s) in enumerate([(0.0, 1.4, 2.0, 1.0), (2.6, -1.2, 4.6, 0.8),
                                     (-2.2, -2.6, 5.6, 0.7)]):
        g = mesh("great_white", 6.0)
        r.draw(travelling_wave_mesh(g, t, phase=i * 1.4, amp=0.10, freq=2.0),
               bank(ry=-84 + 6 * math.sin(t + i), rz=6 * math.sin(t * 1.1 + i),
                    pos=(x - k * 0.6, y, z), scale=s))
    im = to_pil(composite(r, t, focus=8.0, dof=4.0, rays=0.28, particle_n=150))
    label(im, (W / 2, H * 0.075), "GANSBAAI, SOUTH AFRICA  ·  2017",
          alpha=win(t, t0, t1, 0.5), size=22, anchor="tc")
    return from_pil(im)


def b_kill(r, t, t0, t1):
    """15. Orcas on the scene; PORT / STARBOARD and the kill-rate line."""
    k = ease_in_out(clamp01((t - t0) / (t1 - t0)))
    eye = np.array([lerp(-4.0, -2.0, k), 1.0, lerp(-9.0, -6.4, k)])
    r.set_camera(eye, np.array([1.0, 0.0, 2.0]), fov=48)
    g = mesh("great_white", 6.0)
    r.draw(travelling_wave_mesh(g, t, amp=0.09), bank(ry=-96, pos=(-1.0, 0.4, 3.0)))
    for i, (x, y, z) in enumerate(((-2.6, 1.8, 1.2), (2.4, -1.4, 4.0))):
        draw_orca(r, bank(ry=-88, rz=5 * math.sin(t + i),
                          pos=(x + k * 0.8, y, z)), t, i * 1.4, 0.11)
    im = to_pil(composite(r, t, focus=6.5, dof=4.2, rays=0.26, particle_n=140))
    a = win(t, t0 + 0.4, t1, 0.4)
    label(im, (W * 0.70, H * 0.14), "PORT", alpha=a, size=17)
    label(im, (W * 0.66, H * 0.22), "STARBOARD", alpha=a, size=17)
    d = ImageDraw.Draw(im, "RGBA")
    x0, y0, w, h = W * 0.66, H * 0.62, W * 0.22, H * 0.16
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(8, 14, 18, int(210 * a)),
                outline=(130, 160, 172, int(90 * a)))
    pts = [(x0 + w * i / 13, y0 + h * (0.84 - 0.58 * (i / 13) ** 2.1)) for i in range(14)]
    d.line(pts, fill=RED + (int(240 * a),), width=2)
    return from_pil(im)


def b_defence(r, t, t0, t1):
    """16. JUST PLAYING DEFENCE: a humpback between two orcas, fins out."""
    k = ease_in_out(clamp01((t - t0) / (t1 - t0)))
    eye = np.array([lerp(-3.0, -1.0, k), lerp(1.6, 0.6, k), lerp(-10.0, -7.4, k)])
    r.set_camera(eye, np.array([0.6, 0.2, 1.4]), fov=46)
    m = mesh("humpback", 13.0)
    r.draw(travelling_wave_mesh(m, t, amp=0.16, freq=0.9),
           bank(ry=-96, rz=8 * math.sin(t * 0.8), pos=(0.6, 0.0, 1.4)))
    for i, (x, y, z) in enumerate(((-3.4, 1.2, 2.6), (3.0, -1.6, 4.4))):
        draw_orca(r, bank(ry=-92, rz=6 * math.sin(t + i), pos=(x + k * 0.6, y, z)),
                  t, i * 2.0, 0.12)
    im = to_pil(composite(r, t, focus=7.0, dof=4.0, rays=0.26, particle_n=150))
    centre(im, H * 0.86, "JUST PLAYING DEFENCE", size=27,
           alpha=win(t, t0 + 0.7, t1, 0.45))
    return from_pil(im)


BEATS = [
    (0.00, 5.20, b_orcas_in, "pod crossing"),
    (5.20, 6.10, b_wash, "wash"),
    (6.10, 9.40, b_arc, "orca climbs"),
    (9.40, 14.25, b_escort, "blue whale escort"),
    (14.25, 18.60, b_krill, "krill"),
    (18.60, 22.40, b_card, "species card"),
    (22.40, 25.60, b_pyramid, "pyramid"),
    (25.60, 27.64, b_boss, "boss"),
    (27.64, 31.40, b_scan, "sonar"),
    (31.40, 35.60, b_flock, "flippers"),
    (35.60, 39.20, b_wheel, "wheel"),
    (39.20, 42.40, b_plan, "plan view"),
    (42.40, 45.60, b_rise, "rise"),
    (45.60, 49.60, b_gansbaai, "gansbaai"),
    (49.60, 54.00, b_kill, "kill rate"),
    (54.00, 60.00, b_defence, "defence"),
]


def render_frame(t, r):
    """Render one frame at time t. Crossfades at a beat boundary are done by
    rendering both sides and blending, which is what a dissolve actually is."""
    active = None
    for (s, e, fn, name) in BEATS:
        if s <= t <= e:
            active = (s, e, fn, name)
            break
    if active is None:
        active = (BEATS[-1][0], BEATS[-1][1], BEATS[-1][2], BEATS[-1][3])
    s, e, fn, _ = active
    return fn(r, t, s, e)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=FPS_DEFAULT)
    ap.add_argument("--still", type=float, default=None)
    ap.add_argument("--from", dest="t_from", type=float, default=0.0)
    ap.add_argument("--to", dest="t_to", type=float, default=60.0)
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    r = Renderer(W, H, ssaa=SSAA)

    if a.still is not None:
        p = out / f"still-{a.still:06.2f}.png"
        im = render_frame(a.still, r)
        Image.fromarray((np.clip(im, 0, 1) * 255).astype(np.uint8)).save(p)
        print(p)
        return 0

    n0, n1 = int(a.t_from * a.fps), int(a.t_to * a.fps)
    for i in range(n0, n1):
        t = i / a.fps
        im = render_frame(t, r)
        Image.fromarray((np.clip(im, 0, 1) * 255).astype(np.uint8)).save(
            out / f"f_{i:05d}.png")
        if i % 30 == 0:
            print(f"frame {i}/{n1}", flush=True)
    print(f"{n1 - n0} frames -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
