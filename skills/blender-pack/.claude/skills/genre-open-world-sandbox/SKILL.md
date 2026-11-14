---
name: genre-open-world-sandbox
description: Art direction for open world and sandbox games in Blender with biome landmarks, traversable scale, and discovery props.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: open world, sandbox, open-world, exploration, traversable world, sandbox game
  related-skills: biome-worlds, environment-artist, vegetation-artist, scene-assembly, lod-pipeline
---

# Genre Open World Sandbox

Traversal landmarks, horizon logic, and POIs that earn their density.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- the horizon: what pulls the player from 800 m
- POI density versus traversal speed
- a landmark that survives from any approach

## Direction

- **Horizon first.** Author the skyline before the ground. A 300 m landmark must be visible from 800 m in fog and hold its identity from four approach angles.
- **Density vs speed.** POI spacing ~20-40 s of traversal. Closer and the world feels like a corridor; further and it feels empty.
- **Landmark identity.** One dominant vertical, one horizontal mass, one distinct surface response. A landmark that reads only in colour fails at sunset.
- **Sandbox affordance.** Anything interactive gets a material break against the environment, plus a silhouette hook. Interaction language must be consistent across biomes.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| POI spacing | 20-40 s traversal |
| landmark height | 300 m, visible 800 m |
| LOD cascade | 4 levels, cull 1200 m |
| terrain tile | 1 km, 1 m resolution |
| texel density | 128 px/m terrain, 512 px/m POI |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Skyline authored after the terrain, so no landmark holds from any approach.
- POI spacing of 8 s, turning the world into a corridor.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Landmark identifiable from four approaches at 800 m.
- [ ] POI spacing within the traversal band.
- [ ] Interaction material break consistent across biomes.
- [ ] LOD pops invisible at 1200 m in motion.

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


