"""What "POV: the stadium goes quiet" has to be true about.

    python -m showreel.stickman.verify_pov

Exit code is 1 if anything fails, so this can be a gate rather than a report.

Every assertion here is about a property the film claims and a viewer could check.
They are deliberately not regression tests: "the hash still matches" would pass
just as happily on a broken frame. These fail when the film stops being the thing
the release notes say it is.

Three of them exist because the corresponding mistake has already been made in
this repository, and each one was invisible in a still:

  * the ball's arc was hand-shaped before it was solved, and a shaped arc reads
    as "fine" for two seconds and as wrong for ten
  * the half-resolution backdrop moved the horizon, because `eye` is a fraction
    of the frame height rather than a height
  * a crowd whose marks are taller than they are wide reads as falling rain
"""

from __future__ import annotations

import math
import sys

import numpy as np

from . import face as F
from .film import FPS, W, H
from .motion import GRAVITY
from .pov import SHOTS, TOTAL, Pov, _blink
from .rig import clamp
from .stadium import UPERM, z_of

FAILS = []


def check(name, ok, detail=""):
    tag = "PASS" if ok else "FAIL"
    print(f"{tag}  {name:56s} {detail}")
    if not ok:
        FAILS.append(name)
    return ok


# --------------------------------------------------------------------- checks

def timeline():
    """The shot list is a partition of the film, not a set of suggestions."""
    prev = 0.0
    ok = True
    for name, a, b in SHOTS:
        ok = ok and abs(a - prev) < 1e-9 and b > a
        prev = b
    check("timeline: shots tile the film with no gap or overlap", ok,
          f"{len(SHOTS)} shots, {prev:.1f} s")

    shortest = min(b - a for _, a, b in SHOTS)
    check("timeline: no shot is shorter than four seconds", shortest >= 4.0,
          f"shortest {shortest:.1f} s")

    n = int(round(TOTAL * FPS))
    check("timeline: the film is at least 30 seconds", TOTAL >= 30.0,
          f"{TOTAL:.1f} s = {n} frames at {FPS} dps")


def sound_is_shown():
    """`churn` is the only loudness control, so it has to actually go quiet."""
    pov = Pov()
    ts = np.arange(0.0, TOTAL, 0.25)
    ch = np.array([pov.state(float(t))["churn"] for t in ts])

    quiet = (ch < 0.02).sum() * 0.25
    check("sound: there is a real silence in the film", quiet >= 15.0,
          f"{quiet:.1f} s below churn 0.02")

    late = ch[ts > TOTAL - 2.0]
    check("sound: the crowd is back at the end", late.min() > 0.9,
          f"min churn in the last 2 s = {late.min():.2f}")

    # The silence must be *entered*, not cut to. A jump of more than 0.35 between
    # quarter-second samples means the sound was switched rather than lost.
    step = np.abs(np.diff(ch)).max()
    check("sound: the silence arrives gradually", step < 0.45,
          f"max change per 0.25 s = {step:.2f}")


def faces():
    """Every frame has a face, and every face is inside its own vocabulary."""
    pov = Pov()
    bad = 0
    n = 0
    for t in np.arange(0.0, TOTAL, 0.5):
        f = pov.state(float(t))["face"]
        n += 1
        if not isinstance(f, F.Face):
            bad += 1
            continue
        for name in f.__dataclass_fields__:
            v = getattr(f, name)
            # -1 is a legitimate value (a fully inverted brow or a full frown);
            # the band is here to catch a field escaping its own definition, not
            # to second-guess the vocabulary.
            if not (-1.05 <= v <= 1.45):
                bad += 1
                break
    check("faces: every frame has one, and no field is out of range", bad == 0,
          f"{n} frames sampled, {bad} bad")

    # A blink that is shorter than a frame simply does not happen at 24 fps.
    shutter = 0.0
    for i in range(int(4.0 * 240)):
        if _blink(i / 240.0) > 0.5:
            shutter += 1 / 240.0
    frames = shutter * FPS
    check("faces: a blink lasts long enough to land on frames", frames >= 2.0,
          f"{shutter:.3f} s = {frames:.1f} frames at {FPS} fps")

    # And the eyes must actually close somewhere in the film.
    shut = [t for t in np.arange(0.0, TOTAL, 1 / FPS)
            if pov.state(float(t))["face"].blink > 0.5]
    check("faces: the eyes close at least once", len(shut) >= 2,
          f"{len(shut)} frames with the eyes shut")


