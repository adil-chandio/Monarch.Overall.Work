# External evidence — connected-app snapshot

This directory records what was actually found in Google Drive, Google Docs, Notion, Linear, Supabase, Vercel, Gmail and Dropbox during the continuity sweep. It is a **timestamped discovery snapshot**, not a live mirror and not proof that Arena chat memory transferred.

- `APP_SNAPSHOT.json` — machine-readable counts, IDs, links, errors and gaps.
- `DRIVE_INDEX.md` — exact Drive IDs for session logs, resume states, codexes, start-here docs, receipts and the history archive.
- `../evidence/external/drive_text/` — imported text/plain exports of Drive files and native Google Docs.
- `../evidence/external/drive/session_logs/` — canonical renamed copies of duplicate-named `RESUME_STATE.md` and `MONARCH_STICKMAN_ANIMATION_SESSION_LOG.md` snapshots.
- `../evidence/github/` — commit-pinned GitHub evidence; stronger than external-app descriptions.

## Evidence level

Everything here is `connected_app_record` unless it is a raw `CHAT_TRANSCRIPT.jsonl` inside the imported history archive, which is `verbatim_transcript` but partial. Screenshots remain `screenshot_only` in `../evidence/screenshots/`.

## Safety

- Raw Drive/Docs/satellite text is preserved byte-for-byte, including original CRLF/trailing spaces. Root `.gitattributes` disables EOL conversion and `git diff --check` whitespace errors under `docs/continuity/`; the hashes in `EVIDENCE_MANIFEST.json` are the integrity source of truth.
- No OAuth tokens, passwords, API keys, service-role keys, or env var values are copied.
- Account email addresses are redacted from the snapshot where they are not necessary evidence.
- Vercel env keys are listed with empty/redacted values only.
- Three stale Drive IDs and one legacy Notion Google Doc HUB ID returned 404 and are recorded as gaps, not silently substituted.
- Dropbox content read is blocked by `email_not_verified`; metadata only is recorded.

## Key finding

The connected apps contain substantial **workflow, style, project, session-log, deployment and receipt** evidence, but no complete Arena chat export. Supabase `saved_conversations` is empty. Therefore exact all-chat preservation still requires real Arena exports imported through `docs/continuity/IMPORT_PROTOCOL.md`.
