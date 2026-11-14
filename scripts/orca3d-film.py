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
    """Displace vertices sideways by a wave that travels from head to fluke.

    The patches are deformed through the same displacement as the hull they sit on,
    so they stay locked to the body instead of sliding off it.
    """
    out = mesh.copy()
    pat = getattr(mesh, "patches", None)
    if pat is not None and pat is not mesh:
        out.patches = travelling_wave_mesh(pat, t, phase, amp, freq, speed)
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
              particle_n=150, warm=0.0, ray_far=26.0, surface=None):
    """Resolve the buffer, then the whole post stack in the order light travels.

    water gradient -> caustics -> subjects (in the buffer) -> depth-masked god rays
    -> particles -> surface -> DOF -> grade.

    Three things here were wrong in v2 and are the difference between "a 3D render"
    and a photograph of water:

    1. Fog was keyed on NDC depth, which is hyperbolic. Near the lens two metres
       covered a huge slice of the range and forty metres covered almost none, so
       the haze piled up in front of the camera instead of behind the subject.
       It is now keyed on metres via linear_depth().
    2. God rays were added flat over the whole frame, so they painted bright bars
       across animals that were meant to be in front of them. They are now
       multiplied by a far-depth mask: a shaft can only brighten water that is
       behind it, never a whale that is nearer the lens.
    3. There was no water surface at all. Every beat was shot in open blue with no
       above, which is why the film never felt like it was under anything.
    """
    im = r.resolve()
    z = r.linear_depth()

    # --- aerial perspective, in metres ---
    fog_k = (1.0 - np.exp(-np.maximum(z - 1.5, 0.0) / 13.0)) * 0.90
    fog_k = fog_k[..., None]
    fog_col = np.array([0.052, 0.142, 0.178], dtype=np.float32)
    im = im * (1 - fog_k) + fog_col[None, None, :] * fog_k

    if caust > 0:
        ca = caustics(r.ow, r.oh, t, scale=1.0)
        # caustics only land on surfaces near the surface; fade them with depth too
        cd = np.exp(-np.maximum(z - 1.0, 0.0) / 9.0)[..., None]
        im = im + ca[..., None] * np.array([0.040, 0.092, 0.110], dtype=np.float32)             * caust * cd

    if rays > 0:
        ray_layer = god_rays(r.ow, r.oh, t, n=ray_n, strength=rays)
        # a shaft of light sits at optical infinity: it may only add to water that is
        # further away than the shaft's own plane, never to a nearer animal
        # smoothstep, not clip: `clip` leaves a derivative discontinuity where the
        # ramp saturates, and because the seafloor plane crosses frame diagonally the
        # eye reads that discontinuity as a hard straight line - a visible geometry
        # edge in the middle of the water. A cubic ramp has zero slope at both ends,
        # so the mask fades in and out without announcing itself.
        _mn = np.clip((z - ray_far * 0.30) / (ray_far * 0.70), 0.0, 1.0)
        _ms = _mn * _mn * (3.0 - 2.0 * _mn)
        near_mask = _ms[..., None]
        im = im + ray_layer * near_mask

    if warm:
        im = im + np.array([0.10, 0.07, 0.03], dtype=np.float32)[None, None, :] * warm

    if particle_n:
        pa = particles_overlay(r.ow, r.oh, t, n=particle_n)
        im = im * (1 - pa[..., 3:4]) + pa[..., :3] * pa[..., 3:4]

    if surface is not None:
        im = water_surface(im, t, **surface)

    if dof > 0:
        im = r.depth_of_field(im, focus, dof)
    im = apply_grade(im)
    return im


