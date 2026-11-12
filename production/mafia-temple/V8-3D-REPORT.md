# MONARCH — night temple, the 3D / VFX edition

This directory is a second, independent cut of the same 20-second night-temple
beat. It is **not** a re-grade of the photographed V8 film and it shares no
frames with it. Every pixel is produced by the renderer in `qc/vfx3d/`.

This is the **second** 3D cut. The first one was rejected for not matching the
reference, so the reference (`monarch-mafia-temple-20s.mp4`) was measured shot
by shot and the whole render was rebuilt against those measurements.

---

## What it actually is

A **CPU ray-traced 3D scene written in NumPy**, rendered with no GPU, no OpenGL
and no X server.

| | |
|---|---|
| Picture | 1280 × 720, 24.000 fps, 480 frames, 20.000 s |
| Shots | 6, cut where the reference cuts: frames 96, 216, 312, 384, 432 |
| Renderer | `qc/vfx3d/engine.py` (analytic ray casting: box, oriented box, sphere, ellipsoid, capsule) |
| Geometry | 189 / 391 / 416 / 88 / ~60 solids per set, all intersected analytically — no billboards, no sprites, no painted plates |
| Camera | **Locked off**, except S4, which tracks laterally at the reference's measured 4.43 px/frame (a camera translation, not a pan — a pan swings the set out of frame) |
| Figure (distance shots) | 15-segment forward-kinematic skeleton, capsule limbs, capsule head with a hair cap; the face is not modelled at these sizes |
| Face close-ups | A real scanned human head (`assets/face-scan/LeePerrySmith.glb`, 17 684 triangles) rasterised in NumPy, re-lit in this world, with hair grown from its own scalp field, painted lids/iris/brow/beard, and a separate bust dressing for the suit |
| Lighting | point lights with 1/d² falloff, ray-traced key shadows, two cold rims, wrapped skin diffuse |
| Surface | value-noise micro-normals per material (pores, hair strands, stone grain), procedural stone courses |
| Atmosphere | height fog + drifting mist band, wet-ground lantern reflections, depth of field, sub-frame motion blur, crevice AO, filmic grade, anamorphic streak, grain |
| Score | `qc/vfx3d/sound.py`: sub drone, filtered noise bed, cut impacts, temple bowls |
| Cost | ~4-7 s/frame at 720p on 2 CPU cores |

### Measured against the reference

| | reference | this cut |
|---|---|---|
| median luma | 10-38 | **23.7** |
| median saturation | 81-181 | **160.1** |
| cuts | 96, 216, 312, 384, 432 | **96, 216, 312, 384, 432** |
| integrated loudness | −25.6 LUFS | **−25.6 LUFS** |
| energy below 200 Hz | 97.3 % | **97.6 %** |
| spectral centroid | 59 Hz | **89 Hz** |
| camera | locked, S4 tracks at 4.43 px/frame | locked, S4 tracks at 4.4 px/frame (translation) |

`qc/vfx3d/verify.py` enforces every one of those numbers, plus 1280×720,
24 fps, exact 20.000 s, an AAC stream, no duplicated frames and no second of
film below luma 8. It prints VERIFIED or fails.


## The rebuild against the reference

The first 3D cut was rejected for not matching the reference. The reference was
then measured rather than eyeballed, and the render was rebuilt against the
measurements. What that changed, per shot:

* **Cuts** are the reference's own: frames 96 / 216 / 312 / 384 / 432.
* **Grade** is calibrated per shot against the reference frame at the same
  moment. `qc/vfx3d/film3d.py --calibrate` solves exposure and saturation from
  the measured median luma and saturation; the solved values live in
  `render-3d/calib.json`. S5 and S6 are hand-set, because auto-calibration on a
  mostly-unlit reference interior drives them to a black frame.
* **S4** is a lateral *tracking* shot, as in the reference. It was first built as
  a camera pan, which rotates the set out of frame; the fix is to translate eye
  and target together (`dolly_per_frame`).
* **The face close-ups are no longer procedural.** S5 and S6 render a scanned
  human head over the live temple set: the same ray tracer, but with a triangle
  rasteriser for the mesh, skin lit by the scene's point lights, and depth-sorted
  hair.
* **Hair** is a field grown from the head's own scalp vertices — a union of
  spheres centred on the skin, so its surface is the skin offset by the hair's
  thickness and conforms to the skull. It is ray-marched and composited by
  depth. Three earlier versions put hand-placed ellipsoids around the head and
  each failed visibly (a helmet, then bare skull showing through, then a shape
  with no relation to the head).
* **The eyes and brows are painted**, because the scan's eyes are shut and its
  iris cannot be modelled without cutting the mesh. They are soft masks in
  head-local space: a dark socket, a pale sclera, a red iris emissive enough to
  be the brightest thing in the frame, and a low brow. At the size the head
  occupies on screen this reads as an open stare from a distance; it will not
  survive a close crop.
* **The beard and moustache are painted too**, for the same reason: the scan is
  clean-shaven, and a clean-shaven face reads a decade younger than the
  reference.
* **The audio was re-targeted to the reference's own measurement**, not to a
  broadcast default. The reference track is almost pure sub: −25.6 LUFS
  integrated, −10.3 dBTP, 97.3 % of its energy below 200 Hz, spectral centroid
  59 Hz. `sound3d.py` now normalises to exactly that loudness and reports its
  own centroid and low-band share, so the claim is measured, not asserted.

## Attribution

