# Farm-survival stickman reference — production analysis and evidence register

## Scope and what “complete” can honestly mean here

The Drive folder contains `videoplayback.mp4` (01:07:17.718) and a separate 90.165 s screen recording. This report concerns **the long video only**, not a proven audit of the entire channel. The source was downloaded and its SHA-256 matched `86222809c190003f6562ab96ef89b28b831a07bfa364496931458cccd14b21d6`; no source video, audio or frame images were committed to the public repository.

**Work performed**

1. Local FFmpeg decoded every 30th source frame; 4,038 frame samples with recorded PTS cover 0–4,037 s at exact 1-second intervals. Pixel/RGB and difference metrics were saved for all of them. This is **sampled measurement**, not visual inspection of all 4,038 samples or of every encoded frame.
2. I visually examined a contact-sheet overview of **404 actual source frames**, one every 10 seconds from 0 through 4,030 seconds. These are 160×90 proxies; fast actions, tiny text and intervening edits can be missed.
3. I visually examined all **150 frames** in 0–5 s and all **90 frames** in 25–28 s, plus one actual frame per second through the first minute and 18 one-second samples from 67:00 to the ending. [Opening visual log](ACTUAL-FRAME-OPENING-REVIEW.md).
4. Every minute was submitted to Gemini in separate clips: 66 successes on the first pass and two successful retries. Those outputs are **model-generated and can be wrong**, not verified viewing. [Main pass](drive-video-coverage-pass.json) · [50:00–52:00 retry](drive-video-gap-retry.json).
5. The entire decoded audio was measured in 4,038 one-second mono RMS/peak bins; a separate approximate PocketSphinx speech-recognition pass returned text for all 68 one-minute clips; the output contains substantial recognition errors. No direct listening, sound-source separation or independently verified narration transcript is available.

**Do not interpret this as a flawless frame-by-frame/audio audit.** Video sampling and model output cannot establish exact motion across the full 67 minutes; no audio tool here independently identifies the music or sound effects. Channel identity, multi-video consistency, animation tool, production team, source artwork, music licensing and retention performance are unknown. The companion screen recording was sampled separately at approximately 3-second intervals: it shows YouTube Studio analytics for other Shorts, not an identifiable source-channel page for the long video. Its private analytics are not reproduced here and cannot establish the reference video’s performance.

[Per-second measured numerical evidence](drive-video-second-metrics.json) · [uncalibrated scene-change candidates](drive-video-scene-candidates.json) · [prior opening study](ACTUAL-FRAME-OPENING-REVIEW.md)

## 1. What the long video visibly contains

From actual ten-second samples across the whole source, this is a **long-form illustrated survival narrative** with recurring farm buildings and landscape; a recurring red-and-white-cap character; other stylized circular-face figures; on-screen day/time labels; radio and phone objects; inventories, quantities, diagrams and written rules; exterior, interior and infographic-style compositions. The end includes a visible “DAY 100 / THE END” card around 67:10. These are properties of this file—not proof of how every upload on the channel is made.

### Visual navigation map (verified samples, approximate source times)

| Range | Actual sampled visual anchors | What remains uncertain |
|---|---|---|
| 00:00–08:00 | Sunrise farm / barn / field and phone alert; ~01:10 screen/broadcast, ~01:20 failed-call graphic, ~02:00 water quantity, ~04:00 radio, ~06:00 door handle, ~07:40 diagrams. | Events between ten-second samples and actual sounds. |
| 08:00–16:20 | Liquid/quantity and livestock graphics; food/pantry, rain/farm, radio, diagrams and notebook; ~13:20 “DAY 13”; phone and tally marks later. | Whether each object is animated continuously; exact captions and narration. |
| 16:20–24:40 | Notebook, medicine icons, door, note/card, “DAY 30,” inventories, calendars, maps, water and “STAY / GO” graphics. | Precise narrative chronology, character intentions and exact on-screen copy. |
| 24:40–32:40 | Farm/field travel, sweat/water graphics, isolated house, pantry/radio, schematic effects, grain-elevator-like structures and more characters. | Identity and motivations of characters; any SFX or music. |
| 32:40–40:50 | Industrial/farm settings, dehydration-style charts, repeated bottle icons, faces, radio, route symbols, food inventory, agricultural supplies. | Story details from model outputs remain provisional. |
| 40:50–49:00 | Group scenes, calendar/notebook, farms, field figures, “DAY 60,” radio, binocular-like framing and maps. | Exact grouping of events, cut points and audio relationships. |
| 49:00–57:10 | Radio/clock graphics; stylized family/relationship diagrams, plans, farm, building/door and interior scenes. | Exact words, dialogue, and factual causality. |
| 57:10–67:17 | Repeated face close-ups and graphic text; farmhouse and figures; later note, radio and return to farm motifs; 67:10 end card. | Scene transitions between samples, end sound, and exact script. |

