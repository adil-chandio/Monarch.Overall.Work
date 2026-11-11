"""Faces: an expression, drawn on the head the rig already has.

The figure in v1--v3 had one eye dot, which is enough to tell you which way it is
facing and nothing else. That ceiling is the reason this module exists: a head
that can only hold a dot cannot be frightened, and a film about a man walking up
to a penalty with the stadium going quiet is a film about a face.

Two decisions shape everything below.

**The head stays a circle.** An oval with a jaw and a chin would be a different
character, and it would fight the line drawing around it. So the head is the same
circle the rig has always drawn -- filled with paper and given the same heavy rim
-- and the face lives inside it. That is the stickman contract: one circle, and
whatever we put on it is the character.

**The features are geometry, not sprites.** Every eye, brow and mouth is an
ellipse, a tapered stroke or a filled polygon placed in a rotated head-local
frame and scaled by the head radius. That means the face is correct at any size
(in a 700 px close-up and a 40 px long shot), it rotates with the head, and it
mirrors when the figure turns around. A face made of pasted art cannot do any of
those three.

The local frame is (a, b): ``a`` runs from the back of the head toward the face,
``b`` runs down. Both are fractions of the head radius and both rotate with
``head_ang``, so a figure that leans into a shot keeps its eyes level with its
head instead of its eyes staying level with the horizon -- which is the single
most common way a cartoon face reads as broken.

An eye is three marks: a dark oval, a paper disc where the eye is looking, and a
dot inside that disc for the pupil. The paper disc is what makes looking-away
legible; a solid dark eye with a highlight can change shape but cannot point.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

import numpy as np

from . import ink as inkmod


# ------------------------------------------------------------------ expression

@dataclass(frozen=True)
class Face:
    """One expression. Every field is 0..1 unless the comment says otherwise.

    Frozen because expressions get composed: a shot says ``STRAIN.blended(FEAR,
    0.4)`` or ``FOCUS.at(blink=1.0)`` and the preset is never mutated, so a
    named expression cannot drift because one scene edited it in place.
    """

    blink: float = 0.0          # 0 open, 1 shut
    eye_open: float = 1.0       # aperture multiplier; <1 is a suspicious squint
    pupil_a: float = 0.0        # where the eyes look, +forward  (-1..1)
    pupil_b: float = 0.0        # +down (-1..1)
    squint: float = 0.0         # 0 round eyes, 1 the happy "^" arch
    brow_raise: float = 0.0     # -1 low and heavy, +1 up the forehead
    brow_angle: float = 0.0     # + inner ends up (worried), - inner ends down (angry)
    brow_pinch: float = 0.0     # brows pulled together toward the nose
    mouth_curve: float = 0.12   # -1 frown, +1 smile
    mouth_open: float = 0.0     # 0 closed line, 1 a full shout
    mouth_width: float = 1.0    # 0.6 pursed, 1.3 wide
    mouth_shift: float = 0.0    # + pushes the mouth toward the front of the face
    teeth: float = 0.0          # paper band inside an open mouth
    sweat: float = 0.0
    blush: float = 0.0
    turn: float = 0.30          # 0 frontal-ish, 1 full profile (far eye vanishes)
    jaw: float = 0.0            # >0 drops the chin; use with mouth_open

    # -- composition -------------------------------------------------------

    def at(self, **kw):
        return replace(self, **kw)

    def blended(self, other, k):
        """Linear blend toward ``other``, k=0 -> this, k=1 -> other."""
        k = 0.0 if k < 0.0 else 1.0 if k > 1.0 else k
        out = {}
        for name in self.__dataclass_fields__:
            a = getattr(self, name)
            b = getattr(other, name)
            out[name] = a + (b - a) * k
        return Face(**out)

    def t(self, k):
        """Blend from NEUTRAL toward this expression, k=0 -> NEUTRAL."""
        return NEUTRAL.blended(self, k)

    def eye_aperture(self):
        return max(0.0, (1.0 - self.blink) * self.eye_open)


# The vocabulary. Named for what the face is doing, not for an emotion -- "fear"
# is a judgement, "shocked" is a shape, and the shape is the thing being drawn.
NEUTRAL = Face()

CALM = Face(brow_raise=0.10, mouth_curve=0.18)

BLINK = Face(blink=1.0)

# Eyes narrowed, brows low and level, mouth a flat line. Walking out of a tunnel
# into a full stadium.
FOCUS = Face(eye_open=0.74, brow_raise=-0.42, brow_angle=-0.18, mouth_curve=-0.18,
             mouth_width=0.86)

# The same face with the jaw set: FOCUS plus the moment before the kick.
GRIT = Face(eye_open=0.62, brow_raise=-0.55, brow_angle=-0.34, brow_pinch=0.45,
            mouth_curve=-0.10, mouth_open=0.24, mouth_width=1.0, teeth=1.0,
            jaw=0.18)

# Breathing hard after the sprint: mouth open, brows up, eyes half shut.
BREATH = Face(eye_open=0.66, brow_raise=0.42, brow_angle=0.22, mouth_curve=-0.30,
              mouth_open=0.38, mouth_width=0.92, jaw=0.30, sweat=0.18)

JOY = Face(eye_open=0.30, squint=1.0, brow_raise=0.55, brow_angle=0.30,
           mouth_curve=1.0, mouth_open=0.40, mouth_width=1.20, teeth=1.0,
           blush=0.55, jaw=0.26)

SHOCK = Face(eye_open=1.24, brow_raise=1.0, brow_angle=0.55, mouth_open=0.66,
             mouth_curve=-0.55, mouth_width=0.68, jaw=0.55)

FEAR = Face(eye_open=0.95, brow_raise=0.78, brow_angle=0.72, brow_pinch=0.30,
            mouth_open=0.30, mouth_curve=-0.78, mouth_width=0.78, sweat=0.85,
            jaw=0.26)

RELIEF = Face(eye_open=0.34, blink=0.42, brow_raise=0.20, brow_angle=0.16,
              mouth_curve=0.55, mouth_open=0.16, mouth_width=1.0, jaw=0.14)

# Looking right down the lens. Used once, at the end.
DIRECT = Face(eye_open=0.90, brow_raise=0.18, mouth_curve=0.34, turn=0.06)

# A scowl aimed at somebody else.
DISDAIN = Face(eye_open=0.58, brow_raise=-0.30, brow_angle=-0.62, brow_pinch=0.30,
               mouth_curve=-0.55, mouth_width=0.74, mouth_shift=-0.10)


# -------------------------------------------------------------------- geometry

def _basis(head, head_r, facing, head_ang):
    """Head centre (mask pixels), radius and the rotated local frame.

    ``head`` and ``head_r`` are already in the mask's pixel space -- the caller
    multiplies by the supersample factor, because only the caller knows it.
    """
    c = np.asarray(head, float)
    hr = float(head_r)
    ang = float(head_ang or 0.0) * 0.85
    f = 1.0 if facing >= 0 else -1.0
    ca, sa = math.cos(ang), math.sin(ang)
    fwd = np.array([f * ca, sa])      # toward the face
    dwn = np.array([-f * sa, ca])     # down along the face
    return c, hr, fwd, dwn


def _p(c, hr, fwd, dwn, a, b):
    """Point at face-local (a, b), in fractions of the head radius."""
    return c + (fwd * a + dwn * b) * hr


def _lens(c, hr, fwd, dwn, ca_, cb_, half_w, up, down, curve, n=15):
    """A closed mouth shape: an opening that tapers to points at both corners.

    Sampled rather than a four-point polygon. A quadrilateral has straight edges
    between the corners, which is why an early version of this read as a diamond
    rather than as a mouth -- an opening has to close to nothing at the corners,
    and only a sampled curve does that.
    """
    top, bot = [], []
    for i in range(n):
        u = -1.0 + 2.0 * i / (n - 1)
        taper = max(0.0, 1.0 - u * u) ** 0.62
        a = ca_ + u * half_w
        # Corner lift: positive ``curve`` raises the corners, i.e. a smile.
        b = cb_ - curve * 0.085 * (u * u - 0.34)
        top.append(_p(c, hr, fwd, dwn, a, b - up * taper))
        bot.append(_p(c, hr, fwd, dwn, a, b + down * taper))
    return top + bot[::-1]


def draw_face(ink_mask, paper_mask, pose, face, *, value=255, ss=1):
    """Rasterise one expression into two L masks.

    ``ink_mask`` receives the dark features; ``paper_mask`` receives the parts
    that are the paper showing through -- the iris highlight, the teeth, the
    blush. Keeping them separate rather than as colours means the caller decides
    the compositing order without this function needing the palette.
    """
    d_ink = ink_mask
    d_paper = paper_mask
    c, hr, fwd, dwn = _basis(np.asarray(pose.head, float) * ss,
                             float(pose.head_r) * ss,
                             pose.facing,
                             getattr(pose, "head_ang", 0.0))

    turn = min(1.0, max(0.0, face.turn))

    # ---- eyes ----------------------------------------------------------
    # The near eye sits toward the front of the face. The far eye slides forward
    # and shrinks as the head turns away, and is gone by a full profile.
    eye_b = -0.12
    near_a = 0.26 + 0.06 * turn
    far_a = -0.21 + 0.19 * turn
    near_w, near_h = 0.185, 0.235
    # The far eye is smaller because it is further away, but not by much: a 0.6
    # size ratio reads as a mismatched pair of eyes rather than as depth. 0.8 is
    # enough to say "three-quarter view" and still reads as one face.
    far_scale = (1.0 - turn * 0.55) * 0.86
    far_w, far_h = 0.185 * far_scale, 0.230 * far_scale

    ap = face.eye_aperture()
    look_a = max(-1.0, min(1.0, face.pupil_a))
    look_b = max(-1.0, min(1.0, face.pupil_b))

    eyes = [(near_a, near_w, near_h, 1.0)]
    if far_w > 0.02:
        eyes.append((far_a, far_w, far_h, 0.86))

    for i, (ea, ew, eh, tint) in enumerate(eyes):
        cx, cy = _p(c, hr, fwd, dwn, ea, eye_b)

        if ap < 0.075:
            # Shut: an arc, not a bar. A straight line reads as a drawn-on eyelid.
            hw = ew * hr
            inkmod.stroke(d_ink, (cx - hw * 0.92, cy + hr * 0.026),
                          (cx + hw * 0.92, cy + hr * 0.026),
                          max(1.0, hr * 0.052 * tint), value,
                          taper_start=0.45, taper_end=0.45, bulge=0.32)
            continue

        rw = ew * hr
        rh = eh * hr * min(1.0, ap) ** 0.85

        if face.squint > 0.5:
            # The happy arch: two strokes meeting at a peak above the eye.
            # The arch is sized from the *full* eye height, not the squashed
            # aperture: a happy squint still occupies the whole eye socket, and
            # deriving it from `rh` (which eye_open shrank) made it a tiny
            # caret floating in the middle of the face.
            full = eh * hr
            lift = hr * 0.050 * (face.squint - 0.5) * 2.0
            peak = (cx, cy - full * 0.55 - lift)
            w = max(1.0, hr * 0.078 * tint)
            inkmod.stroke(d_ink, (cx - rw, cy + full * 0.22), peak, w, value,
                          taper_start=0.38, taper_end=0.58, bulge=0.16)
            inkmod.stroke(d_ink, peak, (cx + rw, cy + full * 0.22), w, value,
                          taper_start=0.58, taper_end=0.38, bulge=0.16)
            continue

        # The eye itself.
        d_ink.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=value)

        # Where it is looking: a paper disc, then a pupil inside it. The disc is
        # clamped so it can slide to the edge of the eye without leaving it.
        iris_r = min(rw, rh) * 0.52
        ia = look_a * (rw - iris_r * 0.92)
        ib = look_b * (rh - iris_r * 0.92)
        ix, iy = cx + ia, cy + ib
        d_paper.ellipse([ix - iris_r, iy - iris_r, ix + iris_r, iy + iris_r],
                        fill=value)
        pr = iris_r * 0.50
        d_ink.ellipse([ix - pr, iy - pr, ix + pr, iy + pr], fill=value)
        # Catchlight, on the light side, small enough to survive a 40 px head.
        gr = max(0.9, pr * 0.42)
        d_paper.ellipse([ix - pr * 0.15 - gr, iy - pr * 0.55 - gr,
                         ix - pr * 0.15 + gr, iy - pr * 0.55 + gr], fill=value)

    # ---- brows ---------------------------------------------------------
    # Two strokes whose inner ends move independently of their outer ends. The
    # angle is what carries the expression: inner-down is anger, inner-up is fear,
    # both-up is surprise. Everything else is a blend of those three.
    raise_ = face.brow_raise * 0.15
    ang = face.brow_angle * 0.30
    pinch = face.brow_pinch * 0.09
    if face.squint > 0.5:
        raise_ += 0.09

    for tag in ("near", "far"):
        if tag == "near":
            root_a, tip_a, w = 0.10 - pinch, 0.44 - pinch * 0.4, 1.0
            root_b = -0.355 - raise_ - ang * 0.30
        else:
            if far_w <= 0.02:
                continue
            root_a = -0.40 + 0.16 * turn - pinch * 0.5
            tip_a = -0.13 + 0.16 * turn
            w = 0.82
            root_b = -0.375 - raise_ - ang * 0.26
        tip_b = root_b + 0.045
        inkmod.stroke(d_ink,
                      _p(c, hr, fwd, dwn, root_a, root_b),
                      _p(c, hr, fwd, dwn, tip_a, tip_b),
                      max(1.0, hr * 0.086 * w), value,
                      taper_start=0.50, taper_end=0.30, bulge=0.24)

    # No nose. On a circle there is nowhere to put one: inside the silhouette it
    # reads as a stray tick, and to break the circle it would have to be a beak.
    # The style already asks the audience to read a circle as a head; a drawn nose
    # fights that contract instead of supporting it.

    # ---- mouth ---------------------------------------------------------
    mw = 0.33 * face.mouth_width
    ma = 0.12 + face.mouth_shift * 0.14 + face.jaw * 0.02
    mb = 0.33 + face.jaw * 0.15

    if face.mouth_open > 0.055:
        half = face.mouth_open
        up = half * 0.26
        down = half * 0.30
        poly = _lens(c, hr, fwd, dwn, ma, mb, mw, up, down, face.mouth_curve)
        d_ink.polygon([tuple(q) for q in poly], fill=value)
        if face.teeth > 0.05:
            # A band of paper across the top of the opening. It reads as teeth at
            # any size, and at small sizes it just reads as an open mouth lit
            # from inside, which is also correct.
            band_up = up * 0.30 * face.teeth
            band_down = up * 0.85 * face.teeth
            tpoly = _lens(c, hr, fwd, dwn, ma, mb - up * 0.35,
                          mw * 0.80, band_up, band_down, face.mouth_curve)
            d_paper.polygon([tuple(q) for q in tpoly], fill=value)
    else:
        # A closed mouth is a single stroke with a curve. Three points is enough
        # to make a smile read; more and the taper stops working.
        lift = face.mouth_curve * 0.11
        w = max(1.0, hr * 0.075 * (0.78 + 0.30 * face.mouth_width))
        a0 = _p(c, hr, fwd, dwn, ma - mw, mb - lift * 0.50)
        a1 = _p(c, hr, fwd, dwn, ma, mb + lift * 0.62)
        a2 = _p(c, hr, fwd, dwn, ma + mw, mb - lift * 0.50)
        inkmod.stroke(d_ink, a0, a1, w, value, taper_start=0.32, taper_end=0.88,
                      bulge=0.18)
        inkmod.stroke(d_ink, a1, a2, w, value, taper_start=0.88, taper_end=0.32,
                      bulge=0.18)

    # ---- sweat ---------------------------------------------------------
    if face.sweat > 0.04:
        s = face.sweat
        # At the temple, on the silhouette, falling. Two drops because one reads
        # as a blemish and two read as sweat.
        for k, (sa, sb, sz) in enumerate(((0.72, -0.34, 1.0), (0.50, -0.62, 0.62))):
            if k == 1 and s < 0.45:
                continue
            p = _p(c, hr, fwd, dwn, sa, sb + 0.13 * s)
            r = hr * 0.062 * sz * (0.60 + 0.40 * s)
            tip = p + dwn * (-r * 1.35) + fwd * (-r * 0.25)
            pts = [tuple(tip)]
            for j in range(9):
                t = math.pi * (0.10 + 0.80 * j / 8.0)
                pts.append((p[0] + math.cos(t) * r, p[1] + math.sin(t) * r))
            d_ink.polygon(pts, fill=value)

    # ---- blush ---------------------------------------------------------
    if face.blush > 0.05:
        # Mid value, not full: the mask is an alpha channel, so 88 is a tint
        # rather than a mark. The only place a feature is not opaque.
        v = int(88 * min(1.0, face.blush))
        for ba in (0.46, -0.26):
            p = _p(c, hr, fwd, dwn, ba, 0.15)
            rw = hr * 0.16
            rh = hr * 0.085
            d_ink.ellipse([p[0] - rw, p[1] - rh, p[0] + rw, p[1] + rh], fill=v)
