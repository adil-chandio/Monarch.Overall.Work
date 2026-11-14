---
name: genre-card-party-idle
description: Art direction for card games, deck builders, party games, idle/incremental, educational, and rhythm game presentational spaces in Blender.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: card game, deck builder, party game, idle, incremental, educational, rhythm game, UI stage
  related-skills: prop-artist, camera-cinematography, materials, lookdev, minimalist-style
---

# Genre Card Party Idle

Cards, boards and idle props read as physical objects with a consistent material grammar.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- card legibility at hand size
- material grammar that separates rarity from function
- a board that reads as a place, not as a diagram

## Direction

- **Card legibility at hand size.** At 12 cm on screen, the card frame carries rarity, the art carries identity, the type carries function. Three jobs, three zones, never overlapping.
- **Material grammar.** Foil means rarity, wear means age, edge colour means faction. One material channel per meaning; mixing them destroys the language.
- **Board as place.** Idle and party games need a board that reads as a location with weight: thickness, edge treatment, light falloff. A flat plane with icons is a prototype.
- **Physical honesty.** Cards have thickness (0.3 mm), bevel, and a visible edge. Boards have thickness and a lip. Cheapness reads as flatness.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| card size | 63x88 mm, 0.3 mm thick |
| frame zones | 6 mm border, art 60%, text 18% |
| board thickness | 3-5 mm, 2 mm lip |
| texel density | 1024 px/m card face |
| tri budget | 300 card, 5k board prop |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Cards rendered as flat planes with no thickness; cheapness reads immediately.
- Material channels overloaded, so foil also means faction.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Card readable at hand size on a 720p screen.
- [ ] One material channel per meaning, no mixing.
- [ ] Board reads as an object with thickness at a 30 degree angle.
- [ ] Card edge visible at max tilt without z-fighting.

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


