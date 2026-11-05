# The room, from the plate's own pair — and the bug that made the blob

The screenshot showed a dark red **blob** behind the figure, a **pasted** look, and a
vertical band at the frame's edge. The cause was one mistake in my code, not in the art.

## What the assets actually are

Every plate ships as **two registered layers** — the set with nobody in it, and the
subject with its own alpha:

| plate | back | front | authored offset | rebuild error |
|---|---|---|---|---|
| cta-hero | 768×1376 | 659×1060 RGBA | (54, 288) | 5.76 |
| bag-green | 768×1376 | 494×907 RGBA | (120, 234) | 10.36 |
| bag-stool | 768×1376 | 415×512 RGBA | (174, 528) | 14.92 |
| hands-red | 768×1376 | 734×947 RGBA | (24, 156) | 6.09 |

The offsets are measured, not guessed: compositing front over back at those offsets
reproduces the original plate to within 5.8/255. **That is the green-screen separation
already done correctly** — the subject on one layer, a clean room on another.

## The bug

`pair()` scaled the room by its depth and the subject by *its* depth
(`f/(f+z)` = 1.53× against 0.71×). One plate, two scales, so the subject no longer sat on
the offset it was authored at: his baked contact shadow slid out to the left and sat on
the wall as a red blob, and the room's edges moved inside the frame.

Fixed by one rule: **the pair shares a single scale.** Depth is expressed only as what a
camera does to a plane — how far it shifts, and how far it turns (`_perspective`, a real
projection of the four corners). The room is drawn with `BORDER_REPLICATE` so its plane
continues past the frame, and an outer band is eased toward the room's own mean so no
edge can read as a border.

## What it looks like now

`public/demo/v5-34-3d.mp4` — 210 frames, 61 s to build, no black frames, no frozen frames.
The figure is inside a continuous red room, his own shadow falls on the floor where it
belongs, the frame has no border, and the year is a separate plane behind him that the
camera slides across.

## Still true, still said plainly

The photographic objects are ours, not the reference's. The edit, the timecodes, the type
system, the grade and the camera are the reference's.
