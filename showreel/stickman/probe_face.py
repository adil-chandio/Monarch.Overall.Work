"""Development probe: render the face vocabulary as a contact sheet.

Not part of the film. It exists so the expressions can be looked at as a set --
twelve heads at the size the camera will actually hold them -- instead of being
judged one at a time while a shot is being debugged.

    python -m showreel.stickman.probe_face [--out PATH] [--cols N]
"""

from __future__ import annotations

import argparse

import numpy as np
from PIL import Image, ImageDraw

from . import face as F
from .ink import disc, limb_ribbon, ring, stroke
from .render import ink
from .rig import Pose, build_pose

SET = [
    ("neutral", F.NEUTRAL),
    ("calm", F.CALM),
    ("focus", F.FOCUS),
    ("grit", F.GRIT),
    ("breath", F.BREATH),
    ("joy", F.JOY),
    ("shock", F.SHOCK),
    ("fear", F.FEAR),
    ("relief", F.RELIEF),
    ("direct", F.DIRECT),
    ("disdain", F.DISDAIN),
    ("blink", F.BLINK),
]


def head_pose(cx, cy, r, facing=1.0, head_ang=0.0, height=None):
    """A pose that is only a head, for looking at faces in isolation."""
    p = Pose()
    p.head = np.array([cx, cy], float)
    p.head_r = r
    p.facing = facing
    p.head_ang = head_ang
    p.height = height if height is not None else r / 0.0863
    p.tone = "ink"
    for name in ("pelvis", "waist", "chest", "neck", "shoulder_near",
                 "shoulder_far", "hip_near", "hip_far", "elbow_near",
                 "elbow_far", "wrist_near", "wrist_far", "knee_near",
                 "knee_far", "ankle_near", "ankle_far", "toe_near", "toe_far"):
        setattr(p, name, np.array([cx, cy + r * 4], float))
    p.hand_len = 8.0
    p.foot_len = 8.0
    return p


def sheet(out="probe_face.png", cols=4, cell=360, r=110, facing=1.0):
    n = len(SET)
    rows = (n + cols - 1) // cols
    W, H = cols * cell, rows * cell
    img = Image.new("RGB", (W, H), (247, 243, 234))
    d = ImageDraw.Draw(img)

    for i, (name, expr) in enumerate(SET):
        cx = (i % cols) * cell + cell // 2
        cy = (i // cols) * cell + cell // 2 - 12
        pose = head_pose(cx, cy, r, facing=facing)

        # A stub neck so the head is not floating.
        limb_ribbon(d, (cx, cy + r * 0.96), (cx, cy + r * 1.18),
                    (cx, cy + r * 1.30), 26, 30, 22, (24, 22, 28))

        rgba = ink(pose, face=expr, paper=(0.99, 0.975, 0.95),
                   size=(W, H))
        sub = Image.fromarray((np.clip(rgba[..., :3], 0, 1) * 255).astype(np.uint8))
        m = Image.fromarray((np.clip(rgba[..., 3], 0, 1) * 255).astype(np.uint8))
        img.paste(sub, (0, 0), m)

        d.text((cx - 34, (i // cols) * cell + cell - 34), name, fill=(20, 20, 20))

    img.save(out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="probe_face.png")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--facing", type=float, default=1.0)
    a = ap.parse_args(argv)
    print("wrote", sheet(a.out, cols=a.cols, facing=a.facing))


if __name__ == "__main__":
    main()
