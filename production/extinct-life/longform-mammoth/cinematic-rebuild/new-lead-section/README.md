# New lead section — an empty rung instead of a culprit (652–689 s)

The 2025 microbial study is the easiest place in the film to fake a reveal. Bacteria
related to known pathogens, hundreds of specimens, a dying population: the dramatic
edit writes itself, and it would be wrong. The narration says the study **did not
identify a disease**, and that "related does not mean responsible".

So this 37-second section is an **evidence ladder** with the last rung left empty.

## What is on screen

| Shot | Time | Content |
|---|---|---|
| 0 | 0.0–10.0 | A specimen band: hundreds of ticks, captioned as hundreds of specimens including material older than the island population |
| 1 | 10.0–20.0 | Rungs appear: microbial DNA recovered · related to known pathogens · authenticated with controls · and a dashed, empty `A DISEASE THAT KILLED THEM` |
| 2 | 20.0–29.0 | The contamination/authentication caveat, and that the comparisons open questions rather than close them |
| 3 | 29.0–37.0 | `THE DIAGNOSIS IS STILL MISSING`, with the two sentences the narration gives |

The empty rung is drawn as a dashed outline with `no disease was identified` beside
it. Absence is the content, not an omission.

## What this section must never do

- **Never show a pathogen, a plaque, a microscope or a sick animal.** Each would
  convert "related" into "responsible", which is precisely the error the narration
  spends twelve seconds warning against.
- **Never imply the specimens are the Wrangel population.** The band is captioned as
  including material older than the island population, following the narration.
- **Never present authentication as a formality.** The controls beat is on screen
  because ancient microbial DNA is easy to introduce and hard to authenticate.
- **Never end on a resolution.** The section ends on a missing diagnosis, and the film's
  own verdict only begins at 689 s.

## Limits

- The tick count (160) is a **visual quantity**, not a specimen count; the narration
  says "hundreds" and the plate says "hundreds" without a number.
- No source figure, prevalence or effect size is depicted, because none is spoken.
- The 2025 study is named only as "2025 microbial study" in the footer; it needs a
  proper citation in the film's end credits and has not had specialist review here.

## Commands

```sh
node production/extinct-life/longform-mammoth/cinematic-rebuild/new-lead-section/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/new-lead-section/render-preview.mjs 1110
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py new-lead-section
```

1110 frames, 1280×720, 30 fps, silent. `inspect.mjs` checks determinism, animal
count, the seeded tick band and that the diagnosis-missing state is present only at
the tail. Not approved, not final, not authorised.
