"""Shot 5: the duel -- two bodies, one edge.

The first shot with two characters in it, and the reason it is worth doing is that
a second body makes every cheat visible. One figure can walk an authored curve and
nobody can tell. Two figures that touch cannot: from the frame the silhouette's
hands meet the line figure's back onward, every frame either agrees about where
that contact is or the shot is broken.

The choreography is a chain of consequences, each link computed from the one
before it:

    approach   the hero stands at the lip with its back to the void, looking out
               over it. It is not on guard, because it does not know anyone is
               behind it -- which is the whole reason the shot works
    close      the silhouette walks in. It is only ever seen from behind, so it
               reads as a shape rather than as a person
    shove      contact is a constraint, not a look: the silhouette's hands are
               placed on the hero's back *after* the hero's pose is solved, so
               they cannot drift off it
    break      the hero's feet leave the ground. It is not thrown -- it is
               pushed, and a push is a velocity, not a place. Everything after
               this frame is ballistics with that velocity in it
    drop       the void takes it. The camera does not follow: it holds on the
               edge, which is what makes the hole feel like a depth instead of a
               stripe
    still      the silhouette at the lip, alone. It does not celebrate. The last
               beat belongs to the hole

Nothing here is a curve fitted to look right. The contact is solved onto the body.
The fall is a projectile from the lip with the velocity the shove gave it. The
disappearance is the void occluding the body, which is what a void is for.

Units are world pixels, y down, like every other module in this package.
"""

from __future__ import annotations

import math

import numpy as np

from .motion import GRAVITY
from .rig import P, build_pose, clamp, lerp, pelvis_height, smoothstep, ease_in_out

FPS = 24

# ------------------------------------------------------------------ the set

# The chasm, exactly as the previous film staged it. Reusing the set is not laziness:
# the set is already verified (lips, depth, the painting order), and a fight is
# interesting because of what the people do, not because of a new backdrop.
NEAR_LIP = -150.0
FAR_LIP = 780.0
GAP_DEPTH = 430.0

# Marks. The hero stands with its heels on the lip; the silhouette comes in from
# solid ground behind it and never has to step onto anything but floor.
# The camera must stand on solid ground: an x past the edge is a camera floating
# over the valley, and what it sees is the underside of the world.
# Framing, solved from the set rather than chosen: at this lens and this cam_x the
# hero's feet sit exactly on the near lip, and the void's visible window (the far
# wall between the far rim and the near lip) is 559 rows tall. That window is the
# only place a falling body can be seen, so the shot is built around its size.
CAM_X = -92.0
CAM_ZOOM = 1.30
# The lens sits low -- 15% of frame height, roughly knee level on the figures. That
# is not a stylistic choice: a camera standing on the ground looking at an edge
# sees the edge against the far view, with the drop below it filling the bottom of
# frame. Raise the lens and the floor in front of the edge occludes the drop
# entirely, which is what a hole looks like from above and a cliff does not.
CAM_EYE = 0.250

# The hero stands with its heels on the lip. The silhouette comes in from solid
# ground behind it, so every frame of the approach is on floor that exists.
HERO_X = NEAR_LIP - 96.0
FOE_FROM = HERO_X - 1180.0
FOE_STOP = HERO_X - 128.0

# Durations, seconds. At 24 fps a beat shorter than four frames is a flicker
# rather than an action.
T_APPROACH = 1.85
T_SHOVE = 0.62
T_BREAK = 0.46
T_DROP = 0.62
T_STILL = 1.20

# The push. 1 px = 2.5 mm at this figure size, so 900 px/s is 2.25 m/s -- a hard
# two-handed shove from a standing start, and enough to clear the lip.
SHOVE_V = 980.0


