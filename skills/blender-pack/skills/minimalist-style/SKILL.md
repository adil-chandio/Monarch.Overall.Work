---
name: minimalist-style
description: Minimalist and abstract-leaning art direction for Blender with reduced forms, limited palettes, and negative space.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: minimalist, minimal, abstract, reduced forms, negative space, simple shapes
  related-skills: stylized-style, materials, camera-cinematography, lookdev
---

# Minimalist Style

Reduction with intent: one idea per frame, negative space as a subject, and precise proportion.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- the single idea the frame carries
- negative space as a designed element
- proportion precision where few forms exist

## Direction

- **One idea.** Each frame carries one form, one colour event, or one motion. A second idea halves the first; there is no 'and' in minimalism.
- **Negative space.** Treat emptiness as a shape with a designed boundary. 40-70% of frame is deliberate void.
- **Proportion precision.** With three forms on screen, the ratio between them is the whole composition. 1:1.618, 1:2, 2:3; choose and hold.
- **Material restraint.** 1-2 materials, 1-2 colours, one finish. Surface variation is the detail.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| objects per frame | 1-3 |
| negative space | 40-70% |
| palette | 1-2 colours + neutral |
| materials | 1-2 |
| proportion | golden or integer ratio |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- A second idea per frame, halving the first.
- Negative space left over rather than designed.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] One idea per frame, countable.
- [ ] Negative space has a designed boundary.
- [ ] Object ratios follow a chosen proportion system.
- [ ] No more than two materials.

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


