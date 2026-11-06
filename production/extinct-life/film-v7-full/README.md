# Extinct Life — full enhanced English moving-3D master

## Scope

This is the **complete approved 13,163-frame / 438.766667-second English master**, not another selected 61-second development clip. It preserves the approved 1,048-word script, voice-02 assets, chapter timing, 1920×1080 and 30 fps. No new narration, hidden speed changes, V5 generated scene plates, stock-video substitute or reuse of an earlier rendered movie.

Implementation/source is not itself a delivered film. Until the new workflow completes and creates `DELIVERY.json`, a finished export must **not** be claimed. On successful export, the MP4 is a full-master **creative-review candidate**, not a guarantee of perfection, a measured threefold improvement, expert anatomy, enjoyment or retention.

## What changed across the full story

25 continuous stages follow the narration, rather than cutting on all 58 planning beats. `coverage.json` maps planning intervals to implementation; interval coverage is **not** a claim that all artistic/scientific tasks have been independently validated.

| Story purpose | Actual authored moving-3D setup/action |
|---|---|
| Opening living trace | Improved stance-locked mastodon; cleared camera/subject corridor instead of foreground branches across its face |
| Broken DNA | Separate short, broken schematic ladder fragments; never assembled into a full genome |
| Formation and earlier plant clues | Undulating layered exposure, embedded leaf-remain illustration and separated sample carrier; not the later accumulating-section set |
| Sample/question | Closed sediment sleeve sliding into its cradle; not a replay of the later pipette transfer |
| Shedding / transport / burial | Biological-material marker, river advection, surface landing, scattered transport markers, distinct deposited cohorts and deposit-age bracket |
| Survival / binding | Breakage and selective loss; cold slows illustrative motion without restoring lost material; separate mineral-lamella set with fragments settling onto the surface |
| Extraction | Vessel, pipette travel, transfer and receiver; illustrative procedure, not a calibrated protocol |
| Identification | Candidate alignment, shared reference stretches and an explicitly empty reference slot |
| Alternative explanations | A separate clean-hood set, separated material and end-damage check; damage is one check, not proof alone |
| Branch support | A freestanding branching support model; short candidate fragment reaches the shared branch, not an exact-species/genome reconstruction |
| Community | Open wetland terrace, compensated reindeer walk-to-browse, sapling contact pose, independent small-animal action and background mastodon movement |
| Complementary proxies | Physical DNA, pollen and leaf-remain illustrations; visibly different evidence types rather than a claimed complete inventory |
| Imagined encounter | One-way goose takeoff, foot locking, leaves and shore detail; camera follows the complete 39-second traversal, beyond the old excerpt's ~23-second camera schedule |
| Reconstruction limits | Separate incomplete wireframe diorama above material evidence; illustration fades while the evidence foundation remains |
| Missing signals | New physical process-channel model: selective loss, sample bypass and incomplete recognition; no signal is not animal absence |
| Combined incomplete evidence | Independently opening archive drawers, disjoint record types and visible empty space; not another view of the three proxy trays |
| Ending | Necessary return to the shore/sample, interstitial fragments in a granular aggregate, canopy inference and a continuous return to the present coast/incomplete-record title |

The visual review caught and corrected both foreground-tree obstruction and initially repeated bench layouts. A support-node scale error was also caught in native stills and fixed before the final render. Shared materials/rigs/motifs are intentional continuity, **not 25 claimed wholly unique worlds**.

## Sound

`full_sound.py` extends the revised soft-material engine to the **full timeline**, with sequence-relative action cues, distance-conscious restrained foot contacts, rolling sediment textures, water/leaf events and contextual ambience. No phantom pipette drops under the closed sample. No punctuation bleeps, generic transition impacts, 72 Hz contact tones, hard ear-to-ear switching or alleged field recordings.

The full score uses two primary-source, attributed Scott Buckley recordings: **Hiraeth** and **Undertow**. Each selected passage is used once, with a two-second musical crossfade; insufficient source length fails instead of looping or silently substituting a procedural score. `MUSIC-LICENSE.json` records the primary pages and CC-BY 4.0 credits. Both credits must also appear in a YouTube description if the owner later uploads; no YouTube upload is performed here.

Narration-priority mixing retains the broad gentle music EQ, rounded 4.2 kHz foley upper roll-off, 45 ms attack / 350 ms release detector, short click tapers, conservative positive stereo, premaster peak protection and encoded loudness/headroom checks. Voice is not globally muffled to fake softness. Signal checks are **not** human ear-comfort, ASMR or continuous-listening certification.

## Reproducible production / QC

- `python production/extinct-life/film-v7-full/prepare.py`
- `.venv/bin/python -m unittest discover -s tests -p 'test_extinct_v7_full.py' -v`
- `.venv/bin/python production/extinct-life/film-v7-full/finish.py --voice-only` — narration-only work preview, explicitly not the scored export.
- `node production/extinct-life/film-v7-full/render.mjs --stills` — 51 native samples covering every stage, including the final encounter frame; cross-cache deterministic seek and locked-camera subject progression.
- `.github/workflows/extinct-v7-full.yml` — full audio/native preflight; 36 fresh non-overlapping frame shards, capped at 12 concurrent jobs; contiguous coverage audit, original narration mix, full decode, actual encoded audio analysis, attributed GitHub release and persisted QC.
- `finish.py --assemble-only` deliberately reuses the **new run's approved full-master audio artifact**, not a newly improvised mix during assembly.
- `English-v7.srt` is the existing approved full-master subtitle timing/text, preserved verbatim because narration/timing are unchanged; it is not newly invented word alignment.

Generated video/audio/native inspection files stay in ignored `.cache/extinct-v7/` or GitHub artifacts/releases, not Git. Earlier V4/V6 deliveries are preserved, never relabeled as V7.

## Accuracy / acceptance boundaries

Stylized procedural 3D, not photoreal field footage, expert biological/anatomical validation, true fluid simulation, actual sequence reads, calibrated molecular motion or specimen counts. Approximate two-million-year **deposit** age is not direct dating of an individual molecule. No complete genome, cloning, exact appearance, proven co-occurrence, complete inventory, current-oldest-record, claim-free-music or audience-response assertion. Owner creative approval and uninterrupted human watch/listen remain separate from engineering QC.
