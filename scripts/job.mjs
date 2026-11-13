#!/usr/bin/env node
/**
 * job.mjs — the ledger for long work that must survive a sandbox reset.
 *
 * WHY THIS EXISTS
 * ---------------
 * On 2026-11-13 a 20-second 3D render was finished: 480 frames, all 14 QC
 * checks passing, a 12.6 MB MP4 encoded. The agent reported it ready and did
 * not upload it. The operator was away. The sandbox reset. Frames, MP4 and two
 * hours of compute were gone, and the render had to start over.
 *
 * Nothing about that was a .gitignore problem. The repo simply had no concept
 * of a job: nowhere to write "I am at 480/480, the MP4 exists, it is NOT yet on
 * Drive", and no rule saying that a session may not go idle in that state.
 *
 * The rule this file enforces:
 *
 *     A sandbox is temporary. If you pause, everything you would need to
 *     continue must already exist somewhere a reset cannot reach — GitHub for
 *     text, Drive for media. Pausing with an upload pending is a bug.
 *
 * USAGE
 * -----
 *   node scripts/job.mjs start <id> --goal "..." --total 480 --unit frames
 *   node scripts/job.mjs progress <id> --done 320 [--note "S4 done"]
 *   node scripts/job.mjs artifact <id> <path>        # registers a real, finished file
 *   node scripts/job.mjs uploaded <id> <path> --drive-id <id> --sha256 <hash>
 *   node scripts/job.mjs decide <id> --q "..." --a "..."
 *   node scripts/job.mjs pause <id> --q "approve S5 lighting?"   # refuses if unsafe
 *   node scripts/job.mjs resume <id>                              # prints where to continue
 *   node scripts/job.mjs check <id>                               # what is blocking a pause
 *   node scripts/job.mjs done <id>
 *   node scripts/job.mjs list
 *
 * Every command writes jobs/<id>.json (machine) and jobs/<id>.md (human) and
 * commits them. `pause` is the important one: it fails loudly if the job is not
 * actually resumable.
 */
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync, statSync } from "node:fs";
import { resolve, relative, basename } from "node:path";

const ROOT = resolve(import.meta.dirname, "..");
const JOBS = resolve(ROOT, "jobs");
const argv = process.argv.slice(2);
const cmd = argv[0];

const flag = (name, fallback = null) => {
  const i = argv.indexOf(`--${name}`);
  return i !== -1 && argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[i + 1] : fallback;
};
const has = (name) => argv.includes(`--${name}`);

function die(msg) {
  console.error(`job: ${msg}`);
  process.exit(1);
}

const ID = argv[1] && !argv[1].startsWith("--") ? argv[1] : null;

function path(id) {
  return resolve(JOBS, `${id}.json`);
}

function load(id) {
  const p = path(id);
  if (!existsSync(p)) die(`no job "${id}" — create it with: node scripts/job.mjs start ${id}`);
  return JSON.parse(readFileSync(p, "utf8"));
}

function sha256(file) {
  const h = createHash("sha256");
  h.update(readFileSync(file));
  return h.digest("hex");
}

function human(bytes) {
  if (bytes >= 1048576) return `${(bytes / 1048576).toFixed(1)} MB`;
  if (bytes >= 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${bytes} B`;
}

/* ---------- what makes a job unsafe to pause ------------------------------- */

/**
 * Blockers are the things that would be lost by a reset. Deliberately short:
 * a warning nobody reads is worse than no warning.
 */
function blockers(job) {
  const out = [];
  for (const a of job.artifacts) {
    if (a.bytes > 0 && !a.drive_id) {
      out.push(`${relative(ROOT, a.path) || a.path} (${human(a.bytes)}) is not on Drive yet — \`node scripts/job.mjs uploaded\` needs a drive_id`);
    }
    if (a.bytes > 0 && !a.sha256) {
      out.push(`${relative(ROOT, a.path) || a.path} has no recorded sha256 — an upload without a hash is not proof of content`);
    }
  }
  if (!job.resume.next_command) {
    out.push("resume.next_command is empty — a new session would not know the next command to run");
  }
  return out;
}

