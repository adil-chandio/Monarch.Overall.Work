import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { chromium } from 'playwright';

const ROOT = process.cwd();
const PUBLIC_DIR = path.join(ROOT, 'public');
const TMP_SEQ_DIR = path.join(PUBLIC_DIR, 'showreel', '_tmp_frames');
const FRAMES_OUT = '/tmp/sr_frames_60fps';
const CLEAN_MASTER = process.env.CLEAN_MASTER || '/tmp/MON-DEMO26_Proof_Over_Promises_v3_1080p60_Master.mp4';
const PREVIEW_OUT = path.join(PUBLIC_DIR, 'demo-preview.mp4');
const POSTER_OUT = path.join(PUBLIC_DIR, 'demo-poster.jpg');
const ENC_OUT = path.join(ROOT, 'deliverables', 'MON-DEMO26_v3_Master_60fps.enc');
const AUDIO_IN = path.join(PUBLIC_DIR, 'showreel', 'audio_master_60fps.m4a');

const TOTAL_FRAMES = 2160; // 36.00s @ 60fps (v3 Absolute Cinema)
const WORKERS = 4;

const RSA_PUBLIC_KEY = `-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA2DbfNglj8pNCYKZ883is
3NQh9UXlGP54jSstgG4v6lpnlG6VQsVrSp50J3OtaUVh59vCKa/uJea2XEMxff95
ergwPiUPofgyyl2qmsWI0VZVSoB2c8KusbQ4M6Yq9sYb/Skisp5KbifO+2YTc/Z3
9AS0/9hISwTdHjrjo5uEh68RW6Eb9L13pz3D4eE70h8bK7Mpkx8kO6btI4OH+Pr+
X1bJ4HPKg+7VdHFmgj3GZ4/ND3Dzyavc4oX/qgz6lW811sHrrKAkee3gQhyECHjS
P6Zu4pIPy/eP8JnIIH08Qkt3G7a/Bk+/9JVOBfWt5oqR2djfi/LxS5d3IrF9JLUU
/FCqUIzTyYP3rzMqrSyX9KLvEOEROsI8FQKxIv58IH0Bnr002qB/LvWIk4OCAUSY
mOWRaaA3Sml/It1sQ59/hXXI/6UWNFfwwW9SkaRzvEVM2xil8mx0+/GaLx2SLmiN
pDCYuFplFSqo3pHjM/37cQY2Pr9kIR6WjtO+Oqi/BOArGm1tYJO5yipt+j0NYQn8
RCN4HhW22PuP2pJuWZ7Sz4egbv2v/p8KRpAOH/7arCLM8HL68B9VFFdC85AVI1P1
Eu1h//abnU2HiVvF81PIGqmSpp3H78vTHf/ziwoN5eKuZZ7HNFKdmUrQFkZIvnV1
JbdfZray29FFN7MCsy/g+AECAwEAAQ==
-----END PUBLIC KEY-----`;

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ttf': 'font/ttf',
  '.mp4': 'video/mp4',
  '.m4a': 'audio/mp4',
};

function extractRealFilmSequences() {
  console.log('[1/5] Pre-decoding real Portfolio v37 film sequences (intro, lawone, paanch)...');
  const clips = [
    { key: 'intro', src: path.join(PUBLIC_DIR, 'proof', 'intro.mp4'), ss: '4.0' },
    { key: 'lawone', src: path.join(PUBLIC_DIR, 'proof', 'lawone.web.mp4'), ss: '10.0' },
    { key: 'paanch', src: path.join(PUBLIC_DIR, 'proof', 'paanch.web.mp4'), ss: '8.0' },
  ];

  for (const c of clips) {
    const outDir = path.join(TMP_SEQ_DIR, c.key);
    fs.mkdirSync(outDir, { recursive: true });
    execFileSync('ffmpeg', [
      '-y',
      '-ss', c.ss,
      '-i', c.src,
      '-vf', 'fps=20,scale=640:-2',
      '-frames:v', '130',
      '-q:v', '3',
      path.join(outDir, '%04d.jpg'),
    ], { stdio: 'inherit' });
  }
}

