# Deliverables index

Generated 2026-11-13 by `node scripts/build-deliverables-index.mjs`. **Do not edit by hand** — regenerate.

This file is the reason media can live outside Git without being lost. Every render gets one row: what it is,
how many bytes, its content hash, whether Git still carries it, and where the surviving copy lives.

`where: UNRECORDED` is not a pass — it means the file is in Git and has no external home yet. Files over 20 MB in
that state are listed under **To do** at the bottom.

## Totals

| | |
|---|---|
| Files listed here | 26 |
| Media inside Git (whole repo) | 1.06 GB across 185 files |
| Media inside Git, this folder only | 815.6 MB |
| Recorded in an external location | 1 |
| Tracking to-do (>20 MB, no external copy) | 12 |

## Rules these rows obey

1. A file may leave Git **only after** its row here names a surviving copy.
2. `sha256` is content evidence, not decoration — it proves the Drive copy is the file you rendered.
3. Nothing is deleted from disk by any script in this repo. Deletion is a human decision, made with this table open.

## Files

| File | Size | Kind | In Git | Where | sha256 |
|---|---:|---|---|---|---|
| `Last-Mammoths-Review-Reel-13min-720p.mp4` | 94.8 MB | video | yes | **UNRECORDED** | `479a30ae59ad` |
| `Last-Mammoths-Review-Reel-v8-720p.mp4` | 82.7 MB | video | yes | **UNRECORDED** | `deee8881e913` |
| `Last-Mammoths-Review-Reel-v9-720p.mp4` | 82.0 MB | video | yes | **UNRECORDED** | `ef6448a5f6cf` |
| `Extinct_Life_EP01_Amber_Atlas_Full_1080p.mp4` | 66.6 MB | video | yes | **UNRECORDED** | `345ad8314ac1` |
| `Last-Mammoths-Full-Film-3D-1080p.mp4` | 63.4 MB | video | yes | **UNRECORDED** | `d63a7cfd288a` |
| `Extinct_Life_EP01_Urdnglish_ShortShot_Rebuild_1080p.mp4` | 51.3 MB | video | yes | **UNRECORDED** | `08bf4770262a` |
| `Homotherium-Cub-3D-Rebuild-1080x1920.mp4` | 46.1 MB | video | yes | **UNRECORDED** | `38fa5c8d2060` |
| `Last-Mammoths-Opening-01-3D-1080p.mp4` | 45.3 MB | video | yes | **UNRECORDED** | `7102afe463cb` |
| `MON-DEMO26_v3_Master_60fps.enc` | 42.2 MB | video | yes | **UNRECORDED** | `15daeebe1171` |
| `MON-DEMO26_Proof_Over_Promises_v3_1080p60_Master.mp4` | 42.2 MB | video | yes | **UNRECORDED** | `6b0addb742c8` |
| `Extinct_Life_EP01_Lost_World_1080p.mp4` | 28.5 MB | video | yes | **UNRECORDED** | `ce49a107621e` |
| `Extinct_Life_Opening_25D_Cinema_Polish_45s_1080p.mp4` | 20.1 MB | video | yes | **UNRECORDED** | `90be37109e63` |
| `Extinct_Life_24s_Continuity_Proof_1080p.mp4` | 18.6 MB | video | yes | **UNRECORDED** | `a598f9a85202` |
| `Extinct-Life-V15-Continuity-Rebuild-1080x1920.mp4` | 17.7 MB | video | yes | **UNRECORDED** | `20307333d5e9` |
| `Extinct-Life-V14-Mastodon-Short-1080x1920.mp4` | 17.1 MB | video | yes | **UNRECORDED** | `a0fcd8196b76` |
| `Extinct-Life-V16-Evolving-Story-1080x1920.mp4` | 14.7 MB | video | yes | **UNRECORDED** | `f53a3266f92d` |
| `Extinct_Life_Opening_25D_Amber_Atlas_45s_1080p.mp4` | 14.3 MB | video | yes | **UNRECORDED** | `4e52cf91eb29` |
| `Extinct_Life_Opening_V2_45s_1080p.mp4` | 13.4 MB | video | yes | **UNRECORDED** | `b71cae9520d7` |
| `Homotherium-Cub-Premium-Fast-Cut-1080x1920.mp4` | 12.1 MB | video | yes | **UNRECORDED** | `be1a2c936fb0` |
| `Homotherium-Cub-Clean-Fast-Cut-1080x1920.mp4` | 10.9 MB | video | yes | **UNRECORDED** | `d626152ff81b` |
| `Last-Mammoths-Genetics-3D-Scene-Test.mp4` | 7.0 MB | video | yes | **UNRECORDED** | `b1f028b7df63` |
| `Homotherium-Cub-This-Saber-Toothed-Cub-Still-Has-Its-Fur-1080x1920.mp4` | 6.8 MB | video | yes | **UNRECORDED** | `cd6402bff52d` |
| `Last-Mammoths-Genetics-3D-Recut-Test.mp4` | 6.6 MB | video | yes | **UNRECORDED** | `cc4b9412cd8b` |
| `Extinct-Life-V14-YouTube-Launch-Kit.zip` | 5.9 MB | archive | yes | **UNRECORDED** | `67db480950d4` |
| `Last-Mammoths-3D-Isolation-Test-22s.mp4` | 5.3 MB | video | yes | **UNRECORDED** | `09583cfca74e` |
| `Last-Mammoths-Gait-Test-3s.mp4` | 612 KB | video | no | Drive 3d animation · 1BxRaf5lucFswbBvAJahUelm4r6YMgzQd ✓ | `a7603a2592cb` |

