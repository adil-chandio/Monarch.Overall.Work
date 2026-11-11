# Island life — walking to vegetation, unfinished 3D scene

An 18-second illustrative scene for the island chapter: the rigged mammoth walks, comes to a kinematic stop, and reaches toward a small grass clump before withdrawing. It depicts no observed individual, known behaviour or exact Wrangel location. The mountain, vegetation, stones and snow are invented. The mesh and rig depend on the third-party SDPM-attributed model; see `../mammoth-rig/README.md` for rights/source identity and anatomical uncertainty. The ground uses the existing generated tundra texture on 3D geometry; see `../living-world/README.md`.

The walking cycle, deceleration, trunk movements and plant bending are hand-authored. The plant is not pulled or eaten, and none of the interactions are force simulation. This is not an approved final shot: foot/skinned-mesh motion, body weight, ground contact, trunk/plant contact, scene lighting, realistic habitat and edit timing need continuous visual and scientific review. The static flat strip under the animal does not establish slope handling.

```
node production/extinct-life/longform-mammoth/cinematic-rebuild/island-approach/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/island-approach/render-preview.mjs 540
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py island-approach
```

The inspector checks deterministic seeks, deformed sole sample heights at ten instants and nearest sampled trunk/grass vertices during selected moments. It does **not** establish continuous physical contact, force, natural behaviour or anatomy. Output and workprint are ignored under `.cache/`; music/voice have not been continuously reviewed, and no new SFX is mixed into the sequence.