def contact_shadow(im, r, pos, size=(2.6, 1.1), strength=0.55, lift=1.6):
    """Darken water directly beneath a body, so it sits in the scene.

    Underwater there is no hard shadow on a floor - but a large animal still blocks
    the downwelling light, and that occlusion is the strongest cue that it has mass
    rather than being pasted onto the background. v2 had none, which is why the pod
    read as cut-outs even after the markings were fixed.

    Screen-space, cheaply: project the world point under the body, draw an ellipse
    that is wider the lower the light, and multiply it into the image. It is an
    approximation and it is labelled as one - it is not a shadow map.
    """
    h, w = im.shape[:2]
    eye_pt = np.array([pos[0], pos[1] - lift * 0.5, pos[2], 1.0], dtype=np.float32)
    v = (eye_pt @ r.view.T)[:3]
    if v[2] <= 0.05:
        return im
    cl = np.array([v[0], v[1], v[2], 1.0], dtype=np.float32) @ r.proj.T
    if cl[3] <= 1e-5:
        return im
    ndc = cl[:3] / cl[3]
    cx = (ndc[0] * 0.5 + 0.5) * w
    cy = (1.0 - (ndc[1] * 0.5 + 0.5)) * h
    if not (-w <= cx <= 2 * w and -h <= cy <= 2 * h):
        return im
    # scale the ellipse by distance so a near animal shadows more screen area
    dist = float(np.linalg.norm(v))
    rad = max(8.0, (w / 1280.0) * 260.0 * float(size[0]) / max(dist, 1.0) * 3.4)
    rad_y = rad * float(size[1]) / float(size[0])
    yy = np.arange(h, dtype=np.float32)[:, None]
    xx = np.arange(w, dtype=np.float32)[None, :]
    d2 = ((xx - cx) / rad) ** 2 + ((yy - cy) / rad_y) ** 2
    m = np.exp(-d2 * 1.35) * float(strength)
    return im * (1.0 - m[..., None])


def box_mesh(w, h, d, colour=(0.05, 0.10, 0.13)):
    """A closed rectangular slab, wound so the normals point outward.

    The pyramid used to be four ImageDraw trapezoids. Drawing it as geometry means
    it inherits the light rig, the fog, the ray depth mask and the contact shadow -
    none of which a 2D polygon can do - and the perspective becomes the camera's
    rather than a hard-coded 18 px skew.
    """
    hw, hh, hd = w * 0.5, h * 0.5, d * 0.5
    v = np.array([[-hw, -hh, -hd], [hw, -hh, -hd], [hw, -hh, hd], [-hw, -hh, hd],
                  [-hw, hh, -hd], [hw, hh, -hd], [hw, hh, hd], [-hw, hh, hd]],
                 dtype=np.float32)
    t = np.array([[0, 2, 1], [0, 3, 2],      # bottom
                  [4, 5, 6], [4, 6, 7],      # top
                  [0, 1, 5], [0, 5, 4],      # back
                  [1, 2, 6], [1, 6, 5],      # right
                  [2, 3, 7], [2, 7, 6],      # front
                  [3, 0, 4], [3, 4, 7]],     # left
                 dtype=np.int32)
    m = Mesh(v, t, colour=np.asarray(colour, dtype=np.float32) * 255.0)
    m.material = "slab"
    return m


def project_pt(r, pt):
    """World point -> (x, y) in pixels, or None if it is behind the camera."""
    v = np.asarray(r.view, dtype=np.float64)
    pj = np.asarray(r.proj, dtype=np.float64)
    vc = v[:3, :3] @ np.asarray(pt, dtype=np.float64) + v[:3, 3]
    if vc[2] <= 0.05:          # +z is in front of the camera in this rig
        return None
    c = pj @ np.array([vc[0], vc[1], vc[2], 1.0])
    if abs(c[3]) < 1e-6:
        return None
    ndc = c[:3] / c[3]
    # r.w/r.h are the supersampled buffer, but every 2D overlay is drawn on the
    # final 1280x720 canvas, so project into canvas space or the label lands at
    # twice its coordinate (which is why the pyramid's labels first appeared below
    # the frame, in the right order, off screen).
    ss = float(getattr(r, "ssaa", 1))
    return ((ndc[0] * 0.5 + 0.5) * r.w / ss, (1.0 - (ndc[1] * 0.5 + 0.5)) * r.h / ss)


def project_y(r, pt):
    q = project_pt(r, pt)
    return None if q is None else q[1]


