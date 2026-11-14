---
name: comic-book-style
description: Comic book and graphic-novel art direction for Blender with ink-line emphasis, halftone cues, and high-contrast framing.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: comic book, comics, graphic novel, ink lines, halftone, Ben Day, superhero comic
  related-skills: stylized-style, materials, rendering, compositing, camera-cinematography
---

# Comic Book Style

Four-colour ink logic: heavy blacks, flat flats, and halftone that reads as print.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- black placement for shape, not for shadow
- flat colour fills with a limited palette
- halftone dot angle and how it survives motion

## Direction

- **Ink blacks.** Placed as shapes: under a chin, a coat interior, a shadow cast on a wall. Black is a design element, not a falloff.
- **Flat flats.** 3-5 colours per panel, flat fills, no gradients. Print-era comics had a fixed colour set; the constraint is the look.
- **Halftone.** CMYK-aligned screen at 45 degrees for black, 15/75 for chroma. Dots are UV-anchored and sized by screen-space density, not by material.
- **Line weight.** Contour 3-5 px, interior 1-2 px, cross-hatch 0.5 px. Heavy on the outside, thin on the inside.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| flats | 3-5 per scene |
| black area | 15-25% of frame |
| halftone | 45 deg black, 15/75 chroma |
| contour | 3-5 px screen |
| gradients | none |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Black used as shadow falloff instead of as shape.
- Gradients creeping into flat fills.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Black used as shape, not as shading falloff.
- [ ] Flats within 3-5 colours.
- [ ] Halftone angle consistent and moire-free.
- [ ] Line weight heavy outside, thin inside.

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


