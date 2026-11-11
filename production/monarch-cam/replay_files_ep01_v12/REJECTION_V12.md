# REJECTED — V12 "REPLAY FILES Ep.1" (owner review, 2026-11-11)

**Verdict: REJECTED.** 13 phone screenshots of the downloaded MP4 were supplied by the
owner. This file stays in the repository only as a record of what went wrong. It is NOT a
deliverable and must not be presented, linked or re-cut as the answer.

## What the owner actually asked for

A **"Caught on Camera" clip compilation**: find many of the BEST viral clips from social
media (Instagram / TikTok / Reddit / Twitter / Dailymotion), pick the most
attention-grabbing, funny, shocking, mind-blowing, eye-catching, hooky scenes INSIDE those
clips, compile them, and keep viewers engaged with real footage + commentary + editing.
Before that: deep, 10x, microscope-level forensic study of the caught-on-camera niche,
other viral/growing channels, their niches, their best-performing millions-view videos,
scripts, clips and editing.

## What was built instead (fatal errors)

| # | Fatal error | Evidence in screenshots |
|---|---|---|
| 1 | **0:00–1:40 static title/method/diagram cards with only VO. Zero clips.** ~100 s of dead air before any footage. | 0:02, 0:12, 0:29, 1:01, 1:25, 1:41 frames |
| 2 | **Reused the exact archived `deliverables/*.mp4` finals the owner had already set aside / rejected.** No new clip was acquired. | clip-window frames, `EDL_V12_ACTUAL.json` |
| 3 | **Long static diagram holds in the middle** (20–27 s each) — "one image in front of which the talking starts again". | 2:19, "Expected vs Actual", "The Late Explanation", "Scale Error", "Sound vs Silence" |
| 4 | **Wrong niche / wrong format.** Built an abstract "replay rule / analytics forensic" essay instead of a caught-on-camera clip compilation. | every card title |
| 5 | **Owner-only analytics talk** (Spikes, Intro, Dips, 5 API lanes, view-count tables) shown full-screen to viewers. Nobody watches that. | "Evidence Base", "The Method" cards |
| 6 | **Cringe / cheap perceived quality** on a phone: a 16:9 static-card deck letterboxed into a huge black field. | all screenshots |
| 7 | Presented it as "the best viral video / ban gaya". Technical QC 8/8 was treated as if it meant creative quality. | previous assistant answer |

## Root cause

The render was optimised for what was locally available (own-work SVGs + old finals) and
for passing machine checks. It was **not** optimised for the niche, for the first 3 seconds,
for clip density, or for the owner's explicit instruction to bring in NEW viral clips.
Reusing already-rejected assets and padding runtime with static diagrams was the core
mistake. A technical pass is not a creative pass.

## Rules carried forward to V13

1. **Clip at frame 1.** No static intro, no "method" card, no 100 s VO before footage.
2. **Many DIFFERENT new clips**, not one, not eight old finals, not the NASA V10 Short.
3. Inside each clip, select the **most hooky window** (objective motion/surprise scoring),
   not a random in-point.
4. **No full-screen diagrams as content.** Small lower-third labels / counters only;
   footage stays on screen for essentially the whole runtime.
5. Commentary is **short bursts over footage**, never a monologue over a static image.
6. Research first, with real API evidence: caught-on-camera niche, real viral/growing
   channels, real millions-view videos, structure/pacing/editing. No invented retention,
   CTR, RPM, transcripts or rankings.
7. No upload / publish / monetisation / legal-clearance / virality / perfection claim.

Replacement work lives in `research/caught_on_camera_v13/`.
