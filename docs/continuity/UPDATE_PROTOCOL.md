# Update protocol — keep the latest state from disappearing

The user's specific pain: a chat stops mid-work; after refresh/“continue” it restarts from the beginning, or the latest running task disappears and an older task appears. This protocol makes the repo the stable state carrier.

## After every meaningful step

1. **Append an event** (prompt, result, decision, problem, fix, state change, artifact, or rejected option):

   ```bash
   python3 tools/continuity.py checkpoint \
     --id evt-unique-id \
     --title "Exact short title" \
     --kind result \
     --space yt-automation \
     --evidence-level repo_evidence \
     --details "What changed, why, result, problems/fixes, exact IDs" \
     --ref path/to/file-or-evidence \
     --status "active status" \
     --next-action "Exact next action"
   ```

2. **Update `STATE.json`** when the active task, status, next action, claims, or gaps change. Keep one `active_task`; keep unresolved parallel work in `parallel_task`. Never silently delete old state.

3. **Update `DECISION_LOG.jsonl`** for a new user choice or rejection. Include rejected options.

4. **Update `PROMPT_RESULT_LOG.jsonl`** for a consequential prompt/result pair. Mark `exact_text_confidence` honestly.

5. **Update `PROBLEMS_FIXES.md`** for a new failure/dead end and the fix that actually worked.

6. **Refresh hashes and counts**:

   ```bash
   python3 tools/continuity.py refresh
   python3 tools/continuity.py render
   ```

   `checkpoint` now does this automatically after appending an event; run the two commands explicitly after any manual JSON/JSONL edit.

7. **Validate before push**:

   ```bash
   python3 tools/continuity.py validate
   python3 tools/continuity.py render --check
   python3 -m py_compile tools/continuity.py
   git diff --check
   ```

8. **Commit and push only on the active Arena branch**:

   ```bash
   git add AGENTS.md README.md .gitignore config/continuity.json tools/continuity.py \
     .github/workflows/continuity-validate.yml docs/continuity
   git commit -m "docs(continuity): checkpoint exact latest state"
   git push origin arena/390292fc-monarch-overall-work
   ```

CI runs `validate` and `render --check` on every push that touches the archive.

## Hourly / event-driven checkpoints

The earlier EMS-20261011-001 request asked for hourly/event-driven checkpoint packages and five-platform sync ledgers. This repo now provides:

- append-only `EVENTS.jsonl` and generated `TIMELINE.md`;
- `STATE.json` with exact `next_action`;
- `EVIDENCE_MANIFEST.json` hashes;
- `evidence/github/` snapshots of branches, PRs, runs and commits;
- `external/APP_SNAPSHOT.json` for connected-app discovery;
- `chat_exports/` for raw chat bytes.

It does **not** magically export Arena chats. A real export must be supplied/imported. Connected apps are snapshots, not live bidirectional mirrors.

## Do not

- Do not hand-edit generated `STATE.md`, `COVERAGE.md`, `SESSION_INDEX.md`, `TIMELINE.md`, `DECISION_LOG.md`, `PROMPT_RESULT_LOG.md`, `EVIDENCE_MANIFEST.md`; edit the JSON/JSONL source and run `render`.
- Do not leave unimported files in `chat_exports/inbox/`; `validate` fails on them.
- Do not set a claim to `true` without a verbatim acceptance/result record.
- Do not switch, rename, or push another branch.
- Do not remove old sessions, rejected options, failed runs or dead-end notes to make the archive look tidy.