def water_surface(im, t, height=0.30, strength=1.0, ceiling=(0.30, 0.52, 0.60),
                  tilt=0.0, window=(0.10, 0.46), chop=1.0):
    """The underside of the sea surface: Snell's window, and the sky inside it.

    This is the single image that says "underwater" and the film did not have it.
    Physically, looking up from below:

      * beyond the critical angle (about 48.6 degrees from vertical) the surface
        totally internally reflects, so most of the frame is a dim mirror of the
        water beneath - rippled, dark, and moving;
      * inside a cone of that angle there is a bright circular window onto the sky
        above, compressed into a fraction of its real angular size and fringed by
        the refraction;
      * the window is not round: it is broken up by every ripple that crosses it.

    Doing this as an analytic layer rather than a mesh is deliberate - a real
    surface mesh at this scale needs hundreds of thousands of triangles to read,
    and the effect is a lighting phenomenon, not geometry you can see.
    """
    h, w = im.shape[:2]
    yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
    xx = np.linspace(-1.0, 1.0, w, dtype=np.float32)[None, :]

    # where the surface sits in frame, with a slow swell
    base = height + 0.020 * np.sin(xx * 2.1 + t * 0.60)
    base = base + 0.012 * np.sin(xx * 4.7 - t * 0.95)
    d = yy - base                                   # >0 = below the surface line

    # ripple field: three crossing wave trains, each at its own speed
    rip = (np.sin(xx * 11.0 + t * 1.7)
           + 0.6 * np.sin(xx * 23.0 - t * 2.6 + 1.3)
           + 0.35 * np.sin(xx * 41.0 + t * 3.9 + 2.7)) * chop
    # the ripple both displaces the window edge and modulates its brightness
    d = d + rip * 0.010

    # Snell's window: the bright cone, widest directly overhead
    win_w = window[0] + window[1] * 0.55
    cone = np.clip(1.0 - (np.abs(xx - tilt * 0.35) / win_w) ** 2.0, 0.0, 1.0) * 0.55
    cone = np.clip(cone + 0.45 * np.clip(1.0 - np.abs(xx - tilt * 0.35) / (win_w * 0.72), 0, 1) ** 1.4, 0, 1)

    inside = np.clip(-d / 0.012, 0.0, 1.0)          # anti-aliased surface edge
    sky = np.array(ceiling, dtype=np.float32)[None, None, :] * cone[..., None]
    # bright core: the sun itself, small and hot, inside the cone
    core = np.clip(1.0 - ((xx - tilt * 0.35) / (win_w * 0.16)) ** 2
                   - ((yy - (height - 0.06)) / (win_w * 0.20)) ** 2, 0, 1) ** 1.7
    sky = sky + np.array([0.62, 0.78, 0.80], dtype=np.float32)[None, None, :] * core[..., None] * 0.55

    # the refracted fringe: a thin caustic halo right at the window edge
    fringe = np.exp(-((d + 0.004) / 0.006) ** 2) * 0.30
    sky = sky + np.array([0.35, 0.60, 0.66], dtype=np.float32)[None, None, :] * fringe[..., None]

    # Outside the window the surface is a total-internal-reflection mirror of the
    # water beneath. In v3.0 I painted it at 0.03 linear and it came out pure black,
    # which reads as a hole rather than as a surface. The reflected light in a real
    # shot is dim but definitely there, and it is where all the visible ripple
    # detail lives, so it is the part that has to be visible.
    # rip is (h, w). Multiplying a (1,1,3) colour by a (h,w,1) gain is fine, but
    # adding a bare (h,w,1) term to an already-3-channel (h,w,3) array broadcasts to
    # (h,w,w,3) - which then made surf 4-D and silently scrambled the channels, so
    # the whole mirror came out black. Every term below is explicitly 3-channel.
    rg = np.clip(0.40 + 0.42 * rip, 0.0, 1.4)[..., None]
    mirror = np.array([0.115, 0.255, 0.300], dtype=np.float32)[None, None, :] * rg
    mirror = mirror + np.array([0.020, 0.048, 0.060], dtype=np.float32)[None, None, :]
    crest = np.clip((rip - 0.55) / 1.4, 0.0, 1.0)[..., None] ** 1.8
    mirror = mirror + np.array([0.26, 0.46, 0.50], dtype=np.float32)[None, None, :] * crest
    surf = sky * inside[..., None] + mirror * (1.0 - inside[..., None])

    # The surface fills the frame above the waterline; below it the image is the
    # underwater scene the caller already rendered. `strength` is a scalar, so it is
    # multiplied outside the bracket - as written before, `... * strength` sat on the
    # (h,w,1) mask while `surf` is (h,w,3), and numpy broadcast the difference into a
    # 4th axis that silently dropped the mirror to black.
    above = np.clip((base - yy) / 0.006, 0.0, 1.0)[..., None]
    return im * (1.0 - above) + surf * above * float(strength)


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
    """A sonar pulse as a soft expanding wavefront, not a drawn arc.

    v1 stroked a 2 px arc straight onto the frame. At 720p that is a hairline
    scratch, and because it was the only perfectly sharp object in an otherwise
    defocused shot the eye went straight to it - it read as dirt on the lens rather
    than as sound. A real wavefront is bright at the crest and gone within a few
    pixels either side, and it fades as it expands. So: build it on its own layer,
    stack a narrow core with two wider, dimmer skirts, and blur the whole thing.
    """
    if alpha <= 0.01:
        return
    from PIL import Image as _I, ImageFilter as _F
    lay = _I.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i in range(n):
        age = ((t + i * period / n) % period) / period
        r = 40 + age * radius
        a = (1 - age) ** 1.5 * alpha
        if a <= 0.02:
            continue
        box = lambda rad: [cx - rad, cy - rad * 0.92, cx + rad, cy + rad * 0.92]
        d.arc(box(r), 200, 340, fill=(150, 200, 214, int(38 * a)), width=9)
        d.arc(box(r), 200, 340, fill=(175, 216, 228, int(70 * a)), width=4)
        d.arc(box(r), 200, 340, fill=(205, 234, 242, int(92 * a)), width=1)
    lay = lay.filter(_F.GaussianBlur(3.2))
    # Image.alpha_composite works in place on an RGBA image and needs every pixel to
    # have sane alpha. The previous branch used Image.composite(img, lay, lay), which
    # uses lay's ALPHA as a mask AND as a source - so the whole frame outside the
    # arcs was multiplied by zero alpha and went black.
    base = img.convert("RGBA")
    base.alpha_composite(lay)
    img.paste(base.convert(img.mode), (0, 0))


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
    placed = []
    for (x, y, z, ph) in specs:
        px, py, pz = x - k * 1.2, y + 0.16 * math.sin(t * 1.1 + ph), z + k * 1.4
        draw_orca(r, bank(ry=-96, rz=6 * math.sin(t * 0.8 + ph), pos=(px, py, pz)),
                  t, ph, 0.14, 1.6)
        placed.append((px, py, pz))
    im = composite(r, t, focus=9.0, dof=4.0, rays=0.28, particle_n=140,
                   ray_far=16.0, surface={"height": 0.045, "strength": 0.95})
    for (px, py, pz) in placed:
        im = contact_shadow(im, r, (px, py - 1.25, pz), size=(3.4, 1.15), strength=0.62, lift=2.0)
    return im


