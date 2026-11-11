"""Locomotion that obeys the ground.

The rule that separates animation from puppetry is simple: a foot that is
bearing weight does not move. So the feet are not posed relative to the hips.
The hips travel, and each foot is placed in *world* space and pinned there for
as long as it carries load.

Everything else follows from that constraint, and the arithmetic is worth
writing down because getting it wrong is exactly how rigs end up skating.

Let D be the distance the body covers in one full cycle (two steps) and B the
fraction of the cycle a foot is planted. During stance the body moves B*D while
the foot is fixed, so the foot must land B*D/2 ahead of the hips and leave B*D/2
behind them. That pins both contact positions, and the gap between them is D/2:
one step. The swing foot then covers the remaining distance, which is why it
travels faster than the body -- it has to catch up.

The walk and the run differ in one physical fact: a walk always has a foot down,
a run has a flight phase in which neither foot does. B = 0.62 is a walk; B = 0.34
is a run with 32% of each cycle airborne. Making that a number instead of two
hand-built cycles means speed can ramp continuously and the feet never slide.
"""

from __future__ import annotations

import math

import numpy as np

from .rig import clamp, lerp, smoothstep

GRAVITY = 2900.0  # px / s^2 at the scale this film is staged in


def hermite(u, p0, p1, m0, m1):
    """Cubic Hermite from p0 to p1 over u in [0,1] with end slopes m0, m1.

    Used for the swing foot so its velocity matches the stance it left and the
    stance it is about to enter. A smoothstep would put both end velocities at
    zero, which shows up as a small hitch every single step.
    """
    u2 = u * u
    u3 = u2 * u
    return ((2 * u3 - 3 * u2 + 1) * p0
            + (u3 - 2 * u2 + u) * m0
            + (-2 * u3 + 3 * u2) * p1
            + (u3 - u2) * m1)


class Gait:
    """A locomotion cycle that can be played at any speed without skating.

    ``stride`` is D, the ground distance covered in one cycle, as a fraction of
    figure height. ``stance`` is B. ``lift`` is swing clearance.
    """

    def __init__(self, height, *, stride=0.58, stance=0.62, lift=0.050,
                 bob=0.026, arm_swing=0.62, lean=0.055, hip_frac=0.930):
        self.height = height
        self.D = stride * height
        self.B = stance
        self.lift = lift * height
        self.bob_amp = bob * height
        self.arm_swing = arm_swing
        self.lean = lean
        # Hip height while moving, as a fraction of full standing hip height. A
        # walk cannot happen with locked knees: to reach a stride the leg has to
        # be bent, and the only way to bend it is to stand lower. This is the
        # number that makes the stride legal, and ``max_stride`` derives what it
        # buys rather than trusting a value picked by eye.
        self.hip_frac = hip_frac

        # The foot is planted B*D/2 ahead at touchdown and B*D/2 behind at
        # toe-off. Both constants are fixed once B is chosen.
        self.A = self.B * self.D * 0.5

        # Relative horizontal velocity of a planted foot, in cycle fractions.
        # dy/du of the swing curve must meet this at both ends or the foot pops.
        self.slope = -(1.0 - self.B) / max(self.B, 1e-3)

    # -- limits -------------------------------------------------------------

    def max_stride(self, reach):
        """Longest stride this hip height allows before the leg over-extends.

        From the contact geometry: at touchdown the foot is A = B*D/2 ahead of
        the hip, and the hip sits ``h`` above the floor. The leg must reach both,
        so (B*D/2)^2 + h^2 <= reach^2. Solve for D.
        """
        h = reach * self.hip_frac
        half = math.sqrt(max(0.0, reach * reach - h * h))
        return 2.0 * half / max(self.B, 1e-3)

    # -- timing -------------------------------------------------------------

    def period_for_speed(self, speed):
        """Cycle duration for a given ground speed, in seconds."""
        return self.D / max(speed, 1e-6)

    def speed_for_period(self, period):
        return self.D / max(period, 1e-6)

    # -- feet ---------------------------------------------------------------

    def foot(self, phase, pelvis_x, ground_y, *, side=0.0):
        """World-space contact point and foot pitch for one foot.

        The result is expressed in the same frame as ``pelvis_x``, which is what
        makes the planted foot actually stay planted. An earlier version
        recomputed the body's travel from the cycle phase and added it back, so
        the foot drifted one full stride behind the hips for every cycle the
        figure had already walked -- the body ran away from its own feet.

        ``side`` offsets the cycle: 0.5 puts the second leg half a cycle out.
        """
        p = (phase + side) % 1.0
        B = self.B
        A = self.A

        if p < B:
            u = p / B
            # Constant in world space, because the pelvis advances at exactly
            # the rate this term retreats: both are D per cycle.
            x = pelvis_x + A * (1.0 - 2.0 * u)
            y = ground_y
            # A stick figure's foot has no ankle roll to speak of: a few
            # degrees either way is all the silhouette can carry without
            # reading as a hoof.
            pitch = lerp(-0.07, 0.16, smoothstep(min(1.0, u * 1.15)))
        else:
            u = (p - B) / (1.0 - B)
            s = hermite(u, 0.0, 1.0, self.slope, self.slope)
            x = pelvis_x + A * (2.0 * s - 1.0)
            y = ground_y - self.lift * math.sin(math.pi * min(u, 1.0)) ** 0.9
            pitch = lerp(0.16, -0.07, smoothstep(u))

        return np.array([x, y], float), pitch

    # -- body ---------------------------------------------------------------

    def hip_offset(self, phase):
        """Signed vertical offset of the hips from their standing height.

        Troughs at each foot contact, peaks at mid-stance, twice per cycle, and
        the amplitude grows with speed because the body drops further onto a
        loaded leg when it is. Positive y is down.
        """
        return self.bob_amp * 0.5 * (1.0 + math.cos(4.0 * math.pi * phase))

    def shoulder_x(self, phase):
        """Horizontal sway of the upper body, opposite the forward leg."""
        return math.cos(2.0 * math.pi * phase)


def settle(t, *, frequency=2.4, damping=5.0, amplitude=1.0):
    """Damped oscillation that starts at ``amplitude`` and dies out.

    Used for everything that gets knocked: the body after a landing, the head
    after a stop, an arm after a swing. One function with different constants is
    what makes the motion read as having mass.
    """
    if t <= 0.0:
        return amplitude
    return amplitude * math.exp(-damping * t) * math.cos(2.0 * math.pi * frequency * t)


def projectile(t, p0, v0, g=GRAVITY):
    """Position and velocity of a free body at time t."""
    p0 = np.asarray(p0, float)
    v0 = np.asarray(v0, float)
    pos = p0 + v0 * t + np.array([0.0, 0.5 * g * t * t])
    vel = v0 + np.array([0.0, g * t])
    return pos, vel


def launch_velocity(delta, flight_time, g=GRAVITY):
    """Velocity needed to cross ``delta`` in ``flight_time`` under gravity.

    Solving for this instead of eyeballing an arc is what makes a jump read as
    heavy or light for a reason rather than by taste.
    """
    delta = np.asarray(delta, float)
    return np.array([delta[0] / flight_time,
                     (delta[1] - 0.5 * g * flight_time * flight_time) / flight_time])


def impact(t, duration, depth=0.22):
    """Vertical scale for an impact: 1.0 at rest, a fast dip, a settle."""
    if t <= 0.0 or t >= duration:
        return 1.0
    u = t / duration
    return 1.0 - depth * math.exp(-7.0 * u) * math.cos(2.0 * math.pi * 2.2 * u)
