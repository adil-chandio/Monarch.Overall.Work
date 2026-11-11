# verdict-close — the last forty-nine seconds

49 s of native picture (1470 frames at 30 fps), placed at **734.0 s**, running to the
film's end at 783.0 s. This is what the film ends on.

## Why it exists

The assembled film ended with **107 s of printed plate** (652–759 s) and then swapped to
animals for the last thirteen. Contact sheets of that stretch showed the problem plainly:
the ledger's four shots are near-identical tables, and the film's final statement — *a
possibility is not a verdict* — was delivered as a line of type on a spreadsheet.

But the close is not an enumeration. It is the argument that the enumerated categories
are allowed to coexist. An argument belongs over a place. So:

- `ledger-section` now stops at **734 s** (its first 1350 frames), ending after the
  *not established* shot. Its last shot, *a possibility is not a verdict*, was removed —
  the same sentence is now said over the island.
- `verdict-section` (759–783 s) is **no longer placed**. Its own wide shot of the same
  plain made the cut read as a repeat. The file is kept on disk for comparison.
- this section carries the two closing statements as lower-thirds and then simply holds.

The cut lands on a shot boundary in the ledger rather than mid-enumeration. The total
timeline is unchanged, so no other section moves.

## What it shows

Four long holds over the same four animals on the same plain, at evening light:

| shot | frames | seconds |
|---|---|---|
| the herd, still | 0–390 | 0–13 |
| settle and hold | 390–750 | 13–25 |
| the plain, and the light moving | 750–1110 | 25–37 |
| deepening toward the horizon | 1110–1470 | 37–49 |

The herd drifts a few metres and settles; the light does the work. Nothing is counted,
labelled or pointed at. The first cut of this section stopped at 25 s, which made the
film cut from this plain straight to `verdict-section` — another near-identical wide shot
of the same plain. It now absorbs that span, so the closing argument plays over one
uninterrupted place.

## What it refuses

- **No claim.** The lower-thirds are quotations of the narration underneath them, timed
  to the lines that speak them (`A possibility is not a verdict`, spoken 736.6–740.1;
  `These categories do not have to compete`, spoken 749.1–751.5). Both are local-time
  offsets from the build, so if the narration is re-timed these must be re-checked. The
  second card clears at 755.5 s, so the last half-minute is picture with no type at all.
- **No number, date, or count** anywhere in the frame.
- **No depiction of the bottleneck**, and no sick or dying animal. The herd is not the
  genetic result; the burn-in says so.
- **No new event.** No storm, no human, no arrival, no sunset theatrics — only the light
  going warm, which the scene's own look table controls.
- **No scrim box.** The lower-thirds sit on a full-width vertical gradient; a hard panel
  over this picture read as a slide laid on top of it.

## Honesty

Burn-in: `WRANGEL · ILLUSTRATIVE RECONSTRUCTION`.

Terrain, weather, herd size and camera move are invented. The animals are the same
third-party rig used across this project (`../mammoth-rig/README.md`); **the rig's rights
are unresolved and this section cannot be distributed until they are cleared.**

## Numbers

- 1470 frames, 56994 triangles, 4 animals, `claimMade: false`, `historical_geography: false`
- build: **−16.3 LUFS / −1.4 dBTP**, 1470 frames, offset 734.0 s
- silent review render: `.cache/mammoth-verdict-close/verdict-close-motion-review-silent.mp4`

## Commands

```bash
node production/extinct-life/longform-mammoth/cinematic-rebuild/verdict-close/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/verdict-close/render-preview.mjs 750
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py verdict-close
```

`inspect.mjs` probes nine times for animal count, triangle count, shot index and which
lower-third is up, and asserts that the same seek produces the same JPEG.

## A bug worth remembering

The fog colour was being interpolated as a **packed 24-bit integer** and passed to
`setHex()`. Between two greys the blended integer lands on magenta, and the horizon
flashed purple for most of a second at each look change (visible near 747 s and 756 s of
the assembled reel). Interpolate colour **per channel**; the helper is now `lerpHexRGB`
in both this section and `island-hold`. `coat-section`, `island-chapter` and
`verdict-section` still use the packed form, but their look tables interpolate between
near-identical greys, so a pixel probe of the horizon across their whole length shows no
hue break — they were checked, not assumed.
