# Known limits — Monarch night temple

This file exists so no later chat, agent or message can quietly upgrade these
statements into a claim the evidence does not support. If a line here is fixed,
replace it with a measurement and a path to the evidence; do not delete it.

## Never claim without new evidence

1. **Likeness match.** The on-screen face is an AI-generated approximation. No
   human, descriptor or owner acceptance has verified it. The V8 cut does not
   improve identity; the face still drifts during the head turn.
2. **Finished film.** V8 is a 20 s engineering cut: five generated shots, graded,
   stabilised, deflickered, upscaled, with a mastered sound bed. It is not the
   approved deliverable and it is not "final quality".
3. **Human review.** Nobody has listened to the sound or watched the film at
   native speed in this session. Loudness and motion numbers are measurements,
   not perception.
4. **Resolution.** Sources are 512×288 (WAN) to 768×448 (LTX). Output is a
   learned 2× + 720p re-frame. This is not native 1080p and must not be sold as
   such.
5. **Anatomy and physics.** Hands/feet still merge, shoes float, and there is no
   contact shadow or reflection under the runner. Stabilisation does not change
   this.
6. **Rights.** No visual-model or output licence review has been recorded here.
   CC0 provenance for the audio stems is in `audio/SOURCES.md`. Neither is legal
   clearance for publication.
7. **Budget of truth.** The 3D Blender route (`3d-pilot/`) is a generic
   untextured stand-in. It is not a reference-matched character and it is not in
   the V8 film.

## Engineering facts V8 does establish (with evidence paths)

| Fact | Evidence |
| --- | --- |
| 480 frames / 20.000 s, zero duplicated frames, one 5-frame dissolve | `qc/test_film_tools.py` timeline tests; `qc/out/v8/render_log.json` |
| Per-shot deflicker, stabilisation and camera moves applied | `render_log.json → shots[*]` |
| Eye glow verified and tracked on 97/97 close-up frames | `render_log.json → S5-closeup.eye_track` |
| Worst luma step 29.50 → 13.81; S2 jitter 5.39 → 3.26 px | `qc/out/v8/compare.json` |
| Sound −25.6 → −15.7 LUFS, true peak −10.3 → −1.3 dBTP | `qc/out/v8/sound_log.json` |
| 8 of 26 source clips contain long freezes | `qc/clip_metrics.json` |

## Regeneration, not storage

The MP4, WAV, models and logs live in untracked paths (`render-v8/`,
`qc/out/`, `qc/models/`). They are rebuilt by the commands in
`V8-CUT-REPORT.md`; the repo stores the code, the measurement JSON and the
report, not the media. `.gitignore` is a guard, not a security boundary —
already-tracked files and `git add -f` still bypass it.
