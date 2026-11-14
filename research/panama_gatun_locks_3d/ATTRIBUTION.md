# Attribution and production notes

Project: *This ship is about to climb a mountain* — the original Gatun Locks (Panama Canal)
Format: 1080 x 1920 vertical, 30 fps, 47.0 s, English narration
Status: **private review cut** — not published anywhere.

## How it was made (full disclosure)

There is no Blender, no GPU, no game engine and no downloaded 3-D asset in this piece.

- **Geometry, camera, lighting, rasteriser**: written for this project in NumPy
  (`build_video.py`, ~1150 lines). It is a small software renderer: a z-buffered
  triangle rasteriser with perspective-correct attributes, flat/per-vertex shading,
  an analytic sun with cheap ray-marched wall/gate shadows, a wet waterline band,
  procedural surface variation, a height-field water shader with Fresnel sky
  reflection and a sun glint, then a film-style grade (ACES tonemap, bloom,
  split-tone, vignette, grain).
- **Camera**: nine hand-authored beats, each solved numerically so its subject fits the
  9:16 frame; no third-party camera rig or motion capture.
- **Narration**: synthetic voice (Arena.ai speech synthesis), written for this piece.
  It is a generated voice, not a human recording, and it is not a clone of any
  identifiable person.
- **Captions**: generated from the narration audio by forced alignment (`align.py`),
  typeset in **Manrope** (SIL Open Font License 1.1), already present in this repository
  at `public/showreel/fonts/Manrope-800.ttf`.
- **Sound effects**: all from this repository's own DSP kit (`audio/takes/*.wav`,
  generated for this repo with `tools/sfx_takes.py`) — no commercial sample packs, no
  film audio, nothing ripped from anywhere. The music bed, the water movement layer
  and the machinery hum are synthesised in `build_audio.py` from sine partials and
  filtered noise.

## Assets and licences

| Asset | Source | Licence / status |
|---|---|---|
| Geometry, shaders, renderer | original, this project | original work |
| Narration | synthetic voice, generated for this project | original recording, generated |
| Music bed / water / hum | synthesised in `build_audio.py` | original work |
| Sound effects | `audio/takes/*.wav` in this repository | generated for this repo |
| Manrope typeface | repository copy | SIL Open Font License 1.1 |
| Terrain, water, sky | procedural, generated at render time | original work |

No third-party photographs, video, textures, models or music are used. Nothing here is
attributed to an outside creator because nothing outside this repository and the
Panama Canal Authority's published description (facts) was used.

## Facts

See `FACT_CHECK.md` for the claim-by-claim source mapping and the list of deliberate
simplifications (sectioned near wall, single lane, compressed fill times, stylised
proportions).

## Capability notes (what this is and is not)

- It is **genuine 3-D**: real geometry, real camera moves, real lighting, animated
  gates, ship and water — not a still image with a zoom.
- It is **not** path-traced and **not** a fluid simulation: shadows are analytic, water
  is a height field, and there is no global illumination. It reads as a stylised
  engineering explainer, not as photoreal footage.
- Animation, narration, captions and sound effects all come from one shared timeline
  (`state(t)` for the animation, `audio/align.json` for the captions, and the same
  caption ids drive the sound cues).
- Rendered at a native 1080x1920, 30 fps. No frame interpolation, no upscaling.

## Human review still required

1. **Watch it end to end at full size** — pacing, caption legibility on a phone, and
   whether any beat feels too long or too fast.
2. **Listen with headphones** — voice level against the bed, and whether any sound
   effect reads as too "synthetic".
3. **Fact check sign-off** — `FACT_CHECK.md` should be read by someone who knows the
   canal; the claims are sourced, but the simplification list should be accepted as
   acceptable for the intended audience.
4. **Look at the geometry honestly** — it is a stylised model. If it needs to read as
   photoreal, this renderer is the wrong tool and the piece should be rebuilt in a real
   DCC package on real hardware.
5. **Decide on publication** — nothing has been uploaded anywhere.
