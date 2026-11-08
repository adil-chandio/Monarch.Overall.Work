# Repository agent contract — MONARCH OS

This repository is the source of truth. A new Arena chat must not ask the user to
re-explain old work, re-upload old screenshots, or repeat answered choices.

## Mandatory first action

```bash
python3 tools/continuity.py resume
```

That command validates `docs/continuity/`, prints the current commit-pinned
bootstrap prompt with the **active Monarch Cam channel capsule already embedded**,
and gives the exact reading order. If `AGENTS.md`, `tools/continuity.py` or
`docs/continuity/` are missing, use root `RECOVER.md` or
`python3 tools/continuity.py recover` first. Do not ask the user to explain the
channel or workflow. Read, in order:

1. `docs/continuity/channels/monarch-cam/00_START_HERE.md` (active channel)
2. `AGENTS.md`
3. `docs/continuity/00_START_HERE.md`
4. `docs/continuity/NEW_CHAT_PROMPT.md`
5. `docs/continuity/STATE.json` and `STATE.md`
6. `docs/continuity/MINDSET.md`
7. `docs/continuity/WORK_LEVELS.md`
8. `docs/continuity/DECISION_LOG.jsonl` and `PROMPT_RESULT_LOG.jsonl`
9. `docs/continuity/PROBLEMS_FIXES.md`
10. `docs/continuity/COVERAGE.json` and `GAPS.md`
11. `docs/continuity/SESSION_INDEX.json` plus the active session file
12. `docs/continuity/EVENTS.jsonl` (tail first) and `TIMELINE.md`
13. `docs/continuity/EVIDENCE_MANIFEST.json` and the linked evidence files
14. `config/spaces.json`, `config/channels.json`, `config/repos.json`, `docs/architecture/`

## Non-negotiable behaviour

- Treat **verbatim transcript** evidence as stronger than **session memory**, and session memory as stronger than **screenshot-only** evidence.
- Never claim that screenshots, summaries, or connected-app records are complete Arena chat transcripts.
- Never claim human approval, creative acceptance, sign-off, perfection, human full-motion/native-audio listening, retention improvement, virality, or audience results unless a verbatim acceptance record is imported.
- **Active channel is Monarch Cam**, one of the three channels. The repo carries its identity, strategy, rights rules, rejections, exact next action and production workflow. A new chat must not ask the user to explain them. Legacy `config/channels.json` slots are preserved; the name mismatch is an explicit gap.
- V4 and V5 of the `monarch-cam` ranking Short are explicitly rejected. Technical QC is not creative acceptance.
- Do not re-ask answered questions. Do not reuse rejected geometry, unverified media, or dead-end fixes.
- When work advances, append a checkpoint and update the state ledger:
  `python3 tools/continuity.py checkpoint --title "..." --details "..." --evidence-level repo_evidence --ref <path>`
- When the user supplies a real chat export, preserve raw bytes:
  `python3 tools/continuity.py import-chat FILE --session-id ID --title "..." --source "..." --coverage partial`
- Before pushing, run `python3 tools/continuity.py validate` and `python3 tools/continuity.py render --check`.
- Work only on the Arena session branch. Never switch, rename, or push another branch.

The continuity archive lives in `docs/continuity/`; the validator/importer is
`tools/continuity.py`; CI enforcement is `.github/workflows/continuity-validate.yml`.
