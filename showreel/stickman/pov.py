"""POV: the stadium goes quiet -- the film, second cut.

Ninety seconds, ten shots, one figure, one keeper, one ball, one crowd. The first
cut was six shots of seventeen seconds each with one camera move apiece, and it
was honest and it was slow. This one is cut to the bone: every shot is two or
three camera setups, every setup is short enough to stay ahead of the eye, and
every loud thing in the film has a quiet thing before it.

    0.0   5.0   cold       black, an aperture, and a figure in the mouth of it
    5.0  13.0   walk       three setups -- the stand, the boots, the face
   13.0  22.0   the warm   two touches, and the second one is a disaster
   22.0  31.0   the set    the ball is placed, then the eyes get a whole setup
   31.0  41.5   the strike run-up, plant, contact at 37.30, then slow motion
   41.5  49.0   the roar   the sound comes back and does not stop
   49.0  58.0   the replay the contact again, from behind, at a fifth of speed
   58.0  72.0   the turn   he looks at us, winks, and puts a finger to his lips
   72.0  82.0   the walk-off  he comes at the lens until the aperture closes
   82.0  90.0   the card   black, and one question

The spine is unchanged -- loud, then nothing, then everything -- because that is
the only reason the film exists. What changed is the cutting: the hush is a *drop*
in the middle of a busy film rather than a long quiet stretch, so it is felt as an
absence instead of as pacing.

**The clock is not the camera's.** Two shots run their own time: the strike goes to
a third of speed at contact, and the replay runs the same half-second of contact
at a fifth of speed. The rig is still solved at true gravity inside the warp, so
the ball is slow rather than floaty. Stretching the render instead would only have
made a low frame rate.

**Impacts are solved, then felt.** The camera shake after contact is a decaying
sine on the frame, the flash is two frames of white, and the ball is a ballistic
whose launch velocity is solved from where it has to arrive. The one thing that is
authored outright is the wink: there is no physics in eyelids.
"""

from __future__ import annotations

import math

import numpy as np

from . import face as F
from .film import FPS, FIG_H, H, W, Performer
from .motion import GRAVITY
from .rig import P, build_pose, clamp, ease_in_out, lerp, pelvis_height, smoothstep
from .stadium import UPERM, Stadium, z_of

TOTAL = 90.0

SHOTS = (
    ("cold", 0.0, 5.0),
    ("walk", 5.0, 13.0),
    ("warm", 13.0, 22.0),
    ("set", 22.0, 31.0),
    ("kick", 31.0, 41.5),
    ("roar", 41.5, 49.0),
    ("replay", 49.0, 58.0),
    ("turn", 58.0, 72.0),
    ("walkoff", 72.0, 82.0),
    ("endcard", 82.0, 90.0),
)

# The four moments the sound, the text and the verifier all have to agree on.
GRASS_STEP = 7.90        # the footfall that takes the crowd away
CONTACT = 37.30          # boot on ball
WINK = 66.10
SHUSH = 68.40
QUESTION = 82.60         # the card

# The penalty spot is the origin of the world x axis. Negative is behind him.
SPOT_X = 0.0
BALL_R = 0.065          # fraction of figure height: a size-four ball is 22 cm


def _shot_at(t):
    for name, a, b in SHOTS:
        if t < b:
            return name, a, b, clamp((t - a) / max(b - a, 1e-6))
    name, a, b = SHOTS[-1]
    return name, a, b, 1.0


def cam(*, x=0.0, eye=0.24, zoom=1.0, tilt=0.0, rise=0.0):
    return {"x": x, "eye": eye, "zoom": zoom, "tilt": tilt, "rise": rise}


def _place_goal(zoom, frac, cam_x, goal_d):
    """World-x origin that puts the goal centre at ``frac`` of the frame width.

    Solving it rather than eyeballing it means the goal stays where the
    composition put it when the camera moves, and a shot can be re-timed without
    re-aiming.
    """
    z = z_of(goal_d)
    return (frac * W - W * 0.5) * z / max(zoom, 1e-6) + cam_x


def _eye_for_row(row, zoom, wy=-0.86 * FIG_H, tilt=0.0):
    """Camera height that puts a world point at ``row`` of the frame.

    ``sy/H = 0.5 + (wy + eye*H)*zoom/H + tilt``, so this is that solved for eye.
    Doing it this way matters: an eye height picked by hand means the same shot
    re-framed itself every time the zoom changed, which is exactly what happened
    when the second cut was first assembled -- the tight setups put the head at a
    third of the frame with the legs cut off at the ankle.
    """
    eye = ((row - 0.5 - tilt) * H / max(zoom, 1e-6) - wy) / H
    return min(0.52, max(0.02, eye))


