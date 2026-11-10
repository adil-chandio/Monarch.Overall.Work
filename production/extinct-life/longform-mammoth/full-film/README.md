# The Last Mammoths — full film

A long-form film adaptation of the research-stage script: the completed 60-second 3D opening followed by the island, genetics, environment, humans, 2024 genomes, missing-evidence, verdict and ending chapters. `../FILM-VO.json` is the production narration; it is a tightened and science-corrected adaptation, not a word-for-word recording of the earlier `SCRIPT-V1.md` draft. The narration is synthesised with the previously selected voice-04 at its original speed.

## Sound redesign

The opening's original drone, wind and regular low pulse are **not reused**. A fresh original tonal score uses soft sustained chords and sparse felt-like notes, plus restrained pitched transitions. The new soundtrack covers both the opening and the rest of the film. `SOUND-DESIGN.json` records its construction. Automated measurements are not a substitute for a listener's subjective judgement.

## Visual provenance

The opening uses original procedural 3D. Later chapters combine original animated Three.js geometry with eight AI-generated background illustrations. These are explicitly labelled as illustrations in the frame, and are not presented as actual photographs, maps, laboratory observations or fossil evidence. Backgrounds are compressed JPEG derivatives of generated images. The later 3D compositions were rendered at 1280×720 and 4 fps, blended to 30 fps and upscaled for the 1080p master; they are not claimed to be native 1080p/30 fps 3D renders. The charts are schematic unless specific values are stated.

## Science

Claims and qualifications follow the 2017, 2019, 2024 and 2025 papers listed in `../opening-3d/SOURCES.md` and the production narration. Predicted coat phenotype is not claimed as an observation; effective population size is not a headcount; the absence of final-generation genomes is not the absence of all evidence; no single killer is claimed. The original script draft remains separate and still contains wording that should not be used without review.

## Rebuild

Requires Node.js, Three.js 0.187, Playwright, `@sparticuz/chromium`, Python, numpy, scipy, Pillow, imageio-ffmpeg, and PocketSphinx; this sandbox used a root `.venv` and root `node_modules`. The audio cache, 3D plate and generated QC contact sheet are written under `.cache/longform-mammoth-full/`.

```sh
.venv/bin/python production/extinct-life/longform-mammoth/full-film/plan.py
.venv/bin/python production/extinct-life/longform-mammoth/full-film/sound.py
node production/extinct-life/longform-mammoth/full-film/render.mjs
.venv/bin/python production/extinct-life/longform-mammoth/full-film/finish.py
.venv/bin/python production/extinct-life/longform-mammoth/full-film/check_final.py
.venv/bin/python production/extinct-life/longform-mammoth/full-film/validate.py
```

The subtitle timing uses automatic known-transcript alignment and should not be described as a manual listening review. `DELIVERY-QC.json` records the automated decode, loudness and sampled-frame checks. No automated check certifies creative quality.

No YouTube publication has been authorised or performed.
