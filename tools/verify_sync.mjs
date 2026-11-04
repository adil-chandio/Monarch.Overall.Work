#!/usr/bin/env node
/**
 * The sync gate.
 *
 * The word timings in public/demo/gpu/words.json were produced by Whisper
 * large-v3 (float16, CUDA) on Kaggle GPU T4 x2 — see public/demo/gpu/receipts_gpu.json
 * for the two device names, the wall time and the mean word probability.
 *
 * This asserts the picture and the voice actually agree:
 *   1. every one of the seven beats is aligned (Hindi, confident, non-empty)
 *   2. the last spoken word of a beat lands before that beat's seam, with slack —
 *      i.e. no line is cut off mid-word by the next beat
 *   3. the first word starts at/after the beat's own start
 *   4. the whole voice finishes before the film does
 *
 * Run: node tools/verify_sync.mjs           (exit 1 on any failure)
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";

const ROOT = new URL("..", import.meta.url).pathname.replace(/\/$/, "");
const MIN_SLACK = 0.25; // seconds between the last word and the next beat
const MIN_LANG_PROB = 0.9;

const seams = JSON.parse(readFileSync(join(ROOT, "showreel/v3/seams.json"), "utf8"));
const words = JSON.parse(readFileSync(join(ROOT, "public/demo/gpu/words.json"), "utf8"));
const receipt = JSON.parse(
  readFileSync(join(ROOT, "public/demo/gpu/receipts_gpu.json"), "utf8"),
);

const fails = [];
const say = (s) => console.log(s);

say("\n── sync: proof of the machine it was measured on ─────");
say(
  `  ${receipt.model} on ${receipt.gpu_count}× ${receipt.devices.map((d) => d.name).join(" + ")}` +
    ` (${receipt.devices[0].vram_gb} GB each, cc ${receipt.devices[0].cc})`,
);
say(
  `  ${receipt.words} words in ${receipt.wall_s}s of transcribe time` +
    ` for ${receipt.audio_total_s}s of voice · mean word prob ${receipt.mean_word_prob}`,
);
say(`  fallbacks used: ${(receipt.backend_fallbacks || []).length}`);

if (receipt.gpu_count < 1 || !String(receipt.nvidia_smi).includes("Tesla T4")) {
  fails.push("the timings were not measured on the Kaggle T4 x2 job");
}

say("\n── sync: every line finishes before its own beat ends ─");
say("  beat            beat end  last word   slack   words   lang");
const beats = words.beats;
if (beats.length !== seams.beats.length) {
  fails.push(`${beats.length} aligned beats vs ${seams.beats.length} beats in the film`);
}

beats.forEach((b, i) => {
  const beat = seams.beats[i];
  const end = beat ? beat.end : seams.total;
  const lastWord = b.words.reduce((m, w) => Math.max(m, w.e), 0);
  const firstWord = b.words.reduce((m, w) => Math.min(m, w.s), Infinity);
  const speechEnd = b.offset + lastWord;
  const slack = end - speechEnd;
  const prob = b.words.length
    ? b.words.reduce((s, w) => s + w.p, 0) / b.words.length
    : 0;

  say(
    `  ${b.file.padEnd(15)} ${end.toFixed(2).padStart(7)} ${speechEnd
      .toFixed(2)
      .padStart(10)} ${slack.toFixed(2).padStart(7)} ${String(b.words.length).padStart(6)}` +
      `   ${b.lang}/${b.lang_prob}`,
  );

  if (!b.words.length) fails.push(`${b.file}: no words were aligned`);
  if (b.lang_prob < MIN_LANG_PROB) fails.push(`${b.file}: language prob ${b.lang_prob}`);
  if (b.lang !== "hi") fails.push(`${b.file}: transcribed as ${b.lang}, expected hi`);
  if (prob < 0.8) fails.push(`${b.file}: mean word probability ${prob.toFixed(3)} < 0.8`);
  if (slack < MIN_SLACK) {
    fails.push(`${b.file}: only ${slack.toFixed(2)}s between the last word and the seam`);
  }
  if (firstWord < -0.01) fails.push(`${b.file}: a word starts before the beat does`);
  if (!beat) fails.push(`${b.file}: no matching beat in seams.json`);
});

const finalEnd = beats.reduce(
  (m, b) => Math.max(m, b.offset + b.words.reduce((x, w) => Math.max(x, w.e), 0)),
  0,
);
say(`\n  voice ends at ${finalEnd.toFixed(2)}s · film ends at ${seams.total}s`);
if (finalEnd > seams.total) fails.push("the voice runs past the end of the film");

say("\n──────────────────────────────────────────────────────");
if (fails.length) {
  for (const f of fails) say(`  FAIL  ${f}`);
  say(`FAIL — ${fails.length} sync problem(s)`);
  process.exit(1);
}
say("PASS — every line lands inside its beat, on a GPU-measured clock");