def _aim(out, x, *, zoom, eye=None, tilt=0.0, lead=0.0, goal_d=30.0, frac=1.34,
         show_goal=False, show_pylons=False, rise=0.0, head_row=None,
         ground_row=None):
    """Point the camera at ``x`` with ``lead`` in pixels, and place the set.

    Every setup in the film goes through here, so a setup is five numbers and a
    pair of flags rather than ten lines of projection arithmetic repeated twenty
    times -- which is how the first cut ended up with a goal framed out of a shot
    that was still painting it.
    """
    cx = x + lead
    if head_row is not None:
        eye = _eye_for_row(head_row, zoom, tilt=tilt)
    elif ground_row is not None:
        eye = _eye_for_row(ground_row, zoom, wy=0.0, tilt=tilt)
    out["cam"] = cam(x=cx, eye=eye, zoom=zoom, tilt=tilt, rise=rise)
    out["goal_d"] = goal_d
    out["show_goal"] = show_goal
    out["show_pylons"] = show_pylons
    out["origin"] = _place_goal(zoom, frac, cx, goal_d)


def _shake(t, at, *, amp=1.0, decay=0.40, freq=15.0):
    """A decaying sine, in pixels, for an impact the camera feels.

    Not noise: noise on a locked-off frame reads as damage, and a shake that
    reverses on a period reads as a camera on a spring. This is the second one.
    """
    e = t - at
    if e < 0.0 or e > decay * 5.0:
        return 0.0
    return amp * math.exp(-e / decay) * math.sin(2.0 * math.pi * freq * e)


# ----------------------------------------------------------------- the figure

def _stand(perf, x, *, facing=1.0, breath_t=0.0, lean=0.0, head_tilt=0.0,
           crouch=0.0, hands=None, tone="ink", curl=0.075):
    h = perf.height
    b = math.sin(2.0 * math.pi * 1.25 * breath_t) * h * 0.0028
    hip_y = -pelvis_height(h, 0.06 + crouch) + b
    fn = np.array([x + h * 0.075, 0.0])
    ff = np.array([x - h * 0.052, 0.0])
    chest = np.array([x, hip_y - P["spine"] * h * 0.55])
    if hands is None:
        hands = perf.arm_targets(0.0, chest, 0.0, lean)
    return build_pose((x, hip_y), h, facing=facing, lean=lean, curl=curl,
                      head_tilt=head_tilt, foot_near=fn, foot_far=ff,
                      hand_near=hands[0], hand_far=hands[1], tone=tone)


def _walk(perf, gait, x, phase, *, facing=1.0, lean_extra=0.0, head_tilt=0.0,
          arm_up=0.0):
    h = perf.height
    g = gait
    fn, pn = g.foot(phase, x, 0.0, side=0.0)
    ff, pf = g.foot(phase, x, 0.0, side=0.5)
    hip_y = -pelvis_height(h, 0.10) + g.hip_offset(phase)
    lean = g.lean + lean_extra
    chest = np.array([x, hip_y - P["spine"] * h * 0.55])
    swing = math.cos(2.0 * math.pi * phase) * g.arm_swing
    hands = perf.arm_targets(phase, chest, swing, lean, up=arm_up)
    return build_pose((x, hip_y), h, facing=facing, lean=lean, curl=0.085,
                      head_tilt=head_tilt, foot_near=fn, foot_far=ff,
                      pitch_near=pn, pitch_far=pf,
                      hand_near=hands[0], hand_far=hands[1])


def _blink(t, period=3.4, phase=0.0, dur=0.14):
    """A blink long enough to survive 24 fps: 0.14 s is five frames."""
    u = ((t + phase) % period) / dur
    if u >= 1.0:
        return 0.0
    return math.sin(math.pi * u) ** 0.7


def _wink(t, at, hold=0.30, rise=0.10):
    """0 -> 1 -> 0 over ``hold`` seconds, starting at ``at``."""
    u = (t - at) / max(hold, 1e-6)
    if u < 0.0 or u > 1.0 + rise / max(hold, 1e-6):
        return 0.0
    if u < rise / max(hold, 1e-6):
        return u / (rise / max(hold, 1e-6))
    if u > 1.0:
        return max(0.0, 1.0 - (u - 1.0) / (rise / max(hold, 1e-6)))
    return 1.0


# --------------------------------------------------------------------- shots

