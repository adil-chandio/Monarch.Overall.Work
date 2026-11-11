# Contact section — what the dates can and cannot carry (411–455 s)

The human question is the one place where a documentary is most tempted to resolve
something the record has not. This 44-second section is built so that it cannot: the
screen keeps the dated evidence and the unresolved possibilities in **two registers**
for the whole passage, and the divider between them never opens.

## Structure

| Shot | Time | Content |
|---|---|---|
| 0 | 0.0–14.0 | Two registers side by side. **ESTABLISHED BY THE DATES**: archaeological evidence at ~3,600 cal BP, centuries after the youngest known mammoth remains. **NOT RESOLVED BY THE DATES**: first arrival, a human contribution, direct evidence of an encounter. A dashed divider labelled `KEPT SEPARATE` |
| 1 | 14.0–27.0 | `DIRECT EVIDENCE WOULD BE HARD TO FIND` — a field of empty dashed survey squares; an encounter between a few people and a few animals leaves little that survives; *not ruled out* is not the same as established, in either direction |
| 2 | 27.0–33.4 | `ELSEWHERE IS NOT HERE` — an arrow from other sites that stops at a cross marked `NOT TRANSFERABLE`; archaeology shows the species met, but this island needs its own evidence; a card saying what would change the picture |
| 3 | 33.4–41.6 | `AN APPARENT GAP IS NOT A VERDICT` — human involvement is possible but not established; two equal verdict boxes, `PROOF OF INNOCENCE` and `PROOF OF HUNTING`, both struck through |
| 4 | 41.6–44.0 | `THREE WITNESSES HAVE OFFERED CLUES` / `None has shown the final moment`, handing off to the closing argument |

## Rules this section follows

- **No human is depicted, and no mammoth is depicted with a human.** No spear, no fire,
  no camp, no kill site. The whole question is whether an encounter left evidence; a
  picture of the encounter would answer it visually while the script says it is open.
- **The two verdicts are destroyed equally.** Struck through at the same weight, because
  "the gap is not proof of innocence, and it is not proof of hunting" is symmetric.
- **No dates are invented.** The two dates shown (~4,000 and ~3,600 cal BP) are the ones
  spoken in the narration; the subtraction of roughly 400 years is disclosed as
  subtraction in `people-section`, and this section shows only the two endpoints.
- **Transfer is shown as refused**, not merely described: the arrow visibly fails.

## Limits

- The survey grid is a **schematic of the search**, not a map of any real survey area,
  and its cell count means nothing.
- "None has been found" is true of the evidence described in the narration, not a claim
  about every archaeological survey ever conducted on Wrangel Island.
- The section does not adjudicate the 2019 researchers' caution; it restates it.
- No archaeological review has been done. This plate must not be treated as a summary
  of the archaeology.

## Commands

```sh
node production/extinct-life/longform-mammoth/cinematic-rebuild/contact-section/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/contact-section/render-preview.mjs 1320
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py contact-section
```

1320 frames, 1280×720, 30 fps, silent. Not approved, not final, not authorised.
