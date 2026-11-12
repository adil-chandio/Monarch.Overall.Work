"""Second patch pass for scene.mjs, driven by the still-frame review.

Fixes:
 1. Graph-space cards were MeshStandardMaterial in a scene with no lights in
    graph space -> they rendered as dim grey. Now unlit and full strength.
 2. Fur cones were 23:1 needles -> read as porcupine quills. Shorter, denser,
    lighter, and lying flatter against the body.
 3. The DNA helix washed out to white because base colour and emissive were the
    same bright cyan. Now a dark base with a saturated emissive.
 4. four-arcs was a thin, off-centre, mostly-empty row. Rebuilt as a centred
    evidence timeline: rail, stems, nodes, four large cards, fast stagger.
 5. The sea was metallic enough to throw a hard white glare column. Softened.
 6. island-rise framing now pulls back and up so the floe reads as an island.
 7. Cards get a soft plate behind the type so they read as plates, not floats.
"""
from pathlib import Path

P = Path(__file__).resolve().parent / 'scene.mjs'
s = P.read_text()


def sub(old, new, tag):
    global s
    assert s.count(old) == 1, f'{tag}: expected 1 match, found {s.count(old)}'
    s = s.replace(old, new)


# ---------------------------------------------------------------- 7. card plates
sub(
    """function textPlate(lines, opts = {}) {
  const w = opts.w || 1400, h = opts.h || 460;
  const main = opts.main || 'Anton', sub = opts.sub || 'Manrope';
  return canvasTex(w, h, (g) => {
    g.clearRect(0, 0, w, h);
    const accent = opts.accent || '#e9dcc4';""",
    """function textPlate(lines, opts = {}) {
  const w = opts.w || 1400, h = opts.h || 460;
  const main = opts.main || 'Anton', sub = opts.sub || 'Manrope';
  return canvasTex(w, h, (g) => {
    g.clearRect(0, 0, w, h);
    if (opts.plate) {
      g.fillStyle = 'rgba(9,20,31,0.72)';
      g.beginPath();
      g.roundRect(6, 6, w - 12, h - 12, 22);
      g.fill();
      g.strokeStyle = 'rgba(150,200,230,0.22)';
      g.lineWidth = 3;
      g.stroke();
    }
    const accent = opts.accent || '#e9dcc4';""",
    'plate')

# ---------------------------------------------------------------- 1 + 7. cards
sub(
    """function cardMesh(title, sub, accent, w = 2.5, h = 1.45, titleSize = 132, subSize = 52) {
  const tex = textPlate([title, sub], { w: 1000, h: 580, titleSize, subSize, accent, center: true, color: '#f4efe4' });
  const mat = new T.MeshStandardMaterial({
    map: tex, transparent: true, roughness: 0.5, metalness: 0.05,
    emissive: 0xffffff, emissiveMap: tex, emissiveIntensity: 0.5, side: T.DoubleSide
  });
  const mesh = new T.Mesh(new T.PlaneGeometry(w, h), mat);
  return mesh;
}""",
    """function cardMesh(title, sub, accent, w = 2.5, h = 1.45, titleSize = 132, subSize = 52, plate = true) {
  const tex = textPlate([title, sub], { w: 1000, h: 580, titleSize, subSize, accent, center: true, color: '#f6f1e6', plate });
  // graph space carries no lights, so these plates are unlit on purpose
  const mat = new T.MeshBasicMaterial({ map: tex, transparent: true, side: T.DoubleSide });
  const mesh = new T.Mesh(new T.PlaneGeometry(w, h), mat);
  return mesh;
}""",
    'cardMesh')

# ---------------------------------------------------------------- 3. helix colour
sub(
    """  const mat = new T.MeshStandardMaterial({
    color, emissive: color, emissiveIntensity: emissive, roughness: 0.3, metalness: 0.1,
    transparent: true, opacity: 1
  });""",
    """  const mat = new T.MeshStandardMaterial({
    color: 0x0c2f49, emissive: color, emissiveIntensity: emissive, roughness: 0.35, metalness: 0.05,
    transparent: true, opacity: 1
  });""",
    'helixmat')

# ---------------------------------------------------------------- 2. fur
sub(
    """  const coatGeo = new T.ConeGeometry(0.015, 0.15, 4, 1, true);
  coatGeo.translate(0, 0.075, 0);""",
    """  const coatGeo = new T.ConeGeometry(0.021, 0.075, 4, 1, true);
  coatGeo.translate(0, 0.037, 0);""",
    'coatgeo')

