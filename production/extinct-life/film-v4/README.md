# V4 — continuous-flow revision requested after viewing v3

The user liked v3 but rejected its repetitive setups, repeating action loops and frequent cuts/splits. **This new instruction supersedes the previous ≤3-second-shot rule.** The target is evolving action and a continuous visual journey, not a higher cut count.

## What actually changed

- **18 story-led continuous sequences**, replacing the old 181 forced coverage windows. The 181 windows remain only as a narration audit; they do not choose camera angles or trigger edits.
- Absolute-time Hermite camera tracks with continuous position/velocity. Three same-stage chapter handoffs are also joined rather than edited back into another similar set. No modulo-five camera angle selection, no three-second coverage reset and no chapter-time actor reset.
- Same-stage changes happen inside one physical environment, with smoothly interpolated fragment/specimen actions. Cross-scale/world changes use full-frame, eased focus bridges, not split screens, wipes or instantaneous hard cuts. This is **not a claim of one literal unbroken real-life camera shot**.
- Every narrative sequence has a unique deterministic set seed **and a physical treatment**: opening dry clearing, deadwood bank, open river terrace, reed-margin delta, different gravel topography, exposed mineral ledges, circular sample racks, angled slide holders and extraction rails. Required returns do not replay a previous rendered clip. Repeated scientific subjects and shared animal/material models still exist; seed uniqueness alone is not proof of perceptual originality.
- Animal root motion traverses/browses one way instead of oscillating back and forth. The imagined delta has one takeoff event that continues across spoken phrases; it does not reset the goose at each new sentence. Evidence inspection and reference alignment progress once instead of spinning on a short loop. Natural gait/wing beats and wind remain cyclical physical motions, not recycled video clips.
- A newly arranged chapter-specific original synthesized score, with more space and different melodic contours, replaces the fixed four-note/8.4-second pattern. Environment ambience spans whole sequences with soft tails, instead of restarting on every sentence. Foot contacts, granular handling, a single flight and pipette delivery remain motivated, not transition whooshes.
- The approved English narration, script, duration and scientific qualifiers are unchanged: natural voice `voice-02`, **7:18.77 / 13,163 frames / 1080p30**. No fresh audition, hidden speed change or old MP4 reuse.

## What is not claimed

This remains stylized illustrative 3D, not photoreal ancient footage, a calibrated molecular simulation, a recovered encounter or an exact animal portrait. The clay albedo is the AI-generated asset from the approved proof; its bump is a derived image, not measured height. Original animal/material source reuse is disclosed; old rendered footage is not used.

The music/foley are synthesized originals, not a recorded orchestra or a licensed premium track. No guarantee of perfection, hypnosis, virality, retention or owner creative approval is made. Mathematical tests, unique seeds, stills and hashes do not establish that every scene is interesting or that the final sound is subjectively premium.

## Checks and reproduction

```sh
python production/extinct-life/film-v4/build_plan.py
node production/extinct-life/film-v4/direction.test.mjs
.venv/bin/python -m unittest discover -s production/extinct-life/film-v4 -p test_revision.py
node production/extinct-life/film-v4/render.mjs --chapter=0 --stills
# Eight full native chapter encodes, or the sixteen exact frame ranges in Actions:
node production/extinct-life/film-v4/render.mjs --chapter=0
.venv/bin/python production/extinct-life/film-v4/finish.py
```

The camera test evaluates all 13,163 frames. On this revision it checks 190 old within-sequence beat boundaries without a camera reset, unique designs/seeds, complete coverage, bounded per-frame camera displacement and acceleration. It is not a perceptual-quality score. Shared model source is served under `/shared/`; shared approved narration under `/voice/`. Render caches and generated pictures/audio stay in ignored `.cache/extinct-v4/`.

Local representative native scene generation and A→B→A deterministic seeks have passed for chapters 1, 3, 5, 6 and 7. A real 45-frame native-motion range across an old cut boundary has also encoded. Audio-only assembly has run; `audio-work-check.json` records the limited scope of that test. The new score is raised and measured at the intended background level rather than leaving the old bed roughly 30 dB under the voice; its measured stem RMS is −36.16 dBFS versus the mixed dialogue-led track at −20.91 dBFS. Smooth attack/release dialogue ducking avoids sentence-by-sentence level steps. Full v4 MP4 completion is **not yet claimed**. The separate `extinct-film-v4.yml` workflow renders all frames, assembles, measures loudness and decodes the final file before publishing a clearly labelled candidate prerelease. It does not upload to YouTube.

The earlier completed v3 remains historical: https://github.com/adil-chandio/Monarch.Overall.Work/releases/tag/extinct-life-v3-42224196920 . It is not the corrected v4 download.
