# Island in compressed seasons — unfinished 3D sequence

A 30-second illustrative sequence for the start of the island chapter: a low
continuous camera move over an invented Arctic coast while the same ground
passes from winter snow through a bare thaw and brief summer back into snow.
Three instances of the third-party rigged mammoth (see `../mammoth-rig/README.md`)
walk, stand and graze on the plain. No cut, no labelled location beyond a
disclosure line, and no claim that this is Wrangel's actual terrain, vegetation,
sea level or weather.

## What is real and what is invented

- **Geometry:** a generated terrain mesh with a low ridge behind the plain and a
  separate water plane. Distances, ridge shapes and shoreline are arbitrary.
- **Season change:** one shader-driven snow-cover value, not a simulation. Snow
  retreats and returns as a pattern; it is not accumulation, melt or drift
  physics, and no dates are implied.
- **Animals:** the walk clip is a hand-authored in-place cycle; two animals hold
  a stance phase and one tips slightly as if grazing. Contact with ground is
  approximated by a soft shadow blob, not computed deformation. All animals share
  one mesh, so repetition may be visible; spacing and heading differ.
- **Sound:** none of its own. The editor places this under the existing
  narration/score draft; wind and surf would need a separate reviewed mix.

## Limits and review status

Discrete stills were inspected during development; the full 30 seconds has
**not** been continuously viewed. Foot/pad contact on the changing ground,
scale against the boulders, the plausibility of the season transition at this
speed and the repetition of one animal mesh all need human review. The scene is
not a reconstruction and must keep its on-screen illustrative disclosure if used.

```
node production/extinct-life/longform-mammoth/cinematic-rebuild/island-years/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/island-years/render-preview.mjs 900
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py island-thaw
```

Only an excerpt is placed so far: `island-thaw` cuts 4.0–12.0 s of this render into
140–148 s, where the storyboard asks for compressed seasons. The rest of the 30 s has
no assigned slot yet and is **not** part of the measured coverage.

`inspect.mjs` checks deterministic seeks, browser errors, three animals with the
expected triangle count, a monotonic-ish snow/thaw/winter curve, and that sampled
deformed sole vertices exist. Those are structural checks only. Renders and
workprints land in `.cache/` and are not deliverables.
