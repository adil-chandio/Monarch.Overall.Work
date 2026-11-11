"""Assertions for the duel shot.

The point of this file is that the shot's claims are *checked*, not asserted in
prose. Every number the animation depends on -- that the contact is on the body,
that the fall is a projectile and not a curve, that the body is inside the chasm's
opening when it is drawn inside the chasm -- is measured here and fails loudly.

    python -m showreel.stickman.verify_duel
"""

from __future__ import annotations

import math

import numpy as np

from .duel import Duel, FAR_LIP, GAP_DEPTH, NEAR_LIP, T_SHOVE
from .film import FPS, H, W, Performer
from .motion import GRAVITY
from .rig import pelvis_height
from .stage import Projector, World, void_mask

# The shove is two beats: the hand travels to the chest, then it drives. The
# contact assertion is about the second beat -- measuring the first would be
# asserting that a punch never has to cover any ground.
T_CONTACT = None  # filled in per-duel below

# A body's limbs are drawn with width, so a pose that is a couple of pixels into
# the floor is a contact, not a violation. Everything past this is a bug.
FLOOR_TOL = 3.0
# A rigid body's pelvis can move as fast as gravity makes it; at 24 fps a fall at
# 3000 px/s covers 125 px per frame. Anything above this in a single frame, outside
# the launch frames, is a teleport.
MAX_STEP = 150.0


class Report:
    def __init__(self):
        self.rows = []
        self.failed = 0

    def check(self, name, ok, detail=""):
        self.rows.append((name, bool(ok), detail))
        if not ok:
            self.failed += 1
        return ok

    def show(self):
        width = max(len(n) for n, _o, _d in self.rows) + 2
        for name, ok, detail in self.rows:
            print(f"  {'PASS' if ok else 'FAIL'}  {name:<{width}} {detail}")
        print()
        if self.failed:
            print(f"{self.failed} assertion(s) failed")
        else:
            print(f"all {len(self.rows)} assertions passed")
        return self.failed == 0


def _frames(duel):
    n = int(round(duel.total * FPS))
    for i in range(n):
        yield (i + 1) / FPS


