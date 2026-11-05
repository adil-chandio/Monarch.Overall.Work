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

/* ffmpeg, ffprobe and their paths: one place, the same rules as tools/ffbin.py.
   FFMPEG env wins, then PATH, then the python imageio bundle, then imageio's own
   resolver. Returns a path string; throws with the reason if none work. */
function resolveBinary(name) {
  const envKey = name === "ffmpeg" ? process.env.FFMPEG : process.env.FFPROBE;
  if (envKey) return envKey;
  const onPath = spawnSync("sh", ["-c", `command -v ${name}`], { encoding: "utf8" });
  if (onPath.status === 0 && onPath.stdout.trim()) return onPath.stdout.trim();
  const py = spawnSync(
    "python3",
    ["-c", `import sys; sys.path.insert(0,'tools'); from ffbin import ${name}; print(${name}())`],
    { encoding: "utf8" }
  );
  if (py.status === 0 && py.stdout.trim()) return py.stdout.trim().split("\n").pop();
  throw new Error(`${name} not found (FFMPEG env, PATH, imageio bundle all missed): ${(py.stderr || "").trim().split("\n").pop()}`);
}

const FPS = Number(arg("fps", "30"));
/* Supersampling factor. The plates are the reference's own 720x1280 frames, and the
   compositions push them by a fraction of a percent — at deviceScaleFactor 1 that
   push is a bilinear resample by a non-integer factor, which inside Chrome cost
   more than half the detail: the plate measures 308 on Laplacian variance and came
   out of the browser at 137, while the same PNG through the same x264 settings came
   back at 307.7 (i.e. the encode is lossless). Rendering at 2x and downscaling with
   lanczos in the encode keeps the detail and sharpens the type as a side effect. */
const SS = Number(arg("ss", "2"));
const TRACE = path.join(ROOT, arg("trace", "analysis/v4-build/render-part.log"));

/* Workflow logs are not always retrievable from this environment, and a blind
   failure costs a whole render cycle. So the renderer narrates itself to a file
   that the job commits: the run's own log, from inside the failure. */
function trace(msg) {
  const line = `[${new Date().toISOString()}] ${msg}`;
  console.log(line);
  try {
    fs.mkdirSync(path.dirname(TRACE), { recursive: true });
    fs.appendFileSync(TRACE, line + "\n");
  } catch {}
}
const ONLY = arg("only", null);
/* A checkpoint render: stop the picture at a fraction of the film so the first
   shots can be judged before the rest is built. `--part 0.30` renders 0.000 to
   30 % of the duration; `--part-tag` names the output so a checkpoint can never be
   confused with, or overwrite, the full master. */
const PART = Number(arg("part", "1"));
const PART_TAG = arg("part-tag", null);
const FRAMES_DIR = path.join(ROOT, "public/demo/v4-frames");

const COMPOSITION = path.join(ROOT, "showreel/v4/index.html");