function render(job) {
  const pct = job.total > 0 ? Math.round((job.done / job.total) * 100) : 0;
  const L = [];
  L.push(`# ${job.id}`);
  L.push("");
  L.push(`**${job.status}** · ${job.done}/${job.total} ${job.unit} (${pct}%) · updated ${job.updated}`);
  L.push("");
  if (job.goal) L.push(`> ${job.goal}`);
  L.push("");
  L.push("## Resume here");
  L.push("");
  L.push("```bash");
  L.push(job.resume.next_command || "(not set)");
  L.push("```");
  if (job.resume.notes) {
    L.push("");
    L.push(job.resume.notes);
  }
  L.push("");
  L.push("## Artifacts");
  L.push("");
  if (job.artifacts.length === 0) {
    L.push("_none yet_");
  } else {
    L.push("| file | bytes | sha256 | Drive |");
    L.push("|---|---:|---|---|");
    for (const a of job.artifacts) {
      L.push(`| \`${relative(ROOT, a.path) || a.path}\` | ${human(a.bytes)} | \`${a.sha256 ? a.sha256.slice(0, 12) : "—"}\` | ${a.drive_id ? `\`${a.drive_id}\`` : "**NOT UPLOADED**"} |`);
    }
  }
  L.push("");
  if (job.decisions.length) {
    L.push("## Decisions (already answered — do not ask again)");
    L.push("");
    for (const d of job.decisions) L.push(`- **${d.at.slice(0, 10)}** ${d.q} → ${d.a}`);
    L.push("");
  }
  if (job.log.length) {
    L.push("## Log");
    L.push("");
    for (const e of job.log.slice(-40)) L.push(`- \`${e.at.slice(11, 16)}\` ${e.what}`);
    L.push("");
  }
  return L.join("\n");
}

/** Returns true only when the ledger is on disk AND committed AND pushed.
 *  Anything less is not durable, and callers that matter (`pause`) must treat
 *  a false return as a blocker rather than a warning. */
function pathIsTracked(id) {
  try {
    execFileSync("git", ["ls-files", "--error-unmatch", `jobs/${id}.json`], { cwd: ROOT, stdio: "pipe" });
    return true;
  } catch {
    return false;
  }
}

function save(job, note) {
  let pushed = false;
  mkdirSync(JOBS, { recursive: true });
  job.updated = new Date().toISOString();
  if (note) job.log.push({ at: job.updated, what: note });
  writeFileSync(path(job.id), JSON.stringify(job, null, 2) + "\n");
  writeFileSync(resolve(JOBS, `${job.id}.md`), render(job));
  // Commit immediately. A ledger entry that only exists on disk is exactly the
  // thing this file was written to prevent.
  try {
    execFileSync("git", ["add", "-A", "jobs"], { cwd: ROOT, stdio: "pipe" });
    const dirty = (() => {
      try {
        execFileSync("git", ["diff", "--cached", "--quiet"], { cwd: ROOT, stdio: "pipe" });
        return false;
      } catch {
        return true;
      }
    })();
    if (dirty) {
      execFileSync("git", ["commit", "-q", "-m", `job(${job.id}): ${job.status} ${job.done}/${job.total} — checkpoint`], { cwd: ROOT, stdio: "pipe" });
      console.log(`job: committed jobs/${job.id}.*`);
    }
    if (!pathIsTracked(job.id)) {
      console.error(
        "job: WARNING jobs/ is not tracked by git — the ledger is only in the sandbox.\n" +
          "     Check .gitignore and `git status jobs/`.",
      );
      return false;
    }
    // A commit in the sandbox is still in the sandbox. Push, or the ledger has
    // exactly the durability of the thing it was written to protect.
    const branch = execFileSync("git", ["rev-parse", "--abbrev-ref", "HEAD"], { cwd: ROOT, encoding: "utf8" }).trim();
    try {
      execFileSync("git", ["push", "-q", "origin", `HEAD:${branch}`], { cwd: ROOT, stdio: "pipe" });
      console.log(`job: pushed to origin/${branch}`);
      pushed = true;
    } catch {
      console.error(
        `job: WARNING committed locally but NOT pushed (branch ${branch}).\n` +
          "     Run `bash scripts/git-push-retrying.sh " + branch + "` before you pause.\n" +
          "     A ledger that only exists in the sandbox protects nothing.",
      );
    }
  } catch (e) {
    console.error("job: WARNING could not commit the ledger — check `git status` before you stop");
    return false;
  }
  return pushed;
}

/* ---------- commands ------------------------------------------------------ */

