# The Lost World Inside a Handful of Dirt — English film v3

**Production candidate, not an owner-approved finished film.** This production replaces the rejected full-film timelines. The approved v3 English master is the sole narration source. No YouTube upload is authorized.

## Measured, not estimated

- Fresh user-selected English narrator: `voice-02`; eight lossless source clips with hashes in `voice-provenance.json`.
- Natural speech: **435.800625 seconds**. No stretching or acceleration.
- Authored film: **438.766667 seconds / 7:18.77**, 13,163 native 1920×1080 frames at 30 fps, including short chapter tails.
- 211 acoustically subdivided, manually subject-mapped shot windows, each at most three seconds. This count is **not** evidence that the creative quality is sufficient.
- Forced word alignment is an estimate, not a verified human pronunciation/transcription review. Optional English subtitle timing has the same limitation.

## Actual implementation

`animals.mjs` / `sculpt.mjs` implement original illustrative articulated mastodon-lineage, reindeer, hare, rodent and goose stand-ins. Smooth-union implicit surfaces, moving knees, trunk, ears, antlers and feather wings are meshes, not panned animal pictures. They are stylized stand-ins, **not photoreal or anatomically authoritative recovered individuals**.

`worlds.mjs` implements connected reconstructed habitat, polar-desert coast, shedding/river transport, sediment layers, conceptual mineral binding/fragments, pipette extraction, reference trays and evidence/pollen scenes. It uses original procedural geometry and the clay material assets already used in the approved proof. No proof footage is looped into the film. The original **AI-generated clay albedo** and its grayscale/autocontrast bump derivative remain in `../flow-proof/materials/`. The bump is not a measured physical height field; provenance is retained in `../flow-proof/README.md`.

`scene.mjs` evaluates absolute frame time. Actor action continues across coverage cuts; seeking backwards does not accumulate transforms. Shot coverage uses a consistent side of the action. Scientific qualifications are visible in the picture. A reconstructed community is not a filmed co-occurrence; conceptual particles are not actual reads, a complete genome, or a calibrated molecular simulation.

`finish.py` adds the untouched natural voice at its measured chapter offsets, an original synthesized felt-key/string-style score and sparse original synthesized environmental/physical foley. **This is not a recorded orchestra or a licensed premium stock score.** It uses measured two-pass loudness targeting, optional selectable English subtitles, full video decode checks, frame counts and hashes. The detectors and still checks do **not** substitute for a human full-length audiovisual review.

## Quality status and limitations

Internal native-frame checks found and corrected backwards animal framing, intersecting-ball torso silhouettes, flat marching-cube normals, floating background rocks, foreground macro occlusion, river grid-like highlights, resting T-pose wings and an unmotivated pipette motion. All eight chapters passed native-frame generation and deterministic A→B→A seeking locally. Representative frames have been visually inspected, and short real native-motion ranges have encoded successfully. Audio-only assembly also ran successfully (premaster −17.32 LUFS / −2.65 dBTP; preliminary normalization output −16.10 LUFS / −1.80 dBTP). These are audio-only test results, not measurements of a completed movie.

The animal/laboratory look remains visibly stylized. **Do not describe this candidate as photoreal, premium-quality approved, flawless, creatively validated, or already watched/listened through by a human.** Full-render completion is reported only by the actual successful render/assembly job and its generated `QC.json`. Until then, `manifest.json` truthfully remains render-pending / `full_film_complete: false`.

## Reproduce

Runtime: Node 22, Python 3.11, `three@0.187.0`, `playwright@1.64.1`, `@sparticuz/chromium@153.0.0`, `imageio-ffmpeg==0.6.0`, `numpy==2.2.6`. `prepare.py` additionally requires PocketSphinx to rebuild the estimated acoustic alignment; do not silently realign a different voice or script.

```sh
.venv/bin/python -m unittest discover -s production/extinct-life/film-v3 -p test_film.py
node production/extinct-life/film-v3/render.mjs --chapter=0 --stills
node production/extinct-life/film-v3/render.mjs --chapter=0
# Repeat chapter indices 1 through 7, or use the sixteen parallel ranges in Actions.
.venv/bin/python production/extinct-life/film-v3/finish.py
```

For an internal audio-only test, append `--audio-only` to `finish.py`. This does **not** produce or certify a finished film. Scratch frames, browser bundles, temporary PCM, score stems and encodes live in ignored `.cache/extinct-v3/`.

## Durable download

**Subsequent verified status:** [run 42224196920](https://github.com/adil-chandio/Monarch.Overall.Work/actions/runs/42224196920) completed successfully and published the [full v3 candidate with QC](https://github.com/adil-chandio/Monarch.Overall.Work/releases/tag/extinct-life-v3-42224196920). The owner liked the overall film but requested substantially less repetition and smoother flow. The active correction is `../film-v4/`; this v3 film is historical, not that revised download. The original authoring manifest below is retained as a pre-render provenance record.

`.github/workflows/extinct-film-v3.yml` renders sixteen non-overlapping native frame ranges, checks the coverage, assembles all eight chapters, normalizes audio and decodes every output frame. Only successful assembly produces the full MP4, subtitles and QC. The workflow then publishes an explicitly labelled **production-candidate prerelease** under tag `extinct-life-v3-RUN_ID`; it does not upload to YouTube. A queued/running workflow is **not** a finished downloadable movie.

Science: see `../script-lab/SCIENCE-LEDGER-v3.md` and the unchanged approved `master-v3.json`.
