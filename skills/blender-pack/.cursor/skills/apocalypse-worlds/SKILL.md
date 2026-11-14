---
name: apocalypse-worlds
description: Apocalyptic and dystopian world art direction for Blender including post-apocalyptic, zombie, alien invasion, post-human, dystopian, and utopian contrast sets.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: post-apocalyptic, post-apoc, zombie apocalypse, alien invasion, dystopian, utopian, post-human, wasteland
  related-skills: environment-artist, prop-artist, materials, set-dressing, vehicle-artist
---

# Apocalypse Worlds

Post-collapse environments where the story is in the failure mode, not the rubble.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- what ended this place, visible in the geometry
- reclamation stage (days / years / decades)
- salvage logic that explains why things are where they are

## Direction

- **Name the failure.** Flood, fire, war, abandonment, bio-event: each leaves a different signature. Pick one and let every surface agree. Mixed causes read as generic rubble.
- **Reclamation stage.** Days: intact structures, no growth. Years: structural collapse, early growth. Decades: canopy over roofs, roads as drainage. Choose a stage and hold it.
- **Salvage logic.** Things were taken, not scattered. Empty shelves, cut cables, removed doors. Debris that looks dropped reads as a set, not a place.
- **Silhouette of ruin.** Broken buildings need a readable break line: a sheared wall, a collapsed span. Uniform damage is texture, not ruin.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| stage | growth | structure | palette |
| --- | --- | --- | --- |
| days | 0% | intact, ash | grey, hot |
| years | 20-40% | partial collapse | ochre, rust |
| decades | 60-90% | canopy over roof | green, deep |
| centuries | 100% | mounds | moss, stone |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Mixed failure causes (flood plus fire plus war), reading as generic rubble.
- Debris that looks dropped rather than removed.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Failure cause identifiable from geometry alone.
- [ ] Reclamation stage consistent across every surface.
- [ ] Salvage pattern shows removal, not scattering.
- [ ] Break lines read as shear, not as noise.

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


