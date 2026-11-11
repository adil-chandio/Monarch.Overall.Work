"""The film: world-space performance, camera, and the frame loop.

World space is the character's plane: y = 0 is the floor, negative is up, and
one unit is one frame pixel at zoom 1. The figure is built and animated entirely
in those units, and the Projector is applied once at the end. That is why a
push-in separates the hills correctly: the figure and the scenery were never in
screen space to begin with.

Every performance here comes from one of three authorities:

    the gait      feet pinned in world space, so a planted foot cannot slide
    gravity       anything airborne follows a solved ballistic arc
    springs       every stop, landing and impact overshoots and settles

Nothing is keyframed by eye. If a motion looks wrong it has a cause, and the cause
is a number in this file.
"""

from __future__ import annotations

import math

import numpy as np

from .rig import P, build_pose, clamp, lerp, pelvis_height, smoothstep, ease_in_out
from .motion import Gait, settle

FPS = 24
W, H = 1080, 1920

FIG_H = 700.0        # figure height in world pixels
EYE = 0.285          # camera eye height, fraction of frame height


class Performer:
    """The figure plus its two gaits. Height is a world-space number."""

    def __init__(self, height=FIG_H):
        self.height = height
        # A walk has a foot down at all times; stance 0.62 leaves 38% of the
        # cycle in swing, which is why one foot is always loaded. The stride is
        # 0.53 because anything longer over-extends the leg at touchdown: see
        # Gait.max_stride, which derives that ceiling rather than guessing it.
        self.walk = Gait(height, stride=0.53, stance=0.62, lift=0.048,
                         bob=0.020, arm_swing=0.44, lean=0.055, hip_frac=0.940)
        # A run does not. Stance 0.34 means 32% of every cycle is airborne, so
        # the feet leave the ground -- which is the entire physical difference.
        self.run = Gait(height, stride=0.86, stance=0.34, lift=0.115,
                        bob=0.050, arm_swing=1.10, lean=0.175, hip_frac=0.905)

    # -- arms ---------------------------------------------------------------

    def arm_targets(self, phase, chest, swing, lean, *, up=0.0, spread=0.0):
        """Hand positions that swing opposite the legs and never lock straight.

        The hands are placed on an arc of radius 0.90 of full arm reach around
        the shoulder. Because the radius stays inside the reach, the IK always
        has a bend to find -- a target outside the reach makes the solver
        straighten the arm, which is what a scarecrow looks like. The arc is
        centred on "hanging down and a little forward" rather than on the
        vertical, so the arms clear the thighs instead of cutting through them.
        """
        h = self.height
        reach = (P["upper_arm"] + P["forearm"]) * h * 0.86
        out = []
        for sign in (+1.0, -1.0):
            # Base hang angle: down, tipped forward by a few degrees.
            base = math.pi * 0.5 - 0.10
            ang = base + swing * sign + lean * 0.35 - up
            out.append(chest + np.array([math.cos(ang) * reach,
                                         math.sin(ang) * reach]))
        return out


# ---------------------------------------------------------------- shot bodies
#
# Every shot returns (pose, cam_x, zoom, tilt, extra). ``extra`` carries
# one-shot effects such as an impact flash; it defaults to zero.

def shot_walk(t, dur, perf):
    """Establishing: the figure walks in from the left, already at speed."""
    h = perf.height
    g = perf.walk

    # Speed is integrated, not assumed, so the stride always matches it. The
    # phase is driven by distance, not time: change the speed and the cadence
    # changes, but no footfall is ever skipped.
    n = 10
    x = -0.95 * h
    for i in range(n):
        tt = t * (i + 1) / n
        x += (300.0 + 150.0 * smoothstep(clamp(tt / 1.6))) * (t / n)

    speed = 300.0 + 150.0 * smoothstep(clamp(t / 1.6))
    phase = (x / g.D) % 1.0

    hip_y = -pelvis_height(h) * g.hip_frac + g.hip_offset(phase)
    lean = g.lean + 0.030 * math.sin(2.0 * math.pi * phase)

    fn, pn = g.foot(phase, x, 0.0, side=0.0)
    ff, pf = g.foot(phase, x, 0.0, side=0.5)

    chest = np.array([x, hip_y - P["spine"] * h * 0.55])
    hands = perf.arm_targets(phase, chest, g.arm_swing, lean)

    pose = build_pose((x, hip_y), h, facing=1.0, lean=lean, curl=0.055,
                      foot_near=fn, foot_far=ff, pitch_near=pn, pitch_far=pf,
                      hand_near=hands[0], hand_far=hands[1])

    cam_x = x + h * 0.11
    zoom = lerp(1.00, 1.09, smoothstep(clamp(t / dur)))
    return pose, cam_x, zoom, 0.0


