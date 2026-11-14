#!/usr/bin/env python3
"""
EP01 - the first 60 seconds, built as real 3D.

Every shot is a camera curve, a light rig and an animation state. Nothing is a
still, nothing is an image. Framing is *solved*: the field of view comes from the
subject's real height and the fraction of frame it must fill at the camera's real
distance, after the camera has been pulled inside the cave volume.

Geometry contract (all metres):
    floor        y = -1.35
    boulder      centre (0, -1.35, 0), radii (0.42, 0.30, 0.42)  -> top y = -1.05
    skull        origin on the boulder top, snout towards +z
    bear         origin at the feet, nose near z = +1.6, shoulder y = +1.45
    warm key     the hand torch the person is holding
    cold fill    the cave mouth, ~15-18 m down the bore, blue

Beat sheet (matches the fact-checked script, chapter 0 + start of 1):
  0.0   skull on a rock, torchlight        -> the gesture
  9.0   pull back, the room grows          -> scale
 17.0   the animal, backlit in the mouth   -> the bear
 27.0   it comes up and fills the doorway  -> ONE DOOR
 36.0   the skull again, closer            -> 600 kg was never the story
 46.0   the walk: weight, momentum         -> movement
 54.0   the mouth, cold light, to black    -> hand-off to chapter 1
"""
from __future__ import annotations

import math

import numpy as np

from geo3d import Cave, ease, ease_out

W, H = 960, 540          # nominal; the renderer sets the real size
FPS = 24
DUR = 60.0

BOULDER = dict(centre=(0.0, -1.35, 0.0), radii=(0.42, 0.30, 0.42))
SKULL_ORIGIN = (0.0, -1.05, 0.0)
SKULL_MID = (0.0, -1.06, 0.02)
BEAR_POS = (0.0, -1.35, 1.50)
# the walk is defined once here so the camera, the feet and the footstep cues all
# agree: stride 0.55 m at 1.0 Hz = 0.55 m/s, which is 4.4 m over the 8 s shot
BEAR_WALK = dict(z0=1.30, z1=-3.10, freq=1.0, stride=0.55)


def bear_walk_pos(u):
    return (0.0, -1.35, BEAR_WALK["z0"] + (BEAR_WALK["z1"] - BEAR_WALK["z0"]) * u)


def lerp(a, b, t):
    return a + (b - a) * t


def _inside(eye, tgt, cave, margin=0.34):
    """Slide the camera towards its subject until it is out of the rock."""
    e = np.asarray(eye, np.float32).copy()
    t = np.asarray(tgt, np.float32)
    for _ in range(80):
        if float(cave.sdf(e[None, :])[0]) < -margin:
            break
        e = e + (t - e) * 0.04
    return e


def _shake(u, amp=0.006, seed=0.0):
    """An operator holds the camera: micro drift, not a gimbal."""
    return np.array([amp * math.sin(u * 2.1 + seed),
                     amp * 0.7 * math.sin(u * 3.3 + 1.7 + seed),
                     amp * 0.8 * math.sin(u * 1.7 + 3.1 + seed)], np.float32)


def framed(centre, offset, eye_y, subj_h, frac, cave, shake=0.0, seed=0.0):
    """(eye, target, fov) with the fov derived from the *final* distance."""
    c = np.asarray(centre, np.float32)
    tgt = c.copy()
    eye = np.array([c[0] + offset[0], eye_y, c[2] + offset[2]], np.float32)
    eye = _inside(eye, tgt, cave)
    if shake:
        eye = eye + _shake(0.0, shake, seed)
    d = float(np.linalg.norm(eye - tgt))
    vfov = 2.0 * math.degrees(math.atan(subj_h / (2.0 * frac * max(d, 0.08))))
    return eye, tgt, vfov


def orbit(centre, az_deg, dist, eye_y, subj_h, frac, cave, shake=0.0, seed=0.0):
    a = math.radians(az_deg)
    return framed(centre, (math.sin(a) * dist, 0.0, math.cos(a) * dist), eye_y,
                  subj_h, frac, cave, shake, seed)


