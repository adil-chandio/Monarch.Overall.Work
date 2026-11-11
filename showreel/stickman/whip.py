"""A whip, and the swing it becomes.

The film's second character holds a rope. The rope hangs. Then it is a swing.

The only interesting problem here is the hand-off: the moment the figure grabs
the rope, the rope stops being a free object and becomes the thing holding the
figure up. Everything after that is not animation, it is constraint solving --
the hands are wherever the chain ends, and the body is solved to reach them.

That is why this module owns the *authority* rather than the shape:

    hanging   the chain is pinned at its anchor and the tip is free. The figure
              stands on the ground and does not touch it.
    grab      the hands are placed on the chain tip, and the chain is driven by
              the tip. For a few frames the body is still grounded, so the rope
              takes no load and goes slack -- which is what happens when you
              pick up a rope that is lying on the ground.
    swing     the chain hangs from its anchor, the hands ride the tip, and the
              body hangs off the hands. Body position comes from the chain, not
              from a curve. Gravity decides the arc, so the speed at the bottom
              and the hang at the top are the same number.
    land      the grip opens and the body becomes ballistic again.

Nothing in here is keyframed. The swing's timing is the pendulum's timing.
"""

from __future__ import annotations

import math

import numpy as np

from .rig import P, clamp, lerp, smoothstep


class SwingRig:
    """A figure hanging from a rope, solved rather than posed.

    The body is described from the grip downward: the hands are at the chain
    tip, the arms are extended, and the pelvis hangs a fixed distance below the
    shoulders. That leaves the pelvis position determined by the chain plus a
    lean, which is exactly the physical relationship and needs no separate
    animation.

    The legs are free, and they are where the acting is: a figure hanging still
    has heavy legs, and a figure swinging throws them ahead of the body and then
    lets them trail, because a leg has mass and the body's motion is a rotation.
    """

    def __init__(self, height, anchor, rope_length, *, grab_t=0.0,
                 release_t=1.0, ground_y=0.0):
        self.height = height
        self.anchor = np.asarray(anchor, float)
        self.rope_length = rope_length
        self.grab_t = grab_t
        self.release_t = release_t
        self.ground_y = ground_y

        # Arm span from shoulder to wrist, at full stretch. The body hangs off
        # the grip by this much plus the shoulder-to-pelvis distance.
        self.arm_reach = (P["upper_arm"] + P["forearm"]) * height * 0.985
        self.torso = P["spine"] * height * 0.62 + P["neck"] * height

    def hand_offset(self, grip, swing_angle=0.0):
        """How far the grip sits from the pelvis that hangs off it.

        Exposed because the catch is solved in *pelvis* space -- the pelvis is the
        point with the ballistic path -- while the rope is solved in *hand* space.
        The difference between the two is a fixed vector at a given angle, and the
        capture solve needs it as a number rather than as a second copy of the
        geometry.
        """
        down = np.array([math.sin(swing_angle), math.cos(swing_angle)])
        return down * (self.arm_reach * 0.995 + self.torso)

    def body_from_grip(self, grip, *, swing_angle=0.0, tuck=0.0, facing=1.0,
                       hand_span=1.0):
        """Return (pelvis, shoulder, hand, lean) for a body hanging at ``grip``.

        ``swing_angle`` is measured from vertical and is the direction the body
        is *currently* being pulled -- so the torso trails the hands on the way
        down and leads on the way up, which is the visual signature of a swing.
        """
        grip = np.asarray(grip, float)

        # Hands on the grip. Near hand slightly lower and behind, so the grip
        # reads as two hands on one rope rather than as a single claw.
        hand_near = grip + np.array([-0.018, 0.010]) * self.height
        hand_far = grip + np.array([0.014, -0.004]) * self.height

        # Shoulders sit below the hands, along the line from the grip toward the
        # body's own direction of hanging. ``hand_span`` shrinks the hang for a
        # grabbing pose, where the arms are not fully extended yet: a figure
        # whose arms go from folded to locked in one frame has teleported its
        # own shoulders, and that is visible no matter how good the rope is.
        # ``down`` points from the grip toward the ground: +y in world units,
        # rotated by the swing angle. Every joint below the hands is reached by
        # moving ALONG this vector, never against it. (The first version
        # subtracted it, which hung the body upside down above the rope --
        # invisible in a unit test that only checked distances, obvious in one
        # frame of film.)
        down = np.array([math.sin(swing_angle), math.cos(swing_angle)])
        shoulder = grip + down * (self.arm_reach * 0.995 * hand_span)

        # Pelvis hangs off the shoulders, but a hanging body does not hang
        # straight: the hips drift toward the swing's inside edge.
        lean = -swing_angle * 0.55
        pelvis = shoulder + down * self.torso

        # Legs. Hanging legs are long and heavy: they drop below the pelvis and
        # lag behind a swinging torso, so they are offset opposite the angular
        # velocity -- which is what ``tuck`` bundles up.
        leg_len = (P["thigh"] + P["shin"]) * self.height
        knee = pelvis + down * (leg_len * 0.50) + np.array([(0.10 + tuck * 0.30), 0.0]) * self.height
        ankle = pelvis + down * (leg_len * 0.98) + np.array([(0.02 + tuck * 0.55), 0.0]) * self.height

        return dict(pelvis=pelvis, shoulder=shoulder, lean=lean,
                    hand_near=hand_near, hand_far=hand_far,
                    knee=knee, ankle=ankle, down=down)

    def phase(self, t):
        if t < self.grab_t:
            return "reach"
        if t < self.release_t:
            return "swing"
        return "fly"


def pendulum_state(theta0, length, t, *, gravity=2900.0, damping=0.22, omega0=0.0):
    """Closed-form-ish pendulum, integrated in one go.

    Integrated rather than evaluated from an elliptic-function solution because
    the swing in this film starts from rest at an angle, and a numeric solution
    with damping is both shorter to write and closer to what a real rope does --
    the amplitude decays, which is the cue that the swing is losing energy.
    """
    theta = float(theta0)
    # ``omega0`` is not decoration. A figure that grabs a rope while it is moving
    # arrives with angular momentum, and the rope can only cancel the radial part
    # of its motion -- a rope pulls, it does not push. So the swing's amplitude is
    # set by the catch, not by the angle: start from rest at 40 degrees and you
    # get a small polite arc; arrive at 40 degrees doing 1500 px/s and you get a
    # real swing. Passing the velocity in is what makes the two agree.
    omega = float(omega0)
    dt = 1.0 / 480.0
    n = int(max(0.0, t) / dt)
    k = gravity / max(length, 1e-6)
    for _ in range(n):
        accel = -k * math.sin(theta) - damping * omega
        omega += accel * dt
        theta += omega * dt
    return theta, omega
