---
name: genre-racing-sports
description: Art direction for racing and sports games in Blender with track landmarks, stadium kits, and high-speed readability.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: racing, sports, track, stadium, race course, sports arena
  related-skills: vehicle-artist, environment-artist, materials, camera-cinematography
---

# Genre Racing Sports

Track flow read at speed, braking reference objects, and a vehicle silhouette that tells you its class.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- at 200 km/h, what the player can actually resolve
- corner entry reference, not corner decoration
- vehicle class from outline alone

## Direction

- **Speed budget.** At 200 km/h a player resolves ~25 m ahead. Every corner needs a reference object at 2x braking distance, not at the apex.
- **Flow.** Curvature should be continuous; a kink that reads fine in a top-down view is a wall at speed. Flatten the radius transition, not the kerb.
- **Braking references.** Distinct silhouettes, repeatable colours, one language per track. Signage must be readable at 120 m and 200 km/h: high contrast, thick strokes.
- **Vehicle class.** Silhouette carries class: wide and low (GT), tall and boxy (truck), narrow and faired (bike). Do not rely on livery.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| track width | 10-14 m (14 m overtaking) |
| braking marker | 2x braking distance |
| sign legibility | 120 m at 200 km/h |
| vehicle tri | 60k player car, 25k AI |
| texel density | 512 px/m exterior, 1024 px/m cockpit |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Curvature authored top-down, producing a kink that is a wall at 200 km/h.
- Braking markers placed at the apex instead of at 2x braking distance.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] At-speed replay: is the corner entry readable without the map?
- [ ] Signage legible at 120 m in the fogged variant.
- [ ] Kerb and surface transitions do not launch the car.
- [ ] Vehicle class identifiable from a black silhouette.

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


