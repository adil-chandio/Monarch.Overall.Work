"""One-shot patch for scene.mjs: fix the six visual defects found in delivery QC.

Defects, in order of audience impact:
 1. empty-slot shot rendered against a hidden backdrop -> 6.5 s of near-black.
 2. empty-slot had no headline of its own (it relied on a screen overlay that
    collided with the slot frame).
 3. four-arcs showed one card at a time in a black void.
 4. island-rise read as a white pancake, not an ice floe in the Arctic Ocean.
 5. fur was sparse enough to read as bristles; helix was blown out to white.
 6. graph-space cards were too dim to read.
"""
from pathlib import Path

P = Path(__file__).resolve().parent / 'scene.mjs'
s = P.read_text()


def sub(old, new, tag):
    global s
    assert s.count(old) == 1, f'{tag}: expected 1 match, found {s.count(old)}'
    s = s.replace(old, new)


# ---------------------------------------------------------------- 1. floe
sub(
    """function buildFloe() {
  const g = new T.Group();
  const geo = new T.CircleGeometry(16, 72);
  const pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), y = pos.getY(i);
    const d = Math.hypot(x, y);
    if (d > 0.01) {
      const a = Math.atan2(y, x);
      const edge = 15.2 + Math.sin(a * 3.1) * 1.5 + Math.sin(a * 5.7 + 1.2) * 0.9 + Math.sin(a * 2.3 + 0.4) * 1.2;
      const s = edge / d;
      pos.setXY(i, x * s, y * s);
    }
    pos.setZ(i, Math.sin(x * 0.7) * 0.04 + Math.cos(y * 0.55) * 0.05);
  }
  geo.computeVertexNormals();
  geo.rotateX(-Math.PI / 2);
  const ice = new T.Mesh(geo, new T.MeshStandardMaterial({ color: 0xbfd6e4, roughness: 0.42, metalness: 0.06 }));
  g.add(ice);
  const snow = new T.Mesh(geo.clone(), new T.MeshStandardMaterial({ color: 0xeaf2f7, roughness: 0.95, transparent: true, opacity: 0.55 }));
  snow.position.y = 0.05; snow.scale.setScalar(0.985);
  g.add(snow);
  return g;
}""",
    """function floeEdge(a) {
  return 9.4 + Math.sin(a * 3.1) * 1.15 + Math.sin(a * 5.7 + 1.2) * 0.66 + Math.sin(a * 2.3 + 0.4) * 0.85;
}
function buildFloe() {
  const g = new T.Group();
  const N = 96;
  const geo = new T.CircleGeometry(1, N);
  const pos = geo.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), y = pos.getY(i);
    const d = Math.hypot(x, y);
    if (d > 0.01) {
      const a = Math.atan2(y, x);
      pos.setXY(i, (x / d) * floeEdge(a), (y / d) * floeEdge(a));
    }
    pos.setZ(i, Math.sin(x * 0.7) * 0.04 + Math.cos(y * 0.55) * 0.05);
  }
  geo.computeVertexNormals();
  geo.rotateX(-Math.PI / 2);
  const ice = new T.Mesh(geo, new T.MeshStandardMaterial({ color: 0xbfd6e4, roughness: 0.42, metalness: 0.06 }));
  g.add(ice);
  const snow = new T.Mesh(geo.clone(), new T.MeshStandardMaterial({ color: 0xeaf2f7, roughness: 0.95, transparent: true, opacity: 0.55 }));
  snow.position.y = 0.05; snow.scale.setScalar(0.985);
  g.add(snow);
  // slab edge: the floe has to read as floating ice, not a flat white sheet
  const ring = [];
  for (let i = 0; i < N; i++) {
    const a = (i / N) * Math.PI * 2;
    const r = floeEdge(a) * 0.995;
    ring.push([Math.cos(a) * r, Math.sin(a) * r]);
  }
  const vp = [], idx = [];
  for (const [x, z] of ring) { vp.push(x, 0, z, x, -1.15, z); }
  for (let i = 0; i < N; i++) {
    const a = i * 2, b = i * 2 + 1;
    const c = ((i + 1) % N) * 2, d = ((i + 1) % N) * 2 + 1;
    idx.push(a, c, b, b, c, d);
  }
  const skirt = new T.BufferGeometry();
  skirt.setAttribute('position', new T.Float32BufferAttribute(vp, 3));
  skirt.setIndex(idx);
  skirt.computeVertexNormals();
  const edge = new T.Mesh(skirt, new T.MeshStandardMaterial({ color: 0x7ea9c2, roughness: 0.5, metalness: 0.05, transparent: true, opacity: 0.92 }));
  g.add(edge);
  return g;
}""",
    'floe')

