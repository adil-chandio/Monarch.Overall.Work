"""Motion for the armature: curves, springs and physics.

Animation is timing, not poses. This module supplies the pieces that make
movement read as weight instead of as a slide:

  * easing curves that match real acceleration (nothing here is linear)
  * a second-order spring, so a hand or a chest *follows* the body instead of
    arriving with it — overlapping action
  * a ballistic arc for anything that leaves the ground
  * a walk cycle driven by entered distance, so the feet can stay planted

Every value is a function of time, so a frame is reproducible from its number.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

GRAVITY = 981.0          # cm/s^2; the figure is 1000 units = 1.8 m tall


# --------------------------------------------------------------------- curves
def clamp01(t):
    return 0.0 if t < 0 else (1.0 if t > 1 else t)


def ease_in_out(t):
    t = clamp01(t)
    return t * t * (3 - 2 * t)


def ease_out(t, p=3.0):
    return 1.0 - (1.0 - clamp01(t)) ** p


def ease_in(t, p=3.0):
    return clamp01(t) ** p


def ease_out_back(t, s=1.70158):
    """Overshoot then settle — the snap of a hand reaching a handle."""
    t = clamp01(t) - 1.0
    return t * t * ((s + 1) * t + s) + 1.0


def smoothstep(a, b, x):
    if b == a:
        return 0.0 if x < a else 1.0
    return ease_in_out((x - a) / (b - a))


CURVES = {'linear': clamp01, 'ease': ease_in_out, 'out': ease_out,
          'in': ease_in, 'back': ease_out_back}


# --------------------------------------------------------------------- spring
@dataclass
class Spring:
    """Second-order follow for overlapping action.

    A hand does not stop when the arm stops; it overshoots and settles. Feeding
    the driving value through this produces exactly that lag.
    """
    value: float = 0.0
    velocity: float = 0.0
    stiffness: float = 120.0
    damping: float = 16.0

    def step(self, target, dt):
        a = self.stiffness * (target - self.value) - self.damping * self.velocity
        self.velocity += a * dt
        self.value += self.velocity * dt
        return self.value

    def run(self, targets, dt):
        return np.array([self.step(float(t), dt) for t in targets], np.float32)


# ------------------------------------------------------------------ keyframes
@dataclass
class Channel:
    """(time, value, curve) keys; curve belongs to the segment leaving a key."""
    keys: list = field(default_factory=list)
    default: float = 0.0

    def value(self, t):
        k = self.keys
        if not k:
            return self.default
        if t <= k[0][0]:
            return k[0][1]
        if t >= k[-1][0]:
            return k[-1][1]
        for i in range(len(k) - 1):
            t0, v0 = k[i][0], k[i][1]
            t1, v1 = k[i + 1][0], k[i + 1][1]
            if t0 <= t < t1:
                name = k[i][2] if len(k[i]) > 2 else 'ease'
                u = (t - t0) / max(1e-6, t1 - t0)
                f = CURVES.get(name, ease_in_out)(u)
                return v0 + (v1 - v0) * f
        return k[-1][1]


def keys(*pairs, curve='ease'):
    return [(p[0], p[1], p[2] if len(p) > 2 else curve) for p in pairs]


# ---------------------------------------------------------------- locomotion
def walk_phase(distance, stride, offset=0.0):
    """Phase in radians for a walk that has travelled `distance` units."""
    return (distance / max(1e-6, stride)) * math.tau + offset


def step_bob(phase, amp=1.0):
    """Lowest at contact, highest at passing — twice per stride."""
    return -math.cos(2.0 * phase) * 0.5 * amp


def hip_sway(phase, amp=1.0):
    """Weight shifts over the planted foot once per stride."""
    return math.sin(phase) * amp


def foot_lift(phase, height=34.0):
    """Height of a swinging foot above the ground; zero through stance."""
    s = math.sin(phase)
    if s <= 0:
        return 0.0
    return math.sin(s * math.pi * 0.5) ** 2 * height


def arm_swing(phase, amp=16.0):
    """Arms counter-swing the legs; the far arm leads by pi."""
    return math.sin(phase) * amp


# ------------------------------------------------------------------- details
def ballistic(v0, angle_deg, t):
    """Projectile position, y up, in drawing units."""
    a = math.radians(angle_deg)
    return v0 * math.cos(a) * t, v0 * math.sin(a) * t - 0.5 * GRAVITY * t * t


def blink(t, times, dur=0.11):
    """1.0 while an eyelid is shut, eased around it."""
    v = 0.0
    for bt in times:
        d = t - bt
        if -dur < d < dur:
            v = max(v, ease_in_out(1.0 - abs(d) / dur))
    return v


def breathe(t, rate=0.24, depth=1.0):
    """Chest rise: about fifteen breaths a minute."""
    return (math.sin(t * rate * math.tau) * 0.5 + 0.5) * depth


def settle(t, start, dur=0.9, amp=1.0):
    """A decaying wobble after an impact — follow-through, not a stop."""
    d = t - start
    if d < 0 or d > dur:
        return 0.0
    k = 1.0 - d / dur
    return math.sin(d * 19.0) * amp * (k ** 2)
