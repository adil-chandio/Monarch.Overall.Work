# Multilingual YouTube investigation

This folder contains the reproducible, nonrandom evidence behind an editorial language decision. It does not contain credentials, private analytics, user screenshots, comments, subtitle files, or downloaded videos. The preceding comparison remains in `../monarch_og_audit/`.

The collection plan covers native-script/phrased searches in 17 languages: English, Hindi, Spanish, Portuguese, Urdu, Arabic, Indonesian, French, German, Japanese, Bengali, Turkish, Italian, Chinese, Russian, Korean and Tamil. One common engineering question, two API duration filters and six additional recent-query lanes result in 46 planned searches. The search API's `short` means **under four minutes**, not necessarily a Short; later analysis uses ≤60 seconds as a conservative candidate and ≥4 minutes as a long-form proxy. 61–239 seconds remain explicitly ambiguous. Successful search queries, failed queries, and circuit-skipped queries must all be counted separately; 46 planned does not imply 46 successful.

The channel list is intentionally selected, supplemented with at most one small-channel, winner-selected result per search language. Selected recent upload playlists are bounded to at most four pages; platform-wide distributions and success rates cannot be inferred. Sample medians, highs and lows are sorted **within a channel and format**, with videos published before `2026-10-23T00:00:00Z`; the trusted session date is November 5 and all retained videos are published before November 6 UTC. Language codes and native search terms indicate relevance only; actual narration language is not independently established without playback or other reliable corroboration. A regional search does not establish audience country.

**Clock warning:** the actual runner and API server have reported November 13 while the trusted session date is November 5. Public counters and metadata cannot be backdated, even when publication is before November 6; they are runner-reported observations, not verified November 5 numbers. No as-of-now growth, velocity, historical numbers or causation may be inferred from them. Channel subscriber numbers are rounded. A sample cannot prove which channel is actively growing without dated comparable historical receipts.

To re-run locally where an authorized YouTube Data API key is already available:

```sh
python -m unittest discover -s research/monarch_language_audit/tests -v
YOUTUBE_API_KEY="$YOUTUBE_API_KEY" python research/monarch_language_audit/multilingual_youtube.py --output /tmp/language-youtube.json
```

No key should ever be printed or checked in. API errors cause bounded retries and circuit-skipped receipts, not silent success. The on-branch GitHub Actions workflow reads the existing configured secret and transfers only public metadata as a checksum-verified Git blob; this blob is public and GitHub's retention of it is not guaranteed to be short.
