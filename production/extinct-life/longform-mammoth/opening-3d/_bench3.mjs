// Bench v3 — renders the real scene under several cost profiles and reports
// the wall-clock cost of each, plus the visual difference between them.
//
// Usage: node _bench3.mjs
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { chromium } from 'playwright';
import serverChromium from '@sparticuz/chromium';

const ROOT = process.cwd();
const BASE = path.join(ROOT, 'production/extinct-life/longform-mammoth/opening-3d');
const CACHE = path.join(ROOT, '.cache/longform-mammoth-opening');
const OUT = path.join(CACHE, 'bench3');
fs.mkdirSync(OUT, { recursive: true });

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

const PROFILES = [
  ['prod', ''],
  ['noaa', 'aa=0'],
  ['basic', 'furmat=basic'],
  ['lambert', 'furmat=lambert'],
  ['l3', 'lights=3'],
  ['coat50', 'coat=0.5'],
  ['no-under', 'under=0'],
  ['combo-a', 'aa=0&furmat=lambert&lights=4'],
  ['combo-b', 'aa=0&furmat=basic&lights=4&under=0'],
  ['combo-c', 'aa=0&furmat=lambert&lights=4&coat=0.7&under=0.5'],
  ['combo-d', 'aa=0&furmat=basic&lights=4&coat=0.7&under=0.4'],
];

const FRAMES = [200, 510, 780, 1600];
const results = {};

for (const [tag, q] of PROFILES) {
  // A fresh browser per profile: SwiftShader leaks enough on a 2 M-triangle
  // scene that reusing one across eleven profiles kills it.
  const browser = await chromium.launch({
    executablePath: await serverChromium.executablePath(),
    env: { ...process.env, LD_LIBRARY_PATH: path.join(ROOT, '.cache/extinct-v14/libs/lib') },
    args: [...serverChromium.args, '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-dev-shm-usage'],
    headless: true,
  });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));
  const t0 = Date.now();
  await page.goto('http://127.0.0.1:' + server.address().port + (q ? '?' + q : ''), { waitUntil: 'commit', timeout: 120000 });
  await page.waitForFunction(() => window.__ready, null, { timeout: 600000, polling: 500 });
  const ready = (Date.now() - t0) / 1000;

  // warm-up
  await page.evaluate((f) => { for (const x of f) window.__seek(x); }, FRAMES);
  const t1 = Date.now();
  const per = await page.evaluate((f) => {
    const { renderer } = window.__dbg;
    const gl = renderer.getContext();
    const px = new Uint8Array(4);
    const times = [];
    for (const x of f) {
      const a = performance.now();
      window.__seek(x);
      gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
      times.push(performance.now() - a);
    }
    return times;
  }, FRAMES);
  const wall = (Date.now() - t1) / 1000;
  const stats = await page.evaluate(() => {
    const r = window.__dbg.renderer;
    return { calls: r.info.render.calls, tris: r.info.render.triangles };
  });
  // one visual sample per profile for the comparison sheet
  await page.evaluate(() => { window.__seek(200); });
  const jpg = await page.evaluate(() => document.querySelector('#final').toDataURL('image/jpeg', 0.92).split(',')[1]);
  fs.writeFileSync(path.join(OUT, tag + '-0200.jpg'), Buffer.from(jpg, 'base64'));

  const avg = per.reduce((a, b) => a + b, 0) / per.length;
  results[tag] = { query: q, ready_s: +ready.toFixed(1), ms_per_frame: +avg.toFixed(0), wall_s: +wall.toFixed(1), ...stats, errors: errs };
  console.log(tag.padEnd(10), 'ready', ready.toFixed(1) + 's', 'frame', avg.toFixed(0) + 'ms', 'tris', stats.tris, errs.length ? 'ERRORS ' + errs.join(';') : '');
  await browser.close();
}

fs.writeFileSync(path.join(CACHE, 'bench3.json'), JSON.stringify(results, null, 2));
console.log('\n' + JSON.stringify(results, null, 2));
await browser.close();
server.close();