def bear_shot(pos, yaw, dist, eye_y, subj_h, frac, cave, side=1.0, lead=0.0,
              shake=0.0, seed=0.0, lift=1.05):
    """Broadside framing: the camera sits perpendicular to the way the animal faces."""
    p = np.asarray(pos, np.float32)
    face = np.array([math.sin(yaw), 0.0, math.cos(yaw)], np.float32)
    perp = np.array([math.cos(yaw), 0.0, -math.sin(yaw)], np.float32) * side
    centre = p + face * 0.30 + np.array([0.0, lift, 0.0], np.float32)
    off = (perp * math.cos(lead) + face * math.sin(lead)) * dist
    return framed(centre, off, eye_y, subj_h, frac, cave, shake, seed)


class Rig:
    """Per-shot camera + light + animation. u is normalised time in the shot."""

    def __init__(self, name, dur, cam, lights, act, text="", texpos="low", exposure=1.0):
        self.name, self.dur = name, dur
        self.exposure = exposure
        self.cam, self.lights, self.act = cam, lights, act
        self.text, self.texpos = text, texpos

    def sample(self, t):
        u = min(max(t / self.dur, 0.0), 1.0)
        eye, tgt, fov = self.cam(u)
        return (np.asarray(eye, np.float32), np.asarray(tgt, np.float32), float(fov),
                [(np.asarray(L["pos"](u), np.float32), L["col"], L["pow"](u), L.get("kind", "point"))
                 for L in self.lights], self.act(u), self.exposure)


def _skull(act_extra=None, torch=(0.98, -1.30, 0.50), rot=0.42):
    d = dict(kind="skull", scale=1.0, pos=SKULL_ORIGIN, rot=rot,
             boulder=BOULDER, torch=torch)
    if act_extra:
        d.update(act_extra)
    return d


def _bear(pose=0.0, walk=0.0, phase=0.0, pos=BEAR_POS, yaw=0.0, breath=0.0):
    return dict(kind="bear", pose=pose, walk=walk, phase=phase, pos=pos, yaw=yaw, breath=breath)


