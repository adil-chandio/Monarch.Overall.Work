# Extinct Life — V15 continuity rebuild

## Authorization and scope

The user explicitly authorized rebuilding **our extinct-life Short** after the earlier production stop: “Woh poori video banao ab new level ke sath Jo hamne dekha seekha usko next level lejake”. This authorizes this new Short, not modifications to the V13/V14 full films, the already selected thumbnail, or YouTube publication.

**New complete edit specification:** 43.5 seconds, native 1080×1920, 30fps / 1,305 actual rendered frames. The old 50-second rejected Short remains separate and unchanged. The new video is `deliverables/Extinct-Life-V15-Continuity-Rebuild-1080x1920.mp4` when export completes. Check `DELIVERY.json` and `QC.json`, rather than treating this specification as an export-completion claim.

The live preview runs from `node production/extinct-life/shorts-v15-continuity/film/render.mjs --serve --port=4193`; press **Play with sound**. It is the complete animated edit, not an MP4 export receipt.

## What actually changes

- **Subject locomotion, not a turntable:** the existing original mastodon sculpt now advances along its local forward axis while the existing foot-cycle's stance speed is compensated by root travel. The camera tracks/pushes rather than orbiting a stationary model. This is authored deformation, not anatomical or physical validation.
- **A functional sampling action:** two authored gloved grips remain parented to the tool, its open bore permits insertion, sediment layers collect inside the tube, and the same core leaves the hole with the tool. This is an educational cutaway, not an exact recreation of field equipment or actual sample handling.
- **Contact before payoff:** the short DNA illustration moves toward a flat mineral face, then settles at an authored contact height. A restrained contact cue comes after arrival, not an arbitrary glowing transformation into a living animal.
- **Reference comparison remains partial:** visible A/C/G/T symbols, short incoming pieces and intentional missing regions explain comparison without inventing a complete genome, real sequence, probability or one-fragment proof of taxonomic identity.
- **A forest rather than a featureless pedestal:** fine leaf instances, layered trunks, foreground plants, atmospheric depth, textured soil/bark, direct lighting and dynamic shadow maps replace the old wide-shot setup. Static geometry is batched by material; the video is not downscaled or frame-interpolated.
- **More visual room:** the old large multi-line headings are replaced with compact contextual labels; captions use outlined phrase text. The comparison camera was pulled back after native stills showed side-cropping. The binding camera was reframed to separate the contact region from captions.
- **Tighter Short pacing:** the approved 102-word English Short narration text and selected voice recordings are retained. Pitch-preserving FFmpeg `atempo=50/43.5` applies only to this new Short, with captions and sound events retimed to the same output clock. This is NOT an unchanged-speed claim. Full-film voice/script/speed/duration remain untouched.
- **Restrained redesigned audio:** original mallet/pad/bass arrangement retained but reduced; most generic transition sweeps removed. Synthetic sampling grit and timed contact/alignment cues accompany specific actions. No competitor audio, music or voice was copied.

## Evidence-informed, not a false research-completion claim

The actual-footage study informed support relationships, sequential action, caption/voice semantic correspondence, held states and mechanism continuity. The ten source soundtracks reached running models. However, the requested exhaustive manual frame-by-frame + perceptual-audio study remains incomplete; it is not being relabelled complete to justify this production. No source project settings, creator rig, voice ID or stems were recovered.

No guaranteed million views, studio-quality/anatomical perfection, exact creator-style parity, owner approval or independent perceptual listening is claimed. The original creature asset still has a stylized sculpt; it has not become a new studio-quality character simply because the motion/material/lighting changed. The gloved hands are authored schematic geometry. Molecular processes and reference strings are illustrative, not literal filmed molecules or the study's real alignment output.

## Reproduction

Dependencies already used by the existing film pipeline: Node, `three`, `playwright`, `@sparticuz/chromium`, Python NumPy/SciPy/Pillow/imageio-ffmpeg. Model/font assets are the repository's original assets and existing licensed fonts.

```bash
# Reconstruct the original selected English narration WAV if the existing cache is absent:
.venv/bin/python production/extinct-life/shorts-v14/film/prepare_audio.py
mkdir -p .cache/shorts-v15/stills
cp .cache/shorts-v14/narration.wav .cache/shorts-v15/narration.wav
.venv/bin/python production/extinct-life/shorts-v15-continuity/film/sound.py
.venv/bin/python production/extinct-life/shorts-v15-continuity/film/test_timeline.py
# These two independent native halves may be run concurrently:
node production/extinct-life/shorts-v15-continuity/film/render.mjs --from=0 --to=650
node production/extinct-life/shorts-v15-continuity/film/render.mjs --from=650 --to=1305
.venv/bin/python production/extinct-life/shorts-v15-continuity/film/finish.py
```

`finish.py` refuses mismatched/incomplete source receipts, concatenates the first-generation H.264 halves without upscaling/interpolation, muxes AAC audio, decodes all 1,305 output frames, measures the encoded audio, extracts review images and checks protected old-source hashes. Numerical checks do not replace watching or creative acceptance. The binary delivery is ignored by Git under the repository's existing convention; no new public upload is authorized.
