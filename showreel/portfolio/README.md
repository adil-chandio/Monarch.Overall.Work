# MONARCH portfolio

User-supplied landscape portfolio reference, adapted to the MONARCH name, black/red
palette and the supplied masked character. The portfolio examples are existing project
videos from this repository, not the reference's embedded project footage.

`assets/character.png` is the supplied green-screen image. `assets/reference-sound.m4a`
is the unchanged audio stream from the supplied Drive reference, used at the user's
request for the same music and sound effects. It can contain any voices present in that
reference. Rights to the soundtrack should be checked before public/commercial use.

## Render

From the repository root (Python, NumPy, Pillow, OpenCV and `imageio-ffmpeg` required):

```sh
python3 showreel/portfolio/render.py
```

Source footage is taken from `public/proof/` and the existing `public/demo-preview.mp4`
and `public/demo/demo-short-30s.mp4`; the temporary resized derivatives in
`/tmp/monarch-portfolio` may be deleted to force regeneration. Output:
`public/demo/monarch-portfolio.mp4`.

## Verification

- 1280×720, 30 fps, 1097 frames (36.57 s), H.264/AAC. Reference: 1920×1080,
  approximately 50 fps, 36.55 s. This is an adaptation, not an exact visual replica.
- Full decode completed without errors; frames reviewed at 1, 2, 6, 10, 11, 13, 15,
  18, 19, 21, 24, 26, 27, 30, 33 and 35 s, including full-size intro and project shots.
- FFmpeg audio-stream-copy MD5 is `22d48dcc0721cb91a00e0221a0027ff0` for the
  reference video, extracted audio and finished video. The supplied audio was not
  re-encoded or altered.

## Enhanced edition (v2)

`public/demo/monarch-portfolio-v2.mp4` is a 1920×1080, 30 fps re-render of the
MONARCH portfolio. Run `python3 showreel/portfolio/render_v2.py` from the repository
root. Temporary resized footage is cached in `/tmp/monarch-portfolio-v2`; remove that
cache when replacing source media. It preserves the supplied soundtrack by stream copy.

Changes: animated foreground push and layered graphic depth; timing accents informed by
reference audio peaks; larger moving project cards with rounded frames, shadows and a
subtle tilt; different selections in the last section rather than repeating the first;
section titles, a progress indicator and a branded ending. It uses the same repository
project footage, not frames from the reference. The source character is a still, so the
movement is layered 2.5D rather than a new performance or true 3D animation.

The source audio is unchanged and its rights should be verified before public or
commercial distribution.
