# 3D character feasibility — initial rig probe

**Status: technical probe only, not the approved likeness/motion pilot and not a usable character.** No part of the supplied reference is loaded or transmitted by this probe. The user has requested the full 20-second production; a usable reference-matched character and motion quality are still unproven, so this probe cannot be used as the finished film.

## What was actually tested

- Blender 4.2.0 Python + MPFB 2.0.18 (`d0a32e57a7f915cb2f2b95410e2117648c7bbb7e`) could create a base human and a weighted 52-bone Mixamo-style armature. A generic suit and hair mesh were fitted in a private local test.
- One static, plain studio image at **480×640, Cycles CPU, 8 samples, 2 threads**, took **5.43 seconds** on this sandbox. This is not an estimate for a detailed 1080p production frame, nor for GitHub runners.
- The result is a generic stand-in, **not a reconstruction of the supplied face**. It has incorrect hair, no beard, no eye detail, wrong suit styling and bare feet. The skin is a flat procedural material. Facial rigging, walk, run, head turn, expression, foot contact and temporal stability have not yet been tested. The test therefore fails the character/likeness gate and must not be presented as the pilot or used in the film.
- The MakeHuman assets checkout tested here is `dmaugis/makehuman-py3-assets` at `2f4033a364a7e97479e17ed630ccb999395730c6`, whose repository and individual asset files identify them as AGPLv3. Texture files in that checkout were Git LFS pointers, so they were **not available** during the test. Clear licenses and acquire working assets before production; do not assume assets in other packs have identical terms.

## Reproducing this generic probe

`rig_probe.py` is an experimental source-checkout probe, not a final pipeline. It does not retrieve dependencies or assets. Use a compatible local install of `bpy==4.2.0`, a source checkout of MPFB 2.0.18 on `PYTHONPATH`, and an authorized MakeHuman assets checkout. Set `MAKEHUMAN_ASSETS` to the `base` directory and `PILOT_OUTPUT` to a private scratch directory. On systems running a Blender executable, adapt the extension setup to the installed MPFB extension. This script forcibly exits after saving because the standalone `bpy` wheel segfaulted at Python shutdown in this sandbox. An ordinary Blender executable should use normal shutdown instead.

The local container also required X11/OpenGL runtime shared libraries before the `bpy` wheel would import. Treat those libraries and all other external dependencies as separately licensed. No reference images, derived face assets, renders or third-party assets are stored in this directory.

## Remaining blockers

1. Obtain or build an animatable, rights-cleared head with a demonstrable match to the reference from front, three-quarter and profile views, plus usable eyes, hair and beard. A generic MPFB base does not solve this.
2. Create properly fitted suit and shoes, a facial rig, and licensed movement or recorded mocap; test walk, run, foot contact, head turn and expression on the **same** character.
3. Run and inspect a real moving pilot before final-shot production; do not present a failed pilot as a finished film. Only then benchmark final-scene quality and per-frame costs and design the distributed Actions render.

If an appropriately licensed reference-matched rig is supplied, it could unblock the likeness step; otherwise face reconstruction, sculpting and material development still require feasibility work and potentially specialist tools or an artist. Research code licenses and model/asset licenses must be checked separately.
