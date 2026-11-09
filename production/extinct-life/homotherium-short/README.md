# This Saber-Toothed Cub Still Has Its Fur

Standalone English evidence-led Short. 51 seconds, 1080 × 1920, 30 fps. No associated long-film CTA; no YouTube publication authorized.

## Scientific and visual provenance

Primary source: Lopatin et al., *Mummy of a juvenile sabre-toothed cat Homotherium latidens from the Upper Pleistocene of Siberia*, Scientific Reports 14, 28016 (2024), https://doi.org/10.1038/s41598-024-79546-1 . Figures 2, 4 and 7 used under **CC BY 4.0**, https://creativecommons.org/licenses/by/4.0/ . Copyright remains with the respective source authors. Original PNGs, acquisition URLs, hashes and rights basis are in `SOURCE-LICENSE.json`.

Changes: panel crops, removal of surrounding white background and some printed panel labels, resizing, compositing, animated framing, editorial highlight sweep. See `ASSET-EDITS.json` and `film/prepare_assets.py`. Remaining scientific labels are part of the original photographs. No anatomical retouching or invented specimen features. The published CT-based skull model is partially reconstructed by mirroring the undeformed right side: this film does not represent the graphic sweep as new tomography, live scanning or our own measurement. Photographic comparison panels are explicitly not displayed to a common measurement scale.

Map: Natural Earth 1:110m land, public domain, https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_land.geojson . Approximate discovery location plotted at 67.6872 N, 146.7703 E from the source paper. Globe is an original cartographic illustration, not recovery-site footage.

Original schematic body outline and feature icons illustrate preservation limits/soft tissues; they are not anatomical reconstructions or measured footprints. The specimen is dead, partial preserved remains; recovered in 2020, described in 2024. Calibrated date range is 35,471–37,019 cal BP. Approximately three weeks old is a dental-development estimate, not a known birth date. “Tiny survivor of deep time” refers to preservation, not survival alive. No adult saberfangs, awakening or de-extinction claim. Species identification relies on comparative morphology and CT, not DNA in this film.

Audio: selected synthetic English voice `voice-04`; continuous narration preserved without speed change in `source/narration.flac`. Original quiet procedural pad and transition accents, not reused music. Captions in `English.srt` and baked into film. See `VOICE-PROVENANCE.json`, `SOUND-DESIGN.json`.

## Reproduction

With the repository's existing Node dependencies, Python environment, Chromium libraries and fonts installed:

```sh
.venv/bin/python production/extinct-life/homotherium-short/film/prepare_assets.py
.venv/bin/python production/extinct-life/homotherium-short/film/prepare_sound.py
node production/extinct-life/homotherium-short/film/render.mjs
```

Native frame stream is encoded as H.264 without upscaling. Raw/intermediate renders remain under `.cache/homotherium-short` and are not committed. Preview: `node production/extinct-life/homotherium-short/film/render.mjs --serve --port=4196`.

This is original storytelling using licensed research imagery, not clips or audio copied from the reference creators. Relevant YouTube research demonstrates topic interest, not guaranteed reach, causal retention findings or a complete audiovisual forensic review. Prior films and the chosen previous thumbnail are unchanged.

## Publication description / reusable attribution

This saber-toothed cub still has its fur—after more than 35,000 years. Scientists studied the preserved partial remains of a roughly three-week-old Homotherium cub found in Siberian permafrost. Its fur, ears, neck and paws reveal details bones alone cannot. These are preserved remains, not a living or resurrected animal.

Research and photographs/CT-based models: Lopatin et al., Scientific Reports 14, 28016 (2024), https://doi.org/10.1038/s41598-024-79546-1 . Figures 2, 4 and 7, CC BY 4.0, https://creativecommons.org/licenses/by/4.0/ ; cropped, background-separated, resized and animated. Cartography: Natural Earth (public domain). Original motion graphics, sound design and synthetic narration. Illustrative graphics are not new scientific measurements. No YouTube upload has been made by this production process.

## Delivered checks

Final MP4: `deliverables/Homotherium-Cub-This-Saber-Toothed-Cub-Still-Has-Its-Fur-1080x1920.mp4`. All 1,530 video frames decoded without errors; 51 seconds, 30 fps, native 1080 × 1920. Final AAC mix measured −16.17 LUFS integrated, −1.44 dBTP, 3.10 LU loudness range. Six structural/provenance tests passed. Final encoded film sampled every two seconds (26 positions), plus native-size checks of key compositions; not claimed as continuous audiovisual viewing/listening. Detailed machine report: `DELIVERY-QC.json`. This evidence-led motion film deliberately reuses the real head photograph for its later lion comparison, but does not repeat an unrelated earlier-film scene or endcard. Small surviving numbered labels in the paw photographs belong to the published source and are not our measurements.
