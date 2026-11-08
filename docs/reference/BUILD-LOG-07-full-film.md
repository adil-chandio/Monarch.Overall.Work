# BUILD-LOG 07 — the whole edit, 0.000 s to 23.267 s

`tools/v5.py` built the first seven seconds and proved the camera, the room and the type.
This log covers `tools/v6.py`, which fills the **entire** reference edit with our own
plates, and `tools/film_score.py` + `tools/mix.py`, which give it twenty-three seconds of
score and a cue sheet on every cut.

## What changed, and why

| | v5-34 (approved) | v6-11 |
|---|---|---|
| length | 0.000–7.000 s (s1–s5) | **0.000–23.267 s, all thirteen shots** |
| frame count | 210 | **698** at 30 fps |
| sound | none | 77 cues + 23 s score, −14.7 LUFS, −0.5 dBTP |

## The plate problem, solved shot by shot

The reference's shots are *macros and wides* of objects; ours arrive as full-frame plates.
Covering the frame with a plate is what made earlier versions read as a different edit, so
each shot's framing was rebuilt from the plate's own content:

- **s3 / s10 (the green macro).** Our plate has the packet centred; the reference crops it
  at the left and bottom edge, huge. The packet is now drawn at 600–760 px wide, anchored
  off-frame, with a soft cast shadow on the field, and the headline is set inside the frame
  (the reference's own 650 px ink width is 90 % of the frame, which cannot be reproduced
  without clipping, so it is set at 528 px and both copies kept whole).
- **s4 / s11 (the storm wide).** The plate is a medium shot. `wide_storm()` rebuilds the
  frame from the plate's own sky, then places the stool back into it at 0.80–0.88 scale,
  bottom-anchored and feathered at the top, so the shot reads as the reference's wide
  instead of a zoomed medium.
- **s5 / s6 / s12 / s13 (the red room).** The pair's *back* plate is no longer drawn. The
  wall is drawn here instead, so drawing the plate's wall on top of it doubled every
  vignette (that banding was the last artifact in v5's look). What is kept is the part worth
  keeping — the front layer at its exact authored offset (`hero_only()`), a warm bounce
  behind the silhouette, and a contact shadow on the floor.
- **the baked red smear.** Our hero plate carries an out-of-focus red patch beside the
  head, baked into its grade. Over a rebuilt wall it read as a drawing. `defog_front()`
  removes it by two tests that both have to hold — no detail at any scale the man has, and
  red with almost no green — and fades those pixels toward the wall instead of cutting them,
  so no edge appears.
- **the hands.** Our red plate has hands holding cash; the reference has hands holding cash.
  The layer is not pasted as a rectangle: `fingers_only()` cuts the warm, detailed pixels,
  `drop_green_cells()` kills the plate's own green marker, `despill()` pulls the key's green
  out of the edge, and `oval_fade()` has no straight side. Moved around the room at its own
  depth, it can never bring its background with it.
- **the graphic furniture.** Not a set of nested boxes (that read as a window): one tilted
  card outline, one chevron half out of frame, one green cell, all at the wall's depth so
  the camera slides them against the man. Bright strokes, not fills.

## Every shot, and what it is built from

| shot | time | framing built from | type |
|---|---|---|---|
| s1 | 0.000–0.533 | fitted plate surface | TWENTY, ink 164 px at (128, 591) vs the reference's 168 at (132, 599) |
| s2 | 0.533–0.800 | gradient card | BILLION slam, TWENTY small |
| s3 | 0.800–1.333 | green field + cropped packet | BILLION + rotated ghost copy |
| s4 | 1.333–3.133 | `wide_storm()` | HE → NO |
| s5 | 3.133–9.167 | drawn wall + hero + hands | 2008 behind |
| s6 | 9.167–11.733 | same, tighter | lens glow, subscribe card |
| s7 | 11.733–12.200 | fitted plate surface | TWENTY, ink 162 px vs 169 |
| s8 | 12.200–12.500 | gradient card | BILLION skewed |
| s9 | 12.500–12.700 | our macro plate | — |
| s10 | 12.700–13.000 | macro + packet + field | BILLION + ghost |
| s11 | 13.000–14.833 | `wide_storm()` | HE, HE SAID, NO |
| s12 | 14.833–20.633 | drawn wall + hero + hands | 2008, chevrons |
| s13 | 20.633–23.267 | drawn wall + hero, dolly out | flash, SUBSCRIBE card |

## Measured against the reference

`tools/match_ref.py` finds the type in both films by the same rule and reports the
difference in its ink box, then fits an affine between the two frames:

| shot | ink dx | dy | dw | affine scale | rotation |
|---|---|---|---|---|---|
| s1 | −4 px | −8 px | −4 px | 0.983 | 0.0° |
| s2 | +8 | +44 | +28 | 0.989 | +0.6° |
| s7 | −2 | −21 | −7 | 1.045 | +0.1° |
| s8 | +161 | +55 | +20 | 1.033 | −1.3° |

s8 is mid-transition in the reference (its `BILLION` is still sliding), so its box is not a
fair target. s3, s4, s10 and s11 are excluded from the mean: their ink rules pick up the
packet's dark leather and the red set, so the boxes merge and do not measure the word.

## The score

`tools/film_score.py` writes twenty-three seconds of music as a **list of sections**: chord,
intensity, groove and pattern. The arrangement is ours (D minor, i–VI–III–VII with a
turn-through-C at the loop), and no reference audio is used — only measured numbers:

- the reference's **spectrum**, as the target every band is moved onto;
- the reference's **loudness arc**, in one-second windows (−14.7 dBFS at 0 s, −13.6 at the
  subscribe, −12.9 at the CTA, −18.6 in the quiet between) applied to our own music as a
  slow gain, so the film breathes where the reference breathes;
