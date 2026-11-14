---
name: cartoon-style
description: Cartoon art direction for Blender with squash-stretch readable shapes, bold colors, and graphic silhouettes for games and animation.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: cartoon, toon, rubber hose, Saturday morning, bold cartoon, graphic cartoon
  related-skills: stylized-style, anime-style, materials, rendering, character-artist
---

# Cartoon Style

Shape language first: appeal, squash and stretch, and a palette that reads at any size.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- shape language (round, square, triangle) and character
- squash and stretch range in the deformation
- appeal - whether the form invites the eye

## Direction

- **Shape language.** Round = friendly, square = solid, triangle = dangerous. Every character and prop commits to one primary shape. Mixing is fine; having no primary is not.
- **Squash and stretch.** 1.2-1.4x extremes on impact and anticipation. Cartoon physics, staged and readable; the exaggeration is what sells the weight.
- **Appeal.** Big forms, small details, clear negative space. Appeal is a technical property: if the silhouette is not pleasing at thumbnail size, it is not finished.
- **Palette.** 5-7 saturated hues with one dark for contrast. Value structure still matters; cartoon is not flat.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| squash/stretch | 1.2-1.4x extremes |
| palette | 5-7 saturated hues |
| bevel | 20-60 mm (soft) |
| silhouette | reads at 64 px |
| texture | flat or 2-3 band ramp |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- No committed primary shape, so nothing is appealing at thumbnail size.
- Uniform soft shading instead of staged squash and stretch.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Every character has a committed primary shape.
- [ ] Impact frames show visible squash/stretch.
- [ ] Silhouette pleasing at 64 px.
- [ ] Palette within 5-7 hues with one dark.

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


