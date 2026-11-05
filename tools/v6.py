#!/usr/bin/env python3
"""v6 -- the whole reference edit, filled with our own plates.

`tools/v5.py` built the first seven seconds; it proved the camera and the room. This file
keeps that machinery (imported, not copied) and does three things it could not:

  1. **every shot is sounded and staged, 0.000 s to 23.267 s** -- all thirteen, not five;
  2. **the reference's own graphic devices** are rebuilt from our plates: the tilted
     money-packet card behind the red room, the hands holding cash, the macro of the
     green packet, the "BILLION" ghost inside the word, the slow push in the room;
  3. **the parts that read as a sticker are fixed** -- cutout edges feather into the set,
     the portrait is lit into the room instead of pasted on it, and the room has a real
     light direction, a floor falloff and haze.

Everything is measured from the reference: the shot table in `analysis/v4-build/shots.json`,
the ink widths of the type, the greens of the fields. None of the reference's own frames or
assets are ever drawn -- only numbers.

    python3 tools/v6.py --spec spec/v5-02.json --out public/demo/v6-01.mp4
    python3 tools/v6.py --stills /tmp/v6 --from 3.2 --to 9.2
"""
import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v5 as base                                    # noqa: E402  the proven camera + room
from ffbin import ffmpeg                             # noqa: E402

W, H = base.W, base.H
CAM = base.CAM
GAIN = base.GAIN
rgb = base.rgb
glyph = base.glyph
draw_text = base.draw_text
draw_layer = base.draw_layer
place = base.place
place_px = base.place_px
plate_gradient = base.plate_gradient
plate_image = base.plate_image
plate_colour = base.plate_colour
plate_surface = base.plate_surface
feather_edges = base.feather_edges
warp_place = base.warp_place
vignette = base.vignette
grain = base.grain
ease = base.ease
lerp = base.lerp

GREEN = base.GREEN                                   # #7dbb0b, measured off the reference
INK_RED = base.INK_RED                               # #9d090a
GLASS = base.GLASS                                   # #efe7d6
A = "showreel/v4/assets/"

SPEC: dict = {}
T: dict[str, np.ndarray] = {}


