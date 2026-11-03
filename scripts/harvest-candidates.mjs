#!/usr/bin/env node
/**
 * Candidate harvester — sweeps GitHub topics that matter to the five spaces,
 * scores each repo, and writes docs/repo-intel/candidates.json.
 * Read-only. No clones. Safe to re-run.
 *
 *   node scripts/harvest-candidates.mjs
 */
import { writeFileSync, mkdirSync } from 'node:fs';
import { execFileSync } from 'node:child_process';

const TOPICS = [
  'youtube-automation', 'youtube', 'shorts', 'faceless',
  'text-to-speech', 'tts', 'voice-cloning', 'whisper', 'subtitle',
  'text-to-video', 'video-generation', 'video-editing', 'remotion', 'ffmpeg',
  'music-generation', 'audio-processing', 'sound-design', 'audio-effects',
  'thumbnail', 'content-creation', 'content-automation',
  'ai-agents', 'deep-research', 'web-scraping', 'seo',
  'prompt-engineering', 'claude-skills', 'agent-skills', 'social-media', 'video', 'music', 'agent',
];

// topic -> the space it primarily serves. A repo inherits every space whose topic it appeared under.
const SPACES = {
  'yt-automation': ['youtube-automation', 'youtube', 'shorts', 'faceless', 'subtitle', 'thumbnail', 'text-to-speech', 'tts', 'voice-cloning', 'whisper', 'social-media'],
  'monarch-studio': ['text-to-video', 'video-generation', 'video-editing', 'remotion', 'ffmpeg', 'music-generation', 'audio-processing', 'sound-design', 'audio-effects', 'video', 'music'],
  'personal-brand': ['content-creation', 'content-automation'],
  portfolio: ['portfolio'],
  ops: ['ai-agents', 'deep-research', 'web-scraping', 'seo', 'prompt-engineering', 'claude-skills', 'agent-skills'],
};

const sleep = (ms) => Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);

const gh = (path) => JSON.parse(execFileSync('gh', ['api', path], { encoding: 'utf8', maxBuffer: 16 * 1024 * 1024 }));

const seen = new Map();

for (const topic of TOPICS) {
  for (const page of [1, 2]) {
    let items = [];
    for (let attempt = 0; attempt < 3; attempt += 1) {
      try {
        items = gh(`search/repositories?q=topic:${topic}+stars:>150&sort=stars&order=desc&per_page=30&page=${page}`).items || [];
        break;
      } catch (error) {
        const msg = String(error.message || '');
        if (!msg.includes('rate limit')) { items = []; break; }
        process.stderr.write('r');
        sleep(22000); // search API: 30 requests/minute
      }
    }
    sleep(2200);
    if (!items.length) break;
    for (const it of items) {
      if (seen.has(it.full_name)) {
        seen.get(it.full_name).topics.add(topic);
        continue;
      }
      seen.set(it.full_name, {
        name: it.full_name,
        stars: it.stargazers_count,
        license: it.license?.spdx_id || 'NONE',
        sizeMb: Math.round(it.size / 1024),
        language: it.language,
        pushed: (it.pushed_at || '').slice(0, 10),
        archived: it.archived,
        forks: it.forks_count,
        desc: (it.description || '').slice(0, 160),
        topics: new Set([topic]),
      });
    }
  }
  process.stderr.write(`. ${topic}\n`);
}

const usable = (license) => ['MIT', 'Apache-2.0', 'BSD-3-Clause', 'BSD-2-Clause', 'MPL-2.0', 'CC0-1.0', 'ISC'].includes(license);

const rows = [...seen.values()]
  .filter((r) => !r.archived)
  .map((r) => {
    const t = [...r.topics];
    const spaceScores = Object.entries(SPACES).map(([space, words]) => {
      const hits = t.filter((x) => words.includes(x)).length;
      return { space, hits };
    }).sort((a, b) => b.hits - a.hits);
    const best = spaceScores[0];
    const allSpaces = spaceScores.filter((x) => x.hits > 0).map((x) => x.space);
    const licenseOk = usable(r.license);
    const freshness = r.pushed >= '2026-05-01';
    const score =
      Math.min(40, Math.log10(r.stars + 1) * 9) +
      (licenseOk ? 20 : 0) +
      (freshness ? 15 : 0) +
      Math.min(15, best.hits * 5) +
      (r.sizeMb < 60 ? 10 : r.sizeMb < 200 ? 5 : 0);
    return { ...r, topics: t, space: best.space, spaces: allSpaces, licenseOk, freshness, score: Math.round(score) };
  })
  .sort((a, b) => b.score - a.score);

const payload = {
  generated: new Date().toISOString().slice(0, 10),
  topicsScanned: TOPICS.length,
  totalFound: rows.length,
  bySpace: Object.fromEntries(
    Object.keys(SPACES).map((s) => [s, rows.filter((r) => r.space === s).length])
  ),
  counts: {
    licenseOk: rows.filter((r) => r.licenseOk).length,
    recent: rows.filter((r) => r.freshness).length,
    score60plus: rows.filter((r) => r.score >= 60).length,
  },
  repos: rows,
};

mkdirSync(new URL('../docs/repo-intel/', import.meta.url), { recursive: true });
writeFileSync(new URL('../docs/repo-intel/candidates.json', import.meta.url), JSON.stringify(payload, null, 2));

console.log(`\n${rows.length} unique repos from ${TOPICS.length} topics`);
console.log('by space:', payload.bySpace);
console.log('license-clean:', payload.counts.licenseOk, '| recent:', payload.counts.recent, '| score>=60:', payload.counts.score60plus);
console.log('\nTop 25:');
for (const r of rows.slice(0, 25)) {
  console.log(`${String(r.score).padStart(3)} ${String(r.stars).padStart(7)} ${r.license.padEnd(12)} ${String(r.sizeMb + 'MB').padStart(7)} ${r.space.padEnd(16)} ${r.name}`);
}
