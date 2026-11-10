# V2 storyboard retiming — provisional

`retime.py` maps the 82 original V2 blocks to the 796.042-second revised narration. Identical voice takes use measured offsets; the two retakes use matching automatic caption words and interpolation. `storyboard-retimed-draft.json` explicitly flags all 13 blocks touching the rewritten sections. This mapping produced some unusably short candidate blocks, so it must not be treated as a picture edit.

`rebuild_retake_blocks.py` replaces those blocks with clause-oriented intent for the changed sections, based on provisional auto captions. `storyboard-retimed-reblocked.json` contains 83 contiguous draft blocks. Both files are **plans**, not rendered footage or listening/science/rights/creative sign-off. The original storyboard and old timings remain preserved.

```
python3 production/extinct-life/longform-mammoth/cinematic-rebuild/storyboard-retime/retime.py
python3 production/extinct-life/longform-mammoth/cinematic-rebuild/storyboard-retime/rebuild_retake_blocks.py
```

Do not assume machine captions perfectly match spoken syllables; listen to the revised narration and adjust cuts and actions. The reblocking describes intent and may need further changes once actual actions, music and transition handles exist.
