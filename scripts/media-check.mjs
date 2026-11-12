#!/usr/bin/env node
/**
 * media-check.mjs — the one place that decides what may enter Git.
 *
 * Reads config/media-policy.json and enforces it. Two modes:
 *
 *   node scripts/media-check.mjs --staged   # pre-commit: only what is being committed
 *   node scripts/media-check.mjs --all      # CI / audit: the whole tracked tree
 *
 * Exit 0 = clean. Exit 1 = violations. Nothing is ever deleted or modified: this
 * script only reports. Deleting is a human decision with an index line attached.
 *
 * Why this exists: .gitignore had one line (deliverables/*.mp4) and one directory
 * deep it silently stopped working. 185 media files totalling 1.1 GB are tracked
 * today. A rule that lives in prose gets forgotten; a rule that lives in CI does not.
 */
import { execFileSync } from "node:child_process";
import { readFileSync, statSync, existsSync } from "node:fs";
import { extname, resolve } from "node:path";

const ROOT = resolve(import.meta.dirname, "..");
const POLICY_PATH = resolve(ROOT, "config/media-policy.json");

/* ---------- tiny helpers ---------- */

const RED = "\x1b[31m", YEL = "\x1b[33m", GRN = "\x1b[32m", DIM = "\x1b[2m", RST = "\x1b[0m";
const bold = (s) => `\x1b[1m${s}${RST}`;

function mb(bytes) {
  return `${(bytes / 1_048_576).toFixed(1)} MB`;
}

function git(args, opts = {}) {
  return execFileSync("git", args, { cwd: ROOT, encoding: "utf8", maxBuffer: 256 * 1024 * 1024, ...opts });
}

function loadPolicy() {
  if (!existsSync(POLICY_PATH)) {
    console.error(`${RED}config/media-policy.json is missing.${RST} The guard has no rule to enforce.`);
    process.exit(1);
  }
  return JSON.parse(readFileSync(POLICY_PATH, "utf8"));
}

/** Build ext -> kind map, e.g. ".mp4" -> "video". */
function buildExtMap(policy) {
  const map = new Map();
  for (const [kind, exts] of Object.entries(policy.media_extensions)) {
    for (const ext of exts) map.set(ext.toLowerCase(), kind);
  }
  return map;
}

/** Convert a keep-list glob into a regex. Supports **, *, and trailing / for "inside this dir". */
function globToRegex(glob) {
  let out = "";
  const g = glob.replace(/\/+$/, "");
  for (let i = 0; i < g.length; i++) {
    const c = g[i];
    if (c === "*") {
      if (g[i + 1] === "*") {
        // ** — swallow the following slash too, so docs/**/*.csv.gz matches docs/a/b.csv.gz
        out += ".*";
        i++;
        if (g[i + 1] === "/") i++;
      } else {
        out += "[^/]*";
      }
    } else if ("\\^$+.()|{}[]".includes(c)) {
      out += "\\" + c;
    } else {
      out += c;
    }
  }
  return new RegExp(`^${out}(${glob.endsWith("/") ? "/.*" : ""})$`);
}

function isKeptInGit(path, policy) {
  const keep = policy.keep_in_git?.paths ?? [];
  for (const glob of keep) {
    if (globToRegex(glob).test(path)) return glob;
    // a bare directory entry like public/thumbnails/ must also match the dir itself
    if (glob.endsWith("/") && (path === glob || path.startsWith(glob))) return glob;
  }
  return null;
}

/* ---------- collect the file list + sizes ---------- */

function trackedFilesWithSizes() {
  // ls-tree -l gives "<mode> <type> <sha> <size>\t<path>" — one pass, no stat calls.
  const out = git(["ls-tree", "-r", "-l", "HEAD"]);
  const rows = [];
  for (const line of out.split("\n")) {
    if (!line) continue;
    const tab = line.indexOf("\t");
    if (tab === -1) continue;
    const meta = line.slice(0, tab).trim().split(/\s+/);
    const path = line.slice(tab + 1);
    if (meta[1] !== "blob") continue;
    const size = meta[3] === "-" ? 0 : Number(meta[3]);
    rows.push({ path, bytes: size });
  }
  return rows;
}

function stagedFilesWithSizes() {
  // ACM = added/copied/modified. Deletions have no content to check.
  const out = git(["diff", "--cached", "--name-only", "--diff-filter=ACM", "-z"]);
  const paths = out.split("\0").filter(Boolean);
  const rows = [];
  for (const p of paths) {
    const abs = resolve(ROOT, p);
    let bytes = 0;
    try {
      bytes = statSync(abs).size;
    } catch {
      continue; // staged deletion or unreadable; nothing to weigh
    }
    rows.push({ path: p, bytes });
  }
  return rows;
}

/* ---------- checks ---------- */

