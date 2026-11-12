# Fictional celebrity — deluxe 3D revision

A further reconstruction of the one-minute fictional story, not a recovery of
the lost original. This builds on `celebrity_cinematic_3d`: the ten established
narration takes and 24 fps timeline are retained. The scenes and generic skinned
actors remain fully modeled 3D, with no photographic backdrop.

## What changed

- Actual 1080 × 1920 Cycles render at 16 samples with OpenImageDenoise, tighter
  adaptive sampling and a higher-quality denoise prefilter; it is not upscaled.
- Hand-following phone pickup, a modeled hollow cup/open handle, and a closer
  palm meeting over the street barrier. These contacts are approximate; the
  system is not a collision-aware, fully hand-keyed performance.
- Folded bedding, additional set dressing and bystanders, refined kitchen and
  car coverage, a warmer night interior, a modeled night skyline and gentler
  moving camera work.
- A new stereo mix with an identified CC0 piano recording, recorded film-premiere
  crowd ambience, distant traffic, steps, a car-door effect and camera shutters.
  The same ten original narration takes are retained. Captions are styled for a
  safer portrait-frame margin, and their split points were checked against pauses
  in those recordings; they are not word-aligned captions.

The result is a **stylized 3D preview**, not a photorealistic cinema master.
Characters are generic fictional avatars, facial animation is not lip-synced,
and fingers, gaze, walk/foot contacts, the cutaway vehicle and buildings remain
simplified. Low-sample denoising can flicker in motion. Automated checks and
sampled stills cannot replace continuous viewing or critical listening.

## Reproduce

The workflow `.github/workflows/celebrity-deluxe-3d.yml` renders forty 36-frame
(1.5-second) shards and assembles them in timeline order. Requirements: Python
3.11, `bpy==4.2.23`, `numpy==2.2.6`, `Pillow==13.0.0`,
`imageio-ffmpeg==0.8.1`, `pybullet==3.2.7`, FFmpeg with libass, DejaVu Sans,
and the Linux GL/X runtime. `gh` fetches all hash-pinned licensed assets.

```sh
python showreel/celebrity_cinematic_3d/fetch_assets.py /path/to/visual-assets
python showreel/celebrity_deluxe_3d/fetch_assets.py /path/to/visual-assets --group visual
python showreel/celebrity_deluxe_3d/fetch_assets.py /path/to/audio-assets --group audio
CINEMA_ASSETS=/path/to/visual-assets python showreel/celebrity_deluxe_3d/probe_scene.py
CINEMA_ASSETS=/path/to/visual-assets python showreel/celebrity_deluxe_3d/render.py \
  --width 1080 --samples 16 --stills 3.5,5,14.5,24.5,42,49.5,56 --out /path/to/stills
# Render the forty ranges, encode as 00.mp4 … 39.mp4, then:
python showreel/celebrity_deluxe_3d/assemble.py /path/to/clips /path/to/audio-assets output.mp4
```

`probe_scene.py` samples seated posture, phone and cup position, palm distance,
doorway joints and hero visibility. Tests check timeline coverage, caption pause
locations and source metadata. Neither establishes convincing motion or sound
quality. Complete attribution and license notices are in `ASSET_CREDITS.txt`.