def shot_stop(t, dur, perf):
    """The walk decelerates. The body has to catch up with the feet."""
    h = perf.height
    g = perf.walk
    x = shot_stop.x0 if hasattr(shot_stop, "x0") else 0.0

    # Decelerating speed, integrated the same way the walk integrates.
    v0 = 450.0
    def speed_at(tt):
        return v0 * (1.0 - smoothstep(clamp(tt / (dur * 0.72))))

    n = 12
    x = 0.0
    for i in range(n):
        tt = t * (i + 1) / n
        x += speed_at(tt) * (t / n)

    u = clamp(t / dur)
    phase = (x / g.D) % 1.0
    # Plant: the feet stop travelling and settle under the body.
    plant = smoothstep(clamp((u - 0.66) / 0.34))

    hip_y = -pelvis_height(h) * lerp(1.0, 0.958, plant)
    hip_y += g.hip_offset(phase) * (1.0 - plant) * (1.0 - plant)

    lean = lerp(g.lean + 0.03 * math.sin(2 * math.pi * phase), 0.010, plant)
    # Weight arriving compresses the spine once and settles.
    hip_y += 2.5 * settle(max(0.0, t - dur * 0.72), frequency=3.0, damping=6.5)

    fn, pn = g.foot(phase, x, 0.0, side=0.0)
    ff, pf = g.foot(phase, x, 0.0, side=0.5)
    pn = lerp(pn, 0.0, plant)
    pf = lerp(pf, 0.0, plant)
    fn = np.array([lerp(fn[0], x + h * 0.085, plant), lerp(fn[1], 0.0, plant)])
    ff = np.array([lerp(ff[0], x - h * 0.055, plant), lerp(ff[1], 0.0, plant)])

    chest = np.array([x, hip_y - P["spine"] * h * 0.55])
    # Arms finish their swing and then hang, with the trailing one overshooting.
    ot = max(0.0, t - dur * 0.70)
    swing = g.arm_swing * (1.0 - plant) * (1.0 - plant)
    hands = perf.arm_targets(phase, chest, swing, lean)
    hands[0] = hands[0] + np.array([7.0 * settle(ot, frequency=2.1, damping=5.0), 0.0])
    hands[1] = hands[1] + np.array([-7.0 * settle(ot, frequency=2.1, damping=5.0), 0.0])

    pose = build_pose((x, hip_y), h, facing=1.0, lean=lean,
                      curl=0.055 + 0.045 * plant,
                      foot_near=fn, foot_far=ff, pitch_near=pn, pitch_far=pf,
                      hand_near=hands[0], hand_far=hands[1])

    zoom = lerp(1.06, 1.18, ease_in_out(clamp(u / 0.85)))
    return pose, x + h * 0.10, zoom, 0.0


shot_stop.x0 = 0.0


def shot_look(t, dur, perf):
    """A held stop, then the figure turns and looks back over its shoulder.

    The turn has to be legible on a figure with no face, so it is built from
    three cues at once rather than one: the head rotates past the spine, the
    spine rotates a little itself, and the near arm crosses the body. Any one of
    those alone reads as a twitch; together they read as a decision.
    """
    h = perf.height
    u = clamp(t / dur)

    x = 8.0 * smoothstep(u)            # a drift, so the hold is not a freeze
    hip_y = -pelvis_height(h) * 0.958 - 2.5 * smoothstep(clamp(u * 1.7))

    look = smoothstep(clamp((u - 0.26) / 0.38))
    head_tilt = -0.62 * look           # head goes well past the spine
    lean = -0.055 * look               # spine leans away from the look
    # A figure with no face turns its whole silhouette: the facing sign sets
    # which side the eye dot and the body's depth split sit on.
    facing = 1.0 - 0.35 * look

    fn = np.array([x + h * 0.085, 0.0])
    ff = np.array([x - h * 0.055, 0.0])

    chest = np.array([x, hip_y - P["spine"] * h * 0.55])
    hands = perf.arm_targets(0.0, chest, 0.0, lean)
    # The near hand comes up and across the chest as the figure turns.
    hands[0] = hands[0] + np.array([-h * 0.055 * look, -h * 0.105 * look])

    pose = build_pose((x, hip_y), h, facing=facing, lean=lean, curl=0.075,
                      head_tilt=head_tilt,
                      foot_near=fn, foot_far=ff, pitch_near=0.0, pitch_far=0.0,
                      hand_near=hands[0], hand_far=hands[1])

    zoom = lerp(1.16, 1.46, ease_in_out(smoothstep(clamp((u - 0.16) / 0.58))))
    return pose, x + h * 0.09, zoom, 0.0


