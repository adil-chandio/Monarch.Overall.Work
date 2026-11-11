# Coat section — five illustrative shots for 250–284 s

This is the "satin coat" passage: the FOXQ1 loss-of-function result, the caveat that the coat was **predicted and never observed**, and the return to a moving animal. The narration for this stretch asks for a sample comparison and a hair strand; what is built here is deliberately narrower — **the animal itself**, plus one texture close-up. A researcher, a sample tray and a comparison bench are *not* in this scene, because every attempt at procedural people and props in this repository has read as a toy. The picture here is honest about being illustrative rather than pretending to be a lab.

Nothing in this folder is a reconstruction of a Wrangel mammoth, a specimen, a micrograph or a photograph of anyone's coat. Terrain, weather, herd size, light and every animal position are authored. The third-party rig is described in `../mammoth-rig/README.md`; its rights are still unresolved.

## Shots

| Shot | Time | What happens | Why it is here |
|---|---|---|---|
| 0 | 0.0–9.0 | Macro pass over a wool texture, dissolving into the animal at 8.0–9.4 s | The passage's actual subject is a **trait**, not a specimen. The on-screen line changes to `ILLUSTRATIVE COAT TEXTURE · NOT AN OBSERVED ANIMAL` while the macro is up. |
| 1 | 9.0–17.0 | Very close flank, animal walking past a static camera | Mass and coat at the scale the narration is talking about. |
| 2 | 17.0–25.0 | Low camera on the legs; snow breaking under the feet, calf behind | The rig's strongest asset is the walk cycle. Keep the camera where that reads. |
| 3 | 25.0–31.0 | Herd walking into low sun, wind in the grass | Room for the "does not prove it lost its wool" line. |
| 4 | 31.0–34.0 | Small in the landscape, big sky | Exit hold; the next chapter is the environment. |

Total 34 s at 30 fps (1020 frames), 1280×720.

## What the rig can and cannot do (measured)

- **Facing:** the mesh faces local **−X**. Every animal must be yawed by π to travel along +X. Before this was measured, the herd walked backwards along its own path. The fix is in `place()` and is documented there.
- **Clips:** only `WalkInPlace_Experimental` and `Idle_Experimental` exist.
- **Trunk:** hand-authored trunk rotation moves the tip by roughly 6 cm for ±0.6 rad — the bones are effectively rigid in this export. A "trunk reaching for grass" shot was attempted, looked wrong, and was **removed** rather than faked. `island-chapter`'s shot 2 still uses a mixer freeze for its trunk beat and should be re-judged on the same basis.

These are mechanical observations. They do not certify anatomy, behaviour or realism.

## Commands

From the repository root:

```sh
node production/extinct-life/longform-mammoth/cinematic-rebuild/coat-section/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/coat-section/render-preview.mjs 1020
```

`inspect.mjs` checks determinism (same seek twice → identical JPEG), that a storm/macro probe changes state, animal and triangle counts, shot boundaries, all five animals and browser errors. It writes stills to `.cache/mammoth-coat-section/`.

## Limits

- The macro pass is a **texture**, tiled and light-swept. It is not a micrograph, a specimen photograph or evidence about wool density.
- No shot shows a prediction being compared with an observation, because no such observation exists in the sources used here.
- The "satin" idea is not depicted. Showing a smooth-coated animal would assert the unverified outcome the narration explicitly withholds.
- Audio is the shared narration draft offset; there is no original sound design for this section.
- Not approved, not final, and not part of a finished film.