if (cmd === "start") {
  if (!ID) die("start needs an id");
  if (existsSync(path(ID))) die(`job "${ID}" already exists — use \`progress\` or \`resume\``);
  const now = new Date().toISOString();
  const job = {
    id: ID,
    status: "running",
    goal: flag("goal", ""),
    total: Number(flag("total", 0)),
    done: Number(flag("done", 0)),
    unit: flag("unit", "steps"),
    created: now,
    updated: now,
    resume: { next_command: flag("next", ""), notes: "" },
    artifacts: [],
    decisions: [],
    log: [],
  };
  save(job, `started: ${job.goal}`);
  console.log(`job: started ${ID} (0/${job.total} ${job.unit})`);
  if (!job.resume.next_command) {
    console.log("job: set the resume command now — `node scripts/job.mjs resume-set " + ID + " --next \"...\"`");
    console.log("     that single field is what a new session reads first after a reset.");
  }
  process.exit(0);
}

if (cmd === "progress") {
  const job = load(ID);
  if (has("done")) job.done = Number(flag("done"));
  if (has("total")) job.total = Number(flag("total"));
  if (flag("note")) job.log.push({ at: new Date().toISOString(), what: flag("note") });
  if (flag("next")) job.resume.next_command = flag("next");
  job.status = job.done >= job.total && job.total > 0 ? "artifacts-pending" : "running";
  save(job);
  console.log(`job: ${ID} ${job.done}/${job.total} ${job.unit}`);
  process.exit(0);
}

if (cmd === "resume-set") {
  const job = load(ID);
  if (flag("next")) job.resume.next_command = flag("next");
  if (flag("notes")) job.resume.notes = flag("notes");
  save(job);
  console.log("job: resume instructions saved");
  process.exit(0);
}

if (cmd === "artifact") {
  const job = load(ID);
  const rel = argv[2] && !argv[2].startsWith("--") ? argv[2] : null;
  if (!rel) die("artifact needs a path");
  const abs = resolve(ROOT, rel);
  if (!existsSync(abs)) die(`no such file: ${rel}`);
  const bytes = statSync(abs).size;
  const hash = sha256(abs);
  const existing = job.artifacts.find((a) => a.path === abs);
  if (existing) {
    existing.bytes = bytes;
    existing.sha256 = hash;
  } else {
    job.artifacts.push({ path: abs, bytes, sha256: hash, drive_id: null });
  }
  save(job, `artifact ${rel} ${human(bytes)} sha256 ${hash.slice(0, 12)}`);
  console.log(`job: registered ${rel} — ${human(bytes)} — sha256 ${hash.slice(0, 12)}`);
  console.log("job: this file is NOT safe yet. Upload it to Drive, then run `uploaded` with the id.");
  process.exit(0);
}

if (cmd === "uploaded") {
  const job = load(ID);
  const rel = argv[2] && !argv[2].startsWith("--") ? argv[2] : null;
  if (!rel) die("uploaded needs a path");
  const abs = resolve(ROOT, rel);
  const a = job.artifacts.find((x) => x.path === abs);
  if (!a) die(`${rel} was never registered — run \`artifact\` first so its sha256 exists`);
  const id = flag("drive-id");
  if (!id) die("--drive-id is required. A file without a Drive id is still one reset away from gone.");
  const claimed = flag("sha256");
  if (claimed && claimed !== a.sha256) {
    die(`sha256 mismatch: recording ${claimed.slice(0, 12)} but the file on disk hashes to ${a.sha256.slice(0, 12)} — the Drive copy is not this file`);
  }
  a.drive_id = id;
  a.uploaded_at = new Date().toISOString();
  save(job, `uploaded ${rel} -> Drive ${id}`);
  console.log(`job: ${rel} is now durable (Drive ${id})`);
  process.exit(0);
}

if (cmd === "decide") {
  const job = load(ID);
  const q = flag("q");
  const a = flag("a");
  if (!q || !a) die("decide needs --q and --a");
  job.decisions.push({ at: new Date().toISOString(), q, a });
  save(job, `decision recorded: ${q} -> ${a}`);
  console.log("job: decision recorded. Future sessions read these and must not re-ask.");
  process.exit(0);
}

if (cmd === "check") {
  const job = load(ID);
  const b = blockers(job);
  if (b.length === 0) {
    console.log(`job: ${ID} is safe to pause — everything needed to continue is outside the sandbox`);
    process.exit(0);
  }
  console.error(`job: ${ID} is NOT safe to pause. ${b.length} blocker(s):`);
  for (const x of b) console.error(`  - ${x}`);
  process.exit(1);
}

