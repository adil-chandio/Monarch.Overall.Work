# V13 — Complete enhanced English POV film

Owner-authorized extension of the enjoyed V12 POV opening to the **entire original 7:18.7667 English master**, not another minute experiment. V9, V10, V11 and V12 are retained unchanged.

## Locked master

- 1920 × 1080, 30 fps, 13,163 native frames; eight chapters.
- Original 1,048-word approved English script and all eight voice-02 FLACs; no new narration, hidden speed changes, omissions or translated replacement.
- Full original subtitles supplied separately as `English.srt`.
- The opening continues to frame 1925 (1:04.1667), preserving the sentence beginning at 1:01.143 rather than interrupting it at the old experiment boundary.
- Full narration-beat intersections are recorded in `coverage.json`; this proves scheduled coverage, not creative quality or biological validation.

## Full-film spatial direction

The opening retains field approach and sample transfer, molecular-detail inserts, eroded bank, reference handling and living-world observation. `feature.mjs` stages all subsequent source mechanisms from human-height first-person or explicitly conceptual scientific-detail cameras, rather than the earlier full film's orbiting display camera. It includes river-bank travel following transported material, exposed sediment, damage/mineral detail, laboratory extraction, reference matching, controls, branch/support comparison, community and evidence proxies, animal encounter, reconstruction limits, archive gaps, integration, present coastline, canopy and closing.

- Articulated black-suit investigator sleeves with fixed-length joint chains, gloved sample/notebook handling and reachable camera-relative props.
- Human-scale laboratory context around explanatory apparatus; simulated volumes and reference blocks are illustrative, not real study reads/protocols.
- Independent original production animal meshes and native gait/deformation, rodent detail, species-focused observation, goose and leaf movement.
- Atmosphere/environment lighting, AO/antialiasing, deterministic absolute-frame updates, limited world cache and concise projected labels; no large persistent upper caption panels.
- Short eight-frame transitions between later spaces; scientific-detail views deliberately leave literal human-eye scale. DNA-shaped symbols are enlarged diagrams, not DNA visible to a naked eye.
- Earlier production meshes, animation systems and material maps are reused **as assets**, never earlier rendered movie frames. Existing material albedo includes AI-generated textures; this is not scene-image animation.

## Sound and attribution

Unchanged original voice timing, two licensed non-repeating Scott Buckley score excerpts, narration ducking, crossfade and restrained synthesized material-specific foley. See `CREDITS.md`, generated `MUSIC-CREDITS.md`, `MUSIC-LICENSE.json` and generated `SOUND-QC.json`. Foley is synthetic, not field recordings or certified binaural ASMR.

## Reproducible workflow

Full rebuild workflow: `.github/workflows/extinct-v13-full-pov.yml`. The delivered correction uses `.github/workflows/extinct-v13-pov-correction.yml`: it retains the initial run's freshly generated V13 shards and unchanged full soundtrack, and replaces all six shard ranges touching coast/closing or their transitions. A large-cover visibility selector initially also hid small hand-cuff groups; the selector now tests torus radius >0.9m, and native guards explicitly require visible palms. `NATIVE-RENDER-PROVENANCE.json` records both runs/commits and exact corrected parts. No V9/V10/V11/V12 movie footage is used.

1. Source/hash/subtitle/coverage checks and analytic motion/kinematics tests.
2. Full soundtrack construction; native samples from every stage, critical opening contact and opening-to-full boundary. Absolute seek/determinism and locked-camera subject-motion checks.
3. Forty-eight exact contiguous native-frame shards, each frame checked for nonblank output, page/shader failures and fixed-length/reachable arms.
4. Gap-free assembly, complete decode, encoded loudness/true-peak measurement, selected actual-encoded frame extraction, SHA-256 and GitHub release. No YouTube upload.

Local commands:

```sh
.venv/bin/python production/extinct-life/film-v13-full-pov/finish.py --voice-only
node production/extinct-life/film-v13-full-pov/render.mjs --stills
.venv/bin/python -m unittest discover -s tests -p 'test_extinct_v13_full.py' -v
node production/extinct-life/film-v13-full-pov/render.mjs --serve --port=4193
```

`--voice-only` is only a development preview; the release must use the complete scored mix. Full build uses `finish.py --audio-only` then native shards and `finish.py --assemble-only`.

## Honest scope

Stylized explanatory 3D, not photorealism, an exact portrait of ancient life, evidence of literal co-occurrence, expert-validated biology, fluid/rigid-body simulation, actual ancient reads or calibrated laboratory procedure. Technical signal/decode/native sample checks and sampled visual inspection are **not** an uninterrupted human full-film audiovisual review, reference-quality equivalence, measurable “3× improvement,” zero-flaw assurance or guaranteed retention. Final owner creative review remains separate from successful technical delivery.
