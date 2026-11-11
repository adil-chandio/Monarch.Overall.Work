# Verdict section — one sustained landscape for 759–783 s

The final chapter argues rather than reveals: the picture should stop throwing new
evidence at the viewer and let a single place sit still while the narration says what
is supported, what is plausible, and what was never established. That is what this
24-second scene is for.

It is **not** a reconstruction of Wrangel, not footage of the last mammoths, and not
a depiction of the extinction. Terrain, sky, weather, herd size, spacing and every
camera move are authored. The animals are the same third-party rig described in
`../mammoth-rig/README.md`, whose source identity and rights are still unresolved.
`WRANGEL · ILLUSTRATIVE RECONSTRUCTION` is burned in as a disclosure line; no date,
count or cause appears on screen.

## Shots

| Shot | Time | Camera | Content |
|---|---|---|---|
| 0 | 0.0–9.0 | Wide, high horizon, slow lateral drift | Four animals small on a plain with most of the frame given to sky |
| 1 | 9.0–17.0 | Lower and closer | The herd further off, read as a group rather than individuals |
| 2 | 17.0–24.0 | Pull back and settle | Wind in the grass; the animals drift toward the horizon and the shot ends still |

The section deliberately reuses the **palette and terrain family** of
`final-crossing/` without reusing its composition: `final-crossing` ends on one
footprint at low sun, this ends on open ground. Together they run 759–796 s.

## What this section does not claim

- It does not visualise a cause of extinction. No ice crust, no hunters, no disease,
  no starving animal, no final death.
- It does not show a recovered or "healthy" population as a verdict either; a
  handful of animals walking is compatible with both stability and decline.
- Four animals is a **staging choice**, not a population figure. Effective
  population size is not a head count, and neither is this.
- The wind, haze and grain are illustrative weather.

Mechanically the render is 720 frames at 1280×720, 30 fps, silent. `inspect.mjs`
verifies determinism, animal and triangle counts, that the shot index advances in the
expected pattern, and that the sky value rises through the section. None of that is
evidence of quality.

## Commands

From the repository root:

```sh
node production/extinct-life/longform-mammoth/cinematic-rebuild/verdict-section/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/verdict-section/render-preview.mjs 720
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py verdict-section
```

Output and the workprint live in the ignored `.cache/`. Not approved, not final,
not authorised for publication.
