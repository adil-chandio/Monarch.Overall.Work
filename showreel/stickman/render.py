"""Putting a frame together.

Order is the order light arrives:

    backdrop (sky, sun, ridges, floor, floor marks)
      ground shadow, projected along the light direction
      the figure, its far limbs behind its torso, its near limbs in front
      motion smear, as ghost copies of where the body actually was
      rim light, aerial lift, vignette, grade, grain

Nothing here is a sprite. Every mark on the frame is either a backdrop function
evaluated for this camera, or a joint of the rig projected through that same
camera -- which is why the figure stays welded to the floor when the camera moves.
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .film import FPS, H, W, build_shots, Performer
from .rig import Pose, build_pose
from .stage import Projector, World, paint

SS = 2  # supersample for the ink pass

# The figure is 700 world units tall and the frame is 1920. At a lens of 1.0 the
# character would occupy a third of a vertical frame, which is a wide shot of an
# empty desert. This is the base lens: it puts the figure at roughly two thirds
# of frame height with its feet on the lower third line, which is where a
# nine-by-sixteen composition wants them.
BASE_ZOOM = 1.62


# ----------------------------------------------------------------- the figure

def project_pose(pose, proj):
    """Map every joint of a world-space pose into frame pixels."""
    out = Pose()
    out.facing = pose.facing
    out.height = pose.height * proj.zoom
    out.head_r = pose.head_r * proj.zoom
    out.hand_len = pose.hand_len * proj.zoom
    out.foot_len = pose.foot_len * proj.zoom
    for name, val in pose.joints():
        setattr(out, name, proj.point(val))
    return out


def ink(pose_screen, *, colour=(0.075, 0.070, 0.085), far_fade=0.52, size=None):
    """Rasterise the figure as coverage, then tint it. Returns float RGBA."""
    W_, H_ = size if size is not None else (W, H)
    wi, hi = W_ * SS, H_ * SS
    img = Image.new("L", (wi, hi), 0)
    d = ImageDraw.Draw(img)

    for p0, p1, part in pose_screen.segments():
        far = part.startswith("far")
        width = _width_for(part) * pose_screen.height
        r = max(0.9, width * 0.5 * SS)
        val = int(255 * (far_fade if far else 1.0))
        _capsule(d, p0 * SS, p1 * SS, r, val)

    # Head: a ring, not a disc. The ring is what carries the expression.
    hr = pose_screen.head_r * SS
    cx, cy = pose_screen.head * SS
    rim = max(1.2, _width_for("spine") * pose_screen.height * 0.5 * SS)
    d.ellipse([cx - hr, cy - hr, cx + hr, cy + hr], fill=255)
    inner = hr - rim * 2.05
    if inner > 0.8:
        d.ellipse([cx - inner, cy - inner, cx + inner, cy + inner], fill=0)

    # Eye. A single dot on the facing side; two dots would make it a front view.
    eye_r = max(1.1, hr * 0.070)
    ex = cx + pose_screen.facing * hr * 0.40
    ey = cy - hr * 0.10
    d.ellipse([ex - eye_r, ey - eye_r, ex + eye_r, ey + eye_r], fill=255)

    img = img.resize((W_, H_), Image.LANCZOS)
    a = np.asarray(img, dtype=np.float32) / 255.0
    rgba = np.zeros((H_, W_, 4), np.float32)
    rgba[..., 0] = colour[0]
    rgba[..., 1] = colour[1]
    rgba[..., 2] = colour[2]
    rgba[..., 3] = a
    return rgba


# Segment widths as a fraction of figure height. The torso is the heaviest line,
# limbs thinner, the far side thinner again -- that is the whole depth cue.
_WIDTH = {
    "spine": 0.0152,
    "leg": 0.0142,
    "foot": 0.0116,
    "arm": 0.0124,
    "far_arm": 0.0114,
    "far_leg": 0.0130,
    "far_foot": 0.0106,
}


def _width_for(part):
    return _WIDTH.get(part, 0.0130)


def _capsule(draw, p0, p1, r, val):
    """A round-capped thick line, drawn as a polygon plus two discs."""
    p0 = np.asarray(p0, float)
    p1 = np.asarray(p1, float)
    d = p1 - p0
    L = float(np.hypot(d[0], d[1]))
    if L < 1e-5:
        draw.ellipse([p0[0] - r, p0[1] - r, p0[0] + r, p0[1] + r], fill=val)
        return
    u = d / L
    n = np.array([-u[1], u[0]]) * r
    draw.polygon([tuple(p0 + n), tuple(p1 + n), tuple(p1 - n), tuple(p0 - n)], fill=val)
    draw.ellipse([p0[0] - r, p0[1] - r, p0[0] + r, p0[1] + r], fill=val)
    draw.ellipse([p1[0] - r, p1[1] - r, p1[0] + r, p1[1] + r], fill=val)


# ------------------------------------------------------------------- compositing

def composite(frame, rgba, opacity=1.0):
    a = rgba[..., 3:4] * opacity
    return frame * (1.0 - a) + rgba[..., :3] * a


def ground_shadow(frame, pose, proj, *, light=(0.55, 1.0), strength=0.26,
                  airborne=0.0):
    """The figure's shadow, projected along the light onto the floor.

    Each joint is pushed along the light direction until it meets y = 0, and the
    extremes of the result are joined. So the shadow stretches and shortens with
    the pose instead of being a fixed blob under the feet, which is the cue that
    tells the eye how tall the figure is and where it is standing.
    """
    xs = []
    for name, val in pose.joints():
        if name in ("head_r", "facing", "height", "hand_len", "foot_len"):
            continue
        depth = max(0.0, -val[1])           # height above the floor
        drop = depth * light[0] / light[1]
        xs.append(proj.sx(val[0] + drop))
    if not xs:
        return frame
    x0, x1 = min(xs), max(xs)
    y_screen = float(proj.sy(0.0))
    span = max(6.0, x1 - x0)

    # Build the blob small and blur it: a soft contact shadow, not a decal.
    sw, sh = 320, 64
    simg = Image.new("L", (sw, sh), 0)
    d = ImageDraw.Draw(simg)
    rx = span / W * sw * 0.5
    cy = sh * 0.5
    d.ellipse([sw * 0.5 - rx, cy - sh * 0.16, sw * 0.5 + rx, cy + sh * 0.16], fill=255)
    simg = simg.filter(ImageFilter.GaussianBlur(3.0))
    mask = np.asarray(simg.resize((W, H), Image.BILINEAR), np.float32) / 255.0

    # Concentrate it around the floor line; a shadow does not float in the sky.
    yy = np.arange(H, dtype=np.float32)[:, None]
    band = np.exp(-((yy - y_screen) / (H * 0.0105)) ** 2)
    mask = mask * band * strength

    # A shadow cast from height is weaker and more diffuse: the light source has
    # a real angular size, so the further the caster is from the floor the softer
    # and fainter its shadow. Scaling both makes the figure look lifted rather
    # than pasted over its own shadow.
    if airborne > 0.0:
        k = float(np.clip(airborne / (0.55 * 700.0), 0.0, 1.0))
        mask = mask * (1.0 - 0.55 * k)

    tint = np.array([0.10, 0.085, 0.080], np.float32)
    return frame * (1.0 - mask[..., None]) + tint * mask[..., None]


def smear(frame, samples, proj, *, base_opacity=0.26):
    """Ghost copies of the body along its recent path.

    This is a smear done properly: instead of a stylised stretched shape, the
    actual pose from two or three earlier instants is inked, thinner and fainter,
    underneath the live one. It says the truth about where the body just was,
    which is what the technique is for.
    """
    for rgba, op in samples:
        frame = composite(frame, rgba, op)
    return frame


def rim_light(frame, pose_screen, proj, world, *, strength=0.55):
    """Light catching the sunward edge of the ink.

    The ink mask is shifted along the light and subtracted from itself; what is
    left is the thin sliver of figure the light can reach. Cheap, and derived
    from the drawing rather than painted on.
    """
    lum = frame.mean(axis=2)
    ink_mask = np.clip(1.0 - lum * 7.0, 0.0, 1.0)
    shift = max(1, int(round(2.2 * proj.zoom)))
    edge = np.clip(ink_mask - np.roll(ink_mask, shift, axis=1), 0.0, 1.0)
    edge *= strength
    tint = np.array(world.pal["sun"], np.float32) * 0.55 + 0.45
    return frame + (tint - frame) * edge[..., None]


def air_and_grade(frame, world, *, zoom=1.0, grain_seed=0):
    """Atmosphere, vignette, a film curve and grain."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    # Aerial lift: the top of the frame sits further away, so it goes hazy.
    hz = float(np.clip(H * 0.5, 1, H - 1))
    haze = np.clip(1.0 - yy / hz, 0.0, 1.0) ** 1.5 * 0.055
    haze_col = np.array(world.pal["haze"], np.float32)
    frame = frame * (1.0 - haze[..., None]) + haze_col * haze[..., None]

    # Vignette.
    r = np.sqrt(((xx - W * 0.5) / (W * 0.5)) ** 2 + ((yy - H * 0.5) / (H * 0.5)) ** 2)
    vig = 1.0 - 0.26 * np.clip((r - 0.62) / 0.95, 0.0, 1.0) ** 1.7
    frame = frame * vig[..., None]

    # Film curve: lift the blacks, warm the highlights.
    lift = np.array([0.014, 0.012, 0.020], np.float32)
    gain = np.array([1.035, 1.000, 0.962], np.float32)
    frame = np.clip(frame * gain + lift, 0.0, 1.0)
    frame = frame + (frame * frame * (3.0 - 2.0 * frame) - frame) * 0.20

    # Grain, at half resolution so it reads as film and not as noise.
    rng = np.random.default_rng(1000 + grain_seed)
    n = rng.standard_normal((H // 2, W // 2)).astype(np.float32)
    n = np.repeat(np.repeat(n, 2, axis=0), 2, axis=1)[:H, :W]
    frame = frame + n[..., None] * 0.013

    return np.clip(frame, 0.0, 1.0)


# --------------------------------------------------------------------- a frame

def render_time(shots, perf, world, t_global):
    """Render the film at an arbitrary global time, in seconds."""
    # Locate the shot.
    acc = 0.0
    shot = None
    local = 0.0
    for s in shots:
        if t_global < acc + s.duration or s is shots[-1]:
            shot = s
            local = min(t_global - acc, s.duration)
            break
        acc += s.duration

    out = shot(local, perf)
    pose, cam_x, zoom, tilt = out[0], out[1], out[2], out[3]

    proj = Projector(W, H, cam_x=cam_x, eye=0.250, zoom=zoom * BASE_ZOOM, tilt=tilt)
    frame = paint(world, proj)

    airborne = out[4] if len(out) > 4 else 0.0
    frame = ground_shadow(frame, pose, proj, airborne=airborne)

    # Smear: only on fast motion, and only from a real earlier pose.
    speed = abs(out[5] - _prev_x(shot, local, perf)) if len(out) > 5 else 0.0
    ghosts = _smear_count(speed)
    if ghosts:
        layer = []
        for k in range(ghosts, 0, -1):
            tp = local - k * (1.0 / FPS) * 0.55
            if tp < 0:
                continue
            prev = shot(tp, perf)
            layer.append((ink(project_pose(prev[0], proj)), 0.15))
        frame = smear(frame, layer, proj)

    pose_s = project_pose(pose, proj)
    frame = composite(frame, ink(pose_s))
    frame = rim_light(frame, pose_s, proj, world)
    frame = air_and_grade(frame, world, zoom=zoom, grain_seed=int(t_global * FPS))
    return frame


def _prev_x(shot, local, perf):
    tp = max(0.0, local - 1.0 / FPS)
    try:
        return shot(tp, perf)[5]
    except Exception:
        return 0.0


def _smear_count(speed):
    if speed < 12:
        return 0
    if speed < 26:
        return 1
    return 2
