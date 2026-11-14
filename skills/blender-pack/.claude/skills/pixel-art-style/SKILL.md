---
name: pixel-art-style
description: Pixel-art and texel-constrained art direction for Blender assets destined for pixel rendering, low-res textures, or HD-2D-adjacent pixel reads.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: pixel art, pixel, texel, low res texture, sprite-like, pixelated
  related-skills: lowpoly-style, retro-8bit-style, retro-16bit-style, hd-2d-style, materials
---

# Pixel Art Style

Hand-authored pixel discipline: clusters, anti-alias control, and intentional jaggies.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- cluster shapes and their intentionality
- selective anti-aliasing versus accidental blur
- readability at the target resolution

## Direction

- **Clusters, not pixels.** Form is built from 2x2 to 4x4 clusters. Single-pixel noise reads as dirt, not as shading.
- **Selective AA.** Anti-alias only where a curve meets a flat, never along a straight edge. Clean jaggies are the style; smudged ones are a mistake.
- **Hue shifting.** Shadows shift toward blue, lights toward yellow, never toward black and white. Pure black and white are reserved for the extremes of the ramp.
- **Author at 1x.** Never downscale a 4x render; downscaling produces dead pixels and uneven clusters.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| cluster | 2x2 to 4x4 px |
| ramp | 5-7 steps, hue shifted |
| AA | curves only, 1 px |
| black/white | ramp extremes only |
| export | 1x authored, nearest |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Downscaled 4x render, producing dead pixels and uneven clusters.
- Single-pixel noise mistaken for shading.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] No isolated single-pixel noise in shading.
- [ ] Anti-aliasing appears only on curves.
- [ ] Shadows hue-shift, not desaturate to black.
- [ ] Authored at 1x, no downscale artifacts.

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


