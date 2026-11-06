#!/usr/bin/env node
/**
 * v4 composition gate.
 *
 * A browser render only tells you a frame is black *after* it is black. This runs
 * the composition's own timeline under jsdom + real GSAP and asserts the things
 * that would silently ruin the film:
 *
 *   1. every selector the timeline touches exists in the document
 *   2. the duration and frame rate match REF-01 exactly (23.35 s / 30 fps)
 *   3. each of the 13 measured cuts actually changes the picture
 *   4. at most one scene is visible at a time outside a declared dissolve
 *   5. the two graded states fire (red-eye, flash) and the CTA pill holds
 *   6. a sampled frame is never fully transparent / empty
 *
 * Exit code 1 on any failure, so the render never runs on a broken composition.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { JSDOM } from "jsdom";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..");
const COMP = path.join(ROOT, "showreel/v4/index.html");

const EXPECT_DURATION = 23.35;
const EXPECT_FPS = 30;
const CUTS = [0.533, 0.833, 1.0, 1.3, 3.133, 9.133, 11.7, 12.167, 12.467, 12.967, 13.333, 14.8];

const failures = [];
const notes = [];
const fail = (m) => failures.push(m);
const note = (m) => notes.push(m);

const html = fs.readFileSync(COMP, "utf8");

// ---- 1. the document --------------------------------------------------------
const dom = new JSDOM(html, { runScripts: "outside-only", pretendToBeVisual: true });
const { window } = dom;
const doc = window.document;

// jsdom has no layout; these are the only stubs the timeline needs
window.requestAnimationFrame = (cb) => setTimeout(() => cb(16), 0);
window.HTMLElement.prototype.animate = function () { return { cancel() {}, finished: Promise.resolve() }; };

// real GSAP, not a mock — the timeline's own numbers are what is under test
const gsapSrc = fs.readFileSync(path.join(ROOT, "showreel/v4/vendor/gsap.min.js"), "utf8");
window.eval(gsapSrc);

const inline = html.match(/<script>([\s\S]*?)<\/script>/);
if (!inline) {
  console.error("FAIL: no inline composition script found");
  process.exit(1);
}
try {
  window.eval(inline[1]);
} catch (e) {
  console.error("FAIL: composition threw while building the timeline:", e.message);
  process.exit(1);
}

// ---- 2. duration and fps ----------------------------------------------------
const dur = window.__duration;
const fps = window.__fps;
if (Math.abs(dur - EXPECT_DURATION) > 1e-6) fail(`duration ${dur} != ${EXPECT_DURATION}`);
else note(`duration ${dur}s, ${fps} fps`);
if (fps !== EXPECT_FPS) fail(`fps ${fps} != ${EXPECT_FPS}`);

// ---- 1b. every selector exists ---------------------------------------------
const tl = window.__timelines && window.__timelines.main;
if (!tl) {
  console.error("FAIL: window.__timelines.main was not published");
  process.exit(1);
}
const sel = new Set();
const walk = (targets) => {
  const list = typeof targets === "string" ? [targets] : Array.from(targets || []);
  for (const t of list) {
    if (typeof t === "string") {
      for (const part of t.split(",")) {
        const s = part.trim();
        if (s && s.startsWith("#") && !s.includes(" ")) sel.add(s);
      }
    } else if (t && t.nodeType === 1) {
      if (t.id) sel.add("#" + t.id);
    }
  }
};
for (const ch of tl.getChildren(true, true, true)) {
  // GSAP 3 exposes these as methods, not properties
  try {
    if (typeof ch.targets === "function") walk(ch.targets());
  } catch (e) {
    fail(`could not read a tween's targets: ${e.message}`);
  }
}
for (const s of sel) if (!doc.querySelector(s)) fail(`timeline targets a missing element: ${s}`);
note(`${sel.size} distinct targets resolved`);

// ---- 3. frame sampling helpers ---------------------------------------------
const scenes = Array.from(doc.querySelectorAll("section.scene"));
if (scenes.length < 14) fail(`expected at least 14 scenes, found ${scenes.length}`);
const tableIds = new Set((window.__scenes || []).map((r) => "#" + r[0]));
const orphans = scenes.map((el) => "#" + el.id).filter((id) => !tableIds.has(id));
if (orphans.length) fail(`scenes in the document but not in the timeline table: ${orphans.join(", ")}`);

const opacityOf = (el) => {
  let v = parseFloat(window.getComputedStyle(el).opacity);
  return Number.isNaN(v) ? 1 : v;
};
const transformOf = (el) => window.getComputedStyle(el).transform || "none";
const visible = () => scenes.map((el) => ({ id: el.id, o: opacityOf(el) })).filter((s) => s.o > 0.02);

function stateAt(t) {
  tl.pause();
  tl.time(t, false);
  return {
    visible: visible(),
    transforms: scenes.map(transformOf),
    flash: opacityOf(doc.querySelector("#flash")),
    redEye: opacityOf(doc.querySelector("#redEye")),
    pillY: opacityOf(doc.querySelector("#pillY")),
  };
}

// ---- 4. cut activity: the picture must change at every measured cut ---------
const FPS_STEP = 1 / fps;
let last = stateAt(0.2);
let activeCuts = 0;
const sampled = [];
for (let t = FPS_STEP; t < dur; t += FPS_STEP) {
  const s = stateAt(t);
  const sameVisible =
    s.visible.length === last.visible.length &&
    s.visible.every((v, i) => v.id === last.visible[i].id);
  const sameXform = s.transforms.every((v, i) => v === last.transforms[i]);
  const sameFlash = Math.abs(s.flash - last.flash) < 0.01;
  const moved = !(sameVisible && sameXform && sameFlash);
  if (moved) sampled.push(t);
  last = s;
}
for (const c of CUTS) {
  const hits = sampled.filter((t) => Math.abs(t - c) <= 2.5 * FPS_STEP);
  if (hits.length === 0) fail(`cut at ${c}s changes nothing on screen`);
  else activeCuts++;
}
note(`${activeCuts}/${CUTS.length} measured cuts produce a visible change`);

// ---- 5. at most one scene alive outside a dissolve -------------------------
// the overlap windows are derived from the composition's own scene table instead of a
// hand-written list: a dissolve is allowed to lay one plate over another exactly
// inside its own window (that is what makes the cut read), and nowhere else.
const SCENE_TABLE = window.__scenes || [];
const DISSOLVES = SCENE_TABLE.filter((r) => r[2] > 0).map((r) => [
  r[1] - 2 / fps,
  r[1] + Math.max(r[2] * 0.75, 2 / fps) + 1 / fps,
]);
if (DISSOLVES.length === 0) fail("composition published no dissolve windows");
const inDissolve = (t) => DISSOLVES.some(([a, b]) => t >= a && t <= b);
const busy = [];
for (let t = FPS_STEP; t < dur; t += FPS_STEP) {
  if (inDissolve(t)) continue;
  tl.pause();
  tl.time(t, false);   // the loop must move the timeline itself, not read time 0
  const vis = visible();
  if (vis.length > 1) busy.push({ t: +t.toFixed(3), vis: vis.map((v) => v.id).join("+") });
}
if (busy.length > 0) {
  // report the clusters, not hundreds of frames
  const spans = [];
  for (const b of busy) {
    const s = spans[spans.length - 1];
    if (s && b.t - s.end <= 0.12 && b.vis === s.vis) s.end = b.t;
    else spans.push({ start: b.t, end: b.t, vis: b.vis });
  }
  for (const s of spans.slice(0, 12)) {
    fail(`two scenes visible at ${s.start}-${s.end}s (${s.vis}) — the reference never layers plates`);
  }
  note(`${busy.length} overlapping frames in ${spans.length} spans`);
}

// ---- 6. the graded states ---------------------------------------------------
// The flash's height is not a taste. REF-01's own decoded luma at 20.633 peaks at
// 145 over a ~40 base, so a white flash over this picture comes out near 0.5 — an
// earlier build ran it at 0.9, measured 217, and this gate was written to that
// number instead of to the reference. Assert a band around the measurement.
const atFlash = stateAt(20.65);
if (atFlash.flash < 0.35 || atFlash.flash > 0.65)
  fail(`flash at 20.65s is opacity ${atFlash.flash}; REF-01 measures ~0.5 (145 luma over a 40 base)`);
else note(`flash fires on the measured frame at opacity ${atFlash.flash} (~145 luma, as REF-01)`);
// three frames, as measured: 20.633, +1, +2 — clear by the fourth
const afterFlash = stateAt(20.78);
if (afterFlash.flash > 0.05) fail(`flash still on at 20.78s (opacity ${afterFlash.flash})`);
if (afterFlash.redEye < 0.9) fail(`red-eye grade not on after the flash (opacity ${afterFlash.redEye})`);
else note("red-eye grade lands 3 frames after the flash, as measured");

const s7 = stateAt(10.2);
if (!(s7.redEye > 0.9)) fail(`red-eye grade missing in the 9.13 s shot (opacity ${s7.redEye})`);
if (!(s7.pillY > 0.9)) fail(`subscribe pill missing in the 9.13 s shot (opacity ${s7.pillY})`);
else note("red-eye + yellow pill both live in shot 7");

const cta = stateAt(22.5);
const glass = opacityOf(doc.querySelector("#glassCard"));
if (glass < 0.9) fail(`glass CTA card not holding at 22.5 s (opacity ${glass})`);
else note("glass CTA card holds to the last frame");

const pillEnd = opacityOf(doc.querySelector("#s14pillY"));
if (pillEnd > 0.05) fail(`yellow pill still visible over the glass card (opacity ${pillEnd})`);

// ---- 7. nothing is empty ----------------------------------------------------
for (const t of [0.25, 0.6, 1.2, 2.4, 5, 10, 12, 13.6, 16, 19, 21.5, 23.2]) {
  const s = stateAt(t);
  if (s.visible.length === 0) fail(`no scene visible at ${t}s — that frame renders black`);
}
note("12 sampled seconds all have a visible plate");

// ---- report -----------------------------------------------------------------
for (const n of notes) console.log("  ✓", n);
if (failures.length) {
  console.error(`\n${failures.length} gate failure(s):`);
  for (const f of failures) console.error("  ✗", f);
  process.exit(1);
}
console.log(`\ncomposition gate: PASS (${CUTS.length} cuts, ${((dur) / FPS_STEP) | 0} frames)`);
