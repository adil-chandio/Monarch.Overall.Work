# Cinematic rebuild — experimental excerpt, not a finished film

This project is a work in progress, **not** the requested complete documentary. `SHOT-PLAN.md` describes the intended full-film shots. The earlier rendered excerpt is `deliverables/Last-Mammoths-3D-Isolation-Test-22s.mp4`, a 22-second excerpt covering the beginning of the post-opening island chapter. It ends mid-narration. It was rendered frame-by-frame at 1280×720, 30 fps: 660 scene evaluations. It is not a 1080p final master.

The previously published test uses a procedurally generated 3D mammoth, tundra, rocks, vegetation, sky, water, snow and camera moves. The earlier floating floe has been replaced with approximate coastal terrain. Two AI-generated images are used **only as UV material maps** on 3D geometry (fur and tundra), not as slides or background illustrations. The island is artistic and is not a geographic reconstruction of Wrangel. A later silent 3-second motion test is `deliverables/Last-Mammoths-Gait-Test-3s.mp4`; it uses the current gait and is not a film. The source now includes a later kinematic walking experiment with four-beat foot placement, terrain-height foot-center targets and fur parented to limbs and feet. The published test predates it. Legs are single segments, feet can intersect obstacles, and the trunk and head are not articulated; see `GAIT-NOTES.md`. The anatomy, fur, terrain and lighting are stylized and need substantial refinement. No herd, laboratory, archaeological and molecular scenes have yet been completed.

Test audio comes from 60 seconds into the existing replacement full-film mix, not the old rejected opening soundtrack. Subtitles are automatically aligned; no continuous human listening or subtitle review was performed. The encoded test passed a full ffmpeg decode; `RENDER-TEST.json` records the older source-frame render, not the current gait source. `verify_scene.mjs` checks deterministic limb pivots and errors, not animation quality or anatomical accuracy.

Run from repository root, with Three.js/Playwright/Chromium and imageio-ffmpeg installed:

```sh
node --test production/extinct-life/longform-mammoth/cinematic-rebuild/test_gait.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/verify_scene.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/render.mjs --stills --frames=0,210,390,540
node production/extinct-life/longform-mammoth/cinematic-rebuild/render.mjs --from=0 --to=660
# First build the replacement audio cache if it is absent:
.venv/bin/python production/extinct-life/longform-mammoth/full-film/sound.py
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/finish_test.py
```

The test does not overwrite the earlier full-film master. Do not publish either to YouTube without explicit authorization.
