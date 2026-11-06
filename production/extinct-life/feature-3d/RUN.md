# Production render hold — script revision first

**Current state, 6 November 2026:** rendering is disabled in `sequence.json`. Do not render against the old script/audio or treat its 404.8-second timeline as v2 timing.

- Historical chapter-only run: https://github.com/adil-chandio/Monarch.Overall.Work/actions/runs/42159702799 — subsequently verified **completed/cancelled**.
- Hold workflow: https://github.com/adil-chandio/Monarch.Overall.Work/actions/runs/42161344245 — completed successfully without a render.
- Public-script research: https://github.com/adil-chandio/Monarch.Overall.Work/actions/runs/42161344457 — succeeded and produced actual caption-derived evidence.
- Approved 24-second 3D style remains approved. No repeated opening/style approval gate is required.

## Script dependency

Read `../script-lab/ENGLISH-MASTER-v2.md`, its same-script translation in `../script-lab/OWNER-REVIEW-v2.md`, and `../../../docs/research/extinct-script-forensics/REPORT.md`.

The v2 master contains 1,045 English whitespace-token words. Fresh narration is not measured. Old Urdu clips and their estimated DTW timing do not narrate the rewrite. The old timeline and renderer remain historical implementation material, not a v2 shot list.

## Implementation reality

Only chapter index 2 has an authored 52.1-second 3D scene. The remaining seven worlds/animal rigs are not implemented. The existing source/seek checks and inspected stills do not establish a finished chapter or full film. No revised full-film playback exists to review.

## Resume conditions

1. Finish script comprehension/translation review and fresh natural narration; measure actual duration without time stretching. Current/growing-channel script-coverage gaps must remain disclosed.
2. Author v2 phrase-level subject/action/spatial-transition contracts and a new measured timeline. Preserve the approved moving 3D style and the maximum three-second shot rule, without equating quick cuts with continuity.
3. Adapt and implement all meaningful worlds/rigs. Never fill missing worlds with the existing sediment scene or repeated proof footage.
4. Update renderer, finisher and tests against the new master. Only then deliberately lift the render hold; never toggle it as a substitute for implementation.
5. Inspect actual encoded picture and audio before any completion claim. Full feature delivery and durable GitHub download remain outstanding. No YouTube upload is authorised.
