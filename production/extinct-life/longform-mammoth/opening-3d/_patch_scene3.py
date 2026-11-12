"""Third patch pass for scene.mjs, from the second still review.

Fixes:
 1. four-arcs cards ran off both edges of frame and sat high. Shrunk the
    cards, widened the spacing, pulled the camera back, centred the group.
 2. promise shot: the empty-slot frame collided with the PLAUSIBLE column and
    the four plates were oversized. Compact layout, slot scaled down and
    dropped, red string reserved for the witnesses shot.
 3. resolve shot: floe read as a small paper cutout with a hard white glare
    streak on the sea. Camera moved in on the animal; sea made less metallic.
 4. shoulder-wool was cropped so tight the animal stopped reading. Pulled back
    to a three-quarter head-and-shoulder view.
 5. Fur: the shag layer was 11:1 needles. Made it stubbier and rarer, coat
    denser, so the hide reads as wool rather than bristles.
 6. DNA helix rungs were too heavy, reading as a spring. Thinner and fewer,
    and the strand glow raised so it reads cyan.
"""
from pathlib import Path

P = Path(__file__).resolve().parent / 'scene.mjs'
s = P.read_text()


def sub(old, new, tag):
    global s
    assert s.count(old) == 1, f'{tag}: expected 1 match, found {s.count(old)}'
    s = s.replace(old, new)


# ---------------------------------------------------------------- 6. helix rungs
sub(
    """  const rungGeo = new T.CylinderGeometry(0.016, 0.016, 1, 6);
  const rungs = new T.InstancedMesh(rungGeo, mat.clone(), 34);
  const d = new T.Object3D();
  for (let i = 0; i < 34; i++) {
    const t = i / 33, a = t * Math.PI * 2 * turns;""",
    """  const rungGeo = new T.CylinderGeometry(0.0095, 0.0095, 1, 6);
  const rungs = new T.InstancedMesh(rungGeo, mat.clone(), 24);
  const d = new T.Object3D();
  for (let i = 0; i < 24; i++) {
    const t = i / 23, a = t * Math.PI * 2 * turns;""",
    'rungs')

sub(
    "const helix = buildHelix(0.38, 1.8, 2.1, 0x3fd2ff, 1.05);",
    "const helix = buildHelix(0.38, 1.8, 2.1, 0x3fd2ff, 1.7);",
    'helixglow')

# ---------------------------------------------------------------- 5. fur
sub(
    """  const coatGeo = new T.ConeGeometry(0.021, 0.075, 4, 1, true);
  coatGeo.translate(0, 0.037, 0);
  const coat = new T.InstancedMesh(coatGeo, furMat, 26000);
  const coatSurface = [
    ...ellipsoidPoints(1.16, 1.06, 2.15, 13000, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 1.95, -0.15)), n: v.n })),
    ...ellipsoidPoints(0.88, 0.74, 0.98, 5600, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.68, 0.30)), n: v.n })),
    ...ellipsoidPoints(0.92, 0.86, 0.92, 3600, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.02, -1.70)), n: v.n })),
    ...ellipsoidPoints(0.84, 0.92, 1.00, 1100, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.72, 2.10)), n: v.n })),
    ...ellipsoidPoints(1.02, 1.02, 0.95, 2000, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.34, 0.55)), n: v.n }))
  ];""",
    """  const coatGeo = new T.ConeGeometry(0.026, 0.055, 4, 1, true);
  coatGeo.translate(0, 0.027, 0);
  const coat = new T.InstancedMesh(coatGeo, furMat, 34000);
  const coatSurface = [
    ...ellipsoidPoints(1.16, 1.06, 2.15, 17000, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 1.95, -0.15)), n: v.n })),
    ...ellipsoidPoints(0.88, 0.74, 0.98, 7400, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.68, 0.30)), n: v.n })),
    ...ellipsoidPoints(0.92, 0.86, 0.92, 4600, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.02, -1.70)), n: v.n })),
    ...ellipsoidPoints(0.84, 0.92, 1.00, 1400, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.72, 2.10)), n: v.n })),
    ...ellipsoidPoints(1.02, 1.02, 0.95, 2600, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.34, 0.55)), n: v.n }))
  ];""",
    'coatgeo2')

sub(
    """  const shagGeo = new T.ConeGeometry(0.011, 0.115, 4, 1, true);
  shagGeo.translate(0, 0.057, 0);
  const shag = new T.InstancedMesh(shagGeo, furMat, 15000);
  const shagSurface = [
    ...ellipsoidPoints(1.16, 1.06, 2.15, 8500, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 1.95, -0.15)), n: v.n })),
    ...ellipsoidPoints(1.02, 1.02, 0.95, 3200, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.34, 0.55)), n: v.n })),
    ...ellipsoidPoints(0.88, 0.74, 0.98, 3000, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.68, 0.30)), n: v.n }))
  ];""",
    """  const shagGeo = new T.ConeGeometry(0.017, 0.085, 4, 1, true);
  shagGeo.translate(0, 0.042, 0);
  const shag = new T.InstancedMesh(shagGeo, furMat, 12000);
  const shagSurface = [
    ...ellipsoidPoints(1.16, 1.06, 2.15, 6400, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 1.95, -0.15)), n: v.n })),
    ...ellipsoidPoints(1.02, 1.02, 0.95, 2400, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.34, 0.55)), n: v.n })),
    ...ellipsoidPoints(0.88, 0.74, 0.98, 2200, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.68, 0.30)), n: v.n }))
  ];""",
    'shaggeo2')

