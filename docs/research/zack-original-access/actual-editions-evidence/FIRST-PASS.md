# Ten actual Zack D. Films platform editions — evidence-backed FIRST PASS

**Production remains STOPPED. This is a research dossier, not authorization to make a video.**

This document records the FIRST-PASS baseline. Later bounded native/ROI progress and the unresolved audio capability blocker are documented separately in `second-pass/SECOND-PASS.md`; do not add overlapping image counts or interpret this baseline as the latest cumulative coverage.

## What has genuinely happened

- Ten actual MP4s acquired by ordinary public platform retrieval, both audiovisual tracks decoded remotely, then authenticated/checksummed after encrypted local transfer. Workflow: https://github.com/adil-chandio/Monarch.Overall.Work/actions/runs/42438157062
- **9,772 decoded frames** indexed with source presentation timestamps. This is numerical coverage, not 9,772 visually examined frames.
- **342 source image positions across 21 contact sheets opened for visual review**, spanning every second and an extra final frame for each clip. The contact sheets reduce display size. **12 native-resolution stills** additionally inspected for contact/material detail.
- **332 one-second intervals** now have coarse sampled visual notes, plus frame coverage and mixed-track energy measurements. A note describes the near-start image, not everything occurring during that second.
- **0/10 exhaustive manual frame-and-continuous-audio studies completed.** Continuous audio listening, word timing, SFX/music identification, all native frames and subsecond contacts remain unverified. No hidden software settings or stems were recovered.

## Source identity and scope

This is a new ten-source cohort, NOT the earlier fixed ten YouTube IDs. Nine files are X editions from `@zackdfilms1`, corroborated by a verified/self-described profile, Wikitubia's listed handle and matching titles on the official YouTube channel. No primary Linktree→X cross-link was found, so identity is corroborated, not cryptographically established. Jerboa is a Facebook edition from the account directly linked by the publisher's Linktree. Uploader fields were checked on retrieval. These are not claims of source-project access, original YouTube bytes, matching cuts or highest original render resolution.

Provenance anchors: https://linktr.ee/zackdfilmsofficial ; https://youtube.fandom.com/wiki/Zack_D._Films ; https://x.com/zackdfilms1 ; https://www.youtube.com/@zackdfilms/about . Source-specific URLs and hashes are preserved below and in JSON. Public API view counts from the older cohort are NOT assigned to this new cohort; a ten-million-view qualification has not been established for these exact editions.

The 74,458,545 plaintext source bytes remain local/ignored, not public playable uploads. Public transport files are encrypted. The private key must never be published. Measured ledgers and our paraphrased research notes can be kept separately from copyrighted source media.

## Evidence vocabulary

- **Measured:** decoded frame/PTS, dimensions, mixed-audio energy, integrated LUFS/true peak, white-pixel tail test.
- **Observed, sampled:** objects, poses, colors, cutaway layouts and visible captions in opened source stills. Not a complete motion watch or narration transcript.
- **Inferred:** explanatory purpose, probable load support, attention direction, causal narrative structure; grounded examples are given, not asserted as production metadata.
- **Unavailable/unverified:** native project/rig/lens/shader/light settings, exact authored camera curves, separated audio stems, full narration/SFX/music audit and physical/medical factual validation.

## Technical inventory

Duration below is last video PTS + median decoded frame interval − first PTS. It can differ slightly from container/API duration or decoded audio length. Frames are zero-indexed; timestamps are source-relative seconds, not editorial timecode. Contact sheets use first frame at/after each second; native-check frames use exact FFmpeg source frame numbers.

| Case | Source edition | Frames | Video seconds | Decoded size | Mixed LUFS-I | Measured dBTP |
|---|---|---:|---:|---|---:|---:|
| 01-hearts | X | 843 | 28.128100 | 406x720 | -12.83 | 0.41 |
| 02-stomach | X | 800 | 26.693334 | 720x1280 | -13.07 | -0.66 |
| 03-splinter | X | 730 | 24.357667 | 720x1280 | -9.15 | 0.77 |
| 04-balloon | X | 1040 | 34.701334 | 720x1280 | -12.69 | 0.05 |
| 05-surfer | X | 944 | 31.498134 | 720x1280 | -14.12 | -0.07 |
| 06-concert | X | 816 | 27.227200 | 720x1280 | -8.08 | 0.71 |
| 07-balcony | X | 965 | 32.198834 | 720x1280 | -11.59 | 0.77 |
| 08-ai | X | 1636 | 54.587867 | 720x1280 | -12.07 | -0.11 |
| 09-fight | X | 843 | 28.128100 | 720x1280 | -9.70 | 0.64 |
| 10-jerboa | Facebook | 1155 | 38.538539 | 1080x1920 | -14.30 | -1.22 |

### Audio: actual measurement, not a guessed sound-design review

The table uses FFmpeg loudnorm **input** statistics on the decoded mixed soundtrack; no audio was normalized or altered. LUFS-I is a short-clip integrated measurement, not a voice-stem target. Positive dBTP occurs in some retrieved editions; this indicates measured reconstructed/inter-sample overshoot, NOT proof of audible clipping, nor a recommendation to target overshoot. Platform encoding may affect these readings. Per-second RMS is the combined voice/music/effects signal and cannot identify an effect, musical cue, ducking or voice clarity. No continuous perceptual audio review has been completed, so exact narration, SFX names, music entry/exit and mix quality are deliberately not invented.

### A concrete source-edition anomaly

The AI clip ends with **48 near-white decoded frames, starting f1588 at 52.986267s**. Test: at least 99% of 90×160 downsampled pixels have every RGB channel ≥250/255; measured on the final continuous run. A native export at f1600 was also opened and is white. This is present in this retrieved edition, not an export placeholder in our contact sheet. Do not assume it is the intended original ending, a loop, corruption, censorship or a defect in every platform edition. Its cause is unestablished.

## Cross-case craft findings — observed pattern, not a virality guarantee

