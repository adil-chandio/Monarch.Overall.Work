/**
 * MONARCH v2 engine — real renderer.
 *
 * Replaces the PIL text-card approach with a Skia canvas (@napi-rs/canvas):
 * real gradients, blur filters, blend modes, clipping, paths, particles.
 *
 * Every transition obeys skills/hyperframes/cut-the-curve + motion-doctrine:
 * hard cuts at peak velocity, mirrored power4 eases, partial travel (12% of frame),
 * blur peak of 10px on the wrapper, word-cascade waterfalls, and no scene ever
 * freezes — the last 2.2x of every beat is re-timed so it is still moving at the cut.
 */
import { createCanvas, GlobalFonts } from '@napi-rs/canvas';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(import.meta.dirname, '../..');
const W = 1920, H = 1080, FPS = 30;
const FFMPEG = path.join(ROOT, '.venv/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2');

// ---------------------------------------------------------------- fonts
GlobalFonts.registerFromPath(path.join(ROOT, 'showreel/v2/assets/Anton-Regular.ttf'), 'Anton');
GlobalFonts.registerFromPath(path.join(ROOT, 'showreel/v2/assets/Poppins-Bold.ttf'), 'PoppinsB');
GlobalFonts.registerFromPath(path.join(ROOT, 'showreel/v2/assets/Poppins-SemiBold.ttf'), 'PoppinsSB');
GlobalFonts.registerFromPath(path.join(ROOT, 'showreel/v2/assets/Poppins-Medium.ttf'), 'PoppinsM');

// ---------------------------------------------------------------- palette
const C = {
  ink: '#05060a', deep: '#0a0d16', panel: '#111624', line: '#1e2637',
  white: '#f4f6fb', dim: '#7c879e', faint: '#2a3346',
  red: '#ff2d46', amber: '#ffb020', cyan: '#22d3ee', lime: '#a3e635',
};

// ---------------------------------------------------------------- eases (GSAP equivalents)
const ease = {
  p2in: t => t * t,
  p3in: t => t * t * t,
  p4in: t => t * t * t * t,
  p4out: t => 1 - Math.pow(1 - t, 4),
  p3out: t => 1 - Math.pow(1 - t, 3),
  p2out: t => 1 - Math.pow(1 - t, 2),
  expoOut: t => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t)),
  p5out: t => 1 - Math.pow(1 - t, 5),
};

const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const p = (t, a, b) => clamp((t - a) / (b - a));

// ---------------------------------------------------------------- timing
const timing = JSON.parse(fs.readFileSync(path.join(ROOT, 'public/demo/vo/timing.json'), 'utf8'));
const STARTS = timing.starts, TOTAL = timing.total;
const BOUND = [...STARTS.slice(1), TOTAL];

const CUT = 0.24;      // 7 frames at 30fps — half the seam window
const TRAVEL = 230;    // 12% of 1920 — partial travel, never a full-frame push
const LEAD = 0.22;     // the incoming scene is already this far into its own motion

// ---------------------------------------------------------------- the world
const scenes = [];
const scene = (name, index, draw) => scenes.push({ name, index, start: STARTS[index], end: BOUND[index], draw });

// =========================================================== primitives
const rgba = (hex, a) => {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
};
function rnd(seed) {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
}
function text(ctx, str, x, y, { font = 'PoppinsB', size = 64, color = C.white, align = 'left', alpha = 1, spacing = 0 } = {}) {
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.font = `${size}px ${font}`;
  ctx.fillStyle = color;
  ctx.textAlign = align;
  ctx.textBaseline = 'alphabetic';
  if (spacing) ctx.letterSpacing = `${spacing}px`;
  ctx.fillText(str, x, y);
  ctx.restore();
}
function measure(ctx, str, font, size, spacing = 0) {
  ctx.save();
  ctx.font = `${size}px ${font}`;
  if (spacing) ctx.letterSpacing = `${spacing}px`;
  const w = ctx.measureText(str).width;
  ctx.restore();
  return w;
}
function roundRect(ctx, x, y, w, h, r) {
  const rr = Math.min(r, Math.abs(w) / 2, Math.abs(h) / 2);
  ctx.beginPath();
  ctx.moveTo(x + rr, y);
  ctx.arcTo(x + w, y, x + w, y + h, rr);
  ctx.arcTo(x + w, y + h, x, y + h, rr);
  ctx.arcTo(x, y + h, x, y, rr);
  ctx.arcTo(x, y, x + w, y, rr);
  ctx.closePath();
}
/** a giant, slowly drifting numeral behind the composition — the depth layer */
function ghost(ctx, str, x, y, size, color, u, a = 0.055) {
  ctx.save();
  ctx.globalAlpha = a;
  const sc = 1.0 + 0.06 * u;
  ctx.translate(x, y); ctx.scale(sc, sc);
  text(ctx, str, 0, 0, { font: 'Anton', size, color, spacing: -6 });
  ctx.restore();
}

/** the framed panel every beat is built inside — a moving window, not a bare slide */
function plate(ctx, x, y, w, h, accent, a = 1) {
  ctx.save();
  ctx.globalAlpha *= a;
  const g = ctx.createLinearGradient(x, y, x + w, y + h);
  g.addColorStop(0, 'rgba(18,23,36,0.92)');
  g.addColorStop(1, 'rgba(10,13,22,0.92)');
  ctx.fillStyle = g;
  roundRect(ctx, x, y, w, h, 18); ctx.fill();
  ctx.strokeStyle = rgba(accent, 0.30);
  ctx.lineWidth = 1.5;
  roundRect(ctx, x, y, w, h, 18); ctx.stroke();
  // corner ticks — the panel reads as a measured instrument
  ctx.strokeStyle = rgba(accent, 0.75);
  ctx.lineWidth = 3;
  [[x, y, 1, 1], [x + w, y, -1, 1], [x, y + h, 1, -1], [x + w, y + h, -1, -1]].forEach(([px, py, sx, sy]) => {
    ctx.beginPath(); ctx.moveTo(px + 26 * sx, py); ctx.lineTo(px, py); ctx.lineTo(px, py + 26 * sy); ctx.stroke();
  });
  ctx.restore();
}

