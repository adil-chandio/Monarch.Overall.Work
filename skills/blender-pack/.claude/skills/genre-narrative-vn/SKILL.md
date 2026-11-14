---
name: genre-narrative-vn
description: Art direction for visual novel, interactive movie, walking simulator, and story-driven presentation spaces in Blender.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: visual novel, interactive movie, walking simulator, narrative game, story scene, VN background
  related-skills: camera-cinematography, lighting, set-dressing, archviz, compositing
---

# Genre Narrative Vn

Staging for dialogue: camera-safe blocking, expression range, and backgrounds that hold a text box.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- where the text box goes and what must stay visible behind it
- expression range at 1.5 m from the camera
- background contrast that never fights the UI

## Direction

- **Text-safe framing.** Reserve the lower 30% and one side for UI. Character framing that pushes the face into the text zone is unusable regardless of quality.
- **Expression at 1.5 m.** Eyes, brows and mouth carry everything. Model at the distance the game actually shows; 4k skin detail behind a text box is wasted budget.
- **Background value.** Keep backgrounds 1-1.5 stops darker than the character's lit face, and low-contrast in the UI zone. High-contrast background detail behind text is the most common VN readability failure.
- **Pose language.** Static silhouettes for listening, one clear break for speaking. Two characters sharing a silhouette class blur together at any resolution.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | target |
| --- | --- |
| character framing | mid-thigh up, face above 45% line |
| text zone | lower 30% + left/right bias |
| background value | character +1 to +1.5 stops |
| expression range | >= 6 poses |
| texel density | 1024 px/m face |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Character framed into the text zone; the face is always half-covered.
- Background contrast fighting the dialogue box.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Face never enters the UI zone in any pose.
- [ ] Six expressions distinguishable at 1.5 m.
- [ ] Background stays below the contrast threshold in the text zone.
- [ ] Two characters never share a silhouette class.

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


