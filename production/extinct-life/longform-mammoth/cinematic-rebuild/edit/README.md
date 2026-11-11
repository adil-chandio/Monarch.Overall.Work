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
placed. `check_coverage.py` reports overlapping candidate windows instead of aborting
and measures coverage as the union of verified windows. The current union is
**761.3 s of 796.0 s**, leaving ~35 s with no picture.

The island-seasons insert adds a low wind bed from the existing candidate recording;
its provenance and the unverified master identity are recorded in
`../ambience-sources/README.md`. It has not been auditioned. The `ledger-section` insert (689–759 s) and the `new-lead-section` insert
(652–689 s) carry no original sound design either: it is an evidence ladder for the 2025 microbial
study, ending on an empty rung rather than a culprit. The coat-section insert
uses the shared narration draft only, with no original sound design.

## Continuous environment passage (354–384s)

`build_environment.py` joins the 16-second water inference with the 14-second labelled rain-on-snow hypothesis and places the original narration/score continuously across the cut. A candidate Washington brook derivative fades out across the cut as a candidate Brazil rain derivative leads into the second shot. Neither recording is an Arctic field recording, and both are unreviewed and source-master equivalence remains unresolved. See `../ambience-sources/brook-candidate/README.md`, `../ambience-sources/README.md` and the scene READMEs. The 30-second joined file overlaps the two standalone insert windows and is **not additional coverage**. `check_environment_sync.py` compares three short decoded waveform windows against the source audio, which does not replace human review.

```
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_environment.py
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/check_environment_sync.py
```
