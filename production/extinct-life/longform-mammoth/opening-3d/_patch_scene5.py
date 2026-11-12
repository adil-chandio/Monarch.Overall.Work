#!/usr/bin/env python3
"""Pass 5: rebuild the coat as real fleece + kill the InstancedMesh overflow.

Root causes found this pass:
  * coat.count (63000) exceeded the InstancedMesh capacity (62000), so the GPU read
    past the instance-matrix buffer and drew garbage matrices -> the rainbow shard
    artefacts on the shoulder and the leg.
  * Fur was sampled from ANALYTIC ellipsoids while the visible hide is a LUMPY,
    scaled, rotated mesh. The two never agree, so the coat floated, sank and left
    bare smooth "shell plates" showing through.
  Fix: bake every hide volume's transform into its geometry, merge those exact
    geometries into one fur surface, and sample tufts area-weighted from the real
    triangles. Tufts now sit exactly on the hide with no bald patches.

Also: the coat and shag shared one material, so fading the shag during the
"lost insulation" beat faded the whole animal. They now use separate materials.
"""
from pathlib import Path

SCENE = Path(__file__).with_name("scene.mjs")
s = SCENE.read_text()

START = "function buildMammoth() {"
END = "/* ---------- world: floe, sea, snow, breath ---------- */"
i = s.index(START)
j = s.index(END)

NEW = r'''function buildMammoth() {
  const g = new T.Group();
  const hideMat = new T.MeshStandardMaterial({ color: 0x8a6647, roughness: 0.94, metalness: 0.0 });
  const furMat = new T.MeshStandardMaterial({ color: 0x9a7550, roughness: 0.92, metalness: 0.0 });
  const shagMat = new T.MeshStandardMaterial({ color: 0x8e6b47, roughness: 0.95, metalness: 0.0, transparent: true });
  const tuskMat = new T.MeshStandardMaterial({ color: 0xefe3c6, roughness: 0.28, metalness: 0.04 });
  const eyeMat = new T.MeshStandardMaterial({ color: 0x120c08, roughness: 0.1, metalness: 0.15 });

  // Hide volumes. Each transform is baked into the geometry so the very same
  // triangles can be reused as the fur surface later.
  const bodyGeo = lumpy(new T.SphereGeometry(1, 64, 48), 0.13, 1.0);
  bodyGeo.scale(1.16, 1.06, 2.15); bodyGeo.translate(0, 1.95, -0.15);
  g.add(new T.Mesh(bodyGeo, hideMat));

  const humpGeo = lumpy(new T.SphereGeometry(1, 48, 36), 0.11, 1.0);
  humpGeo.scale(0.88, 0.74, 0.98); humpGeo.translate(0, 2.68, 0.30);
  g.add(new T.Mesh(humpGeo, hideMat));

  const rumpGeo = lumpy(new T.SphereGeometry(1, 40, 30), 0.11, 1.0);
  rumpGeo.scale(0.92, 0.86, 0.92); rumpGeo.translate(0, 2.02, -1.70);
  g.add(new T.Mesh(rumpGeo, hideMat));

  const shoulderGeo = lumpy(new T.SphereGeometry(1, 40, 30), 0.10, 1.0);
  shoulderGeo.scale(1.02, 1.02, 0.95); shoulderGeo.translate(0, 2.34, 0.55);
  g.add(new T.Mesh(shoulderGeo, hideMat));

  const neckGeo = new T.CylinderGeometry(0.66, 0.84, 1.0, 24);
  neckGeo.rotateX(0.34); neckGeo.translate(0, 2.38, 1.32);
  g.add(new T.Mesh(neckGeo, hideMat));

  const headGeo = lumpy(new T.SphereGeometry(1, 48, 36), 0.09, 1.0);
  headGeo.scale(0.84, 0.92, 1.00); headGeo.rotateX(-0.14); headGeo.translate(0, 2.72, 2.10);
  g.add(new T.Mesh(headGeo, hideMat));

  for (const s of [-1, 1]) {
    const dome = new T.Mesh(new T.SphereGeometry(1, 26, 20), hideMat);
    dome.scale.set(0.38, 0.34, 0.44); dome.position.set(s * 0.30, 3.20, 2.06); g.add(dome);
    const ear = new T.Mesh(new T.SphereGeometry(1, 24, 18), hideMat);
    ear.scale.set(0.50, 0.11, 0.32); ear.position.set(s * 0.78, 2.84, 1.78); ear.rotation.z = s * 0.26; g.add(ear);
    const eye = new T.Mesh(new T.SphereGeometry(0.075, 16, 12), eyeMat);
    eye.position.set(s * 0.50, 2.80, 2.62); g.add(eye);
    const glint = new T.Mesh(new T.SphereGeometry(0.022, 10, 8), new T.MeshBasicMaterial({ color: 0xd8ecff }));
    glint.position.set(s * 0.535, 2.835, 2.67); g.add(glint);
  }

  const trunk = new T.Mesh(taperedTube(
    [[0, 2.52, 2.58], [0, 2.02, 2.92], [0.02, 1.34, 2.92], [0.04, 0.74, 2.72], [0.02, 0.46, 2.46]],
    (t) => 0.32 - 0.21 * t, 80, 16), new T.MeshStandardMaterial({ color: 0x6b4f39, roughness: 0.86 }));
  g.add(trunk);
  for (const s of [-1, 1]) {
    const tusk = new T.Mesh(taperedTube(
      [[s * 0.32, 2.12, 2.54], [s * 0.76, 2.04, 3.10], [s * 1.04, 2.22, 3.58], [s * 1.00, 2.54, 3.96]],
      (t) => 0.105 * (1 - t * 0.92), 64, 12), tuskMat);
    g.add(tusk);
  }

  const legGeos = [];
  for (const [x, z, h] of [[-0.60, 1.20, 1.92], [0.60, 1.20, 1.92], [-0.62, -1.25, 1.96], [0.62, -1.25, 1.96]]) {
    const legGeo = new T.CylinderGeometry(0.27, 0.35, h, 20, 1);
    legGeo.translate(x, h / 2 + 0.08, z);
    g.add(new T.Mesh(legGeo, hideMat));
    legGeos.push(legGeo);
    const foot = new T.Mesh(new T.CylinderGeometry(0.34, 0.38, 0.26, 20), hideMat);
    foot.position.set(x, 0.13, z + 0.05); g.add(foot);
  }
  const tail = new T.Mesh(taperedTube(
    [[0, 2.20, -2.18], [0.04, 1.76, -2.52], [0.04, 1.44, -2.68]], (t) => 0.09 - 0.05 * t, 20, 8), hideMat);
  g.add(tail);

  /* ---- fur surface: merge the real hide geometry, then sample its triangles ---- */
  const furSurfaceGeo = mergeFurSurface([
    bodyGeo, humpGeo, rumpGeo, shoulderGeo, neckGeo, headGeo, ...legGeos
  ]);
  const surface = sampleSurface(furSurfaceGeo, 30000);

  const dummy = new T.Object3D();
  const col = new T.Color();
  const up = new T.Vector3(0, 1, 0);

  // Layer A: chunky wool clumps. Rounded low-poly blobs read as fleece; cones read
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
  g.add(coat);

  // Layer B: long guard hairs that break the silhouette against the sky.
  const shagGeo = new T.ConeGeometry(0.012, 0.058, 4, 1, true);
  shagGeo.translate(0, 0.028, 0);
  const shagSurface = sampleSurface(furSurfaceGeo, 9000);
  const shag = new T.InstancedMesh(shagGeo, shagMat, shagSurface.length);
  shagSurface.forEach((s, i) => {
    const n = s.n.clone().add(new T.Vector3(R() - 0.5, R() - 0.5, R() - 0.5).multiplyScalar(0.42)).normalize();
    const dir = n.clone().lerp(new T.Vector3(0, -1, 0), 0.62).normalize();
    dummy.position.copy(s.p).addScaledVector(dir, 0.016);
    dummy.quaternion.setFromUnitVectors(up, dir);
    dummy.rotateY(R() * Math.PI * 2);
    dummy.rotateX((R() - 0.5) * 0.3);
    dummy.scale.set(1, (0.55 + R() * 0.6) * (1 - 0.35 * Math.max(0, n.y)), 1);
    dummy.updateMatrix();
    shag.setMatrixAt(i, dummy.matrix);
    col.setHSL(0.068 + R() * 0.026, 0.24 + R() * 0.14, 0.22 + R() * 0.15);
    shag.setColorAt(i, col);
  });
  shag.count = shagSurface.length;
  g.add(shag);

  g.userData.trunkTip = new T.Vector3(0.02, 0.46, 2.46);
  g.userData.shag = shag;
  g.userData.coat = coat;
  return g;
}

'''