class JumpRig:
    """A run-up, a ballistic flight and a landing that costs.

    Kept as an object because a jump is the one thing here that genuinely cannot
    be a pure function of ``t`` expressed in one line: the launch position, the
    flight time and the landing point are solved together and then evaluated.

    The flight is a real parabola. Given a horizontal speed and a flight time,
    the vertical launch velocity is whatever gravity requires to return to the
    floor exactly at the end. Nothing about the arc is eyeballed, so a longer
    flight automatically gets a higher apex and the hang time is honest.
    """

    def __init__(self, perf, *, run_up=1.15, apex_frac=0.52, run_speed=640.0):
        self.perf = perf
        self.h = perf.height
        self.g = perf.run
        self.run_up = run_up
        self.speed = run_speed
        g = 2900.0

        # Flight time is derived from the apex, not picked: for a rise h under
        # gravity g, the launch speed is sqrt(2gh) and the full flight (up and
        # back down) is 2*sqrt(2h/g). Chasing a flight time instead and hoping
        # the apex looks right is how a jump ends up a hop.
        self.apex = apex_frac * self.h
        self.flight = 2.0 * math.sqrt(2.0 * self.apex / g)
        self.total = run_up + self.flight

        self.x0 = -self.h * 0.95

    def state(self, t):
        """Return (pose, cam_x, zoom, tilt, airborne_height, x_on_ground)."""
        h = self.h
        g = self.g

        if t < self.run_up:
            # Accelerating run: speed ramps from a standstill to full.
            n = 12
            x = self.x0
            for i in range(n):
                tt = t * (i + 1) / n
                frac = clamp(tt / self.run_up)
                x += self.speed * (0.35 + 0.65 * smoothstep(frac)) * (t / n)
            frac = clamp(t / self.run_up)
            phase = ((x - self.x0) / g.D) % 1.0

            hip_y = -pelvis_height(h) * g.hip_frac + g.hip_offset(phase)
            lean = lerp(0.10, g.lean, smoothstep(frac))

            fn, pn = g.foot(phase, x, 0.0, side=0.0)
            ff, pf = g.foot(phase, x, 0.0, side=0.5)

            # The last stride becomes the launch: the take-off leg compresses.
            load = smoothstep(clamp((frac - 0.78) / 0.22))
            hip_y += h * 0.070 * load
            lean = lerp(lean, 0.30, load)

            chest = np.array([x, hip_y - P["spine"] * h * 0.52])
            hands = self.perf.arm_targets(phase, chest, g.arm_swing, lean)
            # Arms drive back on the last step: that is where the lift comes from.
            for i, sgn in enumerate((-1.0, +1.0)):
                hands[i] = hands[i] + np.array([sgn * -h * 0.10 * load,
                                                h * 0.06 * load])

            pose = build_pose((x, hip_y), h, facing=1.0, lean=lean, curl=0.075,
                              foot_near=fn, foot_far=ff, pitch_near=pn, pitch_far=pf,
                              hand_near=hands[0], hand_far=hands[1])
            zoom = lerp(1.13, 1.20, smoothstep(frac))
            return pose, x + h * 0.10, zoom, 0.0, 0.0, x


        if t < self.total:
            # Airborne.
            u = (t - self.run_up) / self.flight
            x_take = self.x0 + self.speed * self.run_up * 0.72
            x = x_take + self.speed * (t - self.run_up)

            # Height above the floor: a parabola that leaves and returns at zero.
            rise = 4.0 * self.apex * u * (1.0 - u)   # 0 at both ends, apex at u=0.5
            hip_y = -pelvis_height(h) - rise

            # Tuck on the way up, extend to meet the floor on the way down.
            tuck = math.sin(math.pi * clamp(u)) ** 0.75
            fn = np.array([x + h * 0.075, hip_y + h * (0.40 - 0.20 * tuck)])
            ff = np.array([x - h * 0.045, hip_y + h * (0.44 - 0.26 * tuck)])
            pn = lerp(-0.30, 0.32, u)
            pf = lerp(-0.14, 0.20, u)

            lean = lerp(0.26, 0.04, smoothstep(u))
            chest = np.array([x, hip_y - P["spine"] * h * 0.5])
            # Arms are thrown up by the launch and trail behind in the air.
            up = math.sin(math.pi * clamp(u * 1.25)) ** 0.7
            hands = self.perf.arm_targets(0.0, chest, 0.0, lean)
            hands[0] = hands[0] + np.array([-h * 0.10 * up, -h * 0.19 * up])
            hands[1] = hands[1] + np.array([+h * 0.12 * up, -h * 0.16 * up])

            pose = build_pose((x, hip_y), h, facing=1.0, lean=lean, curl=0.045,
                              foot_near=fn, foot_far=ff, pitch_near=pn, pitch_far=pf,
                              hand_near=hands[0], hand_far=hands[1])
            zoom = lerp(1.18, 1.22, u)
            return pose, x + h * 0.04, zoom, 0.0, rise, x

        # Landed. The absorption is a damped spring on the hip height, so the
        # body sinks, overshoots and recovers instead of easing politely.
        ot = t - self.total
        x_land = self.x0 + self.speed * self.run_up * 0.72 + self.speed * self.flight
        absorb = math.exp(-7.0 * ot) * math.cos(2.0 * math.pi * 2.4 * ot)
        crouch = clamp(0.34 + 0.30 * absorb)
        hip_y = -pelvis_height(h, crouch)

        fn = np.array([x_land + h * 0.115, 0.0])
        ff = np.array([x_land - h * 0.075, 0.0])
        lean = lerp(0.30, 0.04, smoothstep(clamp(ot / 0.40)))

        chest = np.array([x_land, hip_y - P["spine"] * h * 0.50])
        # Arms come forward to counterbalance, then settle.
        bal = math.exp(-5.5 * ot) * math.cos(2.0 * math.pi * 2.0 * ot)
        hands = self.perf.arm_targets(0.0, chest, 0.0, lean)
        hands[0] = hands[0] + np.array([-h * 0.10 * bal, -h * 0.10 * bal])
        hands[1] = hands[1] + np.array([+h * 0.09 * bal, -h * 0.08 * bal])

        pose = build_pose((x_land, hip_y), h, facing=1.0, lean=lean, curl=0.11,
                          foot_near=fn, foot_far=ff, pitch_near=0.0, pitch_far=0.0,
                          hand_near=hands[0], hand_far=hands[1])
        zoom = lerp(1.20, 1.16, smoothstep(clamp(ot / 0.5)))
        return pose, x_land + h * 0.06, zoom, 0.0, 0.0, x_land


