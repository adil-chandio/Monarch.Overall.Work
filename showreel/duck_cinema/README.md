# Invisible Thread: ocean shot R&D

This is a **10-second 3D motion test**, not a complete or publish-ready film. It uses a deterministic CPU ray caster: ellipsoid toy geometry, animated water heightfield and normals, lighting, and an independently moving perspective camera. It uses no still images. The toy and waves are stylized reconstructions, not archival footage. The test borrows the opening audio from the prior first-cut MP4; that audio includes generated narration and a synthesized bed.

## Render

Python 3, NumPy, Pillow, imageio-ffmpeg, DejaVu Sans; the audio input must contain an audio stream:

```sh
python -m pip install numpy Pillow imageio-ffmpeg
python showreel/duck_cinema/render_ocean.py --audio /path/to/opening-audio.mp4 --output /path/to/motion-test.mp4
```

Frames are reproducible functions of time. The test is 480x854, 24 fps; it needs serious visual development, a multi-shot edit, sound polish, and final audio mastering before release. Run render and audit before judging quality; it is not the complete duck story.

## Research boundaries

* [2026 Short on the same subject](https://www.youtube.com/shorts/BmPPei5QHKE) and [2025 Short](https://www.youtube.com/shorts/ax7WrLEiXmw) establish that this subject has existing competition, based on search metadata. Their shot-by-shot visuals were not verified.
* [Secondary coverage of fern](https://sigmastory.in/fern-proves-high-end-3d-animation-and-documentaries-are-the-future-of-youtube/) describes 3D spatial reconstructions in long-form documentary; it is a craft reference, not proof of a specific Short's retention.
* [NOAA: Mapping Friendly Floatees](https://sanctuaries.noaa.gov/education/teachers/ocean-mysteries/mapping-floatees.html) gives the primary research foundation: approximately 29,000 bath toys were spilled, and found objects can inform understanding of currents and winds. Do not imply the toys alone mapped the whole ocean or display invented routes as real data.

## Proposed house direction: The Invisible Thread

Blend tactile, cinematic reconstructions with animated, explicitly sourced maps and a gold thread connecting the tiny object to the large system. Sequence ideas: immediate dramatic cause, cargo spill, low waterline toy shot, geographically sourced recovery points, the evidence-to-model connection, and a perspective-flip ending. Camera, surfaces and subjects should move for narrative reasons; do not substitute zooming stills for animation. Avoid unverified trajectories and guarantee no retention outcome.
