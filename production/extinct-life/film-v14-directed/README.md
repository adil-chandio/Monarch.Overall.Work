# V14 — forensic-directed full English rebuild

Status: **published full-film V14 review prerelease**. Corrected cloud render/assembly succeeded; sampled encoded review is complete (439 whole-second samples, 300 motion-strip samples, four individual HD samples). All six tests pass. [Download the full film](https://github.com/adil-chandio/Monarch.Overall.Work/releases/download/extinct-life-v14-corrected-42411599346/Extinct_Life_V14_Directed_English_1080p.mp4). See [encoded review and remaining weaknesses](../review-v14/V14-ENCODED-REVIEW.md), `QC.json` and `DELIVERY.json`. Full-film creative acceptance remains **false**: long science holds, a tight/cropped encounter approach and stylised performance remain. No continuous watch/listen or flawless-film certificate is claimed. Existing V13 is unchanged.

## Locked continuity

438.766667 seconds, 13,163 frames, native 1920×1080 at 30 fps. Original eight chapters, script hash, subtitles, original voice assets and timing remain intact. No previous rendered film is used as a plate. Shared original mesh/material/motion assets remain explicitly credited. No new voice selection is needed because the approved narration is retained.

## Actual changes

- `science.mjs`: purpose-built 3D extraction, reference matching, hypothetical control contamination, lineage, complementary proxies, reconstruction boundary, evidence losses and integration. These replace the common vial/notebook routine, not merely its labels. Science views explicitly declare conceptual imagery, no experimental data and non-calibrated scale.
- `direction.mjs`: explicit species shots at naming beats; separate opposite-bank encounter; visible takeoff; water-transport cutaway; closer sample return. This is a mixed operator/observer film, not a claim that every explanatory view is a literal human-eye camera.
- Species camera changes are immediate authored cuts, avoiding a dissolve that eats the short naming beats. Hare/rodent blocking is separated from deer. Rodent has limbs/paws/nose/whiskers rather than only head/body primitives.
- Creature takeoff has earlier vertical clearance and delayed flap deployment, with wing motion anchored nearer the shoulder instead of scaling the entire wing toward the body's origin. This improves the visible launch, not an expert avian-biomechanics certification.
- `worlds.mjs`: narrower/more restrained water, denser ground mesh, cleared animal reading zones, varied illustrative broadleaf/conifer plant forms, distinct encounter hero travel and visible symbolic transport traces.
- `scene.mjs`: leaf inspection stem clears when the leaf enters the hand; original purposeful scoop/page/lens opening actions retained.
- `feature.mjs`: stable 32px labels with placement collision avoidance; persistent 24px qualifiers; no generic lab operator arms in explanatory diagrams; title moved to cleaner sky space; metadata follows actual transition length.
- `full_sound.py`: removes unmotivated paper sounds under abstract diagrams and footsteps under a non-walking sediment cutaway. Original voice and attributed non-repeating score treatment retained. Continuous final-master listening remains a separate gate.

## Validation, not just implementation flags

`render.mjs --stills` covers all 27 stages plus exact species, takeoff and closing frames. At these sampled frames, actor-only ray checks require a majority unobstructed subject and minimum projected subject size. This deliberately does NOT claim complete environmental/grass/text occlusion validation, every-frame subject visibility or expert anatomy.

Visual-source fingerprint binds native QC and final QC to the inspected modules and schedule. Stale inspection or unknown mixed-revision parts fail assembly. The framing correction explicitly permits only hash-sealed base-run shards entirely outside changed stages and outgoing transition dependencies; all eleven overlapping shards must be fresh. See `PATCH-PROVENANCE.json`. The renderer still checks blank output, fixed-length reachable arms, visible palms, shader/page errors and absolute-seek determinism. Unit tests separately lock full script/voice coverage and shot contracts.

The workflow renders all pictures afresh in 48 non-overlapping shards, checks complete decoded frame count and encoded loudness/peaks, then extracts 439 whole-second samples, full-resolution samples and finer motion strips from the actual encoded candidate. It initially creates a **draft** release pending encoded creative review. The corrected candidate has now been published as a review prerelease after the scoped review linked above; this is not full creative sign-off. Technical pass flags are not “zero flaws,” scientific approval, uninterrupted listening or owner acceptance.

## V13 finding disposition

| Finding | Implemented response | Remaining acceptance obligation |
|---|---|---|
| F01 repeated wildlife | Separate encounter blocking/cameras and transport beat | Compare both encoded sequences, including their long tails |
| F02 generic lab gesture | New stage-specific scientific actions; generic arms removed | Comprehension review of action/result chains |
| F03 small evidence | Closer scientific camera and enlarged macro fragments | Final-size/mobile reading review |
| F04 species readability | Explicit distinct shots, separated hare/rodent, sampled size/occlusion gates | Encoded naming-beat inspection |
| F05 hidden takeoff | Opposite-bank shot, earlier clearance and shoulder-relative flap | Continuous launch review, not only a still |
| F06 annotations without actions | Explicit shot contracts and stage-specific operations | Compare every narrative beat against visible consequence |
| F07 low-information holds | Internal changes in comparisons/controls/losses, transport cutaway | Whole-film pacing review; no measured audience-retention claim |
| F08 scale confusion | Persistent conceptual/reconstruction qualifiers | Check viewers can distinguish illustration from specimen/data |
| F09 soil abstraction | Burial progression and protected/unprotected illustrative traces | Domain-science and diagram-comprehension review |
| F10 weak comparisons | Distinct reference/control/lineage/proxy/gap/integration worlds | No actual assay, taxon certainty, proportions or counts implied |
| F11 obstructing trunk | Specific inspection stem cleared after lift | Encoded 59–64 sec inspection |
| F12 label issues | Stable larger labels, contrast backing, collision placement, persistent qualifiers | Text/subject overlap and final-size reading review |
| F13 procedural environment | Water/terrain/plant-form changes; deliberately stylised | Art-direction consistency review; not photorealism |
| F14 performance | New blocking, rodent details and revised goose flap/clearance | Remaining gait/contact/anatomy limitations are NOT declared solved |
| F15 floating POV | Purposeful mixed observer/operator modes; unnecessary lab arms removed | Camera comfort and transition continuity |
| F16 easing/contact | Revised leaf descent and takeoff clearance | Targeted trajectory/contact playback; not general physics certification |
| F17 transitions | Declared transition length honoured, species opening not blended | Encoded boundary/brightness review |
| F18 ending | Closer, smaller sediment sample and clearer title hierarchy | Emotional payoff review, not an objective quality score |

## Commands

```sh
node production/extinct-life/film-v14-directed/render.mjs --stills
.venv/bin/python -m unittest discover -s tests -p test_extinct_v14_directed.py -v
# Full mix/render/assemble: .github/workflows/extinct-v14-directed.yml
```

Local proof audio may be narration-only while working; it is not the final scored master. `DELIVERY.json` and final `QC.json` are generated only by successful assembly, never copied from V13.