def shot_walkoff(t, dur, perf):
    """Walk out of frame. The camera lets it go."""
    h = perf.height
    g = perf.walk
    x0 = shot_walkoff.x0
    x = x0 + 430.0 * t
    phase = ((x - x0) / g.D) % 1.0

    hip_y = -pelvis_height(h) * g.hip_frac + g.hip_offset(phase)
    lean = g.lean
    fn, pn = g.foot(phase, x, 0.0, side=0.0)
    ff, pf = g.foot(phase, x, 0.0, side=0.5)

    chest = np.array([x, hip_y - P["spine"] * h * 0.55])
    hands = perf.arm_targets(phase, chest, g.arm_swing, lean)
    pose = build_pose((x, hip_y), h, facing=1.0, lean=lean, curl=0.055,
                      foot_near=fn, foot_far=ff, pitch_near=pn, pitch_far=pf,
                      hand_near=hands[0], hand_far=hands[1])
    head_turn = 0.0
    zoom = lerp(1.10, 0.99, smoothstep(clamp(t / dur)))
    return pose, x + h * 0.16, zoom, 0.0


shot_walkoff.x0 = 0.0


class Shot:
    """A shot is a duration plus a function of (t, duration, performer).

    Continuity between shots is explicit: each shot carries the ground position
    the previous one ended at, so the figure does not teleport across a cut.
    """

    def __init__(self, name, fn, duration, *, start_x=0.0, **opts):
        self.name = name
        self.fn = fn
        self.duration = duration
        self.start_x = start_x
        self.opts = opts

    def __call__(self, t, perf):
        """Call the shot body, adapting a bound method that takes only t."""
        if getattr(self.fn, "__self__", None) is not None:
            return self.fn(t)
        return self.fn(t, self.duration, perf)


def build_shots(perf):
    jump = JumpRig(perf)
    shots = [
        Shot("walk", shot_walk, 2.9),
        Shot("stop", shot_stop, 2.3, start_x=0.0),
        Shot("look", shot_look, 2.1, start_x=0.0),
        Shot("jump", jump.state, jump.total + 1.0),
        Shot("walkoff", shot_walkoff, 2.9, start_x=0.0),
    ]
    return shots
