#!/usr/bin/env node
/**
 * Mine the comment field of the most-commented video in the freshest API-lane report.
 *
 * Why a script instead of an inline workflow step: the previous version nested a heredoc
 * inside an `if` inside a run block, and its indentation was wrong enough that the whole
 * thing failed silently — the run went green and produced no comment file at all. A script
 * is testable (`node scripts/yt-comments.mjs --dry-run`), and CI can fail loudly.
 *
 * Cost: `commentThreads` is 1 quota unit per page, up to 100 comments per page.
 *
 * Usage:
 *   node scripts/yt-comments.mjs                # pick automatically
 *   node scripts/yt-comments.mjs <videoId>      # mine a specific video
 *   node scripts/yt-comments.mjs --dry-run      # show the pick, spend nothing
 */
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { commentReport } from './yt-intel.mjs';
import { OUT } from './yt-index.mjs';

const args = process.argv.slice(2);
const dryRun = args.includes('--dry-run');
// One video per measured topic, instead of one video overall. Six topics were on the desk and
// exactly one of them had had its audience listened to — the other five verdicts were being
// written without ever reading a comment on those topics.
const perTopic = args.includes('--per-topic');
const maxFlag = args.indexOf('--max');
const maxTopics = maxFlag >= 0 ? Number(args[maxFlag + 1]) || 4 : 4;
const explicit = args.find((a) => !a.startsWith('--') && !/^\d+$/.test(a));

/** Candidates: api-lane reports only — the web lane has no comment counts at all. */
export function candidates(dir = OUT) {
  if (!existsSync(dir)) return [];
  const out = [];
  const chosen = new Set(mined);
  for (const f of readdirSync(dir)) {
    if (!f.endsWith('.json') || f.startsWith('comments-')) continue;
    let d;
    try { d = JSON.parse(readFileSync(join(dir, f), 'utf8')); } catch { continue; }
    if (d?.lane !== 'api' || d?.status !== 'ok') continue;
    for (const r of d.rows || []) {
      if (!r?.id || !r.comments) continue;
      out.push({ id: r.id, comments: r.comments, title: r.title || '', topic: d.topic || '', at: d.fetched_at || 0 });
    }
  }
  // Most comments wins; freshest report breaks ties. Recency matters because an ask-heavy
  // comment field six months old is a brief for a video that has already been made.
  return out.sort((a, b) => b.comments - a.comments || b.at - a.at);
}

/**
 * Pick a video whose comment field can actually brief a video.
 *
 * "Most comments" is the wrong objective and the first real run proved it: it chose an
 * entertainment video with 10,418 comments, where the top-liked comments were jokes about a
 * YouTuber's haircut. Useful comments come from videos whose audience is trying to DO
 * something — so how-to intent in the title/description breaks the tie, and a raw comment
 * count only decides within that group.
 */
const HOW_TO = /\b(how to|how i|tutorial|guide|step by step|setup|workflow|tips|free)\b/i;

/** Best single candidate inside one report: how-to intent first, then raw comment count. */
function bestIn(report) {
  const rows = (report.rows || []).filter((r) => r?.id && r.comments);
  if (!rows.length) return null;
  return rows.sort((a, b) => {
    const aHow = HOW_TO.test(`${a.title || ''} ${report.topic || ''}`) ? 1 : 0;
    const bHow = HOW_TO.test(`${b.title || ''} ${report.topic || ''}`) ? 1 : 0;
    if (aHow !== bHow) return bHow - aHow;
    return (b.comments || 0) - (a.comments || 0);
  })[0];
}

/** One pick per api-lane report, skipping videos we have already mined. */
export function picksPerTopic(dir = OUT) {
  if (!existsSync(dir)) return [];
  const mined = new Set(
    readdirSync(dir)
      .filter((f) => f.startsWith('comments-') && f.endsWith('.json'))
      .map((f) => f.replace(/^comments-/, '').replace(/\.json$/, '')),
  );
  const out = [];
  const chosen = new Set(mined);
  for (const f of readdirSync(dir)) {
    if (!f.endsWith('.json') || f.startsWith('comments-')) continue;
    let d;
    try { d = JSON.parse(readFileSync(join(dir, f), 'utf8')); } catch { continue; }
    if (d?.lane !== 'api' || d?.status !== 'ok') continue;
    // A video can be the top row in several topic reports. Mining the same comment field
    // twice under two topic names would look like two independent audience readings and be
    // one. Chosen ids are global to this run, not per topic.
    const rows = (d.rows || []).filter((r) => r?.id && r.comments && !chosen.has(r.id));
    const best = bestIn({ ...d, rows });
    if (!best) continue;
    chosen.add(best.id);
    out.push({ id: best.id, comments: best.comments, title: best.title || '', topic: d.topic || '', at: d.fetched_at || 0 });
  }
  // Freshest report first: an audience's asks age faster than its size does.
  return out.sort((a, b) => b.at - a.at);
}

const picked = explicit
  ? [{ id: explicit, comments: null, title: '(named explicitly)', topic: '' }]
  : (perTopic ? picksPerTopic() : candidates().sort((a, b) => {
      const aHow = HOW_TO.test(`${a.title} ${a.topic}`) ? 1 : 0;
      const bHow = HOW_TO.test(`${b.title} ${b.topic}`) ? 1 : 0;
      if (aHow !== bHow) return bHow - aHow;
      return b.comments - a.comments || b.at - a.at;
    }));

if (!picked.length) {
  console.log('no API-lane report with comment counts yet — nothing to mine');
  console.log('this is expected until at least one topic has run with YOUTUBE_API_KEY set');
  process.exit(0);
}

const targets = perTopic ? picked.slice(0, maxTopics) : picked.slice(0, 1);
console.log(perTopic
  ? `mining ${targets.length} topic(s), one video each — 1 quota unit per video`
  : `mining ${targets[0].id} · ${targets[0].comments ?? '?'} comments · ${targets[0].title.slice(0, 60) || targets[0].topic}`);
if (dryRun) {
  for (const t of targets) console.log(`  would mine ${t.id} · ${t.topic} · ${t.comments} comments`);
  console.log('dry run — no quota spent');
  process.exit(0);
}

let okCount = 0;
const failures = [];
for (const t of targets) {
  console.log(`\n[${t.topic || 'explicit'}] ${t.id} · ${t.comments ?? '?'} comments · ${t.title.slice(0, 60)}`);
  const { file, data } = await commentReport(t.id);
  if (!data || data.status !== 'ok') {
    console.error(`  no usable report (status: ${data?.status ?? 'missing'}) ${data?.detail || ''}`);
    failures.push(t.topic || t.id);
    continue;
  }
  okCount += 1;
  console.log(`  ${file}`);
  console.log(`  ${data.n} comments · ${data.reading}`);
}

if (!okCount) {
  console.error('comment mining produced nothing usable');
  process.exit(1);
}
console.log(`\n${okCount}/${targets.length} mined${failures.length ? ` — failed: ${failures.join(', ')}` : ''}`);