class Duel:
    """The whole shot, solved as one object.

    Kept as one class because the beats share state that has to stay continuous --
    the contact, the exact velocity the body has when its feet leave the lip, and
    the point at which the void takes it -- and the only reliable way to keep them
    continuous is to compute each from the one before, in one place.
    """

    def __init__(self, perf):
        self.perf = perf
        self.h = perf.height

        self.t_shove = T_APPROACH
        self.t_break = self.t_shove + T_SHOVE
        self.t_drop = self.t_break + T_BREAK
        self.t_still = self.t_drop + T_DROP
        self.total = self.t_still + T_STILL

        self.leave = self._solve_leave()

    # -- the hero's stance --------------------------------------------------

    def _hero_pose(self, *, look_out=1.0, brace=0.0, lean_extra=0.0):
        """The hero at the lip, with its back to the void.

        ``brace`` tightens the stance and drops the hips a little: a body that
        expects to be hit stands lower and wider than one that is looking at a
        sunset. The shot starts at brace 0 and never really gets above 0.3, because
        the hero never gets to prepare.
        """
        h = self.h
        x = HERO_X
        crouch = 0.06 + 0.16 * brace
        hip = -pelvis_height(h, crouch)
        lean = -0.03 * look_out + 0.16 * brace + lean_extra
        curl = 0.10 + 0.10 * brace

        # Heels near the lip, toes pointing out over it. This is the detail that
        # makes the shot frightening: the feet are already at the edge, so there is
        # no step back available.
        fn = np.array([x + h * 0.105, 0.0])
        ff = np.array([x - h * 0.085, 0.0])
        chest = np.array([x, hip - P["spine"] * h * 0.54])
        hands = self.perf.arm_targets(0.0, chest, 0.0, lean, up=0.10 + 0.10 * brace)
        return build_pose((x, hip), h, facing=1.0, lean=lean, curl=curl,
                          head_tilt=-0.06 * look_out + 0.10 * brace,
                          foot_near=fn, foot_far=ff,
                          hand_near=hands[0], hand_far=hands[1])

    # -- the shove ----------------------------------------------------------

    def _solve_leave(self):
        """The hero's velocity the instant its feet leave the floor.

        A shove at the back does two things: it translates the body and it rotates
        it. The translation is what carries it over the lip; the rotation is what
        makes it arrive face-up instead of feet-first. Both come from one impulse,
        so they are solved together here rather than keyed as two curves that
        happen to look related.
        """
        h = self.h
        # The impulse is horizontal and applied at the shoulder blades, a little
        # above the centre of mass, so a small part of it becomes forward pitch.
        return dict(v=np.array([SHOVE_V, -60.0]),
                    spin=1.15,          # rad/s of forward tumble
                    chest=np.array([HERO_X, -pelvis_height(h, 0.10)
                                    - P["spine"] * h * 0.86]))

    # The reach covers this fraction of the shove; the rest is the drive.
    REACH = 0.60

    def _contact(self, hero, t):
        """Where the silhouette's hands go, given the hero's solved pose.

        Taken from the hero's back *after* the hero is solved, not from a stored
        point. That distinction is the whole assertion: a stored point is a guess
        that the pose will be where the guess said, and it was wrong by 261 px --
        a third of a figure -- on the frames where the hero is driven forward.
        """
        h = self.h
        s = clamp((t - self.t_shove) / T_SHOVE)
        return hero.chest + np.array([-h * 0.06, h * 0.06]), s

    def in_void(self, t):
        """Is the hero inside the chasm at time ``t``?

        The renderer needs this, because a body inside a hole can only be seen
        through the hole's opening: below the near lip the ground in front of the
        chasm is between the body and the lens. Clipping the figure to the same
        wedge the backdrop was painted with is the occlusion the scene already has.
        """
        if t < self.t_break:
            return False
        tt = t - self.t_break
        v = self.leave["v"]
        p0 = np.array([HERO_X, -pelvis_height(self.h, 0.10)])
        p = p0 + v * tt + np.array([0.0, 0.5 * GRAVITY * tt * tt])
        # From the frame the pelvis crosses the lip line, the near ground starts to
        # occlude. Clipping earlier is harmless because the mask keeps everything
        # above the lip, and it removes the one-frame pop at the boundary.
        return bool(p[0] > NEAR_LIP - self.h * 0.02)

    # -- dispatch -----------------------------------------------------------

    def state(self, t):
        """Return (hero_pose, foe_pose, camera).

        Either pose may be None: the hero is gone once the void takes it, and the
        renderer draws one figure instead of two on those frames.
        """
        if t < self.t_shove:
            return self._approach(t)
        if t < self.t_break:
            return self._shove(t)
        if t < self.t_drop:
            return self._break(t)
        if t < self.t_still:
            return self._drop(t)
        return self._still(t)

    # -- approach -----------------------------------------------------------

    def _foe_x(self, t):
        u = clamp(t / max(T_APPROACH, 1e-6))
        # A walk, not a sprint: the horror is how ordinary the approach is.
        return lerp(FOE_FROM, FOE_STOP, ease_in_out(smoothstep(u)) ** 0.92)

    def _foe_walk(self, t, *, lean=0.08):
        h = self.h
        g = self.perf.walk
        x = self._foe_x(t)
        phase = ((x - FOE_FROM) / g.D) % 1.0
        hip = -pelvis_height(h) * g.hip_frac + g.hip_offset(phase)
        fn, pn = g.foot(phase, x, 0.0, side=0.0)
        ff, pf = g.foot(phase, x, 0.0, side=0.5)
        chest = np.array([x, hip - P["spine"] * h * 0.55])
        hands = self.perf.arm_targets(phase, chest, g.arm_swing, lean)
        return build_pose((x, hip), h, facing=1.0, lean=lean, curl=0.08,
                          foot_near=fn, foot_far=ff, pitch_near=pn, pitch_far=pf,
                          hand_near=hands[0], hand_far=hands[1],
                          tone="silhouette")

    def _approach(self, t):
        h = self.h
        u = clamp(t / max(T_APPROACH, 1e-6))

        # The hero looks out over the void. A breath, and a slow weight shift onto
        # the near foot -- a body at rest at the edge of something, not a statue.
        sway = math.sin(2.0 * math.pi * u * 0.8)
        hero = self._hero_pose(look_out=1.0, brace=0.10 * smoothstep(u))
        hero = _translate(hero, np.array([h * 0.006 * sway, math.sin(2.0 * math.pi * u * 1.1) * 1.8]))

        cam = dict(x=lerp(FOE_FROM + 820.0, CAM_X, smoothstep(clamp(u / 0.94))),
                   zoom=lerp(CAM_ZOOM - 0.04, CAM_ZOOM, smoothstep(u)),
                   height=CAM_EYE, lead=0.0, tilt=0.0, rise=0.0, shake=0.0)
        return hero, self._visible(self._foe_walk(t), cam, margin=120.0), cam

    # -- shove --------------------------------------------------------------

    def _shove(self, t):
        """The silhouette's hands arrive and drive.

        The hero is still grounded here: this is the beat where the feet are
        skidding and the body has not yet been given to gravity. It is short --
        nine frames -- because the interesting part is what happens after it.
        """
        h = self.h
        s = clamp((t - self.t_shove) / T_SHOVE)
        drive = smoothstep(s)

        # The hero, driven forward and pitched. The hips travel further than the
        # head because the impulse arrives at the shoulders and the legs have to
        # catch up.
        hero = self._hero_pose(look_out=0.4, brace=0.30, lean_extra=0.34 * drive)
        # Translate horizontally only. A vertical translate of a solved pose pushes
        # its toes through the floor, which is exactly what the assertion caught.
        hero = _translate(hero, np.array([h * 0.075 * drive, 0.0]))

        # The silhouette, throwing its weight through the push.
        x = lerp(FOE_STOP, FOE_STOP + h * 0.03, drive)
        hip = -pelvis_height(h, lerp(0.10, 0.26, drive))
        lean = lerp(0.08, 0.54, drive)
        chest = np.array([x, hip - P["spine"] * h * 0.54])

        contact, s_t = self._contact(hero, t)
        # The reach and the drive are different beats and they need different
        # curves. The hand travels on an arc to the chest (``reach``), and once it
        # is there it stays there while the body goes over (``drive``). Using one
        # eased parameter for both meant the hand was still 240 px short on the
        # frame the hero started to fall -- a shove that never landed.
        reach = smoothstep(clamp(s_t / self.REACH))
        hands = self.perf.arm_targets(0.0, chest, 0.0, lean)
        for i in range(2):
            target = contact + np.array([h * 0.02, i * h * 0.06])
            hands[i] = hands[i] * (1.0 - reach) + target * reach

        # Its rear foot is still planted; the front one has stepped in.
        foe = build_pose((x, hip), h, facing=1.0, lean=lean,
                         curl=0.08 + 0.16 * drive,
                         foot_near=np.array([x + h * 0.22, 0.0]),
                         foot_far=np.array([x - h * 0.02, 0.0]),
                         hand_near=hands[0], hand_far=hands[1],
                         tone="silhouette")

        cam = dict(x=CAM_X, zoom=lerp(CAM_ZOOM, CAM_ZOOM + 0.04, drive),
                   height=CAM_EYE, lead=0.0, tilt=0.0, rise=0.0,
                   shake=0.30 * drive)
        return hero, foe, cam

    # -- break --------------------------------------------------------------

    def _break(self, t):
        """Airborne, tipping forward, still above the floor.

        The feet leave the lip here. Everything after this frame is the projectile
        the shove described, which is why the state is computed from ``_solve_leave``
        rather than authored.
        """
        h = self.h
        tt = t - self.t_break
        v = self.leave["v"]
        p0 = np.array([HERO_X, -pelvis_height(h, 0.10)])
        p = p0 + v * tt + np.array([0.0, 0.5 * GRAVITY * tt * tt])
        pitch = self.leave["spin"] * tt

        # Tipping forward: the body rotates about its own centre, so the head goes
        # down and forward and the legs come up behind. That is what a shove does.
        axis = np.array([math.sin(pitch), -math.cos(pitch)])
        fn = p + np.array([axis[0] * h * 0.44, axis[1] * h * 0.40])
        ff = p + np.array([axis[0] * h * 0.40 - h * 0.06, axis[1] * h * 0.44])

        hero = build_pose(tuple(p), h, facing=1.0,
                          lean=0.30 + 0.55 * pitch, curl=0.20,
                          head_tilt=0.30 * pitch,
                          foot_near=fn, foot_far=ff,
                          pitch_near=-0.30, pitch_far=-0.24)

        # The silhouette stays where the push ended, watching it go. Its arms are
        # still extended: a push is not withdrawn, it is followed through.
        x = FOE_STOP + h * 0.10
        hip = -pelvis_height(h, 0.26)
        chest = np.array([x, hip - P["spine"] * h * 0.54])
        hands = self.perf.arm_targets(0.0, chest, 0.0, 0.54)
        hands[0] = hands[0] + np.array([h * 0.14, -h * 0.10])
        hands[1] = hands[1] + np.array([h * 0.12, -h * 0.06])
        foe = build_pose((x, hip), h, facing=1.0, lean=0.54, curl=0.24,
                         foot_near=np.array([x + h * 0.22, 0.0]),
                         foot_far=np.array([x - h * 0.02, 0.0]),
                         hand_near=hands[0], hand_far=hands[1],
                         tone="silhouette")

        cam = dict(x=lerp(CAM_X, CAM_X + 26.0, smoothstep(tt / T_BREAK)),
                   zoom=lerp(CAM_ZOOM + 0.04, CAM_ZOOM + 0.09, smoothstep(tt / T_BREAK)),
                   height=CAM_EYE, lead=0.0, tilt=0.0, rise=0.0,
                   shake=0.30 * math.exp(-5.0 * tt))
        return hero, foe, cam

    # -- drop ---------------------------------------------------------------

    def _fall_pose(self, t):
        """The hero, ballistic, at any time after the break -- or None if off frame.

        Returns None once the body has left the bottom of frame, which is a fact
        about the projection, not a decision: the camera has a finite view and a
        falling body leaves it. That is the difference between a fall that reads and
        a fall that is cut away from.
        """
        h = self.h
        tt = t - self.t_break
        v = self.leave["v"]
        p0 = np.array([HERO_X, -pelvis_height(h, 0.10)])
        p = p0 + v * tt + np.array([0.0, 0.5 * GRAVITY * tt * tt])
        pitch = self.leave["spin"] * tt

        axis = np.array([math.sin(pitch), -math.cos(pitch)])
        fn = p + np.array([axis[0] * h * 0.44, axis[1] * h * 0.40])
        ff = p + np.array([axis[0] * h * 0.40 - h * 0.06, axis[1] * h * 0.44])
        return build_pose(tuple(p), h, facing=1.0,
                          lean=0.30 + 0.62 * pitch, curl=0.20,
                          head_tilt=0.30 * pitch,
                          foot_near=fn, foot_far=ff,
                          pitch_near=-0.30, pitch_far=-0.24)

    def _visible(self, pose, cam, *, margin=90.0):
        """Is any part of ``pose`` inside the frame the camera describes?

        Uses the same projection the renderer will use, so the answer is about this
        frame rather than about a guess. Both axes matter: a walk-on that enters
        from the side has a sliver of a figure inside the frame, and drawing that
        sliver -- a torso with no head, half a leg -- is how a shot acquires the
        look of a bug. A body is drawn entirely or not at all, and the margin is
        chosen so that it appears the frame it is meaningfully on screen.
        """
        if pose is None:
            return None
        from .film import H as FH, W as FW
        from .stage import Projector
        proj = Projector(FW, FH, cam_x=cam["x"], cam_y=cam.get("rise", 0.0),
                         eye=cam["height"], zoom=cam["zoom"], tilt=cam["tilt"])
        pts = [np.asarray(v) for _n, v in pose.joints()]
        sxs = np.array([float(proj.sx(p[0])) for p in pts])
        sys_ = np.array([float(proj.sy(p[1])) for p in pts])
        if sxs.max() < -margin or sxs.min() > FW + margin:
            return None
        if sys_.min() > FH + margin or sys_.max() < -margin:
            return None
        return pose

    def _drop(self, t):
        """The void has it, and the camera does not follow.

        The lens holds on the lip. A camera operator tracking a fall would have to
        point at the floor of a valley they cannot see, and the whole point of the
        shot is that nobody gets to see the bottom.
        """
        foe = self._foe_at_lip(t, step=smoothstep(clamp((t - self.t_drop) / 0.5)))
        cam = dict(x=lerp(CAM_X, CAM_X + 22.0, smoothstep(clamp((t - self.t_break) / 0.9))),
                   zoom=lerp(CAM_ZOOM + 0.06, CAM_ZOOM + 0.02, smoothstep(clamp((t - self.t_break) / 0.9))),
                   height=CAM_EYE, lead=0.0, tilt=0.0, rise=0.0, shake=0.0)
        hero = self._visible(self._fall_pose(t), cam)
        return hero, foe, cam

    # -- still --------------------------------------------------------------

    def _foe_at_lip(self, t, *, step=0.0):
        """The silhouette walks the last step to the edge and looks down."""
        h = self.h
        x = lerp(FOE_STOP + h * 0.10, HERO_X + h * 0.16, step)
        g = self.perf.walk
        phase = ((x - FOE_FROM) / g.D) % 1.0
        if step >= 1.0:
            hip = -pelvis_height(h, 0.10)
            fn = np.array([x + h * 0.10, 0.0])
            ff = np.array([x - h * 0.07, 0.0])
            pn = pf = 0.0
        else:
            hip = -pelvis_height(h) * g.hip_frac + g.hip_offset(phase)
            fn, pn = g.foot(phase, x, 0.0, side=0.0)
            ff, pf = g.foot(phase, x, 0.0, side=0.5)

        # Leaning out over the edge to see bottom: the head goes past the lip,
        # which is the only thing in the shot that acknowledges the drop is deep.
        lean = lerp(0.40, 0.62, step)
        chest = np.array([x, hip - P["spine"] * h * 0.54])
        hands = self.perf.arm_targets(0.0, chest, 0.0, lean)
        return build_pose((x, hip), h, facing=1.0, lean=lean,
                          curl=0.10 + 0.14 * step,
                          head_tilt=0.26 * step,
                          foot_near=fn, foot_far=ff,
                          pitch_near=pn, pitch_far=pf,
                          hand_near=hands[0], hand_far=hands[1],
                          tone="silhouette")

    def _still(self, t):
        h = self.h
        u = clamp((t - self.t_drop) / max(T_STILL, 1e-6))
        # The body is still falling for the first frames of this beat. It stops
        # being drawn when it leaves the frame, not when the beat changes.
        foe = self._foe_at_lip(t, step=smoothstep(clamp(u / 0.34)))
        cam = dict(x=lerp(CAM_X + 22.0, CAM_X + 44.0, smoothstep(u)),
                   zoom=lerp(CAM_ZOOM + 0.02, CAM_ZOOM + 0.16, smoothstep(u)),
                   height=CAM_EYE, lead=0.0, tilt=0.0, rise=0.0, shake=0.0)
        hero = self._visible(self._fall_pose(t), cam)
        return hero, foe, cam


# ------------------------------------------------------------------- helpers

def _translate(pose, offset):
    """Move a whole solved pose. Used for breathing, which is whole-body."""
    offset = np.asarray(offset, float)
    for name, val in pose.joints():
        setattr(pose, name, val + offset)
    return pose


