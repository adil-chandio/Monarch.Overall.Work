# Fictional celebrity — cinematic 3D pass

This is a further revision of the one-minute reconstruction, not the lost
original. It retains the ten original narration takes and their timings. The
fictional characters remain actual skinned, animated 3D meshes with motion
clips, blink/smile shapes and approximate hand contact. There are no still-photo
backgrounds. Faces are not lip-synced.

The pass rebuilds the bedroom, kitchen, entrance, road and apartment window;
adds modeled architecture, sidewalk, storefronts, curb and lane paint; places a
licensed 3D sedan, scanned plant, lamp, furniture and PBR materials; revises the
lighting, color, cameras, opening door, and bent-knee sitting. The car interior
is still a modeled cutaway, and the overall look is stylized rather than
photorealistic. The captions follow estimated splits rather than word-aligned
transcription. Motion and prop contacts are not perfect. The synthesized
music/foley are retained; the final mix receives loudness normalization.

## Reproduction

The GitHub Actions workflow `.github/workflows/celebrity-cinematic-3d.yml`
parallelizes 20 three-second Cycles shards. Render settings are 720×1280, 24
fps, eight samples and OpenImageDenoise; final assembly creates H.264/AAC.
Requirements include Python 3.11, Blender Python 4.2.23, PyBullet, NumPy,
Pillow, imageio-ffmpeg, FFmpeg/libass, DejaVu Sans and Linux GL/X libraries.
The asset fetcher uses `gh`, checks every SHA-256 and stores assets outside Git.

```sh
python showreel/celebrity_cinematic_3d/fetch_assets.py /path/to/assets
CINEMA_ASSETS=/path/to/assets python showreel/celebrity_cinematic_3d/probe_scene.py
CINEMA_ASSETS=/path/to/assets python showreel/celebrity_cinematic_3d/render.py \
  --width 720 --samples 8 --stills 2.5,14.5,18.5,24.5,32,42,49,56 --out /path/to/stills
# Render 20 ranges of three seconds, encode them to 00.mp4 through 19.mp4,
# and assemble them:
python showreel/celebrity_cinematic_3d/assemble.py /path/to/clips output.mp4
```

`tests/` checks cue coverage, manifest hashes and attribution. The Blender
pose/framing probe checks seated joint geometry, prop proximity, moving actor
coverage and visible clothing, but does not prove natural animation. Full
credits and licenses, including the CC BY 4.0 sedan attribution and the
Rocketbox MIT notice, are in [ASSET_CREDITS.txt](ASSET_CREDITS.txt).

References consulted: [Kyard's converted and credited assets](https://github.com/yixuanchen189756-source/Kyard-assets#director3d-models-v2),
[Poly Haven materials and props](https://polyhaven.com/license),
[Microsoft Rocketbox](https://github.com/microsoft/Microsoft-Rocketbox),
[Avatar Studio](https://github.com/memoriesrohit/avatar-studio),
[Blender-kit camera/rig reference](https://github.com/Muhrashya/Blender-kit),
and [Filament material documentation](https://github.com/google/filament).
The latter two were consulted for ideas, not incorporated as code.
