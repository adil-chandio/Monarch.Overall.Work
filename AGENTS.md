# AGENTS.md — read this first

You are an agent working in `Monarch.Overall.Work`. This file exists so the operator does not have to repeat
the same context in every new chat. **A new chat does not remember the last one. This file does.**

Read in this order, and stop reading when you have what you need:

| # | File | Gives you |
|---|---|---|
| 1 | **this file** | the rules that are not negotiable |
| 2 | [`README.md`](./README.md) | what the app is, five spaces, how to run it |
| 3 | [`docs/architecture/01-REPO-STRUCTURE.md`](./docs/architecture/01-REPO-STRUCTURE.md) | folder layout, data model, hard rules |
| 4 | [`docs/architecture/07-MEDIA-AND-REPO-SIZE.md`](./docs/architecture/07-MEDIA-AND-REPO-SIZE.md) | **before you touch any video, audio, image or model** |
| 5 | [`skills/INDEX.md`](./skills/INDEX.md) | 958 vendored skills, routed per space |
| 6 | [`docs/architecture/06-YT-INTEL.md`](./docs/architecture/06-YT-INTEL.md) | the research desk and its measured vs borrowed data |

---

## The operator

- Works from an **Android phone**. Not a laptop. Design for that.
- Says what they mean plainly, in Roman Urdu. Answer plainly, in the same register. No ceremony.
- Has been burned by confident wrong answers. **A measured "I don't know" beats a fluent guess every time.**
- Standing rules, stated repeatedly and not to be relaxed:

| Rule | Meaning |
|---|---|
| **Nothing is deleted** | No file, no commit, no skill, no workflow. Not to save space, not "because it's duplicated". Deletion is the operator's click, with the evidence in front of them. |
| **Nothing is lost** | If something must leave Git, an index row naming its surviving copy must exist **first**. |
| **Nothing is invented** | A handle, a folder id, a benchmark figure, an upload size. If it was not measured, it says `unconfirmed`. |
| **Ask before irreversible work** | History rewrites, force-pushes, bulk `git rm --cached`, Drive deletions. |
| **No repo explosion** | Do not create new repos and move work into them. `config/repos.json`: "Satellites are referenced, never merged." |

---

## What this repo is

The **operating system** for five work domains — not the content itself.

| Space | Route | Runs |
|---|---|---|
| `yt-automation` | `/space/yt-automation` | faceless channels + the production factory that feeds them |
| `monarch-studio` | `/space/monarch-studio` | video editing + website development, clients, settlement |
| `personal-brand` | `/space/personal-brand` | motivational + AI-BTS accounts |
| `portfolio` | `/space/portfolio` | the public proof surface — real numbers only |
| `ops` | `/space/ops` | money, calendar, agents, repo health |

---

## The one rule that gets broken most

> **Git holds knowledge. Media lives outside Git and gets one line inside it.**

Measured 2026-11-13: tracked tree 1,348 MB, of which **1.09 GB was media** across 185 files. `.git` was 4.5 GB
against a 1 GB target. The cause was a one-line guard (`deliverables/*.mp4`) that matched a single directory depth.

**Do not add a video, audio file, image plate, 3D model or archive to Git.** Not temporarily. Not with `git add -f`.
Not "just to test". The pre-commit hook will refuse, and it is right to.

| Instead | Where |
|---|---|
| a finished master | YouTube Unlisted → then `drive.google.com` link → then an index row |
| delivery / packaging / client handoff | Drive, in the channel folder from `config/drive-map.json` |
| the knowledge from a video you watched | a `.md` note with the link and what it taught — **that** goes in Git |
| a reference video you were shown | the same: link + note, never the file |

```bash
npm run guard          # is anything wrong right now
npm run guard:test     # did someone loosen the rule
node scripts/build-deliverables-index.mjs
```

Full detail: [`docs/architecture/07-MEDIA-AND-REPO-SIZE.md`](./docs/architecture/07-MEDIA-AND-REPO-SIZE.md).

---

## Long jobs — the rule that cost a finished video

On 2026-11-13 this happened, and it must never happen again:

| | |
|---|---|
| Work done | 480/480 frames rendered, all 14 QC checks passing, a 12.6 MB MP4 encoded |
| What the agent did | reported it ready and ended the turn |
| What it did **not** do | upload it, or write down that it was unuploaded |
| What happened | the operator was away; the sandbox reset; frames, MP4 and ~2 hours of compute were gone |
| What it cost | the entire render, start to finish, twice over |