# ---------------------------------------------------------------- 2. fur density + softer tusks
sub(
    """  const coatGeo = new T.ConeGeometry(0.013, 0.21, 4, 1, true);
  coatGeo.translate(0, 0.105, 0);
  const coat = new T.InstancedMesh(coatGeo, furMat, 16000);
  const coatSurface = [
    ...ellipsoidPoints(1.16, 1.06, 2.15, 4200, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 1.95, -0.15)), n: v.n })),
    ...ellipsoidPoints(0.88, 0.74, 0.98, 1800, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.68, 0.30)), n: v.n })),
    ...ellipsoidPoints(0.92, 0.86, 0.92, 1100, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.02, -1.70)), n: v.n })),
    ...ellipsoidPoints(0.84, 0.92, 1.00, 260, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.72, 2.10)), n: v.n })),
    ...ellipsoidPoints(1.02, 1.02, 0.95, 900, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.34, 0.55)), n: v.n }))
  ];""",
    """  const coatGeo = new T.ConeGeometry(0.015, 0.15, 4, 1, true);
  coatGeo.translate(0, 0.075, 0);
  const coat = new T.InstancedMesh(coatGeo, furMat, 26000);
  const coatSurface = [
    ...ellipsoidPoints(1.16, 1.06, 2.15, 13000, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 1.95, -0.15)), n: v.n })),
    ...ellipsoidPoints(0.88, 0.74, 0.98, 5600, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.68, 0.30)), n: v.n })),
    ...ellipsoidPoints(0.92, 0.86, 0.92, 3600, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.02, -1.70)), n: v.n })),
    ...ellipsoidPoints(0.84, 0.92, 1.00, 1100, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.72, 2.10)), n: v.n })),
    ...ellipsoidPoints(1.02, 1.02, 0.95, 2000, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.34, 0.55)), n: v.n }))
  ];""",
    'coat')

sub(
    """  const shagGeo = new T.ConeGeometry(0.005, 0.27, 4, 1, true);
  shagGeo.translate(0, 0.135, 0);
  const shag = new T.InstancedMesh(shagGeo, furMat, 9000);
  const shagSurface = [
    ...ellipsoidPoints(1.16, 1.06, 2.15, 4200, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 1.95, -0.15)), n: v.n })),
    ...ellipsoidPoints(1.02, 1.02, 0.95, 1600, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.34, 0.55)), n: v.n })),
    ...ellipsoidPoints(0.88, 0.74, 0.98, 900, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.68, 0.30)), n: v.n }))
  ];""",
    """  const shagGeo = new T.ConeGeometry(0.006, 0.20, 4, 1, true);
  shagGeo.translate(0, 0.10, 0);
  const shag = new T.InstancedMesh(shagGeo, furMat, 15000);
  const shagSurface = [
    ...ellipsoidPoints(1.16, 1.06, 2.15, 8500, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 1.95, -0.15)), n: v.n })),
    ...ellipsoidPoints(1.02, 1.02, 0.95, 3200, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.34, 0.55)), n: v.n })),
    ...ellipsoidPoints(0.88, 0.74, 0.98, 3000, []).map((v) => ({ p: v.p.clone().add(new T.Vector3(0, 2.68, 0.30)), n: v.n }))
  ];""",
    'shag')

# ---------------------------------------------------------------- 3. shoulder helix colour
sub(
    "const helix = buildHelix(0.36, 1.7, 2.1, 0x35c9ff, 2.4);",
    "const helix = buildHelix(0.38, 1.8, 2.1, 0x3fd2ff, 1.05);",
    'helix')

