// Frame renderer for the 3D opening. Playwright + headless Chromium (SwiftShader)
// captures each frame from the WebGL canvas and pipes JPEGs into ffmpeg.
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { spawn, execFileSync } from 'node:child_process';
import { once } from 'node:events';
import { chromium } from 'playwright';
import serverChromium from '@sparticuz/chromium';

const ROOT = process.cwd();
const BASE = path.join(ROOT, 'production/extinct-life/longform-mammoth/cinematic-rebuild');
const CACHE = path.join(ROOT, '.cache/longform-mammoth-cinematic-rebuild');
fs.mkdirSync(CACHE, { recursive: true });
fs.mkdirSync(path.join(CACHE, 'stills'), { recursive: true });
const arg = (k, d) => {
  const hit = process.argv.find((x) => x.startsWith('--' + k + '='));
  if (!hit) return d;
  const i = hit.indexOf('=');
  return hit.slice(i + 1);
};
const S = JSON.parse(fs.readFileSync(path.join(BASE, 'timeline.json')));
const BUILD = createHash('sha256').update(fs.readFileSync(path.join(BASE, 'scene.mjs')))
  .update(fs.readFileSync(path.join(BASE, 'timeline.json')))
  .update(fs.readFileSync(path.join(BASE, 'gait.mjs')))
  .update(fs.readFileSync(path.join(BASE, 'stage.html')))
  .update(fs.readFileSync(path.join(BASE, 'assets/fur.jpg')))
  .update(fs.readFileSync(path.join(BASE, 'assets/tundra.jpg'))).digest('hex');

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
  res.setHeader('Content-Type', ({
    '.mjs': 'application/javascript', '.js': 'application/javascript', '.html': 'text/html',
    '.json': 'application/json', '.ttf': 'font/ttf', '.wav': 'audio/wav'
  })[path.extname(f)] || 'application/octet-stream');
  fs.createReadStream(f).pipe(res);
});
await new Promise((r) => server.listen(process.argv.includes('--serve') ? Number(arg('port', 4288)) : 0, '0.0.0.0', r));
if (process.argv.includes('--serve')) console.log('Opening preview ready on port ' + server.address().port);

let browser, enc;
const errors = [];
try {
  browser = await chromium.launch({
    executablePath: await serverChromium.executablePath(),
    env: { ...process.env, LD_LIBRARY_PATH: path.join(ROOT, '.cache/extinct-v14/libs/lib') },
    args: [...serverChromium.args, '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-dev-shm-usage'],
    headless: true,
  });
  const page = await browser.newPage({ viewport: { width: S.width, height: S.height }, deviceScaleFactor: 1 });
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('response', (r) => { if (r.status() >= 400) errors.push(r.status() + ' ' + r.url()); });
  await page.goto('http://127.0.0.1:' + server.address().port + (arg('query', '') ? '?' + arg('query', '') : ''));
  try {
    await page.waitForFunction(() => window.__ready, null, { timeout: 180000 });
  } catch (e) {
    console.error('Page never became ready. Collected errors:', errors.length ? errors : '(none captured)');
    throw e;
  }
  if (errors.length) throw Error(errors.join(';'));

  const capture = async (f) => page.evaluate((f) => {
    window.__seek(f);
    const jpg = document.querySelector('#final').toDataURL('image/jpeg', 0.95).split(',')[1];
    return { jpg, state: window.__state };
  }, f);

  if (process.argv.includes('--stills')) {
    const frames = arg('frames', '30,150,300,420,600,780,900,1080,1260,1380,1500,1620').split(',').map(Number);
    const states = [];
    for (const f of frames) {
      const a = await capture(f);
      fs.writeFileSync(path.join(CACHE, 'stills', String(f).padStart(4, '0') + '.jpg'), Buffer.from(a.jpg, 'base64'));
      states.push(a.state);
      console.log('still', f, a.state.shot, 'gen', a.state.graph, 'ms', a.state.timings.frame.toFixed(1));
    }
    fs.writeFileSync(path.join(CACHE, 'STILL-QC.json'), JSON.stringify({ frames, states, page_errors: errors }, null, 2));
  } else {
    const from = Number(arg('from', 0)), to = Number(arg('to', S.total_frames));
    const FF = execFileSync(path.join(ROOT, '.venv/bin/python'), ['-c', 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())'], { encoding: 'utf8' }).trim();
    enc = spawn(FF, ['-y', '-v', 'warning', '-probesize', '32', '-analyzeduration', '0', '-f', 'image2pipe', '-framerate', '30',
      '-vcodec', 'mjpeg', '-i', 'pipe:0', '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-threads', '2',
      '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
      path.join(CACHE, `part-${from}-${to}.mp4`)], { stdio: ['pipe', 'inherit', 'inherit'] });
    const done = once(enc, 'exit');
    let n = 0; const sceneRuns = []; const renderStart = Date.now();
    for (let f = from; f < to; f++) {
      const a = await capture(f);
      if (!sceneRuns.length || sceneRuns.at(-1).shot !== a.state.shot) sceneRuns.push({ shot: a.state.shot, from: f, to: f + 1 });
      else sceneRuns.at(-1).to = f + 1;
      if (!enc.stdin.write(Buffer.from(a.jpg, 'base64'))) await once(enc.stdin, 'drain');
      if (++n % 30 === 0) console.log('frame', f, '/', to, a.state.shot, 'elapsed_s', ((Date.now() - renderStart) / 1000).toFixed(1));
    }
    enc.stdin.end();
    const [code] = await done;
    if (code) throw Error('Encode failed ' + code);
    if (errors.length) throw Error(errors.join(';'));
    fs.writeFileSync(path.join(CACHE, `render-${from}-${to}.json`), JSON.stringify({
      from, to, frames: to - from, width: S.width, height: S.height, fps: S.fps,
      source_sha256: BUILD, query: arg('query', ''),
      video_sha256: createHash('sha256').update(fs.readFileSync(path.join(CACHE, `part-${from}-${to}.mp4`))).digest('hex'),
      scene_runs: sceneRuns, page_errors: errors,
      render_seconds: (Date.now() - renderStart) / 1000
    }, null, 2));
  }
} finally {
  if (enc && enc.exitCode === null) enc.kill();
  if (browser) await browser.close();
  server.close();
}