// =========================================================== stage
function paintWorld(ctx, t) {
  const g = ctx.createLinearGradient(0, 0, W, H);
  g.addColorStop(0, '#070912');
  g.addColorStop(0.55, C.deep);
  g.addColorStop(1, '#080a13');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);

  // a slow parallax drift so the ground is never a still image
  const drift = (t * 16) % 220;
  ctx.save();
  ctx.strokeStyle = 'rgba(34,211,238,0.05)';
  ctx.lineWidth = 1;
  for (let x = -drift; x < W + 220; x += 220) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
  }
  ctx.strokeStyle = 'rgba(34,211,238,0.035)';
  for (let y = 0; y < H; y += 220) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
  }
  ctx.restore();

  // embers
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 150; i++) {
    const sx = rnd(i * 7.7) * W;
    const sy = (rnd(i * 3.3) * H + t * (14 + rnd(i) * 30)) % (H + 120) - 60;
    const a = 0.05 + rnd(i * 5.1) * 0.13;
    ctx.fillStyle = i % 5 === 0 ? rgba(C.cyan, a) : rgba(C.red, a * 0.75);
    ctx.beginPath(); ctx.arc(sx, sy, 1 + rnd(i * 9.3) * 2.4, 0, 7); ctx.fill();
  }
  ctx.restore();

  const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.26, W / 2, H / 2, H * 0.95);
  vg.addColorStop(0, 'rgba(0,0,0,0)');
  vg.addColorStop(1, 'rgba(0,0,0,0.74)');
  ctx.fillStyle = vg;
  ctx.fillRect(0, 0, W, H);
}

// =========================================================== scenes
/* ---------- 1 · hook: the share bar, inside a panel ---------- */
scene('hook', 0, (ctx, t, u) => {
  // panel enters with the scene and keeps drifting — the window itself moves
  const px = 120 - 40 * (1 - ease.p4out(p(u, 0, 0.22)));
  const pw = W - 240;
  plate(ctx, px, 170, pw, 740, C.red);

  ghost(ctx, '25', px + 60, 700, 620, C.red, u, 0.05);

  // the 25% bar: grows for the whole beat, never settles
  const grow = 0.18 + 0.82 * ease.p3out(p(u, 0.00, 0.55));
  const barX = px + pw - 380, barW = 290, fullH = 620, barH = fullH * 0.25 * grow;
  const barY = 850 - barH;

  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  const gl = ctx.createRadialGradient(barX + barW / 2, barY, 0, barX + barW / 2, barY, 430 * grow);
  gl.addColorStop(0, rgba(C.red, 0.34 * grow));
  gl.addColorStop(1, rgba(C.red, 0));
  ctx.fillStyle = gl; ctx.fillRect(0, 0, W, H);
  ctx.restore();

  ctx.strokeStyle = rgba(C.dim, 0.35); ctx.lineWidth = 2; ctx.setLineDash([9, 13]);
  roundRect(ctx, barX, 850 - fullH, barW, fullH, 10); ctx.stroke(); ctx.setLineDash([]);

  ctx.fillStyle = rgba(C.red, 0.18);
  ctx.fillRect(barX, barY, barW, barH);
  ctx.fillStyle = C.red;
  ctx.fillRect(barX, barY, barW, 6);

  // the number is the bar's own readout — it keeps ticking to 25
  const n = Math.round(4 + 21 * ease.p3out(p(u, 0.00, 0.42)));
  text(ctx, `${n}%`, barX + barW / 2, barY - 30, { font: 'Anton', size: 190, color: C.white, align: 'center' });

  // headline: waterfall entry, word by word, gaps decaying ×0.84
  const words = ['EK', 'VIDEO', 'HAR', 'VIEW', 'KA'];
  let x = px + 90, gap = 0.075;
  let at = 0.00;
  words.forEach((wd, i) => {
    const big = wd === 'VIDEO';
    const size = big ? 196 : 122;
    const pr = ease.expoOut(p(u, at, at + 0.26));
    if (pr > 0) {
      const w = measure(ctx, wd, 'Anton', size, big ? -2 : 1);
      text(ctx, wd, x, 452 + (1 - pr) * (big ? 90 : 54), {
        font: 'Anton', size, color: big ? C.red : C.white, spacing: big ? -2 : 1,
      });
      x += w + 26;
    }
    at += gap; gap *= 0.84;
  });

  // carrier rule keeps growing for the whole beat → always in motion
  ctx.fillStyle = C.red;
  ctx.fillRect(px + 90, 520, 660 * ease.p3out(p(u, 0.00, 0.85)), 7);

  // the "26 others" tick strip — the counterpoint, already running
  const filled = Math.round(29 * ease.p3out(p(u, 0.10, 0.85)));
  for (let i = 0; i < 29; i++) {
    ctx.fillStyle = i < filled ? rgba(C.dim, 0.55) : rgba(C.faint, 0.7);
    ctx.fillRect(px + 90 + i * 21, 640, 13, i < filled ? 26 : 13);
  }
});

