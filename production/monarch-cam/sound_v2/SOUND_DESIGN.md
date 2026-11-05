# MONARCH CAM — 30-second Sound V2

## Scope

This is a **soundtrack-only revision** of the approved opening. The H.264 picture stream from `MONARCH_CAM_Bear_Opening_30s_Preview.mp4` is copied without re-rendering. Footage, typography, diagrams, corrected question wording, cuts and narration script remain unchanged. The old procedural drone/noise/air layer is not decoded, filtered or reused.

## Source and placement method

- **Discovery:** Openverse audio records with CC0 licence filters.
- **Rights check:** every candidate's original Freesound page displays CC0 1.0 and commercial modification/use permission. No NC/ND asset and no permission outreach.
- **Selection:** Earshot ranks several fixed 30-second music excerpts for a restrained mysterious documentary score and screens AudioSet voice/vocal labels. If the model route is unavailable, the fixed fallback is the dark orchestral excerpt at 18.0 seconds; this is recorded in `review/music_selection.json`.
- **Frame-exact design:** `cues.json` is derived from the actual picture constants. Earshot locates clean one-shot sections inside the longer whoosh/impact recordings; the mixer then places each excerpt by its own measured 10 ms envelope peak on the requested 30 fps frame.
- **No unsupported action:** no handle pull, latch, door open/close, bear roar or vehicle hit. The 5.7 s entry cut is intentionally without physical foley because the door is already open.

## Mix architecture

1. Approved script, same `en-US-AndrewNeural` narration route and bounded retries.
2. One CC0 instrumental music excerpt, high-pass/low-pass cleanup, slow scene arc, fade-in/out and voice-reactive ducking.
3. One real CC0 forest-night recording at a quiet background level. It is sound-design ambience, not claimed as original NPS camera sound.
4. Licensed pro-produced whoosh and soft-impact excerpts only on visible graphic reveals. Model ticks are short high-passed excerpts of the same impact recording, not newly synthesized tones.
5. Voice envelope: 50 ms measurement, approximately 120 ms look-ahead, 12 ms attack and 260 ms recovery. Music receives the deepest duck; ambience and graphic SFX receive gentler ducking.
6. Two-pass integrated-loudness mastering to approximately −14 LUFS. A conservative −3.5 dBTP intermediate target and limiter operate at loudnorm's 192 kHz internal rate before the final 48 kHz resample, leaving headroom for 192 kbps AAC inter-sample peaks.

## Returned evidence

- `review/resolved_cues.json`: exact frames, measured source peaks and timeline placements.
- `review/music_selection.json`: candidate ranking, vocal screen and selected source range.
- `review/mix_report.json`: source trims, EQ, levels and ducking settings.
- `review/stems_premaster/`: separate voice, music, ambience, SFX and full premaster WAVs (Actions artifact, not committed as large Git blobs).
- `review/MONARCH_CAM_Sound_V2_soundtrack.wav`: mastered stereo soundtrack in the Actions artifact.
- `review/technical_qc.json`: 30 s / 900 frames / stereo 48 kHz, loudness, AAC true peak, clipping/discontinuity checks and V1/V2 video-stream hashes.
- `review/audio_qc.json`: the project's nine measured web-audio gates on the actual delivered AAC stream.
- `review/earshot_*`: final model timeline, annotated review sheet and critique when the model route completes.
- `CREDITS.md` and `review/YOUTUBE_DESCRIPTION_CREDITS.txt`: exact source, creator, licence and modification record.

Measured/model QC is not represented as human listening approval. The user remains the final creative listener, and audience retention or monetisation results cannot be guaranteed.
