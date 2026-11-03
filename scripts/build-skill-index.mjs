#!/usr/bin/env node
/**
 * Builds skills/INDEX.md + docs/repo-intel/skills-index.json by reading every
 * SKILL.md frontmatter in skills/. Run after vendoring anything new.
 *
 *   node scripts/build-skill-index.mjs
 */
import { readdirSync, readFileSync, writeFileSync, existsSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';

const ROOT = new URL('..', import.meta.url).pathname;
const SKILLS = join(ROOT, 'skills');

const walk = (dir, out = []) => {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === 'node_modules' || entry.name === '.git') continue;
    const p = join(dir, entry.name);
    if (entry.isDirectory()) walk(p, out);
    else if (entry.name === 'SKILL.md') out.push(p);
  }
  return out;
};

const frontmatter = (text) => {
  const m = text.match(/^---\s*\n([\s\S]*?)\n---/);
  if (!m) return {};
  const out = {};
  for (const line of m[1].split('\n')) {
    const kv = line.match(/^([a-zA-Z_-]+):\s*(.+)$/);
    if (kv) out[kv[1]] = kv[2].replace(/^["']|["']$/g, '').trim();
  }
  return out;
};

// space routing by pack name and by skill keywords
const PACK_SPACE = {
  hyperframes: 'monarch-studio', 'video-shotcraft': 'monarch-studio', 'vox-collage-motion': 'monarch-studio',
  'opus55-code-motion': 'monarch-studio', director: 'monarch-studio', 'capcut-cli': 'monarch-studio',
  'claude-code-video-toolkit': 'monarch-studio', 'ffmpeg-skill': 'monarch-studio', 'html-video': 'monarch-studio',
  distilly: 'monarch-studio',
  humanizer: 'ops', scrapling: 'ops', 'agent-reach': 'ops', last30days: 'ops', 'deep-research': 'ops',
  marketingskills: 'personal-brand', 'baoyu-skills': 'personal-brand',
  'claude-skills': 'ops', 'wshobson-agents': 'ops', ponytail: 'ops', 'planning-with-files': 'ops',
  'skill-seekers': 'ops', 'prompt-master': 'ops', 'book-to-skill': 'ops', 'elephant-goldfish': 'ops',
  'website-cloner': 'monarch-studio', 'html-anything': 'monarch-studio',
};

const KEYWORD_SPACE = [
  [/\b(youtube|youtube-?shorts|thumbnail|channel|upload|ctr|retention|script|voice-?over|tts|facet?less|swipe)\b/gi, 'yt-automation'],
  [/\b(video|film|motion|edit|render|ffmpeg|audio|sound|music|mix|loudness|color grade|remotion|b-?roll|subtitle|caption burn)\b/gi, 'monarch-studio'],
  [/\b(instagram|tiktok|social|caption|copywriting|copy|post|brand|pillar|hook|newsletter|email|outreach)\b/gi, 'personal-brand'],
  [/\b(seo|landing|portfolio|website|clone|design system|typography)\b/gi, 'portfolio'],
  [/\b(agent|scrape|scraping|research|plan|skill|prompt|review|test|deploy|finance|invoice|git|database|supabase|security)\b/gi, 'ops'],
];

// Keyword evidence outranks the pack default: a marketing skill that talks about
// thumbnails belongs to yt-automation, not to whichever pack it shipped in.
const route = (pack, text) => {
  const counts = KEYWORD_SPACE.map(([re, space]) => ({
    space,
    hits: (text.match(new RegExp(re.source, 'gi')) || []).length,
  })).sort((a, b) => b.hits - a.hits);
  if (counts[0] && counts[0].hits > 0) {
    // a single generic word is weak evidence; require 2 hits OR no pack mapping
    if (counts[0].hits >= 2 || !PACK_SPACE[pack]) return counts[0].space;
  }
  return PACK_SPACE[pack] || 'ops';
};

const files = walk(SKILLS);
const entries = [];

for (const file of files) {
  const rel = relative(SKILLS, file);
  const pack = rel.split('/')[0];
  const text = readFileSync(file, 'utf8');
  const fm = frontmatter(text);
  const name = fm.name || rel.split('/').slice(-2)[0] || pack;
  const desc = (fm.description || text.split('\n').find((l) => l.trim() && !l.startsWith('---') && !l.startsWith('#')) || '').slice(0, 220);
  entries.push({
    name,
    pack,
    space: route(pack, `${name} ${desc}`),
    path: `skills/${rel}`,
    bytes: statSync(file).size,
    license: fm.license || '',
  });
}

entries.sort((a, b) => a.space.localeCompare(b.space) || a.pack.localeCompare(b.pack) || a.name.localeCompare(b.name));

const bySpace = entries.reduce((acc, e) => { (acc[e.space] ||= []).push(e); return acc; }, {});

const packs = [...new Set(entries.map((e) => e.pack))].sort();

const lines = [
  '# Skills index',
  '',
  `Generated ${new Date().toISOString().slice(0, 10)} by \`scripts/build-skill-index.mjs\`. Do not edit by hand.`,
  '',
  `**${entries.length} skills across ${packs.length} packs.** Every pack is vendored read-only with provenance in its \`MONARCH-PROVENANCE.md\`.`,
  '',
  '## Routing',
  '',
  '| Space | Skills | Packs |',
  '|---|---|---|',
];

for (const [space, list] of Object.entries(bySpace).sort((a, b) => b[1].length - a[1].length)) {
  const p = [...new Set(list.map((e) => e.pack))].sort().join(', ');
  lines.push(`| \`${space}\` | ${list.length} | ${p} |`);
}

lines.push('', '## All skills', '');
for (const [space, list] of Object.entries(bySpace).sort((a, b) => a[0].localeCompare(b[0]))) {
  lines.push(`### ${space}`, '', '| Skill | Pack | Size | File |', '|---|---|---|---|');
  for (const e of list) lines.push(`| \`${e.name}\` | ${e.pack} | ${(e.bytes / 1024).toFixed(1)} KB | \`${e.path}\` |`);
  lines.push('');
}

writeFileSync(join(SKILLS, 'INDEX.md'), lines.join('\n'));
writeFileSync(join(ROOT, 'docs/repo-intel/skills-index.json'), JSON.stringify({
  generated: new Date().toISOString().slice(0, 10),
  total: entries.length,
  packs: packs.length,
  bySpace: Object.fromEntries(Object.entries(bySpace).map(([k, v]) => [k, v.length])),
  entries,
}, null, 2));

console.log(`${entries.length} skills · ${packs.length} packs`);
console.log(Object.fromEntries(Object.entries(bySpace).map(([k, v]) => [k, v.length])));
console.log('wrote skills/INDEX.md and docs/repo-intel/skills-index.json');
