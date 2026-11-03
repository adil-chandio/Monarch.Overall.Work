# Space Operating Model — how each mini space actually runs

Each space has the same skeleton so the app feels consistent, but a different "engine" in the middle.

```
Space
├── 01 Brief        what this space exists to produce
├── 02 Pipeline     the repeatable stages (this is the engine)
├── 03 Assets       where its raw material comes from
├── 04 Scoreboard   the numbers that decide if it is working
└── 05 Agents       the automations allowed to touch it
```

---

## Space 1 — `yt-automation` (YouTube Automation Business)

**Brief:** three faceless channels, run as a factory, not as art projects.

**Channels (configured in `config/channels.json`, not in JSX):**

| Slot | Channel | Niche | Format | Cadence | Primary KPI |
|---|---|---|---|---|---|
| CH-01 | _to be filled_ | e.g. AI/tools explainers | long-form 8–12 min + 3 shorts | 2 uploads/wk | avg view duration ≥ 50% |
| CH-02 | _to be filled_ | e.g. motivation/story | shorts-only | 1/day | swipe-away < 25% |
| CH-03 | _to be filled_ | e.g. documentary/lore | long-form | 1/wk | CTR ≥ 6% |

**Pipeline (the factory board, 8 stages):**
```
IDEA → RESEARCH → HOOK → SCRIPT → VOICE → VISUAL → ASSEMBLY → UPLOAD → (ANALYTICS back to IDEA)
```
Every content item is a row in Supabase `content_items` with `stage` = one of those.
Analytics feeds back: a video that underperforms its channel's median becomes a "post-mortem" card that blocks the next similar idea.

**Assets:** scripts in repo (`config`/DB), voice+video renders in `World-Channel-` (asset-store) or Drive. This repo holds **only the row + the link**.

**Scoreboard:** uploads shipped / week, median retention, swipe-away %, CTR, subs/video. No vanity total-views number.

**Agents allowed:** idea generator (needs human `HAAN` before script), thumbnail variants, caption pass, upload-pack builder. **No auto-publish.**

**Hard rule:** generic stock B-roll as the hero is banned (per `03_VISUAL_OS.md` in `Monarch-Agent`). Faceless ≠ stock spam.

---

## Space 2 — `monarch-studio` (video editing + website development)

**Brief:** the revenue engine. This is the only space allowed to touch money.

**Pipeline (client job, 7 stages):**
```
INQUIRY → SCOPED → (50% advance) → PRODUCTION → WATERMARKED PREVIEW → (settlement) → CLEAN MASTER
```
**Existing implementation:** `client_inquiries` → `client_portals` → `payment_submissions` → `payment_status` (`unpaid` / `proof_submitted` / `verified`).
Portal codes look like `MON-DEMO26`. Rule enforced in code: **clean master URL is never rendered before `verified`.**

**Assets:** `deliverables/` for masters under 45 MB; Drive for anything bigger; `showreel/` for the pipeline that renders them.

**Scoreboard:** open inquiries, average time-to-first-reply, advance collected, verified vs unpaid portals, delivered this month.

**Agents allowed:** intake triage, invoice draft, portal creation, watermark preview render. **Never** a payment verification without the founder.

---

## Space 3 — `personal-brand`

**Brief:** three public identities, each with a different voice and a different audience. They must not blur into one feed.

| Account | Voice | Audience | Content unit | KPI |
|---|---|---|---|---|
| Motivational / youth growth | direct, Roman-Urdu + English, no lecture | 16–25 PK | 30–45s vertical | saves + shares |
| AI / BTS | behind-the-scenes, technical honesty | builders, clients | 20–60s vertical or carousel | profile visits → leads |
| Portfolio / showcase | editorial, sparse | buyers | case-study posts | inbound inquiries |

**Pipeline per account:** `PILLAR → HOOK → BEAT SHEET → CAPTURE → CUT → CAPTION → SCHEDULE → POSTED`.
Pillars are fixed per account (max 4) so the feed never drifts.

**Rule:** one production session → many posts. Never one post per session; that is how accounts die.

**Scoreboard:** posts shipped/week, saves rate, follower growth 30d, inbound DMs that mention a post.

---

## Space 4 — `portfolio`

**Brief:** the public proof surface. Read-only for the public, editable only by you.

**Content:** the showreel, real analytics screenshots (`583,290` views, `92.5%` retention, `80.5%` viewed-vs-swiped), live builds, case studies generated from actually delivered portals.

**Rule:** every case study must map to a real `client_portals` row or a real film file. No invented clients, no invented metrics.

**Scoreboard:** inquiries from portfolio, showreel completion, time on case study.

---

## Space 5 — `ops`

**Brief:** the only space with a cross-cutting view. Everything else is single-domain.

**Contains:** task board across all spaces, money desk (rails, invoices, settlements), calendar (upload days, client deadlines, render nights), agent run log, repo health widget from `config/repos.json`.

**Rule:** ops can read every space. No other space can read ops.

---

## Cross-space contracts

1. **One id space.** A content item, a client portal, and a task all carry a `space_id`.
2. **One decision log.** Every "we will do X" ends up in `knowledge_notes` with a date — otherwise it did not happen.
3. **One approval gate.** Anything that spends money or publishes publicly stops for an explicit `HAAN`.
4. **One scoreboard language.** Numbers are either real or absent. Never estimated, never rounded up for effect.
