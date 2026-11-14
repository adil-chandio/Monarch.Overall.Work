---
name: historical-worlds
description: Historical and period world art direction for Blender including Western, pirate, samurai/ninja, Viking, ancient Egypt/Greece/Rome, Victorian, modern, and military eras.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: western, pirate, samurai, ninja, Viking, ancient Egypt, ancient Greece, Roman, Victorian, modern, military, Cold War, World War
  related-skills: environment-artist, prop-artist, character-artist, materials, set-dressing
---

# Historical Worlds

Period-correct materials, construction methods and wear for a named place and decade.

## Read this before you touch the scene

An art-direction skill earns its place by changing decisions, not by listing
adjectives. This one exists to settle these questions before modelling starts:

- construction method before surface detail
- material availability for the period and place
- wear that matches the period's tools

## Direction

- **Name the period and place.** 'Medieval' is not a brief; 'Norman England, 1180' is. Construction, materials and tools all follow from the answer.
- **Construction before ornament.** A timber-frame building has a structural logic: posts, braces, infill. Get the frame right and the ornament is a detail; get it wrong and no amount of carving saves it.
- **Material availability.** No anachronisms: plate glass in 1300, machine-sawn timber in 1600, aniline dyes before 1856. Each error is a visible, checkable failure.
- **Period wear.** Hand-tool marks (adze, chisel, saw pit), uneven dimensions, repairs in a different material. Machine-perfect surfaces read as modern regardless of shape.

## Numbers

Defaults that hold up in production. Deviate deliberately, not by accident.

| element | check |
| --- | --- |
| timber | hand-hewn, uneven section |
| masonry | coursed, mortar 10-20 mm |
| glazing | leaded before 1600, plate after 1700 |
| fasteners | wooden peg, then wrought nail |
| texel density | 512 px/m hero surface |

## Failure modes

The specific ways this direction gets lost. If any of these are true, the skill was
read and not applied.

- Anachronistic materials: plate glass in 1300, machine-sawn timber in 1600.
- Machine-perfect dimensions on a hand-made object.

## Checklist

Run this against the finished scene, not against the intent.

- [ ] Every material is available in the stated period and place.
- [ ] Construction logic survives a structural read.
- [ ] Tool marks match the period's tools.
- [ ] No machine-perfect dimension on a hand-made object.

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


