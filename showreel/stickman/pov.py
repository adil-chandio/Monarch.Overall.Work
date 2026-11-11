"""POV: the stadium goes quiet -- the film.

Ninety seconds, six shots, one figure, one ball, one keeper, one crowd.

The spine is a single idea, and every shot serves it: **the crowd is loud, then it
is not, then it is.** Everything else is a man walking to a penalty spot.

    0       7    cold open      a slit of light at the end of a tunnel
        7  24    the walk       he steps onto the grass and the sound stops
       24  41    the warm-up    two touches, one of them wrong
       41  58    the set        he looks at the goal for a long time
       58  71    the strike     run-up, plant, contact
       71  90    the turn       the net settles; he looks down the lens

Three rules the shots obey.

**The sound is shown, not heard.** There is no audio in this cut, so the crowd has
to be visible: ``churn`` is how much the stand moves, and it is the film's only
loudness control. At churn 0 the stand is a photograph and the silence is total.
That is also why the palette cools with it -- a silent stadium and a loud one
cannot be the same colour.

**Time is animation time, not wall time.** The strike is in slow motion because the
shot warps its own clock. The rig is still solved at true gravity inside the warp,
so the ball is slow rather than floaty; stretching the render instead would only
have made a low frame rate.

**The goal is placed, not found.** The projection has depth and one lateral axis,
so the only way to put the goal off to one side of the frame -- rather than
directly behind the hero -- is to slide the whole set along x. That is what
``_place_goal`` does, and it is also why a true side-on view of a pitch is not
representable here.
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
    ("cold", 0.0, 7.0),
    ("walk", 7.0, 24.0),
    ("warm", 24.0, 41.0),
    ("set", 41.0, 58.0),
    ("kick", 58.0, 71.0),
    ("turn", 71.0, TOTAL),
)

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
    """A blink long enough to survive 24 fps.

    0.14 s is 3.4 frames, so at least two frames land inside it. A 0.08 s blink
    falls between frames and simply does not happen.
    """
    u = ((t + phase) % period) / dur
    if u >= 1.0:
        return 0.0
    return math.sin(math.pi * u) ** 0.7


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
        """A slit of light with a stadium at the end of it.

        The only shot where he is backlit. He is a black shape in the aperture and
        the noise is a wall he has not stepped through yet.
        """
        h = self.perf.height
        out["tunnel"] = 1.0 - ease_in_out(clamp((u - 0.10) / 0.90)) * 0.90
        out["show_goal"] = True
        out["show_pylons"] = True
        out["churn"] = 0.50 + 0.50 * clamp(u * 1.5)
        out["palette"] = "floodlit"
        out["goal_d"] = 46.0

        zoom = 0.58 + 0.20 * ease_in_out(u)
        cx = h * 0.06
        out["cam"] = cam(x=cx, eye=0.255, zoom=zoom, tilt=0.075)
        out["origin"] = _place_goal(zoom, 0.62, cx, out["goal_d"])

        gait = self.perf.walk
        x = -h * 0.30 + h * 0.44 * ease_in_out(u)
        pose = _walk(self.perf, gait, x, u * dur / gait.period_for_speed(560.0),
                     facing=1.0, head_tilt=-0.04)
        out["hero"] = pose
        out["face"] = F.FOCUS.at(brow_raise=-0.28)
        out["light"] = 0.08 + 0.34 * u

    # -- 2. the walk --------------------------------------------------------

    def _shot_walk(self, out, t, dur, u):
        """He steps onto the grass and the sound is gone.

        The silence starts on the frame *before* the first footfall lands. Starting
        it on the contact frame reads as a cue; starting it a frame early reads as
        a room emptying.
        """
        h = self.perf.height
        gait = self.perf.walk
        speed = 620.0
        phase = (t * speed / gait.D) % 1.0
        x = -h * 0.55 + speed * t
        out["goal_d"] = 40.0
        out["show_goal"] = True
        out["show_pylons"] = True

        zoom = 1.02
        cx = x + h * 0.30
        out["cam"] = cam(x=cx, eye=0.250, zoom=zoom, tilt=0.055)
        out["origin"] = _place_goal(zoom, 0.86, cx, out["goal_d"])

        out["hero"] = _walk(self.perf, gait, x, phase, facing=1.0)
        k = clamp((t - 0.35) / 1.6)
        out["churn"] = 0.95 * (1.0 - smoothstep(k)) ** 1.3
        out["palette"] = "hush" if k > 0.72 else "floodlit"
        blink = max(_blink(t, 3.1, 0.4), _blink(t, 4.9, 2.2) * 0.9)
        out["face"] = F.CALM.blended(F.FOCUS, 0.5 * smoothstep(clamp(t / 7.0))) \
                         .at(blink=blink)
        out["light"] = 0.30

    # -- 3. warm-up ---------------------------------------------------------

    def _shot_warm(self, out, t, dur, u):
        """Two touches, one of them wrong.

        The failure is not decoration: a film about a man under pressure has to
        show him beaten by something small before the thing that matters, or the
        pressure is a claim rather than a demonstration.
        """
        h = self.perf.height
        x = SPOT_X - h * 0.34
        out["goal_d"] = 30.0
        # Framed out: this is a medium, and the goal is behind the lens's right
        # edge. Turning it off is the honest description of that framing.
        out["show_goal"] = False
        out["show_pylons"] = False

        zoom = 1.48 + 0.06 * u
        cx = x + h * 0.12
        out["cam"] = cam(x=cx, eye=0.250, zoom=zoom, tilt=0.030)
        out["origin"] = _place_goal(zoom, 1.34, cx, out["goal_d"])

        ball = None
        if 4.4 <= t < 7.6:
            bx, by = self._juggles(t - 4.4, x + h * 0.30, h)
            ball = self._ball(bx, by)
        elif 7.6 <= t < 12.4:
            bt = t - 7.6
            vx, vy = 300.0, -520.0
            bx = x + h * 0.30 + vx * bt
            by = -0.62 * h + vy * bt + 0.5 * GRAVITY * bt * bt
            if by > -BALL_R * h:
                by = -BALL_R * h
            ball = self._ball(bx, by)

        lunging = 7.9 <= t < 9.8
        if lunging:
            k = smoothstep(clamp((t - 7.9) / 0.6))
            hands = [np.array([x + h * 0.36, -h * 0.40]),
                     np.array([x + h * 0.12, -h * 0.46])]
            pose = _stand(self.perf, x + h * 0.05 * k, facing=1.0, breath_t=t,
                          lean=0.30 * k, head_tilt=0.12 * k, crouch=0.26 * k,
                          hands=hands)
        else:
            hands = None
            if 4.4 <= t < 7.6:
                # Hands up, ready to play the ball back.
                raise_ = math.sin(math.pi * clamp((t - 4.4) / 3.2))
                hands = [np.array([x + h * 0.22, -h * (0.60 + 0.10 * raise_)]),
                         np.array([x + h * 0.02, -h * (0.58 + 0.08 * raise_)])]
            pose = _stand(self.perf, x, facing=1.0, breath_t=t, hands=hands,
                          head_tilt=0.02 + 0.05 * math.sin(t * 0.7),
                          crouch=0.10 if hands is not None else 0.0)

        out["hero"] = pose
        out["ball"] = ball
        out["churn"] = 0.0
        out["palette"] = "hush"

        expr = F.CALM.at(brow_raise=0.10)
        if lunging:
            expr = F.FEAR.blended(F.SHOCK, 0.35)
        elif 9.8 <= t < 11.6:
            expr = F.DISDAIN.at(sweat=0.22)
        elif t >= 11.6:
            expr = F.GRIT.blended(F.FOCUS, 0.5)
        out["face"] = expr.at(blink=_blink(t, 3.7, 0.9) * (0.0 if lunging else 1.0))
        out["light"] = 0.28

    # -- 4. the set ---------------------------------------------------------

    def _shot_set(self, out, t, dur, u):
        """The long look. Almost nothing happens, and that is the shot.

        One action -- set the ball down, stand up, look at the goal -- and one
        camera move, from a medium to a close, so the last seconds are the eyes and
        nothing else.
        """
        h = self.perf.height
        x = SPOT_X - h * 0.24
        out["goal_d"] = 30.0
        out["show_goal"] = False
        out["show_pylons"] = False

        push = ease_in_out(clamp((u - 0.30) / 0.70))
        zoom = 1.42 + 1.55 * push
        cx = x + h * (0.20 - 0.14 * push)
        out["cam"] = cam(x=cx, eye=0.250, zoom=zoom, tilt=0.028 + 0.012 * push)
        out["origin"] = _place_goal(zoom, 1.34, cx, out["goal_d"])

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
        out["churn"] = 0.0
        out["palette"] = "hush"

        expr = F.FOCUS.at(eye_open=0.82)
        if t > 12.0:
            expr = F.FOCUS.blended(F.GRIT, smoothstep(clamp((t - 12.0) / 1.4)))
        if t < 10.0:
            expr = expr.at(blink=_blink(t, 4.2, 1.3))
        out["face"] = expr
        out["light"] = 0.26

    # -- 5. the strike ------------------------------------------------------

    def _shot_kick(self, out, t, dur, u):
        """Run-up, plant, contact -- then the ball is somebody else's problem."""
        h = self.perf.height
        # The goal is placed far enough that it fits in the frame with its posts,
        # because a goal that only fits its net does not read as a goal. The cost
        # is that the strike is from further out than a penalty spot; the set is a
        # depth model with one lateral axis and this is the honest way to frame it.
        out["goal_d"] = 38.0
        out["show_goal"] = True
        out["show_pylons"] = False

        # The shot's own clock. Everything up to contact runs at speed; from
        # contact it slows to a third, which is where the film slows down.
        contact_at = 6.30
        slow_from = contact_at
        if t < slow_from:
            st = t
        else:
            st = slow_from + (t - slow_from) / 3.2

        zoom = 0.86 + 0.14 * u
        cx = -h * 0.30 + h * 0.62 * clamp(st / contact_at)
        out["cam"] = cam(x=cx, eye=0.248, zoom=zoom, tilt=0.032)
        out["origin"] = _place_goal(zoom, 0.62, cx, out["goal_d"])
        z_goal = z_of(out["goal_d"])

        grip = st < contact_at
        if grip:
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

        # -- the ball: leaves the spot, arrives at the goal
        if st < contact_at:
            ball = self._ball(SPOT_X + h * 0.30, -BALL_R * h)
        else:
            ball = self._ball(*self._strike(st - contact_at, h, out["origin"],
                                            z_goal))

        out["hero"] = pose
        out["ball"] = ball
        out["churn"] = 0.0
        out["palette"] = "hush"
        out["face"] = expr.at(blink=0.0)
        out["light"] = 0.27 if grip else 0.34
        out["keeper"] = self._keeper(st, h, out["origin"], z_goal)

    def _keeper(self, st, h, goal_x, z_goal):
        """A silhouette on the line, shifting his weight.

        He is never the hero's rival in frame -- he is a shape at the far end of
        the pitch, which is what a keeper is from eleven metres.
        """
        if st < 3.6:
            return None
        k = clamp((st - 3.6) / 1.2)
        sway = math.sin(st * 2.1) * h * 0.06
        return _stand(self.perf, goal_x + sway * k, facing=-1.0, breath_t=st,
                      lean=-0.04, crouch=0.10 + 0.12 * k, tone="silhouette")

    # -- 6. the turn --------------------------------------------------------

    def _shot_turn(self, out, t, dur, u):
        """The net settles. The sound comes back. He looks at us."""
        h = self.perf.height
        out["goal_d"] = 32.0
        out["show_goal"] = False
        out["show_pylons"] = False

        k = clamp((t - 1.4) / 3.6)
        out["churn"] = smoothstep(k) ** 0.8 if t < 5.2 else 1.0
        out["palette"] = "floodlit" if t > 2.8 else "hush"

        turn = smoothstep(clamp((t - 6.0) / 2.0))
        facing = lerp(1.0, -1.0, turn)
        x = SPOT_X - h * 0.10

        push = ease_in_out(clamp((t - 4.8) / 6.5))
        zoom = 1.34 + 1.38 * push
        cx = x + h * (0.16 - 0.16 * turn)
        out["cam"] = cam(x=cx, eye=0.250, zoom=zoom, tilt=0.026 + 0.012 * push)
        out["origin"] = _place_goal(zoom, 1.34, cx, out["goal_d"])

        out["hero"] = _stand(self.perf, x, facing=max(0.08, facing), breath_t=t,
                             head_tilt=-0.02 - 0.12 * turn)
        out["ball"] = None

        expr = F.CALM.at(eye_open=0.9)
        if t > 1.6:
            expr = F.RELIEF.blended(F.CALM, clamp((t - 1.6) / 3.0))
        if t > 6.6:
            expr = F.DIRECT.at(blink=0.0)
        expr = expr.at(blink=_blink(t, 5.0, 2.4) * (1.0 if t < 8.6 else 0.0))
        out["face"] = expr
        out["light"] = 0.30 + 0.34 * out["churn"]

    # -- helpers ------------------------------------------------------------

    # The strike: how long the ball is in the air, in story seconds, and how high
    # it is when it reaches the net.
    FLIGHT = 0.55
    NET_Y = -0.55

    def _strike(self, e, h, goal_x, z_goal):
        """The struck ball's position a time ``e`` after contact.

        Height is a real ballistic: ``y = y0 + vy*e + g*e^2/2``, with the one free
        parameter -- the launch velocity -- solved from where the ball has to be
        when it arrives, rather than picked. Everything else (how far it has
        travelled and how far into the picture it has gone) is a ground track,
        which gravity does not touch.

        A hand-shaped arc was the first version and it is the sort of thing that
        looks fine for two seconds and wrong for ten: the ball hangs, then drops.
        """
        T = self.FLIGHT
        f = clamp(e / T)
        y0 = -0.30 * h
        y1 = self.NET_Y * h
        # Solve vy from y(T) = y1.
        vy = (y1 - y0 - 0.5 * GRAVITY * T * T) / T
        by = y0 + vy * e + 0.5 * GRAVITY * e * e
        if f >= 1.0:
            by = y1
        # Ground track: the ball travels toward the goal's lateral position and
        # away from the camera in step, so it shrinks into the net instead of
        # staying the size it left at.
        bz = lerp(1.0, z_goal, f)
        bx = lerp(SPOT_X + h * 0.30, goal_x, f)
        return bx, by, bz

    def _juggles(self, t, x, h):
        """A ball played on the knee. Solved ballistics, damped each contact."""
        # Peak height and period follow from the impulse: t = 2*sqrt(2H/g).
        H0 = 0.30 * h
        T = 2.0 * math.sqrt(2.0 * H0 / GRAVITY)
        n = t / T
        i = int(n)
        f = n - i
        amp = H0 * (0.86 ** i)
        # Minus, because world y grows downward: a ball on the way up has an
        # increasingly negative y. Adding this term made the ball sink below its
        # own starting height and come back, i.e. it bounced downward, which the
        # fit caught as a gravity of the wrong sign.
        y = -(0.62 * h) - 4.0 * amp * f * (1.0 - f)
        return x, y
