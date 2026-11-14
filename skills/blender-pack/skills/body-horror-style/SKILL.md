---
name: body-horror-style
description: Body horror art direction for Blender focusing on flesh wrongness, mutation, fusion, and visceral material storytelling.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: body horror, mutation, flesh, visceral, grotesque anatomy, Cronenberg
  related-skills: horror-style, creature-artist, sculpting, materials, character-artist
---

# Body Horror Style

Anatomical wrongness with internal logic: mutation that follows a rule the viewer can learn.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- the rule the mutation follows
- anatomical reference that is almost correct
- the restraint that makes the reveal land

## Direction

- **Mutation with a rule.** Growth follows a system: symmetry, repetition, or a function. Random lumps read as a modelling error; a rule reads as disease.
- **Almost-correct anatomy.** Start from real musculature and derive. The horror is in the recognition of a real structure doing the wrong thing.
- **Restraint budget.** One reveal per scene, and the camera does not linger. Overexposure kills the effect faster than any amount of detail.
- **Wetness and subsurface.** Body horror needs SSS, specular wetness, and a plausible colour (bruise yellow-green, not pure red). Dry grey flesh reads as rubber.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| reveal | 1 per scene, <= 4 s |
| SSS radius | 2-8 mm |
| wetness roughness | 0.15-0.35 |
| bruise palette | yellow-green to deep purple |
| symmetry rule | stated and held |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Random mutation with no rule, reading as a modelling error.
- Dry grey flesh with no SSS or specular.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Mutation follows a stated rule consistently.
- [ ] Anatomy derived from real reference.
- [ ] One reveal per scene, not repeated.
- [ ] Flesh reads wet: SSS plus specular present.

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


