# Celebrity POV 3D renderer — unfinished experiment

This is a **work in progress, not a finished video**. `render.py` constructs geometry, lights, camera and simple procedural character motion in Blender's Python API and can render sample stills or attempt a 60-second sequence. It does not use background image plates or stock video. It reuses the earlier user-selected voice clips and a procedural score.

A seven-frame render was technically successful, but visual review showed a rudimentary toy-like character, limited performance and sparse scenes, below the requested premium animation quality. The training scene does **not** yet have a credible foot-to-ball kick; fan interaction and luxury detail are inadequate. The original `render.py` version was not rendered as a full video. The separate rigged technical draft described below was rendered and sampled, but it remains below the requested quality. Still previews are scratch outputs and deliberately not included.

Requirements: Python 3.11, `bpy==4.2.23`, numpy, Pillow, imageio-ffmpeg, Blender's system graphics libraries, and the existing voice clips in `showreel/celebrity_pov/audio`. For debugging only:

```sh
python showreel/celebrity_3d/render.py --stills --samples 2
```

The resulting stills are not a substitute for the requested animated video. A usable production needs a properly licensed, high-quality character rig, animation and interactions, better sets and lighting, render-time optimization, followed by full visual/audio QC. No claim that this depicts Ronaldo's real appearance, routine, or endorsement is intended.

## Rigged-character experiment

`render_rigged.py` uses an articulated mannequin and looping CC0 animation from Quaternius, sourced through `shonejj/WorldapocalypticRetrogame` commit `ae169369be6d8be92d8c52d97c19469d48091991` (`public/models/survivor.glb`, Git blob `5f9388ca0f0b976cbd337bcccbee29f2d3724e70`). See `assets/LICENSE-CC0.txt`. The character is a generic mannequin, **not** Ronaldo's face or likeness. It is still a rough technical pilot: no accurate ball kick, hands, fan interaction, facial performance, realistic body/outfit or premium production finish. Brand/name refers to an imagined scenario, not verified facts or endorsement.

For chunked rendering, `--start` / `--end` select integer-second boundaries and `--silent` creates a video-only clip; `mux.py` concatenates twelve 5-second clips and adds existing synthetic narration plus original procedural sound bed. Test any resulting video for animation, audio synchronization and quality before calling it finished.

## 60-second technical draft (rigged test)

`deliverables/monarch-celebrity-pov-rigged-pilot.mp4` is a 60.000-second, 360×640, 24 fps draft: 1,440 generated frames, H.264 video and mono AAC, reusing the previously selected narration. Twelve clips were rendered from Blender geometry and assembled with an original procedural bed; the full file was decoded in QC. Source SHA-256 is recorded in `docs/repo-intel/celebrity-3d-rigged-render.json`; the delivered file's SHA-256 is `a0444b7e0268ca5fad39e94a7272521be9254b7c4103f588c63875028d7e5252`.

**This is not a premium or publication-ready result.** The generic CC0 mannequin has no Ronaldo likeness or facial performance, character actions repeat, the ball is not convincingly kicked, fan interaction is limited, and the lounge sequence holds for a long time. It is mostly third-person rather than a continuous first-person POV. The sets and low-resolution lighting remain basic and narration/music have not been independently listened to for quality. File decoding and contact-sheet checks do not prove audiovisual or creative quality. The “FICTIONAL” label is on screen; the story is imagined and is not a factual private routine or endorsement.

## Experimental action sequencing

`--experimental-sequences` enables seekable Blender NLA action clips and crossfades; `action_timeline.py` is an opt-in experiment based on timing and blending principles reviewed in `docs/repo-intel/ANIMATION-REPOSITORIES-REVIEW.md`. Test with Blender's bpy Python: `python showreel/celebrity_3d/tests/test_action_timeline.py`. This does not add football-specific actions or make the existing pilot finished. The parallel draft workflow is manually triggered to avoid automatically rendering the old pilot on unrelated changes.

## Experimental kick blocking (not a finished shot)

`render_rigged.py --experimental-kick` enables an additive right-thigh pose sequence and deterministic ball collision bake. The ball starts moving only when the sampled toe proxy closes on it; a low, ball-following camera is cut in for the strike. The simulation uses a spherical ball/foot proxy, fixed substeps, gravity, a simple ground bounce, rolling friction and a simplified impulse. It is **not a physically complete simulation**: no aerodynamic drag, spin dynamics, real foot collision shape, deformable body, full limb IK, ground reaction or calibrated athletic motion. Impact is approximated between substeps and may miss very fast/tunneling collisions. Ball roll is only approximate.

Tests: `python -m unittest discover -s showreel/celebrity_3d/tests -p 'test_football_physics.py' -v`; then run `tests/test_action_timeline.py` and `tests/test_kick_experiment.py` under the bpy environment. The integration test found one proxy impact at approximately 18.943 s, confirms pose changes under Blender's evaluated NLA, no pre-contact ball movement, ground bounds and reproducible bakes. A two-second 180×320 one-sample animation rendered; eight frames at 4 fps were inspected. These checks are not continuous-motion or audio QC and do not establish realism. The visual test still shows a faceless mannequin, abrupt camera follow, weak upper-body/leg performance and very sparse surroundings; it is not a premium football shot and has not been published as the final video.
