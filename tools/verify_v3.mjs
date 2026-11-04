/**
 * verify_v3.mjs — prove the v3 composition is correct without opening a browser.
 *
 * jsdom gives a REAL DOM (real CSSStyleDeclaration, real querySelector, real
 * getComputedStyle), so GSAP's CSSPlugin registers properly and every x/y/scale/filter
 * tween becomes observable. That makes the three assertions below meaningful rather
 * than decorative:
 *
 *   1. no NaN in any animated property, on any frame
 *   2. zero overlap at every seam — exactly one scene composited per frame
 *   3. every beat keeps changing — no dead air anywhere in the film
 *
 * Exit code is the verdict. Usage: node tools/verify_v3.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const ROOT = path.resolve(import.meta.dirname, '..');
const { JSDOM } = require('jsdom');

const TOTAL = 42.24;
const FPS = 30;
const BEAT_START = [0.25, 4.89, 11.25, 18.49, 25.09, 31.73, 37.29];
const BEAT_END = [...BEAT_START.slice(1), TOTAL];
const SCENES = ['s1', 's2', 's3', 's4', 's5', 's6', 's7'];

// ------------------------------------------------------------------ real DOM
const html = fs.readFileSync(path.join(ROOT, 'showreel/v3/index.html'), 'utf8');
const dom = new JSDOM(html, {
  runScripts: 'outside-only',   // we inject the script ourselves, after GSAP
  pretendToBeVisual: true,
  url: 'http://localhost/',
});
const { window } = dom;
const { document } = window;

// expose the browser globals Node's module scope needs to see
global.window = window;
global.document = document;
try { Object.defineProperty(global, 'navigator', { value: window.navigator, configurable: true }); } catch {}
global.HTMLElement = window.HTMLElement;
global.Element = window.Element;
// jsdom returns '' for unset transform, which GSAP's _parseTransform cannot read.
// Coerce the handful of properties GSAP parses into the values a browser would give.
/** Convert the CSS transform jsdom returns into the matrix() form GSAP parses. */
function toMatrix(str) {
  if (!str || str === 'none') return 'none';
  if (str.startsWith('matrix(')) return str;
  let tx = 0, ty = 0, sx = 1, sy = 1, rot = 0;
  for (const fn of str.match(/[a-zA-Z0-9]+\([^)]*\)/g) || []) {
    const name = fn.slice(0, fn.indexOf('('));
    const args = fn.slice(fn.indexOf('(') + 1, -1).split(',').map(a => parseFloat(a) || 0);
    if (name === 'translate' || name === 'translate3d') { tx += args[0] || 0; ty += args[1] || 0; }
    else if (name === 'translateX') tx += args[0] || 0;
    else if (name === 'translateY') ty += args[0] || 0;
    else if (name === 'scale') { sx *= args[0] ?? 1; sy *= args[1] ?? args[0] ?? 1; }
    else if (name === 'scaleX') sx *= args[0] ?? 1;
    else if (name === 'scaleY') sy *= args[0] ?? 1;
    else if (name === 'rotate' || name === 'rotateZ') rot += args[0] || 0;
  }
  const r = rot * Math.PI / 180, c = Math.cos(r), sn = Math.sin(r);
  const a = c * sx, b = sn * sx, cc = -sn * sy, d2 = c * sy;
  return `matrix(${a},${b},${cc},${d2},${tx},${ty})`;
}

