---
name: folk-horror-style
description: Folk horror art direction for Blender with rural ritual uncanny, pastoral daylight dread, and community-wrongness storytelling.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: folk horror, rural horror, ritual, pagan, pastoral dread, village horror, Wicker Man
  related-skills: horror-style, environment-artist, set-dressing, vegetation-artist, materials
---

# Folk Horror Style

Daylight dread: ritual objects, agricultural cycles, and a community that is politely wrong.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- daylight as the horror condition, not night
- ritual objects embedded in ordinary life
- the wrongness in ordinary rural detail

## Direction

- **Daylight horror.** Overcast, flat, high-key light. Bright and wrong is more unsettling than dark and loud, and it is much harder to do.
- **Ritual in the everyday.** Offerings on a windowsill, a chair facing the field. The objects are ordinary; only the arrangement is wrong.
- **Agricultural calendar.** Everything is seasonal and cyclical: harvest, sowing, culling. The world is on a schedule the visitor does not know.
- **Politeness.** The community is warm and slightly too practised. Architecture should be tidy, maintained, and just slightly off in proportion.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| light | overcast, 4000-5500 K, flat |
| contrast | 2:1 to 3:1, soft shadows |
| palette | earth, bone, one faded red |
| wrongness | 1 per scene, in arrangement |
| camera | eye level, static, wide |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Falling back on darkness, which is a different genre.
- Five wrong things per scene instead of one arrangement.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Horror reads in daylight with no darkness assist.
- [ ] Ritual objects sit inside ordinary domestic life.
- [ ] One arrangement is wrong per scene, not five.
- [ ] Palette holds earth/bone with a single red accent.

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


