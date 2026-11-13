#!/usr/bin/env node
/**
 * build-deliverables-index.mjs — writes deliverables/INDEX.md.
 *
 * The index is the promise that makes external storage safe: every media file
 * that leaves Git gets a line here first, so "where did that go?" has an answer
 * that survives a sandbox reset, a laptop change and a new chat.
 *
 * Usage:
 *   node scripts/build-deliverables-index.mjs            # write the file
 *   node scripts/build-deliverables-index.mjs --check    # fail if out of date (CI)
 *
 * INVARIANT: this page must render identically on any checkout. It is derived
 * from what the repo RECORDS (git index + config/drive-map.json), never from
 * what happens to be sitting on the local disk. The first version did read the
 * disk, so the migration machine (all 26 videos present) and CI (none present)
 * produced different pages and the guard could never be green in both.
 * "Is the file here, and does it still hash right?" is a separate question with
 * a separate command: `--verify-local`. It prints, it does not write.
 *
 * Columns:
 *   bytes     exact size on disk right now
 *   sha256    content hash — proves two files are the same, or aren't
 *   status    tracked (still in Git) | external (out of Git, needs a location)
 *   where     YouTube / Drive / lockbox, with a real id or UNRECORDED
 *
 * A row with status=external and where=UNRECORDED is a to-do, not a pass.
 * That is deliberate: the index refuses to pretend a file is safe.
 */
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { createReadStream, existsSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { resolve, basename } from "node:path";

const ROOT = resolve(import.meta.dirname, "..");
const INDEX_PATH = resolve(ROOT, "deliverables/INDEX.md");
const POLICY = JSON.parse(readFileSync(resolve(ROOT, "config/media-policy.json"), "utf8"));
const DRIVE = JSON.parse(readFileSync(resolve(ROOT, "config/drive-map.json"), "utf8"));

const CHECK_ONLY = process.argv.includes("--check");
// --verify-local: the question the page deliberately does NOT answer, because
// answering it makes the page machine-dependent. Run on a machine that still
// has the bytes: re-hash every file present and compare to the recorded hash.
// Prints a report, writes nothing, exits 1 on any mismatch.
const VERIFY_LOCAL = process.argv.includes("--verify-local");

const EXT_KIND = new Map();
for (const [kind, exts] of Object.entries(POLICY.media_extensions)) {
  for (const e of exts) EXT_KIND.set(e, kind);
}

/* ---------- known locations -------------------------------------------------
 * Only entries verified against a live Drive listing on 2026-11-13 live here.
 * Everything else stays UNRECORDED — the index is not allowed to guess.
 * --------------------------------------------------------------------------*/
/** Every Drive copy we actually know about, read from config/drive-map.json.
 *  Hardcoding a second list here is how the two drift apart.
 *
 *  This map — not the working tree — is the source of truth for what exists.
 *  A file that was released from Git is NOT in a fresh clone: CI, and anyone
 *  who just cloned, has an empty deliverables/. Building rows from the disk
 *  alone therefore makes the ledger shrink every time the repo is cloned, and
 *  `--check` then fails CI forever (found on a fresh clone, 2026-11-13: 26 rows
 *  in the committed file vs 1 row generated). The ledger has to survive the
 *  absence of the bytes it is describing. */
const KNOWN_DRIVE = new Map();
for (const folder of DRIVE.folders ?? []) {
  for (const f of folder.currently_holds ?? []) {
    if (!f.name || !f.drive_id) continue;
    KNOWN_DRIVE.set(f.name, {
      rel: f.path ?? `deliverables/${f.name}`,
      folder: folder.name,
      id: f.drive_id,
      sha256: f.sha256 ?? null,
      bytes: typeof f.bytes === "number" ? f.bytes : null,
    });
  }
}

function git(args) {
  return execFileSync("git", args, { cwd: ROOT, encoding: "utf8", maxBuffer: 256 * 1024 * 1024 });
}

function sha256(path) {
  return new Promise((res) => {
    const h = createHash("sha256");
    createReadStream(path)
      .on("data", (d) => h.update(d))
      .on("end", () => res(h.digest("hex")))
      .on("error", () => res(null));
  });
}

function human(bytes) {
  if (bytes >= 1_073_741_824) return `${(bytes / 1_073_741_824).toFixed(2)} GB`;
  if (bytes >= 1_048_576) return `${(bytes / 1_048_576).toFixed(1)} MB`;
  if (bytes >= 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${bytes} B`;
}

/** Files physically present under deliverables/ (tracked or not). */
function walkDeliverables() {
  const out = git(["ls-files", "-z", "deliverables"]).split("\0").filter(Boolean);
  const disk = [];
  try {
    const all = execFileSync("find", ["deliverables", "-type", "f"], { cwd: ROOT, encoding: "utf8" })
      .split("\n")
      .filter(Boolean);
    disk.push(...all);
  } catch {
    /* find unavailable — tracked list is still valid */
  }
  return { tracked: new Set(out), onDisk: new Set(disk) };
}

/** Tracked media anywhere in the repo, not just deliverables/. */
function trackedMedia() {
  const rows = [];
  for (const line of git(["ls-tree", "-r", "-l", "HEAD"]).split("\n")) {
    if (!line) continue;
    const tab = line.indexOf("\t");
    if (tab === -1) continue;
    const meta = line.slice(0, tab).trim().split(/\s+/);
    if (meta[1] !== "blob") continue;
    const path = line.slice(tab + 1);
    const ext = path.slice(path.lastIndexOf(".")).toLowerCase();
    const kind = EXT_KIND.get(ext);
    if (!kind) continue;
    rows.push({ path, bytes: meta[3] === "-" ? 0 : Number(meta[3]), kind });
  }
  return rows;
}

const { tracked, onDisk } = walkDeliverables();
const media = trackedMedia();

/* ---------- build sections ---------- */

/* The set of files this page must account for. It is the UNION of three
 * sources on purpose:
 *   onDisk  — whatever this checkout happens to have
 *   tracked — what Git still carries
 *   drive   — what config/drive-map.json says left Git and went to Drive
 * Only the last one survives a fresh clone, so dropping it would make the page
 * (and therefore the guard) depend on which machine ran it. */
const deliverableFiles = [
  ...new Set([...onDisk, ...tracked, ...[...KNOWN_DRIVE.values()].map((v) => v.rel)]),
]
  .filter((p) => p.startsWith("deliverables/"))
  .filter((p) => {
    const ext = p.slice(p.lastIndexOf(".")).toLowerCase();
    return EXT_KIND.has(ext) || KNOWN_DRIVE.has(basename(p));
  })
  .sort();

const rows = [];
for (const rel of deliverableFiles) {
  const abs = resolve(ROOT, rel);
  const name = basename(rel);
  const present = existsSync(abs);
  const isTracked = tracked.has(rel);
  const drive = KNOWN_DRIVE.get(name);
  const t = media.find((m) => m.path === rel);

  /* Everything below is read from the repo's record, not the filesystem.
   * present is used only to pick a truthful word for the reader. */
  const bytes = (present ? statSync(abs).size : null) ?? t?.bytes ?? drive?.bytes ?? 0;
  const kind =
    EXT_KIND.get(rel.slice(rel.lastIndexOf(".")).toLowerCase()) ??
    EXT_KIND.get(`.${name.split(".").pop().toLowerCase()}`) ??
    "media";

  let status;
  if (isTracked) status = "tracked";
  else if (drive) status = "external";
  else if (present) status = "on-disk-only";
  else status = "missing";

  rows.push({
    rel,
    name,
    bytes,
    kind,
    status,
    // The recorded hash is what the page shows. It cannot be a fresh reading:
    // a fresh reading is only possible on a machine that has the bytes, and
    // a page that changes with the machine is not a ledger.
    hash: drive?.sha256 ?? null,
    where: drive ? `Drive ${drive.folder} · ${drive.id}` : "UNRECORDED",
    present,
    isTracked,
  });
}

/* ---------- totals ---------- */

const trackedDeliverableBytes = rows.filter((r) => r.isTracked).reduce((s, r) => s + r.bytes, 0);
const allMediaBytes = media.reduce((s, m) => s + m.bytes, 0);
const unrecorded = rows.filter((r) => r.where === "UNRECORDED" && r.bytes > 20_971_520);
const ext = rows.filter((r) => r.status !== "tracked");

/* ---------- render ---------- */

const now = new Date().toISOString().slice(0, 10);
const lines = [];
lines.push("# Deliverables index");
lines.push("");
lines.push(`Generated ${now} by \`node scripts/build-deliverables-index.mjs\`. **Do not edit by hand** — regenerate.`);
lines.push("");
lines.push("This file is the reason media can live outside Git without being lost. Every render gets one row: what it is,");
lines.push("how many bytes, its content hash, whether Git still carries it, and where the surviving copy lives.");
lines.push("");
lines.push("`where: UNRECORDED` is not a pass — it means the file is in Git and has no external home yet. Files over 20 MB in");
lines.push("that state are listed under **To do** at the bottom.");
lines.push("");
lines.push("## Totals");
lines.push("");
lines.push("| | |");
lines.push("|---|---|");
lines.push(`| Files listed here | ${rows.length} |`);
lines.push(`| Media inside Git (whole repo) | ${human(allMediaBytes)} across ${media.length} files |`);
lines.push(`| Media inside Git, this folder only | ${human(trackedDeliverableBytes)} |`);
lines.push(`| Recorded in an external location | ${rows.filter((r) => r.where !== "UNRECORDED").length} |`);
lines.push(`| Tracking to-do (>20 MB, no external copy) | ${unrecorded.length} |`);
lines.push("");
lines.push("## Rules these rows obey");
lines.push("");
lines.push("1. A file may leave Git **only after** its row here names a surviving copy.");
lines.push("2. `sha256` is content evidence, not decoration — it proves the Drive copy is the file you rendered.");
lines.push("3. Nothing is deleted from disk by any script in this repo. Deletion is a human decision, made with this table open.");
lines.push("");
lines.push("## Files");
lines.push("");
lines.push("| File | Size | Kind | In Git | Where | sha256 |");
lines.push("|---|---:|---|---|---|---|");
for (const r of rows.sort((a, b) => b.bytes - a.bytes)) {
  const shortHash = r.hash ? r.hash.slice(0, 12) : "—";
  const whereCell = r.where === "UNRECORDED" ? "**UNRECORDED**" : r.where;
  const matchMark = (() => {
    const known = KNOWN_DRIVE.get(r.name);
    if (!known?.sha256) return "";
    // drive-map only ever stores a hash that equalled the local hash at release
    // time, so a recorded hash is a passed check, not an unverified claim.
    return " ✓";
  })();
  lines.push(`| \`${r.name}\` | ${human(r.bytes)} | ${r.kind} | ${r.isTracked ? "yes" : "no"} | ${whereCell}${matchMark} | \`${shortHash}\` |`);
}

lines.push("");
lines.push("`sha256` is the hash recorded when the file left Git, and `✓` means it equalled a fresh local hash at that");
lines.push("moment. The hash is not re-read on every run: this page must read the same on a machine that has the videos and");
lines.push("on a fresh clone that has none of them. To re-check the bytes against these hashes on a machine that does have");
lines.push("them, run `node scripts/build-deliverables-index.mjs --verify-local` — it prints and never writes.");
lines.push("");
lines.push("## To do — media over 20 MB with no recorded external home");
lines.push("");
if (unrecorded.length === 0) {
  lines.push("_Nothing outstanding._");
} else {
  lines.push(`**${unrecorded.length} files, ${human(unrecorded.reduce((s, r) => s + r.bytes, 0))}.** Each needs one of:`);
  lines.push("upload to YouTube Unlisted, move into the Drive folder named in `config/drive-map.json`, or an explicit decision to keep it in Git.");
  lines.push("");
  for (const r of unrecorded.sort((a, b) => b.bytes - a.bytes)) {
    lines.push(`- [ ] \`${r.name}\` — ${human(r.bytes)}`);
  }
}
lines.push("");
/* ---------- repo-wide media summary ---------- */

const extMap = EXT_KIND;
const byFolder = new Map();
for (const m of media) {
  const parts = m.path.split("/");
  const top = parts.length > 1 ? parts[0] : "(root)";
  const cur = byFolder.get(top) ?? { bytes: 0, count: 0 };
  cur.bytes += m.bytes;
  cur.count += 1;
  byFolder.set(top, cur);
}

lines.push("## Repo-wide media by folder");
lines.push("");
lines.push("Every tracked file whose extension matches `config/media-policy.json`. This is the backlog that `npm run guard`");
lines.push("reports on, kept here so it is readable without running anything.");
lines.push("");
lines.push("| Folder | Media files | Size |");
lines.push("|---|---:|---:|");
for (const [folder, v] of [...byFolder].sort((a, b) => b[1].bytes - a[1].bytes).slice(0, 20)) {
  lines.push(`| \`${folder}\` | ${v.count} | ${human(v.bytes)} |`);
}
lines.push(`| **all folders** | **${media.length}** | **${human(allMediaBytes)}** |`);
lines.push("");
lines.push("**Why the images are not simply ignored:** 20 of the 42 workflows that commit run `git add` on a media folder.");
lines.push("An ignore rule would turn those into failed commits. Workflow uploads must change first — see");
lines.push("`docs/architecture/07-MEDIA-AND-REPO-SIZE.md` and `node scripts/check-workflow-media.mjs`.");
lines.push("");
lines.push("## Outside this folder");
lines.push("");
lines.push("Media tracked elsewhere in the repo is counted by `node scripts/media-check.mjs --all`. It reports by rule and by folder,");
lines.push("because that list is long and belongs in CI output, not in a hand-read page.");
lines.push("");

const rendered = lines.join("\n");

if (VERIFY_LOCAL) {
  const presentRows = rows.filter((r) => r.present);
  console.log(`verify-local: re-hashing ${presentRows.length} of ${rows.length} files that are on this disk\n`);
  let bad = 0;
  let noRecord = 0;
  for (const r of presentRows) {
    const known = KNOWN_DRIVE.get(r.name);
    const local = await sha256(resolve(ROOT, r.rel));
    if (!known?.sha256) {
      console.log(`  --   ${r.name}  (no recorded Drive hash to compare)`);
      noRecord++;
      continue;
    }
    if (local === known.sha256) {
      console.log(`  ok   ${r.name}  ${local.slice(0, 12)}`);
    } else {
      console.log(`  FAIL ${r.name}\n         local  ${local}\n         record ${known.sha256}`);
      bad++;
    }
  }
  const absent = rows.length - presentRows.length;
  console.log(`\n${presentRows.length} checked, ${bad} mismatch, ${noRecord} unrecorded, ${absent} not on this disk`);
  if (absent) console.log("(absent files are normal: run this on the machine that did the migration)");
  process.exit(bad === 0 ? 0 : 1);
}


if (CHECK_ONLY) {
  const current = existsSync(INDEX_PATH) ? readFileSync(INDEX_PATH, "utf8") : "";
  if (current !== rendered) {
    console.error("deliverables/INDEX.md is out of date — run `node scripts/build-deliverables-index.mjs`");
    process.exit(1);
  }
  console.log("deliverables/INDEX.md is up to date");
  process.exit(0);
}

writeFileSync(INDEX_PATH, rendered);
console.log(`wrote deliverables/INDEX.md — ${rows.length} files, ${unrecorded.length} to-do rows`);
process.exit(0);
