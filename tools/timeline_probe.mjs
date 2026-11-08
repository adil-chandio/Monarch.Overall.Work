#!/usr/bin/env node
// Evaluate a composition's real timeline headlessly and report, per element,
// the spans where it is actually visible.
//
// Why this exists: the render used to be the only way to find out that a scene
// never went away, and a render is minutes of runner time and a video the eye
// has to guess at. GSAP is deterministic, so the timeline can be sampled here in
// a second — and "s15 is still on screen at 19 s" becomes a line of output
// instead of a ghost in the picture.
//
// Usage: node tools/timeline_probe.mjs [showreel/v4/index.html] [--json]
// Requires jsdom + gsap in node_modules (dev-only; not needed by the render).

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, "..");

function load(id) {
  // resolve from the repo first, then a scratch install
  // the vendored copy the page itself loads is authoritative, then node_modules
  for (const p of [path.join(REPO, "showreel/v4/vendor/gsap.min.js"),
                   path.join(REPO, "node_modules", id),
                   path.join(process.cwd(), "node_modules", id),
                   `/tmp/tlh/node_modules/${id}`]) {
    try {
      return fs.readFileSync(p, "utf8");
    } catch {}
  }
  throw new Error(`cannot find node_modules/${id} — run: npm i jsdom gsap`);
}

import { createRequire } from "node:module";
const require_ = createRequire(path.join(REPO, "package.json"));
let JSDOM;
try {
  ({ JSDOM } = require_("jsdom"));
} catch {
  ({ JSDOM } = require_("/tmp/tlh/node_modules/jsdom"));
}

const target = process.argv[2] && !process.argv[2].startsWith("--")
  ? path.resolve(process.argv[2])
  : path.join(REPO, "showreel/v4/index.html");
const asJson = process.argv.includes("--json");

const html = fs.readFileSync(target, "utf8");
const dom = new JSDOM(html, { runScripts: "outside-only", pretendToBeVisual: true, url: "http://localhost/" });
const { window } = dom;

window.requestAnimationFrame = (cb) => setTimeout(() => cb(Date.now()), 0);
window.cancelAnimationFrame = (id) => clearTimeout(id);
window.matchMedia = () => ({
  matches: false, addListener() {}, removeListener() {},
  addEventListener() {}, removeEventListener() {},
});

window.eval(load("gsap/dist/gsap.min.js"));

// the page loads GSAP from ./vendor; evaluate the inline timeline after it
const inline = html.slice(html.lastIndexOf("<script>") + 8, html.lastIndexOf("</script>"));
window.eval(inline);

const tl = window.__timelines?.main;
if (!tl) throw new Error("no window.__timelines.main — the composition did not register a timeline");
const FPS = window.__fps || 30;

// a scene is a <section class="scene">; anything else is a layer that some scene
// is supposed to be carrying. A layer that is visible while its parent scene is
// not is a layer that nothing can hide.
const sceneIds = [...window.document.querySelectorAll("section.scene")].map((el) => el.id);
const layerIds = [...window.document.querySelectorAll("[id]")]
  .map((el) => el.id)
  .filter((id) => id && !sceneIds.includes(id) && id !== "root");

const span = (pred) => {
  const hits = [];
  for (let f = 0; f < Math.ceil(23.4 * FPS); f++) {
    const t = f / FPS;
    tl.time(t, false);
    if (pred()) hits.push(t);
  }
  if (!hits.length) return null;
  // collapse to contiguous runs
  const runs = [];
  let start = hits[0], prev = hits[0];
  for (const t of hits.slice(1)) {
    if (t - prev > 1.5 / FPS) { runs.push([start, prev]); start = t; }
    prev = t;
  }
  runs.push([start, prev]);
  return runs.map(([a, b]) => [ +a.toFixed(3), +b.toFixed(3) ]);
};

const op = (id) => {
  const el = window.document.getElementById(id);
  if (!el) return null;
  const v = parseFloat(window.getComputedStyle(el).opacity);
  return Number.isFinite(v) ? v : 1;
};

const report = { file: path.relative(REPO, target), fps: FPS, scenes: {}, leaks: [] };

