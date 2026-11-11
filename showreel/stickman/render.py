"""Putting a frame together.

Order is the order light arrives:

    backdrop (sky, sun, ridges, floor, floor marks)
      cast shadow, projected along the light and softened by height
      dust, if anything just hit the floor
      the figure, its far limbs behind its torso, its near limbs in front
      smear ghosts, oldest first, under the live pose
      rim light, aerial lift, vignette, grade, grain

Nothing is a sprite. Every mark on the frame is either a backdrop function
evaluated for this camera, or a joint of the rig projected through that same
camera -- which is why the figure stays welded to the floor when the camera moves.

The ink pass is the one place this differs from a wireframe: strokes are drawn
with a width profile (tapered ends, a heavier middle), the head is a true annulus
that is thicker at the bottom, and hairline grain breaks the edges so they read
as ink on paper rather than as vector antialiasing.
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import ink as inkmod
from .film import FPS, H, W, build_shots, Performer
from .rig import Pose
from .stage import Projector, World, paint
from .spring import Dust

# The figure is 700 world units tall and the frame is 1920, so a lens of 1.0
# would show it at 36% of frame height -- a wide shot of an empty desert. A lens
# of about 1.75 puts it at two thirds of frame height with its feet on the lower
# third line, which is where a nine-by-sixteen composition wants them. The shot
# files carry their own lens values; this is only the reference point.
REFERENCE_ZOOM = 1.75


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


# Widths as a fraction of figure height. The torso is the heaviest line, the
# limbs thinner, the far side thinner and lighter -- that is the whole depth cue.
_WIDTH = {
    "spine": 0.0165,
    "leg": 0.0152,
    "foot": 0.0124,
    "arm": 0.0132,
    "far_arm": 0.0118,
    "far_leg": 0.0134,
    "far_foot": 0.0108,
}

# How much of the ink value a far limb keeps.
_FAR = 0.50


def ink(pose_screen, *, colour=(0.078, 0.072, 0.086), size=None, seed=0):
    """Rasterise the figure as tapered ink. Returns a float RGBA array."""
    W_, H_ = size if size is not None else (W, H)
    wi, hi = W_ * inkmod.SS, H_ * inkmod.SS

    far = Image.new("L", (wi, hi), 0)
    near = Image.new("L", (wi, hi), 0)
    d_far = ImageDraw.Draw(far)
    d_near = ImageDraw.Draw(near)

    scale = pose_screen.height

    for p0, p1, part in pose_screen.segments():
        is_far = part.startswith("far")
        draw = d_far if is_far else d_near
        width = _WIDTH.get(part, 0.0132) * scale * inkmod.SS
        inkmod.stroke(draw, np.asarray(p0) * inkmod.SS, np.asarray(p1) * inkmod.SS,
                      width, 255,
                      taper_start=0.62, taper_end=0.60, bulge=0.13)

    # Head: a proper ring, heavier at the bottom, plus the eye.
    hr = pose_screen.head_r * inkmod.SS
    cx, cy = pose_screen.head * inkmod.SS
    rim = max(1.0, _WIDTH["spine"] * scale * 0.5 * inkmod.SS * 1.10)
    inkmod.ring(d_near, (cx, cy), hr, rim, 255)

    eye_r = max(1.0, hr * 0.072)
    ex = cx + pose_screen.facing * hr * 0.40
    ey = cy - hr * 0.10
    inkmod.disc(d_near, (ex, ey), eye_r, 255)

    a_near = np.asarray(near.resize((W_, H_), Image.LANCZOS), np.float32) / 255.0
    a_far = np.asarray(far.resize((W_, H_), Image.LANCZOS), np.float32) / 255.0

    # Far limbs are drawn at reduced value: it is the only depth cue a pure line
    # drawing has, and without it a profile collapses into one flat silhouette.
    alpha = np.maximum(a_near, a_far * _FAR)

    rgba = np.zeros((H_, W_, 4), np.float32)
    rgba[..., 0] = colour[0]
    rgba[..., 1] = colour[1]
    rgba[..., 2] = colour[2]
    rgba[..., 3] = np.clip(alpha, 0.0, 1.0)
    return rgba


# ----------------------------------------------------------------- compositing

def composite(frame, rgba, opacity=1.0):
    a = rgba[..., 3:4] * opacity
    return frame * (1.0 - a) + rgba[..., :3] * a


def ground_shadow(frame, pose, proj, *, light=(0.58, 1.0), strength=0.28,
                  airborne=0.0):
    """The figure's shadow, projected along the light onto the floor.

    Each joint is pushed along the light until it meets y = 0 and the extremes of
    the result are joined, so the shadow stretches and shortens with the pose
    instead of being a fixed blob. The higher the caster, the weaker and wider its
    shadow: a real light has an angular size, so it cannot produce a hard shadow
    from two metres up.
    """
    xs = []
    for name, val in pose.joints():
        if name in ("head_r", "facing", "height", "hand_len", "foot_len"):
            continue
        height_above = max(0.0, -val[1])
        xs.append(proj.sx(val[0] + height_above * light[0] / light[1]))
    if not xs:
        return frame

    x0, x1 = min(xs), max(xs)
    span = max(8.0, x1 - x0)
    y_screen = float(proj.sy(0.0))

    sw, sh = 360, 72
    simg = Image.new("L", (sw, sh), 0)
    d = ImageDraw.Draw(simg)
    rx = span / W * sw * 0.5
    cy = sh * 0.5
    # Wider and fainter with height: the penumbra grows with distance.
    k = float(np.clip(airborne / 400.0, 0.0, 1.0))
    d.ellipse([sw * 0.5 - rx * (1.0 + 0.9 * k), cy - sh * 0.15 * (1.0 + 2.0 * k),
               sw * 0.5 + rx * (1.0 + 0.9 * k), cy + sh * 0.15 * (1.0 + 2.0 * k)],
              fill=255)
    simg = simg.filter(ImageFilter.GaussianBlur(3.4 + 5.0 * k))
    mask = np.asarray(simg.resize((W, H), Image.BILINEAR), np.float32) / 255.0

    yy = np.arange(H, dtype=np.float32)[:, None]
    band = np.exp(-((yy - y_screen) / (H * 0.0115)) ** 2)
    mask = mask * band * strength * (1.0 - 0.55 * k)

    # A shadow cannot fall on a hole. Blank the mask over the gap, which is the
    # detail that stops a jump over a chasm from looking like a jump over a
    # painted stripe.
    world = getattr(proj, "_world", None)
    if world is not None and getattr(world, "gaps", None):
        xs_cols = np.arange(W, dtype=np.float32)[None, :] + 0.5
        wx = proj.cam_x + (xs_cols - W * 0.5) * 1.0 / proj.zoom
        solid = np.ones((1, W), np.float32)
        for gx0, gx1, _ in world.gaps:
            solid *= np.logical_not((wx >= gx0) & (wx <= gx1)).astype(np.float32)
        mask = mask * solid

    tint = np.array([0.115, 0.093, 0.078], np.float32)
    return frame * (1.0 - mask[..., None]) + tint * mask[..., None]


def dust_layer(frame, dust, proj, world):
    """Draw the dust motes, back to front.

    A mote is an ellipse at its projected position, so it inherits the camera. It
    is drawn in the floor's own colour lifted toward the sky, which is what dirt
    actually looks like when it is lit from behind.
    """
    if not dust:
        return frame
    img = Image.fromarray((np.clip(frame, 0, 1) * 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    base = np.array(world.pal["ground_far"], np.float32)
    pale = np.array(world.pal["haze"], np.float32)
    parts = sorted(dust.parts, key=lambda q: q.p[1])
    for q in parts:
        # A mote over a hole has nothing to have been kicked off, so it is culled
        # rather than left hanging in a place the camera can see through.
        if not world.is_solid(q.p[0]):
            continue
        sx, sy = proj.point(q.p)
        if not (-80 < sx < W + 80 and -80 < sy < H + 80):
            continue
        r = q.radius * proj.zoom
        a = int(255 * 0.52 * q.alpha)
        if a <= 1 or r < 0.6:
            continue
        col = base * (0.55 + 0.45 * q.u) + pale * (0.20 + 0.25 * q.u)
        d.ellipse([sx - r, sy - r * 0.86, sx + r, sy + r * 0.86],
                  fill=tuple(int(255 * c) for c in np.clip(col, 0, 1)) + (a,))
    return np.asarray(img, dtype=np.float32) / 255.0


def speed_lines(frame, pose_screen, proj, strength):
    """A few short strokes trailing a fast limb.

    Not motion blur -- that would be wrong at 24 fps with a crisp ink look. These
    are drawn strokes along the actual direction of travel of the fastest joints,
    which is what a hand-drawn smear does and what the eye expects.
    """
    if strength <= 0.02:
        return frame
    img = Image.fromarray((np.clip(frame, 0, 1) * 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    ink_col = (30, 26, 32)
    for name, v in pose_screen.joints():
        if name not in ("wrist_near", "wrist_far", "toe_near", "toe_far"):
            continue
        n = 3
        for i in range(n):
            f = 0.35 + 0.28 * i
            a = int(52 * strength * (1.0 - i / n))
            if a <= 2:
                continue
            x0 = v[0] - 16 * f * strength
            y0 = v[1] - 6 * f * strength
            d.line([x0, y0, x0 + 26 * strength, y0 + 3 * strength],
                   fill=ink_col + (a,), width=max(1, int(2 * proj.zoom)))
    return np.asarray(img, dtype=np.float32) / 255.0


def rim_light(frame, proj, world, *, strength=0.42):
    """Light catching the sunward edge of the ink."""
    lum = frame.mean(axis=2)
    ink_mask = np.clip(1.0 - lum * 7.0, 0.0, 1.0)
    shift = max(1, int(round(2.0 * proj.zoom)))
    edge = np.clip(ink_mask - np.roll(ink_mask, shift, axis=1), 0.0, 1.0)
    edge *= strength
    tint = np.array(world.pal["sun"], np.float32) * 0.50 + 0.50
    return frame + (tint - frame) * edge[..., None]


def air_and_grade(frame, world, *, zoom=1.0, grain_seed=0):
    """Atmosphere, vignette, a film curve and grain."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    hz = float(np.clip(H * 0.52, 1, H - 1))
    haze = np.clip(1.0 - yy / hz, 0.0, 1.0) ** 1.5 * 0.050
    haze_col = np.array(world.pal["haze"], np.float32)
    frame = frame * (1.0 - haze[..., None]) + haze_col * haze[..., None]

    r = np.sqrt(((xx - W * 0.5) / (W * 0.5)) ** 2 + ((yy - H * 0.5) / (H * 0.5)) ** 2)
    vig = 1.0 - 0.24 * np.clip((r - 0.64) / 0.95, 0.0, 1.0) ** 1.7
    frame = frame * vig[..., None]

    lift = np.array([0.013, 0.011, 0.019], np.float32)
    gain = np.array([1.032, 1.000, 0.964], np.float32)
    frame = np.clip(frame * gain + lift, 0.0, 1.0)
    frame = frame + (frame * frame * (3.0 - 2.0 * frame) - frame) * 0.20

    rng = np.random.default_rng(1000 + grain_seed)
    n = rng.standard_normal((H // 2, W // 2)).astype(np.float32)
    n = np.repeat(np.repeat(n, 2, axis=0), 2, axis=1)[:H, :W]
    frame = frame + n[..., None] * 0.012

    return np.clip(frame, 0.0, 1.0)


# --------------------------------------------------------------------- a frame

def _locate(shots, t_global):
    acc = 0.0
    for s in shots:
        if t_global < acc + s.duration or s is shots[-1]:
            return s, min(t_global - acc, s.duration)
        acc += s.duration
    return shots[-1], 0.0


def _smear_count(speed_px):
    if speed_px < 16:
        return 0
    if speed_px < 34:
        return 1
    return 2


class Sequence:
    """The film as a stateful strip of time.

    Dust cannot be a pure function of time -- a particle's path depends on the
    frames before it -- so it is simulated. This class owns that simulation and
    advances it frame by frame, which also means a render is reproducible: the
    same seed and the same frame order produce the same dust every time.

    Impacts are detected rather than declared: a foot that is suddenly lower than
    the floor was going to be, and moving down faster than a threshold, is a
    landing, and the puff is scaled by how fast it arrived.
    """

    def __init__(self, shots, perf, world, *, seed=11):
        self.shots = shots
        self.perf = perf
        self.world = world
        self.dust = Dust(seed=seed)
        self.t = 0.0
        self.prev = None
        self.shake = 0.0
        self.shake_t = 0.0
        self._landed = set()

    def _pose_at(self, t):
        acc = 0.0
        for i, s in enumerate(self.shots):
            if t < acc + s.duration or s is self.shots[-1]:
                return i, min(t - acc, s.duration)
            acc += s.duration
        return len(self.shots) - 1, 0.0

    def advance(self, dt):
        """Step the simulation by dt and return the frame at the new time."""
        self.t += dt
        idx, local = self._pose_at(self.t)
        pose, cam = self.shots[idx](local, self.perf)

        # --- impact detection -------------------------------------------------
        key = (idx, self.shots[idx].duration)
        toe = max(pose.toe_near[1], pose.toe_far[1])
        if self.prev is not None:
            prev_toe = self.prev
            speed = (toe - prev_toe) / max(dt, 1e-6)   # positive = downward
            if speed > 900.0 and toe < 14.0 and self.world.is_solid(pose.pelvis[0]):
                self.dust.kick((pose.pelvis[0], 0.0),
                               min(1.6, speed / 2200.0),
                               count=int(9 + 8 * min(1.6, speed / 2200.0)),
                               direction=0.6 if pose.facing > 0 else -0.6)
                # A landing also shakes the camera. Amplitude follows the impact.
                self.shake = min(1.0, speed / 3000.0)
                self.shake_t = 0.0
        self.prev = toe

        self.dust.step(dt)
        self.shake_t += dt
        return self.render(self.t, shake=self.shake, shake_t=self.shake_t)

    def render(self, t_global, *, shake=0.0, shake_t=0.0):
        return render_time(self.shots, self.perf, self.world, t_global,
                           dust=self.dust, shake=shake, shake_t=shake_t)


def render_time(shots, perf, world, t_global, *, dust=None, shake=0.0,
                shake_t=0.0):
    """Render the film at an arbitrary global time, in seconds.

    ``dust`` is an optional simulation stepped by the caller; when it is absent
    this renders a still with no particles, which is what a look-dev frame wants.
    """
    shot, local = _locate(shots, t_global)
    pose, cam = shot(local, perf)

    t_prev = max(0.0, local - 1.0 / FPS)
    prev_pose = shot(t_prev, perf)[0]
    prev_screen = project_pose(prev_pose, Projector(
        W, H, cam_x=cam["x"], cam_y=cam.get("rise", 0.0), eye=cam["height"],
        zoom=cam["zoom"], tilt=cam["tilt"]))

    # Camera shake, decaying. Expressed in frame fractions so it reads the same
    # at any lens; a landing that shook the frame by pixels would look different
    # in a wide shot than in a close one, which is not how a camera behaves.
    sh_x = sh_y = 0.0
    if shake > 0.0:
        amp = shake * 0.022 * math.exp(-9.0 * shake_t)
        sh_x = amp * math.sin(2.0 * math.pi * 13.0 * shake_t)
        sh_y = amp * math.sin(2.0 * math.pi * 9.7 * shake_t + 1.3)

    proj = Projector(W, H, cam_x=cam["x"] + cam["lead"] * perf.height - sh_x * 260.0,
                     cam_y=cam.get("rise", 0.0) + sh_y * 380.0,
                     eye=cam["height"], zoom=cam["zoom"], tilt=cam["tilt"])
    proj._world = world
    world_frame = cam.get("_force_scale")

    frame = paint(world, proj)

    # Airborne height, for the shadow: the pelvis is the honest reference.
    airborne = max(0.0, -(pose.pelvis[1] + 320.0))

    frame = ground_shadow(frame, pose, proj, airborne=airborne)
    if dust is not None:
        frame = dust_layer(frame, dust, proj, world)

    # Smear: only on genuinely fast motion, and only from a real earlier pose.
    dx = float(np.hypot(*(project_pose(pose, proj).pelvis
                          - project_pose(prev_pose, proj).pelvis)))
    ghosts = _smear_count(dx * FPS)
    if ghosts:
        for k in range(ghosts, 0, -1):
            tp = local - k * (1.0 / FPS) * 0.6
            if tp < 0:
                continue
            gp = shot(tp, perf)[0]
            frame = composite(frame, ink(project_pose(gp, proj)), 0.12)

    pose_screen = project_pose(pose, proj)
    frame = composite(frame, ink(pose_screen))
    frame = rim_light(frame, proj, world)
    frame = air_and_grade(frame, world, zoom=cam["zoom"], grain_seed=int(t_global * FPS))
    return frame