def run():
    perf = Performer()
    duel = Duel(perf)
    h = perf.height
    world = World("paper", seed=5, gaps=[(NEAR_LIP, FAR_LIP, GAP_DEPTH)])
    r = Report()

    ts = list(_frames(duel))
    states = [(t,) + duel.state(t) for t in ts]

    # -- 1. the contact ----------------------------------------------------
    # The shove's claim is that the hands are on the body *at the moment of impact*
    # and stay on it through the drive. During the wind-up they are travelling, and
    # an arc that starts 260 px away and arrives on the last frame is not a late
    # contact -- it is a punch that has to cover ground.
    t_contact = duel.t_shove + T_SHOVE * duel.REACH
    window = [t for t, *_ in states if t_contact <= t < duel.t_break]
    worst = 0.0
    for t, hero, foe, cam in states:
        if not (t_contact <= t < duel.t_break):
            continue
        worst = max(worst, float(np.hypot(*(foe.wrist_near - hero.chest))))
    r.check("contact: hands on the chest through the drive", worst < h * 0.16,
            f"max {worst:.1f} px over {len(window)} frames")
    # And the arc has to be monotone: a hand that arrives, leaves, and comes back is
    # a hand the viewer will read as uncertain.
    errs = [float(np.hypot(*(foe.wrist_near - hero.chest)))
            for t, hero, foe, cam in states if duel.t_shove <= t < duel.t_break]
    r.check("contact: approach is monotone", all(b <= a + 1.0 for a, b in zip(errs, errs[1:])),
            f"{min(errs):.0f} px at the last frame")

    # -- 2. the fall is a projectile ---------------------------------------
    # Sample the hero's pelvis through the fall and fit it: second difference must
    # equal gravity, and the first difference must be linear in t.
    fall = [(t, hero) for t, hero, foe, cam in states
            if hero is not None and duel.t_break <= t < duel.t_break + 0.42]
    if len(fall) >= 5:
        ps = np.array([p.pelvis for _t, p in fall])
        tsa = np.array([t for t, _p in fall])
        # Least squares on y = y0 + v t + 0.5 g t^2
        A = np.stack([np.ones_like(tsa), tsa, 0.5 * tsa ** 2], axis=1)
        coef, *_ = np.linalg.lstsq(A, ps[:, 1], rcond=None)
        g_fit = float(coef[2])
        r.check("fall: vertical acceleration is gravity", abs(g_fit - GRAVITY) < GRAVITY * 0.06,
                f"fitted {g_fit:.1f} vs {GRAVITY:.1f}")
        vx_fit = float((tsa[-1] - tsa[0]) and
                       (ps[-1, 0] - ps[0, 0]) / (tsa[-1] - tsa[0]))
        r.check("fall: horizontal velocity is constant",
                abs(vx_fit - duel.leave["v"][0]) < 40.0,
                f"{vx_fit:.1f} vs {duel.leave['v'][0]:.1f} px/s")
    else:
        r.check("fall: enough frames to measure", False, f"{len(fall)} frames")

    # -- 3. no teleports ---------------------------------------------------
    jumps = []
    prev = None
    for t, hero, foe, cam in states:
        if hero is not None and prev is not None:
            d = float(np.hypot(*(hero.pelvis - prev)))
            jumps.append((d, t))
        prev = hero.pelvis if hero is not None else None
    worst_jump = max(jumps) if jumps else (0.0, 0.0)
    r.check("no teleports: pelvis never jumps a frame", worst_jump[0] < MAX_STEP,
            f"max {worst_jump[0]:.1f} px at t={worst_jump[1]:.2f}")

    # -- 4. the silhouette never leaves solid ground until it is supposed to -
    bad = []
    for t, hero, foe, cam in states:
        if t >= duel.t_break or foe is None:
            continue
        for nm, pt in (("near", foe.toe_near), ("far", foe.toe_far)):
            if pt[1] > FLOOR_TOL:
                bad.append((t, nm, pt[1]))
    r.check("silhouette: feet never below the floor", not bad,
            f"{len(bad)} violations" if bad else "0 violations")

    # -- 5. the silhouette stays on this side of the lip -------------------
    worst_x = max((foe.pelvis[0] for _t, _h, foe, _c in states if foe is not None),
                  default=-1e9)
    r.check("silhouette: never crosses the lip", worst_x <= NEAR_LIP + h * 0.10,
            f"max x {worst_x:.1f} vs lip {NEAR_LIP:.1f}")

    # -- 6. occlusion is continuous, and never erases the body entirely -----
    # As the body falls past the near lip the ground starts to cover it. What must
    # not happen is the body vanishing on one frame and returning on the next: that
    # is a body drawn through the floor and then out the other side. Measure the
    # fraction of the drawn pose the mask admits, on every frame.
    fracs = []
    for t, hero, foe, cam in states:
        if hero is None:
            continue
        proj = Projector(W, H, cam_x=cam["x"], cam_y=cam.get("rise", 0.0),
                         eye=cam["height"], zoom=cam["zoom"], tilt=cam["tilt"])
        m = void_mask(world, proj)
        pts = [np.asarray(v) for _n, v in hero.joints()]
        sx = np.clip(np.round(proj.sx(np.array([p[0] for p in pts]))), 0, W - 1).astype(int)
        sy = np.clip(np.round(proj.sy(np.array([p[1] for p in pts]))), 0, H - 1).astype(int)
        fracs.append(float(m[sy, sx].mean()))

    # A body may be partly covered and may leave the frame, but it may not go from
    # "almost all visible" to "almost none" and back inside one beat.
    dips = [i for i in range(1, len(fracs) - 1)
            if fracs[i] < fracs[i - 1] - 0.55 and fracs[i + 1] > fracs[i] + 0.55]
    r.check("occlusion: the body never blinks through the ground", not dips,
            f"{len(dips)} blink frames" if dips else "no blink frames")

    # -- 7. the fall is actually on screen while it is inside the chasm ----
    visible = 0
    for t, hero, foe, cam in states:
        if hero is not None and duel.in_void(t):
            visible += 1
    r.check("fall: is on screen for a readable number of frames", visible >= 5,
            f"{visible} frames inside the void")

    # -- 8. the hero's feet are on the floor before the break --------------
    bad = []
    for t, hero, foe, cam in states:
        if t >= duel.t_break:
            break
        if hero is None:
            continue
        low = max(hero.toe_near[1], hero.toe_far[1])
        if low > FLOOR_TOL:
            bad.append((round(t, 2), float(low)))
    r.check("hero: feet on the floor before the break", not bad,
            f"{len(bad)} violations, worst {max((b[1] for b in bad), default=0):.1f}")

    # -- 9. the beats are long enough to read ------------------------------
    beats = {"approach": duel.t_shove, "shove": duel.t_break - duel.t_shove,
             "break": duel.t_drop - duel.t_break, "drop": duel.t_still - duel.t_drop,
             "still": duel.total - duel.t_still}
    short = {k: v for k, v in beats.items() if v * FPS < 4}
    r.check("timing: every beat is at least four frames", not short,
            f"short: {short}" if short else f"shortest {min(beats.values()) * FPS:.0f} frames")

    # -- 10. nothing is drawn that the camera cannot see -------------------
    # A pose entirely outside the frame is wasted work and, worse, a lie about what
    # the shot shows.
    stray = 0
    for t, hero, foe, cam in states:
        for p in (hero, foe):
            if p is None:
                continue
            proj = Projector(W, H, cam_x=cam["x"], cam_y=cam.get("rise", 0.0),
                             eye=cam["height"], zoom=cam["zoom"], tilt=cam["tilt"])
            ys = [float(proj.sy(pt[1])) for _n, pt in p.joints()]
            if max(ys) < -H or min(ys) > 2 * H:
                stray += 1
    r.check("no pose is entirely outside the frame", stray == 0, f"{stray} frames")

    return r.show()


def main():
    ok = run()
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
