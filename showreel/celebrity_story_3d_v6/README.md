# Celebrity morning — third-person 3D film (v6)

A 60-second portrait-format film built entirely from rendered 3D geometry: a
fictional public figure's morning, from a 5:40 phone call through a red-carpet
walkout to a dark apartment at the end of the day.

**Deliverable:** `deliverables/celebrity-story-third-person-3d-v6.mp4`
(60 s, 480×854, 24 fps, H.264 + AAC, ~10 MB, SHA-256 `70d3bd01…bc3257`).

## What is actually in it

Everything visible is geometry rendered in Cycles — no stock footage, no still
plates, no 2D compositing of the scene.

- **Characters** are Rocketbox rigs (MIT, via `memoriesrohit/avatar-studio`) with
  80 bones, 52 ARKit blend shapes and the full Rocketbox mocap action set. Each
  character carries four outfits in the GLB; exactly one set is ever visible.
- **Furniture** is Poly Haven CC0, rescaled to real dimensions (the source scans
  are not 1:1). Textures fall back to procedural bump where the CC0 set has no
  map for a slot.
- **The street** is authored geometry: rust-red cladding with fins and windows,
  recessed lobby, canopy, red carpet with brass edging, rope line, press wall,
  lamp posts, planters, bollards, a parked saloon car and a far block behind it.
- **Contacts are measured, not guessed.** The mug, phone and letter are placed on
  the evaluated palm frame of the posed clip (`motion.grasp_frame`), so they sit
  inside the fingers instead of floating beside them.
- **Camera placement is solved per frame.** Each shot asks for a subject, an
  azimuth and a distance; the solver then rejects angles that are inside
  furniture, that leave the camera without clearance on eight rays, or that fail
  to project the subject inside the frame with margin. That is what removed the
  wall-of-shoulder-blades shots in earlier cuts.
- **Audio** is synthesised from the cue table: a three-section pad score, room
  tone, street wash, shutter clicks and a loudness-normalised mix. There is no
  recorded foley and no licensed music.

## How it is produced

`build_narration.py` trims the recorded takes to speech, fits them with one
global tempo factor and writes `script.json`. Every act boundary and every shot
is derived from those cue times, so picture and voice cannot drift apart.

Rendering is sharded: `.github/workflows/celebrity-3d-v6.yml` renders twelve
five-second clips on separate runners, then one job joins, mixes and records the
finished blob. A local 60 s render at these settings would take many hours on two
cores; the sharded run finishes in about 50 minutes.

```sh
./showreel/celebrity_story_3d_v6/setup.sh            # environment + pinned assets
python showreel/celebrity_story_3d_v6/fetch_audio.py # takes by blob id
python showreel/celebrity_story_3d_v6/build_narration.py
python showreel/celebrity_story_3d_v6/render.py --stills 1,14,40,58 --samples 6
python showreel/celebrity_story_3d_v6/mux.py <clips dir> out.mp4
```

## Limitations, stated plainly

- **It is not at the reference's level.** The reference is photoreal live
  action; this is a game-engine-grade avatar in a modelled set. Skin, cloth and
  hair read as CG at any size.
- **No sit or floor pose exists** in the mocap set, so scenes that need one are
  staged standing. The closing line was rewritten to match the blocking rather
  than pretending otherwise.
- **Faces are stylised.** Expressions are blend-shape values driven by hand;
  there is no lip sync and no facial animation to the voice.
- **Motion is clip-based**, blended by hand, not regenerated. Walks are baked-root
  so feet do not skate, but there is no true foot contact solving on stairs or
  uneven ground.
- **480×854 at 2 samples per pixel** with denoising, not a delivery master.
  A 1080×1920, higher-sample render is possible but costs roughly twenty times
  the compute.
- **The narration voice is synthetic** (`voice-04` from this session's audition),
  and the score is oscillator-based rather than composed music.

## Assets and licences

`showreel/celebrity_lookdev/assets.json` and `extra_assets.json` pin every
external GLB by Git blob and are fetched, never committed. Characters:
Microsoft Rocketbox via `memoriesrohit/avatar-studio`, MIT — the full notice is
in `showreel/celebrity_lookdev/ROCKETBOX-MIT.txt`. Furniture: Poly Haven CC0 as
documented by `Sanikaa205/INTERIO/public/assets/furniture/LICENSES.md`. The
character is a generic avatar and is not a likeness of any real person; the film
is marked FICTIONAL on screen.
