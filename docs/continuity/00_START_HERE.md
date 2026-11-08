# 00 · START HERE — new chat / crash recovery

**Do not ask the user to re-explain old work.** The repo already contains the latest state, evidence, decisions, prompts, results, problems and fixes.

## First command

```bash
python3 tools/continuity.py resume
```

This validates the archive and prints the exact copy-paste bootstrap prompt with the current HEAD pinned **and the active Monarch Cam channel capsule embedded**. If validation fails, fix the archive before doing new production work. If continuity files are missing, use root `RECOVER.md` / `python3 tools/continuity.py recover` first.

## Current snapshot

- Repo: `adil-chandio/Monarch.Overall.Work`
- Active branch: `arena/390292fc-monarch-overall-work`
- Head at capture: `393edd658e8336780e1cd4aea4cf5b5261c2d1e3`
- Five spaces: `yt-automation`, `monarch-studio`, `personal-brand`, `portfolio`, `ops` (`config/spaces.json`).
- Legacy three config slots: Monarch Lab, Mindful Momentum, Curious Miles (`config/channels.json`). Owner says **Monarch Cam is one of the three channels**; Monarch Cam is the active channel workstream with its own `@Monarch-Cam` channel and `production/monarch-cam/` tree. The mismatch is an explicit gap; legacy slots are preserved.
- **Active channel:** Monarch Cam — [channel 00_START_HERE](./channels/monarch-cam/00_START_HERE.md), `python3 tools/continuity.py channel`, [root shortcut](../../MONARCH_CAM.md).
- Active running task: Monarch Cam channel workflow is ready for easy continuation; a new chat inherits state/playbook/workflow/next action without user explanation. Infrastructure continuity archive delivered at `4b3574c1c936e47cf2a68d719bae0e9fe6a2380a`; **real Arena chat exports still need to be dropped into `chat_exports/inbox/` and imported** to close the exactness gap. Pack commit `a8596fa869df50593270ed53b39a11f2bc8ca0e0`, CI runs `42499227414` and `42499591071` succeeded.
- Parallel video task: V4 and V5 ranking Shorts are **creatively rejected**. No V6 package, workflow, rights-cleared funny social-platform clip set, renderer, QC contract or MP4 exists. Do not re-present V4/V5 as final.

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
  --space ops --branch arena/390292fc-monarch-overall-work \
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