/* ---------- 2 · the other 29 ---------- */
scene('others', 1, (ctx, t, u) => {
  const px = 110, pw = W - 220, py = 150, ph = 780;
  plate(ctx, px, py, pw, ph, C.cyan);

  ghost(ctx, '29', px + 40, py + 760, 620, C.cyan, u, 0.045);

  // 32 cells; 29 fill as a shrinking-gap cascade, 3 stay empty — the story is the gap
  const cols = 8, cw = 74, ch = 112, gap = 13;
  const gx = px + 700, gy = py + 90;
  for (let i = 0; i < 32; i++) {
    const c = i % cols, r = Math.floor(i / cols);
    const at = 0.05 + i * 0.021;
    const pr = ease.p3out(p(u, at, at + 0.34));
    if (pr <= 0) continue;
    const x = gx + c * (cw + gap), y = gy + r * (ch + gap);
    ctx.fillStyle = 'rgba(124,135,158,0.10)';
    roundRect(ctx, x, y, cw, ch, 5); ctx.fill();
    if (i < 29) {
      const fh = ch * pr;
      ctx.fillStyle = rgba(C.cyan, 0.22);
      roundRect(ctx, x, y + ch - fh, cw, fh, 5); ctx.fill();
      ctx.fillStyle = rgba(C.cyan, 0.8);
      roundRect(ctx, x, y + ch - fh, cw, Math.min(4, fh), 2); ctx.fill();
    } else {
      ctx.strokeStyle = rgba(C.dim, 0.4 * pr); ctx.lineWidth = 2; ctx.setLineDash([6, 6]);
      roundRect(ctx, x, y, cw, ch, 5); ctx.stroke(); ctx.setLineDash([]);
    }
  }

  // 75% readout, still counting right up to the cut
  const pct = Math.round(34 + 41 * ease.p3out(p(u, 0.02, 0.96)));
  text(ctx, `${pct}%`, px + 70, py + 470, { font: 'Anton', size: 330, color: C.white });
  text(ctx, 'BAANT RAHE HAIN', px + 76, py + 552, { font: 'PoppinsSB', size: 60, color: C.cyan, spacing: 4 });
  text(ctx, 'UNTEES VIDEOS · 75% SAB KA', px + 76, py + 618, { font: 'PoppinsM', size: 38, color: C.dim, spacing: 2 });

  // 29 body ticks, drawn as a ladder that grows all beat
  for (let i = 0; i < 29; i++) {
    const q = ease.p4out(p(u, 0.02 + i * 0.016, 0.24 + i * 0.016));
    if (q <= 0) continue;
    ctx.fillStyle = rgba(C.cyan, 0.18 + 0.2 * q);
    ctx.fillRect(px + 76, py + 680 + i * 9, 80 * q + 8, 4);
  }
});

/* ---------- 3 · the 36x gap ---------- */
scene('gap', 2, (ctx, t, u) => {
  const px = 110, pw = W - 220, py = 150, ph = 780;
  plate(ctx, px, py, pw, ph, C.red);

  ghost(ctx, '36', 60, py + 470, 660, C.amber, u, 0.05);
  const base = py + 700;
  // bars keep growing across the whole beat
  const grow = 0.18 + 0.82 * ease.p3out(p(u, 0.00, 0.78));
  const h1 = 590 * grow, h2 = 16 * grow;
  const x1 = px + pw - 330, x2 = px + pw - 700, bw = 100;

  ctx.strokeStyle = 'rgba(244,246,251,0.20)'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(x2 - 90, base + 2); ctx.lineTo(x1 + bw + 70, base + 2); ctx.stroke();

  ctx.fillStyle = rgba(C.dim, 0.8);
  roundRect(ctx, x2, base - h2, bw, h2, 3); ctx.fill();
  text(ctx, '51,654', x2 + bw / 2, base + 58, { font: 'PoppinsSB', size: 36, color: C.dim, align: 'center' });
  text(ctx, 'TYPICAL', x2 + bw / 2, base + 98, { font: 'PoppinsM', size: 22, color: C.faint, align: 'center', spacing: 3 });

  const g2 = ctx.createLinearGradient(x1, base - h1, x1, base);
  g2.addColorStop(0, C.red);
  g2.addColorStop(1, 'rgba(255,45,70,0.15)');
  ctx.fillStyle = g2;
  roundRect(ctx, x1, base - h1, bw, h1, 3); ctx.fill();
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  const gl = ctx.createRadialGradient(x1 + bw / 2, base - h1, 0, x1 + bw / 2, base - h1, 360);
  gl.addColorStop(0, rgba(C.red, 0.45)); gl.addColorStop(1, rgba(C.red, 0));
  ctx.fillStyle = gl; ctx.fillRect(x1 - 360, base - h1 - 360, 900, 720);
  ctx.restore();
  text(ctx, '19,22,751', x1 + bw / 2, base - h1 - 34, { font: 'Anton', size: 70, color: C.white, align: 'center' });
  text(ctx, '#1 VIDEO', x1 + bw / 2, base + 58, { font: 'PoppinsSB', size: 36, color: C.red, align: 'center' });
  text(ctx, 'SAME TOPIC', x1 + bw / 2, base + 98, { font: 'PoppinsM', size: 22, color: C.faint, align: 'center', spacing: 3 });

  // the multiplier: inverse-zoom ARRIVAL (1.25 → 1), then a slow continued push
  const pr = ease.expoOut(p(u, 0.00, 0.26));
  if (pr > 0) {
    const sc = (1.25 - 0.25 * pr) * (1 + 0.035 * p(u, 0.5, 1));
    ctx.save();
    ctx.translate(px + 200, py + 380);
    ctx.scale(sc, sc);
    ctx.globalAlpha = 0.15 + 0.85 * pr;
    text(ctx, '36×', 0, 0, { font: 'Anton', size: 300, color: C.white });
    text(ctx, 'KA FARQ', 6, 64, { font: 'PoppinsSB', size: 50, color: C.amber, spacing: 6 });
    ctx.restore();
  }
  // the ratio line draws itself across the beat
  ctx.fillStyle = rgba(C.amber, 0.8);
  ctx.fillRect(px + 200, py + 500, 380 * ease.p3out(p(u, 0.25, 0.95)), 4);
});

