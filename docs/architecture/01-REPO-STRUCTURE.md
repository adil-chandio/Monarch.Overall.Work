# MONARCH OS — Repository Structure

**One repo. One deploy. Five work domains. Zero repos left orphaned.**

Status: proposed structure, ready to implement in waves.
Audience: Adil (operator) + any agent working in this repo.

---

## 1. The one-line model

> `Monarch.Overall.Work` is the **operating system**.
> Every other GitHub repo is a **satellite** — linked to a domain space, not merged into it.

Merging a 1 GB Python animation system into a React workspace would produce a repo nobody can clone, deploy, or reason about. Instead: **control plane here, execution planes where they belong, one index that knows about all of them.**

---

## 2. Top-level layout

```
Monarch.Overall.Work/
├── index.html                    # Vite entry (existing)
├── package.json                  # build = vite build (existing)
├── vite.config.js
├── README.md                     # rewritten: what this repo is
│
├── src/                          # ── CONTROL PLANE (the app) ──
│   ├── main.jsx                  # root router (existing: ?workspace, ?portal)
│   ├── shell/                    # NEW: app-wide chrome, nav, command palette
│   │   ├── Shell.jsx             #   sidebar + topbar + domain switcher
│   │   ├── RouteMap.js           #   single source of truth for every route
│   │   └── CommandPalette.jsx    #   Ctrl+K across all domains
│   ├── spaces/                   # NEW: one folder per work domain
│   │   ├── yt-automation/
│   │   │   ├── SpaceHome.jsx     #   the mini space (3 channels + business)
│   │   │   ├── ChannelRoom.jsx   #   per-channel pipeline, scripts, uploads
│   │   │   ├── FactoryBoard.jsx  #   idea → script → voice → visual → upload
│   │   │   └── channels.config.js#   CH-01/02/03 definitions (single source)
│   │   ├── monarch-studio/
│   │   │   ├── SpaceHome.jsx     #   films + websites delivery desk
│   │   │   ├── ClientDesk.jsx    #   inquiries, portals, payment submissions
│   │   │   └── ShowreelDesk.jsx  #   beats, drive links, render runs
│   │   ├── personal-brand/
│   │   │   ├── SpaceHome.jsx     #   motivational + AI-BTS accounts
│   │   │   ├── AccountsRoom.jsx  #   per-account calendar + pillars
│   │   │   └── InspirationFeed.jsx
│   │   ├── portfolio/
│   │   │   ├── SpaceHome.jsx     #   the public face + case studies
│   │   │   └── CaseStudy.jsx
│   │   └── ops/                  #   cross-cutting: finance, calendar, agents
│   │       ├── MoneyDesk.jsx
│   │       └── AgentDesk.jsx
│   ├── B2BStudio.jsx             # existing public storefront + portal (KEEP)
│   ├── b2b.css                   # existing
│   └── lib/
│       ├── supabase.js           # existing client
│       ├── config.js             # NEW: reads src/config/*.json, validates
│       └── spaceStore.js         # NEW: per-space query helpers
│
├── config/                       # ── SOURCE OF TRUTH (data, not code) ──
│   ├── spaces.json               # 5 domains, ids, labels, icons, colors, routes
│   ├── channels.json             # 3 YT channels: id, name, niche, cadence, KPI
│   ├── social.json               # 2 personal brand accounts + portfolio
│   ├── repos.json                # NEW: index of all 22 GitHub repos + role + status
│   ├── services.json             # studio pricing catalog (mirrors DB seed)
│   └── payment-rails.json        # rails, instructions, no secrets
│
├── supabase/
│   ├── migrations/               # versioned SQL (existing pattern)
│   └── functions/public-intake/  # edge function (existing)
│
├── skills/                       # vendored agent skills (existing)
├── showreel/                     # 60fps render pipeline + python audio (existing)
├── gpu-engine/                   # b2b render jobs (existing)
├── deliverables/                 # masters (existing — see rule 5)
├── docs/                         # this folder
│   ├── architecture/             # 01..05 decision docs
│   └── zero-budget-launch-playbook.md
├── public/                       # static assets served by Vite
└── .github/workflows/            # CI: render, audit, deploy
```

---

## 3. The five spaces (exactly what you asked for)

| # | Space id | Name | What lives here | Primary source |
|---|---|---|---|---|
| 1 | `yt-automation` | YouTube Automation Business | 3 faceless channels + the factory that feeds them | `config/channels.json` + Supabase `channels`, `content_items` |
| 2 | `monarch-studio` | MONARCH® Studio | Video editing + website dev: clients, portals, money | Supabase `client_inquiries`, `client_portals`, `payment_submissions`, `agency_services` |
| 3 | `personal-brand` | Personal Brand | Motivational/youth account + AI-BTS account + portfolio account | `config/social.json` + Supabase `channels` (platform=instagram/tiktok) |
| 4 | `portfolio` | Portfolio | Public proof, case studies, showreel, live site | `public/`, `proof/`, external `adil-chandio/portfolio` |
| 5 | `ops` | Ops (cross-cutting) | Money, calendar, tasks, agents, repo index | Supabase `tasks`, `projects`, `saved_conversations` + `config/repos.json` |