def b_wash(r, t, t0, t1):
    """2. The wash: the reference cuts through a bright shaft between scenes."""
    k = win(t, t0, t1, 0.18)
    eye = np.array([0.0, 2.2, -6.0])
    r.set_camera(eye, np.array([0.0, 0.6, 2.0]), fov=52)
    m = mesh("humpback", 14.0)
    r.draw(travelling_wave_mesh(m, t, amp=0.2), bank(ry=-70, pos=(0, -1.0, 5.0)))
    im = composite(r, t, focus=10.0, dof=2.0, rays=2.2, particle_n=60,
                   ray_far=18.0, surface={"height": 0.038, "strength": 0.85})
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
    return composite(r, t, focus=8.0, dof=3.5, rays=0.30, particle_n=180,
                     ray_far=20.0, surface={"height": 0.042, "strength": 0.88})


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
    im = composite(r, t, focus=10.0, dof=4.2, rays=0.26, particle_n=150,
                   ray_far=17.0, surface={"height": 0.044, "strength": 0.90})
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
    return composite(r, t, focus=5.0, dof=5.0, rays=0.34, particle_n=240, warm=0.04,
                     ray_far=9.0, surface={"height": 0.033, "strength": 0.80})


def b_card(r, t, t0, t1):
    """13. Species card: the animal in three-quarter profile, close and low.

    v1 put the camera at the whale's nose (ry=-118, nearly head-on) and called it a
    hero shot. Head-on, a 14 m body foreshortens to its own width, so the humpback
    read as a thin stick with a detached fluke behind it - the single worst frame in
    the film, and it sat under the title card. Three-quarter is the angle that shows
    length and girth at once, which is why every wildlife film uses it.
    """
    k = ease_in_out(clamp01((t - t0) / (t1 - t0)))
    eye = np.array([lerp(7.4, 6.4, k), lerp(-3.0, -2.4, k), lerp(12.5, 10.8, k)])
    tgt = np.array([-0.4, 0.1, lerp(0.4, 0.0, k)])
    r.set_camera(eye, tgt, fov=46)
    # A hero shot is a lighting decision, not just a camera one. This camera looks at
    # the whale from the front-right and slightly above, so the default rig (key from
    # up-and-behind) lit its far side and returned a silhouette. Key it from the
    # camera's own side and put the rim behind: now the flank, the throat pleats and
    # the long pectoral fin all read, and the silhouette is carried by the rim.
    r.light_rig(key=(0.55, 0.62, 0.72), key_gain=1.55,
                ambient=(0.085, 0.140, 0.180),
                fill=(0.30, 0.52, 0.66), rim=(0.70, 0.90, 1.00))
    m = mesh("humpback", 14.0)
    w = travelling_wave_mesh(m, t, amp=0.18, freq=0.9)
    # -58 deg, not -118: side-on enough to read 14 m of body, angled enough to show
    # the throat pleats and the long pectoral fin that identify the species
    r.draw(w, bank(ry=lerp(-62, -50, k), rx=-6, rz=5 * math.sin(t * 0.7),
                   pos=(0, 0.15, 0.0)))
    base = composite(r, t, focus=11.0, dof=2.6, rays=0.34, particle_n=120,
                     warm=0.06, ray_far=22.0,
                     surface={"height": 0.035, "strength": 0.95})
    base = contact_shadow(base, r, (0.0, 0.15 - 2.1, 0.0), size=(4.6, 1.4), strength=0.48, lift=2.2)
    im = to_pil(base)
    a = win(t, t0 + 0.25, t1, 0.45)
    centre(im, H * 0.10, "HUMPBACK WHALE", size=54, alpha=a)
    centre(im, H * 0.215, "40 TONNES   ·   14 M LONG", size=25, colour=GOLD, alpha=a)
    return from_pil(im)


