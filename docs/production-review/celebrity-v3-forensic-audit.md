# Celebrity-life 3D v3 — independent viewer and production audit

## Scope and evidence

Reviewed the delivered `celebrity-story-third-person-3d-v3.mp4`, not an imagined future edit. Evidence: a successful full-file decode (1,440 video frames; 60.00 s), visual inspection of 60 one-second samples, and 6-fps samples in seven one-second windows starting at 3, 10, 14, 27, 36, 44 and 52 s. Earlier v3 stills and the renderer, script, mixing code and sampled table-clearance audit were also inspected. One sample per second is **not every frame**. No human audio listening was performed; the audio findings below are based on the actual mux script and measurements, not a claim that the performance or sound quality was heard. The alternate voiceover is a separate, unsynchronised audition/proposal, not a finished mix.

## Bottom line

**The v3 is a genuine animated 3D, third-person improvement over v2, but it does not yet reach the user's desired premium cinematic, believable, emotionally engaging level.** The removed table crossings, more legible prop positions, actual rigged characters and calmer grading are progress. But it still plays like a dressed game-engine blocking pass: limited staging, stiff generic performances, repeated waves, sparse red-carpet environment, very literal voiceover and minimal designed sound. Better resolution alone will not solve those problems. The scenes need new actions, closer contact work, character-specific acting and a real sound/edit pass.

### Quick creative scorecard (subjective production assessment, not measured metrics)

| Area | Assessment / 10 | Why |
|---|---:|---|
| Concept / hook | 4 | A celebrity's private/public contrast is usable, but the opening is an ordinary static room and call, without a strong visual question or emotional promise. |
| Story / pacing | 4 | Clear time-of-day arc; mostly chronological description, no obstacle, reversal or escalation, long holds and repeated carpet beat. |
| Staging / art direction | 4 | Table issue improves; empty floors, generic furnishings, simple plants and featureless event walls make scale and wealth unconvincing. |
| Character / acting | 4 | Textured rigged humans and wardrobe changes help, but the smile/blink controls and recycled mocap do not supply specific intention or emotionally legible eyelines. |
| Action / physical contact | 3 | Better placement than v2; hands are not actually gripping props, cup/mouth contact and foot planting remain approximate, and the fan interaction is only a wave. |
| Camera / edit | 4 | Stable compositions and shot changes are understandable, but repeated wide-to-medium coverage and small uniform pushes are predictable. |
| Lighting / image finish | 4 | Controlled warm/cool palette and AgX; little motivated contrast, edge separation or environment complexity. 3-sample denoising can soften detail. |
| Sound design / music | 2–3 provisional | The code creates a minimal synthetic mono bed, clicks and noise bursts rather than a layered scene-based cinematic soundscape. Listening is needed to evaluate the result. |
| Delivery integrity | 7 | Full decode, 960×540 at 24 fps and 60 s; not a quality score or a collision guarantee. |

## Technical facts

- Video: H.264 High, 960×540, 24 fps, 1,440 frames, ~613 kb/s video stream, yuv420p. Deliberate letterbox inside image further reduces active picture height. Full output duration 60.00 s; decoded successfully.
- Audio: AAC, mono, 48 kHz, ~159 kb/s. FFmpeg volumedetect reports mean −16.7 dBFS and sample peak −1.3 dBFS. These are **not integrated LUFS or true peak**. A mono master cannot demonstrate a stereo surround-like soundstage.
- Render: Cycles, three samples per pixel, denoising, AgX medium-high contrast. Camera focal lengths vary roughly 36–55 mm, but every cut uses essentially the same small eased position offset: +0.13 m X, +0.18 m Y, +0.025 m Z. Easing is helpful, but identical drift is not motivated camera direction.
- Sound bed source: four sine tones at 55/82.407/110/164.81 Hz, a synthetic 85 Hz pulse every 0.75 s, exponential noise bursts at transitions, and eleven synthetic shutter noises. Eight recorded narration cues are mixed with this bed and loudness-normalised by the script. No recorded room tone, realistic dialogue/crowd, tactile Foley, composed orchestration or stereo stems are present in that code. Nothing here proves how they sound subjectively.
- Foot/toe-to-table XY-AABB check: 0.25 s spacing, minimum sampled landmark separation 1.2085 m and no violations at a 0.10 m proxy. It checks neither the full character meshes nor collisions with every prop or environment object.

## Scene-by-scene and shot-by-shot audit

