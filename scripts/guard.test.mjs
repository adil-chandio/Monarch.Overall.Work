/**
 * Guard tests. Run with `node scripts/guard.test.mjs`.
 *
 * These test the RULE, not the data. If someone loosens config/media-policy.json
 * until the repo is allowed to grow again, these fail before the rule can be
 * forgotten. They deliberately do not assert "the repo is clean today" — the
 * 148 existing violations are a known, tracked backlog, not a test failure.
 */
import assert from "node:assert";
import { readFileSync } from "node:fs";
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
  // 50 MB is what has actually been exercised end to end; 100 MB is the tool ceiling.
  assert.ok(policy.upload_limits.verified_upload_max_bytes <= policy.upload_limits.connector_max_bytes);
  assert.ok(policy.upload_limits.verified_note.includes("untested"), "the gap between ceilings must stay stated");
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

console.log(`\n${passed} guard tests passed`);
