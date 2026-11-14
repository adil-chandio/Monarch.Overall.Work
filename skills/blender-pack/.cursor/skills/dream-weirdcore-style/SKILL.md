---
name: dream-weirdcore-style
description: Dreamcore, weirdcore, and traumacore-inspired art direction for Blender with nostalgic wrongness, liminal nostalgia, and surreal childhood spaces.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: dreamcore, weirdcore, traumacore, dream horror, nostalgic horror, surreal childhood, weirdcore edit
  related-skills: liminal-space-style, dream-surreal-mood, horror-style, compositing, lighting
---

# Dream Weirdcore Style

Familiar places with one wrong rule, lit like a memory, and an emptiness that watches.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- the single rule that is wrong, held consistently
- lighting borrowed from a different memory
- empty space that feels occupied

## Direction

- **One wrong rule.** Doors in a field, a room with no corners, stairs that go nowhere. Hold it for the whole scene; weirdcore fails when the rules keep changing.
- **Memory lighting.** Overexposed, low-contrast, slightly too warm or slightly too cold. The look of a photo taken with a flash in 2004.
- **Occupied emptiness.** The scene is empty but arranged as if someone just left: a chair pulled out, a tap running, a light on.
- **Low-fi texture.** Slight softness, mild chromatic fringing, JPEG-ish compression on hard edges. Perfection breaks the found-image feel.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| exposure | +1.0 to +1.8 EV, blown sky |
| contrast | 1.5:1, low |
| wrong rule | 1, held throughout |
| texture | soft, 1-2 px fringing |
| emptiness | 0 people, arranged for people |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- The wrong rule changing between scenes.
- Razor-sharp edges, destroying the found-image feel.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] One wrong rule, consistent across the scene.
- [ ] Lighting reads as flash photography, not as daylight.
- [ ] No people present, but human arrangement visible.
- [ ] Texture softened; no razor-sharp edges.

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