Times are editorial cue boundaries from the actual renderer; individual frames may land on the nearest 1/24 s. Observations below refer to sampled frames, not an assurance that all intervening frames are clean.

### 00.00–03.50 — Apartment / phone wide
**Viewer:** We understand a man is in an upscale-looking room, but not who he is or why we should care. At 0–1 s he is simply standing; neither the incoming call nor stakes are established by a visual insert. Sofa and skyline indicate location, yet the clean, oversized room and repetitive windows make it feel constructed. **Animation:** hand rises toward the head; no visible motivated pickup or screen interaction. The previous table-through-leg defect is not apparent in the checked v3 frames. **Camera/light:** static-feeling medium wide with a tiny forward drift; warm consistent fill has limited sculpting. **Priority:** start on an unmistakable buzzing phone or a private gesture, establish character identity through environment and show a motivated reach; don't add fake sensational stakes.

### 03.50–07.20 — Phone closer
**Viewer:** The upright phone now reads better near the ear; some fingers, wrist and device still look aligned by proximity rather than convincingly holding it. A listener's attention needs either a reaction or a reveal, not just a held pose. **Animation:** no evidence of finger-specific grip, cheek clearance or lip/dialogue acting. Motion is a stock `Phone_Rig` sampled over 150 action frames. **Direction:** use a hand/prop rig with constrained fingers and verify ear/face clearance through the whole move; add a subtle eye focus shift and responsive pause. A second angle must add information, not only scale.

### 07.20–10.60 — Coffee wide
**Viewer:** The cup is more readable than the old large cylinder and the table no longer blocks the legs in the reviewed samples. However the cup seems to appear already in the hand; there is no establishing placement, pickup or weight. **Physics:** an authored hand-relative offset is not a contact solve; liquid stays decorative. **Direction:** show pickup from a plausible surface, wrap fingers at handle or body, align the rim to mouth, then lower and place it; keep liquid level/gravity coherent or avoid showing a problematic interior.

### 10.60–13.50 — Sip closer
**Viewer:** The cup approaches the mouth, but the hand and rim are small and facial contact can still look approximate. The action takes multiple seconds with little story development. **Direction:** use a 3/4 profile, physically believable elbow and wrist arc, one reaction beat and a clear motivated transition. Check contact at every frame around the sip, not only at 1 fps.

### 13.50–16.80 — Corridor wide
**Viewer:** The actor starts moving, a helpful change in pace, but the corridor is an empty plane and the walk feels like a loop rather than leaving a location. There is no door or architectural route that sells the transition. **Animation:** reused `Walk_Rig`; root motion is compensated but planted feet and gait/camera relationship are not physically solved. **Direction:** author a destination, add foreground/parallax, check foot locks and stride; use cut on directional movement.

### 16.80–19.70 — Corridor medium
**Viewer:** A tighter view shows the face and outfit but is almost the same action rather than a new idea; voice says outside quiet won't last without a visual buildup. **Direction:** use reflections of approaching photographers, a doorman or an elevator/exit indicator as a visual bridge; let anticipation increase before the cut. Keep the celebrity fictional.

### 19.70–23.50 — Carpet approach
**Viewer:** The suit and red carpet communicate event, but venue reads like a blank interior with a strip of red and a barrier. A single visible attendee in many samples and wide empty floor undercut the claimed crowd and excitement. **Animation:** motion switches from walk to wave at 23.5; different skinned background characters are an improvement over v2's block figures, but sparse background and repeated wave animation limit realism. **Direction:** motivated entrance, event branding, layered photographers/phones at varied depths and a wider-to-close visual crescendo; balance readable subject against crowd density.

### 23.50–27.60 — Wave medium
**Viewer:** The wave communicates acknowledgment, but it is generic and held for much of the shot; no reaction close-up or reciprocal action makes it meaningful. The lens doesn't show a clear individual being acknowledged. **Direction:** use an eyeline match, one meaningful fan reaction and a distinct action beat; avoid deploying the same wave twice later.

### 27.60–31.80 — Studio two-shot
**Viewer:** Both characters now turn toward one another and no obvious table crossing is visible in the checked samples. This fixes a major staging fault. Yet both stand rigidly between unoccupied chairs, in a set with sparse furniture and no readable microphone or production team; “conversation” is asserted more than dramatized. **Animation:** torso/root rotation is not eye contact, turn-taking or conversational listening. **Direction:** establish seating or a plausible standing interview setup, clear facing/eye-line, gestures with pauses and reactions, and show a recorder or unobtrusive lav.

