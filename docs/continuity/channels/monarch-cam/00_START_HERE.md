# Monarch Cam — 00 START HERE (new chat, zero explanation needed)

**This is the active channel workstream.** The owner describes Monarch Cam as one of the three channels. Do not ask the user to explain the channel, the workflow, the style, the rejections, or the next action. Everything needed is already in this file and its linked files.

- Channel: **Monarch Cam** / `@Monarch-Cam` — https://www.youtube.com/@Monarch-Cam
- Space: `yt-automation`
- Production root: `production/monarch-cam/`
- Active branch: `arena/2b012328-monarch-overall-work`
- One command: `python3 tools/continuity.py resume` (it embeds this channel capsule automatically)
- Channel-only command: `python3 tools/continuity.py channel`
- Stale checkout: `RECOVER.md` / `python3 tools/continuity.py recover`

## Exact identity

> **Real wildlife moments, explained through original behaviour-led storytelling.**

- Primary series: `Too Close: Wildlife in Human Space`
- Secondary series: `Nature's Hidden Tricks` (only after the primary cluster is coherent)
- Owner audit verdict: do **not** delete the channel, do **not** mass-delete old videos, do **not** re-upload the 25-view ranking repeatedly, do **not** start another random niche experiment.
- Old bear winner is still active; new-release system is stalled and incoherent. Rebuild around two organised wildlife promises.

## Three-channel reconciliation (explicit gap)

`config/channels.json` currently lists three legacy slots: `Monarch Lab`, `Mindful Momentum`, `Curious Miles`. Monarch Cam has its own live YouTube channel and production tree. Until the owner explicitly renames a slot, treat Monarch Cam as the **active channel workstream** and preserve the legacy config unchanged. Do not delete, rename, or invent a fourth config slot. Do not claim the config is fully reconciled.

## Exact current state

- Continuity archive is delivered, validated and commit-pinned. Full Arena chat exports are still missing; `full_arena_export_available=false`.
- V4 and V5 ranking Shorts are **creatively rejected**: V4 “sirf text likh diya”; V5 “NAHI abhi bhi theek se nhi” plus four screenshots. Technical QC is not acceptance.
- A separate V6 technical package is built; V5 stays untouched. It uses seven per-title CC0 Commons originals, a source/clip/social-origin ledger, corrected geometry, raw per-window native audio, renderer, QC contract and a workflow. CI run `42517651544` succeeded and the V6 MP4 exists. Human review/acceptance is pending.
- V5 geometry dead end: hook/question occluded by right `1.–7. LIST`; V6 uses a centered colorful top hook and fully visible left `1.–7.` black label plates with progressive labels, right platform UI, bottom comment/Subscribe, payoff cuts/zoom, reaction bubbles and emojis.
- V6 uses only per-title verified CC0 Commons originals, not unverified real social-platform reposts. Only native per-window source audio is allowed; no generated sound/audio substitution, no silent segments, no third-party reposts, no strict CC0-only assumption applied to social clips.
- No human full-motion/native-audio listening, approval, sign-off, perfection, retention, virality or audience-result claim.

## Exact next action

Open this file, inherit `CHANNEL_STATE.json`, then continue the single active Monarch Cam lane without asking the user to explain how to do it. The separate V6 technical package is built; open the MP4 and QC evidence, perform human full-motion/native-audio review, and do not claim creative acceptance. V5 stays untouched. For the broader channel rebuild, follow `PLAYBOOK.md` and `WORKFLOW.md` from the latest recorded state, not from scratch.

## How to work (already decided)

1. `python3 tools/continuity.py resume` (or `recover` first if files are missing).
2. Read `CHANNEL_STATE.json`, `NEXT_ACTION.md`, `PLAYBOOK.md`, `WORKFLOW.md`, `REJECTIONS.md`, `EVIDENCE.md`.
3. Verify rights per title before any edit; keep a clip ledger.
4. Build in a separate package, never by modifying V5.
5. Run validator, QC, commit/push on the active branch.
6. Append a checkpoint and update `CHANNEL_STATE.json` / `STATE.json` before ending.
7. Never claim acceptance or results without a verbatim record.

## Source truth

- `PLAYBOOK.md` — 30-day plan, series, calendar, brand, rights, Shorts rules.
- `WORKFLOW.md` — exact production workflow and commands.
- `NEXT_ACTION.md` — single next-action capsule.
- `EASY_RESUME.md` — copy-paste prompt with no user explanation.
- `REJECTIONS.md` — V4/V5 and dead ends; V6 is not acceptance.
- `EVIDENCE.md` — exact commits, runs, hashes, deliverables, V6 package.
- `production/monarch-cam/short_ranking_raw_v6/RANKING_V6_PLAN_AND_METADATA.md` — V6 rights, geometry, audio and QC contract.
- `.github/workflows/monarch-cam-short-ranking-raw-v6.yml` — V6 build/QC workflow.
- `docs/MONARCH_CAM_LIVE_FORENSIC_AUDIT_2026-11-05.md`
- `docs/MONARCH_CAM_30_DAY_GROWTH_REVENUE_PLAN_2026-11.md`
- `docs/MONARCH_CAM_PERMISSION_FREE_BEAR_FOOTAGE_PLAN_2026-11.md`
- `docs/continuity/PROBLEMS_FIXES.md`, `WORK_LEVELS.md`, `GAPS.md`.
