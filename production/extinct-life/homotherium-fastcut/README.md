# Homotherium — clean 2D fast-cut edit

User-selected base: commit `d61ed05`, `deliverables/Homotherium-Cub-This-Saber-Toothed-Cub-Still-Has-Its-Fur-1080x1920.mp4`. The subsequent 3D rebuild is rejected as the direction for this Short. It remains archived, not deleted. This edit uses the original licensed evidence imagery and selected English narration, not any cub geometry from that rebuild.

## Editorial changes

- **46 seconds**, native **1080 × 1920 / 30 fps**, 35 hard-cut shot intervals, mean shot length 1.31 seconds.
- Pure 2D compositing. No 3D subject, meshes, WebGL renderer or 3D globe. The geographic locator is now a flat illustrated map.
- Tighten inter-phrase dead time without speeding or changing spoken words. Exact source-to-destination speech edit map: `AUDIO-EDITS.json`. Preserve small source handles and 8ms audio fades rather than clipping abruptly at a phoneme. Same selected `voice-04`; no new narration audition.
- Main subject, short captions and locally necessary evidence qualifiers. Remove persistent branding, episode/scene counters, long top headings, decorative dust, multiple information cards, icon lists and repeated bottom credits. A compact source credit appears during the final 2.2 seconds; full reusable attribution is below.
- Close-up → context → evidence → comparison cuts. Short geometric accent sounds and an original 116 BPM rhythm/pad are ducked under the voice; no animal sounds, recovery-site foley or copied reference audio.
- Caption chunks are editorial subdivisions of measured phrase timings, not certified word-level ASR alignment. No claim that 35 cuts guarantee retention or viral performance.

`film/timeline.json` holds all shot intervals, short caption chunks and phrase timings. `film/prepare.py` reproducibly builds the timeline and soundtrack from the retained original source. Intermediate renders/audio remain in `.cache/homotherium-fastcut`.

## Accuracy and rights

Research and images: Lopatin et al., *Mummy of a juvenile sabre-toothed cat Homotherium latidens from the Upper Pleistocene of Siberia*, Scientific Reports 14, 28016 (2024), https://doi.org/10.1038/s41598-024-79546-1 . Figures 2, 4 and 7, **CC BY 4.0**, https://creativecommons.org/licenses/by/4.0/ . Cropped, white-background-separated, resized and composited; framing highlights selected details but does not anatomically retouch them. Original acquisition manifest and figure hashes: `../homotherium-short/SOURCE-LICENSE.json`. Derived crop details/hashes: `../homotherium-short/ASSET-EDITS.json`.

The CT-based skull model is the published figure, partly reconstructed by mirroring the undeformed right side; it is not our own live scan, actual newly acquired tomography, or our own volumetric reconstruction. Its source/model status is labelled locally. The user's “no 3D” direction applies to production technique: a flat photograph of the paper's CT-based model remains scientific evidence, not a rendered 3D scene.

The cub is dead, partial remains recovered in 2020, not a living or resurrected cat or a whole intact mummy. Calibrated dates: 35,471–37,019 cal BP. Approximate three-week age comes from dental-development comparison, not a known date of birth. Homotherium is not Smilodon or a true tiger. Comparing ear/neck/paw photographs illustrates reported qualitative differences, not measurements from display sizes. Comparison panels explicitly say they use different display scales. The script retains the incomplete-mummy and uncertain-reconstruction caveats. Full living appearance is not invented or presented as established footage. Tight shot changes do not turn this into a claim of animal movement.

Map: Natural Earth 1:110m public-domain land, https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_land.geojson . Approximate discovery locality: 67.6872 N, 146.7703 E. The flat cropped cartographic illustration is not footage of an actual frozen animal recovery scene.

Original synthetic rhythmic bed and cut accents; no third-party music. Original source narration/provenance: `../homotherium-short/source/narration.flac`, `../homotherium-short/VOICE-PROVENANCE.json`. Full script unchanged from `../homotherium-short/NARRATION.txt`, apart from caption-number typography. English caption sidecar: `English.srt`.

## Rebuild

```sh
.venv/bin/python production/extinct-life/homotherium-fastcut/film/prepare.py
node production/extinct-life/homotherium-fastcut/film/render.mjs
.venv/bin/python production/extinct-life/homotherium-fastcut/film/validate.py
```

Existing repository Python/Node dependencies, Chromium libraries and typefaces required. Source assets are reused from the preserved `homotherium-short` directory. No older exports are overwritten. GitHub delivery only; no YouTube publication authorized or performed.

## Reusable publication attribution

This saber-toothed cub still has its fur—after more than 35,000 years. The preserved partial remains of a roughly three-week-old Homotherium cub reveal details bones alone cannot. Preserved does not mean alive or resurrected.

Research and photographs/CT-based reference: Lopatin et al., Scientific Reports 14, 28016 (2024), https://doi.org/10.1038/s41598-024-79546-1 . Figures 2, 4, 7 under CC BY 4.0, https://creativecommons.org/licenses/by/4.0/ ; cropped, background-separated, resized and composited. Map: Natural Earth (public domain). Original editing, synthetic narration and sound design. The published CT model is partly reconstructed; comparison images are not at a shared measurement scale. No new scientific measurement is claimed.

## Delivered verification

Final file: `deliverables/Homotherium-Cub-Clean-Fast-Cut-1080x1920.mp4` (11,478,670 bytes). SHA-256: `d626152ff81bde872d831ca33afa075031bbc5df8ed78a7ba7e57662a4a560ba`. Full 1,380-frame decode passed; 46 seconds, native 1080 × 1920 at 30 fps. Final AAC measured −16.15 LUFS, −1.45 dBTP, 2.40 LU loudness range. Eight structural/editorial-provenance checks passed. Final encoded film sampled every two seconds and once within each of the 35 shot intervals, plus the end-credit placement and key native compositions. Caption polish avoids orphan single-word chunks and uses two-to-five words per chunk. These are sampled visual / automated audio checks, not a certified continuous human-style audiovisual watch/listen. The selected original and archived 3D export hashes were checked unchanged.
