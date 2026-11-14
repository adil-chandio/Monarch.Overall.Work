---
name: liminal-space-style
description: Liminal space and Backrooms art direction for Blender with empty transitional architecture, wrong familiarity, and endless repetition.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: liminal, liminal space, Backrooms, empty mall, empty school, poolrooms, transitional space
  related-skills: horror-style, environment-artist, lighting, materials, scene-assembly
---

# Liminal Space Style

Transitional places emptied of purpose: wrong lighting, wrong scale, no exits that make sense.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- the lighting that belongs to a different time of day
- architecture with no function (a corridor to nowhere)
- the exit that exists but does not lead out

## Direction

- **Wrong light.** Office fluorescents at night, daylight with no windows. The light belongs to a different scene than the one you are in.
- **Architecture without purpose.** Corridors with doors that all lead back, a pool with no changing room, an airport with no flights. Remove the function and the place becomes hostile.
- **Exit that fails.** The player must be able to see an exit and have it not work. A sealed room is a puzzle; a room whose exit loops is dread.
- **Emptiness has a texture.** Clean, maintained, recently vacated. Dust and damage turn liminal into abandoned; clean and empty is worse.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| light temp | mismatched to context, 3200-6500 K |
| ceiling height | 2.6-9 m (wrong for function) |
| props | 0-3 per room |
| surface | clean, low roughness |
| audio | room tone only, no music |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Dust and damage, turning liminal into abandoned.
- Lighting that matches the context instead of contradicting it.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Lighting temperature belongs to another context.
- [ ] Rooms have no recoverable function.
- [ ] An exit is visible and does not lead out.
- [ ] Surfaces are clean, not decayed.

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


