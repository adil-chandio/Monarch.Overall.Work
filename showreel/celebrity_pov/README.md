# Celebrity POV animated pilot

60-second vertical test, English, 540×960, 30 fps. This is a fictional, illustrative Ronaldo-inspired day, not his verified private routine or an endorsement. The number 7 is generic; no real voice is cloned. It is a creative pilot, not a finished publication master.

## Production and limitations

- Three original AI-generated illustrated background plates, no stock footage or A/B-roll. They are **static illustrations**, with small camera movement; they are not genuine 3D environments. Foreground crowd, characters, limbs, ball, shadow, props, text and light flashes are independently redrawn and animated each frame. This is a lightweight **layered 2.5D-style** animation, not a fully rigged 3D production or proof of competitor quality.
- English narration generated with the user-selected synthetic voice. Music and transition tones are synthesized procedurally by `render.py`; no stock music or sound effects.
- This first test uses a simple code-drawn stickman and repeated environments. Walk cycles may have foot sliding and scene interaction is limited; the camera mostly shows third-person staging rather than continuous first-person perspective. Human review, rights/policy review, sourcing and refinement are needed before publication.
- Video duration 60s / 1,800 frames; observed integrated audio approximately -16.7 LUFS and true peak -1.37 dBTP, below the repository's -14 LUFS target, so not a final mastered mix. Timing verified against voice clip durations; captions are concise paraphrases rather than verbatim subtitles.

## Render

Install Pillow, NumPy, and imageio-ffmpeg in your Python environment, then from the repo root:

```
python showreel/celebrity_pov/render.py --output deliverables/monarch-celebrity-pov-test.mp4
```

The generated image assets and selected-voice audio clips used by the renderer are stored alongside it for reproducibility. An unrelated past forensic report remains incomplete; this prototype does not claim to replicate any unviewed competitor's animation.
