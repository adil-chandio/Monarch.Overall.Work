# yt_intel — YouTube intelligence, $0, keyless-first

Everything here runs from a laptop with no paid API, no subscription and no extension.
Two access lanes, chosen automatically and printed in every report:

| lane | needs | gives | costs |
|---|---|---|---|
| `api` | a free YouTube Data API key in `YOUTUBE_API_KEY` | exact view/like/comment counts, 50-item search pages, ISO publish times | 100 quota units per search (10,000/day ≈ 99 searches) |
| `web` | nothing | autocomplete demand signals, channel RSS (last 15 uploads, real timestamps), public search-result JSON, thumbnails at 5 sizes, transcripts via yt-dlp | YouTube throttles datacenter IPs — a block is reported, never hidden |

## Commands

```bash
python -m yt_intel lanes                                # which lane, how much quota left
python -m yt_intel demand  "ai video editing" --deep    # is anyone actually asking?
python -m yt_intel topic   "ai video editing" --limit 30 --json out.json
python -m yt_intel channel @mkbhd                       # roster + thumbnail fingerprint
python -m yt_intel reverse dQw4w9WgXcQ                  # teardown a video that won
python -m yt_intel comments dQw4w9WgXcQ                 # mine the comment field (API lane)
python -m yt_intel ideas   "ai video editing"            # trend + evergreen families
python -m yt_intel.test_offline                         # 53 assertions, no network needed
```

## What each module measures

| module | question | method | honest limit |
|---|---|---|---|
| `demand` | is anyone asking? | YouTube autocomplete position, spread, alphabet expansion, Google Trends slope | not search volume; an absent signal scores `None`, not zero |
| `forensic` | who already won, and how? | views-per-hour, concentration (top-3 share), ridge regression of log10(views) on title features, word lift, hook-pattern shares | correlational; refuses to fit below 20 rows |
| `thumbprint` | what do the winning thumbnails do? | skin-tone presence (YCbCr + saturation gate), dominant hue, contrast, text-band edge energy | not face recognition, not OCR — deliberately |
| `reverse` | how was this video built? | transcript → wpm, filler rate, CTA density, reading grade, hook window, structure map, drive mapping, replication plan | transcript depends on captions existing |
| `comments` | what did the audience ask for? | `commentThreads` → phrases for asks (sequel, sibling topic, which tool), objections (did not work, cost, pacing), asset wants | needs the API lane; refuses below 20 comments |
| `ideas` | what should we make? | autocomplete expansion + 12 psychology-grounded structures | every idea carries its own risk |
| `decide` | build it or not? | weighted GO/SHARPEN/NO with receipts, objections, missing signals and a next probe | always returns an objection; never silently optimistic |

## Why it refuses so often

The failure mode of a scraper is not crashing — it is publishing a confident number
derived from nothing. So:

- fewer than 20 rows → **no regression at all**, with the reason printed
- fewer than 15 videos → **no psychology profile** ("astrology with a chart")
- an unreachable autocomplete endpoint → `score: null`, `confidence: 0`, and a note
  saying the signal is *unavailable*, not *zero*
- every decision carries `strongest_against[]` and `next_probe`, even when the verdict is GO

## Files

```
yt_intel/
  http.py        retry/backoff, 1 req/s rate limit, disk cache (deterministic reruns)
  client.py      the only module that talks to YouTube; API + keyless lanes; quota budget
  demand.py      autocomplete, alphabet expansion, intent, Google Trends, scoring
  forensic.py    saturation, title regression, word lift, hook patterns, psychology map
  thumbprint.py  thumbnail image statistics + channel fingerprint
  reverse.py     teardown of a winning video
  decide.py      greenlight decision with objections
  ideas.py       idea families + WTF bank
  cli.py         every command above
  test_offline.py  53 assertions, no network
```
