# Genetics sequence — work-in-progress 3D test

This is a **29.77-second experiment**, not the requested finished documentary. It renders a reconstructed laboratory and an illustrative DNA double helix as animated 3D geometry, with camera cuts and the beginning of the draft genome narration. The laboratory and sample labels are invented illustrative props, not a depiction of the researchers' actual equipment or specimens; the helix is schematic and does not encode an actual genetic sequence. The visuals are stylized, not photorealistic. It does not contain mammoth locomotion.

The output, `deliverables/Last-Mammoths-Genetics-3D-Scene-Test.mp4`, is 1280×720 at 30 fps. It uses the unretimed `03-genome.mp3` take and automatically aligned captions from the adapted full-script draft. It has **no music or sound effects**, and the voice and captions have not been reviewed by a human. The adaptation is not a verbatim reading of the research-stage script. These technical tests do not certify documentary accuracy, editorial quality, natural animation, or viewing quality. Do not substitute this test for the full film or publish it as finished.

## Render and check

From the repository root, with Three.js, Playwright, the Sparticuz Chromium binary, Python and `imageio-ffmpeg` installed:

```sh
node production/extinct-life/longform-mammoth/cinematic-rebuild/molecular-lab/render.mjs --verify
node production/extinct-life/longform-mammoth/cinematic-rebuild/molecular-lab/render.mjs --stills
node production/extinct-life/longform-mammoth/cinematic-rebuild/molecular-lab/render.mjs
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/molecular-lab/finish.py
```

The renderer evaluates each of 893 frames independently. It creates a temporary plate and a source-hash manifest under `.cache/mammoth-molecular-lab`; the finishing script refuses a plate if the scene or stage has changed since rendering, adds narration and approximate subtitles, checks full decode and peak level, and records the result in `SCENE-TEST-QC.json`. Source and dependencies must be available locally. The `--verify` checks only deterministic seeking, scanner movement and changing DNA images; it is not a substitute for visual review.

The rest of the adapted narration, 3D scenes, believable mammoth animation, soundtrack, sound design, editorial and review required for the entire film remain unfinished. No YouTube publication has been authorised.
