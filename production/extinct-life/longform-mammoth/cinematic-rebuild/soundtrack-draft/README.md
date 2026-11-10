# Narration + score draft — not a finished soundtrack or film

`Narration-Score-DRAFT.m4a` mixes the current 796.1-second narration draft (unchanged speech speed) with three excerpts of pre-existing licensed music. It does **not** have picture-synchronised SFX or completed scene transitions, and has not received continuous human listening, pronunciation, intelligibility, sound-design or music-transition review. The older rejected mechanical opening bed is not used. This mix is not proof that every audible sound is acceptable to the user. It must be revised against the final edit.

## Music credits and modifications

- 'Passage Of Time' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au — https://www.scottbuckley.com.au/library/passage-of-time/
- 'Beautiful Oblivion' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au — https://www.scottbuckley.com.au/library/beautiful-oblivion/
- 'A Kind Of Hope' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au — https://www.scottbuckley.com.au/library/a-kind-of-hope/

All three have been excerpted, level-adjusted, faded and mixed under narration. License: https://creativecommons.org/licenses/by/4.0/ . Sources and the unverified relationship between the third-party AAC copies and composer's downloadable masters are documented in `../music-sources/README.md`. The composer requests that, if used on YouTube, attribution also appear in the video description. No YouTube publishing is authorized.

## Rebuild / mechanical QC

```
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/soundtrack-draft/build.py
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/soundtrack-draft/check_sync.py
```

`DRAFT-QC.json` records full decode, hash, loudness and peak; `SYNC-QC.json` checks correlation around the start of each narration take. These do not check the full take, emotional quality or accuracy of any spoken content. The mix is preliminary, not mastered to picture.
