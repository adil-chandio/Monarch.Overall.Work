#!/usr/bin/env python3
"""Pass 9: weight fur sampling by area, and fur the trunk.

Why the body still showed smooth plates:
  sampleVisible() picked a part UNIFORMLY at random, so the 14 hide parts each
  received ~1/14 of the samples regardless of size. The body (about 30 square
  units of hide) got the same budget as one leg (about 1.5), so the body ended up
  with ~80 curls per square unit - spacing 0.11 - while the legs were packed
  solid. The visible result was a dense carpet on the legs and bare hide on the
  torso.

  Fix: weight the part choice by each part's true triangle area, then sample.

Also in this pass:
  * The trunk was a bare, oversized brown banana and the ear a large detached
    flipper. The trunk is now furred with the rest of the animal, tapered
    properly, and the ear is smaller and closer to the skull.
  * Clump size is slightly smaller now that coverage is guaranteed, so the coat
    reads as wool rather than popcorn.
"""
from pathlib import Path

SCENE = Path(__file__).with_name("scene.mjs")
s = SCENE.read_text()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n}, found {s.count(old)}: {old[:90]!r}"
    s = s.replace(old, new)


# ------------------------------------------------------- area-weighted part choice
sub(
    """// Sample the visible hide only: reject any point that lies inside another volume.
function sampleVisible(parts, count) {
  const tables = parts.map((p) => buildTriTable(p.geo));
  const out = [];
  const maxGuard = count * 40;
  let guard = 0;
  while (out.length < count && guard++ < maxGuard) {
    const pi = Math.floor(R() * parts.length);
    const cand = drawPoint(tables[pi]);""",
    """// Sample the visible hide only: reject any point that lies inside another volume.
// Part choice is weighted by surface area, otherwise every part receives the same
// budget and the large volumes end up bare.
function sampleVisible(parts, count) {
  const tables = parts.map((p) => buildTriTable(p.geo));
  const cumArea = new Float64Array(parts.length);
  let areaSum = 0;
  for (let k = 0; k < parts.length; k++) { areaSum += tables[k].total; cumArea[k] = areaSum; }
  const out = [];
  const maxGuard = count * 40;
  let guard = 0;
  while (out.length < count && guard++ < maxGuard) {
    const pick = R() * areaSum;
    let pi = 0;
    while (pi < parts.length - 1 && cumArea[pi] < pick) pi++;
    const cand = drawPoint(tables[pi]);""",
)

# ------------------------------------------------------- trunk geometry + fur
sub(
    """  const trunk = new T.Mesh(taperedTube(
    [[0, 2.52, 2.58], [0, 2.02, 2.92], [0.02, 1.34, 2.92], [0.04, 0.74, 2.72], [0.02, 0.46, 2.46]],
    (t) => 0.235 - 0.185 * t, 80, 16), new T.MeshStandardMaterial({ color: 0x7d5c42, roughness: 0.84 }));
  g.add(trunk);""",
    """  const trunkGeo = taperedTube(
    [[0, 2.52, 2.58], [0, 2.02, 2.92], [0.02, 1.34, 2.92], [0.04, 0.74, 2.72], [0.02, 0.46, 2.46]],
    (t) => 0.225 - 0.175 * t, 80, 16);
  g.add(new T.Mesh(trunkGeo, new T.MeshStandardMaterial({ color: 0x7d5c42, roughness: 0.84 })));""",
)

sub(
    """    const ear = new T.Mesh(new T.SphereGeometry(1, 24, 18), hideMat);
    ear.scale.set(0.50, 0.11, 0.32); ear.position.set(s * 0.78, 2.84, 1.78); ear.rotation.z = s * 0.26; g.add(ear);""",
    """    const ear = new T.Mesh(new T.SphereGeometry(1, 24, 18), hideMat);
    ear.scale.set(0.36, 0.10, 0.26); ear.position.set(s * 0.66, 2.86, 1.86); ear.rotation.z = s * 0.30; g.add(ear);""",
)

# The trunk joins the fur surface so it gets a coat like the rest of the animal.
sub(
    """  const hideParts = [
    { geo: bodyGeo, test: ellipsoidTest([0, 1.95, -0.15], [1.16, 1.06, 2.15]) },""",
    """  const hideParts = [
    { geo: bodyGeo, test: ellipsoidTest([0, 1.95, -0.15], [1.16, 1.06, 2.15]) },
    { geo: trunkGeo, test: null },""",
)

# --------------------------------------------------------------- clump tuning
sub(
    """  const surface = sampleVisible(hideParts, 34000);""",
    """  const surface = sampleVisible(hideParts, 46000);""",
)

sub(
    """    const sc = 0.024 + R() * 0.016;""",
    """    const sc = 0.020 + R() * 0.014;""",
)

sub(
    """  const underSurface = sampleVisible(hideParts, 26000);""",
    """  const underSurface = sampleVisible(hideParts, 30000);""",
)

SCENE.write_text(s)
print("scene.mjs patched (pass 9)")
