# Resume capsule — EMS-20261014-FLOW-REPAIR

**Status:** `active`  
**Title:** Recover and correct Einstein flow-state edit  
**Style:** `studio-operation`  
**Checkpoint sequence:** 1  
**Last checkpoint:** 2026-10-14T16:13:35Z

## Goal

Review actual reference and previous deliveries; preserve existing work; correct motion, caption timing, clean branding and accurate Urdu-English delivery without another slideshow.

## Acceptance criteria

- [ ] Actual reference visually reviewed; existing V2/V4 and audio recovered first
- [ ] No static-slide substitution; detailed scene motion and synchronized captions
- [ ] No Monarch/Instagram on-screen tags; standard H264 yuv420p AAC export
- [ ] Verified downloadable Drive delivery plus durable source recovery

## Exact next action

Inspect dense reference frames and narration waveforms; build reference-derived clean motion edit with shot-level Urdu-English synchronization.

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
- Latest checkpoint package: `operations/continuity/checkpoints/EMS-20261014-FLOW-REPAIR/0001-20261014T161335Z`

Never restart this task from the beginning when these records exist. Verify the journal, inspect the latest checkpoint, then execute **Exact next action**.
