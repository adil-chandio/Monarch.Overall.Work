# 07 — Media and repo size

**Status:** enforced since 2026-11-13. Source of truth: [`config/media-policy.json`](../../config/media-policy.json).
**Read this before adding any video, audio, image plate, 3D model or archive to the repo.**

---

## The one rule

> **Git holds knowledge. Media lives outside Git and gets one line inside it.**

| | |
|---|---|
| **Inside Git** | text, skills, docs, config, code, measurements, and **one small row per media file** |
| **Outside Git** | video, audio, image plates, 3D models, archives |
| **Never lost** | every outside file has a row naming where the surviving copy lives |

This is not a storage preference. It is the only arrangement that survives the three constraints this workspace actually has:

1. the sandbox disk is **21 GB with 4.5 GB free**
2. GitHub's per-file ceiling is **100 MB** and the repo target is **1 GB**
3. the operator works from a **phone**, so a 12 GB clone is not merely slow, it is unusable

---

## What went wrong (measured, not guessed)

On 2026-11-13 the repo was **11.5 GB**: `.git` 4.5 GB + working tree 7.0 GB. Tracked content alone was **1,348 MB** across 6,957 files.

| Cause | Size | Detail |
|---|---:|---|
| Media tracked in Git | **1.09 GB** | 185 files: 47 video, 87 audio, 13 models, 1 archive, plus image plates |
| Dead pack file | **1.29 GB** | `.git/objects/pack/tmp_pack_TXpr58`, an interrupted operation Git itself calls garbage |
| Duplicate history | **~2.1 GB** | three versions of the same 13-minute reel (v8, v9, v13min = 261 MB), all retained forever |

**The guard was one line.** `.gitignore` line 10 read `deliverables/*.mp4`. A glob with one directory level. `deliverables/sub/a.mp4` walked straight past it, and so did every file in `production/`, `refs/`, `public/` and `gpu-engine/`. Measured at the time:

| Path | Verdict before | after |
|---|---|---|
| `deliverables/x.mp4` | blocked | blocked |
| `deliverables/sub/a.mp4` | **allowed** | blocked |
| `public/demo-preview.mp4` (24 MB, tracked) | **allowed** | blocked |
| `production/extinct-life/x/renders/a.mp4` | **allowed** | blocked |
| `refs/a.enc`, `google_drive/`, `image-search/` | **allowed** | blocked |
| `public/thumbnails/`, `public/proof/`, `public/showreel/` | allowed | allowed (deliberately) |

---

## The real growth mechanism (found 2026-11-13)

The guard was one line. That was only half the story. The other half is **20 of the 42 workflows that commit**.

```
node scripts/check-workflow-media.mjs
```

| | |
|---|---|
| 50 workflows total | |
| 42 run `git commit` | they write results back into the repo |
| **20 `git add` a media path** | they push stills and frames straight into history on every run |

Examples, measured:

| Workflow | What it commits |
|---|---|
| `extinct-v14-directed.yml` | `git add production/extinct-life/film-v14-directed production/extinct-life/review-v14` |
| `extinct-v13-forensic.yml` | `git add production/extinct-life/review-v13` |
| `extinct-feature-3d.yml` | `git add deliverables/Extinct_Life_3D_Chapter03_Production_1080p.mp4` — an mp4, by name, on purpose |

**So adding a `.gitignore` rule alone would break 20 working pipelines.** The rule and the workflows have to move together. That is why this is staged, not switched.

### The fix, per workflow

```
before:  render → cp stills into production/…/inspection → git add → git commit → push
after:   render → upload stills as an Actions artifact (90 days, free) → commit only the JSON/CSV/MD
```

Nothing is deleted. The measurement files stay. The frames stop accumulating.

---

## Regenerable evidence — the honest exception

560 tracked images (176 MB) are not creative assets. Most are **measurement output extracted from a master that is already released**, by a script that is already in the repo.

The clearest case, measured:

| | |
|---|---|
| `production/extinct-life/review-v14/` | |
| text evidence — `EVIDENCE.json`, `every-frame-metrics.csv` (13,164 rows), `audio-per-second.csv`, review `.md`, generator `.py` | **5 files, 1.3 MB** |
| images — `full-resolution/`, `seconds/` | **102 files, 22.4 MB** |
| | images are **17× the bytes of the evidence they illustrate** |

**The images are a rendering of numbers that are already stored as text.** Keeping both stores the answer twice and the question once.

### The rule that makes removing them safe

`config/media-policy.json → regenerable_evidence` requires **all three** before a folder qualifies:

1. the **generator script** is in the repo
2. the **source master is pinned by sha256** — so a regeneration cannot silently use a different film
3. the **text evidence stays** — CSVs, JSON, the review markdown

Verified pins:

