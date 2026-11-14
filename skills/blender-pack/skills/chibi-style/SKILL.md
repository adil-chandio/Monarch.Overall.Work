---
name: chibi-style
description: Chibi and SD proportion art direction for Blender characters with oversized heads, simplified anatomy, and cute silhouette rules.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: chibi, SD, super deformed, cute proportions, chibi character
  related-skills: anime-style, cartoon-style, character-artist, stylized-style
---

# Chibi Style

3-4 head proportions with adult motion language and oversized props that stay functional.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- head-to-body ratio consistency across the cast
- prop scale relative to the oversized head
- expression readability at tiny body size

## Direction

- **Ratio lock.** Pick 3 or 4 heads and hold it across the whole cast. A 3-head hero beside a 4-head NPC reads as two art styles, not two characters.
- **Expression budget.** With a head at 1/3 of the body, the face carries everything. Eyes at 1/4 head width, mouth as a shape, no nose geometry needed.
- **Prop exaggeration.** Props scale with the head, not the body: a 1.2x oversized weapon reads as charming, a 2x one reads as broken.
- **Adult motion.** Chibi bodies move with full-weight adult timing: grounded feet, real anticipation. The contrast between cute form and real weight is the entire appeal.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| heads | 3 or 4, locked |
| eye width | 1/4 head |
| prop scale | 1.1-1.3x realistic |
| body:head | 2:1 to 3:1 |
| texel density | 512 px/m face |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- A 3-head hero beside a 4-head NPC; the cast reads as inconsistent.
- Chibi form with chibi motion, losing the weight contrast that makes it work.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Every character in the cast has the same head count.
- [ ] Face readable at 64 px tall.
- [ ] Props within 1.3x realistic scale.
- [ ] Animation timing matches full-weight adult motion.

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


