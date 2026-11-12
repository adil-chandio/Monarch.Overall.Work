#!/usr/bin/env python3
"""Pass 6: fleece must actually look like fleece.

Problems seen in the pass-5 stills:
  * The coat clumps were Octahedra at radius 0.030-0.054 -> they read as brown crystal
    shards, not wool. Now icosahedral curls at ~0.020-0.032 with far more of them.
  * Big smooth grey "plates" showed through the coat. Cause: the fur was sampled from
    the MERGED geometry, and the shoulder sphere / hump / neck sit mostly INSIDE the
    body, so ~40% of all samples landed on hidden surfaces and never covered anything.
    Fix: each hide volume is sampled separately and samples that fall inside another
    volume are rejected, so every tuft is spent on visible surface.
  * Snow points used sizeAttenuation, so flakes close to the lens became big soft
    blobs across the frame. Size reduced and the field pushed away from the camera.
  * The trunk was a huge dark hook that dominated the silhouette. Slimmer, lighter.
"""
from pathlib import Path

SCENE = Path(__file__).with_name("scene.mjs")
s = SCENE.read_text()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n}, found {s.count(old)}: {old[:90]!r}"
    s = s.replace(old, new)


# ---------------------------------------------------------------- sampling rework
sub(
    """// Area-weighted triangle sampling: returns {p, n} pairs sitting exactly on the mesh.
function sampleSurface(geo, count) {
  const index = geo.index.array;
  const P = geo.attributes.position.array;
  const N = geo.attributes.normal.array;
  const tri = index.length / 3;
  const cum = new Float64Array(tri);
  let total = 0;
  const a = new T.Vector3(), b = new T.Vector3(), c = new T.Vector3();
  const ab = new T.Vector3(), ac = new T.Vector3(), cr = new T.Vector3();
  for (let t = 0; t < tri; t++) {
    const i0 = index[t * 3] * 3, i1 = index[t * 3 + 1] * 3, i2 = index[t * 3 + 2] * 3;
    a.set(P[i0], P[i0 + 1], P[i0 + 2]); b.set(P[i1], P[i1 + 1], P[i1 + 2]); c.set(P[i2], P[i2 + 1], P[i2 + 2]);
    ab.subVectors(b, a); ac.subVectors(c, a);
    total += cr.crossVectors(ab, ac).length() * 0.5;
    cum[t] = total;
  }
  const out = [];
  for (let k = 0; k < count; k++) {
    const target = R() * total;
    let lo = 0, hi = tri - 1;
    while (lo < hi) { const mid = (lo + hi) >> 1; if (cum[mid] < target) lo = mid + 1; else hi = mid; }
    const t = lo;
    const i0 = index[t * 3] * 3, i1 = index[t * 3 + 1] * 3, i2 = index[t * 3 + 2] * 3;
    let u = R(), v = R();
    if (u + v > 1) { u = 1 - u; v = 1 - v; }
    const w = 1 - u - v;
    out.push({
      p: new T.Vector3(
        P[i0] * w + P[i1] * u + P[i2] * v,
        P[i0 + 1] * w + P[i1 + 1] * u + P[i2 + 1] * v,
        P[i0 + 2] * w + P[i1 + 2] * u + P[i2 + 2] * v),
      n: new T.Vector3(
        N[i0] * w + N[i1] * u + N[i2] * v,
        N[i0 + 1] * w + N[i1 + 1] * u + N[i2 + 1] * v,
        N[i0 + 2] * w + N[i2 + 2] * u + N[i2 + 2] * v).normalize()
    });
  }
  return out;
}""",
    """// Analytic "am I inside this hide volume?" tests. The mammoth is built from
// overlapping ellipsoids and capsules; a fur sample that lands on a buried surface
// is wasted, so every sample is checked against every OTHER volume.
function ellipsoidTest(c, r) {
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
}

// Area-weighted triangle sampling on one geometry.
function sampleGeometry(geo, count) {
  const index = geo.index.array;
  const P = geo.attributes.position.array;
  const N = geo.attributes.normal.array;
  const tri = index.length / 3;
  const cum = new Float64Array(tri);
  let total = 0;
  const a = new T.Vector3(), b = new T.Vector3(), c = new T.Vector3();
  const ab = new T.Vector3(), ac = new T.Vector3(), cr = new T.Vector3();
  for (let t = 0; t < tri; t++) {
    const i0 = index[t * 3] * 3, i1 = index[t * 3 + 1] * 3, i2 = index[t * 3 + 2] * 3;
    a.set(P[i0], P[i0 + 1], P[i0 + 2]); b.set(P[i1], P[i1 + 1], P[i1 + 2]); c.set(P[i2], P[i2 + 1], P[i2 + 2]);
    ab.subVectors(b, a); ac.subVectors(c, a);
    total += cr.crossVectors(ab, ac).length() * 0.5;
    cum[t] = total;
  }
  const out = [];
  for (let k = 0; k < count; k++) {
    const target = R() * total;
    let lo = 0, hi = tri - 1;
    while (lo < hi) { const mid = (lo + hi) >> 1; if (cum[mid] < target) lo = mid + 1; else hi = mid; }
    const t = lo;
    const i0 = index[t * 3] * 3, i1 = index[t * 3 + 1] * 3, i2 = index[t * 3 + 2] * 3;
    let u = R(), v = R();
    if (u + v > 1) { u = 1 - u; v = 1 - v; }
    const w = 1 - u - v;
    out.push({
      p: new T.Vector3(
        P[i0] * w + P[i1] * u + P[i2] * v,
        P[i0 + 1] * w + P[i1 + 1] * u + P[i2 + 1] * v,
        P[i0 + 2] * w + P[i1 + 2] * u + P[i2 + 2] * v),
      n: new T.Vector3(
        N[i0] * w + N[i1] * u + N[i2] * v,
        N[i0 + 1] * w + N[i1 + 1] * u + N[i2 + 1] * v,
        N[i0 + 2] * w + N[i2 + 2] * u + N[i2 + 2] * v).normalize()
    });
  }
  return out;
}

// Sample the visible hide only: reject any point that lies inside another volume.
function sampleVisible(parts, count) {
  const out = [];
  let guard = 0;
  const maxGuard = count * 14;
  while (out.length < count && guard++ < maxGuard) {
    const part = parts[Math.floor(R() * parts.length)];
    const cand = sampleGeometry(part.geo, 1)[0];
    if (!cand) continue;
    let buried = false;
    for (const other of parts) {
      if (other === part) continue;
      if (other.test && other.test(cand.p)) { buried = true; break; }
    }
    if (buried) continue;
    out.push({ p: cand.p, n: cand.n, part });
  }
  return out;
}""",
)

