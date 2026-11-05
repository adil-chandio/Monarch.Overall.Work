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
    # only in the band the patch lives in: his jacket's red-lit edge is smooth red too, and
    # it is part of the lighting, so the mask stops above the shoulder line
    hh = out.shape[0]
    band = np.clip((0.46 - np.linspace(0, 1, hh)) / 0.10, 0, 1)[:, None]
    m = m * band
    out[..., 3] = out[..., 3] * (1 - 0.96 * m)
    return np.clip(out, 0, 255).astype(np.uint8)


def cash_only(img: np.ndarray) -> np.ndarray:
    """Keep only the banknotes in the hands plate: the object, not the hands.

    The reference cuts to hands holding cash; our plate has the same gesture, but the layer
    it lives in is a full red frame whose edges can never be hidden on a lit wall. The notes
    are the part that reads at speed, and they are separable by their own colour -- warm,
    desaturated, much greener than the red set -- with a hard test that no red passes.
    """
    out = img.copy()
    f = out[..., :3].astype(np.float32)
    b, g, r = f[..., 0], f[..., 1], f[..., 2]
    luma = 0.114 * b + 0.587 * g + 0.299 * r
    m = ((luma > 68) & (g > r * 0.56) & (b > r * 0.34)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros_like(m)
    for k in range(1, n):
        x, y, w, h, area = st[k]
        if area > 2600 and w > 40 and h > 26 and w / max(h, 1) > 1.05:
            keep[lab == k] = 1
    keep = cv2.dilate(keep, np.ones((5, 5), np.uint8))
    a = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 2.2)
    out[..., 3] = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    # the notes' own brightness: no red tint left on them
    out[..., :3] = np.clip(f * 1.06 + 6, 0, 255).astype(np.uint8)
    return out


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


def wide_storm(scale: float = 0.92, dy: float = 0.0, high_key: float = 1.0,
               desat: float = 0.72) -> np.ndarray:
    """s4/s11's framing: a wide grey day, the stool small and low in the frame.

    The plate is a medium shot; the reference's shot is a wide. Covering the frame with the
    medium shot (which is what `plate_image` does) is what made this read as a different
    shot, not a different grade: so the sky is rebuilt from the plate's own top and the
    stool is placed back into it at a fraction of the size, small and low -- then feathered
    on **all four sides** so the plate's rectangle never shows as a seam.
    """
    pl = base.asset(A + "plate-bag-stool.png")[..., :3].astype(np.float32)
    sky = pl[: int(pl.shape[0] * 0.42)]
    sky = cv2.resize(sky, (W, int(H * 0.80)), interpolation=cv2.INTER_LANCZOS4)
    sky = cv2.GaussianBlur(sky, (0, 0), 6)
    field = np.empty((H, W, 3), np.float32)
    field[: sky.shape[0]] = sky
    field[sky.shape[0]:] = sky[-1:, :, :]
    # the plate, smaller, bottom-anchored, and the rest of the frame *replicated from its own
    # edge* -- not from a different image -- so there is no line to see where the plate ends
    ph = int(pl.shape[0] * (W * scale) / pl.shape[1])
    pw = int(W * scale)
    sub = cv2.resize(pl, (pw, ph), interpolation=cv2.INTER_LANCZOS4)
    x0 = (W - pw) // 2
    y0 = int(H - ph + dy * H)
    big = cv2.copyMakeBorder(sub, H, H, W, W, cv2.BORDER_REFLECT_101)
    field = big[H - y0:H - y0 + H, W - x0:W - x0 + W].copy()
    # a couple of pixels of blur only where the replication bands are, so the join is soft
    soft = cv2.GaussianBlur(field, (0, 0), 3)
    m = np.zeros((H, W), np.float32)
    m[max(0, y0 + 2):min(H, y0 + ph - 2), max(0, x0 + 2):min(W, x0 + pw - 2)] = 1.0
    m = cv2.GaussianBlur(m, (0, 0), 6)[..., None]
    field = field * m + soft * (1 - m)
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
    sc = pop(t, 0.500, 0.12)
    draw_text(f, "TWENTY", 34, lerp(566, 546, k), 176, GREEN, opacity=0.96)
    draw_text(f, "BILLION", 226, lerp(560, 538, k), 400 * sc, GREEN, skew=0.02,
              blur=lerp(7.0, 0.0, k))
    vignette(f, 0.55)


