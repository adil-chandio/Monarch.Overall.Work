# Action-depth revision 2 — build on the positively received moving-3D excerpt

The owner said the prior moving-3D revision was better and requested further enhancement and a more interesting/engaging experience. This is directional feedback, not evidence of retention or blanket approval of every new frame. The full 7:19 English-film request remains active; this source still renders the selected 60.97-second excerpt, not the whole film.

## Actual animation changes

1. **Followable current tracer:** a 3D leaf falls, lands with expanding surface rings and travels down the channel toward the highlighted sample location. It is a visible illustrative leaf, NOT DNA made visible at leaf scale.
2. **Visible trace transport:** enlarged symbolic material/trace markers remain within the wet channel, progress without resets, and disperse across a small sediment shoal on arrival. Instanced-particle frustum culling is disabled because their transforms move far beyond the first frame's cached bounds; otherwise the follow camera could lose them despite correct state values.
3. **Environment:** curved water/shore alignment, bank-height-aware stone/tree placement, textured rather than flat pale stones. These remain stylized meshes/materials, not claimed photoreal field reconstruction.
4. **Developing deposition:** five bands visibly accumulate above two existing bands. Three schematic enlarged-marker cohorts fall and remain exposed at different section depths. The cap follows the growing surface; vertical growth preserves the same wavy band boundaries to avoid opening seams. This is a schematic explanation of accumulation, not measured sedimentation or dates assigned to marker cohorts.
5. **Age attaches to deposits:** a world-space bracket spans the section. It is not a molecule-age marker. The camera includes margin for the bracket, and label layout measures text width rather than assuming every tag is the same width.
6. **Character/environment detail:** subtle head orientation during the bird's departure, two leaves detach at the passing animal/branch contact, flutter down and remain on the ground; the branch has a small damped recovery. Attached leaves disappear when their detached versions begin. This remains explicitly imagined behaviour, not a recovered interaction.
7. **Sound follows shared events:** leaf-water landing, material landings and branch-leaf rustle use `action-cues.json`, shared with the animation. Existing attributed composed score and approved voice remain; no voice rewrite or speed change.

## Mechanical checks versus creative claims

`action.test.mjs` checks channel visibility bounds, monotonic transport, growing layers, exposed-cohort heights and continuous leaf release/landing. Native checks include the release frame and verify the actual branch-to-detached-leaf world-space discrepancy is below 1 mm. Locked-camera checks require both the mastodon and bird positions to progress, not merely a changing water shader.

These checks do not establish expert anatomical accuracy, professional sound review, viewer engagement, retention, virality or “perfect/premium” visual finish. Full human continuous AV review is not claimed. Current rendered results and release provenance are recorded in `QC.json` / `DELIVERY.json`; older release links remain historical versions, not this revision's automatic approval.

## Still unfinished

The complete film's action/environment variety, complete 58-task execution, stronger character/material finish and full-film audiovisual review remain unfinished. No new structure approval is requested, and this work does not revive the rejected V5 slides/image-plate pipeline.