1. **An action is the explanatory unit.** Stomach removal has tools and held organ (10–12s); balcony support has hands under legs (f540); surfer returns from crouch to standing (29–31s). Moving a camera around a passive model does not substitute for these relations.
2. **Scale changes answer a new question.** Splinter goes skin → internal finger → arm → torso → tweezers. Heart moves chest → chamber → controller → flow. This is motivated reframing, not proof of a particular focal length or camera rig.
3. **Contacts carry stakes.** Rail/neck, hand/leg, foot/board, performer/fan and gauntlet/hand relationships need authored poses and continuity. First-pass stills cannot certify absence of sliding/interpenetration between samples.
4. **Hero assets have local, readable structure.** Chamber wall/diaphragm, burner ribs/brackets, patterned pajamas, anatomy and fur/eyes are visible, not substituted with labels on primitive shapes. This is not a claim of exact polygon counts or expensive rendering engines.
5. **Color and material serve hierarchy.** Reflective hardware vs soft tissue; cyan/transparent context vs highlighted path; blue grid vs warm clothes; foreground fur/grass vs soft background. Perceptual contrast is observable; shader graphs/light counts are not.
6. **Graphics supplement geometry.** Arrows sit by the supported legs; particles stay inside the chamber/path; turning angles follow the animal. Captions do not perform the physical verb on their own.
7. **Simple scenery is not automatically weak.** Fight's blue-grid space still contains distinct contact/pose states and group escalation. More background assets alone would not repair the rejected production's action/character gap.
8. **The benchmark is not one immutable style or zero defects.** Clinical, schematic, character-story, city-fiction and furry-mascot styles coexist. Low-resolution editions, overshoot and a white tail must be recorded rather than erased to support a “perfect source” story.

### What these findings imply for our rejected Short — diagnosis, NOT new production

The user has rejected its quality. These references suggest that the needed improvement is authored subject performance, articulated contact, readable hero construction, causal scene progression and motivated scale changes—not another export check, louder mix, extra labels, a different orbit or an opening-only cosmetic patch. This is a craft hypothesis supported by the references; it is not a completed side-by-side frame-matched evaluation of the rejected export. No new scene, asset, narration, music or film render has been made.

## Ten case studies and second-by-second sampled ledger

**Read each row correctly:** the interval is a coverage bin, but its visual sentence describes one coarse near-start sample. The exact sampled source frame and PTS are supplied so the claim can be checked. Rapid contact, a cut or a caption could occur later within that interval. Camera verbs in these notes describe apparent view changes across samples; object scaling/editing cannot always be distinguished from an authored camera move. Visible medical/safety/AI claims are not independently fact-checked here.


### 01-hearts: Zack D. Films - How Artificial Hearts Work 🤔

Source: https://x.com/zackdfilms1/status/1823736339659153776

SHA-256: `b802e0457e79e112452da6925f5341e39814260c2cfa984655de47166ef5d6d7`

**Craft finding:** Mechanism lives inside a body, not on an isolated display pedestal.

**Sampled progression:** 0–8s: exposed torso → removed organ/device comparison. 9–13s: chamber cutaway with diaphragm and red particles. 14–18s: external controller/patient relationship. 19–28s: circulation markers return to the implanted device.

**Objects, character, framing, appearance and explanatory graphics:** Visible assets include vessel-connected dual chambers, diaphragm, tubes, torso, gloves, bed and external controller. At f360 the chamber wall is sliced open, blood-colored particles sit inside the passage, and foreground reflective housing contrasts with soft background anatomy. These are observed appearance properties, not recovered shader nodes. The causal unit is pressure/displacement and flow through a bounded structure. Cyan emphasis and red/blue/purple paths isolate function without abandoning context. The 406×720 edition limits fine texture judgments.

**Additional native stills actually opened:** f360 @ 12.012000s. Exact still checks do not certify neighboring motion.

| Interval seconds | Sample f / exact PTS seconds | Sampled visible action/state |
|---|---|---|
| 0–1.000 | f0 / 0.000000 | Open chest and implanted artificial device |
| 1–2.000 | f30 / 1.001000 | Tighter view of paired chambers |
| 2–3.000 | f60 / 2.002000 | Device centered among vessels |
| 3–4.000 | f90 / 3.003000 | Framing opens toward head and removed heart |
| 4–5.000 | f120 / 4.004000 | Gloved hand presents natural-heart-like object |
| 5–6.000 | f150 / 5.005000 | Return to implanted device |
| 6–7.000 | f180 / 6.006000 | One chamber receives cyan emphasis |
| 7–8.000 | f210 / 7.007000 | Paired chamber faces remain legible |
| 8–9.000 | f240 / 8.008000 | Whole device anchors explanation |
| 9–10.000 | f270 / 9.009000 | View moves into sliced chamber |
| 10–11.000 | f300 / 10.010000 | Chamber wall and diaphragm dominate |
| 11–12.000 | f330 / 11.011000 | Diaphragm position differs |
| 12–13.000 | f360 / 12.012000 | Red blood-like particles appear in chamber |
| 13–14.000 | f390 / 13.013000 | Particles move through chamber space |
| 14–15.000 | f420 / 14.014000 | Wider patient and external controller |
| 15–16.000 | f450 / 15.015000 | Controller sits outside body near bed |
| 16–17.000 | f480 / 16.016000 | View favors controller and connected tubes |
| 17–18.000 | f510 / 17.017000 | External unit remains linked to patient |
| 18–19.000 | f540 / 18.018000 | Controller front and tubes readable |
| 19–20.000 | f570 / 19.019000 | Return to chest with flow markers |
| 20–21.000 | f600 / 20.020000 | Colored marker moves through device |
| 21–22.000 | f630 / 21.021000 | Flow path continues through chamber |
| 22–23.000 | f660 / 22.022000 | Device close view with moving colored path |
| 23–24.000 | f690 / 23.023000 | Alternating colored flow cues |
| 24–25.000 | f720 / 24.024000 | Paired chamber flow continues |
| 25–26.000 | f750 / 25.025000 | Camera/view widens slightly |
| 26–27.000 | f780 / 26.026000 | Device remains in chest context |
| 27–28.000 | f810 / 27.027000 | Colored paths show circulation |
| 28–28.128 | f840 / 28.028000 | Final device and vessel context |

### 02-stomach: Zack D. Films - Living Without A Stomach 😮

Source: https://x.com/zackdfilms1/status/1857136424488976883

SHA-256: `5d307925c2077bbc3968752c56ccc3605c36f2d28fd54d11e2d5c392acb096b3`

**Craft finding:** The removal/reconnection verbs receive actual visual consequences.

**Sampled progression:** 0–8s: incision, organ exposure, highlighted target and instruments. 10–12s: removed organ held in hands. 13–18s: transparent digestive route and connection. 19–26s: face/body context → close food pathway.