# ---------------------------------------------------------------- 4. card mesh: brighter, tunable type
sub(
    """function cardMesh(title, sub, accent, w = 2.5, h = 1.45) {
  const tex = textPlate([title, sub], { w: 1000, h: 580, titleSize: 132, subSize: 52, accent, center: true, color: '#f4efe4' });
  const mat = new T.MeshStandardMaterial({
    map: tex, transparent: true, roughness: 0.5, metalness: 0.05,
    emissive: 0xffffff, emissiveMap: tex, emissiveIntensity: 0.22, side: T.DoubleSide
  });""",
    """function cardMesh(title, sub, accent, w = 2.5, h = 1.45, titleSize = 132, subSize = 52) {
  const tex = textPlate([title, sub], { w: 1000, h: 580, titleSize, subSize, accent, center: true, color: '#f4efe4' });
  const mat = new T.MeshStandardMaterial({
    map: tex, transparent: true, roughness: 0.5, metalness: 0.05,
    emissive: 0xffffff, emissiveMap: tex, emissiveIntensity: 0.5, side: T.DoubleSide
  });""",
    'cardMesh')

# ---------------------------------------------------------------- 5. the empty slot becomes a framed evidence hole
sub(
    """// empty slot: glowing frame + dissolving helix fragment
const slot = new T.Group();
slot.position.set(0, -0.35, 0.1);
const slotMat = new T.MeshStandardMaterial({ color: 0xffb27a, emissive: 0xff9a55, emissiveIntensity: 1.6, transparent: true, opacity: 0.85 });
const bar = (w, h, x, y) => { const m = new T.Mesh(new T.BoxGeometry(w, h, 0.05), slotMat); m.position.set(x, y, 0); slot.add(m); };
bar(2.5, 0.045, 0, 0.72); bar(2.5, 0.045, 0, -0.72); bar(0.045, 1.48, -1.24, 0); bar(0.045, 1.48, 1.24, 0);
const frag = buildHelix(0.3, 1.05, 1.4, 0xffc79a, 1.5);
frag.position.set(0, 0, 0.15);
slot.add(frag);""",
    """// empty slot: the fifth evidence slot, framed and lit, with nothing inside it
const slot = new T.Group();
slot.position.set(0, -0.9, 0.15);
const slotFrameTex = canvasTex(1200, 700, (g, w, h) => {
  g.clearRect(0, 0, w, h);
  g.strokeStyle = 'rgba(255,178,122,0.95)'; g.lineWidth = 7;
  g.strokeRect(10, 10, w - 20, h - 20);
  g.strokeStyle = 'rgba(255,178,122,0.28)'; g.lineWidth = 2;
  g.strokeRect(28, 28, w - 56, h - 56);
  g.strokeStyle = 'rgba(255,220,190,1)'; g.lineWidth = 9;
  const L = 78;
  for (const [cx, cy, sx, sy] of [[10, 10, 1, 1], [w - 10, 10, -1, 1], [10, h - 10, 1, -1], [w - 10, h - 10, -1, -1]]) {
    g.beginPath(); g.moveTo(cx, cy + sy * L); g.lineTo(cx, cy); g.lineTo(cx + sx * L, cy); g.stroke();
  }
});
const slotFrameMat = new T.MeshBasicMaterial({ map: slotFrameTex, transparent: true, depthWrite: false });
const slotFrame = new T.Mesh(new T.PlaneGeometry(2.5, 1.458), slotFrameMat);
slotFrame.renderOrder = 2;
slot.add(slotFrame);
const slotGlowMat = new T.MeshBasicMaterial({ map: DOT_TEX, transparent: true, depthWrite: false, blending: T.AdditiveBlending, color: 0xff9a55 });
const slotGlow = new T.Mesh(new T.PlaneGeometry(3.7, 2.3), slotGlowMat);
slotGlow.position.z = -0.06;
slotGlow.renderOrder = 1;
slot.add(slotGlow);
const slotHeadTex = canvasTex(1400, 300, (g, w, h) => {
  g.clearRect(0, 0, w, h);
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.font = '400 118px Anton';
  g.fillStyle = '#ffd9b8';
  g.fillText('NO FINAL WITNESS', w / 2, h * 0.30);
  g.fillStyle = 'rgba(255,178,122,0.95)';
  g.fillRect(w / 2 - 66, h * 0.53, 132, 6);
  g.font = '800 50px Manrope';
  g.fillStyle = 'rgba(238,226,212,0.86)';
  g.fillText('the last ~300 years are not in the file', w / 2, h * 0.74);
});
const slotHeadMat = new T.MeshBasicMaterial({ map: slotHeadTex, transparent: true, depthWrite: false });
const slotHead = new T.Mesh(new T.PlaneGeometry(2.12, 0.454), slotHeadMat);
slotHead.position.set(0, 0.06, 0.03);
slotHead.renderOrder = 3;
slot.add(slotHead);
const frag = buildHelix(0.2, 0.72, 1.2, 0xffc79a, 1.4);
frag.position.set(0, -0.3, 0.0);
frag.renderOrder = 1;
slot.add(frag);""",
    'slot')

