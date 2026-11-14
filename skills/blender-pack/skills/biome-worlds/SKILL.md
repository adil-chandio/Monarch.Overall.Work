---
name: biome-worlds
description: Biome and setting art direction for Blender covering underwater, desert, arctic, jungle, underground, and floating-island environments.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: underwater, desert, arctic, jungle, underground, cave, floating islands, biome, climate setting
  related-skills: environment-artist, vegetation-artist, lighting, materials, scene-assembly
---

# Biome Worlds

Biomes that differ in light, scale and material before they differ in colour.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- biome identity without hue
- the transition band between biomes
- vegetation scale as the primary biome signal

## Direction

- **Identity before hue.** Two biomes must differ in light angle, vegetation scale, and ground material. If the only difference is the colour grade, the biome swap reads as a filter.
- **Transition bands.** 30-60 m of blending, never a hard seam. Use a third set of transitional assets; a hard line between two palettes is the most visible world-building failure.
- **Scale signal.** Vegetation height is the strongest biome cue in first person: 0.3 m ground cover, 1.5 m shrub, 8 m canopy, 30 m emergent. Pick a band per biome and hold it.
- **Ground truth.** Ground material carries the biome's water history. Silt means slow water, angular rock means recent violence.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| biome | veg height | ground | key light |
| --- | --- | --- | --- |
| tundra | 0.1-0.4 m | frost-shattered rock | low, cold |
| temperate | 0.3-1.5 m / 20 m canopy | loam | 45 deg, neutral |
| desert | 0-0.6 m | aeolian sand | high, warm |
| rainforest | 1.5 m / 35 m canopy | silt, leaf litter | dappled, 80% overcast |
| volcanic | 0 m | basalt, ash | point, orange |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Biomes distinguished only by colour grade, reading as a filter.
- Hard seam between adjacent biomes with no transitional assets.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Greyscale screenshot: biomes still distinguishable.
- [ ] No hard seam between adjacent biomes.
- [ ] Vegetation height holds its band across the biome.
- [ ] Ground material consistent with the biome's water history.

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


