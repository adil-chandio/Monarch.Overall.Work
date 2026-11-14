---
name: hd-2d-style
description: HD-2D art direction combining pixel characters/sprites with 3D environments, depth of field, and theatrical lighting.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: HD-2D, HD2D, Octopath, triangle strategy, pixel 3D hybrid
  related-skills: pixel-art-style, environment-artist, camera-cinematography, lighting, compositing
---

# Hd 2D Style

Pixel sprites in 3D space: depth of field, layered parallax, and lighting that respects the sprite.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- the sprite/3D boundary and how light crosses it
- parallax layering that gives 2D sprites real depth
- post-processing that unifies both worlds

## Direction

- **Lit sprites in a lit world.** Sprites need normal maps or a light response that matches the 3D set. A flat sprite in a lit room reads as a sticker.
- **Parallax layers.** 3-5 depth layers with distinct fog values. The sprite sits at one layer, the set occupies the rest; the eye reads depth from fog, not from perspective.
- **Post unifies.** Tilt-shift or a shallow DOF, film grain and a shared grade on both sprite and set. Without a shared post pass, the two mediums never merge.
- **Sprite resolution.** Author at 2-4x the camera resolution so camera moves do not shimmer. Point filtering for the sprite, bilinear for the set.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| parallax layers | 3-5, distinct fog |
| sprite res | 2-4x camera |
| DOF | tilt-shift, 8-20% frame |
| filtering | sprite point, set bilinear |
| grade | shared LUT on both |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- A flat sprite in a lit set, reading as a sticker.
- No shared post pass, so the two mediums never merge.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Sprite responds to scene light, not flat-lit.
- [ ] 3-5 parallax layers present with distinct fog.
- [ ] Camera move produces no sprite shimmer.
- [ ] Shared post pass applied to sprite and set.

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


