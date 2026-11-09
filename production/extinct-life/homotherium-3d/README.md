# Homotherium cub — actual 3D rebuild

This is a separate rebuild prompted by the user's correction that the previous Short was photo-based motion graphics, not the requested 3D production. Earlier exports, scenes and thumbnail are preserved.

## Scope and limitations

51 seconds, 1080 × 1920, 30 fps. Uses the previously selected English narrator and continuous sound mix without speeding the voice. Original **stylized procedural 3D illustration**, not a recovered scientific model, photogrammetry, or photorealistic anatomy. The cub is an original volumetric smooth implicit surface, with geometric fur fibers, small ears, closed eyelids, short muzzle, robust anterior body and broad forepaws. It is deliberately a partial anterior body, with no speculative living hindquarters, adult saberfangs, breathing, awakening, walking or resurrection. The model illustrates a preserved subject; it is not evidence of its exact living appearance. Stylization and resemblance still require creative judgment and are not validated by render tests.

The published CT-based reference remains an explicitly labelled image on a spatial display, not a fabricated volumetric CT or a new scan. It was partially reconstructed by mirroring in the original study. The staged layered ice volume does not reproduce the actual discovery context. The wireframe volume marks uncertain reconstruction, not associated measured bone anatomy. No calibrated measurements are made from this illustrative model.

## Sources and attribution

Research: Lopatin et al., *Mummy of a juvenile sabre-toothed cat Homotherium latidens from the Upper Pleistocene of Siberia*, Scientific Reports 14, 28016 (2024), https://doi.org/10.1038/s41598-024-79546-1 . CT-based figure 4A: **CC BY 4.0**, https://creativecommons.org/licenses/by/4.0/ , cropped, background-separated, resized and composited. Original files and source hashes: `../homotherium-short/SOURCE-LICENSE.json`; source processing details: `../homotherium-short/ASSET-EDITS.json`. Cub and paw photographs were inspected as morphological references but are not presented as measured 3D data.

The partial dead remains were discovered in Siberia in 2020, described in 2024. Calibrated date range: 35,471–37,019 cal BP. Roughly three weeks is estimated from dental development. Soft-tissue contrasts with a similar-aged lion are qualitative statements from the paper, not measurements of this model. “Survivor of deep time” means preservation, not surviving alive.

## Technical construction

`film/cub.mjs`: original ellipsoidal anatomical blocking merged into a smooth signed-distance implicit surface through marching cubes, seeded geometric fibers, procedural material and facial detail geometry.

`film/scene.mjs`: native Three.js meshes, lighting, cast shadows, stage, layered ice, spatial reference display, moving perspective cameras and illustration labels. The subject is geometry, not a flat image made to look dimensional. Overlays/captions remain a 2D compositing layer, as appropriate. The full script and timing follow `../homotherium-short/NARRATION.txt` and `film/timeline.json`.

`film/render.mjs`: deterministic native 1080 rendering via existing Chromium/Three.js tooling; intermediate frames remain in `.cache/homotherium-3d`. No source media is copied from competing YouTube creators.

Audio source/provenance and captions: `../homotherium-short/source/narration.flac`, `../homotherium-short/VOICE-PROVENANCE.json`, `../homotherium-short/SOUND-DESIGN.json`, `../homotherium-short/English.srt`. Original synthetic sound design, no third-party music. Recreate mix with `../homotherium-short/film/prepare_sound.py` before rendering if cache is absent.

```sh
.venv/bin/python production/extinct-life/homotherium-short/film/prepare_sound.py
node production/extinct-life/homotherium-3d/film/render.mjs
# Interactive native-3D preview:
node production/extinct-life/homotherium-3d/film/render.mjs --serve --port=4197
```

No YouTube publication is authorized or performed. This production makes no guaranteed performance or scientific-reconstruction accuracy claim. Automated checks and sampled stills are not a full human-style audiovisual watch/listen or creative acceptance.

## Review render, not a photoreal final-quality certification

Delivered 51-second native-1080 3D review render: `deliverables/Homotherium-Cub-3D-Rebuild-1080x1920.mp4`. All 1,530 frames decoded without errors. AAC audio: −16.17 LUFS integrated, −1.44 dBTP. Five structural checks passed. Final encoded frames sampled at two-second intervals (26 positions) and key native frames examined. Complete continuous audiovisual listening/watching has not been certified.

**Creative limitations remain:** the model is visibly stylized, with simplified closed eyelids, short procedural fibers and a smoothed partial-body silhouette. This is a genuine 3D rebuild but not a photoreal sculpt or a claim that the user's aspirational “next-level” quality bar is fulfilled. The same original 3D subject recurs in camera/feature shots; they are not ten unique environments. The CT shot is intentionally still a source-image reference. Do not market it as a measured scientific reconstruction or use automated tests as proof of creative acceptance.
