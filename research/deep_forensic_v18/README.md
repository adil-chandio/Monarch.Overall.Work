# V18.1 — Deep 10x forensic (Shorts / Medium / Long) — entry point

**Status: research complete; niche NOT approved.** User said: “abhi decide NAHI hua”.

## Padhne ka order

1. **`FINAL_DEEP_FORENSIC_V18_ROMAN_URDU.md`** — final user-facing Roman Urdu report (10x / microscope). Status + boundary, 24 lanes, 717-candidate distribution, duration/hook/chapter/tag/description forensics, titles, descriptions + CTA, 575 comments, 40 thumbnails, channel proxies, transcript blocker, Short vs Medium vs Long, niche scoring (tie), provisional recommendation, A/B/C decision.
2. `PRODUCTION_BLUEPRINT_V18_ROMAN_URDU.md` — production blueprint (scripts, titles, descriptions, chapters, tags, comments, thumbnails, editing plan, safety/rights/QC).
3. `EPISODE_00_EDL_V18.json` — machine-readable: teen formats ke scripts, EDL, titles, descriptions, chapters, tags, comment prompts, thumbnail specs, QC.
4. `EVIDENCE_TABLES_V18.md` — machine evidence tables.
5. `FORENSIC_EVIDENCE_EXTRACT_V18.json` — auditable extract (717 index, 40 teardown cards, derived tables).
6. `RECOMMENDATION_V18.json` — ranked options + scoring + pending decision + boundaries.
7. `DEEP_FORENSIC_V18.md` — auto-generated Actions appendix (raw, not the final report).
8. `api_evidence/` — asli API dump (run `43249117208`, `2026-11-12T15:39:12Z`, HARD QC PASS).

## Run facts

- GH run `43249117208` — success 5m37s — HARD QC PASS (raw dump `2347` = in-memory `2347` = manifest `2347`).
- 24 lanes, 1,122 lane rows, **2,347** unique public videos, **804** channels, **726** million-view videos, **717** title-safe candidates, **40** deep teardowns, **23** comment-mined videos (**575** comments), **40** thumbnails, **12** transcript attempts (**0 pass**), ~**2,549** quota units.
- Reproduce: push `v18-deep-trigger.txt` (`.github/workflows/yt-deep-forensic-v18.yml`). Local derive: `python3 build_v18_evidence_extract.py` (no network).

## Boundaries (do not overclaim)

No competitor video/audio download, no video-frame inspection, no competitor transcript (12/12 blocked), no private retention/CTR/RPM, no verified growth ranking, no causal claim, no legal/human/creative approval, no upload/publish, no monetisation outcome, no guaranteed views/virality/perfection. Creator descriptions are synopses/chapter metadata, not spoken scripts.