| Folder | Generator | Pinned source |
|---|---|---|
| `review-v13/` | `extract_evidence.py` | `29639cfd09dc15c7aa76568865618002fad69ff3ffda5307b2d01d6dc90719d0` |
| `review-v14/` | `extract_evidence.py` | `9ff2ebf9a007ab6118f4cf0417dedacb09e67bec2ba95e1d1c3d6995e4238f26` (226 MB master) |

**Not covered, and therefore staying:** every `film-v*/inspection/` still. Those come from `cp -r .cache/…/stills production/…/inspection`, which is a render output with no pinned source, not a scripted extraction. They move only when their owning workflow is changed to upload instead of commit.

---

## The four layers

### 1. `.gitignore` — repo-wide, anchored

The guard block at the bottom of `.gitignore` lists every media family with `*.<ext>` patterns, so depth no longer matters. It then re-allows exactly four paths that are small, load-bearing, and referenced by the app:

```
!public/thumbnails/**    1.6 MB — 1080x1920 posters the app renders
!public/proof/**         1.3 MB — the public portfolio surface
!public/showreel/**      0.9 MB — referenced by src/
!public/demo-poster.jpg  0.4 MB — poster frame paired with the demo video
```

Plus `docs/research/**/*.csv.gz` (measured frame indexes, text-derived) and the single approved public proof master `deliverables/MON-DEMO26_Proof_Over_Promises_v3_1080p60_Master.mp4`.

**Images are deliberately NOT in the ignore list yet.** Of 771 tracked images (203 MB), 211 are load-bearing (public surfaces + measured CSVs). The other 560 (176 MB) fall into two buckets — scripted, regenerable evidence (safe to remove once the pins are respected) and workflow `inspection/` output (removable only after the owning workflow uploads instead of commits). Ignoring them today would fail those 20 workflows. See *Regenerable evidence* above.

### 2. `.gitattributes` — stop the noise

`* text=auto eol=lf` ends line-ending churn across machines. Every media extension is declared `binary` so Git never attempts a diff or merge on a video. `skills/**` is marked `linguist-vendored` so 958 vendored skills do not drown the repo's own language stats.

### 3. `scripts/media-check.mjs` — the only place that decides

```
node scripts/media-check.mjs --staged    # pre-commit: only what is being committed
node scripts/media-check.mjs --all       # CI/audit: the whole tracked tree
```

It reads `config/media-policy.json` and reports. It **never deletes or modifies anything.** Exit 1 means "a human must decide", with the exact `git rm --cached` instruction attached.

### 4. `.github/workflows/repo-guard.yml` — the machine that does not forget

Runs on every PR and every push to `main`. Fails the build when:

- `scripts/guard.test.mjs` fails — the **rule itself** was loosened
- `npm test` fails — config shape broke
- `npm run build` fails
- `deliverables/INDEX.md` is stale

The media backlog is **reported but does not block** (see below).

### Local hook

```
bash scripts/install-hooks.sh
```

Sets `core.hooksPath=scripts/hooks`, so a forced `git add -f` of a video is refused at commit time. Verified: a forced-staged `.mp4` produced exit 1 and no commit was created.

---

## Why the backlog does not block CI

148 media files are already tracked. Blocking every PR until all 148 are moved would mean **no work can merge for weeks** — including the work that fixes the problem. So:

| Check | Blocks? | Why |
|---|---|---|
| guard rules hold | **yes** | a loosened rule lets the repo grow again |
| config tests | **yes** | a broken config is a broken app |
| build | **yes** | a broken build is a broken deploy |
| index stale | **yes** | a lying index loses files |
| media violations | **no** | pre-existing debt, tracked in `deliverables/INDEX.md` |

**No new media can enter.** The existing pile is a visible to-do list, not a secret.

---

## The three storage tiers

| Tier | Holds | Measured | Rule |
|---|---|---|---|
| **YouTube Unlisted** | the master of every finished video | free, unlimited, permanent | every finished render lands here before it counts as delivered |
| **Drive** | delivery copies, packaging, client handoff, competitor reference | 10.71 GB free of 15 GB (2026-11-13) | one copy per delivered video; never the only copy of something irreplaceable |
| **Sandbox disk** | work in progress | 4.5 GB free of 21 GB | temporary by definition; a reset must never destroy the only copy of anything |
| **Dropbox** | cold tier | 2.00 GB allocated, 35 MB used | only when YouTube and Drive are both wrong for the artefact |

---

## Upload ceilings — the honest numbers

| | |
|---|---|
| Tool ceiling for Drive/Dropbox uploads from this environment | **100 MB** |
| Actually exercised end to end | **~50 MB** |
| Anything above 50 MB | **untested** — do not promise it before trying it |

**Consequence:** a 12-minute master must be encoded at **≤ 0.85 Mbps + 128 kbps audio** to land at ~95 MB. That is not a quality compromise:

- the existing 12-minute **1080p 3D** film in this repo is **63.4 MB** (0.7 Mbps effective)
- YouTube re-encodes every upload, so a fatter master buys no visible quality
- a smaller master uploads faster, downloads faster to a phone, and costs less sandbox disk

