# Extinct Life — The Lost World Inside a Handful of Dirt

Full English 16:9 **Amber Atlas 2.5D production cut**. Target/measured timeline: **450.633 seconds (7:30.633)**, 1920×1080, native 30 fps, **13,519 frames**.

Output: `deliverables/Extinct_Life_EP01_Amber_Atlas_Full_1080p.mp4`.

## Full-film scope

The approved 45-second Cinema Polish opening is followed by **eight new narrated sections and 40 newly staged body shots**, not a loop or stretch of the opening. Shared visual systems are deliberately reused for narrative continuity; this does not mean 40 unique environments. Scene timings are measured at chapter level; no word-aligned subtitles are claimed.

The body introduces moving plant specimens, conceptual pollen magnification, environmental transport, sediment/core sampling, fragmentary sequences, mineral binding, a schematic laboratory, reference matching/identification limits, illustrative fauna, evidence integration, approximate age and a closing reveal. Independent parts, wind, water, animal articulation, particle transport, layer movement, eased camera scale and short dissolves provide motion rather than acquired image pans.

Everything is interpretive motion illustration, **not photorealistic documentary footage**. Artwork is not anatomy-, botany- or locomotion-validated. The scientific/creative distinction is part of the film, not just this README. See `SOURCES.md`.

“Premium”, engagement and retention are production aspirations, not certified results. Owner approval of the complete film remains pending. No superiority over competitors or full real-time creative watch is claimed.

## Source files

- `narration.json`: exact eight new spoken scripts; existing opening remains separate.
- `narration/*.flac`: preserved lossless isolated new voice stems. Included intentionally to permit editing/reproduction without regenerating a voice.
- `voice-provenance.json`: original generated voice PCM hashes and durations; FLAC decoding was checked for exact equality.
- `prepare.py`: measures stems, builds timeline, synthesizes the original quiet score/air/material cues and assembles body sound.
- `timeline.json`: actual chapter/shot frames and narrative sequence.
- `stage.html`: shared Amber Atlas drawing/rig primitives; `scenes.js`: full-film-specific scene systems/compositor.
- `render.mjs`: native Skia rasterization and two-worker chapter rendering.
- `render-checks.json`: 40 out-of-order seek checks; same frame encoding after unrelated seeks.
- `finish.py`: opening/body assembly, full-film two-pass loudness normalization, chapter metadata, final decode and diagnostic/frame samples.
- `QC.json`: measurements of the actual final encode, generated after completion.
- `test_contract.py`: source/timing/media regressions, not a creative-quality score.

The final film's opening is re-encoded and its soundtrack normalized as part of the full mix; it is **not advertised as bit-identical** to the standalone opening. The rejected first full-film cut is not used. New narration uses the same selected `voice-00`, without new voice auditions.

## Reproduce

From the repository root, using Node 22 and Python:

```sh
npm install --no-save --package-lock=false --ignore-scripts @napi-rs/canvas@1.1.0
python3 -m venv .venv
.venv/bin/pip install numpy==2.4.6 pillow==13.0.0 imageio-ffmpeg==0.8.1
.venv/bin/python production/extinct-life/feature-25d/prepare.py
node production/extinct-life/feature-25d/render.mjs --stills
node production/extinct-life/feature-25d/render.mjs --verify
node production/extinct-life/feature-25d/render.mjs --all
.venv/bin/python production/extinct-life/feature-25d/finish.py
.venv/bin/python production/extinct-life/feature-25d/test_contract.py
```

Required system fonts: `/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf` and `DejaVuSans.ttf`. The previously delivered opening MP4 must be present. FLAC stems are decoded automatically if the runtime WAVs are absent. Runtime audio, chapter intermediates and preview sheets remain in ignored `.cache/extinct-feature/`. No scene footage or remote font is fetched at render time. The HTML is authoring source; the native render is authoritative, not a browser pixel-match guarantee.

Each chapter can also be rendered explicitly with `--chapter 0` through `--chapter 7`. Re-render affected chapters after any source change; do not reuse stale intermediates from different sources. Final H.264/AAC distribution compression is separate from native frame drawing. Frame interpolation is not used.

## Review limits

All 40 body-shot native previews are inspected for layout, with spot checks at full resolution. The final audit decodes all frames, measures encoded audio, checks black/freeze diagnostics, samples the final encode twice per second and produces 20 review frames covering all chapters/opening/closing. Low-motion conceptual/coast holds are disclosed in QC; a freeze diagnostic is not silently removed or called a creative score. These checks do not establish biological precision, audience response or absolute perfection.

No YouTube upload/scheduling, paid rendering service or external GPU allocation is authorized or performed. The prior cuts remain intact.

## Completed delivery checks

Final file: **69,864,240 bytes**, **450.633 seconds**, **13,519 fully decoded frames** at 1920×1080 / native 30 fps. Encoded audio measures **−16.11 LUFS / −1.35 dBTP**. No black intervals were detected. All **901 half-second decoded samples are distinct**. Low-motion freeze diagnostics remain recorded for coast and settled explanatory holds. Forty native shot previews and twenty final-encode samples were inspected; all six regression tests pass. This is not a claim of a full real-time audiovisual watch, anatomical validation, audience testing or absolute perfection.

The first assembly's duration cutoff dropped one frame. Final assembly now rebuilds exact frame-index timestamps with `setpts=N/(30*TB)` and passthrough frame synchronization, rather than stretching/interpolating frames or hiding the count mismatch. Final decoded count matches all source frames.
