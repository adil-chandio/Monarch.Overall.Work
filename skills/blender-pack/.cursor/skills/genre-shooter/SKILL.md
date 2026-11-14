---
name: genre-shooter
description: Art direction for FPS, TPS, shooter, battle royale, and extraction-shooter maps and props in Blender with sightline and cover language.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: shooter, FPS, TPS, battle royale, extraction shooter, cover shooter, gun game art
  related-skills: environment-artist, hard-surface, prop-artist, collision-proxy, scene-assembly
---

# Genre Shooter

Sightlines, cover, landmarking, loot readability - scale to the camera the player actually has.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- sightline length and cover rhythm before any prop detail
- the difference between first-person and third-person scale
- landmark silhouette that survives at 60 m in fog

## Direction

- **Sightlines.** Max engagement distance is a number, not a vibe. FPS 0-40 m, TPS 0-80 m, BR rotation 0-300 m. Every corridor either supports or denies one of those.
- **Cover ladder.** Three heights only: low (crouch, 0.9 m), mid (stand, 1.35 m), high (full block, 2.1 m). Anything between those is unreadable in a firefight.
- **Landmarks.** One dominant silhouette per rotation sector, distinguishable by outline alone. If two sectors read the same in silhouette, the map has no orientation.
- **Loot language.** Rarity is colour plus geometry, never colour alone: a hue shift that fails in colourblind mode is not a language.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| cover height | 0.9 / 1.35 / 2.1 m |
| sightline | FPS 40 m, TPS 80 m, BR 300 m |
| door width | 1.0-1.2 m (1.6 m combat) |
| prop density | 1 hero per 12 m, filler <= 25% screen |
| texel density | 512 px/m hero, 256 px/m filler |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Cover heights authored by eye, so crouch cover is 1.0 m and the player is exposed while believing they are safe.
- Loot rarity coded only in hue; unreadable for ~8% of players.
- Rotation sectors that differ in detail but share a silhouette.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Silhouette test at 60 m with fog on: can you name the sector?
- [ ] Cover heights snap to the ladder, not to taste.
- [ ] Colourblind pass: rarity still readable as grey.
- [ ] Collision proxies match visible geometry within 5 cm.

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