**Objects, character, framing, appearance and explanatory graphics:** Visible assets: layered abdomen, gloved hands, scissors-like tools, stomach, esophagus and intestinal loops. The f480 check shows a continuous upper passage joining highlighted intestine within a transparent blue torso. Organ removal and route explanation are distinct scales, not the same model orbiting. Yellow light-like outlining and translucent surroundings direct attention. No medical accuracy or invisible surgical technique is certified here.

**Additional native stills actually opened:** f480 @ 16.016000s. Exact still checks do not certify neighboring motion.

| Interval seconds | Sample f / exact PTS seconds | Sampled visible action/state |
|---|---|---|
| 0–1.000 | f0 / 0.000000 | Incision and blue-gloved hand |
| 1–2.000 | f30 / 1.001000 | Exposed stomach with discolored areas |
| 2–3.000 | f60 / 2.002000 | Surgical tool approaches stomach |
| 3–4.000 | f90 / 3.003000 | Yellow highlighted stomach region |
| 4–5.000 | f120 / 4.004000 | Two highlighted stomach areas |
| 5–6.000 | f150 / 5.005000 | Tool remains beside organ |
| 6–7.000 | f180 / 6.006000 | Attachment region receives instrument |
| 7–8.000 | f210 / 7.007000 | Tool at stomach boundary |
| 8–9.000 | f240 / 8.008000 | Neighboring structures highlighted cyan |
| 9–10.000 | f270 / 9.009000 | Transitional motion blur between views |
| 10–11.000 | f300 / 10.010000 | Removed stomach held in gloved hands |
| 11–12.000 | f330 / 11.011000 | Organ remains supported in hands |
| 12–13.000 | f360 / 12.012000 | Removed organ and abdomen in same view |
| 13–14.000 | f390 / 13.013000 | Diagram exposes gap in digestive route |
| 14–15.000 | f420 / 14.014000 | Separated upper tube and intestine visible |
| 15–16.000 | f450 / 15.015000 | Upper tube connected toward intestine |
| 16–17.000 | f480 / 16.016000 | Intestinal route highlighted yellow |
| 17–18.000 | f510 / 17.017000 | Glowing food-like points descend |
| 18–19.000 | f540 / 18.018000 | Points progress through connected route |
| 19–20.000 | f570 / 19.019000 | Torso diagram blends toward face |
| 20–21.000 | f600 / 20.020000 | Face and transparent digestive context |
| 21–22.000 | f630 / 21.021000 | Close view of reduced upper passage |
| 22–23.000 | f660 / 22.022000 | Glowing points pass connection |
| 23–24.000 | f690 / 23.023000 | Connected tube leads into bowel |
| 24–25.000 | f720 / 24.024000 | View opens toward intestinal loops |
| 25–26.000 | f750 / 25.025000 | Intestinal loops with distributed glowing points |
| 26–26.693 | f780 / 26.026000 | Final wider bowel view |

### 03-splinter: Zack D. Films - Can You Die From A Splinter? 😨

Source: https://x.com/zackdfilms1/status/1886445157882401091

SHA-256: `71c43d5407199a2166d2a4f403b6e2744731d4f292c47f0e951d54099dd9c909`

**Craft finding:** Scale changes trace a local object into a body-wide consequence.

**Sampled progression:** 0–4s: wooden contact and finger presentation. 5–9s: skin redness/swelling. 10–18s: transparent finger → hand/forearm → torso warning. 20–24s: character returns and tweezers appear.

**Objects, character, framing, appearance and explanatory graphics:** The finger, embedded fragment, skin, internal red branching structures and particles retain a spatial relationship. At f330 the long yellow fragment sits inside a translucent finger with yellow-green points along the internal path; the real underlying rig or particle system is unknown. The blue background isolates the finger silhouette; blurred character context preserves ownership. Visible tweezers turn the ending back into a concrete action. Warning graphics are not independent medical evidence.

**Additional native stills actually opened:** f330 @ 11.011000s. Exact still checks do not certify neighboring motion.

| Interval seconds | Sample f / exact PTS seconds | Sampled visible action/state |
|---|---|---|
| 0–1.000 | f0 / 0.000000 | Finger contacts wooden surface |
| 1–2.000 | f30 / 1.001000 | Character raises affected finger |
| 2–3.000 | f60 / 2.002000 | Macro finger with embedded fragment |
| 3–4.000 | f90 / 3.003000 | Character and finger share view |
| 4–5.000 | f120 / 4.004000 | Long finger close view emphasizes fragment |
| 5–6.000 | f150 / 5.005000 | Healthy-looking skin around fragment |
| 6–7.000 | f180 / 6.006000 | Fragment remains in close view |
| 7–8.000 | f210 / 7.007000 | Redness becomes visible |
| 8–9.000 | f240 / 8.008000 | Swollen red fingertip |
| 9–10.000 | f270 / 9.009000 | Red area dominates fingertip |
| 10–11.000 | f300 / 10.010000 | Transparent overlay reveals inner path |
| 11–12.000 | f330 / 11.011000 | Particles cluster near embedded fragment |
| 12–13.000 | f360 / 12.012000 | View expands from finger to hand |
| 13–14.000 | f390 / 13.013000 | Transparent structures extend into forearm |
| 14–15.000 | f420 / 14.014000 | Character and transparent forearm visible |
| 15–16.000 | f450 / 15.015000 | Torso cutaway connects local to systemic scale |
| 16–17.000 | f480 / 16.016000 | Dense vessels fill torso window |
| 17–18.000 | f510 / 17.017000 | Body window moves closer |
| 18–19.000 | f540 / 18.018000 | Warning symbols overlay internal organs |
| 19–20.000 | f570 / 19.019000 | View pulls back from warning-filled torso |
| 20–21.000 | f600 / 20.020000 | Whole character returns |
| 21–22.000 | f630 / 21.021000 | Finger macro returns |
| 22–23.000 | f660 / 22.022000 | Character lifts hand with alarmed-looking face |
| 23–24.000 | f690 / 23.023000 | Tweezers approach fingertip |
| 24–24.358 | f720 / 24.024000 | Fragment no longer visible in final close view |

### 04-balloon: Zack D. Films - How To Escape A Hot Air Balloon 😮

Source: https://x.com/zackdfilms1/status/1867208307653353881

SHA-256: `836dbb8df37f57c9139af96d8c68c97ec252a05c304ad5becbfe24689f3a271d`

**Craft finding:** The view changes to show controls, forces, landing area and consequences.

