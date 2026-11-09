# 00 · START HERE — new chat / crash recovery

**Do not ask the user to re-explain old work.** The repo already contains the latest state, evidence, decisions, prompts, results, problems and fixes.

## First command

```bash
python3 tools/continuity.py resume
```

This validates the archive and prints the exact copy-paste bootstrap prompt with the current HEAD pinned **and the active Monarch Cam channel capsule embedded**. If validation fails, fix the archive before doing new production work. If continuity files are missing, use root `RECOVER.md` / `python3 tools/continuity.py recover` first.

## Current snapshot

- Repo: `adil-chandio/Monarch.Overall.Work`
- Active branch: `arena/2b012328-monarch-overall-work`
- Head at capture: `8cb1e6abf64074db6ff7bfe3dcd496594f329780`
- Five spaces: `yt-automation`, `monarch-studio`, `personal-brand`, `portfolio`, `ops` (`config/spaces.json`).
- Legacy three config slots: Monarch Lab, Mindful Momentum, Curious Miles (`config/channels.json`). Owner says **Monarch Cam is one of the three channels**; Monarch Cam is the active channel workstream with its own `@Monarch-Cam` channel and `production/monarch-cam/` tree. The mismatch is an explicit gap; legacy slots are preserved.
- **Active channel:** Monarch Cam — [channel 00_START_HERE](./channels/monarch-cam/00_START_HERE.md), `python3 tools/continuity.py channel`, [root shortcut](../../MONARCH_CAM.md).
- Active running task: Monarch Cam channel workflow is ready for easy continuation; a new chat inherits state/playbook/workflow/next action without user explanation. V6 was rejected after its GitHub download link; the separate V7 viral-style ranking task is active. V6 technical QC and links are not creative acceptance. Infrastructure continuity archive delivered at `4b3574c1c936e47cf2a68d719bae0e9fe6a2380a`; **real Arena chat exports still need to be dropped into `chat_exports/inbox/` and imported** to close the exactness gap. Pack commit `a8596fa869df50593270ed53b39a11f2bc8ca0e0`, CI runs `42499227414` and `42499591071` succeeded.
- Parallel video task: V4 and V5 ranking Shorts are **creatively rejected**. V6 is a separate built technical package with per-title CC0 Commons originals, not unverified social-platform reposts. V6 MP4 and CI run exist; do not re-present V4/V5 as final or claim V6 approval.

## Exact reading order

1. `channels/monarch-cam/00_START_HERE.md`, `CHANNEL_STATE.json`, `NEXT_ACTION.md`, `PLAYBOOK.md`, `WORKFLOW.md`, `EASY_RESUME.md`.
2. Root `AGENTS.md`, `RECOVER.md`, `MONARCH_CAM.md`.
3. This file, then `NEW_CHAT_PROMPT.md`.
4. `STATE.json` / `STATE.md`, `CHANNEL_INDEX.md`.
5. `MINDSET.md`, `WORK_LEVELS.md`.
6. `DECISION_LOG.jsonl`, `PROMPT_RESULT_LOG.jsonl`, `PROBLEMS_FIXES.md`.
7. `COVERAGE.json`, `GAPS.md`.
8. `SESSION_INDEX.json` and the active session file.
9. `EVENTS.jsonl` tail / `TIMELINE.md`.
10. `EVIDENCE_MANIFEST.json` and the linked evidence files.
11. `config/spaces.json`, `config/channels.json`, `config/repos.json`, `docs/architecture/`.

## What must not happen

- No “sab kuch push ho gaya / everything is preserved” claim while `COVERAGE.json` says the full Arena export is missing.
- No treating a screenshot, session memory, Drive session log, Linear description, or Notion page as a verbatim Arena transcript.
- No re-asking choices already recorded in `DECISION_LOG.jsonl`.
- No reusing V5 hook/list geometry, strict CC0-only assumption, unverified platform reposts, silent/graphic clips, or `Lucanus Cervus fighting.webm`.
- No claim of approval, perfection, human listening, audience retention, virality, sign-off, or results.
- No switching away from the active Arena branch.

## If a chat export arrives

