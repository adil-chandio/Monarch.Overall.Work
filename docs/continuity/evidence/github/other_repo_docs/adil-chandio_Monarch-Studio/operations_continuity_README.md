# Continuity, recovery and sync ledger

This system solves four failure modes: an agent stopping mid-task, a refresh losing the newest state, stale work replacing newer work, and remote platforms drifting apart.

## Guarantees

- exactly one active task slot;
- atomic state files;
- hash-chained append-only event journal;
- visible-chat transcript from task initialization;
- exact next action and running-process ledger;
- immutable checkpoint packages and per-platform sync ledger;
- event-driven checkpoints plus a 55-minute watch process;
- permanent promotion into a named style on completion.

## Commands

```bash
python3 tools/continuity.py resume
python3 tools/continuity.py status
python3 tools/continuity.py log --kind user --actor user --file prompt.txt
python3 tools/continuity.py checkpoint --summary "..." --next-action "..." --commit --push
python3 tools/continuity.py watch --interval-seconds 3300 --commit --push
python3 tools/continuity.py audit --max-age-minutes 70
python3 tools/continuity.py complete --summary "..." --destination styles/<style-id>/projects
```

`outbox/<task>/<checkpoint>/SYNC.json` is authoritative for cross-platform delivery. A platform is not updated merely because another platform succeeded.

## Important limitation

Arena connectors are available only while an agent turn is executing. The watch process can checkpoint and Git-push if credentials/remotes exist, but unattended Notion/Linear/Google Docs connector calls cannot be promised between turns. Those targets remain in the durable outbox and are drained immediately when the agent is active again.