"""Assert the properties that make the motion physical.

Smoothness is easy to fake; these are the things that are hard to fake and easy
to get wrong, so they are checked rather than eyeballed:

1. A stance foot does not move in world space.
2. A stance foot does not go below the floor, and a swing foot does clear it.
3. No grounded pose floats, and every airborne frame is clear of the floor.
4. The jump apex matches the physics that produced the flight time.
5. No limb is over-extended past its bone lengths.
6. Nobody stands in the hole. Both take-off and landing feet are on solid ground,
   and the arc genuinely clears the lip rather than clipping through the void.

Run:  python -m showreel.stickman.verify
"""

from __future__ import annotations

import math
import sys

import numpy as np

from .film import (EDGE_X, FPS, GAP, GAP_LEFT, GAP_RIGHT, LAND_X, Performer,
                   build_shots)
from .rig import P
from .motion import Gait, GRAVITY

FAILS = []


def check(name, ok, detail=""):
    print(f"  [{'ok  ' if ok else 'FAIL'}] {name}{(('  ' + detail) if detail else '')}")
    if not ok:
        FAILS.append(name)


def foot_is_static():
    print("\n1. stance foot does not slide")
    g = Performer().walk
    worst = 0.0
    for i in range(200):
        phase = i / 200.0 * 4.0
        pelvis_x = g.D * phase
        for side in (0.0, 0.5):
            p = (phase + side) % 1.0
            if p > g.B:
                continue
            here, _ = g.foot(phase, pelvis_x, 0.0, side=side)
            # During stance the foot sits at pelvis + A*(1 - 2u); the test is
            # that this equals where it touched down, pelvis_touch + A.
            u = p / g.B
            expected = (pelvis_x - g.D * u * g.B) + g.A
            worst = max(worst, abs(here[0] - expected))
    check("stance foot is world-static", worst < 1e-6, f"max error {worst:.2e} px")


def feet_and_floor():
    print("\n2. feet meet the floor correctly")
    g = Performer().walk
    lowest = 0.0
    lift = 0.0
    for i in range(400):
        phase = i / 400.0
        for side in (0.0, 0.5):
            (x, y), _ = g.foot(phase, g.D * phase, 0.0, side=side)
            lowest = max(lowest, y)          # y grows downward
            lift = max(lift, -y)
    check("no foot below the floor", lowest < 1e-6, f"deepest {lowest:.4f} px")
    check("the swing foot clears the floor", lift > 0.01,
          f"max lift {lift:.1f} px = {lift / g.height * 100:.1f}% of height")


def figure_on_floor():
    print("\n3. the figure meets the floor when grounded")
    perf = Performer()
    shots, _jump = build_shots(perf)
    grounded, airborne = [], []
    for shot in shots:
        n = max(2, int(shot.duration * FPS))
        for k in range(n):
            pose, _cam = shot(shot.duration * k / (n - 1), perf)
            if shot.name == "jump":
                continue
            grounded.append(max(pose.toe_near[1], pose.toe_far[1]))
    worst = max(grounded) if grounded else 0.0
    check("no grounded pose floats", worst < 1.5, f"highest contact y {worst:.2f}")

    # Airborne clearance: on the jump shot, every frame between take-off and
    # touchdown must have both feet above the floor.
    jump = shots[2].fn.__self__
    for k in range(int(shots[2].duration * FPS)):
        t = shots[2].duration * k / max(int(shots[2].duration * FPS) - 1, 1)
        if jump.phase(t) != "air":
            continue
        pose, _cam = shots[2](t, perf)
        airborne.append(max(pose.toe_near[1], pose.toe_far[1]))
    if airborne:
        check("every airborne frame is clear of the floor", min(airborne) < -4.0,
              f"closest approach {min(airborne):.1f} px")