# ---------------------------------------------------------------- 3. sea
sub(
    """  const mat = new T.MeshStandardMaterial({ color: 0x14334a, roughness: 0.46, metalness: 0.16 });""",
    """  const mat = new T.MeshStandardMaterial({ color: 0x14334a, roughness: 0.62, metalness: 0.05 });""",
    'sea2')

# ---------------------------------------------------------------- 1. arcs layout
sub(
    "const ARC_X = [-4.05, -1.35, 1.35, 4.05];",
    "const ARC_X = [-3.72, -1.24, 1.24, 3.72];",
    'arcx')

sub(
    """  const m = cardMesh(d[0], d[1], d[2], 2.72, 1.58, 118, 44);
  m.userData.home = new T.Vector3(ARC_X[i], 0.26, 0.1);""",
    """  const m = cardMesh(d[0], d[1], d[2], 2.32, 1.35, 100, 38);
  m.userData.home = new T.Vector3(ARC_X[i], 0.34, 0.1);""",
    'arccards')

sub(
    "  'four-arcs': { from: [[0, 0.55, 9.2], [0, 0.5, 8.6]], look: [[0, 0.55, 0], [0, 0.5, 0]] },",
    "  'four-arcs': { from: [[0, 0.62, 10.6], [0, 0.58, 10.0]], look: [[0, 0.62, 0], [0, 0.58, 0]] },",
    'arccam2')

# ---------------------------------------------------------------- 2 + 4. card layout per kind
sub(
    """  strings.visible = kind === 'witnesses' || kind === 'promise';""",
    """  strings.visible = kind === 'witnesses';""",
    'strings')

sub(
    """    const e = ease(local);
    c.position.copy(c.userData.home);
    c.position.z = lerp(-1.0, 0, e);
    c.position.y = c.userData.home.y + lerp(0.7, 0, e);
    c.rotation.y = lerp(-0.9, 0, e) + Math.sin(t * 0.8 + i) * 0.02;
    c.rotation.x = lerp(0.35, 0, e);
    c.scale.setScalar(1);
    c.material.opacity = e;
  });""",
    """    const e = ease(local);
    c.position.copy(c.userData.home);
    c.position.z = lerp(-1.0, 0, e);
    c.position.y = c.userData.home.y + lerp(0.7, 0, e);
    c.rotation.y = lerp(-0.9, 0, e) + Math.sin(t * 0.8 + i) * 0.02;
    c.rotation.x = lerp(0.35, 0, e);
    c.material.opacity = e;
    if (kind === 'promise') {
      // compact row, clear of the three verdict columns below
      c.scale.setScalar(0.72);
      c.position.y = 1.42 + lerp(0.7, 0, e);
      c.position.z = -0.5 + lerp(-1.0, 0, e);
    } else {
      c.scale.setScalar(1);
    }
  });""",
    'cards-promise')

sub(
    """    slot.position.y = kind === 'promise' ? -0.62 : -0.9;
    slot.scale.setScalar(kind === 'empty' ? 1.55 : 1);""",
    """    slot.position.y = kind === 'promise' ? -0.18 : -0.9;
    slot.scale.setScalar(kind === 'empty' ? 1.55 : 0.52);""",
    'slotpromise')

# ---------------------------------------------------------------- 3 + 4. cameras
sub(
    "  'shoulder-wool': { from: [[3.0, 3.05, 5.0], [2.2, 2.85, 4.0]], look: [[0.45, 2.55, 1.95], [0.45, 2.5, 2.05]] },",
    "  'shoulder-wool': { from: [[4.6, 3.35, 7.4], [3.5, 3.05, 5.9]], look: [[0.35, 2.6, 1.5], [0.4, 2.55, 1.7]] },",
    'shouldercam')

sub(
    "  'resolve': { from: [[-2.8, 2.2, 23], [1.3, 1.95, 17]], look: [[-0.5, 2.25, 0], [-0.2, 2.1, 0]] },",
    "  'resolve': { from: [[-3.1, 2.15, 13.5], [1.5, 1.95, 9.6]], look: [[-0.45, 2.3, 0.2], [-0.15, 2.15, 0.4]] },",
    'resolvecam')

P.write_text(s)
print('scene.mjs patched (pass 3)')
