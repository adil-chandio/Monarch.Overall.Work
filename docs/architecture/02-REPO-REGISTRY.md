# Repo Registry — all 22 repositories, classified

Checked live against the GitHub API on 2026-11-03.

| Repo | Size | Lang | Last push | Role | Space | Verdict |
|---|---|---|---|---|---|---|
| `Monarch.Overall.Work` | 580 MB | JS/React | 2026-11-03 | **core** | all | The OS. Everything you touch weekly happens here |
| `Monarch-Studio` | 1003 MB | Python | 2026-11-02 | satellite | studio | Durable multi-style video editing/animation system. Keep separate, call from here |
| `Monarch.Stickman` | 916 MB | Python | 2026-10-25 | satellite | studio | Animation rig work. Keep separate |
| `Social-media-Ref-Content-` | 404 MB | — | 2026-11-02 | asset-store | personal-brand | Reference content library. Never clone here |
| `World-Channel-` | 145 MB | — | 2026-11-02 | asset-store | yt-automation | YT channel media. Reference only |
| `portfolio` | 26 MB | CSS | 2026-10-31 | satellite | portfolio | Portfolio v37. Deploys to GitHub Pages — public proof surface |
| `Monarch-Agent` | 12 MB | Python | 2026-10-07 | satellite | ops | 17-gate QC CLI, approval ladder, production law. Policy source |
| `Mana-android` | 5 MB | HTML | 2026-10-19 | satellite | ops | Native Android voice AI OS. Separate product |
| `ali.` | 4 MB | HTML | 2026-02-18 | archive | — | Old experiment. Archive after confirming duplicates |
| `Maya` | 2 MB | TS | 2026-08-31 | satellite | ops | Maya AI OS web surface |
| `empty.` | 2 MB | — | 2026-08-28 | archive | — | Archive (name suggests intent, content unclear) |
| `adil-chandio` | 0 MB | — | 2026-10-31 | archive | — | GitHub profile README repo. Keep only if profile README is wanted |
| `Monarch.Assistant-` / `Monarch-Assistant-` | 0 MB | JS | 2026-09-16 | archive | — | Empty. Archive |
| `Monarch-domain` | 0 MB | TS | 2026-09-14 | archive | — | Empty. Archive |
| `M-Domain` | 0 MB | — | 2026-09-01 | archive | — | Empty. Archive |
| `Automonarch` | 0 MB | — | 2026-09-04 | archive | — | Empty. Archive |
| `creatorreach-ai` | 0 MB | TS | 2026-09-03 | archive | — | Empty. Archive (name overlaps outreach CRM now built in core DB) |
| `Monarch-automation-` | 0 MB | — | 2026-08-30 | archive | — | Empty. Archive |
| `Social.Automation` | 0 MB | — | 2026-08-30 | archive | — | Empty. Archive |
| `empty..` | 0 MB | HTML | 2026-02-09 | archive | — | Empty. Archive |
| `old.porfolio.vercel` | 0 MB | TS | 2026-08-20 | archive | — | Superseded by `portfolio`. Archive |
| `Adil-chandio-` | 0 MB | — | 2026-10-11 | archive | — | Empty. Archive |

## Summary

- **22 repos · ~3.2 GB · 9 empty**
- **1 core + 6 satellites + 2 asset stores + 13 archive candidates**
- Nothing is deleted. Archive = read-only, still linked from `config/repos.json`.

## Archive procedure (per repo, when confirmed empty)

```bash
# 1. confirm it is really empty or duplicated
gh repo view <owner>/<repo> --json isEmpty,diskUsage,defaultBranchRef

# 2. archive through the real GitHub endpoint (NOT the delete endpoint)
gh api -X PATCH repos/adil-chandio/<repo> -f archived=true -f visibility=public
```

Archive keeps the code and the URL alive, removes it from your active list, and is fully reversible.

## The rule that keeps this working

> A satellite repo is **referenced**, never **merged**.
> If something in a satellite becomes needed every day, move *the output* here (a JSON, a frame, a link) — not the 1 GB engine.
