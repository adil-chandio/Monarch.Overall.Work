#!/usr/bin/env node
/**
 * Shallow clone a repo into .harvest/<slug>, then copy only skill-shaped files
 * (SKILL.md trees, references, licenses) into skills/<slug>/.
 * Skips node_modules, .git, media, and anything over the per-file cap.
 * Prints a JSON line so the caller can record provenance.
 */
import { execFileSync } from 'node:child_process';
import { mkdirSync, rmSync, cpSync, existsSync, readdirSync, statSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const argv = process.argv.slice(2);
const opt = (name) => {
  const i = argv.indexOf(`--${name}`);
  if (i === -1) return null;
  const v = argv[i + 1];
  argv.splice(i, 2);
  return v ?? true;
};
// include globs, e.g. --include data/** --include prompts/**
const includes = [];
for (let i = argv.length - 1; i >= 0; i -= 1) {
  if (argv[i] === '--include') { includes.unshift(argv[i + 1]); argv.splice(i, 2); }
}
const [repo, slugArg, licenseNote = ''] = argv;
const slug = slugArg || repo.split('/')[1].toLowerCase();
const root = process.cwd();
const tmp = join(root, '.harvest', slug);
const dest = join(root, 'skills', slug);

const sh = (cmd, args, opts = {}) => execFileSync(cmd, args, { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024, ...opts });

const defaultBranch = sh('gh', ['api', `repos/${repo}`, '--jq', '.default_branch']).trim();
const sha = sh('gh', ['api', `repos/${repo}/commits/${defaultBranch}`, '--jq', '.sha']).trim();

rmSync(tmp, { recursive: true, force: true });
mkdirSync(tmp, { recursive: true });

try {
  sh('git', ['clone', '--depth', '1', '--filter=blob:none', '--no-checkout', `https://github.com/${repo}.git`, tmp]);
  sh('git', ['-C', tmp, 'sparse-checkout', 'init', '--no-cone']);
  writeFileSync(join(tmp, '.git', 'info', 'sparse-checkout'), [
    '/SKILL.md', '/AGENTS.md', '/CLAUDE.md', '/README.md', '/LICENSE*', '/NOTICE*', '/ROADMAP.md',
    '/*/SKILL.md', '/*/*/SKILL.md', '/*/*/*/SKILL.md', '/*/*/*/*/SKILL.md',
    '/skills/**', '/references/**', '/*/references/**', '/*/*/references/**',
    '/scripts/**', '/*/scripts/**',
    '/.agents/skills/**', '/.claude/skills/**', '/.codex/skills/**',
    '/docs/**', '/docs/adr/**', '/assets/scripts/**',
    ...includes.map((g) => `/${g}`),
  ].join('\n'));
  sh('git', ['-C', tmp, 'checkout', '--quiet']);
} catch (error) {
  console.error(`CLONE FAILED ${repo}: ${String(error.message).split('\n')[0]}`);
  process.exit(2);
}

// size guard: drop single files over 2 MB and media extensions
const MEDIA = /\.(png|jpe?g|gif|webp|mp4|mov|mp3|wav|zip|pdf|woff2?|ttf|otf|svg)$/i;
const walk = (dir) => readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
  if (e.name === '.git' || e.name === 'node_modules') return [];
  const p = join(dir, e.name);
  if (e.isSymbolicLink()) {
    // keep only symlinks that resolve; drop the rest (they break on clone and on CI)
    try { statSync(p); return [p]; } catch { rmSync(p, { force: true }); droppedLinks += 1; return []; }
  }
  return e.isDirectory() ? walk(p) : [p];
});
let droppedLinks = 0;
let dropped = 0;
for (const file of walk(tmp)) {
  const keep = !MEDIA.test(file) && statSync(file).size < 2 * 1024 * 1024;
  if (!keep) { rmSync(file, { force: true }); dropped += 1; }
}

rmSync(dest, { recursive: true, force: true });
mkdirSync(dest, { recursive: true });
cpSync(tmp, dest, { recursive: true, dereference: true, filter: (src) => !src.includes('/.git') });

const files = walk(dest).length;
const skillFiles = walk(dest).filter((f) => /SKILL\.md$|AGENTS\.md$/.test(f)).length;

// provenance header
const header = `# ${repo}

- **Vendored:** ${new Date().toISOString().slice(0, 10)}
- **Upstream:** https://github.com/${repo}
- **Commit:** \`${sha}\`
- **License:** ${licenseNote || 'see LICENSE in this folder'}
- **Vendored by:** \`scripts/vendor-skill.mjs\` — skills only, no media, no node_modules
- **Rule:** read-only reference. Do not edit files here; note adaptations in \`skills/${slug}/MONARCH-NOTES.md\`.
`;
writeFileSync(join(dest, 'MONARCH-PROVENANCE.md'), header);

rmSync(tmp, { recursive: true, force: true });
console.log(JSON.stringify({ repo, slug, sha, files, skillFiles, dropped, brokenLinks: droppedLinks, includes, ok: true }));
