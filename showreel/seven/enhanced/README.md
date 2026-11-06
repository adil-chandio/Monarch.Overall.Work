# Seven MONARCH reference adaptations — enhancement pass

The seven `public/demo/monarch-reference-0N-enhanced.mp4` files are separate enhanced versions; the prior adaptations are left intact. Each retains the broad sequence and timing of its earlier adaptation, with MONARCH branding and the red/black visual theme.

- **01:** softened projection beam and antialiased motion.
- **02:** separately moving, shadowed cards with shallow perspective; beveled hexagons.
- **03:** dimensional MONARCH name treatment and eye highlights clipped to the eye.
- **04:** individual card, portrait and store motion with shallow perspective.
- **05:** three new AI-generated pixel-art objects and independent character/hand drift. See `../README-05.md` for Twemoji attribution for other icons.
- **06:** independently moving bust, profile, crown and perspective book; main-frame-only crop, with no BTS timeline.
- **07:** independent framed artwork and helmet motion, with a revised fist/plaque entrance; main composition without BTS timeline.

The motion is 2D/2.5D compositing and perspective transforms on still artwork, **not** fully modeled or rigged 3D. These are approximations and are not pixel-identical recreations. Several other assets are AI-generated stills; see the individual original READMEs for asset details and font licenses. The new camera, mouse and pencil assets were generated for this pass.

01–05 preserve the supplied reference audio, including any narration that may not match the changed on-screen text. Rights to the supplied audio have not been established; obtain permission before public/commercial use. The source audio is HE-AAC and may not be playable in all browsers. 06–07 are silent because their supplied references have no audio; no new music or sound effects have been added to those two.

## Rebuild

Requires Python 3, Pillow, NumPy, OpenCV and the FFmpeg helper/dependencies in the repository. 01–05 require the user-supplied reference videos for their audio; do not commit those reference files. Supply the directory containing `01.mp4` through `05.mp4`:

```sh
for n in 1 2 3 4 5 6 7; do
  python3 showreel/seven/enhanced/render.py --video "$n" --reference-dir /path/to/reference-videos || exit 1
done
```

For a still preview, use `--sample 2.9 5.5`; images are written under `/tmp`. Outputs are H.264 at 60 fps. This is the output frame rate, not a claim that source footage contains 60 unique original frames or that quality is tripled.

## Validation

All seven outputs were fully decoded with OpenCV. Frame counts in order: 660, 1572, 720, 2194, 1084, 600, 1380. Resolutions: 1276×718, 720×1280, 1280×720, 720×1280, 960×720, 720×964 and 1080×1920. Audio decoded from 01–05 matched the supplied originals over their respective durations less the final 0.1 seconds. 06–07 have no audio streams. Representative rendered frames and selected ending/transition samples were visually inspected; this is not a guarantee of frame-perfect reference fidelity.
