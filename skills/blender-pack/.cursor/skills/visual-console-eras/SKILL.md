---
name: visual-console-eras
description: Visual era art direction for Blender covering PS1–PS5 stylistic cues, retro arcade, DOS, CRT, VHS, and film-grain presentation.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: PS1 style, PS2 style, PS3 style, PS4 style, PS5 style, retro arcade, DOS style, CRT style, VHS style, film grain
  related-skills: lowpoly-style, psx-horror-style, realistic-style, compositing, materials
---

# Visual Console Eras

Console-generation constraint packs: what each era's hardware could and could not do.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- the era's actual limits (resolution, palette, polygon count, filtering)
- the artefacts that identify the era
- which limits to honour and which to stylise

## Direction

- **Pick one era and honour its numbers.** PS1: 320x240, 15-bit colour, affine texture mapping, no z-buffer, vertex snapping. N64: 320x240, bilinear, fog to hide draw distance. PS2: 640x480, 8 MB texture memory.
- **Signature artefacts as intent.** Affine warping, dithered gradients, vertex jitter and fog walls are the era's fingerprints. Recreate them deliberately, not accidentally.
- **Do not mix eras.** A PS1 body with PS3 specular is a muddle. Choose the lighting model that matches the vertex budget.
- **Readability survives the limits.** If the era's limits destroy gameplay readability, break the limit for gameplay elements only.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| era | res | colour | signature |
| --- | --- | --- | --- |
| PS1 | 320x240 | 15-bit, dither | affine warp, vertex snap |
| N64 | 320x240 | 16-bit | bilinear blur, fog wall |
| PS2 | 640x480 | 24-bit | 8 MB tex, heavy bloom |
| GC | 640x480 | 24-bit | 8-light hardware |
| 360 | 1280x720 | 24-bit | normal maps, bloom |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Mixing eras: PS1 geometry with PS3 specular.
- Signature artefacts reproduced accidentally rather than deliberately.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Era numbers documented and honoured.
- [ ] Signature artefacts reproduced intentionally.
- [ ] No lighting model from a later era.
- [ ] Gameplay readability preserved where limits conflict.

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