Why `portfolio` and `ops` are separate: a client-facing proof surface must never share a screen with internal money data, and ops is the only space allowed to read across all others.

---

## 4. Navigation model (how it feels to use)

```
┌──────────────────────────────────────────────────────────────┐
│  ⌘K  MONARCH OS                        [space switcher]   ●  │
├────────────┬─────────────────────────────────────────────────┤
│ YT AUTOMATION  │                                              │
│   ├ CH-01      │   Space home: 3 channel cards + factory board │
│   ├ CH-02      │   → click a channel = that channel's room     │
│   ├ CH-03      │   → drag a content item across stages         │
│   └ Factory     │                                              │
│ STUDIO         │                                              │
│ PERSONAL       │                                              │
│ PORTFOLIO      │                                              │
│ OPS            │                                              │
└────────────┴─────────────────────────────────────────────────┘
```

- **One URL per space:** `/space/yt-automation`, `/space/monarch-studio`, …
- **One URL per channel:** `/space/yt-automation/ch/ch-01`
- **Deep links preserved:** `?portal=MON-DEMO26` and `?workspace=1` keep working exactly as today.
- **Command palette** indexes tasks, content items, portals, repos, notes — one search box over everything.

---

## 5. Data model (what is new in Supabase)

Existing tables are reused, not replaced. Only three additions:

```sql
-- 1. channel space binding: which of the 3 channels belongs to which space
alter table public.channels add column if not exists space_id text not null default 'yt-automation';

-- 2. repo index in the database (mirrors config/repos.json so the UI can query it)
create table if not exists public.github_repos (
  name text primary key,
  role text not null default 'archive'
    check (role in ('core','satellite','asset-store','archive')),
  space_id text not null default 'ops',
  visibility text not null default 'public',
  size_mb numeric,
  language text,
  status text not null default 'active'
    check (status in ('active','paused','archived','merge-candidate')),
  notes text not null default '',
  last_pushed_at timestamptz,
  updated_at timestamptz not null default now()
);

-- 3. unified work item view: content AND client jobs in one pipeline
create view public.work_queue as
  select 'content'::text as kind, id, workspace_id, channel_id, title, stage,
         planned_for as due_at, updated_at
    from public.content_items
  union all
  select 'client'::text, p.id, c.workspace_id, null,
         p.project_title, p.payment_status, null, p.updated_at
    from public.client_portals p
    join public.client_inquiries c on c.portal_id = p.id;
```

Everything else (`tasks`, `projects`, `knowledge_notes`, `vault_*`) already exists and is wired in `src/main.jsx`.

---

## 6. Repo policy — the 22 repos under control

Current reality (checked live): **22 repos, 9 of them empty, ~3.2 GB total.**

| Role | Repos | Rule |
|---|---|---|
| `core` | `Monarch.Overall.Work` | Only repo you actively develop in weekly |
| `satellite` | `Monarch-Studio` (1.0 GB Python), `Monarch-Agent`, `Monarch.Stickman` (916 MB), `Mana-android`, `Maya`, `portfolio` | Keep separate. Linked by `config/repos.json`. Never merge code; only reference |
| `asset-store` | `Social-media-Ref-Content-` (404 MB), `World-Channel-` (145 MB) | Large media. Reference only, never clone into this repo |
| `archive` | 9 empty repos + `empty..`, `empty.`, `ali.`, `old.porfolio.vercel`, `M-Domain`, `Monarch-domain`, `Automonarch`, `creatorreach-ai`, `Monarch-automation-`, `Social.Automation`, `Monarch-Assistant-`, `Adil-chandio-` | Freeze, then archive (not delete) once confirmed empty |

**Rule 5 (hard):** this repo never exceeds ~1 GB. Media that large goes to `asset-store` repos or Google Drive, and this repo holds only the link.

---

## 7. What gets built in which wave

| Wave | Scope | Files touched | Deploy impact |
|---|---|---|---|
| **W1** | `config/*.json` + `docs/architecture/*` + `src/lib/config.js` + repo index script | +9 new files, 0 edits to existing | none (data only) |
| **W2** | Shell + routing + `/space/*` routes, spaces as read-only dashboards over existing data | `src/main.jsx` (route map only), +12 new | one deploy, all old URLs still work |
| **W3** | Writable: content pipeline, channel rooms, studio desk over Supabase | +6 new, 3 migration files | one deploy + 1 migration |
| **W4** | Ops desk: money, calendar, agent runs, repo health widget | +4 new | one deploy |
| **W5** | Public portfolio space + case studies generated from real deliverables | +3 new | one deploy |

Each wave is independently shippable and independently revertable. Nothing is a big-bang rewrite.

---

## 8. Hard rules

1. **One deploy per wave**, verified on the live URL before the next wave starts.
2. **No secret ever enters `config/`.** Only labels, ids, public URLs.
3. **Old URLs never break:** `/?portal=CODE`, `/?workspace=1`, `/showreel/index.html`.
4. **Every space reads from `config/` or Supabase — never hardcoded lists in JSX.**
5. **Repo size stays under 1 GB.** Big media lives elsewhere.
6. **A repo is archived, never deleted**, until its contents are confirmed duplicated.
7. **Copy rule:** no fabricated numbers anywhere in UI. Real metrics or nothing.
