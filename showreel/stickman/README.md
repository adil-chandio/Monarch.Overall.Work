# Stickman

A figure animated by a rig, not by cutouts.

## What this is

`rig.py` builds a stick figure out of a hip, a two-bone spine, a neck, a head,
two arms and two legs. Limbs are solved with two-bone inverse kinematics; the
spine runs forward from a lean curve. `motion.py` drives it with three
authorities and nothing else:

* **the gait** — feet are pinned in world space, so a planted foot cannot slide.
  Stride and hip height are related by the contact geometry, not by taste:
  `Gait.max_stride` derives the longest legal stride for a given hip height.
* **gravity** — anything airborne follows a solved ballistic arc. The jump's
  flight time comes from its apex (`t = 2*sqrt(2h/g)`), not from a guess.
* **springs** — every stop, landing and impact is a damped oscillator, so it
  overshoots and settles instead of easing politely.

`stage.py` holds one projection, used by the backdrop and the figure alike, so
parallax is a consequence of geometry rather than a per-layer effect.

## Verification

    python -m showreel.stickman.verify

Checks the properties that make the motion believable rather than merely smooth:
that a stance foot does not move, that the figure stays on the floor, that the
jump's apex matches the physics, and that no limb over-extends.

## Render

    python -m showreel.stickman.render_film --out deliverables/monarch-stickman-1080x1920.mp4
    python -m showreel.stickman.render_film --out deliverables/monarch-stickman-preview.mp4 --preview

Frames stream into ffmpeg; a full cut is never held in memory.

## Limits, stated plainly

* One figure, one camera, no dialogue, no background action.
* The figure has no face beyond a single eye dot, so expression is carried by
  silhouette, timing and gaze direction only.
* Thickness is constant along a limb; there is no real cel-shaded volume, only
  near/far separation and a rim light.
