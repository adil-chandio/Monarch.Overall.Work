# 05 · Spaces operating model (as built)

> This file describes what is actually wired in `src/`, not what is planned. If the code
> and this document disagree, the code is right and this document is a bug.

---

## 1. The five spaces

| Space | Route | Sections | Owns |
|---|---|---|---|
| `yt-automation` | `/?workspace=1&space=yt-automation` | Command deck · Channel studio · Publishing calendar · Idea inbox | the three channel slots, cadence, format specs |
| `monarch-studio` | `…&space=monarch-studio` | Studio deck · Portals & unlock · Client leads · Payment rails · Outreach · Film projects · Skill library | client work, money, delivery |
| `personal-brand` | `…&space=personal-brand` | Identity deck · Social studio · Showcase cuts · Prompt vault | voice, pillars, social accounts |
| `portfolio` | `…&space=portfolio` | Proof surface · Case studies · Asset shelf · Credits | the public proof surface |
| `ops` | `…&space=ops` | Ops deck · Task queue · Knowledge base · Agent library · Vault · Connections · Access | money, tasks, repo health, agents |

Deep links are real: `?space=ops&page=knowledge` opens Ops → Knowledge base on first paint,
with the correct space tab, breadcrumb and selected sidebar item. `history.replaceState`
keeps the URL in sync as you move, so any view can be copied and sent.

---

## 2. The isolation rules (this is the whole point of "intentional separation")

1. **A space may only show its own numbers.** `src/lib/spaces.js` computes counts per space
   from `config/*.json` and the user's own records. Nothing is shared implicitly.
2. **Empty means empty.** Every space home prints the *source* of each figure
   (`config/channels.json`, `table:tasks`, …) and says "not connected yet" rather than
   rendering a zero that looks like performance.
3. **Channels only exist inside `yt-automation`.** `showsChannels(spaceId)` gates the
   sidebar group, so the studio space does not leak the YouTube roster into its navigation.
4. **Money only exists inside `monarch-studio` and `ops`.** Rails, prices and settlement
   never appear on the public or portfolio surfaces.
5. **One collision to resolve, surfaced not hidden.** `config/channels.json` CH-02 carries a
   `conflict_flag` because it overlaps the personal-brand motivational account. The UI
   renders that flag in the channel roster instead of silently running both.

---

## 3. The config → UI contract

Config files use different shapes on purpose (a rail has `label` and no status, a service
sells a price *range*, a social account lists several platforms). The UI never guesses:

```
config/*.json  ──►  src/lib/normalise.js  ──►  rows with one stable shape  ──►  components
                          ▲
                          └── src/lib/normalise.test.mjs  (npm test)
```

`normalise.js` is pure and import-free-by-design, so `npm test` runs it under plain Node
with no bundler, no jsdom and no network. Six tests currently guard:

- price ranges vs single prices vs "quote"
- every channel normalises with a name, handle and a rendered KPI string
- rails split into *usable from Pakistan* vs *cannot onboard*, from
  `unavailable_from_pakistan` — never a hard-coded status
- services always expose a title, a price and a turnaround
- social accounts flatten `platforms[]`
- the repo registry count matches `config/repos.json`

A new config field that the UI needs is therefore a two-line change plus a test, not a
JSX hunt.

---

## 4. Command palette (⌘K / Ctrl-K)

One list, built from live data — not a static menu:

- 5 spaces (home)
- every section of every space (27 entries)
- channels, repos, payment rails, services
- the user's own tasks and content

Keyboard: `↑ ↓` move, `↵` open, `ESC` close. Opening a result navigates *and* rewrites the
URL, so ⌘K is also how you produce a shareable link to any corner of the OS.

---

## 5. Proof surface (Portfolio → Case studies)

The case study is a **reader**, not a slide. It fetches:

| File | Produced by | Rendered as |
|---|---|---|
| `public/showreel/audio_qc.json` | `showreel/audio_qc/gates.py --profile web` | loudness / peak / LRA / movement / mono / clipping rows + the 9 gate chips |
| `public/showreel/ctr_report.json` | `python -m showreel.ctr` | three scored thumbnails, ranked titles, scored hooks |

If either file is absent the panel says *"not measured yet"* and explains how to produce
it. There is no fallback constant. That is the "no fabricated numbers" rule expressed as
code rather than as a promise in a README.

---

## 6. Wave status

| Wave | Scope | State |
|---|---|---|
| W1 | config, docs, registry | **done** |
| W2 | space shell, sections, deep links, ⌘K | **done** (`9ec3b55`) |
| W3 | writable pipelines (upload → analyse → gate → publish) for yt-automation | next |
| W4 | ops money desk + repo health widget | pending |
| W5 | portfolio case studies, SEO/OG per study | **partially done** — proof surface shipped (`09a73cb`), OG tags pending |

### W3 scope (next, concrete)

1. `yt-automation` gets an **upload → QC** lane that calls the same gate code the showreel
   uses (loudness, true peak, mono fold, click detection) before a file can be marked ready.
2. The gate result is written to the record, so a task can never be "done" without a
   measurement.
3. Channel studio shows the last measured KPI per channel slot instead of a placeholder.

### W5 remainder

- OG/Twitter meta per case study, generated at build time from the same JSON.
- One page per shipped deliverable, indexed from `deliverables/`.
