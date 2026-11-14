---
name: manga-style
description: Manga-inspired art direction for Blender emphasizing monochrome value design, speed lines, screentone feel, and manga panel staging.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: manga, seinen, shonen, shojo, screentone, manga panel, Japanese comic
  related-skills: anime-style, comic-book-style, compositing, camera-cinematography
---

# Manga Style

Ink discipline: line weight hierarchy, screentone density, and hatching that describes form.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- line weight hierarchy (contour > interior > detail)
- screentone dot density and moire control
- hatching direction that follows form

## Direction

- **Line weight hierarchy.** Contour 3-4 px, interior 1-2 px, detail 0.5-1 px. Uniform weight reads as a colouring book, not as manga.
- **Screentone.** Dot density in three steps, rotated 15/45/75 degrees to avoid moire. Screen-space tones swim; UV-anchored tones hold.
- **Hatching follows form.** Direction wraps around volume and tightens in shadow. Cross-hatching is reserved for the darkest 10%.
- **Ink blacks.** Pure black for shadow shapes, never for shading. Grey is tone, black is shape.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| contour line | 3-4 px |
| interior line | 1-2 px |
| tone angles | 15 / 45 / 75 deg |
| dot sizes | 0.3 / 0.5 / 0.8 mm at 2k |
| black area | <= 12% of frame |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Uniform line weight, reading as a colouring book.
- Screentime anchored to screen space, swimming under motion.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Line weight varies by role, not by distance.
- [ ] Screentone anchored to UV, no swimming.
- [ ] No moire pattern at any camera angle.
- [ ] Black used for shapes, not for shading.

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