# ---------------------------------------------------------------- fur rebuild
sub(
    """  /* ---- fur surface: merge the real hide geometry, then sample its triangles ---- */
  const furSurfaceGeo = mergeFurSurface([
    bodyGeo, humpGeo, rumpGeo, shoulderGeo, neckGeo, headGeo, ...legGeos
  ]);
  const surface = sampleSurface(furSurfaceGeo, 30000);""",
    """  /* ---- fur surface: sample the VISIBLE hide only ---- */
  const hideParts = [
    { geo: bodyGeo, test: ellipsoidTest([0, 1.95, -0.15], [1.20, 1.10, 2.19]) },
    { geo: humpGeo, test: ellipsoidTest([0, 2.68, 0.30], [0.92, 0.78, 1.02]) },
    { geo: rumpGeo, test: ellipsoidTest([0, 2.02, -1.70], [0.96, 0.90, 0.96]) },
    { geo: shoulderGeo, test: ellipsoidTest([0, 2.34, 0.55], [1.06, 1.06, 0.99]) },
    { geo: neckGeo, test: capsuleTest([0, 2.60, 1.16], [0, 2.16, 1.48], 0.86) },
    { geo: headGeo, test: ellipsoidTest([0, 2.72, 2.10], [0.88, 0.96, 1.04]) },
  ];
  for (const lg of legGeos) {
    const cx = lg.attributes.position.array[0];
    hideParts.push({ geo: lg, test: capsuleTest([cx, 0.05, 0], [cx, 2.05, 0], 0.38) });
  }
  const surface = sampleVisible(hideParts, 34000);""",
)

sub(
    """  // Layer A: chunky wool clumps. Rounded low-poly blobs read as fleece; cones read
  // as quills, which is what made the animal look like a porcupine.
  const clumpGeo = new T.OctahedronGeometry(1, 0);
  const coat = new T.InstancedMesh(clumpGeo, furMat, surface.length);
  surface.forEach((s, i) => {
    const n = s.n.clone().add(new T.Vector3(R() - 0.5, R() - 0.5, R() - 0.5).multiplyScalar(0.34)).normalize();
    dummy.position.copy(s.p).addScaledVector(n, 0.012);
    dummy.quaternion.setFromUnitVectors(up, n);
    dummy.rotateY(R() * Math.PI * 2);
    dummy.rotateX((R() - 0.5) * 0.9);
    const sc = 0.030 + R() * 0.024;
    dummy.scale.set(sc, sc * (0.58 + R() * 0.5), sc);
    dummy.updateMatrix();
    coat.setMatrixAt(i, dummy.matrix);
    col.setHSL(0.072 + R() * 0.024, 0.26 + R() * 0.16, 0.29 + R() * 0.19);
    coat.setColorAt(i, col);
  });
  coat.count = surface.length;
  g.add(coat);""",
    """  // Layer A: dense wool curls. Small, rounded, overlapping icosahedra read as fleece;
  // large faceted solids read as crystal shards, which is what pass 5 produced.
  const clumpGeo = new T.IcosahedronGeometry(1, 0);
  const coat = new T.InstancedMesh(clumpGeo, furMat, surface.length);
  surface.forEach((s, i) => {
    const n = s.n.clone().add(new T.Vector3(R() - 0.5, R() - 0.5, R() - 0.5).multiplyScalar(0.38)).normalize();
    dummy.position.copy(s.p).addScaledVector(n, 0.008);
    dummy.quaternion.setFromUnitVectors(up, n);
    dummy.rotateY(R() * Math.PI * 2);
    dummy.rotateX((R() - 0.5) * 1.1);
    dummy.rotateZ((R() - 0.5) * 1.1);
    const sc = 0.019 + R() * 0.014;
    dummy.scale.set(sc, sc * (0.62 + R() * 0.5), sc);
    dummy.updateMatrix();
    coat.setMatrixAt(i, dummy.matrix);
    col.setHSL(0.072 + R() * 0.026, 0.24 + R() * 0.16, 0.26 + R() * 0.20);
    coat.setColorAt(i, col);
  });
  coat.count = surface.length;
  g.add(coat);""",
)