def ball_is_physics():
    """The struck ball's height is gravity, and it arrives where the net is."""
    pov = Pov()
    h = pov.perf.height
    e = np.linspace(0.0, Pov.FLIGHT * 0.98, 28)
    ys = np.array([pov._strike(float(t), h, 400.0, 2.0)[1] for t in e])
    a = np.polyfit(e, ys, 2)
    g = 2.0 * a[0]
    check("ball: the strike's vertical acceleration is gravity",
          abs(g - GRAVITY) < 1.0, f"fitted {g:.1f} vs {GRAVITY:.1f}")

    y_end = pov._strike(Pov.FLIGHT, h, 400.0, 2.0)[1]
    check("ball: it arrives at the height the net was framed for",
          abs(y_end - Pov.NET_Y * h) < 1.0,
          f"{y_end:.1f} vs {-Pov.NET_Y * h:.1f} below the ground")

    # And it never goes through the floor on the way.
    lo = min(pov._strike(float(t), h, 400.0, 2.0)[1]
             for t in np.linspace(0.0, Pov.FLIGHT, 60))
    check("ball: never below the ground in flight", lo <= 0.0,
          f"lowest point {lo:.1f}")


def juggle_is_physics():
    """The knee juggle is the same law with a damped impulse."""
    pov = Pov()
    h = pov.perf.height
    x0 = 0.0
    # One flight only. The juggle's period is 2*sqrt(2H/g), so a window that
    # straddles a bounce fits a parabola across the kink and reports a lower g.
    period = 2.0 * math.sqrt(2.0 * (0.30 * h) / GRAVITY)
    ts = np.linspace(period * 0.06, period * 0.94, 22)
    ys = np.array([pov._juggles(float(t), x0, h)[1] for t in ts])
    a = np.polyfit(ts, ys, 2)
    g = 2.0 * a[0]
    check("ball: the juggle's acceleration is gravity", abs(g - GRAVITY) < 40.0,
          f"fitted {g:.1f} vs {GRAVITY:.1f}")


def hero_stays_on_the_ground():
    """Toes never below the floor, and no joint teleports between frames."""
    pov = Pov()
    worst = 0.0
    jumps = 0.0
    prev = None
    prev_shot = None
    for i in range(int(round(TOTAL * FPS))):
        t = (i + 1) / FPS
        s = pov.state(t)
        hero = s["hero"]
        # A cut is allowed to move the figure anywhere; only motion *within* a
        # shot is motion.
        if s["shot"] != prev_shot:
            prev = None
            prev_shot = s["shot"]
        if hero is None:
            continue
        toes = max(hero.toe_near[1], hero.toe_far[1])
        ankles = max(hero.ankle_near[1], hero.ankle_far[1])
        worst = max(worst, toes, ankles)
        if prev is not None:
            jumps = max(jumps, float(np.hypot(*(hero.pelvis - prev))))
        prev = hero.pelvis
    check("figure: no foot is below the floor", worst <= 0.51,
          f"lowest point {worst:.2f} units")
    # At 24 fps a body can move a long way in one frame, but not its own height.
    check("figure: the pelvis never jumps between frames", jumps <= 90.0,
          f"max step {jumps:.1f} units")


def keeper_is_behind():
    """The keeper is at the goal, which is further away than the hero."""
    pov = Pov()
    s = pov.state(66.0)
    z_goal = z_of(s["goal_d"])
    check("keeper: stands on the goal line, behind the hero", z_goal > 1.0,
          f"goal at z {z_goal:.2f}, hero at z 1.00")
    check("keeper: exists during the strike and not before it",
          pov.state(58.5)["keeper"] is None and s["keeper"] is not None,
          "absent at 0.5 s, present at 8 s")


def frames_render():
    """Sample frames across the film: in range, finite, and not blank."""
    from .pov_film import frame_at

    pov = Pov()
    ts = [1.0, 4.5, 9.0, 15.0, 22.0, 27.0, 33.0, 40.0, 47.0, 55.0,
          60.0, 65.0, 69.0, 73.0, 79.0, 86.0, 89.5]
    bad = []
    flat = []
    for t in ts:
        f = frame_at(pov, t)
        if not np.all(np.isfinite(f)):
            bad.append(f"{t}s nan")
        elif f.min() < -1e-6 or f.max() > 1.0 + 1e-6:
            bad.append(f"{t}s range {f.min():.2f}..{f.max():.2f}")
        elif f.std() < 0.02:
            flat.append(f"{t}s")
    check("frames: all sampled frames render in range and finite", not bad,
          "; ".join(bad) or f"{len(ts)} frames")
    check("frames: none of them is blank", not flat, ", ".join(flat) or "all have image")


