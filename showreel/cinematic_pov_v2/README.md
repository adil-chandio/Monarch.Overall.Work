# Reference-inspired celebrity POV: second cinematic draft

One-minute, 960×540, 24 fps, fictional 2D animation. No source imagery, reference character design, stock footage, or reference audio is used. Every frame is generated from drawing primitives, gradients, blur and lighting overlays. Some scene elements deliberately hold or repeat. Existing selected synthetic narration is reused; it is not an imitation of a celebrity's voice. The imagined day is not a factual account of Ronaldo's private routine or an endorsement.

Changes since `cinematic_pov`: layered environment details, softer atmospheric clouds and light, shot-local camera push/track, pupil blinks and garment details, a first-person cup reach/lift/return, a first-person football contact beat and a hand-held phone insert. The ball and shoe use an authored geometric contact cue; this is **not** simulated rigid-body physics or real athletic motion. Sound bed has original synthesized cues for some visible moments, not recordings from the reference. Narration subtitles are paraphrases.

Reproduce with Pillow, NumPy and imageio-ffmpeg:

```sh
python showreel/cinematic_pov_v2/render.py --output deliverables/monarch-cinematic-pov-v2.mp4
python -m unittest discover -s showreel/cinematic_pov_v2/tests -v
```

QA: four automated tests passed (timeline and audio files, authored ball-contact geometry and release order, frame dimensions and repeatability, changes across selected frame pairs). One complete candidate was sampled at 1 fps across 60 seconds plus 8 fps for the football insert and 4 fps for the cup insert. Those samples revealed the cup visually separating from the hand; the grip and cup return were corrected, and the final cup section was rechecked at 4 fps. The final file was fully decoded: 1,440 frames, 60 seconds, with audio. `volumedetect` reported mean -17.5 dBFS and max -1.4 dBFS; neither is integrated loudness or true peak. **No human audio listening or every-frame visual QC was performed**. SHA-256 `96addd9408741798ee191573b110fc9788532593095d916dd691dc6ac6aee92c`.

Limitations: character acting, foot planting, asset detail, staging and audio remain simplified; the scenery and character are not at the reference's quality. The scene is 2D with simulated camera moves; not a real 3D/physics render. This is an improved draft, **not a perfect, final or publication-ready reference match**.