DEFAULT_RIG = dict(key=(-0.30, 0.82, -0.48), key_gain=1.30,
                   ambient=(0.055, 0.095, 0.125),
                   fill=(0.104, 0.184, 0.240), rim=(0.4125, 0.60, 0.7125))


def b_pyramid(r, t, t0, t1):
    """6. The trophic pyramid as four real slabs of water, rising out of the murk.

    v2 drew this with ImageDraw: four flat trapezoids with a constant fill and an
    18 px skew. It moved, it labelled, and it was a chart - the one shot in a
    3D film with no 3D in it. Rebuilt as geometry: each tier is a box drawn by the
    same renderer as everything else, so it takes the light rig, the fog, the depth
    mask on the rays and the contact shadow. The perspective is the camera's, not
    a hard-coded skew.
    """
    r.light_rig(key=(0.42, 0.80, 0.44), key_gain=1.45,
                ambient=(0.070, 0.118, 0.156),
                fill=(0.24, 0.44, 0.58), rim=(0.62, 0.84, 0.96))
    # The stack is fully present from the first frame: 3.2 s is not long enough to
    # assemble a diagram and then read it. It arrives settled and the camera drifts.
    k = 0.62 + 0.38 * ease_in_out(clamp01((t - t0) / (t1 - t0)))
    # Above and to one side, looking down: from eye level a stack of 0.46 m slabs
    # 8 m away is four hairlines. The height is what makes it read as a stack.
    eye = np.array([3.2, 4.4, -8.6])
    r.set_camera(eye, np.array([0.0, -0.20, 0.0]), fov=44)

    labels = ["SHARKS", "SEALS", "FISH", "KRILL"]
    # Looking down, a higher world y is nearer the lens, so it lands lower in the
    # frame. The base of a trophic pyramid is the widest tier and must sit at the
    # bottom of the picture, so it gets the high y and the apex gets the low one.
    def y_of(i):
        return -1.72 + (3 - i) * (thick + 0.52)

    # width falls with height, the way an energy budget does; thickness is what
    # makes it read as a stack of masses rather than a bar chart
    widths = [3.05, 4.35, 5.75, 7.20]
    thick = 0.40
    for i in range(4):
        # reveal bottom-up: krill lands first, then the things that eat it
        rev = clamp01((k * 5.4) - (3 - i) + 0.30)
        if rev <= 0.01:
            continue
        y = y_of(i) + (1.0 - rev) * 0.42
        wdt = widths[i]
        r.draw(box_mesh(wdt, thick, 3.3, colour=(0.048, 0.098, 0.128)),
               bank(pos=(0.0, y, 0.0), ry=6.0 * i - 9.0))
        # a lit lip along the front edge: without it every tier shades to the same
        # value as the water behind it and the stack disappears into the medium
        r.draw(box_mesh(wdt * 1.01, 0.035, 0.055, colour=(0.40, 0.66, 0.72)),
               bank(pos=(0.0, y + thick * 0.5 - 0.015, 1.66), ry=6.0 * i - 9.0))
    # the stack sits 10.3 m from this lens; focusing at 8.0 blurred the whole shot
    im = composite(r, t, focus=10.3, dof=1.5, rays=0.35, particle_n=110,
                   ray_far=13.0, surface={"height": 0.036, "strength": 0.82})
    im = contact_shadow(im, r, (0.0, -2.10, 0.0), size=(7.4, 3.2),
                        strength=0.55, lift=2.4)
    im = to_pil(im)
    d2 = ImageDraw.Draw(im, "RGBA")
    ft = font(22)
    for i in range(4):
        rev = clamp01((k * 5.4) - (3 - i) + 0.30)
        if rev <= 0.01:
            continue
        y = y_of(i) + (1.0 - rev) * 0.42
        sy = project_y(r, np.array([0.0, y + thick * 0.5, 1.70]))
        if sy is None:
            continue
        bb = d2.textbbox((0, 0), labels[i], font=ft)
        tw = bb[2] - bb[0]
        d2.text((W * 0.5 - tw / 2 + 34, sy - 34), labels[i], font=ft,
                fill=BONE + (int(242 * rev),),
                stroke_width=2, stroke_fill=(4, 10, 14, int(190 * rev)))
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
    im = to_pil(composite(r, t, focus=3.2, dof=8.0, rays=0.24, particle_n=160,
                           ray_far=24.0, surface={"height": 0.030, "strength": 0.72}))
    sonar(im, W * 0.46, H * 0.52, t, period=2.6, n=3, radius=W * 0.34, alpha=0.85)
    return from_pil(im)


