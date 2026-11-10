# The Last Mammoths — 3D opening

**Finished opening:** `deliverables/Last-Mammoths-Opening-01-3D-1080p.mp4` — 60 seconds, 1920×1080, 30 fps, English narration, original score, sound design and burned-in English captions. `English.srt` contains the captions separately. This is the first minute, not the complete long-form film.

## Production

The mammoth, ice, DNA helix, graphics and score are original procedural work. The 3D animal is a **stylised illustration, not a photograph** or scan; the population curve is a schematic of modelled effective population size, not headcount or a diversity curve. The source basis and qualifications are in `SOURCES.md`.

The voice is platform-synthesised voice-04, unsped. Captions use PocketSphinx word-level alignment against the exact known transcript, with the actual narration start offset applied. The word boundaries are automatic estimates, not a claim of human listening review.

The opening narration describes the 2017 coat phenotype as a prediction, not observed loss of insulation, and attributes the later recovery inference to a separate study. The earlier `SCRIPT-V1.md` is a research-stage draft and requires scientific review before any further production.

## Reproduce

The following was tested from the repository root with Node.js, Three.js 0.187.0, Playwright 1.64.1, `@sparticuz/chromium` 153.0.0, Python, numpy 2.4.6, scipy 1.17.1, Pillow 13.0.0, imageio-ffmpeg 0.8.1 and PocketSphinx 5.1.1. These production dependencies are not pinned in the root package manifest. The renderer expects JS packages under the root `node_modules` and Python at `.venv/bin/python`; browser libraries may need adjustment outside this sandbox.

```sh
.venv/bin/python production/extinct-life/longform-mammoth/opening-3d/align_captions.py
.venv/bin/python production/extinct-life/longform-mammoth/opening-3d/build_timeline.py
.venv/bin/python production/extinct-life/longform-mammoth/opening-3d/prepare_sound.py
node production/extinct-life/longform-mammoth/opening-3d/render.mjs --from=0 --to=1800 '--query=furmat=lambert&lights=4&hidemat=lambert&coat=2&under=0.8&clump=0.75'
.venv/bin/python production/extinct-life/longform-mammoth/opening-3d/finish.py
.venv/bin/python production/extinct-life/longform-mammoth/opening-3d/check_final.py
.venv/bin/python production/extinct-life/longform-mammoth/opening-3d/validate.py
```

The rendering cache is `.cache/longform-mammoth-opening/`. `finish.py` refuses an incomplete or stale full render without a matching manifest and video hash. Rendering in the two-core software WebGL sandbox took about 77 minutes; a GPU environment may differ.

## Verification

`DELIVERY-QC.json` records the final SHA-256, full video decode, 1,800-frame count, output dimensions, loudness measurement and one-second sampled frames. Automated measurements and selected still inspection are not a claim of continuous human-style audiovisual watching or a guarantee of creative quality. The visual style is stylised rather than photoreal.

**No YouTube publication has been authorised or performed.**
