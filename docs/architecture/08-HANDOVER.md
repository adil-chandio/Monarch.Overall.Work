# Handover — read this first in a new session

Written 2026-11-13. This file exists because the work is not the *files*, it is the
*reasoning*. Anyone (human or agent) picking this up should be able to continue
without re-deriving a single decision, and without repeating a single mistake.

Read in this order: this file → `07-MEDIA-AND-REPO-SIZE.md` → `config/media-policy.json`
→ `deliverables/INDEX.md`.

---

## 1. What the repo is for

Git holds **knowledge**. Media lives **outside** Git. Every media file that leaves
Git keeps one line in `deliverables/INDEX.md` so "where did that go?" always has
an answer. That sentence is the whole policy; everything else is enforcement.

Three storage tiers, in order of authority:

| Tier | Holds | Why it is the right place |
|---|---|---|
| **YouTube Unlisted** | the master of every finished video | free, unlimited, permanent, streams and downloads, survives a sandbox reset |
| **Drive** | delivery copies, packaging, client handoff | where the operator actually picks files up (Android) |
| **Sandbox disk** | work in progress | temporary by definition |
| Dropbox | cold tier | only when the first three are wrong for the artefact |

The operator is **Android-only**. Anything that requires a desktop file manager is
not a delivery. A Drive link is a delivery.

---

## 2. The one habit that matters

**Never trust the disk. Trust the record.**

This is not a style preference. It cost two red CI runs in one day:

- the index page listed 26 rows locally and 1 in a fresh clone, because rows were
  built from `find deliverables/`
- a guard test counted 9 evidence folders locally and 0 in a fresh clone, for the
  same reason

A released file is *supposed* to be absent from a clone. So:

```bash
node scripts/build-deliverables-index.mjs --check          # must pass here AND in a clone
node scripts/build-deliverables-index.mjs --verify-local   # are the bytes here, still hashing right?
```

If you write a new check, run it in a fresh clone before you believe it:

```bash
git clone --depth 1 --branch arena/ba8d901e-monarch-overall-work \
  https://github.com/adil-chandio/Monarch.Overall.Work.git /tmp/freshcheck
cd /tmp/freshcheck && node scripts/guard.test.mjs
```

---

## 3. The migration loop (proven, 26 files)

Never release a file from Git until its replacement is proven byte-identical.

```
1. sha256sum <file>                                  # local truth
2. upload to the Drive folder named in config/drive-map.json
3. get_file → sha256Checksum                         # Drive truth
4. compare 2 and 3 — if they differ, STOP. Do not release.
5. git rm --cached <file>                            # index only; disk untouched
6. add {name, bytes, drive_id, sha256} to config/drive-map.json
7. node scripts/build-deliverables-index.mjs         # the ledger now names it
8. confirm the file is still on disk, same byte count
```

A successful upload is **not** proof of content. Step 3 is not optional.