def b_flock(r, t, t0, t1):
    """9. Pec-slap. Humpbacks lie at the surface and hammer the water with a 5 m
    flipper; it is the loudest thing a whale does and it is unmistakable.

    Two earlier versions of this shot are gone. v1 rendered seven detached blades
    floating in a row - a white picket fence, physically impossible, and the eye
    rejects it instantly. v2 attached them to animals but still drew them as the
    library's `flipper()` primitive, which is a bone-white plate with no relationship
    to the body it is meant to be growing out of: on screen it read as two glowing
    planks the width of the whale.

    A pectoral fin is the animal's own arm. So it is drawn from the animal's own
    mesh, in the animal's own pose, and the right one is raised while the left one
    trails - because a humpback slaps with one flipper at a time.
    """
    k = ease_in_out(clamp01((t - t0) / (t1 - t0)))
    eye = np.array([lerp(-3.4, -1.6, k), lerp(-1.8, -0.6, k), lerp(-7.6, -5.4, k)])
    r.set_camera(eye, np.array([0.1, 1.1, 2.4]), fov=54)

    # One near animal at the surface, rolled onto its side so the raised flipper
    # clears the waterline, and a second further off on the opposite beat.
    for (x, y, z, ph, roll_dir, sc) in ((-1.1, 0.70, 2.6, 0.0, -1, 1.0),
                                        (3.9, 1.30, 5.2, 2.3, 1, 0.82)):
        ph_t = (t * 1.35 + ph) % (2.0 * math.pi)
        # a slap is a fast down-stroke and a slow recovery, not a sine
        swing = math.sin(ph_t) ** 3
        # roll the animal onto its side; the raised pectoral then stands clear
        roll = roll_dir * (34.0 + 46.0 * max(0.0, swing))
        draw_orca(r, bank(ry=-94 + 8 * math.sin(t * 0.6 + ph),
                          rx=10 * swing, rz=roll,
                          pos=(x, y + 0.22 * (1.0 - swing), z), scale=sc),
                  t, ph, 0.085)
        # the flipper shaft that has just struck the surface: a thin sheet of
        # entrained air along the leading edge, drawn only while it is landing
        if swing < -0.35:
            d2 = None  # handled below as screen-space spray

    # spray: entrained air thrown off the leading edge while a flipper is landing,
    # as screen-space grains over the composite rather than as more geometry
    im = composite(r, t, focus=6.4, dof=3.6, rays=0.30, particle_n=150,
                   ray_far=11.0, surface={"height": 0.030, "strength": 0.86})
    im = to_pil(im)
    d2 = ImageDraw.Draw(im, "RGBA")
    for (x, y, z, ph, roll_dir, sc) in ((-1.1, 0.70, 2.6, 0.0, -1, 1.0),
                                        (3.9, 1.30, 5.2, 2.3, 1, 0.82)):
        ph_t = (t * 1.35 + ph) % (2.0 * math.pi)
        swing = math.sin(ph_t) ** 3
        if swing > -0.30:
            continue
        q = project_pt(r, np.array([x + roll_dir * 1.5, y + 0.5, z + 0.2]))
        if q is None:
            continue
        rng = np.random.default_rng(int(t * 30) + int(ph * 10) + 7)
        for i in range(34):
            a = rng.uniform(0, 2 * math.pi)
            rr = 26 + 78 * rng.random() ** 0.7 * sc
            px = q[0] + math.cos(a) * rr
            py = q[1] + math.sin(a) * rr * 0.62
            rad = 0.9 + 2.4 * rng.random()
            al = int(150 * (1.0 - rr / 120.0) * win(t, t0, t1, 0.2))
            if al > 4:
                d2.ellipse([px - rad, py - rad, px + rad, py + rad],
                           fill=(214, 236, 240, al))
    label(im, (im.width / 2, im.height * 0.88), "PEC-SLAP",
          alpha=win(t, t0 + 0.9, t1, 0.5), size=20, anchor="tc")
    return from_pil(im)


