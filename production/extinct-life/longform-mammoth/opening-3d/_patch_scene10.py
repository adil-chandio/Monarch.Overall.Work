#!/usr/bin/env python3
"""Pass 10: guarantee fur coverage, and make the coat read as wool, not popcorn.

Why the bald patches kept coming back:
  The burial test was an APPROXIMATION (analytic ellipsoids and capsules) of the
  real hide meshes. Whenever the approximation was a little too large - the neck
  capsule swallowed the back of the skull, the shoulder sphere swallowed the
  chest - it rejected samples that were actually on the VISIBLE surface. Every
  rejection was a bald patch, and the patches moved with every tweak.

  The rejection only ever saved instances; it was never needed for correctness.
  So it is removed. Fur is now placed on EVERY hide surface, area-weighted.
  Buried fur is simply hidden by the depth test, and a bald patch is impossible.

Also in this pass:
  * Tufts are now aligned to the surface normal with only a small random tilt.
    Free-rotating blobs read as popcorn; aligned tufts read as a fleece.
  * The skull domes join the fur surface, and the ears are smaller and tucked in,
    so the head stops looking like an elephant.
  * Instance counts are sized for the new scheme.
"""
from pathlib import Path

SCENE = Path(__file__).with_name("scene.mjs")
s = SCENE.read_text()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n}, found {s.count(old)}: {old[:90]!r}"
    s = s.replace(old, new)


# ------------------------------------------------------- drop the burial rejection
sub(
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
    const cand = drawPoint(tables[pi]);
    let buried = false;
    for (let k = 0; k < parts.length; k++) {
      if (k === pi) continue;
      if (parts[k].test && parts[k].test(cand.p)) { buried = true; break; }
    }
    if (buried) continue;
    out.push({ p: cand.p, n: cand.n, part: parts[pi] });
  }
  console.log('[fur] sampled', out.length, 'of', count, 'visible points in', guard, 'draws');
  return out;
}""",
    """// Place fur on every hide surface, weighted by surface area.
