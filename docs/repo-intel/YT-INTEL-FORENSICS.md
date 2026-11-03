# YT Intel — what was studied, what was built, what is still missing

**Date:** 2026-11-03 · **Scope:** YouTube research capability at $0
**Rule applied:** every claim below is either a measurement in this repo or a repo that
was opened and read. Nothing is asserted from memory.

---

## 1. Landscape scan (what exists, what it costs)

GitHub search, sorted by stars, licence checked per repo:

| repo | stars | licence | what it actually is | verdict |
|---|---|---|---|---|
| `jdepoix/youtube-transcript-api` | 8.5k | MIT | transcript fetch, Python API | **pattern adopted** — our `client.transcript()` does the same via yt-dlp's caption endpoint, no extra dependency |
| `ScrapeCreators/social-media-research-skills` | 5.4k | MIT | 14 agent skills for social research **backed by their paid API** | **vendored for method only** — see `skills/social-research-skills/MONARCH-PROVENANCE.md` |
| `ZeroPointRepo/youtube-skills` | 1.2k | MIT | transcript/search skills, also API-keyed | read, not vendored — its value is auth plumbing we do not need |
| `yanhua1010/self-media-content-workflow` | 642 | MIT | content ops templates + review cadence | **vendored** (`skills/self-media-workflow/`) |
| `mitchelljy/Trending-YouTube-Scraper` | 375 | BSD-2 | trending scrape via Data API | superseded — our `client.search()` covers it |
| `drawrowfly/tiktok-scraper` | 5.2k | **none** | TikTok scraping | **rejected: no licence** |

Not available at any price from this network: `vidIQ`, `TubeBuddy`, `Noxinfluencer`,
`Social Blade` — all are web apps (or paid APIs), not libraries. Their *signals* are what
matter, so each one was re-derived from public data instead:

| paid tool signal | how yt_intel gets it, free |
|---|---|
| vidIQ "search volume" | autocomplete position + spread + alphabet expansion (`demand.py`) |
| TubeBuddy "keyword score" | the same, weighted, with confidence and a printed explanation |
| Social Blade "channel growth" | channel RSS (15 latest uploads with real timestamps) → upload cadence + views/hour |
| Noxinfluencer "outlier score" | `forensic.saturation()` — top-3 share, winner ratio, fresh-upload rate |
| thumbnail A/B tools | `thumbprint.py` (colour/face/text-energy) + `showreel/ctr` (feed-size survival) |

---

## 2. What was built

```
yt_intel/
  http.py        1 req/s, backoff, disk cache — a block raises, never returns empty
  client.py      API lane (free key, 10k units/day, budgeted) + keyless lane; quota allocator
  demand.py      autocomplete position/spread/expansion, intent, Trends slope, weighted score
  forensic.py    views/hour, saturation shape, ridge regression on title features,
                 word lift, hook-pattern shares, psychology map
  thumbprint.py  skin-presence gate, dominant hue, contrast, text-band energy, fingerprint
  reverse.py     transcript teardown: wpm, CTA density, reading grade, hook window, replication
  style.py       cut detection, shot lengths, hook cut rate, motion, look, lower-third density
  decide.py      GO / SHARPEN / NO / RETRY with parts, objections, missing signals, next probe
  ideas.py       trend family + 12 evergreen curiosity structures + WTF bank
  cli.py         demand · topic · channel · reverse · style · ideas · lanes
  test_offline.py 68 assertions, no network required
```

### The four verdicts, and why RETRY exists

| verdict | meaning | what you do |
|---|---|---|
| `GO` | demand + entry room + readable mechanism | make it |
| `SHARPEN` | topic is live, angle is not differentiated | change the angle, not the topic |
| `NO` | the numbers do not support a day of production | kill it |
| `RETRY` | **we could not measure** (blocked/throttled) | re-run with an API key or from another network |

`RETRY` was added after the first live run in this sandbox: `youtube.com` is unreachable
here (TLS connection closed), and the tool initially reported `NO` — the same output as
"nobody wants this". Those are opposite conclusions from identical empty data, so they
are now structurally different.

---

## 3. Measurement rigour (the part that is easy to get wrong)

