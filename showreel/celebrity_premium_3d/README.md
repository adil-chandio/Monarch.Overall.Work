# Fictional celebrity 3D upgrade

This is an independently rendered revision of `celebrity-rebuilt-3d-preview`,
not a recovery of the missing original. It keeps the same ten narration takes,
script timings, score/foley and estimated captions. The protagonist is a generic
fictional person, not a likeness of an actual celebrity.

The revision renders actual moving 3D geometry in Blender Cycles: skinned
Rocketbox people with mocap walk/wave/idle clips, facial blend shapes and
joint-head contact solving; modelled rooms, street, furniture and an animated
car door; physical lights and materials; and shot-specific camera moves. The
render uses 480×854, 24 fps, four Cycles samples with denoising. This is still a
low-sample, game-like/stylized preview, not a photorealistic or production
cinema master. Its sets and automobile remain relatively simple, and facial
animation is not lip-synced. Captions use estimated rather than word-aligned
splits. No photographs or static image backgrounds are used.

## Reproduction

The GitHub Actions workflow `.github/workflows/celebrity-premium-3d.yml` runs
20 independently rendered three-second shards, then joins them with the existing
`celebrity_recovery_3d` audio and captions. The ten source WAVs and timing JSON
are tracked in `celebrity_story_3d_v6/trimmed/` and `script.json`. Runtime
requirements are Python 3.11, Blender Python 4.2.23, PyBullet, NumPy, Pillow,
imageio-ffmpeg, FFmpeg with libass, DejaVu Sans, and the platform graphics
libraries. The asset fetcher requires an authenticated `gh` CLI.

```sh
python showreel/celebrity_premium_3d/fetch_assets.py /path/to/assets
CINEMA_ASSETS=/path/to/assets python showreel/celebrity_premium_3d/render.py \
  --width 480 --samples 4 --stills 3,14.5,32,42,48,56 --out /path/to/stills
# For each shard, render --start i*3 --end (i+1)*3 into PNG frames,
# encode 72 frames to NN.mp4, then:
python showreel/celebrity_premium_3d/assemble.py /path/to/clips output.mp4
```

On minimal Linux installations, `bpy` additionally needs system GL/X libraries.
The characters and furniture are fetched outside the repository, verified by
SHA-256 against `celebrity_lookdev/assets.json`, and never committed.

## Sources, research, and credits

- Rigged avatars and their baked mocap are Microsoft Rocketbox, MIT,
  © 2020 Microsoft, distributed as GLBs by
  [Avatar Studio](https://github.com/memoriesrohit/avatar-studio). The upstream
  [Rocketbox library](https://github.com/microsoft/Microsoft-Rocketbox/tree/0943055db6ec570bcef9f2c8b41c9e5467c808f9)
  and full MIT notice are in [ASSET_CREDITS.txt](ASSET_CREDITS.txt).
- The textured nightstand is Painted Wooden Nightstand by Kirill Sannikov,
  [Poly Haven](https://polyhaven.com/a/painted_wooden_nightstand), CC0 1.0;
  the adapted file is distributed by
  [INTERIO](https://github.com/Sanikaa205/INTERIO/blob/main/public/assets/furniture/LICENSES.md).
- Camera staging and locomotion considerations were compared with the
  [Blender-kit](https://github.com/Muhrashya/Blender-kit/tree/4217423c028bbf7e86f1a65376cc0cbcb9720c97)
  camera/rig notes. PBR principles were checked against
  [Filament](https://github.com/google/filament/tree/d42f15d6bbf1af4da3fec2b5b59b8387eb3ce491).
  Neither project's code is incorporated. The glTF sample repository was also
  examined, but its car asset was not used.

The camera moves are restrained pushes/tracking shots; they do not imply a
continuous one-take capture. The score and foley are synthesized. The motion
clips and contact solves do not guarantee perfect foot planting or prop grips.
