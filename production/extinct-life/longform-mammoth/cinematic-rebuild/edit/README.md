# Film editing — incomplete workprints

The 796.042-second narration has **not** been turned into a complete film. This folder builds six candidate editorial sections and tracks coverage without labelling missing footage as finished. The sources are existing native-3D development footage; no previously rejected slide/recut video is used. The shots remain provisional and are **not** a substitute for the storyboard's missing narrative action. The opening repeats two visual sources, lacks several requested physical actions, and ends mid-story. The same 3D mammoth model appears repeatedly. The hypothesis and genomic-gap inserts are conceptual work, not observation. Caption timing, visual continuity and science are not reviewed. They need substantial animation and edit work.

`opening-cut.json` describes a first-pass 0–85s picture edit with exact frame counts and hash-pinned source render files. `build_opening.py` makes an unapproved 85s A/V workprint using the prior unreviewed narration/score. `build_insert.py` builds five separate inserts at provisional 130s (island life), 172.733s (2017 genome comparison), 354s (water inference), 370s (rain-on-snow hypothesis) and 629.0667s (2024 genomic gap). All output is ignored in `.cache/mammoth-edit/`; it is not a deliverable. The map depicts modern shorelines only; the dig is illustrative and not a Wrangel site. The ice sequence is hypothetical, and the gap is explicitly a gap in the 2024 genetic sample set, not in all evidence. No voice sync has been manually reviewed. Of the standalone inserts, only the water insert includes candidate stream ambience; its source, illustrative location and listening caveats are in `../ambience-sources/brook-candidate/README.md`. Other standalone inserts have no scene-specific SFX. The island-life insert uses a temporary 0.88 gain reduction to meet the true-peak guardrail; its level is not a final mastering decision.

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

## Continuous environment passage (354–384s)

`build_environment.py` joins the 16-second water inference with the 14-second labelled rain-on-snow hypothesis and places the original narration/score continuously across the cut. A candidate Washington brook derivative fades out across the cut as a candidate Brazil rain derivative leads into the second shot. Neither recording is an Arctic field recording, and both are unreviewed and source-master equivalence remains unresolved. See `../ambience-sources/brook-candidate/README.md`, `../ambience-sources/README.md` and the scene READMEs. The 30-second joined file overlaps the two standalone insert windows and is **not additional coverage**. `check_environment_sync.py` compares three short decoded waveform windows against the source audio, which does not replace human review.

```
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_environment.py
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/check_environment_sync.py
```
