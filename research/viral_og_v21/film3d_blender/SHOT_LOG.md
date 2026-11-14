# Blender shot log — real-geometry bear for EP01

Everything in this folder replaces the raymarched "blob" animal of the v3 cut with a
mesh that has an actual silhouette, an actual face and actual keyframes. It runs
headless on this box: `bpy` 4.2.0 as a Python module, Cycles on 2 CPU cores, no GUI
and no GPU (see `tools/blender_local/BLENDER_LOCAL.md`).

## Files

| file | what it is |
|---|---|
| `shots/bear_shot3.py` | character + set + camera builder and a stills renderer |
| `shots/bear_walk.py` | the 10 s animated shot (240 frames @ 24 fps) |
| `shots/encode_shot.py` | PNG sequence -> H.264 mp4 (imageio-ffmpeg binary in this image) |
| `make_cut_blender.py` | splices the shot into the 60 s episode master, keeps the v3 audio |
| `shots/out/` | renders and `.blend` files (frames gitignored: rebuildable) |
| `out/final_v4/` | the cut: 60 s master, per-shot segments, QC sheet |

## Run

```bash
cd research/viral_og_v21/film3d_blender
export LD_LIBRARY_PATH=$PWD/../../tools/blender_local/x11_shim

# stills (three angles, 640x360)
python3 shots/bear_shot3.py --stills --samples 32

# one test frame of the animation
python3 shots/bear_walk.py --step 240 --frames 73 73 --samples 28

# the whole shot, every 3rd frame, 480x270  (~30 s/frame here)
python3 shots/bear_walk.py --step 3 --samples 20 --frames 1 240 --res 480 270
python3 shots/encode_shot.py out/bear_walk_10s.mp4 --pattern walk_preview_ --fps 8
```

Two pieces come out of `bear_walk.py`:

* `--face` walk (default timeline, 240 frames = 10 s): the animal stands, swings its
  head to the lens, takes two heavy steps, stops. Used for S3, S4, S6.
* `--face-beat --face` (144 frames = 6 s): the head lifts into the lens, breath, fire
  flicker; a separate close piece for the face beat. Extra light `LIGHT_eye` (area,
  110 W, just off the lens) because the fire is *behind* the animal there — without it
  the eyes and muzzle fall into shadow.
* `--tag NAME` sets the frame prefix, `--res W H` overrides output size.

`--step 3` on a 24 fps scene means each stored frame is 3/24 s, so the sequence plays
back at 8 fps to run in real time. `encode_shot.py` takes the playback rate.

## The animal (measured, not estimated)

* built from ellipsoids and tapered capsules -> joined -> voxel remesh (`0.032`) ->
  smooth (1.15, 14 iters) -> decimate `0.35` -> subsurf 1
* nose-to-tail ≈ 2.9 m, shoulder ≈ 1.5 m, 13.9k faces after decimation
* head carried **low and forward, under the shoulder hump**. That hump-over-head
  silhouette is the read; a head level with the hump turns the animal into one lump.
* face is four marks only: two eyeballs + irises, a wet nose pad, a bezier mouth line

## The face: placed by raycast, not by coordinates

The eyes/nose/mouth are separate objects that must sit **on the finished skin**. The
body is remeshed, relaxed, decimated and then subdivided, which moves the surface by
1-2 cm — so hand-written coordinates from the pre-remesh sculpt bury the eyes *inside*
the head. That is what happened first: the eyes rendered nowhere, only the nose pad
poked out, and the animal read as a noseless lump.

What works: cast a ray at the evaluated body from outside (`Object.ray_cast` on the
evaluated object) along each mark's direction, and sit the mark a millimetre proud of
the hit point:

| mark | ray from | direction |
|---|---|---|
| eye (±) | `(0, 1.32, 1.14) + d * 0.9` | `d = normalize((±0.62, 0.70, 0.30))` |
| nose pad | `(0, 2.6, 1.045)` | `(0, -1, 0)` |
| mouth curve | 5 samples across x at y=2.6 | `(0, -1, 0)` |

Second bug, same area: the rewrite dropped the tail of `build_bear` that links,
parents and records the parts (`bear["face_parts"]`). Without parenting, the eyes stay
where they were modelled while the head turns — in the face shot they floated next to
the animal. Both are fixed; `--face` now yields
`FACE_eyeball_±1, FACE_iris_±1, FACE_nose_pad, FACE_mouth`, all children of `BEAR_body`.

