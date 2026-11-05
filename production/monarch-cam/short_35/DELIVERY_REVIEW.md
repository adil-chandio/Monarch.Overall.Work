# Final Delivery Review — This Bear Didn’t Need the Door

**Delivered file:** `deliverables/MONARCH_CAM_This_Bear_Window_35s_Short.mp4`  
**Final production run:** `42069978281`  
**Branch:** `arena/c678cc81-monarch-overall-work`  
**Delivered SHA256:** `df189a7ae250be4e7c1fd62b5a7ef566ec3bfed8aace28d47884407a8c09df24`

## Creative result

A native 1080×1920, 35.000-second Short built from the explicitly public-domain NPS *Bears in Cars* footage. The hook is the real window action, not a claimed handle opening. The 70-word narration moves from the immediate physical question to a general food-conditioning explanation, then closes with prevention and a return to the opening angle. The original **SEARCH → FOOD REWARD → CHECK AGAIN** diagram is an explanatory model, not a claim about this individual bear’s unrecorded history.

No handle pull, door movement, food reward, attack, bear vocalisation or native camera audio is fabricated. No virality or audience-retention result is promised.

## Measured delivery

| Check | Result |
|---|---|
| Duration / frames | 35.000 s / 1,050 frames |
| Picture | 1080×1920, H.264, 30 fps |
| Audio | AAC, 48 kHz stereo |
| Delivered AAC loudness | −14.31 LUFS integrated |
| Delivered true peak | −3.30 dBTP |
| Nine-gate audio QC | All nine passed |
| Technical QC | All nine passed |
| Click runs / clipping runs | 0 / 0 |
| Narration slots | 70 words, all phrases inside their slots with headroom |

Mastering used the proven V2-style two-pass loudnorm, conservative 192 kHz limiting and AAC-domain calibration. No QC gate was bypassed or weakened.

## Visual and model-assisted review

The first frame, cover and 12-frame vertical contact sheet were reviewed at phone scale. The final revision:

- tightened the archival action crop by 10% while preserving the 4:3 vehicle context;
- moved captions closer to the action window;
- accelerated the three-step learning-loop reveal;
- held the prevention caption through the final frame for a clearer loop/payoff;
- restored the installed Earshot API’s lazy model loading so SFX selection, timeline, sheet and critique all ran.

Earshot returned **launch-grade**, with 22/23 scored metrics in range, 0 critical and 0 major issues. Its one minor advisory was a thin low end. This was reviewed and intentionally accepted: adding a cinematic sub-drop or kick would imply an unsupported event and risk masking narration. The model also reported that two very quiet diagram ticks were not detected as onsets; those are restrained −31 dBFS graphic accents, not missing picture events. Model output is advisory evidence, not human listening approval.

## Review artifacts

- `review/vertical_contact_sheet.jpg` — 12-frame visual review
- `review/cover.jpg` — cover reference
- `review/technical_qc.json` and `review/audio_qc.json` — measured gates
- `review/voice_ledger.json`, `review/cue_ledger.json`, `review/visual_edit_ledger.json` — exact timing/source records
- `review/earshot_timeline.json`, `review/earshot_sheet.png`, `review/earshot_critique.json` — model-assisted review
- `review/mastering_calibration.json`, `review/click_repair.json`, `review/source_mix_report.json` — sound provenance and calibration
- `CREDITS.md`, `review/UPLOAD_METADATA.txt`, `review/FINAL_NARRATION.txt` — upload package

## Release caveat

All objective gates and advisory reviews pass. Actual **stayed to watch, engaged views, average view duration, percentage viewed, loops and subscriber lift** can only be judged after publication in equivalent windows. Virality remains an objective, not a guarantee.
