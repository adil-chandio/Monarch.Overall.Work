#!/usr/bin/env python3
"""Pass 4: kill the sea specular column, rebuild the coat as real fleece, light the animal.

Root causes found this pass:
  * updateWorld() set sea.material.roughness = 0.18 every frame, silently undoing the
    pass-2/3 roughness work -> the low sun smeared into a hard vertical glare column
    on the water. The per-frame line now drives roughness from a single constant.
  * The coat/shag cones were long, sparse and near-black -> the animal read as a
    porcupine. Wool now uses many more, much shorter, lighter, downward-lying tufts
    over a lighter hide, plus a soft fuzz shell that breaks the silhouette.
  * The animal was lit almost entirely from behind, so the camera-facing side was
    black. A dedicated wool key/fill from camera-left now shapes the coat.
"""
from pathlib import Path

SCENE = Path(__file__).with_name("scene.mjs")
s = SCENE.read_text()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n} match, found {s.count(old)}: {old[:80]!r}"
    s = s.replace(old, new)


# ---------------------------------------------------------------- 1. sea material
sub(
    """  const mat = new T.MeshStandardMaterial({ color: 0x14334a, roughness: 0.62, metalness: 0.05 });""",
    """  const mat = new T.MeshStandardMaterial({ color: 0x16394f, roughness: 0.88, metalness: 0.0 });""",
)

# The per-frame roughness write was the reason the glare column survived three passes.
sub(
    """  sea.material.roughness = 0.18;""",
    """  sea.material.roughness = 0.88;""",
)

# ---------------------------------------------------------------- 2. lighting rig
sub(
    """scene.add(new T.HemisphereLight(0x8fb9d8, 0x0b1620, 0.42));
// Low sun behind the animal: the silhouette does the storytelling in the wide shot.
const key = new T.DirectionalLight(0xffcf9c, 3.1); key.position.set(9, 3.4, -26); scene.add(key);
const rim = new T.DirectionalLight(0x9fd4ff, 1.9); rim.position.set(-13, 7, -14); scene.add(rim);
const fill = new T.DirectionalLight(0x4f83ad, 0.78); fill.position.set(5, 4, 12); scene.add(fill);
const warm = new T.PointLight(0xffb070, 5, 22, 2); warm.position.set(-2.2, 2.4, 2.2); scene.add(warm);""",
    """scene.add(new T.HemisphereLight(0x9cc4e0, 0x101d28, 0.78));
// Low sun behind the animal: the silhouette does the storytelling in the wide shot.
const key = new T.DirectionalLight(0xffcf9c, 3.1); key.position.set(9, 3.4, -26); scene.add(key);
const rim = new T.DirectionalLight(0x9fd4ff, 1.9); rim.position.set(-13, 7, -14); scene.add(rim);
const fill = new T.DirectionalLight(0x4f83ad, 0.78); fill.position.set(5, 4, 12); scene.add(fill);
const warm = new T.PointLight(0xffb070, 5, 22, 2); warm.position.set(-2.2, 2.4, 2.2); scene.add(warm);
// Wool rig: a soft key from camera-left that rakes across the coat so the fleece
// reads as fleece instead of a black cut-out, plus a cool bounce off the ice.
const woolKey = new T.DirectionalLight(0xffe0bd, 2.35); woolKey.position.set(-9, 5.2, 11); scene.add(woolKey);
const woolFill = new T.DirectionalLight(0x8fb6d8, 0.95); woolFill.position.set(7.5, 1.6, 9); scene.add(woolFill);
const iceBounce = new T.PointLight(0xbcd6ea, 2.4, 14, 2); iceBounce.position.set(0.4, 0.5, 4.2); scene.add(iceBounce);""",
)

# The per-frame key override also fought the rig; keep the sun behind but stable.
sub(
    """  warm.intensity = 6 + Math.sin(t * 1.3) * 0.8;
  key.intensity = 2.1 + Math.sin(t * 0.4) * 0.1;""",
    """  warm.intensity = 5 + Math.sin(t * 1.3) * 0.7;
  key.intensity = 2.6 + Math.sin(t * 0.4) * 0.12;
  // The wool rig leans in as the camera closes on the animal.
  const close = kind === 'shoulder' ? 1 : kind === 'resolve' ? 0.7 : 0.42;
  woolKey.intensity = 2.35 * close;
  woolFill.intensity = 0.95 * close;
  iceBounce.intensity = 2.4 * close;""",
)

# ---------------------------------------------------------------- 3. fleece rebuild
# Hide: lighter, warmer, less specular so the light actually reaches it.
sub(
    """  const hideMat = new T.MeshStandardMaterial({ color: 0x6b4c34, roughness: 1.0, metalness: 0.0 });
  const furMat = new T.MeshStandardMaterial({ color: 0x7a5a3e, roughness: 1.0 });""",
    """  const hideMat = new T.MeshStandardMaterial({ color: 0x8a6647, roughness: 0.94, metalness: 0.0 });
  const furMat = new T.MeshStandardMaterial({ color: 0x9a7550, roughness: 0.92, metalness: 0.0 });""",
)

# Coat: many more, much shorter, much lighter tufts that lie along the body.
sub(
    """  const coatGeo = new T.ConeGeometry(0.026, 0.055, 4, 1, true);
  coatGeo.translate(0, 0.027, 0);
  const coat = new T.InstancedMesh(coatGeo, furMat, 34000);""",
    """  const coatGeo = new T.ConeGeometry(0.030, 0.026, 5, 1, true);
  coatGeo.translate(0, 0.011, 0);
  const coat = new T.InstancedMesh(coatGeo, furMat, 62000);""",
)

