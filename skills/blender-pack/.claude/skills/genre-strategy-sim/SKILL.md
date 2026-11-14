---
name: genre-strategy-sim
description: Art direction for strategy, RTS, turn-based strategy, tower defense, MOBA, city builder, colony sim, and simulation games in Blender.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: strategy, RTS, turn-based strategy, tower defense, MOBA, city builder, colony sim, simulation, life sim, farming sim
  related-skills: isometric-style, environment-artist, prop-artist, scene-assembly, vegetation-artist
---

# Genre Strategy Sim

Readable from 40 m up: unit silhouettes, tile language, and UI-safe colour coding.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- unit type at maximum zoom-out
- team ownership without relying on colour alone
- terrain that reads as passable or not

## Direction

- **Zoom-out contract.** Everything must be readable at the game's furthest camera. Design at that zoom first, then add detail inward. Detail that only exists at close zoom is decoration.
- **Team coding.** Colour plus shape plus decal. Colourblind-safe pairs, and a shape difference at 40 m. Never colour alone.
- **Terrain grammar.** Three passability classes with distinct surface language: flat/walkable, broken/slow, blocked/impassable. Blocked terrain needs a hard silhouette, not a texture.
- **Tile and grid.** Snap to the simulation grid exactly. A mesh half a tile off is a unit that walks into a wall it can see.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| unit height | 1.8 m, base >= 0.6 m |
| max camera | 40 m, unit reads >= 12 px |
| grid | 1 m tile, snap exact |
| team colour | dE >= 25, plus shape |
| texel density | 256 px/m units, 128 px/m terrain |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Detail authored at close zoom, invisible at the camera the game actually uses.
- Team colour as the only ownership cue.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Zoom-out screenshot: every unit type identifiable.
- [ ] Greyscale pass: teams still separable.
- [ ] Terrain passability matches the navmesh.
- [ ] No mesh straddles a tile boundary.

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