### 31.80–36.40 — Studio closer
**Viewer:** Closer composition improves readability; one performer can be partially cropped, and no reaction/reverse shot sells an actual exchange. The broad facial changes are too subtle to carry the scene. **Direction:** motivated shot/reverse-shot across a consistent axis, interviewer asks/gestures, celebrity listens and responds; face and hands need authored timing rather than perpetual generic talking.

### 36.40–40.20 — Fan / carpet wide
**Viewer:** Moving the fan behind the rail clarifies separation, but the same pink-shirt character also appeared as studio guest, risking a confusing identity/location jump. A wave from across an empty barrier does not visibly establish waiting or personal connection. **Direction:** distinct cast/wardrobe and fan identity; show waiting, mutual eye contact, then acknowledgment. If interaction is only a wave, don't imply a handshake or autograph.

### 40.20–44.30 — Fan closer
**Viewer:** More legible framing but hero and fan remain separated and reaction is small. No clear shot of the fan receiving the gesture. **Direction:** isolate fan's reaction, show a reciprocal gesture, then let the celebrity return to event; verify no arm/rail intersections during movement.

### 44.30–48.20 — Second carpet wide
**Viewer:** We return to nearly the same carpet coverage and repeat the wave; energy falls where escalation is needed. Sparse crowd, identical environment, and broad neutral wall don't suggest press pressure. **Direction:** compress or replace this beat with a meaningful second action, e.g. a photographer's request and the celebrity choosing to pause. Coordinate practical flashes and reactions, not random visual noise.

### 48.20–52.20 — Second wave close
**Viewer:** Framing is clean, but another nearly identical wave is not fresh storytelling. **Direction:** use a short reaction, glance, turn and exit instead; reserve a held moment for the emotional contrast that follows.

### 52.20–56.20 — Return home wide
**Viewer:** Cooler sky makes a different time of day readable, and table no longer occupies his path in checked frames. A sudden cut/wardrobe change makes the return feel like teleportation. The line “the door closes” is not supported by a visible door closure. **Direction:** show an entry/door action or rewrite the claim; motivate lighting/time shift through a clear transition.

### 56.20–60.00 — Quiet close / ending
**Viewer:** Reflective pose gives closure, but it is a generic hand-to-face hold, with no specific emotional change and no strong final visual. **Direction:** include a prop or action that links back to the opening, then a quiet look/settle; give final image and final line breathing space rather than holding a stock pose.

## Script-to-picture inconsistencies

1. “Phones rise, and strangers call his name” is stronger than evidence: visible crowd is sparse, and there is no identifiable name shown or documented spoken crowd. Either add scripted/licensed distinct crowd calls and show phones, or describe attention more generally.
2. “Conversation begins” is supported only by two gesturing figures; no audible on-screen exchange is established by the text/mux code. Show turn-taking or narrate an appearance instead.
3. “Someone who has waited to meet him” claims waiting that the film does not establish. Show waiting before the wave; otherwise say someone is waiting beyond the barrier, not claim a meeting.
4. “The door closes” has no visible door action. Film it in the next version or omit it.
5. A wave matters to a fan is a reasonable emotional interpretation, but the present shot has insufficient reaction evidence to make the audience feel it.
6. There is no real person portrayed or factual celebrity routine established; keep all names, details and claims fictional.

## Voiceover proposal — separate asset, not a new video

The selected audition voice was used to generate `deliverables/celebrity-story-voiceover-proposal.mp3`. It is an English masculine narration sample, 50.52 s file duration, 24 kHz mono MP3 at 32 kb/s, produced as one uninterrupted take. It is **not synced to the 60 s film** and the performance has not been human-listened to here. Before production, audition the delivery, revise any unnatural emphasis, generate separate high-quality cues, align to picture and leave breathing room; do not stretch it blindly across the timeline.

**Proposed text:**

> Before the world sees the star, his day is already moving. One call, and the quiet begins to slip away. A few stolen minutes with a coffee. Then it is time to step outside. In a moment, a private morning becomes a public performance. At the event, phones go up, lights flash, and every gesture is noticed. But the work does not stop at the carpet. In the studio, another conversation, another story to tell. Then, beyond the barrier, someone waits for just one moment. A wave takes a second. For a fan, it can mean much more. And when the lights finally fade, the man behind the image returns to the quiet he left behind.