function startStaticServer(port = 4173) {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      const cleanUrl = decodeURIComponent((req.url || '/').split('?')[0]);
      const rel = cleanUrl === '/' ? '/index.html' : cleanUrl;
      const fullPath = path.join(PUBLIC_DIR, rel);
      if (!fullPath.startsWith(PUBLIC_DIR) || !fs.existsSync(fullPath) || fs.statSync(fullPath).isDirectory()) {
        res.writeHead(404);
        res.end('Not found');
        return;
      }
      const ext = path.extname(fullPath).toLowerCase();
      res.writeHead(200, {
        'Content-Type': MIME[ext] || 'application/octet-stream',
        'Cache-Control': 'public, max-age=3600',
      });
      fs.createReadStream(fullPath).pipe(res);
    });
    server.listen(port, '127.0.0.1', () => resolve(server));
  });
}

async function renderFramesParallel(port) {
  console.log(`[2/5] Capturing ${TOTAL_FRAMES} deterministic 1920x1080 @ 60fps frames across ${WORKERS} Chromium workers...`);
  fs.rmSync(FRAMES_OUT, { recursive: true, force: true });
  fs.mkdirSync(FRAMES_OUT, { recursive: true });

  const sysChrome = ['/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium-browser']
    .find((p) => fs.existsSync(p));
  console.log(`  Using browser binary: ${sysChrome || 'Playwright bundled Chromium'}`);

  const browser = await chromium.launch({
    headless: true,
    ...(sysChrome ? { executablePath: sysChrome } : {}),
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--font-render-hinting=none'],
  });

  const chunk = Math.ceil(TOTAL_FRAMES / WORKERS);
  const t0 = Date.now();

  await Promise.all(
    Array.from({ length: WORKERS }, async (_, w) => {
      const startF = w * chunk;
      const endF = Math.min(TOTAL_FRAMES, (w + 1) * chunk);
      const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 },
        deviceScaleFactor: 1,
      });
      const page = await context.newPage();
      await page.goto(`http://127.0.0.1:${port}/showreel/index.html?headless=1`, {
        waitUntil: 'networkidle',
      });

      // Guarantee all @font-face fonts + initial images are decoded
      await page.evaluate(async () => {
        await document.fonts.ready;
        const imgs = Array.from(document.querySelectorAll('img')).filter((i) => i.getAttribute('src'));
        await Promise.all(
          imgs.map((img) =>
            img.complete
              ? Promise.resolve()
              : new Promise((r) => {
                  img.onload = r;
                  img.onerror = r;
                })
          )
        );
      });

      for (let f = startF; f < endF; f++) {
        await page.evaluate(async (frame) => {
          await window.__setFrame(frame);
          await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
        }, f);

        const outPath = path.join(FRAMES_OUT, `frame_${String(f).padStart(5, '0')}.jpg`);
        await page.screenshot({ path: outPath, type: 'jpeg', quality: 96 });

        if ((f - startF) % 120 === 0) {
          const sec = ((Date.now() - t0) / 1000).toFixed(1);
          console.log(`  [Worker ${w}] frame ${f}/${endF - 1} (${sec}s elapsed)`);
        }
      }
      await context.close();
    })
  );

  await browser.close();
  console.log(`  ✓ Captured all ${TOTAL_FRAMES} frames in ${((Date.now() - t0) / 1000).toFixed(1)}s.`);
}

