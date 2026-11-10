# The Last Mammoths — 3D opening (work in progress)

This is the source for a planned 60-second, 1920×1080, 30 fps opening. **The current revision has not been rendered or approved as a finished video.** An older local MP4 predates the visual and scientific corrections and must not be treated as the finished deliverable.

## Current state

- Original procedural Three.js mammoth, ice, DNA and case-board scenes; generated English voice and an original procedural score.
- Narration now describes the predicted coat phenotype as a prediction, not observed loss of insulation; the later population recovery inference is attributed to a separate study.
- Current sampled stills show visible, faceted, patchy coat tufts. They do not yet meet the requested premium visual quality. Fur coverage, materials and lighting need more work before the full render.
- Captions are approximated using speech activity and character-weighted timing, **not forced alignment**; they require a listening pass and manual correction. The original voice take remains unsped.
- Thirty-frame software-render tests took about 3.27 seconds/frame for a denser candidate and 2.17 seconds/frame for a sparser candidate, excluding browser startup. No current candidate has met the previous 1.5 seconds/frame goal in that production-path test. These figures are from a two-core CPU/SwiftShader environment, not GPU performance.
- The earlier long-form `SCRIPT-V1.md` is a research draft and still needs a full science and language review before production; its old cold open is superseded by the corrected take in this folder.

## Build and review

From the repository root, with Node.js, Three.js, Playwright, `@sparticuz/chromium`, Python, numpy, scipy, Pillow and imageio-ffmpeg installed. Tested versions: Three.js 0.187.0, Playwright 1.64.1, `@sparticuz/chromium` 153.0.0; Python packages numpy 2.4.6, scipy 1.17.1, Pillow 13.0.0 and imageio-ffmpeg 0.8.1. These dependencies are not yet pinned in the repository manifest:

```sh
.venv/bin/python production/extinct-life/longform-mammoth/opening-3d/align_captions.py
.venv/bin/python production/extinct-life/longform-mammoth/opening-3d/build_timeline.py
.venv/bin/python production/extinct-life/longform-mammoth/opening-3d/prepare_sound.py
node production/extinct-life/longform-mammoth/opening-3d/render.mjs --stills --frames=100,200,340,600,900,1200,1600
.venv/bin/python production/extinct-life/longform-mammoth/opening-3d/validate.py
```

The renderer expects packages in the root `node_modules`, Python at `.venv/bin/python`, and its cached audio in `.cache/longform-mammoth-opening/`. It uses a headless software WebGL renderer and a sandbox-specific `LD_LIBRARY_PATH`; another machine may require adjusting browser dependencies. Scene profiles such as `--query=aa=0&furmat=lambert&lights=4&hidemat=lambert&coat=1.6&under=0.4` are experimental, not a locked production look. Stills and test segments are generated in `.cache/`.

When visual, caption and scientific review is complete, a full render is `node production/extinct-life/longform-mammoth/opening-3d/render.mjs --from=0 --to=1800` (with the chosen query). `finish.py` will refuse an incomplete or stale render without a matching manifest. Run `check_final.py` only after successful muxing and then review the actual finished video with sound; automated checks cannot certify creative quality.

## Provenance and limits

The mammoth, environment, case-board graphics and soundtrack are original procedural work. The animal is an illustration, **not a photograph**, scan or recorded footage; the graphs are schematic, not literal measurements. Sources and qualifications are in `SOURCES.md`. The population curve represents a schematic model of effective population size, not headcount or a diversity curve.

**No YouTube publication has been authorised or performed.**