async function main() {
  // resolved before anything uses them: the supersampling guard below sits inside the
  // frame loop and referenced a const that was declared near the encode, which is a
  // temporal-dead-zone error and killed the render outright
  const ffmpegBin = resolveBinary("ffmpeg");
  const ffprobeBin = (() => { try { return resolveBinary("ffprobe"); } catch { return null; } })();
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
      /* deviceScaleFactor on the viewport alone does not magnify the page — a
         page that is 720 CSS px wide is rasterised at 720 px either way, which is
         why passing --ss 2 changed nothing at all in the delivered file. The page
         has to be zoomed as well, and then the screenshot is taken at the zoomed
         size and scaled back down to 720x1280 in the encode. */
      ...(SS > 1 ? [`--force-device-scale-factor=${SS}`] : []),
    ],
    defaultViewport: { width: 720, height: 1280, deviceScaleFactor: SS },
  });

  const page = await browser.newPage();
  page.on("console", (m) => {
    if (m.type() === "error") console.error("[page]", m.text());
  });
  page.on("pageerror", (e) => console.error("[pageerror]", e.message));

  await page.goto("file://" + COMPOSITION, { waitUntil: "load", timeout: 120000 });

  /* A calibration switch, not a feature: every plate is replaced by a 2 px
     checkerboard, which no resample can survive. Render one frame with --calibrate
     and the frame tells you exactly what the pipeline does to detail, without
     guessing whether a given plate is "supposed" to be sharp. */
  if (process.argv.includes("--calibrate")) {
    await page.evaluate(() => {
      for (const el of document.querySelectorAll(".plate")) {
        el.style.backgroundImage = "url('./assets/ref/_checker.png')";
        el.style.backgroundSize = "100% 100%";
        el.style.filter = "none";
      }
    });
  }

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
  const partFrames = Math.max(1, Math.round(frameCount * PART));
  for (let i = 0; i < partFrames; i++) times.push(i / fps);

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

  // force the timeline to actually evaluate t=0: a zero-duration set at time 0 can be
  // pending on the first capture, which is how frame 0 came out black
  await page.evaluate(() => {
    const tl = window.__timelines.main;
    tl.time(1 / 30, false);
    tl.time(0, false);
  });
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  await new Promise((r) => setTimeout(r, 80));

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
    if (n === 0 && SS > 1) {
      // the whole point of --ss is a bigger raster; if it is not bigger, say so now
      // rather than discovering it after the encode
      const dims = spawnSync(ffmpegBin, ["-hide_banner", "-i", file], { encoding: "utf8" });
      const m = /,\s(\d{3,5})x(\d{3,5})/.exec(dims.stderr || "");
      if (m && Number(m[1]) < 720 * SS * 0.98) {
        trace(`WARNING: --ss ${SS} asked for ${720 * SS} px wide frames, got ${m[1]} — ` +
              `the page was not zoomed, so this render has no supersampling`);
      } else if (m) {
        trace(`  supersampled: frames are ${m[1]}x${m[2]}`);
      }
    }
    if (n === 0) {
      // a black first frame is a render failure, not a style choice
      const probe = await page.screenshot({ type: "png" });
      const fsMod = await import("node:fs");
      fsMod.writeFileSync(path.join(ROOT, "public/demo/v4-frame0.png"), probe);
    }
    n++;
    if (n % 60 === 0) trace(`  ${n}/${target.length} frames`);
  }

  await browser.close();

  if (ONLY) {
    console.log(`rendered a single frame at ${ONLY}s -> ${FRAMES_DIR}`);
    return;
  }

  const outPath = path.join(ROOT, OUT);
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  const onDisk = fs.readdirSync(FRAMES_DIR).filter((f) => /^f_\d{5}\.png$/.test(f)).length;
  if (onDisk !== partFrames) {
    throw new Error(`frame dir holds ${onDisk} PNGs but this render is ${partFrames} frames`);
  }
  // ffmpeg and ffprobe are not guaranteed to be on PATH — the sandbox that builds
  // this film has neither, and the CI runner has both. tools/ffbin.py already
  // resolves all three cases (FFMPEG env, PATH, bundled), so the render asks it
  // rather than assuming, and prints exactly which binary it used when the encode
  // fails instead of throwing a bare "encode failed" with the reason on a stderr
  // nobody can read.
  const ff = spawnSync(
    ffmpegBin,
    [
      "-y", "-v", "error", "-framerate", String(fps),
      /* explicit start number and exact frame count: without these ffmpeg happily
         muxed 700 frames out of a directory that still held 701 PNGs from the
         previous run, and the extra frame came from a different build of the film */
      "-start_number", "0", "-i", path.join(FRAMES_DIR, "f_%05d.png"),
      "-frames:v", String(partFrames), "-fps_mode", "cfr", "-r", String(fps),
      /* back down to the delivery size, with a filter that keeps the detail the 2x
         render captured instead of averaging it away */
      ...(SS > 1 ? ["-vf", `scale=720:1280:flags=lanczos`] : []),
      /* REF-01 is a 980 kb/s 720p30 master. A near-lossless encode here would
         measure twice the edge density of the reference for no delivery benefit,
         so the film is encoded into the same band it will be published in. */
      "-c:v", "libx264", "-preset", "slow", "-crf", "20",
      "-maxrate", "1600k", "-bufsize", "3200k",
      "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
      /* the reference master is tagged tv/bt709; an untagged file is interpreted
         per-player, and the first comparison against the reference reported a
         brightness difference that was partly this */
      "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
      "-color_range", "tv",
      "-movflags", "+faststart", outPath,
    ],
    { encoding: "utf8" }
  );
  if (ff.status !== 0) {
    const why = (ff.stderr || ff.error?.message || "").trim().split("\n").slice(-8).join(" | ");
    throw new Error(`ffmpeg encode failed (${ffmpegBin}, exit ${ff.status}): ${why || "no stderr"}`);
  }

  // the encode must contain exactly the frames we captured: an off-by-two here is
  // how the previous master ended up 698 frames long
  const counted = (() => {
    if (!ffprobeBin) {
      // no ffprobe here (the authoring sandbox has none). Counting frames is still
      // possible: decode the file and divide by the frame size.
      const raw = spawnSync(ffmpegBin, ["-v", "error", "-i", outPath, "-vf", "scale=64:114",
        "-pix_fmt", "gray", "-f", "rawvideo", "-"], { maxBuffer: 1 << 28 });
      const frames = Math.round(raw.stdout.length / (64 * 114));
      return { status: 0, stdout: String(frames) };
    }
    return spawnSync(
    ffprobeBin,
    ["-v", "error", "-count_frames", "-select_streams", "v:0",
     "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", outPath],
    { encoding: "utf8" }
    );
  })();
  /* Compare against THIS render's frame count, not the whole film's. A checkpoint
     render is 210 frames by construction, so testing it against frameCount (701)
     failed every checkpoint while the encode was perfectly correct — the error even
     read "encode has 210 frames, expected 210", because the message used the right
     number and the test used the wrong one. */
  const got = parseInt((counted.stdout || "").trim(), 10);
  if (Number.isFinite(got) && got !== partFrames) {
    throw new Error(`encode has ${got} frames, expected ${partFrames}`);
  }
  const mb = (fs.statSync(outPath).size / 1e6).toFixed(2);
  console.log(`wrote ${OUT} (${partFrames} frames, ${mb} MB)` +
    (PART < 1 ? ` — checkpoint at ${(PART * 100).toFixed(0)} %${PART_TAG ? ` (${PART_TAG})` : ""}` : ""));
}

main().catch((e) => {
  console.error("RENDER FAILED:", e.message);
  process.exit(1);
});
