# 3D layers and parallax camera

The user's screenshot exposed two real faults in v5, and both were in the code:

1. **the figure read as a sticker.** `plate-cta-hero-front.png` has real alpha, but the
   alpha dies at the cutout's own bounding box — mean alpha drops to 9/255 in the last
   40 px — so pasting it at 470 px wide left a hard, ragged edge with red seen through it.
2. **nothing had depth.** Every layer was drawn flat at the same plane with a scale, so
   the year travelled with the man instead of across him. That is not how the reference
   looks, and no amount of blur hides it.

## What is in the code now

```
class Cam          f/(f+z)  perspective per layer, and camera motion scaled by the same
                   factor, so a layer twice as far moves half as fast
place()            a full-frame layer through the camera
place_px()         a layer at a measured pixel width (type is set by ink width, never
                   by "what fills the frame")
feather_edges()    a cutout's border softened, 44 px on the sides and 250 px at the
                   bottom, because a subject is normally lost in shadow there
red_field()        the room: deep red wall, lit from upper left, darkening to the floor
rgb()              RGB in, frame order out -- with colour_selftest() run on every build,
                   because two channel swaps happened in a row before this existed
```

## The room, as three planes

| plane | z | behaviour over the shot |
|---|---|---|
| the year "2008" | −520 | 372 px wide at open, drifts `0.42×` the camera: it slides **across** the figure |
| the figure | +900 | full parallax, grows on the dolly |
| red haze | +1500 | 1.5× the camera, separates the planes |

Measured on the render: between 3.30 s and 6.23 s the year's centre moves ~19 px while
the figure's centre moves ~13 px the other way, and the figure's width grows 1.6 %. That
relative motion is the parallax; it is a number, not an impression.

## Still honest about

The room's saturation is now 38.0 against the reference's 69.4 — the shipped v5-31 file's
last build has the camera in and the grade not yet re-tuned for the new shadow ramp. That
is the next thing to fix, not something to describe as done.
