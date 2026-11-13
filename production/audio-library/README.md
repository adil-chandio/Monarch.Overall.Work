# Shared MONARCH SFX library

This is the common sound-effect registry for every video space in this repository. Video-specific mixes keep their own stems and cue sheets, but all of them can discover the same curated SFX sources and use the same frame-locked renderer/QC tool.

## Current user-provided collection

`catalog.json` indexes selected excerpts from four user-provided SFX-demo reels currently available in the workspace under `google_drive/`. Those original reels are **not** stored in this public repository. Their rights have not been independently verified, so the catalog labels them private-review-only. Do not use them in a public/client release until their license/permission is established. Do not commit or redistribute extracted audio payloads from these reels.

## Add future SFX

1. Put user-supplied source files in `production/audio-library/inbox/` (or make them available in `google_drive/` through the connected account). The inbox and generated cache are intentionally ignored by Git.
2. Inventory them with `python3 tools/sfx_sync.py scan --root production/audio-library/inbox --output .cache/sfx-inbox-scan.json`.
3. Review the actual audio and, for demo reels, the visible label/timeline. Add a source and individually cued excerpts to `catalog.json`; record provenance, license status, tags, and accurate excerpt bounds. A scan is discovery only—it does not grant rights or make a source approved.
4. For each video, create a project-local cue sheet keyed to the actual shot/action frame and mood. Render the SFX stem with `tools/sfx_sync.py render`; use `--private-review` for unverified user-provided material only in a private draft. Public release must fail closed unless every selected asset is cleared.

## Cue-sheet format

A cue sheet has `fps`, `duration_seconds`, and `events` (or `placements`). Each event uses an exact `frame` and either an explicit `cue_id`/`cue`, or `tags` plus `vibe` for deterministic catalog matching. Add a short `visual_action` explaining the picture event. Optional `gain`, `gain_db`, `pan`, `duration_seconds`, `foreground`, and fade settings are supported. The generator writes a 48 kHz stereo SFX-only WAV and a resolved cue report.

The shared tool locks sample starts to video frames, applies per-cue fades/pan/gain, validates asset rights mode and frame bounds, and can sidechain the SFX stem under narration/music. It does not infer visual meaning from an arbitrary final MP4: the video build/agent must author the action-to-frame map from the shot plan or rendered timeline, then QC the sync. No workflow can guarantee subjective "perfect" sound; the frame lock and evidence report make the timing reproducible and reviewable.
