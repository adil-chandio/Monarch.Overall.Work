# Monarch Cam evidence — exact commits, runs, hashes and source docs

## Branch / continuity commits

- Active branch: `arena/2b012328-monarch-overall-work`.
- Pre-continuity head / V5 static docs: `393edd658e8336780e1cd4aea4cf5b5261c2d1e3`.
- Continuity pack commit: `a8596fa869df50593270ed53b39a11f2bc8ca0e0`.
- Exact-state commit: `4b3574c1c936e47cf2a68d719bae0e9fe6a2380a`.
- Pack CI success: `42499227414` — https://github.com/adil-chandio/Monarch.Overall.Work/actions/runs/42499227414
- Final-state CI success: `42499591071` — https://github.com/adil-chandio/Monarch.Overall.Work/actions/runs/42499591071

## Video commits / runs

- V3: `2ec267126ef64790cd3cd38b30362c0a4b849594`; build `410095112`; gate `221b897…`; success `42383560080`; artifact `13579076898`.
- V4: `331eafbf64af770eb451e6967a3eaab3a9bbbb39`; final run `42404195062` / `128498253881`; artifact `13587220215`.
- V5: `[skip ci] 8fc1dcd203a7662a0f662cbb56f816276ec1a0fa`; success `42430602404`; artifact `13597706464`; `37,855,740` bytes; `expired=false`. Static fixes `393edd6`.
- V5 diagnostics/fixes: `ff52bd9`, `f5c1c6f`, `f0a92fb`, `14ef4a2`, `27b0a44`, `ff8aa55`, `99f4548349ee6213315d01d97587673c204f9c20`.
- No run after `393edd6` for V5. V6 run `42516794773` failed at `Nine web audio gates` (exit 2, module invoked with no CLI args); fixed and succeeded in run `42517651544`.

## Deliverables

- V5 MP4: `deliverables/MONARCH_CAM_7_Unexpected_Animal_Moments_Ranked_60s_Short_RAW_FULLSCREEN_V5.mp4`, `28,043,097` bytes, SHA-256 `8948f67f4ab0fb419fd1d53a10f1db68a0c6848347aa80961a1a607f9806306a`; `60.0s`, `1080x1920`, `30fps`, `1800` frames; seven moments; durations `[9,9,9,9,9,4,11]`s; ranks `[7,6,5,4,3,2,1]`.
- V4 MP4: `deliverables/MONARCH_CAM_5_Unexpected_Animal_Skills_Ranked_35s_Short_RAW_FULLSCREEN_V4.mp4`, `57,405,096` bytes, SHA-256 `2bc12b0bc0422c93b401b0af67499dba3a034584abbe15e3712f51f7f994af28`.
- V3 MP4 preserved: `deliverables/MONARCH_CAM_5_Unexpected_Animal_Skills_Ranked_35s_Short_CLEAN_PREMIUM_V3.mp4`, `31,930,639` bytes.
- V6 technical package built at `production/monarch-cam/short_ranking_raw_v6/`, CI run `42517651544` / workflow commit `5559b52`; subsequently rejected by the user after its GitHub upload/link. Its QC and download links are not creative acceptance. A separate V7 package is configured at `production/monarch-cam/short_ranking_raw_v7/` with `.github/workflows/monarch-cam-short-ranking-viral-v7.yml`; no V7 MP4, QC or download link exists yet.

## V5 QC (technical, not acceptance)

- `review/technical_qc.json`: `passed=true`, 40 checks, no failures.
- `review/audio_qc.json`: `pass=true`, 9/9 web gates, `failed=[]`.
- `review/qc_summary.json`: 47/47 flags true; human/full-motion/listening/sign-off and outcome/AI/audio-layer false flags remain false.
- Static metadata runner flags intentionally false pre-build. No human full-motion/native-audio listening, approval, sign-off, perfection, retention, virality or audience-result claim.

## V5 source package

- `production/monarch-cam/short_ranking_raw_v5/ranking_short_spec.json`
- `production/monarch-cam/short_ranking_raw_v5/candidate_sources.json` — 11 CC0 assets.
- `production/monarch-cam/short_ranking_raw_v5/review/selected_windows.json`
- `production/monarch-cam/short_ranking_raw_v5/review/qc_summary.json`
- `production/monarch-cam/short_ranking_raw_v5/review/technical_qc.json`
- `production/monarch-cam/short_ranking_raw_v5/review/audio_qc.json`
- `production/monarch-cam/short_ranking_raw_v5/review/native_audio_ledger.json`
- `production/monarch-cam/short_ranking_raw_v5/CREDITS.md`
- `production/monarch-cam/short_ranking_raw_v5/RANKING_V5_PLAN_AND_METADATA.md`

## V6 technical package (configured, MP4/run pending)

