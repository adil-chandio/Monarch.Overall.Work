"""The film: shots, staging and the performance.

Rewritten from the first cut, which walked a figure across a desert and stopped.
The figure was correct and the film was not, because a cut needs decisions, not
locomotion. This one has four shots with a reason to be in that order:

    SHOT 1  the figure is alone and still. The camera crouches low. A head turn
            starts before anything else moves -- a thought, then a body.

    SHOT 2  anticipation. The figure sinks, coils, and the camera pushes in on
            the compression. It does not jump yet. The wait is the shot.

    SHOT 3  the jump, and the landing that costs. Low camera, wide enough to
            hold the arc; dust on the impact; the body absorbs and recovers.

    SHOT 4  the aftermath. It looks back at the gap it crossed, shrugs, and
            walks. The camera lets it go and stops moving first.

Everything here is still driven by three authorities -- the gait for the feet,
gravity for anything airborne, springs for everything that gets knocked -- with
one addition: a global timeline counter (``Tick``) that lets a shot be written
against a running clock so that anticipation, follow-through and overlap line up
without hand-tuned offsets at every call site.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .rig import P, build_pose, clamp, lerp, pelvis_height, smoothstep, ease_in_out
from .motion import Gait, settle


FPS = 24
W, H = 1080, 1920
FIG_H = 700.0          # figure height, world units
GRAVITY = 2900.0       # world units / s^2

# The one piece of set that matters. The figure has to stand on the lip, not
# near it, and the gap has to be wide enough that a jump across it is a decision.
GAP_LEFT = -150.0
GAP_RIGHT = 780.0
GAP_DEPTH = 430.0
GAP = (GAP_LEFT, GAP_RIGHT, GAP_DEPTH)

# Where the figure stands before and after. Both are far enough back from the
# lip that its feet are on solid ground with room to spare.
STAND_X = -430.0
EDGE_X = GAP_LEFT - 96.0        # coiled, toes almost on the lip
LAND_X = GAP_RIGHT + 88.0       # first step beyond the far lip


# --------------------------------------------------------------------- camera

@dataclass
class Camera:
    """A camera move, described rather than keyframed.

    ``lead`` is how far ahead of the subject the frame looks: a camera that
    always centres its subject feels like a targeting reticle, so the figure is
    kept off-centre and allowed to move inside the frame.
    ``push`` is the zoom at the end of the shot; the move is eased.
    ``height`` is where the lens sits, as a fraction of frame height. A low lens
    makes a figure loom, a high one makes it small and observed.
    """
    x: float = 0.0
    zoom0: float = 1.0
    zoom1: float = 1.0
    height: float = 0.25
    lead: float = 0.10
    lead_end: float | None = None
    tilt: float = 0.0
    shake: float = 0.0
    # Vertical follow, in world units. Zero keeps the camera planted; a positive
    # value lifts the frame, which is right for the top half of a jump arc.
    rise: float = 0.0


def camera_state(cam, u):
    """Interpolate a camera move at shot-progress ``u``."""
    e = ease_in_out(smoothstep(clamp(u)))
    lead_end = cam.lead if cam.lead_end is None else cam.lead_end
    return dict(
        x=cam.x,
        zoom=lerp(cam.zoom0, cam.zoom1, e),
        height=cam.height,
        lead=lerp(cam.lead, lead_end, e),
        tilt=cam.tilt,
        shake=cam.shake * (1.0 - clamp(u)) ** 2,
        rise=cam.rise,
    )


# -------------------------------------------------------------------- helpers

def hip_standing(h):
    """Hip height for a standing figure: knees almost straight but not locked."""
    return pelvis_height(h, 0.06)


def arc(from_pose_tip, to_pose_tip, u, height=0.12):
    """A tip position along an arc instead of a straight line.

    Every natural swing is an arc; interpolating a hand between two points in a
    straight line is the single most common reason a rig looks like it is sliding
    instead of reaching. The arc is bowed perpendicular to the chord by
    ``height`` of the chord's length.
    """
    p0 = np.asarray(from_pose_tip, float)
    p1 = np.asarray(to_pose_tip, float)
    chord = p1 - p0
    n = np.array([-chord[1], chord[0]])
    norm = float(np.hypot(n[0], n[1]))
    if norm > 1e-6:
        n = n / norm
    bow = math.sin(math.pi * clamp(u)) * height * norm
    return p0 + chord * u + n * bow


# ----------------------------------------------------------------- performer

class Performer:
    """The figure plus its two gaits. Height is a world-space number."""

    def __init__(self, height=FIG_H):
        self.height = height
        # A walk always has a foot down; stance 0.62 leaves 38% of the cycle in
        # swing, so one foot is always loaded. Stride 0.53 because anything
        # longer over-extends the leg at touchdown -- see Gait.max_stride.
        self.walk = Gait(height, stride=0.53, stance=0.62, lift=0.048,
                         bob=0.020, arm_swing=0.44, lean=0.055, hip_frac=0.940)
        # A run does not: stance 0.34 means 32% of each cycle is airborne.
        self.run = Gait(height, stride=0.86, stance=0.34, lift=0.115,
                        bob=0.050, arm_swing=1.10, lean=0.175, hip_frac=0.905)

    def arm_targets(self, phase, chest, swing, lean, *, up=0.0, spread=0.0):
        """Hand positions on an arc that never let the IK lock the elbow.

        The hands sit on a circle of radius 0.86 of full arm reach. Inside the
        reach there is always a bend to find; at the reach the solver straightens
        the arm, which is what a scarecrow looks like. The arc is centred on
        "hanging down and slightly forward" so the arms clear the thighs.
        """
        h = self.height
        reach = (P["upper_arm"] + P["forearm"]) * h * 0.86
        out = []
        for sign in (+1.0, -1.0):
            base = math.pi * 0.5 - 0.10
            ang = base + swing * sign + lean * 0.35 - up
            out.append(chest + np.array([math.cos(ang) * reach,
                                         math.sin(ang) * reach]))
        return out


# --------------------------------------------------------------------- shots

class Shot:
    def __init__(self, name, duration, fn):
        self.name = name
        self.duration = duration
        self.fn = fn

    def __call__(self, t, perf):
        # Jump.pose_at is a bound method taking only t; plain shot functions take
        # (t, duration, performer). Adapting here keeps every call site simple.
        if getattr(self.fn, "__self__", None) is not None:
            return self.fn(t, perf)
        return self.fn(t, self.duration, perf)


def shot_alone(t, dur, perf):
    """SHOT 1 -- stillness, then a decision.

    The whole shot is one head turn and one weight shift. It exists to establish
    that this figure has intent, so that the jump in shot 3 is something it chose
    rather than something that happened to it.
    """
    h = perf.height
    u = clamp(t / dur)

    # A breath, not a pose: two centimetres of vertical drift over the hold.
    breath = math.sin(2.0 * math.pi * u * 1.4) * 2.2
    hip_y = -hip_standing(h) + breath

    # Anticipation of the turn: the weight goes onto the near foot a beat before
    # the head moves, which is how a real turn starts.
    shift = smoothstep(clamp((u - 0.18) / 0.28))
    look = smoothstep(clamp((u - 0.34) / 0.30))

    X = STAND_X
    fn = np.array([X + h * (0.070 - 0.020 * shift), 0.0])
    ff = np.array([X - h * (0.050 - 0.014 * shift), 0.0])

    head_tilt = -0.05 - 0.52 * look
    lean = -0.02 - 0.045 * look
    facing = 1.0 - 0.30 * look

    chest = np.array([X, hip_y - P["spine"] * h * 0.55])
    hands = perf.arm_targets(0.0, chest, 0.0, lean)
    # The near hand lifts as the weight settles: secondary, small, and late.
    hands[0] = hands[0] + np.array([-h * 0.030 * shift, -h * 0.052 * shift * look])

    pose = build_pose((X, hip_y), h, facing=facing, lean=lean, curl=0.070,
                      head_tilt=head_tilt,
                      foot_near=fn, foot_far=ff, pitch_near=0.0, pitch_far=0.0,
                      hand_near=hands[0], hand_far=hands[1])

    # A slow dolly right, so the gap creeps into frame while the figure is still
    # deciding. The audience sees the problem before the character admits it.
    cam = Camera(x=X + h * 0.28 * u, zoom0=1.66, zoom1=1.62, height=0.245,
                 lead=0.115, lead_end=0.055)
    return pose, camera_state(cam, u)


def shot_coil(t, dur, perf):
    """SHOT 2 -- walk the last two steps to the lip, then coil.

    Two actions in one shot: the approach, which has to look like it means it,
    and the anticipation, which has to look like it is holding back. The cut
    from the previous shot lands on the first footfall, so the step happens in
    the same instant the audience changes angle.
    """
    h = perf.height
    g = perf.walk
    u = clamp(t / dur)

    # Walk from STAND_X to EDGE_X over the first 45% of the shot.
    travel = smoothstep(clamp(u / 0.45))
    x = lerp(STAND_X, EDGE_X, travel)

    # Settle: sink into the coil over the last half, hold, then a final
    # compression that releases into the cut.
    sink = smoothstep(clamp((u - 0.46) / 0.40))
    extra = smoothstep(clamp((u - 0.86) / 0.14)) * 0.10

    walk_fade = 1.0 - smoothstep(clamp((u - 0.40) / 0.12))
    phase = ((x - STAND_X) / g.D) % 1.0

    crouch = 0.06 + 0.58 * sink + extra * 0.35
    hip_stand = -pelvis_height(h, crouch)
    hip_walk = -pelvis_height(h) * g.hip_frac + g.hip_offset(phase)
    hip_y = lerp(hip_walk, hip_stand, 1.0 - walk_fade)

    # Feet: walk cycle while moving, then plant with the near toe on the lip.
    # The last stride has to be cut short at the lip, because a walk cycle knows
    # nothing about the hole: without this clamp the trailing foot swings out
    # over the void and the figure appears to walk on air for two frames.
    fn_w, pn_w = g.foot(phase, x, 0.0, side=0.0)
    ff_w, pf_w = g.foot(phase, x, 0.0, side=0.5)
    # The clamp has to account for the toe, which sits up to 0.62 foot-lengths
    # in front of the ankle contact. Clamping the contact to the lip still puts
    # the toe over the edge, so the contact is clamped short by that much plus a
    # margin -- and the swing foot is compressed by its airborne height, because
    # a foot high in the air is a foot whose toe is not over anything.
    toe_reach = h * P["foot"] * 0.62
    limit = GAP_LEFT - toe_reach - h * 0.02
    fn_w = np.array([min(fn_w[0], limit), fn_w[1]])
    ff_w = np.array([min(ff_w[0], limit), ff_w[1]])
    fn_s = np.array([EDGE_X + h * 0.098, 0.0])
    ff_s = np.array([EDGE_X - h * 0.088, 0.0])
    k = 1.0 - walk_fade
    fn = np.array([lerp(fn_w[0], fn_s[0], k), lerp(fn_w[1], fn_s[1], k)])
    ff = np.array([lerp(ff_w[0], ff_s[0], k), lerp(ff_w[1], ff_s[1], k)])
    pn = lerp(pn_w, 0.0, k)
    pf = lerp(pf_w, 0.0, k)

    back = smoothstep(clamp((u - 0.50) / 0.42))

    # A coil is a squat, not a bow: the chest stays over the feet and the fold
    # goes into the spine's curl, because leaning the whole torso this far reads
    # as a figure folding in half.
    lean = lerp(g.lean, 0.055 + 0.12 * sink, k)

    chest = np.array([x + h * 0.045 * sink, hip_y - P["spine"] * h * 0.50])
    hands = perf.arm_targets(phase, chest, g.arm_swing * walk_fade, lean)
    # Arms swing back and keep drifting after the body has stopped.
    hands[0] = hands[0] + np.array([-h * (0.180 * back), h * (0.105 * back)])
    hands[1] = hands[1] + np.array([-h * (0.150 * back), h * (0.090 * back)])

    pose = build_pose((x + h * 0.045 * sink, hip_y), h, facing=1.0,
                      lean=lean, curl=lerp(0.055, 0.12 + 0.26 * sink, k),
                      foot_near=fn, foot_far=ff,
                      pitch_near=pn, pitch_far=pf,
                      hand_near=hands[0], hand_far=hands[1],
                      squash=1.0 - 0.075 * sink * k)

    # The lens pulls back as the figure goes down, because a crouched figure is
    # short and a push-in would crop the very feet that have to sit on the lip.
    cam = Camera(x=lerp(STAND_X + h * 0.10, EDGE_X + h * 0.055, travel),
                 zoom0=1.66, zoom1=1.46, height=0.234,
                 lead=0.085, lead_end=0.135)
    return pose, camera_state(cam, u)


@dataclass
class Jump:
    """The jump itself, solved rather than posed.

    Apex fixes the flight time: for a rise A under gravity g, launch speed is
    sqrt(2gA) and the whole flight is 2*sqrt(2A/g). Given that, the horizontal
    speed is whatever carries the figure across the gap in exactly that time --
    which is why this jump looks like it had to be committed to.

    The shapes on either side of the flight are springs: an anticipation coil
    that continues past the pose it was aiming for, and a landing absorb that
    dips, overshoots and settles.
    """
    apex: float = 0.60          # of figure height
    gap: float = 1.15           # horizontal distance, in figure heights
    coil: float = 0.42          # seconds of crouch before launch
    recover: float = 0.85       # seconds of landing settle after touchdown
    run_in: float = 0.0         # seconds of run before the coil

    @property
    def total(self):
        return self.run_in + self.coil + self.flight + self.recover

    def __post_init__(self):
        self.h = None
        self.flight = None

    def setup(self, h):
        self.h = h
        self.apex_px = self.apex * h
        # Apex fixes the flight time: t = 2*sqrt(2A/g) for a rise A and a return
        # to the same height. The horizontal speed is then whatever carries the
        # figure across in exactly that time -- so the jump is committed to, in
        # the same way a real one is: you cannot adjust halfway.
        self.flight = 2.0 * math.sqrt(2.0 * self.apex_px / GRAVITY)
        self.x0 = EDGE_X
        self.x_land = LAND_X
        self.gap_px = self.x_land - self.x0
        self.speed = self.gap_px / self.flight
        self.take = self.run_in + self.coil
        self.land = self.take + self.flight
        return self

    # -- phases -------------------------------------------------------------

    def phase(self, t):
        if t < self.run_in:
            return "run"
        if t < self.take:
            return "coil"
        if t < self.land:
            return "air"
        return "land"

    def pose_at(self, t, perf):
        h = self.h
        if self.h is None:
            self.setup(perf.height)
            h = self.h

        ph = self.phase(t)

        if ph == "coil":
            u = (t - self.run_in) / max(self.coil, 1e-6)
            # Down fast, hold, then a tiny extra compression just before release:
            # the "settle" that tells the eye the spring is loaded.
            sink = smoothstep(clamp(u / 0.62))
            extra = smoothstep(clamp((u - 0.74) / 0.20)) * 0.10
            crouch = 0.06 + 0.56 * sink + extra * 0.30
            hip_y = -pelvis_height(h, crouch)

            back = smoothstep(clamp((u - 0.10) / 0.55))
            fn = np.array([self.x0 + h * 0.098, 0.0])
            ff = np.array([self.x0 - h * 0.088, 0.0])
            # A coil is a squat, not a bow. The chest stays over the feet and the
            # fold goes into the spine's curl, because leaning the whole torso
            # this far reads as a figure folding in half.
            lean = 0.06 + 0.14 * sink

            chest = np.array([self.x0 + h * 0.045 * sink,
                              hip_y - P["spine"] * h * 0.50])
            hands = perf.arm_targets(0.0, chest, 0.0, lean)
            hands[0] = hands[0] + np.array([-h * (0.170 * back), h * (0.100 * back)])
            hands[1] = hands[1] + np.array([-h * (0.145 * back), h * (0.085 * back)])

            pose = build_pose((self.x0 + h * 0.045 * sink, hip_y), h,
                              facing=1.0, lean=lean, curl=0.12 + 0.26 * sink,
                              foot_near=fn, foot_far=ff,
                              pitch_near=0.0, pitch_far=0.0,
                              hand_near=hands[0], hand_far=hands[1],
                              squash=1.0 - 0.075 * sink)

            # The compression has to stay in frame. As the hips drop the figure
            # gets shorter, so the lens pulls back to hold the whole body: a
            # push-in here would crop the feet exactly when they matter.
            cam = Camera(x=self.x0 + h * 0.055 * sink, zoom0=1.62, zoom1=1.44,
                         height=0.232, lead=0.075, lead_end=0.145)
            return pose, camera_state(cam, u)

        if ph == "air":
            u = (t - self.take) / max(self.flight, 1e-6)
            u = min(u, 0.999)
            x = self.x0 + self.speed * (t - self.take) + (self.x_land - self.x0) * 0.0
            x = self.x0 + self.speed * (t - self.take)

            # A true parabola: zero at both ends, apex at the middle.
            rise = 4.0 * self.apex_px * u * (1.0 - u)
            hip_y = -pelvis_height(h, 0.02) - rise

            # Tuck on the way up, extend to meet the floor on the way down. The
            # switch happens past the apex, because a falling body has to reach.
            tuck = math.sin(math.pi * clamp(u * 1.06)) ** 0.72

            # In the air the feet are targets, not contacts. The legs tuck on
            # the way up and reach for the far lip on the way down, which is the
            # only cue the eye needs that the landing is intended.
            fn = np.array([x + h * (0.055 + 0.085 * u), hip_y + h * (0.46 - 0.30 * tuck)])
            ff = np.array([x - h * (0.070 - 0.075 * u), hip_y + h * (0.49 - 0.34 * tuck)])
            pn = lerp(-0.16, 0.10, u)
            pf = lerp(-0.10, 0.06, u)

            lean = lerp(0.42, -0.06, smoothstep(u))
            chest = np.array([x, hip_y - P["spine"] * h * 0.48])
            # Arms: thrown up by the launch, then trailing above the head, then
            # starting to come down before the feet land.
            up = math.sin(math.pi * clamp(u * 1.20)) ** 0.65
            down = smoothstep(clamp((u - 0.68) / 0.32))
            hands = perf.arm_targets(0.0, chest, 0.0, lean)
            hands[0] = hands[0] + np.array([-h * 0.115 * up + h * 0.05 * down,
                                            -h * 0.235 * up + h * 0.24 * down])
            hands[1] = hands[1] + np.array([+h * 0.135 * up - h * 0.06 * down,
                                            -h * 0.200 * up + h * 0.21 * down])

            # Stretch on the way up, squash on the way down: the arc is a spring.
            stretch = 0.030 * math.sin(math.pi * clamp(u * 1.5)) if u < 0.66 else 0.0

            pose = build_pose((x, hip_y), h, facing=1.0, lean=lean, curl=0.05,
                              foot_near=fn, foot_far=ff,
                              pitch_near=pn, pitch_far=pf,
                              hand_near=hands[0], hand_far=hands[1],
                              stretch=stretch)

            # The camera follows the arc only a little and pulls back instead.
            #
            # Tracking the rise fully would remove the sense of height, and
            # tracking 62% of it -- the first attempt -- pushed the far lip off
            # the bottom of the frame at the apex, which is precisely the moment
            # the gap has to be visible. So the lens opens up to keep both the
            # figure and the lip in shot, and the camera rises by 30%, which is
            # enough to keep the figure from hitting the top edge without
            # letting the floor slide out of frame.
            # The floor row at touchdown is already near the bottom edge, so the
            # only way to keep both the head and the lip in shot is to hold the
            # lens and let the figure climb through the upper frame. A jump that
            # stays centred is a jump with no height in it.
            # The lens opens through the arc, which does two things at once: it
            # keeps the far lip inside the bottom of frame at touchdown, and a
            # widening frame on the way down reads as the ground coming up to
            # meet the figure rather than the figure falling onto it.
            cam = Camera(x=x + h * 0.02, zoom0=1.46, zoom1=1.16,
                         height=0.240, lead=0.085, lead_end=0.075,
                         rise=0.16 * rise)
            return pose, camera_state(cam, clamp(u))

        # Landed: absorb, overshoot, recover. One damped spring driving crouch,
        # and a second, lagging one driving the arms, so they arrive after the
        # body has already stopped going down.
        ot = t - self.land
        absorb = math.exp(-5.6 * ot) * math.cos(2.0 * math.pi * 1.85 * ot)
        crouch = clamp(0.50 + 0.40 * absorb)
        hip_y = -pelvis_height(h, crouch)

        # The near foot lands first and forward of the lip, the far one behind
        # it: a two-footed landing at the same instant reads as a cut-out.
        first = smoothstep(clamp(ot / 0.12))
        # The far foot is the one that used to end up pointing into the hole: its
        # ankle lands behind LAND_X and the toe, which sits a third of a foot
        # further back, cleared the lip by nothing. Both feet are now placed so
        # that ankle *and* toe are past the far lip with margin.
        fn = np.array([self.x_land + h * (0.150 - 0.030 * first), 0.0])
        ff = np.array([self.x_land + h * (0.020 + 0.020 * first), 0.0])
        lean = lerp(0.44, 0.03, smoothstep(clamp(ot / 0.55)))

        chest = np.array([self.x_land + h * 0.02 * absorb,
                          hip_y - P["spine"] * h * 0.48])
        bal = math.exp(-4.2 * ot) * math.cos(2.0 * math.pi * 1.6 * ot - 0.9)
        hands = perf.arm_targets(0.0, chest, 0.0, lean)
        hands[0] = hands[0] + np.array([-h * 0.135 * bal, -h * 0.10 * bal])
        hands[1] = hands[1] + np.array([+h * 0.120 * bal, -h * 0.085 * bal])

        pose = build_pose((self.x_land + h * 0.02 * absorb, hip_y), h,
                          facing=1.0, lean=lean, curl=0.13 + 0.08 * bal,
                          foot_near=fn, foot_far=ff,
                          pitch_near=0.0, pitch_far=0.0,
                          hand_near=hands[0], hand_far=hands[1],
                          squash=1.0 - 0.085 * max(0.0, absorb))

        # The camera starts where the air phase left it -- no snap across the
        # cut at touchdown -- and then settles down as the figure does, a beat
        # later. The first frame after the landing is a continuation, not a new
        # setup; the earlier version jumped from lens 1.16 to 1.52 in one frame
        # and threw the floor off the bottom of the screen.
        land_rise = 0.16 * self.apex_px
        settle_lag = 0.62 * self.apex_px * math.exp(-3.4 * ot) * math.cos(
            2.0 * math.pi * 0.55 * ot)
        rise = land_rise * math.exp(-2.6 * ot) + max(0.0, settle_lag) * 0.25
        cam = Camera(x=self.x_land + h * 0.02, zoom0=1.16, zoom1=1.58,
                     height=0.245, lead=0.075, lead_end=0.070,
                     rise=rise)
        return pose, camera_state(cam, clamp(ot / max(self.recover, 1e-6)))


def shot_after(t, dur, perf):
    """SHOT 4 -- the look back, and letting it go.

    Two beats: the figure turns to look at what it just crossed, then walks out.
    The camera stops moving before the figure does, so the last thing on screen
    is the figure leaving the frame rather than the frame chasing it.
    """
    h = perf.height
    g = perf.walk
    u = clamp(t / dur)

    turn = smoothstep(clamp(u / 0.22))
    walk_start = 0.40
    walking = smoothstep(clamp((u - walk_start) / 0.20))

    # Position: stands on the far lip, turns to look back across the gap, then
    # walks away from it. Integrated so the stride matches the speed.
    walk_time = max(0.0, t - walk_start * dur)
    speed = 430.0
    x = LAND_X + 12.0 + speed * walk_time * walking

    phase = (x / g.D) % 1.0
    hip_stand = -pelvis_height(h, 0.06)

    if walking < 1.0:
        hip_y = lerp(hip_stand, -pelvis_height(h) * g.hip_frac + g.hip_offset(phase),
                     walking)
    else:
        hip_y = -pelvis_height(h) * g.hip_frac + g.hip_offset(phase)

    head_tilt = -0.42 * turn * (1.0 - walking)
    lean = lerp(-0.03 * turn, g.lean, walking)

    fn_s, pn_s = g.foot(phase, x, 0.0, side=0.0)
    ff_s, pf_s = g.foot(phase, x, 0.0, side=0.5)
    # Standing: both feet set back from the lip, because a figure that has just
    # landed does not stand with its toes over the edge.
    fn = np.array([lerp(LAND_X + h * 0.060, fn_s[0], walking),
                   lerp(0.0, fn_s[1], walking)])
    ff = np.array([lerp(LAND_X - h * 0.070, ff_s[0], walking),
                   lerp(0.0, ff_s[1], walking)])
    pn = lerp(0.0, pn_s, walking)
    pf = lerp(0.0, pf_s, walking)

    chest = np.array([x, hip_y - P["spine"] * h * 0.55])
    hands = perf.arm_targets(phase, chest, g.arm_swing * walking, lean)

    pose = build_pose((x, hip_y), h, facing=1.0, lean=lean, curl=0.07,
                      head_tilt=head_tilt,
                      foot_near=fn, foot_far=ff, pitch_near=pn, pitch_far=pf,
                      hand_near=hands[0], hand_far=hands[1])

    # The camera holds on the lip for the look back, then trails the figure as it
    # walks away -- following at 0.62 of its speed, not 1.0, so it falls behind
    # and the figure drifts toward the edge of frame, and not 0.0 either, because
    # a film that ends on an empty desert has ended by accident. The gap stays
    # in shot for as long as the figure is visible, which is the point of the
    # last look back.
    e = ease_in_out(smoothstep(clamp((u - 0.34) / 0.50)))
    # The camera trails at 0.86 of the figure's speed and the lead shrinks, so
    # the figure drifts toward the right third of frame and stays in it: a
    # 9:16 frame is only 540 world units wide at this lens, so a trailing camera
    # loses its subject within half a second if it follows any slower.
    cam = dict(x=lerp(GAP_RIGHT - h * 0.10, x * 0.86, e),
               zoom=lerp(1.72, 1.34, e),
               height=0.250, lead=lerp(0.055, 0.02, e), tilt=0.0, shake=0.0,
               rise=0.0)
    return pose, cam


def build_shots(perf):
    jump = Jump().setup(perf.height)
    return [
        Shot("alone", 3.1, shot_alone),
        Shot("coil", 2.5, shot_coil),
        Shot("jump", jump.total, jump.pose_at),
        Shot("after", 3.6, shot_after),
    ], jump
