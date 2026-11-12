#!/usr/bin/env python3
"""Pass 8: close the bald patches in the coat.

Why the smooth grey plates survived pass 6/7:
  The burial tests used INFLATED radii (body 1.20 vs the real 1.16). The shoulder
  sphere sits entirely inside the body, so:
    - every shoulder-surface sample fell inside the inflated body test and was
      rejected, and
    - the body samples in the shoulder region fell inside the inflated shoulder
      test and were rejected too.
  Both sides rejected, and a hole in the coat appeared exactly where the smooth
  hide showed through.

  Fix: test against the REAL radii with a 0.99 threshold, so a point only counts
  as buried when it is genuinely inside another volume. Overlapping volumes then
  behave like a union: the outer surface wins, the inner one is buried, and no
  mutual hole can form.

Also:
  * Lumpy displacement was large enough to push the body through the shoulder
    sphere and confuse the analytic test. Reduced, so the volumes stay clean and
    the fleece provides the texture instead.
  * A dense fine underfur layer was added so the coat has no gaps at any distance.
  * The feet are now furred too; they were bare cylinders.
"""
from pathlib import Path

SCENE = Path(__file__).with_name("scene.mjs")
s = SCENE.read_text()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n}, found {s.count(old)}: {old[:90]!r}"
    s = s.replace(old, new)


# --------------------------------------------------------------- exact burial tests
sub(
    """function ellipsoidTest(c, r) {
  return (p) => {
    const dx = (p.x - c[0]) / r[0], dy = (p.y - c[1]) / r[1], dz = (p.z - c[2]) / r[2];
    return dx * dx + dy * dy + dz * dz < 1.0;
  };
}
function capsuleTest(a, b, r) {
  const abx = b[0] - a[0], aby = b[1] - a[1], abz = b[2] - a[2];
  const l2 = abx * abx + aby * aby + abz * abz;
  return (p) => {
    const px = p.x - a[0], py = p.y - a[1], pz = p.z - a[2];
    let t = (px * abx + py * aby + pz * abz) / l2;
    t = t < 0 ? 0 : t > 1 ? 1 : t;
    const dx = px - abx * t, dy = py - aby * t, dz = pz - abz * t;
    return dx * dx + dy * dy + dz * dz < r * r;
  };
}""",
    """// A point counts as buried only when it is genuinely inside another volume.
// The 0.99 threshold keeps coincident surfaces from rejecting each other, which
// is what opened bald patches in the previous passes.
const BURIED = 0.99;
function ellipsoidTest(c, r) {
  return (p) => {
    const dx = (p.x - c[0]) / r[0], dy = (p.y - c[1]) / r[1], dz = (p.z - c[2]) / r[2];
    return dx * dx + dy * dy + dz * dz < BURIED * BURIED;
  };
}
function capsuleTest(a, b, r) {
  const abx = b[0] - a[0], aby = b[1] - a[1], abz = b[2] - a[2];
  const l2 = abx * abx + aby * aby + abz * abz;
  const rr = r * r * BURIED * BURIED;
  return (p) => {
    const px = p.x - a[0], py = p.y - a[1], pz = p.z - a[2];
    let t = (px * abx + py * aby + pz * abz) / l2;
    t = t < 0 ? 0 : t > 1 ? 1 : t;
    const dx = px - abx * t, dy = py - aby * t, dz = pz - abz * t;
    return dx * dx + dy * dy + dz * dz < rr;
  };
}""",
)

# --------------------------------------------------------------- real radii
sub(
    """  const hideParts = [
    { geo: bodyGeo, test: ellipsoidTest([0, 1.95, -0.15], [1.20, 1.10, 2.19]) },
    { geo: humpGeo, test: ellipsoidTest([0, 2.68, 0.30], [0.92, 0.78, 1.02]) },
    { geo: rumpGeo, test: ellipsoidTest([0, 2.02, -1.70], [0.96, 0.90, 0.96]) },
    { geo: shoulderGeo, test: ellipsoidTest([0, 2.34, 0.55], [1.06, 1.06, 0.99]) },
    { geo: neckGeo, test: capsuleTest([0, 1.91, 1.15], [0, 2.85, 1.49], 0.80) },
    { geo: headGeo, test: ellipsoidTest([0, 2.72, 2.10], [0.88, 0.96, 1.04]) },
  ];""",
    """  const hideParts = [
    { geo: bodyGeo, test: ellipsoidTest([0, 1.95, -0.15], [1.16, 1.06, 2.15]) },
    { geo: humpGeo, test: ellipsoidTest([0, 2.68, 0.30], [0.88, 0.74, 0.98]) },
    { geo: rumpGeo, test: ellipsoidTest([0, 2.02, -1.70], [0.92, 0.86, 0.92]) },
    { geo: shoulderGeo, test: ellipsoidTest([0, 2.34, 0.55], [1.02, 1.02, 0.95]) },
    { geo: neckGeo, test: capsuleTest([0, 1.91, 1.15], [0, 2.85, 1.49], 0.76) },
    { geo: headGeo, test: ellipsoidTest([0, 2.72, 2.10], [0.84, 0.92, 1.00]) },
  ];""",
)