def scene_s3(f, t, u):
    """0.800-1.333  the green field: the packet large and cropped, one headline.

    The reference prints the word twice, but its second copy is *behind* the packet and a
    shade darker, never a lime ghost crossing the headline. Two copies at the same size and
    opacity read as a glitch, so this shot carries one headline, set inside the frame.
    """
    f[:] = green_field(0.92, glow=(0.55, 0.22))
    k = ease(u, "out")
    sh = np.zeros((H, W, 4), np.uint8)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.clip(1 - (((xx - 0.40 * W) / (0.46 * W)) ** 2 + ((yy - 0.82 * H) / (0.22 * H)) ** 2), 0, 1) ** 1.3
    sh[..., 3] = (g * 90).astype(np.uint8)
    draw_layer(f, sh, 0, 0, W, opacity=0.75, h=H)
    draw_layer(f, T["bag"], lerp(60, 34, k), lerp(500, 470, k), lerp(566, 600, k),
               opacity=lin(t, 0.833, 0.90), blur=lerp(8.0, 0.0, k), rot=-6 + 3 * k)
    draw_text(f, "BILLION", lerp(84, 62, k), lerp(206, 180, k), lerp(452, 500, k),
              rgb(20, 30, 4), opacity=lin(t, 0.833, 0.93), rot=-8.0, blur=lerp(10.0, 0.0, k))
    vignette(f, 0.26)


def scene_s4(f, t, u):
    """1.333-3.133  the packet on the stool in the storm; HE, then NO.

    REF: HE 78px at (126,237); NO 430px at (112,300) under it. The storm is high-key and
    the packet stays fully in frame -- this shot is the wide, the next one is the macro.
    """
    f[:] = wide_storm(scale=lerp(0.92, 0.95, ease(u, "smooth")), dy=lerp(0.02, -0.01, u))
    ka = ease(lin(t, 2.10, 2.20), "out")
    draw_text(f, "HE", 126, 236, 78 * lerp(1.08, 1.0, ka), INK_RED, opacity=min(1.0, ka * 2.2),
              blur=lerp(3.0, 0.0, ka))
    a = ease(lin(t, 2.55, 2.70), "out")
    if a > 0:
        sc = lerp(1.28, 1.0, a)
        draw_text(f, "NO", 112 + (1 - sc) * 120, 302 + (1 - sc) * 70, 400 * sc, INK_RED,
                  opacity=min(1.0, a * 2.0), rot=-2.0, blur=lerp(5.0, 0.0, a))
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
              yaw=yaw, pitch=pitch, lift=52 + math.sin(u * math.pi * 2.0) * 2.5, halo=0.0)
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
             orbit_x=lerp(-20, 20, p), orbit_y=lerp(8, -8, p),
             yaw=lerp(-3.0, 3.0, p), pitch=lerp(1.0, -1.0, p), year=0.30)
    # No floating hands/cash cutout: keep the compositing clean.
    vignette(f, 0.42)


def scene_s6(f, t, u):
    """9.167-11.733  tighter, the lenses hot, the subscribe card."""
    p = ease(u, "smooth")
    red_room(f, t, u, push=1.12 + 0.07 * p,
             orbit_x=lerp(20, -12, p), orbit_y=lerp(-8, 8, p),
             yaw=lerp(3.0, -3.0, p), pitch=lerp(-1.0, 1.0, p), year=0.26)
    glow(f, T.get("lens"), t)
    a = ease(lin(t, 9.62, 9.94), "out")
    if a > 0:
        card_pill(f, 226, lerp(964, 906, a), a, "subscribe", "& like", 274)
    vignette(f, 0.44)


def glow(f, lens, t):
    """The red hit on the lenses: the one hot detail in a dark room."""
    if lens is None:
        return
    pulse = 0.74 + 0.26 * math.sin(t * 3.1)
    place_px(f, lens, 604.0, 208.0, 0.0, -4.0, 0.0, opacity=0.60 * pulse, blur=2.4,
             anchor=(0.5, 0.5))


