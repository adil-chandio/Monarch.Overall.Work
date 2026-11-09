# Celebrity POV 3D renderer — unfinished experiment

This is a **work in progress, not a delivered video**. `render.py` constructs geometry, lights, camera and simple procedural character motion in Blender's Python API and can render sample stills or attempt a 60-second sequence. It does not use background image plates or stock video. It reuses the earlier user-selected voice clips and a procedural score.

A seven-frame render was technically successful, but visual review showed a rudimentary toy-like character, limited performance and sparse scenes, below the requested premium animation quality. The training scene does **not** yet have a credible foot-to-ball kick; fan interaction and luxury detail are inadequate. The full video has **not** been rendered or reviewed. Still previews are scratch outputs and deliberately not included.

Requirements: Python 3.11, `bpy==4.2.23`, numpy, Pillow, imageio-ffmpeg, Blender's system graphics libraries, and the existing voice clips in `showreel/celebrity_pov/audio`. For debugging only:

```sh
python showreel/celebrity_3d/render.py --stills --samples 2
```

The resulting stills are not a substitute for the requested animated video. A usable production needs a properly licensed, high-quality character rig, animation and interactions, better sets and lighting, render-time optimization, followed by full visual/audio QC. No claim that this depicts Ronaldo's real appearance, routine, or endorsement is intended.
