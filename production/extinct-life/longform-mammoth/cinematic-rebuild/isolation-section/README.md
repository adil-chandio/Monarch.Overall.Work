# Isolation section — a cross-section, not a coastline (86–114 s)

Around ten thousand years ago rising sea cut a population off from the mainland. The
temptation is to draw a map. **That would be dishonest here**, because the actual
palaeoshoreline of the Wrangel shelf is not known at the precision a drawn coastline
implies, and `../island-map/` already carries only modern coastlines with a standing
warning.

So this 28-second section draws a **cross-section of the process** and labels it as
one: two land masses, the shelf between them, and water rising through it.

## What is on screen

| Shot | Time | Content |
|---|---|---|
| 0 | 0.0–9.0 | Mainland and island, low water, shelf exposed between them |
| 1 | 9.0–18.0 | Water rises through the shelf; `ROUTE CUT` appears as the two masses separate |
| 2 | 18.0–28.0 | The three-population panel: Wrangel, East European plain, St Paul Island |

The three dates are **the approximations the narration speaks** (~15,000 years for the
East European plain, ~5,600 for St Paul Island, thousands of years of persistence on
Wrangel). They are not calibrated ranges, and the panel says so.

## What this section must never do

- **Never trace a coastline.** The shapes are blocks, not land. `SCHEMATIC
  CROSS-SECTION · NOT A PALAEOGEOGRAPHIC RECONSTRUCTION` is burned in.
- **Never imply the three populations shared a cause.** The panel lists three
  histories side by side precisely so that "other populations disappeared earlier and
  under different conditions" is visible rather than asserted.
- **Never show animals crossing or drowning.** The section is about a route closing,
  not a disaster witnessed.

## Layout notes (fixed while reviewing)

- The water plane originally spanned the whole frame and cut through both land
  masses; it now fills only the gap between them, with a thin sea line drawn beyond
  each coast.
- The three-population panel originally overlapped the section base; it now starts
  below it. Both were caught by looking at the rendered stills, not by the asserts —
  `inspect.mjs` cannot see a collision.

## Commands

```sh
node production/extinct-life/longform-mammoth/cinematic-rebuild/isolation-section/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/isolation-section/render-preview.mjs 840
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py isolation-section
```

840 frames, 1280×720, 30 fps, silent. `inspect.mjs` checks determinism, the shot
pattern, that the water line rises between the first and last probe, and that the
route-cut label and the panel are present at the tail. Not approved, not final.