function check(rows, policy, { mode }) {
  const extMap = buildExtMap(policy);
  const hard = policy.size_gate.hard_fail_bytes;
  const warn = policy.size_gate.warn_bytes;

  const violations = [];
  const warnings = [];
  const keptHits = [];
  let mediaTracked = 0;
  let mediaBytes = 0;

  for (const { path, bytes } of rows) {
    const ext = extname(path).toLowerCase();
    const kind = extMap.get(ext);

    // 1. hard single-file ceiling — applies to EVERY file, media or not
    if (bytes >= hard) {
      violations.push({
        path,
        bytes,
        rule: "size_gate.hard_fail_bytes",
        why: `${mb(bytes)} is at or over GitHub's hard 100 MB file ceiling. A push with this file is rejected, so the commit would be built on a lie.`,
        fix: "move it out of Git and record it in deliverables/INDEX.md instead",
      });
      continue;
    }

    if (!kind) continue; // text, code, small binaries — not our business

    mediaTracked++;
    mediaBytes += bytes;

    // 2. media in a keep-list path is allowed
    const kept = isKeptInGit(path, policy);
    if (kept) {
      keptHits.push({ path, bytes, glob: kept });
      continue;
    }

    // 3. media outside the keep list is a violation
    violations.push({
      path,
      bytes,
      rule: `media_extensions.${kind}`,
      why: `a ${kind} file is tracked in Git and is not on keep_in_git.paths. It will sit in history forever and be cloned by everyone, forever.`,
      fix: "git rm --cached it (the file stays on disk), then add a line to deliverables/INDEX.md saying where it lives",
    });
  }

  // 4. per-file warn for non-media big files
  for (const { path, bytes } of rows) {
    if (bytes >= warn && bytes < hard && !extMap.has(extname(path).toLowerCase())) {
      warnings.push({ path, bytes, why: `non-media file is ${mb(bytes)} — large data in Git` });
    }
  }

  return { violations, warnings, keptHits, mediaTracked, mediaBytes, fileCount: rows.length, totalBytes: rows.reduce((s, r) => s + r.bytes, 0) };
}

/* ---------- report ---------- */

function report({ violations, warnings, keptHits, mediaTracked, mediaBytes, fileCount, totalBytes }, policy, mode) {
  const scale = policy.repo_budget;
  const budgetPct = (totalBytes / scale.target_bytes) * 100;

  console.log(bold(`\nmedia-check · mode=${mode}`));
  console.log(`${DIM}rule: ${policy.principle.git_holds}${RST}\n`);

  if (mode === "staged") {
    console.log(`  being committed     ${mb(totalBytes)} in ${fileCount} file(s)`);
    console.log(`  of which media      ${mb(mediaBytes)} across ${mediaTracked} file(s)\n`);
  } else {
    console.log(`  tracked tree        ${mb(totalBytes)}`);
    console.log(`  of which media      ${mb(mediaBytes)} across ${mediaTracked} files`);
    console.log(`  budget (${scale.target_human})  ${budgetPct.toFixed(1)}% used\n`);
  }

  if (keptHits.length) {
    const keptBytes = keptHits.reduce((s, k) => s + k.bytes, 0);
    console.log(`${GRN}allowed (keep_in_git)${RST}  ${keptHits.length} files, ${mb(keptBytes)}`);
    const byGlob = new Map();
    for (const k of keptHits) byGlob.set(k.glob, (byGlob.get(k.glob) ?? 0) + k.bytes);
    for (const [g, b] of [...byGlob].sort((a, b) => b[1] - a[1])) {
      console.log(`  ${g.padEnd(56)} ${mb(b).padStart(9)}`);
    }
    console.log();
  }

  if (warnings.length) {
    console.log(`${YEL}warnings${RST} (${warnings.length})`);
    for (const w of warnings.slice(0, 10)) console.log(`  ${mb(w.bytes).padStart(9)}  ${w.path}`);
    if (warnings.length > 10) console.log(`  … and ${warnings.length - 10} more`);
    console.log();
  }

  if (!violations.length) {
    console.log(`${GRN}✓ no media violations${RST} — Git holds knowledge only\n`);
    if (totalBytes > scale.warn_bytes) {
      console.log(`${YEL}⚠ repo tree is above ${(scale.warn_bytes / 1_073_741_824).toFixed(1)} GB${RST} — see docs/architecture/07-MEDIA-AND-REPO-SIZE.md\n`);
    }
    return 0;
  }

  // group by rule so the output is a to-do list, not a wall
  const byRule = new Map();
  for (const v of violations) {
    if (!byRule.has(v.rule)) byRule.set(v.rule, []);
    byRule.get(v.rule).push(v);
  }

  console.log(`${RED}✗ ${violations.length} violations${RST}`);
  for (const [rule, list] of byRule) {
    const bytes = list.reduce((s, v) => s + v.bytes, 0);
    console.log(`\n  ${bold(rule)}  ${list.length} files · ${mb(bytes)}`);
    console.log(`  ${DIM}${list[0].why}${RST}`);
    for (const v of list.slice(0, 8)) console.log(`    ${mb(v.bytes).padStart(9)}  ${v.path}`);
    if (list.length > 8) console.log(`    … and ${list.length - 8} more`);
  }

  console.log(`\n  ${bold("fix:")} ${violations[0].fix}`);
  console.log(`  ${DIM}full instructions: docs/architecture/07-MEDIA-AND-REPO-SIZE.md${RST}\n`);
  return 1;
}

/* ---------- main ---------- */

const arg = process.argv[2];
const mode = arg === "--staged" ? "staged" : arg === "--all" ? "all" : null;
if (!mode) {
  console.error("usage: node scripts/media-check.mjs --staged | --all");
  process.exit(2);
}

const policy = loadPolicy();
const rows = mode === "staged" ? stagedFilesWithSizes() : trackedFilesWithSizes();

if (mode === "staged" && rows.length === 0) {
  process.exit(0); // nothing staged, nothing to say
}

process.exit(report(check(rows, policy, { mode }), policy, mode));
