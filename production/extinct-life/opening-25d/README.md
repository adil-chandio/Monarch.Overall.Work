# Extinct Life — Amber Atlas / 2.5D comparison

**Deliverable:** `deliverables/Extinct_Life_Opening_25D_Amber_Atlas_45s_1080p.mp4`

A separate 45-second, 1920×1080, native 30 fps **multiplane 2.5D motion-illustration alternative** to the 3D opening. The full 6–8-minute episode is not replaced or completed by this style comparison. Owner style approval remains pending; “premium” is the art-direction target, not a measured performance result.

## Art direction

- Deep forest/ink: `#103c3b`, `#0b242c`
- Pine and atmospheric teal: `#24574b`, `#547e78`
- Warm amber evidence accent: `#e4b66b`
- Ivory editorial type and maps: `#f0e7cd`
- Warm brown/gold cutout animal, cooler distant planes, restrained procedural grain.
- Self-hosted system DejaVu Serif for editorial titles; sans-serif for labels. No remote font requests.

This is deliberately illustrated/cutout, not photoreal wildlife footage. Animal anatomy, locomotion, vegetation placement, habitat appearance and solar lighting are artistic interpretations, not validated study reconstructions.

## What makes it 2.5D rather than a still-image slideshow

The world is constructed from independent drawing/animation systems: distant terrain, far trees, middle trees, river, ground, articulated animal, near grass and foreground fern planes. Far and middle planes travel at different camera coefficients (0.22 / 0.52); near foreground travels at 0.9–1.3. Scale, overlap, atmospheric colour and depth-ordered shadows establish depth.

Animal limbs use two-bone IK-like target construction with planted and lifted gait phases; trunk, tail and body are separately articulated. Wind bends tree parts and foreground fronds; water highlights advect; bird silhouettes flap and translate. Sediment layers separate, and individual schematic fragments move into reference positions while mismatches remain separated.

Tree components are original vector drawings cached into in-memory canvases for rendering efficiency. This is ordinary graphics rasterization, **not an acquired photograph or AI image used as a slide**. No image-generation tool, competitor screenshot, video frame, stock photograph or downloaded illustration is used as a scene plate. A fine procedural grain tile is a finishing effect, not scene content.

## Controlled audio comparison

The existing 3D opening's AAC audio is copied without re-recording, remixing, time-stretching or re-encoding. `finish.py` checks that both videos decode to the **same SHA-256 audio hash over 45 seconds**. This isolates visual treatment rather than making the new style seem stronger through louder music or a different voice.

Reference: `deliverables/Extinct_Life_Opening_V2_45s_1080p.mp4`, already committed in `7fdf6510be5cbb0fd886739936d639fa562e5efa`.

Narration, original score, ambience and foley remain the previous opening's soundtrack. Newly animated footsteps and birds are not represented as authentic field audio. No extinct-animal calls are fabricated. No aligned subtitle track is claimed.

## Scene continuity

The same 45-second narrative is retained: animal/lineage hook → concept coast → Greenland locator → separating sediment → fragment/reference comparison → reconstructed woodland → limits of appearance → unresolved evidence → question/title. Durations follow the prior opening for an A/B style review. Scientific distinctions remain visible in labels.

## Sources and rights

- Scientific source: Kjær et al. (2022), Nature, https://www.nature.com/articles/s41586-022-05453-y ; DOI 10.1038/s41586-022-05453-y. Approximate age, not an exact date or a new discovery/current-record claim.
- Greenland polygon: Natural Earth 1:110m countries, public domain, https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson . Only the Greenland polygon is retained; locator approximate.
- All scenery, animal, plants, birds, diagrams, surface texture and drawing/animation code: original procedural work in `stage.html`.
- Font: local DejaVu Serif system font, rendered into the movie, not vendored as a font asset. Library/runtime licences still apply when distributing software; no new external creative assets are included.
- Soundtrack: unchanged original 3D-opening track, including its disclosed synthetic narration.

## Reproduce from repository root

Use the Node versions/install command in `../motion-lab/dependencies.json` and Python requirements in `../episode-001/requirements.txt`. Ensure `/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf` exists and the reference MP4 is present (restore from Git if missing).

1. `node production/extinct-life/opening-25d/render.mjs --stills`
2. Inspect sampled layouts, particularly type, gait, perspective cues and foreground occlusion.
3. `node production/extinct-life/opening-25d/render.mjs`
4. `.venv/bin/python production/extinct-life/opening-25d/finish.py`
5. `.venv/bin/python production/extinct-life/opening-25d/test_contract.py`

The renderer seeks exact frame indices, captures the completed canvas directly (not a wall-clock animation recording), and encodes two contiguous ranges, totaling 1,350 frames. All drawing remains time-indexed and deterministic. The temporary allowlisted server binds to 0.0.0.0 and closes after rendering. Cache/runtime files remain under the ignored `.cache/extinct-opening-25d/`.

`QC.json` records actual output size, full decode/frame count, encoded audio measurement, audio identity, and black/freeze diagnostics. Sampled-frame/technical checks are not anatomical validation, a complete creative watch, audience testing or evidence of superiority over competitors. Competitor playback remains unverified. No YouTube upload/scheduling, paid generation service or GPU allocation is initiated by this project.

## Completed comparison checks

The final file is 15,020,033 bytes. All 1,350 frames decode. The 45-second decoded audio hash matches the 3D reference exactly. Encoded audio measures -16.20 LUFS / -1.98 dBTP. No black intervals were reported. The freeze detector flags low-motion/settled explanatory diagram sections; these are recorded in QC.json rather than hidden or claimed as a universal green result. All 90 half-second motion samples have distinct decoded hashes. Five structural regressions pass. Ten final-encode frame samples were visually inspected; this is not a complete audiovisual creative watch or an anatomy/retention validation.
