# Monarch Cam rejections and dead ends — do not retry blindly

## Creative rejection

- **V4** ranking Short: user said **“sirf text likh diya”**.
- **V5** ranking Short: user said **“NAHI abhi bhi theek se nhi”** plus four screenshots.
- Technical V5 delivery at `393edd658e8336780e1cd4aea4cf5b5261c2d1e3` is **not** creative acceptance.
- V5 QC `40/40` technical, `9/9` audio, `47/47` summary flags are not approval. Human/listening/sign-off/outcome flags remain false.
- Do not re-present V4/V5 as final, claim done, or treat a commit-pinned MP4 as approval.

## V5 geometry

- `review/cover_hook.jpg` shows V5 hook lines/question occluded by the `1.–7. LIST`.
- `render_ranking_visual_raw_v5.py` uses centered 104pt hook lines `y=300+150i`, question 72pt `y=800`, list `(650,460)-(1040,1186)`, rank burst `(60,1430)`, reaction `(60,1080,540,150)`.
- Reference requires centered colorful top hook, fully visible left `1.–7.` black label plates, progressive labels, payoff cuts/zoom, reaction bubbles, emojis, right platform UI, bottom comment/Subscribe.
- No V5 right panel / bottom rank burst. Add safe-area/social-origin checks; `technical_qc_raw_v5.py` has none.

## Source dead ends

- `verify_sources.py` is strict CC0-only; `technical_qc_raw_v5.py` checks `seven_cc0_originals` / `api_license_verified`; `ranking_short_spec.json` `seven_cc0_sources=true` needs revision.
- Broad Commons searches mix CC BY / BY-SA / PD / FAL / silent material. `Category:CC0 videos` empty; `incategory:"CC0 videos" animal` 0.
- `Lucanus Cervus fighting.webm` has no audio / bogus 63h duration.
- Do not use unverified platform reposts / @onlymeamro footage, old Soviet cartoons, FAL Peuple Loup clips requiring attribution, silent/graphic Reddit K9/dog-wolf/pitbull clips, unverified TikTok heroic-cat, Oriental Cat Shorts, `Animals Workout Mix II`, `Adorable Animals...`, `Hutong Meow`, `Most Funny and Cute Baby Elephant...`, `African Lion funny video`, `My Chameleon is funny`, or nuanced PD/CC0-fallback Grizzly GoPro as a cleared funny platform-clip substitute.
- Rights metadata for those dead ends is preserved in `docs/continuity/PROBLEMS_FIXES.md`. No rights-cleared funny social-platform clip has been selected.

## Audio / V4 dead ends

- V3 dance renderer/audio/music/SFX/narration/native ambience are not raw moment audio. No generated sound/audio substitution.
- Old silent starfish/octopus/titmouse manifest/spec and `audio_codec:null` must not return.
- `Helostoma temminkii kissing.ogv` effectively silent.
- Two-pass/dynamic/linear/TP/limiter variants failed; delivered-AAC calibration with `alimiter=0.75` was selected for V4. `ffmpeg adeclick` hung >5m; bounded interpolation selected.
- `oriental_dove` upstream HTTP 429/robot policy resolved by cache/backoff/original CC0 URLs.
- Failed runs `42396617606`, `42397191709`, `42399953907`, `42401006868`, `42401490506`, `42402744112`, `42403697302` and their fixes are in `PROBLEMS_FIXES.md`.

## V6 is a technical build, not acceptance

- A separate V6 package is built with seven per-title CC0 Commons originals, corrected centered hook / left `1.–7.` plates, right UI, bottom bar, safe-area and social-origin QC, renderer and workflow. CI run `42517651544` succeeded, but the user rejected V6 after its GitHub upload/link; do not re-present it.
- V6 does **not** use unverified real social-platform reposts; the earlier `NEXT_ACTION.md` requirement for social-platform clips is not claimed resolved.
- V6 MP4 and CI run exist. Do not claim V6 is accepted, approved, watched in full motion, listened to by a human, or proven with audience results until a real record exists.
- V5 is untouched and V4/V5/V6 remain rejected.

## Channel-strategy dead ends

- Do not delete Monarch Cam, mass-delete old videos, re-upload the 25-view ranking repeatedly, buy engagement, run random daily uploads, copy animal collision/harm, use `Part 2/3/4` as main package, treat credit/Section 107 as clearance, blame the AI label without evidence, or change five variables and call it an algorithm mystery.
- Do not claim About text alone caused 25 views or that a shadowban exists without Studio evidence.
- Do not claim human approval, full-motion/native-audio listening, sign-off, perfection, retention, virality, revenue or audience results.