0. **A retry is not a measurement.** When the sample does not arrive (`rate_limited`, no
   key, blocked IP) the report is a `RETRY` stub; the queue now *keeps* the previous
   measured report rather than overwriting a real result with it, and stamps `fetched_at`
   at write time so the index can order reports honestly. The retry itself is recorded in
   `public/yt-intel/queue-runs.jsonl`, which is the audit trail, not the research desk.
1. **Refuse small samples.** `title_signal` returns `insufficient` below 20 rows;
   `funnel`/`psych_profile` below 15. A regression on 12 rows is astrology with decimals.
2. **Ridge penalty scales with n.** A fixed λ=2.0 on standardised data over-shrank a
   120-row sample and under-reported a planted effect by half.
3. **Per-SD → raw units.** Coefficients are per standard deviation; a 0/1 flag has SD 0.5,
   so the naive conversion halves every binary effect. Converted back through `beta/sd`.
4. **Skin-tone test needs a saturation gate.** A plain CbCr test called a neutral bone
   background 65 % "face". Real portraits in the same suite read 1.5–5 %.
5. **Honest absence.** An unreachable autocomplete endpoint scores `None` with
   `confidence: 0` and a printed note — never a middle-of-the-road 50.

---

## 4. Still missing (ranked by how much it costs us)

1. **Comment mining — implemented, unproven.** `yt_intel comments <id>` now exists:
   `commentThreads` (1 unit/page, up to 100 comments), mined into three actionable buckets
   — what the audience *asked for* (sequel / sibling topic / which tool), what they
   *objected to* (did not work / cost / pacing), and what asset they *wanted* (file,
   template, course). Deliberately phrase-led, not sentiment-scored: "sentiment 0.62"
   cannot be written into a script, "9 of 100 asked for part 2" can.
   Not yet run against a live key, and the keyless lane returns `unavailable` rather than
   an empty list — so until the first keyed run, treat the phrase lists as untested
   against real comments (they are unit-tested against synthetic ones).
2. **Live validation in this sandbox** — every network probe here fails with
   `SSL_ERROR_SYSCALL`. The parsers (`_rich_grid`, `_from_lockup`) are written against
   YouTube's 2024+ `lockupViewModel` layout but have not yet seen a real response. First
   run on a normal network must be treated as a shakedown.
3. **Transcript reliability** — depends on captions existing and on yt-dlp's signature
   work keeping up. `transcript_status` says `auto` vs `manual` vs `no_captions`, and that
   must never be collapsed into "ok".
4. **`style.py` thresholds** — `cut_threshold=0.22` on normalised RGB distance was tuned
   on one 36-second film with 3 cuts. It needs calibration against a known-cut-heavy
   reference before its `cuts_per_minute` is quoted anywhere public.
5. **Multi-country trending** — keyless trending pages differ per region; not implemented.
6. **Scheduled research** — the workflow runs (`.github/workflows/yt-intel.yml`, Mondays
   04:00 UTC, plus push on `yt-intel-trigger.txt`) and has produced reports keylessly from
   the keyless web lane. The Data API lane has never executed: no key has been present on
   any run yet, so `quota`, `commentThreads` and the API parsers remain unproven in CI.
7. **`search.list` order** — every report so far is relevance-ordered, which is why a
   2-year-old video can sit at rank 3 in a "2026" topic. `--order date` and
   `--order viewCount` exist and must be run to read fresh-wave velocity rather than
   all-time authority.

---

## 5. First run to do on a connected machine

```bash
export YOUTUBE_API_KEY=...        # free, Google Cloud console, YouTube Data API v3
python -m yt_intel lanes          # expect: lane api, quota 10000
python -m yt_intel.test_offline   # 68 assertions, no network
python -m yt_intel topic "ai video editing" --limit 30 --json public/yt-intel/ai-video-editing.json
node scripts/yt-index.mjs         # rebuild the index the UI reads
python -m yt_intel style reference.mp4 --compare deliverables/MON-DEMO26_Proof_Over_Promises_v3_1080p60_Master.mp4
```

Then open the workspace → **YouTube Automation → Research desk**.