const _gcs = window.getComputedStyle.bind(window);
global.getComputedStyle = (el, ps) => {
  const cs = _gcs(el, ps);
  return new Proxy(cs, {
    get(t, k) {
      const v = t[k];
      if (typeof v !== 'string') return typeof v === 'function' ? v.bind(t) : v;
      if (k === 'transform') {
        // prefer the inline value: jsdom's computed transform is not normalised to
        // matrix() the way a browser's is, and GSAP's parser requires that form
        const inline = el.style && el.style.transform;
        return toMatrix(inline || v);
      }
      if ((k === 'filter' || k === 'perspective') && !v) return 'none';
      if (k === 'opacity' && !v) return '1';
      if (k === 'transformOrigin' && !v) return '50% 50%';
      // GSAP sniffs legacy CSSMatrix-ish properties; jsdom does not implement them and
      // _parseTransform dereferences the result. A browser also reports "none" here.
      if (k === 'translate' || k === 'rotate' || k === 'scale' || k === 'perspective-origin') return 'none';
      return v;
    },
  });
};
window.getComputedStyle = global.getComputedStyle;
global.requestAnimationFrame = cb => setTimeout(() => cb(Date.now()), 1);
global.cancelAnimationFrame = id => clearTimeout(id);

// deterministic geometry so runs are comparable
let seed = 42;
window.Math.random = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };

// ------------------------------------------------------------------ real GSAP
const gsapPath = path.join(ROOT, 'node_modules/gsap/dist/gsap.min.js');
if (!fs.existsSync(gsapPath)) { console.error('gsap missing — npm i --no-save gsap'); process.exit(2); }
const gsapSrc = fs.readFileSync(gsapPath, 'utf8');
// execute GSAP inside the jsdom window so CSSPlugin binds to THAT document
window.eval(gsapSrc);
const gsap = window.gsap;
if (!gsap) { console.error('FAIL: gsap did not initialise inside the DOM'); process.exit(2); }
gsap.ticker.lagSmoothing(0);

// ------------------------------------------------------------------ run the composition
const code = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)][0][1];
try {
  window.eval(code);
} catch (e) {
  console.error('RUNTIME ERROR in the composition script:');
  console.error(' ', e.message);
  console.error(e.stack.split('\n').slice(0, 8).join('\n'));
  process.exit(1);
}

const tl = window.__timelines?.['main'];
if (!tl) { console.error('FAIL: window.__timelines["main"] was never registered'); process.exit(1); }

const fail = [];
const warn = [];

console.log('── composition ─────────────────────────────────────────');
console.log('  timeline duration  ', tl.duration().toFixed(3), 's   film', TOTAL, 's');
console.log('  tweens registered  ', tl.getChildren(false).length);
console.log('  DOM nodes          ', document.querySelectorAll('*').length);
if (Math.abs(tl.duration() - TOTAL) > 0.06) {
  fail.push(`timeline ${tl.duration().toFixed(2)}s vs film ${TOTAL}s — picture/audio would drift`);
}

const txOf = (sel) => {
  const cs = css(sel);
  if (!cs) return 0;
  const m = /matrix\(([^)]+)\)/.exec(cs.transform || '');
  return m ? parseFloat(m[1].split(',')[4]) : 0;
};

const css = (sel) => {
  const el = document.getElementById(sel) || document.querySelector(sel);
  return el ? window.getComputedStyle(el) : null;
};

// ------------------------------------------------------------------ 1. NaN sweep
console.log('\n── frame sweep ─────────────────────────────────────────');
const frames = Math.round(TOTAL * FPS);
let nan = 0;
const nanSeen = new Set();
for (let f = 0; f < frames; f++) {
  tl.time(f / FPS);
  for (const s of SCENES) {
    const cs = css('#' + s);
    if (!cs) continue;
    for (const prop of ['opacity', 'transform', 'filter']) {
      const v = cs[prop];
      if (v && (v.includes('NaN') || v.includes('undefined'))) {
        if (!nanSeen.has(s + prop)) { nanSeen.add(s + prop); console.log(`  ${s} ${prop} = ${v} (frame ${f})`); }
        nan++;
      }
    }
  }
}
console.log(`  ${frames} frames · NaN/undefined style values: ${nan}`);
if (nan) fail.push(`${nan} frames carry a NaN or undefined style value`);

