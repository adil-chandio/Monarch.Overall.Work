# Script-first rebuild — latest text draft v3

## Latest script

- [English master v3](ENGLISH-MASTER-v3.md): new original 1,048-word narration informed by the expanded actual-script studies.
- [Paired owner review v3](OWNER-REVIEW-v3.md): the same story in English and easy Urdu-English, including the scientific limits.
- [Science/change ledger v3](SCIENCE-LEDGER-v3.md): source continuity, metaphors and what changed.
- Canonical paired data: `master-v3.json`; regenerate with `python production/extinct-life/script-lab/build_v3.py`.
- Reading-rate estimate: **6:33–7:29 at 160–140 wpm**, before pauses; **not measured audio**. Urdu duration remains unknown until fresh recording.
- V3 is text only. No fresh VO/render, retention guarantee, or independent listener/bilingual verification is claimed. V2 remains preserved below as a previous draft, not the latest narration.

## Previous v2 review packet

The approved 24-second moving 3D style is unchanged. Rendering remains on hold; the old audio/timeline does not narrate the revised master.

## Expanded research follow-up

[Expanded script forensics](../../../docs/research/extinct-script-forensics/expanded/REPORT.md) adds 19 individually decoded actual-text cases (17 complete, two partial), including seven complete contemporary million-view long-form scripts. [Applied workflow](../../../docs/research/extinct-script-forensics/expanded/APPLIED-WORKFLOW.md) maps the new findings against all eight v2 blocks. That research packet records the edit plan that preceded v3. The paired v3 draft linked above now implements the revision; v2 remains preserved. Neither packet is a new narration or render.

## Read in this order

1. [Forensic report](../../../docs/research/extinct-script-forensics/REPORT.md): evidence, limits, old-script audit and changes.
2. [English master](ENGLISH-MASTER-v2.md): complete original 1,045-word narration.
3. [Same-script easy Urdu-English owner review](OWNER-REVIEW-v2.md): eight faithful passage pairs and manual alignment checks.
4. [Our repeatable workflow](../../../docs/research/extinct-script-forensics/WORKFLOW.md): from supported surprise to measured audiovisual delivery.
5. [Science ledger](SCIENCE-LEDGER.md): thirteen claim IDs and explicit visual restrictions.

`master-v2.json` is canonical. The Markdown readings and `validation.json` are generated from it. No old voice file should be renamed/reused as v2.

## Reproduce offline checks

Run from the repository root:

```sh
python production/extinct-life/script-lab/build_forensics.py
python production/extinct-life/script-lab/build_packet.py
python production/extinct-life/script-lab/test_packet.py
```

Last executed result: **11 tests passed**, plus Python compilation and `git diff --check`. Tests verify evidence coverage, generated-text consistency, counts, known-unknown timing, metadata minimisation, cached blocked-attempt behaviour and the render hold. They do **not** prove engagement, independent translation accuracy, actual voice quality or finished-film quality.

## Honest scope

Completed: two PBS-edition cue-complete textual case studies (260 cues, 36 manual phases, 978 one-second coverage rows), two additional untimed narrative comparisons, old-master audit, workflow and bilingual v2 draft.

Incomplete: actual scripts of the blocked contemporary/growing-channel leads; retention/visual/audio forensic validation; fresh v2 narration and measured timing; phrase-level v2 shot list; seven missing 3D worlds/rigs; finished full film and durable final-video delivery.

The current research script reuses known caption attempts by default. An opt-in public-track refresh never retries known unavailable cases. A metadata/privacy maintenance push must not trigger another unchanged bot-blocked extraction attempt.