| Duration | Bitrate | Measured size | Fits 100 MB? |
|---|---|---:|---|
| 12 min | 0.70 Mbps (existing film) | 63.4 MB | ✅ |
| 12 min | 0.85 Mbps (target) | 95.1 MB | ✅ |
| 12 min | 1.10 Mbps | 123 MB | ❌ |
| 12 min | 4.50 Mbps | 500 MB | ❌ |

---

## The flow that replaces "put it in the repo"

```
1. render in the sandbox, targeting the encode numbers above
2. upload to Drive, into the channel folder named in config/drive-map.json
3. add one row to deliverables/INDEX.md  (auto-generated — run the script)
4. hand the link to the operator; YouTube Studio can import from Drive directly
5. remove the sandbox copy only after step 3 exists and the upload is confirmed
```

### The index row

```
| File | Size | Kind | In Git | Where | sha256 |
| `Homotherium-Cub-3D-Rebuild-1080x1920.mp4` | 46.1 MB | video | yes | **UNRECORDED** | `38fa5c8d2060` |
```

`UNRECORDED` is deliberate. The index refuses to pretend a file is safe.

---

## What has NOT been done, and why

These are decisions, not oversights. Each needs the operator's explicit yes because each is irreversible or visible.

| # | Not done | Why it waits | Cost of waiting |
|---|---|---|---|
| 1 | `git rm --cached` on 148 media files | Removes them from the next commit's tree. Files stay on disk, but the change is visible in every clone. | Repo stays 1.35 GB tracked |
| 2 | History rewrite (`git filter-repo`) | Needs `git bundle --all` first; rewrites every commit hash; invalidates 3 open PRs; requires a force-push | `.git` stays 4.5 GB |
| 3 | `git gc` to drop the 1.29 GB dead pack | Safe, but it is disk surgery on `.git` and should not be the first thing done blind | 1.29 GB wasted |
| 4 | Deleting `v8`/`v9`/`v13min` duplicate reels from history | The user's standing rule is **nothing is deleted** | 261 MB duplicated |
| 5 | Removing unused Drive bundles (6 × `EMS-…_cp000X.bundle`, ~534 MB) | Same rule | Drive holds 534 MB of checkpoints |
| 6 | Rewriting 20 workflows to upload instead of commit | Each has its own verify list; a bulk edit is how a working pipeline breaks | The repo keeps regrowing from those 20 the next time they run |
| 7 | Dropping 560 regenerable/evidence images (176 MB) | Blocked behind #6 for the `inspection/` half, and needs approval for the scripted half | 176 MB of duplicated numbers |
| 8 | 757 tracked images are not covered by an ignore rule yet | 211 are deliberate (public surfaces + measured CSVs); the other 546 are regenerable or workflow output and depend on #6 and #7 | new images can still be added by workflow until #6 lands |

**Phase order if and when approved:** gc → `git rm --cached` → bundle backup → history rewrite. Each phase is independently valuable; none requires the next.

---

## Standing rules

1. **Video never enters Git.** Not temporarily. Not "just this once".
2. **A file leaves Git only after its index row names a surviving copy.**
3. **90% of the 1 GB budget is for text** — 3802 `.md` files are 31 MB; 958 skills are 44 MB. The knowledge layer can grow 10× and still fit.
4. **No force-push without `git bundle --all` on disk first.**
5. **Never promise an upload size that has not been tested at that size.**
6. **Nothing in `scripts/` deletes user files.** Deletion is a human decision made with `deliverables/INDEX.md` open.

---

## Commands

```bash
npm run guard              # audit the whole tracked tree
npm run guard:staged       # what a commit would add
npm run guard:test         # 21 tests on the rule itself
npm run index:deliverables # regenerate deliverables/INDEX.md
npm run index:check        # CI: fail if the index is stale
npm run hooks:install      # install the pre-commit guard
npm run test:all           # config tests + guard tests
node scripts/check-workflow-media.mjs            # which workflows still commit media
node scripts/check-workflow-media.mjs --json     # same, machine-readable
```

---

## Where the numbers came from

Every figure on this page was measured on 2026-11-13 in this repository, not estimated:

- `git ls-tree -r -l HEAD` → tracked tree 1,348 MB, 6,957 files
- `git cat-file --batch-all-objects --batch-check` → 3,452 MB of unique blobs in history
- `git count-objects -vH` → 2.33 GiB packed + 861 MiB loose + **1.29 GiB garbage**
- `du -sh` per folder → `deliverables` 817 MB, `production` 364 MB, `refs` 74 MB
- `git check-ignore --no-index` per pattern → the bypass table above
- Drive `list_files` (live) → folder ids and contents in `config/drive-map.json`
- Drive storage panel (operator screenshot) → 4.29 GB used of 15 GB

Anything that could not be measured is labelled **unconfirmed** rather than filled in.
