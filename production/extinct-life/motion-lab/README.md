# Procedural motion lab — NOT an episode delivery

This is an 18-second **engineering/previsualization test**, not a premium-finished documentary, not the planned 45-second representative opening, and not a competitor benchmark. The animal/environment cinematography, licensed real footage and editorial narration required for that opening are not present here. Owner approval of this lab must not be inferred.

## What is actually implemented

- Original procedural Three.js geometry; **no generated or acquired image plates**.
- 1,250 individually transformed sediment grains and five separated 3D strata.
- Camera movement through changing geometry into an abstract fragment field.
- Independent fragment rotation in real 3D, not pans across a flattened still.
- Frame-indexed 1080p/60 rendering, using the existing showreel's deterministic capture approach rather than its B2B content or encryption.
- Original sparse stereo score and event-specific granular/transition foley, with separate WAV stems in the ignored local cache.

Geometry is intentionally schematic. Colours and fragment shapes are not study measurements, exact geology, actual DNA reads or validated molecular structures. The sediment-to-fragment flight is a visual metaphor, not a literal scale-continuous microscope recording. This low-complexity lab **does not establish photorealistic animal or environment capability**.

## Run from repository root

1. Use the pinned installation command in `dependencies.json`. These local experiment packages are not added to the main app package.json/lockfile.
2. Ensure the episode Python environment has Pillow, numpy and imageio-ffmpeg (`episode-001/requirements.txt`).
3. `node production/extinct-life/motion-lab/render.mjs --stills` for sampled frame/layout checks.
4. `node production/extinct-life/motion-lab/render.mjs` for the full 1,080-frame picture render. Software WebGL can take many minutes; it is not a real-time GPU render.
5. `.venv/bin/python production/extinct-life/motion-lab/audio.py` to write original stems, mux AAC, and record measured audio values.

The Chromium npm package supplies browser binaries and NSS/NSPR runtime libraries; the harness unpacks these into the ignored cache if needed. Capture serves only the stage and Three.js build files, not arbitrary repository files. Its temporary server is closed after capture. For ephemeral software-rendering use only, not a production web deployment.

## Outputs

- `deliverables/Extinct_Life_3D_Motion_Lab_NOT_EPISODE.mp4`
- `production/extinct-life/motion-lab/QC.json`
- `.cache/extinct-motion-lab/` — picture render, sampled frames, independent score/foley stems and runtime libraries. Not committed.

## Creative gate remains open

Read `../episode-001/PRODUCTION_V2.md`. Actual competitor playback was blocked in the latest public-runner test; no scene-level competitor superiority claim is supported. Obtain owner-supplied review excerpts before declaring a reference-matched visual standard. Rights-cleared moving environment/animal scenes and a polished representative edit remain to be produced. Do not expand the technical lab into seven minutes of floating grains and molecule icons as another shortcut.
