# Amber Atlas — Cinema Polish v2

**Output:** `deliverables/Extinct_Life_Opening_25D_Cinema_Polish_45s_1080p.mp4`  
**Scope:** A revised 45-second opening, not the completed 6–8-minute flagship. The original Amber Atlas MP4 and source are preserved separately.

## Implemented visual pass

- Refined ink / atmospheric teal / restrained amber palette; soft lens-edge falloff, quieter grain and less prominent diagram grid.
- Cleaner animal silhouette, darker tapered leg shading instead of bright joint-like lines, contact shadows, and upper limbs occluded beneath the torso. The gait remains articulated, with stance/swing phases; it is **not zoologically validated**.
- A time-keyed cubic Hermite camera rail with continuous first derivative at its internal keys. Shot-specific eased dolly moves, independent near/far parallax and moving water, vegetation and birds remain active.
- Short two-scene dissolves replace abrupt scene changes. Selected seams carry an amber point between light, locator and evidence: **an editorial metaphor, not a literal sample journey**. The title builds over the continuing woodland rather than cutting to a static card.
- Brief eased headline introductions, staggered reference-fragment arrivals, reduced technical-header clutter and a clearer serif/sans hierarchy.
- `edit.json` is the explicit shot/seam/camera ledger. `stage.html` is the actual deterministic animation source. No downloaded photograph, generated scene plate or competitor frame is used.

The drawings are intentionally illustrated 2.5D, not photorealistic footage. Existing anatomy, habitat and scene-interpretation limitations still apply. This is a polish revision within the selected direction, not proof of retention, audience engagement or competitive superiority.

## Audio control

The previous 2.5D MP4's original 45-second AAC soundtrack is **copied unchanged**. No new voice, music, foley, loudness increase or time stretching. `finish.py` verifies identical decoded audio hashes. This makes the visual comparison fair; it is not advertised as a new sound-design pass. Voice and music remain synthetic/original, not authentic extinct-animal or Greenland field recordings.

## Native render pipeline

This revision executes the Canvas source with `@napi-rs/canvas` (Skia), avoiding browser screenshot/IPC capture. Each frame is independently drawn at **1920×1080, native 30 fps**. No interpolated or duplicated 60 fps claim. Rasterization/font metrics may differ slightly from a browser; the delivered native encode is the reviewed artifact.

From the repository root, with Node 22 and Python available:

```sh
npm install --no-save --package-lock=false --ignore-scripts @napi-rs/canvas@1.1.0
python3 -m venv .venv
.venv/bin/pip install imageio-ffmpeg==0.8.1 pillow==13.0.0
node production/extinct-life/opening-25d-v2/render.mjs --stills
node production/extinct-life/opening-25d-v2/render.mjs --verify
node production/extinct-life/opening-25d-v2/render.mjs
.venv/bin/python production/extinct-life/opening-25d-v2/finish.py
.venv/bin/python production/extinct-life/opening-25d-v2/test_contract.py
```

System fonts `/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf` and `DejaVuSans.ttf` are required and registered as AtlasSerif and Arial respectively. No remote font fetch. The previous 2.5D MP4 must be present for muxing. Temporary media and native runtime dependencies are not committed.

`--verify` checks seven non-monotonic seek sequences by comparing encoded-frame SHA-256 hashes and records numerical camera samples around edit seams. Run it before `finish.py` so those checks are included in QC.

## Validation and limits

`QC.json` is generated from the final encode: full decode/frame count, resolution/fps, black/freeze diagnostics, 90 half-second decoded hashes, audio identity and loudness. Low-motion map/diagram holds are reported honestly, not hidden or treated as a creative score. Final-encode samples are reviewed for layout and transitions; sampled inspection is not a complete audiovisual creative watch, biological validation or audience test. Owner approval of this revision remains pending. No aligned subtitle track is claimed.

## Sources / rights

- Science: Kjær et al., *Nature* (2022), DOI **10.1038/s41586-022-05453-y**. https://www.nature.com/articles/s41586-022-05453-y — approximate ~2-million-year Greenland ecosystem evidence; no claim that fragmentary DNA is a whole genome, exact photograph or resurrection recipe. No current-record claim.
- Greenland polygon: Natural Earth 1:110m countries, **public domain**. https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson — coarse outline; Kap København locator approximate.
- Scenery, animal rig, vegetation, birds, diagrams, procedural texture and animation code: original work from the previous Amber Atlas implementation, revised here.
- DejaVu fonts are system-installed, not vendored; font/library licences apply to software redistribution. `@napi-rs/canvas` and bundled encoder licensing remain separate from creative-asset provenance.
- Full earlier provenance: `../opening-25d/README.md`.

No YouTube upload, paid rendering service or GPU allocation is initiated.

## Completed encode checks

The delivered revision is **21,034,105 bytes**, 45 seconds, 1,350 fully decoded 1080p/30 frames. Audio matches the prior Amber Atlas cut exactly and measures **−16.20 LUFS / −1.98 dBTP**. No black intervals were detected. All **90 half-second decoded frame hashes are distinct**. The freeze detector still reports low-motion coast/map/settled-diagram holds; these remain visible in QC rather than being relabelled as clean. Seven out-of-order seek probes reproduce their encoded frames exactly; numerical camera derivative checks and all five structural/media regressions pass. Ten final-encode sampled frames were visually inspected.