//
// Deliberately NO burial rejection. An analytic "is this point inside another
// volume" test can only ever approximate the real meshes; every false rejection
// was a bald patch in the coat. Buried fur is hidden by the depth test anyway,
// so sampling everything guarantees complete coverage.
function sampleVisible(parts, count) {
  const tables = parts.map((p) => buildTriTable(p.geo));
  const cumArea = new Float64Array(parts.length);
  let areaSum = 0;
  for (let k = 0; k < parts.length; k++) { areaSum += tables[k].total; cumArea[k] = areaSum; }
  const out = [];
  for (let k = 0; k < count; k++) {
    const pick = R() * areaSum;
    let pi = 0;
    while (pi < parts.length - 1 && cumArea[pi] < pick) pi++;
    out.push({ p: drawPoint(tables[pi]).p, n: drawPoint(tables[pi]).n, part: parts[pi] });
  }
  console.log('[fur] placed', out.length, 'tufts over', parts.length, 'hide surfaces');
  return out;
}""",
)

# drawPoint is now called twice per sample; make it return both fields in one go.
sub(
    """    out.push({ p: drawPoint(tables[pi]).p, n: drawPoint(tables[pi]).n, part: parts[pi] });""",
    """    const d = drawPoint(tables[pi]);
    out.push({ p: d.p, n: d.n, part: parts[pi] });""",
)

# ------------------------------------------------------- skull dome joins the coat
sub(
    """  for (const s of [-1, 1]) {
    const dome = new T.Mesh(new T.SphereGeometry(1, 26, 20), hideMat);
    dome.scale.set(0.38, 0.34, 0.44); dome.position.set(s * 0.30, 3.20, 2.06); g.add(dome);
    const ear = new T.Mesh(new T.SphereGeometry(1, 24, 18), hideMat);
    ear.scale.set(0.36, 0.10, 0.26); ear.position.set(s * 0.66, 2.86, 1.86); ear.rotation.z = s * 0.30; g.add(ear);""",
    """  const domeGeos = [];
  for (const s of [-1, 1]) {
    const domeGeo = new T.SphereGeometry(1, 26, 20);
    domeGeo.scale(0.34, 0.30, 0.40);
    domeGeo.translate(s * 0.28, 3.16, 2.06);
    g.add(new T.Mesh(domeGeo, hideMat));
    domeGeos.push(domeGeo);
    const ear = new T.Mesh(new T.SphereGeometry(1, 24, 18), hideMat);
    ear.scale.set(0.30, 0.085, 0.22); ear.position.set(s * 0.60, 2.82, 1.88); ear.rotation.z = s * 0.34; g.add(ear);""",
)

sub(
    """    { geo: headGeo, test: ellipsoidTest([0, 2.72, 2.10], [0.84, 0.92, 1.00]) },
  ];""",
    """    { geo: headGeo, test: ellipsoidTest([0, 2.72, 2.10], [0.84, 0.92, 1.00]) },
    ...domeGeos.map((geo) => ({ geo, test: null })),
  ];""",
)

# ------------------------------------------------------- fleece alignment
sub(
    """    const n = s.n.clone().add(new T.Vector3(R() - 0.5, R() - 0.5, R() - 0.5).multiplyScalar(0.38)).normalize();
    dummy.position.copy(s.p).addScaledVector(n, 0.008);
    dummy.quaternion.setFromUnitVectors(up, n);
    dummy.rotateY(R() * Math.PI * 2);
    dummy.rotateX((R() - 0.5) * 1.1);
    dummy.rotateZ((R() - 0.5) * 1.1);
    const sc = 0.020 + R() * 0.014;
    dummy.scale.set(sc, sc * (0.62 + R() * 0.5), sc);""",
    """    // Tufts lie along the surface normal with only a slight tilt, so the coat
    // reads as a fleece rather than a pile of loose spheres.
    const n = s.n.clone().add(new T.Vector3(R() - 0.5, R() - 0.5, R() - 0.5).multiplyScalar(0.16)).normalize();
    dummy.position.copy(s.p).addScaledVector(n, 0.006);
    dummy.quaternion.setFromUnitVectors(up, n);
    dummy.rotateY(R() * Math.PI * 2);
    dummy.rotateX((R() - 0.5) * 0.34);
    dummy.rotateZ((R() - 0.5) * 0.34);
    const sc = 0.021 + R() * 0.013;
    dummy.scale.set(sc, sc * (0.80 + R() * 0.55), sc);""",
)

sub(
    """    const n = s.n.clone().add(new T.Vector3(R() - 0.5, R() - 0.5, R() - 0.5).multiplyScalar(0.45)).normalize();
    dummy.position.copy(s.p).addScaledVector(n, 0.004);
    dummy.quaternion.setFromUnitVectors(up, n);
    dummy.rotateY(R() * Math.PI * 2);
    dummy.rotateX((R() - 0.5) * 1.4);
    dummy.rotateZ((R() - 0.5) * 1.4);
    const sc = 0.011 + R() * 0.010;
    dummy.scale.set(sc, sc * (0.6 + R() * 0.6), sc);""",
    """    const n = s.n.clone().add(new T.Vector3(R() - 0.5, R() - 0.5, R() - 0.5).multiplyScalar(0.20)).normalize();
    dummy.position.copy(s.p).addScaledVector(n, 0.003);
    dummy.quaternion.setFromUnitVectors(up, n);
    dummy.rotateY(R() * Math.PI * 2);
    dummy.rotateX((R() - 0.5) * 0.4);
    dummy.rotateZ((R() - 0.5) * 0.4);
    const sc = 0.012 + R() * 0.010;
    dummy.scale.set(sc, sc * (0.75 + R() * 0.55), sc);""",
)

# ------------------------------------------------------- counts
sub(
    """  const surface = sampleVisible(hideParts, 46000);""",
    """  const surface = sampleVisible(hideParts, 52000);""",
)
sub(
    """  const underSurface = sampleVisible(hideParts, 30000);""",
    """  const underSurface = sampleVisible(hideParts, 34000);""",
)
sub(
    """  const shagSurface = sampleVisible(hideParts, 9000);""",
    """  const shagSurface = sampleVisible(hideParts, 11000);""",
)

SCENE.write_text(s)
print("scene.mjs patched (pass 10)")
