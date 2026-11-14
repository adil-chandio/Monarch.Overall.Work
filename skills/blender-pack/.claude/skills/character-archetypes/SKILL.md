---
name: character-archetypes
description: Character archetype art direction for Blender covering fantasy races, horror creatures, roles (knight, assassin, detective), and body types (mecha, android, chibi, etc.).
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: archetype, elf, dwarf, orc, goblin, vampire, werewolf, zombie, alien, mecha, android, knight, assassin, superhero, villain, witch, wizard, cowboy, soldier
  related-skills: character-artist, creature-artist, anime-style, realistic-style, materials
---

# Character Archetypes

Archetype silhouettes and proportion kits that a player can classify before they read a name.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- silhouette classification in under one second
- proportion kit that matches the archetype's role
- costume mass that survives at gameplay distance

## Direction

- **Classify by silhouette.** Tank wide and low (1.6:1 width:height), rogue narrow and asymmetric, mage tall and vertical, healer soft and rounded. One glance, no colour needed.
- **Proportion kits.** Heroic 8 heads, stylised 6, chibi 3, brute 5 with widened shoulders. Lock the kit per archetype; mixing heads-per-figure blurs the cast.
- **Costume mass.** 3 masses maximum per character: torso, shoulders, one asymmetric accent. A fourth mass makes the silhouette mush at 20 m.
- **Role in the prop.** Weapon or tool scale signals role before animation does: 0.4 m for a caster, 1.8 m for a bruiser.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| archetype | heads | W:H | prop |
| --- | --- | --- | --- |
| tank | 7 | 1.6 | 1.4 m shield |
| rogue | 7.5 | 0.9 asym | 0.5 m blade |
| mage | 8 | 1.0 vertical | 1.8 m staff |
| healer | 7.5 | 1.1 soft | 0.4 m focus |
| brute | 5 | 1.9 | 1.2 m club |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Heads-per-figure drifting across the cast, reading as two art styles.
- A fourth costume mass that turns the silhouette to mush at 20 m.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Cast classifiable from black silhouettes alone.
- [ ] Heads-per-figure consistent within an archetype.
- [ ] No character carries more than three costume masses.
- [ ] Prop scale matches role at 20 m.

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


