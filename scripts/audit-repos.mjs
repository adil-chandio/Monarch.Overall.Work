#!/usr/bin/env node
/**
 * Repo audit — compares config/repos.json with what GitHub actually reports.
 * Usage:  node scripts/audit-repos.mjs          (needs `gh` authenticated)
 *         node scripts/audit-repos.mjs --offline (config only, no network)
 * Exit 1 on drift so CI can fail loudly instead of silently rotting.
 */
import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';

const CFG = JSON.parse(readFileSync(new URL('../config/repos.json', import.meta.url), 'utf8'));
const offline = process.argv.includes('--offline');

const declared = new Map(CFG.repos.map((r) => [r.name, r]));

let live = [];
if (!offline) {
  try {
    const out = execFileSync('gh', [
      'api', `users/${CFG.owner}/repos?per_page=100`,
      '--jq', '[.[] | {name, size, private, language, pushed_at}]',
    ], { encoding: 'utf8', maxBuffer: 8 * 1024 * 1024 });
    live = JSON.parse(out);
  } catch (error) {
    console.error('GitHub API unreachable — falling back to offline mode.');
    console.error(String(error.message).split('\n')[0]);
  }
}

const pad = (v, n) => String(v ?? '-').padEnd(n).slice(0, n);
const rows = [];
const problems = [];

if (live.length) {
  for (const repo of live) {
    const cfg = declared.get(repo.name);
    if (!cfg) problems.push(`untracked repo: ${repo.name} (${Math.floor(repo.size / 1024)} MB)`);
    rows.push({
      name: repo.name,
      sizeMb: Math.floor(repo.size / 1024),
      role: cfg?.role ?? 'UNTRACKED',
      space: cfg?.space ?? '-',
      status: cfg?.status ?? 'unknown',
    });
  }
  for (const name of declared.keys()) {
    if (!live.some((r) => r.name === name)) problems.push(`declared but not on GitHub: ${name}`);
  }
} else {
  for (const repo of CFG.repos) {
    rows.push({ name: repo.name, sizeMb: repo.size_mb, role: repo.role, space: repo.space ?? '-', status: repo.status });
  }
}

rows.sort((a, b) => b.sizeMb - a.sizeMb);

console.log(`\nMONARCH® repo audit — ${rows.length} repos${offline ? ' (offline)' : ''}\n`);
console.log(pad('REPO', 32) + pad('SIZE', 9) + pad('ROLE', 14) + pad('SPACE', 18) + 'STATUS');
console.log('-'.repeat(90));
for (const r of rows) {
  console.log(pad(r.name, 32) + pad(`${r.sizeMb} MB`, 9) + pad(r.role, 14) + pad(r.space, 18) + r.status);
}

const totalMb = rows.reduce((s, r) => s + Number(r.sizeMb || 0), 0);
const empty = rows.filter((r) => !r.sizeMb).length;
const archive = rows.filter((r) => r.status === 'archived-candidate').length;

console.log('-'.repeat(90));
console.log(`${rows.length} repos · ${totalMb} MB total · ${empty} empty · ${archive} archive candidates`);

if (problems.length) {
  console.log('\nDRIFT:');
  for (const p of problems) console.log(`  ! ${p}`);
  process.exit(1);
}
console.log('\nNo drift. config/repos.json matches GitHub.\n');