/* ---------- 4 · top five ---------- */
scene('topfive', 3, (ctx, t, u) => {
  const px = 100, pw = W - 200, py = 130, ph = 820;
  plate(ctx, px, py, pw, ph, C.red);

  text(ctx, 'TOP FIVE MEIN TEEN', px + 60, py + 92, { font: 'PoppinsSB', size: 42, color: C.dim, spacing: 4 });

  const rows = [
    ['1', 'HOW TO START', '1.92M', true],
    ['2', 'HOW TO START', '1.21M', true],
    ['3', 'BEGINNER SETUP', '767K', false],
    ['4', 'HOW TO START', '757K', true],
    ['5', 'FULL GUIDE', '675K', false],
  ];
  let y = py + 150, gap = 0.125;
  let at = 0.03;
  rows.forEach(([n, label, views, howto], i) => {
    const pr = ease.expoOut(p(u, at, at + 0.26));
    if (pr > 0) {
      const dx = (1 - pr) * 150;
      ctx.save();
      ctx.globalAlpha = pr;
      ctx.translate(dx, 0);
      ctx.fillStyle = howto ? 'rgba(255,45,70,0.10)' : 'rgba(124,135,158,0.06)';
      roundRect(ctx, px + 50, y, pw - 100, 118, 12); ctx.fill();
      if (howto) {
        ctx.strokeStyle = rgba(C.red, 0.5); ctx.lineWidth = 2;
        roundRect(ctx, px + 50, y, pw - 100, 118, 12); ctx.stroke();
        ctx.fillStyle = C.red; ctx.fillRect(px + 50, y, 7, 118);
      }
      text(ctx, n, px + 96, y + 82, { font: 'Anton', size: 62, color: howto ? C.red : C.dim });
      text(ctx, label, px + 200, y + 76, { font: 'Anton', size: 54, color: C.white, spacing: 1 });
      text(ctx, views, px + pw - 130, y + 76, { font: 'Anton', size: 54, color: howto ? C.red : C.dim, align: 'right' });
      ctx.restore();
    }
    y += 132;
    at += gap; gap *= 0.84;
  });

  // the verdict keeps travelling in, then the underline keeps drawing → never still
  const pr = ease.p4out(p(u, 0.72, 0.98));
  if (pr > 0) {
    ctx.fillStyle = rgba(C.amber, 0.9);
    const vy = Math.min(y + 4, py + ph - 62);
    ctx.fillRect(px + 50, vy, (pw - 100) * pr, 5);
    text(ctx, 'KOI NAHI BATATA: KAUN CHHOD GAYA', px + 54, vy + 58, { font: 'PoppinsSB', size: 40, color: C.amber, alpha: pr, spacing: 2 });
  }
  // live "3 of 5" tally at the top right
  const tally = Math.round(3 * ease.p3out(p(u, 0.45, 0.98)));
  text(ctx, `${tally}/5`, px + pw - 70, py + 96, { font: 'Anton', size: 62, color: C.red, align: 'right' });
});