# --------------------------------------------------------------- gentler displacement
sub(
    """  const bodyGeo = lumpy(new T.SphereGeometry(1, 64, 48), 0.13, 1.0);""",
    """  const bodyGeo = lumpy(new T.SphereGeometry(1, 64, 48), 0.055, 1.0);""",
)
sub(
    """  const humpGeo = lumpy(new T.SphereGeometry(1, 48, 36), 0.11, 1.0);""",
    """  const humpGeo = lumpy(new T.SphereGeometry(1, 48, 36), 0.045, 1.0);""",
)
sub(
    """  const rumpGeo = lumpy(new T.SphereGeometry(1, 40, 30), 0.11, 1.0);""",
    """  const rumpGeo = lumpy(new T.SphereGeometry(1, 40, 30), 0.045, 1.0);""",
)
sub(
    """  const shoulderGeo = lumpy(new T.SphereGeometry(1, 40, 30), 0.10, 1.0);""",
    """  const shoulderGeo = lumpy(new T.SphereGeometry(1, 40, 30), 0.04, 1.0);""",
)
sub(
    """  const headGeo = lumpy(new T.SphereGeometry(1, 48, 36), 0.09, 1.0);""",
    """  const headGeo = lumpy(new T.SphereGeometry(1, 48, 36), 0.04, 1.0);""",
)

# --------------------------------------------------------------- feet get fur
sub(
    """    const foot = new T.Mesh(new T.CylinderGeometry(0.34, 0.38, 0.26, 20), hideMat);
    foot.position.set(x, 0.13, z + 0.05); g.add(foot);""",
    """    const footGeo = new T.CylinderGeometry(0.34, 0.38, 0.26, 20);
    footGeo.translate(x, 0.13, z + 0.05);
    g.add(new T.Mesh(footGeo, hideMat));
    legGeos.push({ geo: footGeo, x, z, h: 0.26, foot: true });""",
)

sub(
    """  for (const lg of legGeos) {
    hideParts.push({ geo: lg.geo, test: capsuleTest([lg.x, 0.05, lg.z], [lg.x, lg.h + 0.08, lg.z], 0.37) });
  }""",
    """  for (const lg of legGeos) {
    const y0 = lg.foot ? 0.0 : 0.05, y1 = lg.foot ? 0.26 : lg.h + 0.08;
    const r = lg.foot ? 0.40 : 0.37;
    hideParts.push({ geo: lg.geo, test: capsuleTest([lg.x, y0, lg.z + (lg.foot ? 0.05 : 0)], [lg.x, y1, lg.z + (lg.foot ? 0.05 : 0)], r) });
  }""",
)

# --------------------------------------------------------------- dense underfur
sub(
    """  coat.count = surface.length;
  g.add(coat);""",
    """  coat.count = surface.length;
  g.add(coat);

  // Layer A2: fine underfur. Small, very dense curls that seal every gap so the
  // smooth hide never shows through the coat at any camera distance.
  const underGeo = new T.IcosahedronGeometry(1, 0);
  const underSurface = sampleVisible(hideParts, 26000);
  const under = new T.InstancedMesh(underGeo, furMat, underSurface.length);
  underSurface.forEach((s, i) => {
    const n = s.n.clone().add(new T.Vector3(R() - 0.5, R() - 0.5, R() - 0.5).multiplyScalar(0.45)).normalize();
    dummy.position.copy(s.p).addScaledVector(n, 0.004);
    dummy.quaternion.setFromUnitVectors(up, n);
    dummy.rotateY(R() * Math.PI * 2);
    dummy.rotateX((R() - 0.5) * 1.4);
    dummy.rotateZ((R() - 0.5) * 1.4);
    const sc = 0.011 + R() * 0.010;
    dummy.scale.set(sc, sc * (0.6 + R() * 0.6), sc);
    dummy.updateMatrix();
    under.setMatrixAt(i, dummy.matrix);
    col.setHSL(0.070 + R() * 0.028, 0.22 + R() * 0.16, 0.22 + R() * 0.20);
    under.setColorAt(i, col);
  });
  under.count = underSurface.length;
  g.add(under);""",
)

# Larger main clumps now that the underfur seals the gaps.
sub(
    """    const sc = 0.019 + R() * 0.014;""",
    """    const sc = 0.024 + R() * 0.016;""",
)

sub(
    """  g.userData.shag = shag;
  g.userData.coat = coat;""",
    """  g.userData.shag = shag;
  g.userData.coat = coat;
  g.userData.under = under;""",
)

SCENE.write_text(s)
print("scene.mjs patched (pass 8)")
