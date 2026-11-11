# Coverage section — why "more damage" can mean "more readable" (557–585 s)

The 2024 study's most counter-intuitive point is that a genome can look worse simply
because more of it was read. The narration's own analogy is a room seen through
windows of different sizes. That analogy is drawn **literally** here, because any
substitution — glowing strands, cracked DNA, red damage markers — would smuggle in the
claim the section exists to refuse.

## What is on screen

| Shot | Time | Content |
|---|---|---|
| 0 | 0.0–7.0 | Title and subtitle |
| 1 | 7.0–14.0 | Two windows over the **same** room: a small crop reads **18 marks**, a large crop reads **129** |
| 2 | 14.0–20.0 | One matched-coverage window over the whole room, and the instruction to test the difference rather than assume it |

The marks are a fixed, seeded field. Neither window is "worse": the small window is a
crop of the identical room, so the count difference is purely an aperture effect.

## What this section must never do

- **Never colour the extra marks as damage.** The whole point is that the extra marks
  are more of the same room being read, not a sicker animal.
- **Never claim a real coverage number.** 18 and 129 are illustrative counts chosen to
  read clearly at 720p; they are not the study's depth figures and must not be quoted
  as such.
- **Never imply the opposing trends are settled.** This plate stops before the
  "highest-impact variants became less common / moderate variants accumulated" beat at
  ~589 s, which needs its own treatment and its own "predicted effects" caveat.

## Bug worth remembering

The first version of this plate drew two **empty** windows. A random-hash multiplier
was far too small (`40503`), so every mark's y-coordinate collapsed onto one line and
the crop contained zero points. The count labels printed "0 MARKS IN VIEW", which is
how it was caught. Fixed by using full-width multipliers (`1597334677`); the section now
verifies 18 / 129. If a future scene uses hash noise, check the *distribution*, not just
that the code runs.

## Commands

```sh
node production/extinct-life/longform-mammoth/cinematic-rebuild/coverage-section/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/coverage-section/render-preview.mjs 600
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py coverage-section
```

600 frames, 1280×720, 30 fps, silent. `inspect.mjs` checks determinism, the 140-mark
room, two windows in the first plate, the matched-coverage plate at the tail, and no
browser errors. Not approved, not final, not authorised.
