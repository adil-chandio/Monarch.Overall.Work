# Film editing — incomplete workprints

The 796.042-second narration has **not** been turned into a complete film. This folder builds seven candidate editorial sections and tracks coverage without labelling missing footage as finished. The sources are existing native-3D development footage; no previously rejected slide/recut video is used. The shots remain provisional and are **not** a substitute for the storyboard's missing narrative action. The opening repeats two visual sources, lacks several requested physical actions, and ends mid-story. The same 3D mammoth model appears repeatedly. The hypothesis and genomic-gap inserts are conceptual work, not observation. Caption timing, visual continuity and science are not reviewed. They need substantial animation and edit work.

`opening-cut.json` describes a first-pass 0–85s picture edit with exact frame counts and hash-pinned source render files. `build_opening.py` makes an unapproved 85s A/V workprint using the prior unreviewed narration/score. `build_insert.py` builds separate inserts at provisional 130s (island approach), 140s (island chapter), 172.733s (2017 genome comparison), 250s (coat section), 354s (water inference), 370s (rain-on-snow hypothesis), 629.0667s (2024 genomic gap) and 783s (closing crossing). All output is ignored in `.cache/mammoth-edit/`; it is not a deliverable. The map depicts modern shorelines only; the dig is illustrative and not a Wrangel site. The ice sequence is hypothetical, and the gap is explicitly a gap in the 2024 genetic sample set, not in all evidence. No voice sync has been manually reviewed. Of the standalone inserts, only the water insert includes candidate stream ambience; its source, illustrative location and listening caveats are in `../ambience-sources/brook-candidate/README.md`. Other standalone inserts have no scene-specific SFX. The island-life insert uses a temporary 0.88 gain reduction to meet the true-peak guardrail; its level is not a final mastering decision.

The scripts require the exact hash-pinned prior rendered clips in the ignored cache, Python `imageio-ffmpeg` and the soundtrack. Some of those files are local and need rerendering from their respective scene directories. The living-world opening shot specifically requires `MAMMOTH_REVIEW_CACHE="$PWD/.cache/living-world-edit" node production/extinct-life/longform-mammoth/cinematic-rebuild/living-world/render-preview.mjs 690`. Hardware/software differences can change rendered hashes, requiring an intentional editorial check and plan update rather than silent replacement. Map/gap renders are produced with their respective `render-preview.mjs`. Run from repository root:

```
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_opening.py
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py island-approach
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py genome-comparison
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py stream
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py hypothesis
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py genomic-gap
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/check_coverage.py
```

Builds perform full FFmpeg decode, frame count, peak and source-hash checks, but **not** continuous listening, audiovisual sign-off, science accuracy, rights clearance or assessment of storytelling quality. `check_coverage.py` counts a segment only if its QC matches the actual cache file. A complete duration is not equivalent to a finished film, and a partial duration must not be distributed as the completed documentary. See each scene's README and the soundtrack/music/asset READMEs for sources, rights uncertainties and required credits. Nothing authorizes YouTube publication.

## Island chapter and coat section (140–170s, 250–274s)

`island-chapter/` is a 60-second, seven-shot sequence in one invented Arctic world,
and it is now placed **twice from disjoint parts of the same render**:

| insert | source range | placed | narration under it |
| --- | --- | --- | --- |
| `island-chapter` | 0.0–30.0 s | 140.0–170.0 s | "Picture an island population…" and the 2019 collagen passage |
| `island-chapter-2` | 30.0–60.0 s | 220.0–250.0 s | premature stop signals, smell-receptor losses, selection, the moving-animal handoff to the coat |

They share no frames. Together they cover 60 s of the sequence against a 60 s
picture requirement, so this is not padding by repetition — but it is also not new
picture, and it does not reduce how much footage still has to be made. The earlier
140.9 s offset left a 0.9 s hole in the coverage union and was corrected to 140.0.

`coat-section/` is 34 seconds in five shots: a macro wool-texture pass, a close
flank, a low leg/weight shot, the herd walking into low sun, and an exit hold. It is
placed at **250.0–274.0 s**, under the FOXQ1 passage and its explicit caveat that the
coat was predicted and never observed. It contains **no researcher, sample tray or
comparison bench** — those subjects have read as toys in this project and were not
attempted here. The macro pass carries its own disclosure line.