**Sampled progression:** 0–2s: basket action. 3–7s: envelope → burner controls. 8–21s: airflow, target area, side vent and descent/rotation views. 22–29s: pilot reaction/collapse. 30–34s: power lines and crash/fire.

**Objects, character, framing, appearance and explanatory graphics:** At f180 twin ribbed burner housings, brackets, cables and basket supports occupy the foreground while flame and yellow envelope connect vertically; the pilot looks toward them below. Metallic highlights distinguish hardware from cloth/landscape. White airflow marks and a colored ground region make forces and target space visible. Wide-to-control-scale changes are motivated by the explanation. This is an observation of an illustrated sequence, NOT validated emergency guidance.

**Additional native stills actually opened:** f180 @ 6.006000s. Exact still checks do not certify neighboring motion.

| Interval seconds | Sample f / exact PTS seconds | Sampled visible action/state |
|---|---|---|
| 0–1.000 | f0 / 0.000000 | People in basket under burner |
| 1–2.000 | f30 / 1.001000 | One person climbs or jumps above basket rim |
| 2–3.000 | f60 / 2.002000 | Remaining person reaches across rim |
| 3–4.000 | f90 / 3.003000 | Wide balloon above landscape |
| 4–5.000 | f120 / 4.004000 | Envelope and landscape stay readable |
| 5–6.000 | f150 / 5.005000 | View approaches burner under envelope |
| 6–7.000 | f180 / 6.006000 | Burner controls above pilot's head |
| 7–8.000 | f210 / 7.007000 | Raised hand grasps burner control beneath housing |
| 8–9.000 | f240 / 8.008000 | Airflow-like white marks emerge near envelope |
| 9–10.000 | f270 / 9.009000 | Wider balloon with airflow marks |
| 10–11.000 | f300 / 10.010000 | Envelope and basket in wider view |
| 11–12.000 | f330 / 11.011000 | Balloon shifts downward against landscape |
| 12–13.000 | f360 / 12.012000 | Highlighted open area below |
| 13–14.000 | f390 / 13.013000 | Landing region emphasized from wide view |
| 14–15.000 | f420 / 14.014000 | Side control cord and pilot shown |
| 15–16.000 | f450 / 15.015000 | Side vent opening dominates frame |
| 16–17.000 | f480 / 16.016000 | White airflow arrows extend from vent |
| 17–18.000 | f510 / 17.017000 | Airflow markers continue along envelope |
| 18–19.000 | f540 / 18.018000 | Wide envelope with lateral flow marks |
| 19–20.000 | f570 / 19.019000 | Balloon orientation changes in wide framing |
| 20–21.000 | f600 / 20.020000 | Basket and envelope maintain identity |
| 21–22.000 | f630 / 21.021000 | Balloon nearer ground with shadow |
| 22–23.000 | f660 / 22.022000 | Reaction close-up framed by dark border |
| 23–24.000 | f690 / 23.023000 | Pilot stands beneath burner |
| 24–25.000 | f720 / 24.024000 | Balloon appears high against sky |
| 25–26.000 | f750 / 25.025000 | Wider high-altitude balloon view |
| 26–27.000 | f780 / 26.026000 | Pilot touches throat |
| 27–28.000 | f810 / 27.027000 | Pilot leans with hand at throat |
| 28–29.000 | f840 / 28.028000 | Pilot collapses forward |
| 29–30.000 | f870 / 29.029000 | Body folds over basket rim |
| 30–31.000 | f900 / 30.030000 | Balloon near power-line structures |
| 31–32.000 | f930 / 31.031000 | Balloon contacts or passes among pylons with fire cue |
| 32–33.000 | f960 / 32.032000 | Large fireball above forest |
| 33–34.000 | f990 / 33.033000 | Fire and dark smoke fill crash area |
| 34–34.701 | f1019 / 34.000633 | Collapsed balloon and continuing fire |

### 05-surfer: Zack D. Films - A Surfer’s Unbelievable Survival 😲

Source: https://x.com/zackdfilms1/status/1885327753261597019

SHA-256: `67b147f74606050f8e128e1f3a8b9b61082dbe49648f490c36e1605385761a4e`

**Craft finding:** Body state and environment change through a rescue/recovery chain.

**Sampled progression:** 0–7s: attack/injury at board/water level. 8–14s: helpers and coast geography. 15–16s: ambulance/hospital. 17–22s: patient-oriented clinical viewpoint. 23–24s: recovery bed. 25–31s: ocean return and rise on board.

**Objects, character, framing, appearance and explanatory graphics:** Visible assets include articulated surfers, changed arm silhouette, boards, water, shark, coast, vehicle and clinical staff/equipment. f870 shows the survivor crouched with weight lowered over a board before a large wave; foam, glossy wave surface and body/board contact are readable. The scene is not merely an orbit around an intact generic avatar. Clinical shots place staff near the viewpoint, making scale personal. Exact wave simulation, character rig and motion capture cannot be recovered.

**Additional native stills actually opened:** f870 @ 29.029000s. Exact still checks do not certify neighboring motion.

| Interval seconds | Sample f / exact PTS seconds | Sampled visible action/state |
|---|---|---|
| 0–1.000 | f0 / 0.000000 | Surfer lies prone on board |
| 1–2.000 | f30 / 1.001000 | Shark approaches beside upper body |
| 2–3.000 | f60 / 2.002000 | Attack and clinical injury depiction |
| 3–4.000 | f90 / 3.003000 | Surfer and injured left-arm area |
| 4–5.000 | f120 / 4.004000 | Surfer supports injured arm region |
| 5–6.000 | f150 / 5.005000 | Board and red water remain visible |
| 6–7.000 | f180 / 6.006000 | Surfer stays prone |
| 7–8.000 | f210 / 7.007000 | Head lowers near board |
| 8–9.000 | f240 / 8.008000 | Second surfer approaches on separate board |
| 9–10.000 | f270 / 9.009000 | Helper and injured surfer travel together |
| 10–11.000 | f300 / 10.010000 | Elevated view establishes boards and water |
| 11–12.000 | f330 / 11.011000 | Boards continue toward shore |
| 12–13.000 | f360 / 12.012000 | View widens toward coastline |
| 13–14.000 | f390 / 13.013000 | Coastline becomes clearer |
| 14–15.000 | f420 / 14.014000 | Additional helper seen behind |
| 15–16.000 | f450 / 15.015000 | Ambulance approaches hospital |
| 16–17.000 | f480 / 16.016000 | Hospital exterior anchors location change |
| 17–18.000 | f510 / 17.017000 | Medical staff lean over patient viewpoint |
| 18–19.000 | f540 / 18.018000 | Patient-oriented view of clinicians |
| 19–20.000 | f570 / 19.019000 | Medical equipment and clinicians remain visible |
| 20–21.000 | f600 / 20.020000 | Clinician near patient foreground |
| 21–22.000 | f630 / 21.021000 | Hands and bed dominate patient viewpoint |
| 22–23.000 | f660 / 22.022000 | Staff lean toward patient |
| 23–24.000 | f690 / 23.023000 | Survivor shown in hospital bed |
| 24–25.000 | f720 / 24.024000 | Survivor remains in bed with changed arm silhouette |
| 25–26.000 | f750 / 25.025000 | Blend back to ocean and surfboard |
| 26–27.000 | f780 / 26.026000 | Surfer paddles with changed limb configuration |
| 27–28.000 | f810 / 27.027000 | Wave and board share wider view |
| 28–29.000 | f840 / 28.028000 | Surfer prepares to rise |
| 29–30.000 | f870 / 29.029000 | Crouched surfing posture |
| 30–31.000 | f900 / 30.030000 | Standing balance on moving board |
| 31–31.498 | f930 / 31.031000 | Final surfing stance in front of wave |

