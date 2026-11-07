# Approved stickman 3D experiment — 1:01 English

Owner authorization: “Ok ab banao video.” New one-minute experiment; **V9 remains unchanged**. The additional second completes the existing sentence ending at 60.743s; the next sentence begins at 61.143s and is excluded. No new voice audition, rewritten script, hidden speed change, generated image assets or slideshow.

## Implementation

- `scene.mjs`: original procedural Three.js scene; articulated fixed-length investigator limbs, planted feet, head/eye/scarf reactions, handled lens/book/leaf/fragments, separating sediment, a growing conceptual environment, puzzle and animated elephant-like stand-in. Camera and object motion are independently authored; movement remains with the camera frozen. No claim of photoreal or physically validated simulation.
- `schedule.json`: first two original approved English voice-02 chapters and hashes retained. B01 begins at frame 0; B02 at frame 1600. Source chapter metadata is intentionally unchanged even though the second chapter is excerpted.
- `render.mjs`: every frame rendered natively at 1920×1080/30fps; six nonoverlapping 305-frame H.264 shards. Deterministic absolute seek, visible-picture/limb checks, locked-camera motion test and sampled native-frame inspection. No old movie reuse.
- `finish.py`: SHA-verified original speech at original timing, a non-looped licensed Hiraeth excerpt, gentle narration-dependent ducking, restrained original synthetic material/contact foley and final delivery normalization. Full decoded frame-count verification and measured final audio statistics. `--voice-only` is a local preview option, not the release mix.
- `English.srt`: first 18 unchanged subtitle entries; optional sidecar, not large persistent upper captions.
- `CREDITS.md`: required music attribution, scientific source, conceptual illustration/review limitations. Keep with the MP4.
- `DELIVERY.json`, `QC.json`, `AUDIO-QC.json`, `seek-QC.json`, `inspection/`: produced by the delivery workflow, not invented in advance. Delivery metadata links the downloadable release file.

## Reproduce / preview

Use the repository root and the pinned Node/Python dependencies in `.github/workflows/extinct-stickman-minute.yml`.

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_extinct_stickman_minute.py' -v
.venv/bin/python production/extinct-life/film-v10-stickman/finish.py
node production/extinct-life/film-v10-stickman/render.mjs --stills
node production/extinct-life/film-v10-stickman/render.mjs --serve --port=4190
# Render all six exact ranges separately, then assemble:
# --from=0 --to=305 ; 305..610 ; 610..915 ; 915..1220 ; 1220..1525 ; 1525..1830
.venv/bin/python production/extinct-life/film-v10-stickman/finish.py --assemble
```

Public music downloads are executed on GitHub Actions, where the artist's official host is reachable. No licensed source audio or large final movie is committed. The workflow publishes the actual MP4, captions, credits and technical reports as a GitHub prerelease for owner creative review; it does not upload to YouTube. Frame/sample tests and audio statistics do not establish uninterrupted human audiovisual review, reference parity, exhaustive reference analysis, audience geography, RPM or virality.
