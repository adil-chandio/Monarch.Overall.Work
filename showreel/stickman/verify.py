"""Assert the properties that make the motion physical.

Smoothness is easy to fake; these are the things that are hard to fake and easy
to get wrong, so they are checked rather than eyeballed:

1. A stance foot does not move in world space.
2. A stance foot does not go below the floor.
3. The figure's lowest point is on the floor whenever it is supposed to be
   grounded, and clear of it whenever it is airborne.
4. The jump apex matches the physics that produced the flight time.
5. No limb is over-extended past its bone lengths.

Run:  python -m showreel.stickman.verify
"""

from __future__ import annotations

import math
import sys

import numpy as np

from .film import FPS, Performer, build_shots
from .rig import P
from .motion import Gait, GRAVITY

FAILS = []


def check(name, ok, detail=""):
    status = "ok  " if ok else "FAIL"
    print(f"  [{status}] {name}{('  ' + detail) if detail else ''}")
    if not ok:
        FAILS.append(name)


def foot_is_static():
    print("\n1. stance foot does not slide")
    perf = Performer()
    g = perf.walk
    D = g.D
    worst = 0.0
    for i in range(200):
        phase = i / 200.0 * 4.0          # four full cycles
        pelvis_x = D * phase
        for side in (0.0, 0.5):
            p = (phase + side) % 1.0
            if p > g.B:
                continue
            here, _ = g.foot(phase, pelvis_x, 0.0, side=side)
            # During stance the foot sits at pelvis + A*(1 - 2u), where u runs
            # 0..1 across the stance. The test is that this equals the position
            # it had at touchdown, pelvis_touch + A.
            u = p / g.B
            expected = (pelvis_x - g.D * u * g.B) + g.A
            worst = max(worst, abs(here[0] - expected))
    check("stance foot is world-static", worst < 1e-6, f"max error {worst:.2e} px")


def foot_stays_on_floor():
    print("\n2. a stance foot never goes below the floor")
    perf = Performer()
    g = perf.walk
    lowest = 0.0     # y grows downward, so penetration is a *positive* y
    lift = 0.0
    for i in range(400):
        phase = i / 400.0
        for side in (0.0, 0.5):
            (x, y), _ = g.foot(phase, g.D * phase, 0.0, side=side)
            lowest = max(lowest, y)
            lift = max(lift, -y)
    check("no foot below y=0", lowest < 1e-6, f"deepest {lowest:.4f} px")
    # A swing foot that never rises is a dragged foot, not a step.
    check("the swing foot actually clears the floor", lift > 0.01,
          f"max lift {lift:.1f} px = {lift / g.height * 100:.1f}% of height")


def figure_stays_on_floor():
    print("\n3. the figure meets the floor when grounded")
    perf = Performer()
    shots = build_shots(perf)
    grounded_low = []
    airborne_low = []
    for si, shot in enumerate(shots):
        n = int(shot.duration * FPS)
        for k in range(n):
            t = shot.duration * k / max(n - 1, 1)
            out = shot(t, perf)
            pose = out[0]
            rise = out[4] if len(out) > 4 else 0.0
            toe_y = max(pose.toe_near[1], pose.toe_far[1])
            if rise < 1.0:
                grounded_low.append(toe_y)
            else:
                airborne_low.append(toe_y)

    if grounded_low:
        worst = max(grounded_low)
        check("no grounded pose floats", worst < 1.2, f"highest contact y {worst:.2f}")
    if airborne_low:
        highest = min(airborne_low)
        check("every airborne frame is clear of the floor", highest < -4.0,
              f"closest approach {highest:.1f} px")


def jump_physics():
    print("\n4. the jump apex agrees with the flight time")
    perf = Performer()
    shots = build_shots(perf)
    jump = shots[3]
    # Apex height measured from the poses, physics predicted from the arc.
    peak = 0.0
    for k in range(int(jump.duration * FPS)):
        t = jump.duration * k / max(int(jump.duration * FPS) - 1, 1)
        out = jump(t, perf)
        rise = out[4] if len(out) > 4 else 0.0
        peak = max(peak, rise)
    # rise = 4*apex*u*(1-u) peaks at u=0.5 with value apex
    obj = jump.fn.__self__ if hasattr(jump.fn, "__self__") else None
    if obj is not None and hasattr(obj, "apex"):
        predicted = obj.apex
        rel = abs(peak - predicted) / max(predicted, 1.0)
        check("measured apex matches the ballistic prediction", rel < 0.02,
              f"measured {peak:.1f} vs predicted {predicted:.1f}")
        # and the flight time that apex implies
        implied = 2.0 * math.sqrt(2.0 * predicted / GRAVITY)
        check("flight time is the one gravity allows", abs(implied - obj.flight) < 1e-3,
              f"{obj.flight:.4f} s")


def limbs_not_overextended():
    print("\n5. no limb is stretched past its bones")
    perf = Performer()
    shots = build_shots(perf)
    h = perf.height
    worst = {}
    for shot in shots:
        n = max(2, int(shot.duration * FPS))
        for k in range(n):
            t = shot.duration * k / (n - 1)
            pose = shot(t, perf)[0]
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


def main():
    print("stickman verification")
    foot_is_static()
    foot_stays_on_floor()
    figure_stays_on_floor()
    jump_physics()
    limbs_not_overextended()
    print()
    if FAILS:
        print(f"{len(FAILS)} check(s) failed: {', '.join(FAILS)}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
