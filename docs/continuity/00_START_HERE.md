# 00 · START HERE — new chat / crash recovery

**Do not ask the user to re-explain old work.** The repo already contains the latest state, evidence, decisions, prompts, results, problems and fixes.

## First command

```bash
python3 tools/continuity.py resume
```

This validates the archive and prints the exact copy-paste bootstrap prompt with the current HEAD pinned. If validation fails, fix the archive before doing new production work.

## Current snapshot

- Repo: `adil-chandio/Monarch.Overall.Work`
- Active branch: `arena/390292fc-monarch-overall-work`
- Head at capture: `393edd658e8336780e1cd4aea4cf5b5261c2d1e3`
- Five spaces: `yt-automation`, `monarch-studio`, `personal-brand`, `portfolio`, `ops` (`config/spaces.json`).
- Three channels: Monarch Lab, Mindful Momentum, Curious Miles (`config/channels.json`).
- Active continuity task: repo-backed continuation archive implemented; **real Arena chat exports still need to be dropped into `chat_exports/inbox/` and imported** to close the exactness gap.
- Parallel video task: V4 and V5 ranking Shorts are **creatively rejected**. No V6 package, workflow, rights-cleared funny social-platform clip set, renderer, QC contract or MP4 exists. Do not re-present V4/V5 as final.

## Exact reading order

1. Root `AGENTS.md`.
2. This file, then `NEW_CHAT_PROMPT.md`.
3. `STATE.json` / `STATE.md`.
4. `MINDSET.md`, `WORK_LEVELS.md`.
5. `DECISION_LOG.jsonl`, `PROMPT_RESULT_LOG.jsonl`, `PROBLEMS_FIXES.md`.
6. `COVERAGE.json`, `GAPS.md`.
7. `SESSION_INDEX.json` and the active `sessions/*.md` file.
8. `EVENTS.jsonl` tail / `TIMELINE.md`.
9. `EVIDENCE_MANIFEST.json` and the linked evidence files.
10. `config/spaces.json`, `config/channels.json`, `config/repos.json`, `docs/architecture/`.

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
  --evidence-level repo_evidence --ref path/to/evidence
```

Then update `STATE.json`, `render`, `validate`, `render --check`, commit and push. Full protocol: `UPDATE_PROTOCOL.md`.
