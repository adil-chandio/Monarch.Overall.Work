# EP01 production — handoff

**Picture is 97 shots / 515.0 s (8:34). VO is 10 of 11 reels, fitted to 493.6 s. Mix is 515.0 s.**
Everything here is reproducible from this folder.

## What is finished, and what is not

| Item | State |
|---|---|
| Fact-checked script (1,567 words) | **done**, `../EPISODE_01_RETENTION_SCRIPT_V3.md` |
| Shot list, 50 beats → 97 renderable shots | **done**, `shots.py` + `out/timeline_ext.json` |
| Keyframe art direction, 36 plates specified | **11 of 36 generated** (`out/kf_*.png`) |
| Camera moves, grain, letterbox, burn-ins | **done**, `render_key.py` |
| Picture assembly, 515 s | **done**, `out/picture_full.mp4` |
| VO, 10 of 11 reels | **done**, `vo/vo_01..10.mp3` — reel 11 missing |
| Sound bed: ambience, torch, wind, risers, sub-booms, score, reverb | **done**, `build_audio.py` |
| Mix, 515 s stereo | **done**, `out/mix.m4a` |
| Final 1920×1080 with audio | **done**, `out/EP01_bear_PROOFCUT_11plates.mp4` |

**Not done, and cannot be done honestly in one pass:** 25 keyframes are still missing, so those
shots currently borrow the nearest hero plate through `FALLBACK` in `build_film2.py`. That is a
proof cut, not a finished film. The cut is complete and watchable end to end; the coverage is not.

## To finish

1. Generate the 25 remaining plates. `python3 gen_keys.py` prints the exact prompt for each.
2. `rm -rf out/segs2 && python3 build_film2.py` — re-renders, ~20 min.
3. Record reel 11 (`vo/vo_11.txt`, the closing 140 words) or paste it into `generate_speech`.
4. `python3 build_audio.py` — re-fits VO and rebuilds the bed.
5. Final mux, the command is in `RUN.md`.

## Honest limits of this pipeline

* **Camera moves are 2.5D.** Push/pull/drift/shake on a still plate. There is no parallax,
  no new geometry, no character animation. A real 3D character pipeline needs a GPU; this
  box has 2 cores and 3 GB, and the numpy point-splat renderer in `engine.py`/`film.py`
  (kept, working, but not used in the cut) cannot reach film quality at any speed that fits here.
* **Nothing moves inside the frame.** Dust, breath, fur, water and fire are baked into the
  plates. Adding motion would need per-plate particle passes.
* **The plates are AI-generated stills.** They are art direction, not photography, and they
  are not evidence. Every factual claim in the film sits on the script's source list, not on
  the pictures.

## Cue sheet

65 cues from `beats.py`: a whoosh on every cut, a sub-boom on the nine stated beats,
a riser into five of them, a tick on text cards. Score is one drone chord per chapter,
ducked from 8:27 to the end so the last line lands in silence.
