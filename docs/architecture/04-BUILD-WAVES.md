# Build Waves — how this gets built without breaking anything

Five waves. Each one ships, gets verified on the live URL, then the next one starts.
No wave requires the previous wave to be perfect — only deployed and reachable.

---

## W1 — Foundation (data + docs), zero UI change

**Ships:** `config/spaces.json`, `channels.json`, `social.json`, `repos.json`, `services.json`, `payment-rails.json`, `src/lib/config.js`, these docs.

**Why first:** every later screen reads from config. If lists stay hardcoded in JSX, the fifth space always drifts from the first.

**Verify:** `npm run build` passes, live site unchanged, `node scripts/audit-repos.mjs` prints the repo table.

**Risk:** none. No route, no UI, no DB change.

---

## W2 — Shell + 5 read-only spaces

**Ships:** `src/shell/Shell.jsx`, `RouteMap.js`, `CommandPalette.jsx`, five `SpaceHome.jsx` screens rendering **existing** data (Supabase + config), route `/space/:id`.

**Not in W2:** any write action. Spaces display; they do not edit.

**Verify:**
- `/space/yt-automation` shows the 3 channels from config
- `/space/monarch-studio` shows real `client_inquiries` / `client_portals` rows
- `?portal=MON-DEMO26` still opens the live portal, unchanged
- `?workspace=1` still opens the founder workspace
- `Ctrl+K` finds a task, a content item and a portal code

**Risk:** moderate — touches routing. Mitigation: route map is a single file; old routes handled first in `parseRouteFromLocation`.

---

## W3 — Writable pipelines

**Ships:** factory board with drag-between-stages, channel rooms with script/hook/thumbnail panels, studio client desk with portal creation, migration `202611100001_space_ids.sql`.

**Verify:** create a content item → move it through 3 stages → refresh → state persists (Supabase, not localStorage). Create a portal in `unpaid` state → confirm clean-master URL is not exposed.

**Risk:** moderate — first write path. Mitigation: keep `workspace_state` sync untouched; new writes go to dedicated tables.

---

## W4 — Ops desk

**Ships:** `MoneyDesk`, cross-space task board, calendar, agent run log, repo health widget reading `config/repos.json` + `github_repos` table.

**Verify:** money desk shows only aggregate + per-portal status, never a client's full payment detail on the public route.

**Risk:** low — reads only.

---

## W5 — Portfolio space + case studies

**Ships:** `/space/portfolio`, case-study template driven by real portal + deliverable rows, SEO/OG tags per case study.

**Verify:** every case study links to a real portal code or a real file. Zero invented clients.

**Risk:** low — new routes only.

---

> **Status (2026-11-03):** W1 done, **W2 done** (`9ec3b55` — space shell, deep links,
> ⌘K), **W3 partially done** (`dc26a09` + `96b348c…` — research desk: demand → saturation →
> mechanism → verdict, backed by `yt_intel/`; the desk now runs unattended in CI and holds six
> real topic reports), W5 partially done (`09a73cb` — proof surface). See
> [`05-SPACES-OPERATING-MODEL.md`](./05-SPACES-OPERATING-MODEL.md) for the as-built model
> and the concrete W3 scope.
>
> **What the research desk actually proves today:** the pipeline is real (a scheduled run
> fetches, measures, decides, commits and indexes — run `41652813373` onward, all steps
> green), and each card shows its verdict *with* confidence, median views and views/hour.
> What it does **not** yet prove: anything from the Data API lane. No `YOUTUBE_API_KEY` has
> ever been present, so exact view counts, comment mining and quota accounting are written
> and unit-tested but have never been executed against Google. That is one secret away, and
> `docs/setup/YOUTUBE-API-KEY.md` is the five-minute path.

## Definition of done (per wave)

- [ ] `npm run build` clean
- [ ] deployed and reachable on the live URL
- [ ] all pre-existing URLs still work (`/`, `/?portal=`, `/?workspace=1`, `/showreel/`)
- [ ] no fabricated number anywhere in the UI
- [ ] the wave's own verify list, checked by hand, not assumed
- [ ] committed with a message naming the wave

## Rollback

Every wave is a commit range. Rolling back = redeploy the previous commit. No wave deletes a table or a route, so rollback never loses data.