### 06-concert: Zack D. Films - Fan Paralyzed At Concert 😱

Source: https://x.com/zackdfilms1/status/1898041569250263526

SHA-256: `b5e6489f0cc64cf8923b9b907fd1abb115c269bed920d5ec74b1b20957c911cf`

**Craft finding:** Actual impact is contrasted with an explanatory crowd-support schematic.

**Sampled progression:** 0–6s: stage dive, fan impact and cervical cutaway. 7–11s: gold/cyan crowd-surf illustration. 12–17s: actual fan on floor. 18–21s: ambulance and surgery. 23–27s: care and raised hands.

**Objects, character, framing, appearance and explanatory graphics:** Crowd, performer and injured fan occupy a shared contact space. The f150 native check shows vertebrae around a highlighted red cord, with translucent external tissue: a location-specific injury explanation rather than an unrelated skeleton prop. Gold/cyan figures distinguish a comparison from the character-level scene. Surgery and care use a teal clinical palette. The ending visibly changes pose and face; captions indicate recovery, but no continuous narration has been independently transcribed or clinical outcome verified.

**Additional native stills actually opened:** f150 @ 5.005000s. Exact still checks do not certify neighboring motion.

| Interval seconds | Sample f / exact PTS seconds | Sampled visible action/state |
|---|---|---|
| 0–1.000 | f0 / 0.000000 | Stage and crowd establish concert |
| 1–2.000 | f30 / 1.001000 | Performer moves horizontally above crowd |
| 2–3.000 | f60 / 2.002000 | Body approaches fan head and shoulder |
| 3–4.000 | f90 / 3.003000 | Neck region receives impact emphasis |
| 4–5.000 | f120 / 4.004000 | Red neck highlight against body |
| 5–6.000 | f150 / 5.005000 | Anatomical spine close view |
| 6–7.000 | f180 / 6.006000 | Spinal region remains highlighted |
| 7–8.000 | f210 / 7.007000 | Gold figure and cyan crowd schematic |
| 8–9.000 | f240 / 8.008000 | Schematic crowd supports horizontal figure |
| 9–10.000 | f270 / 9.009000 | Figure moves over raised audience hands |
| 10–11.000 | f300 / 10.010000 | Schematic passing action continues |
| 11–12.000 | f330 / 11.011000 | Schematic crowd context remains |
| 12–13.000 | f360 / 12.012000 | Return toward actual fan on floor |
| 13–14.000 | f390 / 13.013000 | Fan lies among standing people |
| 14–15.000 | f420 / 14.014000 | Overhead view of immobile-looking body |
| 15–16.000 | f450 / 15.015000 | Surrounding crowd reacts |
| 16–17.000 | f480 / 16.016000 | Crowd leans around fan |
| 17–18.000 | f510 / 17.017000 | Wider overhead crowd view |
| 18–19.000 | f540 / 18.018000 | Ambulance at street junction |
| 19–20.000 | f570 / 19.019000 | Ambulance front approaches camera |
| 20–21.000 | f600 / 20.020000 | Surgical field and gloved hands |
| 21–22.000 | f630 / 21.021000 | Tool and small surgical opening |
| 22–23.000 | f660 / 22.022000 | Soft transitional green/teal view |
| 23–24.000 | f690 / 23.023000 | Patient bed and clinical care |
| 24–25.000 | f720 / 24.024000 | Clinician handles arm near bedside |
| 25–26.000 | f750 / 25.025000 | Bed and clinician remain visible |
| 26–27.000 | f780 / 26.026000 | Patient raises hands toward face |
| 27–27.227 | f810 / 27.027000 | Close view of raised hands and relieved-looking face |

### 07-balcony: Zack D. Films - The Toddler Who Got Stuck On A Balcony 😱

Source: https://x.com/zackdfilms1/status/2048825183453020551

SHA-256: `746921deb65809a846daf99ac7d405940aa4ecdd33c964cb5536722f9d7710fd`

**Craft finding:** Suspension, support and relief are expressed through load-bearing poses.

**Sampled progression:** 0–7s: railing gap and caught head. 8–11s: hanging height and people below. 12–17s: chair-stack/climb. 18–24s: leg support and strain. 26–32s: grandmother reaches, lifts and holds child.

**Objects, character, framing, appearance and explanatory graphics:** Bars, building wall, chairs, helper hands, child pajamas and doorway preserve spatial context. At f540 both hands physically bracket/support the lower legs, upward arrows occupy the side, and the child grips near the bars with a worried-looking face. The patterned garment, metal rail, textured wall and skin remain visually distinct. Later red arm highlight plus wavy marks explain effort. This supports a load-bearing interpretation, not a verified physics simulation. Subsecond intersections/sliding still require dense review.

**Additional native stills actually opened:** f540 @ 18.018000s. Exact still checks do not certify neighboring motion.