# --------------------------------------------------------------------------- helpers
def lin(t: float, a: float, b: float) -> float:
    """0 before a, 1 after b, linear between -- the only timing primitive needed."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return min(1.0, max(0.0, (t - a) / (b - a)))


def pop(t: float, at: float, dur: float = 0.16, back: float = 1.9) -> float:
    """A scale a touch over 1 then settling: the way type lands in this kind of reel."""
    u = lin(t, at, at + dur)
    if u <= 0:
        return 0.0
    e = 1 + (back - 1) * math.exp(-6.0 * u) * math.sin(9.0 * u) * (1 - u * 0.4)
    return u * e


def despill(img: np.ndarray, erode: int = 2) -> np.ndarray:
    """Take the green screen's own colour off a cutout's edge.

    Our plates are keyed off a green screen, so the outermost few pixels of every cutout
    still carry green. Over a bright field that shows up as a teal fringe -- cheap, and the
    one thing that makes a clean plate read as a cutout. Erode the alpha edge by a couple of
    pixels and pull the remaining green toward neutral there.
    """
    out = img.copy()
    a = out[..., 3].astype(np.float32)
    k = np.ones((erode * 2 + 1, erode * 2 + 1), np.uint8)
    a = cv2.erode(a, k)
    a = cv2.GaussianBlur(a, (0, 0), erode * 0.7)
    b, g, r = out[..., 0].astype(np.float32), out[..., 1].astype(np.float32), out[..., 2].astype(np.float32)
    over = np.clip(g - np.maximum(r, b) * 1.02, 0, None)
    g = g - over * 0.75
    out[..., 1] = np.clip(g, 0, 255).astype(np.uint8)
    out[..., 3] = np.clip(a, 0, 255).astype(np.uint8)
    return out


def defog_front(img: np.ndarray) -> np.ndarray:
    """Remove the out-of-focus red smear our hero plate baked beside the head.

    The pair's front layer carries a soft red patch that was part of the original grade;
    over a rebuilt wall it reads as a drawing, which is exactly the artifact the brief
    calls a glitch. It is separable two ways at once: the patch is *smooth* (no detail at
    any scale the man has) and it is *red with almost no green* -- skin and leather both
    carry a lot of green, so a ratio test leaves the subject alone. Where both hold, the
    pixel is faded toward the wall instead of being cut, so no edge appears.
    """
    out = img.astype(np.float32)
    b, g, r = out[..., 0], out[..., 1], out[..., 2]
    grey = cv2.cvtColor(out[..., :3].astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
    detail = np.abs(cv2.GaussianBlur(grey, (0, 0), 2.0) - cv2.GaussianBlur(grey, (0, 0), 14.0))
    smooth = np.clip(1 - detail / 9.0, 0, 1)
    red = np.clip((r - np.maximum(b, g) * 1.25) / 70.0, 0, 1)
    m = cv2.GaussianBlur(smooth * red, (0, 0), 10.0).astype(np.float32) * 0.92
    wall = np.array([26, 10, 12], np.float32)
    out[..., :3] = out[..., :3] * (1 - m[..., None]) + wall * m[..., None]
    out[..., 3] = out[..., 3] * (1 - 0.62 * m)
    return np.clip(out, 0, 255).astype(np.uint8)


def fingers_only(img: np.ndarray, thr: float = 26.0) -> np.ndarray:
    """Keep only the hands and the cash in a cutout, by their own local contrast.

    The hands plate's front layer is mostly the red set; the hands and the notes are the
    only things in it with strong local detail and warm, desaturated colour. Cutting them
    out there -- instead of pasting the rectangle and fading its edges -- means the layer
    can be moved around the room freely without ever bringing its own background with it.
    """
    out = img.copy()
    bc = cv2.GaussianBlur(out[..., :3].astype(np.float32), (0, 0), 2.0)
    coarse = cv2.GaussianBlur(out[..., :3].astype(np.float32), (0, 0), 16.0)
    detail = np.linalg.norm(bc - coarse, axis=2)
    b, g, r = out[..., 0].astype(np.float32), out[..., 1].astype(np.float32), out[..., 2].astype(np.float32)
    warm = np.clip((np.minimum(g, b) - r * 0.55) / 26.0, 0, 1)      # skin and cash are warm
    m = np.clip((detail - thr) / 22.0, 0, 1) * 0.85 + warm * 0.55
    m = np.clip(m, 0, 1)
    m = cv2.morphologyEx((m * 255).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((13, 13), np.uint8))
    m = cv2.GaussianBlur(m.astype(np.float32) / 255.0, (0, 0), 4.0)
    out[..., 3] = (out[..., 3].astype(np.float32) * m).astype(np.uint8)
    return out


def oval_fade(img: np.ndarray, soft: float = 0.30) -> np.ndarray:
    """Fade a layer's alpha to nothing toward its own edges, on an ellipse.

    `feather_edges` ramps the *border* of the rectangle, which still leaves four straight
    sides of a rectangular cutout visible against a lit wall. An elliptical falloff has no
    straight side at all, so a layer of smoke, glass or hands can sit on a wall and read as
    something the light is doing to the wall rather than as a rectangle pasted over it.
    """
    out = img.copy()
    h, w = out.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx / w - 0.5) / 0.52) ** 2 + ((yy / h - 0.5) / 0.56) ** 2)
    m = np.clip((1.0 - d) / soft, 0, 1)
    m = cv2.GaussianBlur(m, (0, 0), min(w, h) * 0.06)
    out[..., 3] = (out[..., 3].astype(np.float32) * m).astype(np.uint8)
    return out


def drop_green_cells(img: np.ndarray) -> np.ndarray:
    """Take the key's own green markers out of a cutout.

    The hands plate was shot against a red set with green markers on it; the marker came
    through the cut as a solid green square. Nothing in the plate is that green, so a hard
    green test removes it without touching skin or cash.
    """
    out = img.copy()
    b, g, r = out[..., 0].astype(np.int32), out[..., 1].astype(np.int32), out[..., 2].astype(np.int32)
    m = ((g > 120) & (g > r * 1.6) & (g > b * 2.2)).astype(np.uint8)
    m = cv2.dilate(m, np.ones((9, 9), np.uint8))
    a = out[..., 3].astype(np.float32)
    a[cv2.GaussianBlur(m, (0, 0), 3) > 0.15] = 0
    out[..., 3] = a.astype(np.uint8)
    return out


def key_red(img: np.ndarray, thr: int = 74) -> np.ndarray:
    """Cut our plates' own deep-red background off a foreground.

    The hands plate is red-on-red: chroma alone cannot separate them, so the separation
    is by the *amount* of red -- the set is a flat dark red, the hands and the cash are
    brighter and browner, and the difference survives a small blur.
    """
    b, g, r = img[..., 0].astype(np.float32), img[..., 1].astype(np.float32), img[..., 2].astype(np.float32)
    m = ((r - (b + g) * 0.5) + (r - 60) * 0.35).astype(np.float32)
    m = cv2.GaussianBlur(m, (0, 0), 2.2)
    a = np.clip((m - thr) / 42.0, 0, 1)
    return np.dstack([img[..., :3], (a * 255).astype(np.uint8)])


def light_into(frame: np.ndarray, layer: np.ndarray, expr, t: float, k: float = 1.0) -> np.ndarray:
    """Put a plate back into the room that lit it.

    A cutout pasted on a field reads as a sticker because the field and the subject do not
    share a light: the reference's man is lit by the red wall behind him, so his shoulders
    pick up the wall's colour and his shadow side goes down to the wall's value. This adds
    the wall's hue as a rim and multiplies a soft falloff across the subject.
    """
    out = layer.astype(np.float32)
    ih, iw = out.shape[:2]
    yy, xx = np.mgrid[0:ih, 0:iw].astype(np.float32)
    rim = np.clip((xx / iw) * 0.55 + 0.18, 0, 1) ** 1.6
    a = (out[..., 3:4] / 255.0)
    tint = expr
    out[..., :3] = out[..., :3] * (0.94 + 0.06 * k) + tint * (rim[..., None] * 34 * k) * a[..., None]
    out[..., :3] *= (0.72 + 0.28 * a) * 1.0
    out[..., :3] = np.clip(out[..., :3], 0, 255)
    return out.astype(np.uint8)


# ------------------------------------------------------------------ field / fixtures
def green_field(deep: float = 1.0, glow: tuple[float, float] = (0.42, 0.30)) -> np.ndarray:
    """The reference's green: #7dbb0b where the light is, darker at the corners."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx / W - glow[0]) / 1.0) ** 2 + ((yy / H - glow[1]) / 0.9) ** 2)
    lit = np.clip(1.15 - d * 0.72, 0, 1.25)
    dark = rgb(46, 78, 8)
    mid = rgb(104, 154, 18)
    bright = rgb(146, 198, 40)
    f = dark + (mid - dark) * np.clip(lit, 0, 1)[..., None]
    f = f + (bright - mid) * np.clip(lit - 0.62, 0, 1)[..., None] * 1.6
    f *= (1 - 0.30 * np.clip((yy / H - 0.55) / 0.45, 0, 1) ** 1.4)[..., None]
    return np.clip(f * deep, 0, 255)


