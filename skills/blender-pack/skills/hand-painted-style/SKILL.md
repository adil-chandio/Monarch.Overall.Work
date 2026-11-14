---
name: hand-painted-style
description: Hand-painted texture art direction for Blender with brushwork albedo, soft value transitions, and stylized PBR restraint.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: hand painted, hand-painted, painted texture, brushwork, stylized painted
  related-skills: stylized-style, texture-workflow, materials, lookdev
---

# Hand Painted Style

Painterly textures with visible brush direction that follows form and light, not UV space.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- brush stroke direction following the form
- value structure that survives the texture's removal
- light painted in, not lit by an engine

## Direction

- **Stroke follows form.** Brush direction wraps around the cylinder, up the wall, along the muscle. Strokes that follow UV space instead read as a decal.
- **Value first.** The texture's value structure must work with the lighting off. Hand-painted art carries its own light; engine lighting is a supplement.
- **Painted light.** Baked highlights and shadows are part of the texture. Use an unlit or lightly-lit shader so the painted light is not doubled by real light.
- **Edge control.** Hard edges at form breaks, soft edges inside a form. Uniform softness reads as blur; uniform hard edges read as cel.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| texture res | 2048 hero, 1024 filler |
| shader | unlit or 20% lit |
| stroke width | 2-8 px at 2k |
| value range | 0.15-0.85, no pure white |
| UV | painted in UV space, strokes follow form |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Strokes following UV space instead of form.
- Engine lighting doubling the painted light.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Stroke direction follows form on every curved surface.
- [ ] Texture reads with engine lighting off.
- [ ] Hard edges only at form breaks.
- [ ] No pure black or pure white in the texture.

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


