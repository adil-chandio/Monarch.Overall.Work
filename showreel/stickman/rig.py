"""A stick figure built as an actual rig.

There is one hip, one spine, one neck and one head, plus two arms and two legs.
The legs and arms are solved with two-bone inverse kinematics; the spine is
forward kinematics from a lean curve. Nothing is pasted, nothing is drawn by
hand, and every frame is computed from a time value.

That matters because of what a stick figure *is*: a symbol with no painted
surface to interpolate. The previous pipeline's ceiling was that it had only six
painted poses and no side view of an elbow, so it could only cut between held
images. Here the ceiling is different and honest -- a figure with four bones per
limb can do anything four bones can reach, and it will never ghost.

The view is a profile with a slight over-the-shoulder depth split: the limbs on
the camera side are drawn brighter and wider than the limbs behind, so a side
view does not collapse into a single line soup.

Units are pixels; y grows downward. Angles are radians as atan2 returns them:
0 points at +x, +pi/2 points at +y (down).
"""

from __future__ import annotations

import math

import numpy as np

TAU = 2.0 * math.pi


# ------------------------------------------------------------------ arithmetic

def clamp(x, lo=0.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x


def lerp(a, b, t):
    return a + (b - a) * t


def smoothstep(t):
    t = clamp(t)
    return t * t * (3.0 - 2.0 * t)


def ease_out_cubic(t):
    t = clamp(t)
    return 1.0 - (1.0 - t) ** 3


def ease_in_cubic(t):
    t = clamp(t)
    return t ** 3


def ease_in_out(t):
    t = clamp(t)
    return 0.5 - 0.5 * math.cos(math.pi * t)


def ease_out_back(t, overshoot=1.7):
    t = clamp(t) - 1.0
    return 1.0 + (overshoot + 1.0) * t ** 3 + overshoot * t * t


def ease_out_elastic(t, period=0.44, decay=7.5):
    t = clamp(t)
    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    return 1.0 - math.exp(-decay * t) * math.cos(TAU * t / period)


def spring(t, frequency=2.2, damping=4.4):
    """Underdamped settle: 0 -> 1 with a decaying overshoot."""
    t = clamp(t)
    if t >= 1.0:
        return 1.0
    return 1.0 - math.exp(-damping * t) * (
        math.cos(TAU * frequency * t) + (damping / (TAU * frequency)) * math.sin(TAU * frequency * t)
    )


def approach(current, target, rate, dt):
    """Exponential approach that is frame-rate independent."""
    return target + (current - target) * math.exp(-rate * dt)


# ---------------------------------------------------------------- proportions

# Fractions of figure height. Roughly the seven-and-a-half-head canon, adjusted
# for a symbol whose head is a ball sitting on a neck rather than a face.
P = {
    "thigh": 0.222,
    "shin": 0.226,
    "foot": 0.052,
    "spine": 0.300,
    "neck": 0.030,
    "head_r": 0.086,
    "upper_arm": 0.158,
    "forearm": 0.152,
    "hand": 0.050,
    "shoulder": 0.040,   # half-width of the shoulder line in depth
    "hip": 0.026,
}

# Depth split: how far the near side of the body sits in front of the far side,
# as a fraction of figure height, expressed as a screen-space offset. A profile
# view needs this or the two legs read as one very thick leg.
NEAR = np.array([+0.008, -0.006])
FAR = np.array([-0.007, +0.004])
NEAR_SCALE = 1.0
FAR_SCALE = 0.972


# Normalise so that `height` really is the figure's full standing height:
# thigh + shin + spine + neck + two head radii = 1.0. Without this the figure is
# 5% shorter than the number the camera framed it for, and ground contact drifts.
_TOTAL = P["thigh"] + P["shin"] + P["spine"] + P["neck"] + 2.0 * P["head_r"]
for _k in list(P):
    P[_k] /= _TOTAL

LEG_REACH = (P["thigh"] + P["shin"]) * 0.985


def pelvis_height(height, crouch=0.0):
    """How far the hip centre sits above the ground for a figure of ``height``.

    ``crouch`` in 0..1 shortens the legs, which is what a crouch physically is.
    Exposing this stops callers from inventing a hip position the leg solver
    then has to lie about.
    """
    return LEG_REACH * height * (1.0 - 0.34 * clamp(crouch))


class Pose:
    """One figure at one instant, as points in the frame.

    Also carries the draw order: ``limbs()`` yields (segment, layer, tint) so the
    renderer can paint far limbs behind the torso and near limbs in front.
    """

    __slots__ = (
        "pelvis", "waist", "chest", "neck", "head", "head_r",
        "shoulder_near", "shoulder_far", "hip_near", "hip_far",
        "elbow_near", "elbow_far", "wrist_near", "wrist_far",
        "knee_near", "knee_far", "ankle_near", "ankle_far",
        "toe_near", "toe_far",
        "facing", "height", "hand_len", "foot_len", "tone", "head_ang",
    )

    def __init__(self):
        for name in self.__slots__:
            setattr(self, name, None)

    # -- drawing ------------------------------------------------------------

    def segments(self):
        """Yield (p0, p1, part) for every stroke in the figure.

        ``part`` decides width, tint and whether it is near or far, which is all
        the renderer needs. Order is draw order: back to front.
        """
        yield self.shoulder_far, self.elbow_far, "far_arm"
        yield self.elbow_far, self.wrist_far, "far_arm"
        yield self.hip_far, self.knee_far, "far_leg"
        yield self.knee_far, self.ankle_far, "far_leg"
        yield self.ankle_far, self.toe_far, "far_foot"

        yield self.pelvis, self.waist, "spine"
        yield self.waist, self.chest, "spine"
        yield self.chest, self.neck, "spine"
        yield self.hip_near, self.knee_near, "leg"
        yield self.knee_near, self.ankle_near, "leg"
        yield self.ankle_near, self.toe_near, "foot"

        yield self.shoulder_near, self.elbow_near, "arm"
        yield self.elbow_near, self.wrist_near, "arm"

    def children(self):
        """Attachment points another figure can be hung from.

        Both hands and the head top, because a swing can be held by either hand
        or by the neck -- and which one it is changes the whole shape of the
        pendulum, so it is not a detail that can be faked later.
        """
        return {
            "wrist_near": self.wrist_near,
            "wrist_far": self.wrist_far,
            "hand_near": self.wrist_near + (self.wrist_near - self.elbow_near) * 0.5,
            "hand_far": self.wrist_far + (self.wrist_far - self.elbow_far) * 0.5,
            "head_top": self.head - np.array([0.0, self.head_r]),
            "head": self.head,
        }

    def joints(self):
        for name in self.__slots__:
            v = getattr(self, name)
            if isinstance(v, np.ndarray):
                yield name, v


def solve_limb(root, target, len_a, len_b, bend):
    """Two-bone IK. Returns (middle joint, end joint).

    ``bend`` is +1 or -1 and chooses which side of the root->target line the
    middle joint sits on. Unreachable targets are pulled to just inside full
    extension instead of being clamped onto the root, which is the difference
    between a leg that straightens under a jump and a leg that folds backwards
    through itself.
    """
    root = np.asarray(root, float)
    target = np.asarray(target, float)
    delta = target - root
    dist = float(np.hypot(delta[0], delta[1]))
    if dist < 1e-5:
        return root + np.array([0.0, len_a * bend]), root.copy()

    reach = (len_a + len_b) * 0.998
    d = min(max(dist, abs(len_a - len_b) + 1.0), reach)
    u = delta / dist

    a = (len_a * len_a - len_b * len_b + d * d) / (2.0 * d)
    h = math.sqrt(max(0.0, len_a * len_a - a * a))

    foot = root + u * a
    middle = foot + np.array([-u[1], u[0]]) * (h * bend)
    end = root + u * d
    return middle, end


def foot_from_contact(contact, pitch, foot_len, facing=1.0, reach=0.62):
    """Turn a ground contact point and a foot angle into (ankle, toe).

    A stick figure's foot is one bone, so there is no heel to model. The rule
    that makes it behave is simple and exact: whichever end of that bone is
    lower rests on the contact point. Positive pitch points the toe down, which
    is push-off and lifts the ankle; negative pitch points it up, which is a heel
    strike and leaves the ankle on the ground.

    Doing it this way means the foot can never sink through the floor, because
    the contact point *is* the floor and the whole bone is placed relative to it.
    Rotating about the ankle instead -- which is the obvious thing to write --
    drives the toe a third of a foot-length under the ground on every toe-off.
    """
    contact = np.asarray(contact, float)
    direction = np.array([math.cos(pitch) * facing, math.sin(pitch)])
    half = foot_len * reach
    # The toe offset from the ankle is (cos p, sin p) * half. Positive pitch
    # points the toe *down* in screen space, so sin p > 0 means the toe is the
    # lower end and must take the contact -- the earlier version had this
    # backwards, which is why the toe floated a hundred pixels behind the plant.
    if math.sin(pitch) >= 0.0:
        toe = contact
        ankle = contact - direction * half
    else:
        ankle = contact
        toe = contact + direction * half
    return ankle, toe


def build_pose(
    pelvis_xy,
    height,
    *,
    facing=1.0,
    lean=-0.0,
    curl=0.10,
    head_tilt=0.0,
    foot_near=None,
    foot_far=None,
    pitch_near=0.0,
    pitch_far=0.0,
    squash=1.0,
    stretch=0.0,
    hand_near=None,
    hand_far=None,
    bend_near=+1.0,
    bend_far=-1.0,
    head_reach=None,
    tone="ink",
):
    """Assemble the figure.

    ``pelvis_xy`` is the hip centre in the frame. ``foot_*`` and ``hand_*`` are
    targets in frame space, which is the whole point: a planted foot stays
    planted while the hips travel over it. ``lean`` tips the torso toward the
    facing direction; ``curl`` bends the upper spine further than the lower one,
    which is what stops an upright figure from looking like a broom.

    Elbow bend sign: the human elbow folds so the hand travels forward and up,
    so the elbow apex points *backwards* -- i.e. opposite the facing direction.
    """
    p = Pose()
    p.facing = facing
    p.tone = tone
    h = height
    f = facing

    # Squash and stretch, applied to the whole figure about its contact point.
    # ``squash`` < 1 compresses vertically; ``stretch`` > 0 lengthens. Volume is
    # not conserved by scaling alone, so the caller is responsible for the width
    # compensation -- see ``render.squash_width``. A stick figure has no volume
    # to preserve, so the effect is carried by the spine and the timing instead,
    # which is why the number is used for the torso and not the bones.
    p.height = h * (1.0 + stretch)

    pelvis = np.asarray(pelvis_xy, float)
    p.pelvis = pelvis

    h = h * (1.0 + stretch) * squash if stretch else h * squash
    spine_len = P["spine"] * h
    neck_len = P["neck"] * h
    head_r = P["head_r"] * h * (1.0 / squash) ** 0.35

    # Spine as two segments: lower back at half the lean, upper at full lean
    # plus curl. Curling forward makes a crouch read as a crouch.
    lower_ang = lean * 0.45
    upper_ang = lean * 1.0 + curl
    waist = pelvis + np.array([math.sin(lower_ang) * f, -math.cos(lower_ang)]) * (spine_len * 0.52)
    chest = waist + np.array([math.sin(upper_ang) * f, -math.cos(upper_ang)]) * (spine_len * 0.48)

    neck_ang = lean + curl * 0.7 + head_tilt * 0.25
    neck = chest + np.array([math.sin(neck_ang) * f, -math.cos(neck_ang)]) * neck_len
    head_ang = lean + curl * 0.55 + head_tilt
    head = neck + np.array([math.sin(head_ang) * f, -math.cos(head_ang)]) * head_r

    # ``head_reach`` puts the head a given distance past the neck instead of at
    # its resting length. This is what lets a figure reach the top of a hanging
    # chain: the hand is at the chain, the pelvis hangs off the elbow, and the
    # neck has to give a little to bridge the gap. Clamped to a sane multiple of
    # the neck so a bad target cannot pull the head off the body.
    if head_reach is not None:
        lo = neck_len + head_r * 0.72
        hi = lo + neck_len * 0.85 + head_r * 0.55
        r = clamp(float(head_reach), lo, hi)
        d = head - neck
        head = neck + d / max(float(np.hypot(d[0], d[1])), 1e-6) * r

    p.waist, p.chest, p.neck, p.head, p.head_r = waist, chest, neck, head, head_r
    # The head's own angle, carried on the pose so the face can rotate with it.
    # Without this the eyes stay level with the horizon while the head leans, and
    # the face reads as a sticker sliding around a circle.
    p.head_ang = head_ang

    near_off = NEAR * h
    far_off = FAR * h
    sh = P["shoulder"] * h
    hp = P["hip"] * h

    p.shoulder_near = chest + near_off + np.array([0.0, sh * 0.35])
    p.shoulder_far = chest + far_off - np.array([0.0, sh * 0.35])
    p.hip_near = pelvis + near_off * 0.7
    p.hip_far = pelvis + far_off * 0.7

    thigh = P["thigh"] * h
    shin = P["shin"] * h
    foot_len = P["foot"] * h
    p.foot_len = foot_len



    # solve_limb's perpendicular for a downward root->target is (-1, 0), so a
    # bend of -1 puts the knee at +x. Facing right, the knee must go forward.
    knee_bend = -1.0 * f
    for tag, hip, foot, pitch, scale, bend in (
        ("near", p.hip_near, foot_near, pitch_near, NEAR_SCALE, knee_bend),
        ("far", p.hip_far, foot_far, pitch_far, FAR_SCALE, knee_bend),
    ):
        if foot is None:
            knee = hip + np.array([foot_len * f * 0.25, thigh])
            ankle = hip + np.array([0.0, thigh + shin])
            toe = ankle + np.array([foot_len * f * 0.85, 0.0])
        else:
            # ``foot`` is a *contact point*: the lowest place the foot touches,
            # with pitch bringing the toe down (positive) or up (negative). The
            # foot is a single bone from ankle to toe, so the rule that keeps it
            # out of the floor is: whichever end is lower sits on the contact.
            ankle, toe = foot_from_contact(foot, pitch, foot_len, f)
            knee, ankle = solve_limb(hip, ankle, thigh * scale, shin * scale, bend)
            # solve_limb may have pulled the ankle inward if the contact was out
            # of reach. In that case the foot must slide *with* the ankle, or the
            # toe stays where the contact wanted it and the foot bone stretches.
            actual = float(np.hypot(*(ankle - hip)))
            ideal = float(np.hypot(*(foot_from_contact(foot, pitch, foot_len, f)[0] - hip)))
            if ideal > 1e-6 and actual < ideal - 1e-3:
                shift = (ideal - actual) / ideal
                # Keep the foot bone rigid: re-derive the toe from the ankle at a
                # fixed length. The direction is kept from the contact solve.
                d = (toe - ankle)
                n = float(np.hypot(d[0], d[1]))
                if n > 1e-6:
                    toe = ankle + d / n * (foot_len * 0.62)
        # The rig guarantees a foot does not go through the floor. The contact
        # solve cannot produce one, but the reach correction above can tilt the
        # foot bone by a couple of units, so it is clamped here once rather than
        # trusted at every call site -- the alternative is a millimetre of toe
        # under the grass on a handful of frames, which is exactly the kind of
        # thing that is invisible until it is pointed at.
        ankle = np.array([ankle[0], min(float(ankle[1]), 0.0)])
        toe = np.array([toe[0], min(float(toe[1]), 0.0)])
        setattr(p, f"knee_{tag}", knee)
        setattr(p, f"ankle_{tag}", ankle)
        setattr(p, f"toe_{tag}", toe)

    upper = P["upper_arm"] * h
    fore = P["forearm"] * h
    p.hand_len = P["hand"] * h
    # The elbow folds so the hand travels forward: its apex points backwards,
    # i.e. toward -x when facing right.
    elbow_bend = +1.0 * f
    for tag, sh_pt, hand, bend, scale in (
        ("near", p.shoulder_near, hand_near, elbow_bend, NEAR_SCALE),
        ("far", p.shoulder_far, hand_far, elbow_bend, FAR_SCALE),
    ):
        if hand is None:
            hand = sh_pt + np.array([0.0, (upper + fore) * 0.96])
        hand = np.asarray(hand, float)
        # A hand target is a request, not a command. Pull it back inside 96% of
        # the arm's reach before solving, so a pose that asks for a little too
        # much gets a nearly-straight arm instead of a silently stretched one.
        # Every gesture in the film stacks offsets, and without this clamp those
        # offsets can add up past the bone length.
        reach = (upper + fore) * scale * 0.96
        off = hand - sh_pt
        dist = float(np.hypot(off[0], off[1]))
        if dist > reach:
            hand = sh_pt + off * (reach / dist)
        elbow, wrist = solve_limb(sh_pt, hand, upper * scale, fore * scale, bend)
        setattr(p, f"elbow_{tag}", elbow)
        setattr(p, f"wrist_{tag}", wrist)

    return p