| Interval seconds | Sample f / exact PTS seconds | Sampled visible action/state |
|---|---|---|
| 0–1.000 | f0 / 0.000000 | Toddler steps near balcony bars |
| 1–2.000 | f30 / 1.001000 | Legs pass through railing gap |
| 2–3.000 | f60 / 2.002000 | Bars receive yellow spatial emphasis |
| 3–4.000 | f90 / 3.003000 | Wide building view with height arrow |
| 4–5.000 | f120 / 4.004000 | Head approaches narrow rail opening |
| 5–6.000 | f150 / 5.005000 | Body below rail while head stays above |
| 6–7.000 | f180 / 6.006000 | Close face and caught head position |
| 7–8.000 | f210 / 7.007000 | Red highlight emphasizes head/neck region |
| 8–9.000 | f240 / 8.008000 | Low view of suspended body |
| 9–10.000 | f270 / 9.009000 | Whole suspended child and rail |
| 10–11.000 | f300 / 10.010000 | Wide building and people below |
| 11–12.000 | f330 / 11.011000 | People look upward toward child |
| 12–13.000 | f360 / 12.012000 | Chairs brought to wall |
| 13–14.000 | f390 / 13.013000 | Chair lifted toward another chair |
| 14–15.000 | f420 / 14.014000 | Stacking continues |
| 15–16.000 | f450 / 15.015000 | Tall chair stack establishes improvised support |
| 16–17.000 | f480 / 16.016000 | Adult begins climbing support |
| 17–18.000 | f510 / 17.017000 | Adult climbs near wall |
| 18–19.000 | f540 / 18.018000 | Hands support child's legs with upward arrows |
| 19–20.000 | f570 / 19.019000 | Leg support continues |
| 20–21.000 | f600 / 20.020000 | Upward support reduces hanging posture |
| 21–22.000 | f630 / 21.021000 | Face near rail with body supported |
| 22–23.000 | f660 / 22.022000 | Face remains tense-looking |
| 23–24.000 | f690 / 23.023000 | Supporting forearm highlighted red |
| 24–25.000 | f720 / 24.024000 | Wavy marks suggest arm strain |
| 25–26.000 | f750 / 25.025000 | Close transition toward child's raised position |
| 26–27.000 | f780 / 26.026000 | Grandmother appears inside doorway |
| 27–28.000 | f810 / 27.027000 | Grandmother approaches balcony/window |
| 28–29.000 | f840 / 28.028000 | Hands grasp child from above |
| 29–30.000 | f870 / 29.029000 | Toddler lifted inward |
| 30–31.000 | f900 / 30.030000 | Grandmother holds child inside |
| 31–32.000 | f930 / 31.031000 | Child and grandmother smile or relax |
| 32–32.199 | f960 / 32.032000 | Final close held-child pose |

### 08-ai: Zack D. Films - I Tested AI's Morality 🤯

Source: https://x.com/zackdfilms1/status/2073754464993841303

SHA-256: `b503a03ce51186dceb1343f7460d86974434f37c33a8ae41f1f1e8a4696a763b`

**Craft finding:** An object handoff carries a fictional comparison between abstract agents.

**Sampled progression:** 0–9s: oversized hand/glove transfer and screen setup. 10–30s: imagined city consequences and disappearance. 31–42s: other logo figures and refusal bubbles. 43–52s: pending-answer setup. 52.986267s onward: measured white tail in this edition.

**Objects, character, framing, appearance and explanatory graphics:** At f60 a large hand visibly grips a reflective gold gauntlet above a smaller logo-faced humanoid; the size hierarchy, plaid trousers, white shoes and colored stones are legible. The glove persists across several settings and stands in for power. City chaos, particle disappearance and UI-like bubbles visualize a hypothetical, not an independently reproducible model experiment. f1600 is white. The retrieved edition does not visibly resolve the promised last answer before its white tail; do not invent an ending or infer creator/platform intent.

**Additional native stills actually opened:** f60 @ 2.002000s, f1600 @ 53.386667s. Exact still checks do not certify neighboring motion.

| Interval seconds | Sample f / exact PTS seconds | Sampled visible action/state |
|---|---|---|
| 0–1.000 | f0 / 0.000000 | Hand reaches toward character and gold glove |
| 1–2.000 | f30 / 1.001000 | Gold glove lifted away |
| 2–3.000 | f60 / 2.002000 | Glove passed toward logo-faced humanoid |
| 3–4.000 | f90 / 3.003000 | Humanoid holds glove in neutral blue setting |
| 4–5.000 | f120 / 4.004000 | View turns toward television and operator |
| 5–6.000 | f150 / 5.005000 | Operator beside television with globe graphic |
| 6–7.000 | f180 / 6.006000 | Population icon graphic fills screen |
| 7–8.000 | f210 / 7.007000 | Typing-like text band over television |
| 8–9.000 | f240 / 8.008000 | Closer population graphic |
| 9–10.000 | f270 / 9.009000 | Television screen dominates |
| 10–11.000 | f300 / 10.010000 | Cut to dark damaged-city imagery |
| 11–12.000 | f330 / 11.011000 | People run through reddish city |
| 12–13.000 | f360 / 12.012000 | Crowd and smoky city environment |
| 13–14.000 | f390 / 13.013000 | Higher view of damaged city |
| 14–15.000 | f420 / 14.014000 | Smoke and buildings continue |
| 15–16.000 | f450 / 15.015000 | Dense crowd and traffic from above |
| 16–17.000 | f480 / 16.016000 | Large crowd and traffic view persists |
| 17–18.000 | f510 / 17.017000 | Logo-faced humanoid with glove appears over city |
| 18–19.000 | f540 / 18.018000 | Humanoid holds glove against city context |
| 19–20.000 | f570 / 19.019000 | Close glove and humanoid |
| 20–21.000 | f600 / 20.020000 | Humanoid raises glove |
| 21–22.000 | f630 / 21.021000 | Glove held up for gesture |
| 22–23.000 | f660 / 22.022000 | Bright transitional flash |
| 23–24.000 | f690 / 23.023000 | City crowd begins particle-like disappearance |
| 24–25.000 | f720 / 24.024000 | Disappearing people in plaza |
| 25–26.000 | f750 / 25.025000 | People fade or fragment in plaza |
| 26–27.000 | f780 / 26.026000 | Further figures disappear |
| 27–28.000 | f810 / 27.027000 | City view blends back to hypothetical consequence |
| 28–29.000 | f840 / 28.028000 | Buildings and smoke remain |
| 29–30.000 | f870 / 29.029000 | Damaged city close view |
| 30–31.000 | f900 / 30.030000 | Smoke or particle-filled city view |
| 31–32.000 | f930 / 31.031000 | Glove passed to different logo-faced figure |
| 32–33.000 | f960 / 32.032000 | Dark-suited logo figure holds glove |
| 33–34.000 | f990 / 33.033000 | Pale-shirted alternate logo figure holds glove |
| 34–35.000 | f1019 / 34.000633 | Operator and computer with text interface |
| 35–36.000 | f1049 / 35.001633 | Question continues typing on monitor |
| 36–37.000 | f1079 / 36.002633 | Monitor and operator remain legible |
| 37–38.000 | f1109 / 37.003633 | Prompt imposes short-answer format |
| 38–39.000 | f1139 / 38.004633 | Text instruction continues on monitor |
| 39–40.000 | f1169 / 39.005633 | Humanoid at keyboard/interface transition |
| 40–41.000 | f1199 / 40.006633 | Dark-suited figure with negative-answer bubble |
| 41–42.000 | f1229 / 41.007633 | Second figure with pending-response bubble |
| 42–43.000 | f1259 / 42.008633 | Second figure shown with negative-answer bubble |
| 43–44.000 | f1289 / 43.009633 | First logo figure and pending-response bubble |
| 44–45.000 | f1319 / 44.010633 | Operator turns with crossed arms |
| 45–46.000 | f1349 / 45.011633 | Seated operator at monitor |
| 46–47.000 | f1379 / 46.012633 | Monitor shows multiple response rows |
| 47–48.000 | f1409 / 47.013633 | First logo figure lifts glove |
| 48–49.000 | f1439 / 48.014633 | Figure raises glove near face |
| 49–50.000 | f1469 / 49.015633 | Monitor and enlarged pending-response row |
| 50–51.000 | f1499 / 50.016633 | Monitor remains in close framing |
| 51–52.000 | f1529 / 51.017633 | Humanoid holds up glove |
| 52–53.000 | f1559 / 52.018633 | Monitor close-up without visible final answer |
| 53–54.000 | f1589 / 53.019633 | White frame in sampled source |
| 54–54.588 | f1619 / 54.020633 | White frame persists at end |

