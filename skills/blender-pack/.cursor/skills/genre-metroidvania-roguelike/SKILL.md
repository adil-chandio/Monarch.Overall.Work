---
name: genre-metroidvania-roguelike
description: Art direction for metroidvania, roguelike, and roguelite games in Blender with biome gates, room modules, and run-readable props.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: metroidvania, roguelike, roguelite, room modules, procedural rooms, ability gate
  related-skills: environment-artist, scene-assembly, materials, biome-worlds
---

# Genre Metroidvania Roguelike

Gated traversal, room-as-sentence, and an ability that visibly changes the map.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- the gate before the key
- room identity in one screen
- permanent progression in the environment, not the menu

## Direction

- **See the gate first.** A traversal ability is only satisfying if the player already met the obstacle. Gate before key, always. The gate needs a distinct silhouette that survives being seen from the wrong side.
- **One room, one sentence.** Each room states one idea: a shaft, a fight, a choice. If a room needs two ideas, it is two rooms.
- **Ability legibility.** The thing the new ability does must already exist in the world as an unclimbable wall, an unreachable ledge, a sealed door. Model those in the same kit as the bridge the ability later builds.
- **Roguelike variant.** Procedural rooms need authored sockets, not authored rooms: fixed entry/exit heights, fixed light direction, variable dressing inside a rule set.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| room grid | 2 m, rooms 16-24 m wide |
| gate silhouette | distinct >= 30% outline change |
| jump clearance | 2.2 m base, 3.4 m with ability |
| tileset module | 1 texture set per biome |
| texel density | 256 px/m |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Ability granted before the obstacle was ever seen, so the upgrade feels arbitrary.
- Procedural rooms with variable entry heights, breaking traversal.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Gate is visible and legible before the ability is granted.
- [ ] Each room is describable in one sentence.
- [ ] Procedural sockets keep entry/exit heights fixed.
- [ ] Ability-gated ledge height is consistent across biomes.

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


