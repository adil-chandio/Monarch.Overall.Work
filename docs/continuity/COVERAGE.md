# Evidence coverage

This archive is honest about evidence strength. A screenshot is never promoted to a transcript.

```json
{
  "captured_at": "2026-11-08T15:32:32Z",
  "channels": {
    "active_channel": "monarch-cam",
    "capsule": "docs/continuity/channels/monarch-cam/EASY_RESUME.md",
    "entrypoint": "docs/continuity/channels/monarch-cam/00_START_HERE.md",
    "index": "docs/continuity/channels/CHANNEL_INDEX.json",
    "indexed": 4,
    "next_action": "docs/continuity/channels/monarch-cam/NEXT_ACTION.md",
    "note": "Legacy config/channels.json slots preserved; do not claim reconciliation.",
    "owner_statement": "Monarch Cam is one of our 3 channels.",
    "playbook": "docs/continuity/channels/monarch-cam/PLAYBOOK.md",
    "reconciliation_status": "explicit_gap",
    "state": "docs/continuity/channels/monarch-cam/CHANNEL_STATE.json",
    "workflow": "docs/continuity/channels/monarch-cam/WORKFLOW.md"
  },
  "connected_app_records": {
    "dropbox_files": 1,
    "gmail_drafts": 4,
    "google_docs": 12,
    "google_drive_resume_states": 13,
    "google_drive_session_logs": 11,
    "linear_projects": 13,
    "notion_pages": "multiple, truncated",
    "snapshot": "docs/continuity/external/APP_SNAPSHOT.json",
    "supabase_columns": 232,
    "supabase_saved_conversations": 0,
    "supabase_tables": 22,
    "vercel_projects": 2
  },
  "counts": {
    "channel_files": 10,
    "channels_indexed": 4,
    "decisions": 19,
    "events": 56,
    "manifest_files": 358,
    "prompt_results": 13,
    "screenshots": 29,
    "sessions_indexed": 29
  },
  "evidence_levels": {
    "archive_metadata": "Generated archive metadata, hash index or integrity manifest.",
    "connected_app_record": "Drive/Docs/Notion/Linear/Supabase/Vercel/Gmail/Dropbox record or imported text.",
    "gap": "Known missing source; explicitly not claimed as preserved.",
    "operating_contract": "Human-readable continuity contract, protocol, index or session note.",
    "repo_evidence": "Git object, commit, branch, PR, workflow run, or checked-in file.",
    "screenshot_only": "Partial visible screenshot image evidence; never a full transcript.",
    "session_memory": "Condensed session-memory reconstruction; lower confidence.",
    "state_ledger": "Machine-readable state, coverage, session index or append-only JSONL ledger.",
    "verbatim_event_log": "Exact hash-chained event/journal file; not a chat transcript.",
    "verbatim_source": "Raw imported transcript/export bytes before normalization.",
    "verbatim_transcript": "Exact exported chat turns; raw bytes authoritative."
  },
  "gaps": [
    "No complete Arena chat export/JSON in workspace or connected apps.",
    "Current chat/sidebar exact turns not programmatically exportable.",
    "EMS transcript is partial and has no assistant turns.",
    "Connected apps are timestamped snapshots, not live mirrors.",
    "V6 technical build complete with seven per-title CC0 Commons originals; real social-platform reposts remain unverified; human full-motion/native-audio review and creative acceptance are not recorded.",
    "Human listening/approval/sign-off not recorded.",
    "Owner says Monarch Cam is one of the 3 channels; config/channels.json still lists 3 legacy slot names.",
    "Stale checkout can restore an old commit without continuity files; RECOVER.md / recover are mitigations, not live sync."
  ],
  "generated_at": "2026-11-08T17:50:20Z",
  "note": "Evidence coverage is honest: a screenshot is never promoted to a transcript, and a connected-app summary is not a complete Arena export.",
  "policy": "COVERAGE.verbatim_transcripts.full_arena_export_available must remain false until every known chat has a complete raw export and STATE/COVERAGE/GAPS are deliberately updated.",
  "repo_evidence": {
    "commits": 998,
    "heads": 11,
    "manifest": "docs/continuity/evidence/github/README.md",
    "pull_requests": 4,
    "repos_inspected": 22,
    "runs": 452,
    "satellite_files": 120,
    "tags": 16,
    "workflows": 18
  },
  "schema_version": "1.0.0",
  "screenshots": {
    "audio_tool_context": 3,
    "index": "docs/continuity/evidence/screenshots/screenshot_index.json",
    "new_chat_evidence": 4,
    "ranking_reference": 8,
    "total": 29,
    "youtube_analytics_history": 14
  },
  "verbatim_transcripts": {
    "available": true,
    "complete_sessions": 0,
    "full_arena_export_available": false,
    "imported_sessions": 2,
    "known_partial_source": "EMS-20261011-001 CHAT_TRANSCRIPT.jsonl: 3 user messages, 0 assistant messages",
    "partial_sessions": 2
  }
}
```

## Evidence levels
```json
{
  "archive_metadata": "Generated archive metadata, hash index or integrity manifest.",
  "connected_app_record": "Drive/Docs/Notion/Linear/Supabase/Vercel/Gmail/Dropbox record or imported text.",
  "gap": "Known missing source; explicitly not claimed as preserved.",
  "operating_contract": "Human-readable continuity contract, protocol, index or session note.",
  "repo_evidence": "Git object, commit, branch, PR, workflow run, or checked-in repository file.",
  "screenshot_only": "Visible screenshot image evidence; truncated/partial and never a full transcript.",
  "session_memory": "Condensed session-memory reconstruction; lower confidence than a transcript.",
  "state_ledger": "Machine-readable state, coverage, session index or append-only JSONL ledger.",
  "verbatim_event_log": "Exact exported hash-chained event/journal file; not a chat transcript.",
  "verbatim_source": "Raw imported transcript/export bytes before normalization.",
  "verbatim_transcript": "Exact exported chat turns; raw bytes are authoritative."
}
```
