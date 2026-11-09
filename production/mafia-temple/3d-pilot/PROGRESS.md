# Blender 3D blockout and motion rig (research, not final)

This is a genuine geometry-and-rig workflow, not image-to-video. It does **not** contain a reference-matched character or a completed 20-second film. No supplied photograph was used to produce these assets. The human remains a generic, untextured MPFB stand-in with the wrong face, hair and beard; the temple is rudimentary. There is no running performance, facial rig, smile, red eyes, full edit or approved final audio. Do not present this as the requested finished film.

## What is built

- `build_temple_blockout.py` builds a low-detail 3D street, gate, temple, pavement and practical lanterns, plus static gate and aerial cameras. These are meshes/lights, not image backgrounds.
- `build_ik_walk_test.py` loads the generic `rig_probe.blend`, adds fitted test shoes, assigns each shoe rigidly to its foot bone and creates two-bone leg IK, animated planted ankle targets and provisional arm rotations. It keys 72 frames at 24 fps; it is a walk test, not a run.
- `audit_ik_walk.py` evaluates the shoe mesh and ankle controls for each studio-frame stance. In the current specific generic test, lowest-point clearance was -0.00014 to +0.00234 m relative to the studio floor, max ankle target error 0.00262 m, and planted control drift 0.0 m between adjacent stance frames. These numbers are not proof of plausible gait or a complete contact patch; inspect clothing, leg anatomy, mesh penetration and animation visually. Results apply to this studio geometry only.
- `combine_motion_blockout.py` combines the scene with the generic walking rig, adjusts the controls for pavement height, and has an opt-in 72-frame 3D render. The geometry and animation require extensive art, motion and likeness work before they could be used.
- `build_20s_blockout.py` adds an entire five-shot 480-frame timeline. The IK knee pole was adjusted after measuring the generic rig's lateral knee displacement, but the movement still lacks convincing running, the head motion tilts instead of properly turning, and the rendered figure does not match the reference. `render_20s_blockout.py` rendered a 480×270, 24 fps, 20-second noisy blockout; a provisional sound bed was muxed locally, without creative listening or footstep-sync review. It is a work-in-progress, not the requested final. Owner-only Drive copies of the blockout MP4 and project were made; neither is publicly released.
- A local, private face-texture projection test using the supplied reference produced visible seams, mismatched hair and unnatural eyes. It was rejected and is not included in the generic 20-second project or uploaded. No reference material was sent to GitHub.

## Dependencies and privacy

As in README.md, the tested source checkouts were MPFB 2.0.18 (`d0a32e57a7f915cb2f2b95410e2117648c7bbb7e`) and MakeHuman assets (`2f4033a364a7e97479e17ed630ccb999395730c6`). The latter checkout identifies its assets as AGPLv3 and has Git LFS pointer textures rather than real textures. Clear rights for any commercial/public release and acquire actual usable materials; don't assume third-party asset terms are uniform. Blender Python 4.2.0 ran on CPU after loading required Linux runtime libraries. The GitHub workflow in this branch transfers **only public Ubuntu runtime packages**, never user media.

These scripts write renders and .blend files to `PILOT_OUTPUT` (default private `/tmp/monarch-3d-probe`), not Git. Do not commit recognizable reference images, models or renders. `.gitignore` is a guard, not a security boundary: already tracked files and force-adds remain possible. The original photo and recognizable derivatives must stay private. Local `/tmp` may be cleared between turns.

## Reproduction order

Install Blender Python/MPFB and required system libraries, set `PYTHONPATH` to the MPFB `src` folder, `MAKEHUMAN_ASSETS` to its `base` asset directory, and `PILOT_OUTPUT` to a private directory. Run `rig_probe.py`, `build_ik_walk_test.py`, `audit_ik_walk.py`, `build_temple_blockout.py`, then `combine_motion_blockout.py`. Set `RENDER_TEST_ANIMATION=1` on the last command to render a 3-second low-resolution animation test. This workflow deliberately does not upload material anywhere.
