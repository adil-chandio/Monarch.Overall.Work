# Resume capsule — EMS-20261011-003

**Status:** `rendering`  
**Title:** TUMHARI RESERVED SEAT · Monarch Cinema Tabahi V2 · dual-style 3× enhancement  
**Style:** `monarch-stickman-animation + monarch-noir-film`  
**Checkpoint sequence:** 1  
**Last checkpoint:** 2026-10-11T00:45:21Z

## Goal

Preserve both accepted originals, then rebuild the same 74-second 16:9 narrative and exact selected voice into two separate Monarch-level V2 masters with materially stronger animation, editing, motion graphics, 3-D depth/motion control, transitions, effects, sound design and music—smooth, cinematic, attention-grabbing and full of earned WTF moments rather than noisy over-editing.

## Acceptance criteria

- [ ] V1 masters and permanent packages remain immutable; all V2 work lives in clearly versioned WF-01 and WF-03 production packages.
- [ ] The locked 74.00-second easy-Urdunglish script, 34-beat timeline, exact un-stretched voice-00 and 1920×1080 16:9 format remain shared across both V2 films.
- [ ] WF-01 and WF-03 retain unmistakably separate visual, animation, editing, transition, colour, typography, music and sound identities.
- [ ] Every beat receives demonstrably richer but readable animation, cinematic edit logic, motion graphics, controlled 3-D depth, motivated effects, secondary motion and smooth transitions, including multiple earned WTF/payoff moments.
- [ ] Both soundtracks are independently redesigned with stronger score architecture, stereo SFX/ASMR, impacts, risers, motifs and micro-detail while preserving narration intelligibility and avoiding clipping or fatigue.
- [ ] Both V2 masters pass unchanged-or-stricter objective delivery gates, freshness/novelty review, full source/provenance preservation, Drive upload and independent GitHub/Notion/Linear/Google Docs synchronization.

## Exact next action

Wait for WF-01 V2 mute master render process; verify exact 74.00 s output, then render WF-03 in two segments, mux exact voice-led mixes, run 40 delivery/delta gates on both, inspect failures, and only then package/synchronize.

## Running processes

- `wf-01-v2-cinema-render-b3ef0666` — WF-01 V2 cinema render — running

## Recovery command

```bash
python3 tools/continuity.py resume
```

## Durable evidence

- Active state: `workflows/current/ACTIVE_TASK.json`
- Hash-chained action journal: `workflows/current/JOURNAL.jsonl`
- Visible user/assistant transcript: `workflows/current/CHAT_TRANSCRIPT.jsonl`
- Active payload only: `workflows/current/payload/`
- Latest checkpoint package: `operations/continuity/checkpoints/EMS-20261011-003/0001-20261011T004521Z`

Never restart this task from the beginning when these records exist. Verify the journal, inspect the latest checkpoint, then execute **Exact next action**.
