// Rebuild test: 3D island isolation sequence. Derived from the opening scene.
// Every form here is procedurally built for this film: no imported models, no photographs,
// no competitor footage. Reconstruction is illustrative, not photographic.
import * as T from 'three';

await document.fonts.load('800 48px Manrope');
await document.fonts.load('80px Anton');
const S = await (await fetch('/timeline.json')).json();
const W = S.width, H = S.height, FPS = S.fps;
// AI-generated images are used only as UV material maps on 3D geometry,
// never as still-image backgrounds or slide plates.
const loader = new T.TextureLoader();
const [furMap, tundraMap] = await Promise.all([
  loader.loadAsync('/assets/fur.jpg'), loader.loadAsync('/assets/tundra.jpg')
]);
for (const t of [furMap,tundraMap]) { t.colorSpace=T.SRGBColorSpace; t.wrapS=t.wrapT=T.RepeatWrapping; t.anisotropy=4; }
furMap.repeat.set(2,1); tundraMap.repeat.set(32,32);


// Render-cost profile. Defaults are the production values; the query string
// only exists so the cost of each option can be measured in the real scene
// before it is adopted. See _bench3.mjs.
const QS = new URLSearchParams(location.search);
const qn = (k, d) => (QS.has(k) ? parseFloat(QS.get(k)) : d);
const PROF = {
  aa: QS.get('aa') !== '0',
  furMat: QS.get('furmat') || 'standard',
  lights: qn('lights', 6),
  coat: qn('coat', 0.42),
  under: qn('under', 0),
  shag: qn('shag', 0.65),
  clump: qn('clump', 0.5),
  clumpGeom: QS.get('clumpgeom') || 'ico',
  hideTex: QS.get('hidetex') !== '0',
  dropShag: QS.get('shag') === '0',
  hideMat: QS.get('hidemat') || 'standard',
};

/* ---------- deterministic noise helpers ---------- */
const mulberry = (seed) => () => {
  seed |= 0; seed = seed + 0x6D2B79F5 | 0;
  let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
  t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
  return ((t ^ t >>> 14) >>> 0) / 4294967296;
};
const R = mulberry(20251109);
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ease = (x) => 1 - Math.pow(1 - clamp(x), 3);
const smooth = (x) => { const t = clamp(x); return t * t * (3 - 2 * t); };
const lerp = (a, b, t) => a + (b - a) * t;
const v3 = (a) => new T.Vector3(a[0], a[1], a[2]);
const mixV = (a, b, t) => new T.Vector3(lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t));

/* ---------- renderer ---------- */
const renderer = new T.WebGLRenderer({ antialias: PROF.aa, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.outputColorSpace = T.SRGBColorSpace;
renderer.toneMapping = T.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;
renderer.domElement.id = 'final';
document.body.appendChild(renderer.domElement);

const scene = new T.Scene();
scene.fog = new T.FogExp2(0x14364d, 0.0125);
const camera = new T.PerspectiveCamera(38, W / H, 0.4, 3000);
camera.position.set(0, 3, 16);

/* ---------- textures ---------- */
function canvasTex(w, h, draw) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d'); draw(g, w, h);
  const tex = new T.CanvasTexture(c);
  tex.colorSpace = T.SRGBColorSpace;
  tex.anisotropy = 4;
  return tex;
}
const softDot = () => canvasTex(128, 128, (g, w, h) => {
  const grad = g.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
  grad.addColorStop(0, 'rgba(255,255,255,0.95)');
  grad.addColorStop(0.45, 'rgba(255,255,255,0.28)');
  grad.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = grad; g.fillRect(0, 0, w, h);
});
const DOT_TEX = softDot();

/* ---------- procedural wool ---------- */
// A hide that is itself wool. Two textures come out of this: a mottled fibre
// colour map and a matching normal map, so the gaps between coat clumps read
// as shadowed wool instead of bare skin. That is what lets the coat be much
// sparser without the animal going bald.
function hash2(x, y) {
  let h = x * 374761393 + y * 668265263;
  h = (h ^ (h >> 13)) * 1274126177;
  return ((h ^ (h >> 16)) >>> 0) / 4294967296;
}
function vnoise(x, y) {
  const xi = Math.floor(x), yi = Math.floor(y);
  const xf = x - xi, yf = y - yi;
  const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
  const a = hash2(xi, yi), b = hash2(xi + 1, yi), c = hash2(xi, yi + 1), d = hash2(xi + 1, yi + 1);
  return (a * (1 - u) + b * u) * (1 - v) + (c * (1 - u) + d * u) * v;
}
function fbm(x, y, oct) {
  let sum = 0, amp = 0.5, f = 1;
  for (let i = 0; i < oct; i++) { sum += amp * vnoise(x * f, y * f); f *= 2.03; amp *= 0.5; }
  return sum;
}
function woolTextures(size = 512) {
  const HGT = new Float32Array(size * size);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      // Stretched noise reads as fibres lying along one direction.
      const fib = fbm(x * 0.09, y * 0.30, 4);
      const clump = fbm(x * 0.045, y * 0.045, 3);
      HGT[y * size + x] = fib * 0.68 + clump * 0.32;
    }
  }
  const col = canvasTex(size, size, (g, w, h) => {
    const img = g.createImageData(w, h);
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const i = y * w + x;
        const n = HGT[i];
        // Dark chocolate brown with warm and cool fibre variation.
        const warm = fbm(x * 0.13, y * 0.13, 3);
        const r = 74 + n * 52 + warm * 26;
        const gg = 50 + n * 38 + warm * 12;
        const b = 33 + n * 24;
        img.data[i * 4] = Math.min(255, r);
        img.data[i * 4 + 1] = Math.min(255, gg);
        img.data[i * 4 + 2] = Math.min(255, b);
        img.data[i * 4 + 3] = 255;
      }
    }
    g.putImageData(img, 0, 0);
  });
  col.wrapS = col.wrapT = T.RepeatWrapping;
  col.repeat.set(3, 3);
  const nrm = canvasTex(size, size, (g, w, h) => {
    const img = g.createImageData(w, h);
    const at = (x, y) => HGT[((y + h) % h) * w + ((x + w) % w)];
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const i = y * w + x;
        const dx = (at(x + 1, y) - at(x - 1, y)) * 2.4;
        const dy = (at(x, y + 1) - at(x, y - 1)) * 2.4;
        const len = Math.hypot(dx, dy, 1);
        img.data[i * 4] = ((-dx / len) * 0.5 + 0.5) * 255;
        img.data[i * 4 + 1] = ((-dy / len) * 0.5 + 0.5) * 255;
        img.data[i * 4 + 2] = ((1 / len) * 0.5 + 0.5) * 255;
        img.data[i * 4 + 3] = 255;
      }
    }
    g.putImageData(img, 0, 0);
  });
  nrm.wrapS = nrm.wrapT = T.RepeatWrapping;
  nrm.repeat.set(3, 3);
  return { color: col, normal: nrm };
}
const WOOL = woolTextures(512);

function textPlate(lines, opts = {}) {
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
    const accent = opts.accent || '#e9dcc4';
    if (opts.rule !== false) {
      g.fillStyle = accent;
      if (opts.center) g.fillRect(w * 0.5 - w * 0.03, h * 0.14, w * 0.06, h * 0.035);
      else g.fillRect(w * 0.06, h * 0.20, w * 0.055, h * 0.06);
    }
    const titleSize = opts.titleSize || 120;
    g.textAlign = 'left'; g.textBaseline = 'alphabetic';
    g.font = `400 ${titleSize}px ${main}`;
    g.fillStyle = opts.color || '#f3ece0';
    const tw = g.measureText(lines[0]).width;
    const tx = opts.center ? (w - tw) / 2 : w * 0.06;
    g.fillText(lines[0], tx, h * 0.52);
    if (lines[1]) {
      g.font = `800 ${opts.subSize || 54}px ${sub}`;
      g.fillStyle = opts.subColor || 'rgba(226,236,244,0.72)';
      const sw = g.measureText(lines[1]).width;
      g.fillText(lines[1], opts.center ? (w - sw) / 2 : w * 0.06, h * 0.76);
    }
  });
}