Mesh density was raised to keep the sculpt through the remesh: voxel `0.026`, smooth
`1.0 × 8`, decimate `0.30` (was `0.032 / 1.15 × 14 / 0.35`), and the muzzle/jaw were
lengthened so the head has a profile.

## Coat: two dead ends, recorded so they are not repeated

1. **Particle hair.** `ParticleSettings.hair_length` is not in object space here; the
   strands came out metres long and filled the frame. Also `child_nbr` ->
   `child_percent` in 4.2 and `ParticleSystem.particle_size` does not exist.
2. **Fur shell.** A duplicated body, solidified 10 mm and displaced by a Voronoi
   texture, is not bound to the pose. It lagged the body and read as a *second
   silhouette* — a woolly ghost standing next to the bear. It was also parented late,
   which made it worse in the animated shots.

What ships: **shading only** on the body mesh — a rough dark coat material with a
fine noise bump (scale 48, strength 0.34, detail 8). No second surface, so no ghost,
and every visible pixel belongs to the animal.

## Light / camera that were arrived at by test frames

| | value |
|---|---|
| camera | loc `(3.35, 4.75, 1.26)`, target `(0, 0.42, 1.05)`, 44 mm, f/3.5 |
| push-in | ends at `(3.05, 4.30, 1.22)`, target `(0, -0.30, 1.05)` — stops before the body crops |
| fire | point 900 W, `(1.0, 0.42, 0.13)`, 0.22 m radius, energy animated on the light datablock |
| torch key | area 260 W, `(1.0, 0.62, 0.34)`, 0.8 m, at `(3.4, -2.6, 2.4)` |
| cave-mouth fill | area 200 W cold `(0.42, 0.58, 0.95)`, 4 m |
| rim | area 95 W cold, 2.6 m, from behind-left (stronger values paint a disc on the wall) |
| world | volume density 0.008, anisotropy 0.45 |
| view transform | AgX, Medium High Contrast |

The nose pad and iris were mirror-smooth at first and were the only blown-out pixel in
frame; they are satin now (roughness 0.34 / 0.22).

## Cost on this box (2 CPU cores, denoised)

| res | samples | per frame |
|---|---|---|
| 320×180 | 16 | ~1 s |
| 400×225 | 20-28 | 14-28 s |
| 480×270 | 20 | ~30 s |
| 640×360 | 28-48 | 55-70 s |

A 10 s shot = 240 frames: ~1 h at 480×270 every 3rd frame, ~2.5 h at 400×225 every
frame, ~4 h at 640×360 full rate. 1080p stays out of reach on this hardware.

## What is in the v4 master (measured)

`out/final_v4/EP01_BEAR_1min_3D_v4_640x360_MASTER.mp4` — 60.00 s, 640×360, 24 fps,
H.264 High + AAC 192k stereo, ~9.7 MB.

| shot | source | notes |
|---|---|---|
| S1, S2 | v3 segment, stream-copied | skull on the rock, pull back |
| S3 | Blender walk, full take | caption `PLACED.` |
| S4 | Blender walk, in 0.8 s, punch-in 1.45x | caption `ONE DOOR` |
| S5 | v3 segment | `600 KG - NOT THE BIGGEST` |
| S6 | Blender walk, in 1.8 s | the walk, no caption |
| S7 | v3 segment | `NOT A BEAR'S ANY MORE` |

The three animal shots were raymarched blobs in v3 and are real geometry here. S4 is a
punched-in later part of the same take rather than a fourth render: the ten seconds
used twice in a row would read as a repeated shot.

The Blender renders are clean plates; the two captions are burnt at cut time with
ffmpeg `drawtext`, at the same position/size/colour the v3 renderer used (centred,
`y = 0.82 * h`, 29 pt, `#EBE9E5`, 1.2 px dark outline). No other overlay is added:
no heading, logo, watermark or credit.

## Cut integration

`make_cut_blender.py` rebuilds the 60 s master from the seven v3 segments, replacing
S3 (the animal appears), S4 (it comes up) and S6 (the walk) with this render, and
muxing the untouched `out/mix60.wav` (VO + score + footstep cues, frame-locked).
The Blender render is a clean plate — no type — so the two captions that sit on those
shots (`PLACED.`, `ONE DOOR`) are drawn at cut time with ffmpeg `drawtext`, in the same
position, size and colour as the v3 renderer used. That keeps the "captions only, no
other overlays" rule: nothing else is burnt in.

`--dry-run` prints the plan without touching anything.
