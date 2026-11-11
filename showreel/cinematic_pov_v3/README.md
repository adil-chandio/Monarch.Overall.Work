# Celebrity POV — motion and contact pass

A one-minute, 960×540, 24 fps illustrated test derived from the preceding reference-inspired draft. All visual frames are generated from procedural shapes, gradients and effects; no reference frames, still-image backgrounds or stock footage are used. A fictional celebrity day is illustrated, not a verified private routine, likeness or endorsement. Existing selected synthetic narration and a procedural music/SFX mix are used; no celebrity voice clone or reference audio.

## Changes

- A wake-up pose now precedes the face reaction; first-person mug and football shots remain.
- Walking/running use a distance-driven gait with world-space planted stance, lifted swing and two-link knee IK; path speeds were reduced to keep targets within limb reach. Footstep cue times are computed from gait landings, rather than manually placed at unrelated times.
- In two football shots, the authored toe/ball contact happens before release. After release, the ball follows a constant opposing rolling deceleration until stopped and spins approximately by travel distance divided by radius. Contact sound cues align with the authored moments. This is not a full rigid-body collision or measured football performance.
- The sky has a stylized compressed-day sun arc; previously added layered sets, shadowing, restrained glow, blur and shot-local camera moves remain. These are illustrations and screen-space effects, not physically based graphics.

## Verification and limitations

Ten automated tests pass: gait stance and swing continuity, limb lengths for reachable targets, non-reversing friction model, authored contact geometry, cue times, selected image changes and deterministic seeking. FFmpeg decoded the full output: 1,440 frames in 60 seconds, with audio. I directly inspected 60 one-fps output samples, plus approximately 14 samples of the 5.7–8s walk at 6 fps, 12 samples of the 16.65–17.65s kick at 12 fps and 10 samples of the 19.1–20.4s POV contact at 8 fps. These sample timestamps are approximate. No human audio listening or inspection of all frames was done; mean/max volumedetect -17.5/-1.4 dBFS is neither LUFS nor true peak. File SHA-256 `02fcf10d2a63f5b7cd67f0135e5c91fdf7d05c66ad0a83d435c01e818eb08b2b`.

**Important:** This is stylized 2D blocking, not realistic full-body biomechanics, a calibrated physics simulation or a reference-quality finished film. Heel/toe rotation, leg weight, torso balance, collisions with other objects, airflow, true 3D perspective, changing lighting, richer performance and aural quality are not fully solved. Output inspection indicates the body and environments remain visibly simple, especially held scenes. These tests do not certify aesthetic quality.

## Reproduce

```sh
python -m unittest discover -s showreel/cinematic_pov_v3/tests -v
python showreel/cinematic_pov_v3/render.py --output deliverables/monarch-cinematic-pov-v3.mp4
```

Requires Pillow, NumPy, imageio-ffmpeg and the existing `showreel/celebrity_pov/audio` files.
