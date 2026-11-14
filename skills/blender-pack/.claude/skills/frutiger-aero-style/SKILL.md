---
name: frutiger-aero-style
description: Frutiger Aero art direction for Blender with glossy skeuomorphism, aqua UI cues, nature-tech optimism, and mid-2000s futurism.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: Frutiger Aero, aero, aqua UI, glossy 2000s, vista aesthetic, bubbly futurism
  related-skills: neon-retrofuturism, materials, lighting, environment-artist, lookdev
---

# Frutiger Aero Style

Glossy 2000s optimism: aqua glass, skeuomorphic buttons, sunlit greens and a very specific specular.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- the gloss response - bright, wide, and always on the shoulder
- aqua glass with visible refraction
- nature and technology sharing one frame without irony

## Direction

- **The gloss.** Wide, soft specular along one shoulder, plus a hard highlight. Roughness 0.08-0.18 with a clearcoat layer. Gloss is the signature; a matte frutiger surface is a different style.
- **Aqua glass.** Green-blue transmissive volume, IOR 1.35-1.45, visible refraction. Build bubbles as thick shells with dispersion, not as spheres with alpha.
- **Palette.** Fresh green, sky cyan, white, and one saturated accent. High key, low contrast, sunlit. No mud, no grey.
- **Skeuomorphism.** Buttons are physically pressed: bevel, inner shadow, gradient. Forms are rounded with a 1-3 cm radius, never sharp.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| roughness | 0.08-0.18 + clearcoat |
| glass IOR | 1.35-1.45 |
| bevel radius | 10-30 mm |
| palette | green 7BC043, cyan 4FC3F7, white |
| exposure | +0.7 to +1.2 EV |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Matte materials with a green tint, which is not frutiger aero at all.
- Bubbles as alpha spheres instead of refractive shells.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Every hero surface has a visible shoulder gloss.
- [ ] Glass shows refraction at grazing angles.
- [ ] No pure grey or mud tone anywhere.
- [ ] All edges rounded; zero sharp corners on props.

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


