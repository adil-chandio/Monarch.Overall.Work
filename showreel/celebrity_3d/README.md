# Celebrity POV 3D renderer — unfinished experiment

This is a **work in progress, not a delivered video**. `render.py` constructs geometry, lights, camera and simple procedural character motion in Blender's Python API and can render sample stills or attempt a 60-second sequence. It does not use background image plates or stock video. It reuses the earlier user-selected voice clips and a procedural score.

A seven-frame render was technically successful, but visual review showed a rudimentary toy-like character, limited performance and sparse scenes, below the requested premium animation quality. The training scene does **not** yet have a credible foot-to-ball kick; fan interaction and luxury detail are inadequate. The full video has **not** been rendered or reviewed. Still previews are scratch outputs and deliberately not included.

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
