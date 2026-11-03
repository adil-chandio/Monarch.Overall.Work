#!/usr/bin/env node
/**
 * Build `public/yt-intel/index.json` from whatever reports are on disk.
 *
 * The UI never runs Python and never runs a scraper; it reads this one small file. That
 * keeps the research desk instant, offline-capable and impossible to fake: every card
 * points at the full report it came from.
 *
 * Usage: node scripts/yt-index.mjs [slug]   (slug = refresh just that report, optional)
 */
import { existsSync, readdirSync, readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, basename } from 'node:path';

const OUT = process.env.YT_INTEL_OUT || join('public', 'yt-intel');
const INDEX = join(OUT, 'index.json');
const only = process.argv[2];

function entryFor(file) {
  const data = JSON.parse(readFileSync(file, 'utf8'));
  const d = data.decision || {};
  return {
    topic: data.topic || basename(file, '.json'),
    at: data.fetched_at ? new Date(data.fetched_at * 1000).toISOString() : new Date().toISOString(),
    file: basename(file),
    lane: data.lane || 'unknown',
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
    } : null,
    title_signal: data.title_signal?.status === 'ok' ? {
      strength: data.title_signal.strength, read: data.title_signal.read, n: data.title_signal.n,
    } : null,
  };
}

if (!existsSync(OUT)) mkdirSync(OUT, { recursive: true });
const files = existsSync(OUT) ? readdirSync(OUT).filter((f) => f.endsWith('.json') && f !== 'index.json') : [];
const picked = only ? files.filter((f) => f.replace(/\.json$/, '').includes(only)) : files;

let previous = { reports: [] };
if (existsSync(INDEX)) {
  try { previous = JSON.parse(readFileSync(INDEX, 'utf8')); } catch { /* rebuild from scratch */ }
}
const fresh = picked.map((f) => entryFor(join(OUT, f)));
const merged = [...fresh, ...(previous.reports || []).filter((r) => !fresh.some((f) => f.topic === r.topic))]
  .sort((a, b) => String(b.at).localeCompare(String(a.at)))
  .slice(0, 40);

writeFileSync(INDEX, JSON.stringify({ updated: new Date().toISOString(), reports: merged }, null, 2) + '\n');
console.log(`index: ${merged.length} reports -> ${INDEX}`);
