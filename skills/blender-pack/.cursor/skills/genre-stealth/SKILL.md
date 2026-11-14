---
name: genre-stealth
description: Art direction for stealth-game spaces in Blender with shadow volumes, patrol-friendly layouts, and concealment materials.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: stealth, stealth game, shadow play, infiltration, stealth level art
  related-skills: environment-artist, lighting, materials, scene-assembly
---

# Genre Stealth

Light and shadow as a readable mechanic, cover at crouch height, patrol sightline staging.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- where the shadow actually is versus where the player thinks it is
- cover at crouch eye height (1.1 m), not at chest height
- the visual difference between safe and one step from detected

## Direction

- **Light is a collider.** Author light pools as explicit volumes. If the shader and the gameplay light disagree, the player learns to distrust the image.
- **Cover height.** Crouch eye is 1.1 m. Cover that stops at 1.0 m reads as exposed even when it is safe. Mismatch between visual top and collision top is the single most common stealth bug.
- **Hanging cover.** Vents, ledges and pipes need a visible handhold. A ledge you cannot see from below is not an affordance.
- **Detection staging.** Safe / suspicious / alert must differ in enemy posture and light, not only in an icon. Stage it in geometry so it reads in a screenshot.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| crouch eye | 1.1 m |
| low cover top | 1.25 m (visual = collision) |
| light pool | >= 0.6 m of floor, soft edge |
| patrol sightline | 8-14 m corridor |
| texel density | 512 px/m hero, 256 px/m set |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Visual cover top at 1.25 m, collision top at 1.05 m; the player is shot through a wall they are hiding behind.
- Light pools painted as decals, disagreeing with the gameplay light volume.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Light volume and shader agree within 1 cm at the boundary.
- [ ] Every low cover has collision matching its visible top.
- [ ] Safe/shadow state survives a greyscale screenshot.
- [ ] No cover is climbable by accident.

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


