---
name: stop-motion-craft-style
description: Stop-motion and craft aesthetics for Blender including claymation, paper craft, and handmade physical-material cues.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: stop motion, claymation, clay, paper craft, papercraft, handmade, craft aesthetic, puppet physical
  related-skills: materials, lighting, camera-cinematography, character-artist, mascot-puppet-horror
---

# Stop Motion Craft Style

Handmade miniature logic: real materials at 1:12 scale, a shallow set, and visible frame-stepping.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- material honesty at miniature scale (felt, clay, cardboard, wood)
- shallow depth of field appropriate to a small set
- frame-stepping and its imperfect timing

## Direction

- **Miniature scale.** Build at 1:12; the camera is 0.3-1.2 m from the set. Depth of field is shallow because the set is small, not because it is a style choice.
- **Real materials.** Felt fuzz, clay fingerprints, cardboard edges, visible seams. Smooth 3D-printed surfaces break the illusion immediately.
- **Frame-stepping.** 12 fps on twos, with intentional timing imperfections. Perfect interpolation reads as CGI; the small jitter is the craft.
- **Set imperfection.** Slight dust, a thumbprint, a painted backdrop with visible brush strokes.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| scale | 1:12 |
| fps | 12 (twos), stepped |
| DOF | f/2.8 equivalent, shallow |
| materials | felt, clay, card, wood |
| camera distance | 0.3-1.2 m from set |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Smooth 3D-printed surfaces that break the miniature illusion.
- Interpolated playback at 24 fps instead of 12 on twos.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Materials read handmade at the camera distance.
- [ ] Depth of field matches the miniature scale.
- [ ] Playback is stepped, not interpolated smooth.
- [ ] Backdrop shows brush or seam evidence.

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


