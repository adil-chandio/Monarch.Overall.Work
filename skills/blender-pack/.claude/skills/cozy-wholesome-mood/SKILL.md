---
name: cozy-wholesome-mood
description: Cozy, cute, wholesome, relaxing, and peaceful mood direction for Blender assets and scenes.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: cozy, cute, wholesome, relaxing, peaceful, hygge, warm lighting cozy
  related-skills: stylized-style, lighting, set-dressing, materials, camera-cinematography
---

# Cozy Wholesome Mood

Warmth as a lighting problem: soft sources, low contrast, and clutter that reads as care.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- light softness and warmth as the primary mood device
- clutter density that reads as lived-in, not messy
- roundness and material softness across the whole set

## Direction

- **Light from inside the room.** Warm practicals, 2700-3000 K, with a soft source size (>= 0.5 m). A point light reads as a spotlight; a soft area light reads as a lamp.
- **Low contrast.** 2:1 to 3:1 key to fill, with a lifted toe. Cozy needs visible shadow detail; crushed blacks are the opposite of the mood.
- **Clutter as care.** Density 15-25 props per 10 m2, all intentional: books used, mugs paired, blankets folded. Random scatter reads as neglect.
- **Roundness.** 5-20 mm bevels on everything, no sharp corners, no hard metal. Softness is the material language.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| colour temp | 2700-3000 K |
| key:fill | 2:1 to 3:1 |
| prop density | 15-25 per 10 m2 |
| bevel | 5-20 mm everywhere |
| palette | amber, cream, sage, terracotta |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Point lights standing in for soft practicals, producing spotlights.
- Crushed blacks in the corners.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Every light source has a visible soft fixture.
- [ ] Shadow detail present in the darkest corner.
- [ ] Prop density within band and every prop intentional.
- [ ] No sharp corner on any prop.

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