sub(
    """  const shagGeo = new T.ConeGeometry(0.006, 0.20, 4, 1, true);
  shagGeo.translate(0, 0.10, 0);""",
    """  const shagGeo = new T.ConeGeometry(0.011, 0.115, 4, 1, true);
  shagGeo.translate(0, 0.057, 0);""",
    'shaggeo')

sub(
    """    const dir = n.clone().lerp(down, 0.5).normalize();
    dummy.position.copy(p).addScaledVector(dir, 0.01);""",
    """    const dir = n.clone().lerp(down, 0.66).normalize();
    dummy.position.copy(p).addScaledVector(dir, 0.01);""",
    'coatdir')

sub(
    """    col.setHSL(0.072 + R() * 0.022, 0.30 + R() * 0.18, 0.17 + R() * 0.14);
    coat.setColorAt(i, col);""",
    """    col.setHSL(0.070 + R() * 0.024, 0.26 + R() * 0.16, 0.21 + R() * 0.15);
    coat.setColorAt(i, col);""",
    'coatcol')

sub(
    """    const dir = n.clone().lerp(down, 0.78).normalize();
    dummy.position.copy(s.p).addScaledVector(dir, 0.02);""",
    """    const dir = n.clone().lerp(down, 0.86).normalize();
    dummy.position.copy(s.p).addScaledVector(dir, 0.02);""",
    'shagdir')

sub(
    """    dummy.scale.set(1, (0.6 + R() * 0.8) * (1 - 0.4 * Math.max(0, n.y)) * (s.z < -1.2 ? 0.6 : 1), 1);""",
    """    dummy.scale.set(1, (0.55 + R() * 0.55) * (1 - 0.4 * Math.max(0, n.y)) * (s.z < -1.2 ? 0.6 : 1), 1);""",
    'shagscale')

sub(
    """    col.setHSL(0.068 + R() * 0.03, 0.26 + R() * 0.18, 0.14 + R() * 0.16);
    shag.setColorAt(i, col);""",
    """    col.setHSL(0.066 + R() * 0.03, 0.22 + R() * 0.16, 0.17 + R() * 0.14);
    shag.setColorAt(i, col);""",
    'shagcol')

# ---------------------------------------------------------------- 5. sea glare
sub(
    """  const mat = new T.MeshStandardMaterial({ color: 0x17374d, roughness: 0.26, metalness: 0.42 });""",
    """  const mat = new T.MeshStandardMaterial({ color: 0x14334a, roughness: 0.46, metalness: 0.16 });""",
    'sea')

# ---------------------------------------------------------------- 4. four arcs rebuild
sub(
    """// four arcs: four lines of evidence on one timeline, revealed in order
const arcRail = new T.Mesh(new T.BoxGeometry(9.6, 0.045, 0.045), new T.MeshBasicMaterial({ color: 0x8fd6ff, transparent: true, opacity: 0.55 }));
arcRail.position.set(-4.8, 0.86, -0.5);
arcRail.visible = false;
graph.add(arcRail);
const arcData = [
  ['2017', 'MELTDOWN', '#ff8f7a'],
  ['2019', 'STABLE, THEN ICE', '#9fe8c6'],
  ['3,600 BP', 'HUMANS TOO LATE', '#ffb27a'],
  ['2024', 'RECOVERED', '#8fd6ff'],
];
const arcCards = arcData.map((d, i) => {
  const m = cardMesh(d[0], d[1], d[2], 2.4, 1.39, 104, 42);
  m.userData.home = new T.Vector3(-3.75 + i * 2.5, -0.16, 0.1);
  m.userData.delay = i * 0.13;
  m.visible = false;
  graph.add(m);
  return m;
});
const arcNodes = arcData.map((d, i) => {
  const n = new T.Mesh(new T.SphereGeometry(0.085, 14, 10), new T.MeshBasicMaterial({ color: d[2] }));
  n.position.set(-3.75 + i * 2.5, 0.86, -0.5);
  n.visible = false;
  graph.add(n);
  return n;
});""",
    """// four arcs: the four lines of evidence, hung on one timeline
const ARC_X = [-4.05, -1.35, 1.35, 4.05];
const ARC_RAIL_Y = 1.28;
const arcRail = new T.Mesh(new T.BoxGeometry(9.5, 0.05, 0.05), new T.MeshBasicMaterial({ color: 0x8fd6ff, transparent: true, opacity: 0.6 }));
arcRail.position.set(-4.75, ARC_RAIL_Y, -0.5);
arcRail.visible = false;
graph.add(arcRail);
const arcData = [
  ['2017', 'MELTDOWN', '#ff8f7a'],
  ['2019', 'STABLE, THEN ICE', '#9fe8c6'],
  ['3,600 BP', 'HUMANS TOO LATE', '#ffb27a'],
  ['2024', 'RECOVERED', '#8fd6ff'],
];
const arcCards = arcData.map((d, i) => {
  const m = cardMesh(d[0], d[1], d[2], 2.72, 1.58, 118, 44);
  m.userData.home = new T.Vector3(ARC_X[i], 0.26, 0.1);
  m.userData.delay = i * 0.1;
  m.visible = false;
  graph.add(m);
  return m;
});
const arcNodes = arcData.map((d, i) => {
  const n = new T.Mesh(new T.SphereGeometry(0.1, 16, 12), new T.MeshBasicMaterial({ color: d[2] }));
  n.position.set(ARC_X[i], ARC_RAIL_Y, -0.5);
  n.visible = false;
  graph.add(n);
  return n;
});
const arcStems = arcData.map((d, i) => {
  const st = new T.Mesh(new T.BoxGeometry(0.035, 1.0, 0.035), new T.MeshBasicMaterial({ color: d[2], transparent: true, opacity: 0.5 }));
  st.position.set(ARC_X[i], ARC_RAIL_Y - 0.5, -0.5);
  st.visible = false;
  graph.add(st);
  return st;
});""",
    'arcbuild')

