# MONARCH OS — `Monarch.Overall.Work`

**One repo. One deploy. Five work domains. Every other GitHub repo is a linked satellite.**

| Space | Route | What it runs | Detail |
|---|---|---|---|
| **YouTube Automation** | `/space/yt-automation` | 3 faceless channels + the production factory that feeds them | [03](./docs/architecture/03-SPACE-OPERATING-MODEL.md#space-1--yt-automation-youtube-automation-business) |
| **Monarch Studio** | `/space/monarch-studio` | video editing + website development, clients, portals, settlement | [03](./docs/architecture/03-SPACE-OPERATING-MODEL.md#space-2--monarch-studio-video-editing--website-development) |
| **Personal Brand** | `/space/personal-brand` | motivational/youth account + AI-BTS account + showcase identity | [03](./docs/architecture/03-SPACE-OPERATING-MODEL.md#space-3--personal-brand) |
| **Portfolio** | `/space/portfolio` | the public proof surface — real numbers only | [03](./docs/architecture/03-SPACE-OPERATING-MODEL.md#space-4--portfolio) |
| **Ops** | `/space/ops` | money, calendar, agents, repo health | [03](./docs/architecture/03-SPACE-OPERATING-MODEL.md#space-5--ops) |

Start here → **[docs/architecture/](./docs/architecture/README.md)**

- **[01 — Repository structure](./docs/architecture/01-REPO-STRUCTURE.md)**: layout, five spaces, data model, hard rules
- **[02 — Repo registry](./docs/architecture/02-REPO-REGISTRY.md)**: all 22 repos classified core / satellite / asset-store / archive
- **[03 — Space operating model](./docs/architecture/03-SPACE-OPERATING-MODEL.md)**: pipeline, assets, scoreboard, allowed agents per space
- **[04 — Build waves](./docs/architecture/04-BUILD-WAVES.md)**: five shippable waves with verify lists and rollback

## Repo health

```bash
node scripts/audit-repos.mjs            # live drift check against GitHub
node scripts/audit-repos.mjs --offline  # config only

npm run guard              # media & size policy over the whole tracked tree
npm run guard:test         # 21 tests on the guard rules themselves
npm run index:deliverables # regenerate deliverables/INDEX.md
npm run hooks:install      # install the pre-commit media guard
```

## Git holds knowledge, not media

This repo is the operating system. It is not a media locker.

| Inside Git | Outside Git |
|---|---|
| skills, docs, config, code, measurements | video, audio, image plates, models, archives |
| **and one index row per media file**, naming where the surviving copy lives | |

The rule lives in [`config/media-policy.json`](./config/media-policy.json), is enforced by
[`scripts/media-check.mjs`](./scripts/media-check.mjs) and by
[`.github/workflows/repo-guard.yml`](./.github/workflows/repo-guard.yml), and is explained in
**[07-MEDIA-AND-REPO-SIZE.md](./docs/architecture/07-MEDIA-AND-REPO-SIZE.md)**.

Measured on 2026-11-13: tracked tree 1,348 MB, of which 1.09 GB was media across 185 files — 816 MB of it in
`deliverables/`. The old guard was a single line, `deliverables/*.mp4`, which matched one directory depth and
nothing else. That is fixed; nothing new can enter. **Nothing has been deleted** — the backlog is listed, with
sizes and hashes, in [`deliverables/INDEX.md`](./deliverables/INDEX.md).

Where media lives instead: **YouTube Unlisted** (unlimited, permanent, free) for masters, **Drive** for delivery
and packaging, **Dropbox** as cold storage. Folder ids are recorded in
[`config/drive-map.json`](./config/drive-map.json) — read live from Drive, never guessed.

Last run: **22 repos · 3,207 MB · 11 empty · 10 archive candidates**, no drift.

## Config is the source of truth

`config/spaces.json`, `channels.json`, `social.json`, `services.json`, `repos.json`, `payment-rails.json`.
Read through `src/lib/config.js`. **Never hardcode these lists in a component.**

## Run it

```bash
npm install
npm run dev     # Vite dev server (Arena preview host allowed)
npm run build
```

Routes that must never break: `/`, `/?portal=CODE`, `/?workspace=1`, `/showreel/`.

---

## Run the current private preview

```bash
npm install
npm run dev
```

The Vite dev server is configured for the Arena preview host. For a production bundle:

```bash
npm run build
```

## Implemented in this build

- Premium responsive workspace shell, mini-app navigation, global search (`Ctrl/Cmd + K`), and a clear private-preview notice.
- Dashboard and persistent local tasks, priorities, inbox filters, month navigation, starter projects, and project rooms with task/notes sections.
- Separate channel spaces for the three sample YouTube channels, a content pipeline, stage changes, and a video workspace for idea/brief, research, hook, script, thumbnail/packaging notes, and production checklist.
- Social Studio with account spaces, pillars, short-form planning, and an editable production stage.
- AI & Agent Library for manually saved conversation summaries, tags, project context, and follow-up actions.
- Knowledge notes and Monarch Vault folders plus Discord-inspired spaces, channels, and local conversations. File upload, image/video/audio previews where supported, download, and manual delete work in the browser preview using IndexedDB; workspace records use local browser storage.
- Team roster and role selection are interactive in preview mode. Invites are visibly marked as local-only and do not send email or grant real access.
- A reviewed Supabase SQL foundation is included at `supabase/migrations/202610300001_monarch_core.sql`: workspace membership roles, RLS, core work data, private Vault bucket, and storage access policies.

## Important: what this preview does not yet provide

A separate **free-plan** Supabase project named `monarch-workspace` has been created in the ap-south-1 region. The unrelated `whatsapp-ai-saathi` project was not changed. Two migrations are applied: the private workspace/RLS foundation and a revision-checked workspace-state sync function. Email/password sign-up is enabled with email confirmation; the Arena preview and deployed Vercel URLs are allowed as auth redirects. A Vercel Hobby deployment is live at https://monarch-workspace-beryl.vercel.app (deployed from the current Arena branch).

Once you create and confirm your Monarch account in the preview, low-volume work records (tasks, ideas, scripts, projects, chat summaries, notes, and Vault conversations) sync to the private `workspace_state` record, so they can follow your account across devices. A revision check prevents a stale device from silently overwriting a newer saved version. The first account gets its own private workspace.

**Vault file bytes still stay in the current browser.** The private Storage bucket and workspace access rules exist, but the app's upload/download path has not yet been switched to cloud storage. Browser storage can be cleared or run out of quota. Do not treat it as backup, and don't upload irreplaceable files yet. The free plan has provider limits and can pause/sleep; there is no promise of 100 GB or unlimited retention.

The team roster can read the cloud membership list, but email invitations and role-change actions in the UI are not yet wired to the server. The database roles and RLS policies are in place; real invitation acceptance still needs a trusted server-side flow. Arena history is not auto-imported, and YouTube/social publishing is not connected.

## Cloud foundation notes

1. Project setup uses only a publishable Supabase key in the browser; no service-role key is included in the app.
2. Auth confirmation and redirects are configured for the Arena preview, the deployed Vercel host, and localhost. The current deployment is from the session branch; future Vercel deployments may need to be triggered manually unless Git auto-deploy is enabled.
3. The private Vault bucket and RLS are set up, but cloud file upload, resumable transfers, backup/restore, and invitation email are pending before team files are used for real work.
4. Keep the workspace on the free plan unless you explicitly choose otherwise. Watch provider quotas; don't assume included storage or bandwidth will cover large media.
5. Before inviting teammates, test separate accounts and verify Owner/Admin/Editor/Contributor/Viewer permissions in the live cloud project.