def card_pill(f, x, y, a, line1, line2, w, face="Poppins-SemiBold.ttf"):
    """Translucent rounded glass, composited from the current frame, away from the face."""
    if a <= 0.01:
        return
    w = int(w * lerp(0.94, 1.0, a)); h = int(w * 0.56)
    x, y = int(x), int(y)
    if x < 0 or y < 0 or x + w > W or y + h > H:
        return
    r = max(5, int(h * .18))
    mask = np.zeros((h, w), np.uint8)
    cv2.rectangle(mask, (r, 0), (w-r-1, h-1), 255, -1)
    cv2.rectangle(mask, (0, r), (w-1, h-r-1), 255, -1)
    for cx in (r, w-r-1):
        for cy in (r, h-r-1):
            cv2.circle(mask, (cx, cy), r, 255, -1, cv2.LINE_AA)
    roi = f[y:y+h, x:x+w]
    blurred = cv2.GaussianBlur(roi, (0, 0), 8)
    glass = blurred * .42 + np.array([215, 220, 229], np.float32) * .58
    blend = (mask.astype(np.float32) / 255 * a * .82)[..., None]
    roi[:] = roi * (1-blend) + glass * blend
    edge = cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
    m = (edge.astype(np.float32) / 255 * a * .42)[..., None]
    roi[:] = roi * (1-m) + 245 * m
    draw_text(f, line1, x + w * 0.14, y + h * 0.14, w * 0.72, (40, 38, 36), opacity=a * 0.95, face=face)
    draw_text(f, line2, x + w * 0.32, y + h * 0.54, w * 0.36, (40, 38, 36), opacity=a * 0.90, face=face)


def scene_s7(f, t, u):
    """11.733-12.200  the loop head: TWENTY again, fast, brighter."""
    f[:] = plate_surface(SPEC["plate_coef"], SPEC["plate_basis"]) * 1.07
    k = ease(u, "out")
    sc = pop(t, 11.667, 0.15)
    draw_text(f, "TWENTY", 132, lerp(660, 592, k), 438 * sc, GREEN,
              opacity=lin(t, 11.667, 11.76), blur=lerp(8.0, 0.0, k))
    vignette(f, 0.28)


def scene_s8(f, t, u):
    """12.200-12.500  BILLION alone on black, skewed."""
    f[:] = plate_gradient([(0.5, 0.5, 0.9, (26, 26, 26))], (9, 9, 9))
    k = ease(u, "out")
    sc = pop(t, 12.00, 0.13)
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
    """Replay the green field and original bag, not the unrelated macro plate."""
    scene_s3(f, 0.90 + 0.40 * u, u)


def scene_s11(f, t, u):
    """13.000-14.833  the stool; HE, HE SAID, then NO over everything."""
    f[:] = wide_storm(scale=lerp(0.93, 0.96, ease(u, "smooth")), dy=lerp(0.01, -0.02, u),
                      high_key=lerp(0.6, 1.0, lin(t, 13.10, 13.70)))
    kh = ease(lin(t, 13.73, 13.83), "out")
    draw_text(f, "HE", 126, 236, 78 * lerp(1.08, 1.0, kh), INK_RED, opacity=min(1.0, kh * 2.2),
              blur=lerp(3.0, 0.0, kh))
    ks = ease(lin(t, 13.88, 14.00), "out")
    draw_text(f, "SAID", 216, 250, 150 * lerp(1.06, 1.0, ks), INK_RED, opacity=min(1.0, ks * 2.2),
              blur=lerp(3.0, 0.0, ks))
    a = ease(lin(t, 14.00, 14.14), "out")
    if a > 0:
        sc = lerp(1.26, 1.0, a)
        draw_text(f, "NO", 96 + (1 - sc) * 120, 300 + (1 - sc) * 70, 452 * sc, INK_RED,
                  opacity=min(1.0, a * 2.0), rot=-2.0, blur=lerp(5.0, 0.0, a))
    vignette(f, 0.34)


