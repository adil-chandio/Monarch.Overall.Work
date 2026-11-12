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
| Camera | **Locked off**, as in the reference, except S4 which pans at the reference's measured rate |
| Figure | 15-segment forward-kinematic skeleton, capsule limbs, and a head built from face volumes |
| Face | `world.head_solids()`: ~60 ellipsoids/capsules — skull, jaw, brow ridges, nose, lids, lips, moustache, goatee, hair; irises are emissive |
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
| energy below 200 Hz | 58-69 % | **~75 %** |
| camera | locked (S4 pans 4.75 px/frame) | locked (S4 pans 4.9°/s) |

`qc/vfx3d/verify.py` enforces every one of those numbers, plus 1280×720,
24 fps, exact 20.000 s, an AAC stream, no duplicated frames and no second of
film below luma 8. It prints VERIFIED or fails.

## What it is not

These are limits, not modesty:

* **Not photoreal, and not close to it.** It reads as a stylised,
  high-contrast 3D set: flat-shaded boxes, hard silhouettes, procedural fabric
  instead of cloth. It is closer to a stylised cinematics test than to a film
  plate.
* **Not a likeness.** The figure is a generic low-poly stand-in with a
  procedural walk cycle. It is not the person in the V8 film and no attempt was
  made to reproduce a face. There is no facial rig, no skin shading, no cloth
  simulation.
* **No global illumination, no reflections of geometry.** Wet stone mirrors the
  *lights*, not the architecture. There is no path tracing: no bounce light, no
  caustics, no soft shadows (the moon shadow is a single hard ray).
* **No motion blur, no depth of field, no anti-aliasing.** Edges are resolved to
  one sample per pixel; at 720p that is visible on the roof and column edges.
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
qc/vfx3d/geom.py     rays, planes, boxes, spheres, capsules, torus, camera
qc/vfx3d/scene.py    materials, the temple, the lights, the figure's skeleton
qc/vfx3d/render.py   frame trace, shading, shadows, wet floor, sky, rain, post
qc/vfx3d/film3d.py   the five shots, the render loop, the encode
qc/vfx3d/verify.py   technical gates run against the finished file
```

## Reproduce

```bash
cd production/mafia-temple
python qc/vfx3d/film3d.py --out render-3d/monarch-temple-3d.mp4 \
  --width 1280 --height 720 --workers 2 --frames-dir render-3d/frames \
  --audio render-3d/sound_v8.wav --crf 17 --preset slow
python qc/vfx3d/verify.py render-3d/monarch-temple-3d.mp4
```

The soundtrack is the V8 master (`qc/make_sound_v8.py`); the picture is new.

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
