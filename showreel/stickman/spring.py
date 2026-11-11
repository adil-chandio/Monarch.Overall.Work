"""Secondary motion: the part of animation that is not the pose.

A limb tip has mass. When the shoulder moves, the hand does not arrive with it --
it is dragged along, overshoots, and settles. That lag is called overlapping
action, and on a stick figure it is the single strongest cue that something is
being animated rather than drawn. Without it every limb stops dead the instant
its owner does, which reads as a puppet on strings.

The model is the honest one: a point mass on a spring, driven by whatever the
pose says the tip should be. It is simulated with semi-implicit Euler at a fixed
substep, so the result depends on the target motion and the constants and not on
the frame rate.

One rule matters more than the constants: the *contact* never follows a spring.
A foot bearing weight is pinned by the ground, so it is driven directly from the
gait. Dragging a planted foot is skating, and no amount of nice overshoot on the
other end makes up for it.
"""

from __future__ import annotations

import math

import numpy as np


class Spring2:
    """A critically-to-under-damped point that chases a target in two axes.

    ``stiffness`` and ``damping`` are in per-second units, so the behaviour is
    independent of how often ``step`` is called as long as the substep is fixed.
    ``damping`` at ``2*sqrt(stiffness)`` is critical damping: no overshoot. Lower
    it for drag, raise it for a tight, snappy limb.
    """

    def __init__(self, position, *, stiffness=180.0, damping=16.0,
                 max_speed=None):
        self.p = np.asarray(position, float)
        self.v = np.zeros(2, float)
        self.k = float(stiffness)
        self.c = float(damping)
        self.max_speed = max_speed

    def step(self, target, dt, *, substeps=3):
        target = np.asarray(target, float)
        h = dt / substeps
        for _ in range(substeps):
            accel = self.k * (target - self.p) - self.c * self.v
            self.v += accel * h
            if self.max_speed is not None:
                speed = float(np.hypot(self.v[0], self.v[1]))
                if speed > self.max_speed:
                    self.v *= self.max_speed / speed
            self.p += self.v * h
        return self.p

    def snap(self, position):
        self.p = np.asarray(position, float)
        self.v[:] = 0.0


class Follow:
    """A one-dimensional follower, for things that only swing.

    Used for the head, which pivots rather than translates, and for anything else
    that is better described as an angle than a position.
    """

    def __init__(self, value=0.0, *, stiffness=120.0, damping=11.0):
        self.x = float(value)
        self.v = 0.0
        self.k = float(stiffness)
        self.c = float(damping)

    def step(self, target, dt, *, substeps=2):
        h = dt / substeps
        for _ in range(substeps):
            accel = self.k * (target - self.x) - self.c * self.v
            self.v += accel * h
            self.x += self.v * h
        return self.x


class Particle:
    """A dust mote: a point under gravity with drag and a lifetime."""

    __slots__ = ("p", "v", "life", "age", "r0", "r1", "spin")

    def __init__(self, p, v, life, r0, r1, spin=0.0):
        self.p = np.asarray(p, float)
        self.v = np.asarray(v, float)
        self.life = float(life)
        self.age = 0.0
        self.r0 = float(r0)
        self.r1 = float(r1)
        self.spin = float(spin)

    def step(self, dt, *, gravity=520.0, drag=2.6):
        self.age += dt
        self.v[1] += gravity * dt
        self.v *= math.exp(-drag * dt)
        self.p = self.p + self.v * dt

    @property
    def alive(self):
        return self.age < self.life

    @property
    def u(self):
        return min(1.0, self.age / max(self.life, 1e-6))

    @property
    def radius(self):
        return self.r0 + (self.r1 - self.r0) * self.u

    @property
    def alpha(self):
        # Fade in fast, out slow: a puff is dense when it leaves the ground.
        u = self.u
        if u < 0.12:
            return u / 0.12
        return (1.0 - (u - 0.12) / 0.88) ** 1.5


class Dust:
    """A pool of dust motes, spawned by impacts and footfalls.

    Kept as its own system so that what the effects layer draws is caused by
    something: a puff exists because a foot actually landed with a measured
    vertical speed, not because a random number said so.
    """

    def __init__(self, seed=0):
        self.rng = np.random.default_rng(seed)
        self.parts = []

    def kick(self, at, strength, *, count=7, spread=1.0, direction=0.0):
        """Spawn a puff at a ground contact.

        ``strength`` scales speed and lifetime together, so a heavy landing
        throws more dust for longer without needing a separate parameter.
        """
        at = np.asarray(at, float)
        for i in range(count):
            ang = (-math.pi * 0.5
                   + self.rng.uniform(-0.85, 0.85)
                   + direction * 0.35)
            speed = (40.0 + 150.0 * self.rng.random()) * strength
            v = np.array([math.cos(ang) * speed * 1.15 + direction * 55.0 * strength,
                          math.sin(ang) * speed * 0.55])
            p = at + np.array([self.rng.uniform(-8, 8), self.rng.uniform(-4, 2)])
            life = (0.45 + 0.55 * self.rng.random()) * (0.7 + 0.6 * strength)
            r0 = self.rng.uniform(3.0, 7.0) * (0.6 + 0.8 * strength)
            r1 = r0 + self.rng.uniform(16.0, 34.0) * (0.5 + 0.9 * strength)
            self.parts.append(Particle(p, v, life, r0, r1, spread))

    def step(self, dt):
        for p in self.parts:
            p.step(dt)
        self.parts = [p for p in self.parts if p.alive]

    def __bool__(self):
        return bool(self.parts)
