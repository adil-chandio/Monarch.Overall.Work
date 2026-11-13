/**
 * Guard tests. Run with `node scripts/guard.test.mjs`.
 *
 * These test the RULE, not the data. If someone loosens config/media-policy.json
 * until the repo is allowed to grow again, these fail before the rule can be
 * forgotten. They deliberately do not assert "the repo is clean today" — the
 * 148 existing violations are a known, tracked backlog, not a test failure.
 */
import assert from "node:assert";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { resolve } from "node:path";

const ROOT = resolve(import.meta.dirname, "..");
const read = (p) => JSON.parse(readFileSync(resolve(ROOT, p), "utf8"));

let passed = 0;
const test = (name, fn) => {
  fn();
  passed++;
  console.log("  ok", name);
};

/* ---------- config/media-policy.json ---------- */

const policy = read("config/media-policy.json");

test("media policy declares every media family it claims to guard", () => {
  for (const kind of ["video", "audio", "model", "archive"]) {
    assert.ok(Array.isArray(policy.media_extensions[kind]), `missing family: ${kind}`);
    assert.ok(policy.media_extensions[kind].length > 0, `empty family: ${kind}`);
  }
});

test("the hard-fail gate matches GitHub's real 100 MB ceiling", () => {
  assert.equal(policy.size_gate.hard_fail_bytes, 100000000);
  assert.ok(policy.size_gate.warn_bytes < policy.size_gate.hard_fail_bytes);
});

test("every keep_in_git path explains itself", () => {
  const why = policy.keep_in_git.why_per_path;
  for (const p of policy.keep_in_git.paths) {
    assert.ok(why[p], `keep_in_git entry has no reason: ${p}`);
    assert.ok(why[p].length > 20, `reason too thin to be useful: ${p}`);
  }
});

test("the verified upload limit is not confused with the hard limit", () => {
  // 100 MB is the connector ceiling; verified_upload_max_bytes is the largest
  // size actually exercised. These used to be 50 MB vs 100 MB and the note had
  // to say "untested", because the gap was real and nobody had tried it. The
  // 2026-11-13 migration closed the gap: 99,408,313 B uploaded and its Drive
  // sha256 matched local. So the honest assertion is no longer "keep saying
  // untested" — it is "prove the claim, and never exceed the wall".
  const L = policy.upload_limits;
  assert.ok(L.verified_upload_max_bytes <= L.connector_max_bytes, "verified size cannot exceed the hard ceiling");
  assert.ok(
    !L.verified_note.includes("untested"),
    "the gap is closed — if a size is again unproven, lower verified_upload_max_bytes instead of re-wording the note",
  );
  // A claimed ceiling must be backed by the ladder that measured it, and the
  // top rung must be the claimed number. This is the part that makes the claim
  // auditable: a bare "we tried it" is not evidence.
  assert.ok(Array.isArray(L.size_ladder_measured) && L.size_ladder_measured.length > 0, "the measured size ladder is missing");
  const top = Math.max(...L.size_ladder_measured.map((r) => r.bytes));
  assert.equal(top, L.verified_upload_max_bytes, "the ladder's top rung must equal the claimed verified maximum");
  for (const rung of L.size_ladder_measured) {
    assert.ok(rung.bytes > 0 && typeof rung.what === "string" && rung.what.length > 3, `a ladder rung is not explained: ${JSON.stringify(rung)}`);
  }
});

test("encode targets fit inside the upload ceiling", () => {
  const L = policy.encode_targets.longform_1080p;
  const worstCaseBytes =
    ((L.video_bitrate_mbps + L.audio_bitrate_kbps / 1000) * 1_000_000 * L.duration_max_minutes * 60) / 8;
  const withOverhead = worstCaseBytes * (1 + L.container_overhead_pct / 100);
  assert.ok(
    withOverhead < policy.upload_limits.connector_max_bytes,
    `a ${L.duration_max_minutes}-min master at ${L.video_bitrate_mbps} Mbps + ${L.audio_bitrate_kbps} kbps audio + ${L.container_overhead_pct}% overhead would be ${(withOverhead / 1048576).toFixed(0)} MB — over the upload ceiling`
  );
  assert.ok(
    Math.abs(withOverhead / 1048576 - L.size_target_mb) < 5,
    `stated size_target_mb (${L.size_target_mb}) does not match the arithmetic (${(withOverhead / 1048576).toFixed(1)} MB)`
  );
});

