---
name: vector-style
description: Vector-clean art direction for Blender with flat fills, sharp silhouettes, and UI-like graphic clarity.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: vector, flat design, clean vector, graphic flat, svg-like
  related-skills: minimalist-style, cartoon-style, materials, rendering
---

# Vector Style

Flat fills, constant-width strokes, and gradient restraint - the vector look in 3D.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- fill flatness and stroke consistency
- gradient restraint - one per surface at most
- silhouette as the only depth cue

## Direction

- **Flat fills.** Each surface is one value (or a two-stop gradient), with a hard edge to the next. Shading is a decision, not a falloff.
- **Constant strokes.** Outlines are a fixed screen-space width, not world-space. A world-space line on a receding object thins to nothing.
- **One gradient per surface.** A second gradient turns flat design into a 2000s web banner. Rim light is a shape, not a glow.
- **Silhouette depth.** Overlap and edge treatment carry depth; fog, AO and specular are removed or heavily quantised.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| stroke | 2-4 px screen space, constant |
| fills | 1 value or 2-stop gradient |
| gradients | max 1 per surface |
| shading | quantised to 2-3 bands |
| specular | off, or a single shape |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- World-space outlines that thin to nothing with distance.
- A second gradient per surface, turning flat design into a 2000s banner.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Stroke width constant at every depth.
- [ ] No surface has two gradients.
- [ ] Depth reads from overlap alone with the fog off.
- [ ] No smooth specular highlight anywhere.

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


