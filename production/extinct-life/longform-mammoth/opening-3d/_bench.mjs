// Render-cost bench. Isolates where the wall-clock time goes in the software
// rasteriser: WebGL submit time vs GPU-side (SwiftShader) fill time, and the
// per-frame cost of the fur layers.
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
const tReady = Date.now();
await page.waitForFunction(() => window.__ready, null, { timeout: 600000, polling: 1000 });
console.error('ready in', ((Date.now() - tReady) / 1000).toFixed(1), 's');

// Installed hooks
await page.evaluate(() => {
  const { renderer, scene } = window.__dbg;
  window.__bench = {
    // Pure submit cost: JS-side scene update + GL command queueing.
    submitOnly(frames) {
      const t0 = performance.now();
      for (const f of frames) window.__seek(f);
      return (performance.now() - t0) / frames.length;
    },
    // Submit + a blocking readback, which forces SwiftShader to finish all
    // queued raster work. This is the true cost of the frame.
    fullFrame(frames) {
      const t0 = performance.now();
      for (const f of frames) {
        window.__seek(f);
        const gl = renderer.getContext();
        const px = new Uint8Array(4);
        gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
      }
      return (performance.now() - t0) / frames.length;
    },
    // Readback of the whole canvas = what toDataURL pays on top of raster.
    readback(frames) {
      const t0 = performance.now();
      for (const f of frames) {
        window.__seek(f);
        const gl = renderer.getContext();
        const px = new Uint8Array(1920 * 1080 * 4);
        gl.readPixels(0, 0, 1920, 1080, gl.RGBA, gl.UNSIGNED_BYTE, px);
      }
      return (performance.now() - t0) / frames.length;
    },
    stats() {
      return { calls: renderer.info.render.calls, tris: renderer.info.render.triangles, progs: renderer.info.programs.length };
    },
    // Toggle the fur layers off to price them.
    fur(on) {
      scene.traverse((o) => {
        if (o.isInstancedMesh && o.material && o.material.name) { /* noop */ }
      });
      window.__furMeshes = window.__furMeshes || [];
      if (!window.__furMeshes.length) {
        scene.traverse((o) => { if (o.isInstancedMesh) window.__furMeshes.push(o); });
      }
      window.__furMeshes.forEach((m) => { m.visible = on; });
      return window.__furMeshes.length;
    },
    // Toggle every light off except one.
    lights(n) {
      window.__lights = window.__lights || [];
      if (!window.__lights.length) {
        scene.traverse((o) => { if (o.isLight) window.__lights.push(o); });
      }
      window.__lights.forEach((l, i) => { l.visible = i < n; });
      return window.__lights.length;
    },
  };
});

const FRAMES = [100, 180, 200, 260, 340, 480, 510, 600, 780, 1000, 1290, 1600];
const out = {};
out.stats = await page.evaluate(() => window.__bench.stats());
out.submit_ms = await page.evaluate((f) => window.__bench.submitOnly(f), FRAMES);
out.full_ms = await page.evaluate((f) => window.__bench.fullFrame(f), FRAMES);
out.readback_ms = await page.evaluate((f) => window.__bench.readback(f), FRAMES);

const nFur = await page.evaluate(() => window.__bench.fur(false));
out.full_ms_no_fur = await page.evaluate((f) => window.__bench.fullFrame(f), FRAMES);
await page.evaluate(() => window.__bench.fur(true));

const nLights = await page.evaluate(() => window.__bench.lights(1));
out.full_ms_1_light = await page.evaluate((f) => window.__bench.fullFrame(f), FRAMES);
await page.evaluate((n) => window.__bench.lights(n), nLights);

// Resolution sweep: does the cost scale with pixels (fill-bound) or not?
for (const scale of [0.75, 0.5]) {
  await page.evaluate((s) => {
    const { renderer } = window.__dbg;
    renderer.setSize(Math.round(1920 * s), Math.round(1080 * s), false);
  }, scale);
  out['full_ms_scale_' + scale] = await page.evaluate((f) => window.__bench.fullFrame(f), FRAMES);
}
await page.evaluate(() => window.__dbg.renderer.setSize(1920, 1080, false));

out.fur_meshes = nFur;
out.lights = nLights;
console.log(JSON.stringify(out, null, 2));
fs.writeFileSync(path.join(CACHE, 'bench.json'), JSON.stringify(out, null, 2));

await browser.close();
server.close();
