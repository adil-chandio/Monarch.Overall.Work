# Island hold — native picture under the genetic argument (473–539 s)

This section exists to answer a problem that only appeared once the film was assembled:
from 473 s to 646 s the timeline was **173 seconds of uninterrupted printed plate**, and
a viewer would have watched six minutes of the documentary's most important chapter
without anything living on screen. Every plate was individually defensible; together
they had turned an argument into a slide sequence.

So this is not a new claim. It is **the island put back under the voice**, so the genetic
distinctions have somewhere to sit.

## What it is

66 seconds, four slow moves across one plain under a drifting overcast:

| Shot | Time | Camera |
|---|---|---|
| 0 | 0.0–20.0 | Wide, high horizon, most of the frame given to sky |
| 1 | 20.0–38.0 | Lower and closer, herd read as a group |
| 2 | 38.0–52.0 | Across the plain, animals further off |
| 3 | 52.0–66.0 | Pull back and settle; ends still |

It carries the bottleneck, immune-gene and two-measures passages (473–539 s), then hands
back to `genetic-strain` at 539 s, just after "recovery did not mean its genetic risks
disappeared".

## What it deliberately does not do

- **Makes no claim.** No number, no date, no cause, no count. The only text on screen is
  the disclosure line `WRANGEL · ILLUSTRATIVE RECONSTRUCTION · NOT A DEPICTION OF THE
  GENETIC RESULT`.
- **Never shows the bottleneck as animals.** Four animals are on screen throughout — the
  same four in every shot. Nothing about population size is depicted, because a herd
  shrinking to eight would be exactly the false census this production keeps refusing.
- **Never cuts on a narration beat.** The overcast drifts continuously and the four moves
  are barely perceptible; a picture cut under "then came the surprise" would punctuate a
  claim the voice does not punctuate.
- **Never shows sick, starving or dying animals.** The narration's claims here are
  statistical. A distressed animal would be a medical claim.

## Limits — read before using

- Terrain, weather, herd size, spacing and every camera move are **authored**. This is not
  a reconstruction of Wrangel and not a depiction of these events.
- The animals are the third-party rig in `../mammoth-rig/README.md`, whose **source
  identity and rights are still unresolved**. This section cannot ship until that is
  settled.
- No snow-cover or vegetation plausibility review has been done. The ground reads as snow
  and pale tundra; whether that is right for the specific centuries in question has not
  been checked against the sources.
- The burn-in is a disclosure, not a caption: it must remain visible in any cut of this
  footage, and it must not be cropped out in a different aspect ratio.
- Motion review is sampled stills plus determinism checks, **not** continuous viewing.

## Commands

```sh
node production/extinct-life/longform-mammoth/cinematic-rebuild/island-hold/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/island-hold/render-preview.mjs 1980
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py island-hold
```

1980 frames, 1280×720, 30 fps, silent. Not approved, not final, not authorised.
