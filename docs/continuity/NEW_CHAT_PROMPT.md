# Copy-paste prompt for a new Arena chat

Paste everything below into the new chat. `{{BRANCH}}`, `{{HEAD}}` and `{{TREE_URL}}` are filled automatically by `python3 tools/continuity.py resume`.

---

You are resuming **MONARCH OS** inside `adil-chandio/Monarch.Overall.Work`.

- Active branch: `{{BRANCH}}`
- Exact HEAD: `{{HEAD}}`
- Commit-pinned tree: {{TREE_URL}}
- Do not switch, rename, or push another branch.

**Do not ask me to re-explain, re-show, re-upload, or re-do old work.** A new chat must continue from the exact latest mindset, knowledge, experience, work level, decisions, prompts, results, problems and fixes recorded in the repo.

First run:

```bash
python3 tools/continuity.py resume
```

Then read, in order:

1. `AGENTS.md`
2. `docs/continuity/00_START_HERE.md`
3. `docs/continuity/NEW_CHAT_PROMPT.md`
4. `docs/continuity/STATE.json` and `STATE.md`
5. `docs/continuity/MINDSET.md`
6. `docs/continuity/WORK_LEVELS.md`
7. `docs/continuity/DECISION_LOG.jsonl` and `PROMPT_RESULT_LOG.jsonl`
8. `docs/continuity/PROBLEMS_FIXES.md`
9. `docs/continuity/COVERAGE.json` and `GAPS.md`
10. `docs/continuity/SESSION_INDEX.json` plus the active session file
11. `docs/continuity/EVENTS.jsonl` tail and `TIMELINE.md`
12. `docs/continuity/EVIDENCE_MANIFEST.json` and linked evidence
13. `config/spaces.json`, `config/channels.json`, `config/repos.json`, `docs/architecture/`

Honour the evidence levels: `verbatim_transcript` > `verbatim_event_log` > `repo_evidence` > `connected_app_record` > `screenshot_only` > `session_memory` > `gap`. Screenshots are not transcripts. Session memory is not a verbatim export. Do not claim “everything is preserved” while `COVERAGE.json` says the full Arena chat export is missing.

Current state you must inherit:

- The repo structure is one core repo, one deploy, five spaces: `yt-automation`, `monarch-studio`, `personal-brand`, `portfolio`, `ops`. Three channels are Monarch Lab, Mindful Momentum, Curious Miles.
- The continuity archive itself is implemented with state ledger, session index, event/decision/prompt-result ledgers, evidence manifest, importer, validator, CI and commit-pinned bootstrap. Real Arena chat exports still need to be imported to close the exactness gap.
- The `monarch-cam` ranking Short V4 and V5 are explicitly rejected by the user. V4 was “sirf text likh diya”; V5 was “NAHI abhi bhi theek se nhi”. Technical QC, 40/40 checks, 9/9 audio gates and 47/47 flags are **not** creative acceptance. No V6 package, workflow, source ledger, rights-verified funny social-platform clips, rendered MP4, QC contract or final delivery exists.
- V5 hook/list geometry occludes the hook and question; the reference requires a centered colorful top hook and a fully visible left `1.`–`7.` black label plate list with progressive labels, payoff cuts/zoom, reaction bubbles and emojis.
- Only native per-window source audio is allowed; no generated sound/audio substitution, no silent segments, no unverified platform reposts, no strict CC0-only assumption without revising rights gates.
- Earlier work includes V2/V3/V4/V5 builds, portfolio live wiring, extinct-life wall Short, animated POV storyboard test, portrait research, B2B agency OS, WF‑01/02/03/04/05/07 workflows, Drive/Notion/Linear/Docs style libraries and session logs. Exact commits, runs, hashes and dead ends are in `WORK_LEVELS.md` and `PROBLEMS_FIXES.md`.
- The user communicates in Roman Urdu/Hinglish, often says “Bhai”, “Continue karo”, “done kro”, “bar bar ruk q rahe ho”, “perfectly correctly accurately next level”, “bagair kuch chore miss kiye”, and “tabahi level”. They want direct execution, no repeated questions, no stopping mid-build, no false completion claims, and no re-doing old work.
- Do not claim human full-motion/native-audio listening, approval, sign-off, perfection, retention improvement, virality, or audience results. Historical YouTube Studio analytics are historical metrics only, not outcome promises.

Before any new production work, run `python3 tools/continuity.py validate`. After every meaningful step, append a checkpoint with `python3 tools/continuity.py checkpoint`, update `STATE.json` if the active task/status/next action changed, then `refresh`, `render`, `validate`, `render --check`, commit and push on `{{BRANCH}}`.

If I provide real Arena chat exports, preserve raw bytes with `python3 tools/continuity.py import-chat`, mark coverage honestly, and only then upgrade a session to `verbatim_transcript`.

Now acknowledge the exact resumed state in one short paragraph and tell me the single next action. Do not ask me to repeat the history.