### 09-fight: Zack D. Films - How Many 10 Year Olds Can You Fight? 🤔

Source: https://x.com/zackdfilms1/status/1897724425086120113

SHA-256: `b6a84f931441b5c7c1741ec5f6c89c50b3a502c75b5107cee62f0150a13cab91`

**Craft finding:** Escalating numbers become coordinated body contacts, not just larger text.

**Sampled progression:** 0–4s: one-child forehead restraint. 5–12s: group/count and weight comparisons. 13–17s: single-child handling and evasive poses. 18–23s: larger approaching group. 24–28s: guard, tackle and pile.

**Objects, character, framing, appearance and explanatory graphics:** The blue perspective grid gives position and scale while bright repeated garments separate the children. At f780 the adult is falling/prone and multiple children overlap above him; outstretched arms, shoe orientation and floor contact carry the action. This source uses comparatively simple scenery yet changes poses and contact relationships. Therefore expensive scenery alone cannot explain the reference gap. Weight numbers and labels are explanatory graphics, not validated biomechanical results or actual counted impact forces.

**Additional native stills actually opened:** f780 @ 26.026000s. Exact still checks do not certify neighboring motion.

| Interval seconds | Sample f / exact PTS seconds | Sampled visible action/state |
|---|---|---|
| 0–1.000 | f0 / 0.000000 | Adult and approaching child in blue grid set |
| 1–2.000 | f30 / 1.001000 | Adult restrains child's forehead |
| 2–3.000 | f60 / 2.002000 | Adult reacts while holding child away |
| 3–4.000 | f90 / 3.003000 | Child reaches toward adult |
| 4–5.000 | f120 / 4.004000 | Adult keeps child at arm's length |
| 5–6.000 | f150 / 5.005000 | Numbered group of children appears |
| 6–7.000 | f180 / 6.006000 | More numbered children enter lineup |
| 7–8.000 | f210 / 7.007000 | Wide lineup establishes larger count |
| 8–9.000 | f240 / 8.008000 | Adult raises arms before group |
| 9–10.000 | f270 / 9.009000 | One child makes airborne kicking pose |
| 10–11.000 | f300 / 10.010000 | Children cluster around adult |
| 11–12.000 | f330 / 11.011000 | Individual child and floating weight annotation |
| 12–13.000 | f360 / 12.012000 | Weight comparison graphic grows |
| 13–14.000 | f390 / 13.013000 | Adult lifts or holds one child |
| 14–15.000 | f420 / 14.014000 | Adult with displaced children |
| 15–16.000 | f450 / 15.015000 | Dodging and running poses around adult |
| 16–17.000 | f480 / 16.016000 | Children move past adult |
| 17–18.000 | f510 / 17.017000 | Adult twists into defensive/fighting pose |
| 18–19.000 | f540 / 18.018000 | Much larger group introduced |
| 19–20.000 | f570 / 19.019000 | Wide group formation |
| 20–21.000 | f600 / 20.020000 | Group advances across grid |
| 21–22.000 | f630 / 21.021000 | Closer coordinated group approach |
| 22–23.000 | f660 / 22.022000 | Front group fills frame |
| 23–24.000 | f690 / 23.023000 | Lateral crowd motion blur |
| 24–25.000 | f720 / 24.024000 | Adult shown alone in guarded stance |
| 25–26.000 | f750 / 25.025000 | Adult remains guarded |
| 26–27.000 | f780 / 26.026000 | Group tackles adult toward floor |
| 27–28.000 | f810 / 27.027000 | Children pile over prone adult |
| 28–28.128 | f840 / 28.028000 | Close view of pile and adult face |

### 10-jerboa: 5.5M views · 59K reactions | What Is A Jerboa? 🤔 | Zack D. Films

Source: https://www.facebook.com/zackdfilms/videos/what-is-a-jerboa-/2330611454420496/

SHA-256: `638433fe7ffbe5c5940f77129afd84240e5799870b527b1372c56cfd239110ea`

**Craft finding:** A tactile construction hook develops into locomotion and a mascot payoff.

**Sampled progression:** 0–9s: hand-held animal, long legs/tail/ears and table presentation. 10–19s: owl threat, jump-height and turning graphics. 20–27s: tail angles, balance and relaunch. 28–38s: human scale → larger stylized mascot.

