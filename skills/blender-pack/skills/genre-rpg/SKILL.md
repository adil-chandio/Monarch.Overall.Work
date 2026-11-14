---
name: genre-rpg
description: Art direction for RPG, JRPG, CRPG, ARPG, and MMORPG worlds in Blender including loot rarity reads and region identity.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: RPG, JRPG, CRPG, ARPG, MMORPG, loot, quest hub, RPG environment
  related-skills: fantasy-worlds, environment-artist, prop-artist, character-artist, materials
---

# Genre Rpg

Hub-readable towns, dungeon loops that teach themselves, and props that carry quest state.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- the difference between a hub and a dungeon in the first two seconds
- interaction affordance at player height
- repeatable modular kits that still feel hand-placed

## Direction

- **Hub vs dungeon.** A hub is open, lit warm, vertical sightline to a landmark. A dungeon is enclosed, lit directional, no sightline past 15 m. The player must know which one they are in before the HUD tells them.
- **The teaching loop.** Every dungeon mechanic appears once safely, once under pressure, once combined. Geometry, not text, does the teaching: a ledge you can see but not reach is a promise.
- **Quest state on props.** Doors, chests and levers need three readable states (locked / openable / spent) at 8 m. State lives in silhouette and emissive, not in an outline shader.
- **Modular kits.** Snap on a 2 m grid with 0.5 m sub-grid for trim. A kit that needs nudging is not a kit.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| grid | 2 m module, 0.5 m trim |
| corridor width | 3 m (combat 4.5 m) |
| door height | 2.4 m hero, 2.1 m filler |
| prop tri budget | 1.5k filler, 12k hero |
| texel density | 256 px/m walls, 512 px/m hero props |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Modules that almost snap, needing 2 cm of nudging on every wall.
- Quest-state props that communicate only through a floating icon.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Blinded test: hub or dungeon, answerable in 2 s.
- [ ] Interaction states readable at 8 m in the darkest lighting variant.
- [ ] Every module snaps without a visible seam on a flat wall.
- [ ] No prop intersects player capsule volume.

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