/* ---------- 5 · saturated → concentrated ---------- */
scene('swap', 4, (ctx, t, u) => {
  const px = 100, pw = W - 200, py = 130, ph = 820;
  plate(ctx, px, py, pw, ph, C.amber);

  // 29-spoke lattice: the concentration made physical
  const cx = px + pw - 380, cy = py + 400;
  const spread = Math.PI * 2 * 0.16;
  const open = ease.p4out(p(u, 0.00, 0.42));
  const hubR = 92;

  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 29; i++) {
    const f = i / 28;
    const a = -Math.PI / 2 + (f - 0.5) * spread * open;
    const len = (290 + 200 * Math.abs(Math.sin(f * 3.1))) * open;
    const x2 = cx + Math.cos(a) * len, y2 = cy + Math.sin(a) * len;
    const g = ctx.createLinearGradient(cx, cy, x2, y2);
    g.addColorStop(0, 'rgba(255,45,70,0.8)');
    g.addColorStop(1, 'rgba(255,45,70,0.04)');
    ctx.strokeStyle = g; ctx.lineWidth = 3.5;
    ctx.beginPath(); ctx.moveTo(cx + Math.cos(a) * hubR, cy + Math.sin(a) * hubR); ctx.lineTo(x2, y2); ctx.stroke();
    ctx.fillStyle = rgba(C.amber, 0.95);
    ctx.beginPath(); ctx.arc(x2, y2, 4.5, 0, 7); ctx.fill();
  }
  const hubGlow = ctx.createRadialGradient(cx, cy, 0, cx, cy, hubR * 2.4);
  hubGlow.addColorStop(0, rgba(C.amber, 0.5)); hubGlow.addColorStop(1, rgba(C.amber, 0));
  ctx.fillStyle = hubGlow; ctx.fillRect(cx - 260, cy - 260, 520, 520);
  ctx.restore();
  ctx.save();
  ctx.globalAlpha = open;
  ctx.fillStyle = C.amber;
  ctx.shadowColor = rgba(C.amber, 0.9); ctx.shadowBlur = 34;
  ctx.beginPath(); ctx.arc(cx, cy, hubR * 0.44, 0, 7); ctx.fill();
  ctx.restore();

  // state A: SATURATED struck out, then blasted apart
  const strike = ease.p4out(p(u, 0.14, 0.34));
  const fadeA = 1 - p(u, 0.44, 0.58);
  if (fadeA > 0) {
    ctx.save();
    ctx.globalAlpha = fadeA;
    const shake = u > 0.36 ? Math.max(0, 1 - (u - 0.36) / 0.12) : 0;
    ctx.translate(px + 140 + Math.sin(u * 200) * 6 * shake, py + 330 + Math.cos(u * 240) * 5 * shake);
    const sc = 1 + 0.05 * strike;
    ctx.scale(sc, sc);
    text(ctx, 'SATURATED', 0, 0, { font: 'Anton', size: 170, color: C.dim, spacing: 2 });
    ctx.strokeStyle = C.red; ctx.lineWidth = 13; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(-12, -44); ctx.lineTo(-12 + 930 * strike, -44); ctx.stroke();
    ctx.restore();

    const blast = p(u, 0.36, 0.72);
    if (blast > 0) {
      ctx.save();
      ctx.globalCompositeOperation = 'lighter';
      for (let i = 0; i < 34; i++) {
        const a = -Math.PI * 0.62 + rnd(i * 2.3) * Math.PI * 1.24;
        const d = (60 + rnd(i * 4.1) * 520) * ease.p3out(blast);
        ctx.globalAlpha = (1 - blast) * 0.75;
        ctx.fillStyle = i % 4 === 0 ? C.red : C.dim;
        const s = 4 + rnd(i * 8.8) * 9;
        ctx.save();
        ctx.translate(px + 130 + Math.cos(a) * d, py + 285 + Math.sin(a) * d * 0.72);
        ctx.rotate(a + blast * 3);
        ctx.fillRect(-s / 2, -s / 2, s, s * 1.5);
        ctx.restore();
      }
      ctx.restore();
    }
  }

  // the 1-vs-29 split, drawn as two stacked bars — the beat's second anchor
  {
    const bx = px + 140, by = py + ph - 190, bw2 = 640;
    const oneW = bw2 * 0.97 * ease.p4out(p(u, 0.30, 0.62));
    const restW = bw2 * 0.03 * 29 * ease.p4out(p(u, 0.34, 0.78));
    ctx.fillStyle = rgba(C.amber, 0.85);
    ctx.fillRect(bx, by, Math.max(oneW, 2), 16);
    text(ctx, '#1', bx, by - 12, { font: 'PoppinsSB', size: 26, color: C.amber, spacing: 2 });
    ctx.fillStyle = rgba(C.red, 0.45);
    ctx.fillRect(bx, by + 34, Math.min(restW, bw2), 16);
    text(ctx, '29 OTHERS', bx, by + 78, { font: 'PoppinsSB', size: 26, color: rgba(C.dim, 1), spacing: 2 });
  }

  // state B: CONCENTRATED — inverse-zoom arrival, then a continued push
  const pr = ease.expoOut(p(u, 0.56, 0.84));
  if (pr > 0) {
    const sc = (1.25 - 0.25 * pr) * (1 + 0.03 * p(u, 0.84, 1));
    ctx.save();
    ctx.translate(px + 140, py + 330); ctx.scale(sc, sc);
    ctx.globalAlpha = 0.12 + 0.88 * pr;
    ctx.shadowColor = rgba(C.amber, 0.55); ctx.shadowBlur = 60;
    text(ctx, 'CONCENTRATED', 0, 0, { font: 'Anton', size: 160, color: C.amber, spacing: 1 });
    ctx.restore();

    // three proof lines, each entering on its own beat — but never all settled
    const lines = ['EK JEETNE WALA', 'UNTEES USKI COPY', 'EK HI JAGAH'];
    let at = 0.70, gap = 0.09;
    lines.forEach((ln, i) => {
      const q = ease.p4out(p(u, at, at + 0.16));
      if (q > 0) {
        const yy = py + 430 + i * 58;
        ctx.fillStyle = rgba(C.white, 0.16 * q);
        ctx.fillRect(px + 142, yy - 34, 620 * q, 1.5);
        text(ctx, ln, px + 142 + 26 * (1 - q), yy, { font: 'PoppinsSB', size: 39, color: i === 2 ? C.amber : C.white, alpha: q, spacing: 3 });
      }
      at += gap; gap *= 0.84;
    });
  }
});

/* ---------- 6 · eleven of a hundred ---------- */
scene('comments', 5, (ctx, t, u) => {
  const px = 100, pw = W - 200, py = 130, ph = 820;
  plate(ctx, px, py, pw, ph, C.lime);

  ghost(ctx, '11', px + pw - 560, py + 780, 700, C.lime, u, 0.035);

  // 100 cells fill one by one; the grid keeps ticking for the whole beat
  const filled = Math.round(11 * ease.p4out(p(u, 0.06, 0.78)));
  const cell = 52, gapx = 8, gx = px + 70, gy = py + 70;
  for (let i = 0; i < 100; i++) {
    const c = i % 20, r = Math.floor(i / 20);
    const on = i < filled;
    if (on) {
      ctx.save();
      ctx.shadowColor = rgba(C.lime, 0.75); ctx.shadowBlur = 26;
      ctx.fillStyle = C.lime;
    } else ctx.fillStyle = 'rgba(124,135,158,0.20)';
    roundRect(ctx, gx + c * (cell + gapx), gy + r * (cell + gapx), cell, cell, 8); ctx.fill();
    if (on) ctx.restore();
  }

  const pr = ease.p4out(p(u, 0.08, 0.46));
  text(ctx, '11', px + 70, py + 680, { font: 'Anton', size: 220, color: C.lime, alpha: pr });
  text(ctx, 'PAISE DENA CHAHTE HAIN', px + 260, py + 606, { font: 'PoppinsSB', size: 50, color: C.white, alpha: pr, spacing: 2 });
  text(ctx, '100 COMMENTS MEIN SE · AUR TUTORIAL NAHI', px + 264, py + 666, { font: 'PoppinsM', size: 34, color: C.dim, alpha: pr, spacing: 2 });

  // a live scanning column sweeps the grid — the plate is never a still
  const scanX = gx + ((u * 1.4) % 1) * (pw - 140);
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  const sg = ctx.createLinearGradient(scanX - 60, 0, scanX + 60, 0);
  sg.addColorStop(0, rgba(C.lime, 0)); sg.addColorStop(0.5, rgba(C.lime, 0.10)); sg.addColorStop(1, rgba(C.lime, 0));
  ctx.fillStyle = sg;
  ctx.fillRect(scanX - 60, gy, 120, cell * 5 + gapx * 4);
  ctx.restore();
});