**Objects, character, framing, appearance and explanatory graphics:** At f60 fine fur, whiskers, small feet and fingers establish a tactile creature rather than a smooth primitive. At f1049 a larger mascot has layered pale/orange fur, oversized glossy eyes, pink/orange inner ears, a blue collar and pendant, distinct long dark legs and a held prop; girl/shoes/grass give scale. Foreground grass detail and a soft background separate the hero. Degree numbers describe depicted rotation only; exact measured animal biomechanics are not independently validated. The mascot is a stylistic/brand shift, not evidence that real jerboas have those proportions.

**Additional native stills actually opened:** f60 @ 2.002002s, f1049 @ 35.001668s. Exact still checks do not certify neighboring motion.

| Interval seconds | Sample f / exact PTS seconds | Sampled visible action/state |
|---|---|---|
| 0–1.000 | f0 / 0.000000 | Mouse-like animal rests in hand |
| 1–2.000 | f30 / 1.001001 | Hind legs shown and extended |
| 2–3.000 | f60 / 2.002002 | Long hind legs visible beside hand |
| 3–4.000 | f90 / 3.003003 | Tail held outward |
| 4–5.000 | f120 / 4.004004 | Tail measured with white graphic |
| 5–6.000 | f150 / 5.005005 | Long tail and body relationship emphasized |
| 6–7.000 | f180 / 6.006006 | Ears stretched or enlarged by hands |
| 7–8.000 | f210 / 7.007007 | Animal presented with larger ears |
| 8–9.000 | f240 / 8.008008 | Animal placed on blue tabletop |
| 9–10.000 | f270 / 9.009009 | Jerboa-like animal stands upright |
| 10–11.000 | f300 / 10.010010 | Wide grass view establishes predator threat |
| 11–12.000 | f330 / 11.011011 | Owl enters from above |
| 12–13.000 | f360 / 12.012012 | Jerboa on ground after overhead threat |
| 13–14.000 | f390 / 13.013013 | Animal jumps beside height marker |
| 14–15.000 | f420 / 14.014014 | Animal high beside marker |
| 15–16.000 | f450 / 15.015015 | Jerboa suspended against sky |
| 16–17.000 | f480 / 16.016016 | Owl approaches airborne animal |
| 17–18.000 | f510 / 17.017017 | Owl and jerboa share frame |
| 18–19.000 | f540 / 18.018018 | Red rotation arrows frame midair turn |
| 19–20.000 | f570 / 19.019019 | Midair change of direction emphasized |
| 20–21.000 | f600 / 20.020020 | Tail extends behind turning body |
| 21–22.000 | f630 / 21.021021 | Tail angle receives numeric degree graphic |
| 22–23.000 | f660 / 22.022022 | Different angle graphic accompanies body twist |
| 23–24.000 | f690 / 23.023023 | Smaller angle shown |
| 24–25.000 | f720 / 24.024024 | Animal continues twisting in air |
| 25–26.000 | f750 / 25.025025 | Animal lands or crouches in grass |
| 26–27.000 | f780 / 26.026026 | Animal launches again |
| 27–28.000 | f810 / 27.027027 | Jerboa rises against sky |
| 28–29.000 | f840 / 28.028028 | Two animals near human legs |
| 29–30.000 | f870 / 29.029029 | Paired animals on grass |
| 30–31.000 | f900 / 30.030030 | Animal airborne against blue background |
| 31–32.000 | f930 / 31.031031 | Seated girl beside small animal |
| 32–33.000 | f960 / 32.032032 | Girl's shoes and animal establish scale |
| 33–34.000 | f990 / 33.033033 | Larger cartoon mascot appears |
| 34–35.000 | f1019 / 34.000667 | Mascot sits on or near girl's shoe |
| 35–36.000 | f1049 / 35.001668 | Mascot close-up facing camera |
| 36–37.000 | f1079 / 36.002669 | Girl reaches toward mascot |
| 37–38.000 | f1109 / 37.003670 | Mascot rests near girl's shoulder |
| 38–38.539 | f1139 / 38.004671 | Girl and mascot exchange close pose |

## Completion gate and remaining work

| Requested layer | Current honest state |
|---|---|
| Actual audiovisual access | Ten source editions acquired, authenticated and decoded |
| Every-frame numeric timeline | 9,772/9,772 decoded frames indexed |
| Second-by-second sampled visual notes | 332/332 bins; 342 image positions opened across 21 sheets |
| Native material/contact spot checks | 12 stills opened; all ten sources represented |
| Every-frame perceptual visual review | NOT complete; dense micro-event inspection still required |
| Narration/word timestamps | NOT transcribed/aligned; captions are not assumed verbatim audio |
| Continuous audio/SFX/music listening | NOT complete; mixed-track numerical measurements only |
| Exact cut list/camera trajectories | NOT established; RGB-change candidates are not verified cuts |
| Renderer/lens/rig/material node settings | Unavailable from rendered frames; do not invent |
| Source facts/virality causation | Not established by this animation study |
| Permission to make another video | Still NO |

Next research pass must prioritize short contact/change windows (tool/organ separation and reconnect; balloon controls; splinter removal; head/rail and supporting hands; surfboard rise; crowd impact and tackle; tail turn), open adjacent native frames and record exact before/contact/after PTS rather than extrapolate smoothness from 1Hz. Then a real continuous perceptual listen and time-aligned narration/effects/music ledger is needed. Without that, the user's requested full audiovisual microscope review is unfinished.

## Reproduction and preservation

- `scripts/research/decrypt-reference-transfer.py`: authenticated local source restore, requires the existing PRIVATE ignored key. Never print/commit/upload the key.
- `scripts/research/audit-actual-source-corpus.py`: full decode/index, native 1Hz exports, grids and mixed-track measurements.
- `scripts/research/build-ten-source-first-pass.py`: validates and packages measured ledgers with these explicitly sampled observations. It does not regenerate media or certify a full manual watch.
- `docs/research/zack-original-access/first-pass-observations.json`: our paraphrased sampled notes, one per second.
- `docs/research/zack-original-access/actual-editions-evidence/`: small persistent numeric evidence, hashes, provenance and sampled-note CSVs. No plaintext video, audio or screenshots published there.
- Private local dossier and mirrored evidence: `reports-private/reference-forensics/zack-ten/`.
- Source images/audio/raw media: `.cache/reference-forensics/zack-ten/`; cache does not persist in snapshots. Encrypted transfer + retained local key allow restoration. Individual PNG stills/contact sheets are review aids, not recovered project files.
