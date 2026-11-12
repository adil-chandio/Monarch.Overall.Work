# MONARCH — night temple, the 3D / VFX edition

This directory is a second, independent cut of the same 20-second night-temple
beat. It is **not** a re-grade of the photographed V8 film and it shares no
frames with it. Every pixel is produced by the renderer in `qc/vfx3d/`.

Read this page before watching, because "3D" covers a very wide range and the
honest statement of what this is matters more than the label.

---

## What it actually is

A **CPU ray-traced 3D scene written in NumPy**, rendered in this sandbox with no
GPU, no OpenGL and no X server.

| | |
|---|---|
| Picture | 1280 × 720, 24.000 fps, 480 frames, 20.000 s |
| Renderer | `qc/vfx3d/film3d.py` + `render.py` (analytic ray casting, not SDF marching) |
| Geometry | ~160 solid primitives: boxes, spheres, capsules, a torus. All intersected analytically — no billboards, no sprites, no painted plates |
| Camera | 5 shots, real camera moves in 3D (dolly, crane descent, oblique push) |
| Figure | 14-segment forward-kinematic skeleton rebuilt every frame, capsules emitted from joint positions |
| Lighting | 1 directional moon with **real ray-traced shadows** + 15 point lights (lanterns, shoji spill) with 1/d² falloff |
| Surface | world-space procedural detail: stone courses, wood grain, tile ridges, wet patches |
| Atmosphere | exponential height fog, wet-ground mirror, 3 rain layers, bloom, filmic tone curve, grain |
| Cost | ~12 s/frame at 720p on 2 CPU cores; ~100 minutes for the film |

Everything above is in git and reproducible on any machine with NumPy and
ffmpeg. There is no binary asset, no model download, no stock footage.

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
