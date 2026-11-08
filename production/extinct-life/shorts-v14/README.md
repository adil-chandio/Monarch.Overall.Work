# Extinct Life V14 — first audience-acquisition Short

**Production authorised by owner on 8 November 2026; public posting NOT authorised.** This folder preserves the researched proposal, authored source and review export evidence. It does not modify V13/V14 or the approved long-film thumbnail.

## Deliverables

- Main review export: repository-root `deliverables/Extinct-Life-V14-Mastodon-Short-1080x1920.mp4` (see DELIVERY.json).
- `English.srt`: matched approved 102-word English narration; phrase-level editorial alignment.
- `DESCRIPTION.txt` and `UPLOAD-CHECKLIST.md`: draft upload package and native Related Video prerequisites.
- `ZACK-MOTION-STUDY.md`: four original Zack-upload transcript/metadata audits, mechanism-level transfer, explicit source-footage/frame-level limitation.
- `RESEARCH.md`, `research/CORPUS.{json,csv}`: earlier 20-original / 13-million-plus research cohort and boundaries.
- `PROPOSAL.md`: original approval-stage proposal, intentionally preserved as historical draft; current generated duration/settings are in `film/timeline.json` and DELIVERY.json.
- `VOICE-PROVENANCE.json`, `audio/*.flac`: selected narration voice and lossless source chunks, unsped.
- `SOUND-DESIGN.json`, `film/sound.py`: own instrumental music, original synthetic illustrative Foley, narration ducking and mix generation.
- `film/scene.mjs`, `stage.html`, `render.mjs`, `timeline.json`: native portrait Three.js authored animation and renderer.
- `QC.json`, `review/`: post-encode objective checks, opened inspection frames and explicitly unverified creative/listening acceptance.

## Reproduce

Requires repository Node dependencies `three`, `playwright`, `@sparticuz/chromium`, Python numpy/scipy/imageio_ffmpeg/Pillow, existing licensed repo fonts, native original animal GLBs and the Chromium runtime libraries used by V14. The existing workspace has these; installing from the root package alone is not sufficient because historical render dependencies are not all declared there. Dependencies/host libraries are not vendored in this folder.

1. Run `.venv/bin/python production/extinct-life/shorts-v14/film/prepare_audio.py` to restore the three archival takes and the 50-second, 48 kHz narration at the timeline offsets. No TTS rerun or speed change is required.
2. Run `.venv/bin/python production/extinct-life/shorts-v14/film/sound.py` to produce mix/stems. Original fixed RNG score, not competitor audio.
3. Run `node production/extinct-life/shorts-v14/film/render.mjs --stills` for first inspection. Full halves use `--from=0 --to=750` and `--from=750 --to=1500`; two software-rendering workers need substantial time/memory. Use `--serve --port=4194` only for the interactive scene, not the encoded-video delivery.
4. Run `.venv/bin/python production/extinct-life/shorts-v14/film/finish.py` to concatenate/mux and run encoded inspections. This requires both complete render halves, and writes the main MP4 plus QC artifacts.
5. Run `.venv/bin/python production/extinct-life/shorts-v14/film/test_timeline.py` (8 tests).

## Rights / scientific boundaries / remaining review

Native animal GLBs are existing original procedural sculpts from `film-v9-full/native-meshes/ASSETS.json`; modified by existing V14 deformation code, with authored short-coat details and new portrait direction. They are reused assets—not newly anatomically expert-validated animals. No competitor scene, soundtrack or character copied. Fonts retain the repository's Anton/Manrope OFL licensing in `youtube-v14/licenses/`. DNA, sediments, mineral surfaces and reference blocks are schematic; forests/animals imagined reconstructions. No exact study sequence data, precision confidence score, intact genome or resurrection is depicted.

**Not a certified Zack-level production.** Source-video frame-by-frame competitor audit was unavailable. Independent anatomical validation, full perceptual audio listening and owner's final creative acceptance remain open. The export is a concrete review candidate, not a declaration of “no flaws.”

## Final render lighting trade-off

Full dynamic shadow maps made software-render readback prohibitively slow. The final native-resolution render uses direct-lit Phong wide-shot materials, procedural surface textures and authored soft contact-occlusion planes; PBR materials remain in the molecular close-ups. Per-strand coat line geometry is disabled in the wide shots; fine coat/skin surface texture remains. No frame interpolation, reduced-resolution 3D pass or upscale is used. This is a disclosed procedural/stylized review export, not path-traced studio realism.
