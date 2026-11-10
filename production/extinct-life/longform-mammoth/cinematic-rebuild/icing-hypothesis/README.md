# Rain-on-snow hypothesis — experimental native 3D

A time-compressed conceptual 14-second scene shows rain, then a suggested icy surface and stylized frozen foliage. The color change is a shader, not physical ice deposition. It illustrates one environmental hypothesis, not a recorded event, an observed fatal Wrangel winter, or a demonstrated cause of mammoth extinction. The 2019 paper discusses rain-on-snow and ice crust as possibilities: [Arppe et al.](https://doi.org/10.1016/j.quascirev.2019.105884); [University of Helsinki summary](https://www.helsinki.fi/en/luomus/news/last-mammoths-died-remote-island). The hypothetical relationship is also qualified in the narration. Land, vegetation and weather are invented; no exact island habitat or frozen plant anatomy is claimed.

This uses generated 3D terrain, grass blades, ice shells, weather and light, alongside a candidate snow material and 3D grass model documented in `../material-sources/README.md`. Rain and splash phases are analytical and vegetation/icing motion is authored: no fluid, freezing, plant, ecological or animal-access simulation. The sparse scene, exaggerated frozen-foliage color, simple glaze, bright lighting, repeated stones, transitions and interaction still need substantial improvement. Its visuals do not clearly demonstrate grass being inaccessible, and it must not be considered finished or used as proof. No continuous human picture or sound review has occurred. The shot has no animal interaction and must not stand in for such action.

Run from repository root:

```
node production/extinct-life/longform-mammoth/cinematic-rebuild/icing-hypothesis/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/icing-hypothesis/render-preview.mjs 420
```

The inspector tests browser errors, deterministic time seeking, grass count, and the time envelopes of rain and glaze. The silent review renderer hashes its inputs and output in ignored `.cache/mammoth-icing-hypothesis/`; these checks do not verify beauty, realism, physical behavior, science, or editorial timing. The automatic narration transcript suggests approximately 06:10–06:24, not yet listened to or locked. Do not publish this development test as a completed film.

After a current 420-frame render finishes, `.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/icing-hypothesis/mix_preview.py` creates an ignored-cache 14-second comparison against the provisional narration/score around 06:10, adding a quiet excerpt from the rain candidate. The script refuses stale render/input hashes, decodes every frame, and checks a true-peak ceiling. It is not a final mix, not an Arctic field recording, and not evidence of listening or shot approval; the approximate sync and the possible machine-like sound objection require human review.
