# Third pass — actual audio model route working; deeper native motion evidence

**Production remains STOPPED. No new animation, narration, music or replacement film was produced.**

## Seedha result

Audio access/model-ingestion ka rasta ab chal gaya hai: **10/10 actual original-local soundtracks** ka model pass complete hai. Yeh sirf captions ko audio maan lena nahi: decoded source sound was input to two running audio models. Lekin model output ko personally sun kar verified listening, perfectly corrected transcription, ya completed every-native-frame study nahi kaha ja raha.

### Exact completion boundary

| Layer | Actual state |
|---|---|
| Actual ten MP4s acquired/authenticated | 10/10 creator-attributed platform editions; cohort/platform caveats unchanged |
| Decoded frame/PTS numerical coverage | 9,772/9,772 |
| Actual soundtrack model ingestion | **10/10**, source association verified |
| ASR word-timestamp entries | **867**, model-derived, not a corrected transcript |
| Broad overlapping audio-event windows | **69**, 10-second windows / 5-second stride; not discrete SFX counts |
| Word entries scoring below 0.8 | **44**, explicitly flagged; high score also does not guarantee correctness |
| One-second sample positions opened | 342 |
| Cumulative full native stills opened | **33** unique source positions |
| Cumulative native-pixel ROI positions opened | **227**; some overlap full stills/samples |
| Any visual scope, deduplicated | **572/9,772** source positions |
| Source positions not opened in any visual scope | **9200** |
| Exhaustive manual visual + continuous perceptual audio studies | **0/10** — NOT complete |

A full native still, a contact-area crop, a 1Hz thumbnail and a numerically decoded frame are different evidence scopes. Opening a full still does not certify every pixel/detail or adjacent motion. The requested full microscope-level study is not complete merely because the audio models now ran successfully.

## The audio route that actually worked

1. **Eight direct matches.** Runner re-fetched the public platform sources through the established ordinary route, checked uploader identity, and compared concatenated encoded-audio packet SHA-256 against the original local corpus. Only exact matches were analyzed.
2. **Two blocked inputs were NOT silently substituted.** Stomach had a public-download timeout; the re-fetched AI soundtrack failed the exact encoded-packet hash gate. Hash difference alone does not establish changed narrative content; encoding/edition differences are possible. Either way, it was excluded from old-source analysis.
3. **Ephemeral encrypted bridge for the two originals.** A runner generated a temporary RSA-3072 key in its own process memory and published only the public key. Locally, each original MP4 hash and original encoded-audio hash were checked; derived PCM was encrypted with AES-GCM, with session/source/PCM-hash binding and RSA-OAEP key wrapping. The runner authenticated/decrypted it, checked exact PCM integrity and analyzed those original inputs.
4. **Results returned encrypted to the existing LOCAL recipient.** The long-term local private key never left this workspace. Runner recipient private key was not published or transferred. No playable reference audio, raw transcripts or source screenshots were added to public Git.
5. Two earlier audio runs failed on result serialization, not model/media authorization. The NumPy scalar/boolean bug was diagnosed, fixed and regression-tested; the final runs below produced actual authenticated results.

Successful model pass (eight exact encoded matches): https://github.com/adil-chandio/Monarch.Overall.Work/actions/runs/42452351652

Successful original-local bridge (remaining two): https://github.com/adil-chandio/Monarch.Overall.Work/actions/runs/42452846962

### Model/input limits — essential, not fine print

- Speech model: `Systran/faster-whisper-base.en`, CPU int8, English, beam size 5, word timestamps, no VAD filter; previous-text conditioning disabled in the executed code.
- Event model: `MIT/ast-finetuned-audioset-10-10-0.4593`, sigmoid class scores, top five labels per overlapping window. Scores are not calibrated certainty and windows do not localize a sound to one frame.
- **325.857 seconds** of derived audio input across the ten sources. Inputs were downmixed/resampled to 16kHz mono int16 for model inference. This is NOT original full-band stereo fidelity or separated voice/music/effects stems. Existing 48kHz stereo floating-point mix measurements remain a separate evidence layer.
- ASR may be wrong about proper names, technical terms, punctuation and word boundaries. The 44 low-score entries need review, but the other entries are not automatically verified.
- Model names/code/package metadata are recorded; do not assume independently pinned identical model-weight revisions between the two jobs. Speaker identity, actual TTS service/voice ID, exact music track/license, mix automation and SFX source assets remain unavailable.
- **No continuous perceptual listening is certified.** This route solves actual-audio model access, not every remaining auditory judgment.

