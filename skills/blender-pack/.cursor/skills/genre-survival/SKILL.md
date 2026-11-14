---
name: genre-survival
description: Art direction for survival and survival-horror gameplay spaces in Blender emphasizing resource props, crafting readability, and tension routes.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: survival, survival horror, crafting, resource gathering, survival game art
  related-skills: environment-artist, prop-artist, horror-style, set-dressing, biome-worlds
---

# Genre Survival

Resource legibility, craftable silhouettes, and base-building that reads as shelter.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- whether a resource node is harvestable or spent at 20 m
- shelter-ness: can the player tell this blocks weather
- tier progression visible in material, not in a tooltip

## Direction

- **Node states.** Harvestable, depleted, respawning: three distinct silhouettes AND three distinct values. A node that only differs by emissive is invisible in daylight.
- **Tier language.** Tier 1 rough plank and lashing, tier 2 sawn and joined, tier 3 machined and welded. Material response carries progression; the player should read their own wealth from a screenshot.
- **Shelter readability.** Overhead cover, windbreak, and enclosed volume are separate visual claims. A roof that does not visually overhang does not read as shelter.
- **Craft affordance.** Hand tools read at 1.5 m, structures at 6 m. Anything that must be found on the ground gets a silhouette break (a hook, a handle, a lean).

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| node size | 0.4-1.2 m, silhouette break >= 15% |
| build grid | 0.5 m snap, 2.5 m wall height |
| prop texel | 512 px/m hand prop, 256 px/m structure |
| tri budget | 800 node, 4k structure module |
| LOD switch | 25 m / 60 m / cull 140 m |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Node states that differ only by an emissive tint, invisible at noon.
- Tier progression expressed in tooltips rather than material.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Daylight pass: node state readable without emissive.
- [ ] Screenshot test: could a stranger rank the tiers?
- [ ] Shelter claims match the collider, not the mesh.
- [ ] Build pieces snap on a slope without floating.

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


