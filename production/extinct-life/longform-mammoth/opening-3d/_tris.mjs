// Diagnostic: where do the triangles actually live?
import path from 'node:path';
import http from 'node:http';
import fs from 'node:fs';
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
await page.goto('http://127.0.0.1:' + server.address().port, { waitUntil: 'commit', timeout: 120000 });
await page.waitForFunction(() => window.__ready, null, { timeout: 600000, polling: 500 });

const report = await page.evaluate(() => {
  const { scene } = window.__dbg;
  const rows = [];
  scene.traverse((o) => {
    if (!o.isMesh && !o.isPoints && !o.isLine) return;
    const g = o.geometry;
    if (!g) return;
    const tris = o.isPoints ? (g.attributes.position?.count || 0)
      : g.index ? g.index.count / 3 : (g.attributes.position?.count || 0) / 3;
    const inst = o.isInstancedMesh ? o.count : 1;
    rows.push({
      name: o.name || o.type,
      mat: o.material?.type || '-',
      tris: Math.round(tris * inst),
      per: Math.round(tris),
      inst,
      visible: o.visible,
    });
  });
  rows.sort((a, b) => b.tris - a.tris);
  const total = rows.reduce((a, b) => a + b.tris, 0);
  return { total, rows };
});
console.log('TOTAL TRIS', report.total);
console.log('top 18 objects:');
for (const r of report.rows.slice(0, 18)) {
  console.log(String(r.tris).padStart(9), (r.name + '/' + r.mat).padEnd(38), 'per=' + r.per, 'inst=' + r.inst, r.visible ? '' : '(hidden)');
}
await browser.close();
server.close();
