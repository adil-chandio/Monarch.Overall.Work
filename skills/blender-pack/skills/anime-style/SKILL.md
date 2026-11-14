---
name: anime-style
description: Anime and cel-shaded art direction for Blender with hard color breaks, toon shaders, clean silhouettes, and anime proportion language.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: anime, cel shade, toon shader, anime style, hard shadows, manga, Japanese animation look
  related-skills: stylized-style, materials, rendering, character-artist, compositing
---

# Anime Style

Cel shading with line control, rim light as a shape, and hair that reads as volume.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- cel band count and the shadow's edge quality
- line weight on silhouette versus interior
- hair and cloth as silhouette-defining volumes

## Direction

- **Two to three bands.** Light, shadow, and one specular band. Band edges follow form and are hard; a soft gradient anywhere breaks the style.
- **Line hierarchy.** Silhouette 3-5 px, interior 1-2 px, face features 0.5-1 px. Outline width is screen-space constant; a world-space line on a distant character vanishes.
- **Hair as volume.** Hair is modelled as masses, not strands: 5-12 clumps per character, each with its own silhouette. Anime hair is a shape language.
- **Rim light as a shape.** A thin, bright, hard-edged rim on the shadow side separates the character from the background. It is a painted shape, not a lighting term.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| bands | 2-3, hard edge |
| silhouette line | 3-5 px |
| interior line | 1-2 px |
| hair clumps | 5-12 masses |
| rim | 2-6 px hard shape |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- A soft gradient anywhere in the shading, breaking the cel look.
- World-space outlines that vanish on distant characters.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Band edges hard at every distance.
- [ ] Silhouette line constant in screen space.
- [ ] Hair reads as masses, not strands.
- [ ] Rim is a shape with a hard edge.

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


