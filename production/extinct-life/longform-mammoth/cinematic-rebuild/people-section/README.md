# People section — the dated record, without people in it (391–411 s)

The narration's third witness is us: people hunted mammoths elsewhere, so it is fair
to ask whether anyone reached Wrangel while the animals were alive. The honest
picture of that question is **not** a hunter. It is a record with two dated positions
and an unresolved stretch between them.

So this 20-second scene is a printed plate, not a re-enactment. There are no
figures, no tools, no fire, no footprints, no staged encounter, and no artefact
photograph. Every prior attempt at procedural people and props in this project read
as a toy, and inventing an encounter would assert the one thing the narration
explicitly leaves open.

## What is on screen

| Shot | Time | Content |
|---|---|---|
| 0 | 0.0–7.0 | Title, then the dated rail draws in from the left |
| 1 | 7.0–14.0 | Both positions marked; the ~400-year interval bracket appears above the rail |
| 2 | 14.0–20.0 | "Earliest evidence ≠ first arrival", with the two-sentence caveat |

The marked positions are **the dates spoken in the narration** (~4,000 cal BP for
the youngest known mammoth remains, ~3,600 cal BP for the earliest known
archaeological evidence of people on the island). They are approximate, they are
not a calibrated confidence interval, and the four-century figure is a subtraction
of two approximations — not a measured gap.

## What this plate must never imply

- That the island was unvisited before 3,600 cal BP. Earliest *known* evidence is not
  first arrival, and the copy says so on screen.
- That the gap is exculpatory. "Not proof of innocence, nor of hunting" is written
  into the plate deliberately.
- That the marks are a site plan, a map or an artefact. The footer states
  `SCHEMATIC · NOT A SITE, MAP OR ARTEFACT · ILLUSTRATIVE`.
- That a date is a cause. The section ends before the narration's "three witnesses;
  none has shown the final moment".

## Determinism note

The paper-fibre texture is generated from a fixed integer hash of the pixel index,
not from the shared scene RNG. An earlier version advanced the RNG inside `draw()`,
which made two seeks to the same time produce different frames; `inspect.mjs`'s
same-seek-twice check caught it. Any future overlay work in this repository should
follow the same rule.

## Commands

From the repository root:

```sh
node production/extinct-life/longform-mammoth/cinematic-rebuild/people-section/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/people-section/render-preview.mjs 600
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py people-section
```

600 frames, 1280×720, 30 fps, silent. `inspect.mjs` checks determinism, the absence of
animals, the two marks, and that the interval bracket is absent at the head and
present at the tail. It does not check typography legibility on a real display,
reading order, or whether a viewer finds the plate convincing.
