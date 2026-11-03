#!/usr/bin/env node
/**
 * Walk config/topic-queue.json and run yt_intel on each entry, in order, until the
 * per-run cap or the Data API quota would be exceeded.
 *
 * Why a queue instead of one cron topic: a research tool that only looks at whatever was
 * typed into a form last week stops being a research system. This makes the weekly run
 * accumulate a real topic pool, and it stops before burning quota it cannot afford
 * (1 search = 100 units, so `max_per_run` is the real budget control).
 *
 * Usage: node scripts/yt-queue.mjs [--limit 30] [--max 4] [--only "topic fragment"]
 */
import { execFile } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { promisify } from 'node:util';

const run = promisify(execFile);
const PY = process.env.PYTHON_BIN || 'python3';
const OUT = process.env.YT_INTEL_OUT || join('public', 'yt-intel');
const QUEUE = process.env.YT_QUEUE || join('config', 'topic-queue.json');

const arg = (name, fallback) => {
  const i = process.argv.indexOf(`--${name}`);
  return i === -1 ? fallback : process.argv[i + 1];
};
const defaultLimit = Number(arg('limit', 30));
const only = arg('only', null);

mkdirSync(OUT, { recursive: true });

if (!existsSync(QUEUE)) {
  console.error(`no queue at ${QUEUE}`);
  process.exit(2);
}
const queue = JSON.parse(readFileSync(QUEUE, 'utf8'));
const cap = Number(arg('max', queue.max_per_run || 4));
const list = (queue.topics || []).filter((t) => !only || t.topic.includes(only));
if (!list.length) {
  console.error('queue is empty (or --only matched nothing)');
  process.exit(2);
}

// How much quota is left *right now*, from the same file the Python tool writes.
let remaining = 10000;
const budgetFile = join('.cache', 'yt-intel', 'budget.json');
if (existsSync(budgetFile)) {
  try { remaining = 10000 - (JSON.parse(readFileSync(budgetFile, 'utf8')).used || 0); } catch { /* fresh day */ }
}
const perTopic = 101; // 1 search (100) + 1 videos.list (1); keyless costs nothing
const affordable = Math.floor(remaining / perTopic);

const plan = list.slice(0, Math.max(0, Math.min(cap, affordable)));
console.log(`queue: ${list.length} topics · cap ${cap} · quota allows ${affordable} → running ${plan.length}`);
if (!plan.length) {
  console.log('not enough quota left today; the schedule will pick this up tomorrow');
  process.exit(0);
}

const results = [];
for (const [i, item] of plan.entries()) {
  const limit = String(item.limit || defaultLimit);
  const slug = item.topic.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
  const file = join(OUT, `${slug}.json`);
  console.log(`\n[${i + 1}/${plan.length}] ${item.topic} (limit ${limit})`);
  try {
    const { stdout } = await run(PY, ['-m', 'yt_intel', 'topic', item.topic, '--limit', limit, '--json', file],
      { maxBuffer: 32 * 1024 * 1024 });
    const data = existsSync(file) ? JSON.parse(readFileSync(file, 'utf8')) : null;
    const d = data?.decision || {};
    console.log(`  ${d.verdict || '?'} ${d.score ?? '—'} — ${d.reason || stdout.trim()}`);
    results.push({ topic: item.topic, verdict: d.verdict, score: d.score, status: data?.status, count: data?.count, why: item.why });
  } catch (e) {
    console.error(`  failed: ${String(e.message).slice(0, 300)}`);
    results.push({ topic: item.topic, verdict: 'ERROR', error: String(e.message).slice(0, 200), why: item.why });
  }
}

// Keep the run itself on the record, so a topic that keeps returning RETRY is visible.
const ledger = join(OUT, 'queue-runs.jsonl');
const prev = existsSync(ledger) ? readFileSync(ledger, 'utf8') : '';
writeFileSync(ledger, prev + JSON.stringify({ at: new Date().toISOString(), results }) + '\n');

console.log('\nsummary');
for (const r of results) {
  console.log(`  ${String(r.verdict || '?').padEnd(8)} ${String(r.score ?? '—').padEnd(5)} ${r.topic}`);
}