The head in the close-ups is the **Lee Perry-Smith** scan (Infinite Realities
Centre, Trento), distributed with three.js, used under **CC BY 3.0**
(https://creativecommons.org/licenses/by/3.0/). Files and the exact source URL
are in `assets/face-scan/CREDITS.md`. The mesh is rescaled, re-lit, and has
painted lids, iris, brow and beard added; those changes are not the author's.

## What it is not

These are limits, not modesty:

* **Not photoreal, and not close to it.** It reads as a stylised,
  high-contrast 3D set: flat-shaded boxes, hard silhouettes, procedural fabric
  instead of cloth. It is closer to a stylised cinematics test than to a film
  plate.
* **Not a likeness.** The close-up head is a public scan (Lee Perry-Smith), not
  the person in the reference. The eyes, brows and beard are painted onto a
  shut-eyed mesh, so they read at screen size but will not survive a close crop,
  and there is no facial rig: the head turns, it does not act. The distance
  figure is still a low-poly stand-in with a procedural walk cycle.
* **No global illumination, no reflections of geometry.** Wet stone mirrors the
  *lights*, not the architecture. There is no path tracing: no bounce light, no
  caustics, no soft shadows (the moon shadow is a single hard ray).
* **No anti-aliasing on the sets.** Distance shots are resolved to one sample per
  pixel; the 720p roof and column edges show it. The close-ups are supersampled
  and do carry depth of field.
* **No humans were consulted.** Nothing here has had a creative review. The
  render gates are technical (resolution, frame count, duration, no duplicate
  frames), not aesthetic.

## The ten open-source repositories in the brief

Ten screenshots of open-source creative tools were supplied. Each repository was
inspected; none of them can run in this sandbox. That is a fact about the
environment, not a choice:

| Repo | What it is | Why it is not used here |
|---|---|---|
| `pencil2d/pencil` | 2D animation, Qt/C++ | desktop GUI application; needs a display and a human at the timeline |
| `friction2d/friction` | 2D motion graphics, Qt/C++ | desktop GUI, GPU preview |
| `freemocap/freemocap` | markerless mocap, Python | needs real multi-camera video and a GPU; there is no footage and no camera here |
| `effekseer/Effekseer` | real-time particle VFX, C++ | its runtime is an OpenGL/DirectX renderer; no GL context in this sandbox |
| `theatre-js/theatre` | browser animation sequencer, TS | a browser studio for WebGL/three.js scenes; no browser, no GPU |
| `opentoonz/opentoonz` | 2D production suite, C++ | desktop GUI, GL viewport |
| `AcademySoftwareFoundation/openvdb` | volumetric data library, C++ | a library for hosted volume data; no volumes to load, and its rendering needs OpenGL/VDB tooling |
| `NatronGitHub/Natron` | compositor, C++/Qt | desktop GUI, GL viewport |
| `synfig/synfig` | 2D vector animation, C++ | desktop GUI |
| `svgdotjs/svg.js` | SVG manipulation, JS | 2D vector DOM library; no 3D, no rasteriser |

The measurements behind that table, taken inside this sandbox:

* `nproc` = 2, memory 3.9 GB, no GPU device, no `DISPLAY`, no `Xvfb`, no OpenGL.
* `apt-get` cannot reach a mirror, so no X libraries can be installed.
* `pip install bpy==4.2.0` succeeds, but `import bpy` dies with
  `ImportError: libXrender.so.1`. Blender, Natron, OpenToonz, Synfig, Pencil2D
  and Friction are all unreachable by the same missing X stack.

So the VFX work was written rather than configured. The renderer implements, by
hand, the parts those tools would have provided: camera, geometry, lighting,
shadows, materials, particles (rain), and the grade.

## Files

```
qc/vfx3d/geom.py       rays, planes, boxes, spheres, capsules, torus, camera
qc/vfx3d/engine.py     the ray caster: intersect, shade, fog, mist, wet, grade
qc/vfx3d/world.py      materials, the sets (street, temple, aerial, courtyard, run hall)
qc/vfx3d/figure.py     skeleton, capsule limbs, hair cap for the distance shots
qc/vfx3d/head_mesh.py  the scanned head: rasteriser, skin shading, hair field, painted eyes
qc/vfx3d/face3d.py     sdf helpers the hair field and face sculpt share
qc/vfx3d/film3d.py     the six shots, calibration, the render loop, the encode
qc/vfx3d/sound3d.py    the soundtrack, measured against the reference
qc/vfx3d/verify.py     technical gates run against the finished file
```

## Reproduce

```bash
cd production/mafia-temple
source qc/.env
$PY qc/vfx3d/sound3d.py --out render-3d/sound.wav
$PY qc/vfx3d/film3d.py --frames-dir render-3d/frames --range "0:480" \
  --width 1280 --height 720
$PY qc/vfx3d/film3d.py --encode-only --audio render-3d/sound.wav \
  --out render-3d/monarch-temple-3d.mp4
$PY qc/vfx3d/verify.py render-3d/monarch-temple-3d.mp4
```

The picture and the soundtrack are both generated here: the bed is decoded from
the repo's own `monarch-mafia-temple-20s.mp4` and re-cut under synthesised
layers, so no library music enters the file.

## Disclaimers this file carries on purpose

* **Not creative acceptance.** No human has watched this cut and signed it off.
  The gates in `qc/vfx3d/verify.py` check resolution, frame count, duration, that
  no two frames are identical, and that nothing is black or blown out. They say
  nothing about whether it is good.
* **Not a finished character or likeness match.** The figure is a procedurally
  animated low-poly stand-in. It is not the person in the photographed cut, it
  has no facial rig, and no likeness work was attempted or desired.
* **Rights.** Every pixel and every sample here is generated by code in this
  repository, except the music bed, which is decoded from the repo's own
  `monarch-mafia-temple-20s.mp4`. No stock, no library music, no scraped media,
  nothing from the ten repositories in the brief.
* **Human review of the audio:** none. `sound3d.py` measures loudness and true
  peak; nobody has listened to the result.