The sampled timeline is a **navigation map**, not a substitute for watching the source; the existence of a graphic at one timestamp does not prove how long it stays visible.

## 2. Writing and narrative design

### Observed structure

- **Time as a built-in structure:** day labels and eventual “DAY 100” ending are visible at sampled points. They segment a long scenario and make progress legible without needing a separate chapter introduction every time. Exact durations between every story day are not measured.
- **Recurring places and objects:** farm buildings, radio, phone, water and inventories recur across the overview. Their reuse builds continuity and gives the viewer reference points even when the camera shifts between character scenes and diagrams.
- **Opening grammar:** the actual 0–60 s frames progress from ordinary farm setting → surprised facial reaction → distant figures → labelled abnormal motion → phone warning → ominous foreground figures. The independently generated opening ASR suggests second-person narration, but precise wording remains unverified.
- **Question → decision → consequence** is a plausible writing model from the combined overview and Gemini minute outputs: explain a survival constraint, visualize options/resources, then return to the character or wider threat. It is an interpretive framework, not a measured audience-retention mechanism.
- **Closing/callback hypothesis:** late radio and farm imagery resemble objects at the opening; contextual connection is plausible, but its full story meaning needs a verified transcript/listening pass.

### Practical script observations

1. The time/day counter provides orientation and a built-in promise of progress.
2. Threat is introduced through specific visual details, not only a generic danger label: the sampled 23–25 s frames display “TOO STIFF” / “TOO FAST” against one figure.
3. Practical information can be externalized as an icon, graphic comparison, list or map instead of forcing characters to explain everything in dialogue.
4. Repeated props such as the radio can carry an ongoing question across chapters, while inventories establish concrete limits.
5. Long-form descriptions should not be treated as instructions for real survival; no medical, food-safety or emergency advice from the film was fact-checked here.

These are storytelling analyses, not evidence that the video was written by a particular author or that any particular hook improved retention.

## 3. Art direction and compositing

### Direct visual observations

- **Characters:** circular dark faces, simple white facial features, colored headwear, small body shapes and readable emotional face changes. Clothing and hair distinguish characters across low-detail shots. Expression close-ups can be visually large even when the full-body figures are small.
- **Environment:** farm house, barn, silo, interior rooms, fields and grain-elevator-like settings recur; distant tree silhouettes, hills and sunrise/sunset gradients supply depth. Wide shots often reserve much of the frame for the setting rather than the small figure.
- **Screen treatment:** dark letterbox-style bands are visible in the source opening; graphic sections use near-black/dark backgrounds with light text and colored accent icons. We did not measure safe areas, actual fonts or the project canvas configuration.
- **Depth cues:** foreground characters or dark shapes partly obscure a background farm in the opening; background blur, hazy landscape, lighting gradients and differently sized objects create visual separation. This establishes appearance, not a specific parallax setup or true 3D.
- **Information design:** isolated icons, numerical comparisons, flow/route diagrams, checklists and short all-caps text cards visually reframe the story as a survival system. The ten-second proxy cannot establish font family or exact text at every timestamp.

### Ending: directly inspected one-second samples

- **67:00–67:01:** a hand holds a note; visible lines include “WATER AND PEOPLE” and “MILL CREEK ROAD”; an additional small label says “YOUR HANDWRITING.” The text is visually sampled, not a verified spoken quote.
- **67:02–67:03:** smiling cap-wearing face, followed by closed door.
- **67:04–67:07:** bright light enters through the opening; by 67:05 three small figures are visible against the bright doorway. Their identities and relationships cannot be established from these frames alone.
- **67:08–67:17:** “DAY 100” then “THE END” appear over the doorway; the final sampled frame is at 67:17 and the source ends at approximately 67:17.718. Prior Gemini output invented events continuing to one minute within this 17.7-second clip; those extrapolated events are invalid.

### Engineering interpretation, not proof of source method

The repeated locations, props, face shapes and layout templates are **consistent with an asset-reuse/layered workflow**. A practical replication study could catalog reusable backgrounds, separate character-expression states and props, but no project file was available: we cannot say the original used After Effects, Blender, a game engine, procedural graphics or AI tools. Identifying a look as “2D” does not prove how it was authored.

## 4. Animation and editing under the microscope

### Verified 30 fps frame windows

