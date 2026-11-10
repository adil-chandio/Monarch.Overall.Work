# Cinematic rebuild: experimental, not a completed film

This folder records the setup for an initial native-30-fps, 1280×720 frame-by-frame technical test for a no-slideshow 3D rebuild. Only stills and approximately four seconds were rendered before the test was stopped: the visual result did not meet the requested standard. No complete 22-second test or new documentary master exists. It reuses and modifies the previous procedural opening scene and its renderer; it is not a finished chapter and does not meet the full film request. `SHOT-PLAN.md` covers the remaining film and the requirements for meaningful completion.

If run to completion, the 22-second test renders to `.cache/longform-mammoth-cinematic-rebuild/`, not over an existing delivered film. `render.mjs` captures individual scene evaluations, rather than interpolating from a 4-fps plate. Test audio, if available, comes from 60 seconds into the replacement full-film mix, not the old rejected opening soundtrack. The existing animal is not rigged, and the scene is a bare floe, not a defensible depiction of Wrangel terrain. This is a technical experiment, not the requested final-quality documentary.

Run from repository root, with Three.js/Playwright/Chromium and imageio-ffmpeg installed:

```sh
node production/extinct-life/longform-mammoth/cinematic-rebuild/render.mjs --stills --frames=0,210,390,540
node production/extinct-life/longform-mammoth/cinematic-rebuild/render.mjs --from=0 --to=660
```

Do not publish the prior or test film to YouTube without explicit authorization.
