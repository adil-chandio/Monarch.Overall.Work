#!/usr/bin/env node
/**
 * yt-intel bridge — lets the Node app and CI call the Python tool without a second
 * implementation of the scoring rules.
 *
 * Every number the UI shows is computed once, here, by yt_intel. The Node side only
 * moves JSON and writes reports. That is deliberate: two implementations of "winnability"
 * would eventually disagree, and then the dashboard would be wrong in a way nobody can see.
 */
import { execFile } from 'node:child_process';
import { mkdirSync, writeFileSync, existsSync, readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { promisify } from 'node:util';
import { buildIndex } from './yt-index.mjs';

const run = promisify(execFile);
const PY = process.env.PYTHON_BIN || 'python3';
const OUT = process.env.YT_INTEL_OUT || join('public', 'yt-intel');

export async function topicReport(topic, { limit = 30, out } = {}) {
  mkdirSync(OUT, { recursive: true });
  const slug = topic.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
  const file = out || join(OUT, `${slug}.json`);
  // A retry is not a measurement. If this run could not fetch (no key, throttled IP), keep
  // the last report that actually measured something — otherwise one bad hour replaces a
  // real result with a stub that reads like a verdict. Same rule as scripts/yt-queue.mjs.
  const before = existsSync(file) ? readFileSync(file, 'utf8') : null;
  const { stdout, stderr } = await run(
    PY,
    ['-m', 'yt_intel', 'topic', topic, '--limit', String(limit), '--json', file],
    { maxBuffer: 32 * 1024 * 1024 },
  );
  let data = existsSync(file) ? JSON.parse(readFileSync(file, 'utf8')) : null;
  let kept = false;
  if (data && data.status !== 'ok' && before) {
    let prev = null;
    try { prev = JSON.parse(before); } catch { prev = null; }
    if (prev?.status === 'ok' && prev?.count > 0) {
      if (!prev.fetched_at) prev.fetched_at = Math.floor(Date.now() / 1000);
      writeFileSync(file, JSON.stringify(prev, null, 2) + '\n');
      data = prev;
      kept = true;
    }
  }
  if (data) writeIndex();
  return { file, stdout: stdout.trim(), stderr: stderr.trim(), data, kept };
}

/**
 * Comment mining, written next to the topic reports so the desk can read it.
 * Only meaningful on the API lane: the keyless lane reports `unavailable` rather than
 * pretending the video has no comments.
 */
export async function commentReport(videoId, { limit = 100, out } = {}) {
  mkdirSync(OUT, { recursive: true });
  const file = out || join(OUT, `comments-${videoId}.json`);
  const { stdout } = await run(
    PY,
    ['-m', 'yt_intel', 'comments', videoId, '--limit', String(limit), '--json', file],
    { maxBuffer: 32 * 1024 * 1024 },
  );
  const data = existsSync(file) ? JSON.parse(readFileSync(file, 'utf8')) : null;
  return { file, data, stdout: stdout.trim() };
}

export async function demandReport(topic) {
  const { stdout } = await run(PY, ['-m', 'yt_intel', 'demand', topic, '--json'], { maxBuffer: 8 * 1024 * 1024 });
  return JSON.parse(stdout);
}

export async function lanes() {
  const { stdout } = await run(PY, ['-m', 'yt_intel', 'lanes', '--json']);
  return JSON.parse(stdout);
}

/**
 * The index the UI reads is built in one place only — `scripts/yt-index.mjs`.
 * This used to keep a second, subtly different copy here (no confidence, no saturation
 * shape, and every card timestamped with the current clock). Importing the builder is the
 * fix: one file, one shape, no drift.
 */
export function writeIndex() {
  return buildIndex(null, OUT);
}

/** Append a measurement to the local ledger — one JSONL row per run, never overwritten. */
export function logRun(record) {
  mkdirSync(OUT, { recursive: true });
  const file = join(OUT, 'runs.jsonl');
  const line = JSON.stringify({ at: new Date().toISOString(), ...record }) + '\n';
  const prev = existsSync(file) ? readFileSync(file, 'utf8') : '';
  writeFileSync(file, prev + line);
  return file;
}

if (process.argv[1]?.endsWith('yt-intel.mjs')) {
  const [cmd, ...rest] = process.argv.slice(2);
  if (cmd === 'topic') {
    topicReport(rest.join(' ')).then((r) => {
      const d = r.data?.decision;
      console.log(`${topicReport.name}: ${r.file}`);
      if (r.kept) console.log('  (could not re-measure; kept the previous measured report)');
      if (d) console.log(`  verdict ${d.verdict} ${d.score} — ${d.reason}`);
      else console.log(`  ${r.stdout}`);
      if (r.stderr) console.error(r.stderr);
    }).catch((e) => { console.error(String(e.message).slice(0, 500)); process.exit(1); });
  } else if (cmd === 'comments') {
    commentReport(rest[0] || '')
      .then(({ file, data, stdout }) => {
        if (data?.status === 'ok') {
          console.log(`comments: ${file}`);
          console.log(`  ${data.n} comments · ${data.reading}`);
        } else {
          console.log(stdout || `no comment report for ${rest[0]}`);
        }
      })
      .catch((e) => { console.error(String(e.message).slice(0, 500)); process.exit(1); });
  } else if (cmd === 'lanes') {
    lanes().then((l) => console.log(JSON.stringify(l, null, 2))).catch((e) => { console.error(e.message); process.exit(1); });
  } else {
    console.log('usage: node scripts/yt-intel.mjs topic "<topic>" | comments <videoId> | lanes');
  }
}
