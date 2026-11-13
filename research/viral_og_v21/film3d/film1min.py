#!/usr/bin/env python3
"""
EP01 — the first 60 seconds, built as real 3D.

Every shot is a camera curve, a light rig and an animation state. Nothing is
a still. Times are within the 60 s film.

Beat sheet (matches the fact-checked script, chapter 0 + start of 1):
  0.0  skull on a rock, firelight          -> the gesture
  9.0  pull back, the cave goes dark       -> scale
 17.0  bear revealed, backlit in the tunnel -> the animal
 27.0  it fills the doorway (rear)          -> ONE DOOR
 36.0  slow push to the skull, fire         -> 600 kg is not the story
 46.0  walk cycle, bear crosses frame       -> movement, weight, physics
 54.0  the mouth, cold light, cut to black  -> hand-off to chapter 1
"""
from __future__ import annotations

import math

import numpy as np

from geo3d import Cave, bear, skull, bone_pile, rocks, Dust, Flame, ease, ease_out

W, H = 960, 540          # render size; upscaled to 1080p at encode
FPS = 24
DUR = 60.0


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    return t * t * (3 - 2 * t)


class Rig:
    """Per-shot camera + light + animation. t is local seconds in the shot."""

    def __init__(self, name, dur, cam, target, fov, lights, act, text="", texpos="low"):
        self.name, self.dur = name, dur
        self.cam, self.target, self.fov = cam, target, fov
        self.lights, self.act, self.text, self.texpos = lights, act, text, texpos

    def sample(self, t):
        u = min(max(t / self.dur, 0.0), 1.0)
        return (np.asarray(self.cam(u), np.float32),
                np.asarray(self.target(u), np.float32),
                self.fov(u),
                [(np.asarray(L["pos"](u), np.float32), L["col"], L["pow"](u), L.get("kind", "point"))
                 for L in self.lights],
                self.act(u))


# ---------------------------------------------------------------- the film