s = s[:i] + NEW + s[j:]

# --- helpers that the new builder needs, inserted before buildMammoth -------------
HELPERS = r'''// Merge several hide geometries into one indexed buffer for fur sampling.
function mergeFurSurface(parts) {
  const pos = [], nor = [], idx = [];
  let off = 0;
  for (const g of parts) {
    const pa = g.attributes.position.array, na = g.attributes.normal.array;
    for (let i = 0; i < pa.length; i++) pos.push(pa[i]);
    for (let i = 0; i < na.length; i++) nor.push(na[i]);
    const gi = g.index.array;
    for (let i = 0; i < gi.length; i++) idx.push(gi[i] + off);
    off += g.attributes.position.count;
  }
  const geo = new T.BufferGeometry();
  geo.setAttribute('position', new T.Float32BufferAttribute(pos, 3));
  geo.setAttribute('normal', new T.Float32BufferAttribute(nor, 3));
  geo.setIndex(idx);
  return geo;
}

// Area-weighted triangle sampling: returns {p, n} pairs sitting exactly on the mesh.
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
}

'''
s = s.replace(START, HELPERS + START, 1)

# The shag now owns its material, so fading it no longer fades the whole animal.
old_shag = """    const shag = mammoth.userData.shag;
    shag.material.transparent = true;
    shag.material.opacity = 1 - lift * 0.92;"""
new_shag = """    const shag = mammoth.userData.shag;
    shag.material.opacity = 1 - lift * 0.92;"""
assert s.count(old_shag) == 1
s = s.replace(old_shag, new_shag)

SCENE.write_text(s)
print("scene.mjs patched (pass 5)")