def wide_storm(scale: float = 0.82, dy: float = 0.0, high_key: float = 1.0,
               desat: float = 0.72) -> np.ndarray:
    """s4/s11's framing: a wide grey day, the stool small in the lower third.

    The plate is a medium shot; the reference's shot is a wide. Covering the frame with the
    medium shot (which is what `plate_image` does) is what made this read as a different
    shot, not a different grade: so the sky is rebuilt from the plate's own top and the
    stool is placed back into it at a fraction of the size, small and low.
    """
    pl = base.asset(A + "plate-bag-stool.png")[..., :3].astype(np.float32)
    sky = pl[: int(pl.shape[0] * 0.42)]
    sky = cv2.resize(sky, (W, int(H * 0.78)), interpolation=cv2.INTER_LANCZOS4)
    sky = cv2.GaussianBlur(sky, (0, 0), 6)
    field = np.zeros((H, W, 3), np.float32)
    field[: sky.shape[0]] = sky
    field[sky.shape[0]:] = sky[-1:, :, :]
    # the whole plate, smaller, bottom-anchored, feathered into the sky
    ph = int(pl.shape[0] * (W * scale) / pl.shape[1])
    sub = cv2.resize(pl, (int(W * scale), ph), interpolation=cv2.INTER_LANCZOS4)
    alpha = np.ones((ph, sub.shape[1]), np.float32)
    ramp = int(ph * 0.22)
    alpha[:ramp] = (np.linspace(0, 1, ramp) ** 1.3)[:, None]
    alpha = cv2.GaussianBlur(alpha, (0, 0), 9)
    x0 = (W - sub.shape[1]) // 2
    y0 = int(H - ph + dy * H)
    ys0, ys1 = max(0, y0), min(H, y0 + ph)
    xs0, xs1 = max(0, x0), min(W, x0 + sub.shape[1])
    a = alpha[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0][..., None]
    field[ys0:ys1, xs0:xs1] = sub[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0] * a + \
        field[ys0:ys1, xs0:xs1] * (1 - a)
    lum = field.mean(axis=2, keepdims=True)
    field = field * (1 - desat * 0.55) + lum * (desat * 0.55)
    field = np.clip(field * (1.05 + 0.13 * high_key) + 14 * high_key, 0, 255)
    return field


def money_ghost(word: str, light: int, dark: int) -> np.ndarray:
    """A word repeated in two tones so it reads as a wall of notes, as in the reference.

    The reference's green shots carry "BILLION" twice: once in the bright field colour as
    the headline, once a shade darker behind it, half hidden by the packet. That second
    copy is what makes the field look printed rather than empty.
    """
    g = glyph(word)
    a = g.astype(np.float32) / 255.0
    col = np.array([light, light, light], np.float32)
    out = np.zeros((g.shape[0], g.shape[1], 4), np.uint8)
    out[..., :3] = (col * a[..., None]).astype(np.uint8)
    out[..., 3] = (a * 255 * 0.55).astype(np.uint8)
    return out


def graphics_stack(t: float, u: float) -> None:
    """The red room's graphic furniture: the tilted money card, the ribbons, the cell.

    These are the shapes the reference keeps moving behind the man for six seconds -- a
    large tilted card with the packet's silhouette, a green cell, thin wire arcs. They are
    drawn at two depths so the camera slides them across him.
    """
    p = ease(u, "smooth")
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    red = rgb(176, 30, 30)
    # the tilted card: the packet's silhouette, blown up and laid on the wall
    card = np.zeros((H, W, 3), np.float32)
    quad = np.float32([[(0.02 + 0.05 * p) * W, (0.10 - 0.03 * p) * H],
                       [(0.74 + 0.05 * p) * W, (0.02 + 0.02 * p) * H],
                       [(0.80 + 0.03 * p) * W, (0.74 + 0.04 * p) * H],
                       [(0.06 + 0.02 * p) * W, (0.80 + 0.02 * p) * H]])
    cv2.fillConvexPoly(card, quad.astype(np.int32), (1.0, 1.0, 1.0), cv2.LINE_AA)
    card = cv2.GaussianBlur(card, (0, 0), 1.2)
    # ribbons: three thin bars laid across the card, the reference's graphic rhythm
    for i, off in enumerate((-0.10, 0.02, 0.14)):
        q = quad.copy()
        q[:, 1] += off * H + 0.04 * H * math.sin(t * 1.1 + i)
        cv2.fillConvexPoly(card, q.astype(np.int32), (0, 0, 0) if False else (0.16, 0.16, 0.16), cv2.LINE_AA)
    k, dx, dy = CAM.project(-430.0, 0.0, 0.0, 0.0)
    layer = red[None, None, :] * card
    # a soft shadow behind the card, then the card itself
    sh = cv2.GaussianBlur(card[..., 0], (0, 0), 18) * 0.55
    T["frame_shadow"] = sh.astype(np.float32)