```bash
python3 tools/continuity.py import-chat docs/continuity/chat_exports/inbox/FILE \
  --session-id UNIQUE_ID --title "Exact chat title" \
  --source "Arena export" --coverage complete \
  --evidence-level verbatim_transcript \
  --space ops --branch arena/2b012328-monarch-overall-work \
  --notes "Full export supplied by user."
```

Use `--coverage partial` unless the file is genuinely the complete chat. Then `refresh`, `render`, `validate`, commit and push.

## If work advances

```bash
python3 tools/continuity.py checkpoint --title "..." --details "..." \
  --evidence-level repo_evidence --ref path/to/evidence \
  --status "..." --next-action "..."
```

`checkpoint` appends the event, updates `STATE.json`, refreshes hashes/coverage and renders ledgers automatically. Then run `validate`, `render --check`, commit and push. Full protocol: `UPDATE_PROTOCOL.md`.

## V6 rejection / V7 active task — 2026-11-09

- V6 was rejected after its GitHub upload/download-link answer: `Yeh Kya chutiyapa banaya ha NAHI abhi bhi theek se nhi ...` plus six reference screenshots. Technical QC, 49/49 checks, 9/9 audio gates, CI success and V6 links are **not** creative acceptance.
- The user wants `📈 trending viral videos` / social-platform clips, `viral ke sath sath purani bhi chalenge`, `bas clips mazedar next level honi chaiye`, the best hooked/engaging scenes extracted, and a full 60s ranking built on them. The reference screenshots show `ranking list kese lagi ha sab kuch visible horha ha main hamra kuch kat nhi rha`: full-screen uncut clip, visible hook, all 1.-7. list items, right UI, caption bubble, Subscribe and bottom chrome.
- V7 is a separate package at `production/monarch-cam/short_ranking_raw_v7/` with workflow `.github/workflows/monarch-cam-short-ranking-viral-v7.yml` and deliverable `deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_VIRALSTYLE_V7.mp4`.
- Rights boundary: ten rights-cleared social-origin Commons mirrors; per-title Commons API extmetadata, original SHA-1, Credit/Categories social origin and CC BY attribution; no unverified currently trending TikTok/Instagram/Reddit/Dailymotion/YouTube reposts, no current-trending claim, no legal opinion.
- Visual boundary: blurred full-frame background plus sharp uncut source frame; no V6 crop routine, no zoom, no black empty top, no letterbox; all seven labels visible from the first frame.
- No V7 MP4, QC, download link, human full-motion/native-audio listening, creative approval, sign-off, perfection, retention, virality or audience result is claimed yet. V4/V5/V6 stay rejected; V5 untouched.

## Clean V8 — built, not approved — 2026-11-09

- **Status:** `v8_clean_build_committed_human_review_pending`.
- **CI:** `42653605976` / job `129286160076` succeeded; commit-back `9b18446`.
- **Deliverable:** `deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_CLEAN_V8.mp4` (`22,459,082` bytes, SHA-256 `1c44fb345f3f8582ee22b6c333c39050968669b8f6fc0012d9a5b56b3d03e1e7`).
- **Direct link:** `https://github.com/adil-chandio/Monarch.Overall.Work/raw/arena/2b012328-monarch-overall-work/deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_CLEAN_V8.mp4`
- **Visual:** V7 overlay clutter removed; only a slim `7→1` rank strip, small moment badge and thin progress line remain outside the central unobstructed content region. Sharp uncut source on ambient-lifted blurred full-frame background. Two cuts were moved off a black fade-in and a static title card after committed contact-sheet review.
- **Objective records:** `68/68` technical checks, `9/9` unchanged web audio gates, seven continuous raw native-audio windows, zero quiet half-second blocks, per-title Commons API rights/social-origin/SHA-1 ledgers.
- **Limits:** exact reference frames/full motion/audio were not obtainable; the user refused further frame requests; no exact-reference-match claim. Exact rights-cleared currently trending named-platform clips remain unmet; older verified Commons social-origin mirrors used. No full legal compliance, human full-motion/native-audio listening, creative approval, sign-off, perfection, retention, virality, 3x, likes/subscribes, same-path replacement or audience result is claimed.
- **Rule:** V4/V5/V6/V7 are rejected. V8 CI success, QC and link are objective records, not creative acceptance.