def film():
    cave = Cave()
    shots = []

    # 1 - the skull on the rock, firelight -----------------------------------------------------------------
    shots.append(Rig(
        "S1", 9.0,
        cam=lambda u: (-0.34 + 0.06 * u, 0.20 + 0.10 * u, -1.30 + 0.14 * u),
        target=lambda u: (0.02, 0.10, 0.05),
        fov=lambda u: 34.0 - 2.0 * u,
        lights=[dict(pos=lambda u: (0.95, -1.05 + 0.05 * u, 0.85),
                     col=(1.00, 0.46, 0.14), pow=lambda u: 3.0,
                     kind="fire", flicker=True)],
        act=lambda u: dict(kind="skull", scale=1.0, pos=(0.0, -0.02, 0.0), rot=0.55),
        text="37,000 - 28,000 YEARS AGO"))

    # 2 - pull back, the room grows -------------------------------------------------------------------------
    shots.append(Rig(
        "S2", 8.0,
        cam=lambda u: (-0.45 + 0.20 * u, 0.32 + 0.40 * u, -1.6 - 2.2 * u),
        target=lambda u: (0.0, 0.20 + 0.30 * u, 0.3 + 0.9 * u),
        fov=lambda u: 36.0 - 4.0 * u,
        lights=[dict(pos=lambda u: (0.95, -1.0, 0.85), col=(1.00, 0.46, 0.14),
                     pow=lambda u: 3.0, kind="fire", flicker=True),
                dict(pos=lambda u: (0.0, 0.7, cave.mouth_z + 0.6), col=(0.42, 0.60, 1.00),
                     pow=lambda u: 55.0, kind="portal")],
        act=lambda u: dict(kind="skull", scale=1.0, pos=(0.0, -0.02, 0.0), rot=0.55),
        text="A SKULL ON A ROCK"))

    # 3 - the bear, backlit ----------------------------------------------------------------------------------
    shots.append(Rig(
        "S3", 10.0,
        cam=lambda u: (0.55 - 0.30 * u, 0.72 - 0.06 * u, -5.6 + 0.9 * u),
        target=lambda u: (-0.05, 0.85, 2.0),
        fov=lambda u: 40.0 - 3.0 * u,
        lights=[dict(pos=lambda u: (0.0, 0.9, cave.mouth_z + 0.4), col=(0.44, 0.62, 1.00),
                     pow=lambda u: 70.0, kind="portal"),
                dict(pos=lambda u: (0.6, -1.5, -8.4), col=(1.00, 0.52, 0.20),
                     pow=lambda u: 2.2, kind="fire", flicker=True)],
        act=lambda u: dict(kind="bear", pose=0.06 * u, walk=0.0, phase=0.0,
                           pos=(0.0, 0.0, 1.9), yaw=0.10 * math.sin(u * 2.2), breath=math.sin(u * 5)),
        text="PLACED."))

    # 4 - it fills the doorway -------------------------------------------------------------------------------
    shots.append(Rig(
        "S4", 9.0,
        cam=lambda u: (0.0, 0.70 - 0.30 * u, -3.0 + 0.7 * u),
        target=lambda u: (0.0, 0.90 + 0.20 * u, 1.8),
        fov=lambda u: 52.0 - 5.0 * u,
        lights=[dict(pos=lambda u: (0.0, 1.1, cave.mouth_z + 0.3), col=(0.42, 0.60, 1.00),
                     pow=lambda u: 85.0, kind="portal"),
                dict(pos=lambda u: (-1.5, 0.4, -4.2), col=(1.00, 0.50, 0.18),
                     pow=lambda u: 2.6, kind="fire", flicker=True)],
        act=lambda u: dict(kind="bear", pose=0.18 + 0.62 * ease_out(u), walk=0.0, phase=0.0,
                           pos=(0.0, 0.0, 1.5), yaw=0.0, breath=math.sin(u * 4)),
        text="ONE DOOR"))

    # 5 - the skull again, closer ----------------------------------------------------------------------------
    shots.append(Rig(
        "S5", 10.0,
        cam=lambda u: (-0.40 + 0.14 * u, 0.26 - 0.07 * u, -1.05 + 0.28 * u),
        target=lambda u: (0.04, 0.09, 0.02),
        fov=lambda u: 30.0 - 3.0 * u,
        lights=[dict(pos=lambda u: (0.80, -0.85, 1.10), col=(1.00, 0.45, 0.13),
                     pow=lambda u: 2.6, kind="fire", flicker=True),
                dict(pos=lambda u: (0.0, 0.6, cave.mouth_z), col=(0.40, 0.58, 1.0),
                     pow=lambda u: 30.0, kind="portal")],
        act=lambda u: dict(kind="skull", scale=1.0, pos=(0.0, -0.02, 0.0), rot=0.55 + 0.06 * u),
        text="600 KG - NOT THE BIGGEST"))

    # 6 - walk cycle, weight and physics ---------------------------------------------------------------------
    shots.append(Rig(
        "S6", 8.0,
        cam=lambda u: (1.05 - 0.15 * u, 0.85, -3.4 + 0.6 * u),
        target=lambda u: (0.20 - 0.18 * u, 0.85, 0.4),
        fov=lambda u: 34.0,
        lights=[dict(pos=lambda u: (0.0, 0.9, cave.mouth_z + 0.5), col=(0.44, 0.62, 1.00),
                     pow=lambda u: 60.0, kind="portal"),
                dict(pos=lambda u: (1.1, -1.6, -4.6), col=(1.00, 0.52, 0.20),
                     pow=lambda u: 2.4, kind="fire", flicker=True)],
        act=lambda u: dict(kind="bear", pose=0.0, walk=1.0, phase=u * 2 * math.pi * 2.4,
                           pos=(0.0, 0.0, 0.9 - 1.3 * u), yaw=math.pi * 0.5, breath=0.0),
        text=""))

    # 7 - the mouth, cold ----------------------------------------------------------------------------------
    shots.append(Rig(
        "S7", 6.0,
        cam=lambda u: (0.0, 0.80, -0.6 + 0.35 * u),
        target=lambda u: (0.0, 0.85, cave.mouth_z),
        fov=lambda u: 46.0,
        lights=[dict(pos=lambda u: (0.0, 1.2, cave.mouth_z + 1.0), col=(0.46, 0.64, 1.00),
                     pow=lambda u: 110.0, kind="portal")],
        act=lambda u: dict(kind="none"),
        text="NOT A BEAR'S ANY MORE"))
    return cave, shots


def total(sh):
    return sum(s.dur for s in sh)