## Stale workspace

- A stale checkout can show old commit `ac3a529...`, modified `.gitignore`, and untracked V3/dance-clean drafts while missing continuity files. Back up untracked drafts to `/tmp`, restore `.gitignore`, `git clean -fd -e deliverables`, explicit-refspec fetch, then `git merge --ff-only`. See `RECOVER.md` and `python3 tools/continuity.py recover`.
- `/tmp`, `google_drive/`, `tmp_chat_evidence/` and connector staging are not canonical repo truth.

## V6 rejection / V7 active task — 2026-11-09

- V6 was rejected after its GitHub upload/download-link answer: `Yeh Kya chutiyapa banaya ha NAHI abhi bhi theek se nhi ...` plus six reference screenshots. Technical QC, 49/49 checks, 9/9 audio gates, CI success and V6 links are **not** creative acceptance.
- The user wants `📈 trending viral videos` / social-platform clips, `viral ke sath sath purani bhi chalenge`, `bas clips mazedar next level honi chaiye`, the best hooked/engaging scenes extracted, and a full 60s ranking built on them. The reference screenshots show `ranking list kese lagi ha sab kuch visible horha ha main hamra kuch kat nhi rha`: full-screen uncut clip, visible hook, all 1.-7. list items, right UI, caption bubble, Subscribe and bottom chrome.
- V7 is a separate package at `production/monarch-cam/short_ranking_raw_v7/` with workflow `.github/workflows/monarch-cam-short-ranking-viral-v7.yml` and deliverable `deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_VIRALSTYLE_V7.mp4`.
- Rights boundary: ten rights-cleared social-origin Commons mirrors; per-title Commons API extmetadata, original SHA-1, Credit/Categories social origin and CC BY attribution; no unverified currently trending TikTok/Instagram/Reddit/Dailymotion/YouTube reposts, no current-trending claim, no legal opinion.
- Visual boundary: blurred full-frame background plus sharp uncut source frame; no V6 crop routine, no zoom, no black empty top, no letterbox; all seven labels visible from the first frame.
- No V7 MP4, QC, download link, human full-motion/native-audio listening, creative approval, sign-off, perfection, retention, virality or audience result is claimed yet. V4/V5/V6 stay rejected; V5 untouched.

## V7 — 2026-11-09

- **Status:** rejected after the GitHub download link was given.
- **Evidence:** `docs/continuity/evidence/screenshots/V7_rejection_20261109-191249.png`.
- **Reason:** `Aby yeh clean Karna itna kuch q bhar rakha ha main content to Nazar hi nhi arha ha yeh sab hatana ...` — too many overlays; main content not visible; user wants a clean build matching the referenced Short exactly.
- **Reference:** `https://youtube.com/shorts/08-ocSDpt7o?si=5F7y2w9H6Sso5bQK` (`onlymeamro`, `Ranking Most Impressive Moments Ever #shorts`, 60s).
- **Rule:** V7 technical QC, 65/65 checks, 9/9 audio gates, CI success, committed MP4 and GitHub link are not creative approval. V4/V5/V6/V7 remain rejected. V8 is a separate clean lane; do not reuse exact reference clips without rights/permission. The user refused further requests for reference frames, so V8 was built clean/content-first with no exact-reference-match claim.

## Clean V8 — built, not approved — 2026-11-09

- **Status:** `v8_clean_build_committed_human_review_pending`.
- **CI:** `42653605976` / job `129286160076` succeeded; commit-back `9b18446`.
- **Deliverable:** `deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_CLEAN_V8.mp4`, `22,459,082` bytes, SHA-256 `1c44fb345f3f8582ee22b6c333c39050968669b8f6fc0012d9a5b56b3d03e1e7`.
- **Visual correction:** V7 clutter removed; minimal `7→1` strip, moment badge and progress line only. Two windows moved off a black fade-in and a static title card after contact-sheet review.
- **Not claimed:** exact reference frames/full motion, exact match, exact rights-cleared currently trending named-platform clips, full legal compliance, human full-motion/native-audio listening, creative approval, sign-off, perfection, retention, virality, 3x, likes/subscribes, same-path replacement or audience result.
- **Rule:** V8 technical QC `68/68`, `9/9` audio gates, CI success, committed contact sheets and GitHub link are objective records, **not** creative acceptance.
