# Script-first rebuild — v2 review packet

The approved 24-second moving 3D style is unchanged. Rendering remains on hold; the old audio/timeline does not narrate the revised master.

## Expanded research follow-up

[Expanded script forensics](../../../docs/research/extinct-script-forensics/expanded/REPORT.md) adds 19 individually decoded actual-text cases (17 complete, two partial), including seven complete contemporary million-view long-form scripts. [Applied workflow](../../../docs/research/extinct-script-forensics/expanded/APPLIED-WORKFLOW.md) maps the new findings against all eight v2 blocks. This is an edit plan, not a silently substituted v3 master or a new narration/render. The canonical v2 remains unchanged pending the next paired revision.

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
