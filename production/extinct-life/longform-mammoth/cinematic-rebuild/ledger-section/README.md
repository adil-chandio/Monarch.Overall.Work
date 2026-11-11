# Evidence ledger — three tiers of confidence (689–759 s)

Seventy seconds of narration do the most important work in the film: they sort the
evidence into what is **supported**, what is **plausible but not proven**, and what is
**not established**. Everything before this point builds towards that sorting, and
everything after it asks what evidence is still missing.

A conventional documentary would illustrate this passage with a culprit. This section
illustrates it with the sorting itself.

## Structure

| Shot | Time | Content |
|---|---|---|
| 0 | 0.0–3.0 | `WHAT CAN WE SAY?` — the narration's own question, then the three column heads |
| 1 | 3.0–24.0 | **SUPPORTED**: bottleneck then modelled recovery; reduced diversity and increased homozygosity; persistent genetic strain; dietary isotopes broadly stable; other signals read as possible water-quality change |
| 2 | 24.0–36.5 | **PLAUSIBLE, NOT PROVEN**: icing event; disease; poorer water; human involvement; a combination of pressures on a small isolated population |
| 3 | 36.5–45.0 | **NOT ESTABLISHED**: a single named killer; a directly recorded fatal winter; a genetic test proving the cause |
| 4 | 45.0–70.0 | The final generations are absent from the larger genome dataset — absence there is not absence of evidence; `A POSSIBILITY IS NOT A VERDICT`; `THESE CATEGORIES DO NOT HAVE TO COMPETE` |

Entries appear on the syllable that speaks them (2.0–42.7 s local), so the picture is
never ahead of the narration and never asserts a tier the voice has not reached.

## Rules this section follows

- **No cause is pictured, at any tier.** Not a plague, not ice, not a hunter. The three
  tiers are text on a paper plate precisely so no entry acquires an illustration that
  would rank it above its neighbours.
- **"Plausible" is never styled as likely.** The amber tier is a different category, not
  a weaker green.
- **The absence beat is the point**, so it is stated rather than implied: the larger
  genomic dataset does not reach the last generations.
- **No tier is ever empty of caveat.** The section ends on complementarity — vulnerability
  and a sudden event could work together — explicitly labelled a hypothesis.

## Limits

- Every line is a paraphrase of the narration's own wording; the plate adds no finding,
  prevalence, date or citation of its own.
- Column ordering is a presentation choice, not a claim about weight of evidence.
- Captions are already carried by the film's own caption track; this plate is not a
  substitute for it, and the two must be checked together for duplication at 689–759 s.
- No scientific review of the tier assignment has been done. The tiers follow the
  narration, not an independent audit of the literature.

## Commands

```sh
node production/extinct-life/longform-mammoth/cinematic-rebuild/ledger-section/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/ledger-section/render-preview.mjs 2100
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py ledger-section
```

2100 frames, 1280×720, 30 fps, silent. Not approved, not final, not authorised.