# dust sits inside the new frame
sub(
    """  const p = new T.Points(geo, new T.PointsMaterial({ size: 0.1, map: DOT_TEX, transparent: true, opacity: 0.7, depthWrite: false, color: 0xffc79a }));
  p.userData = { seed, base: pos.slice(), n };
  slot.add(p);""",
    """  const p = new T.Points(geo, new T.PointsMaterial({ size: 0.09, map: DOT_TEX, transparent: true, opacity: 0.7, depthWrite: false, color: 0xffc79a }));
  p.userData = { seed, base: pos.slice(), n };
  p.renderOrder = 1;
  slot.add(p);""",
    'dust')

# ---------------------------------------------------------------- 6. two-truth panels
sub(
    """const panelA = cardMesh('DAMAGED', 'measured, real', '#ff8f7a', 3.0, 1.7);
panelA.position.set(-2.5, 0.5, 0.2);
const panelB = cardMesh('RECOVERED', 'also measured', '#7fe3ff', 3.0, 1.7);
panelB.position.set(2.5, 0.5, 0.2);""",
    """const panelA = cardMesh('DAMAGED', 'measured, real', '#ff8f7a', 3.4, 1.95);
panelA.position.set(-2.75, 0.5, 0.2);
const panelB = cardMesh('RECOVERED', 'also measured', '#7fe3ff', 3.4, 1.95);
panelB.position.set(2.75, 0.5, 0.2);""",
    'truths')

# ---------------------------------------------------------------- 7. four arcs -> one timeline
sub(
    """// four-arc cards
const arcData = [
  ['2017', 'MELTDOWN', '#ff8f7a'],
  ['2019', 'STABLE, THEN ICE', '#9fe8c6'],
  ['3,600 BP', 'HUMANS TOO LATE', '#ffb27a'],
  ['2024', 'RECOVERED', '#8fd6ff'],
];
const arcCards = arcData.map((d, i) => {
  const m = cardMesh(d[0], d[1], d[2], 3.4, 1.9);
  m.position.set(0, 0, 0.2);
  m.visible = false;
  graph.add(m);
  return m;
});""",
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
    'arcs')

