# Reference 07 — MONARCH adaptation

`public/demo/monarch-reference-07.mp4` is a 23-second, 1080 × 1920, 60 fps adaptation of the seventh supplied reference. It follows the reference's broad sequence: warrior reveal, ornate frame and captions, typography, portrait, hands, raised fist and closing helmet. The visuals and words are adapted for MONARCH in a red, black and white palette.

Following the request to remove the behind-the-scenes editing timeline from video 6, this version presents the main vertical composition full-screen rather than reproducing the reference's surrounding timeline and editor badge. The original reference contains no audio stream, so the output is silent.

This is an approximation, not a pixel-identical recreation. The six warrior, helmet, frame and hand illustrations in `assets/07-*.png` were independently AI-generated; motion is 2D layer animation rather than original footage or fully animated 3D characters. The imagery is symbolic creative direction, not a claim about an actual historical person or MONARCH project.

## Rebuild

Requires Python 3, Pillow, NumPy, OpenCV and the FFmpeg helper/dependencies used elsewhere in this repository:

```sh
python3 showreel/seven/render_07.py
```

The render does not require the supplied reference. Fonts: Inter (`assets/Inter-OFL.txt`), Oswald (`assets/Oswald-OFL.txt`), Instrument Serif (`assets/InstrumentSerif-OFL.txt`) and Poppins (`assets/Poppins-OFL.txt`).

## Validation

All 1,380 frames of the output decoded successfully at 1080 × 1920 and 60 fps. FFmpeg confirms a 23-second video-only file, matching the reference's lack of an audio stream.
