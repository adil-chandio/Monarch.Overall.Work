# Clean V8 plan and metadata

## Why V8 exists

The delivered V7 MP4 was rejected after its GitHub link. The user's exact feedback: too many things
were stuffed into the clean version and the main content was not visible; remove them all and rebuild
every element by watching the linked Short.

The reference link is `https://youtube.com/shorts/08-ocSDpt7o?si=5F7y2w9H6Sso5bQK`
(`Ranking Most Impressive Moments Ever #shorts`, `onlymeamro`, 60s; a same-title TikTok original by
`thatoneamro` was also found). This environment retrieved oEmbed/watch metadata but could not play
the Short or extract its frames. Therefore **no exact visual reproduction of that video is claimed**.
The user then said to proceed by whatever means, so V8 is built from the unambiguous part of the
feedback: make it clean, make the main footage visible.

## What was removed from V7

- Two-line color-split hook and `WAIT FOR #1`
- Seven dark rank rows / plates / labels
- Right-side heart, comment, save, share, remix icons
- `@Monarch-Cam` handle line
- Comment bubble `Wait for #1 - which one is your rank?`
- `Subscribe` button
- Bottom caption and `HOME / DISCOVER / INBOX / PROFILE` app navigation
- Top app chrome (`12:20`, `For You`, `Following`, search icon)
- Payoff reaction text and emoji bubble
- Full-frame dark gradient and white transition flash

Important distinction: the large central play button, phone status bar, file header, scrub bar and
volume/fullscreen controls visible in the rejection screenshot are **phone/gallery player chrome**,
not baked into the MP4. They are not drawn by this renderer and cannot be removed from the MP4.

## What V8 draws instead

- Blurred full-frame background with a soft ambient luminance lift (no black empty half).
- Sharp, uncut, aspect-preserving source frame centered on that background. No crop, no zoom,
  no letterbox, no V6 `cover_crop()`.
- A slim top rank strip `7 6 5 4 3 2 1` with the active rank highlighted (y=150..230).
- A small translucent moment badge with `#rank` and the moment label (y=1650..1738).
- A thin timeline progress line (y=1760..1765).

All three elements are inside the platform safe area and **outside** the central content region
`[0, 400, 1080, 1520]`. Combined overlay bounding-box area is under 6% of the frame. The sharp
source band is completely unobstructed.

## Visual window correction after the first clean render

The first clean V8 render was technically clean, but the committed contact sheet showed two cuts
landing on non-moments: rank 6 opened on a black fade-in and rank 5 opened on a static
`Guion Original` title card. The runner's audio/motion score had picked those windows because they
were loud and continuous, not because they were funny.

The committed one-frame-per-second candidate contact sheets were reviewed, and two windows were
moved to the actual gag while keeping every audio gate unchanged:

- `quaker_scarecrow`: `0.0s` -> `3.0s` (scarecrow sits up / jumps into the breakfast scene).
- `caption_fail`: `75.5s` -> `80.0s` (presenters and the caption-chaos green-hat payoff).

`select_moments_v8.py` re-measures each override against the runner's own half-second RMS probe and
refuses it unless all 17 half-second blocks are above `-65 dBFS` with zero quiet blocks. The
`source_audio_audit_v8.py` step and the nine unchanged web gates then re-verify the actual muxed
audio, so the override cannot silently weaken the audio policy.

## Technical contract

- 60.0s / 1800 frames / 30fps / 1080x1920 vertical.
- Seven ranked moments, 7 -> 1, hard cuts only.
- Raw per-window native source audio only: no VO, music, SFX, bed, generated calls, AI audio,
  substitution or added layers. Nine unchanged web gates must pass.
- Per-title Commons API rights/social-origin verification, original SHA-1, restrictions and
  CC BY attribution recorded.
- Separate deliverable: `deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_CLEAN_V8.mp4`.
  V7 remains in the repo as rejected evidence; no same-path replacement.

## Not claimed

No exact reference match, no currently trending named-platform clips, no full legal compliance,
no human full-motion/native-audio listening, no creative approval/sign-off, no perfection,
retention, virality, 3x, likes/subscribes, same-path replacement or audience result.