test("the short encode target also fits", () => {
  const S = policy.encode_targets.shortform_1080x1920;
  const bytes =
    ((S.video_bitrate_mbps + S.audio_bitrate_kbps / 1000) * 1_000_000 * S.duration_max_seconds) / 8;
  const withOverhead = bytes * (1 + S.container_overhead_pct / 100);
  assert.ok(withOverhead < policy.upload_limits.connector_max_bytes);
  assert.ok(Math.abs(withOverhead / 1048576 - S.size_target_mb) < 3, "short target arithmetic is off");
});

test("storage tiers are ordered cheapest-and-most-permanent first", () => {
  const ranks = policy.tiers.map((t) => t.rank);
  assert.deepEqual([...ranks].sort((a, b) => a - b), ranks, "tiers must be listed by rank");
  assert.equal(policy.tiers[0].id, "youtube_unlisted");
});

test("the policy states what must never happen", () => {
  for (const phrase of ["force-push", "delete a file", "promise an upload size"]) {
    assert.ok(
      policy.never.some((n) => n.includes(phrase)),
      `policy.never is missing: ${phrase}`
    );
  }
});

/* ---------- config/drive-map.json ---------- */

const drive = read("config/drive-map.json");

test("every Drive folder entry carries provenance", () => {
  for (const f of drive.folders) {
    assert.ok(f.id && f.id.length > 20, `folder without a real id: ${f.name}`);
    assert.ok(f.status, `folder without status: ${f.name}`);
    assert.ok(
      ["mapped", "unmapped", "candidate_only"].includes(f.status),
      `unknown status '${f.status}' on ${f.name}`
    );
  }
});

test("the quota figure is recorded with a date and a source", () => {
  const q = drive.quota_measured;
  assert.ok(q.at && q.source, "a number without a date and a source is a rumour");
  assert.equal(q.total_gb - q.used_gb, q.free_gb, "free space must equal total minus used");
});

test("every gap between Drive and the channel config is named", () => {
  const channelIds = new Set(read("config/channels.json").channels.map((c) => c.id));
  assert.ok(drive.channel_gaps.length >= 4, "known gaps must stay listed");
  for (const gap of drive.channel_gaps) {
    assert.ok(gap.action && gap.action.length > 10, `gap without an action: ${gap.channel}`);
    if (gap.channel.startsWith("ch-")) {
      assert.ok(channelIds.has(gap.channel.split(" ")[0]), `gap refers to an unknown channel: ${gap.channel}`);
    }
  }
});

/* ---------- config/channels.json ---------- */

const channels = read("config/channels.json").channels;

test("every channel has an id, a slot, a name and a KPI", () => {
  const ids = new Set();
  for (const c of channels) {
    assert.ok(c.id && !ids.has(c.id), `duplicate or missing id: ${c.id}`);
    ids.add(c.id);
    assert.ok(c.slot, `${c.id} has no slot`);
    assert.ok(c.name, `${c.id} has no name`);
    assert.ok(c.kpi && c.kpi.primary && c.kpi.target !== undefined, `${c.id} has no KPI target`);
  }
});

test("no handle is invented — null is allowed, a guess is not", () => {
  for (const c of channels) {
    if (c.handle === null) {
      assert.ok(c.handle_status, `${c.id} has no handle and does not say so`);
    } else {
      assert.ok(c.handle.startsWith("@"), `${c.id} handle is not an @handle`);
    }
  }
});

test("every channel added after the original three says why", () => {
  for (const c of channels) {
    const n = Number(c.id.replace("ch-", ""));
    if (n > 3) {
      assert.ok(c.added_because && c.added_because.length > 20, `${c.id} was added silently`);
      assert.ok(c.evidence, `${c.id} has no evidence block`);
    }
  }
});

test("a channel with a Drive folder points at a folder listed in drive-map", () => {
  const driveIds = new Set(drive.folders.map((f) => f.id));
  for (const c of channels) {
    if (c.drive_folder_id) {
      assert.ok(driveIds.has(c.drive_folder_id), `${c.id} points at a Drive folder not in drive-map.json`);
    }
  }
});

test("every Drive folder that claims a channel exists in channels.json", () => {
  const channelIds = new Set(channels.map((c) => c.id));
  for (const f of drive.folders) {
    if (f.maps_to_channel && f.status === "mapped") {
      assert.ok(channelIds.has(f.maps_to_channel), `drive-map ${f.name} -> unknown channel ${f.maps_to_channel}`);
    }
  }
});

