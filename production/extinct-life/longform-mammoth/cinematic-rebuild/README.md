# Cinematic rebuild — production work in progress, not a finished film

This folder holds the 3D production for the long-form mammoth documentary. It is
**not** a finished film: no full-length picture-locked master exists, no sequence
has had continuous human viewing or listening, and nothing here is authorised for
publication. Mechanical QC (decode, frame counts, loudness, seek determinism,
sampled geometry probes) is not evidence of artistic, anatomical or scientific quality.

## What exists now

| area | state |
| --- | --- |
| `full-script-v2/` | Ten science-qualified narration takes, 796.042 s, auto-aligned captions, source crosswalk. Human script, caption, pronunciation and science review outstanding. |
| `soundtrack-draft/` | Continuous narration + music draft (796.1 s). No SFX; not continuously auditioned. |
| `storyboard-retime/` | 83 provisional blocks over the full narration length. Not picture lock. |
| `edit/` | Editor scripts that place verified silent renders under the narration draft, plus coverage accounting. 389.0 s of the 796.0 s timeline is covered by verified candidate windows, with overlaps reported rather than hidden. |
| `island-chapter/` | 60 s, seven-shot Arctic sequence (dawn herd, tracking walk, trunk to grass, calf, stream crossing, squall, dusk). 30 s placed at 140 s. |
| `coat-section/` | 34 s, five shots (macro wool texture, close flank, low legs, herd into low sun, exit hold). 24 s placed at 250 s. |
| `island-years/` | 30 s compressed-season study. An 8 s excerpt is available as an alternate; not currently placed. |
| `isolation-section/` | 28 s schematic cross-section of sea-level isolation plus the three-population panel; placed at 86 s. No coastline traced. |
| `island-approach/` | 18 s walk-and-forage scene; 10 s placed at 130 s. |
| `coverage-section/` | 20 s two-window plate for the coverage-bias argument; placed at 557 s. Repeats the narration's own room analogy literally. |
| `reversal-section/` | 22 s modelled-bottleneck curve for the 2024 result; placed at 473 s. Deliberately no herd and no animal count. |
| `people-section/` | 20 s dated-record plate for the human-evidence passage; placed at 391 s. No people, tools or artefact images. |
| `verdict-section/` | 24 s sustained landscape for the closing argument; placed at 759 s. |
| `final-crossing/` | 13 s closing motif ending on a stylised footprint; placed at 783 s. |
| `comparison-lab/` | 20 s sample-comparison workbench; placed at 172.7 s. |
| `stream-scene/`, `icing-hypothesis/` | 16 s stream and 14 s labelled rain-on-snow hypothesis; placed at 354 s and 370 s. |
| `genome-gap/`, `genome-record/`, `island-map/` | Conceptual evidence visuals; the gap timeline (17 s) is placed at 629 s. |
| `excavation/`, `foraging/`, `shoreline/`, `living-world/`, `sample-workflow/` | Earlier native-3D studies, variously stylised; not continuously reviewed. |
| `mammoth-rig/`, `skeleton-reference/`, `material-sources/`, `ambience-sources/` | Third-party assets and candidate recordings with documented, **unresolved** master identity and rights questions. |

## What is still missing

Roughly 407 s of the narration has no verified picture. The laboratory/genetics
chapter, the isotope and chemistry passages, the human-evidence chapter, the 2024
genome work and the verdict need sequences that do not yet exist or are only
partially built. Audio needs a continuous mix with ambience and music decisions,
and the whole film needs one uninterrupted viewing pass.

## Standing limits

All animal, terrain, weather and archaeology imagery is illustrative. The rig, its
source and its rights are unresolved (see `mammoth-rig/README.md`). Field recordings
are not Arctic (see `ambience-sources/README.md`). Scientific caveats live in the
narration and must not be contradicted by what is on screen. Never label an
assembly or excerpt as the finished film.

## Older notes (largely superseded)

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