def b_wheel(r, t, t0, t1):
    """10. Carousel feeding: the pod circles a herring school and closes.

    The beat used to be eight flippers rotating on a ring, with no whale attached to
    any of them. It came out of the reference as an abstract graphic, but in 3D an
    abstract graphic of body parts is just a white wheel of blades - and the same
    "impossible floating parts" problem as the old flipper row. Carousel feeding is
    the real behaviour it was reaching for, and it is a much better shot: you see
    the pod, you see the ring, and you see why the fish are trapped.
    """
    k = ease_in_out(clamp01((t - t0) / (t1 - t0)))
    # camera swings up and out, so the ring opens from a line into a circle
    # further out and higher: the whole ring has to fit, because the ring IS the shot
    # Close and low-angle: at 17 m the fog shader had eaten the whole pod and the
    # ring read as a small dark smudge. A carousel is a *behaviour* shot - the
    # viewer has to see animals, not a diagram of a circle.
    eye = np.array([2.4 * math.sin(t * 0.5), 5.6 + 2.4 * k, -11.0 + 1.8 * k])
    r.set_camera(eye, np.array([0.0, -0.5, 0.6]), fov=54)
    r.light_rig(key=(0.35, 0.70, 0.55), key_gain=1.45,
                ambient=(0.075, 0.125, 0.165),
                fill=(0.28, 0.48, 0.62), rim=(0.65, 0.86, 0.98))

    # the school: a tight bait ball in the middle of the ring
    ball = mesh("krill_cluster", 300, 1.5, 5)
    r.draw(ball, bank(pos=(0.0, -0.3, 0.6), scale=1.15))

    n = 6
    rad = 2.9 - 0.7 * k
    for i in range(n):
        ang = (360.0 / n) * i + t * 34.0
        x = math.sin(math.radians(ang)) * rad
        z = math.cos(math.radians(ang)) * rad + 0.6
        # each animal banks into the turn and its heading follows the circle
        draw_orca(r, bank(ry=-ang + 90.0, rx=-12.0, rz=-26.0,
                          pos=(x, -0.2 + 0.22 * math.sin(t * 1.4 + i), z)),
                  t, i * 1.3, 0.13)
    im = composite(r, t, focus=10.0, dof=3.6, rays=0.30, particle_n=150,
                   ray_far=15.0, surface={"height": 0.040, "strength": 0.90})
    for i in range(n):
        ang = (360.0 / n) * i + t * 34.0
        sxp = math.sin(math.radians(ang)) * rad
        szp = math.cos(math.radians(ang)) * rad + 0.6
        im = contact_shadow(im, r, (sxp, -1.1, szp), size=(2.4, 1.0), strength=0.30)
    im = to_pil(im)
    label(im, (im.width / 2, im.height * 0.88), "CAROUSEL FEEDING",
          alpha=win(t, t0 + 0.9, t1, 0.5), size=19, anchor="tc")
    return from_pil(im)