**This was not a `.gitignore` problem.** The repo had no concept of a job: nowhere
to write "480/480 done, MP4 exists, NOT yet on Drive", and no rule that a session
may not go idle in that state. The agent was not careless; it was never told.

### The rule

> **A sandbox is temporary. Before you pause, approve, or end a turn, everything
> needed to continue must already exist somewhere a reset cannot reach.**
> Text → GitHub (committed **and pushed**). Media → Drive (with a `drive_id`).

A finished video that exists only in the sandbox is not finished. It is one
reset away from never having existed.

### The mechanism

`node scripts/job.mjs` — a ledger in `jobs/`, committed to Git on every write.

```bash
node scripts/job.mjs start <id> --goal "..." --total 480 --unit frames --next "bash scripts/render-all.sh --from 319"
node scripts/job.mjs progress <id> --done 320 --note "S4 done, S5 lighting next"
node scripts/job.mjs artifact <id> <file>              # records bytes + sha256
node scripts/job.mjs uploaded <id> <file> --drive-id <id> [--sha256 <h>]
node scripts/job.mjs decide <id> --q "..." --a "..."   # an approval, so it is never re-asked
node scripts/job.mjs pause <id> [--q "..."]            # REFUSES if the job is not resumable
node scripts/job.mjs resume <id>                       # what a new session reads first
```

`pause` exits 1 when an artifact has no `drive_id` or no `sha256`, or when
`resume.next_command` is empty. That refusal is the point: it turns "the agent
forgot" into a command that cannot succeed.

### What every long job must carry

Four things, written down **before** the first pause, not after:

1. **`resume.next_command`** — the literal command a fresh session runs to continue. Not a description. A command.
2. **Every finished artifact registered with its sha256**, and every one uploaded with a `drive_id`.
3. **Every approval recorded with `decide`** — so the next session does not ask the operator the same question at the same 75%.
4. **The ledger pushed.** A commit in the sandbox is still in the sandbox.

### The approval window — ask early, ask once

The operator is a phone user in a different time zone from the work. "I will ask
at 75% when it is ready to look at" is the single decision that turns a working
render into a lost one, because 75% is exactly when nobody is looking.

| When to ask | What to ask | Why then |
|---|---|---|
| **Before any long run starts** | the whole list: lighting, camera, palette, music, duration, output name. Ten questions at 5% cost one message | every one of them is cheaper to answer now than to re-render later |
| **As soon as a file exists** | nothing — just upload it, then report the link with progress | the upload is not a decision, it is a safety step. Never wait for approval to upload |
| **At a genuine fork** | one question, with your recommendation and the cost of each branch | a fork with two defensible answers is the only thing worth stopping for |
| **Never** | "should I continue?", "is this okay?", "shall I proceed?" | the answer is always yes, and asking it strands the job |

**Never let a question be the thing that stands between a finished file and an
upload.** If you must ask something, upload first, ask second, and record the
question in the job ledger so the next session sees it without the operator
repeating it.

**Batch, do not stream.** One message with five questions beats five messages
with one, because the operator answers them in one sitting. Streaming questions
across a 2-hour render guarantees at least one of them arrives while the phone is
in a pocket.

### If you are about to be idle anyway

Sometimes the work genuinely cannot continue without an answer. Then:

1. Register every finished artifact (`job.mjs artifact`) and upload every one
   (`job.mjs uploaded --drive-id`).
2. Write `resume.next_command` as a literal command, so a new session does not
   have to reconstruct your intent from a log.
3. Record the question with `job.mjs decide`-style framing and leave the job
   `paused`.
4. `job.mjs check` must exit 0. If it exits 1, the job is not resumable and you
   are about to repeat the incident.
5. Push. Then tell the operator in one line: what is done, where the file is,
   what you need.

### While the operator is away

The operator works from a phone and is often not looking. That is normal, not an
exception. So:

- **Do not wait at 75% to ask something you could have asked at 5%.** Batch the
  approvals early. Every question you defer to the middle of a render is a
  question that strands the render.
- **Upload as soon as the file exists**, not at the end of the job. An uploaded
  partial beats a perfect file that evaporated.
- **Never end a turn with unuploaded media.** Run `node scripts/job.mjs check <id>`
  first. If it fails, fix it or say plainly that the work is at risk — but do not
  go quiet.

### Checkpoints are not git history

