# Celebrity morning — 2D animated cut (v1)

A 60-second portrait film, 1080×1920 at 24 fps, built as a **2D painted cut-out
animation** rather than a 3D render. Same script, same narration takes, same cue
timings as the 3D version; everything visual is new.

**Deliverable:** `deliverables/monarch-celebrity-story-2d.mp4`
(60.0 s, 1080×1920, 24 fps, H.264 + AAC, 29 MB, SHA-256 `72362103…4018f`).

## Why 2D

The 3D cut was limited by its assets: a game-grade avatar with no sit pose, no
lip sync, low samples and dozens of render hours. Painted 2D plates remove those
ceilings — the art carries the quality, and the code controls light, camera and
timing. It also renders here in about 25 minutes instead of hours, so every frame
gets checked before delivery.

## How it is made

| Layer | What it is |
| --- | --- |
| Backgrounds | Six painted plates (bedroom dawn, kitchen, street, barrier, night interior, plus the bedroom re-used for the window beat), generated at 9:16 and cached at overscan size. |
| Characters | Four painted cut-outs on flat chroma green, keyed with a soft matte, despilled at the edge, then placed and deformed in code. |
| Camera | Every shot declares a start/end pan, tilt and zoom with a hand-held jitter term; slow push-ins and drifts give the stills motion. |
| Light | Volumetric shafts from windows, bloom, halation, per-act grade (warm dawn, cool street, cold night), vignette, film grain. |
| Captions | Burned in, timed to the voice: they fade in a fifth of a second after each line starts and out before it ends. |
| Sound | Narration takes at their cues, a three-section pad score, room tone, street wash, crowd murmur, and foley (shutters, footsteps, door, pour) placed from the same cue table. |

The whole film renders in one pass: `film2d.py` composites and pipes raw frames
into ffmpeg, then `mix2d.py` lays the sound and normalises to −16 LUFS.

```sh
python showreel/celebrity_story_2d/film2d.py --out /tmp/silent.mp4
python showreel/celebrity_story_2d/mix2d.py /tmp/silent.mp4 out.mp4
```

To re-render a single beat while iterating:
`film2d.py --t0 34 --t1 40 --still /tmp/check.jpg`

## What is verified, and how

- **Every shot** was reviewed as a frame probe at its midpoint before the final
  render; the crowd was repositioned, the mug insert re-cropped and the reach
  beat given real movement as a result.
- **Picture/voice sync** comes from one source of truth (`script.json`, built by
  `build_narration.py` from the recorded takes), not from hand-placed subtitles.
- **Audio** was measured, not assumed: integrated loudness −16.3 LUFS, true peak
  −0.9 dBFS, no clipped samples, and speech sits in every act with the intended
  gap at the cut to black.

## Honest limits

- **The characters are single painted poses.** Motion is camera movement, drift,
  breathing and parallax plus edge deformation — not frame-by-frame animation.
  There is no walk cycle in this cut and no lip sync; mouths are closed painted
  art. A hero walk would need a second painted pose per step.
- **Cut-outs read as cut-outs.** Against painterly plates they sit slightly
  "pasteded-on"; a rim light pass and contact shadow soften it but do not remove it.
- **Coverage is thin**: fourteen shots for sixty seconds means some beats hold a
  single composition for four to eleven seconds.
- **Backgrounds are generated art**, consistent in palette but not painted by a
  human; small details (a stanchion base, a window mullion) do not always match
  the adjacent plate.
- **The voice is synthetic** and the score is oscillator-based, as in the 3D cut.
- The on-screen mark reads FICTIONAL; the character is not a likeness of any real
  person.

## Files

| Path | Purpose |
| --- | --- |
| `core2d.py` | Gradient/mask primitives, light shafts, bloom, grain, grade, captions. |
| `cutout.py` | Chroma key, despill, matte trim, placement, contact shadows, limb shear. |
| `film2d.py` | Scene/character model, camera, per-shot compositing, frame streaming. |
| `acts.py` | The edit: 14 shots with framing, camera moves and grades. |
| `mix2d.py` | Score, ambience, foley placement, narration assembly, loudness. |
| `assets/` | The painted plates and cut-outs this cut was built from. |