# ------------------------------------------------------------------------ shots
def scene_s1(f, t, u):
    """0.000-0.533  TWENTY rises on the lit card. Ink measured at x132 y~600 w438."""
    f[:] = plate_surface(SPEC["plate_coef"], SPEC["plate_basis"]) * 1.02
    k = ease(u, "out")
    draw_text(f, "TWENTY", 132, lerp(648, 596, k), lerp(446, 438, k), GREEN,
              opacity=lin(t, 0.02, 0.16), blur=lerp(5.0, 0.0, k))
    vignette(f, 0.30)


def scene_s2(f, t, u):
    """0.533-0.800  the slam. REF: BILLION 392px at (211,544), TWENTY 199px at (71,553)."""
    f[:] = plate_gradient([(0.55, 0.5, 0.95, (32, 32, 32))], (10, 10, 10))
    k = ease(u, "out")
    sc = pop(t, 0.541, 0.17)
    draw_text(f, "BILLION", 211, lerp(566, 544, k), 392 * sc, GREEN, skew=0.02,
              blur=lerp(7.0, 0.0, k))
    draw_text(f, "TWENTY", 78, lerp(572, 553, k), 176, GREEN, opacity=0.96,
              blur=lerp(3.0, 0.0, k))
    vignette(f, 0.55)


def scene_s3(f, t, u):
    """0.800-1.333  the green field: the packet huge and cropped, BILLION over it.

    REF measures the headline at 650px wide inside the upper 42 % and the packet bleeding
    off the bottom and the left edge -- a macro, not a product shot.
    """
    f[:] = green_field(0.92, glow=(0.55, 0.22))
    k = ease(u, "out")
    # shadow the packet throws on the field, so it is standing in front of it
    sh = np.zeros((H, W, 4), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.clip(1 - (((xx - 0.36 * W) / (0.46 * W)) ** 2 + ((yy - 0.80 * H) / (0.22 * H)) ** 2), 0, 1) ** 1.3
    sh[..., 3] = (g * 90).astype(np.uint8)
    draw_layer(f, sh, 0, 0, W, opacity=0.75, h=H)
    draw_layer(f, T["bag"], lerp(4, -18, k), lerp(478, 446, k), lerp(600, 640, k),
               opacity=lin(t, 0.803, 0.86), blur=lerp(9.0, 0.0, k), rot=-7 + 4 * k)
    # the shallow rotated copy, the way the reference prints it twice
    draw_text(f, "BILLION", 34, lerp(300, 268, k), 214, rgb(24, 34, 6), opacity=0.85,
              rot=-58.0, blur=lerp(6.0, 0.0, k))
    draw_text(f, "BILLION", lerp(96, 70, k), lerp(198, 172, k), lerp(470, 528, k),
              rgb(20, 30, 4), opacity=lin(t, 0.806, 0.90), rot=-9.0, blur=lerp(10.0, 0.0, k))
    vignette(f, 0.26)


def scene_s4(f, t, u):
    """1.333-3.133  the packet on the stool in the storm; HE, then NO.

    REF: HE 78px at (126,237); NO 430px at (112,300) under it. The storm is high-key and
    the packet stays fully in frame -- this shot is the wide, the next one is the macro.
    """
    f[:] = wide_storm(scale=lerp(0.80, 0.86, ease(u, "smooth")), dy=lerp(0.03, -0.01, u))
    ka = ease(lin(t, 1.84, 2.04), "out")
    draw_text(f, "HE", 126, 236, 78 * lerp(1.10, 1.0, ka), INK_RED, opacity=ka,
              blur=lerp(5.0, 0.0, ka))
    a = ease(lin(t, 2.02, 2.18), "out")
    if a > 0:
        sc = lerp(1.35, 1.0, a)
        draw_text(f, "NO", 112 + (1 - sc) * 120, 300 + (1 - sc) * 70, 400 * sc, INK_RED,
                  opacity=a, rot=-2.0, blur=lerp(9.0, 0.0, a))
    vignette(f, 0.30)


def red_room(f, t, u, push: float, orbit_x: float, orbit_y: float, yaw: float, pitch: float,
             lit: float = 1.0, stack: bool = True, year: float = 0.30) -> None:
    """The room: wall light, the graphic stack at its own depth, the man, haze, the year."""
    orbit_x, orbit_y = orbit_x * GAIN[0], orbit_y * GAIN[0]
    yaw, pitch = yaw * GAIN[0], pitch * GAIN[0]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx / W - 0.24) / 0.95) ** 2 + ((yy / H - 0.12) / 0.80) ** 2)
    lit_ = np.clip(1 - d, 0, 1) ** 1.45
    dark, bright = rgb(20, 2, 4), rgb(122, 17, 18)
    wall = dark + (bright - dark) * lit_[..., None]
    wall *= (1 - 0.50 * np.clip((yy / H - 0.52) / 0.48, 0, 1) ** 1.3)[..., None]
    f[:] = np.clip(wall * 0.92, 0, 255)
    if stack:
        # the reference's graphic furniture: nested chevrons, a dark card, a green cell
        cv2_shapes(f, t, u, orbit_x, orbit_y)
    hero_only(f, s=base.COVER * 1.02 * push, orbit_x=orbit_x, orbit_y=orbit_y,
              yaw=yaw, pitch=pitch, lift=52 + math.sin(u * math.pi * 2.0) * 2.5)
    place_px(f, T["2008"], -300.0, 470 * push, orbit_x * 1.15 - 26, orbit_y * 1.15, 0.0,
             opacity=year, blur=0.8, anchor=(0.42, 0.045),
             yaw=yaw * 0.9 + 4.0, pitch=pitch * 0.9)


