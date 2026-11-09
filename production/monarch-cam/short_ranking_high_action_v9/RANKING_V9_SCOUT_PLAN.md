# Monarch Cam — high-action V9 candidate scout

## Why this lane exists

Clean V8 kept the content-first, uncluttered layout, but its clip quality was rejected: several selected windows were static, ordinary CCTV, title cards or weak visual moments. The user asked for genuinely funny, interesting, hooked, amazing, mind-blowing, eye-opening, hilarious or shocking **visible movement/action/payoff** in every ranked window — not “kuch nhi.” This is a separate corrected V9 lane, not a replacement of V4/V5/V6/V7/V8 and not a same-path overwrite.

The V8 clean visual system remains the target for the later final build: full-screen uncut source frames on an ambient-lifted blurred full-frame background; slim `7→1` top rank strip; small bottom-left moment badge; thin progress line; all outside the central `[0,400,1080,1520]` region; overlay area `<6%`; no V6 `cover_crop()`, zoom, black empty upper half, letterbox/black bars, cut-off list, tiny boxed list or V7 clutter. Native raw per-window source audio only: no VO, music bed, SFX, generated calls, AI audio, substitution or added layers. The nine unchanged web audio gates remain required. The final MP4 remains `60.0s / 1800f / 30fps / 1080x1920` with seven `7→1` moments.

## What this scout does

`candidate_scout_v9.json` lists 20 fresh high-action candidate files mirrored on Wikimedia Commons from YouTube or Vimeo. `scout_candidates_v9.py`:

1. Verifies each title's licence, attribution requirement, creator, credit/categories, social-origin tokens, restrictions, original SHA-1, size, duration and dimensions through the Commons API.
2. Rejects files with disallowed licences, `license review needed (video)`, non-free-audio flags, CC BY-SA/2.0/4.0, fair-use-only or non-empty `Restrictions`.
3. Downloads either the small Commons original or a Commons VP9/Opus derivative; no unverified social repost is downloaded.
4. Uses `ffprobe`/`ffmpeg` to measure the file's own native audio stream and one-frame-per-second visual motion for up to 600 seconds.
5. Scores all possible 8.6 s windows for continuous native audio, audible level and visible motion, with an additional high-action motion threshold.
6. Writes two real runner contact sheets per candidate: a separated top-motion overview and 0.5 s frames from the best 8.6 s window. Those sheets are committed for visual inspection before any final V9 source/window lock.

This scout does **not** render the final Short and does not lock the final seven. The committed `scout_report.json` and `scout_summary.json` are runner measurements, not creative approval.

## Rights and source boundary

The pool uses rights-cleared social-origin Commons originals/derivatives with exact attribution and restriction fields recorded in the API ledger. It does not claim currently trending TikTok/Instagram/YouTube/Reddit/Dailymotion clips, exact reference clips, all named platforms represented, or full legal compliance. Older clips are allowed by the user's `viral ke sath sath purani bhi chalenge` instruction. The exact reference Short `https://youtube.com/shorts/08-ocSDpt7o` was not available as real frames/full motion/native audio in this authoring environment; metadata/thumbnails/search are not a substitute and no exact-match claim is made.

## What still has to happen

- Inspect the committed candidate contact sheets and the final MP4's own contact sheets/frames after a successful V9 CI run.
- Curate seven distinct high-action windows with visible payoff and continuous native audio, plus reserves.
- Build the separate `..._HIGH_ACTION_V9.mp4` through a V9 workflow preserving the clean V8 layout, native per-window audio and unchanged web gates.
- Inspect the real committed MP4, technical/audio QC, source/rights/social-origin/native-audio ledgers, then give only that corrected V9 MP4's own GitHub link.

Technical QC, audio gates, CI success, contact sheets and links are not human full-motion/native-audio listening, creative approval, perfection, retention, virality, 3x, likes/subscribes or audience-result claims.
