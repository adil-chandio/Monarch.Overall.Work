# Bear 60 s cut — v3 changes (code + preview)

The v2 master had three faults that were measurable, not cosmetic:

1. **No contact shadows.** `visibility()` only occluded against the cave SDF, so the
   bear never darkened the floor under it and the skull sat on the boulder like a
   sticker. v3 adds `solid_shadow()` in `render3d.py`: the props are marched into the
   set's lighting, so the animal's shadow falls on the rock and the skull's falls on
   the boulder. `shade_surface()` also takes the AO term, so limb joins go dark.
2. **Un-motivated lighting.** The bear was keyed by a fake point light floating in
   mid-air, which also fogged the dust into an orange "sun" and washed the fur to
   flat cream (`exposure 2.30–2.45` on `C=[0.085,0.062,0.045]`). v3 gives the film one
   warm source that exists on screen — **the humans' fire** (`FIRE_POS`, `FIRE_LIGHT`,
   `sdf.Fire`: stone ring + crossed logs, `geo3d.Embers`) — and every warm light is a
   flame or a torch with a position. Lights that exist only to shape the props are
   flagged `in_air=False` so they never add a glow to the air. Exposure is now
   0.8–1.3 instead of 2.3.
3. **The animals were blobs.** Rebuilt `BEAR` (shoulder hump, brow ridge, small low
   ears, blunt muzzle, deeper chest, four separated pillars) and `SKULL_PARTS` (crest,
   two orbits, zygomatic arch, maxilla + canines). Added fur break-up and bone
   staining/suture lines in `render_clip.py`. Also: a second, smaller cranium beside
   the first, because the film is about a bear that hunts humans and the humans' kill
   should be in the frame.

Framing was rebuilt from the measured cage width (`Cave.radius_at`) rather than by
eye: S3/S4/S6 now stand 7–8.6 m back so the 2.9 m animal, its shadow and the wall all
fit; S1/S2/S5 use the 3/4-high angle at 1.2–1.4 m, which is the only angle where this
skull reads. S4's rear-up was replaced by a step-forward + head turn: the rear-up never
held together at 640×360 (raised limbs read as loose lumps).

`sky` is now applied wherever a ray leaves the cave (it used to be gated on "shots with
no subject", so the opening went black as soon as the animal entered the last shot).

## Preview

`out/v3/PREVIEW_v3_contactsheet.png` — 8 frames (S1–S7 + a second S4 sample), 480×270 each.

## Still not good enough (honest)

- Faces do not exist: there is no eye/brow micro-geometry, only a dark material patch.
- Fur is noise displacement + shading, not strands. At 640×360 it reads as coarse fur;
  at 1080p it would read as sand.
- The last shot is the animal crossing the daylight mouth, backlit. It reads as a shape,
  not as a bear — acceptable as a closing beat, not as a hero frame.
- 640×360 at ~10 s/frame on 2 CPU cores: a full 9:19 episode is not practical here.


---

# v3 render — what shipped (measured, 2026-11-14)

`out/v3/EP01_BEAR_1min_3D_v3_640x360_MASTER.mp4`

| check | result |
|---|---|
| duration | 60.00 s (1440 frames @ 24 fps) |
| picture | 640×360, h264 High, yuv420p, 1566 kb/s, 24.000 fps |
| audio | AAC-LC 48 kHz stereo, 205 kb/s, from `out/mix60.wav` (existing VO/score/SFX mix) |
| container | mp4, faststart |
| full decode | `ffmpeg -f null -` exits 0, no errors (1440 frames decoded) |
| audio level | mean −18.7 dB, peak −2.7 dB (no clipping) |
| file size | 13.3 MB |

Frame sampling: 14 stills (3, 7, 12, 15, 21, 26, 30, 34, 40, 45, 50, 53, 56, 59 s) →
`out/v3/QC_v3_contactsheet_14frames.png`. Every shot cut landed on its planned beat, no
black frames, no missing geometry, captions present on the intended shots.

Render cost: 7 shots as separate files, single process, 2.6–7.7 s/frame, ~2 h 10 min
wall clock for 60 s. (Two parallel processes were 12× slower on this 3.9 GB / 2 core
box — do not parallelise by process here.)

## Not done / remaining review items

- **No human watching or listening pass.** I sampled 14 stills and measured the file;
  nobody has watched the 60 s end to end or listened to the mix on speakers.
- No caption/human pronunciation check on the new picture; the audio is the same
  `mix60.wav` as v2, so any timing worry from v2 still applies.
- Faces/aperture detail do not exist; fur is noise+shading, not strands.
- S7 (54–60 s) is a backlit shape in daylight; it is a closing beat, not a hero frame.
- Not uploaded anywhere. Local file only.