def cv2_shapes(f, t, u, ox, oy):
    """The reference's graphic furniture, kept to two marks: a tilted card and a chevron.

    Drawn as thin bright strokes at the wall's own depth, so they slide against the man by
    parallax. Two marks, not a cluster: the reference's wall reads as design, and a stack of
    nested boxes reads as a window.
    """
    p = ease(u, "smooth")
    k_, dx, dy = CAM.project(-460.0, ox, oy, 0.0)
    thick = max(1, int(round(1.6 * k_)))
    col = tuple(float(v) for v in rgb(186, 54, 50))
    # the tilted card: three strokes, like the corners of a card being laid down
    cw, ch = W * 0.62, H * 0.52
    cx = (0.02 + 0.05 * p) * W + dx * 0.6
    cy = (0.30 - 0.03 * p) * H + dy * 0.6
    tilt = np.float32([[1, 0, -cw / 2], [0, 1, -ch / 2], [0, 0, 1]])
    rot = cv2.getRotationMatrix2D((0, 0), -14 - 3 * p, 1.0)
    for i, (fw, fh) in enumerate(((1.0, 1.0), (0.72, 0.72))):
        o = (1 - fw) * cw * 0.5
        quad = np.float32([[0, 0], [cw * fw, 0], [cw * fw, ch * fh], [0, ch * fh]])
        quad -= np.float32([cw * fw / 2, ch * fh / 2])
        quad = cv2.transform(quad[None], rot)[0] + np.float32([cw / 2, ch / 2])
        quad += np.float32([cx, cy])
        cv2.polylines(f, [quad.astype(np.int32)], True, col, thick, cv2.LINE_AA)
    # a chevron half out of frame on the right, so the wall is asymmetric like the reference
    x = (0.78 - 0.04 * p) * W + dx * 0.9
    y = (0.16 + 0.03 * p) * H + dy * 0.9
    w2, h2 = W * 0.30, H * 0.34
    pts = np.array([[x, y], [x + w2, y + h2 * 0.42], [x, y + h2]], np.int32)
    cv2.polylines(f, [pts], False, col, thick + 1, cv2.LINE_AA)
    gx = (0.50 + 0.03 * math.sin(t * 0.9)) * W + dx * 1.2
    gy = (0.46 + 0.02 * math.cos(t * 0.7)) * H + dy * 1.2
    sx = max(8, 24 * k_)
    cell = np.zeros((int(sx * 2.2), int(sx * 2.2), 4), np.uint8)
    cv2.rectangle(cell, (int(sx * 0.35), int(sx * 0.35)), (int(sx * 1.85), int(sx * 1.85)),
                  (11, 187, 125, 235), -1, cv2.LINE_AA)
    draw_layer(f, cell, gx, gy, cell.shape[1], opacity=0.62)


def hero_only(f, s: float, orbit_x: float, orbit_y: float, yaw: float, pitch: float,
              lift: float = 0.0, halo: float = 1.0) -> None:
    """The man alone, registered by his authored offset, with the wall's light on him.

    The pair's back plate is not used in this build: the wall here is drawn, so drawing the
    plate's own wall on top of it would double every vignette and every edge (that banding
    is the last artifact this room had). What is kept is the part worth keeping -- the
    front layer at its exact authored offset, a warm bounce behind him and the contact
    shadow that puts him on the floor.
    """
    pr = base.PAIRS["hero"]
    _, dxb, dyb = CAM.project(-520.0, orbit_x, orbit_y, 0.0)
    _, dxf, dyf = CAM.project(620.0, orbit_x, orbit_y, 0.0)
    bx = (W - W * s) / 2 + dxb
    by = (H - base.PLATE_H * base.RATIO * s) / 2 + dyb
    ox_, oy_ = base.plate_to_frame(pr["off"][0], pr["off"][1])
    fx = bx + (ox_ - (W - W * s) / 2) + dxf - dxb
    fy = by + (oy_ - (H - base.PLATE_H * base.RATIO * s) / 2) + dyf - dyb + lift
    front = pr["front"]
    if halo > 0:
        # the wall's bounce: his own silhouette, blurred, tinted, behind him
        m = (front[..., 3].astype(np.float32) / 255.0)
        big = cv2.resize(m, (int(front.shape[1] * s), int(front.shape[0] * s)),
                         interpolation=cv2.INTER_LINEAR)
        halo_img = np.zeros((H, W, 3), np.float32)
        hh, ww = big.shape
        x0, y0 = int(round(fx)), int(round(fy))
        ys0, ys1 = max(0, y0), min(H, y0 + hh)
        xs0, xs1 = max(0, x0), min(W, x0 + ww)
        if ys1 > ys0 and xs1 > xs0:
            halo_img[ys0:ys1, xs0:xs1] = big[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0][..., None]
        halo_img = cv2.GaussianBlur(halo_img, (0, 0), 78)
        f[:] = np.clip(f + halo_img * rgb(150, 30, 28) * 0.16 * halo, 0, 255)
    # contact shadow on the floor
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ell = np.clip(1 - (((xx - W * 0.5) / (W * 0.42)) ** 2 +
                       ((yy - H * 0.985) / (H * 0.045)) ** 2), 0, 1) ** 1.2
    f[:] = f * (1 - 0.72 * ell[..., None])
    warp_place(f, front, s, fx, fy, 1.0, yaw, pitch)