- `production/monarch-cam/short_ranking_raw_v6/ranking_short_spec.json`
- `production/monarch-cam/short_ranking_raw_v6/CREDITS.md`
- `production/monarch-cam/short_ranking_raw_v6/RANKING_V6_PLAN_AND_METADATA.md`
- `production/monarch-cam/short_ranking_raw_v6/ranking_v6_metadata.json`
- `production/monarch-cam/short_ranking_raw_v6/candidate_sources.json`
- `production/monarch-cam/short_ranking_raw_v6/review/selected_windows.json`
- `production/monarch-cam/short_ranking_raw_v6/verify_sources.py`
- `production/monarch-cam/short_ranking_raw_v6/source_recon_ranking.py`
- `production/monarch-cam/short_ranking_raw_v6/source_audio_audit.py`
- `production/monarch-cam/short_ranking_raw_v6/render_ranking_visual_raw_v6.py`
- `production/monarch-cam/short_ranking_raw_v6/build_ranking_audio_raw_v6.py`
- `production/monarch-cam/short_ranking_raw_v6/technical_qc_raw_v6.py`
- `production/monarch-cam/short_ranking_raw_v6/validate_raw_v6.py`
- `.github/workflows/monarch-cam-short-ranking-raw-v6.yml`

Generated V6 evidence: `review/social_origin_ledger.json`, `review/layout_manifest.json`, `review/source_video_ledger.json`, `review/source_audio_audit.json`, `review/native_audio_ledger.json`, `review/audio_qc.json`, `review/technical_qc.json`, `review/qc_summary.json` and the V6 MP4. 49/49 technical checks, 9/9 audio gates, safe-area/social-origin checks passed; human/listening/approval/sign-off flags remain false.

## Channel source documents

- `docs/MONARCH_CAM_LIVE_FORENSIC_AUDIT_2026-11-05.md` — live channel, videos, brand, audit, what not to do, final diagnosis.
- `docs/MONARCH_CAM_30_DAY_GROWTH_REVENUE_PLAN_2026-11.md` — objective, November calendar, series, Shorts, foundation, rights/AI gate.
- `docs/MONARCH_CAM_PERMISSION_FREE_BEAR_FOOTAGE_PLAN_2026-11.md` — NPS PD source pack, CPW research-only note, originality standard.
- `config/channels.json` — three legacy publishing slots; see reconciliation gap.
- `docs/continuity/PROBLEMS_FIXES.md` — all failed runs, source rights metadata and stale-checkout recovery.
- `docs/continuity/WORK_LEVELS.md`, `MINDSET.md`, `GAPS.md`, `STATE.json`, `COVERAGE.json`.

## Live audit metrics (historical, not outcome promises)

- Original 2024 bear video: `952,975` views in 3 October report → `959,920` live on 5 November; `+6,945` in 33 days (~210/day).
- Newest long video: `25 views / 0 public likes after 39 days`.
- Newest Short: `3 views after 13 days`.
- 7 September Short: `5.8K views / 126 likes`.
- Long-form gaps before latest upload: approximately `250 days` and `357 days`.
- Brand contradiction: channel `Monarch Cam`, About `KARMA CAM`, January 2026 bear video `Daily Dose of Smiles`.
- Studio screenshots for latest long and three recent Shorts still needed to determine impressions / CTR / first-30-second retention / Shorts swipe bottleneck.

## V6 rejection / V7 active task — 2026-11-05

- V6 was rejected after its GitHub upload/download-link answer: `Yeh Kya chutiyapa banaya ha NAHI abhi bhi theek se nhi ...` plus six reference screenshots. Technical QC, 49/49 checks, 9/9 audio gates, CI success and V6 links are **not** creative acceptance.
- The user wants `📈 trending viral videos` / social-platform clips, `viral ke sath sath purani bhi chalenge`, `bas clips mazedar next level honi chaiye`, the best hooked/engaging scenes extracted, and a full 60s ranking built on them. The reference screenshots show `ranking list kese lagi ha sab kuch visible horha ha main hamra kuch kat nhi rha`: full-screen uncut clip, visible hook, all 1.-7. list items, right UI, caption bubble, Subscribe and bottom chrome.
- V7 is a separate package at `production/monarch-cam/short_ranking_raw_v7/` with workflow `.github/workflows/monarch-cam-short-ranking-viral-v7.yml` and deliverable `deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_VIRALSTYLE_V7.mp4`.
- Rights boundary: ten rights-cleared social-origin Commons mirrors; per-title Commons API extmetadata, original SHA-1, Credit/Categories social origin and CC BY attribution; no unverified currently trending TikTok/Instagram/Reddit/Dailymotion/YouTube reposts, no current-trending claim, no legal opinion.
- Visual boundary: blurred full-frame background plus sharp uncut source frame; no V6 crop routine, no zoom, no black empty top, no letterbox; all seven labels visible from the first frame.
- No V7 MP4, QC, download link, human full-motion/native-audio listening, creative approval, sign-off, perfection, retention, virality or audience result is claimed yet. V4/V5/V6 stay rejected; V5 untouched.