sub(
    """  const shagSurface = sampleSurface(furSurfaceGeo, 9000);""",
    """  const shagSurface = sampleVisible(hideParts, 9000);""",
)

sub(
    """    const dir = n.clone().lerp(new T.Vector3(0, -1, 0), 0.62).normalize();
    dummy.position.copy(s.p).addScaledVector(dir, 0.016);
    dummy.quaternion.setFromUnitVectors(up, dir);
    dummy.rotateY(R() * Math.PI * 2);
    dummy.rotateX((R() - 0.5) * 0.3);
    dummy.scale.set(1, (0.55 + R() * 0.6) * (1 - 0.35 * Math.max(0, n.y)), 1);""",
    """    const dir = n.clone().lerp(new T.Vector3(0, -1, 0), 0.72).normalize();
    dummy.position.copy(s.p).addScaledVector(dir, 0.012);
    dummy.quaternion.setFromUnitVectors(up, dir);
    dummy.rotateY(R() * Math.PI * 2);
    dummy.rotateX((R() - 0.5) * 0.3);
    dummy.scale.set(1, (0.5 + R() * 0.55) * (1 - 0.35 * Math.max(0, n.y)), 1);""",
)

# ---------------------------------------------------------------- trunk + snow
sub(
    """    (t) => 0.32 - 0.21 * t, 80, 16), new T.MeshStandardMaterial({ color: 0x6b4f39, roughness: 0.86 }));""",
    """    (t) => 0.235 - 0.185 * t, 80, 16), new T.MeshStandardMaterial({ color: 0x7d5c42, roughness: 0.84 }));""",
)

sub(
    """  const mat = new T.PointsMaterial({ size: 0.26, map: DOT_TEX, transparent: true, opacity: 0.42, depthWrite: false, sizeAttenuation: true, color: 0xdceaf5 });""",
    """  const mat = new T.PointsMaterial({ size: 0.115, map: DOT_TEX, transparent: true, opacity: 0.5, depthWrite: false, sizeAttenuation: true, color: 0xdceaf5 });""",
)

sub(
    """function buildSnow(count = 1100) {""",
    """function buildSnow(count = 1600) {""",
)

# Push the snow field away from the near clip so no flake becomes a lens blob.
sub(
    """    pos[i * 3] = (R() - 0.5) * 70; pos[i * 3 + 1] = R() * 13; pos[i * 3 + 2] = (R() - 0.5) * 70;""",
    """    pos[i * 3] = (R() - 0.5) * 90; pos[i * 3 + 1] = R() * 16; pos[i * 3 + 2] = (R() - 0.5) * 90;""",
)

sub(
    """    const y = ((base[i * 3 + 1] - t * (0.5 + s * 0.8)) % 13 + 13) % 13;
    sp.setXYZ(i, base[i * 3] + Math.sin(t * 0.6 + s * 6.2) * 1.6, y, base[i * 3 + 2] + Math.cos(t * 0.45 + s * 5.1) * 1.2);""",
    """    const y = ((base[i * 3 + 1] - t * (0.5 + s * 0.8)) % 16 + 16) % 16;
    sp.setXYZ(i, base[i * 3] + Math.sin(t * 0.6 + s * 6.2) * 1.6, y, base[i * 3 + 2] + Math.cos(t * 0.45 + s * 5.1) * 1.2);""",
)

# ---------------------------------------------------------------- hide colour
# A slightly deeper hide stops the gaps between curls reading as grey plates.
sub(
    """  const hideMat = new T.MeshStandardMaterial({ color: 0x8a6647, roughness: 0.94, metalness: 0.0 });""",
    """  const hideMat = new T.MeshStandardMaterial({ color: 0x6f5138, roughness: 0.96, metalness: 0.0 });""",
)

SCENE.write_text(s)
print("scene.mjs patched (pass 6)")
