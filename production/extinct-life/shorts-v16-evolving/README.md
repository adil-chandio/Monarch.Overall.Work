# V16 — Evolving visual story

A separate revision of the positively received V15 Short, focused on the user's correction: **do not keep returning to the same scene/frame; give each narration beat a new, relevant event.** V15, the full films and the selected thumbnail remain unchanged.

## What changes

Ten successive sets: mastodon opening → supported sediment sampling → lab-to-molecular reveal → environmental shedding → mineral binding → partial reference comparison → river-basin ecosystem → evidence limits → authentication questions → geological investigation journey. The opening mastodon/forest and the reference table do **not** return as an ending. The limits set has two separate actions: an empty supported specimen cradle, then incomplete slots.

The English narration, captions, selected voice and V15 timing remain unchanged. Original liquid, river and canyon cues supplement the retained voice/music mix; these are synthetic illustrative sound design, not field recordings or competitor audio.

**Render provenance:** V15 frames `[0,323)` are retained once as the liked opening/sampling segment. V16 frames `[323,1305)` are newly rendered: **982 new native 1080×1920 frames**, not a claim that all 1,305 frames are new. The final assembly is re-encoded at 30 fps, 43.5 seconds; there is no frame interpolation or lower-resolution 3D upscale. The renderer records the actual scene ID on every captured new frame and consolidates contiguous scene runs. The finisher requires ten distinct, contiguous runs over the complete edit, with no scene-ID re-entry.

## Deliverable and evidence

- `deliverables/Extinct-Life-V16-Evolving-Story-1080x1920.mp4`
- `DELIVERY.json`: exact file hash, bytes and format.
- `QC.json`: full-video decode, sampled image signal, actual encoded AAC loudness, source hashes, actual scene runs and preservation checks.
- `review/`: native encoded-frame extractions and a 45-position reduced overview (generated locally, image intermediates ignored by Git).
- `CREATIVE-REVIEW.md`: observations and limitations of the review actually performed.
- `English.srt`: unchanged companion captions; subtitles are also burned into the movie.

## Rebuild

Run from the repository root with the existing Node dependencies and `.venv` film toolchain. `DEPENDENCIES.json` records browser/Three.js versions. The existing V15 `.cache/shorts-v15/mix.wav` is the audio precursor; if absent, regenerate it with V15's `film/sound.py` and its original selected recordings. Do not substitute newly synthesized speech. The protected V15 MP4 is the video precursor.

```sh
.venv/bin/python production/extinct-life/shorts-v16-evolving/film/prepare_sound.py
mkdir -p .cache/shorts-v16/stills
node production/extinct-life/shorts-v16-evolving/film/render.mjs --stills --frames=390,990
node production/extinct-life/shorts-v16-evolving/film/render.mjs --from=323 --to=1305
.venv/bin/python production/extinct-life/shorts-v16-evolving/film/finish.py
.venv/bin/python production/extinct-life/shorts-v16-evolving/film/test_timeline.py
```

A still check is **not** a final encoded-video review. `finish.py` checks the render receipt against the current scene and timeline, decodes all 1,305 encoded frames, extracts final native review images, measures encoded AAC and verifies protected predecessor hashes. It does not certify subjective quality. Local source preview: `node .../film/render.mjs --serve --port=4194`; the preview is not the final MP4.

## Scientific and review limits

This is stylized explanatory CGI, not photoreal footage, a surveyed reconstruction, an exact molecular simulation or an anatomically certified animal model. The basin/canyon are imagined conceptual environments. Lab tools, cradle, slots and gates are illustrations, not a claim about the original study's hardware, genome completeness or measured confidence. The three question-mark gates ask about authenticity, damage and references; they do not assert fabricated passing results. Mineral protection does not mean perfect preservation. No resurrected animal or complete mastodon genome is claimed.

Ten sets and technical tests do not prove a subjective “3×” improvement, perfection, continuous audiovisual listening, or owner creative acceptance. Reference research remains ten audio-model passes, not ten exhaustive human audiovisual studies. No YouTube publication is authorized or performed; a real related-video target must be configured separately before publishing the Short there.
