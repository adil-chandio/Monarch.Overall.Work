# Excavation — illustrative motion study, not finished film

A 14-second Three.js animation of a brush clearing soil to reveal an unidentified skeletal-reference component. It is **not** a reconstruction of any documented excavation or Wrangel specimen: soil, position, hand, lighting and action are invented. Deforming terrain, bristles, particles and grip are kinematic visual approximations, not physical simulation or a validated field protocol. The fragment is cropped by the soil rather than physically excavated. The motion remains stylized and needs continuous visual/artistic review, improved contact and a science/rights review before use; it is not approved footage.

`assets/reference-fragment.glb` (SHA-256 `90978e81ef3e565d03c9d61da8412415f68446276c8478b50786d6588ada3794`) is derived from the third-party OBJ in `../skeleton-reference/`, whose master identity and rights remain unverified. `extract_fragment.py` regenerates it with Python, numpy and trimesh 5.2.0: weld duplicate seam vertices, select the smallest of three connected components, then center it. The component is not identified anatomically. See the skeleton README for the weak corroboration and caveats. The glove uses the existing unverified J-Toastie-attributed candidate described in `../sample-workflow/README.md`; the soil maps and their source uncertainties are documented in `../material-sources/ambientcg-ground048/README.md`.

From repository root with dependencies installed:

```
node production/extinct-life/longform-mammoth/cinematic-rebuild/excavation/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/excavation/render-preview.mjs 420
```

Inspector evaluates eight sampled timestamps and saves stills under ignored `.cache/mammoth-excavation/`; it checks page errors, asset loading, progress and lift, **not** anatomical/physical correctness or continuous motion. Renderer writes 420 frames at 30 fps, a silent, provisional 1280×720 review file and a hash report into that ignored cache. No final soundtrack or published footage is implied. The separate broom recording in `../foley-sources/broom-candidate/` is not yet auditioned or synchronized.
