---
name: dream-surreal-mood
description: Dreamlike, surreal, mysterious, mystical, hopeful, and chaotic mood direction for Blender scenes.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: dreamlike, surreal, mysterious, mystical, hopeful, chaotic, uncanny mood
  related-skills: dream-weirdcore-style, lighting, vfx-fx, compositing, camera-cinematography
---

# Dream Surreal Mood

Scale violation, soft light with no single source, and geometry that is almost familiar.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- which familiar thing is wrong, and by how much
- lighting without a locatable source
- material softness that reads as memory

## Direction

- **One violation at a time.** Surreal reads when a single rule breaks: a door that is 4 m tall, a room with no corners. Two violations become noise; five become a cartoon.
- **Sourceless light.** Soft, near-ambient, low directional contrast, with a gentle gradient the eye cannot attribute. Sharp shadows break the dream.
- **Almost-familiar.** Borrow real proportions and break one: a chair with the right seat height and a 2.4 m back. The familiar part does the work.
- **Haze and falloff.** 60-70% of frame in atmospheric falloff, low micro-contrast, high macro-contrast.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| directional contrast | <= 2:1 key to fill |
| shadow softness | 20-40 deg penumbra |
| scale violation | 1 per scene, 1.6-3x |
| haze | 60-70% frame coverage |
| palette | 2-3 hues, mid value |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Three scale violations at once, collapsing into cartoon.
- Hard shadow from a locatable source, which breaks the dream logic.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Exactly one scale violation per scene.
- [ ] No hard-edged shadow anywhere.
- [ ] Familiar proportion preserved on the non-violated axis.
- [ ] Value histogram sits in the mid band.

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


