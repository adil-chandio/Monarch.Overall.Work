# Chat exports

This is where exact conversation preservation lives. It is deliberately separate from summaries so evidence level is never confused.

```text
chat_exports/
├── inbox/        # drop real Arena exports here, then import; validator rejects leftovers
└── sources/
    └── <session-id>/
        ├── raw/<original-file>   # immutable raw bytes, SHA-256 in metadata
        ├── normalized.jsonl      # derived convenience view
        └── metadata.json         # source, coverage, parser, hashes, warnings
```

Use `python3 tools/continuity.py import-chat` — do not hand-edit `sources/` after import.

## Current imports

- `EMS-20261011-001` — partial verbatim transcript: 3 user messages, 0 assistant messages.
- `EMS-20261011-001-journal` — partial verbatim event log: hash-chained `JOURNAL.jsonl`.
- `EMS-20261011-001-archive` — raw `history-archive.tar.gz` preserved; connected-app record.

## Evidence rule

The raw file is authoritative. `normalized.jsonl` is derived and may not contain every byte or attachment. A transcript is `complete` only when the user supplies a genuine full chat export; otherwise use `partial`. Screenshots, session memory, Drive logs, Notion pages and Linear descriptions do not belong in `sources/` as transcripts.

See `../IMPORT_PROTOCOL.md` and `../GAPS.md`.
