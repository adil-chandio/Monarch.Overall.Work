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
const explicit = args.find((a) => !a.startsWith('--'));

/** Candidates: api-lane reports only — the web lane has no comment counts at all. */
export function candidates(dir = OUT) {
  if (!existsSync(dir)) return [];
  const out = [];
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

const picked = explicit
  ? [{ id: explicit, comments: null, title: '(named explicitly)', topic: '' }]
  : candidates().sort((a, b) => {
      const aHow = HOW_TO.test(`${a.title} ${a.topic}`) ? 1 : 0;
      const bHow = HOW_TO.test(`${b.title} ${b.topic}`) ? 1 : 0;
      if (aHow !== bHow) return bHow - aHow;
      return b.comments - a.comments || b.at - a.at;
    });

if (!picked.length) {
  console.log('no API-lane report with comment counts yet — nothing to mine');
  console.log('this is expected until at least one topic has run with YOUTUBE_API_KEY set');
  process.exit(0);
}

const target = picked[0];
console.log(`mining ${target.id} · ${target.comments ?? '?'} comments · ${target.title.slice(0, 60) || target.topic}`);
if (dryRun) {
  console.log('dry run — no quota spent');
  process.exit(0);
}

const { file, data } = await commentReport(target.id);
if (!data || data.status !== 'ok') {
  console.error(`comment mining produced no usable report (status: ${data?.status ?? 'missing'})`);
  console.error(data?.detail || '');
  process.exit(1);
}
console.log(`${file}`);
console.log(`  ${data.n} comments · ${data.reading}`);