class Pov:
    """The whole film as a function of time."""

    def __init__(self, perf=None, seed=11):
        self.perf = perf or Performer(FIG_H)
        # One stadium, re-palette-ed per shot, and re-parallaxed by moving its
        # origin. The crowd cloud is generated once and never re-randomised.
        self.stad = Stadium("floodlit", goal_d=30.0, seed=seed, origin_x=0.0)

    def state(self, t):
        name, a, b, u = _shot_at(t)
        out = {
            "shot": name, "t": t, "u": u,
            "cam": cam(),
            "hero": None,
            "face": F.NEUTRAL,
            "hero_z": 1.0,
            "keeper": None,
            "ball": None,
            "tunnel": 1.0,
            "churn": 1.0,
            "palette": "floodlit",
            "stadium": self.stad,
            "goal_d": 30.0,
            "origin": 0.0,
            "show_goal": True,
            "show_pylons": True,
            "light": 0.0,
            "blank": False,
            "flash": 0.0,
            "shake": (0.0, 0.0),
            "strike_e": None,
        }
        getattr(self, "_shot_" + name)(out, t - a, b - a, u)
        self.stad.goal_d = out["goal_d"]
        self.stad.origin_x = out["origin"]
        self.stad.show_goal = out["show_goal"]
        self.stad.show_pylons = out["show_pylons"]
        return out

    def _ball(self, x, y, z=1.0):
        return {"at": np.array([x, y], float), "r": BALL_R * self.perf.height,
                "z": z}

    # -- 1. cold open -------------------------------------------------------

    def _shot_cold(self, out, t, dur, u):
        """Black, then an aperture, then the man in the mouth of it.

        Three setups in five seconds, and the first of them is nothing at all: a
        black frame with a crowd already roaring over it. That half second is what
        makes the first image an event instead of a title.
        """
        h = self.perf.height
        if t < 0.55:
            out["blank"] = True
            out["churn"] = 1.0
            out["palette"] = "floodlit"
            return

        out["churn"] = 1.0
        out["palette"] = "floodlit"
        # A vignette that is closing, not a mask that is nearly shut: at 0.10 the
        # aperture swallowed three quarters of the frame and the shot read as a
        # broken render rather than a tunnel.
        out["tunnel"] = 1.0 - 0.50 * ease_in_out(clamp((t - 0.55) / 0.80))

        gait = self.perf.walk
        x = -h * 0.30 + h * 0.26 * ease_in_out(clamp((t - 0.55) / 4.4))
        phase = ((t - 0.55) * 470.0 / gait.D) % 1.0
        out["hero"] = _walk(self.perf, gait, x, phase, facing=-1.0,
                            head_tilt=-0.03)

        if t < 2.10:                        # A: the slit, far away
            _aim(out, x, zoom=0.62, ground_row=0.72, tilt=0.055, lead=h * 0.10,
                 goal_d=46.0, frac=0.62, show_goal=True)
        elif t < 3.40:                      # B: cut in on the aperture
            _aim(out, x, zoom=1.18, ground_row=0.78, tilt=0.070, lead=h * 0.08,
                 goal_d=44.0, frac=0.64, show_goal=True)
        else:                               # C: the figure fills the mouth
            _aim(out, x, zoom=1.92, head_row=0.42, tilt=0.030, lead=h * 0.06,
                 goal_d=42.0, frac=0.66, show_goal=True)

        out["face"] = F.FOCUS.at(brow_raise=-0.30, sweat=0.10)
        out["light"] = 0.10 + 0.30 * clamp(t / 4.4)

    # -- 2. the walk --------------------------------------------------------

    def _shot_walk(self, out, t, dur, u):
        """Three setups: the stand, the boots, the face.

        The silence starts on the frame *before* the footfall at seven point nine
        lands. Starting it on the contact frame reads as a cue; starting it a frame
        early reads as a room emptying.
        """
        h = self.perf.height
        gait = self.perf.walk
        speed = 620.0
        x = -h * 0.55 + speed * t
        phase = (t * speed / gait.D) % 1.0
        out["hero"] = _walk(self.perf, gait, x, phase, facing=-1.0)

        if t < 2.0:                         # A: the stand towers over him
            _aim(out, x, zoom=1.02, ground_row=0.76, tilt=0.050, lead=h * 0.30,
                 goal_d=40.0, frac=0.86, show_goal=True, show_pylons=True)
        elif t < 4.6:                       # B: down at the boots
            _aim(out, x, zoom=2.60, ground_row=0.58, tilt=0.010, lead=h * 0.09,
                 goal_d=36.0, frac=1.05)
        else:                               # C: the face, still walking
            _aim(out, x, zoom=3.10, head_row=0.42, tilt=0.020, lead=h * 0.02,
                 goal_d=34.0, frac=1.30)

        k = clamp((t - (GRASS_STEP - 5.0 - 0.35)) / 0.75)
        out["churn"] = 0.96 * (1.0 - smoothstep(k)) ** 1.25
        out["palette"] = "hush" if k > 0.55 else "floodlit"
        blink = max(_blink(t, 3.1, 0.4), _blink(t, 4.6, 2.2) * 0.9)
        out["face"] = (F.CALM.blended(F.FOCUS, 0.55 * smoothstep(clamp(t / 4.5)))
                       .at(blink=blink, sweat=0.16 * clamp((t - 3.0) / 4.0)))
        out["light"] = 0.30

    # -- 3. the warm-up -----------------------------------------------------

    def _shot_warm(self, out, t, dur, u):
        """Two touches, and the second one is a disaster.

        The failure is the point: a film about a man under pressure has to show him
        beaten by something small before the thing that matters, or the pressure is
        a claim rather than a demonstration.
        """
        h = self.perf.height
        x = SPOT_X - h * 0.34
        out["palette"] = "hush"
        out["churn"] = 0.0

        if t < 3.4:                         # A: wide, the ball at his feet
            _aim(out, x, zoom=1.50, ground_row=0.86, tilt=0.030, lead=h * 0.12,
                 goal_d=30.0, frac=1.34)
        elif t < 5.2:                       # B: down on the bad touch
            _aim(out, x, zoom=2.00, ground_row=0.75, tilt=0.014, lead=h * 0.15,
                 goal_d=28.0, frac=1.20)
        else:                               # C: the face after it
            _aim(out, x, zoom=2.45, head_row=0.42, tilt=0.020, lead=h * 0.03,
                 goal_d=26.0, frac=1.40)

        ball = None
        if 1.6 <= t < 4.6:
            bx, by = self._juggles(t - 1.6, x + h * 0.30, h)
            ball = self._ball(bx, by)
        elif 4.6 <= t:
            bt = t - 4.6
            vx, vy = 250.0, -430.0
            bx = x + h * 0.30 + vx * bt
            by = -0.62 * h + vy * bt + 0.5 * GRAVITY * bt * bt
            if by > -BALL_R * h:
                by = -BALL_R * h
            ball = self._ball(bx, by)

        lunging = 5.0 <= t < 7.0
        if lunging:
            k = smoothstep(clamp((t - 5.0) / 0.5))
            hands = [np.array([x + h * 0.36, -h * 0.40]),
                     np.array([x + h * 0.12, -h * 0.46])]
            pose = _stand(self.perf, x + h * 0.05 * k, facing=1.0, breath_t=t,
                          lean=0.30 * k, head_tilt=0.12 * k, crouch=0.26 * k,
                          hands=hands)
        else:
            hands = None
            if 1.6 <= t < 4.6:
                raise_ = math.sin(math.pi * clamp((t - 1.6) / 3.0))
                hands = [np.array([x + h * 0.22, -h * (0.60 + 0.10 * raise_)]),
                         np.array([x + h * 0.02, -h * (0.58 + 0.08 * raise_)])]
            pose = _stand(self.perf, x, facing=1.0, breath_t=t, hands=hands,
                          head_tilt=0.02 + 0.05 * math.sin(t * 0.7),
                          crouch=0.10 if hands is not None else 0.0)

        out["hero"] = pose
        out["ball"] = ball

        expr = F.CALM.at(brow_raise=0.10)
        if lunging:
            expr = F.FEAR.blended(F.SHOCK, 0.35)
        elif 7.0 <= t < 8.4:
            expr = F.DISDAIN.at(sweat=0.24)
        elif t >= 8.4:
            expr = F.GRIT.blended(F.FOCUS, 0.55)
        out["face"] = expr.at(blink=_blink(t, 3.7, 0.9) * (0.0 if lunging else 1.0),
                              sweat=0.10 + 0.18 * clamp((t - 6.0) / 2.0))
        out["light"] = 0.28

    # -- 4. the set ---------------------------------------------------------

    def _shot_set(self, out, t, dur, u):
        """Place the ball, stand up, and then give the eyes a setup of their own."""
        h = self.perf.height
        x = SPOT_X - h * 0.24
        out["palette"] = "hush"
        out["churn"] = 0.0

        if t < 2.2:                         # A: the hand and the ball
            _aim(out, x, zoom=2.10, ground_row=0.80, tilt=0.010, lead=h * 0.10,
                 goal_d=26.0, frac=1.10)
        elif t < 5.4:                       # B: he stands up
            push = ease_in_out(clamp((t - 2.2) / 3.2))
            _aim(out, x, zoom=1.62 + 0.34 * push, ground_row=0.88, tilt=0.030,
                 lead=h * 0.14, goal_d=28.0, frac=1.34)
        else:                               # C: the eyes
            push = ease_in_out(clamp((t - 5.4) / 3.6))
            _aim(out, x, zoom=2.70 + 0.95 * push, head_row=0.42,
                 tilt=0.020, lead=h * 0.02, goal_d=26.0, frac=1.40)

        if t < 3.2:
            k = smoothstep(clamp(t / 3.2))
            pose = _stand(self.perf, x, facing=1.0, breath_t=t,
                          crouch=0.46 * (1.0 - k), lean=0.18 * (1.0 - k),
                          head_tilt=0.24 * (1.0 - k))
        else:
            pose = _stand(self.perf, x, facing=1.0, breath_t=t,
                          head_tilt=-0.02 - 0.05 * math.sin(t * 0.5))

        out["hero"] = pose
        out["ball"] = self._ball(SPOT_X + h * 0.14, -BALL_R * h)

        expr = F.FOCUS.at(eye_open=0.82, sweat=0.22)
        if t > 6.0:
            expr = F.FOCUS.blended(F.GRIT, smoothstep(clamp((t - 6.0) / 1.6)))
        if t < 5.0:
            expr = expr.at(blink=_blink(t, 4.2, 1.3))
        out["face"] = expr
        out["light"] = 0.26

    # -- 5. the strike ------------------------------------------------------

    def _shot_kick(self, out, t, dur, u):
        """Run-up, plant, contact -- three setups before the ball moves."""
        h = self.perf.height
        g = out["t"]
        out["palette"] = "hush"
        out["churn"] = 0.0
        st = self._kick_clock(t)

        # Where the man is, solved rather than guessed: the first assembly aimed at a
        # fixed x and left him a third of the frame away from his own run-up, small
        # and at the edge, for three seconds.
        if st < self.CONTACT_AT:
            hx = -h * 1.30 + h * 1.34 * ease_in_out(clamp(st / self.CONTACT_AT))
        else:
            hx = h * 0.02 + h * 0.10 * smoothstep(
                clamp((st - self.CONTACT_AT) / 0.6))

        if g < 34.0:                        # A: the run-up, from the side
            _aim(out, hx, zoom=1.58, ground_row=0.80, tilt=0.030, lead=h * 0.24,
                 goal_d=38.0, frac=0.62, show_goal=True)
        elif g < 36.0:                      # B: closer, still moving
            _aim(out, hx, zoom=1.95, ground_row=0.76, tilt=0.030, lead=h * 0.12,
                 goal_d=38.0, frac=0.62, show_goal=True)
        else:                               # C: the plant and the ball
            _aim(out, hx, zoom=3.10, ground_row=0.70, tilt=0.020, lead=h * 0.03,
                 goal_d=38.0, frac=0.62, show_goal=True)

        pose, expr, ball_x, ball_y, z_goal = self._kick_frame(st, h, out)
        out["hero"] = pose
        out["face"] = expr.at(blink=0.0)
        out["ball"] = self._ball(ball_x, ball_y,
                                 z=z_goal if st > self.CONTACT_AT else 1.0)
        out["light"] = 0.27 if st < self.CONTACT_AT else 0.34
        out["keeper"] = (None if g >= 36.0 else
                         self._keeper(st, h, out["origin"], z_goal,
                                      dive_at=self.CONTACT_AT))

        if st >= self.CONTACT_AT:
            out["strike_e"] = st - self.CONTACT_AT
            out["shake"] = (_shake(g, CONTACT, amp=7.5, decay=0.34, freq=14.0),
                            _shake(g, CONTACT, amp=5.0, decay=0.26, freq=19.0))
            out["flash"] = 0.78 * clamp(1.0 - (g - CONTACT) / 0.070)

    def _kick_clock(self, t):
        """The shot's own time: full speed to contact, then a third of it."""
        if t < self.CONTACT_AT:
            return t
        return self.CONTACT_AT + (t - self.CONTACT_AT) / 3.0

    def _kick_frame(self, st, h, out):
        """The body and the ball at story time ``st`` inside the strike.

        Shared with the replay, which is the same half second of story time seen
        from somewhere else -- so the two shots cannot drift apart.
        """
        z_goal = z_of(out["goal_d"])
        contact_at = self.CONTACT_AT
        bz = None
        if st < contact_at:
            k = clamp(st / contact_at)
            gait = self.perf.walk
            phase = (st * 1.9) % 1.0
            x = -h * 1.30 + h * 1.34 * ease_in_out(k)
            pose = _walk(self.perf, gait, x, phase, facing=1.0,
                         lean_extra=0.16 * k)
            if st > contact_at - 0.30:
                swing = smoothstep(clamp((st - (contact_at - 0.30)) / 0.30))
                pose = build_pose(
                    (x, -pelvis_height(h, 0.16)),
                    h, facing=1.0, lean=0.18, curl=0.10, head_tilt=0.06,
                    foot_near=np.array([x + h * 0.30, 0.0]),
                    foot_far=np.array([x + h * (0.34 + 0.40 * swing), 0.0]),
                    pitch_near=0.0, pitch_far=0.55 * swing,
                    hand_near=np.array([x - h * 0.36, -h * 0.50]),
                    hand_far=np.array([x + h * 0.24, -h * 0.60]))
            expr = F.GRIT if st > contact_at - 0.9 else F.FOCUS
            bx, by = SPOT_X + h * 0.30, -BALL_R * h
        else:
            e = st - contact_at
            k = smoothstep(clamp(e / 0.6))
            x = h * 0.02 + h * 0.10 * k
            pose = build_pose(
                (x, -pelvis_height(h, lerp(0.16, 0.30, k))),
                h, facing=1.0, lean=lerp(0.18, -0.10, k), curl=0.10,
                head_tilt=lerp(0.06, -0.18, k),
                foot_near=np.array([x + h * 0.28, 0.0]),
                foot_far=np.array([x + h * (0.70 - 0.24 * k), -h * 0.10 * k]),
                pitch_near=0.0, pitch_far=lerp(0.55, 0.30, k),
                hand_near=np.array([x - h * 0.42, -h * 0.42]),
                hand_far=np.array([x + h * 0.32, -h * 0.68]))
            expr = F.GRIT.blended(F.JOY, 0.22 * k)
            bx, by, bz = self._strike(e, h, out["origin"], z_goal)
        return pose, expr, bx, by, (bz if bz is not None else 1.0)

    def _keeper(self, st, h, goal_x, z_goal, *, dive_at=None):
        """A silhouette on the line: shifting, then going the wrong way."""
        if st < 3.6:
            return None
        k = clamp((st - 3.6) / 1.2)
        sway = math.sin(st * 2.1) * h * 0.06
        crouch = 0.10 + 0.12 * k
        lean = -0.04
        hands = None
        if dive_at is not None and st > dive_at:
            e = st - dive_at
            gk = smoothstep(clamp(e / 0.45))
            lean = -0.04 - 0.55 * gk
            crouch = 0.10 + 0.12 * k + 0.24 * gk
            hands = [np.array([goal_x + h * (0.10 + 0.62 * gk), -h * (0.60 + 0.12 * gk)]),
                     np.array([goal_x + h * (0.02 + 0.34 * gk), -h * (0.56 + 0.18 * gk)])]
            sway = sway * (1.0 - gk)
        return _stand(self.perf, goal_x + sway * k, facing=-1.0, breath_t=st,
                      lean=lean, crouch=crouch, hands=hands, tone="silhouette")

    # -- 6. the roar --------------------------------------------------------

    def _shot_roar(self, out, t, dur, u):
        """The sound comes back, and this time it stays.

        Three setups, and the last one is the only wide in the film with nothing in
        it but a man and a full stand -- which is the picture the whole ninety
        seconds has been paying for.
        """
        h = self.perf.height
        out["churn"] = 0.18 + 0.82 * smoothstep(clamp(t / 1.5))
        out["palette"] = "floodlit" if t > 0.6 else "hush"
        x = SPOT_X - h * 0.06

        if t < 1.7:                         # A: the net, still moving
            _aim(out, x, zoom=1.12, ground_row=0.78, tilt=0.030, lead=h * 0.16,
                 goal_d=36.0, frac=0.70, show_goal=True, show_pylons=True)
        elif t < 4.3:                       # B: him, arms out
            _aim(out, x, zoom=2.05, head_row=0.34, tilt=0.020, lead=h * 0.04,
                 goal_d=34.0, frac=1.30)
        else:                               # C: the wide
            _aim(out, x, zoom=0.94, ground_row=0.70, tilt=0.042, lead=h * 0.10,
                 goal_d=44.0, frac=0.78, show_goal=True, show_pylons=True)

        k = smoothstep(clamp((t - 0.35) / 0.9))
        # Arms go out and up, not out and in: at 0.42 the elbows bent them back into
        # a shrug, which is a different emotion entirely.
        hands = [np.array([x + h * (0.20 + 0.46 * k), -h * (0.66 + 0.22 * k)]),
                 np.array([x - h * (0.16 + 0.44 * k), -h * (0.68 + 0.16 * k)])]
        out["hero"] = _stand(self.perf, x, facing=-1.0, breath_t=t,
                             lean=-0.07 * k, head_tilt=-0.12 * k, crouch=0.03,
                             hands=hands)
        expr = F.SHOCK.blended(F.JOY, smoothstep(clamp((t - 0.30) / 0.8)))
        out["face"] = expr.at(blink=0.0, sweat=0.30)
        out["ball"] = None
        out["light"] = 0.30 + 0.34 * out["churn"]

    # -- 7. the replay ------------------------------------------------------

    def _shot_replay(self, out, t, dur, u):
        """The contact again, from behind the ball, at a fifth of speed.

        Same story clock as the strike -- `_kick_frame` -- so the boot and the ball
        cannot disagree. Only the lens moved.
        """
        h = self.perf.height
        out["palette"] = "hush"
        out["churn"] = 0.35 + 0.10 * math.sin(t * 3.0)

        st = (self.CONTACT_AT - 0.50) + t * 0.20
        out["goal_d"] = 38.0
        out["show_goal"] = True
        out["show_pylons"] = False
        out["origin"] = _place_goal(2.10, 0.34, h * 0.10, out["goal_d"])
        out["cam"] = cam(x=h * 0.10,
                         eye=_eye_for_row(0.86, 2.10, wy=0.0, tilt=0.060),
                         zoom=2.10 - 0.10 * clamp(t / 9.0), tilt=0.060)

        pose, expr, bx, by, z_goal = self._kick_frame(st, h, out)
        out["hero"] = pose
        out["face"] = expr.at(blink=0.0)
        out["ball"] = self._ball(bx, by, z=z_goal if st > self.CONTACT_AT else 1.0)
        # No keeper in the replay: at this zoom a diving silhouette reads as a
        # black shape standing beside him rather than as a man going the wrong way.
        out["keeper"] = None
        out["light"] = 0.30
        if st > self.CONTACT_AT:
            out["strike_e"] = st - self.CONTACT_AT

    # -- 8. the turn --------------------------------------------------------

    def _shot_turn(self, out, t, dur, u):
        """He looks at us, winks, and shuts the crowd up with one finger.

        The wink is the only authored thing in the film: there is no physics in
        eyelids, and a solve would be a model of a face rather than a face.
        """
        h = self.perf.height
        x = SPOT_X - h * 0.10
        out["goal_d"] = 30.0
        out["show_goal"] = False
        out["show_pylons"] = False
        out["origin"] = _place_goal(2.0, 1.34, x, out["goal_d"])

        turn = smoothstep(clamp((t - 3.8) / 1.6))
        facing = lerp(1.0, -1.0, turn)
        wink = _wink(t, WINK - 58.0, hold=0.36, rise=0.10)
        shush = smoothstep(clamp((t - (SHUSH - 58.0)) / 0.5))

        out["churn"] = 1.0
        if t > (SHUSH - 58.0) - 0.2:
            out["churn"] = 1.0 - 0.72 * smoothstep(
                clamp((t - (SHUSH - 58.0) + 0.2) / 0.9))
        if t > 12.4:
            out["churn"] = 0.28 + 0.72 * smoothstep(clamp((t - 12.4) / 1.5))
        out["palette"] = "floodlit"

        if t < 3.8:                         # A: breathing, crowd on top of him
            _aim(out, x, zoom=1.52, ground_row=0.88, tilt=0.028, lead=h * 0.14,
                 goal_d=30.0, frac=1.34)
        elif t < 7.2:                       # B: he turns into the lens
            _aim(out, x, zoom=2.10 + 0.30 * turn, head_row=0.40, tilt=0.020,
                 lead=h * 0.10, goal_d=28.0, frac=1.36)
        elif t < 9.4:                       # C: the wink
            _aim(out, x, zoom=2.95, head_row=0.42, tilt=0.016, lead=h * 0.02,
                 goal_d=26.0, frac=1.40)
        elif t < 12.2:                      # D: the finger
            _aim(out, x, zoom=2.35, head_row=0.44, tilt=0.016, lead=h * 0.05,
                 goal_d=26.0, frac=1.38)
        else:                               # E: the smirk
            _aim(out, x, zoom=1.95, head_row=0.38, tilt=0.020, lead=h * 0.08,
                 goal_d=28.0, frac=1.36)

        hands = None
        if shush > 0.0:
            # The finger goes to the mouth and stays there: one hand, one gesture.
            mouth = np.array([x + h * 0.085, -h * 0.792])
            hands = [mouth + np.array([h * 0.01, h * 0.020]),
                     np.array([x - h * 0.13, -h * 0.34])]
        out["hero"] = _stand(self.perf, x, facing=max(0.10, facing), breath_t=t,
                             head_tilt=-0.02 - 0.10 * turn + 0.03 * shush,
                             hands=hands)

        expr = F.BREATH.at(sweat=0.30)
        if t > 2.4:
            expr = F.RELIEF.blended(F.BREATH, 0.4)
        if t > 5.4:
            expr = F.CALM.blended(F.DIRECT, smoothstep(clamp((t - 5.4) / 1.6)))
        if t > 9.6:
            expr = F.DIRECT.at(
                mouth_curve=0.10 + 0.34 * smoothstep(clamp((t - 9.6) / 1.0)),
                brow_raise=0.30)
        expr = expr.at(wink=wink,
                       mouth_curve=expr.mouth_curve + 0.45 * wink,
                       brow_raise=expr.brow_raise + 0.25 * wink,
                       blink=_blink(t, 5.0, 2.4) * (1.0 if 0.4 < t < 3.4 else 0.0))
        out["face"] = expr
        out["light"] = 0.30 + 0.34 * out["churn"]

    # -- 9. the walk-off ----------------------------------------------------

    def _shot_walkoff(self, out, t, dur, u):
        """He comes at the lens and the aperture closes on him.

        No cut in this one, and no cut is the point: after eleven setups in seventy
        seconds the last thing the film should do is stop moving the camera.
        """
        h = self.perf.height
        x = SPOT_X - h * 0.10
        out["goal_d"] = 28.0
        out["show_goal"] = False
        out["show_pylons"] = False
        out["churn"] = 1.0
        out["palette"] = "floodlit"

        push = ease_in_out(clamp(t / 9.6))
        zoom = 1.90 + 2.10 * push
        out["origin"] = _place_goal(zoom, 1.36, x + h * 0.06, out["goal_d"])
        tilt = 0.030 + 0.030 * push
        out["cam"] = cam(x=x + h * 0.06,
                         eye=_eye_for_row(0.42 - 0.06 * push, zoom, tilt=tilt),
                         zoom=zoom, tilt=tilt)
        out["tunnel"] = smoothstep(clamp((t - 6.6) / 2.6)) * 0.90

        out["hero"] = _stand(self.perf, x, facing=-1.0, breath_t=t, crouch=0.03,
                             head_tilt=-0.03)
        out["face"] = F.DIRECT.at(mouth_curve=0.42, brow_raise=0.24,
                                  sweat=0.26 * (1.0 - clamp(t / 4.0)))
        out["light"] = 0.30 + 0.30 * out["churn"]

    # -- 10. the card -------------------------------------------------------

    def _shot_endcard(self, out, t, dur, u):
        """Black. The last sound in the film is a crowd that is still there."""
        out["blank"] = True
        out["churn"] = 0.0
        out["palette"] = "floodlit"

    # -- helpers ------------------------------------------------------------

    # Contact inside the strike shot, in story seconds, plus how long the ball is
    # in the air and how high it is when it reaches the net.
    CONTACT_AT = 6.30
    FLIGHT = 0.55
    NET_Y = -0.55

    def _strike(self, e, h, goal_x, z_goal):
        """The struck ball a time ``e`` after contact.

        Height is a real ballistic, with the one free parameter -- the launch
        velocity -- solved from where the ball has to be when it arrives. A
        hand-shaped arc was the first version and it is the sort of thing that
        looks fine for two seconds and wrong for ten: the ball hangs, then drops.
        """
        T = self.FLIGHT
        f = clamp(e / T)
        y0 = -0.30 * h
        y1 = self.NET_Y * h
        vy = (y1 - y0 - 0.5 * GRAVITY * T * T) / T
        by = y0 + vy * e + 0.5 * GRAVITY * e * e
        if f >= 1.0:
            by = y1
        bz = lerp(1.0, z_goal, f)
        bx = lerp(SPOT_X + h * 0.30, goal_x, f)
        return bx, by, bz

    def _juggles(self, t, x, h):
        """A ball played on the knee. Solved ballistics, damped each contact."""
        H0 = 0.30 * h
        T = 2.0 * math.sqrt(2.0 * H0 / GRAVITY)
        n = t / T
        i = int(n)
        f = n - i
        amp = H0 * (0.86 ** i)
        # Minus, because world y grows downward: a ball on the way up has an
        # increasingly negative y.
        y = -(0.62 * h) - 4.0 * amp * f * (1.0 - f)
        return x, y
