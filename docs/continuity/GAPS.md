# Known gaps — what is NOT preserved yet

These gaps are explicit so no new chat is misled into claiming “everything”.

## Primary gap: complete Arena chat exports

- No complete Arena chat export/JSON is present in the workspace or in any connected app search.
- `/tmp` and `/home/user` searches found no candidate transcript files; only unrelated skill docs containing the word `messages`.
- `public.saved_conversations` in Supabase `monarch-workspace` has **0 rows**. `knowledge_notes` 0; `workspace_state` 1 row revision 1.
- Dropbox recursive root has only `/MONARCH_B2B_DELIVERY` and one 783-byte MD; no chat transcript.
- Gmail has 3 B2B outreach drafts and 1 blank draft; no transcript/attachment.
- Vercel has project/deployment metadata for `monarch-concierge-api` and `whatsapp-ai-saathi`; no chat transcript.
- Google Docs has WF‑07 start-here, H3 prompting grammar, H3 facts, free/paid routes, Colab runbook, WF hubs and registries; no Arena chat transcript.
- Notion integration returns workflow hubs, registries, postmortems and a legacy WF‑02 page; no raw Arena transcript.
- Linear project descriptions claim “complete session record” for older WF‑02/Stickman work, but those are project descriptions, not exported Arena chat turns.
- Drive has 11 cumulative Stickman session logs, 13 `RESUME_STATE.md` snapshots, WF‑02/WF‑05 codexes, recovery hubs, receipts and one history archive. These are `connected_app_record` evidence, not full Arena chat exports.

## Current chat and sidebar

- The current chat's exact user/assistant turns are not programmatically exportable from this session. Only the condensed session memory and 4 attached screenshots are available.
- Sidebar titles in the 4 screenshots are truncated. The exact full chat list, full titles, timestamps and unseen turns are unknown. `sessions/screenshot-sidebar-20261108.md` preserves only what is visible.
- The 4 screenshots show branches `arena/6101616c-monarch-overall-work`, `arena/d9c9e65-portfolio`, `arena/ba8d901e-monarch-overall-work`, `arena/1f352b8e-monarch-overall-work`. Their complete conversations are not imported.

## Imported transcript limits

- `EMS-20261011-001/CHAT_TRANSCRIPT.jsonl` has **3 user messages** and **0 assistant messages**. It is a real verbatim transcript fragment, not a complete conversation.
- `JOURNAL.jsonl` is a hash-chained event/action log with `user`, `arena-agent`, `continuity`, `decision`, `action`, `checkpoint` entries. It is exact as an event log, not a chat transcript.
- `EMS-20261011-001-history-archive.tar.gz` is preserved raw; its `RESUME.md`, `HANDOFF.md`, `USER_REQUEST.txt`, `checkpoint.json`, `STATUS.md` and `SYNC.json` are extracted as connected-app records.

## External-tool limits

- Drive search with a broad continuity query returned 100 files and was truncated; targeted exact-name searches were used instead. The 100-file result is not treated as exhaustive.
- Three stale Drive IDs from session memory returned 404 and were replaced with exact-name search results. A legacy Notion Google Doc HUB ID also 404s.
- `dropbox__get_file_content` is blocked by `email_not_verified`; the B2B MD body is not imported.
- Drive `WF02_STYLE_MEMORY_V2_V8_20261016.zip` (43,712,098 bytes), `WF-05 FULL LIBRARY` shortcut target ZIP `1ue4xkG697LP4yH66GCJYPtMr0D17pPkd`, and several large MP4/ZIP source packages are indexed by ID but not downloaded into Git.
- Vercel env values are empty/redacted; no secrets or credentials are copied.
- Other chats are active: branch heads in `evidence/github/branch_heads.json` are a timestamped snapshot, not a live guarantee.

## Video-task gaps

- V4 and V5 are creatively rejected. No V6 package, `.gitignore` exception, workflow, source ledger, rights-verified social-platform clips, extracted scenes, renderer, QC contract, MP4, run or final delivery exists.
- No rights-cleared funny social-platform clip has been selected.
- No human full-motion/native-audio listening, approval, sign-off, perfection, retention, virality or audience-result record exists.

## How to close the gaps

1. Export each complete Arena chat from the UI (JSON/JSONL/MD/TXT).
2. Drop files into `docs/continuity/chat_exports/inbox/`.
3. Run `python3 tools/continuity.py import-chat ... --coverage complete` per chat.
4. Only after every known chat is accounted for, update `COVERAGE.json`, `STATE.json.gaps` and this file, then validate/render/commit/push.
5. For the video task, build a separate V6 package from verified rights, visible hook/list geometry and native audio; do not modify V5.

Until then, describe the archive as **“the most complete repo-backed continuation possible from available evidence, with exact gaps marked”**, not “all chats preserved”.

## Channel-config reconciliation gap

- Owner statement: **Monarch Cam is one of the three channels**. `config/channels.json` still lists three legacy publishing slots: Monarch Lab, Mindful Momentum, Curious Miles. Monarch Cam has its own `@Monarch-Cam` YouTube channel and `production/monarch-cam/` tree.
- Continuity now treats Monarch Cam as the active channel workstream and preserves the legacy config unchanged. Do **not** claim the config is reconciled, do not delete/rename legacy slots, and do not invent a fourth config slot. Exact mapping requires an explicit owner instruction.
- A workspace can also be restored to an old commit without continuity files. `RECOVER.md` / `recover` mitigate this; they do not prove automatic live sync or replace real Arena chat exports.
