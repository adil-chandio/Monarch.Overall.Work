# Why Orcas Fear Humpbacks — 3D film, v3

Sixty seconds, 1280×720, 30 fps, 16 beats. Same timeline and same script as v2.
What changed is everything between the geometry and the eye.

v2 was lit correctly and rendered honestly. The problem was that it had no water.
Every shot took place in a uniform blue medium: the sea had no ceiling, objects did
not sit on anything, distance did not carry mass, and the whole film ended in a
linear grade that clipped the highlights flat. v3 adds the four things that were
missing and rebuilds the fifth.

---

## What v3 actually changed

### 1. Depth is measured in metres now

The renderer wrote NDC depth — a hyperbolic value that spends all its precision in
the first few metres and then flatlines. Everything downstream that wanted to know
"how far away is this pixel" got an answer it could not use.

`Renderer.linear_depth()` recovers true metres:

```
n, f = 0.05, 400.0
m = (2nf) / (f + n − ndc(f − n))
```

Every depth-driven effect is now physical.

### 2. The sea has water in it

v2's fog was a flat lerp, so a whale 4 m away and a whale 30 m away faded by the
same rule and the medium read as tint rather than water. Fog is now exponential
in real distance:

```
fog = (1 − exp(−max(z − 1.5, 0) / 13)) × 0.90      →  (0.052, 0.142, 0.178)
```

Close subjects stay clean, far ones genuinely dissolve, and the falloff is
continuous so a travelling animal fades rather than switching.

### 3. The surface exists

`water_surface()` draws the underside of the sea in every shot that looks up:

- **Snell's window** — the cone of sky above the camera, width
  `window[0] + 0.55·window[1]`, with a bright Gaussian sun core inside it
- **Total internal reflection** outside the window — the mirror of the deep, which
  is dim and cold in reality but present, not black
- **Three ripple trains** at 11 / 23 / 41 Hz summed into a displacement field, so
  the ceiling moves like water and not like a painted lid
- **Crest filaments** — the thin bright lines where a wave turns over

Surface height is 3.5–4.5 % of frame. Higher and it eats the top of the shot as a
black band; that was the first three attempts.

### 4. Objects touch the seabed

`contact_shadow()` projects each body's world position to screen and multiplies an
elliptical Gaussian underneath it, scaled by distance. A shadow is what makes an
animal sit in a place instead of float in front of a background.

Wired into the pod entrance, the humpback card and the carousel.

### 5. The grade is filmic, not a multiplication

v2's grade was `clip(x * gain)`. Every highlight went to 1.0 and stayed there, which
is why the footage read flat and cheap.

`apply_grade()` is now a real pipeline:

| stage | what it does |
| --- | --- |
| shoulder | exponential roll-off above knee 0.76 — 1.0 → 0.917, 2.0 → 0.979 |
| toe | lifts the black point so shadows hold detail |
| filmic S | `(x − 0.42)·contrast + 0.42` |
| smoothstep | 0.30 / 0.70, gives the midtones their shape |
| split tone | shadow `+[0.006, 0.030, 0.046]`, highlight `+[0.045, 0.024, −0.010]` |
| saturation | channel-weighted, protects skin and paper tones |
| vignette | 0.34, `r^2.2` |
| grain | shadow-weighted, `0.010 · clip(1.25 − 1.6·lum, 0.25, 1.25)` |

The teal shadow / warm highlight split is the single biggest reason the frames now
look graded rather than tinted.

### 6. Each shot gets its own light rig

The rig was hard-coded: key from `(-0.30, 0.82, -0.48)` — up and behind. That is
correct for a pod swimming through god rays, and completely wrong for the humpback
species card, whose camera looks at the whale from the front. v2's card shot is a
dark featureless blob under a title.

`Renderer.light_rig()` lets a shot move the key, the gain, the fill and the rim:

```python
r.light_rig(key=(0.55, 0.62, 0.72), key_gain=1.55,
            ambient=(0.085, 0.140, 0.180),
            fill=(0.30, 0.52, 0.66), rim=(0.70, 0.90, 1.00))
```

The card now keys from the camera side and rims from behind: the flank, the throat
pleats and the long pectoral fin all read, and the silhouette is carried by light
instead of by absence.

### 7. The trophic pyramid is geometry now

v2 drew the pyramid with `ImageDraw`: four flat trapezoids, one constant fill each,
a hard-coded 18 px skew. It moved and it labelled, and it was a chart sitting in the
middle of a 3D film.

It is four lit slabs of water now, drawn by the same renderer as the whales, viewed
from above so the stack reads as a stack. Each tier carries a lit lip along its
front edge; without that every slab shades to the same value as the water behind it
and the whole structure dissolves into the medium.

### 8. The humpback has throat pleats

The single feature that identifies a rorqual, and it was absent. Twenty grooves now
run from the chin about a third of the way down the body, each a ribbon of quads
following the surface, tapered at both ends, pushed 20 mm proud so it never
z-fights. They are nearly black on purpose: a groove is a crease, and at cinema
contrast a crease is a dark line.

Also: the animal was `(78, 84, 92)` — a green-grey that read as a submarine. A
humpback's ventral surface is white, so the skin tone is `(150, 152, 148)` and the
grooves carry the contrast.

### 10. Two beats were rendering nothing

The contact sheet caught two shots that had been broken since v1 and that no
earlier check had flagged, because both failed *quietly*:

**The plan view (39.2-42.4 s) was empty water.** Its camera looked straight down
`-y` while the default up vector is `+y`. Those two are anti-parallel, the view
basis is singular, and every one of the six orcas projected to NaN. The frame
contained two sonar arcs and nothing else. Fixed by tilting the axis and passing a
usable up; it is now the best-looking shot in the film — six animals in a radial
guard, seen from above.

**The pec-slap (31.4-35.6 s) was two glowing planks.** The shot drew the library's
standalone `flipper()` primitive, a bone-white plate with no connection to any body,
floating beside an animal that was merely rolling. At the camera the two plates were
wider than the whales. Rebuilt so the flipper is the animal's own pectoral, posed by
the animal's own roll, with spray thrown off it while it lands. That also exposed a
real shading bug: a flat appendage seen from above is a grazing surface, so every
orientation-dependent term fires at once and a *black* fin renders solid white. New
`fin` material: diffuse only.

### 11. God rays respect occlusion

The ray mask fades with depth against the shot's `ray_far`:

```
mask = clip((z − ray_far·0.35) / (ray_far·0.65), 0, 1)
```

Rays stop being a screen-space overlay and start originating behind the subjects.

---

## Audio

The v3 mix adds two layers that v2 did not have, both because the picture now has
information the ear was missing:

- `surface_swell()` — the body of water moving a few metres above the lens: pink
  noise low-passed at 220 Hz, high-passed at 45 Hz, with a slow swell envelope, plus
  a faint 900 Hz–2.6 kHz shimmer where the surface catches light.
- `carousel_rotation()` — the one beat in the film that is spatial. Four overlapping
  band-passed swishes, panned by angle, so the ear hears the pod going round.

45 cues, all from this repo's `sfx/` collection, placed by sample index.

---

## Delivered

| property | value |
| --- | --- |
| file | `Why-Orcas-Fear-Humpbacks-3D-v3-60s-720p.mp4` |
| duration | 60.00 s |
| picture | 1280×720, 30 fps, H.264 High |
| audio | AAC 192 kb/s, 48 kHz stereo |
| loudness | −14.0 LUFS, true peak −1.9 dBTP, LRA 6.1 LU |

Gates: **9/9 PASS**.