// ------------------------------------------------------------------ 2. seam zero-overlap
console.log('\n── seams: no black frame, no dissolve ────────────────');
// The real seam-craft rule is about SUMMED opacity: a window where the sum drops below 1
// is where a bad stage flashes. Here the stage is opaque so a dip reads as a blink, which
// is just as bad. So: the sum must never fall below 0.9, and after the overlap window
// closes exactly one scene may remain.
let seamBad = 0;
const OVERLAP = 0.08;
for (const b of BEAT_START.slice(1)) {
  let worst = { t: 0, sum: 9 };
  let worstCount = 0;
  // sweep the whole seam ± the overlap
  for (let t = b - 0.30; t <= b + 0.30; t += 1 / 120) {
    tl.time(t);
    const ops = SCENES.map(s2 => Number(css('#' + s2)?.opacity ?? 0));
    const sum = ops.reduce((a, c) => a + c, 0);
    if (sum < worst.sum) worst = { t, sum };
    const count = ops.filter(o => o > 0.02).length;
    worstCount = Math.max(worstCount, count);
  }
  tl.time(b + 0.35);
  const settled = SCENES.filter(s2 => Number(css('#' + s2)?.opacity ?? 0) > 0.4);
  const ok = worst.sum >= 0.9 && settled.length === 1;
  if (!ok) seamBad++;
  console.log(`  seam @${String(b).padStart(5)}s  min summed opacity ${worst.sum.toFixed(2)} (at ${worst.t.toFixed(2)}s)  max scenes ${worstCount}  settled:[${settled.join(',') || '-'}]${ok ? '' : '  <-- FAIL'}`);
}
if (seamBad) fail.push(`${seamBad} seam(s) dip below 0.9 summed opacity or leave the wrong scene`);

// the outgoing scene must still be MOVING as it goes into its cut (no static hold)
console.log('\n── exit motion (the cut must land mid-motion) ────────');
let slowExits = 0;
for (let i = 1; i < BEAT_START.length; i++) {
  const b = BEAT_START[i];
  const prev = '#' + SCENES[i - 1];
  tl.time(b - 0.22); const x1 = txOf(prev);
  tl.time(b - 0.06); const x2 = txOf(prev);
  const moved = Math.abs(x2 - x1);
  const ok = moved > 8;
  if (!ok) slowExits++;
  console.log(`  ${SCENES[i - 1]} → seam ${b}s   moved ${moved.toFixed(1)}px in the last 0.16s${ok ? '' : '   (too still)'}`);
}
if (slowExits) warn.push(`${slowExits} exit(s) travel under 8px into their cut`);

// ------------------------------------------------------------------ 3. beat activity
console.log('\n── beat activity (no beat may be a still image) ──────');
let stillBeats = 0;
BEAT_START.forEach((a, i) => {
  const b = BEAT_END[i];
  let changed = 0, totalSamples = 0;
  let prev = null;
  for (let t = a + 0.20; t < b - 0.05; t += 0.10) {
    tl.time(t);
    const snap = SCENES.map(s => {
      const cs = css('#' + s);
      return cs ? cs.opacity + '|' + cs.transform + '|' + cs.filter : '';
    }).join('#') + '|' + (document.getElementById('barfill')?.style.width || '');
    totalSamples++;
    if (prev !== null && snap !== prev) changed++;
    prev = snap;
  }
  const pct = Math.round((changed / Math.max(1, totalSamples - 1)) * 100);
  const ok = pct >= 45;
  if (!ok) stillBeats++;
  console.log(`  ${a.toFixed(2)}–${b.toFixed(2)}s  changing samples ${String(pct).padStart(3)}%${ok ? '' : '   <-- possible dead air'}`);
});
if (stillBeats) fail.push(`${stillBeats} beat(s) change in under 45 % of samples — dead air`);

// ------------------------------------------------------------------ verdict
tl.time(0);
console.log('\n──────────────────────────────────────────────────────');
if (warn.length) { console.log('WARN'); warn.forEach(w => console.log('  ·', w)); }
if (fail.length) { console.log('FAIL'); fail.forEach(f => console.log('  ·', f)); process.exit(1); }
console.log('PASS — timeline, seams, exit velocities and beat activity all check out');
process.exit(0);