def jump_physics():
    print("\n4. the jump agrees with gravity")
    perf = Performer()
    shots, _j = build_shots(perf)
    jump = shots[2].fn.__self__

    # Apex, measured from the arc rather than read off the parameters.
    peak = 0.0
    n = int(shots[2].duration * FPS)
    for k in range(n):
        t = shots[2].duration * k / max(n - 1, 1)
        if jump.phase(t) != "air":
            continue
        u = (t - jump.take) / jump.flight
        peak = max(peak, 4.0 * jump.apex_px * u * (1.0 - u))
    rel = abs(peak - jump.apex_px) / max(jump.apex_px, 1.0)
    check("measured apex matches the ballistic prediction", rel < 0.02,
          f"{peak:.1f} vs {jump.apex_px:.1f}")

    implied = 2.0 * math.sqrt(2.0 * jump.apex_px / GRAVITY)
    check("flight time is the one gravity allows", abs(implied - jump.flight) < 1e-3,
          f"{jump.flight:.4f} s")

    # The horizontal speed has to be exactly gap/flight, or the figure lands in
    # the hole or overshoots the lip.
    want = (LAND_X - EDGE_X) / jump.flight
    check("horizontal speed carries exactly the gap", abs(jump.speed - want) < 1e-6,
          f"{jump.speed:.2f} px/s")


def limbs_not_overextended():
    print("\n5. no limb is stretched past its bones")
    perf = Performer()
    shots, _j = build_shots(perf)
    h = perf.height
    worst = {}
    for shot in shots:
        n = max(2, int(shot.duration * FPS))
        for k in range(n):
            pose, _cam = shot(shot.duration * k / (n - 1), perf)
            pairs = [
                ("leg_near", pose.hip_near, pose.ankle_near,
                 (P["thigh"] + P["shin"]) * h),
                ("leg_far", pose.hip_far, pose.ankle_far,
                 (P["thigh"] + P["shin"]) * h),
                ("arm_near", pose.shoulder_near, pose.wrist_near,
                 (P["upper_arm"] + P["forearm"]) * h),
                ("arm_far", pose.shoulder_far, pose.wrist_far,
                 (P["upper_arm"] + P["forearm"]) * h),
            ]
            for name, a, b, limit in pairs:
                d = float(np.hypot(*(np.asarray(b) - np.asarray(a))))
                worst[name] = max(worst.get(name, 0.0), d / limit)
    for name, ratio in sorted(worst.items()):
        check(f"{name} within bone length", ratio <= 1.0005, f"max {ratio * 100:.1f}%")


def gaps_respected():
    print("\n6. nobody stands in the hole")
    perf = Performer()
    shots, _j = build_shots(perf)
    h = perf.height
    bad = []
    for shot in shots:
        n = max(2, int(shot.duration * FPS))
        for k in range(n):
            t = shot.duration * k / (n - 1)
            pose, _cam = shot(t, perf)
            for tag in ("toe_near", "toe_far", "ankle_near", "ankle_far"):
                x, y = getattr(pose, tag)
                # A foot may only be over a gap if it is airborne, i.e. clearly
                # above the floor plane.
                if GAP_LEFT <= x <= GAP_RIGHT and y > -h * 0.06:
                    bad.append((shot.name, round(t, 2), tag, round(float(x), 1),
                                round(float(y), 1)))
    check("no foot stands over the void", not bad,
          f"{len(bad)} poses in the hole" + (f", first {bad[0]}" if bad else ""))

    # And the take-off / landing points are on solid ground with margin.
    check("take-off foot is on the lip", GAP_LEFT - EDGE_X > h * 0.10,
          f"{GAP_LEFT - EDGE_X:.0f} px of ground behind it")
    check("landing foot is past the far lip", LAND_X - GAP_RIGHT > h * 0.10,
          f"{LAND_X - GAP_RIGHT:.0f} px of ground beyond it")

    # The arc must clear the near lip: at the moment the figure crosses the
    # near edge, its lowest foot has to be above the floor.
    jump = shots[2].fn.__self__
    best = None
    n = int(shots[2].duration * FPS)
    for k in range(n):
        t = shots[2].duration * k / max(n - 1, 1)
        if jump.phase(t) != "air":
            continue
        pose, _cam = shots[2](t, perf)
        for tag in ("toe_near", "toe_far"):
            x, y = getattr(pose, tag)
            if GAP_LEFT <= x <= GAP_RIGHT:
                best = y if best is None else max(best, y)
    if best is not None:
        check("the arc clears the lip", best < -h * 0.05,
              f"closest foot over the void: {best:.0f} px")


def main():
    print("stickman verification")
    foot_is_static()
    feet_and_floor()
    figure_on_floor()
    jump_physics()
    limbs_not_overextended()
    gaps_respected()
    print()
    if FAILS:
        print(f"{len(FAILS)} check(s) failed: {', '.join(FAILS)}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
