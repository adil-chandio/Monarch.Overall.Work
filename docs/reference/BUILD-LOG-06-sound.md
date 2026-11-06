# BUILD-LOG 06 — the sound of v5-35

The picture was approved (v5-34). This log is the audio pass only: the picture is not
touched — every frame is copied, and the muxed file's per-frame md5 list is identical to
v5-34's.

## What was available

The three tools the brief names were checked first:

| tool | reachable | what happened |
|---|---|---|
| **earshot** (github.com/Leonxlnx/earshot) | yes, via `codeload.github.com` | source tarball, CPU-only, run with `PYTHONPATH=/tmp/esrc/earshot-main python3 -m earshot`. Its **252-sound bank** and its `kit` presets (`calm / crisp / launch / minimal`) are the effect source. |
| **Openverse** (5M+ free audio) | **no** | `docs.openverse.org` and `api.openverse.org` are not in the sandbox's allowlist. |
| **Real SFX** (clipping.pro) | **no** | same. |

So every sound in this film is **synthesised in code** — earshot's forge bank for the
effects, our own DSP for the music bed — which is also what the brief asked for
("automatic / scripted, not hand-edited").

`pip install earshot` is the wrong package (a Rust VAD binding by another author); the CLI
comes from the GitHub tarball.

## The reference's own numbers

The reference was measured, not copied: its soundtrack over its quiet passages, and its
spectrum, are the target the mix is graded to.

| | sub 20–120 | low 120–400 | mid 400–1.5k | hi 1.5–5k | air 5–16k | loudness | peak | crest |
|---|---|---|---|---|---|---|---|---|
| reference | 5.9 % | 20.5 % | 34.0 % | 13.4 % | 25.5 % | −14.1 LUFS | −0.3 dBFS | 15.5 dB |
| **v5-35 mix** | 8.1 % | 21.6 % | 32.7 % | **10.1 %** | 23.9 % | **−14.0 LUFS** | −1.0 dBFS | 15.4 dB |

Note the hi band: the reference is already fairly bright, and this mix is **3.3 points
quieter there**. That is the deliberate answer to "kaan ko chubne wale nahi" — the band
that produces sibilance and fatigue is the one that was held back, while the air above it
was lifted so the top still sounds open.

## The cue sheet

Cue times are the measured cuts from `analysis/v4-build/shots.json`, not a feel:

| cue | picture event | role | sound (earshot bank) | where its sync point sits |
|---|---|---|---|---|
| 0.000 | cut in | `swell` | `reverse_swell/dark` | peak 30 ms before the cut |
| 0.170 | first type glyph | `tick` | `pro_hover_tick/ping` | on the glyph |
| 0.370 | type progression | `tock` | `knock/wood` | 25 ms before |
| 0.533 | cut | `hit` + `whoosh.short` | `cut_hit/punch`, `whoosh_fast/crisp` | onset on the cut, whoosh peaks 110 ms after |
| 0.800 | cut | `whoosh.long` | `whoosh_big/thump` | peak 60 ms after the cut |
| 1.060 | land | `drop` | `cut_hit/kick` | on the land |
| 1.333 | cut | `whoosh.short` + `hit` | as above | same rule |
| 1.900 / 2.060 | type beat + slam | `tock` / `hit` + `sub` | `knock/wood`, `sub_drop/punch` | on the beat |
| 3.133 | red room in | `swell` + `hit` | as above | peak before, onset on |
| 4.600 / 6.100 | type beats | `bell` | `mallet/glock` | on the beat |

Every level is **over the bed at that moment**, the way earshot's kit defines it: the
take's loudest 50 ms against the music's median 50 ms in the half-second before the cue.
Nothing is set by ear; the same script re-derives it on any length of film.

## The bed

`tools/music_bed.py` writes the music as numbers: a D-minor pad (i – VI – III – VII, two
bars each), a soft 96 BPM pulse felt rather than heard, a filtered air layer, and a quiet
pluck motif. Then a **six-pass static EQ** moves its band shares onto the reference's
(one pass cannot converge — cutting the sub hands its share to the bands above). It
converges to within 4 % of target.

The bed is then **ducked 7.5 dB for 340 ms** under every hit, drop and long whoosh, with
smoothed edges, so the hits are felt instead of fought.

## Chain

```
tools/music_bed.py  → audio/bed-7.wav        (band-graded to the reference)
tools/mix.py        → audio/mix-7.wav        (17 cues, l50 gain model, duck, air polish, limiter)
ffmpeg -c:v copy    → public/demo/v5-35-sound.mp4
```

Verified: −14.0 LUFS integrated, −1.0 dBFS sample peak, 15.4 dB crest, RC128 LRA 1.5 LU,
0 decode errors, 210/210 frames byte-identical to v5-34.

## Open

- The picture is still **0–7 s** of a 23.3 s edit (`spec/v5-01.json` covers s1–s5 only).
  Cues for s6–s13 are already listed in the shot table and just need their cue lines added
  once the picture reaches them.
- `public/demo/v5-35-sound.mp4` is the same seven seconds with sound; nothing after 7 s.
