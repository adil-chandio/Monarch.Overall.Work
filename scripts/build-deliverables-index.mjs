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

const deliverableFiles = [
  ...new Set([...onDisk, ...tracked, ...[...KNOWN_DRIVE.values()].map((v) => v.rel)]),
]
  .filter((p) => p.startsWith("deliverables/"))
  .filter((p) => {
    const ext = p.slice(p.lastIndexOf(".")).toLowerCase();
    // A recorded Drive copy counts as media even when the extension list moves.
    return EXT_KIND.has(ext) || KNOWN_DRIVE.has(basename(p));
  })
  .sort();

const rows = [];
for (const rel of deliverableFiles) {
  const abs = resolve(ROOT, rel);
  const name = basename(rel);
  let bytes = 0;
  let hash = null;
  const present = existsSync(abs);
  if (present) {
    bytes = statSync(abs).size;
    hash = await sha256(abs);
  } else {
    const t = media.find((m) => m.path === rel);
    // Not on disk and not in the index of this checkout: the size we recorded
    // when it left Git is the only honest number left.
    bytes = t?.bytes ?? KNOWN_DRIVE.get(name)?.bytes ?? 0;
  }
  const isTracked = tracked.has(rel);
  const drive = KNOWN_DRIVE.get(name);
  rows.push({
    rel,
    name,
    bytes,
    hash,
    kind:
      EXT_KIND.get(rel.slice(rel.lastIndexOf(".")).toLowerCase()) ??
      EXT_KIND.get(`.${name.split(".").pop().toLowerCase()}`) ??
      "media",
    // "external" = provably elsewhere. That is a different thing from "missing",
    // which means nobody knows where it went and must be loud.
    status: isTracked
      ? "tracked"
      : drive
        ? "external"
        : present
          ? "on-disk-only"
          : "missing",
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
  // No local hash means the bytes are not in this checkout. That is normal for a
  // released file and is NOT the same as "missing": the hash below is the one
  // recorded at release time, and the Where column says where to find it.
  const shortHash = r.hash
    ? r.hash.slice(0, 12)
    : KNOWN_DRIVE.get(r.name)?.sha256
      ? `${KNOWN_DRIVE.get(r.name).sha256.slice(0, 12)} †`
      : r.status === "missing"
        ? "—"
        : "n/a";
  const whereCell =
    r.where === "UNRECORDED"
      ? "**UNRECORDED**"
      : r.present
        ? r.where
        : `${r.where} (not in this checkout)`;
    const matchMark = (() => {
    const known = KNOWN_DRIVE.get(r.name);
    if (!known?.sha256 || !r.hash) return "";
    return known.sha256 === r.hash ? " ✓" : " ✗ HASH MISMATCH";
  })();
  lines.push(`| \`${r.name}\` | ${human(r.bytes)} | ${r.kind} | ${r.isTracked ? "yes" : "no"} | ${whereCell}${matchMark} | \`${shortHash}\` |`);
}

lines.push("");
lines.push("`†` = the file is not in this checkout, so its hash is the one recorded when it left Git rather than a fresh reading.");
lines.push("That is the normal state of a released file: `git clone` does not fetch Drive. `✓` still means the recorded Drive hash");
lines.push("equalled the local hash at release time.");
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