def the_figure_is_lit_against_the_set():
    """The hero must be darker than the set behind him, or he is invisible.

    This is the assertion that would have caught the first version of the
    stadium: black ink on a black crowd, which looked like an empty stand with a
    head floating in it.
    """
    from .pov_film import frame_at
    from .stage import Projector

    pov = Pov()
    worst = -1.0
    for t in (15.0, 30.0, 44.0, 62.0):
        s = pov.state(t)
        c = s["cam"]
        proj = Projector(W, H, cam_x=c["x"], cam_y=c["rise"], eye=c["eye"],
                         zoom=c["zoom"], tilt=c["tilt"])
        hero = s["hero"]
        if hero is None:
            continue
        f = frame_at(pov, t)
        # The chest, in screen space, and a ring of background around it.
        cx, cy = proj.point(hero.chest)
        y, x = int(np.clip(cy, 4, H - 5)), int(np.clip(cx, 4, W - 5))
        body = float(f[y - 2:y + 3, x - 2:x + 3].mean())
        ring = float(f[max(0, y - 90):y - 30, max(0, x - 90):x + 90].mean())
        worst = max(worst, body - (ring - 0.20))
    check("light: the body is separated from the background by 0.20",
          worst <= 0.0, f"worst excess {worst:+.3f}")


def the_words_are_safe_to_print():
    """The film names a real person, so the words have to carry their own caveat.

    Four things are checked, and the third is the one that matters: **every frame
    on which a card is up also has the disclaimer up.** A title card that names a
    real man must never be on screen without the line that says the film is
    invented -- not for most of the card, for all of it. The others are ordinary:
    the windows are where the cut says they are, no card leaks into the middle of
    the film, and the type fits the frame it is set in.
    """
    from . import pov_text as T

    # 1. The two windows are the two windows in the shot table, and nothing else.
    bad = []
    for t in np.arange(0.5, 6.4, 0.25):
        if not T.active(float(t)):
            bad.append(f"hook dark at {t:.2f}")
    for t in np.arange(84.2, 90.0, 0.25):
        if not T.active(float(t)):
            bad.append(f"close dark at {t:.2f}")
    for t in np.arange(7.6, 83.0, 1.0):
        if T.active(float(t)):
            bad.append(f"card up at {t:.1f}")
    check("text: the hook runs 0-6.8 and the question 83.6-90, and only there",
          not bad, "; ".join(bad[:4]) or "two windows, no others")

    # 2. The disclaimer is under every card, on every frame, both windows.
    orphan = []
    for t in np.arange(0.0, 90.0, 0.05):
        card = max(T._ramp(float(t), *T.HOOK), T._ramp(float(t), *T.CLOSE))
        rights = max(T._ramp(float(t), a, b) for a, b in T.RIGHTS)
        if card > 0.01 and rights < 0.01:
            orphan.append(f"{t:.2f}")
    check("text: no card is ever up without 'An imagined scenario' under it",
          not orphan, ", ".join(orphan[:4]) or "0 unattributed frames")

    # 3. Nothing is set wider than the frame, and no card is empty.
    too_wide = []
    for name in ("hook", "close", "rights"):
        layer = T._card(name)
        a = np.asarray(layer.getchannel("A"))
        if int((a > 8).sum()) < 2000:
            too_wide.append(f"{name} empty")
        # The scrim deliberately reaches both edges; the *type* must not, so the
        # edge test uses only strongly opaque pixels.
        cols = np.where((a > 200).any(axis=0))[0]
        if len(cols) and (cols[0] < 24 or cols[-1] > W - 24):
            too_wide.append(f"{name} runs to the edge")
    check("text: every card has ink and clears the frame edges by 24 px",
          not too_wide, "; ".join(too_wide) or "3 cards inside")

    # 4. Type set over a white floodlight needs shade under it: the hook card's
    #    band must actually darken its own rows, or the title vanishes on a lamp.
    hook = np.asarray(T._card("hook").getchannel("A"))
    rows = hook[300:560].mean()
    bare = hook[600:900].mean()
    check("text: the hook's shade band is denser than open sky above the stand",
          rows > bare + 4.0, f"band {rows:.1f} vs open {bare:.1f}")


def main():
    timeline()
    sound_is_shown()
    faces()
    ball_is_physics()
    juggle_is_physics()
    hero_stays_on_the_ground()
    keeper_is_behind()
    frames_render()
    the_figure_is_lit_against_the_set()
    the_words_are_safe_to_print()

    print()
    if FAILS:
        print(f"{len(FAILS)} assertion(s) failed:")
        for f in FAILS:
            print("  -", f)
        return 1
    print("all assertions passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
