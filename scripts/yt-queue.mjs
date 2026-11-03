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

// Rotation, not truncation. With a cap smaller than the queue, `slice(0, cap)` re-measures
// the first entries every week and the queue's tail silently never runs — the two topics at
// the bottom had never been measured at all. Oldest measurement goes first; queue order is
// the tiebreaker, so a fresh queue still reads top-down on its first pass.
const measuredAt = (item) => {
  const slug = item.topic.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
  const f = join(OUT, `${slug}.json`);
  if (!existsSync(f)) return 0; // never measured -> first
  try {
    const d = JSON.parse(readFileSync(f, 'utf8'));
    return d.status === 'ok' && d.count > 0 ? Number(d.fetched_at || 0) || 1 : 1;
  } catch { return 1; }
};
const rotated = list
  .map((item, i) => ({ item, i, at: measuredAt(item) }))
  .sort((a, b) => a.at - b.at || a.i - b.i)
  .map((x) => x.item);
const plan = rotated.slice(0, Math.max(0, Math.min(cap, affordable)));
console.log(`queue: ${list.length} topics · cap ${cap} · quota allows ${affordable} → running ${plan.length}`);
if (!plan.length) {
  console.log('not enough quota left today; the schedule will pick this up tomorrow');
  process.exit(0);
}

const results = [];
let kept = 0; // topics whose last real measurement survived this run
for (const [i, item] of plan.entries()) {
  const limit = String(item.limit || defaultLimit);
  const slug = item.topic.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
  const file = join(OUT, `${slug}.json`);
  console.log(`\n[${i + 1}/${plan.length}] ${item.topic} (limit ${limit}${item.order ? `, order ${item.order}` : ''})`);
  // A retry is not a measurement. If the sample did not arrive (rate_limited, no key, blocked
  // IP), keep the last report that actually measured something instead of overwriting a real
  // result with a RETRY stub — the stub belongs in the ledger, not in the research index.
  const previousRaw = existsSync(file) ? readFileSync(file, 'utf8') : null;
  let previous = null;
  try { previous = previousRaw ? JSON.parse(previousRaw) : null; } catch { previous = null; }
  try {
    // `order` lets the queue ask the same question a different way: relevance answers "who
    // holds this topic", `thisMonth` answers "what is landing right now". Both matter, and
    // they disagree — so a topic carries its own filter rather than being re-typed by hand.
    const extra = item.order ? ['--order', item.order] : [];
    const { stdout } = await run(PY, ['-m', 'yt_intel', 'topic', item.topic, '--limit', limit, '--json', file, ...extra],
      { maxBuffer: 32 * 1024 * 1024 });
    const data = existsSync(file) ? JSON.parse(readFileSync(file, 'utf8')) : null;
    const d = data?.decision || {};
    console.log(`  ${d.verdict || '?'} ${d.score ?? '—'} — ${d.reason || stdout.trim()}`);
    if (data?.status !== 'ok' && previous?.status === 'ok' && previous?.count > 0) {
      // Timestamping matters: fetched_at is not always written by the branch that produced the
      // report, and the UI sorts on it. Stamp only when it is missing.
      if (!previous.fetched_at) previous.fetched_at = Math.floor(Date.now() / 1000);
      writeFileSync(file, JSON.stringify(previous, null, 2) + '\n');
      console.log(`  kept the previous measured report (${previous.count} videos)`);
      kept = (kept || 0) + 1;
    }
    if (!data) {
      // Python rejected an argument before it ever measured (bad --limit, unknown --order).
      // That used to enter the ledger with no verdict at all, which reads as "measured, no score".
      results.push({ topic: item.topic, verdict: 'ERROR', status: 'no_report',
        error: `no report written; python said: ${stdout.trim().slice(-200)}`, why: item.why });
      continue;
    }
    results.push({
      topic: item.topic, verdict: d.verdict, score: d.score, status: data.status, count: data.count, why: item.why,
      kept_previous: data.status !== 'ok' && previous?.status === 'ok' ? true : undefined,
    });
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
  console.log(`  ${String(r.verdict || '?').padEnd(8)} ${String(r.score ?? '—').padEnd(5)} ${r.topic}${r.kept_previous ? '  (kept last measured report)' : ''}`);
}
if (kept) console.log(`\n${kept} topic(s) could not be re-measured; their previous measured report was kept.`);