def scene_s12(f, t, u):
    """14.833-20.633  the room again, longer: 2008, the stack, the hands, the push."""
    p = ease(u, "smooth")
    red_room(f, t, u, push=1.04 + 0.10 * p,
             orbit_x=lerp(-18, 20, p), orbit_y=lerp(8, -8, p),
             yaw=lerp(-3.0, 3.0, p), pitch=lerp(1.0, -1.0, p), year=0.32)
    # No suitable phone/hand plate: do not introduce a floating cutout over the room.
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
    a = ease(lin(t, 21.02, 21.50), "out")
    if a > 0:
        card_pill(f, 232, lerp(966, 906, a), a, "subscribe", "& like", 268)
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
    hands_cut = oval_fade(fingers_only(despill(drop_green_cells(half), erode=6)), soft=0.62)
    # graded down and desaturated: the hands become a dark detail in the room's foreground,
    # which is how the reference uses them, instead of a lit patch on a red wall
    _f = hands_cut[..., :3].astype(np.float32) * 0.62
    _lum = _f.mean(axis=2, keepdims=True)
    _f = _f * 0.55 + _lum * 0.45
    hands_cut[..., :3] = np.clip(_f, 0, 255).astype(np.uint8)
    T["hands"] = hands_cut
    T["cash"] = cash_only(cv2.resize(hands, (int(hands.shape[1] * 0.62), int(hands.shape[0] * 0.62)),
                                     interpolation=cv2.INTER_AREA))
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


# ---------------------------------------------------------------- camera
# AE's "camera on a large layer": render zoomed (z >= 1) and crop a 720x1280 window
# around the shot's look point. A crop never exposes edges, costs one resize + slice,
# and stays fast on a 2-core box (warpAffine collapses to ~15 s/frame under load).
#
# Each shot gets: look point, push (z0 -> z1), handheld jitter (px), crash-zoom
# punches (t, strength) that spike and decay, and an optional white flash window.
# The red-room shots keep their authored orbit/parallax, so the camera only adds a
# punch there -- no second push, to keep the motion smooth instead of stacked.
CAMERA = {
    #            lx     ly     z0     z1    jit   punches                              flash
    "s1":  dict(lk=(0.45, 0.55), push=(1.02, 1.05), jit=0.6, punch=[(0.10, 0.03)],
                flash=(0.000, 0.370, 1.00)),                       # fade in from white
    "s2":  dict(lk=(0.44, 0.50), push=(1.00, 1.00), jit=0.9, punch=[(0.500, 0.075)],
                flash=None),                                        # the slam
    "s3":  dict(lk=(0.46, 0.55), push=(1.05, 1.00), jit=1.2, punch=[(0.833, 0.060)],
                flash=None),                                        # field crash
    "s4":  dict(lk=(0.42, 0.50), push=(1.02, 1.05), jit=0.7,
                punch=[(2.10, 0.050), (2.55, 0.075)], flash=None),  # HE / NO
    "s5":  dict(lk=(0.50, 0.55), push=(1.02, 1.03), jit=1.2, punch=[(4.15, 0.045)],
                flash=None),
    "s6":  dict(lk=(0.50, 0.55), push=(1.02, 1.03), jit=1.0, punch=[(9.62, 0.045)],
                flash=None),
    "s7":  dict(lk=(0.45, 0.55), push=(1.02, 1.05), jit=0.9, punch=[(11.667, 0.075)],
                flash=(11.667, 11.900, 0.85)),                      # flash into replay
    "s8":  dict(lk=(0.45, 0.55), push=(1.00, 1.00), jit=0.9, punch=[(12.00, 0.085)],
                flash=None),                                        # BILLION slam
    "s9":  dict(lk=(0.46, 0.56), push=(1.07, 1.00), jit=1.3, punch=[(12.50, 0.055)],
                flash=None),                                        # macro zoom-out
    "s10": dict(lk=(0.40, 0.50), push=(1.05, 1.07), jit=1.0, punch=[(12.567, 0.09)],
                flash=None),
    "s11": dict(lk=(0.42, 0.50), push=(1.02, 1.05), jit=0.7,
                punch=[(13.73, 0.050), (13.88, 0.050), (14.00, 0.085)], flash=None),
    "s12": dict(lk=(0.50, 0.55), push=(1.02, 1.03), jit=1.2, punch=[(15.90, 0.045)],
                flash=None),
    "s13": dict(lk=(0.50, 0.50), push=(1.01, 1.03), jit=0.5, punch=[(20.70, 0.050)],
                flash=None),                                        # flash already in scene
}


