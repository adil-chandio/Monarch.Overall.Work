---
name: noir-style
description: Noir art direction for Blender with high-contrast lighting, wet streets, silhouettes, and monochrome or limited-color grading.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: noir, neo-noir, hardboiled, detective noir, high contrast black and white
  related-skills: camera-cinematography, lighting, compositing, materials, lookdev
---

# Noir Style

Chiaroscuro with a story: hard key, deep shadow, and window-blind geometry as language.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- the ratio of lit to unlit and what the shadow hides
- shadow geometry as narrative (blinds, bars, silhouettes)
- desaturation that keeps skin alive

## Direction

- **Hard single key.** Small source, hard shadow, 1:8 to 1:16 key-to-fill. The shadow is a character with its own shape.
- **Shadow geometry.** Blinds, railings, window frames project readable patterns. The pattern is motivated by the set, never by a gobo for its own sake.
- **Desaturation with a live skin tone.** 15-25% saturation overall, skin held at 35-45%. Fully desaturated noir reads as a medical image.
- **Wet streets and smoke.** Specular streaks and volumetric shafts give the hard key something to describe.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| key:fill | 1:8 to 1:16 |
| source size | <= 0.2 m (hard) |
| saturation | 15-25%, skin 35-45% |
| shadow area | 60-80% of frame |
| smoke | 0.01-0.03 density |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Fully desaturated, reading as a medical image.
- Gobo patterns with no motivated source in the set.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Key is hard: shadow edge under 15% penumbra.
- [ ] Shadow pattern motivated by set geometry.
- [ ] Skin retains warmth against the desaturated frame.
- [ ] Lit area under 40% of frame.

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