- the reference's **cut alignment**: taps lead cuts by 20–60 ms, whooshes peak 60–110 ms
  after them — the same rule the cue sheet uses.

## The cue sheet

77 cues, every one on a measured event: the thirteen cuts from `analysis/v4-build/shots.json`
and the sixteen transients the reference's own edit puts inside its first three seconds.
Bed ducks 7.5 dB for 340 ms under each hit, so the hits are felt instead of fought.

| | reference | v6-05 |
|---|---|---|
| integrated loudness | −14.0 LUFS | −14.7 LUFS |
| true peak | −0.3 dBTP | −0.5 dBTP |
| loudness range | 1.9 LU | 2.5 LU |
| sub / low / mid / hi / air | 8.5 / 21.5 / 30.0 / 15.2 / 24.4 % | 10.5 / 23.1 / 29.1 / 13.0 / 22.3 % |
| 2–5 kHz (sibilance) | 11.5 % | 9.6 % |

The hi band stays under the reference's on purpose — that is the band that makes a film
tiring to listen to, and the brief asked for the opposite.

## Chain

```
tools/v6.py --spec spec/v5-02.json --out public/demo/v6-04.mp4          # 698 frames, ~10 min
tools/sfx_takes.py    -> audio/takes/*.wav            (16 earshot bank sounds, 48 kHz)
tools/film_score.py   -> audio/bed-23.wav             (sections, arc, band-graded)
tools/mix.py          -> audio/mix-23.wav             (77 cues, duck, band match, arc, TP limit)
ffmpeg -c:v copy      -> public/demo/v6-11-final.mp4
```

## Open

- s2's type sits 44 px low and 28 px wide against the reference; s7 21 px high. Both are a
  single number each in `tools/v6.py`.
- The reference's s10 macro is tighter than ours; our macro plate's focus falls off sooner.
- Nothing in this build uses a reference frame, a reference asset, or a reference audio
  sample; the reference is read only for measurements (shot table, ink boxes, spectrum,
  loudness arc, transient times).

## The glitch pass (second review)

The first full build passed its numeric checks and still looked wrong frame by frame. What
was actually broken, and what fixed it:

| what it looked like | cause | fix |
|---|---|---|
| the macro shots were **soft everywhere** | `wide_storm()` blurred the whole frame to hide where the plate ended | the plate is now native-resolution; the rest of the frame is filled by **reflecting the plate's own edge** (`BORDER_REFLECT_101`), so there is no join to hide |
| `s8`'s green BILLION reappeared on `s10`'s notes | `render_frame()` called itself for the dissolve source, so a short shot absorbed the *previous* shot's dissolved frame (s8 → s9 at 0.5 s inside a 0.2 s shot → s10) | the dissolve source is now the previous shot's **own** frame (`_draw()`), and s9/s10's dissolve durations were cut to fit inside their shots |
| `TWENTY` and `BILLION` overlapped in `s2` | the two words were laid out independently | `BILLION` starts where `TWENTY` ends |
| a red-lit **blob** of hands on the wall | the hands layer carried the plate's red set through a patchy matte | the hands are cut as objects and graded down 0.62 with desaturation, so they read as a dark foreground detail |
| a stray olive square on his chest | the wall's green marker drawn at the wrong depth | removed |
| the card covered his face | 430 px wide at 80 % opacity | 268 px at 62 %, low in the frame, like the reference's |

Verified on the delivered file: 698/698 frames, 0 black segments, 0 decode errors, muxed
video byte-identical to the master, and **all 13 cuts have a hit within 53 ms** (median 8 ms).
