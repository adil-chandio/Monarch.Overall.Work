# Extinct Life EP01 — Production reset, not a cosmetic revision

Owner rejected the first cut. The rejection is the quality authority: the original MP4 remains a rejected illustrated first cut, not the new channel standard. Do not reuse its image/pan/title-card scene system.

## Direction selected: Cinematic Evidence Expedition

A documentary that alternates **being inside a moving lost world** with **following the physical investigation**. Originality must come from the narrative and explanatory staging, not from copying another channel's frames. This is a provisional direction pending actual competitor playback and owner approval of a representative sequence.

The final target remains **6–8 minutes, English, 16:9**. A 45-second representative sequence is a production gate, NOT a replacement Short. A separate 18-second procedural motion lab verifies technical capability only; it is not that representative sequence and must not be sold as premium final art.

### Three image-making languages, all moving scenes

1. **World / experience:** moving environment, weather, water, vegetation and physically plausible animal action. A camera pan across a generated still does not qualify. Use original animated 3D or appropriately licensed motion footage; realistic synthetic reconstruction must be labeled. No unlicensed competitor shots, prehistoric film/TV clips, or documentary music.
2. **Investigation / evidence:** animated camera over geography, a procedural sediment cross-section that physically separates, fragmented-read comparison, evidence paths that appear because a comparison is performed. No fake scientific readouts, invented lab measurements or white-coat stock standing in for the actual team.
3. **Scale / comprehension:** original 3D scenes and concise graphical inserts that answer a precise question—age, location, relative size or uncertainty. Diagram mechanics are not the actual experiment. No full-screen paragraph cards as the visual backbone.

Still references may be used internally for research or modelling, but **not generated/acquired as an image-slide production workflow**. Do not turn I2V into a concealed pan-and-zoom fallback. A licensed historical document may be shown briefly as evidence, not counted as a motion scene.

### Visual identity

Natural arctic slate and forest greens; amber reserved for the evidence the audience should follow. One attention target at a time. No permanent field-notes dashboard, progress line, equalizer, giant chapter number or brand frame. Labels are small but legible; the scene carries the frame. Differentiate data, inference and reconstruction without covering every shot in disclaimers.

### Camera and editing

- Establish a visible subject/action immediately; no logo lead-in or ceremonial fade from black.
- Plan actual movement paths in 3D, not arbitrary shake over a flat background.
- Match direction/scale across cuts when motivated; preserve geographic and narrative orientation. Do not force a transition on every seam.
- Use temporal sound bridges (J/L cuts), subject match-cuts, foreground occlusion and occasional controlled focus transitions. Avoid incessant glitch/whip/zoom effects.
- Renew information or action frequently, but let a discovery land. A 2–6-second early shot cadence is a starting experiment, not a rule or a retention guarantee. Longer sustained shots can be stronger than busy editing.
- Use a native, consistent motion cadence for scene footage. Render original graphic motion at 60 fps where appropriate. Do not advertise duplicated 24/30 fps source frames as newly captured 60 fps detail or automatically interpolate animal motion.

### Sound and score

Create separate VO, score, location ambience, subject/foley and editorial-transition stems. An animal footfall, grain separation or transition earns its cue; the cut alone does not. Stereo atmosphere; dialogue centered; music ducks under speech. Compose an arc rather than repeating a drone. A deliberate short silence before a major reveal is allowed. No monster vocals invented as paleontological evidence.

Use the house score/sound-design tools as implementation recipes, not unquestioned taste guarantees. The repo's mix-master and reference-match notes conflict on short-form LRA; measure appropriately and do not apply an unsupported 5–9 LU gate to every short test. Technical audio compliance cannot certify premium taste.

## Representative opening to build: 45 seconds

| Time | Scene and actual action | Editorial purpose / sound |
|---|---|---|
| 00–03 | Moving tusked-animal detail in an environment, clearly reconstructed; cut before becoming a beauty-shot loop | Specific cold-open: “Mastodon DNA. In Greenland.” Dry voice, small physical cue, no giant text slam |
| 03–07 | Moving present-day Arctic coast, geography established; do not mislabel a generic coast as study-site footage | Contradiction: ancient evidence versus today's setting; wind bridges the cut |
| 07–12 | Original animated northern-Greenland locator; approximate-age cue introduced once | Locate Kap København; don't imply the study happened in 2026 |
| 12–19 | Procedural sediment cross-section opens; camera follows one highlighted fragment into the material | Evidence was fragmentary DNA, not a recovered whole animal; granular foley localized to action |
| 19–26 | Short damaged fragments compared with a reference visualization; mismatches remain visible | Show interpretation and uncertainty, not a magic automatic species scanner; schematic label |
| 26–34 | Moving reconstructed woodland/estuary; water, vegetation and camera all participate | Pay off the lost-world promise; not exact historical footage or one proven synchronous scene |
| 34–40 | One supported lineage revealed in the evidence map; image separated visually from genetic evidence | Reconstruction does not validate itself; do not claim complete genome or clone |
| 40–45 | Moving world is interrupted by a visibly incomplete evidence path | Open the investigation: “How much of that world can we actually read?” Score pulls back to leave room for the question |

