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

## Three films

| film | module | what it is |
|---|---|---|
| `monarch-stickman-1080x1920.mp4` | `render_film` | 11.5 s. One figure crosses a hole. |
| `monarch-duel-1080x1920.mp4` | `duel_film` | 4.75 s. Two figures, a shove, a fall. |
| `monarch-pov-stadium-v2-1080x1920.mp4` | `pov_film` + `pov_audio` | 90 s, ten shots, sound. A stadium, a face, and a silence. |

The third one changes three things the first two could not: the head can hold an
expression, the world can be a specific place, and the silence can be *heard*
because there is a mix under the picture. See `face.py`, `stadium.py`,
`pov_audio.py`, and `POV_V2_RELEASE_NOTES.md` for what it does not do.

## Verification

    python -m showreel.stickman.verify        # the figure and its physics
    python -m showreel.stickman.verify_duel   # contact, fall, occlusion
    python -m showreel.stickman.verify_pov    # the ninety-second film

Checks the properties that make the motion believable rather than merely smooth:
that a stance foot does not move, that the figure stays on the floor, that the
jump's apex matches the physics, and that no limb over-extends.

## Render

    python -m showreel.stickman.render_film --out deliverables/monarch-stickman-1080x1920.mp4
    python -m showreel.stickman.render_film --out deliverables/monarch-stickman-preview.mp4 --preview

Frames stream into ffmpeg; a full cut is never held in memory.

## Limits, stated plainly

* One figure at a time, one camera, no dialogue.
* The figure's face is drawn from about a dozen parameters, not modelled: it can
  be frightened or delighted, but it cannot be *specific* -- there is no likeness
  and no ageing, and it will never look like a particular person, by design.
* The stadium is a depth model rather than a 3-D scene, so the goal sits behind
  the action instead of beside it.
* Thickness is constant along a limb; there is no real cel-shaded volume, only
  near/far separation and a rim light.
