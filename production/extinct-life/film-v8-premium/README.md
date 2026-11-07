# V8 premium opening — fresh 61-second development candidate

Scope: the first 61.000 seconds of the approved English master. The final complete included sentence ends at approximately 60.743 s; no speed change or mid-word trim is used. This is not a full-film replacement or a claim of creative acceptance.

## What is actually different from V7

- Native Blender 4.2 Cycles CPU renderer, authored here rather than compositing generated scene plates.
- Unified, voxel-remeshed organic animal silhouette (torso, neck, head, trunk and limbs), spatially blended soft deformation, one deliberate forefoot placement, breathing, ear and tail motion. No exposed separate ball-joint limb assemblies.
- Short surface-following coat, tapered tusks, fan-shaped ears, eye sockets/lids, secondary material variation and controlled folds. Still an illustrative anatomical stand-in, not expert-certified anatomy or exact ancient appearance.
- Fully dimensional willow/grass/rocks, irregular ground, cold shore/ridges, changing water surface, sediment strata, plant-remnant view, separate incomplete-fragment evidence views and supported laboratory receiver/rails.
- Seven action/meaning-driven stages; no fixed three-second cut timer. The wetland return changes set dressing, pose/camera/action and introduces leaf-to-water transfer. It does not reuse earlier rendered clips.
- Consistent contextual labels and faithful approved narration captions. Master word alignment remains machine-estimated, not human-verified.
- Unchanged approved voice assets; a licensed non-looped Hiraeth excerpt; new softly shaped synthetic event foley.

## Reproduce

Python 3.11; `bpy==4.2.0`, `numpy==1.26.4`, `pillow==11.3.0`, `imageio-ffmpeg==0.6.0`. On Linux install libGL/Xrender/Xi/Xfixes/Xxf86vm/SM/ICE/xkbcommon runtime dependencies. No GUI is needed. The sandbox lacks several of those system libraries, so native rendering is performed on the GitHub workflow's Ubuntu runner.

```sh
.venv/bin/python production/extinct-life/film-v8-premium/scene.py --from=0 --to=30
.venv/bin/python production/extinct-life/film-v8-premium/finish.py --shard=0
# Render and encode all sixty-one exact 30-frame shards, then:
.venv/bin/python production/extinct-life/film-v8-premium/finish.py --assemble
.venv/bin/python -m unittest discover -s tests -p test_extinct_v8_premium.py -v
```

Seven native look-development views were inspected during the asset gate; the final render gate rechecks the hero view and independent locked-camera surface motion. The final encoded export also supplies seven decoded inspection views. Full moving-frame jobs are gated until that inspection. Render samples are inspection outputs only, never inputs/plates for the movie. Local media stays in `.cache/extinct-v8`; finished delivery is a GitHub release, not YouTube. User-supplied reference files and screenshots remain private and are not dependencies.

## Scientific / quality boundaries

Scenes are illustrative reconstructions and conceptual models, not study footage, a literal sampling protocol, calibrated molecule motion, actual sequence reads, a complete ecosystem or a claim of co-occurrence. Environmental DNA fragments are not whole genomes; deposit age is not direct molecule dating. Signal metrics and native samples do not certify subjective audio comfort, uninterrupted human watch/listen, physical correctness or owner acceptance. See the actual QC/delivery files only after successful assembly.

CPU production uses bounded one-second render shards and persistent static scene data. Two-octave physical-scale material variation avoids expensive, visually unhelpful high-frequency procedural noise. This changes neither resolution, frame rate, frame coverage nor approved narration speed.
