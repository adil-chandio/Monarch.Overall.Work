# Retrieval record, selection, and remaining limits

## Data routes actually used

1. **Public metadata via the existing GitHub secret-backed API workflow.** Local API credentials were unavailable; no credentials were requested, exposed, or placed in files. `scripts/expand-extinct-script-corpus.py` ran in Actions run 42163876846, succeeded, and committed the public derivatives in `15f698c`. The local branch fast-forwarded to recover them.
2. **Bounded discovery.** Six topic/channel searches plus eleven publisher-title searches, at most ten results each; 22 explicit IDs already observed on public pages/catalogue; and the first 100 ≥8-minute entries from the old catalogue. IDs were deduplicated before refreshing video and channel records. Queries are relevance-ordered, not a complete channel crawl or a representative random sample.
3. **Manual modern-script inspection.** Public watch pages sometimes returned transcript prose, sometimes normal navigation/metadata, and sometimes a 401/player error. Normal English-language watch pages and normal short links recovered actual prose for many missing sections. Region/language page variants also sometimes returned prose. These are ordinary public pages, not credential bypasses. A metadata response was never counted as script inspection.
4. **Public publisher text.** PBS episode pages expose transcripts and official caption links. Earlier chunks on older pages contained many recommendations, so the actual script began much later. Reading navigation did not count as reading the script.
5. **Official caption-text alternative.** For the four initially unread Pangea programs, the page's actual official `.txt` caption link was followed. All three chunks of P07 and all four chunks each of P08/P09/P11 were read through. This avoided repeatedly scrolling recommendation-heavy pages.
6. **Timed derivatives.** The collector used the repository's existing normal public-caption module with two concurrent publisher requests, no video downloads, and no raw-caption publication. All eleven new tracks returned timed-caption status. The manually authored beat lists were written separately after prose inspection.

## Per-route inspection facts

| Case(s) | Actual prose inspected | Remaining gap |
|---|---|---|
| M01/M02/M03 | All three prose chunks, assembled across ordinary watch/English/short-link routes | None in the retrieved public text; no AV/timing inspection |
| M04 | Prose 0,1,4 first; then 2,3,6; final missing 5 recovered from short-link English route | None in the retrieved public text |
| M05 | Prose 0 first; 1–4 recovered from short-link English route | None in the retrieved public text |
| M06 | Prose 0 first; 1–3 recovered from English watch route | None in the retrieved public text |
| M07 | Opening prose 0 via English watch; 1–2 via short link | None in the retrieved public text |
| M08 | Prose 0 and 2 only | Middle remains missing; chapter titles are not used as substitutes |
| P01/P02/P03 | Main page prose 2–3 | None in the retrieved main text |
| P04 | Main page prose 1–3; official text ending independently checked | Publisher text ends mid-sentence; not labeled complete |
| P05/P06 | Main prose late 4 and 5, after navigation-heavy chunks | None in the retrieved main text |
| P07 | Official linked text 0–2 | None in the retrieved text |
| P08/P09/P11 | Official linked text 0–3 | None in the retrieved text |
| P10 | Main page prose 1–4 | None in the retrieved main text |

The public fetch service sometimes normalized a requested chunk index to a different returned chunk. The table counts returned actual prose, **not requested indices**. Complete means the retrieved narrative text was inspected through its ending; it does not mean an independently verified official screenplay, a perfect transcription, or that every spoken filler word was captured.

## Performance and edition identity

- Exact ID matching supports the eight modern videos' saved public metrics. Each exceeds one million views in that snapshot. Only seven have complete text inspection.
- Publisher-title API searches produced **candidate** YouTube matches. The collector explicitly labels edition identity unverified. Search rank alone is not a match.
- P01's related dodo upload has a different title/runtime; P10's related PBS clip is 6:14, not 25:37. Neither can inherit the full publisher episode's timing/coverage automatically.
- P03/P04/P05/P06 have same-title leads but different runtimes. These are stronger episode leads, still not evidence of identical edits.
- P04/P05 leads are below one million views. P02 and the long Pangea cuts have no confidently validated like-for-like viral match here. They are craft controls/comparators, not falsely promoted successes.
- The 252 refreshed video records include discovery results of different formats and relevance. They are not all long-form, niche-qualified, successful, or manually read.
- A single video/channel snapshot is not a growth series. Subscribers are not unique viewers. Public views do not reveal audience geography, RPM, retention, CTR, or revenue.
- The choice of already successful contemporary examples introduces survivorship bias. No causal uplift or optimal-hook-frequency statistic is estimated from this packet.

## Timing/visual limits

- Modern prose is untimed. Public chapter links are author-supplied navigation, not manually observed edit points.
- New publisher tracks have cue timing, but the new manual beats are **not** mapped to cue boundaries. Cue hashes/word counts/keywords do not prove semantic coverage.
- The older DNA/whales packet retains its own cue-aligned coding. Its precision is not silently generalized to all nineteen new cases.
- No audiovisual playback review occurred. Soundtrack, acting, cut rate, motion, transitions, and performance cannot be inferred with certainty from text.
- Labels such as plausible engagement function are analytical interpretations. They are not viewer-study outcomes.

## Science and copyright limits

Competitor scripts are craft evidence, not sources of automatic scientific truth. The cases identify risky claims and internal mismatches; a full primary-paper fact-check of every animal trait remains outside this pass. Our film's actual claims still require the science ledger.

Full third-party scripts were not saved or redistributed. Caption data preserve derived features and hashes with only brief opening excerpts. The nineteen studies and 267 beats are original commentary, not rewritten replacement transcripts.

## Build and validation

- Build the register/individual files with `python scripts/build-expanded-forensics.py`.
- Run `python -m unittest discover -s tests -p 'test_expanded_forensics.py' -v`.
- Also run the existing `python production/extinct-life/script-lab/test_packet.py` so the earlier master, bilingual pairs, evidence packet, and render hold remain intact.
- Validation executed successfully on 2026-11-06: **7 expanded-packet tests + 11 existing packet tests = 18 passing tests**; both new research Python scripts compiled; `git diff --check` passed. Rebuilding the 19 individual files and register was byte-for-byte reproducible.
- Automated checks establish structure/provenance/count consistency, not scientific correctness, entertainment quality, retention, or film completion.
