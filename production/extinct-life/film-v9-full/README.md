# Full English film, V9

**Scope:** the entire locked 438.766667 s / 13,163-frame English master, not another opening excerpt. Delivery is complete only when `DELIVERY.json` and actual encoded `QC.json` exist. Owner creative acceptance is separate.

- Original continuous organic animal meshes authored in Blender, including the V8 mastodon sculpt. No prior movie frames, generated-image plates or private reference assets are reused.
- Fresh deterministic native 3D frames. Planted stance kinematics, eased stop/browse/resume, articulated flight surfaces, a leaf release/landing/current trajectory, ripples, moving water and vegetation. These are authored kinematics, **not** a fluid/rigid-body simulation or expert-validated anatomy.
- Quiet, short labels projected from actual world positions; no upper caption cards. Exact approved narration and external SRT remain unchanged. No voice regenerated or time-stretched.
- Separate field exposure, accumulating sediment, mineral binding, supported extraction gantry, reference comparison, clean-hood controls, branch inference, reconstruction display, complementary-record inspection, filters, incomplete archive and closing sample-lid action. Returns are necessary for the story; visual variety is not a retention guarantee.
- Low-sample screen-space contact occlusion, textured ground, wind-animated leaf cards and grass, PBR materials and continuous camera paths. Geometry/shading intentionally stylized, not photoreal site footage.
- Foley contact events follow the same analytic stop/resume clock as the animals. Soft synthesized material sound is not recorded field sound or certified ASMR. Two licensed, non-looped Scott Buckley cues retain full attribution and narration-priority mixing.

## Reproduce

Use pinned dependencies from `.github/workflows/extinct-v9-full.yml`. Original reusable meshes are in `native-meshes/`; regenerate only when authoring changes with `export_assets.py` using `bpy==4.2.0`, `numpy==1.26.4` and system OpenGL/X libraries.

```sh
python -m unittest discover -s tests -p test_extinct_v9_full.py -v
node production/extinct-life/film-v9-full/motion.test.mjs
.venv/bin/python production/extinct-life/film-v9-full/finish.py --audio-only
node production/extinct-life/film-v9-full/render.mjs --stills
node production/extinct-life/film-v9-full/render.mjs --from=0 --to=183
# Render the rest of the disjoint master ranges before assembling.
.venv/bin/python production/extinct-life/film-v9-full/finish.py --assemble-only
```

The workflow renders all 36 disjoint ranges, checks continuity and the exact frame count, decodes the entire encoded master, measures actual encoded audio, saves decoded sample frames, and publishes the actual full MP4 and sidecars to a GitHub release. No YouTube upload. Numeric and sampled checks do not imply uninterrupted human watch/listen, guaranteed ear comfort or reference-level creative acceptance.

## Internal look development

Initial native inspection was rejected internally: sparse environment, harsh shadows and slab-like strata. Subsequent look development added textured ground, more vegetation, contact occlusion, irregular contiguous sediment and supported actuator shafts. A broken ambient-occlusion-only composition producing black frames was caught visually and fixed; capture now explicitly rejects mostly-black frames. The inspection and QC files from the actual final render, not this development history, govern delivery.