sub(
    """  coatSurface.forEach((s, i) => {
    const p = s.p.clone().add(new T.Vector3(R() - 0.5, R() - 0.5, R() - 0.5).multiplyScalar(0.18));
    const n = s.n.clone().add(new T.Vector3(R() - 0.5, R() - 0.5, R() - 0.5).multiplyScalar(0.30)).normalize();
    const dir = n.clone().lerp(down, 0.66).normalize();
    dummy.position.copy(p).addScaledVector(dir, 0.01);
    dummy.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), dir);
    dummy.rotateY(R() * Math.PI * 2);
    dummy.scale.set(0.8 + R() * 0.6, (0.7 + R() * 0.9) * (1 - 0.45 * Math.max(0, n.y)), 0.8 + R() * 0.6);
    dummy.updateMatrix();
    coat.setMatrixAt(i, dummy.matrix);
    col.setHSL(0.070 + R() * 0.024, 0.26 + R() * 0.16, 0.21 + R() * 0.15);
    coat.setColorAt(i, col);
  });""",
    """  coatSurface.forEach((s, i) => {
    const p = s.p.clone().add(new T.Vector3(R() - 0.5, R() - 0.5, R() - 0.5).multiplyScalar(0.16));
    const n = s.n.clone().add(new T.Vector3(R() - 0.5, R() - 0.5, R() - 0.5).multiplyScalar(0.22)).normalize();
    // Tufts point outward only slightly and mostly lie down the flank: wool, not quills.
    const dir = n.clone().lerp(down, 0.80).normalize();
    dummy.position.copy(p).addScaledVector(dir, 0.004);
    dummy.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), dir);
    dummy.rotateY(R() * Math.PI * 2);
    dummy.rotateX((R() - 0.5) * 0.5);
    const sc = 0.75 + R() * 0.55;
    dummy.scale.set(sc, sc * (0.7 + R() * 0.6) * (1 - 0.35 * Math.max(0, n.y)), sc);
    dummy.updateMatrix();
    coat.setMatrixAt(i, dummy.matrix);
    col.setHSL(0.075 + R() * 0.020, 0.30 + R() * 0.14, 0.30 + R() * 0.16);
    coat.setColorAt(i, col);
  });""",
)

# Shag: fewer, thinner, lighter wisps that only break the silhouette.
sub(
    """  const shagGeo = new T.ConeGeometry(0.017, 0.085, 4, 1, true);
  shagGeo.translate(0, 0.042, 0);
  const shag = new T.InstancedMesh(shagGeo, furMat, 12000);""",
    """  const shagGeo = new T.ConeGeometry(0.014, 0.062, 4, 1, true);
  shagGeo.translate(0, 0.030, 0);
  const shag = new T.InstancedMesh(shagGeo, furMat, 7000);""",
)

sub(
    """    const n = s.n.clone().add(new T.Vector3(R() - 0.5, R() - 0.5, R() - 0.5).multiplyScalar(0.45)).normalize();
    const dir = n.clone().lerp(down, 0.86).normalize();
    dummy.position.copy(s.p).addScaledVector(dir, 0.02);
    dummy.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), dir);
    dummy.rotateY(R() * Math.PI * 2);
    dummy.rotateX((R() - 0.5) * 0.35);
    dummy.scale.set(1, (0.55 + R() * 0.55) * (1 - 0.4 * Math.max(0, n.y)) * (s.z < -1.2 ? 0.6 : 1), 1);
    dummy.updateMatrix();
    shag.setMatrixAt(i, dummy.matrix);
    col.setHSL(0.066 + R() * 0.03, 0.22 + R() * 0.16, 0.17 + R() * 0.14);""",
    """    const n = s.n.clone().add(new T.Vector3(R() - 0.5, R() - 0.5, R() - 0.5).multiplyScalar(0.40)).normalize();
    const dir = n.clone().lerp(down, 0.92).normalize();
    dummy.position.copy(s.p).addScaledVector(dir, 0.012);
    dummy.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), dir);
    dummy.rotateY(R() * Math.PI * 2);
    dummy.rotateX((R() - 0.5) * 0.3);
    dummy.scale.set(1, (0.5 + R() * 0.5) * (1 - 0.4 * Math.max(0, n.y)) * (s.z < -1.2 ? 0.6 : 1), 1);
    dummy.updateMatrix();
    shag.setMatrixAt(i, dummy.matrix);
    col.setHSL(0.070 + R() * 0.028, 0.26 + R() * 0.14, 0.24 + R() * 0.15);""",
)

# ---------------------------------------------------------------- 4. camera framing
# Pull the shoulder shot back a touch further and to camera-left so the lit side of
# the coat faces camera.
sub(
    """  'shoulder-wool': { from: [[4.6, 3.35, 7.4], [3.5, 3.05, 5.9]], look: [[0.35, 2.6, 1.5], [0.4, 2.55, 1.7]] },""",
    """  'shoulder-wool': { from: [[4.3, 3.25, 7.2], [3.4, 3.00, 6.2]], look: [[0.30, 2.62, 1.45], [0.34, 2.58, 1.60]] },""",
)

SCENE.write_text(s)
print("scene.mjs patched (pass 4)")
