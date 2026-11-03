---
name: monarch-yt-intel
description: Decide whether a video is worth making, using YouTube's own public signals — demand, saturation, title maths, thumbnail fingerprints, and a reverse teardown of the videos that already won. Keyless and $0 by default.
license: MIT
---

# monarch-yt-intel

The question is never "is this a good idea". It is **"will this specific video beat the
videos already on this topic, with the assets we have today?"**

That question has an answer you can compute. This skill is the loop.

```bash
python -m yt_intel lanes                              # am I in API or keyless lane?
python -m yt_intel demand  "topic" --deep             # is anyone asking?
python -m yt_intel topic   "topic" --limit 30         # who won, and can we enter?
python -m yt_intel reverse <video_id>                 # how was the winner built?
python -m yt_intel channel @handle                    # their thumbnail grammar
python -m yt_intel ideas   "topic"                    # what to actually make
```

---

## 1. The loop (in this order, never out of order)

| step | command | gate to pass |
|---|---|---|
| 1. Demand | `demand "<topic>"` | score ≥ 50 **with** confidence ≥ 0.5 |
| 2. Saturation | `topic "<topic>" --limit 30` | top-3 share < 70 % (a topic one video owns is a wall) |
| 3. Mechanism | same run | ≥ 2 hook patterns appear in ≥ 30 % of the top quartile |
| 4. Teardown | `reverse <id>` on the top 3 | a replication list that is not empty |
| 5. Decision | `decide` output in the same run | verdict GO or SHARPEN with a named angle |
| 6. Craft | `showreel/ctr` (title, thumbnail, hook) | title ≥ 80, thumbnail ≥ 85, hook ≥ 85 |
| 7. Ship + measure | the same numbers, now on **our** video | compare vph against the topic median |

If a step fails, the loop stops there. Making the video anyway is how a channel fills with
content nobody watches.

---

## 2. What each number means (and what it does not)

**views/hour** — the only fair speed metric across videos of different ages. A 3-year-old
video with 1M views and a 2-week-old video with 400k views are not comparable on totals.

**top-3 share** — concentration. 0.42 means the three biggest videos take 42 % of the
topic's views: entry is feasible. 0.85 means the topic has already been decided.

**winnability** — derived from top-3 share, fresh-upload rate and winner ratio. It answers
"is there room *this month*", not "is the topic big".

**title effects** — a ridge regression of log10(views) on title length, presence of a
number, question form and a shouted word. It reports `strength: firm|weak` and refuses
under 20 rows. Read it as a **prior**, never as proof.

**hook patterns** — the share of the top quartile using each structure. Descriptive.

**Nothing here reports search volume.** The only true volume number lives inside YouTube
analytics. Autocomplete position is an ordered proxy: being suggested at all means real
query volume; rank 1 means it beats everything else starting that way.

---

## 3. Two idea families, deliberately different

| family | source | half-life | risk |
|---|---|---|---|
| **trend** | live autocomplete expansions — things people are typing now | weeks | competition arrives fast |
| **curiosity / evergreen** | 12 structural templates grounded in named cognitive effects | years | needs genuine payoff or it burns trust |

The psychology bank is structural, not clickbait: curiosity gap, schema violation,
belief threat, self-reference, loss framing, hidden mechanism. Each template carries its
`risk` field — an idea list without objections is a brainstorm, not a plan.

**The WTF test.** A hook qualifies only if a stranger would say "wait, what?" and the
answer is *true*. `python -m yt_intel ideas "<topic>"` prints a WTF bank for seeding.

---

## 4. Access lanes (why the tool never lies about a missing signal)

| lane | key needed | same results? |
|---|---|---|
| `api` | free YouTube Data API key | exact view/like counts, 50-item pages |
| `web` | none | autocomplete, RSS (15 latest uploads), public result JSON, thumbnails, transcripts |

A blocked or empty response produces `score: null`, `confidence: 0`, and an explicit note
— **not a zero**. "We could not see it" and "nobody wants it" are different answers, and
confusing them is how a channel kills a good idea.

---

## 5. Etiquette (this is not optional)

- 1 request/second, with backoff. The tool enforces it; do not raise it to scrape faster.
- Cache everything to disk (`YT_INTEL_CACHE`), so re-runs cost nothing and are identical.
- Metadata and text only: **no video or audio downloading**, no re-uploading anyone's work.
- Never publish a competitor's numbers without their capture date.
- Reverse-engineering means learning the *mechanism*. Copying the surface is how clones die.

---

## 6. Files

| purpose | path |
|---|---|
| package | `yt_intel/` (see `yt_intel/README.md`) |
| tests, no network needed | `python -m yt_intel.test_offline` (40 assertions) |
| where results should land | `public/yt-intel/<topic>.json` |
| downstream craft gates | `showreel/ctr` (title, thumbnail, hook) |
