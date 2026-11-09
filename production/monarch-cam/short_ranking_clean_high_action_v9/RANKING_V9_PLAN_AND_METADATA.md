# High Action V9 plan and metadata

## Why V9 exists

The clean V8 MP4 passed its technical gates but was rejected after delivery because its clips were weak,
mostly static and ordinary. The user's exact correction asked for genuinely funny, interesting, hooked and
engaging clips in which something amazing, mind-blowing, eye-opening, hilarious or shocking is visibly
happening — movement, action or a payoff — not "kuch nhi." Older rights-cleared clips were explicitly
allowed alongside viral-style clips. The user declined to supply further reference frames and said to proceed
by whatever means.

The reference link is `https://youtube.com/shorts/08-ocSDpt7o?si=5F7y2w9H6Sso5bQK`
(`Ranking Most Impressive Moments Ever #shorts`, `onlymeamro`, 60s; a same-title TikTok original by
`thatoneamro` was also found by metadata). This environment retrieved watch/oEmbed metadata but could not
play the Short or extract its frames. Therefore **no exact visual reproduction of that video is claimed**.
V9 is a separate corrected high-action lane, not a same-path replacement of V4/V5/V6/V7/V8.

## Separate high-action scout lane

A dedicated 20-candidate Commons API rights/native-audio/motion scout and a second-pass 28-window 8.6s
payoff-window scout were run in CI. Their real runner contact sheets, composite sheets and JSON ledgers are
committed under `production/monarch-cam/short_ranking_high_action_v9/`. Automatic best-motion scores alone
were not used as final selection: several automatic windows landed on title cards, black frames, static crew
shots or already-frozen closeups. The committed 0.5s curated payoff contact sheets were inspected, and
`curated_selection_v9.json` locks seven distinct visible-action windows:

| Rank | Source | Source in | Visible payoff |
| --- | --- | --- | --- |
| 7 | `skate_paris` | 28.5s | Street skateboard flip and clean landing |
| 6 | `pacman_stunt` | 77.0s | Giant Sonic/Pac-Man projection reveal and game animation |
| 5 | `funny_hang5` | 13.5s | Two-rider mini-bike trick and visible wipeout |
| 4 | `teen_cliff_jump` | 0.0s | Immediate cliff jump and large overhead splash |
| 3 | `instant_freeze` | 47.0s | Bottle opened; ice crystals race through the liquid |
| 2 | `freestyle_bmx` | 40.5s | High-air BMX backflip in front of a crowd |
| 1 | `rope_jump` | 21.0s | 465m bridge free-fall, canyon rush and rope catch |

`select_moments_v9.py` rechecks every exact 8.6s window against the runner's own half-second RMS probe and
the curated direct native-audio/motion report. A window is refused if any of its 17 half-second blocks is
quiet, if direct native audio is not confirmed, or if curated visible motion is below the threshold. This is
a technical runner/contact-sheet lock, not human full-motion/native-audio listening or creative approval.

## Clean content-first layout retained

The rejected V7 overlay clutter is not restored, and the clean V8 layout is preserved:

- Blurred full-frame background with a soft ambient luminance lift (no black empty half).
- Sharp, uncut, aspect-preserving source frame centered on that background. No crop, no zoom,
  no letterbox, no V6 `cover_crop()`.
- A slim top rank strip `7 6 5 4 3 2 1` with the active rank highlighted (y=150..230).
- A small translucent moment badge with `#rank` and the moment label (y=1650..1738).
- A thin timeline progress line (y=1760..1765).

All three elements are inside the platform safe area and **outside** the central content region
`[0, 400, 1080, 1520]`. Combined overlay bounding-box area is under 6% of the frame. The sharp source
band is completely unobstructed. Outer phone/gallery player chrome is not baked into the MP4.

## Technical contract

- 60.0s / 1800 frames / 30fps / 1080x1920 vertical.
- Seven ranked moments, 7 → 1, hard cuts only.
- Raw per-window native source audio only: no VO, music, SFX, bed, generated calls, AI audio,
  substitution or added layers. Nine unchanged web gates must pass.
- Per-title Commons API extmetadata rights/social-origin verification, original SHA-1, restrictions and
  CC BY attribution recorded. Only `CC0`, `Public domain` and `CC BY 3.0` are allowed.
- Separate deliverable: `deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_HIGH_ACTION_V9.mp4`.
  V3/V4/V5/V6/V7 and the technically successful V8 remain rejected evidence; no same-path replacement.
- `deliverables/.gitignore` re-includes only this V9 MP4 from the root `deliverables/*.mp4` ignore rule.

## Not claimed

No exact reference match, no currently trending named-platform clips, no full legal compliance,
no human full-motion/native-audio listening, no creative approval/sign-off, no perfection,
retention, virality, likes/subscribes, same-path replacement or audience result.
