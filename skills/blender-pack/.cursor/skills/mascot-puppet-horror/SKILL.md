---
name: mascot-puppet-horror
description: Mascot and puppet horror art direction for Blender with cheerful brand characters made wrong, felt/foam materials, and uncanny performance.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: mascot horror, puppet horror, felt horror, costume horror, Happy Tree wrongness, puppet combo adjacent
  related-skills: horror-style, stop-motion-craft-style, character-artist, psx-horror-style, materials
---

# Mascot Puppet Horror

Friendly forms made wrong: mascot proportions, felt and plastic materials, and eyes that do not blink.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- the mascot proportion kit and where it breaks
- handmade material honesty (felt, seams, plastic eyes)
- stillness and non-blinking as the horror device

## Direction

- **Mascot proportions.** Oversized head (1:3), mitten hands, no visible neck, tube limbs. The kit is designed to be friendly; the horror is that it is not.
- **Handmade honesty.** Felt fuzz, visible seams, uneven stitching, plastic eyes with a hard specular. A CGI-smooth mascot reads as a game character, not as a costume someone is inside.
- **Stillness.** The mascot does not idle. No breathing, no weight shift, no blinking. Motion is the tell, so remove the motion.
- **The body inside.** Occasionally imply the operator: a seam that gapes, a hand too large for the glove. One implication per scene.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| head:body | 1:3 |
| felt fuzz | 1-3 mm displacement |
| seam | visible, 4-6 mm |
| eye specular | sharp, 0.05 roughness |
| idle | zero (no breathing, no sway) |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- A CGI-smooth mascot that reads as a game character, not a costume.
- Idle breathing, which kills the stillness.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Mascot kit matches the friendly proportion scheme.
- [ ] Materials read handmade: fuzz, seams, stitching.
- [ ] Zero idle animation on the mascot.
- [ ] At most one operator implication per scene.

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


