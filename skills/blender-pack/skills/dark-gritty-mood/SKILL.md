---
name: dark-gritty-mood
description: Dark, grim, gritty, rusty, abandoned, decayed, industrial, lonely, and melancholic mood direction for Blender.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: dark, grim, gritty, rusty, abandoned, decayed, industrial, lonely, melancholic, tense, eerie, creepy
  related-skills: horror-style, materials, lighting, set-dressing, environment-artist
---

# Dark Gritty Mood

Low-key lighting, controlled contrast, and surfaces that show use rather than dirt.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- where the key light is and what it refuses to show
- contrast ratio that keeps shadow detail
- wear pattern logic, not noise

## Direction

- **Key discipline.** One dominant source, hard falloff, 70-85% of frame in shadow. A second light exists only to separate silhouette, never to fill.
- **Contrast with a floor.** Keep shadow values above 3% linear. Crushed blacks read as a broken render, not as grit. Lift the toe in the grade rather than raising ambient.
- **Wear logic.** Grime accumulates where hands and tools go: edges, handles, thresholds, drip lines. Uniform noise is texture, not story.
- **Palette.** Desaturated, with one warm accent reserved for the story beat. If everything is warm, nothing is.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| key | 1 source, 70-85% shadow area |
| shadow floor | >= 0.03 linear |
| saturation | 0.25-0.45 |
| accent | 1 warm hue, <= 8% pixel coverage |
| roughness range | 0.45-0.95, split by wear |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Crushed blacks, so the grit reads as a broken render.
- Every hue warm, so the single accent has nothing to contrast against.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Shadow detail present, not crushed, in the darkest frame.
- [ ] One warm accent only; count the hues.
- [ ] Wear confined to edges, handles, thresholds.
- [ ] Silhouette separable from background at all times.

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