def scene_s5(f, t, u):
    """3.133-9.167  the red room: 2008, the stack, the hands, a slow push."""
    p = ease(u, "smooth")
    red_room(f, t, u, push=1.0 + 0.09 * p,
             orbit_x=lerp(-46, 62, p), orbit_y=lerp(16, -24, p),
             yaw=lerp(-9.0, 7.0, p), pitch=lerp(2.5, -2.0, p), year=0.30)
    hp = ease(lin(t, 4.15, 5.05), "out")
    if hp > 0:
        place_px(f, T["hands"], 740.0, 520 * lerp(0.86, 1.0, hp), 420 - 90 * hp, 300 + 60 * hp,
                 0.0, opacity=hp * 0.97, blur=lerp(7.0, 0.0, hp), anchor=(0.5, 0.5),
                 yaw=lerp(-18, -7, hp), pitch=7.0)
    vignette(f, 0.42)


def scene_s6(f, t, u):
    """9.167-11.733  tighter, the lenses hot, the subscribe card."""
    p = ease(u, "smooth")
    red_room(f, t, u, push=1.12 + 0.07 * p,
             orbit_x=lerp(66, -34, p), orbit_y=lerp(-22, 26, p),
             yaw=lerp(8.0, -10.0, p), pitch=lerp(-2.2, 3.0, p), year=0.26)
    glow(f, T.get("lens"), t)
    a = ease(lin(t, 9.62, 9.94), "out")
    if a > 0:
        card_pill(f, 128, lerp(904, 846, a), a, "subscribe", "& like", 462)
    vignette(f, 0.44)


def glow(f, lens, t):
    """The red hit on the lenses: the one hot detail in a dark room."""
    if lens is None:
        return
    pulse = 0.74 + 0.26 * math.sin(t * 3.1)
    place_px(f, lens, 604.0, 208.0, 0.0, -4.0, 0.0, opacity=0.60 * pulse, blur=2.4,
             anchor=(0.5, 0.5))


def card_pill(f, x, y, a, line1, line2, w, face="Poppins-SemiBold.ttf"):
    """The reference's card: a frosted rectangle, two centred lines, drop shadow."""
    if a <= 0.01:
        return
    scale = lerp(0.90, 1.0, a)
    w = int(w * scale)
    h = int(w * 0.50)
    shadow = np.zeros((h + 28, w + 28, 4), np.uint8)
    cv2.rectangle(shadow, (14, 20), (w + 14, h + 20), (0, 0, 0, 120), -1, cv2.LINE_AA)
    shadow = cv2.GaussianBlur(shadow, (0, 0), 9)
    draw_layer(f, shadow, x - 14, y - 12, shadow.shape[1], opacity=a * 0.75)
    canvas = np.zeros((h, w, 4), np.uint8)
    cv2.rectangle(canvas, (0, 0), (w - 1, h - 1), (206, 214, 228, 255), -1, cv2.LINE_AA)
    canvas = cv2.GaussianBlur(canvas, (0, 0), 1.0)
    canvas[..., 3] = (canvas[..., 3] * min(1.0, a)).astype(np.uint8)
    draw_layer(f, canvas, x, y, w, opacity=a * 0.80)
    draw_text(f, line1, x + w * 0.13, y + h * 0.12, w * 0.74, (34, 32, 30), opacity=a, face=face)
    draw_text(f, line2, x + w * 0.31, y + h * 0.52, w * 0.38, (34, 32, 30), opacity=a * 0.94,
              face=face)


def scene_s7(f, t, u):
    """11.733-12.200  the loop head: TWENTY again, fast, brighter."""
    f[:] = plate_surface(SPEC["plate_coef"], SPEC["plate_basis"]) * 1.07
    k = ease(u, "out")
    sc = pop(t, 11.742, 0.15)
    draw_text(f, "TWENTY", 132, lerp(660, 592, k), 438 * sc, GREEN,
              opacity=lin(t, 11.735, 11.80), blur=lerp(8.0, 0.0, k))
    vignette(f, 0.28)


def scene_s8(f, t, u):
    """12.200-12.500  BILLION alone on black, skewed."""
    f[:] = plate_gradient([(0.5, 0.5, 0.9, (26, 26, 26))], (9, 9, 9))
    k = ease(u, "out")
    sc = pop(t, 12.20, 0.13)
    draw_text(f, "BILLION", 118, 556, 470 * sc, GREEN, skew=0.03, rot=-2.0,
              blur=lerp(6.0, 0.0, k))
    vignette(f, 0.50)


