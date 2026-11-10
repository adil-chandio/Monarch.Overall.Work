## 2026-11-05 addendum - V11 Phase A/B kickoff (work started, NO render)

- `production/monarch-cam/replay_lab_ep01_v11/`: Phase A source audit + Phase B script draft v0 (12 chapters, 3 hooks, 714 VO words, 15 sources). Generator is idempotent; `RESULT: ALL PASS`.
- New first-party physics source: NASA *Bubbly Chiao* confirms the inverted image is refraction (air to water); NASA FLUTE confirms surface tension. 13/13 evidence JSONs parse; NASA ID / master SHA / V10 Short SHA re-verified unchanged.
- **3 open items:** (1) 16:9 source - local master is `1080x1920` vertical, original 4K not present locally; (2) render/QC toolchain (ffmpeg/ffprobe/numpy/v10_deps) absent in this snapshot; (3) NASA promotional rights gate + user-reported Short monetization ON, `human_legal_review=false`, `commercial_monetization_clearance=false`.
- NO video, NO VO synthesis, NO captions burned, NO render, NO upload/publish, NO monetization change, NO human approval, NO legal clearance, NO guaranteed result. Does NOT supersede the standing human full-motion/native-audio review line below.
- Awaiting user: hook choice (default H1), script approval, voice audition (Phase C), 16:9 source strategy.

## 2026-11-05 addendum - V11 long-form idea selection (idea only, NOT a build)

- New study: `research/long_form_viral_idea_v11/LONG_FORM_VIRAL_IDEA_FORENSIC_STUDY_V11.md`.
- One idea selected: `REPLAY LAB Ep.1 - The Upside-Down Face` (weighted 93.3/100).
- NO video rendered, NO upload/publish, NO YouTube Data API call (no key in workspace), NO rights clearance, NO human approval and NO guaranteed result. The V10 NASA promotional / current-astronaut imagery gate remains OPEN.
- This addendum does NOT supersede the standing 'await human full-motion/native-audio review' line above; it only records that a NEW long-form idea-selection task happened after it.

# Exact next action — Monarch Cam

**Single next action:** await human full-motion/native-audio review of the committed clean V8 MP4 link. Do **not** ask the user again for reference screenshots/clips, do **not** re-present V4/V5/V6/V7, and do **not** claim creative acceptance.

Clean V8 deliverable: `deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_CLEAN_V8.mp4`

Direct download: `https://github.com/adil-chandio/Monarch.Overall.Work/raw/arena/2b012328-monarch-overall-work/deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_CLEAN_V8.mp4`

## Why V7 is not the answer

The user rejected V7 after its GitHub link: `Aby yeh clean Karna itna kuch q bhar rakha ha main content to Nazar hi nhi arha ha yeh sab hatana ...`. Its two-line hook, seven-row list, right platform UI, handle, comment bubble, Subscribe, bottom caption and app chrome accumulated over the footage. Outer phone/gallery player chrome (`0:00/1:00`, status bar, central play button, scrub bar) is **not** part of the MP4 and cannot be removed from it; the baked-in overlays were the actual problem.

V7's `65/65` technical checks, `9/9` audio gates, CI `42562287554`, committed MP4 and GitHub link are **not** creative approval. V4/V5/V6/V7 remain rejected.

## Clean V8 build — 2026-11-09

- Separate package: `production/monarch-cam/short_ranking_clean_v8/`
- Workflow: `.github/workflows/monarch-cam-short-ranking-clean-v8.yml`
- Successful main CI: `42653605976` / job `129286160076`, commit-back `9b18446`
- MP4: `22,459,082` bytes, SHA-256 `1c44fb345f3f8582ee22b6c333c39050968669b8f6fc0012d9a5b56b3d03e1e7`, `60.0s` / `1800` frames / `30fps` / `1080x1920`
- Technical QC: `68/68` checks; unchanged nine web audio gates: `9/9`; seven continuous raw per-window native audio segments, zero quiet half-second blocks; per-title Commons API rights/social-origin/SHA-1/restrictions ledgers committed.
- Visual: blurred ambient-lifted full-frame background plus sharp **uncut** source frame; only a slim `7→1` top rank strip, a small bottom-left moment badge and a thin progress line remain. V7 hook/list/right UI/handle/comment/Subscribe/caption/chrome are removed. Minimal UI sits outside the central main-content region; overlay area stays under `6%`.
- After the first clean render, committed contact sheets showed rank 6 opening on a black fade-in and rank 5 on a static `Guión Original` title card. Those cuts were moved to `3.0s` and `80.0s` respectively, where the actual gags are visible. Each override was re-checked against the runner's own half-second RMS probe; the source audio audit and nine unchanged web gates re-verified the final mux.

## Reference boundary

The referenced Short is `https://youtube.com/shorts/08-ocSDpt7o?si=5F7y2w9H6Sso5bQK` (`onlymeamro`, `Ranking Most Impressive Moments Ever #shorts`, 60s). Metadata, title, author, thumbnail URL and public counts were retrieved, but real frames, full motion and audio were not playable/extractable in this environment. The user then answered `Aby tujhe Karna ha kese bhi Kar Jo kar Lekin kR` and refused further frame requests. V8 therefore proceeds as a clean content-first build with **no exact-reference-match claim**. Exact reference clips, exact pacing/typography/transitions and full creative sign-off remain unknown.

## Rights boundary

The user's exact rights-cleared currently trending TikTok/Instagram/YouTube/Reddit/Dailymotion clips remain unmet. V8 uses older per-title verified Wikimedia Commons social-origin mirrors with attribution/restrictions and original SHA-1 checks. No current-trending claim, exact-reference-clip claim, unverified repost, full legal compliance, human native-audio listening, creative approval, sign-off, perfection, retention, virality, 3x, likes/subscribes, same-path replacement or audience result is claimed.

## No acceptance claim

Successful CI, sampled frames, contact sheets, technical QC and audio gates are objective records only. Human full-motion/native-audio review and creative approval are still pending.
