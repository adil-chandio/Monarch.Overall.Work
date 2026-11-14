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