Voice text above is a proposed rewrite, not already recorded. The original voice selection can be retained, but the first narration has not been approved for this revised opening.

## Repo implementation map: inspected, not just listed

| Need | Existing implementation | Use / limitation |
|---|---|---|
| Deterministic capture | `showreel/render_60fps.mjs` | Adapt frame-seek/capture pattern; do not run its MONARCH encryption, B2B footage or client-brand scene structure |
| Motion principles | `skills/monarch-video-lab/motion-graphics/SKILL.md` | One protagonist, purposeful motion, seam checks; its own anti-pattern list explicitly rejects static fade cards |
| Camera recipes | `skills/video-shotcraft/references/shots/camera/{space-camera-moves,depth-layer-moves,basic-3d-scene}.md` | Exploded-view / depth / camera-path ideas only. Do not turn an educational film into floating UI cards |
| Continuous seams | `skills/hyperframes/motion-doctrine/SKILL.md` | Direction and velocity continuity; selectively applied to film language, not mandatory whole-film leftward motion |
| Musical timing | `skills/video-shotcraft/references/music-beat-sync.md` | Content-led timing until score chosen; beat fit does not override speech or scientific explanation |
| Original score / SFX | `skills/monarch-video-lab/{music-score,sound-design,sfx-library}` | Original stems and manifests, no unknown-license effects |
| Audio measurement | `showreel/audio_qc/{core,gates,compare}.py` | True audio checks; not an aesthetic-quality certification |
| Existing motion engine | `gpu-engine/kaggle/run_b2b_i2v.py` | Real image-to-video code. Current job is B2B-specific and 768×448 / 49 frames, NOT demonstrated native 1080p long-form animal cinematography |
| Existing motion evidence | `gpu-engine/clips/receipts_*.json`, `gpu-engine/qc_report.json` | Demonstrates prior short motion clips. Historical reports are not validation of a new EP01 render |
| Workflow risk | `.github/workflows/kaggle-b2b-render.yml` | Hard-coded to a different historical branch, B2B keyframes and job. DO NOT execute unchanged or push there |
| Generic references | `skills/openmontage` | Repo policy is reference-only; do not copy/link code into this deliverable |

The generated skills index lists 958 skills, but only relevant selected files were inspected in this pass. Quantity is not proof of readiness. A skill description, a render script, an available model and an actually validated shot are four different states.

## Competitor inspection: honest current state

The earlier API dataset supports English-market topic/packaging selection, not claims about actual editing.

Fresh runner attempt: Fossil `nAWpLtG-kNs`, BlackWater `SDs41Ke3v4Q`, BeyondTheBlue `qrfhhZ-Wvmk`, Vividen `td2GgN6lrWE`. All four public opening-excerpt attempts returned YouTube sign-in/bot-verification. Actual openings were **not obtained, watched or scored**. Evidence: `docs/research/data/extinct-motion-review/report.json`. No claim here that a proposed style is objectively better than those videos.

To complete the requested scene-level comparison, obtain user-supplied review clips (preferably the first 60–90 seconds and one mid-film scene from two or three relevant English videos). Do not request login passwords or exported account cookies. Analyse shot boundaries, intrinsic versus camera-only movement, framing/scale, scientific overlays, audio bridges, narrative beats and intervals before each new piece of information. Assess at normal playback speed as well as consecutive frames. Study grammar, not extract production assets.

## Capability/readiness boundaries

The runner detected the existing COMPALI credential slot as populated; Kaggle API token and legacy key slots checked were empty. **Presence is not authentication, verified current quota or permission to promise free GPU time.** No new GPU job was launched. The current I2V worker depends on external model downloads; model access, licence, allocation and animal/anatomy quality require a small isolated smoke test before any production commitment. No paid API or new subscription was started.

A viable documentary also needs rights-cleared moving source scenes or validated original animation. Those assets have not yet been acquired for the above 45-second opening. Do not fill the gap with four images, slow pans, repeated two-second loops or upscaled output passed off as native detail.

## Release gate: do not repeat the first-cut failure

1. Obtain reference playback evidence, or explicitly retain the benchmark as unverified.
2. Approve a real-world/environment/animal art direction from motion, not a still moodboard.
3. Build the 45-second representative sequence with footage, 3D explanation, narration and finished sound—not only a trailer or technical animation test.
4. Watch it full-screen, at phone size, and with sound. Inspect seams in consecutive frames. Reject anatomy warps, sliding feet, looping water, camera disorientation, dead graphic holds, fake measurements or visual promises the evidence cannot support.
5. Owner approves that representative standard **before** expanding it across the full 6–8-minute film. The final scope has not changed.
6. Full-file decode, duration/frame checks, measured audio/true peak after AAC, caption alignment, scientific/source review and rights manifest come after creative approval. These are necessary, not sufficient, for quality.

Do not label an engine test “competitor-beating,” “premium finished,” “retention-proven,” or “algorithm guaranteed.” The next finished episode is not yet produced.
