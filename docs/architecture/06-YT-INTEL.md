# 06 — YT Intel, as built

The research desk on `yt-automation` is not a dashboard with mock data. It is a Python
package, a CI job, a committed report format and one small JSON file the UI reads. This
document is the system as it actually runs on 2026-11-04, including what is proven and what
is still borrowed confidence.

Related: [`../setup/YOUTUBE-API-KEY.md`](../setup/YOUTUBE-API-KEY.md) (the key, in Roman
Urdu), [`../repo-intel/YT-INTEL-FORENSICS.md`](../repo-intel/YT-INTEL-FORENSICS.md)
(measurement rigour and the honest limits of each metric).

---

## 1. The shape

```
YOUTUBE_API_KEY?  ──►  client.py  ──►  forensic.py / demand.py / thumbprint.py / reverse.py / style.py
   (or keyless)          │                         │
                         │                         ▼
                         │                   decide.py  (GO / SHARPEN / NO / RETRY)
                         ▼                         │
              public/yt-intel/<slug>.json  ◄────────┘
                         │
                  scripts/yt-index.mjs  ──►  public/yt-intel/index.json  ──►  src/Spaces.jsx
```

Two access lanes, chosen at runtime and printed in every report:

| lane | needs | gives |
|---|---|---|
| `api` | `YOUTUBE_API_KEY` (free, 10k units/day) | exact views/likes/comments, 50-item search pages, ISO publish times, `commentThreads` |
| `web` | nothing | autocomplete demand, channel RSS, public search-result JSON, thumbnails, transcripts via yt-dlp |

`lanes.json` in the reports folder records which lane the last CI run actually used. The UI
renders that as a badge, so a keyless run can never look like a keyed one.

---

## 2. What runs, and where

| trigger | what happens |
|---|---|
| push touching `yt-intel-trigger.txt` | line 1 = topic (blank = queue), line 2 = search filter, line 3+ = comments |
| `workflow_dispatch` | same, with `topic` / `limit` / `order` inputs |
| Mondays 04:00 UTC | walks `config/topic-queue.json`, capped by `max_per_run` (4) and by quota |

Steps, in order: offline self-test (75 assertions, no network) → resolve key secret →
lane → `doctor` → run plan → research → comment mining → record lane → rebuild index →
artifact → commit.

The queue **rotates**: the least-recently-measured topic goes first, so a cap smaller than
the queue cannot starve the tail. (Before this, the bottom two topics had never been
measured once.)

---

## 3. The report format

One file per topic at `public/yt-intel/<slug>.json`. Keys that matter:

| key | meaning |
|---|---|
| `lane`, `order`, `fetched_at` | how and when this was asked for. Never inferred from the clock. |
| `rows[]` | one row per video; on the API lane it carries `views`, `likes`, `comments`, `tags`, ISO `published` |
| `saturation` | top-3 share, winner ratio, fresh share, median, one-line reading |
| `title_signal` | ridge regression on title features; `insufficient` below 20 rows |
| `decision` | `verdict`, `score`, `confidence`, `parts`, `strongest_for`, `strongest_against`, `missing`, `next_probe` |

`RETRY` is not a verdict about the topic. It means the sample never arrived (throttled IP, no
key, blocked network). It is structurally separate from `NO` because those two conclusions
come from identical empty data and imply opposite actions.

A retry never overwrites a measured report: `scripts/yt-queue.mjs` keeps the previous
measurement and records `kept_previous` in the ledger.

---

## 4. What the numbers are worth

Four things the tool refuses to do, each because it was caught doing it once:

1. **Fit a regression on a small sample.** `title_signal` returns `insufficient` below 20
   rows. A coefficient fitted on 12 rows is astrology with decimals.
2. **Claim certainty from partial data.** `confidence` divides by the *total* weight, not the
   present weight — normalising by what is present reported 1.00 confidence with two of four
   signals.
3. **Say GO without a mechanism.** GO requires `mechanism ≥ 55`; a topic that scored 70 with
   mechanism 25 was being labelled "a readable mechanism all clear".
4. **Judge concentration on a brand-new sample.** A 16-view median with 100% of the sample
   under 30 days old is a young market, not a crowded one.

Comment mining adds a fifth: **a 2.5% floor**. One comment in a hundred is an anecdote, and
the honest reading is "this comment field cannot brief a video" — which is itself an answer.

---

## 5. Proven vs. borrowed

| thing | status |
|---|---|
| keyless web lane (search, ages, views/hour) | **live** — six topics measured in CI |
| API lane (search, videos, exact counts) | **live** — `doctor` 4/4 PASS, quota spent and tracked |
| index → UI → lane badge | **live** — verified in jsdom, not assumed |
| comment mining | **live** — ran on a 3,768-comment how-to video; reading: 6% want to buy teaching |
| `style.py` cut detection | **calibrated on real graded footage** (5 of 5 known cuts), plus a second opinion it reports as a disagreement rather than hiding |
| `thumbprint.py` on live thumbnails | written, unit-tested, not yet run against a keyed channel pull |
| `reverse.py` transcripts | depends on captions existing; `transcript_status` never collapses to "ok" |
| multi-country trending | not implemented |
| scheduled runs | **live** — weekly, plus push |

Anything not in the "live" rows is a claim with a receipt missing, and the docs say so
wherever the number appears.

---

## 6. Cost

$0. No paid API, no subscription, no extension.

- Data API: 10,000 units/day/project. `search` = 100, `videos`/`channels`/`commentThreads` =
  1. A topic run ≈ 101 units; a 100-comment mine = 1 unit.
- GitHub Actions on a public repo: free, unlimited minutes.
- Cache: `.cache/yt-intel/` makes a repeat query cost 0 units.
