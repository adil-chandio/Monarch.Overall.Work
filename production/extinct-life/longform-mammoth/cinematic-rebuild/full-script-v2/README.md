# Full-story narration v2 — production work, not a film

This folder contains a revised, science-qualified *adaptation*, not a verbatim reading of `../../SCRIPT-V1.md` and not the finished 3D documentary. `SCRIPT-CROSSWALK.md` maps original story points to the draft and explicitly lists context details still requiring an editorial decision. The original draft and prior adaptation remain preserved.

The redundant coat and microbial sections were tightened and retaken with the previously selected voice (`04-coat.mp3` and `09-missing.mp3`). The other eight takes are exact copies of the prior version. There is no speed manipulation. `Narration-Draft-v2.m4a` is a continuous, normalized narration draft with chapter gaps; it contains **no music or sound effects**. It is not a finished soundtrack. The files have not received continuous human listening, pronunciation, performance, script or specialist scientific review.

`take-timeline.json` measures approximately **13:16.042** including gaps and ending. The approved `../FULL-FILM-STORYBOARD-V2.md` remains a creative plan, but its 13:53.759 timestamps refer to the prior takes and are stale after these retakes. Do not use its later numbers as the v2 edit list: align the creative beats to the new take and human-reviewed words. The 287 cues in `English-auto.srt` and `caption-data.json` were automatically aligned and need human proofreading and timing review. Year numerals are included as assumed spoken words during alignment, but the speech model may pronounce them differently; forced alignment cannot prove what was said.

The generation/build and consistency tests do not certify anatomy, animation, sound quality, retention, science or film completeness. No complete 3D film, believable mammoth rig, score, SFX or final editorial review is included. No YouTube publication has been authorised.

## Rebuild and consistency checks

With the repository's Python environment, imageio-ffmpeg, numpy, PocketSphinx, and the ten existing MP3 takes available:

```sh
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/full-script-v2/inspect_takes.py
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/full-script-v2/align_plan.py
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/full-script-v2/build_narration.py
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/full-script-v2/check_sync.py
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/full-script-v2/validate.py
```

`build_narration.py` checks input hashes, adds silence between takes, mixes narration without changing speed, encodes AAC, decodes the whole output and records loudness, peak and hash in `NARRATION-QC.json`. `check_sync.py` correlates the first 3.5 seconds of each take with the corresponding place in the assembled narration; results are in `SYNC-QC.json`. `validate.py` checks take/master hashes, timeline gaps, ordered cue timing and exact caption-token coverage including numerals. These are mechanical checks, not a substitute for listening or viewing.
