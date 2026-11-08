# 7 Unexpected Animal Moments, Ranked. — Raw Full-Screen V6

## Status

V6 is a **separate technical package**. V4 and V5 were rejected; V5 is untouched. This document describes a corrected V6 build and its objective checks. It does **not** claim creative acceptance, full-motion human review, native-audio listening by a person, sign-off, perfection, retention, virality, or audience results.

`NEXT_ACTION.md` required per-title rights verification for real social-platform clips before a separate V6 package. V6 does **not** use unverified real social-platform reposts. It uses seven CC0 1.0 Wikimedia Commons original files, each rechecked through the Commons API extmetadata, recorded in `review/social_origin_ledger.json`. No claim is made that this clears third-party TikTok/Reels/Shorts reposts. Third-party social-platform clips remain unselected and unverified.

## What changed from rejected V5

V5 had an occluded centered hook/question, a right-side rank panel, and a bottom rank burst. V6 rebuilds the picture with:

- a centered, colorful top hook (`RANKING` / `7 UNEXPECTED` / `ANIMAL MOMENTS` / `WHICH ONE IS #1?`);
- a fully visible left `1.–7. LIST` with seven black label plates and progressive moment labels;
- custom right-side heart/comment/share platform UI icons (no V5 right rank panel);
- a bottom `COMMENT YOUR RANK` / `SUBSCRIBE` bar (no V5 bottom rank burst);
- reaction bubbles and custom vector emoji drawings;
- full-screen dynamic subject-safe cover crops, hard cuts, payoff cuts/zoom;
- explicit safe-area coordinates and a generated `review/layout_manifest.json`;
- objective QC checks for hook/list visibility, safe-area contract, social-origin ledger, and per-title Commons API verification.

The seven scene windows are inherited from the V5 runner-selected CC0 originals. They are recorded in `review/selected_windows.json` with `probe_basis = "V5 runner-selected windows inherited for V6; no new human review or creative acceptance."` V6 geometry is rebuilt, not copied from V5 review contact sheets.

## Rights and source ledgers

- `CREDITS.md` — seven CC0 1.0 Commons picture sources, creators, file pages, license URLs and voluntary attribution.
- `verify_sources.py` — per-title Commons API extmetadata verification; writes `review/verified_sources.json` and `review/social_origin_ledger.json`.
- `source_recon_ranking.py` — SHA-1 checks, exact window clips, `review/source_video_ledger.json`, `review/source_windows.json`, contact sheets and `review/review-manifest.json`.
- `source_audio_audit.py` — native source audio audit.
- `selected_windows.json` — seven locked windows, ranks `[7,6,5,4,3,2,1]`, source in/out times, native-audio RMS/motion scores inherited from V5.
- `social_origin_ledger.json` — per-title original Commons page, CC0 license, expected SHA-1, original file URL, no third-party repost flags.

No credit/crop/mirror/fair-use argument is treated as clearance. No unverified repost, @handle clip, silent source, generated call, AI audio, music, SFX, bed, narration or audio substitution is used.

## Audio contract

Exactly seven raw per-window native Commons audio segments, 48 kHz stereo, 60.0 seconds, one segment per scene. Hard cuts only; no added layers. `build_ranking_audio_raw_v6.py` writes `review/native_audio_ledger.json`; `python -m showreel.audio_qc.gates` writes `review/audio_qc.json`; `technical_qc_raw_v6.py` checks the delivered AAC stream and the full reference-mechanic picture.

## Picture and QC contract

- `ranking_short_spec.json` — duration, frame count, rank order, audio policy, corrected geometry and safe-area coordinates.
- `render_ranking_visual_raw_v6.py` — corrected V6 renderer; writes silent MP4, first/payoff frames, covers, emoji drawings, visual ledgers, `visual_review_lock.json` and `layout_manifest.json`.
- `validate_raw_v6.py` — dependency-free contract validation.
- `technical_qc_raw_v6.py` — nine web audio gates, duration/frame/codec probe, native-audio ledger, per-title rights, layout manifest, safe-area and social-origin checks.
- `.github/workflows/monarch-cam-short-ranking-raw-v6.yml` — builds, checks, uploads artifact, writes `review/qc_summary.json`, and commits the MP4 plus generated review evidence.

## Upload metadata

- Primary: `7 Unexpected Animal Moments, Ranked. | Native Commons Audio`
- Comments: Seven CC0 Commons moments with their own native audio; corrected V6 geometry; no outcome promised.
- Category: `Entertainment` (24), provisional pending uploader choice.
- Deliverable: `deliverables/MONARCH_CAM_7_Unexpected_Animal_Moments_Ranked_60s_Short_RAW_FULLSCREEN_V6.mp4`
- Measurement: compare 24h / 3d / 7d stayed-to-watch, engaged views, average percentage viewed, loops, comments, shares and channel growth. No result is promised.

## Honest gaps

- No full Arena export or verbatim all-chat transcript is available; this package does not change that continuity gap.
- `config/channels.json` still lists three legacy channel slots; Monarch Cam is the active continuity channel, not an invented fourth config slot.
- No human full-motion review or native-audio listening by a person is recorded.
- No creative approval, sign-off, upload, Studio review, RPM result, retention outcome, virality guarantee or 3× claim is recorded.
- V6 is a technical build for review; it is not a claim that the earlier rejection is resolved.
