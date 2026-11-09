# Homotherium — premium polish of the selected 2D fast-cut Short

Selected original: `d61ed05`. Immediate edit base: clean fast-cut delivery `684d611`. This version preserves the user's no-3D direction, 46-second standalone English script, 35 shot intervals and short readable captions. Previous exports remain unchanged. No YouTube publication.

## What changed

- Replace the earlier simpler beat/bed with an **original instrumental score**: 116 BPM, soft D-minor / B-flat / F / C harmony, bass, restrained plucked motif, short percussion, small stereo echo and a controlled build. Not an externally licensed stock track or competitor audio. The generated score is synthesized from original code with a fixed seed, not produced by the speech tool.
- **11 selective SFX events**, not effects on every cut: seven soft stereo sweeps with rounded low impacts at chapter changes, four quiet tactile detail accents. No animal vocalizations, awakening sound or fake recovery-site field recording.
- Centered unchanged-speed narrator, light rumble filtering, speech-aware lookahead music ducking, smooth release and final loudness normalization. Audio is newly mixed from the original continuous selected narration and retained phrase edit map—not stacked over the previous mastered soundtrack.
- **Seven four-frame transitions** (0.133 seconds) soften selected chapter changes; the other fast feature cuts remain crisp. Only the image region blends: captions do not ghost/double-expose across transitions. No full-screen flashes or long slow dissolves.
- Light rounded masking on detail crops removes harsh rectangular corners. Screen remains uncluttered: source evidence, short captions and locally necessary qualifiers; no branding/header counters, decorative particles, 3D scenes or information-card pile-up.

This is an incremental audiovisual polish, not a claim that a subjective “premium/top-notch” quality bar can be proven by tests or that performance is guaranteed. All 35 shot intervals still use the same underlying licensed evidence set, not 35 unique discoveries or environments.

## Scientific provenance and limits

Lopatin et al., *Mummy of a juvenile sabre-toothed cat Homotherium latidens from the Upper Pleistocene of Siberia*, Scientific Reports 14, 28016 (2024), https://doi.org/10.1038/s41598-024-79546-1 . Figures 2, 4 and 7 under **CC BY 4.0**, https://creativecommons.org/licenses/by/4.0/ . Images are cropped, white-background-separated, resized and composited; anatomy is not retouched. Original source files/hashes and rights basis: `../homotherium-short/SOURCE-LICENSE.json`. Derived crops: `../homotherium-short/ASSET-EDITS.json`.

The published CT-based model is partly reconstructed by mirroring the undeformed right side. It stays a labelled flat source image, not our own scan or volumetric production scene. Comparing the cub and similar-aged lion photos illustrates qualitative reported contrasts, not display-size measurements; comparison panels explicitly note different display scales. These are dead, partial preserved remains, not a whole intact living cub, awakening or de-extinction. The specimen was found in 2020 and described in 2024; calibrated dates: 35,471–37,019 cal BP. Approximate three-week age is estimated from dental development. The script retains incomplete-mummy and uncertain-reconstruction caveats. “Survivor” means preservation. Homotherium is not Smilodon or a true tiger.

Flat map: Natural Earth 1:110m land (public domain), https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_land.geojson . Approximate locality: 67.6872 N, 146.7703 E. Not recovery-site footage.

Narration: selected synthetic `voice-04`, unchanged words and speed; original file and provenance retained in `../homotherium-short/source/narration.flac` and `../homotherium-short/VOICE-PROVENANCE.json`. `AUDIO-EDITS.json` preserves the same silence-tightening source-to-destination map. `English.srt` is unchanged from the clean edit; phrase-based caption subdivisions are editorial, not certified word-level ASR alignment.

## Rebuild

```sh
.venv/bin/python production/extinct-life/homotherium-premium/film/prepare_sound.py
node production/extinct-life/homotherium-premium/film/render.mjs
.venv/bin/python production/extinct-life/homotherium-premium/film/validate.py
```

Requires existing repository Chromium/Node/Python dependencies and typefaces. Source images reuse the preserved original assets. Native 1080 × 1920, 30 fps, 46 seconds / 1,380 frames. Original score, SFX stems and intermediates remain in `.cache/homotherium-premium`; synthesis is reproducible from `film/prepare_sound.py`. No third-party music samples or competing YouTube clips/audio used. GitHub delivery only; no YouTube publication authorized or performed.

## Reusable publication attribution

Research and photographs/CT reference: Lopatin et al., Scientific Reports 14, 28016 (2024), https://doi.org/10.1038/s41598-024-79546-1 . Figures 2, 4, 7: CC BY 4.0, https://creativecommons.org/licenses/by/4.0/ ; cropped, background-separated, resized and composited. Map: Natural Earth (public domain). Original synthetic instrumental score, sound design and synthetic narration. The published CT model is partly reconstructed; comparison photographs are not at a shared measurement scale. These are partial preserved remains, not a resurrected animal. No new scientific measurement is claimed.

## Delivery verification

File: `deliverables/Homotherium-Cub-Premium-Fast-Cut-1080x1920.mp4`, 12,665,119 bytes. SHA-256: `be1a2c936fb00518c9a900b2bb2ee53ab9ee9b334d8a37728df1d34ec0be5ef2`. Native 1080 × 1920, 30 fps, 46 seconds. Full 1,380-frame video decode passed. Final stereo AAC 256 kb/s / 48 kHz measured −16.20 LUFS, −1.46 dBTP, 2.50 LU loudness range. Ten structural/provenance checks passed. Deterministic transition-seam checks and caption safe-width checks passed, with no browser errors. The final encoded film was visually sampled every two seconds; transition frames and selected native compositions were also examined. This does not certify continuous human-style audiovisual watching/listening or subjective “top-notch” acceptance. Original procedural music is intentionally behind the narration, not a loud replacement for speech.
