#!/usr/bin/env node
/**
 * check-tracked-ignored.mjs — the mechanism that actually shrinks a repo.
 *
 * An ignore rule does two things:
 *   1. stops NEW files matching it from being committed        (already worked)
 *   2. makes `git add <dir>` skip matching files, EVEN IF they
 *      are already tracked — verified experimentally:
 *
 *        tracked a.png + `*.png` in .gitignore + `git add dir/`
 *        => a.png modification is NOT staged
 *
 *        ignored a.png + `git add dir/`
 *        => only the non-ignored sibling is staged, exit 0, no error
 *
 * That second property is the lever. Add the rule, and the 20 workflows that
 * `git add production/…` stop re-adding images all by themselves — no workflow
 * edit, no broken pipeline, no 20-file refactor that has to be verified one by one.
 *
 * This script reports the gap between "tracked" and "should be ignored":
 * every tracked path that the current .gitignore would refuse to re-add.
 *
 *   node scripts/check-tracked-ignored.mjs            # summary
 *   node scripts/check-tracked-ignored.mjs --list     # every path
 *   node scripts/check-tracked-ignored.mjs --json
 */
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const ROOT = resolve(import.meta.dirname, "..");
const POLICY = JSON.parse(readFileSync(resolve(ROOT, "config/media-policy.json"), "utf8"));

const git = (args, opts = {}) =>
  execFileSync("git", args, { cwd: ROOT, encoding: "utf8", maxBuffer: 512 * 1024 * 1024, ...opts });

function human(b) {
  if (b >= 1_073_741_824) return `${(b / 1_073_741_824).toFixed(2)} GB`;
  if (b >= 1_048_576) return `${(b / 1_048_576).toFixed(1)} MB`;
  if (b >= 1024) return `${(b / 1024).toFixed(0)} KB`;
  return `${b} B`;
}

/* ---------- tracked files with sizes ---------- */
const rows = [];
for (const line of git(["ls-tree", "-r", "-l", "HEAD"]).split("\n")) {
  if (!line) continue;
  const tab = line.indexOf("\t");
  if (tab === -1) continue;
  const meta = line.slice(0, tab).trim().split(/\s+/);
  if (meta[1] !== "blob") continue;
  rows.push({ path: line.slice(tab + 1), bytes: meta[3] === "-" ? 0 : Number(meta[3]) });
}

/* ---------- which of them would now be refused by .gitignore ---------- */
// --no-index is essential: without it check-ignore consults the index first and
// silently skips every tracked file — which is exactly the set we are asking about.
const paths = rows.map((r) => r.path);
let ignoredSet = new Set();
try {
  const out = git(["check-ignore", "--no-index", "--stdin", "-z"], { input: paths.join("\0") + "\0" });
  ignoredSet = new Set(out.split("\0").filter(Boolean));
} catch (e) {
  // check-ignore exits 1 when nothing matches — that is a valid answer, not a failure
  const out = (e.stdout ?? "").toString();
  ignoredSet = new Set(out.split("\0").filter(Boolean));
}

const stale = rows.filter((r) => ignoredSet.has(r.path));
const staleBytes = stale.reduce((s, r) => s + r.bytes, 0);
const trackedBytes = rows.reduce((s, r) => s + r.bytes, 0);

/* ---------- group by top folder ---------- */
const byTop = new Map();
for (const r of stale) {
  const top = r.path.split("/")[0];
  const cur = byTop.get(top) ?? { bytes: 0, count: 0 };
  cur.bytes += r.bytes;
  cur.count += 1;
  byTop.set(top, cur);
}

/* ---------- keep-list sanity: nothing load-bearing may be stale ---------- */
const keep = POLICY.keep_in_git?.paths ?? [];
const keepViolations = stale.filter((r) =>
  keep.some((glob) => {
    const g = glob.replace(/\/+$/, "");
    return r.path === g || r.path.startsWith(g + "/") || r.path.startsWith(g);
  })
);

/* ---------- report ---------- */
if (process.argv.includes("--json")) {
  console.log(JSON.stringify({
    tracked_files: rows.length,
    tracked_bytes: trackedBytes,
    stale_tracked_files: stale.length,
    stale_tracked_bytes: staleBytes,
    by_top_folder: Object.fromEntries(byTop),
    keep_list_violations: keepViolations.map((r) => r.path),
    detail: process.argv.includes("--list") ? stale : undefined,
  }, null, 2));
} else {
  const RED = "\x1b[31m", GRN = "\x1b[32m", YEL = "\x1b[33m", DIM = "\x1b[2m", RST = "\x1b[0m";
  console.log(`\ntracked-but-ignored audit\n`);
  console.log(`  tracked tree                 ${human(trackedBytes)} in ${rows.length} files`);
  console.log(
    stale.length
      ? `  would be refused on re-add   ${RED}${human(staleBytes)} in ${stale.length} files${RST}`
      : `  would be refused on re-add   ${GRN}none${RST}`
  );
  console.log(`  ${DIM}these files are still in Git, but \`git add <dir>\` now skips them.${RST}`);
  console.log(`  ${DIM}they leave Git only when you run \`git rm --cached\` on purpose.${RST}\n`);

  if (byTop.size) {
    console.log("  by top-level folder");
    for (const [top, v] of [...byTop].sort((a, b) => b[1].bytes - a[1].bytes)) {
      console.log(`    ${top.padEnd(36)} ${human(v.bytes).padStart(9)}  ${String(v.count).padStart(4)} files`);
    }
    console.log();
  }

  if (keepViolations.length) {
    console.log(`${YEL}⚠ keep-list files caught by an ignore rule (${keepViolations.length})${RST}`);
    for (const v of keepViolations.slice(0, 10)) console.log(`    ${v.path}`);
    console.log(`  ${DIM}these must stay in Git — add a !exception before shipping the rule.${RST}\n`);
  }

  if (process.argv.includes("--list") && stale.length) {
    console.log("  every stale path");
    for (const r of stale.sort((a, b) => b.bytes - a.bytes)) {
      console.log(`    ${human(r.bytes).padStart(9)}  ${r.path}`);
    }
    console.log();
  }
}