**Measured upload ceiling**: 100 MB (the connector's request limit). Verified up to
**99,408,313 B**. The old "~50 MB, above that untested" note was wrong and cost real
work — nine files sat in Git because nobody had tried them. The size ladder that
proved it is in `config/media-policy.json → upload_limits.size_ladder_measured`.

---

## 4. `.gitignore` rules that are easy to get backwards

**Exclude contents, never a directory.** `git add <dir>` exits 1 when that dir is
excluded, and GitHub Actions runs every step with `bash -e` — so the job dies.

```
production/extinct-life/film-*/inspection/      WRONG  (job dies on git add)
production/extinct-life/film-*/inspection/**    RIGHT  (adds work, stills stay out)
```

**A `!` negation cannot rescue a file inside an excluded directory.** Git never
re-includes what a directory rule excluded. There is a guard test for this.

**Tracked-but-ignored is a trap.** `.gitignore` does not affect files already in the
index; they keep showing as modified and keep staging. The day you release one with
`git rm --cached`, the ignore rule switches back on and the next `git add` in a
workflow exits 1. `public/demo-preview.mp4` was in exactly that state.

**Never `git add -f`** to defeat a rule. If a rule is wrong, fix the rule.

---

## 5. The push helper

`scripts/git-push-retrying.sh <branch> [attempts]` — 12 attempts, exponential
backoff with jitter, `--autostash`.

Two things it taught us:

- Fixed-interval jitter does **not** resolve contention. Six clients woke together
  and lost every round. Exponential backoff converges at 20 clients (simulated).
- `--autostash` is not cosmetic. A render job leaves `.cache/` dirty; plain
  `git pull --rebase` refuses to run at all on a dirty tree. The comment claimed
  `--autostash` for weeks while the command did not have it.

**Do not wrap a command in `|| true` to make a red step green.** That is how a
regression becomes an unexplained red job. It happened here: `|| true` on `git add`
hid the real cause for four render cycles.

---

## 6. What is migrated, and what deliberately is not

**Migrated to Drive** (all sha256-verified, all still on disk):

| What | Count | Where recorded |
|---|---|---|
| `deliverables/` media | 26 of 26 | `config/drive-map.json` |
| frame-evidence JPGs from `production/` | 537 (142 MB), in 2 archives | `config/drive-map.json` |

**Deliberately still in Git**, with reasons in `config/media-policy.json → keep_in_git`:

- `public/thumbnails|proof|showreel/`, `public/demo-poster.jpg` — the app renders them
- `public/demo-preview.mp4` — `src/B2BStudio.jsx` plays it; it is product surface
- `deliverables/MON-DEMO26_Proof_Over_Promises_v3_1080p60_Master.mp4` — the approved
  public proof master (a Drive spare exists, but Git keeps it on purpose)
- `docs/research/**/*.csv.gz` — measurement data
- **source assets** under `production/`: `.blend` rig, `.glb` meshes (87 references),
  narration `.m4a`, `.mp3`/`.flac` stems, `.png` scene plates. These are inputs, not
  output. Releasing them would break renders, not save space.

**Never deleted.** Every released file is still on disk at its original path. Only
the Git index entry was dropped.

---

## 7. Rules that hold across the whole repo

- **49 workflows, 39 skills entries** must keep running. Nothing that works may break.
  Prove a breakage with a run, not with a reading.
- **Never create extra repos** and link them back.
- `npm test` (6 config tests) and `node scripts/guard.test.mjs` (34) must both pass.
- `node scripts/build-deliverables-index.mjs --check` must pass **and** the page must
  render byte-identically on a machine that holds none of the videos.
- Nothing is deleted to free space. Deletion is a human decision made with
  `deliverables/INDEX.md` open.

---

## 8. Known dead ends — do not retry

| Thing | Why it fails |
|---|---|
| `gh run view <id> --log-failed`, job logs | served from `productionresultssa*.blob.core.windows.net`; unreachable here (`curl` exit 35, SSL). Write diagnostics to `$GITHUB_STEP_SUMMARY` instead |
| `git check-ignore` on a tracked file | needs `--no-index`, otherwise it reports tracked files as not ignored |
| `git gc` with < ~3 GB free | leaves a multi-GB `tmp_pack_*` and fills the disk |
| Stale `.git/objects/pack/*.keep` | pins a pack; `git gc` then duplicates it (4.5 → 5.0 GB). Delete the `.keep` first |
| `rev-list --objects --all` | returns 0 blobs in this repo |
| `gh workflow run`, `gh secret list` | 403 with the current token |

---

## 9. If something is red

1. `gh run view <id> --json jobs` — which **step** failed.
2. Reproduce the step body locally, verbatim, under `bash -e`.
3. Clone the branch fresh and run the same command there.
4. If it only fails in CI, the difference is the environment: a shallow clone, a
   dirty tree, a missing file, or a permission. Not the logic.
5. Write what you learned into this file. A fix without a recorded reason gets
   undone by the next person.

The state of the world is always these three commands:

```bash
node scripts/media-check.mjs --all
node scripts/guard.test.mjs
node scripts/build-deliverables-index.mjs --check
```
