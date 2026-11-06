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
  test_offline.py 104 assertions, no network required
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

1. **Comment mining — implemented and live (2026-11-03).** `yt_intel comments <id>`:
   `commentThreads` (1 unit/page, up to 100 comments), mined into three actionable buckets
   — what the audience *asked for* (sequel / sibling topic / which tool), what they
   *objected to* (did not work / cost / pacing), and what asset they *wanted* (file,
   template, course). Deliberately phrase-led, not sentiment-scored: "sentiment 0.62"
   cannot be written into a script, "9 of 100 asked for part 2" can.
   First real run: 100 comments from a step-by-step automation video →
   `wants to buy time/teaching (6%) is the conversion surface`. Two corrections came out of
   it: a **2.5% floor** (one comment in a hundred was being reported as "the loudest
   objection"), and the picker now prefers how-to intent over raw comment volume, because
   the first pick was an entertainment video whose top comments were jokes.
2. **Live validation** — solved for the API side: GitHub Actions runs now execute the whole
   pipeline with a real key (`doctor` 4/4 PASS, 6 topics, comment mining). The *keyless*
   parsers (`_rich_grid`, `_from_lockup`) remain validated only through CI's web-lane runs,
   which do work, but they are now the fallback rather than the main path.
3. **Transcript reliability** — depends on captions existing and on yt-dlp's signature
   work keeping up. `transcript_status` says `auto` vs `manual` vs `no_captions`, and that
   must never be collapsed into "ok".
4. **`style.py` cut detection — two wrong answers before the right question.** This one is
   worth reading in full, because the first correction was *confidently wrong*.

   The threshold was 0.22, tuned on one 36-second film. Synthetic fixtures with known shot
   lists (0, 3, 7 and 19 cuts) said 0.22 under-counted (6 of 7, 15 of 19) and that 0.14 was
   exact on all four. That shipped — and then real graded footage disagreed:

   | threshold | synthetic fixtures | **real graded master** (5 known hard cuts) |
   |---|---|---|
   | 0.22 (original) | 2 of 7/15/19 … under-counts | **0 of 5** |
   | 0.14 (first fix) | 4/4 exact | **4 of 5** |
   | 0.10 (shipped) | 4/4 exact | **5 of 5**, 2 false positives |

   The graded fixture is six real segments of our own master concatenated with hard cuts —
   real footage, real grade, exact ground truth. Solid-colour shots are the easiest case that
   exists, so a synthetic-only calibration is a *necessary* check that can still be very wrong.

   **The deeper finding, which no threshold can fix:** on this film a real cut can carry a
   *lower* frame delta (0.074) than a whip-pan or flash that is not a cut (peak 0.406). The
   ranges overlap. There is no single absolute number that separates them, so `analyse()` now
   reports a second opinion (`adaptive_cuts`, local-spike detection) beside the primary count,
   with a `cut_agreement` verdict. On our master: 11 primary, 16 adaptive, **"the two methods
   disagree — treat cuts_per_minute as a range, not a number"**. Two detectors that disagree is
   information; one detector is a guess with a decimal point.

   **Still open:** dissolves and fades are not detected by either method, and a film graded per
   scene will need the threshold re-derived from its own footage.
5. **Thumbnail forensics — live, and it found two bugs in itself.** `thumbprint.py` had never
   seen a real thumbnail until a CI step was added for it (`scripts/thumbnails.py` →
   `public/yt-intel/thumbnails.json`); `i.ytimg.com` is TLS-blocked in the agent's sandbox, and
   the module correctly reported `unavailable` rather than inventing a profile. On 12 real
   thumbnails from the newest measured topic:

   - the "dominant colour" was near-black in 10 of 12 (`#0c1213`, `#080c0c`, …) — a biggest-RGB-cube
     vote that near-black wins in every thumbnail ever made. Now hue-clustered, 15° bins, luma
     floor, 4% cluster minimum.
   - `hue_families` listed 22° and 7° as different families with 6 each, totalling 22 over a
     12-thumbnail sample. Now bucketed, then named; the totals must partition the sample.
   - the current read: `face-led: people are the product; house colour is red (6/12)`.
6. **Multi-country trending** — keyless trending pages differ per region; not implemented.
7. **Scheduled research** — the workflow runs (`.github/workflows/yt-intel.yml`, Mondays
   04:00 UTC, plus push on `yt-intel-trigger.txt`) and now executes the **API lane**: exact
   view/like/comment counts, ISO publish times, quota accounting, and comment mining. Every
   run writes `public/yt-intel/lanes.json` (lane, key presence, which secret name, quota
   used) so the state of the pipeline is readable from the repo rather than from a log.
8. **Age handling, and what a young sample is allowed to say.** `--order date` ran for the
   first time and produced a report where every row had `age_days: 0` and `vph: None`: ISO
   timestamps were truncated to whole dates, so a video published at 19:28 today was exactly
   0.0 days old, and `vph` treats zero as "no age". The one search order whose entire purpose
   is velocity had a blank velocity column.

   With sub-day ages, the same report then contradicted itself out loud — the saturation
   reading said "too young to judge" while the decision said `SHARPEN 62.2` at confidence 0.75.
   Three separate faults, all now fixed and pinned:

   - `vph` refuses ages under 6 hours: a two-hour-old video "doing" 400 views/hour is a spike,
     not a rate.
   - youngness is read from `median_age_days < 14`, not from a low view count. The guard used
     to require `median_views < 100`, and the live sample's median was 238 — so it slipped
     through by having slightly too many views to look suspicious.
   - a young sample's winnability is a **placeholder of 50**, it is excluded from the
     confidence figure, and it is narrated as "could not be measured" — never as "a few videos
     already own this topic", which is a claim about a market nobody has measured.

   Live effect on the same topic: `SHARPEN 62.2 @ 0.75` → `NO 49-51 @ 0.5-0.6`.

8. **`search.list` order** — every report so far is relevance-ordered, which is why a
   2-year-old video can sit at rank 3 in a "2026" topic. `--order date` and
   `--order viewCount` exist and must be run to read fresh-wave velocity rather than
   all-time authority.

---

## 5. First run to do on a connected machine

```bash
export YOUTUBE_API_KEY=...        # free, Google Cloud console, YouTube Data API v3
python -m yt_intel lanes          # expect: lane api, quota 10000
python -m yt_intel.test_offline   # 104 assertions, no network
python -m yt_intel topic "ai video editing" --limit 30 --json public/yt-intel/ai-video-editing.json
node scripts/yt-index.mjs         # rebuild the index the UI reads
python scripts/thumbnails.py   # needs a network that serves i.ytimg.com
python -m yt_intel.calibrate_style  # cut-detector calibration on synthetic films
python -m yt_intel style reference.mp4 --compare deliverables/MON-DEMO26_Proof_Over_Promises_v3_1080p60_Master.mp4
```

Then open the workspace → **YouTube Automation → Research desk**.
