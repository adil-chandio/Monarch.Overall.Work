# Decision log

Append-only. Each decision carries its evidence level; rejected options stay visible.

## `2026-10-10T21:27:33Z` · dec-001-ems-system

- Decision: Build one repo-first system/structure with separately named editing styles and empty workflow for the agent
- Why: Because refresh/continue restarts from the beginning and latest running work disappears
- Rejected: Do not fill workflow with agent memory; do not lose latest work; do not rely on chat memory alone
- Evidence level: `verbatim_transcript`
- Refs: `docs/continuity/evidence/external/drive_text/EMS-20261011-001_history_archive/operations/history/EMS-20261011-001/payload/USER_REQUEST.txt`

## `2026-11-08T15:00:00Z` · dec-002-repo-first

- Decision: Make Monarch.Overall.Work the primary source of truth; connected apps are secondary evidence
- Why: User said “sabse zyada ham har cheez repo ke rakhenge”
- Rejected: Do not treat Drive/Notion/Linear/Docs as live mirrors or claim exact all-chat transfer
- Evidence level: `session_memory`
- Refs: `docs/continuity/MINDSET.md`

## `2026-11-08T15:35:00Z` · dec-003-evidence-levels

- Decision: Use explicit evidence levels and keep gaps visible
- Why: Screenshots/session memory/connected-app summaries cannot prove complete transcripts
- Rejected: Do not promote a screenshot to verbatim transcript or claim “everything”
- Evidence level: `repo_evidence`
- Refs: `docs/continuity/README.md`

## `2026-11-05T00:00:00Z` · dec-004-v3

- Decision: V3 choices build_v3 / new_cleared_animal / subtle_rank / 35s_ent
- Why: User selected V3 direction
- Rejected: Earlier 20s and premium/CLEAN variants rejected or superseded
- Evidence level: `session_memory`
- Refs: `docs/continuity/sessions/monarch-cam-v3.md`

## `2026-11-07T15:00:00Z` · dec-005-v4

- Decision: V4 choices new_v4 / raw_only / rank_title; dynamic_cover / shorten / keep_35; replace_silent_sources
- Why: User selected V4 direction
- Rejected: V3 dance renderer/audio/music/SFX not raw moment audio; silent old sources rejected
- Evidence level: `session_memory`
- Refs: `docs/continuity/sessions/monarch-cam-v4.md`

## `2026-11-07T20:00:00Z` · dec-006-v4-reject

- Decision: V4 is not final
- Why: User said “sirf text likh diya”
- Rejected: Do not re-present V4 or equate technical QC with creative acceptance
- Evidence level: `session_memory`
- Refs: `docs/continuity/PROBLEMS_FIXES.md`

## `2026-11-08T00:00:00Z` · dec-007-v5

- Decision: V5 choices new_v5_both / full / seven_60
- Why: User selected full 60s seven-moment direction
- Rejected: V4 35s geometry and silent-source policy superseded
- Evidence level: `session_memory`
- Refs: `docs/continuity/sessions/monarch-cam-v5.md`

## `2026-11-08T02:00:00Z` · dec-008-v5-reject

- Decision: V5 is not final and stays untouched
- Why: User said “NAHI abhi bhi theek se nhi” plus four screenshots
- Rejected: Do not re-present V5, claim approval, or reuse occluding hook/list geometry
- Evidence level: `session_memory`
- Refs: `docs/continuity/PROBLEMS_FIXES.md`

## `2026-11-08T15:52:00Z` · dec-009-v6-separate

- Decision: Any V6 must be a separate package after rights/source verification
- Why: V4/V5 rejected; reference requires full motion, visible hook/list and verified social-platform clips
- Rejected: No V6 files exist; V5 untouched; no rights-cleared platform clip selected
- Evidence level: `gap`
- Refs: `docs/continuity/sessions/monarch-cam-v6-intent.md`

## `2026-11-08T15:00:00Z` · dec-010-extinct-life

- Decision: Extinct-life wall request means a full Short video, not still frames
- Why: User: “Ok ab poori videos”, “Short video hamari”, “Woh poori video banao ab new level ke sath…”
- Rejected: Do not reduce to a still-image storyboard
- Evidence level: `screenshot_only`
- Refs: `docs/continuity/sessions/arena-ba8d901e-extinct-life-wall.md`

## `2026-11-08T15:00:00Z` · dec-011-animated-pov

- Decision: Animated POV must render scenes/character/props/lighting/movement frame by frame
- Why: User objected to inserting a character into images
- Rejected: Remove illustrated backgrounds; do not reuse image-composite approach
- Evidence level: `screenshot_only`
- Refs: `docs/continuity/sessions/arena-1f352b8e-animated-pov.md`

## `2026-11-08T15:50:00Z` · dec-012-import-policy

- Decision: Real Arena exports required before claiming exact all-chat preservation
- Why: No full transcript/JSON found; Supabase saved_conversations=0
- Rejected: Do not fabricate transcripts or mark full_arena_export_available=true
- Evidence level: `repo_evidence`
- Refs: `docs/continuity/IMPORT_PROTOCOL.md`

## `2026-11-08T15:53:00Z` · dec-013-claims-false

- Decision: All approval/acceptance/perfection/outcome claims remain false
- Why: No verbatim acceptance, human listening, sign-off or audience result record
- Rejected: Do not claim retention/virality/perfection or human approval
- Evidence level: `state_ledger`
- Refs: `docs/continuity/STATE.json`

## `2026-11-08T15:51:00Z` · dec-014-branch

- Decision: Work only on arena/390292fc-monarch-overall-work
- Why: Arena session tracking and explicit branch guardrail
- Rejected: Never switch, rename, or push another branch
- Evidence level: `repo_evidence`
- Refs: `docs/continuity/00_START_HERE.md`

## `2026-11-08T15:54:00Z` · dec-015-hourly

- Decision: Use append-only checkpoints plus CI/validator instead of silent hourly automation
- Why: Earlier request for hourly/event-driven push updates; current repo provides protocol not a proven cron
- Rejected: Do not claim hourly automation is proven
- Evidence level: `repo_evidence`
- Refs: `docs/continuity/UPDATE_PROTOCOL.md`

## `2026-11-08T15:46:00Z` · dec-016-scratch

- Decision: Keep google_drive/, tmp_chat_evidence/ and /tmp out of canonical truth
- Why: Connector downloads overwrite duplicate names and /tmp is nonpersistent
- Rejected: Copy to evidence/screenshots and evidence/external/drive_text with hashes
- Evidence level: `repo_evidence`
- Refs: `docs/continuity/evidence/external/drive_import_manifest.json`

## `2026-11-08T16:00:00Z` · dec-017-no-secrets

- Decision: Redact credentials and env values from APP_SNAPSHOT
- Why: Connected-app data includes env key names but values are empty/redacted
- Rejected: Do not copy OAuth tokens, API keys, passwords or service-role keys
- Evidence level: `connected_app_record`
- Refs: `docs/continuity/external/APP_SNAPSHOT.json`

## `2026-11-08T15:35:00Z` · dec-018-generated-md

- Decision: Generated *.md ledgers are derived from JSON/JSONL, never hand-edited
- Why: Prevents circular hashes and stale summaries
- Rejected: Edit STATE.json, COVERAGE.json, SESSION_INDEX.json and append-only ledgers; run render
- Evidence level: `repo_evidence`
- Refs: `docs/continuity/UPDATE_PROTOCOL.md`
