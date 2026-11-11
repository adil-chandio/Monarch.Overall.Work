# 2024 reversal — a modelled bottleneck, deliberately not a herd (473–495 s)

The 2024 study is the film's turn: a severe bottleneck, then a modelled recovery, with
genetic strain surviving both. It is also the section where a picture can most easily
lie, because the numbers are dramatic and the model is easy to stage as animals.

So this 22-second section stages **the model**, not the animals.

## What is on screen

| Shot | Time | Content |
|---|---|---|
| 0 | 0.0–6.0 | 21 outline marks — 7 mainland, 14 Wrangel — then they clear for the plot |
| 1 | 6.0–12.0 | Axes appear with the two spoken values marked: "8 or fewer" and "~250" |
| 2 | 12.0–18.0 | The modelled curve draws left to right, with the ~20-generation marker |
| 3 | 18.0–22.0 | `EFFECTIVE SIZE ≠ HEADCOUNT`, with the model-versus-count sentence |

The curve is generated from the narration's own reported numbers (floor of 8, plateau
of ~250, recovery over ~20 generations) and is labelled **MODELLED / not measured,
not counted** for as long as it is visible.

## What this section must never do

- **Never show eight animals becoming three hundred.** Effective population size is a
  model parameter. Drawing a herd would convert a genetic estimate into a census and
  contradict the narration in the same breath.
- **Never show sick animals, immune failure or "genetic meltdown" as a condition.**
  Immune-gene diversity loss is a genetic finding, not a diagnosis of infection.
- **Never present the curve as measured data.** It carries no confidence interval
  because none is plotted here; the shape is an illustration of a stated direction,
  not a fitted curve from the paper.
- **Never imply the plateau was comfortable.** The section stops before the
  "recovery did not mean its genetic risks disappeared" line at ~544 s, which still
  needs picture.

## Accuracy notes

- 21 genomes = 7 mainland + 14 Wrangel, following the narration and the study.
- "~50,000 years" is the span of the dataset, not the age of the island population.
- The 8 and the ~250 are the numbers **as spoken**; the 8 is an upper bound in the
  source ("eight or fewer"), and the section's axis label says "8 or fewer".
- Coverage and data-quality caveats (546–561 s) are not depicted; a later section
  would have to handle them without turning missing data into damage.

## Determinism

Paper texture is fixed-hash noise, not the scene RNG, so repeated seeks are identical.
`inspect.mjs` asserts that, plus animals = 0 and the curve/warning state at the ends.

## Commands

```sh
node production/extinct-life/longform-mammoth/cinematic-rebuild/reversal-section/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/reversal-section/render-preview.mjs 660
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py reversal-section
```

660 frames, 1280×720, 30 fps, silent. Not approved, not final, not authorised.

Source for the study and its figures: Dehasque et al., Cell (2024),
DOI 10.1016/j.cell.2024.05.033 — see `../genome-record/README.md` and
`../genome-gap/README.md` for the same study's other visuals.