test("the operator-uploads-by-hand decision is recorded and guarded", () => {
  const a = read("config/accounts.json");
  assert.equal(a.publishing.who_publishes, "the operator, by hand");
  const gap = a.known_gaps.find((g) => g.id === "gap-upload-not-built");
  assert.equal(gap.status, "deferred-by-operator", "gap-upload-not-built is no longer marked deferred");
  const agents = readFileSync(resolve(ROOT, "AGENTS.md"), "utf8");
  assert.ok(agents.includes("uploads by hand"), "AGENTS.md lost the by-hand decision");
  assert.ok(/do \*\*not\*\* build an upload automation/i.test(agents), "AGENTS.md no longer forbids building one");
});

test("AGENTS.md keeps the two-account publishing model", () => {
  const agents = readFileSync(resolve(ROOT, "AGENTS.md"), "utf8");
  for (const phrase of [
    "m.adil.chandio",
    "adil.chandio.ai",
    "YouTube only",
    "the same file, four platforms",
    "1-2 per week",
  ]) {
    assert.ok(agents.includes(phrase), `AGENTS.md lost: ${phrase}`);
  }
});

/* ---------- config/accounts.json ---------- */

const accountsFile = read("config/accounts.json");
const accounts = accountsFile.accounts;

test("there are exactly two publishing accounts", () => {
  assert.equal(accounts.length, 2, `expected 2 accounts, found ${accounts.length}`);
  assert.deepEqual(accounts.map((a) => a.id), ["acc-01", "acc-02"]);
});

test("both accounts publish shorts to all four platforms", () => {
  const want = ["TikTok", "Instagram", "YouTube Shorts", "Facebook"];
  for (const a of accounts) {
    assert.deepEqual(
      [...a.platforms.shorts].sort(),
      [...want].sort(),
      `${a.id} does not publish shorts to exactly ${want.join(", ")}`
    );
  }
});

test("long-form is YouTube only, on both accounts", () => {
  for (const a of accounts) {
    assert.deepEqual(a.platforms.long, ["YouTube"], `${a.id} long-form escapes YouTube`);
    assert.ok(a.cadence.long, `${a.id} has no long-form cadence`);
  }
});

test("long-form is capped at 1-2 per week, in the file and in the model block", () => {
  for (const a of accounts) {
    assert.ok(/1-2\s*\/\s*week/.test(a.cadence.long), `${a.id} does not cap long-form at 1-2/week`);
  }
  assert.ok(/1-2 per week/.test(accountsFile.the_model.long_form.cadence), "the_model lost its cadence cap");
});

