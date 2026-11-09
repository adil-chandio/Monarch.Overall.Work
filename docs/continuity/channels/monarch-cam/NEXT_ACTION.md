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

- First V7 CI run `42541601536` failed at the per-title Commons rights ledger because the API key `Restrictions` was checked as lowercase `restrictions`. That contract is fixed.
- Second V7 CI run `42542753775` passed source verification but its renderer was too slow (about `5.6 s/frame` locally), so an optimized cached-UI renderer (~`0.13 s/frame`) is being pushed with workflow `cancel-in-progress: true` to supersede the slow run.
- No V7 MP4, QC, download link, human full-motion/native-audio review or creative acceptance exists yet. Do not give a V4/V5/V6 link.
