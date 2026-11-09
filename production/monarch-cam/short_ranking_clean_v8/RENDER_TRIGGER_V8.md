Clean V8 render trigger.

This file is part of the narrow push-path filter for
`.github/workflows/monarch-cam-short-ranking-clean-v8.yml`.

Pushing a change under `production/monarch-cam/short_ranking_clean_v8/` rebuilds the separate clean
V8 60s MP4, runs the nine unchanged web audio gates plus clean-layout technical QC, and commits the
new MP4/review evidence with `[skip ci]`.

V7 is rejected; do not present its link again. V8 is a separate deliverable path.
