---
name: indie-horror-aesthetics
description: Indie horror aesthetic pack for Blender covering Silent Hill, Fear to Fathom, Puppet Combo, corporate horror, cabin/forest/hospital horror, and related looks.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: Silent Hill, Fear to Fathom, Puppet Combo, indie horror, corporate horror, cabin horror, hospital horror, forest horror, urban decay horror
  related-skills: horror-style, psx-horror-style, liminal-space-style, environment-artist, lighting
---

# Indie Horror Aesthetics

Low-budget horror as craft: constraint-driven dread, not asset shortage.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- what the camera refuses to show
- texture budget converted into tension
- sound-and-light budget as the real horror engine

## Direction

- **Constraint as tool.** Dark corridors, tight FOV and slow turns hide low asset counts and raise tension. The limitation is the technique.
- **Off-screen first.** The threat is established off-screen before it is modelled. Anything fully lit and fully modelled loses its power.
- **Texture economy.** One grime material and one surface variation, applied unevenly. Uniform tiling is what makes low-budget horror look cheap.
- **Sound does the work.** Dread is 70% audio: room tone, distant impacts, a floorboard under the player's own step.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| FOV | 55-65 deg, tight |
| light | <= 2 sources, 80% shadow |
| grime | 1 material, uneven coverage |
| texture set | 2-3 total, reused |
| room tone | continuous, 25-35 dB |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Uniform tiling that makes a low budget look like a low budget.
- Threat revealed fully lit and fully modelled, losing all power.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Threat established off-screen before reveal.
- [ ] No uniform tiling visible on any wall.
- [ ] Shadow covers >= 70% of frame.
- [ ] One reused grime material, applied unevenly.

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


