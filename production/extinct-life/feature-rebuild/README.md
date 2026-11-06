# Extinct Life — Urdu-English short-shot rebuild

This is a **new complete temporary-voice review cut**, replacing the previous edit rather than appending another opening. Topic and scientific meaning are retained from the eight existing English body sections. The reused 45-second opening is removed, including its repeated exposition.

Output: `deliverables/Extinct_Life_EP01_Urdnglish_ShortShot_Rebuild_1080p.mp4`.

## Actual edit contract

- **404.8 seconds / 6:44.8**, native 1920×1080 / 30 fps; **12,144 frames**.
- **231 shots**, each **at most 2.6 seconds**, with no shot over three seconds.
- Eight newly synthesized temporary **easy Urdu-English** voice sections, selected session voice `voice-01`. This is not the future main English voice-over.
- No old intro/full-film video file is a picture or audio input.
- Every sentence is assigned a visible subject/action in `story.py`. Names such as birch/poplar/conifers, hare/reindeer/geese/mastodon get their own cue stages rather than one generic woodland take.
- **47 subject families**, with individually staged takes, framing, depth, actions and cameras. The film necessarily revisits subjects that recur in the narration; object models are reused, not presented as 231 wholly unique environments. No generic old woodland scene is rendered.
- New material includes molecular fields, shedding/transport, soil/core layers, globe/locator, botanical detail, fossil metaphor, paper fragments, mineral adsorption, laboratory extraction, comparison libraries, inference limits and individual animal actions.
- Settings distinguish molecular magnification, cold coast, plant/animal bank, material strata and lab/archive scenes rather than placing every subject on the same display pedestal.
- Original synthesized score, a sparse three-note motif, speech-envelope music ducking, stereo placement and **22 action-tied designed sound cues**. No blanket whoosh on every cut, music louder than narration to disguise the edit, authentic extinct-animal calls or site recordings.

Maximum-shot duration, exact frame coverage and no imported old video are verifiable. **Zero boredom, hypnosis, flawless creativity and audience retention are not verifiable guarantees.**

## Timing honesty — important

`align.py` uses an eSpeak Urdu reference pronunciation, timbre-normalized MFCCs and dynamic time warping against the **actual selected-voice recordings**. Reference speech is an alignment guide only and is not in the movie. Word/phrase positions are **estimates**, not independently ASR-verified or human-verified word alignment.

`estimated-timings.json` preserves these estimates and their method. `timeline.json` records each shot's narrated sentence, character span, subject, action and frame interval. `story.py` explicitly authors each sentence; long stages are split into additional camera/action takes to satisfy the hard duration limit. This replaces the old five equally divided takes per chapter, but does **not** certify that every word is perfectly synchronized. Phrase-level QA remains an owner-review item.

## Scientific / artistic distinction

Science/rights ledger: `../feature-25d/SOURCES.md`. Primary paper: Kjær et al., *Nature* (2022), DOI **10.1038/s41586-022-05453-y**. This is not a new 2026 discovery or current-oldest-DNA claim.

All coast, mineral/molecular, fossil, lab, animal and habitat imagery is explanatory artwork, not actual study-site footage, sample microscopy, measured reads, specimen reconstructions, a calibrated phylogeny or exact animal appearance/behaviour. Generic fossil imagery does not depict a recovered Greenland mastodon skeleton. Uncertainty, reference limitations, non-detection, mixed deposits and no resurrection/complete genome remain in the translated narration. The date is approximate. Greenland outline is Natural Earth public-domain data; locator is approximate.

Drawing/rig primitives from the approved style are reused as source models. The previous scene/shot edit and video clips are not. No AI/stock photograph, acquired illustration or competitor frame is used as a scene plate. Musical/foley sounds are designed synthetic illustrations, not authentic molecular, extinct-animal or laboratory recordings.

## Source files / reproduction

- `narration-ur.json`: exact temporary spoken Urdu-English text.
- `SCRIPT_REVIEW.md`: original English alongside the translated sections.
- `voice/*.flac`: isolated temporary voice stems, preserved for editing.
- `align.py`, `estimated-timings.json`: reproducible estimated phonetic timing, with limits above.
- `story.py`, `prepare.py`, `timeline.json`: authored subject/actions, timing, original score and sound assembly.
- `stage.html`, `objects.js`, `greenland.json`: actual scene source and data.
- `render.mjs`, `render-checks.json`: deterministic native rendering checks.
- `finish.py`, `QC.json`, `test_contract.py`: final assembly, encoded-media diagnostics and regressions.

Use Node 22, `@napi-rs/canvas@1.1.0`, Python 3.11, numpy, Pillow, imageio-ffmpeg, scipy, librosa and espeakng-loader. Required local DejaVu Serif/Sans fonts are registered in the renderer. No reference model download or remote scene plate is needed.

From the repository root:

```sh
# Runtime voice WAVs can be restored from voice/*.flac with the bundled ffmpeg.
.venv/bin/python production/extinct-life/feature-rebuild/align.py
.venv/bin/python production/extinct-life/feature-rebuild/prepare.py
node production/extinct-life/feature-rebuild/render.mjs --stills
node production/extinct-life/feature-rebuild/render.mjs --verify
node production/extinct-life/feature-rebuild/render.mjs --all
.venv/bin/python production/extinct-life/feature-rebuild/finish.py
.venv/bin/python production/extinct-life/feature-rebuild/test_contract.py
```

Intermediates/previews remain in ignored `.cache/extinct-rebuild/`. For main English narration later, generate/align that recording and retime the edit; do not stretch or blindly swap different-length narration. Native frame drawing does not use fps interpolation.

Technical QC is not a complete real-time audiovisual watch, biological validation or retention test. No YouTube upload/scheduling is performed. Earlier versions remain separate.

## Completed encode checks

The actual file is **53,842,746 bytes**, 404.8 seconds, **12,144 fully decoded frames**. All 231 ledger shots are at most **2.6 seconds**. Encoded audio measures **−16.05 LUFS / −2.49 dBTP**. Black/freeze scanning at the documented settings reported no intervals; **810/810 half-second decoded samples are distinct**. All six regressions pass. Forty-seven subject representative previews and seventeen final-encode samples were inspected. Twenty-four out-of-order seeks were rechecked; all 231 midpoint encodings are distinct. These are not certificates of zero boredom, exact word alignment, biological fidelity or audience response.
