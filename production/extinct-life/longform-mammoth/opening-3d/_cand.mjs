// Candidate comparison: cost AND look of each production candidate.
// Usage: node _cand.mjs
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { chromium } from 'playwright';
import serverChromium from '@sparticuz/chromium';

const ROOT = process.cwd();
const BASE = path.join(ROOT, 'production/extinct-life/longform-mammoth/opening-3d');
const CACHE = path.join(ROOT, '.cache/longform-mammoth-opening');
const OUT = path.join(CACHE, 'cand');
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
  // tag                query
  ['A-std6-aa', 'furmat=standard&lights=6&aa=1'],
  ['B-lam4-aa', 'furmat=lambert&lights=4&aa=1'],
  ['C-lam4-noaa', 'furmat=lambert&lights=4&aa=0'],
  ['D-std4-noaa', 'furmat=standard&lights=4&aa=0'],
  ['E-lam5-aa', 'furmat=lambert&lights=5&aa=1'],
  ['F-lam4-aa-hidlam', 'furmat=lambert&lights=4&aa=1&hidemat=lambert'],
  ['G-lam3-noaa', 'furmat=lambert&lights=3&aa=0'],
];

const FRAMES = [200, 510, 780, 1600];
const results = {};
for (const [tag, q] of PROFILES) {
  const browser = await chromium.launch({
    executablePath: await serverChromium.executablePath(),
    env: { ...process.env, LD_LIBRARY_PATH: path.join(ROOT, '.cache/extinct-v14/libs/lib') },
    args: [...serverChromium.args, '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-dev-shm-usage'],
    headless: true,
  });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const errs = [];
  page.on('pageerror', (e) => errs.push(e.message));
  await page.goto('http://127.0.0.1:' + server.address().port + '?' + q, { waitUntil: 'commit', timeout: 120000 });
  await page.waitForFunction(() => window.__ready, null, { timeout: 600000, polling: 500 });
  await page.evaluate((f) => { for (const x of f) window.__seek(x); }, FRAMES);
  const per = await page.evaluate((f) => {
    const { renderer } = window.__dbg;
    const gl = renderer.getContext();
    const px = new Uint8Array(4);
    const times = [];
    for (const x of f) {
      const a = performance.now();
      window.__seek(x);
      gl.readPixels(0, 0, 1,  1, gl.RGBA, gl.UNSIGNED_BYTE, px);
      times.push(performance.now() - a);
    }
    return times;
  }, FRAMES);
  for (const f of [200, 1600]) {
    await page.evaluate((x) => { window.__seek(x); }, f);
    const jpg = await page.evaluate(() => document.querySelector('#final').toDataURL('image/jpeg', 0.92).split(',')[1]);
    fs.writeFileSync(path.join(OUT, tag + '-' + String(f).padStart(4, '0') + '.jpg'), Buffer.from(jpg, 'base64'));
  }
  const avg = per.reduce((a, b) => a + b, 0) / per.length;
  results[tag] = { query: q, ms: +avg.toFixed(0), est_min: +(avg * 1800 / 60000).toFixed(1), errors: errs };
  console.log(tag.padEnd(18), avg.toFixed(0) + 'ms/frame', '~' + (avg * 1800 / 60000).toFixed(1) + 'min for 1800', errs.length ? 'ERR ' + errs.join(';') : '');
  await browser.close();
}
fs.writeFileSync(path.join(CACHE, 'cand.json'), JSON.stringify(results, null, 2));
server.close();
