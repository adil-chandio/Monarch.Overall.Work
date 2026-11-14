---
name: painterly-style
description: Painterly art direction spanning watercolor and oil-painting looks for Blender using soft edges, pigment texture, and illustrative lighting.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: painterly, watercolor, oil painting, impressionist, illustrative paint, gouache
  related-skills: hand-painted-style, stylized-style, materials, compositing, rendering
---

# Painterly Style

Full-frame painterly rendering: brush-oriented shading, edge darkening, and canvas structure.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- brush-oriented shading and its scale
- edge treatment - darkening and impasto
- canvas or paper structure under the image

## Direction

- **Brush-oriented shading.** Post-process or shader that quantises shading into strokes following the normal, not the screen. Screen-space strokes swim under camera motion; normal-aligned strokes hold.
- **Edge darkening.** A soft dark line at occlusion boundaries, 2-4 px, is what makes the image read as paint rather than as a filter.
- **Canvas structure.** A subtle tooth/weave normal at 2-4% strength under everything. Without it, painterly reads as watercolour blur.
- **Palette restraint.** 5-8 hues, mixed on the canvas, not straight from the tube.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| stroke scale | 3-12 px, normal-aligned |
| edge darkening | 2-4 px, 60-80% opacity |
| canvas tooth | 2-4% normal strength |
| palette | 5-8 hues |
| outline | none (edge darkening instead) |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Screen-space strokes that swim under camera motion.
- Edge outline instead of edge darkening.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Strokes stay anchored to the surface under camera motion.
- [ ] Occlusion edges darkened, not outlined.
- [ ] Canvas structure visible at 100% zoom.
- [ ] Palette within 5-8 hues.

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


