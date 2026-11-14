---
name: analog-found-footage-horror
description: Analog, VHS, CRT, and found-footage horror aesthetics for Blender shots including camera imperfections and documentary framing.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: analog horror, found footage, VHS horror, CRT horror, tape horror, Mandel effect, lost media
  related-skills: horror-style, psx-horror-style, camera-cinematography, compositing, lighting
---

# Analog Found Footage Horror

VHS and camcorder grammar: tape artefacts, auto-exposure hunting, and a camera that is a character.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- tape artefact vocabulary and their timing
- camcorder auto-behaviour (hunting exposure, focus breathing)
- the camera operator as a diegetic presence

## Direction

- **Tape vocabulary.** Head-switching noise at the frame bottom, chroma bleed, tracking bands, dropouts and timecode. Each has a real cause; use them as events, not as a constant filter.
- **Auto behaviour.** Camcorders hunt: exposure steps, focus breathes, white balance drifts when a practical enters. Static perfection breaks the illusion instantly.
- **Camera as character.** Handheld float, late reactions, the operator's breathing. The camera should always be a half-second behind the event.
- **Light discipline.** One on-camera source, harsh falloff, blown highlights. Night footage is 90% black with a hot centre.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| artefact | value |
| --- | --- |
| head switching | bottom 8-16 px |
| chroma bleed | 2-4 px horizontal |
| tracking band | 1 per 20-40 s |
| exposure step | +/-0.7 EV hunting |
| resolution | 480x360 effective, upscaled |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Tape artefacts as a constant overlay instead of events.
- Static perfection: no exposure hunt, no focus breathing.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Tape artefacts appear as events, not a constant overlay.
- [ ] Exposure or focus hunts at least once per 10 s.
- [ ] Camera lags the action by a beat.
- [ ] Highlights blow to white, shadows to black.

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