if (cmd === "pause") {
  const job = load(ID);
  const b = blockers(job);
  if (b.length) {
    console.error("job: REFUSING to pause — this is the exact situation that lost a finished video on 2026-11-13.");
    for (const x of b) console.error(`  - ${x}`);
    console.error("");
    console.error("Fix the blockers, then pause. Do not end the turn in this state:");
    console.error("  node scripts/job.mjs artifact <id> <file>      # records sha256");
    console.error("  <upload to Drive with the connector>");
    console.error("  node scripts/job.mjs uploaded <id> <file> --drive-id <id>");
    console.error("  git push                                       # the ledger itself must be pushed");
    process.exit(1);
  }
  job.status = "paused";
  const q = flag("q");
  if (q) job.log.push({ at: new Date().toISOString(), what: `awaiting operator: ${q}` });
  const durable = save(job, "paused");
  if (!durable) {
    console.error(
      "job: REFUSING to call this paused. The ledger was written but is NOT durable\n" +
        "     (not committed, or not pushed, or jobs/ is untracked).\n" +
        "     Fix it with: git add -A jobs && git commit -m 'job checkpoint' && bash scripts/git-push-retrying.sh <branch>",
    );
    process.exit(1);
  }
  console.log(`job: ${ID} paused safely. State is committed and pushed; a reset loses nothing.`);
  if (q) console.log(`job: question for the operator: ${q}`);
  console.log("job: remember to `git push` — a commit that only exists locally is still in the sandbox.");
  process.exit(0);
}

if (cmd === "resume") {
  const job = load(ID);
  const pct = job.total > 0 ? Math.round((job.done / job.total) * 100) : 0;
  console.log(`\n${job.id} — ${job.status} at ${job.done}/${job.total} ${job.unit} (${pct}%)\n`);
  if (job.goal) console.log(`goal: ${job.goal}\n`);
  console.log("NEXT:");
  console.log(`  ${job.resume.next_command || "(not set — reconstruct it from the log below)"}\n`);
  if (job.resume.notes) console.log(`${job.resume.notes}\n`);
  if (job.decisions.length) {
    console.log("ALREADY DECIDED (do not ask these again):");
    for (const d of job.decisions) console.log(`  - ${d.q} -> ${d.a}`);
    console.log("");
  }
  if (job.artifacts.length) {
    console.log("ARTIFACTS:");
    for (const a of job.artifacts) {
      const st = a.drive_id ? `Drive ${a.drive_id}` : "NOT UPLOADED";
      console.log(`  ${st.padEnd(38)} ${human(a.bytes).padStart(9)}  ${relative(ROOT, a.path) || a.path}`);
    }
    console.log("");
  }
  const b = blockers(job);
  if (b.length) {
    console.log(`WARNING: ${b.length} blocker(s) — this job cannot be paused yet:`);
    for (const x of b) console.log(`  - ${x}`);
    console.log("");
  }
  console.log(`last events:`);
  for (const e of job.log.slice(-6)) console.log(`  ${e.at.slice(0, 16)}  ${e.what}`);
  console.log("");
  process.exit(0);
}

if (cmd === "done") {
  const job = load(ID);
  const b = blockers(job);
  if (b.length) {
    console.error("job: cannot mark done — these are unfinished:");
    for (const x of b) console.error(`  - ${x}`);
    process.exit(1);
  }
  job.status = "done";
  save(job, "done");
  console.log(`job: ${ID} marked done`);
  process.exit(0);
}

if (cmd === "list") {
  if (!existsSync(JOBS)) {
    console.log("no jobs yet");
    process.exit(0);
  }
  const files = execFileSync("ls", [JOBS], { encoding: "utf8" }).split("\n").filter((f) => f.endsWith(".json"));
  for (const f of files) {
    const j = JSON.parse(readFileSync(resolve(JOBS, f), "utf8"));
    const pct = j.total > 0 ? Math.round((j.done / j.total) * 100) : 0;
    const unsaf = blockers(j).length ? "  ⚠ NOT PAUSABLE" : "";
    console.log(`${j.status.padEnd(17)} ${String(pct).padStart(3)}%  ${j.id}${unsaf}`);
  }
  process.exit(0);
}

console.log(`job.mjs — the durable ledger for work that must survive a reset

  start <id> --goal "..." --total N [--unit frames]
  progress <id> --done N [--note "..."] [--next "command"]
  resume-set <id> --next "command" [--notes "..."]
  artifact <id> <file>                      record a finished file + its sha256
  uploaded <id> <file> --drive-id <id>      mark it durable
  decide <id> --q "..." --a "..."           record an approval so it is never re-asked
  check <id>                                what blocks a pause
  pause <id> [--q "question"]               refuses unless the job is resumable
  resume <id>                               where to continue
  done <id>
  list

Read AGENTS.md -> "Long jobs" before using this on anything that runs for hours.`);
process.exit(cmd ? 1 : 0);