test("every handle is recorded with its raw form and an honesty flag", () => {
  for (const a of accounts) {
    assert.ok(a.handle, `${a.id} has no handle`);
    assert.equal(typeof a.handle_unverified, "boolean", `${a.id} does not say whether the handle is verified`);
    assert.ok(a.handle_note && a.handle_note.length > 20, `${a.id} does not explain its handle`);
    assert.ok(!/[\s"]/.test(a.handle), `${a.id} handle contains whitespace or a quote: ${JSON.stringify(a.handle)}`);
  }
});

test("both handles match what the operator gave on 2026-11-13", () => {
  const byId = Object.fromEntries(accounts.map((a) => [a.id, a]));
  assert.equal(byId["acc-01"].handle, "m.adil.chandio");
  assert.equal(byId["acc-02"].handle, "adil.chandio.ai");
});

test("the four upload gaps are named, not hidden", () => {
  const ids = new Set(accountsFile.known_gaps.map((g) => g.id));
  for (const want of ["gap-handles", "gap-supersedes-social-json", "gap-upload-not-built"]) {
    assert.ok(ids.has(want), `known_gaps lost ${want}`);
  }
  for (const g of accountsFile.known_gaps) {
    assert.ok(g.fix && g.fix.length > 20, `${g.id} has no fix`);
  }
});

/* ---------- .gitignore ---------- */

const ignore = readFileSync(resolve(ROOT, ".gitignore"), "utf8");

test("the media guard block is present and explains itself", () => {
  assert.ok(ignore.includes("MEDIA GUARD"), "the guard section was removed");
  assert.ok(ignore.includes("config/media-policy.json"), "the guard no longer names its source of truth");
});

test("the one-directory-deep bug cannot come back", () => {
  // The old rule was `deliverables/*.mp4`, which missed deliverables/sub/a.mp4.
  assert.ok(
    !/^deliverables\/\*\.mp4$/m.test(ignore),
    "the narrow deliverables/*.mp4 rule is back — it only matches one directory deep"
  );
  for (const ext of ["mp4", "mov", "wav", "glb", "zip"]) {
    assert.ok(ignore.includes(`*.${ext}`), `no repo-wide ignore for .${ext}`);
  }
});

test("the load-bearing public assets are still exempt", () => {
  for (const dir of ["public/thumbnails", "public/proof", "public/showreel"]) {
    assert.ok(ignore.includes(`!${dir}/**`), `${dir} lost its exemption — the site would break`);
  }
});

/* ---------- .gitattributes ---------- */

const attrs = readFileSync(resolve(ROOT, ".gitattributes"), "utf8");

test("media is declared binary so Git never diffs it", () => {
  for (const ext of ["mp4", "wav", "glb", "jpeg"]) {
    assert.ok(
      new RegExp(`\\*\\.${ext}\\s+binary`).test(attrs),
      `.${ext} is not declared binary`
    );
  }
});

test("text normalises to LF", () => {
  assert.ok(attrs.includes("text=auto eol=lf"), "line endings are unmanaged again");
});

/* ---------- regenerable evidence + the real growth mechanism ---------- */

test("every regenerable-evidence folder ships its generator and a pinned source", () => {
  const re = policy.regenerable_evidence;
  assert.ok(re, "regenerable_evidence block missing");
  for (const f of re.folders) {
    assert.ok(f.generator, `${f.path} claims regenerable but names no generator`);
    assert.ok(f.source_sha256, `${f.path} has no pinned source hash — regenerating would be a guess`);
    assert.match(f.source_sha256, /^[0-9a-f]{64}$/, `${f.path} source hash is not a sha256`);
    assert.ok(
      f.keep_in_git_anyway?.length,
      `${f.path} must keep its text evidence even when the images leave`
    );
    assert.ok(
      f.keep_in_git_anyway.some((n) => n.endsWith(".csv")),
      `${f.path} drops every CSV — the numbers are the point`
    );
  }
});

test("the workflow growth mechanism is measured, not assumed", () => {
  const w = policy.workflow_handoff;
  assert.ok(w, "workflow_handoff block missing");
  assert.ok(w.count_now > 0, "if this reaches zero, delete the block — do not leave a stale claim");
  assert.ok(w.measured_by, "the count must name the script that produces it");
  assert.ok(
    w.count_now < w.of_total_committing,
    "a majority of workflows committing media would mean the design, not a few pipelines, is wrong"
  );
});

/* ---------- the gitignore traps that were actually found ---------- */

const { execFileSync } = await import("node:child_process");
const ignored = (p) => {
  try {
    execFileSync("git", ["check-ignore", "-q", "--no-index", p], { cwd: ROOT });
    return true;
  } catch {
    return false;
  }
};

test("keep_in_git files are never caught by an ignore rule", () => {
  for (const p of policy.keep_in_git.paths) {
    // directory-shaped globs cannot be tested literally; test a file inside them
    const probe = p.endsWith("/") ? p + "__probe__.jpg" : p.replace("**/", "");
    assert.ok(!ignored(probe), `keep_in_git path is being ignored: ${probe}`);
  }
});

test("skills/*/references is not swallowed by the root references/ rule", () => {
  // Measured 2026-11-13: a bare `references/` ignored 1,149 skill files.
  assert.ok(
    !ignored("skills/ffmpeg-skill/references/scripts.md"),
    "the root references/ rule is eating skills/*/references/ again"
  );
  assert.ok(ignored("references/some-video.mp4"), "the root references/ folder is no longer guarded");
});

test("render evidence is ignored but its text evidence is not", () => {
  assert.ok(ignored("production/extinct-life/review-v14/full-resolution/000.jpg"), "extracted frames are not ignored");
  assert.ok(!ignored("production/extinct-life/review-v14/EVIDENCE.json"), "EVIDENCE.json must stay tracked");
  assert.ok(!ignored("production/extinct-life/review-v14/every-frame-metrics.csv"), "the numbers must stay tracked");
});

test("the approved public proof master is exempt", () => {
  assert.ok(
    !ignored("deliverables/MON-DEMO26_Proof_Over_Promises_v3_1080p60_Master.mp4"),
    "the one approved master is being ignored despite being on keep_in_git"
  );
});

test("a file released from Git must have a Drive copy with a matching hash", () => {
  const idx = readFileSync(resolve(ROOT, "deliverables/INDEX.md"), "utf8");
  const driveNames = new Map();
  for (const folder of drive.folders ?? []) {
    for (const f of folder.currently_holds ?? []) {
      if (f.name) driveNames.set(f.name, f.sha256 ?? null);
    }
  }
  // every file the index marks as NOT in Git and NOT recorded is a to-do, which
  // is allowed — but anything marked as having a Drive copy must match its hash
  let checked = 0;
  for (const line of idx.split("\n")) {
    const m = line.match(/^\| `([^`]+)` \| [^|]+ \| [^|]+ \| no \| Drive [^|·]+·[^|]+\| `([0-9a-f]{12})` \|$/);
    if (!m) continue;
    const [, name, shortHash] = m;
    const known = driveNames.get(name);
    assert.ok(known, `${name} is listed with a Drive copy but is not in config/drive-map.json`);
    assert.ok(known.startsWith(shortHash), `${name} hash in the index does not match drive-map.json`);
    checked++;
  }
  assert.ok(checked >= 1, "no fully-migrated file was verified — the migration loop is untested");
});

test("drive-map records the migration precedent with both hashes", () => {
  const p = policy.migration_precedent;
  assert.ok(p, "migration_precedent missing — the loop has never been proven end to end");
  assert.equal(p.sha256_local, p.sha256_drive, "local and Drive hashes disagree");
  assert.match(p.sha256_local, /^[0-9a-f]{64}$/);
  assert.ok(p.drive_id && p.drive_id.length > 20, "precedent has no real Drive id");
  assert.ok(p.result.includes("remains on disk"), "the precedent must state the file stayed on disk");
});

/* ---------- .gitignore: the two traps found on 2026-11-13 ---------------- */

const ignoreFile = readFileSync(resolve(ROOT, ".gitignore"), "utf8");
const ignoreLines = ignoreFile.split("\n").map((l) => l.trim()).filter((l) => l && !l.startsWith("#"));

test("no .gitignore rule excludes a whole folder that workflows `git add`", () => {
  // A directory-excluding rule makes `git add <that dir>` exit 1, and GitHub
  // Actions runs every step with `bash -e` — so the step fails and the job
  // fails. That is not theory: run 43340437009 died on
  //   git add production/extinct-life/film-v8-premium/inspection
  // because .gitignore excluded that directory outright. `git add` on a folder
  // whose CHILDREN are ignored is fine and exits 0, so the rule to enforce is:
  // exclude media inside folders, never the folder itself, when a workflow
  // stages that folder.
  const staged = [];
  const wfDir = resolve(ROOT, ".github/workflows");
  for (const file of readdirSync(wfDir)) {
    if (!file.endsWith(".yml") && !file.endsWith(".yaml")) continue;
    const text = readFileSync(resolve(wfDir, file), "utf8");
    for (const line of text.split("\n")) {
      const m = line.match(/git add ([^|;&]+)/);
      if (!m) continue;
      // `|| true` (or a trailing `; true`) is the documented escape hatch: the
      // step keeps running even when the path resolves to ignored content.
      const guarded = /\|\|\s*true/.test(line) || /;\s*true\s*$/.test(line.trim());
      if (guarded) continue;
      for (const raw of m[1].trim().split(/\s+/)) {
        const token = raw.replace(/^["']|["']$/g, "");
        if (!token || token.startsWith("-") || token.includes("$")) continue;
        staged.push({ token, file });
      }
    }
  }
  assert.ok(staged.length > 0, "parsed no `git add` targets — this test would silently pass forever");
  for (const { token, file } of staged) {
    const rule = ignoreRuleFor(token);
    assert.ok(
      !rule || !rule.isDir,
      `${file} runs \`git add ${token}\`, but .gitignore "${rule?.pattern}" excludes that directory — the step exits 1 under bash -e`,
    );
  }
});

