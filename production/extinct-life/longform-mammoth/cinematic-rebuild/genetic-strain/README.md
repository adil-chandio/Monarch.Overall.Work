# Genetic strain section — what the genomes show and cannot show (495–557 s)

This 62-second passage is where the genetics chapter is most easily inflated. Two
sentences govern it, and both are restrictions rather than findings:

- a group of immune-response genes lost more diversity than the genome as a whole, which
  is **a genetic finding, not a diagnosis of a specific infection**;
- effective population size fell to eight or fewer and recovered to roughly 250, which
  is **a model parameter, not a census of eight mammoths becoming three hundred**.

`reversal-section` (473–495 s) already owns the modelled curve. This section therefore
deliberately **does not draw it again**. It works in direction, comparison and label.

## Structure

| Shot | Time | Content |
|---|---|---|
| 0 | 0.0–16.0 | `TWO MEASURES, ONE GENOME`. Diversity and homozygosity drawn as **two equal-length arrows pointing in opposite directions** from a shared axis — only the relationship is shown, no magnitude. Then `NEITHER IS A DIRECT COUNT OF SICK ANIMALS` |
| 1 | 16.0–30.0 | `A GROUP OF IMMUNE-RESPONSE GENES`. Genome-wide diversity beside immune-gene diversity, because the narration says the latter "declined more than the genome as a whole". Then `A GENETIC FINDING, NOT A DIAGNOSIS`, with the explicit statement that no pathogen is identified here |
| 2 | 30.0–46.0 | `THEN CAME THE SURPRISE`. Two cards carrying the numbers **as spoken** — `EIGHT OR FEWER` at the bottleneck, `~200–300` within roughly 20 generations — then `EFFECTIVE SIZE IS A MODEL PARAMETER — NOT A HEADCOUNT` |
| 3 | 46.0–62.0 | `COMPARATIVELY STABLE — ACROSS THE SAMPLES`; recovery did not mean the risks disappeared; three dashed channels opening toward the coverage-bias test that follows at 557 s |

## Design decisions worth keeping

- **Equal-length opposing arrows in shot 0.** An earlier version drew two bars on one
  scale, which silently claimed one measure was larger. Diversity and homozygosity are
  related but differently scaled quantities; the arrows show direction only.
- **Shot 1 keeps a real comparison** because the narration itself makes one ("declined
  *more than* genome-wide diversity"), and the footer states the bars are not to scale.
- **No curve in shot 2, on purpose.** Repeating the `reversal-section` curve here would
  make the same model look like independent corroboration.
- **No animal, at any point.** Neither eight nor three hundred appears as anything but
  a numeral.
- **No percentage or effect size is printed.** None is spoken; inventing one would make
  the plate look like a figure from the paper.

## Limits

- Bar lengths in shot 1 are schematic proportions, not measurements, and the footer says
  so. They must not be measured off the screen.
- `EIGHT OR FEWER` is an upper bound, following the narration; the plate does not add
  confidence intervals it does not have.
- The section does not name the immune-gene group or the study's statistical method.
- No geneticist has reviewed this plate. It paraphrases the narration and adds no data.

## Commands

```sh
node production/extinct-life/longform-mammoth/cinematic-rebuild/genetic-strain/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/genetic-strain/render-preview.mjs 1860
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py genetic-strain
```

1860 frames, 1280×720, 30 fps, silent. Not approved, not final, not authorised.
