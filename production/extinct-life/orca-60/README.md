# Why Orcas Fear Humpbacks — the reference's first minute

60.00 s · 1280x720 · 30 fps · stereo 48 kHz · −14.3 dBFS

Drive: `1FeqbnCpxH5AuVcOly3VMeruy_8LMVzc1`

## What this is

A beat-for-beat rebuild of the opening minute of the reference video, not an
interpretation of the topic. The beat map in `timeline.json` was read off 62
one-second frames of the reference and every cut is where the reference cuts.

## Files

| file | what it is |
|---|---|
| `timeline.json` | 16 beats + 43 sound cues, each cue tagged with the beat it lands on |
| `sfx-cues.json` | the mixer's cue list only (time, cue, gain, pan, length) |
| `contact-sheet.jpg` | one frame every 3 s of the delivered cut |
| `../characters/*.jpg` | 8 character sheets, 6 poses each |

## Engines

| script | does |
|---|---|
| `scripts/orca-film.py` | the film: water, god-rays, particles, animals, camera, beats |
| `scripts/lib/creatures.py` | every contour, plus `profile()` which turns a top and a bottom edge into one closed bezier |
| `scripts/lib/shading.py` | gradient fills, rim light, hide streaks, depth of field |
| `scripts/sfx.py` | all 43 cues synthesised with numpy — nothing sampled, nothing licensed |
| `scripts/character-sheets.py` | renders the 8 sheets from the same creatures |

## Anatomy rule

The humpback's body, mouth, eye, pleats, baleen and flipper are all authored against
one contour in `creatures.py`. Each landmark is written down next to it. Before this
rule the baleen sat in front of the chin and the flipper was inside the belly,
because the details came from a different sketch than the body.

## Audio chain, and why it is two passes

Narration and SFX are mixed by ffmpeg to a lossless WAV, then gain-staged in numpy
with a tanh limiter, then muxed. Doing it in one ffmpeg pass does not work on this
build: the AAC encoder overshoots the limiter by about 4 dB, so a file that measures
−0.7 dBFS before encoding measures +1.4 after. The WAV ceiling is therefore set at
0.62 and the final file lands at 1.032 peak with one clipped sample.

## Fixes this cut carries

- humpback rebuilt against one contour (baleen, pleats, knobs, eye, fin all aligned)
- `unit_to_px` clamps, so a flipped bbox cannot invert an ellipse box
- `shaded_tile()` is the only way a blurred animal is made; the old inline version
  drew into a throwaway RGB copy and produced empty black boxes on beats 12-14
- patch masks take an int on `L` and a 4-tuple on RGBA