def scene_s9(f, t, u):
    """12.500-12.700  the macro: the packet's leather fills the frame."""
    f[:] = green_field(0.85, glow=(0.5, 0.40))
    k = ease(u, "out")
    place(f, T["macro"], 0.0, 0.0, 0.0, 0.0, cover=lerp(1.34, 1.18, k), opacity=0.98,
          anchor=(0.46, 0.56), blur=lerp(5.0, 0.0, k))
    f[:] = np.clip(f * 0.90, 0, 255)
    vignette(f, 0.34)


def scene_s10(f, t, u):
    """12.700-13.000  the packet close on green, BILLION above and a ghost behind it."""
    f[:] = green_field(0.90, glow=(0.55, 0.26))
    k = ease(u, "out")
    place(f, T["macro"], 0.0, 0.0, 0.0, 0.0, cover=lerp(1.46, 1.30, k), opacity=0.96,
          anchor=(0.56, 0.66), blur=lerp(4.0, 0.0, k))
    draw_layer(f, T["bag"], 106, lerp(452, 424, k), lerp(560, 604, k), opacity=0.95,
               blur=lerp(3.0, 0.0, k), rot=-4.0)
    draw_layer(f, T["ghost"], 96, 200, 470, opacity=0.26, rot=-4.0)
    draw_text(f, "BILLION", 96, 196, 500, rgb(22, 30, 4), opacity=1.0, rot=-4.0,
              blur=lerp(3.0, 0.0, k))
    vignette(f, 0.30)


def scene_s11(f, t, u):
    """13.000-14.833  the stool; HE, HE SAID, then NO over everything."""
    f[:] = wide_storm(scale=lerp(0.82, 0.88, ease(u, "smooth")), dy=lerp(0.01, -0.02, u),
                      high_key=lerp(0.6, 1.0, lin(t, 13.10, 13.70)))
    kh = ease(lin(t, 13.10, 13.30), "out")
    draw_text(f, "HE", 126, 236, 78 * lerp(1.10, 1.0, kh), INK_RED, opacity=kh,
              blur=lerp(5.0, 0.0, kh))
    ks = ease(lin(t, 13.42, 13.62), "out")
    draw_text(f, "SAID", 216, 250, 150 * lerp(1.08, 1.0, ks), INK_RED, opacity=ks,
              blur=lerp(5.0, 0.0, ks))
    a = ease(lin(t, 13.70, 13.94), "out")
    if a > 0:
        sc = lerp(1.32, 1.0, a)
        draw_text(f, "NO", 96 + (1 - sc) * 120, 298 + (1 - sc) * 70, 452 * sc, INK_RED,
                  opacity=min(1.0, a * 1.3), rot=-2.0, blur=lerp(7.0, 0.0, a))
    vignette(f, 0.34)


def scene_s12(f, t, u):
    """14.833-20.633  the room again, longer: 2008, the stack, the hands, the push."""
    p = ease(u, "smooth")
    red_room(f, t, u, push=1.04 + 0.10 * p,
             orbit_x=lerp(-40, 52, p), orbit_y=lerp(20, -26, p),
             yaw=lerp(-8.0, 6.0, p), pitch=lerp(2.2, -1.8, p), year=0.32)
    hp = ease(lin(t, 15.90, 16.90), "out")
    if hp > 0:
        place_px(f, T["hands"], 760.0, 480, 450 + 60 * (1 - hp), 300 - 30 * hp, 0.0,
                 opacity=hp * 0.94, blur=lerp(8.0, 0.0, hp), yaw=lerp(16, 4, hp), pitch=-5.0)
    hp2 = ease(lin(t, 18.40, 19.20), "out")
    if hp2 > 0:
        place_px(f, T["hands"], 900.0, 330, 240 - 30 * hp2, 660, 0.0, opacity=hp2 * 0.55,
                 blur=lerp(7.0, 1.0, hp2), yaw=-10.0, pitch=4.0)
    vignette(f, 0.44)


def scene_s13(f, t, u):
    """20.633-23.267  the CTA: the flash, the card, the year, the room holding."""
    p = ease(u, "out")
    red_room(f, t, u, push=lerp(1.18, 1.02, p),
             orbit_x=lerp(-34, 26, p), orbit_y=lerp(-18, 12, p),
             yaw=lerp(-7.0, 4.5, p), pitch=lerp(2.0, -1.4, p), year=0.30)
    glow(f, T.get("lens"), t)
    if 20.700 <= t < 20.767:                       # the reference's one-frame flash
        f[:] = np.minimum(f * 1.9 + 76, 255)
    hp = ease(lin(t, 21.20, 22.10), "out")
    if hp > 0:
        place_px(f, T["hands"], 700.0, 300, 190, 380, 0.0, opacity=hp * 0.5,
                 blur=lerp(8.0, 2.0, hp), yaw=-14.0, pitch=5.0)
    a = ease(lin(t, 21.02, 21.50), "out")
    if a > 0:
        card_pill(f, 150, lerp(930, 872, a), a, "SUBSCRIBE", "LIKE", 430)
    vignette(f, 0.48)


