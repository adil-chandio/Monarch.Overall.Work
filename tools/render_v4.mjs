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

  // warm pass: paint a couple of frames and throw them away, then come back to 0.
  // Without this the very first captured frame came out fully black — the browser
  // had not composited the CSS background plates yet.
  for (const warm of [0.5, 1.5, 8.0, 16.0, 0.2, 0]) {
    await page.evaluate((time) => {
      const tl = window.__timelines.main;
      tl.pause();
      tl.time(time, false);
    }, warm);
    await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
    await new Promise((r) => setTimeout(r, 60));
  }

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
    if (n === 0) {
      // a black first frame is a render failure, not a style choice
      const probe = await page.screenshot({ type: "png" });
      const fsMod = await import("node:fs");
      fsMod.writeFileSync(path.join(ROOT, "public/demo/v4-frame0.png"), probe);
    }
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
  const onDisk = fs.readdirSync(FRAMES_DIR).filter((f) => /^f_\d{5}\.png$/.test(f)).length;
  if (onDisk !== frameCount) {
    throw new Error(`frame dir holds ${onDisk} PNGs but the film is ${frameCount} frames`);
  }
  const ff = spawnSync(
    "ffmpeg",
    [
      "-y", "-v", "error", "-framerate", String(fps),
      /* explicit start number and exact frame count: without these ffmpeg happily
         muxed 700 frames out of a directory that still held 701 PNGs from the
         previous run, and the extra frame came from a different build of the film */
      "-start_number", "0", "-i", path.join(FRAMES_DIR, "f_%05d.png"),
      "-frames:v", String(frameCount), "-fps_mode", "cfr", "-r", String(fps),
      /* REF-01 is a 980 kb/s 720p30 master. A near-lossless encode here would
         measure twice the edge density of the reference for no delivery benefit,
         so the film is encoded into the same band it will be published in. */
      "-c:v", "libx264", "-preset", "slow", "-crf", "20",
      "-maxrate", "1600k", "-bufsize", "3200k",
      "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
      "-movflags", "+faststart", outPath,
    ],
    { stdio: "inherit" }
  );
  if (ff.status !== 0) throw new Error("ffmpeg encode failed");

  // the encode must contain exactly the frames we captured: an off-by-two here is
  // how the previous master ended up 698 frames long
  const counted = spawnSync(
    "ffprobe",
    ["-v", "error", "-count_frames", "-select_streams", "v:0",
     "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", outPath],
    { encoding: "utf8" }
  );
  const got = parseInt((counted.stdout || "").trim(), 10);
  if (Number.isFinite(got) && got !== frameCount) {
    throw new Error(`encode has ${got} frames, expected ${frameCount}`);
  }
  const mb = (fs.statSync(outPath).size / 1e6).toFixed(2);
  console.log(`wrote ${OUT} (${frameCount} frames, ${mb} MB)`);
}

main().catch((e) => {
  console.error("RENDER FAILED:", e.message);
  process.exit(1);
});