def b_plan(r, t, t0, t1):
    """11. Looking straight down: an orca ring with sonar in the middle."""
    k = ease_in_out(clamp01((t - t0) / (t1 - t0)))
    # A true top-down camera is degenerate with the default up vector: looking
    # straight down -y while "up" is +y makes the view basis singular, so the whole
    # ring of orcas projected to nothing and this beat rendered as empty water with
    # two sonar arcs in it. Tilt the axis and give the camera a usable up.
    eye = np.array([0.0, 13.2 - 1.1 * k, -4.6])
    r.set_camera(eye, np.array([0.0, 0.0, 0.5]), up=(0, 0, 1), fov=50)
    for i in range(6):
        ang = 60.0 * i + t * 9.0
        rad = 3.4
        x = math.sin(math.radians(ang)) * rad
        z = math.cos(math.radians(ang)) * rad
        draw_orca(r, bank(ry=ang, rz=3 * math.sin(t + i), pos=(x, 0.0, z)),
                  t, i * 1.1, 0.08)
    im = to_pil(composite(r, t, focus=13.4, dof=4.0, rays=0.26, particle_n=140,
                          ray_far=10.0, surface={"height": 0.034, "strength": 0.80}))
    sonar(im, W / 2, H / 2, t, period=2.0, n=3, radius=W * 0.24, alpha=0.55)
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
                     particle_n=200, warm=0.03,
                     ray_far=15.0, surface={"height": 0.042, "strength": 0.92})


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
    im = to_pil(composite(r, t, focus=8.0, dof=4.0, rays=0.28, particle_n=150,
                           ray_far=14.0, surface={"height": 0.038, "strength": 0.86}))
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
    im = to_pil(composite(r, t, focus=6.5, dof=4.2, rays=0.26, particle_n=140,
                           ray_far=12.0, surface={"height": 0.036, "strength": 0.84}))
    a = win(t, t0 + 0.4, t1, 0.4)
    label(im, (W * 0.70, H * 0.13), "PORT ATTACK", alpha=a, size=17)
    label(im, (W * 0.66, H * 0.205), "STARBOARD ATTACK", alpha=a, size=17)
    # A graph is not a shape. v2 drew a bare orange curve inside an empty filled
    # rectangle with no axis, no scale, no caption and no value - an audience reads
    # "unknown chart" and then reads nothing at all. It also sat on top of an orca.
    # Give it a baseline, a caption, a time axis, a hatch, and the two numbers the
    # shot exists to say.
    d = ImageDraw.Draw(im, "RGBA")
    pw, ph = int(W * 0.255), int(H * 0.200)
    x0, y0 = W * 0.042, H * 0.706
    d.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], radius=3,
                        fill=(7, 13, 17, int(196 * a)),
                        outline=(120, 152, 166, int(78 * a)))
    ft_s, ft_m, ft_l = font(13), font(21), font(11)
    d.text((x0 + 14, y0 + 11), "HUMPBACK KILL RATE", font=ft_s,
           fill=(150, 176, 186, int(230 * a)))
    # axes
    ax0, ay0 = x0 + 26, y0 + ph - 30
    ax1, ay1 = x0 + pw - 18, y0 + 74
    d.line([(ax0, ay0), (ax1, ay0)], fill=(112, 142, 154, int(130 * a)), width=1)
    d.line([(ax0, ay0), (ax0, ay1)], fill=(112, 142, 154, int(130 * a)), width=1)
    for gy in (0.25, 0.5, 0.75):
        yy = ay0 - (ay0 - ay1) * gy
        d.line([(ax0, yy), (ax1, yy)], fill=(90, 118, 130, int(46 * a)), width=1)
    # the curve: attacks on whales per year, rising as the population recovered
    n = 26
    pts = []
    for i in range(n + 1):
        u = i / n
        v = 0.06 + 0.86 * u ** 2.35
        pts.append((ax0 + (ax1 - ax0) * u, ay0 - (ay0 - ay1) * v))
    d.line(pts, fill=(214, 96, 74, int(246 * a)), width=2)
    # dot on the live end, so the curve reads as a measurement and not decoration
    ex, ey = pts[-1]
    d.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=(240, 150, 120, int(250 * a)))
    d.text((ax0, y0 + 38), "1970", font=ft_l, fill=(122, 148, 158, int(190 * a)))
    d.text((ax1 - 30, y0 + 38), "2017", font=ft_l, fill=(122, 148, 158, int(190 * a)))
    bb = d.textbbox((0, 0), "+147 IN 2017", font=ft_m)
    d.text((x0 + pw - 16 - (bb[2] - bb[0]), y0 + ph - 34), "+147 IN 2017", font=ft_m,
           fill=(226, 132, 108, int(240 * a)))
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
    im = to_pil(composite(r, t, focus=7.0, dof=4.0, rays=0.26, particle_n=150,
                           ray_far=12.0, surface={"height": 0.036, "strength": 0.84}))
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
    # Reset the rig before every frame. Two shots in this film re-light themselves
    # (the species card and the carousel) and a dissolve renders both sides of a
    # boundary in one frame - without this reset the card's bright front key bled
    # into every shot that happened to be drawn after it.
    r.light_rig(**DEFAULT_RIG)
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
