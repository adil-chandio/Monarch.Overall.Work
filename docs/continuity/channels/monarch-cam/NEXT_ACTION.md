# Exact next action — Monarch Cam

**Single next action:** obtain 2–3 screenshots or a short clip from the user's referenced YouTube Short, then build a separate clean V8 lane that matches those frames exactly. Do **not** re-present V4, V5, V6 or V7. Do **not** ask the user to explain the channel, the rejection, or the workflow again.

## Why V6 is not the answer

The user rejected V6 after its GitHub upload and download-link answer:

> `Yeh Kya chutiyapa banaya ha NAHI abhi bhi theek se nhi ... Dekho 📈 trending viral videos ko Uthao clips social media par TikTok Instagram yt or Reddit Dailymotion ... viral ke sath sath purani bhi chalenge bas clips mazedar next level honi chaiye ... un clips se bhi best perfect mazedar hooked engaging scene nikalenge ... ranking list kese lagi ha sab kuch visible horha ha main hamra kuch kat nhi rha to aise hi to ab banao ache se poora`

Six screenshots showed a blurred full-frame background, a sharp uncut human viral clip, a centered two-line color-split hook, visible `1.`–`7.` plates/labels, right platform UI, a caption bubble, Subscribe and bottom app chrome. Those accumulated overlays became the V7 clutter that the user rejected. V6 had a large black empty upper half, a boxed tiny list, CC0 animal-only clips and a V6 crop routine. Its `49/49` technical checks, `9/9` audio gates, safe-area/social-origin checks, CI success and GitHub download link are **not** creative approval.

V3/V4/V5/V6/V7 are rejected. V5 is untouched. The V6 MP4 stays in the repo as evidence of the rejected build, not as a deliverable to re-present.

## Historical V7 task (rejected)

- Real social-origin viral/funny clips, new or old both allowed, with objective best hooked/engaging windows selected from the clips.
- Full 60.0s / 1800-frame / 30fps / 1080x1920 ranking built on those scenes.
- Exact reference-style ranking layout: blurred full-frame background plus sharp **uncut** source frame; no V6 crop routine, no zoom, no black empty top, no letterbox.
- Centered two-line `Ranking Most Impressive / Moments Ever` hook, all seven rank numbers and labels visible from the first frame, right platform UI, `@Monarch-Cam`, comment bubble, Subscribe, bottom caption and app chrome.
- Raw per-window native source audio only; no narration, music, SFX, bed, generated calls or added layers.
- Upload the **new V7 MP4** to GitHub and give its own direct download link. V6's link does not satisfy this task.

## Rights boundary

The user asked for `📈 trending viral videos` and clips from `TikTok Instagram yt or Reddit Dailymotion`. Unverified currently trending reposts from those platforms have no rights record and are not downloaded. V7 uses **ten rights-cleared social-origin Wikimedia Commons mirrors** of older YouTube/Vimeo/SWNS/police viral clips. CI verifies each selected title through Commons API extmetadata, allowed PD/CC BY 3.0 licence, creator, Credit/Categories social origin and original SHA-1; CC BY attribution is recorded. Commons metadata is a rights record, not a legal opinion. No current-trending claim, no exact reference-clip claim, no unverified repost, and no full legal-compliance claim is made.

Two CC BY 3.0 YouTube comedy candidates whose Commons descriptions contained third-party copyright language were removed from the pool. `License review needed (video)`, Mr Bean excerpts, baby-elephant compilations with music/fair-use disclaimers, unverified social reposts and CC BY-SA/CC BY-NC/fair-use-only substitutes remain excluded.

## Historical V7 package (rejected)

- `production/monarch-cam/short_ranking_raw_v7/` — renderer, spec, metadata, credits, candidate sources, rights verifier, source recon, audio audit/builder, technical QC and plan.
- `.github/workflows/monarch-cam-short-ranking-viral-v7.yml` — build/QC workflow with narrow push paths and `[skip ci]` commit-back.
- `deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_VIRALSTYLE_V7.mp4` — new V7 deliverable path.

## No acceptance claim (V7 historical)

This is a technical build for human review. No human full-motion/native-audio listening, creative approval, sign-off, perfection, retention, virality, 3x, subscribe/like, same-path replacement or audience result is claimed.

## Current status — 2026-11-09

- Main V7 CI `42562287554` succeeded technically and committed the MP4/QC evidence at `47012a5`; its GitHub link was given. V7 is nevertheless **rejected** by the user.
- Rejection: the delivered frame is crowded with hook, seven-row list, right UI, handle, comment bubble, Subscribe and bottom chrome; the main content is not visible. The user wants all that removed and every element rebuilt to match the referenced 60s Short `08-ocSDpt7o` exactly.
- Reference metadata was retrieved (`onlymeamro` / `thatoneamro`, 60s, ~89.97M views), but the agent cannot play or extract frames from YouTube/TikTok in this environment. Exact clean layout is still unknown.
- Next: ask the user for 2-3 screenshots or a short clip from the reference video, then build a separate clean V8 lane from that exact visual reference. Keep verified rights-cleared sources or require a user-supplied rights-cleared clip pack/permissions. Do not re-present V4/V5/V6/V7, do not claim creative acceptance, current-trending status, full legal compliance, human listening, perfection, retention, virality or audience results.
