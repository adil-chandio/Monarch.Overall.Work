---
name: fantasy-worlds
description: Fantasy world-building art direction for Blender covering medieval, high fantasy, dark fantasy, and urban fantasy asset language.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: fantasy, medieval, high fantasy, dark fantasy, urban fantasy, castle, magic world
  related-skills: environment-artist, prop-artist, materials, vegetation-artist, creature-artist
---

# Fantasy Worlds

Magic systems with visual rules, architecture that obeys its own physics, and a consistent wonder language.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- the rule the magic follows, visible in the environment
- architecture that obeys a physics, even a fictional one
- wonder budget - how much spectacle per frame

## Direction

- **Write the rule, then build it.** Magic has a cost, a source and a limit. Show the source in the environment (ley lines, crystal seams) so the audience can predict where power is.
- **Architecture obeys.** Floating stone needs a visible counterforce, a tether, or a stated rule. 'It floats' is acceptable only if the world has already paid for it.
- **Wonder budget.** One spectacle per shot. Two competing wonders cancel each other; the eye picks the brighter one and ignores the story.
- **Material language.** Magic-affected surfaces share a material signature (emissive seams, crystalline fracture, verdigris). Consistency is what makes it feel like physics.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| spectacle | 1 per shot |
| magic source | visible in >= 1 per scene |
| emissive seams | consistent width 2-6 cm |
| architecture | counterforce visible |
| palette | 1 magic hue, world neutral |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Floating architecture with no visible counterforce.
- Two competing spectacles in one shot, cancelling each other.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Magic source visible where magic is used.
- [ ] Every impossible structure shows its counterforce.
- [ ] One spectacle element per shot, counted.
- [ ] Magic material signature consistent across scenes.

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


