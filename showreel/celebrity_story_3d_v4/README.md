# Celebrity life: enhanced 3D edition

A fictional, third-person 60-second scene animation. This revision builds on v3: new English voice selected in the audition, retimed as eight scene cues; a newly synthesized original stereo music/effects bed; redesigned public-event lighting and architecture; more deliberate opening framing; a distinct fan rather than the interviewer repeated; a fan reaction angle; and a walking exit in place of the second repeated hero wave. It retains the improved phone/cup positioning and cleared tables from v3. Event backdrop signage is fictional.

## Sound

The score and effects are synthesized from oscillators and noise in `mux.py`, not sampled recordings or a live orchestra. Cues are individually generated voice WAVs at 24 kHz; the first is sped to 1.17× to fit its shot, with the others at native speed. The code constructs a stereo bed and places narration on the timeline before loudness normalization. Step accents, ceramic tick, phone buzz and camera shutter sounds are authored approximations rather than recorded Foley; steps are not automatically tied to foot contact. The source character, motions and furniture are pinned in `../celebrity_lookdev/assets.json` with licensing details. The voice is synthetic, not an imitation of a real celebrity.

## Reproduction

Fetch pinned assets with `../celebrity_lookdev/fetch_assets.py`; install bpy 4.2.23, Pillow, numpy and imageio-ffmpeg. Render 12 five-second shards at `--fps 24 --width 960 --samples 3` into `clip-00/00.mp4` through `clip-11/11.mp4`; `assemble.py` concatenates and calls `mux.py`. Renderer `--stills`, `--probe` and `--audit` support checking the staging. The foot/toe-to-table AABB audit uses a 0.25-second sample interval and 0.1 m proxy; it does not establish full mesh collision safety. Tests check walk-wrap displacement, cue timing accounting for tempo, blink range and a rig seam.

## Known limitations

This is a stylized real-time-game-like render, not a photoreal motion picture. It reuses Rocketbox action clips and maintains authored approximations for finger grips, cup/phone contact and facial movement. No full mesh, foot-lock or fluid simulation has been performed. There is no documented human listening pass, so the synthetic voice/music/effects should be evaluated by ear on multiple devices before publication; loudness metering and decoding are not substitutes. Crowds and studio are still sparse, and the script remains a fictional observational story, not a real person's routine.
