# Approved-style 3D flagship production

The owner approved the 24-second reference and requested the full film with further improvements. See `PRODUCTION.md` for the scope, complete eight-chapter specification and the honest implementation status. **This directory is work in progress, not a finished six-to-eight-minute film. No additional opening-approval gate is requested.**

## Implemented first production sequence

Chapter index 2 (chapter 3, the mineral-preservation passage) uses the original **51.76-second selected voice**, unchanged. Its delivery window is 52.10 s / 1,563 native 1080p30 frames. The rest of the feature remains to be modelled and authored; the renderer deliberately refuses an unimplemented chapter rather than filling it with this scene.

The approved procedural 3D material/lighting engine is extended, not its MP4 footage:

- A continuous textured sediment bank now extends behind the mineral aggregate, replacing an isolated object against a void.
- A complete short illustrative fragment breaks into two separately animated pieces on the breakage cue. One disperses and is lost; the other continues through the same world.
- Thermal jitter decreases in the cold/mineral passage; the surviving fragment approaches and settles on the mineral during the binding explanation.
- A separate exposed fragment is lost during the warning that protection is not eternal. No indestructible shield, magical genome assembly or cloning is shown.
- Surface detail, bound-fragment coverage and a wider sediment archive support the final chemistry/layer explanation.
- Twenty-two authored shot windows have unequal, phrase-motivated durations, all no longer than three seconds. Alternate coverage changes angle/size/detail, while action time and object identity continue.
- New continuous sound bed and restrained break/contact sonification, not a whoosh at every cut.

All molecular shape/colour, temperatures implied by motion, mineral geometry, particle paths and spatial scales are **conceptual**, not measured molecular dynamics or microscopy. Native captions explicitly distinguish the reconstruction from actual sample imagery. Scientific boundaries and the Kjær et al. 2022 source remain those in the approved proof and original source ledger.

## Local commands

```sh
# Uses the same pinned renderer/runtime dependencies as ../flow-proof/.
.venv/bin/pip install -r production/extinct-life/feature-3d/requirements.txt
npm install --no-save --package-lock=false --ignore-scripts playwright@1.64.1 @sparticuz/chromium@153.0.0 three@0.187.0
.venv/bin/python production/extinct-life/feature-3d/test_contract.py
node production/extinct-life/feature-3d/render.mjs --chapter=2 --stills
node production/extinct-life/feature-3d/render.mjs --chapter=2
.venv/bin/python production/extinct-life/feature-3d/finish.py
.venv/bin/python production/extinct-life/feature-3d/test_contract.py
```

Working frames, renderer libraries, WAVs and picture-only encodes stay in ignored `.cache/extinct-feature-3d/ch02/`. The selected voice and approved clay materials are referenced from their existing durable repository files; they are not regenerated or silently substituted.

## Cloud production

`.github/workflows/extinct-feature-3d.yml` renders only entries marked implemented in `sequence.json`. It can parallelise genuinely authored chapters as their worlds are added; it does **not** currently render all eight. The current implementation permits chapter 3 only. Successful output, technical report and frame samples are uploaded as a GitHub artifact. A successful production chapter is also committed to the fixed session branch for durable download, without uploading to YouTube. Run failure is not a completed deliverable.

Planned chapter output: `deliverables/Extinct_Life_3D_Chapter03_Production_1080p.mp4`. It must not be called the full film. Full-film assembly and release remain blocked until all eight actual scene implementations and their rendered coverage exist. A verified full-feature watch/listen and owner review are still required; passing technical tests is not a creative-quality guarantee.
