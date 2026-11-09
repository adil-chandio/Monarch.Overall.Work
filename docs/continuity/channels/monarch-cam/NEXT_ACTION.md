# Exact next action — Monarch Cam

**Single next action:** finish and upload the separate V7 60s ranking Short, then give only the V7 GitHub download link. Do **not** re-present V4, V5 or V6. Do **not** ask the user to explain the channel, the rejection, or the workflow again.

## Why V6 is not the answer

The user rejected V6 after its GitHub upload and download-link answer:

> `Yeh Kya chutiyapa banaya ha NAHI abhi bhi theek se nhi ... Dekho 📈 trending viral videos ko Uthao clips social media par TikTok Instagram yt or Reddit Dailymotion ... viral ke sath sath purani bhi chalenge bas clips mazedar next level honi chaiye ... un clips se bhi best perfect mazedar hooked engaging scene nikalenge ... ranking list kese lagi ha sab kuch visible horha ha main hamra kuch kat nhi rha to aise hi to ab banao ache se poora`

Six screenshots showed a blurred full-frame background, a sharp uncut human viral clip, a centered two-line color-split hook, visible `1.`–`7.` plates/labels, right platform UI, a caption bubble, Subscribe and bottom app chrome. V6 had a large black empty upper half, a boxed tiny list, CC0 animal-only clips and a V6 crop routine. Its `49/49` technical checks, `9/9` audio gates, safe-area/social-origin checks, CI success and GitHub download link are **not** creative approval.

V3/V4/V5/V6 are rejected. V5 is untouched. The V6 MP4 stays in the repo as evidence of the rejected build, not as a deliverable to re-present.

## Active V7 task

- Real social-origin viral/funny clips, new or old both allowed, with objective best hooked/engaging windows selected from the clips.
- Full 60.0s / 1800-frame / 30fps / 1080x1920 ranking built on those scenes.
- Exact reference-style ranking layout: blurred full-frame background plus sharp **uncut** source frame; no V6 crop routine, no zoom, no black empty top, no letterbox.
- Centered two-line `Ranking Most Impressive / Moments Ever` hook, all seven rank numbers and labels visible from the first frame, right platform UI, `@Monarch-Cam`, comment bubble, Subscribe, bottom caption and app chrome.
- Raw per-window native source audio only; no narration, music, SFX, bed, generated calls or added layers.
- Upload the **new V7 MP4** to GitHub and give its own direct download link. V6's link does not satisfy this task.

## Rights boundary

The user asked for `📈 trending viral videos` and clips from `TikTok Instagram yt or Reddit Dailymotion`. Unverified currently trending reposts from those platforms have no rights record and are not downloaded. V7 uses **ten rights-cleared social-origin Wikimedia Commons mirrors** of older YouTube/Vimeo/SWNS/police viral clips. CI verifies each selected title through Commons API extmetadata, allowed PD/CC BY 3.0 licence, creator, Credit/Categories social origin and original SHA-1; CC BY attribution is recorded. Commons metadata is a rights record, not a legal opinion. No current-trending claim, no exact reference-clip claim, no unverified repost, and no full legal-compliance claim is made.

Two CC BY 3.0 YouTube comedy candidates whose Commons descriptions contained third-party copyright language were removed from the pool. `License review needed (video)`, Mr Bean excerpts, baby-elephant compilations with music/fair-use disclaimers, unverified social reposts and CC BY-SA/CC BY-NC/fair-use-only substitutes remain excluded.

## V7 package

- `production/monarch-cam/short_ranking_raw_v7/` — renderer, spec, metadata, credits, candidate sources, rights verifier, source recon, audio audit/builder, technical QC and plan.
- `.github/workflows/monarch-cam-short-ranking-viral-v7.yml` — build/QC workflow with narrow push paths and `[skip ci]` commit-back.
- `deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_VIRALSTYLE_V7.mp4` — new V7 deliverable path.

## No acceptance claim

This is a technical build for human review. No human full-motion/native-audio listening, creative approval, sign-off, perfection, retention, virality, 3x, subscribe/like, same-path replacement or audience result is claimed.

After the V7 CI run succeeds: inspect the new MP4, `review/qc_summary.json`, `review/technical_qc.json`, sampled frames and rights/source ledgers; record the result with `checkpoint`; update `CHANNEL_STATE.json` / `STATE.json`; run `refresh`, `render`, `validate`, `render --check`; commit/push on `arena/2b012328-monarch-overall-work`; then give the V7 download link. If the user again rejects the result, record the exact reason and build a separate V8 lane; do not modify V5 or re-present V4/V5/V6 as final.

## Current CI status — 2026-11-09

- First V7 CI run `42541601536` failed at the per-title Commons rights ledger because the API key `Restrictions` was checked as lowercase `restrictions`. Fixed and CI-verified in the retry.
- Slow run `42542753775` used the unoptimized renderer and was cancelled at `2026-11-09T01:48:07Z` after `cancel-in-progress: true` and the cached-UI renderer were pushed.
- Optimized run `42547437901` completed `failure` in 12m12s: the visual render succeeded in 2m22s, but the native-audio/mux step failed because all 16 measured gain/mastering combinations failed the unchanged `lra_in_range` web gate. Long digital-silence blocks inside selected source windows produced LRA about `87-89 LU` and movement about `225-229 dB`. No artifact, committed MP4, QC, hash or download link exists.
- Diagnostic run `42559696919` succeeded. The probe, selection, audit, audio builder and technical QC now require every complete 0.5-second block of each selected native window to exceed the unchanged `-65 dBFS` threshold; the nine web gates are unchanged and no audio is added or substituted. All seven selected windows have 17 continuous blocks and zero quiet blocks.
- Full CI run `42560161988` rendered and muxed a runner-only MP4 and passed all nine unchanged web audio gates, but technical QC stopped on a missing `blurred_background_fill` key in the renderer's visual QC ledger. The renderer now records that flag, sampled-frame metrics are logged, and failure evidence can be uploaded. No gate or threshold was weakened.
- Full CI retry `42561159698` again passed all nine web audio gates. Technical QC correctly failed three sampled-frame black-area checks because dark source windows made the blurred full-frame background near-black in frames 630/810/990. The renderer now lifts only the blurred background above near-black; the sharp source frame remains uncut and all QC thresholds stay unchanged. A local black-frame simulation passes every sampled-frame threshold.
- Next: trigger the clean full V7 CI retry, watch it to completion, inspect the committed MP4/contact sheets/QC/rights ledgers, then give only the V7 GitHub download link. No human full-motion/native-audio review or creative acceptance exists yet. Do not give a V4/V5/V6 link.