Frames, MP4s and renders are **media**: they never enter Git, no matter how small
or temporary. Durability for media is Drive, not a commit. Git carries the
**ledger and the knowledge** — what was done, what is next, what was decided.

---

## Storage ceilings, measured

| Thing | Number | Source |
|---|---|---|
| GitHub single-file hard cap | **100 MB** | GitHub's own limit |
| Drive/Dropbox upload tool ceiling from this environment | **100 MB** | the tool refuses above this |
| Actually exercised end to end | **99,408,313 B (94.8 MB)** | measured 2026-11-13, 9 files 44-99 MB, sha256 verified on Drive |
| Sandbox disk | 21 GB total, **5.9 GB free** | `df -h` on 2026-11-13 |
| Drive | 15 GB total, **10.71 GB free** | operator screenshot 2026-11-13 |
| Dropbox | 2.00 GB allocated, 35 MB used | live API 2026-11-13 |
| `.git` today | **3.1 GB** | `du -sh .git`, after repack |
| tracked tree today | **470.9 MB** | `git ls-tree -r -l HEAD`, 46% of the 1 GB budget |

**Encode to stay under the ceiling**, do not discover the ceiling mid-render:

| Format | Bitrate | Size |
|---|---|---|
| 12-min longform 1080p | 0.85 Mbps + 128 kbps audio | ~95 MB |
| 60 s vertical | 3.0 Mbps + 128 kbps audio | ~25 MB |

Reference: the 12-minute 1080p 3D film already in this repo is **63.4 MB**.

---

## How to work here

1. **Measure before asserting.** `git`, `du`, `df`, the Drive API, the actual file. If you cannot measure it, say so.
2. **Say what you did not do and why.** Every skipped step with a reason beats a claim without one.
3. **Never delete to save space.** Produce the evidence table and let the operator decide.
4. **Report in the operator's register.** Tables and plain sentences. Bold the number that matters.
4b. **Do not "fix" the image gap before the workflows.** `.gitignore` cannot block images while 20 workflows commit them. Order matters: workflow uploads first, then the rule.
5. **Leave the repo runnable.** `npm test`, `npm run guard:test` and `npm run build` must pass before you stop.
6. **Write it down.** Anything you decided in chat that future-you would need belongs in a file in this repo.
   That is the whole point of `AGENTS.md`, `docs/architecture/`, and `deliverables/INDEX.md`.

---

## Known open items (do not re-diagnose these — they are already measured)

| # | Item | State |
|---|---|---|
| 1 | 148 media files tracked in Git, 1.09 GB | indexed in `deliverables/INDEX.md`, awaiting operator approval to `git rm --cached` |
| 2 | Dead pack file `.git/objects/pack/tmp_pack_TXpr58`, 1.29 GB | safe to `git gc`; awaiting approval |
| 3 | Duplicate reel versions v8 / v9 / 13min, 261 MB | retained by the "nothing is deleted" rule |
| 4 | History rewrite to reclaim ~4.3 GB | needs `git bundle --all` + force-push + 3 open PRs re-based |
| 5 | Drive holds 6 × `EMS-…_cp000X.bundle` ≈ 534 MB | operator's call |
| 6 | `ch-03 Curious Miles` ↔ Drive "Monarch World Channel" | unconfirmed pairing, named in `config/drive-map.json` |
| 7 | `ch-01`, `ch-02` have no Drive folder | named in `config/drive-map.json` |
| 8 | `features` of the app listed in `README.md` under "not yet provided" | still true; do not claim them |
| 9 | **20 of 42 committing workflows `git add` media** | measured by `node scripts/check-workflow-media.mjs`; this is what regrows the repo; needs a per-workflow upload rewrite |
| 10 | 560 tracked images (176 MB) beyond the 211 load-bearing ones | two buckets: scripted regenerable evidence (pins verified) and workflow `inspection/` output; neither can be ignored until #9 lands |
| 11 | Image extensions are **not** in `.gitignore` | deliberate, not an oversight — ignoring them today fails 20 pipelines |

---

## Things that will get you a correction

- Saying "Drive is full" without a number. It is **10.71 GB free**.
- Saying "it will upload" about a 400–600 MB file. The ceiling is **100 MB**, and only **50 MB** is proven.
- Putting a video in Git to "show" the operator something. Show a link and a note.
- Inventing a handle, a channel name, or a Drive folder pairing. Use `null` and `unconfirmed`.
- Reporting a size from memory. Sizes change; measure them.