`island-years/` covers the opening of the island chapter: a 30-second continuous
move through compressed seasons with three animals on invented terrain. `final-crossing/`
is the 13-second closing motif, ending on a stylised footprint. Both carry their own
README with what is invented; neither has had continuous viewing.

```
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py island-chapter
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py island-chapter-2
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py coat-section
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py island-thaw
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py final-crossing
```

`island-approach` is trimmed to 10 s (130–140 s) where the storyboard asks for a
foraging beat; the island chapter then runs continuously from 140.0 s. `island-thaw`
remains available as an 8-second alternate excerpt of the seasonal study but is not
placed. `check_coverage.py` derives the placed timeline from every `*-qc.json` rather
than a hand-kept table (that table drifted twice and stacked two inserts on one window),
reports overlapping candidate windows instead of aborting, and measures coverage as the
union of verified windows. The current union is **796.0 s of 796.07 s**: the only
uncovered frames are the last two, which carry no narration. There are no overlapping
placements and no repeated source seconds (`.cache/audit_duplicates.py`).

The island-seasons insert adds a low wind bed from the existing candidate recording;
its provenance and the unverified master identity are recorded in
`../ambience-sources/README.md`. It has not been auditioned. The `ledger-section` insert (689–759 s) and the `new-lead-section` insert
(652–689 s) carry no original sound design either: it is an evidence ladder for the 2025 microbial
study, ending on an empty rung rather than a culprit. The coat-section insert
uses the shared narration draft only, with no original sound design.

## Picture balance — the finding from the first assembly

`report_picture_balance.py` measures how much of the covered timeline is printed plate
rather than rendered picture, and how long the plates run without interruption. Current
figures: **307.8 s plate / 488.2 s rendered picture (38.7% plate)**, longest single run
**50.0 s** (684–734 s, the verdict plates). No plate run exceeds 60 s.

Assembly found this; section QC could not. Every plate is individually defensible and
several exist to refuse a misleading image — but a run of them turns a documentary into a
slide sequence. Two fixes have been made: `island-hold/` (473–539 s as native picture, with the
`genetic-strain` trim that followed), then `verdict-close/` at 734–759 s, which let the
ledger stop at 734 s. Then a third pass cut the four remaining over-long runs of paper
(274–354, 391–471, 540–646.1, 652–734) with rendered picture taken from renders already
in the film but not yet on screen. Together they took the share from 68.4% to 38.7% and
the longest run from 173.1 s to 50.0 s. The fix is more native picture, never shorter
plates; the same warning is stated at the top of `../README.md`.

## Continuous review reel

`assemble_review.py` joins every **verified** insert into one narration-locked reel so
the film can be watched end to end for the first time. It is a review artifact, not the
final film and not picture lock.

- 796.07 s, 23882 frames, 1280×720, 30 fps, −16.2 LUFS, −0.8 dBTP, 86.7 MB (CRF 23).
- Every one of the 56 placed segments is verified before assembly: frame count, fps,
  narration offset, audio digest and file digest. An insert that fails is excluded.
- Picture is concatenated from the verified workprints; audio is taken from the single
  continuous narration/score draft, so the voice never restarts or drifts across a cut.
- There is at most one labelled card, for the final two frames past the end of the
  narration. A gap card states its exact range and that narration continues underneath:
  a gap is a gap in the edit, not a held shot.
- The reel is deliberately built from verified QC only; an insert that fails
  `check_coverage.py` cannot enter it.

What this does **not** establish: artistic quality, scientific accuracy, pacing, tone
consistency, or that any section belongs where it sits. Those need a human viewing pass,
which has still not happened. Watching the reel is the next step; the report beside it
(`.cache/mammoth-edit/review-reel-report.json`) records the running order and levels.

```sh
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/assemble_review.py --list
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/assemble_review.py
```

## Continuous environment passage (354–384s)

`build_environment.py` joins the 16-second water inference with the 14-second labelled rain-on-snow hypothesis and places the original narration/score continuously across the cut. A candidate Washington brook derivative fades out across the cut as a candidate Brazil rain derivative leads into the second shot. Neither recording is an Arctic field recording, and both are unreviewed and source-master equivalence remains unresolved. See `../ambience-sources/brook-candidate/README.md`, `../ambience-sources/README.md` and the scene READMEs. The 30-second joined file overlaps the two standalone insert windows and is **not additional coverage**. `check_environment_sync.py` compares three short decoded waveform windows against the source audio, which does not replace human review.

