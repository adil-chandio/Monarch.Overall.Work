# Import protocol — turn real chat exports into exact continuity

## Why this exists

Screenshots and session memory are not enough to claim “sab exactly chat”. The only evidence level that supports exact transcript preservation is a raw export. This archive currently has one **partial** older transcript (`EMS-20261011-001`) and no complete Arena chat export. That gap is deliberate and visible.

## Step 1 — obtain the export

From Arena, export the chat as JSON, JSONL, Markdown, or plain text if the UI provides an export/download option. If Arena does not expose a transcript API in the session, save the visible conversation using the available UI export, then attach/copy the file into this repository. Do not reconstruct missing turns from memory and label them verbatim.

Supported inputs:

- `.json` containing a `messages` / `conversation` / `turns` / `chat` / `events` array, or an array of message objects;
- `.jsonl` with one message/event object per line;
- `.md` / `.txt` with `User:` / `Assistant:` / `### User` / `**Assistant:**` style prefixes;
- unknown/binary files are preserved raw with `review_required` warnings but are not normalized.

Message fields recognised: `role|author|sender|speaker|from|actor|type`, `content|text|body|message|value|parts`, and `timestamp|created_at|date|time|createdAt`.

## Step 2 — drop it in the inbox

```bash
cp /path/to/export.json docs/continuity/chat_exports/inbox/
```

Only `README.md` and `.gitkeep` may remain in the inbox after import; `validate` fails on any other file.

## Step 3 — import with honest coverage

```bash
python3 tools/continuity.py import-chat \
  docs/continuity/chat_exports/inbox/export.json \
  --session-id arena-390292fc-full \
  --title "Exact Arena chat title" \
  --source "Arena UI export" \
  --source-url "https://arena.ai/..." \
  --space ops \
  --branch arena/2b012328-monarch-overall-work \
  --kind transcript \
  --evidence-level verbatim_transcript \
  --coverage complete \
  --notes "Full chat export supplied by user; includes user and assistant turns."
```

Use `--coverage partial` for a truncated/partial export. For a hash-chained journal use `--kind event_log --evidence-level verbatim_event_log --coverage partial`. For a ZIP/tar archive use `--kind archive --evidence-level connected_app_record --coverage partial`; raw bytes are preserved but not normalized.

The importer:

- moves/copies the raw file into `chat_exports/sources/<session-id>/raw/`;
- computes SHA-256 and byte size;
- writes derived `normalized.jsonl` and `metadata.json`;
- writes `sessions/<session-id>.md`;
- updates `SESSION_INDEX.json`, `COVERAGE.json`, `EVENTS.jsonl`, `STATE.json`;
- calls `refresh` and `render`.

The **raw file is authoritative**. `normalized.jsonl` is a convenience view; never quote it as more complete than the raw export.

## Step 4 — close the gap truthfully

After importing every complete Arena chat:

1. Run `python3 tools/continuity.py validate`.
2. Update `COVERAGE.json` counts/gaps and `STATE.json.gaps` only if the imports genuinely cover all known chats.
3. Update `GAPS.md`.
4. Run `refresh`, `render`, `validate`, `render --check`.
5. Commit and push on the active branch.

Do not set `full_arena_export_available=true` until the sidebar's full chat list and every chat's turns are accounted for by raw exports. `validate` keeps this flag false by policy.

## Existing imports

- `EMS-20261011-001` — 3 verbatim user messages from `CHAT_TRANSCRIPT.jsonl`, no assistant messages; partial.
- `EMS-20261011-001-journal` — hash-chained `JOURNAL.jsonl`, exact event log, not a chat transcript; partial.
- `EMS-20261011-001-archive` — raw `history-archive.tar.gz` bytes preserved; connected-app record, not normalized.

All other current-chat evidence remains `session_memory`, `screenshot_only`, `repo_evidence`, `connected_app_record`, or `gap`.