def camera(f: np.ndarray, t: float, u: float, fn: str) -> None:
    """The per-shot camera move: push + crash-zoom punches + jitter + white flash."""
    c = CAMERA.get(fn)
    if c is None:
        return
    z = lerp(c["push"][0], c["push"][1], ease(u, "smooth"))
    for pt, s in c["punch"]:
        if t >= pt:
            z += s * math.exp(-(t - pt) / 0.10)
    jit = c["jit"]
    jx = jit * (math.sin(2 * math.pi * 7.3 * t) + 0.6 * math.sin(2 * math.pi * 11.7 * t + 1.3))
    jy = jit * (math.sin(2 * math.pi * 8.9 * t + 2.1) + 0.6 * math.sin(2 * math.pi * 13.3 * t))
    flash_w = 0.0
    fl = c["flash"]
    if fl is not None:
        ft0, ft1, fpk = fl
        if ft0 <= t <= ft1:
            flash_w = fpk * (1.0 - (t - ft0) / max(1e-6, ft1 - ft0))
    if z <= 1.002 and jit == 0.0 and flash_w <= 0.01:
        return  # nothing to move
    f8 = np.clip(f, 0, 255).astype(np.uint8)
    zz = max(z, 1.0)
    sw, sh = int(round(W * zz)), int(round(H * zz))
    g = cv2.resize(f8, (sw, sh), interpolation=cv2.INTER_LINEAR)
    lx, ly = c["lk"]
    cx0 = int(round((sw - W) * lx + jx))
    cy0 = int(round((sh - H) * ly + jy))
    cx0 = max(0, min(sw - W, cx0)); cy0 = max(0, min(sh - H, cy0))
    out = g[cy0:cy0 + H, cx0:cx0 + W]
    if flash_w > 0.01:
        out = np.clip(out.astype(np.float32) * (1.0 - flash_w) + 255.0 * flash_w,
                      0, 255).astype(np.uint8)
    f[:] = out.astype(np.float32)


def _shot_at(t: float, spec: dict) -> dict:
    return next((s for s in spec["shots"] if s["start"] <= t < s["end"]), spec["shots"][-1])


def _draw(i: int, spec: dict) -> np.ndarray:
    """One frame of its own shot, with no dissolve applied."""
    fps = spec["fps"]
    t = i / fps
    shot = _shot_at(t, spec)
    u = (t - shot["start"]) / max(1e-6, shot["end"] - shot["start"])
    f = np.zeros((H, W, 3), np.float32)
    globals()[f"scene_{shot['fn']}"](f, t, u)
    if shot.get("grain", 1.2) > 0:
        grain(f, shot["grain"], i * 7919 + 13)
    camera(f, t, u, shot["fn"])
    return f


def render_frame(i: int, spec: dict) -> np.ndarray:
    """A frame, with its shot's dissolve resolved against the shot before it.

    The dissolve source is the previous shot's **own frame**, drawn without its own
    dissolve. Without that, a short shot nested inside another loses its type into the
    next one (s8's word reappearing 1.5 s later on s10's packet, which is the kind of leak
    that reads as a glitch), and the mix also darkens by squaring the cross-fades.
    """
    fps = spec["fps"]
    t = i / fps
    shot = _shot_at(t, spec)
    f = _draw(i, spec)
    d = shot.get("dissolve_in", 0)
    if d > 0 and t - shot["start"] < d:
        k = ease(min(1.0, (t - shot["start"]) / d), "smooth")
        prev_i = max(0, int(round(shot["start"] * fps)) - 1)
        prev = _draw(prev_i, spec)
        f = prev * (1 - k) + f * k
    return np.clip(f, 0, 255).astype(np.uint8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default="spec/v7-01.json")
    ap.add_argument("--out", default="public/demo/v7-video-only.mp4")
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
        if i % 60 == 0:
            print(f"  frame {i}/{len(frames)} ({time.time()-t0:.0f}s)", flush=True)
    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError("video encoder failed")
    dt = time.time() - t0
    print(f"  {len(frames)} frames in {dt:.1f}s ({len(frames) / dt:.2f} fps) -> {a.out} "
          f"({Path(a.out).stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
