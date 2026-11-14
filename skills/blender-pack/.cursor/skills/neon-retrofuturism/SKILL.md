---
name: neon-retrofuturism
description: Neon, vaporwave, synthwave, and retrofuturistic mood/art direction for Blender with grid horizons, chrome, and dusk palettes.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: neon, vaporwave, synthwave, retrofuturistic, outrun, retrowave, neon nights
  related-skills: sci-fi-punk-worlds, lighting, materials, compositing, environment-artist
---

# Neon Retrofuturism

Emissive-driven lighting, wet specular, and a magenta/cyan grammar that stays readable under bloom.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- emissive as the primary light source, not as decoration
- wet-surface specular as the ground's main feature
- a value range that survives heavy bloom

## Direction

- **Emissive is a light.** Signage and strips are actual light sources with falloff, not glowing decals. Drive the scene from them and let practicals be practicals.
- **Wet ground.** Roughness 0.05-0.15 on ground planes with a normal-mapped ripple. The reflection is the shot; a dry neon street reads as a warehouse with stickers.
- **Two-hue grammar.** Cyan and magenta split the frame, with a warm sodium practical to anchor the human zone. Three light roles, three hues.
- **Value control.** Bloom at 0.6-1.2 with a threshold that does not eat the midtones. If the frame is 90% emissive, nothing reads.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| emissive strength | 8-35 W/m2 practical |
| ground roughness | 0.05-0.15, rippled |
| bloom | 0.6-1.2, threshold 0.85 |
| hues | cyan + magenta + sodium |
| fog | 0.012-0.03 density, height falloff |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Emissive decals with no light contribution, so the street is dark under all the signs.
- Bloom threshold eating the midtones; the frame is 90% glow.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Removing emissives leaves a lit scene (practicals exist).
- [ ] Ground reads wet at a 20 degree grazing angle.
- [ ] Three light roles, no fourth hue.
- [ ] Midtones survive bloom: the histogram has a middle.

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


