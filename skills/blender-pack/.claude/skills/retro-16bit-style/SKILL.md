---
name: retro-16bit-style
description: Retro 16-bit art direction for Blender-assisted SNES/Genesis-era color richness, dither cues, and sprite-like clarity.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: 16-bit, 16bit, SNES, Genesis, Mega Drive, retro 16-bit
  related-skills: pixel-art-style, retro-8bit-style, materials, lookdev
---

# Retro 16Bit Style

16-bit sprite logic applied to 3D: limited palettes, dithered ramps, chunky readable silhouettes.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- palette limits and ramp construction
- sprite-era silhouette discipline at low resolution
- dithering as structure, not noise

## Direction

- **Palette discipline.** 16-32 colours per scene, 4-6 step ramps per material. Colour count is the style; a photoreal texture set destroys it instantly.
- **Ramp shading.** Banded lighting with hard steps (2-4 bands), not smooth falloff. A toon ramp with a stepped curve is closest to the era's hand-shaded sprites.
- **Dithering.** Ordered 2x2 or 4x4 Bayer at the transition bands only. Dither everywhere is noise; dither at the ramp edge is craft.
- **Silhouette first.** Design at 64x64. If the character does not read as a black shape at that size, detail will not save it.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| palette | 16-32 colours / scene |
| ramp steps | 4-6 per material |
| light bands | 2-4 hard |
| dither | 2x2 / 4x4 Bayer, transitions only |
| texel density | 32-64 px/m |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Photoreal texture set, destroying the palette budget instantly.
- Smooth falloff instead of banded ramps.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Colour count within palette budget (measured, not eyeballed).
- [ ] Lighting is banded, not smooth, on every hero surface.
- [ ] Dither present only at transitions.
- [ ] Silhouette test passes at 64x64.

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


