---
name: genre-soulslike
description: Art direction for soulslike games in Blender with monumental melancholy spaces, fog gates, bonfire landmarks, and lethal readability.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: soulslike, souls like, bonfire, fog gate, monumental ruins, difficult action RPG art
  related-skills: dark-gritty-mood, fantasy-worlds, environment-artist, lighting, set-dressing
---

# Genre Soulslike

Readable attack telegraphs through silhouette, arena framing, and weighty architecture.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- telegraph wind-up length and its silhouette break
- arena size relative to the camera's ability to hold the boss
- environmental storytelling that never blocks a dodge lane

## Direction

- **Telegraph geometry.** Every attack gets a distinct pre-move silhouette: raised limb, turned torso, or planted foot. If two attacks share a wind-up silhouette, the fight is unfair no matter how it reads in a design doc.
- **Arena.** The camera must hold the boss plus 6 m of dodge space. Enclosed arenas clamp this; a pillar that eats the camera is worse than no pillar.
- **Dodge lanes.** Keep a 4 m clear ring inside the arena boundary. Set dressing stops at the ring, not at the wall.
- **Weight.** Soulslike reads heavy: thick bases, low centres of gravity, architecture with visible mass. Thin floating geometry breaks the contract.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| arena radius | 14-22 m |
| dodge lane | 4 m clear ring |
| boss height | 3.5-8 m |
| telegraph | >= 0.4 s, silhouette break >= 20% |
| texel density | 1024 px/m hero boss |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Two attacks sharing a wind-up silhouette; the fight is unreadable regardless of hitbox fairness.
- Arena pillars that eat the camera during a dodge.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Two attacks never share a wind-up silhouette.
- [ ] Camera test: boss never exits frame during a dodge.
- [ ] Dodge ring is clear of set dressing.
- [ ] Greyscale test: boss reads against the arena floor.

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