## To do — media over 20 MB with no recorded external home

**12 files, 665.2 MB.** Each needs one of:
upload to YouTube Unlisted, move into the Drive folder named in `config/drive-map.json`, or an explicit decision to keep it in Git.

- [ ] `Last-Mammoths-Review-Reel-13min-720p.mp4` — 94.8 MB
- [ ] `Last-Mammoths-Review-Reel-v8-720p.mp4` — 82.7 MB
- [ ] `Last-Mammoths-Review-Reel-v9-720p.mp4` — 82.0 MB
- [ ] `Extinct_Life_EP01_Amber_Atlas_Full_1080p.mp4` — 66.6 MB
- [ ] `Last-Mammoths-Full-Film-3D-1080p.mp4` — 63.4 MB
- [ ] `Extinct_Life_EP01_Urdnglish_ShortShot_Rebuild_1080p.mp4` — 51.3 MB
- [ ] `Homotherium-Cub-3D-Rebuild-1080x1920.mp4` — 46.1 MB
- [ ] `Last-Mammoths-Opening-01-3D-1080p.mp4` — 45.3 MB
- [ ] `MON-DEMO26_v3_Master_60fps.enc` — 42.2 MB
- [ ] `MON-DEMO26_Proof_Over_Promises_v3_1080p60_Master.mp4` — 42.2 MB
- [ ] `Extinct_Life_EP01_Lost_World_1080p.mp4` — 28.5 MB
- [ ] `Extinct_Life_Opening_25D_Cinema_Polish_45s_1080p.mp4` — 20.1 MB

## Repo-wide media by folder

Every tracked file whose extension matches `config/media-policy.json`. This is the backlog that `npm run guard`
reports on, kept here so it is readable without running anything.

| Folder | Media files | Size |
|---|---:|---:|
| `deliverables` | 26 | 816.2 MB |
| `production` | 91 | 157.1 MB |
| `refs` | 14 | 73.8 MB |
| `public` | 6 | 33.5 MB |
| `gpu-engine` | 17 | 3.4 MB |
| `docs` | 31 | 2.7 MB |
| **all folders** | **185** | **1.06 GB** |

**Why the images are not simply ignored:** 20 of the 42 workflows that commit run `git add` on a media folder.
An ignore rule would turn those into failed commits. Workflow uploads must change first — see
`docs/architecture/07-MEDIA-AND-REPO-SIZE.md` and `node scripts/check-workflow-media.mjs`.

## Outside this folder

Media tracked elsewhere in the repo is counted by `node scripts/media-check.mjs --all`. It reports by rule and by folder,
because that list is long and belongs in CI output, not in a hand-read page.
