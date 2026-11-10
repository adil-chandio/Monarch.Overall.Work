# Mammoth asset and experimental rig — work in progress

This is **not the finished film or a production-approved performance**. It is an attempt to turn a static third-party mammoth model into a usable animated asset. The source has one mesh (29,818 vertices, 56,994 triangles), a colour texture, no armature, and no animations. Its Sketchfab title says “Baby”, but its large tusks and proportions do not reliably establish an age; do not present it as a documented calf or an actual Wrangel specimen. Its anatomical and archaeological accuracy has not been reviewed.

## Source and attribution

- Model as identified by its source project: **“3D High-poly Baby Woolly Mammoth” by SDPM Esare**, https://sketchfab.com/3d-models/3d-high-poly-baby-woolly-mammoth-fce1c86ccedf47a5b9627098be6719d5 ; the creator's listing states **CC BY 4.0**, https://creativecommons.org/licenses/by/4.0/ .
- The `.blend` was obtained from https://github.com/Jmeshesha/Woolly-Mammoth-Visualization/blob/main/Assets/3d%20Models/SkinedModel/3d-high-poly-baby-woolly-mammoth/source/Wooly%20Mammoth.blend (Git blob `30f0bcae1fd33d159f5d311116698075de6408a8`, SHA-256 `816d6088323b836bb5fe66aa88f5e963d3d745053916710a1b9fb1c9550c3f22`). The source project attributes its model to the above listing. The copy's visual similarity and polygon count are consistent, but we have not independently matched it byte-for-byte to a direct Sketchfab download or established the artist's underlying rights. Resolve provenance/rights before public film distribution; do not treat this note as legal clearance.
- The GLB is **modified**: object transform baked, original custom material replaced with a PBR approximation using the embedded base-colour texture, a new armature and spatial weights added, and two experimental animation clips created. Original source `.blend` is kept unchanged. Modified asset SHA-256 `57bd74ba5d01b8e4f3b125d48344fa7c44671982b61350f9a583d845e5ff1b6b`.

## Limitations and required work

The rig uses guessed bone locations, automatic proximity weights and very small kinematic joint rotations. `WalkInPlace_Experimental` is **not** a physically grounded walk: no translation, inverse kinematics, foot lock, terrain collision, transfer of weight, trunk contact, social behaviour or actual fur dynamics are solved. Some foot placements and joints are visibly approximate; the small head/trunk deformation and legs need close, animated review and manual correction. Camera/lighting/display are a crude inspection setup only. A convincing performance also needs anatomy review, grounded animation, environments, storytelling, score/SFX, editorial integration and human review. None of this is proof of final-film quality.

## Reproduction and checks

- `rig_asset.py` is the deterministic construction recipe using Blender 4.2 Python `bpy`; it disables scripts when loading the source file. It requires a functioning graphics library environment for that version of Blender, and exits immediately after export because the local headless wheel crashed in teardown. The separate `validate_glb.py` checks the emitted file after exit.
- `python3 validate_glb.py` checks the GLB structure, embedded texture, eleven joints, two clips and normalized four-influence vertex weights; it cannot check artistic quality or validity of rights.
- From repository root, `node production/extinct-life/longform-mammoth/cinematic-rebuild/mammoth-rig/inspect.mjs` renders six headless inspection frames into the ignored `.cache/mammoth-rig-review`, checks deterministic seek, frame differences and browser errors. Requires the repository's installed Three.js, Playwright, `@sparticuz/chromium` and supporting graphics libraries. These are stills and automated checks, not a continuous animation review or a finished scene.
