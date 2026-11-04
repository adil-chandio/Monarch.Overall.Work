#!/usr/bin/env node
/**
 * Frame-exact renderer for the v4 composition.
 *
 * The composition is one paused GSAP timeline on `window.__timelines.main`. This
 * script seeks that timeline to each frame's exact time, waits for the browser
 * to paint, screenshots, and finally encodes the PNG sequence with ffmpeg. No
 * realtime playback, no dropped frames, no frame pacing guesses — frame n is
 * the composition at exactly n/30 s, which is the only way a cut can land on
 * the measured timecode.
 *
 *   node tools/render_v4.mjs --out public/demo/v4-silent.mp4 [--fps 30] [--only 6.1]
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..");

function arg(name, fallback = null) {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : fallback;
}

const OUT = arg("out", "public/demo/v4-silent.mp4");
const FPS = Number(arg("fps", "30"));
const ONLY = arg("only", null);
const FRAMES_DIR = path.join(ROOT, "public/demo/v4-frames");

const COMPOSITION = path.join(ROOT, "showreel/v4/index.html");

async function main() {
  const puppeteer = (await import("puppeteer-core")).default;
  const exe = process.env.CHROME || process.env.PUPPETEER_EXECUTABLE_PATH;
  if (!exe || !fs.existsSync(exe)) {
    throw new Error(`no chrome binary (CHROME=${exe})`);
  }

  fs.rmSync(FRAMES_DIR, { recursive: true, force: true });
  fs.mkdirSync(FRAMES_DIR, { recursive: true });

  const browser = await puppeteer.launch({
    executablePath: exe,
    headless: "shell",
    args: [
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--allow-file-access-from-files",
      "--force-color-profile=srgb",
      "--hide-scrollbars",
      "--disable-gpu",
      "--font-render-hinting=none",
    ],
    defaultViewport: { width: 720, height: 1280, deviceScaleFactor: 1 },
  });

  const page = await browser.newPage();
  page.on("console", (m) => {
    if (m.type() === "error") console.error("[page]", m.text());
  });
  page.on("pageerror", (e) => console.error("[pageerror]", e.message));

  await page.goto("file://" + COMPOSITION, { waitUntil: "load", timeout: 120000 });

  // fonts and every generated plate must be decoded before frame 0 is grabbed,
  // otherwise the first frames render with fallback type and blank plates.
  await page.evaluate(async () => {
    if (document.fonts && document.fonts.ready) await document.fonts.ready;
    const imgs = Array.from(document.images);
    await Promise.all(
      imgs.map((i) => (i.complete ? Promise.resolve() : new Promise((r) => {
        i.onload = i.onerror = r;
      })))
    );
    // also force every CSS background-image to decode
    const urls = [];
    for (const el of document.querySelectorAll("*")) {
      const bg = getComputedStyle(el).backgroundImage;
      const m = bg && bg.match(/url\("?([^")]+)"?\)/);
      if (m) urls.push(m[1]);
    }
    await Promise.all(
      urls.map((u) => new Promise((r) => {
        const im = new Image();
        im.onload = im.onerror = r;
        im.src = u;
      }))
    );
  });

  const total = await page.evaluate(() => window.__duration);
  const fps = await page.evaluate(() => window.__fps || 30);
  if (!total) throw new Error("composition did not publish window.__duration");

  const frameCount = Math.round(total * fps);
  const times = [];
  for (let i = 0; i < frameCount; i++) times.push(i / fps);

  const target = ONLY ? [Number(ONLY)] : times;
  let n = 0;
  for (const t of target) {
    await page.evaluate((time) => {
      const tl = window.__timelines.main;
      tl.pause();
      tl.time(time, false);
      window.__t = time;
    }, t);
    // two rAFs: one to flush the style change, one to guarantee a painted frame
    await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
    const file = path.join(FRAMES_DIR, `f_${String(n).padStart(5, "0")}.png`);
    await page.screenshot({ path: file, type: "png", optimizeForSpeed: false });
    n++;
    if (n % 60 === 0) console.log(`  ${n}/${target.length} frames`);
  }

  await browser.close();

  if (ONLY) {
    console.log(`rendered a single frame at ${ONLY}s -> ${FRAMES_DIR}`);
    return;
  }

  const outPath = path.join(ROOT, OUT);
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  const ff = spawnSync(
    "ffmpeg",
    [
      "-y", "-v", "error", "-framerate", String(fps),
      "-i", path.join(FRAMES_DIR, "f_%05d.png"),
      "-c:v", "libx264", "-preset", "slow", "-crf", "15",
      "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
      "-movflags", "+faststart", outPath,
    ],
    { stdio: "inherit" }
  );
  if (ff.status !== 0) throw new Error("ffmpeg encode failed");
  const mb = (fs.statSync(outPath).size / 1e6).toFixed(2);
  console.log(`wrote ${OUT} (${frameCount} frames, ${mb} MB)`);
}

main().catch((e) => {
  console.error("RENDER FAILED:", e.message);
  process.exit(1);
});