**Suggested edit cue map for a future re-record, not the timings of the uninterrupted MP3:**
- 00.0–07.2: “Before the world sees the star, his day is already moving. One call, and the quiet begins to slip away.”
- 07.2–13.5: “A few stolen minutes with a coffee. Then it is time to step outside.”
- 13.5–19.7: “In a moment, a private morning becomes a public performance.”
- 19.7–27.6: “At the event, phones go up, lights flash, and every gesture is noticed.”
- 27.6–36.4: “But the work does not stop at the carpet. In the studio, another conversation, another story to tell.”
- 36.4–44.3: “Then, beyond the barrier, someone waits for just one moment.”
- 44.3–52.2: “A wave takes a second. For a fan, it can mean much more.”
- 52.2–60.0: “And when the lights finally fade, the man behind the image returns to the quiet he left behind.”

Cue durations are targets only: individually render, time and revise as needed. Pace and delivery should be intimate and curious at first, lift naturally through the event, and fall to a quieter, sincere close; avoid a constant trailer-voice or exaggerated urgency. The current picture still needs more crowd and fan-reaction coverage to earn the stronger claims.

## Sound blueprint for the next production — recommendations, not sounds already delivered

1. **00–07 call:** subtle room tone and distant city, a specific phone vibration/chime, cloth/hand movement; close, intimate music entry rather than an impact at frame one.
2. **07–13 coffee:** ceramic touch, gentle liquid and sip, surface contact if shown. Keep small sounds dry/near; no generic whoosh on every cut.
3. **13–20 transition:** footsteps matching actual footfalls/material, elevator/door only if pictured, room tone opens into muffled public activity. Build anticipation with a restrained rise.
4. **20–28 event:** layered stereo crowd beds, discrete realistic shutter clusters tied to visible flashes, footsteps and barrier handling. Keep distinct foreground moments; do not invent intelligible names unless written and licensed.
5. **28–36 studio:** quieter controlled ambience, clothes and mic handling, intelligible conversation only if deliberately scripted. Reduce music under speech.
6. **36–44 fan:** event bed pulls back momentarily for the gesture; a specific reciprocal sound/reaction if shown. Avoid canned cheers that imply a large unseen crowd.
7. **44–52 event:** return of crowd and a small musical lift, not a second identical crescendo. Build to a motivated exit.
8. **52–60 ending:** background dies away through an actual transition; room tone and a resolved musical tail give contrast. A door sound must correspond to a shown/implied door, not force a false claim.

**Mix plan:** deliver separate narration, score, ambience and effects stems; dialogue intelligibility first, EQ competing music around vocal presence, automate levels and use short reverb matched to each space. Produce a stereo master and check mono compatibility; measure integrated LUFS, loudness range and true peak with an EBU R128 meter. A sensible draft target for online video is around −14 LUFS integrated and ≤−1 dBTP, but prioritize intelligibility and platform requirements rather than claiming a number without measurement. Human listening on headphones, phone and speakers is essential. No music or Foley library licenses have yet been selected; only use original material or assets with verified commercial, sync and redistribution rights, attribution and source records. Avoid using a famous person's likeness or imitating a recognizable voice.

## What would move the next version toward the target

1. **Story first:** rewrite around a specific fictional emotional contrast, create a visual hook within 0–3 s, remove the redundant second wave and earn the quiet ending with a visible action.
2. **Storyboard and previz:** a beat sheet, overhead blocking, animatic and shot list with clear camera motivation and screen direction before rendering.
3. **Performance/contact:** unique acting beats, deliberate gaze, facial changes, hand/finger constraints, cup and phone pickup/putdown, per-frame contact and foot-lock review. Use simulation only where it improves a shot and verify the results.
4. **Art/lighting:** richer but believable apartment, corridor, real venue and studio, proper scale, more background depth and motivated practical sources; varied close/wide lenses, foreground layers and controlled contrast. Avoid assuming more props automatically equal premium design.
5. **Sound:** source or create properly licensed score, Foley and room/crowd recordings; mix to picture with the selected narration and real transition timing, then listen on multiple devices.
6. **QC:** decode all frames, inspect all cuts and fine 6–12 fps contact windows (and every frame at critical collisions), review sound by listening, meter loudness/true peak, check licensing, compare against the approved animatic and explicitly record unresolved defects. The current landmark check alone cannot certify collision-free animation.