# ---------------------------------------------------------------- 8. cameras
sub(
    """const CAM = {
  'wide-floe': { from: [[-5.2, 1.15, 18], [-2.2, 1.85, 13.0]], look: [[-1.1, 2.35, 0], [-0.7, 2.3, 0]] },
  'shoulder-wool': { from: [[5.4, 3.5, 7.6], [4.1, 3.1, 6.0]], look: [[0.25, 2.55, 1.25], [0.2, 2.5, 1.35]] },
  'island-rise': { from: [[12, 19, 24], [8, 13, 19]], look: [[0, 0.6, 0], [0, 0.3, 0]] },
  'strange-part': { from: [[0, 0.3, 8.4], [0, 0.1, 6.4]], look: [[0, 0, 0], [0, 0, 0]] },
  'genome-record': { from: [[-2.6, 0.8, 10.0], [2.5, 0.7, 9.0]], look: [[-1.5, 0.2, 0], [1.5, 0.5, 0]] },
  'two-truths': { from: [[0, 0.4, 8.6], [0, 0.4, 7.2]], look: [[0, 0.4, 0], [0, 0.4, 0]] },
  'four-witnesses': { from: [[-0.9, 0.85, 11.6], [1.1, 0.8, 10.6]], look: [[-0.5, 0.62, 0], [0.4, 0.62, 0]] },
  'empty-slot': { from: [[0, -0.15, 8.8], [0, -0.35, 5.4]], look: [[0, -0.3, 0], [0, -0.35, 0.1]] },
  'four-arcs': { from: [[0, 0.1, 6.6], [0, 0.1, 6.6]], look: [[0, 0, 0], [0, 0, 0]] },
  'promise': { from: [[0, 0.2, 8.2], [0, -0.1, 7.4]], look: [[0, 0.1, 0], [0, -0.2, 0]] },
  'resolve': { from: [[-2.8, 2.2, 23], [1.3, 1.95, 17]], look: [[-0.5, 2.25, 0], [-0.2, 2.1, 0]] },
};""",
    """const CAM = {
  'wide-floe': { from: [[-4.6, 1.05, 13.5], [-2.4, 1.8, 10.5]], look: [[-1.0, 2.35, 0], [-0.6, 2.3, 0]] },
  'shoulder-wool': { from: [[3.0, 3.05, 5.0], [2.2, 2.85, 4.0]], look: [[0.45, 2.55, 1.95], [0.45, 2.5, 2.05]] },
  'island-rise': { from: [[4.6, 2.8, 9.0], [12.5, 8.0, 21]], look: [[0, 1.6, 0], [0, 0.7, 0]] },
  'strange-part': { from: [[0, 0.3, 8.4], [0, 0.15, 7.0]], look: [[0, 0, 0], [0, 0, 0]] },
  'genome-record': { from: [[-2.6, 0.8, 10.0], [2.5, 0.7, 9.0]], look: [[-1.5, 0.2, 0], [1.5, 0.5, 0]] },
  'two-truths': { from: [[0, 0.4, 8.8], [0, 0.4, 8.0]], look: [[0, 0.4, 0], [0, 0.4, 0]] },
  'four-witnesses': { from: [[-0.9, 0.85, 11.6], [1.1, 0.8, 10.6]], look: [[-0.5, 0.62, 0], [0.4, 0.62, 0]] },
  'empty-slot': { from: [[0, 0.15, 10.6], [0, 0.05, 9.6]], look: [[0, 0.1, 0], [0, 0.05, 0]] },
  'four-arcs': { from: [[0, 0.35, 9.4], [0, 0.35, 8.8]], look: [[0, 0.3, 0], [0, 0.3, 0]] },
  'promise': { from: [[0, 0.2, 8.2], [0, -0.1, 7.4]], look: [[0, 0.1, 0], [0, -0.2, 0]] },
  'resolve': { from: [[-2.8, 2.2, 23], [1.3, 1.95, 17]], look: [[-0.5, 2.25, 0], [-0.2, 2.1, 0]] },
};""",
    'cam')

