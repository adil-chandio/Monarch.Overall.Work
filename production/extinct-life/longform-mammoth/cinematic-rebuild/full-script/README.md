# Expanded documentary narration — production work in progress

This folder is **not the requested completed video**. It contains a 1,935-word science-corrected *adaptation* of the research-stage `../../SCRIPT-V1.md`: the full cold-case story across the opening, island, 2017 genetics, environment, humans, 2024 genetics, missing evidence, verdict and ending. It is not a word-for-word reading and does not preserve every sentence or detail of the original. The old draft contains incorrect or unsupported claims and must not be presented unchanged as accurate science.

The ten MP3 takes use the previously selected English documentary voice at its generated speed. Decoded durations yield an approximately 13:54 timeline with chapter gaps, not a completed soundtrack or film. `inspect_takes.py` checks decoding, duration, hashes and sample peaks. It does **not** check pronunciation, pacing, accuracy or audio quality by listening. The narration and the automatically aligned subtitles need human review. In particular the coat explanation in section 04 and specimen-range explanation in section 09 are repetitive and should be tightened/retaken during editorial review, not claimed to be final.

`planned-shots.json` contains 58 **planned**, time-anchored cinematic beats and 302 automatically aligned subtitle cues. None of these 58 shots has been represented as completed or rendered by the planning tool; source-scene, geometry, animation, art, effects, compositing, sound and full picture editorial remain to be produced. `English-auto.srt` is an approximate known-transcript alignment, not a human-reviewed caption file. The 22-second old test and 3-second gait test in `deliverables/` use older narration and are not this film.

## Scientific guardrails

- 2017 FOXQ1 changes predict a coat phenotype; neither wool loss nor fatal freezing is demonstrated: [Rogers and Slatkin, PLOS Genetics](https://journals.plos.org/plosgenetics/article?id=10.1371/journal.pgen.1006601).
- Stable Wrangel collagen carbon/nitrogen applies to the examined samples, not proof every season was good. Water deterioration and an icing event are hypotheses: [University of Helsinki, 2019 study summary](https://www.helsinki.fi/en/luomus/news/last-mammoths-died-remote-island).
- The recovery figure is modelled effective population size, not a literal animal census. Genetic strain persisted; missing final generations refer to that dataset: [Dehasque et al., Cell 2024](https://www.cell.com/cell/fulltext/S0092-8674(24)00577-4).
- Human presence before the earliest known evidence cannot be excluded; no human cause is established. The microbial paper does not identify a Wrangel killer: [Guinet et al., Cell 2025](https://www.cell.com/cell/fulltext/S0092-8674(25)00917-1).
- Reconstructions must be identified as such; never present invented events, geographic precision, coat appearance, health or specific mammoth behaviour as observed facts.

## Build / validate

Run from the repository root with `imageio-ffmpeg`, `numpy` and PocketSphinx installed:

```sh
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/full-script/inspect_takes.py
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/full-script/align_plan.py
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/full-script/validate.py
```

No YouTube upload has been authorised or performed.
