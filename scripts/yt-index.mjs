#!/usr/bin/env node
/**
 * Build `public/yt-intel/index.json` from whatever reports are on disk.
 *
 * The UI never runs Python and never runs a scraper; it reads this one small file. That
 * keeps the research desk instant, offline-capable and impossible to fake: every card
 * points at the full report it came from.
 *
 * This module is the ONLY place an index entry is shaped. `scripts/yt-intel.mjs` imports
 * `buildIndex()` instead of writing its own entry — it used to have a second copy, which
 * stamped every card with the current clock and carried none of the measurements the card
 * actually displays. Two implementations of the same file is how a dashboard lies quietly.
 *
 * Usage: node scripts/yt-index.mjs [slug]   (slug = refresh just that report, optional)
 */
import { existsSync, readdirSync, readFileSync, writeFileSync, mkdirSync, statSync } from 'node:fs';
import { join, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

export const OUT = process.env.YT_INTEL_OUT || join('public', 'yt-intel');

// Not research reports, but they live in the same folder and the workflow writes them:
//   index.json  the menu itself
//   lanes.json  which access lane the last run used
//   doctor.json the key check's verdict
// Any `*.json` that is not in this set AND has no `decision` block is also treated as a side
// file below — a topic report always carries a decision, so that test is safe.
const SIDE_FILES = new Set(['index.json', 'lanes.json', 'doctor.json', 'thumbnails.json']);

export function entryFor(file) {
  const data = JSON.parse(readFileSync(file, 'utf8'));
  const d = data.decision || {};
  return {
    topic: data.topic || basename(file, '.json'),
    // Never `now`: a report written three weeks ago would look like it was measured today,
    // and the panel sorts on this. Fall back to the file's own mtime, not the clock.
    at: data.fetched_at
      ? new Date(data.fetched_at * 1000).toISOString()
      : statSync(file).mtime.toISOString(),
    file: basename(file),
    lane: data.lane || 'unknown',
    order: data.order || null,
    status: data.status || 'unknown',
    count: data.count ?? 0,
    verdict: d.verdict || null,
    score: d.score ?? null,
    reason: d.reason || '',
    next_probe: d.next_probe || '',
    parts: d.parts || {},
    strongest_against: d.strongest_against || [],
    saturation: data.saturation?.status === 'ok' ? {
      videos: data.saturation.videos,
      top3_share: data.saturation.top3_share,
      winner_ratio: data.saturation.winner_ratio,
      fresh_share_30d: data.saturation.fresh_share_30d,
      median_views: data.saturation.median_views,
      // how old the sample is: a median view count without it cannot be read
      median_age_days: data.saturation.median_age_days ?? null,
      reading: data.saturation.reading,
    } : null,
    // The headline number on the card. `score` alone is not enough to act on: 57 with
    // confidence 0.85 and 57 with confidence 0.3 are different instructions.
    confidence: d.confidence ?? null,
    mechanism: d.parts?.mechanism ?? null,
    // How the sample was asked for. `relevance` shows who owns a topic, `thisMonth` shows
    // what is landing now, `viewCount` shows the all-time ceiling — three different questions
    // that produce three different scores. Without this line a report cannot be told apart
    // from one asked a different way, which is how "median 4 views/hour" and "median 97
    // views/hour" sat on the same desk looking comparable.
    order: data.order || 'relevance',
    vph_median: (() => {
      const v = (data.rows || []).map((r) => r.vph).filter((x) => typeof x === 'number' && x > 0);
      if (!v.length) return null;
      v.sort((a, b) => a - b);
      return Math.round(v[Math.floor(v.length / 2)]);
    })(),
  };
}

/** Rebuild the index; pass a slug fragment to refresh only matching reports. */
export function buildIndex(only = null, out = OUT) {
  const index = join(out, 'index.json');
  if (!existsSync(out)) mkdirSync(out, { recursive: true });
  const files = existsSync(out)
    ? readdirSync(out).filter((f) => f.endsWith('.json') && !SIDE_FILES.has(f))
    : [];
  const picked = only ? files.filter((f) => f.replace(/\.json$/, '').includes(only)) : files;

  let previous = { reports: [] };
  if (existsSync(index)) {
    try { previous = JSON.parse(readFileSync(index, 'utf8')); } catch { /* rebuild from scratch */ }
  }
  // A malformed side file must never take the whole index down: the index is what the UI
  // reads, and one bad byte in doctor.json skipped the commit step for three runs.
  const fresh = [];
  for (const f of picked) {
    try {
      const data = JSON.parse(readFileSync(join(out, f), 'utf8'));
      if (!data || typeof data !== 'object' || !data.decision) continue; // not a report
      fresh.push(entryFor(join(out, f)));
    } catch (e) {
      console.warn(`index: skipped ${f} — ${String(e.message).slice(0, 120)}`);
    }
  }
  // Stale entries must go too: an earlier run indexed `lanes` as if it were a topic, and
  // carrying it forward forever is how a phantom card survives in the UI.
  const KNOWN = new Set(fresh.map((f) => f.topic));
  const carried = (previous.reports || []).filter((r) => {
    if (KNOWN.has(r.topic)) return false;
    const file = r.file ? join(out, r.file) : null;
    if (file && !existsSync(file)) return false;       // report deleted
    if (!file && r.topic !== 'lanes') return true;
    try {
      const d = JSON.parse(readFileSync(file, 'utf8'));
      return Boolean(d && d.decision);                 // still a real report
    } catch { return false; }
  });
  const merged = [...fresh, ...carried]
    .sort((a, b) => String(b.at).localeCompare(String(a.at)))
    .slice(0, 40);

  // Comment mining results live beside the reports. They are not topics, so they are not
  // cards — but a desk that shows verdicts and hides "6% of that audience wants to buy
  // teaching" is hiding the most actionable number it has.
  const comments = [];
  for (const f of existsSync(out) ? readdirSync(out).filter((x) => x.startsWith('comments-') && x.endsWith('.json')) : []) {
    try {
      const c = JSON.parse(readFileSync(join(out, f), 'utf8'));
      if (c.status !== 'ok') continue;
      comments.push({
        video: c.video,
        file: f,
        n: c.n,
        reading: c.reading || '',
        at: statSync(join(out, f)).mtime.toISOString(),
        asks: (c.asks || []).slice(0, 3),
        objections: (c.objections || []).slice(0, 2),
        wants: (c.wants || []).slice(0, 2),
        top_liked: (c.top_liked || []).slice(0, 2).map((x) => ({ likes: x.likes, text: (x.text || '').slice(0, 140) })),
      });
    } catch { /* a malformed comment file must not break the desk */ }
  }
  comments.sort((a, b) => String(b.at).localeCompare(String(a.at)));

  // Thumbnail forensics is a different question — what the winners' packaging looks like —
  // and only the CI runner can fetch i.ytimg.com. It lands as a side file; the desk shows it
  // when present and says nothing when the network refused.
  let thumbnails = null;
  const thumbsFile = join(out, 'thumbnails.json');
  if (existsSync(thumbsFile)) {
    try {
      const t = JSON.parse(readFileSync(thumbsFile, 'utf8'));
      if (t.status === 'ok' && t.n) {
        thumbnails = {
          topic: t.topic || '',
          n: t.n,
          face_rate: t.face_rate,
          avg_contrast: t.avg_contrast,
          avg_busy: t.avg_busy,
          reading: t.reading || '',
          hue_families: (t.hue_families || []).slice(0, 3),
          samples: (t.samples || []).slice(0, 3).map((s) => ({
            id: s.id,
            hex: s.dominant?.hex || null,
            face: s.face_upper_half,
          })),
        };
      }
    } catch { /* a malformed thumbnail file must not break the desk */ }
  }

  writeFileSync(index, JSON.stringify({ updated: new Date().toISOString(), reports: merged, comments, thumbnails }, null, 2) + '\n');
  return { index, count: merged.length, reports: merged, comments: comments.length };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const { index, count, comments } = buildIndex(process.argv[2]);
  console.log(`index: ${count} reports, ${comments} comment analyses -> ${index}`);
}