## What the audio evidence contributes, without making things up

The timed semantic/narrative reading for **each of the ten sources** is in [NARRATION-BEATS-MODEL-ONLY.md](NARRATION-BEATS-MODEL-ONLY.md), including model-derived beat spans, direct visual cross-checks and concrete likely name/spelling errors. The per-case rates, timing ranges, low-score counts and broad labels are in [AUDIO-MODEL-EVIDENCE.md](AUDIO-MODEL-EVIDENCE.md). Full recognized word text/timings stay private for correction; public summaries do not reproduce complete source scripts.

The classifier ranked speech and music strongly across this corpus. Mechanism/story-aligned candidates include heartbeat-like audio in Hearts, siren-like classes in Surfer/Concert, and an explosion class in Balloon. These are **model candidates**, not confirmed heard effects or identified stems.

A useful failure warning: Balcony also received relatively high horse/whinny labels. There is no horse established by the reviewed visuals; that does NOT prove the sound is absent, but makes the classifier suggestion especially important to verify. It must NOT become a confident “horse SFX” annotation. The same caution applies to camera/spray/zipper-like labels elsewhere. Visual coincidence and model score do not replace listening.

ASR-derived full-clip word-entry rates vary roughly from 141 to 181 per minute, rather than establishing one universal narration-speed setting. These are counts of the model's word entries over whole clip duration, not a standardized linguistic count or measured TTS speed parameter. No narration speed, script or duration in the user's existing V14 film was changed.

### Three visual-caption / model-word spot checks

| Source position | Caption directly visible in opened native still | Nearby ASR output, model-derived | Honest interpretation |
|---|---|---|---|
| Hearts f360 / 12.012s | “pushing blood” | blood 11.44–11.90s; through 11.90–12.36s | Caption phrase persists into the model's next-word interval; do not assume strict single-word karaoke. |
| Splinter f690 / 23.023s | “so don't” | so 22.82–22.84s; don't 22.84–23.24s | Approximate phrase correspondence supported; not a fully verified word alignment. |
| Surfer f870 / 29.029s | “with determination” | determination 28.46–28.84s; adapting 28.84–29.96s | Caption/model timing discrepancy needs actual listening before any global offset is prescribed. |

These are three bounded checks, not an all-caption OCR/alignment pass. ASR boundaries can be inaccurate; the table does not establish a confirmed editing defect.

## Deeper motion inspection completed in this pass

Two additional contiguous ROI windows contain **130 opened source-frame positions**, including overlap with earlier work. These are not 130 newly unique full-frame inspections.

### 02-stomach: f240–f300 inclusive

PTS: **8.008000–10.010000s**. Scope: `native_pixel_ROI_sheet_opened`; source-pixel ROI `[100, 250, 600, 900]`.

f240–266: translucent stomach and blue branch-like explanatory structures stay in anatomical context. f267–273: a vertically blurred view transition moves toward the surgical-hands scene. f274–284: both gloved hands contact/support the organ as it visibly rises relative to the incision rim. f285–300: the supported organ is presented above the opening. Full native f274 and f284 were additionally opened, confirming context outside the crop. This resolves part of the previous uncertainty: removal includes an actual supported lift, not only a cut straight to an already-held prop. Exact attachment severing and surgical correctness remain unverified. The blurred transition is observed; a recovered camera velocity/transition plugin is not claimed.

### 05-surfer: f875–f943 inclusive

PTS: **29.195833–31.464767s**. Scope: `native_pixel_ROI_sheet_opened`; source-pixel ROI `[100, 250, 700, 1050]`.

