---
name: retro-8bit-style
description: Retro 8-bit art direction for Blender-assisted pixel/low-res aesthetics inspired by NES-era constraints.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: 8-bit, 8bit, NES, retro 8-bit, four color, chunky pixel
  related-skills: pixel-art-style, retro-16bit-style, lowpoly-style, materials
---

# Retro 8Bit Style

8-bit constraints as a design system: 4-colour ramps, tile grids, and no anti-aliasing anywhere.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- tile grid alignment and per-tile colour limits
- 4-colour ramps with no intermediate values
- one-pixel readability

## Direction

- **4-colour ramps.** Per material: shadow, mid, light, highlight. No fifth value. The constraint is the aesthetic; breaking it produces a muddy 16-bit look.
- **Tile discipline.** Everything on an 8 or 16 px grid, including UV layouts. Off-grid detail reads as a mistake at this resolution.
- **No anti-aliasing.** Hard edges, 1 px lines, point filtering. Bilinear filtering on 8-bit art is the fastest way to destroy the style.
- **One-pixel readability.** Every gameplay-critical shape must resolve in a 1 px line: a ladder, a ledge, a projectile.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| ramp | 4 colours per material |
| tile | 8 / 16 px grid |
| filtering | point, no mip blending |
| line weight | 1 px, no AA |
| texel density | 16-32 px/m |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Five-plus values per material, producing a muddy 16-bit look rather than 8-bit.
- Bilinear filtering on 8-bit art.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Every material is exactly 4 values.
- [ ] Point filtering confirmed; no bilinear anywhere.
- [ ] Gameplay shapes readable as 1 px lines.
- [ ] All geometry snaps to the tile grid.

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


