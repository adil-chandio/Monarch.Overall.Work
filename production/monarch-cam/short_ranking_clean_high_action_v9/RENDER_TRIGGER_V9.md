High Action V9 final render trigger.

This file is part of the narrow push-path filter for
`.github/workflows/monarch-cam-short-ranking-high-action-v9.yml`.

Pushing a change under `production/monarch-cam/short_ranking_clean_high_action_v9/` rebuilds the separate
high-action V9 60s MP4, runs the unchanged nine web audio gates plus clean-layout technical QC, and commits
the new MP4/review evidence with `[skip ci]`.

The technically successful V8 is rejected on clip quality and must not be presented again as accepted.
V9 uses its own deliverable path, its own `deliverables/.gitignore` exception, seven curated high-action
payoff windows, native raw per-window audio and the clean content-first layout.