- **0.000–0.067 s:** black frames; visible fade-in begins at about 0.100 s.
- **2.033 s:** opening exterior changes to barn interior. **3.667 s:** changes to face close-up. **3.933 s:** face changes from smile/simple eyes to wide eye shapes and oval mouth. **4.867 s:** changes to exterior. These are decoded-frame observations at the available resolution, not editing-project cut metadata.
- **25.000–25.933 s:** isolated green figure changes leg pose while “TOO STIFF” and “TOO FAST” graphic labels remain. The scaled contact sheet shows changing poses, but does not prove animation rig, easing or number of unique authored drawings.
- **~25.967 s:** view changes back to two figures in the field. **~26.733 s:** foreground figure is upright; at **~26.767 s** it appears horizontal on the ground in the reviewed sheet. This is a striking one-frame visual change at 30 fps; whether this is intentional, a source-edit artifact or a decoding/seek effect is unverified.
- **~27.867 s:** frame composition switches to a lower foreground with three green figures emerging. These timings come from a seeked source window and should be checked against full-file PTS before claiming an exact edit decision.

### Editing measurement caveat

A full-resolution-time FFmpeg scan after downscaling to 320×180, with `scene > 0.30`, generated **429 scene-change candidates**. The median interval between candidates is **~5.05 s**, but this is **not the median shot length**: transitions, movement and thresholding alter detection. As a concrete false-negative example, the visibly observed 3.667 s face cut was not in the 0.30 candidate list, while 2.033 and 4.867 s were. The list is a review queue, not a verified edit list.

### Production-level reading

The available frames show a mix of held compositions, distinct face states, sparse character poses, moving graphics and large scene/layout changes. The apparent premium effect derives in part from *choice of framing, contrast, information hierarchy, recurring visual motifs and staged reveals*, rather than proving that every character is fully animated on every frame. This is an interpretation of the inspected samples—not a claim about the exact labor or technique used.

## 5. Narration, music, SFX and mix — clear evidence boundaries

- The source has an AAC stereo track; the separate model pass used a 24 kHz mono MP3 derivative and cannot assess stereo mix. The independent PCM pass covers the full duration in 4,038 windows of up to one second. The distribution of **mono 8 kHz downmixed RMS** has approximately 10th/50th/90th percentiles **−22.17 / −16.24 / −12.77 dBFS**. This is energy, not LUFS, source separation, perceived loudness or a measure of whether a sound is voice/music/SFX. The final audio bin is partial.
- Downmix can sum channels above 0 dBFS in floating-point; sample peaks are not true peaks. No claim of clipping, mastering quality or stem balance follows from those numbers.
- PocketSphinx returned approximate speech text for all **68 clips**, including the 17.7-second ending. It is **not verbatim**, and words were demonstrably misrecognized. Its rough story arc is consistent with a farm-outbreak narrative, resource decisions, a group, a radio mystery, and a return/ending; exact dialogue, identity, and detailed chronology require verification. Transcribed source text was kept out of this public repository.
- An audio-only Gemini pass describes narrator, music and sound events in 68 minute clips, but its descriptions were not independently validated and contradict an overlapping pilot on music and voice characteristics. **Exact scream, footsteps, radio sounds, melody, music genre, transition cues, voice processing, BPM, track identity and cue timestamps are unverified.** An audio event classifier or language model alone would not substitute for listening and checking the waveform/stems.

## 6. What can be transferred into a production specification

The following is an **original workflow recommendation derived from observations**, not a claim about how the reference was produced:

1. Write a chaptered narrative first: establish time/place, a specific deviation, a rule or resource conflict, then a consequence and an unresolved question. Give each long chapter a legible progression marker.
2. Build a reusable visual system: limited environment set, characters differentiated by silhouette/color, expression states, prop library, day cards, diagram cards and controlled type hierarchy.
3. Make each sentence decide its own visual treatment: character action when emotion matters, wide establishing view for geography, diagram when relationships/numbers matter, object insert when a prop drives the plot.
4. Plan motion selectively and deliberately: pose-to-pose storytelling, foreground/background depth cues, accent graphics and carefully timed visual changes; avoid assuming all frames must contain full character animation. Test body mechanics and transitions on real frame references rather than copying any model-generated timestamp.
5. Audio must be its own spotting pass: verified narration transcript; music bed and changes; discrete effects; ambience; and moment-by-moment sync/mix review. No exact template can be honestly extracted from the audio until it is listened to.
6. Validate readability at the **actual reference resolution** (640×360), especially small text. The proxy frames show composition but do not justify claiming the original is high-resolution.

## 7. Remaining gaps

- The 4,038 numerical samples are not 4,038 individually viewed images, and neither they nor the two full-frame windows cover the ~121,000 encoded frames. Full-frame manual verification of the entire 67-minute source is not complete.
- Actual narration, SFX, music and mix have not been listened to. Automatic transcripts and Gemini sound descriptions remain unreliable hypotheses.
- Automatic transition candidates are not human-confirmed shot boundaries.
- The separate screen recording shows Studio analytics for other Shorts; it does not establish the identity or performance of the long-video source. Other channel videos require their own source inspection before channel-wide conclusions.
- Perfect accuracy cannot be guaranteed. Evidence classes above distinguish measured facts, visually inspected samples and inferences; recheck source frames/audio whenever a production decision depends on a precise claim.