test("every load-bearing public asset has a matching .gitignore negation", () => {
  // Tracked-but-ignored is a trap. It works today and breaks the day someone
  // releases the file: `git rm --cached` turns the ignore rule back on, and the
  // next `git add <path>` in a workflow exits 1. src/ references are the
  // definition of load-bearing, so anything src/ points at must be explicitly
  // re-included rather than merely surviving as an old index entry.
  const srcDir = resolve(ROOT, "src");
  const referenced = new Set();
  for (const file of readdirSync(srcDir, { recursive: true })) {
    const p = resolve(srcDir, file.toString());
    if (!/\.(jsx?|tsx?|html|css)$/.test(p)) continue;
    for (const m of readFileSync(p, "utf8").matchAll(/["'`](\/[A-Za-z0-9._/-]+\.(?:mp4|webm|m4a|mp3|jpg|jpeg|png|webp))(?:\?[^"'`]*)?["'`]/g)) {
      referenced.add(m[1]);
    }
  }
  assert.ok(referenced.size > 0, "found no media references in src/ — the parser is stale");
  for (const ref of referenced) {
    const rel = `public${ref}`;
    const rule = ignoreRuleFor(rel);
    if (!rule) continue; // not ignored at all — nothing can break
    assert.ok(
      rule.isNegation,
      `${rel} is used by src/ but .gitignore ignores it via "${rule.pattern}" with no "!" exception — releasing it would break the next git add`,
    );
  }
});

/* ---------- a real .gitignore matcher --------------------------------------
 * The first draft of the two tests above compared strings for equality. It
 * passed against the BROKEN .gitignore, because the offending rule was a glob
 * over film-<name>-inspection and the compared token was one concrete folder
 * name. Different strings, same real match. A test
 * that cannot fail is worse than no test, so this matcher follows git's actual
 * rules and is itself checked against git check-ignore below.
 * ------------------------------------------------------------------------*/
function gitignoreRegex(pattern) {
  let pat = pattern.replace(/^!/, "").replace(/\/+$/, "");
  const anchored = pat.includes("/");
  if (!anchored) pat = `**/${pat}`;
  const body = pat
    .replace(/[.+^${}()|[\]\\]/g, "\\$&")
    .replace(/\*\*\//g, "\u0001")
    .replace(/\*\*/g, "\u0002")
    .replace(/\*/g, "[^/]*")
    .replace(/\?/g, "[^/]")
    .replace(/\u0001/g, "(?:.*/)?")
    .replace(/\u0002/g, ".*");
  return new RegExp(`^${body}$`);
}

/** The last matching rule for a path, i.e. what git would actually apply. */
function ignoreRuleFor(relPath) {
  let winner = null;
  for (const pattern of ignoreLines) {
    const isNegation = pattern.startsWith("!");
    const isDir = /\/$/.test(pattern);
    const bare = pattern.replace(/^!/, "");
    if (gitignoreRegex(bare).test(relPath)) winner = { pattern, isNegation, isDir };
    // a directory rule also covers anything beneath it
    if (isDir && gitignoreRegex(bare.replace(/\/+$/, "")).test(relPath)) winner = { pattern, isNegation, isDir };
    if (isDir && relPath.startsWith(bare)) winner = { pattern, isNegation, isDir };
  }
  return winner;
}

test("the deliverables page is built from records, not from the local disk", () => {
  // The bug this encodes: rows were built from `find deliverables/`, so the
  // machine doing the migration (26 videos present) and CI (none present)
  // generated different pages, `--check` failed in CI forever, and repo-guard
  // went red on every commit. A ledger may not depend on which bytes happen to
  // be lying around. Assert on the generator's SOURCE, because running it twice
  // here cannot catch a disk dependency — this machine has the files.
  const gen = readFileSync(resolve(ROOT, "scripts/build-deliverables-index.mjs"), "utf8");
  assert.ok(
    /KNOWN_DRIVE\.values\(\)/.test(gen),
    "generator must union records from config/drive-map.json, or released files vanish from the page",
  );
  assert.ok(
    /--verify-local/.test(gen),
    "the 'are the bytes still here' question needs its own command; folding it into the page is what broke CI",
  );
  // The rendered row must not contain any local-reading result. A page cell
  // that changes with the machine has no business in a committed file.
  const idx = readFileSync(resolve(ROOT, "deliverables/INDEX.md"), "utf8");
  assert.ok(!/not in this checkout/.test(idx), "the page still reports local presence");
  assert.ok(!/†/.test(idx), "the page still shows per-machine hash state");
});

test("no evidence folder was emptied of its text", () => {
  // Releasing frames from Git is only safe while the NUMBERS survive. On
  // 2026-11-13, 537 JPGs (142 MB) came out of nine production/extinct-life
  // folders. Every one of those folders keeps its measurement text — EVIDENCE.json,
  // *.csv, *.md — because that is the evidence; the frames are a picture of it.
  // The failure mode this catches: someone later runs `git rm -r --cached` on a
  // whole folder instead of the media inside it, and the repo is left with a
  // JPG's worth of nothing. It also catches a generator that stopped writing
  // its text: an evidence folder with media and no text is a red flag either way.
  const root = resolve(ROOT, "production/extinct-life");
  let checked = 0;
  for (const dir of readdirSync(root, { withFileTypes: true })) {
    if (!dir.isDirectory()) continue;
    const base = resolve(root, dir.name);
    if (!existsSync(base)) continue;
    for (const sub of ["inspection", "full-resolution", "seconds", "encoded-inspection"]) {
      const p = resolve(base, sub);
      if (!existsSync(p)) continue;
      checked++;
      const text = readdirSync(base).filter((f) => /\.(json|csv|md|txt)$/.test(f));
      assert.ok(
        text.length > 0,
        `${dir.name}/${sub} exists but ${dir.name}/ has no measurement text — the evidence would be lost, not moved`,
      );
    }
  }
  /* Two very different states are both fine, and confusing them is what made
   * this test red in CI while green locally — the same disk-vs-record mistake
   * as the index page:
   *   - this checkout HAS the folders (migration machine): check every one
   *   - it does not (fresh clone, CI): the folders are gone from disk because
   *     the JPGs were released, and there is nothing to check. Asserting a
   *     minimum count here would demand bytes that are not supposed to be in
   *     the repo any more.
   * What must hold in BOTH cases is that the measurement text is still tracked. */
  const trackedText = execFileSync("git", ["ls-files", "production/extinct-life"], {
    cwd: ROOT,
    encoding: "utf8",
  })
    .split("\n")
    .filter((f) => /\.(json|csv|md|txt)$/.test(f) && /extinct-life\/[^/]+\//.test(f));
  assert.ok(
    trackedText.length > 200,
    `only ${trackedText.length} measurement files are still tracked under production/extinct-life — text evidence was released along with the frames`,
  );
});

test("no guard test requires bytes that a fresh clone does not have", () => {
  // Twice today a check was green here and red in CI, both times because it
  // measured the disk: the deliverables page (26 rows here, 1 in CI) and the
  // evidence-folder count (9 here, 0 in CI). Released media is SUPPOSED to be
  // absent from a clone, so any assertion on its presence is a bug waiting for
  // a clean machine.
  //
  // This does not try to run the suite in a sandbox. It asserts the property
  // that matters in the source: no test may demand a file that only exists
  // because someone kept it locally. The concrete shapes are a minimum count of
  // on-disk folders, or existsSync used as a hard assert on released media.
  const src = readFileSync(resolve(ROOT, "scripts/guard.test.mjs"), "utf8");
  // Narrow on purpose. The first version flagged any `checked >= N` and hit a
  // count of ROWS PARSED FROM deliverables/INDEX.md, which is records, not
  // disk — a false positive. The shape that actually breaks is a count
  // accumulated while walking the filesystem, then asserted to be at least N.
  const lines = src.split("\n");
  const offenders = [];
  let countsDisk = false;
  for (const [i, line] of lines.entries()) {
    if (/readdirSync|existsSync|find\b|statSync/.test(line) && !/^\s*\*|^\s*\/\//.test(line)) countsDisk = true;
    if (/assert\.(ok|equal)\(\s*checked\s*>=/.test(line)) {
      // look back for the loop that produced `checked`
      const window = lines.slice(Math.max(0, i - 40), i).join("\n");
      if (/for \(.*of (rows|idx|lines|media|deliverableFiles|driveNames)/.test(window)) continue;
      if (countsDisk) offenders.push(`${i + 1}: ${line.trim()}`);
    }
  }
  assert.deepEqual(offenders, [], `a guard test demands a minimum number of on-disk folders — it will fail on a fresh clone: ${offenders.join(" | ")}`);
});

test("the source assets that renders need are still tracked", () => {
  // 312 MB of media is still in Git after the migration, and that is the correct
  // end state, not leftover work. These files are INPUTS: 3D meshes, a Blender
  // rig, narration recordings, music stems, scene plates. Declared in
  // config/media-policy.json -> source_assets so the next session does not read
  // 312 MB and start "finishing" the migration by breaking the pipeline.
  //
  // The specific files are named because they are the ones a render reads by
  // name. If one leaves Git, the render that needs it fails on a fresh clone.
  const needed = [
    "production/extinct-life/longform-mammoth/cinematic-rebuild/mammoth-rig/assets/SDPM-Mammoth-Experimental-Rig.glb",
    "production/extinct-life/longform-mammoth/cinematic-rebuild/mammoth-rig/assets/SDPM-Wooly-Mammoth.blend",
    "production/extinct-life/longform-mammoth/cinematic-rebuild/soundtrack-draft/Narration-Score-DRAFT.m4a",
    "production/extinct-life/longform-mammoth/cinematic-rebuild/full-script-v2/Narration-Draft-v2.m4a",
    "production/extinct-life/longform-mammoth/full-film/assets/tundra.png",
    "public/demo-preview.mp4",
  ];
  const tracked = new Set(
    execFileSync("git", ["ls-files"], { cwd: ROOT, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 })
      .split("\n")
      .filter(Boolean),
  );
  for (const f of needed) {
    assert.ok(tracked.has(f), `${f} left Git — it is an input, not a deliverable. Releasing it breaks a render on a fresh clone.`);
  }
  assert.ok(policy.source_assets, "config/media-policy.json must keep the source_assets section explaining why 312 MB stays");
  assert.ok(
    policy.source_assets.the_test_before_releasing_any_of_it.length > 80,
    "the source_assets section must keep the test that separates input from output",
  );
});

/* ---------- the durability rule (2026-11-13: a finished video was lost) ---- */

test("the job ledger exists and refuses an unsafe pause", () => {
  // The incident: 480/480 frames rendered, a 12.6 MB MP4 encoded, nothing
  // uploaded, sandbox reset, everything gone. The repo had nowhere to record
  // "done but not delivered" and no rule against going idle there.
  const gen = readFileSync(resolve(ROOT, "scripts/job.mjs"), "utf8");
  assert.ok(/function blockers\(/.test(gen), "job.mjs lost its notion of what makes a pause unsafe");
  assert.ok(/drive_id/.test(gen), "an artifact without a Drive id must be a blocker");
  assert.ok(/sha256/.test(gen), "an artifact without a hash must be a blocker");
  assert.ok(/REFUSING to pause/.test(gen), "pause must refuse, not warn");
  assert.ok(/next_command/.test(gen), "a job with no resume command is not resumable");
  assert.ok(
    /git.*commit.*jobs|\["commit"/.test(gen),
    "the ledger must commit itself — an entry that only exists on disk is the thing this file exists to prevent",
  );
  assert.ok(
    /\["push"/.test(gen),
    "the ledger must PUSH itself — a commit in the sandbox is still in the sandbox, so a ledger that only commits protects nothing",
  );
});

test("AGENTS.md tells a new session that a sandbox is temporary", () => {
  // The rule only works if it is in the file every new chat reads first.
  const agents = readFileSync(resolve(ROOT, "AGENTS.md"), "utf8");
  assert.ok(/Long jobs/.test(agents), "AGENTS.md lost the long-jobs section — a new session would repeat the incident");
  for (const must of ["reset", "drive_id", "before you pause", "next_command"]) {
    assert.ok(
      agents.toLowerCase().includes(must.toLowerCase()),
      `AGENTS.md no longer mentions "${must}" in the durability rule`,
    );
  }
  assert.ok(
    /Do not wait at 75%/.test(agents) || /75%/.test(agents),
    "the 'ask approvals early, not at 75%' lesson must stay — deferring a question strands the render",
  );
  // The rule only holds if the "never block an upload on a question" half is
  // there too. Uploading is a safety step, not a decision, and the incident was
  // precisely a finished file waiting on nothing in particular.
  assert.ok(
    /upload first, ask second/i.test(agents),
    "AGENTS.md must say to upload before asking, not after",
  );
  assert.ok(
    /Batch, do not stream/i.test(agents),
    "the batching rule must stay — streaming questions across a long render strands it",
  );
});

console.log(`\n${passed} guard tests passed`);
