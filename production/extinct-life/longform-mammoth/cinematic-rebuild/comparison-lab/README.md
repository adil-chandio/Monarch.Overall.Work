# Two-genome comparison — unfinished picture element

This 20-second native-3D workbench scene is a staged illustration of the 2017 comparison of two genomes. It is **not the actual laboratory, equipment, specimens, sampling procedure, or field site**. A hand-held light moves from a prop labelled “Siberian mainland” toward a prop labelled “Wrangel Island”; both are generic derived objects, not models of the actual samples. Labels are a narrative aid, not authentic specimen labels. Nothing here implies identical bones or proves the 2017 subjects' precise sampled anatomical elements. Narration supplies the approximate ages and clearly limits inference to two individuals. Source for the comparison and qualification: Rogers and Slatkin, [PLOS Genetics (2017)](https://journals.plos.org/plosgenetics/article?id=10.1371/journal.pgen.1006601).

The worktop, light, materials, camera, layout and scene movement are invented. Hand/lamp grip is approximate, and the motion is kinematic, not performance capture or a validated protocol. The stylized set, matching light, bone textures, cropping, prop realism and motion still require creative and continuous review; it is not approved finished footage. Source/rights verification remains necessary before distribution.

The two props are open-ended crops of the third-party skeleton OBJ (not verified against the Smithsonian master), not independent specimen scans. `extract_props.py` spatially crops and selects connected surface pieces, then reorients them; no inference about anatomy or specimen origin is intended. Requires numpy and trimesh 5.2.0; the input hash is pinned. Output SHA-256: `assets/mainland-prop.glb` `90312db46cbd4f9fd5e717e609eb0450baea7f9d361f37cfa0206b5e889104ef`; `assets/island-prop.glb` `3fe369f7c21b7476ab27ecece21b0b143fe4da57fce09702cbd9878d9eae991a`. See `../skeleton-reference/README.md` for origin and limits. The glove is from the unverified J-Toastie-attributed copy in `../sample-workflow/README.md` (potential CC BY attribution obligations and exact source/licence unresolved).

From the repository root:

```
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/comparison-lab/extract_props.py
node production/extinct-life/longform-mammoth/cinematic-rebuild/comparison-lab/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/comparison-lab/render-preview.mjs 600
```

The inspector checks deterministic frames, basic light travel and explicit uncertainty flags, not contact, anatomy or scientific/artistic approval. The render goes to ignored `.cache/mammoth-comparison-lab/` with source hashes and no soundtrack. A rough sound-to-picture insert can be generated using the edit scripts; it is not a final film.
