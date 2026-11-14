# EP01 bear — v4 (Blender animal) — review note

**Status: rendered, cut, uploaded privately. Not published, not reviewed by a human yet.**
This is the private-review copy only. Nothing here has gone to YouTube or anywhere public.

## The one file to watch

`out/final_v4/EP01_BEAR_1min_3D_v4_640x360_MASTER.mp4`

* 60.00 s, 640×360, 24 fps, H.264 + AAC 192k stereo, 9.7 MB
* Drive (private): `1fdkg1O2xuWVE5S8Im3ZKnoasSlFM1TbD`
* QC contact sheet (24 frames, every 2.5 s): `out/final_v4/QC_v4_contactsheet.png`

Raw shot, no captions, for checking the animation on its own:

* `shots/out/bear_walk_10s.mp4` — 10 s, 480×270, plays at 8 fps (every 3rd frame of a
  24 fps scene). Drive: `19Hnx2_0sWnQR9Z0uRI3bx2viZQ1Jasrq`
* `shots/out/bear_face_9s.mp4` — 9 s face beat, same spec.

## What changed from v3

v3 was the 60 s cut with the animal painted by a raymarcher — a warm blob with a
silhouette but no surface, no face and no real motion. In v4, the three shots that are
the animal are real Blender geometry:

| shot | v3 | v4 |
|---|---|---|
| S3 — it appears | raymarched blob | Blender walk, full take, caption `PLACED.` |
| S4 — it comes up | raymarched blob, pushed in | Blender **face beat** (new), caption `ONE DOOR` |
| S6 — the walk | raymarched blob | Blender walk from 1.8 s in |

S1, S2, S5, S7 are the v3 files, stream-copied (no re-encode). The audio is the
untouched v3 mix (`out/mix60.wav`: VO + score + footstep cues), so picture and sound
stay frame-locked to the same 60 s.

Captions are drawn at cut time and are the only thing burnt into the frame — no
heading, logo, watermark, pointer or credit. That is the standing rule and it holds in
this file.

## What the animal actually is

Built in code, headless, no GUI and no GPU: ellipsoids + tapered capsules → joined →
voxel remesh → smooth → decimate → subdivide; ~14k faces; 2.9 m nose to tail, 1.5 m at
the shoulder, head carried low under the shoulder hump (that silhouette is the read).
Face is six objects: two eyeballs, two irises, a wet nose pad, a mouth curve — all
placed by casting rays at the finished skin (hand-written coordinates buried them
inside the head; that bug cost two passes and is written up in `SHOT_LOG.md`).

## Known limits — read before judging the picture

1. **Not fur.** Particle hair blew up (metres-long strands) and a displaced "fur shell"
   rendered as a ghost second silhouette. The coat is shading only: a rough dark
   material with a fine noise bump. At 640×360 it reads as a short, dense coat; at
   1080p it would read as smooth.
2. **480×270 sources, upscaled.** The 60 s master is 640×360 but the three animal
   segments were rendered at 480×270 and lanczos-upscaled, because 640×360 at 48 spp is
   ~4 h for those 27 s on this box and the box has 2 CPU cores. Sharpness is below the
   v3 segments if you look closely.
3. **No lip-sync / no mocap.** The walk is keyframed by hand: two heavy steps, body dip
   on contact, breathing, head turn. Feet do not plant perfectly on every frame.
4. **The skull shots are still the old raymarch.** S1/S2/S5/S7 are unchanged v3.
5. **Nothing has been listened to or watched by a person.** The audio is verified
   numerically only (60.00 s, mean −18.7 dB, peak −2.7 dB, no silent block).

## Rebuild / re-render

```bash
cd research/viral_og_v21/film3d_blender
export LD_LIBRARY_PATH=$PWD/../../tools/blender_local/x11_shim

python3 make_cut_blender.py --dry-run     # print the shot plan
python3 make_cut_blender.py               # rebuild the v4 master from what is on disk

# re-render the two pieces (slow: ~30 s/frame, 80 + 72 frames on 2 cores)
python3 shots/bear_walk.py --face --step 3 --samples 18 --frames 1 240 --res 480 270 --tag walkface
python3 shots/bear_walk.py --face-beat --face --step 3 --samples 18 --frames 1 216 --res 480 270 --tag facebeat
python3 shots/encode_shot.py shots/out/bear_walk_10s.mp4 --pattern walk_walkface_ --fps 8
python3 shots/encode_shot.py shots/out/bear_face_9s.mp4  --pattern walk_facebeat_ --fps 8
```

Full detail, measurements, costs and the dead ends: `SHOT_LOG.md`.