```
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_environment.py
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/check_environment_sync.py
```

## Running order (after the close rebuild)

`--list` prints this from the coverage table, and it is the only description of the film
that is regenerated rather than written by hand:

| | |
|---|---|
| 0–85 | opening |
| 85–86 | post-verdict beat (coat render) |
| 86–114 | isolation |
| 114–130 | other islands |
| 130–140 | island approach |
| 140–170 | island chapter one |
| 170–172.73 | chapter breath (approach render, final second) |
| 172.73–181.73 | 2017 genome comparison |
| 181.73–187 | 2017 cohort (approach render, second excerpt) |
| 187–192.73 | island population's isolation |
| 192.73–220 | gene disruption |
| 220–250 | island chapter two |
| 250–274 | coat |
| 274–278 | the animal itself |
| 278–280 | Arctic conditions |
| 280–311 | one genome |
| 311–319 | two genomes |
| 319–344.5 | chemistry |
| 344.5–351.8 | seasonal stress |
| 351.8–354 | sparse record (coat render, unused tail) |
| 354–369 | environment: water inference into rain-on-snow |
| 369–383 | hypothesis |
| 383–399 | stream |
| 399–401.4 | dating question |
| 401.4–411 | archaeology |
| 411–411.4 | the gap in the record |
| 411.4–431.4 | people |
| 431.4–437 | foraging |
| 437–448 | shore uncertainty |
| 448–450 | proof of innocence |
| 450–455 | three witnesses |
| 455–471 | genome record |
| 471–472 | fourteen Wrangel animals |
| 472–473 | severity lead-in |
| 473–539 | **island hold** |
| 539–540 | comparative stability lead-in |
| 540–557 | genetic strain |
| 557–562 | windows of different sizes |
| 562–579 | coverage |
| 579–603 | trends |
| 603–609 | no clear accelerating collapse |
| 609–617 | trends, second excerpt |
| 617–625 | lasting strain |
| 625–625.2 | neither finding |
| 625.2–636.2 | genomic gap |
| 636.2–638.2 | final ten generations |
| 638.2–650.2 | island extent |
| 650.2–652 | other evidence |
| 652–655 | 2025 specimens |
| 655–657.7 | the missing witness |
| 657.7–660 | the gap is in the dataset |
| 660–676 | new lead |
| 676–684 | authentication and contamination |
| 684–734 | ledger |
| 734–783 | **verdict close** |
| 783–796.07 | final crossing |

`reversal-section` and `verdict-section` are no longer placed. Both were superseded by
native picture doing the same narrative work, and both files are kept for comparison.

## Handing the reel over

**Where the shipped file lives.** `deliverables/Last-Mammoths-Review-Reel-13min-720p.mp4`
is force-added past the `deliverables/*.mp4` ignore rule (as this repository already does
for its other finished cuts) and committed; its build report sits beside it. Nothing else
of this size is committed — the copy in `.cache/` is the working one.

Why a git commit and not a release asset: the development sandbox cannot reach
`uploads.github.com` (TLS is blocked at the network edge), so `gh release upload` dies
with an EOF after sending nothing. `git push` to `github.com` works, so the file travels
inside the repository instead. A runner-hosted publish workflow
(`.github/workflows/publish-mammoth-review-reel.yml`) exists for anyone who wants a
release asset, but it cannot fetch from the sandbox preview either — that preview returns
403 to an outside client.

Verify a copy with:
`sha256sum deliverables/Last-Mammoths-Review-Reel-13min-720p.mp4`
→ `479a30ae59ad2772e918f78da8100ac0390cff57695bb1f177b9e32edac27f63`


`edit/serve_review_reel.py` exists because `python -m http.server` answers a Range
request with the whole 95 MB body and a `200`, which breaks seeking — a player has to
re-download from zero every time you scrub. This server returns `206` with a correct
`Content-Range`, so the reel can be watched and scrubbed in a browser.

```bash
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/serve_review_reel.py 8123
```

Only `review-reel-continuous.mp4` is served, from an explicit allowlist — there is no
directory listing and no path traversal. A plain URL downloads the file; appending
`?inline=1` plays it in place instead. It resolves `.cache/mammoth-edit/` from the repo
root, so the script is committed but the 95 MB reel never is.

**Not for distribution.** The reel is a work-in-progress assembly and the mammoth rig's
rights are unresolved; this exists to get a review copy to a reader, not to publish.
