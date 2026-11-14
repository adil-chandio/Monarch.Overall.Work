---
name: sci-fi-punk-worlds
description: Sci-fi and punk world art direction for Blender including hard sci-fi, space, cyberpunk, steampunk, dieselpunk, atompunk, solarpunk, biopunk, and clockpunk.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: sci-fi, hard sci-fi, space, cyberpunk, steampunk, dieselpunk, atompunk, solarpunk, biopunk, clockpunk, retrofuturism
  related-skills: hard-surface, environment-artist, vehicle-artist, materials, vfx-fx, neon-retrofuturism
---

# Sci Fi Punk Worlds

Cyberpunk, solar punk and industrial sci-fi: a technology story told through maintenance.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- who maintains this, and where they keep their tools
- technology tier consistency across the scene
- the class story in the materials

## Direction

- **Maintenance story.** Every advanced system has a maintenance access: a panel, a ladder, a labelled conduit. Tech with no service access reads as magic, which breaks the genre.
- **Tier consistency.** One scene, one tech tier. A fusion core next to a CRT monitor is a choice; make it a deliberate one or remove it.
- **Class in materials.** Who has clean anodised metal and who has taped repairs. The material split is the politics of the world, readable without dialogue.
- **Signage and language.** Dense, layered, multilingual signage sells density. Keep the layer count high and the individual signs low-contrast except the story beat.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| service access | every hero system |
| signage layers | 4-7 depth layers |
| tech tier | 1 per scene |
| material split | clean vs repaired, 30/70 |
| emissive | practical, not decorative |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Advanced systems with no maintenance access, reading as magic.
- Tech tiers mixed in one scene without intent.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Every advanced system has visible service access.
- [ ] Tech tier uniform within the scene.
- [ ] Class readable from material condition.
- [ ] Signage layered but not brighter than the story beat.

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


