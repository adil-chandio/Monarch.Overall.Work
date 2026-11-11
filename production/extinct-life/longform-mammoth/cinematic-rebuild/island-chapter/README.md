# Island chapter — 60-second illustrative sequence, unfinished

Seven shots in one invented Arctic world, built to cover the island chapter's
visual beats with a single continuous score of narration:

| time | shot | what happens |
| --- | --- | --- |
| 0–9 s | dawn herd on the ridge | wide landscape, four animals move right, one distant |
| 9–18 s | walking past the lens | closer tracking shot, legs and feet in frame |
| 18–27 s | trunk to the grass | low camera, animal stops; the trunk beat is a mixer hold, not a posed reach |
| 27–36 s | calf behind the adult | two animals cross; one is scaled smaller |
| 36–45 s | crossing the shallow stream | animals wade a shader stream over a pebble bed |
| 45–54 s | snow squall | visibility drops, animals stand into the wind |
| 54–60 s | dusk on the plain | wide again, warm sky, animals small |

This is **not** a reconstruction of Wrangel Island and not a finished chapter. The
terrain, stream, weather, herd size, spacing and every animal position are authored.
All animals share one mesh and one hand-authored in-place walk cycle, so sizes and
repetition are visible; the calf is the same animal scaled down. There is no
collision, ground conforming, fur or water interaction, and no herd behaviour model.
The stream and water are shaders, not fluid simulation.

`WRANGEL · ILLUSTRATIVE RECONSTRUCTION` is burned in for disclosure only; no dates,
places, population numbers or evidence claims appear on screen. The wording still
needs editorial review, and nothing here replaces the narration's caveats.

## Rig behaviour found while reviewing (measured)

The mesh faces **local −X**. `place()` therefore yaws every animal by π before it
can walk along +X. Until that was measured the herd moonwalked away from its own
path — the worst defect in the first full render, and invisible in isolated stills.
The export also ships only `WalkInPlace_Experimental` and `Idle_Experimental`, and
its trunk bones are close to rigid (roughly 6 cm of tip travel for ±0.6 rad). That
is why shot 2 holds a **mixer freeze** instead of posing a trunk reach: the pose is
a hold, not a performance, and should not be described as foraging behaviour.

Review status: sample stills were inspected after each art pass and the wide,
tracking, wading, squall and dusk framings were revised — the squall now carries a
near-lens driven-snow layer and low mist, and the crossing no longer tracks the herd
1:1 (which made two shots read as frozen). The **full 60 seconds has not been continuously
viewed**; foot sliding, the stream crossing's contact, the squall transition and
the dusk grade all need human review. Sound is not included beyond the shared
narration/score draft when the editor builds an insert.

```
node production/extinct-life/longform-mammoth/cinematic-rebuild/island-chapter/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/island-chapter/render-preview.mjs 1800
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py island-chapter
```

`inspect.mjs` checks deterministic seeks, page errors, five animals at the expected
triangle count, that the shot index advances through all seven shots, and that the
squall shot actually raises the storm value. Structural checks only.
