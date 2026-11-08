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

## Original showcase edition (v3)

`public/demo/monarch-portfolio-v3.mp4` replaces the previous repeated project panels
with newly made editing studies and adds an opening hook, intro teasers, section
transitions and a cleaner ending. The supplied masked character, MONARCH black/red
identity and original reference soundtrack remain. It is 1920×1080 at 30 fps.

The new studies are in `public/demo/portfolio-samples/`:

- `time-edit.mp4`, `story-edit.mp4`, `motion-edit.mp4`: three different 9-second,
  540×960 vertical motion studies, with separately synthesized original music/SFX.
- `landscape-01.mp4` through `landscape-04.mp4`: four 960×540 silent editing studies,
  used as video panels in the main portfolio; the main film uses its own soundtrack.

These are original concept studies, **not client projects or actual documentary
footage**. The timepiece, city, workstation, rooftop and prism plates were AI-generated
for this build and animated as 2.5D stills. The user-supplied portrait is also a still;
none of these simulate a live performance. There are cuts, moving text, graphics,
pushes and procedural sound, but the clips should not be described as verified matches
to the source tutorial's production quality.

Rebuild in order (requires NumPy, SciPy, Pillow, OpenCV and imageio-ffmpeg):

```sh
python3 showreel/portfolio/create_samples.py
python3 showreel/portfolio/render_v3.py
```

Resized intermediary footage is cached in `/tmp/monarch-portfolio-v3`; delete that
cache after changing the source samples so the portfolio renderer regenerates them.
The final portfolio soundtrack is stream-copied from `assets/reference-sound.m4a`.
It may contain third-party music, so rights must be checked before public/commercial use.

### Research

YouTube tutorial descriptions and available transcripts were reviewed; direct video
playback was not available in the sandbox. Techniques considered were layered imagery,
word-by-word text, fast but readable cuts, easing and timing effects to the soundtrack:

- [Sharp Motion: documentary-style editing tutorial](https://www.youtube.com/watch?v=wzPGp7X9xwQ)
- [Drew Mahadi: viral reels and shorts in After Effects](https://www.youtube.com/watch?v=3XxmmPon_9A)
- [Short-form hook guide](https://www.capcut.com/create/short-form-video-hooks-first-3-second-patterns)

The studies use new images and type, not frames or audio from those tutorials.

V3 verification: final H.264 video has 1097 frames at 30 fps; all seven studies and
the final MP4 decoded without errors. The final's copied AAC stream hashes to
`22d48dcc0721cb91a00e0221a0027ff0`, the same as the supplied soundtrack. Full-size
frame review included the opening transition, intro, all showcase sections and close.

## Seven-reference showcase edition (v4)

`public/demo/monarch-portfolio-v4.mp4` keeps the v3 main portfolio's masked-character
intro, black/red identity, overall 36.57-second structure and original main-portfolio
soundtrack. The old generic sample screens have been replaced with moving excerpts from
all seven `public/demo/monarch-reference-0N-enhanced.mp4` files:

- Intro teasers: 01 and 03.
- 12–18 seconds: 02, 04 and 06.
- 18–25 seconds: 01, 03 and 05.
- 25–35 seconds: 02, 07 and 04 (different excerpts, with 07 in the center).

These are **selected excerpts playing simultaneously**, not the complete seven videos
played sequentially. They are fit into landscape or portrait display panels with padding
rather than stretched or center-cropped; the rounded panel corners/tilts may conceal a
small part of the picture edges. Video 06 uses its enhanced main-frame-only crop, with
no behind-the-scenes editing timeline. The showcase panels are silent in the main film:
the supplied main-portfolio reference soundtrack is stream-copied instead of mixing all
seven audio tracks. This soundtrack's rights must be checked before public/commercial
use. The enhanced reference adaptations are approximations with 2D/2.5D motion, not
fully animated 3D; see `../seven/enhanced/README.md`.

Rebuild from the repo root, with Python, NumPy, Pillow, OpenCV and imageio-ffmpeg:

```sh
python3 showreel/portfolio/render_v4.py
```

The seven enhanced MP4s and `assets/reference-sound.m4a` are inputs. Resized silent
panel clips are cached in `/tmp/monarch-portfolio-v4`; remove that cache if replacing
an input. The previous v3 and standalone enhanced videos are not overwritten.

Verification: the finished H.264 video is 1920×1080, 30 fps and 1,097 frames. Full
frame decode, representative full-size showcase-frame review, and decoded PCM audio
comparison to the supplied main-portfolio soundtrack were performed.

## Smooth character edition (v5)

`public/demo/monarch-portfolio-v5.mp4` retains the v4 layout and all seven enhanced
showcase clips. It renders at 1920×1080, 60 fps. The character entrance uses a
zero-velocity ease at the ends and a gentler push-in, without the earlier per-beat scale
impulses. Character scale and position are combined in a single subpixel transform on
the foreground layer, with premultiplied alpha to reduce edge fringing; the outro uses
the same compositing method. Intro teaser positions were also adjusted to stay clear of
the lower progress rule while entering. The source is still a photograph: this animates
the foreground layer, not actual facial or body performance. A higher output frame rate
is not a guarantee that every pre-existing source animation has unique 60 fps motion.

Build from the repository root using the same dependencies and enhanced clips as v4:

```sh
python3 showreel/portfolio/render_v5.py
```

Panel intermediates live in `/tmp/monarch-portfolio-v5`; remove this cache when
changing their source files. The reference soundtrack remains unchanged and its rights
must be checked before public/commercial use. The standalone clips and v4 remain intact.

Verification: all 2,194 H.264 frames decoded at 60 fps. Intro, showcase and ending
frames were inspected; no identical consecutive downsampled output frames were found
during the checked 3–8 second intro segment. Decoded audio PCM matched the complete
main-portfolio soundtrack (MD5 `f0fb78634e642844b65445290562cc26`).
