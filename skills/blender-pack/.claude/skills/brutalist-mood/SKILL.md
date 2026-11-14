---
name: brutalist-mood
description: Brutalist and concrete-monument mood direction for Blender architecture and scenes with raw concrete, monumental scale, and austere composition.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: brutalist, brutalism, raw concrete, monumental concrete, austere architecture
  related-skills: archviz, environment-artist, materials, camera-cinematography, minimalist-style
---

# Brutalist Mood

Board-formed concrete mass, structural honesty, and shadow as the primary ornament.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- mass and joint rhythm before surface
- board-form texture scale relative to the building
- shadow as the only ornament

## Direction

- **Mass first.** Brutalism is volume, not texture. Block the massing at 1/8 scale before any material. If the silhouette is weak, no amount of board-forming saves it.
- **Structural honesty.** Visible structure must be the structure. A fake beam that carries nothing is a lie the eye catches in motion.
- **Board-form texture.** Form boards 15-20 cm wide, 2.4-3.6 m long, with visible tie holes at 45 cm spacing. Texture scale is fixed by the formwork, not by taste.
- **Shadow as ornament.** Deep reveals, cantilevers, and recessed joints; no applied decoration. If a surface has decoration, it has failed.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| form board | 15-20 cm x 2.4-3.6 m |
| tie holes | 45 cm grid |
| reveal depth | 8-15 cm |
| texel density | 512 px/m |
| concrete roughness | 0.72-0.86 |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Board-form texture applied at an arbitrary scale, reading as wallpaper.
- Applied ornament, which is the one thing brutalism cannot survive.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Silhouette readable as brutalist at 1/8 scale.
- [ ] Every visible beam carries load.
- [ ] Board-form scale consistent across the building.
- [ ] No applied ornament anywhere.

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


