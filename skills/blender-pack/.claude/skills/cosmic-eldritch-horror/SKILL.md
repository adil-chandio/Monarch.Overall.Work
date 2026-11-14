---
name: cosmic-eldritch-horror
description: Cosmic, eldritch, and Lovecraftian horror art direction for Blender with non-Euclidean cues, impossible scale, and incomprehensible forms.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: cosmic horror, eldritch, Lovecraftian, Lovecraft, non-Euclidean, unknowable, void horror
  related-skills: horror-style, creature-artist, lighting, vfx-fx, compositing
---

# Cosmic Eldritch Horror

Scale that defeats comprehension: geometry that is wrong at a distance, and a viewer who is too small.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- scale cues that make the viewer small
- non-Euclidean suggestion without breaking navigation
- the point where detail stops helping

## Direction

- **Defeat scale.** Familiar units beside impossible ones: a door 40 m tall, stairs with 2000 steps. The viewer measures with the familiar object and fails.
- **Wrong at distance.** Geometry that reads correctly up close and wrong from far away (or the reverse). The reveal is a change of viewpoint, not a jump scare.
- **Navigation safety.** Non-Euclidean suggestion must be cosmetic. If the player can get lost in a way the map cannot represent, the level is broken.
- **Stop detailing.** Eldritch reads best when detail runs out. Let surfaces become texture, then let texture become noise.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| scale anchor | 1 familiar object per shot |
| structure height | 10-40x human |
| fog | 0.02-0.05, hides the end |
| detail falloff | full at 5 m, noise at 60 m |
| camera | low, looking up |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Non-Euclidean geometry that breaks navigation, not just perception.
- Detail continuing to the horizon, defeating the scale.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] A familiar scale anchor exists in every shot.
- [ ] Impossible geometry is cosmetic, never navigational.
- [ ] Detail degrades intentionally with distance.
- [ ] Camera keeps a low, upward angle.

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


