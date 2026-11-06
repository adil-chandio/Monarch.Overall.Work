# 3D parallax: what was actually wrong, and what it is now

The user's verdict on v5-31 was correct: *"3d parallax animation nahi aa rahi"*. Two
separate faults, and the second one was the real blocker.

## Fault 1 — a cutout pasted into a frame

`plate-cta-hero-front.png` is a genuine rotoscope: its edge is an 8 px ramp, not a step
(measured, three scanlines). But its alpha reaches zero inside its own bounding box, 40 px
from the bottom, so placing it anywhere in frame leaves a hard, ragged lower edge with the
background readable through it. Belt-and-braces green-screen keying was tried on our own
plates to rebuild the matte from scratch (`tools/matte.py`) — it works for the bag
(coverage 0.34, soft edge 0.010) and **fails on the portrait**, because a black leather
jacket against a dark red wall has no chroma separation. Recorded, not hidden.

What fixed it instead:

- the subject is scaled so his base lands **outside the visible frame** (anchor 0.52 with
  cover 0.98), so there is no lower edge in shot to be judged;
- `feather_edges()` — 44 px on the sides, 250 px at the bottom;
- a **contact shadow** ellipse that travels with him: the thing that most makes a cutout
  read as pasted is having nothing under it;
- a floor ramp that takes the bottom of the frame to near black.

## Fault 2 — there was no perspective, only offset

`Cam.project()` scaled a layer by `f/(f+z)` and translated it. Every point of a plane kept
its size, so the result was a flat card moving faster — not a plane turning in space.
That is why it measured right and looked wrong.

`_perspective()` now projects the layer's four corners through a pinhole after a real
rotation about Y and X, and warps the layer to that quadrilateral. The near edge grows,
the far edge shrinks, and the plane can be off-axis. One camera drives every plane, at
its own depth and its own angle:

| plane | z | yaw |
|---|---|---|
| the year "2008" | −520 | `0.75×` the camera, plus 5° so it always sits at an angle |
| the subject | +620 | `0.55×` the camera |
| red haze | +1500 | `1.4×` the camera — over-turns, which is what sells depth cheaply |

## Proof, as numbers

`public/demo/v5-parallax-proof.mp4` is the same scene with the orbit multiplied by 3.2 so
the mechanism is unmistakable. Tracking the year's grey ink across it:

```
t=0.00s  year ink centroid x = 517.0
t=0.73s                       506.4
t=1.50s                       469.2
t=2.27s                       411.8
t=2.97s                       370.7      (146 px of travel, against the subject's few px)
```

The subject's shoulders also change width as the plane turns, which is the trapezoid
doing its job. In the film itself the same orbit runs at 1/3 of this amplitude, spread
over 6 s.
