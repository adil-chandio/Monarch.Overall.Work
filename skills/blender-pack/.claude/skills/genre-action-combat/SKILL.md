---
name: genre-action-combat
description: Art direction for action, hack-and-slash, beat 'em up, and fighting-game readable combat spaces and prop language in Blender.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: action game, hack and slash, beat em up, brawler, fighting game, combat arena, action adventure
  related-skills: environment-artist, prop-artist, camera-cinematography, vfx-fx
---

# Genre Action Combat

Hitboxes that match the animation, impact frames, and arena geometry that serves the camera.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- where the weapon actually is versus where the hitbox is
- impact readability in the first 3 frames
- arena geometry that never eats the camera

## Direction

- **Hitbox honesty.** The hitbox follows the weapon's animated volume within one frame. A hitbox that leads or trails the mesh teaches players to distrust the screen.
- **Impact staging.** Frame 1 contact, frames 2-3 freeze plus flash, frames 4-6 debris. The freeze is what sells weight; without it, every hit is a number change.
- **Camera-safe arenas.** 5 m clear of geometry behind the player at default distance. Pillars and walls stop outside that ring.
- **Enemy silhouette hierarchy.** Threat tier in the outline: mass, height, weapon reach. A boss and a grunt must not share a silhouette class.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| hitbox match | 1 frame, 0.033 s |
| hitstop | 2-4 frames light, 6-8 heavy |
| camera clear | 5 m behind player |
| arena ring | 18 m |
| texel density | 1024 px/m hero weapon |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Hitbox that leads the weapon mesh by 2 frames; players learn to distrust the screen.
- No hitstop, so every hit reads as a number change.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Hitbox and mesh agree frame by frame on a debug pass.
- [ ] Every hit has a freeze; none exceed 8 frames.
- [ ] Camera never clips during a dodge or launcher.
- [ ] Threat tier readable from silhouette only.

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