# ---------------------------------------------------------------- 9. graph-space update logic
sub(
    """function updateGraph(t, u, kind) {
  board.material.opacity = 0.0;
  backdrop.visible = kind !== 'empty';
  strings.visible = kind === 'witnesses' || kind === 'promise';
  // witness cards swing in
  cards.forEach((c, i) => {
    const local = clamp((u - c.userData.delay) / 0.32);
    const on = kind === 'witnesses' || kind === 'promise';
    c.visible = on && local > 0;
    if (!c.visible) return;
    const e = ease(local);
    c.position.copy(c.userData.home);
    c.position.z = lerp(-1.0, 0, e);
    c.position.y = c.userData.home.y + lerp(0.7, 0, e);
    c.rotation.y = lerp(-0.9, 0, e) + Math.sin(t * 0.8 + i) * 0.02;
    c.rotation.x = lerp(0.35, 0, e);
    c.material.opacity = e;
  });
  // empty slot glow + dissolving dust
  const slotOn = kind === 'empty' || kind === 'promise';
  slot.position.y = kind === 'promise' ? -0.62 : -0.35;
  slot.visible = slotOn;
  if (slotOn) {
    const p = 0.55 + 0.45 * Math.sin(t * 2.1);
    slotMat.opacity = kind === 'promise' ? 0.34 : p;
    slotMat.emissiveIntensity = 1.2 + p * 1.4;
    frag.rotation.y = t * 0.9;
    frag.scale.setScalar(1 - 0.35 * ((t * 0.5) % 1));
    frag.userData.strandA.material.opacity = 0.9 * (1 - ((t * 0.5) % 1));
    frag.userData.strandB.material.opacity = 0.9 * (1 - ((t * 0.5) % 1));
    frag.userData.rungs.material.opacity = 0.9 * (1 - ((t * 0.5) % 1));
    const dp = dust.geometry.attributes.position, db = dust.userData.base, ds = dust.userData.seed;
    for (let i = 0; i < ds.length; i++) {
      const life = (t * 0.5 + ds[i]) % 1;
      dp.setXYZ(i, db[i * 3] * (1 + life * 0.7), db[i * 3 + 1] * (1 + life * 0.7) + life * 0.5, db[i * 3 + 2] + life * 0.6);
    }
    dp.needsUpdate = true;
    dust.material.opacity = 0.55 * (1 - ((t * 0.5) % 1));
  }""",
    """function updateGraph(t, u, kind) {
  board.material.opacity = 0.24;
  backdrop.visible = true;
  strings.visible = kind === 'witnesses' || kind === 'promise';
  // witness cards swing in
  cards.forEach((c, i) => {
    const on = kind === 'witnesses' || kind === 'promise' || kind === 'empty';
    if (!on) { c.visible = false; return; }
    if (kind === 'empty') {
      // the evidence stays on the board, dimmed, while the hole is revealed
      const e = ease(clamp((u - i * 0.02) / 0.16));
      c.visible = e > 0;
      c.position.set(-3.6 + i * 2.4, 1.75, -0.55);
      c.rotation.set(0, 0, 0);
      c.scale.setScalar(0.62);
      c.material.opacity = 0.34 * e;
      return;
    }
    const local = clamp((u - c.userData.delay) / 0.32);
    c.visible = local > 0;
    if (!c.visible) return;
    const e = ease(local);
    c.position.copy(c.userData.home);
    c.position.z = lerp(-1.0, 0, e);
    c.position.y = c.userData.home.y + lerp(0.7, 0, e);
    c.rotation.y = lerp(-0.9, 0, e) + Math.sin(t * 0.8 + i) * 0.02;
    c.rotation.x = lerp(0.35, 0, e);
    c.scale.setScalar(1);
    c.material.opacity = e;
  });
  // empty slot glow + dissolving dust
  const slotOn = kind === 'empty' || kind === 'promise';
  slot.visible = slotOn;
  slotHead.visible = kind === 'empty';
  if (slotOn) {
    const p = 0.55 + 0.45 * Math.sin(t * 2.1);
    slot.position.y = kind === 'promise' ? -0.62 : -0.9;
    slot.scale.setScalar(kind === 'empty' ? 1.55 : 1);
    slotFrameMat.opacity = kind === 'promise' ? 0.3 : 0.55 + 0.4 * p;
    slotGlowMat.opacity = kind === 'promise' ? 0.10 : 0.18 + 0.16 * p;
    slotHeadMat.opacity = kind === 'empty' ? clamp((u - 0.28) / 0.16) : 0;
    frag.rotation.y = t * 0.9;
    frag.scale.setScalar(1 - 0.35 * ((t * 0.5) % 1));
    frag.userData.strandA.material.opacity = 0.55 * (1 - ((t * 0.5) % 1));
    frag.userData.strandB.material.opacity = 0.55 * (1 - ((t * 0.5) % 1));
    frag.userData.rungs.material.opacity = 0.55 * (1 - ((t * 0.5) % 1));
    const dp = dust.geometry.attributes.position, db = dust.userData.base, ds = dust.userData.seed;
    for (let i = 0; i < ds.length; i++) {
      const life = (t * 0.5 + ds[i]) % 1;
      dp.setXYZ(i, db[i * 3] * (1 + life * 0.7), db[i * 3 + 1] * (1 + life * 0.7) + life * 0.5, db[i * 3 + 2] + life * 0.6);
    }
    dp.needsUpdate = true;
    dust.material.opacity = 0.5 * (1 - ((t * 0.5) % 1));
  }""",
    'updateGraph-cards')

# four arcs timeline reveal
sub(
    """  // four arcs
  arcCards.forEach((c, i) => {
    const local = clamp((u * 4) - i);
    const on = kind === 'arcs' && local > 0 && local < 1;
    c.visible = on;
    if (!on) return;
    const e = ease(local);
    c.position.z = lerp(1.4, 0.2, e);
    c.scale.setScalar(lerp(0.82, 1, e));
    c.material.opacity = Math.min(1, (1 - local) * 4);
    c.rotation.z = lerp(0.16, 0, e);
  });""",
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
    'updateGraph-arcs')

# ---------------------------------------------------------------- 10. big helix sizing
sub(
    "      const big = buildHelix(1.25, 5.2, 2.6, 0x7fe3ff, 1.5);",
    "      const big = buildHelix(1.05, 4.0, 2.4, 0x7fe3ff, 0.95);",
    'bighelix')

P.write_text(s)
print('scene.mjs patched')