function encodeMasters() {
  console.log('[3/5] Encoding Clean 1080p60 Master + Watermarked Client Vault Preview + Poster...');

  // 1. Poster frame (f=390 -> 6.50s: 3D YouTube Studio Proof Deck + 583,290 Views + Retention Curve)
  fs.copyFileSync(path.join(FRAMES_OUT, 'frame_00430.jpg'), POSTER_OUT);

  // 2. Clean Unwatermarked Master (1920x1080 @ 60.0 fps, -crf 17, stream-copied -15.3 LUFS / -2.1 dBTP AAC)
  execFileSync('ffmpeg', [
    '-y',
    '-framerate', '60',
    '-i', path.join(FRAMES_OUT, 'frame_%05d.jpg'),
    '-i', AUDIO_IN,
    '-c:v', 'libx264',
    '-preset', 'slow',
    '-crf', '16',
    '-pix_fmt', 'yuv420p',
    '-r', '60',
    '-c:a', 'copy',
    '-shortest',
    '-movflags', '+faststart',
    CLEAN_MASTER,
  ], { stdio: 'inherit' });

  // 3. Watermarked Client Vault & Storefront Preview (1920x1080 @ 60.0 fps, classy semi-transparent top-right badge)
  const fontRel = 'public/showreel/fonts/IBMPlexMono-400.ttf';
  const wmFilter =
    `drawbox=x=1290:y=22:w=604:h=42:color=black@0.58:t=fill,` +
    `drawtext=fontfile=${fontRel}:text='MONARCH VAULT PREVIEW  |  MON-DEMO26':fontcolor=white@0.82:fontsize=19:x=1312:y=34`;

  execFileSync('ffmpeg', [
    '-y',
    '-i', CLEAN_MASTER,
    '-vf', wmFilter,
    '-c:v', 'libx264',
    '-preset', 'medium',
    '-crf', '20',
    '-pix_fmt', 'yuv420p',
    '-r', '60',
    '-c:a', 'copy',
    '-movflags', '+faststart',
    PREVIEW_OUT,
  ], { stdio: 'inherit' });
}

function encryptCleanMaster() {
  console.log('[4/5] Encrypting Clean 1080p60 Master (RSA-OAEP-4096 + AES-256-GCM)...');
  fs.mkdirSync(path.dirname(ENC_OUT), { recursive: true });
  const plain = fs.readFileSync(CLEAN_MASTER);
  const aesKey = crypto.randomBytes(32);
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('aes-256-gcm', aesKey, iv);
  const ciphertext = Buffer.concat([cipher.update(plain), cipher.final()]);
  const authTag = cipher.getAuthTag();

  const wrappedKey = crypto.publicEncrypt(
    {
      key: RSA_PUBLIC_KEY,
      padding: crypto.constants.RSA_PKCS1_OAEP_PADDING,
      oaepHash: 'sha256',
    },
    aesKey
  );

  // Header: [4B wrappedKeyLen][wrappedKey][12B iv][16B authTag][ciphertext]
  const header = Buffer.alloc(4);
  header.writeUInt32BE(wrappedKey.length, 0);
  const packet = Buffer.concat([header, wrappedKey, iv, authTag, ciphertext]);
  fs.writeFileSync(ENC_OUT, packet);
  console.log(`  ✓ Encrypted clean master -> ${ENC_OUT} (${(packet.length / (1024 * 1024)).toFixed(2)} MB)`);
}

async function main() {
  extractRealFilmSequences();
  const server = await startStaticServer(4173);
  try {
    await renderFramesParallel(4173);
  } finally {
    server.close();
    fs.rmSync(TMP_SEQ_DIR, { recursive: true, force: true });
  }
  encodeMasters();
  encryptCleanMaster();
  fs.rmSync(FRAMES_OUT, { recursive: true, force: true });
  console.log('[5/5] ALL DONE — 1080p60 Master + Preview + Poster ready.');
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

// v3 Absolute Cinema — 2,160 deterministic frames @ 60fps (36.000s), Python-DSP soundtrack baked in CI.

// v3.1 — QC pass: softer bloom rays, in-frame crash zoom, vault spec panel, ecosystem rail, crisp ®.

