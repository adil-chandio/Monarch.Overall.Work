# Native 3D living-world construction — incomplete

A 30-second experimental arctic environment with three clones of the modified SDPM mammoth model, a kinematic walk, approximate graphic footmarks, snow geometry, vegetation, shadow-mapped mammoths, distant procedural terrain and two crossfades. A previously generated AI image (`../assets/tundra.jpg`) is used only as a UV texture on the 3D ground, not as a slide or background plate. **This is not a finished documentary, not a historically exact Wrangel landscape, and not an approved final shot.** The simple terrain, sparse grass, duplicate animal models, uniform pace, low-resolution shadow mapping and graphic footmarks still need significant art/animation work. Interactions, fur motion, terrain collisions and physical snow compression are not simulated. The opening is not yet aligned to the complete narration or the approved storyboard's visual beats. No sound is attached.

The asset, modification details, limitations, source and attribution/rights caveats are recorded in `../mammoth-rig/README.md`. Review those before distribution.

`inspect.mjs` captures sample frames into the ignored `.cache/living-world-review`. It checks deterministic seeks, 3D clip timing, browser errors, and sampled **deformed sole vertices** while the lead animal is planted on a flat plane. The latter checks approximate height and fore-aft stability for a small set of frames; it is not full motion/anatomy/terrain/quality certification. From repository root:

```
node production/extinct-life/longform-mammoth/cinematic-rebuild/living-world/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/living-world/render-preview.mjs 240
```

The second command renders the first eight seconds as a **silent local motion-review file** in ignored cache, not a deliverable. Both require Three.js, Playwright and `@sparticuz/chromium`; rendering also needs the repository's Python imageio-ffmpeg. Output is limited by the available software renderer and has not had continuous human viewing.
