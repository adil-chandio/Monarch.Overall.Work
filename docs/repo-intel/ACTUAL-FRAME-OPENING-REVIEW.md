# Original-file forensic review: first minute, plus all frames of first 5 seconds

## What was actually inspected

Source: user-provided `videoplayback.mp4`; source SHA-256 `86222809c190003f6562ab96ef89b28b831a07bfa364496931458cccd14b21d6`. File was transferred encrypted to a local cache, verified against that hash, and decoded with FFmpeg 9.0.2. It is 640×360 H.264, nominal 30 fps, with 44.1 kHz stereo AAC. The source media and extracted images were **not committed** to this public repository.

- **0:00–0:05:** visually examined all 150 decoded frames on six sequential contact sheets (5×5, scaled to 240×135). Start-of-file FFmpeg timestamps advance 1/30 second; displayed times below are approximate decoded-frame PTS.
- **0:00–1:00:** additionally inspected 60 frames selected as frames 0, 30, 60, … 1770, on four sheets scaled to 320×180. Each row below describes the exact integer-second sample only; events between samples may be missed. The 5-second all-frame pass above takes precedence where applicable.
- **Remainder 1:00–67:17:** not independently frame-inspected in this pass. Earlier Gemini-generated descriptions span the duration but are **not source-frame verification**. No audio was listened to; narration, dialogue, music, SFX and timing remain unverified.

## Shot and motion: all 150 frames of the opening

| Approx. source time/frame | Directly visible |
|---|---|
| Frames 0–2 / 0.000–0.067 | Black image. |
| Frame 3 / 0.100 onward | Farm establishing image fades in from darkness; fixed layered house, barn, silo, fence and sunrise composition. |
| By ~0.5–0.7 s | Small time label appears at bottom left; “DAY 1” is at top left. Background stays compositionally similar through frame 60 / 2.000 s; fine changes at this scaled resolution cannot be quantified. |
| Frame 61 / 2.033 | Exterior changes to barn interior: character in red-and-white cap, pale clothing, black cow, window and vertical wood walls. |
| Frame 110 / 3.667 | Switch to close-up of character’s face, initially simple eyes and smiling mouth. |
| Frame 118 / 3.933 | Expression changes: circular eye shapes enlarge and mouth becomes a small oval; reaction reads visually as surprise. |
| Frame 146 / 4.867 | Switch from face close-up to exterior barn/farm composition. |

A 30 fps video container does **not** establish that character drawings or poses are independently animated 30 times per second. Static holds, background details and foreground effects may coexist. At this resolution and scale, these sheets cannot prove the authoring technique or every subtle motion.

## Integer-second visual log, 00:00–00:59

| Second | Visible at sampled frame |
|---:|---|
| 00 | Black. |
| 01 | Sunrise farm establishing composition; house, barn, silo; small day/time labels. |
| 02 | Farm exterior remains visible. |
| 03 | Barn interior, cap-wearing character and cow. |
| 04 | Close-up surprised expression. |
| 05 | Farm exterior, barn and silo. |
| 06 | Exterior; expanding ring graphic over distant skyline. |
| 07 | Ring graphic remains over the landscape. |
| 08 | Wider valley view with hills, sunrise and small buildings. |
| 09 | Wide valley continues. |
| 10 | Dotted distance marker and “0.5 MILE” become visible. |
| 11 | Distance marker remains. |
| 12 | Farm exterior; cap-wearing figure near barn. |
| 13 | Same setting; figure has shifted left relative to barn. |
| 14 | Figure further left on farm foreground. |
| 15 | Farm exterior and small figure; no large foreground head yet in this sample. |
| 16 | Large out-of-focus back of capped head in foreground, small distant figure on field. |
| 17 | Foreground head and distant figure remain. |
| 18 | Similar over-shoulder composition. |
| 19 | Wider field: two small figures separated horizontally. |
| 20 | Two figures on field. |
| 21 | Two figures in different positions. |
| 22 | Two figures; rear figure closer. |
| 23 | Enlarged green-headed figure; “TOO STIFF” label. |
| 24 | Similar isolated figure and label. |
| 25 | “TOO STIFF” and “TOO FAST” labels appear around the figure. |
| 26 | Return to two figures on field. |
| 27 | One figure lies horizontally on ground; another remains upright. |
| 28 | Three green heads/figures emerge low in grass. |
| 29 | Three figures more visible above grass. |
| 30 | Three upright figures. |
| 31 | Three figures remain in field. |
| 32 | Three figures remain. |
| 33 | Cattle grouped near a fenced area. |
| 34 | Cattle grouping remains. |
| 35 | Cattle grouping remains. |
| 36 | Character face close-up; angular eyebrows and downturned mouth. |
| 37 | Similar worried/angry expression. |
| 38 | Same close-up. |
| 39 | Hand-held phone enters composition, with red “EMERGENCY ALERT” header. |
| 40 | Phone alert text partially populated. |
| 41 | More alert text visible. |
| 42 | Phone remains; text warns against physical contact with someone showing extreme aggression/confusion (small text should be checked against native frame before exact transcription). |
| 43 | Character close-up returns, large white eyes and angular eyebrows. |
| 44 | Same character reaction. |
| 45 | Reaction continues. |
| 46 | Reaction continues. |
| 47 | Reaction continues. |
| 48 | Wide valley with multiple buildings and several thin circular overlays. |
| 49 | Similar wide view; circular overlays in different positions. |
| 50 | Valley and multiple rings. |
| 51 | Valley and multiple rings. |
| 52 | Valley and multiple rings. |
| 53 | Farm exterior; small character near barn. |
| 54 | Same farm composition; character shifted. |
| 55 | Large soft-edged dark forms with glowing eye-like dots in foreground, framing small character. |
| 56 | Foreground forms remain; character farther left. |
| 57 | Foreground forms and small character remain. |
| 58 | Similar layering, character remains between foreground forms. |
| 59 | Farm and foreground forms persist; character near house. |

## Production reading — observation vs inference

- **Observed:** Consistent limited-palette farm environment, black letterbox bands in source, persistent day label in many frames, a foreground/background depth arrangement, graphic rings, text overlays, wide-to-close changes, and a character face changing expression via clearly different shapes.
- **Plausible interpretation, not established:** repeated backgrounds and small local changes suggest an economical layered 2D workflow. Source software, whether backgrounds/characters are hand-drawn, AI-generated, rigged or composited, and actual keyframes are unknown.
- **Editing lesson:** the opening shifts scale between wide place, interior activity, emotional close-up and abstract distance graphic. These are verified visual modes in the opening, not a verified music/SFX rhythm. An automatic shot boundary or full edit count has not been measured.
- **Writing hypothesis:** the visual sequence moves from ordinary farm setting to reaction, distance, pursuit and warning. Exact spoken language, script structure and cause/effect require audio transcription and listening, not guesswork from pictures.
- **Sound measurement:** FFmpeg `volumedetect` on the first 60 s reports `mean_volume -18.1 dB` and `max_volume -0.0 dB` on its decoded 16-bit measurement. This is not LUFS, a true-peak reading, stem separation or identification of narration/music/SFX. No sound names or music cues are verified here.

## What remains

Full 67-minute every-frame review, second-by-second visual verification outside the first minute, independent audio listening and transcription, shot-length analysis, and multi-video/channel research are all incomplete. The 90-second screen recording in the shared folder has not been reviewed during this pass. Script tool `scripts/forensic/opening_contact_sheets.py` can recreate the opening contact sheets with a local copy and FFmpeg; outputs should stay private rather than being committed.
