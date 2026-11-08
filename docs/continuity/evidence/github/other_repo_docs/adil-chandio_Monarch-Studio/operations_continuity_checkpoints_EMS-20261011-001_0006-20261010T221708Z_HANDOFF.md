# Resume capsule — EMS-20261011-001

**Status:** `completed`  
**Title:** Style Library + Crash-Proof Continuity System v1  
**Style:** `studio-operation`  
**Checkpoint sequence:** 6  
**Last checkpoint:** 2026-10-10T22:17:08Z

## Goal

Create separately named permanent editing-style libraries, keep only one running task in workflows/current, preserve exact visible chat/actions and resume state, checkpoint at least hourly, and synchronize evidence to GitHub, Drive, Notion, Linear and Google Docs without silent omissions.

## Acceptance criteria

- [ ] Every permanent editing style has its own complete named folder and knowledge index.
- [ ] workflows/current contains only the single running task and an exact next action.
- [ ] Refresh/restart recovery continues from a verified hash-chained checkpoint rather than restarting.
- [ ] Hourly/event-driven checkpoint packages and five-platform sync ledgers exist.
- [ ] Repository, tests, authorities and remote records validate without unrecorded drift.

## Exact next action

Task complete; consult permanent archive.

## Running processes

- None recorded.

## Recovery command

```bash
python3 tools/continuity.py resume
```

## Durable evidence

- Active state: `workflows/current/ACTIVE_TASK.json`
- Hash-chained action journal: `workflows/current/JOURNAL.jsonl`
- Visible user/assistant transcript: `workflows/current/CHAT_TRANSCRIPT.jsonl`
- Active payload only: `workflows/current/payload/`
- Latest checkpoint package: `operations/continuity/checkpoints/EMS-20261011-001/0006-20261010T221708Z`

Never restart this task from the beginning when these records exist. Verify the journal, inspect the latest checkpoint, then execute **Exact next action**.
