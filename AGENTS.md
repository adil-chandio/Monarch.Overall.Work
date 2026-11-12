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

## Storage ceilings, measured

| Thing | Number | Source |
|---|---|---|
| GitHub single-file hard cap | **100 MB** | GitHub's own limit |
| Drive/Dropbox upload tool ceiling from this environment | **100 MB** | the tool refuses above this |
| Actually exercised end to end | **~50 MB** | only this much is proven |
| Sandbox disk | 21 GB total, **4.5 GB free** | `df -h` on 2026-11-13 |
| Drive | 15 GB total, **10.71 GB free** | operator screenshot 2026-11-13 |
| Dropbox | 2.00 GB allocated, 35 MB used | live API 2026-11-13 |
| `.git` today | **4.5 GB** | `du -sh .git` |
| tracked tree today | **1,348 MB** | `git ls-tree -r -l HEAD` |

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
