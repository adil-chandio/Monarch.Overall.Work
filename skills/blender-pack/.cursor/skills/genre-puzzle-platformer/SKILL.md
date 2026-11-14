---
name: genre-puzzle-platformer
description: Art direction for puzzle and platformer games in Blender with readable interactables, jump volumes, and clear hazard language.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: puzzle, platformer, jump puzzle, puzzle game art, platforming
  related-skills: environment-artist, prop-artist, materials, camera-cinematography
---

# Genre Puzzle Platformer

Readable platforms, honest physics, and a mechanic the geometry teaches before the text does.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- whether a jump is possible from the silhouette alone
- mechanic affordance in the prop's form
- the difference between decoration and standable ground

## Direction

- **Honest physics.** Jump arc, coyote time and platform size must match what the eye predicts. If the arc looks like 3.5 m and the code does 3.0 m, every jump feels unfair.
- **Decor is not ground.** Anything standable gets a flat top and a distinct edge treatment. Anything decorative must never present a flat top at platform height.
- **Teach with geometry.** Introduce a mechanic in a room where failure costs nothing, then in a room where it costs a life. Text is the third teaching tool, not the first.
- **Readable gaps.** Gap width encodes difficulty: under 1 jump-width is casual, 1.2x is the challenge, 1.5x is a set piece.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| run jump | 3.0 m gap, 1.6 m rise |
| platform min | 1.2 m wide |
| coyote time | 0.1 s, buffered 0.12 s |
| edge treatment | >= 8 cm lip |
| texel density | 256 px/m |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- A jump arc that looks 3.5 m and measures 3.0 m; every gap feels unfair.
- Decorative geometry presenting a flat standable top.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Measured arc matches the visual arc within 10 cm.
- [ ] No decorative geometry presents a standable top.
- [ ] First encounter of any mechanic is failure-free.
- [ ] Gap widths map to the difficulty scale.

## Pipeline

Pin the API surface first - read
[`../../shared/references/blender-version-contract.md`](../../shared/references/blender-version-contract.md).

Follow the shared asset pipeline before and after this skill:
[`../../shared/references/asset-pipeline.md`](../../shared/references/asset-pipeline.md).

Validate against [`../../shared/references/validation-checklist.md`](../../shared/references/validation-checklist.md)
and [`../../shared/references/visual-match-checklist.md`](../../shared/references/visual-match-checklist.md).

Drive Blender through MCP per [`../../shared/references/mcp-integration.md`](../../shared/references/mcp-integration.md);
do not narrate UI clicks.

## Related