# ------------------------------------------------------------------------- render
def prepare(spec: dict) -> None:
    global SPEC
    SPEC = spec
    base.S = spec
    base.prepare(spec)                    # bag, stool, portrait, 2008 -- proven in v5
    base.load_pairs()
    base.PAIRS["hero"]["front"] = defog_front(base.PAIRS["hero"]["front"])
    bag = despill(base.cut(base.asset(A + "layers/plate-bag-green-front.png")))
    T["bag"] = bag
    T["bagmask"] = cv2.GaussianBlur((bag[..., 3] > 40).astype(np.float32), (0, 0), 3)
    T["stool"] = base.TSTOOL
    T["hero"] = base.THERO
    T["2008"] = base.T2008
    T["ghost"] = money_ghost("BILLION", 226, 226)
    # the macro: our own green packet, zoomed, as its own plate
    T["macro"] = base.cut(base.asset(A + "plate-macro-green.png"))
    # the hands: cut out of our own red plate by its red content
    hands = cv2.imread(A + "layers/plate-hands-red-front.png", cv2.IMREAD_UNCHANGED)
    half = cv2.resize(hands, (hands.shape[1] // 2, hands.shape[0] // 2),
                      interpolation=cv2.INTER_AREA)
    # the hands are kept as an object, not as a full-frame plate: only the cash and the
    # fingers are cut out (their own local contrast against the red), the rest is dropped,
    # so nothing of the plate's background can ever show as a rectangle on the wall
    T["hands"] = oval_fade(fingers_only(despill(drop_green_cells(half), erode=5)), soft=0.55)
    T["lens"] = make_lens()


def make_lens():
    """The red hit on the glasses, built as a glow, not pasted as a picture.

    The man's lenses are the only specular thing in the room; the reference lets them
    carry a hot red. A soft elliptical bloom with a small hot core does that without
    needing the lens shape, which would have to be tracked by hand.
    """
    w, h = 240, 92
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    for cx, sx in ((0.29, 0.22), (0.71, 0.22)):
        d = np.sqrt(((xx / w - cx) / sx) ** 2 + ((yy / h - 0.5) / 0.42) ** 2)
        pass
    d1 = np.sqrt(((xx / w - 0.30) / 0.20) ** 2 + ((yy / h - 0.52) / 0.34) ** 2)
    d2 = np.sqrt(((xx / w - 0.70) / 0.20) ** 2 + ((yy / h - 0.52) / 0.34) ** 2)
    g = np.clip(1 - np.minimum(d1, d2), 0, 1) ** 1.5
    core = np.clip(1 - np.minimum(d1, d2) * 2.2, 0, 1) ** 2.0
    out = np.zeros((h, w, 4), np.uint8)
    out[..., 2] = np.clip(150 * g + 105 * core, 0, 255)      # BGR: red
    out[..., 1] = np.clip(26 * g + 30 * core, 0, 255)
    out[..., 3] = np.clip(255 * (g * 0.85 + core * 0.55), 0, 255)
    return out


def render_frame(i: int, spec: dict) -> np.ndarray:
    fps = spec["fps"]
    t = i / fps
    shot = next((s for s in spec["shots"] if s["start"] <= t < s["end"]), spec["shots"][-1])
    u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
    f = np.zeros((H, W, 3), np.float32)
    globals()[f"scene_{shot['fn']}"](f, t, u)
    if shot.get("grain", 1.2) > 0:
        grain(f, shot["grain"], i * 7919 + 13)
    d = shot.get("dissolve_in", 0)
    if d > 0:
        k = ease(min(1.0, (t - shot["start"]) / d), "smooth")
        prev = render_frame(max(0, int(round(shot["start"] * fps)) - 1), spec).astype(np.float32)
        f = prev * (1 - k) + f * k
    return np.clip(f, 0, 255).astype(np.uint8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default="spec/v5-02.json")
    ap.add_argument("--out", default="public/demo/v6-01.mp4")
    ap.add_argument("--crf", default="16")
    ap.add_argument("--from", dest="start", type=float, default=0.0)
    ap.add_argument("--to", dest="stop", type=float, default=None)
    ap.add_argument("--stills", default=None)
    ap.add_argument("--gain", type=float, default=1.0)
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text())
    GAIN[0] = a.gain
    t0 = time.time()
    prepare(spec)
    base.colour_selftest()
    print(f"  prepare {time.time() - t0:.2f}s   macro {T['macro'].shape[1]}x{T['macro'].shape[0]}"
          f"  hands {T['hands'].shape[1]}x{T['hands'].shape[0]}")
    fps = spec["fps"]
    stop = spec["duration"] if a.stop is None else a.stop
    frames = [i for i in range(int(round(spec["duration"] * fps))) if a.start <= i / fps < stop]
    if a.stills:
        Path(a.stills).mkdir(parents=True, exist_ok=True)
        for i in frames:
            cv2.imwrite(f"{a.stills}/f{i:04d}.png", render_frame(i, spec))
        print(f"  {len(frames)} stills -> {a.stills}  ({time.time() - t0:.1f}s)")
        return 0
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    enc = subprocess.Popen([ffmpeg(), "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                            "-c:v", "libx264", "-crf", a.crf, "-preset", "medium",
                            "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out],
                           stdin=subprocess.PIPE)
    for i in frames:
        enc.stdin.write(render_frame(i, spec).tobytes())
    enc.stdin.close()
    enc.wait()
    dt = time.time() - t0
    print(f"  {len(frames)} frames in {dt:.1f}s ({len(frames) / dt:.2f} fps) -> {a.out} "
          f"({Path(a.out).stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
