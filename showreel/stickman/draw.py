"""Drawing a stick figure so it looks inked, not vectorised.

The renderer works at 2x supersampling on a coverage mask, then downsamples.
That is what gives the strokes their antialiased, slightly-organic edge without
any texture or brush stamping -- no pasted imagery anywhere.

Two things make the difference between "stickman" and "stickman that moves":

  * round caps and round joints. A stroke that ends in a square reads as a
    rectangle even when the pose is right.
  * tapered ends. Real ink thins where the nib lifts; a constant-width capsule
    is the single biggest tell of a cheap rig.
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SS = 2  # supersample factor for the ink pass


def _tapered_capsule(draw, p0, p1, r0, r1, fill, taper=0.30):
    """A thick line from p0 (radius r0) to p1 (radius r1), round capped.

    Draws a polygon between the two edge offsets plus discs at each end, which
    is cheap and, at this line weight, indistinguishable from a true SDF once
    antialiased.
    """
    p0 = np.asarray(p0, float)
    p1 = np.asarray(p1, float)
    d = p1 - p0
    L = float(np.hypot(d[0], d[1]))
    if L < 1e-6:
        if r0 > 0.4:
            draw.ellipse([p0[0] - r0, p0[1] - r0, p0[0] + r0, p0[1] + r0], fill=fill)
        return
    u = d / L
    n = np.array([-u[1], u[0]])

    # Taper the last stretch so the stroke lifts off the page.
    ta = min(taper, 0.5)
    if ta > 0.0:
        r_taper = r1 * 0.55
        mid = p1 - d * ta * 0.55
        quad = [
            p0 + n * r0, mid + n * r_taper, p1 + n * (r1 * 0.30),
            p1 - n * (r1 * 0.30), mid - n * r_taper, p0 - n * r0,
        ]
        draw.polygon([tuple(q) for q in quad], fill=fill)
        draw.ellipse([mid[0] - r_taper, mid[1] - r_taper,
                      mid[0] + r_taper, mid[1] + r_taper], fill=fill)
        draw.ellipse([p1[0] - r1 * 0.30, p1[1] - r1 * 0.30,
                      p1[0] + r1 * 0.30, p1[1] + r1 * 0.30], fill=fill)
    else:
        quad = [p0 + n * r0, p1 + n * r1, p1 - n * r1, p0 - n * r0]
        draw.polygon([tuple(q) for q in quad], fill=fill)
        draw.ellipse([p1[0] - r1, p1[1] - r1, p1[0] + r1, p1[1] + r1], fill=fill)

    draw.ellipse([p0[0] - r0, p0[1] - r0, p0[0] + r0, p0[1] + r0], fill=fill)


# Per-part styling: line width as a fraction of figure height, and how dark the
# limb sits relative to the front-most ink. Far limbs are thinner and lighter,
# which is the only depth cue a pure line drawing has.
STYLE = {
    "spine":        (0.0150, 1.00),
    "leg":          (0.0140, 1.00),
    "foot":         (0.0115, 1.00),
    "arm":          (0.0122, 1.00),
    "far_arm":      (0.0112, 0.52),
    "far_leg":      (0.0128, 0.52),
    "far_foot":     (0.0105, 0.52),
}


def ink_layers(pose, scale=1.0):
    """Return a list of (mask, colour) to composite, back to front.

    Colour is a float 0..1 ink value; the caller maps it onto the palette.
    """
    items = []
    for p0, p1, part in pose.segments():
        w, v = STYLE[part]
        items.append((p0, p1, w * pose.height, v))
    return items


def draw_figure(pose, size, *, ink=(0.06, 0.06, 0.08), shadow=None, ss=SS):
    """Render one figure onto RGBA at ``size`` (w, h), supersampled.

    Returns a float RGBA array (h, w, 4) at the requested size, ready to be
    alpha-composited over a background. ``shadow`` is an optional
    (x, y, radius_x, radius_y, opacity) tuple drawn as a soft ground blob.
    """
    w, h = size
    W, H = w * ss, h * ss

    img = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(img)

    # Hair: a small tuft, drawn first so the head ball sits on top of its root.
    for p0, p1, part in pose.segments():
        width, value = STYLE[part]
        r = width * pose.height * ss * 0.5
        lum = int(round(255 * value))
        _tapered_capsule(draw, p0 * ss, p1 * ss, r, r, lum, taper=0.0)

    # Head: an ellipse with a slightly thicker rim (ink sits heavier on curves).
    hr = pose.head_r * ss
    cx, cy = pose.head * ss
    rim = STYLE["spine"][0] * pose.height * ss * 0.5 * 1.05
    draw.ellipse([cx - hr, cy - hr, cx + hr, cy + hr], fill=255)
    hole = hr - rim * 1.9
    if hole > 1.0:
        draw.ellipse([cx - hole, cy - hole, cx + hole, cy + hole], fill=0)

    # The eye: one dot, on the facing side. Two dots would read as front view.
    eye_x = cx + pose.facing * hr * 0.42
    eye_r = max(1.2, hr * 0.055) * ss
    draw.ellipse([eye_x - eye_r, cy - hr * 0.10 - eye_r,
                  eye_x + eye_r, cy - hr * 0.10 + eye_r], fill=255)

    img = img.resize((w, h), Image.LANCZOS)

    arr = np.asarray(img, dtype=np.float32) / 255.0
    out = np.zeros((h, w, 4), dtype=np.float32)
    out[..., 0] = ink[0] * arr + (1.0 - arr) * 0.0
    out[..., 1] = ink[1] * arr
    out[..., 2] = ink[2] * arr
    out[..., 3] = arr

    if shadow is not None:
        sx, sy, rx, ry, op = shadow
        sh = Image.new("L", (W, H), 0)
        sd = ImageDraw.Draw(sh)
        sd.ellipse([(sx - rx) * ss, (sy - ry) * ss, (sx + rx) * ss, (sy + ry) * ss], fill=255)
        sh = sh.filter(ImageFilter.GaussianBlur(radius=max(1.0, rx * 0.22 * ss)))
        sh = np.asarray(sh.resize((w, h), Image.LANCZOS), dtype=np.float32) / 255.0
        sh *= op
        # Shadow goes under the ink.
        a = out[..., 3]
        out[..., 3] = a + sh * (1.0 - a)
        for c in range(3):
            out[..., c] = out[..., c] * a / np.maximum(out[..., 3], 1e-6)

    return out