/* ---------- 7 · end ---------- */
scene('end', 6, (ctx, t, u) => {
  const px = 100, pw = W - 200, py = 130, ph = 820;
  plate(ctx, px, py, pw, ph, C.red);

  // stillness before the climax: 0.3–0.75s where only the reticle breathes outward
  const open = ease.p4out(p(u, 0.00, 0.46));
  const cx = W / 2, cy = py + 380, R = 60 + 210 * open;
  ctx.save();
  ctx.globalAlpha = open;
  ctx.strokeStyle = C.red; ctx.lineWidth = 5;
  for (let k = 0; k < 4; k++) {
    const a0 = k * Math.PI / 2 + 0.30;
    ctx.beginPath(); ctx.arc(cx, cy, R, a0, a0 + 0.34 * Math.PI * 2 * 0.34); ctx.stroke();
  }
  for (let k = 0; k < 12; k++) {
    const a = (k / 12) * Math.PI * 2;
    const r0 = R + 26, r1 = R + (k % 3 === 0 ? 54 : 40);
    ctx.strokeStyle = rgba(C.white, k % 3 === 0 ? 0.55 : 0.2);
    ctx.lineWidth = k % 3 === 0 ? 4 : 2;
    ctx.beginPath();
    ctx.moveTo(cx + Math.cos(a) * r0, cy + Math.sin(a) * r0);
    ctx.lineTo(cx + Math.cos(a) * r1, cy + Math.sin(a) * r1);
    ctx.stroke();
  }
  ctx.fillStyle = C.red;
  ctx.beginPath(); ctx.arc(cx, cy, 9, 0, 7); ctx.fill();
  ctx.restore();

  const l1 = ease.expoOut(p(u, 0.30, 0.54));
  const l2 = ease.expoOut(p(u, 0.48, 0.72));
  if (l1 > 0) text(ctx, 'WO Hissa'.toUpperCase(), cx, cy + 330 - 44 * (1 - l1), { font: 'Anton', size: 130, color: C.white, align: 'center', alpha: l1, spacing: 3 });
  if (l2 > 0) text(ctx, 'JO KOI FILM NAHI KARTA', cx, cy + 444 - 40 * (1 - l2), { font: 'Anton', size: 80, color: C.red, align: 'center', alpha: l2, spacing: 2 });

  // the underline keeps drawing to the very last frame
  if (l2 > 0) {
    ctx.fillStyle = rgba(C.red, 0.85);
    ctx.fillRect(cx - 400, cy + 486, 800 * ease.p3out(p(u, 0.66, 1)), 4);
  }
});

/* ---------- INSERTS · full-frame number slams (real cuts inside a beat) ---------- */
function slam(ctx, u, big, sub, color, rays = 44) {
  // radial speed lines burst from the centre on the entry frame
  const burst = ease.p3out(p(u, 0, 0.30));
  ctx.save();
  ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < rays; i++) {
    const a = (i / rays) * Math.PI * 2 + 0.13;
    const r0 = 120 + 90 * burst, r1 = r0 + (240 + 300 * rnd(i * 3.7)) * burst;
    ctx.strokeStyle = rgba(color, 0.16 * (1 - burst * 0.55));
    ctx.lineWidth = 2 + rnd(i * 5.1) * 4;
    ctx.beginPath();
    ctx.moveTo(960 + Math.cos(a) * r0, 500 + Math.sin(a) * r0);
    ctx.lineTo(960 + Math.cos(a) * r1, 500 + Math.sin(a) * r1);
    ctx.stroke();
  }
  ctx.restore();

  // the word scales down into place and keeps drifting — never still
  const sc = 1.30 - 0.30 * ease.expoOut(p(u, 0, 0.34)) + 0.05 * p(u, 0.34, 1);
  ctx.save();
  ctx.translate(960, 500);
  ctx.scale(sc, sc);
  ctx.globalAlpha = 0.2 + 0.8 * ease.p3out(p(u, 0, 0.22));
  ctx.shadowColor = rgba(color, 0.65);
  ctx.shadowBlur = 90;
  text(ctx, big, 0, 40, { font: 'Anton', size: 300, color: C.white, align: 'center', spacing: -4 });
  ctx.restore();

  const pr = ease.p3out(p(u, 0.22, 0.55));
  text(ctx, sub, 960, 700, { font: 'PoppinsSB', size: 52, color, align: 'center', alpha: pr, spacing: 8 });
  ctx.fillStyle = rgba(color, 0.9);
  ctx.fillRect(960 - 300 * pr, 730, 600 * pr, 4);
}

const INSERTS = [
  { at: 14.30, dur: 0.95, draw: (ctx, u) => slam(ctx, u, '36×', 'SAME TOPIC · SAME EFFORT', C.red) },
  { at: 28.60, dur: 0.95, draw: (ctx, u) => slam(ctx, u, '1 / 29', 'EK JEETA · UNTEES HAARE', C.amber, 36) },
];

// =========================================================== seam machinery
/**
 * The scene's own animation clock, retimed so the choreography FILLS the beat instead of
 * finishing in the first second and freezing. `u` is 0→1 across the beat; the outgoing
 * scene's tail is compressed (pow 1/2.2) so it is still travelling into the cut.
 */