def film():
    cave = Cave()
    shots = []

    # ---------------------------------------------------------------- S1  skull, torchlight
    shots.append(Rig(
        "S1", 9.0,
        cam=lambda u: orbit(SKULL_MID, 12.0 + 7.0 * u, 1.32 - 0.10 * u, -0.90,
                            0.36, 0.52, cave, shake=0.004, seed=0.4),
        lights=[dict(pos=lambda u: (0.98, -1.30, 0.50), col=(1.00, 0.47, 0.15),
                     pow=lambda u: 1.15, kind="fire", flicker=True),
                dict(pos=lambda u: (0.0, 0.7, cave.mouth_z), col=(0.40, 0.58, 1.00),
                     pow=lambda u: 24.0, kind="portal")],
        act=lambda u: _skull(dict(rot=0.40 + 0.05 * u)),
        text="37,000 - 28,000 YEARS AGO", exposure=1.15))

    # ---------------------------------------------------------------- S2  pull back
    shots.append(Rig(
        "S2", 8.0,
        cam=lambda u: orbit(SKULL_MID, 19.0 + 10.0 * u, 1.30 + 2.10 * u, -0.90 + 0.34 * u,
                            0.36, 0.52 / (1.0 + 1.35 * u), cave, shake=0.005, seed=1.1),
        lights=[dict(pos=lambda u: (0.98, -1.30, 0.50), col=(1.00, 0.47, 0.15),
                     pow=lambda u: 1.00, kind="fire", flicker=True),
                dict(pos=lambda u: (0.0, 0.7, cave.mouth_z), col=(0.42, 0.60, 1.00),
                     pow=lambda u: 34.0, kind="portal")],
        act=lambda u: _skull(),
        text="A SKULL ON A ROCK", exposure=1.25))

    # ---------------------------------------------------------------- S3  the animal
    shots.append(Rig(
        "S3", 10.0,
        cam=lambda u: bear_shot(BEAR_POS, 1.02 + 0.10 * math.sin(u * 1.6), 4.60 - 0.35 * u,
                                -1.05, 2.35, 0.60, cave, lead=0.20 + 0.22 * u, shake=0.006, seed=2.0),
        lights=[dict(pos=lambda u: (0.0, 0.9, cave.mouth_z + 0.3), col=(0.46, 0.63, 1.00),
                     pow=lambda u: 60.0, kind="portal"),
                dict(pos=lambda u: (-1.30, 0.30, 2.40), col=(0.52, 0.66, 1.00),
                     pow=lambda u: 1.60, kind="fire", flicker=True)],
        act=lambda u: _bear(pose=0.04 * u, yaw=1.02 + 0.10 * math.sin(u * 1.6),
                            breath=math.sin(u * 5.0)),
        text="PLACED.", exposure=2.45))

    # ---------------------------------------------------------------- S4  it comes up
    shots.append(Rig(
        "S4", 9.0,
        cam=lambda u: bear_shot((0.0, -1.35, 1.28), 0.55, 4.55 - 0.75 * u, -0.62,
                                1.20 + 1.15 * ease_out(u), 0.52, cave, lead=0.12,
                                shake=0.007, seed=3.0, lift=1.05 + 0.55 * ease_out(u)),
        lights=[dict(pos=lambda u: (0.0, 1.0, cave.mouth_z + 0.2), col=(0.46, 0.63, 1.00),
                     pow=lambda u: 72.0, kind="portal"),
                dict(pos=lambda u: (-0.90, -1.20, -1.30), col=(1.00, 0.48, 0.16),
                     pow=lambda u: 1.10, kind="fire", flicker=True),
                dict(pos=lambda u: (-1.20, 0.60, 2.30), col=(0.52, 0.66, 1.00),
                     pow=lambda u: 1.50, kind="fire", flicker=True)],
        act=lambda u: _bear(pose=0.16 + 0.64 * ease_out(u), pos=(0.0, -1.35, 1.28),
                            yaw=0.55, breath=math.sin(u * 4.0)),
        text="ONE DOOR", exposure=2.30))

    # ---------------------------------------------------------------- S5  back to the skull
    shots.append(Rig(
        "S5", 10.0,
        cam=lambda u: orbit(SKULL_MID, -28.0 - 9.0 * u, 1.22 - 0.20 * u, -0.88,
                            0.36, 0.54, cave, shake=0.004, seed=4.0),
        lights=[dict(pos=lambda u: (0.92, -1.28, 0.62), col=(1.00, 0.46, 0.14),
                     pow=lambda u: 1.05, kind="fire", flicker=True),
                dict(pos=lambda u: (0.0, 0.6, cave.mouth_z), col=(0.40, 0.58, 1.0),
                     pow=lambda u: 20.0, kind="portal")],
        act=lambda u: _skull(dict(rot=0.38 + 0.08 * u), torch=(0.92, -1.28, 0.62)),
        text="600 KG - NOT THE BIGGEST", exposure=1.10))

    # ---------------------------------------------------------------- S6  the walk
    shots.append(Rig(
        "S6", 8.0,
        cam=lambda u: bear_shot((0.0, -1.35, 0.95 - 1.55 * u), math.pi * 0.5, 4.20,
                                -1.00, 2.20, 0.64, cave, lead=0.10, shake=0.008, seed=5.0),
        lights=[dict(pos=lambda u: (0.0, 0.95, cave.mouth_z + 0.4), col=(0.46, 0.63, 1.00),
                     pow=lambda u: 54.0, kind="portal"),
                dict(pos=lambda u: (1.10, -1.25, -1.10), col=(1.00, 0.52, 0.20),
                     pow=lambda u: 1.35, kind="fire", flicker=True),
                dict(pos=lambda u: (-1.50, 0.40, 1.20), col=(0.52, 0.66, 1.00),
                     pow=lambda u: 0.90, kind="fire", flicker=True)],
        act=lambda u: _bear(pose=0.0, walk=1.0, phase=u * 2 * math.pi * BEAR_WALK["freq"],
                            pos=bear_walk_pos(u), yaw=math.pi * 0.5),
        text="", exposure=1.42))

    # ---------------------------------------------------------------- S7  the mouth, cold
    shots.append(Rig(
        "S7", 6.0,
        # the opening must sit *inside* the frame: its angular radius is about
        # atan(2.4 / d), so the lens has to be wider than that or the frame is
        # nothing but daylight
        cam=lambda u: (np.array([0.55 - 0.20 * u, -0.50, cave.mouth_z - 9.2 + 0.9 * u], np.float32),
                       np.array([-0.10, 0.42, cave.mouth_z + 0.6], np.float32), 64.0),
        lights=[dict(pos=lambda u: (0.0, 1.0, cave.mouth_z + 1.2), col=(0.52, 0.68, 1.00),
                     pow=lambda u: 120.0, kind="portal")],
        act=lambda u: dict(kind="none"),
        text="NOT A BEAR'S ANY MORE", exposure=1.05))

    return cave, shots


def total(sh):
    return sum(s.dur for s in sh)
