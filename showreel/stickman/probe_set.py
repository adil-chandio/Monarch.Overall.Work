"""Development probe: the stadium set at a few camera positions.

    python -m showreel.stickman.probe_set
"""

from __future__ import annotations

import argparse

import numpy as np
from PIL import Image

from .film import H, W
from .stadium import Stadium, paint
from .stage import Projector


def frame(cam, stad=None, tunnel_open=1.0):
    from .stadium import tunnel as tunnel_mod
    stad = stad or Stadium("floodlit", goal_d=cam.get("goal_d", 25.0))
    proj = Projector(W, H, cam_x=cam.get("x", 0.0), cam_y=cam.get("rise", 0.0),
                     eye=cam.get("eye", 0.235), zoom=cam.get("zoom", 1.0),
                     tilt=cam.get("tilt", 0.0))
    f = paint(stad, proj)
    f = tunnel_mod(f, proj, openness=tunnel_open)
    return np.clip(f, 0, 1)


CAMS = {
    "wide": dict(zoom=0.62, eye=0.30, tilt=0.10, goal_d=52.0),
    "pitch": dict(zoom=1.05, eye=0.26, tilt=0.06, goal_d=25.0),
    "goal": dict(zoom=1.55, eye=0.24, tilt=0.02, goal_d=25.0),
    "tunnel": dict(zoom=1.30, eye=0.25, tilt=0.03, goal_d=42.0),
}


def sheet(out="probe_set.png"):
    tiles = []
    for name, cam in CAMS.items():
        t = 0.0 if name == "tunnel" else 1.0
        f = frame(cam, tunnel_open=t)
        img = Image.fromarray((f * 255).astype(np.uint8)).resize((360, 640),
                                                                 Image.LANCZOS)
        tiles.append(img)
    canv = Image.new("RGB", (360 * len(tiles), 640))
    for i, t in enumerate(tiles):
        canv.paste(t, (360 * i, 0))
    canv.save(out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="probe_set.png")
    a = ap.parse_args(argv)
    print("wrote", sheet(a.out))


if __name__ == "__main__":
    main()