Every ROI frame f875–943 was opened across eight labeled sheets. f875–882: torso rises further from the previously inspected low crouch while the remaining hand lifts/extends for balance. f883–906: the body holds a bent-knee surfing stance; hands/fingers and arm presentation change subtly rather than freezing into a rigid figurine pose. f907–943: stance continues with small body adjustments while foam and wave patterns evolve around the board. The previously opened f866–874 therefore connects without a frame gap to the final source frame at f943, but full-still scope applies only to f866–874; the remainder is ROI scope. No observed new hard cut within this final action. Board/foot relationship is visually persistent; world-space foot sliding, hydrodynamics and collision accuracy remain unmeasured. Caption changes are visible at f883 and f907 in the opened sequence; they are not treated as verified speech timing.

### Craft conclusions strengthened or corrected

- **Stomach:** the earlier f240/8.008s 1Hz note was also made more precise: blue branching overlay across the transparent stomach, rather than assigning it to neighboring structures. The new sequential inspection confirms hands lifting the organ relative to the opening. The earlier bounded observation of an already-held organ was incomplete, not proof that the lift was absent. Actual attachment severing still is not certified.
- **Surfer:** f866–943 now has no gap in the inspected action sequence, but mixed scope: first nine frames as full native stills, remaining frames as ROI. The rise develops into a held bent-knee balance with secondary arm/hand changes; foam/wave motion continues around it. Do not turn this into a claim of physical simulation, zero sliding or every-frame whole-scene review.
- **Narration and image need semantic coordination, not always literal repetition.** Splinter's cautionary phrase accompanies a removal action. This is more specific than a rigid rule that every spoken verb must be illustrated at its precise word boundary.
- **Held states can carry meaning.** Organ support, rescue support and surfing balance remain useful even when the main pose changes little. More orbiting, more cuts or louder audio alone would not address the user's rejected-quality concern.

## Still not completed — explicit acceptance gate

The 9,200 unopened source positions, whole-frame details outside the opened ROIs, all other micro-contacts/cut boundaries, continuous perceptual listening, human-corrected word alignment, exact SFX onsets/offsets, music identification/structure, stem-level ducking and phase/stereo judgment remain uncompleted or unavailable. Exact renderer/lens/rig/light/material-node recovery is not possible from rendered footage alone.

For the AI edition, the measured near-white video tail is unchanged. The original-local ASR did not recognize a final one-word response after the setup phrase. This is NOT proof that no response/noise exists in the actual sound; it cannot justify inventing an answer, intended loop or cause of the white tail.

No “10 completed forensic studies,” perfect recovery, zero flaws or guaranteed million views is claimed. The new achievement is a functioning ten-source audio-model route and more exact motion evidence, with honest scope preserved.

## Files and preservation

- `visual-observations.json`, `visual-review-status.json`, `manual-coverage.csv`: explicit visual attestations, exact PTS and deduplicated 9,772-row scope ledger.
- `audio-model-summary.json`, `AUDIO-MODEL-EVIDENCE.md`: public derived metrics/candidate labels, not full transcripts.
- `reports-private/reference-forensics/zack-ten/audio-models/combined-ten-audio-model-results.json`: private merged raw model evidence; per-case narration-word CSVs and event-window JSONs alongside.
- `refs/research-audio-models/` and `refs/research-audio-bridge/results/`: encrypted model-result transport and nonsecret integrity/provenance manifests.
- `refs/research-audio-bridge/`: public ephemeral recipient + encrypted derived PCM + provenance binding. Receiver private key was runner-memory-only, not recoverable from these public files.
- Original full references remain encrypted in `refs/research-transfer/`, with the long-term private key local/ignored. Never publish or delete that local key.
- Source-native third-pass PNGs/contact sheets are in the ignored `.cache/reference-forensics/zack-ten/`; they can be regenerated using the exact source frame IDs/ROI extraction script. Small notes/ledgers are mirrored in the ignored persistent private research directory.

Source-cohort caveat remains: nine corroborated creator-account X editions and one publisher-linked Facebook edition, NOT the earlier fixed YouTube-ID cohort, source projects, proven highest original resolution or a newly verified million-view cohort.

## Research checks

**29 focused tests passed** across source-access guards, authenticated transfer/tamper rejection, NumPy serialization, model-only packaging flags, frozen first/second-pass evidence scopes and current ten-input/visual-coverage/provenance checks. These checks protect record integrity; they are NOT creative acceptance, a human-corrected transcript, perceptual listening or proof of flawless animation.
