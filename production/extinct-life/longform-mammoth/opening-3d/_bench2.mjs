// Bench v2 — prices each render cost driver separately, with warm-up so the
// first-frame shader compile does not pollute the numbers.
//
// Usage: node _bench2.mjs
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { chromium } from 'playwright';
import serverChromium from '@sparticuz/chromium';

const ROOT = process.cwd();
const BASE = path.join(ROOT, 'production/extinct-life/longform-mammoth/opening-3d');
const CACHE = path.join(ROOT, '.cache/longform-mammoth-opening');

const server = http.createServer((req, res) => {
  const u = new URL(req.url, 'http://local');
  const name = decodeURIComponent(u.pathname);
  if (name.includes('..')) return res.writeHead(403).end();
  const files = {
    '/': path.join(BASE, 'stage.html'),
    '/three.module.js': path.join(ROOT, 'node_modules/three/build/three.module.js'),
    '/three.core.js': path.join(ROOT, 'node_modules/three/build/three.core.js'),
    '/Manrope.ttf': path.join(ROOT, 'public/showreel/fonts/Manrope-800.ttf'),
    '/Anton.ttf': path.join(ROOT, 'public/showreel/fonts/Anton-Regular.ttf'),
    '/timeline.json': path.join(BASE, 'timeline.json'),
    '/mix.wav': path.join(CACHE, 'mix.wav'),
  };
  let f = files[name];
  if (!f) {
    if (name.startsWith('/assets/')) f = path.join(BASE, 'assets', name.slice(8));
    else if (name.startsWith('/addons/')) f = path.join(ROOT, 'node_modules/three/examples/jsm', name.slice(8));
    else f = path.join(BASE, name);
  }
  if (!fs.existsSync(f) || fs.statSync(f).isDirectory()) return res.writeHead(404).end();
  res.setHeader('Content-Type', ({ '.mjs': 'application/javascript', '.js': 'application/javascript', '.html': 'text/html', '.json': 'application/json', '.ttf': 'font/ttf', '.wav': 'audio/wav' })[path.extname(f)] || 'application/octet-stream');
  fs.createReadStream(f).pipe(res);
});
await new Promise((r) => server.listen(0, '0.0.0.0', r));

const browser = await chromium.launch({
  executablePath: await serverChromium.executablePath(),
  env: { ...process.env, LD_LIBRARY_PATH: path.join(ROOT, '.cache/extinct-v14/libs/lib') },
  args: [...serverChromium.args, '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-dev-shm-usage'],
  headless: true,
});
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
page.on('pageerror', (e) => console.error('PAGEERROR', e.message));
page.on('console', (m) => { if (m.type() === 'error') console.error('CONSOLE', m.text().slice(0, 200)); });
await page.goto('http://127.0.0.1:' + server.address().port);
await page.waitForFunction(() => window.__ready, null, { timeout: 600000, polling: 500 });

await page.evaluate(() => {
  const { renderer, scene, T } = window.__dbg;
  window.__b = {
    fur: [], lights: [], meshes: [],
    frame(f) { window.__seek(f); const gl = renderer.getContext(); const px = new Uint8Array(4); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); },
    ms(frames) { const t0 = performance.now(); for (const f of frames) this.frame(f); return (performance.now() - t0) / frames.length; },
    collect() {
      this.fur = []; this.lights = []; this.meshes = [];
      scene.traverse((o) => {
        if (o.isInstancedMesh) this.fur.push(o);
        if (o.isLight) this.lights.push(o);
      });
      return { fur: this.fur.length, lights: this.lights.length };
    },
    // name the instanced meshes by their instance count so we can address them
    label() { return this.fur.map((m, i) => i + ':' + m.count).join(' '); },
    setMat(kind) {
      const m = new (kind === 'phong' ? T.MeshPhongMaterial : kind === 'lambert' ? T.MeshLambertMaterial : T.MeshStandardMaterial)(
        kind === 'phong' ? { color: 0xffffff, shininess: 4, specular: 0x1a1208 }
          : kind === 'lambert' ? { color: 0xffffff }
            : { color: 0xffffff, roughness: 0.92, metalness: 0.0 });
      this.fur.forEach((x) => { x.material = m; });
      return kind;
    },
    setFurScale(k) { this.fur.forEach((x) => { x.count = Math.max(1, Math.round(x.userData.baseCount * k)); }); },
    setLightCount(n) { this.lights.forEach((l, i) => { l.visible = i < n; }); },
  };
  window.__b.collect();
  window.__b.fur.forEach((m) => { m.userData.baseCount = m.count; });
});

const FRAMES = [100, 180, 200, 260, 340, 480, 510, 600, 780, 1000, 1290, 1600];
const R = {};
const warm = await page.evaluate(() => window.__b.ms([100, 100, 100, 100]));
const out = { warmup_ms: warm, fur: await page.evaluate(() => window.__b.label()), lights: await page.evaluate(() => window.__b.collect().lights) };

const measure = async (tag, setup) => {
  if (setup) await page.evaluate(setup);
  await page.evaluate(() => window.__b.ms([100, 200, 300]));
  out[tag] = await page.evaluate((f) => window.__b.ms(f), FRAMES);
  console.log(tag.padEnd(26), out[tag].toFixed(0), 'ms/frame');
};

await measure('baseline');

// --- material cost ---
await measure('fur_phong', () => window.__b.setMat('phong'));
await measure('fur_lambert', () => window.__b.setMat('lambert'));
await measure('fur_standard', () => window.__b.setMat('standard'));

// --- light cost ---
await measure('lights_1', () => window.__b.setLightCount(1));
await measure('lights_2', () => window.__b.setLightCount(2));
await measure('lights_3', () => window.__b.setLightCount(3));
await measure('lights_4', () => window.__b.setLightCount(4));
await measure('lights_6', () => window.__b.setLightCount(6));

// --- instance count cost (with the cheapest material) ---
await measure('phong_l4_fur100', () => { window.__b.setMat('phong'); window.__b.setLightCount(4); window.__b.setFurScale(1); });
await measure('phong_l4_fur50', () => window.__b.setFurScale(0.5));
await measure('phong_l4_fur25', () => window.__b.setFurScale(0.25));
await measure('phong_l4_fur0', () => window.__b.setFurScale(0.0001));

// --- combined best guess ---
await measure('phong_l3_fur60', () => { window.__b.setMat('phong'); window.__b.setLightCount(3); window.__b.setFurScale(0.6); });

await page.evaluate(() => { window.__b.setMat('standard'); window.__b.setLightCount(6); window.__b.setFurScale(1); });
console.log(JSON.stringify(out, null, 2));
fs.writeFileSync(path.join(CACHE, 'bench2.json'), JSON.stringify(out, null, 2));
await browser.close();
server.close();