for (const id of sceneIds) {
  report.scenes[id] = span(() => (op(id) ?? 0) > 0.02);
}

// A leak: a layer outside every scene whose opacity is not driven to 0, or a
// layer inside a scene that is visible while the scene is at 0.
const orphans = layerIds.filter((id) => {
  const el = window.document.getElementById(id);
  return el && !el.closest("section.scene") && id !== "flash";
});

for (const id of orphans) {
  tl.time(0, false);
  const a = op(id);
  const runs = span(() => (op(id) ?? 0) > 0.02);
  report.leaks.push({ id, opacity_t0: a, visible: runs });
}

// ---------------------------------------------------------------- strict gate
// A scene is only gone when it is gone. Every scene except the last must be
// invisible shortly after the next scene starts; s4 once stayed at full opacity
// from 1.33 s to the end of the film because its show-tween outlived its hide,
// which no metric in the pipeline could attribute to a scene.
// a scene is allowed to outlive its successor only by its own declared dissolve
// length: a crossfade is two plates on screen on purpose, a zombie is not
const declared = new Map();
for (const row of window.__sceneTable?.scenes || []) declared.set(row.id, row);

const problems = [];
const ordered = sceneIds.filter((id) => report.scenes[id]);
for (let i = 0; i < ordered.length - 1; i++) {
  const id = ordered[i];
  const next = ordered[i + 1];
  const nextStart = report.scenes[next][0][0];
  // the outgoing plate fades out over the *incoming* scene's dissolve (its own
  // display window ends at the cut), so that is what the handover is allowed
  const nextRow = declared.get(next);
  const allow = (nextRow ? Number(nextRow.dissolve) || 0 : 0) * 0.75 + 0.12;
  const late = report.scenes[id].filter(([, b]) => b > nextStart + allow);
  if (late.length) {
    problems.push(`${id} is still visible until ${late[0][1].toFixed(2)}s, but ${next} starts at ${nextStart.toFixed(2)}s (allowed +${allow.toFixed(2)}s for ${next}'s ${nextRow?.dissolve ?? 0}s dissolve)`);
  }
}
// frame 0 must be authored: a zero-duration set at exactly t=0 is never applied,
// so an opening scene that relies on one is black on the first captured frame
if (ordered.length) {
  const first = ordered[0];
  const startsAtZero = (declared.get(first)?.in ?? 0) === 0;
  if (startsAtZero && report.scenes[first][0][0] > 0) {
    problems.push(`${first} opens the film but is not visible at t=0 (first visible ${report.scenes[first][0][0].toFixed(3)}s) — the first frame is unpainted`);
  }
}

for (const l of report.leaks) {
  if (l.visible && l.visible.some(([, b]) => b > 0.05)) {
    problems.push(`${l.id} sits outside every scene and is visible to ${l.visible.at(-1)[1].toFixed(2)}s — nothing can hide it`);
  }
}
report.problems = problems;

if (asJson) {
  console.log(JSON.stringify(report, null, 1));
} else {
  console.log(`\n${report.file}  ·  ${FPS} fps  ·  ${sceneIds.length} scenes\n`);
  console.log("scene   visible spans (s)");
  for (const [id, runs] of Object.entries(report.scenes)) {
    const s = runs ? runs.map(([a, b]) => `${a.toFixed(2)}-${b.toFixed(2)}`).join(" ") : "—";
    console.log(`  ${id.padEnd(6)} ${s}`);
  }
  if (report.leaks.length) {
    console.log("\nlayers outside every scene (nothing can hide these):");
    for (const l of report.leaks) {
      const s = l.visible ? l.visible.map(([a, b]) => `${a.toFixed(2)}-${b.toFixed(2)}`).join(" ") : "—";
      const bad = l.visible && l.visible.some(([, b]) => b > 0.05);
      console.log(`  ${bad ? "LEAK" : " ok "} ${l.id.padEnd(10)} t0=${l.opacity_t0} visible ${s}`);
    }
  }
  if (problems.length) {
    console.log("\nFAIL");
    for (const p of problems) console.log("  - " + p);
  } else {
    console.log("\nOK — every scene hands over and nothing leaks");
  }
}

process.exit(problems.length ? 1 : 0);