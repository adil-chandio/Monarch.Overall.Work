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
      reading: data.saturation.reading,
    } : null,
    // The headline number on the card. `score` alone is not enough to act on: 57 with
    // confidence 0.85 and 57 with confidence 0.3 are different instructions.
    confidence: d.confidence ?? null,
    mechanism: d.parts?.mechanism ?? null,
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
    ? readdirSync(out).filter((f) => f.endsWith('.json') && f !== 'index.json')
    : [];
  const picked = only ? files.filter((f) => f.replace(/\.json$/, '').includes(only)) : files;

  let previous = { reports: [] };
  if (existsSync(index)) {
    try { previous = JSON.parse(readFileSync(index, 'utf8')); } catch { /* rebuild from scratch */ }
  }
  const fresh = picked.map((f) => entryFor(join(out, f)));
  const merged = [...fresh, ...(previous.reports || []).filter((r) => !fresh.some((f) => f.topic === r.topic))]
    .sort((a, b) => String(b.at).localeCompare(String(a.at)))
    .slice(0, 40);

  writeFileSync(index, JSON.stringify({ updated: new Date().toISOString(), reports: merged }, null, 2) + '\n');
  return { index, count: merged.length, reports: merged };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const { index, count } = buildIndex(process.argv[2]);
  console.log(`index: ${count} reports -> ${index}`);
}
