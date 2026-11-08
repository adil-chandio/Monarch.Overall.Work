# Continuity archive — MONARCH OS

This directory is the **repo-backed continuation memory** for `Monarch.Overall.Work`. Its purpose is that a new Arena chat can resume from the latest mindset, knowledge, experience, work level, decisions, prompts, results, problems and fixes without the user re-showing, re-doing, or re-explaining anything.

It does **not** pretend that screenshots are transcripts. Exactness is represented as evidence levels.

## The one command

```bash
python3 tools/continuity.py resume
```

`resume` validates the archive, prints the current commit-pinned bootstrap prompt, and gives the exact reading order. A new coding agent should also read root `AGENTS.md` first.

## Reading order

1. `00_START_HERE.md` — one-page crash-recovery entry.
2. `NEW_CHAT_PROMPT.md` — copy-paste prompt for a fresh Arena chat.
3. `STATE.json` / `STATE.md` — canonical latest state and active task.
4. `MINDSET.md` — how the user wants work continued and communicated.
5. `WORK_LEVELS.md` — every known work level, deliverable, rejection and result.
6. `DECISION_LOG.jsonl` / `PROMPT_RESULT_LOG.jsonl` — choices, exact prompts, results, consequences.
7. `PROBLEMS_FIXES.md` — dead ends and the fixes that actually worked.
8. `COVERAGE.json` / `GAPS.md` — what is preserved, at what evidence level, and what is missing.
9. `SESSION_INDEX.json` + `sessions/*.md` — all known chats/workflows/branches.
10. `EVENTS.jsonl` / `TIMELINE.md` — append-only chronological ledger.
11. `EVIDENCE_MANIFEST.json` + `evidence/` — hashes, screenshots, GitHub and external records.
12. `config/spaces.json`, `config/channels.json`, `config/repos.json`, `docs/architecture/` — repo structure.

## Evidence levels

| Level | Meaning |
|---|---|
| `verbatim_transcript` | Exact exported chat turns. Raw bytes are authoritative. |
| `verbatim_event_log` | Exact exported hash-chained journal/events; not a chat transcript. |
| `verbatim_source` | Raw imported transcript/export bytes before normalization. |
| `repo_evidence` | Commit, branch, PR, workflow run, or checked-in repository file. |
| `connected_app_record` | Drive/Docs/Notion/Linear/Supabase/Vercel/Gmail/Dropbox record or imported text. |
| `screenshot_only` | Visible screenshot image evidence; partial/truncated and never a full transcript. |
| `session_memory` | Condensed session-memory reconstruction; lower confidence than a transcript. |
| `state_ledger` | Machine-readable state, coverage, session index or append-only JSONL ledger. |
| `operating_contract` | Human-readable continuity contract, protocol, index or session note. |
| `archive_metadata` | Generated archive metadata, hash index or integrity manifest. |
| `gap` | Known missing source; explicitly not claimed as preserved. |

## Directory map

- `STATE.json`, `COVERAGE.json`, `SESSION_INDEX.json`, `EVENTS.jsonl`, `DECISION_LOG.jsonl`, `PROMPT_RESULT_LOG.jsonl` — machine-readable ledgers.
- `STATE.md`, `COVERAGE.md`, `SESSION_INDEX.md`, `TIMELINE.md`, `DECISION_LOG.md`, `PROMPT_RESULT_LOG.md`, `EVIDENCE_MANIFEST.md` — generated human-readable views. Run `render`, do not hand-edit.
- `sessions/` — one file per known chat/workflow/branch, with exact evidence refs.
- `chat_exports/inbox/` — drop real Arena exports here, then run `import-chat`.
- `chat_exports/sources/` — immutable raw exports plus derived normalized JSONL and metadata.
- `evidence/screenshots/` — all 29 attached PNGs with hashes and descriptions.
- `evidence/github/` — exact remote heads, tags, PRs, 452 runs, 998 commits, 18 workflows, 22 repos, 120 imported satellite continuity files.
- `evidence/external/` — Drive text imports, session logs, app snapshot, Drive index.
- `external/APP_SNAPSHOT.json` — cross-app discovery result with honest gaps.

## Update protocol

After every meaningful step in any chat:

```bash
python3 tools/continuity.py checkpoint \
  --title "Short exact title" \
  --details "What changed, why, result, problems/fixes" \
  --evidence-level repo_evidence \
  --ref path/to/evidence
```

Then update `STATE.json` if the active task/status/next action changed, run:

```bash
python3 tools/continuity.py refresh
python3 tools/continuity.py render
python3 tools/continuity.py validate
python3 tools/continuity.py render --check
```

Commit and push on the active Arena branch. CI runs the same validator.

## Import protocol

Real chat exports are the only way to upgrade a session from `session_memory`/`screenshot_only` to `verbatim_transcript`. See `IMPORT_PROTOCOL.md`. The importer preserves raw bytes, computes SHA-256, derives normalized JSONL, updates the session index, coverage, events and generated ledgers.

## Guardrails

- Do not claim a complete all-chat archive until full Arena exports are imported.
- Do not claim human approval, creative acceptance, sign-off, perfection, human full-motion/native-audio listening, retention, virality, or audience results.
- V4 and V5 `monarch-cam` ranking Shorts are rejected. Technical QC is not creative acceptance.
- Do not re-ask answered questions or reuse rejected geometry, unverified media, or dead-end fixes.
- Work only on `arena/390292fc-monarch-overall-work`; never switch, rename, or push another branch.