function beatU(sc, role, t) {
  const dur = sc.end - sc.start;
  if (role === 'out') return Math.pow(clamp((sc.end - t) / dur), 1 / 2.2);
  let u = (t - sc.start) / dur;
  if (role === 'in') u += LEAD / dur;
  return clamp(u);
}

function seamAlpha(role, q) {
  // "opacity completes at ~25–30% of its TRAVEL": with a power4.in push, 28% of the
  // distance is reached at q≈0.73 — so the fade runs to 0.73, not 0.28 (the bug).
  if (role === 'out') return 1 - clamp(q / 0.73);
  // entry ignites mid-path at 0.35 — binary 0→1 pops
  return 0.35 + 0.65 * ease.p2out(clamp((q - 0.02) / 0.42));
}

async function main() {
  const canvas = createCanvas(W, H);
  const ctx = canvas.getContext('2d');
  const totalFrames = Math.round(TOTAL * FPS);
  const t0 = Date.now();

  const { spawn } = await import('node:child_process');
  const outPath = path.join(ROOT, 'public/demo/v2-silent.mp4');
  const enc = spawn(FFMPEG, [
    '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${W}x${H}`, '-r', String(FPS), '-i', '-',
    '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', outPath,
  ], { stdio: ['pipe', 'inherit', 'inherit'] });
  const writeFrame = buf => new Promise(res => {
    if (enc.stdin.write(buf)) res(); else enc.stdin.once('drain', res);
  });

  for (let f = 0; f < totalFrames; f++) {
    const t = f / FPS;

    // Exactly one scene is composited per frame — the zero-overlap rule of the Seam Gate.
    // [b-CUT, b) is the outgoing scene's exit; [b, b+CUT) is the incoming scene's entry.
    let cur = 0;
    for (let i = 0; i < scenes.length; i++) if (t >= scenes[i].start) cur = i;
    let drawIdx = cur, role = 'none', qq = 0;
    if (cur > 0) {
      const b = scenes[cur].start;
      if (t < b) { drawIdx = cur - 1; role = 'out'; qq = (t - (b - CUT)) / CUT; }
      else if (t < b + CUT) { drawIdx = cur; role = 'in'; qq = (t - b) / CUT; }
    }

    // an insert shot borrows the frame for its window, and owns its own seams
    let ins = null, insRole = 'none', insQ = 0;
    for (const it of INSERTS) {
      if (t >= it.at && t < it.at + it.dur) { ins = it; insRole = 'none'; insQ = (t - it.at) / it.dur; }
      else if (t >= it.at - CUT && t < it.at) { ins = it; insRole = 'out'; insQ = 999; }
      else if (t >= it.at + it.dur && t < it.at + it.dur + CUT) { ins = it; insRole = 'in'; insQ = 999; }
      if (ins) break;
    }

    paintWorld(ctx, t);

    const sc = scenes[drawIdx];
    // CAMERA WITH INTENT (motion-doctrine §performance): every beat pushes in 5.5% and
    // pans a few px, so no frame of this film is a still image — the plate is inside a
    // moving camera, not pasted on a background.
    const camU = beatU(sc, role, t);
    const camZoom = 1.02 + 0.085 * camU + 0.05 * (role === 'out' ? (1 - camU) : 0);
    // the pan alternates direction per beat so consecutive beats never drift the same way
    const dir = drawIdx % 2 === 0 ? 1 : -1;
    const camPanX = dir * 78 * (camU - 0.5);
    const camPanY = 26 * (camU - 0.5);
    ctx.save();
    ctx.translate(W / 2 + camPanX, H / 2 + camPanY);
    ctx.scale(camZoom, camZoom);
    ctx.translate(-W / 2, -H / 2);

    ctx.save();
    let ox = 0, alpha = 1, blur = 0;
    if (role === 'out') {
      ox = -TRAVEL * ease.p4in(qq);
      alpha = seamAlpha('out', qq);
      blur = 10 * ease.p2in(clamp(qq / 0.9));
    } else if (role === 'in') {
      ox = TRAVEL * (1 - ease.p4out(qq));
      alpha = seamAlpha('in', qq);
      blur = 10 * (1 - ease.p2out(clamp(qq / 0.55)));
    }
    // the wrapper carries the blur — never the children, and never with opacity on the
    // same element (cut-the-curve / seam-craft)
    if (blur > 0.25) ctx.filter = `blur(${blur.toFixed(2)}px)`;
    ctx.globalAlpha = alpha;
    ctx.translate(ox, 0);
    if (ins) {
      // inside the insert window the insert IS the shot
      if (insRole === 'none') ins.draw(ctx, 0.06 + 0.88 * insQ, insQ);
      else {
        // entering/leaving: the insert rushes in along the current, exactly like a seam
        const q = insRole === 'in' ? (t - (ins.at + ins.dur)) / CUT : (t - (ins.at - CUT)) / CUT;
        const oxIn = insRole === 'in' ? TRAVEL * (1 - ease.p4out(q)) : 0;
        const aIn = insRole === 'in' ? seamAlpha('in', q) : 1;
        if (insRole === 'out') ins.draw(ctx, 0.94, 1);
        else {
          ctx.save();
          ctx.globalAlpha = aIn;
          ctx.translate(oxIn, 0);
          ins.draw(ctx, 0.88 * q + 0.02, q);
          ctx.restore();
        }
      }
    } else {
      sc.draw(ctx, t, camU);
    }
    ctx.restore();
    ctx.restore();

    // ---- a light sweep crosses the whole frame every beat: a real full-frame change,
    // and the cheapest way to keep a dark film from reading as static.
    {
      const sw = (t * 0.42) % 1.6 - 0.3;
      const sx = sw * W;
      ctx.save();
      ctx.globalCompositeOperation = 'lighter';
      const lg = ctx.createLinearGradient(sx - 420, 0, sx + 420, H);
      lg.addColorStop(0, 'rgba(34,211,238,0)');
      lg.addColorStop(0.45, 'rgba(120,190,255,0.055)');
      lg.addColorStop(0.55, 'rgba(255,80,110,0.045)');
      lg.addColorStop(1, 'rgba(255,45,70,0)');
      ctx.fillStyle = lg;
      ctx.fillRect(0, 0, W, H);
      ctx.restore();
    }

    // ---- the DATA RIBBON: a motion-graphic element that belongs to the whole film.
    // A scrolling waveform + per-beat ticks, so the bottom of every plate is never dead
    // space and the piece reads as one instrument rather than seven slides.
    {
      const ry = 1000, rh = 44;
      ctx.save();
      ctx.fillStyle = 'rgba(10,13,22,0.72)';
      ctx.fillRect(150, ry, W - 300, rh);
      ctx.strokeStyle = 'rgba(244,246,251,0.10)';
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(150, ry); ctx.lineTo(W - 150, ry);
      ctx.moveTo(150, ry + rh); ctx.lineTo(W - 150, ry + rh); ctx.stroke();

      // the waveform: a moving window of pseudo-noise, mirrored about the ribbon centre
      const span = W - 300;
      for (let i = 0; i < span; i += 3) {
        const ph = (i / span) * 26 + t * 5.5;
        const amp = (0.30 + 0.70 * Math.abs(Math.sin(ph * 0.7 + Math.sin(ph) * 1.4)))
          * (0.45 + 0.55 * Math.abs(Math.sin(ph * 0.23 + 1.1)));
        const h = amp * (rh - 10) * 0.5;
        const on = i / span < t / TOTAL;
        ctx.fillStyle = on ? rgba(C.red, 0.55 + 0.35 * amp) : rgba(C.dim, 0.22);
        ctx.fillRect(150 + i, ry + rh / 2 - h, 2, h * 2);
      }
      // beat ticks sit exactly where the seams are
      scenes.forEach((sc, i) => {
        const bx = 150 + (sc.start / TOTAL) * span;
        const live = t >= sc.start;
        ctx.fillStyle = live ? C.amber : rgba(C.dim, 0.4);
        ctx.fillRect(bx - 1, ry - 8, 3, rh + 16);
        if (live) {
          ctx.fillStyle = rgba(C.amber, 0.7);
          ctx.fillRect(bx - 3, ry - 14, 7, 4);
        }
      });
      // playhead
      const phx = 150 + (t / TOTAL) * span;
      ctx.fillStyle = C.white;
      ctx.fillRect(phx - 1.5, ry - 12, 3, rh + 24);
      ctx.restore();
    }

    // ---- the beat chip: the film names where it is, top-left, on every frame
    {
      const nm = scenes[drawIdx].name.toUpperCase();
      const label = `BEAT ${String(drawIdx + 1).padStart(2, '0')} / 07 · ${nm}`;
      ctx.save();
      ctx.font = '500 22px PoppinsM';
      ctx.letterSpacing = '3px';
      const w = ctx.measureText(label).width + 34;
      ctx.fillStyle = 'rgba(10,13,22,0.85)';
      roundRect(ctx, 60, 34, w, 38, 6); ctx.fill();
      ctx.strokeStyle = 'rgba(255,45,70,0.55)'; ctx.lineWidth = 1.5;
      roundRect(ctx, 60, 34, w, 38, 6); ctx.stroke();
      ctx.fillStyle = C.red; ctx.fillRect(60, 34, 4, 38);
      text(ctx, label, 78, 60, { font: 'PoppinsM', size: 22, color: C.white, spacing: 3 });
      ctx.restore();
    }

    // carrier: the progress rule never leaves the frame
    ctx.fillStyle = 'rgba(244,246,251,0.10)';
    ctx.fillRect(0, H - 8, W, 8);
    ctx.fillStyle = C.red;
    ctx.fillRect(0, H - 8, W * (t / TOTAL), 8);
    ctx.strokeStyle = 'rgba(244,246,251,0.18)';
    ctx.lineWidth = 2;
    [[60, 60], [W - 60, 60], [60, H - 60], [W - 60, H - 60]].forEach(([x, y]) => {
      const sx = x < W / 2 ? 1 : -1, sy = y < H / 2 ? 1 : -1;
      ctx.beginPath(); ctx.moveTo(x + 22 * sx, y); ctx.lineTo(x, y); ctx.lineTo(x, y + 22 * sy); ctx.stroke();
    });

    // grain
    ctx.save();
    ctx.globalCompositeOperation = 'overlay';
    for (let i = 0; i < 900; i++) {
      const s = (f * 977 + i * 13) % 100000;
      ctx.fillStyle = `rgba(255,255,255,${0.02 + rnd(s + 3) * 0.05})`;
      ctx.fillRect(rnd(s) * W, rnd(s + 1.7) * H, 2, 2);
    }
    ctx.restore();

    await writeFrame(canvas.data());
    if (f % 200 === 0) process.stdout.write(`  frame ${f}/${totalFrames} (${((Date.now() - t0) / 1000).toFixed(0)}s)\n`);
  }

  await new Promise(res => { enc.on('close', res); enc.stdin.end(); });
  fs.writeFileSync(path.join(ROOT, 'showreel/v2/seams.json'), JSON.stringify({
    fps: FPS, total: TOTAL, cut: CUT, travel: TRAVEL,
    beats: scenes.map(s => ({ name: s.name, start: +s.start.toFixed(3), end: +s.end.toFixed(3) })),
  }, null, 1));
  console.log(`done: ${totalFrames} frames in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
}

main();