sub(
    """  // four arcs: the rail draws, then each line of evidence lands on it
  arcRail.visible = kind === 'arcs';
  const railP = kind === 'arcs' ? clamp((u - 0.04) / 0.52) : 0;
  arcRail.scale.x = Math.max(0.001, railP);
  arcRail.position.x = -4.8 + 4.8 * railP;
  arcCards.forEach((c, i) => {
    const on = kind === 'arcs';
    const local = clamp((u - 0.1 - i * 0.14) / 0.18);
    c.visible = on && local > 0;
    arcNodes[i].visible = on && local > 0;
    if (!c.visible) return;
    const e = ease(local);
    c.position.copy(c.userData.home);
    c.position.y = c.userData.home.y + lerp(0.5, 0, e);
    c.position.z = lerp(0.9, 0.1, e);
    c.scale.setScalar(lerp(0.88, 1, e));
    c.material.opacity = e;
    c.rotation.z = lerp(0.12, 0, e);
    arcNodes[i].scale.setScalar(lerp(0.4, 1, e));
  });""",
    """  // four arcs: the rail draws, then each line of evidence drops onto it
  const arcsOn = kind === 'arcs';
  arcRail.visible = arcsOn;
  const railP = arcsOn ? clamp((u - 0.03) / 0.4) : 0;
  arcRail.scale.x = Math.max(0.001, railP);
  arcRail.position.x = -4.75 + 4.75 * railP;
  arcCards.forEach((c, i) => {
    const local = clamp((u - 0.06 - i * 0.11) / 0.15);
    c.visible = arcsOn && local > 0;
    arcNodes[i].visible = c.visible;
    arcStems[i].visible = c.visible;
    if (!c.visible) return;
    const e = ease(local);
    c.position.copy(c.userData.home);
    c.position.y = c.userData.home.y + lerp(0.7, 0, e);
    c.position.z = lerp(1.1, 0.1, e);
    c.scale.setScalar(lerp(0.9, 1, e));
    c.material.opacity = e;
    c.rotation.z = lerp(0.1, 0, e);
    arcNodes[i].scale.setScalar(lerp(0.3, 1, e));
    arcStems[i].scale.y = e;
  });""",
    'arclogic')

# ---------------------------------------------------------------- 6. cameras
sub(
    "  'island-rise': { from: [[4.6, 2.8, 9.0], [12.5, 8.0, 21]], look: [[0, 1.6, 0], [0, 0.7, 0]] },",
    "  'island-rise': { from: [[6.4, 2.4, 12.5], [15.0, 9.5, 26]], look: [[0, 1.5, 0], [0, 0.4, 0]] },",
    'islandcam')

sub(
    "  'four-arcs': { from: [[0, 0.35, 9.4], [0, 0.35, 8.8]], look: [[0, 0.3, 0], [0, 0.3, 0]] },",
    "  'four-arcs': { from: [[0, 0.55, 9.2], [0, 0.5, 8.6]], look: [[0, 0.55, 0], [0, 0.5, 0]] },",
    'arccam')

P.write_text(s)
print('scene.mjs patched (pass 2)')
