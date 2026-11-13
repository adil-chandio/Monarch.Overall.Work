# Why Orcas Fear Humpbacks — 60 s, rendered in 3D

1280x720 · 30 fps · 1800 frames · 24 MB · stereo 48 kHz · −12.7 dBFS

Drive: `1SqM38ZoiyUhya4ELqCmB6Pn3ZQoMBkSL`

## There is no vector art in this cut

Every frame is a rasterised 3D scene. `scripts/lib/tri3d.py` is a software renderer
written against numpy because the sandbox has no GPU and no OpenGL:

| stage | what it does |
|---|---|
| `draw()` | view transform → perspective → z-buffer raster, per-pixel barycentric shading |
| normals | per-vertex averaged face normals, interpolated across the triangle |
| light rig | key from above-left, up-fill from the surface, rim from behind |
| specular | two lobes (sharp 96, wide 11) plus wrapped diffuse: wet hide, not rubber |
| depth | linear NDC depth, so a z-test is a plain `<` |
| DOF | circle of confusion from the real z-buffer, two blur levels |
| fog | aerial perspective keyed to depth, which is what gives the water its volume |
| rays | volumetric shafts, attenuated by depth so they never paint over a near subject |
| grade | S-curve, teal lift, saturation, vignette, grain |

`scripts/lib/creatures3d.py` builds the animals as spines of elliptical
cross-sections, so the flank is a real curved surface the camera can orbit.

## Camera and motion

No shot is locked. Beat 1 dollies and pans; the whale rise is a tilt-up on a real
dolly; plan view is a straight-down crane. Bodies are displaced by a travelling
sine along the spine — amplitude rises toward the fluke — so they undulate instead
of sliding.

## Audio

`scripts/sfx.py` synthesises 43 cues with numpy (sub booms, whooshes, sonar pings,
whale calls, risers, bubble bursts, metal stings) and writes a cue JSON. The mix is
two-pass: ffmpeg to a lossless WAV, gain staging and a tanh limiter in numpy, then
mux. One ffmpeg pass cannot work here — the AAC encoder overshoots the limiter by
about 4 dB, so a file that measures −0.7 dBFS before encoding measures +1.4 after.

## Bugs this cut needed

1. `perspective()` was the OpenGL matrix (camera down −z) against a +z-forward view,
   so every clip.w was negative and every frame was empty.
2. `tube()` wound its triangles inward, so backface culling deleted the animals.
3. Face normals were built in world space and dotted with a view-space direction to
   camera. Mixed spaces → everything vanished or rendered inside out.
4. `clear()` was not called on camera change, so the depth buffer held last beat's
   geometry: orcas rendered as ghosts with their dorsal fins outside them.
5. `_vertex_normals` cached by `id(mesh)`. CPython recycles ids, so a 567-vertex
   whale inherited a 612-vertex table and the render died at frame 157.
6. Flat per-face normals made a 22-ring whale a faceted blob; per-vertex normals
   fixed it.
7. Orca patches needed a depth-bias decal pass and a two-sided material, or the
   white saddle never appeared.
8. Rays were added flat over everything; they are now attenuated by depth.

## Honest scope

This is a CPU renderer at ~1.14 s per 720p frame. It has no subsurface scattering,
no soft shadows, no motion blur, and no rigged skin deformation. It is a real 3D
cut with real geometry and real lighting, and it looks like a competent indie 3D
short — not a studio film. Everything above is reproducible from this repo.
