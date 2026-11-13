# Monarch: Shorts and long-form reference audit

## Deliverables

- [Shorts versus long-form comparative report — Roman Urdu](SHORTS_VS_LONG_FORM_RESEARCH_ROMAN_URDU.md): separate strong/weak examples, the supplied reference archive, visual observations, a conditional original topic proposal and a format-specific measurement plan.
- [Sanitized archive observation ledger](ARCHIVE_OBSERVATION_LEDGER.md): observations covering all 71 image entries, indexed by review number, without the private images or their original filenames.
- [Recomputed channel statistics](evidence_summary.json): non-pooled, capped channel samples calculated from the public metadata receipts. `reference_channel_alternate_snapshot.json` repeats most of the channels in the first reference run; **do not add the two runs together**.

## Critical date and sampling limits

The trusted session date is **2026-11-05 UTC**. The collection runners and Google response dates reported **2026-11-13 UTC** (the earlier research run reported November 12). The disagreement is unresolved. A runner-reported timestamp is exactly that: it does **not** verify that a counter, publication, title, thumbnail or third-party estimate existed on November 5. Filtering a video by publication date does not backdate its views or channel counters.

This refresh deliberately used `2026-11-14T00:00:00Z` as the runner-based discovery/inventory end. It therefore contains post-trusted-date records: they are retained to document what the source returned, **not used as verified November 5 activity**. Comparisons labelled mature select videos published before `2026-10-23T00:00:00Z`, at least 14 days before the end of November 5 UTC; the counters are still from the runner-reported later time. Video age, public upload availability, topics and audiences differ. A few additional examples outside the mature samples are explicitly labelled.

Each channel inventory examines at most four newest playlist pages, stopping after it has at least 150 eligible IDs, and chooses at most the 30 most recent eligible videos in each duration group. The last fetched page may overshoot 150. Public, deleted, private or unavailable uploads are not a complete history. `<=60s` is a conservative Short **candidate**; `61–239s` is ambiguous and `>=4m` is a long-video **proxy**. Eligible square/vertical uploads up to three minutes can be Shorts. No public API field in these receipts establishes each video's actual platform classification.

The original planned 39 search queries returned 3 successes and 36 errors. A bounded retry attempted 4 errors, recovered one and stopped after persistent rate limits. Thus **35 of 39 planned query lanes have no successful result**; in particular, all three explicitly >=20-minute discovery queries failed. Selected archive examples and manual checks do not fill that coverage gap. Searches use US availability and an English relevance hint, neither of which proves audience geography. Search/discovery, archive and chosen channels are not random, do not form a platform census, and cannot yield hit probabilities or causal explanations.

All 71 supplied images were reviewed visually. The current tracked tree contains neither those images, their original internal filenames, the decrypted archive nor the private transfer key. The archive and its inventory were transferred as encrypted, unreferenced GitHub Git blobs; the provider's retention of those blobs is unknown. The explicitly shared Drive download ID was included in the pushed workflow definitions; removing it in a later commit would not erase existing Git history. If the share link was not intended for public access, change its sharing permissions at the provider.

The additional visual pass reviewed 40 publicly served thumbnail variants for 10 selected videos. Those numbered variants are **not verified timed frames**. Sixteen of 22 requested model windows returned descriptions; six failed with HTTP 503. A model description is not verified continuous video/audio playback, a transcript, actual cut timing or audience behaviour. Competitor videos were not continuously watched or listened to. The earlier [research README](../monarch_viral_audit/README.md) records blocked caption probes and the additional limitations of returned page text.

## Public receipts and reproducibility

The JSON data below retain the original collector output and any original date warnings without modification. All counts are source-reported snapshots, not Studio metrics. SHA-256 verifies the saved file against the run's named receipt; it cannot validate the source's clock or factual claims. The separately transcribed [third-party growth-history receipt](growth_historical_receipts.json) records provider-reported October and daily rows, not live or Studio-verified growth.

| File | Runner-reported UTC / run | SHA-256 |
|---|---|---|
| [youtube_refresh.json](youtube_refresh.json) | 2026-11-13 00:52; [run 43340383740](https://github.com/adil-chandio/Monarch.Overall.Work/actions/runs/43340383740), commit `9ab3802` | `65505329c5301bac050fb3edaa03429f42d239440c5164abd57648aab8d9c964` |
| [search_retry.json](search_retry.json) | 2026-11-13 01:06; [run 43340852648](https://github.com/adil-chandio/Monarch.Overall.Work/actions/runs/43340852648), commit `9a0ad50` | `bd4af6cd979c48c6615cfba7615008bfd96ef9729304751fd2f2b960fc398dbd` |
| [visual_media.json](visual_media.json) | 2026-11-13 01:07; [run 43341745993](https://github.com/adil-chandio/Monarch.Overall.Work/actions/runs/43341745993), commit `4a8fc94` | `1488a24e7332f90ea0dcab10ea89fbce3861dcecdeba7f03ee23b9c7b2ebbd0c` |
| [reference_channel_snapshot.json](reference_channel_snapshot.json) | 2026-11-13 01:13; [run 43343093917](https://github.com/adil-chandio/Monarch.Overall.Work/actions/runs/43343093917), commit `f935d5d` | `68e3cc09e11f54c31ee00a62fccea1d7bd747d4e6b0057732e62426e8a916cda` |
| [reference_channel_alternate_snapshot.json](reference_channel_alternate_snapshot.json) | 2026-11-13 01:23; [run 43343831319](https://github.com/adil-chandio/Monarch.Overall.Work/actions/runs/43343831319), commit `e1c59eb` | `1d9c397def872d4e136faddf2529e0a2cd8ab2e797fa806ccf0aba8829ea417a` |

First reference run: 33 name matches, 32 successful inventories and one `playlistNotFound`. The second repeated those targets and added an alternate same-name handle: 34 name matches, 33 successful inventories, one `playlistNotFound`. A name match by itself is not screenshot identity; the second run supplied two exact title matches and a further matching truncated title plus durations for the screenshot's `@OddlyHuma-n`. The similarly named `@OddlyHuman007` is a different, unconfirmed screenshot candidate.

```sh
python3 -m unittest discover -s research/monarch_og_audit/tests -v
python3 -m unittest discover -s research/monarch_viral_audit/tests -v
python3 research/monarch_og_audit/summarize_evidence.py
sha256sum research/monarch_og_audit/{youtube_refresh,search_retry,visual_media,reference_channel_snapshot,reference_channel_alternate_snapshot}.json
```

No credentials are needed for offline verification. Live collectors require preconfigured secrets, quota and working services; results can change and reruns do not remove the clock discrepancy. The workflow files explain their push/path triggers and encrypted transfer mechanism. The earlier [celebrity-POV proposal](../monarch_viral_audit/DEEP_YOUTUBE_NICHE_REPORT_ROMAN_URDU.md) remains a separate, unapproved proposal; this broader two-format research does not itself approve a pivot, upload, or use of any creator's material.
