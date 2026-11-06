# Reference 05 — MONARCH adaptation

`public/demo/monarch-reference-05.mp4` is an approximately 18.07-second, 960 × 720, 30 fps, 542-frame adaptation of the fifth supplied reference. It follows its broad sequence of type, character, object vignettes, ring, hand and closing word, with MONARCH copy and a black/red treatment. It is an approximation, not a pixel-identical recreation: the character and hand are AI-generated still images animated as layered cutouts, not fully animated live-action footage. Pixelated object graphics are adapted Twemoji illustrations rather than the reference's artwork.

## Rebuild

With Python 3, Pillow, NumPy, OpenCV and the FFmpeg helper/dependencies used elsewhere in this repository:

```sh
python3 showreel/seven/render_05.py --reference /path/to/05.mp4
```

The supplied reference itself is not checked in. The renderer encodes the visuals and stream-copies its audio. Original reference audio may contain narration that does not match the changed on-screen copy; the rights to that audio have not been verified. Obtain appropriate permission before publishing. Its HE-AAC track may not play in every browser or player.

## Assets and attribution

- Character and hand images in `assets/05-*.png` were AI-generated for this adaptation.
- Graphics adapted from **Twemoji**, Copyright 2020 Twitter, Inc and other contributors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Source: https://github.com/jdecked/twemoji. The graphics were resized, pixelated and, in one case, recolored. The applicable license text is in `assets/05-icons/LICENSE-GRAPHICS`; the upstream code license is also included there.
- Fonts: Inter (`assets/Inter-OFL.txt`) and Poppins (`showreel/v2/assets/Poppins-Bold.ttf`, license `assets/Poppins-OFL.txt`).

## Validation

All 542 video frames decoded successfully at 960 × 720, 30 fps. The first 18 seconds of decoded audio had matching PCM MD5 `2d3d47d2e8d1921f84c0f0f63b490721` in the supplied source and output.
