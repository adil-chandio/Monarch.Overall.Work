# Monarch — the duel (v3)

**4.75 s · 1080×1920 · 24 fps · 114 frames**

The second character. A silhouette walks up behind a line figure that is standing
at the lip of the chasm and shoves it in.

---

## What is actually new

v2 was one figure crossing a hole. v3 is two figures and a contact between them,
which is a different problem: a single figure can walk along an authored curve and
nobody can tell, but two figures that touch cannot. From the frame the silhouette's
hands meet the line figure's back, every frame either agrees about where that
contact is or the shot is broken.

So nothing in the middle of this shot is a curve fitted to look right:

| beat | frames | what decides it |
|---|---|---|
| approach | 45 | the silhouette's gait, integrated from its own stride |
| shove | 15 | the silhouette's hands, solved onto the hero's chest *after* the hero is solved |
| break | 11 | the hero's velocity at the lip, which is the shove's velocity and nothing else |
| drop | 15 | a projectile. `y'' = g`, and the fit below measures it |
| still | 28 | the silhouette walking the last step to the edge |

## The measurements

`python -m showreel.stickman.verify_duel` — **12/12**

```
PASS  contact: hands on the chest through the drive      max 50.5 px over 6 frames
PASS  contact: approach is monotone                      50 px at the last frame
PASS  fall: vertical acceleration is gravity             fitted 2900.0 vs 2900.0
PASS  fall: horizontal velocity is constant              980.0 vs 980.0 px/s
PASS  no teleports: pelvis never jumps a frame           max 93.6 px at t=3.21
PASS  silhouette: feet never below the floor             0 violations
PASS  silhouette: never crosses the lip                  max x -134.0 vs lip -150.0
PASS  occlusion: the body never blinks through the ground no blink frames
PASS  fall: is on screen for a readable number of frames 16 frames inside the void
PASS  hero: feet on the floor before the break           0 violations
PASS  timing: every beat is at least four frames         shortest 11 frames
PASS  no pose is entirely outside the frame              0 frames
```

The two that matter most:

- **the fall is fitted, not asserted.** A least-squares fit of the hero's pelvis
  through the fall returns `g = 2900.0`, which is the number the whole package
  uses. If a future edit put the body on a hand-authored arc, that fit would move
  and the assertion would fail.
- **the contact is monotone.** The hand travels 260 px to the chest and arrives in
  one direction, ending 50 px away — a hand's width. An earlier version had the
  hand still 240 px out on the frame the figure started to fall, which is a shove
  that never lands.

## Three bugs the verifier caught

Worth writing down, because each one was invisible in the stills and obvious in
the numbers:

1. **The hands were placed against a stored point.** `self.leave["chest"]` was
   computed once from a pose that was not the pose being drawn. On the frames where
   the hero is driven forward, the contact was 261 px off — a third of a figure.
   Fixed by passing the solved hero into `_contact()`.
2. **The hero's toes went through the floor during the shove.** The pose was
   translated vertically as a whole. A solved pose cannot be moved in y without the
   feet following it into the ground. Fixed by translating horizontally only.
3. **The body blinked through the ground.** The "is it inside the chasm" test was a
   step function, so the frame that crossed it was drawn either fully inside or
   fully outside the opening. Fixed by clipping from the frame the pelvis passes the
   lip and letting the mask, which is the chasm's own painted wedge, do the rest.

## A structural finding, not a styling one

Two earlier attempts at this shot were abandoned, and the reason is worth stating
because it constrains every future shot on this set:

- **A fall into a hole can barely be seen.** The chasm projects as a wedge; a body
  inside it is occluded almost immediately by the near ground, which is in front of
  the camera. That is what a camera on the near side of a hole actually sees, so it
  is correct — and it means the fall can only be shown for the 16 frames it spends
  in that window.
- **A cliff does not fix it either, at this lens.** With the figures 45% of frame
  height, a body's horizon-crossing reads as "it lies down", not as "it falls". I
  tried a cliff face and dropped it: the rock wall became a bright slab, and the
  drop still did not read as depth.

The lesson is that the *size* of the fall on screen is set by the lens, and at
1080×1920 with a 700 px figure, a four-metre drop is about 300 rows. Showing a fall
properly would need a wider lens and a smaller figure, which is a different
composition, not a different animation.

## What changed in the shared renderer

- `stage._paint_gaps` — the chasm interior is now **lit**, not black. A far wall
  across a void catches the sun; painting it black made the hole read as a strip of
  card on the ground, and it made a dark figure falling in front of it invisible.
  This changes the backdrop of the v2 film as well, for the better.
- `stage.void_mask` — the chasm's painted wedge, exposed so the renderer can clip a
  falling body with the same mask the backdrop was painted with. Above the near lip
  it admits everything, because the line of sight there is clear.
- `render.clip_to_gap` — applies that mask to a figure.
- `whip.SwingRig.hand_offset`, `pendulum_state(omega0=)` — the rig and pendulum
  fixes that were needed to make the rope geometry solvable, kept because the
  duel's catch solve needs the same facts.
- `rig`/`render` unchanged otherwise: the silhouette treatment added in v2 carries
  the whole second character.

## Honest ceiling

The shove is good. The fall is correct and short, and the shortness is a camera
problem, not an animation problem — the numbers say so and the section above says
why. If a longer read of the fall is wanted, the answer is a second shot at a
wider lens, not a longer fall in this one.
