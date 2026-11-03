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
import { join } from 'node:path';
import { promisify } from 'node:util';

const run = promisify(execFile);
const PY = process.env.PYTHON_BIN || 'python3';
const OUT = process.env.YT_INTEL_OUT || join('public', 'yt-intel');

export async function topicReport(topic, { limit = 30, out } = {}) {
  mkdirSync(OUT, { recursive: true });
  const slug = topic.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
  const file = out || join(OUT, `${slug}.json`);
  const { stdout, stderr } = await run(
    PY,
    ['-m', 'yt_intel', 'topic', topic, '--limit', String(limit), '--json', file],
    { maxBuffer: 32 * 1024 * 1024 },
  );
  const data = existsSync(file) ? JSON.parse(readFileSync(file, 'utf8')) : null;
  if (data) writeIndex(topic, file, data);
  return { file, stdout: stdout.trim(), stderr: stderr.trim(), data };
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
 * The index the UI reads. Small, newest-first, capped: it is a menu, not the archive —
 * each entry points at the full report file next to it.
 */
export function writeIndex(topic, reportPath, data) {
  mkdirSync(OUT, { recursive: true });
  const file = join(OUT, 'index.json');
  let current = { reports: [] };
  if (existsSync(file)) {
    try { current = JSON.parse(readFileSync(file, 'utf8')); } catch { current = { reports: [] }; }
  }
  const d = data?.decision || {};
  const entry = {
    topic,
    at: new Date().toISOString(),
    file: reportPath.split(/[\\/]/).slice(-1)[0],
    lane: data?.lane || 'unknown',
    status: data?.status || 'unknown',
    count: data?.count ?? 0,
    verdict: d.verdict || null,
    score: d.score ?? null,
    reason: d.reason || '',
    next_probe: d.next_probe || '',
    parts: d.parts || {},
    strongest_against: d.strongest_against || [],
  };
  const reports = [entry, ...(current.reports || []).filter((r) => r.topic !== topic)].slice(0, 40);
  writeFileSync(file, JSON.stringify({ updated: entry.at, reports }, null, 2) + '\n');
  return file;
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
      if (d) console.log(`  verdict ${d.verdict} ${d.score} — ${d.reason}`);
      else console.log(`  ${r.stdout}`);
      if (r.stderr) console.error(r.stderr);
    }).catch((e) => { console.error(String(e.message).slice(0, 500)); process.exit(1); });
  } else if (cmd === 'lanes') {
    lanes().then((l) => console.log(JSON.stringify(l, null, 2))).catch((e) => { console.error(e.message); process.exit(1); });
  } else {
    console.log('usage: node scripts/yt-intel.mjs topic "<topic>" | lanes');
  }
}
