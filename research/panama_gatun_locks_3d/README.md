# Gatun Locks — 3D vertical explainer (private review cut)

**Deliverable:** `Gatun_Locks_3D_1080x1920_30fps.mp4`
1080 × 1920, 30 fps native, 47.00 s, H.264 High + AAC 48 kHz mono, 52.3 MB.

A 47-second vertical explainer on the *original* Gatun Locks of the Panama Canal:
a ship climbs 85 ft in three steps, lifted only by water — no pumps, no engines.

## What is in this folder

| File | What it is |
|---|---|
| `Gatun_Locks_3D_1080x1920_30fps.mp4` | the cut |
| `QC_CONTACT_SHEET.png` | 13 frames sampled from the encoded file, 1 per 4 s |
| `FACT_CHECK.md` | every claim mapped to a source, plus the disclosed simplifications |
| `ATTRIBUTION.md` | how it was made, asset/licence table, what still needs a human |
| `build_video.py` | the renderer: scene, 9 camera beats, shading, rasteriser, grade, captions |
| `align.py` | forced alignment of the narration -> 43 caption cards |
| `build_audio.py` | narration + synthesised bed, water layer, machinery hum, cue list |
| `render_part.py`, `assemble.py` | parallel render + concat/mux |
| `audio/align.json`, `audio/mix.wav` | caption timings, final 47 s mix |

## How it was built

No Blender, no GPU, no WebGL, no downloaded model. `build_video.py` is a small
NumPy software renderer written for this piece: z-buffered triangle rasteriser with
perspective-correct attributes, analytic sun shadows, a wet waterline band, a
height-field water shader with Fresnel sky reflection, procedural surface variation,
ACES tonemap + bloom + split-tone grade, then caption cards drawn with Pillow.

Two workers rendered 705 frames each at ~2 s/frame; roughly 50 minutes wall clock.

## Honest limitations

- Stylised model, not photoreal: no path tracing, no fluid sim, no textures.
- The **near lock wall is sectioned** to a 1.15 m kerb so the camera can see into
  the chamber (standard cutaway convention, disclosed in `FACT_CHECK.md`).
- Only one lane of the three-pair flight is modelled; fill times are compressed.
- Narration is a synthetic voice; it is labelled as such in `ATTRIBUTION.md`.

**Nothing has been uploaded or published.** Private review only.
