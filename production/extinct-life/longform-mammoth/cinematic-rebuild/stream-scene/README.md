# Stream and bedrock inference — unfinished 3D scene

A 16-second illustrative landscape supports the 2019 researchers' inference that changing bedrock weathering may have affected drinking water. It is **not** a reconstruction of a specific Wrangel stream or the ancient water quality. The study used sulfur/strontium patterns in remains; it did not directly sample a glass of ancient water. See [Arppe et al.](https://www.helsinki.fi/en/luomus/news/last-mammoths-died-remote-island) and `../full-script-v2/SCRIPT-CROSSWALK.md`.

Terrain, rocks, water, snow cover and camera are invented. Water movement is a shader approximation and does not flow around rocks physically; it has no authentic location, season, flow, chemistry or depth. This looks stylized, has simplistic geometry and requires substantial visual/motion review, not a final cinematic shot. The snow uses third-party candidate `../material-sources/ambientcg-snow001/` with unresolved master-equivalence and rights checks. `../ambience-sources/brook-candidate/` is a separate, unreviewed Washington-state recording derivative, not Arctic sound.

```
node production/extinct-life/longform-mammoth/cinematic-rebuild/stream-scene/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/stream-scene/render-preview.mjs 480
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py stream
```

Inspector checks deterministic sampled frames, scene flags and page errors only; not fluid behaviour, science accuracy or artistic quality. Renderer and workprint go into ignored `.cache/`; the insert includes provisional voice, score and candidate brook audio, with no continuous listening or final mix.