/* ---------- sky ---------- */
const skyMat = new T.ShaderMaterial({
  side: T.BackSide, depthWrite: false, fog: false,
  uniforms: {
    top: { value: new T.Color(0x04080f) },
    mid: { value: new T.Color(0x11304a) },
    horizon: { value: new T.Color(0x3f6f8c) },
    glow: { value: new T.Color(0xd89a63) },
    sunDir: { value: new T.Vector3(0.26, 0.045, -0.965).normalize() },
    glowAmt: { value: 1.0 }
  },
  vertexShader: `varying vec3 vDir; void main(){ vDir = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
  fragmentShader: `
    uniform vec3 top, mid, horizon, glow, sunDir; uniform float glowAmt; varying vec3 vDir;
    void main(){
      float h = clamp(vDir.y * 0.5 + 0.5, 0.0, 1.0);
      vec3 col = mix(horizon, mid, smoothstep(0.48, 0.68, h));
      col = mix(col, top, smoothstep(0.62, 0.95, h));
      float d = max(dot(normalize(vDir), normalize(sunDir)), 0.0);
      col += glow * pow(d, 22.0) * 0.85 * glowAmt;
      col += glow * pow(d, 4.0) * 0.10 * glowAmt;
      gl_FragColor = vec4(col, 1.0);
    }`
});
const sky = new T.Mesh(new T.SphereGeometry(1400, 48, 32), skyMat);
scene.add(sky);

/* ---------- lights ---------- */
// Light rig with a priority order. A budget of N keeps the N most important
// lights and brightens the survivors, so cutting the count costs triangles
// and fill, not exposure.
const lightRig = [];
const rigBase = [];
const rigPush = (light, priority) => {
  light.userData.priority = priority;
  lightRig.push(light); rigBase.push(light.intensity);
  scene.add(light);
};
rigPush(new T.HemisphereLight(0x9cc4e0, 0x16222e, 0.92), 1);
// Low sun behind the animal: the silhouette does the storytelling in the wide shot.
const key = new T.DirectionalLight(0xffcf9c, 3.1); key.position.set(9, 3.4, -26); rigPush(key, 2);
const rim = new T.DirectionalLight(0x9fd4ff, 1.9); rim.position.set(-13, 7, -14); rigPush(rim, 4);
// The cool front fill and the warm bounce are folded into the hemisphere and the
// wool rig: eight lights meant eight per-fragment light evaluations per clump.
const warm = new T.PointLight(0xffb070, 5, 22, 2); warm.position.set(-2.2, 2.4, 2.2); rigPush(warm, 5);
// Wool rig: a soft key from camera-left that rakes across the coat so the fleece
// reads as fleece instead of a black cut-out, plus a cool bounce off the ice.
const woolKey = new T.DirectionalLight(0xffe0bd, 2.5); woolKey.position.set(-9, 5.2, 11); rigPush(woolKey, 3);
const woolFill = new T.DirectionalLight(0x8fb6d8, 1.15); woolFill.position.set(7.5, 1.6, 9); rigPush(woolFill, 6);

/* ---------- geometry helpers ---------- */
function taperedTube(points, radiusAt, tubular = 64, radial = 12) {
  const curve = new T.CatmullRomCurve3(points.map(v3));
  const geo = new T.TubeGeometry(curve, tubular, 1, radial, false);
  const pos = geo.attributes.position;
  const row = radial + 1;
  for (let i = 0; i <= tubular; i++) {
    const t = i / tubular;
    const centre = curve.getPointAt(t);
    const scale = radiusAt(t);
    for (let j = 0; j < row; j++) {
      const idx = i * row + j;
      const px = pos.getX(idx) - centre.x, py = pos.getY(idx) - centre.y, pz = pos.getZ(idx) - centre.z;
      pos.setXYZ(idx, centre.x + px * scale, centre.y + py * scale, centre.z + pz * scale);
    }
  }
  geo.computeVertexNormals();
  return geo;
}

/* ---------- the mammoth (original procedural reconstruction) ---------- */
function ellipsoidPoints(rx, ry, rz, count, out = []) {
  for (let i = 0; i < count; i++) {
    const u = R() * 2 - 1, phi = R() * Math.PI * 2;
    const s = Math.sqrt(1 - u * u);
    const dir = new T.Vector3(s * Math.cos(phi), u, s * Math.sin(phi));
    const p = new T.Vector3(dir.x * rx, dir.y * ry, dir.z * rz);
    const n = new T.Vector3(dir.x / rx, dir.y / ry, dir.z / rz).normalize();
    out.push({ p, n });
  }
  return out;
}

// Fibrous surface: a lumpy hide plus two layers of fine strands, so the silhouette
// breaks up like real shaggy fur instead of reading as spikes.
function lumpy(geo, amount, scale) {
  const pos = geo.attributes.position;
  const seedA = mulberry(4242), seedB = mulberry(919);
  const map = new Map();
  for (let i = 0; i < pos.count; i++) {
    const key = `${Math.round(pos.getX(i) * 6)},${Math.round(pos.getY(i) * 6)},${Math.round(pos.getZ(i) * 6)}`;
    let d = map.get(key);
    if (d === undefined) { d = (seedA() - 0.5) * 2 * amount + (seedB() - 0.5) * amount * 0.4; map.set(key, d); }
    const x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i);
    const len = Math.hypot(x, y, z) || 1;
    pos.setXYZ(i, x + (x / len) * d * scale, y + (y / len) * d * scale, z + (z / len) * d * scale);
  }
  geo.computeVertexNormals();
  return geo;
}

// Merge several hide geometries into one indexed buffer for fur sampling.
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

// Analytic "am I inside this hide volume?" tests. The mammoth is built from
// overlapping ellipsoids and capsules; a fur sample that lands on a buried surface
// is wasted, so every sample is checked against every OTHER volume.
// A point counts as buried only when it is genuinely inside another volume.
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
}

// Build one cumulative-area triangle table per part, once.
function buildTriTable(geo) {
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
  return { index, P, N, cum, total, tri };
}

// Draw one random point (position + normal) from a triangle table.
function drawPoint(tb) {
  const target = R() * tb.total;
  let lo = 0, hi = tb.tri - 1;
  while (lo < hi) { const mid = (lo + hi) >> 1; if (tb.cum[mid] < target) lo = mid + 1; else hi = mid; }
  const t = lo;
  const index = tb.index, P = tb.P, N = tb.N;
  const i0 = index[t * 3] * 3, i1 = index[t * 3 + 1] * 3, i2 = index[t * 3 + 2] * 3;
  let u = R(), v = R();
  if (u + v > 1) { u = 1 - u; v = 1 - v; }
  const w = 1 - u - v;
  return {
    p: new T.Vector3(
      P[i0] * w + P[i1] * u + P[i2] * v,
      P[i0 + 1] * w + P[i1 + 1] * u + P[i2 + 1] * v,
      P[i0 + 2] * w + P[i1 + 2] * u + P[i2 + 2] * v),
    n: new T.Vector3(
      N[i0] * w + N[i1] * u + N[i2] * v,
      N[i0 + 1] * w + N[i1 + 1] * u + N[i2 + 1] * v,
      N[i0 + 2] * w + N[i1 + 2] * u + N[i2 + 2] * v).normalize()
  };
}

// Place fur on every hide surface, weighted by surface area.
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
    const d = drawPoint(tables[pi]);
    out.push({ p: d.p, n: d.n, part: parts[pi] });
  }
  console.log('[fur] placed', out.length, 'tufts over', parts.length, 'hide surfaces');
  return out;
}

function buildMammoth() {
  const g = new T.Group();
  // The hide is wool in its own right, so a gap between coat clumps shows
  // shadowed fibre rather than bare skin.
  const hideMat = PROF.hideMat === 'lambert'
    ? new T.MeshLambertMaterial({ color: 0xffffff, map: WOOL.color, normalMap: WOOL.normal })
    : PROF.hideMat === 'basic'
      ? new T.MeshBasicMaterial({ color: 0xffffff, map: WOOL.color })
      : PROF.hideTex
        ? new T.MeshStandardMaterial({
          color: 0xffffff, map: furMap, normalMap: WOOL.normal,
          normalScale: new T.Vector2(0.18, 0.18), roughness: 0.96, metalness: 0.0
        })
        : new T.MeshStandardMaterial({ color: 0x6f5138, roughness: 0.96, metalness: 0.0 });
  // Wool is matte. Under a software rasteriser the PBR branch (roughness,
  // metalness, IBL) costs far more than it adds on a diffuse fleece, so the
  // material class is a measured choice, not a default.
  const furMat = PROF.furMat === 'basic'
    ? new T.MeshBasicMaterial({ color: 0x9a7550 })
    : PROF.furMat === 'lambert'
      ? new T.MeshLambertMaterial({ color: 0x9a7550 })
      : new T.MeshStandardMaterial({ color: 0x9a7550, roughness: 0.92, metalness: 0.0 });
  const shagMat = PROF.furMat === 'basic'
    ? new T.MeshBasicMaterial({ color: 0x8e6b47, transparent: true })
    : PROF.furMat === 'lambert'
      ? new T.MeshLambertMaterial({ color: 0x8e6b47, transparent: true })
      : new T.MeshStandardMaterial({ color: 0x8e6b47, roughness: 0.95, metalness: 0.0, transparent: true });
  const tuskMat = new T.MeshStandardMaterial({ color: 0xefe3c6, roughness: 0.28, metalness: 0.04 });
  const eyeMat = new T.MeshStandardMaterial({ color: 0x120c08, roughness: 0.1, metalness: 0.15 });

  // Hide volumes. Each transform is baked into the geometry so the very same
  // triangles can be reused as the fur surface later.
  const bodyGeo = lumpy(new T.SphereGeometry(1, 64, 48), 0.055, 1.0);
  bodyGeo.scale(1.16, 1.06, 2.15); bodyGeo.translate(0, 1.95, -0.15);
  g.add(new T.Mesh(bodyGeo, hideMat));

  const humpGeo = lumpy(new T.SphereGeometry(1, 48, 36), 0.045, 1.0);
  humpGeo.scale(0.88, 0.74, 0.98); humpGeo.translate(0, 2.68, 0.30);
  g.add(new T.Mesh(humpGeo, hideMat));

  const rumpGeo = lumpy(new T.SphereGeometry(1, 40, 30), 0.045, 1.0);
  rumpGeo.scale(0.92, 0.86, 0.92); rumpGeo.translate(0, 2.02, -1.70);
  g.add(new T.Mesh(rumpGeo, hideMat));

  const shoulderGeo = lumpy(new T.SphereGeometry(1, 40, 30), 0.04, 1.0);
  shoulderGeo.scale(1.02, 1.02, 0.95); shoulderGeo.translate(0, 2.34, 0.55);
  g.add(new T.Mesh(shoulderGeo, hideMat));

  const neckGeo = new T.CylinderGeometry(0.66, 0.84, 1.0, 24);
  neckGeo.rotateX(0.34); neckGeo.translate(0, 2.38, 1.32);
  g.add(new T.Mesh(neckGeo, hideMat));

  const headGeo = lumpy(new T.SphereGeometry(1, 48, 36), 0.04, 1.0);
  headGeo.scale(0.84, 0.92, 1.00); headGeo.rotateX(-0.14); headGeo.translate(0, 2.72, 2.10);
  g.add(new T.Mesh(headGeo, hideMat));

  const domeGeos = [];
  for (const s of [-1, 1]) {
    const domeGeo = new T.SphereGeometry(1, 26, 20);
    domeGeo.scale(0.32, 0.28, 0.38);
    domeGeo.translate(s * 0.26, 3.14, 2.02);
    g.add(new T.Mesh(domeGeo, hideMat));
    domeGeos.push(domeGeo);
    const ear = new T.Mesh(new T.SphereGeometry(1, 24, 18), hideMat);
    ear.scale.set(0.30, 0.085, 0.22); ear.position.set(s * 0.60, 2.82, 1.88); ear.rotation.z = s * 0.34; g.add(ear);
    // Socket ring, then the eye sitting ON the skull surface (z ~ 2.86), so the
    // coat does not swallow it.
    const socket = new T.Mesh(new T.SphereGeometry(0.088, 18, 12),
      new T.MeshStandardMaterial({ color: 0x4a3524, roughness: 0.96 }));
    socket.scale.set(1, 0.82, 0.5);
    socket.position.set(s * 0.545, 2.855, 2.855); g.add(socket);
    const eye = new T.Mesh(new T.SphereGeometry(0.062, 18, 14), eyeMat);
    eye.position.set(s * 0.545, 2.862, 2.895); g.add(eye);
    const glint = new T.Mesh(new T.SphereGeometry(0.019, 10, 8), new T.MeshBasicMaterial({ color: 0xe6f3ff }));
    glint.position.set(s * 0.566, 2.885, 2.922); g.add(glint);
  }

  const trunkGeo = taperedTube(
    [[0, 2.52, 2.58], [0, 2.04, 2.94], [0.02, 1.46, 3.00], [0.04, 0.98, 2.86], [0.03, 0.78, 2.62]],
    (t) => 0.225 - 0.165 * t, 80, 16);
  g.add(new T.Mesh(trunkGeo, new T.MeshStandardMaterial({ color: 0x7d5c42, roughness: 0.84 })));
  for (const s of [-1, 1]) {
    const tusk = new T.Mesh(taperedTube(
      [[s * 0.32, 2.12, 2.54], [s * 0.76, 2.04, 3.10], [s * 1.04, 2.22, 3.58], [s * 1.00, 2.54, 3.96]],
      (t) => 0.105 * (1 - t * 0.92), 64, 12), tuskMat);
    g.add(tusk);
  }

  // Each limb has its own hip pivot. Hide and fur use the same local transform.
  // This simple swing rig is exploratory, not a biomechanically complete walk cycle.
  const legGeos = [], legs = [];
  for (const [x, z, h] of [[-0.60, 1.20, 1.92], [0.60, 1.20, 1.92], [-0.62, -1.25, 1.96], [0.62, -1.25, 1.96]]) {
    const pivot = new T.Group(); pivot.position.set(x, h, z); g.add(pivot);
    const index = legs.length; legs.push(pivot);
    const legGeo = new T.CylinderGeometry(0.27, 0.35, h, 20, 1);
    legGeo.translate(x, h / 2 + 0.08, z);
    const legMesh = new T.Mesh(legGeo, hideMat); legMesh.position.set(-x, -h, -z); pivot.add(legMesh);
    legGeos.push({ geo: legGeo, x, z, h, limb: index });
    const footGeo = new T.CylinderGeometry(0.34, 0.38, 0.26, 20);
    footGeo.translate(x, 0.13, z + 0.05);
    const footMesh = new T.Mesh(footGeo, hideMat); footMesh.position.set(-x, -h, -z); pivot.add(footMesh);
    legGeos.push({ geo: footGeo, x, z, h: 0.26, foot: true, limb: index });
  }
  const tail = new T.Mesh(taperedTube(
    [[0, 2.20, -2.18], [0.04, 1.76, -2.52], [0.04, 1.44, -2.68]], (t) => 0.09 - 0.05 * t, 20, 8), hideMat);
  g.add(tail);

  /* ---- fur surface: sample the VISIBLE hide only ---- */
  const hideParts = [
    { geo: bodyGeo, test: ellipsoidTest([0, 1.95, -0.15], [1.16, 1.06, 2.15]) },
    { geo: trunkGeo, test: (p) => {
      // the trunk root is buried in the skull: reject those samples
      const hx = p.x / 0.84, hy = (p.y - 2.72) / 0.92, hz = (p.z - 2.10) / 1.00;
      return hx * hx + hy * hy + hz * hz < BURIED * BURIED;
    } },
    { geo: humpGeo, test: ellipsoidTest([0, 2.68, 0.30], [0.88, 0.74, 0.98]) },
    { geo: rumpGeo, test: ellipsoidTest([0, 2.02, -1.70], [0.92, 0.86, 0.92]) },
    { geo: shoulderGeo, test: ellipsoidTest([0, 2.34, 0.55], [1.02, 1.02, 0.95]) },
    { geo: neckGeo, test: capsuleTest([0, 1.91, 1.15], [0, 2.85, 1.49], 0.76) },
    { geo: headGeo, test: ellipsoidTest([0, 2.72, 2.10], [0.84, 0.92, 1.00]) },
    ...domeGeos.map((geo) => ({ geo, test: null })),
  ];
  for (const lg of legGeos) {
    const y0 = lg.foot ? 0.0 : 0.05, y1 = lg.foot ? 0.26 : lg.h + 0.08;
    const r = lg.foot ? 0.40 : 0.37;
    hideParts.push({ geo: lg.geo, limb: lg.limb, test: capsuleTest([lg.x, y0, lg.z + (lg.foot ? 0.05 : 0)], [lg.x, y1, lg.z + (lg.foot ? 0.05 : 0)], r) });
  }
  const surface = sampleVisible(hideParts, Math.round(26000 * PROF.coat));
  // Keep the eye sockets clear of the coat.
  const eyePatch = (p) => {
    for (const sgn of [-1, 1]) {
      const dx = p.x - sgn * 0.545, dy = p.y - 2.855, dz = p.z - 2.80;
      if (dx * dx + dy * dy + dz * dz < 0.030) return true;
    }
    return false;
  };

  const dummy = new T.Object3D();
  const col = new T.Color();
  const up = new T.Vector3(0, 1, 0);

  // Layer A: dense wool curls. Small, rounded, overlapping clumps read as
  // fleece; large faceted solids read as crystal shards, which is what pass 5
  // produced. The primitive is selectable because it is the biggest cost
  // lever left and has to be judged by eye, not by a number.
  const CLUMP = {
    ico: () => new T.IcosahedronGeometry(1, 0),
    octa: () => new T.OctahedronGeometry(1, 0),
    tetra: () => new T.TetrahedronGeometry(1, 0),
    cone: () => new T.ConeGeometry(0.62, 1.5, 5, 1, true),
  };
  const clumpGeo = (CLUMP[PROF.clumpGeom] || CLUMP.ico)();
  const coatGroups = [g, ...legs];
  const coats = coatGroups.map(parent => { const m = new T.InstancedMesh(clumpGeo, furMat, surface.length); parent.add(m); return m; });
  const coatCounts = [0, 0, 0, 0, 0];
  surface.forEach((s) => {
    if (eyePatch(s.p)) return;
    const group = s.part.limb === undefined ? 0 : s.part.limb + 1;
    const i = coatCounts[group]++;
    const n = s.n.clone().add(new T.Vector3(R() - 0.5, R() - 0.5, R() - 0.5).multiplyScalar(0.16)).normalize();
    dummy.position.copy(s.p).addScaledVector(n, 0.006);
    if(group) dummy.position.sub(legs[group - 1].position);
    dummy.quaternion.setFromUnitVectors(up, n);
    dummy.rotateY(R() * Math.PI * 2);
    dummy.rotateX((R() - 0.5) * 0.34);
    dummy.rotateZ((R() - 0.5) * 0.34);
    const sc = (0.021 + R() * 0.012) * PROF.clump;
    dummy.scale.set(sc, sc * (1.5 + R() * 1.3), sc);
    dummy.updateMatrix();
    coats[group].setMatrixAt(i, dummy.matrix);
    col.setHSL(0.072 + R() * 0.026, 0.24 + R() * 0.16, 0.26 + R() * 0.20);
    coats[group].setColorAt(i, col);
  });
  coats.forEach((m, i) => { m.count = coatCounts[i]; });

  // Layer A2: fine underfur. Off by default — the wool-textured hide now
  // covers the gaps this layer existed to cover, and it cost 40,000 clumps
  // (800,000 triangles, over half the frame).
  const underGeo = (CLUMP[PROF.clumpGeom] || CLUMP.ico)();
  const underSurface = []; // not yet rigged
  if (underSurface.length) {
    const under = new T.InstancedMesh(underGeo, furMat, underSurface.length);
    underSurface.forEach((s, i) => {
      const n = s.n.clone().add(new T.Vector3(R() - 0.5, R() - 0.5, R() - 0.5).multiplyScalar(0.20)).normalize();
      dummy.position.copy(s.p).addScaledVector(n, 0.003);
      dummy.quaternion.setFromUnitVectors(up, n);
      dummy.rotateY(R() * Math.PI * 2);
      dummy.rotateX((R() - 0.5) * 0.4);
      dummy.rotateZ((R() - 0.5) * 0.4);
      const sc = 0.010 + R() * 0.009;
      dummy.scale.set(sc, sc * (1.3 + R() * 1.1), sc);
      dummy.updateMatrix();
      under.setMatrixAt(i, dummy.matrix);
      col.setHSL(0.070 + R() * 0.028, 0.22 + R() * 0.16, 0.22 + R() * 0.20);
      under.setColorAt(i, col);
    });
    under.count = underSurface.length;
    g.add(under);
  }

  // Layer B: long guard hairs that break the silhouette against the sky.
  const shagGeo = new T.ConeGeometry(0.012, 0.058, 4, 1, true);
  shagGeo.translate(0, 0.028, 0);
  const shagSurface = PROF.dropShag ? [] : sampleVisible(hideParts, Math.round(11000 * PROF.shag));
  const shags = coatGroups.map(parent => { const m = new T.InstancedMesh(shagGeo, shagMat, shagSurface.length); parent.add(m); return m; });
  const shagCounts = [0, 0, 0, 0, 0];
  shagSurface.forEach((s) => {
    const group = s.part.limb === undefined ? 0 : s.part.limb + 1;
    const i = shagCounts[group]++;
    const n = s.n.clone().add(new T.Vector3(R() - 0.5, R() - 0.5, R() - 0.5).multiplyScalar(0.42)).normalize();
    const dir = n.clone().lerp(new T.Vector3(0, -1, 0), 0.72).normalize();
    dummy.position.copy(s.p).addScaledVector(dir, 0.012);
    if(group) dummy.position.sub(legs[group - 1].position);
    dummy.quaternion.setFromUnitVectors(up, dir);
    dummy.rotateY(R() * Math.PI * 2); dummy.rotateX((R() - 0.5) * 0.3);
    dummy.scale.set(1, (0.5 + R() * 0.55) * (1 - 0.35 * Math.max(0, n.y)), 1);
    dummy.updateMatrix(); shags[group].setMatrixAt(i, dummy.matrix);
    col.setHSL(0.068 + R() * 0.026, 0.24 + R() * 0.14, 0.22 + R() * 0.15);
    shags[group].setColorAt(i, col);
  });
  shags.forEach((m, i) => { m.count = shagCounts[i]; });

  g.userData.trunkTip = new T.Vector3(0.03, 0.78, 2.62);
  g.userData.shag = shags[0];
  g.userData.coat = coats[0];
  g.userData.legs = legs;
  return g;
}

/* ---------- world: floe, sea, snow, breath ---------- */
function floeEdge(a) {
  return 9.4 + Math.sin(a * 3.1) * 1.15 + Math.sin(a * 5.7 + 1.2) * 0.66 + Math.sin(a * 2.3 + 0.4) * 0.85;
}
function buildFloe() {
  const g = new T.Group();
  // Mottled sea-ice texture: without it the floe reads as a sheet of paper.
  const iceTex = canvasTex(512, 512, (g, w, h) => {
    g.fillStyle = '#b6cddc'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 260; i++) {
      const x = R() * w, y = R() * h, r = 8 + R() * 54;
      const grad = g.createRadialGradient(x, y, 0, x, y, r);
      const pale = R() > 0.45;
      grad.addColorStop(0, pale ? 'rgba(255,255,255,0.26)' : 'rgba(84,128,162,0.26)');
      grad.addColorStop(1, 'rgba(255,255,255,0)');
      g.fillStyle = grad; g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
    }
    // pressure cracks
    g.strokeStyle = 'rgba(96,138,170,0.16)';
    for (let i = 0; i < 14; i++) {
      g.lineWidth = 0.5 + R() * 0.9;
      g.beginPath();
      let x = R() * w, y = R() * h;
      g.moveTo(x, y);
      for (let k = 0; k < 4; k++) { x += (R() - 0.5) * 46; y += (R() - 0.5) * 46; g.lineTo(x, y); }
      g.stroke();
    }
    g.fillStyle = 'rgba(255,255,255,0.13)';
    for (let i = 0; i < 700; i++) { g.fillRect(R() * w, R() * h, 1 + R() * 2, 1 + R() * 2); }
  });
  iceTex.wrapS = iceTex.wrapT = T.RepeatWrapping;
  iceTex.repeat.set(3, 3);
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
  const ice = new T.Mesh(geo, new T.MeshStandardMaterial({
    color: 0x93b0c6, map: iceTex, roughness: 0.74, metalness: 0.0
  }));
  g.add(ice);
  const snow = new T.Mesh(geo.clone(), new T.MeshStandardMaterial({
    color: 0xc3d6e4, map: iceTex, roughness: 0.96, transparent: true, opacity: 0.30
  }));
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
  const edge = new T.Mesh(skirt, new T.MeshStandardMaterial({ color: 0x5f89a4, roughness: 0.78, metalness: 0.0, transparent: true, opacity: 0.94 }));
  g.add(edge);
  return g;
}
function buildSea() {
  const geo = new T.PlaneGeometry(2400, 2400, 40, 40);
  geo.rotateX(-Math.PI / 2);
  const mat = new T.MeshStandardMaterial({ color: 0x16394f, roughness: 0.88, metalness: 0.0 });
  const mesh = new T.Mesh(geo, mat);
  mesh.position.y = -1.15;
  return mesh;
}
function buildSnow(count = 1600) {
  const pos = new Float32Array(count * 3);
  const seed = new Float32Array(count);
  for (let i = 0; i < count; i++) {
    pos[i * 3] = (R() - 0.5) * 90; pos[i * 3 + 1] = R() * 16; pos[i * 3 + 2] = (R() - 0.5) * 90;
    seed[i] = R();
  }
  const geo = new T.BufferGeometry();
  geo.setAttribute('position', new T.BufferAttribute(pos, 3));
  const mat = new T.PointsMaterial({ size: 0.115, map: DOT_TEX, transparent: true, opacity: 0.5, depthWrite: false, sizeAttenuation: true, color: 0xdceaf5 });
  const pts = new T.Points(geo, mat);
  pts.userData = { seed, base: pos.slice() };
  return pts;
}
function buildBreath(count = 70) {
  const pos = new Float32Array(count * 3);
  const seed = new Float32Array(count);
  for (let i = 0; i < count; i++) { seed[i] = R(); }
  const geo = new T.BufferGeometry();
  geo.setAttribute('position', new T.BufferAttribute(pos, 3));
  const mat = new T.PointsMaterial({ size: 0.52, map: DOT_TEX, transparent: true, opacity: 0.14, depthWrite: false, color: 0xcfe4f2 });
  const pts = new T.Points(geo, mat);
  pts.userData = { seed, count };
  return pts;
}

// Procedural coastal terrain, a visual reconstruction rather than a geographic map.
function buildTundra() {
  const root = new T.Group();
  const N = 150, SIZE = 180, geo = new T.PlaneGeometry(SIZE, SIZE, N, N);
  geo.rotateX(-Math.PI / 2);
  const pos = geo.attributes.position, colors = [];
  const c = new T.Color();
  function height(x,z) {
    const r = Math.hypot(x * 0.80, z * 1.05);
    const slope = -Math.max(0, r - 34) * 0.21;
    const mountain = 8.0 * Math.exp(-((x+17)**2/380 + (z+28)**2/155)) + 5.6 * Math.exp(-((x-23)**2/190 + (z+35)**2/170));
    const details = (vnoise(x*.13,z*.13)-.5)*.7 + (vnoise(x*.33+19,z*.33)-.5)*.17;
    const fade = Math.min(1, Math.max(0, (r-6)/9));
    return slope + mountain + details*fade;
  }
  for(let i=0;i<pos.count;i++) {
    const x=pos.getX(i), z=pos.getZ(i), y=height(x,z); pos.setY(i,y);
    const frost = Math.min(1,Math.max(0, .40 + y*.09 + (vnoise(x*.08+12,z*.08)-.5)*.45));
    c.setRGB(.18+frost*.45,.20+frost*.46,.20+frost*.48); colors.push(c.r,c.g,c.b);
  }
  geo.setAttribute('color', new T.Float32BufferAttribute(colors,3)); geo.computeVertexNormals();
  root.add(new T.Mesh(geo,new T.MeshStandardMaterial({map:tundraMap, roughness:1})));
  // Scattered rocks and low vegetation are real meshes; deterministic seed keeps
  // offline frame rendering stable. Avoid the animal's immediate footprint.
  const rockGeo=lumpy(new T.IcosahedronGeometry(1,1), .2, 1), rockMat=new T.MeshStandardMaterial({color:0x626a65,roughness:1});
  const rocks=new T.InstancedMesh(rockGeo,rockMat,420), dummy=new T.Object3D(); let k=0;
  for(let i=0;i<420;i++){const x=(R()-.5)*100,z=(R()-.5)*100,y=height(x,z); if(y < -.8 || Math.hypot(x,z)<6)continue;
    dummy.position.set(x,y+.07,z); dummy.rotation.set(R(),R()*6,R()); const q=.12+R()*.55;dummy.scale.set(q*1.5,q*.5,q);dummy.updateMatrix();rocks.setMatrixAt(k++,dummy.matrix);}
  rocks.count=k;root.add(rocks);
  const bladeGeo = new T.BufferGeometry();
  const bp=[];for(let i=0;i<5;i++){const a=i*Math.PI/5, dx=Math.cos(a)*.09,dz=Math.sin(a)*.09;bp.push(-dx,0,-dz, dx,0,dz, dx*.35,.52,dz*.35);}
  bladeGeo.setAttribute('position',new T.Float32BufferAttribute(bp,3));bladeGeo.computeVertexNormals();
  const blades=new T.InstancedMesh(bladeGeo,new T.MeshStandardMaterial({color:0x857857,roughness:1,side:T.DoubleSide}),1800);k=0;
  for(let i=0;i<1800;i++){const x=(R()-.5)*68,z=(R()-.5)*68,y=height(x,z);if(y < -.4 || Math.hypot(x,z)<4)continue;
    dummy.position.set(x,y+.18,z);dummy.rotation.set((R()-.5)*.28,R()*6,(R()-.5)*.28);const q=.45+R()*.8;dummy.scale.set(q,q,q);dummy.updateMatrix();blades.setMatrixAt(k++,dummy.matrix);}
  blades.count=k;root.add(blades);
  return root;
}

const world = new T.Group();
// QC helper: ?hide=mist,snow isolates a suspected artefact without a rebuild.
{
  const hide = new URLSearchParams(location.search).get('hide');
  if (hide) window.__hide = new Set(hide.split(',').map((s) => s.trim()));
}
const floe = buildTundra(); world.add(floe);
const sea = buildSea(); world.add(sea);

const mammoth = buildMammoth(); mammoth.position.set(0, 0, 0); mammoth.rotation.y = -0.62; world.add(mammoth);
const snow = buildSnow(); world.add(snow);
const breath = buildBreath(); world.add(breath);
const mistTex = canvasTex(512, 256, (g, w, h) => {
  const grad = g.createLinearGradient(0, h, 0, 0);
  grad.addColorStop(0, 'rgba(150,195,220,0.85)');
  grad.addColorStop(0.45, 'rgba(120,170,205,0.34)');
  grad.addColorStop(1, 'rgba(90,140,180,0)');
  g.fillStyle = grad; g.fillRect(0, 0, w, h);
});
const mist = new T.Mesh(new T.PlaneGeometry(420, 34), new T.MeshBasicMaterial({ map: mistTex, transparent: true, depthWrite: false, opacity: 0.55 }));
mist.position.set(0, 7, -150);
world.add(mist);
const shadow = new T.Mesh(new T.PlaneGeometry(9, 13), new T.MeshBasicMaterial({ map: DOT_TEX, transparent: true, opacity: 0.42, depthWrite: false, color: 0x03080d }));
shadow.rotation.x = -Math.PI / 2; shadow.position.set(0, 0.08, 0.2); world.add(shadow);
scene.add(world);

// Light budget. The most important lights are kept; the rest are switched
// off and the survivors are brightened to keep the exposure roughly where it
// was, so the picture changes far less than the frame time does.
{
  const order = lightRig
    .map((l, i) => ({ l, i, p: l.userData.priority }))
    .sort((a, b) => a.p - b.p);
  const keep = new Set(order.slice(0, Math.max(1, Math.round(PROF.lights))).map((o) => o.i));
  lightRig.forEach((l, i) => {
    l.visible = keep.has(i);
    l.userData.gain = keep.has(i) ? Math.pow(2, (order.length - keep.size) / order.length * 0.42) : 0;
  });
}

/* ---------- DNA helix ---------- */
function buildHelix(radius, height, turns, color, emissive = 1) {
  const g = new T.Group();
  const pts = [];
  const steps = 140;
  for (let i = 0; i <= steps; i++) {
    const t = i / steps, a = t * Math.PI * 2 * turns;
    pts.push(new T.Vector3(Math.cos(a) * radius, t * height - height / 2, Math.sin(a) * radius));
  }
  const curve = new T.CatmullRomCurve3(pts);
  const mat = new T.MeshStandardMaterial({
    color: 0x0c2f49, emissive: color, emissiveIntensity: emissive, roughness: 0.35, metalness: 0.05,
    transparent: true, opacity: 1
  });
  const strandA = new T.Mesh(new T.TubeGeometry(curve, 180, 0.032, 8, false), mat.clone());
  const strandB = new T.Mesh(new T.TubeGeometry(curve, 180, 0.055, 8, false), mat.clone());
  // Taper a tube to a point at both ends by pulling each ring toward the
  // centre-line. The radial direction is (vertex - curvePoint), NOT the vertex
  // normal: a tube's normal is perpendicular to the sweep, so using it shears
  // the tube apart instead of shrinking it.
  const taperEnds = (geo, curve, rows = 181, ring = 9) => {
    const pos = geo.attributes.position;
    const c = new T.Vector3();
    for (let r = 0; r < rows; r++) {
      const t = r / (rows - 1);
      const edge = Math.min(t, 1 - t);
      const k = Math.min(1, edge / 0.07);
      if (k >= 1) continue;
      const kk = k * k * (3 - 2 * k);
      curve.getPointAt(t, c);
      for (let j = 0; j < ring; j++) {
        const i = r * ring + j;
        if (i >= pos.count) break;
        pos.setXYZ(i,
          c.x + (pos.getX(i) - c.x) * kk,
          c.y + (pos.getY(i) - c.y) * kk,
          c.z + (pos.getZ(i) - c.z) * kk);
      }
    }
    geo.computeVertexNormals();
    return geo;
  };
  const p2 = [];
  for (let i = 0; i <= steps; i++) {
    const t = i / steps, a = t * Math.PI * 2 * turns + Math.PI;
    p2.push(new T.Vector3(Math.cos(a) * radius, t * height - height / 2, Math.sin(a) * radius));
  }
  const curve2 = new T.CatmullRomCurve3(p2);
  strandB.geometry = taperEnds(new T.TubeGeometry(curve2, 180, 0.032, 8, false), curve2);
  taperEnds(strandA.geometry, curve);
  g.add(strandA, strandB);
  const rungGeo = new T.CylinderGeometry(0.0075, 0.0075, 1, 6);
  const rungs = new T.InstancedMesh(rungGeo, mat.clone(), 24);
  const d = new T.Object3D();
  for (let i = 0; i < 24; i++) {
    const t = i / 23, a = t * Math.PI * 2 * turns;
    const p = new T.Vector3(Math.cos(a) * radius, t * height - height / 2, Math.sin(a) * radius);
    const q = new T.Vector3(Math.cos(a + Math.PI) * radius, t * height - height / 2, Math.sin(a + Math.PI) * radius);
    d.position.copy(p).add(q).multiplyScalar(0.5);
    d.scale.set(1, p.distanceTo(q), 1);
    d.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), q.clone().sub(p).normalize());
    d.updateMatrix(); rungs.setMatrixAt(i, d.matrix);
  }
  g.add(rungs);
  g.userData = { curve, strandA, strandB, rungs, mat };
  return g;
}
const helix = buildHelix(0.38, 1.8, 2.1, 0x2fb8e8, 0.78);
helix.position.set(0.28, 2.42, 1.55);
helix.visible = false;
world.add(helix);

/* ---------- graph space: case board, panels, arcs ---------- */
const graph = new T.Group();
graph.visible = false;
scene.add(graph);

const boardTex = canvasTex(1024, 640, (g, w, h) => {
  g.fillStyle = '#070d14'; g.fillRect(0, 0, w, h);
  g.strokeStyle = 'rgba(120,160,190,0.10)'; g.lineWidth = 1;
  for (let x = 0; x < w; x += 42) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); }
  for (let y = 0; y < h; y += 42) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); }
  const grad = g.createRadialGradient(w * 0.5, h * 0.45, 40, w * 0.5, h * 0.45, w * 0.75);
  grad.addColorStop(0, 'rgba(40,90,120,0.32)'); grad.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = grad; g.fillRect(0, 0, w, h);
});
const backdropTex = canvasTex(1024, 640, (g, w, h) => {
  const grad = g.createRadialGradient(w * 0.42, h * 0.46, 30, w * 0.5, h * 0.5, w * 0.72);
  grad.addColorStop(0, '#16344c');
  grad.addColorStop(0.45, '#0b1f30');
  grad.addColorStop(1, '#040a11');
  g.fillStyle = grad; g.fillRect(0, 0, w, h);
});
const backdrop = new T.Mesh(new T.PlaneGeometry(42, 24), new T.MeshBasicMaterial({ map: backdropTex, depthWrite: false }));
backdrop.position.set(0, 0, -4.2);
graph.add(backdrop);
const board = new T.Mesh(new T.PlaneGeometry(13.4, 7.6), new T.MeshStandardMaterial({ map: boardTex, roughness: 0.9, transparent: true, opacity: 0.5 }));
board.position.set(0, 0, -1.4);
graph.add(board);

function cardMesh(title, sub, accent, w = 2.5, h = 1.45, titleSize = 132, subSize = 52, plate = true) {
  const tex = textPlate([title, sub], { w: 1000, h: 580, titleSize, subSize, accent, center: true, color: '#f6f1e6', plate });
  // graph space carries no lights, so these plates are unlit on purpose
  const mat = new T.MeshBasicMaterial({ map: tex, transparent: true, side: T.DoubleSide });
  const mesh = new T.Mesh(new T.PlaneGeometry(w, h), mat);
  return mesh;
}
const witnessData = [
  ['GENOME', '2017 · damage', '#8fd6ff'],
  ['CLIMATE', '2019 · ice + water', '#9fe8c6'],
  ['HUMANS', 'earliest evidence', '#ffb27a'],
  ['21 GENOMES', '2024 · recovered', '#c9a7ff'],
];
const cards = witnessData.map((d, i) => {
  const m = cardMesh(d[0], d[1], d[2]);
  m.userData.home = new T.Vector3(-3.35 + i * 2.24, 0.62, 0);
  m.userData.delay = i * 0.07;
  m.visible = false;
  graph.add(m);
  return m;
});
// red string between witness cards
const strings = new T.Group();
graph.add(strings);
for (let i = 0; i < cards.length - 1; i++) {
  const a = cards[i].userData.home.clone().setY(cards[i].userData.home.y - 0.62);
  const b = cards[i + 1].userData.home.clone().setY(cards[i + 1].userData.home.y - 0.62);
  const mid = a.clone().lerp(b, 0.5); mid.y -= 0.34;
  const curve = new T.CatmullRomCurve3([a.clone().setZ(-0.06), mid, b.clone().setZ(-0.06)]);
  const str = new T.Mesh(new T.TubeGeometry(curve, 24, 0.018, 6, false), new T.MeshStandardMaterial({ color: 0xc2453c, emissive: 0x8e1f18, emissiveIntensity: 0.5, roughness: 0.7 }));
  strings.add(str);
}

// empty slot: the fifth evidence slot, framed and lit, with nothing inside it
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
  g.fillText('final ten generations: no sampled genomes', w / 2, h * 0.74);
});
const slotHeadMat = new T.MeshBasicMaterial({ map: slotHeadTex, transparent: true, depthWrite: false });
const slotHead = new T.Mesh(new T.PlaneGeometry(2.12, 0.454), slotHeadMat);
slotHead.position.set(0, 0.29, 0.03);
slotHead.renderOrder = 3;
slot.add(slotHead);
const frag = buildHelix(0.2, 0.72, 1.2, 0xffc79a, 1.4);
frag.position.set(0, -0.37, 0.0);
frag.renderOrder = 1;
slot.add(frag);
const dust = (() => {
  const n = 220, pos = new Float32Array(n * 3), seed = new Float32Array(n);
  for (let i = 0; i < n; i++) { pos[i * 3] = (R() - 0.5) * 1.6; pos[i * 3 + 1] = (R() - 0.5) * 1.3; pos[i * 3 + 2] = (R() - 0.5) * 0.6; seed[i] = R(); }
  const geo = new T.BufferGeometry(); geo.setAttribute('position', new T.BufferAttribute(pos, 3));
  const p = new T.Points(geo, new T.PointsMaterial({ size: 0.09, map: DOT_TEX, transparent: true, opacity: 0.7, depthWrite: false, color: 0xffc79a }));
  p.userData = { seed, base: pos.slice(), n };
  p.renderOrder = 1;
  slot.add(p);
  return p;
})();
graph.add(slot);

// two-truth panels
const truths = new T.Group();
const panelA = cardMesh('DAMAGED', 'measured, real', '#ff8f7a', 3.4, 1.95);
panelA.position.set(-2.75, 0.5, 0.2);
const panelB = cardMesh('RECOVERED', 'also measured', '#7fe3ff', 3.4, 1.95);
panelB.position.set(2.75, 0.5, 0.2);
truths.add(panelA, panelB);
truths.visible = false;
graph.add(truths);

// genome ribbon: a curve that falls then rises
const ribbon = (() => {
  const g = new T.Group();
  const pts = [];
  for (let i = 0; i <= 60; i++) {
    const t = i / 60;
    const y = t < 0.42 ? 1.45 - 3.05 * smooth(t / 0.42) : -1.60 + 3.05 * smooth((t - 0.42) / 0.58);
    pts.push(new T.Vector3(-6 + t * 12, y, Math.sin(t * 7) * 0.22));
  }
  const curve = new T.CatmullRomCurve3(pts);
  const tube = new T.Mesh(new T.TubeGeometry(curve, 200, 0.045, 8, false), new T.MeshStandardMaterial({ color: 0x7fe3ff, emissive: 0x2e7f9c, emissiveIntensity: 1.1, roughness: 0.35 }));
  g.add(tube);
  const marker = new T.Mesh(new T.SphereGeometry(0.17, 20, 16), new T.MeshBasicMaterial({ color: 0xffe7b0 }));
  g.add(marker);
  // labels that explain the curve instead of leaving the viewer to guess
  const labels = [
    ['BOTTLENECK', 'modelled population', new T.Vector3(-2.5, 2.05, 0), '#ff8f7a'],
    ['RECOVERY', 'effective population', new T.Vector3(2.9, 2.05, 0), '#7fe3ff'],
  ];
  for (const [title, sub, pos, accent] of labels) {
    const tex = textPlate([title, sub], { w: 1000, h: 300, titleSize: 92, subSize: 46, accent, center: true });
    const m = new T.Mesh(new T.PlaneGeometry(3.4, 1.02), new T.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false }));
    m.position.copy(pos);
    g.add(m);
  }
  const valley = new T.Mesh(new T.PlaneGeometry(0.03, 3.4), new T.MeshBasicMaterial({ color: 0xff8f7a, transparent: true, opacity: 0.5 }));
  valley.position.set(-1.5, 0, 0);
  g.add(valley);
  g.userData = { curve, marker, tube };
  g.visible = false;
  graph.add(g);
  return g;
})();

// four arcs: the four lines of evidence, hung on one timeline
const ARC_X = [-3.72, -1.24, 1.24, 3.72];
const ARC_RAIL_Y = 1.28;
const arcRail = new T.Mesh(new T.BoxGeometry(9.5, 0.05, 0.05), new T.MeshBasicMaterial({ color: 0x8fd6ff, transparent: true, opacity: 0.6 }));
arcRail.position.set(-4.75, ARC_RAIL_Y, -0.5);
arcRail.visible = false;
graph.add(arcRail);
const arcData = [
  ['2017', 'DAMAGE', '#ff8f7a'],
  ['2019', 'STABLE, THEN ICE', '#9fe8c6'],
  ['3,600 BP', 'HUMANS EVIDENCE', '#ffb27a'],
  ['2024', 'RECOVERED', '#8fd6ff'],
];
const arcCards = arcData.map((d, i) => {
  const m = cardMesh(d[0], d[1], d[2], 2.32, 1.35, 100, 38);
  m.userData.home = new T.Vector3(ARC_X[i], 0.34, 0.1);
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
});

/* ---------- screen overlays + captions (camera-attached) ---------- */
const visHeightAt = (d) => 2 * d * Math.tan((camera.fov * Math.PI / 180) / 2);
const OVERLAY_DIST = 9;
const overlayGroup = new T.Group();
camera.add(overlayGroup);
scene.add(camera);
const overlays = S.overlays.map((o) => {
  // A plated overlay gets a wider canvas so the longest headline always fits
  // inside its own plate.
  const ow = o.plate ? 1700 : 1400;
  const tex = textPlate([o.text, o.sub], {
    w: ow, h: 460, titleSize: Math.round(150 * (o.size / 0.62)), subSize: 54, accent: o.accent,
    center: true, color: '#f4efe4', subColor: 'rgba(222,233,242,0.78)',
    plate: !!o.plate
  });
  const mat = new T.MeshBasicMaterial({ map: tex, transparent: true, depthTest: false, opacity: 0 });
  const mesh = new T.Mesh(new T.PlaneGeometry(1, 1), mat);
  const vh = visHeightAt(OVERLAY_DIST), vw = vh * (W / H);
  const wWorld = vw * (o.size / 0.62) * 0.62 * (o.plate ? 1400 / ow : 1);
  const hWorld = wWorld * (460 / ow);
  mesh.scale.set(wWorld, hWorld, 1);
  mesh.position.set((o.fx - 0.5) * vw, (o.fy - 0.5) * vh, -OVERLAY_DIST);
  mesh.renderOrder = 10;
  overlayGroup.add(mesh);
  return { def: o, mesh, mat };
});

const captionCanvas = document.createElement('canvas');
captionCanvas.width = 1700; captionCanvas.height = 220;
const captionCtx = captionCanvas.getContext('2d');
const captionTex = new T.CanvasTexture(captionCanvas);
captionTex.colorSpace = T.SRGBColorSpace;
const captionMat = new T.MeshBasicMaterial({ map: captionTex, transparent: true, depthTest: false, opacity: 0 });
const captionMesh = new T.Mesh(new T.PlaneGeometry(1, 1), captionMat);
{
  const vh = visHeightAt(OVERLAY_DIST), vw = vh * (W / H);
  const wWorld = vw * 0.82, hWorld = wWorld * (220 / 1700);
  captionMesh.scale.set(wWorld, hWorld, 1);
  captionMesh.position.set(0, -vh * 0.435, -OVERLAY_DIST);
  captionMesh.renderOrder = 11;
  overlayGroup.add(captionMesh);
}
let captionKey = null;
function drawCaption(text) {
  const g = captionCtx;
  const W2 = captionCanvas.width, H2 = captionCanvas.height;
  g.clearRect(0, 0, W2, H2);
  g.font = '800 62px Manrope';
  const tw = g.measureText(text).width;
  const padX = 42, padY = 22;
  g.fillStyle = 'rgba(4,11,17,0.62)';
  g.beginPath();
  g.roundRect((W2 - tw) / 2 - padX, H2 / 2 - 44, tw + padX * 2, 88, 14);
  g.fill();
  g.fillStyle = 'rgba(150,200,230,0.55)';
  g.fillRect((W2 - tw) / 2 - padX, H2 / 2 + 38, tw + padX * 2, 2);
  g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillStyle = '#f6efe2';
  g.fillText(text, W2 / 2, H2 / 2 - 2);
  captionTex.needsUpdate = true;
}

/* ---------- camera language per shot ---------- */
const CAM = {
  'island': { from: [[18, 12, 35], [11, 9, 23]], look: [[0, 0, 0], [0, 1, 0]] },
  'shore': { from: [[-8, 1.0, 15], [-5, 1.8, 12]], look: [[-0.8, 1.9, 0], [-0.5, 2.0, 0]] },
  'coast': { from: [[8, 4, 15], [4.5, 3, 11]], look: [[0, 1.7, 0], [0, 2.0, 0]] },
  'animal': { from: [[-2.8, 2.8, 10.8], [1.2, 2.5, 8.7]], look: [[-0.3, 2.1, 1], [0, 2.2, 1.5]] },
};

/* ---------- per-frame update ---------- */
const ease3 = (u) => u * u * (3 - 2 * u);
function setWorldVisible(v) { world.visible = v; sky.visible = v; }
function updateWorld(t, u, kind) {
  // snow drift
  const sp = snow.geometry.attributes.position, base = snow.userData.base, seed = snow.userData.seed;
  for (let i = 0; i < seed.length; i++) {
    const s = seed[i];
    const y = ((base[i * 3 + 1] - t * (0.5 + s * 0.8)) % 16 + 16) % 16;
    sp.setXYZ(i, base[i * 3] + Math.sin(t * 0.6 + s * 6.2) * 1.6, y, base[i * 3 + 2] + Math.cos(t * 0.45 + s * 5.1) * 1.2);
  }
  sp.needsUpdate = true;
  // breath puffs from the trunk
  const bp = breath.geometry.attributes.position, bs = breath.userData.seed;
  const tip = mammoth.userData.trunkTip.clone().applyEuler(mammoth.rotation).add(mammoth.position);
  for (let i = 0; i < bs.length; i++) {
    const life = (t * 0.34 + bs[i]) % 1;
    const spread = life * 1.9;
    bp.setXYZ(i,
      tip.x + Math.sin(bs[i] * 31 + life * 2.2) * spread * 0.55,
      tip.y + life * 1.35 + Math.sin(bs[i] * 17) * 0.18,
      tip.z + Math.cos(bs[i] * 23 + life * 1.6) * spread * 0.5 + life * 0.7);
  }
  bp.needsUpdate = true;
  breath.material.opacity = 0.11 + 0.04 * Math.sin(t * 1.7);
  // sea level: rises during the island shot
  const seaRise = kind === 'island' ? ease(u) * 0.95 : (kind === 'resolve' ? 0.95 : 0);
  sea.position.y = -1.15 + seaRise;
  sea.material.roughness = 0.88;
  // helix around the shoulder appears in the macro shot
  const helixGrow = 0;
  helix.visible = helixGrow > 0.01;
  if (helix.visible) {
    helix.scale.setScalar(0.45 + helixGrow * 0.95);
    helix.rotation.y = t * 0.55;
    helix.userData.strandA.material.opacity = helixGrow;
    helix.userData.strandB.material.opacity = helixGrow;
    helix.userData.rungs.material.opacity = helixGrow;
    helix.position.set(0.26, 2.46, 1.62);
  }
  // The proposed coat phenotype is an inference, not observed hair loss.
  // Keep the illustrative coat stable while the DNA graphic appears.
  mammoth.userData.shag.material.opacity = 1;
  mammoth.userData.shag.position.y = 0;
  // Exploratory joint motion; paws are not yet inverse-kinematics constrained.
  const phase = t * 1.25;
  mammoth.userData.legs.forEach((leg, i) => { leg.rotation.x = Math.sin(phase + [0, Math.PI, Math.PI, 0][i]) * 0.10; });
  // slow body sway so the animal feels alive
  mammoth.rotation.y = -0.62 + Math.sin(t * 0.32) * 0.04;
  mammoth.position.y = Math.sin(t * 0.9) * 0.035;
  warm.intensity = 5 + Math.sin(t * 1.3) * 0.7;
  key.intensity = 2.6 + Math.sin(t * 0.4) * 0.12;
  // The wool rig leans in as the camera closes on the animal.
  const close = kind === 'shoulder' ? 1 : kind === 'resolve' ? 0.7 : 0.42;
  woolKey.intensity = 2.5 * close * (woolKey.userData.gain || 1);
  woolFill.intensity = 1.15 * close * (woolFill.userData.gain || 1);
}

function updateGraph(t, u, kind) {
  board.material.opacity = 0.24;
  backdrop.visible = true;
  strings.visible = kind === 'witnesses';
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
    c.material.opacity = e;
    if (kind === 'promise') {
      // compact row, clear of the three verdict columns below
      c.scale.setScalar(0.72);
      c.position.y = 1.42 + lerp(0.7, 0, e);
      c.position.z = -0.5 + lerp(-1.0, 0, e);
    } else {
      c.scale.setScalar(1);
    }
  });
  // empty slot glow + dissolving dust
  const slotOn = kind === 'empty' || kind === 'promise';
  slot.visible = slotOn;
  slotHead.visible = kind === 'empty';
  if (slotOn) {
    const p = 0.55 + 0.45 * Math.sin(t * 2.1);
    slot.position.y = kind === 'promise' ? -0.18 : -0.9;
    slot.scale.setScalar(kind === 'empty' ? 1.55 : 0.52);
    slotFrameMat.opacity = kind === 'promise' ? 0.3 : 0.55 + 0.4 * p;
    slotGlowMat.opacity = kind === 'promise' ? 0.10 : 0.18 + 0.16 * p;
    slotHeadMat.opacity = kind === 'empty' ? clamp((u - 0.28) / 0.16) : 0;
    frag.rotation.y = t * 0.9;
    frag.scale.setScalar(0.65 * (1 - 0.35 * ((t * 0.5) % 1)));
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
  }
  // two truths
  truths.visible = kind === 'truths';
  if (truths.visible) {
    const e = ease(u);
    panelA.position.x = lerp(-0.4, -2.5, e);
    panelB.position.x = lerp(0.4, 2.5, e);
    panelA.material.opacity = e; panelB.material.opacity = e;
  }
  // genome ribbon
  ribbon.visible = kind === 'genome';
  if (ribbon.visible) {
    const p = clamp(u * 1.12);
    const pt = ribbon.userData.curve.getPointAt(Math.min(p, 1));
    ribbon.userData.marker.position.copy(pt);
    ribbon.userData.tube.material.opacity = clamp(u * 4);
  }
  // four arcs: the rail draws, then each line of evidence drops onto it
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
  });
}

function applyCamera(shot, u) {
  const cam = CAM[shot.id];
  if (!cam) return;
  const e = ease3(u);
  camera.position.copy(mixV(cam.from[0], cam.from[1], e));
  camera.lookAt(mixV(cam.look[0], cam.look[1], e));
  const fov = shot.id === 'shoulder-wool' ? 35 : shot.id === 'resolve' ? 42 : 38;
  if (Math.abs(camera.fov - fov) > 0.01) { camera.fov = fov; camera.updateProjectionMatrix(); }
}

function updateOverlays(t) {
  overlays.forEach((o) => {
    const d = o.def;
    const on = t >= d.start && t <= d.end;
    o.mesh.visible = on;
    if (!on) { o.mat.opacity = 0; return; }
    const inFade = clamp((t - d.start) / 0.5);
    const outFade = clamp((d.end - t) / 0.6);
    const a = Math.min(inFade, outFade);
    o.mat.opacity = a;
    const rise = (1 - ease(inFade)) * 0.16;
    const vh = visHeightAt(OVERLAY_DIST), vw = vh * (W / H);
    o.mesh.position.y = (d.fy - 0.5) * vh + rise;
  });
}

function updateCaption(t) {
  const c = S.captions.find((c) => t >= c.start && t < c.end);
  const key = c ? c.text : null;
  if (key !== captionKey) { captionKey = key; if (c) drawCaption(c.text); }
  captionMat.opacity = c ? 1 : 0;
}

function paint(frame) {
  const started = performance.now();
  const t = Math.max(0, Math.min(S.duration - 0.0001, frame / FPS));
  const shot = S.shots.find((s) => t >= s.start && t < s.end) || S.shots[S.shots.length - 1];
  const u = (t - shot.start) / (shot.end - shot.start);
  const graphShot = false;
  setWorldVisible(!graphShot);
  graph.visible = graphShot;
  if (!graphShot) {
    updateWorld(t, u, shot.kind);
  } else {
    updateGraph(t, u, shot.kind);
    // keep a faint helix in the graph space for the 'strange part' beat
    const g2 = slot.userData ? null : null;
  }
  if (shot.kind === 'strange') {
    // a large split helix in graph space
    if (!window.__bigHelix) {
      // Integer turns so the two strands close without a kink, saturated cyan so
      // the graphic survives ACES tone mapping, and a halo so it sits in frame.
      const big = buildHelix(1.05, 4.0, 3, 0x2fc4f0, 0.92);
      big.position.set(0, 0.2, 0);
      const halo = new T.Mesh(new T.PlaneGeometry(6.4, 7.6), new T.MeshBasicMaterial({
        map: DOT_TEX, color: 0x1c6f96, transparent: true, opacity: 0.30,
        depthWrite: false, blending: T.AdditiveBlending
      }));
      halo.position.set(0, 0.2, -1.1);
      big.add(halo);
      const halo2 = new T.Mesh(new T.PlaneGeometry(4.2, 5.0), new T.MeshBasicMaterial({
        map: DOT_TEX, color: 0x36a9d8, transparent: true, opacity: 0.26,
        depthWrite: false, blending: T.AdditiveBlending
      }));
      halo2.position.set(0, 0.2, -0.9);
      big.add(halo2);
      graph.add(big);
      window.__bigHelix = big;
    }
    window.__bigHelix.visible = true;
    window.__bigHelix.rotation.y = t * 0.5;
  } else if (window.__bigHelix) {
    window.__bigHelix.visible = false;
  }
  applyCamera(shot, clamp(u));
  updateOverlays(t);
  updateCaption(t);
  renderer.render(scene, camera);
  window.__state = {
    frame, time: t, shot: shot.id, kind: shot.kind,
    graph: graphShot, caption: captionKey,
    timings: { frame: performance.now() - started }
  };
}

window.__seek = paint;
window.__ready = true;
// Measurement handle for the render-cost bench (see _bench.mjs). Read-only
// pointers; nothing in the film path depends on it.
window.__dbg = { scene, renderer, camera, T };
paint(0);


/* QC isolation helper: ?hide=mist,snow,breath,shadow,sky,sea,floe */
window.__applyHides = function () {
  if (!window.__hide) return;
  const map = { sea, mist, snow, breath, shadow, sky, floe, mammoth };
  for (const [k, obj] of Object.entries(map)) {
    if (obj) obj.visible = !window.__hide.has(k);
  }
};
window.__applyHides();
