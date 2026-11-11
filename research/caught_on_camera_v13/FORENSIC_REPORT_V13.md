# V13 — Caught-on-Camera Niche Forensic (10x microscope)

**Status:** research + English production blueprint. This is NOT a claim of upload, publish, monetisation, legal clearance, human approval, perfection, or guaranteed views.

**Owner correction applied:** content is **English**. All VO, captions, lower-thirds and on-screen text in the deliverable are English. The rejected V12 `REPLAY FILES Ep.1`, `MC-01`, the NASA V10 Short, the V12 eight archived finals, and the first violent V13 clip pool are excluded.

**Curation correction:** the second, positive-only V13 pass removed graphic footage but returned mostly low-energy landscape repeats, microscopy diagrams, interviews and title cards. A self-imposed exclusion of the ten V7 rights-cleared social-origin Commons candidates was therefore reversed, and ten further on-brand Commons funny / prank / animal / silent-comedy clips were added through live Commons API search. `curated_titles_v13.json` now defines 20 distinct clips; `selected_windows_v13.json` uses all 20. The low-energy V13 safe-pass windows remain as research evidence but are NOT in the final cut. None of these are the rejected V12 finals or the NASA Short.

---

## 1. Decision: one chosen idea

**Working title:** `CAUGHT ON CAMERA: 20 Moments The Lens Was Not Supposed To Catch`

**Format:** 9:00 (540 s) landscape long-form compilation. 20 different rights-documented Wikimedia Commons clips, used in three escalating rounds, with original English commentary, burned-in English captions, native audio, zooms, speed ramps and replays.

**Rules carried into the edit:**

1. Real footage at **frame 1**. No intro card, no title card, no method card, no diagram, no static slide.
2. No long monologue over stills. VO appears in 3-5 s bursts over moving footage.
3. Pattern interrupt every 3-5 s: cut, zoom punch, speed change, replay, or angle/crop change.
4. Many different clips/moments, not one clip and not the already-used Short.
5. Family-safe / non-graphic selection. Murder CCTV, bombings, missile strikes, crashes, robberies and police-information frames are hard-blocked.
6. Small lower-third source attribution over footage only; credits also live in `rights_ledger_v13.json` and `CREDITS_V13.md`.
7. Narrative spine: cold open → escalation → animal chaos → near misses → instant karma → slow-motion replay → final callback.

Why this idea and not an analytics essay: the strongest API-verified demand lane is **"funniest moments caught on camera"** with `1,874,263,025` cumulative views across 30 sampled videos and a median of `43,987,871` views. The **"caught on camera compilation"** lane is the least concentrated (`top3_share = 0.202`, `winner_ratio = 2.8`), i.e. an entry is feasible rather than owned by one winner. Long-form precedents exist in the same corpus: FailArmy `4,705 s / 163,819,966` views, Daily Dose Of Internet `1,135 s / 80,577,369`, Tannerites `718 s / 134,723,159`, WOW TV `769 s / 37,686,348`.

---

## 2. Data provenance (real API only)

| Evidence | Count | File |
|---|---:|---|
| Search/topic lanes | 8 | `api_evidence/lanes/co-*.json` |
| Lane rows | 240 | same |
| Unique videos after de-duplication | 220 | computed |
| Videos with >= 1,000,000 views | 180 | computed |
| Videos with >= 10,000,000 views | 146 | computed |
| Channel statistics resolved | 146 | `api_evidence/channels/channel_statistics_v13.json` |
| Bulk million-view video details | 60 | `api_evidence/channels/million_view_videos_v13.json` |
| Reverse teardowns attempted | 6 | `api_evidence/channels/reverse_teardowns_v13.json` |
| Usable transcripts | 1 | same |

`run.json` records `key_present: true`, `secret_value_printed_or_stored: false`. Public Data API fields only: views, likes, comments, duration, title, tags, description, channel statistics. No private retention, CTR, RPM, no invented competitor transcripts, no verified "fastest growing" ranking.

---

## 3. Niche demand, lane by lane

| Lane (real `search.list` order) | Total views | Median views | Top-3 share | Winner ratio | Verdict |
|---|---:|---:|---:|---:|---|
| funniest moments caught on camera | 1,874,263,025 | 43,987,871 | 0.293 | 4.7 | SHARPEN |
| dashcam caught on camera | 1,354,487,183 | 24,272,313 | 0.343 | 7.3 | NO |
| unexpected moments caught on camera | 1,327,707,242 | 17,434,532 | 0.396 | 11.9 | NO |
| wildlife caught on camera | 1,113,447,627 | 20,630,074 | 0.373 | 8.8 | NO |
| caught on camera | 983,800,549 | 25,210,974 | 0.281 | 5.3 | SHARPEN |
| caught on camera compilation | 399,679,756 | 11,621,435 | 0.202 | 2.8 | SHARPEN |
| security camera viral moments | 74,972,394 | 21,922 | 0.767 | 1192.9 | NO |
| caught on camera fails compilation | 49,462,650 | 962,385 | 0.388 | 7.2 | SHARPEN |

The lane decision is a corpus-shape signal, not a promise. `funniest`, `caught on camera` and `compilation` are the three SHARPEN lanes with real millions-view demand; `security camera viral moments` is dominated by a few outliers and is not a safe entry point.

Title signals across 220 unique videos: `camera` 125, `caught` 123, `fail` 53, `moment` 43, `security` 41, `best` 27, `funny` 19, `dashcam` 17, `cctv` 15, `unexpected` 14, `viral` 12, `ranking` 11, `wildlife` 14, `animals` 10. The winning vocabulary is literal, concrete and clip-first, not analytics jargon.

---

## 4. Channel-level benchmark (146 real channels)

Median across resolved channels: `660,000` subscribers, `482,010,202` channel views, `558.5` videos. These are API facts, not a "best growing channels" ranking.

Top 10 by cumulative channel views:

| Channel | Channel views | Subscribers | Videos |
|---|---:|---:|---:|
| Dylan Anderson | 35,709,972,802 | 14,600,000 | 3,491 |
| NDTV India | 35,005,028,722 | 27,300,000 | 401,333 |
| Speed McQueen | 31,134,134,419 | 17,300,000 | 5,998 |
| CNN | 22,526,169,635 | 20,100,000 | 189,120 |
| boxtoxtv | 21,856,967,365 | 24,100,000 | 3,153 |
| Mark Rober | 20,179,837,511 | 86,100,000 | 276 |
| Daily Dose Of Internet | 17,642,780,648 | 20,700,000 | 2,023 |
| SimpleGhar Telugu | 14,289,215,219 | 7,210,000 | 1,331 |
| Panda Shorts | 12,722,175,356 | 23,500,000 | 1,335 |
| FaZe Rug | 11,208,076,925 | 30,100,000 | 2,644 |

Relevant compilation-native channels in the same corpus: **FailArmy** `17,500,000` subscribers / `2,481,726,397` views, **America's Funniest Home Videos** `14,200,000` / `8,607,405,061`, **Daily Dose Of Internet** `20,700,000` / `17,642,780,648`, **Just For Laughs Gags** `14,200,000` / `8,607,405,061`. News channels appear because broad search terms surface them; they are benchmarks, not a niche definition.

---

## 5. Million-view video forensics (60 bulk details)

- Median duration `34.0 s`, mean `410.9 s`. `43/60` are <= 60 s, `9/60` are >= 600 s. Shorts dominate by count, but long-form compilations win too.
- Median likes/views `1.2 %`, median comments/views `0.011 %`. These are public ratios only, not retention or CTR.
- Median title length `53` characters. `23/60` contain an emoji, `23/60` a hashtag, `14/60` a number, `13/60` an ALL-CAPS word, `1/60` a question mark.
- Top tags: `funny fails` 9, `try not to laugh` 9, `funny` 8, `funny videos` 8, `fails` 7, `fails of the week` 7, `epic fails` 6, `best fails` 6, `instant regret` 6, `pranks` 6.

Top 10 by views:

| Views | Duration | Channel | Title |
|---:|---|---|---|
| 208,066,454 | PT36S | Chris Colditz | Try NOT to Laugh! Top 10 Funniest Moments #funny |
| 204,756,272 | PT49S | Ice Ranks | Ranking Unexpected Baby First Words |
| 180,673,068 | PT1M1S | Mark Rober | How To Lure A Gorilla With Your Phone |
| 177,984,173 | PT58S | DJI | Cats Caught in Action |
| 163,819,966 | PT1H18M25S | FailArmy | Best Fails of the Year \| Try Not To Laugh |
| 160,214,387 | PT59S | Freshly Charged | Watch the scammer's reaction when he sees the dashcam |
| 155,951,674 | PT18S | nature.science_official | Saqaltay - Vulture |
| 154,354,128 | PT7S | America's Funniest Home Videos | This really confused me at first |
| 134,723,159 | PT11M58S | Tannerites | Caught On Security Camera 12 Foot SKELETON |
| 126,978,846 | PT33S | 10 News | Dashcam Footage Captures Moment Of Instant Karma |

Long-form >= 600 s examples in the same 60: FailArmy `4,705 s`, America's Funniest Home Videos `7,485 s`, FailArmy `3,048 s`, Daily Dose Of Internet `1,135 s`, WOW TV `769 s`, Life Awesome `608 s`. A 9-minute edit is therefore a real lane, not a contradiction of the data.

---

## 6. Script / hook teardown (only where a transcript actually exists)

Six teardowns attempted. `5/6` could not produce a transcript: four YouTube bot-check errors, one `no_captions`. **No transcript is invented.**

The one usable transcript is `KT3e_lKrNss` — `Ranking Unexpected Baby First Words`, `204,756,272` views, `PT49S`:

- `48` words, `58.8 wpm`, reading grade `1.8`, `0` CTAs, `0` filler words.
- First sentence: `Oh, bless you.` Opens with "you" in the first 12 words.
- Structure map: cold open `0:00`, hook restated `0:03`, setup/promise `0:10`, first proof `0:22`, escalation `0:30`, payoff `0:39`, outro `0:45`.
- Replication note from the teardown: keep addressing the viewer early; beat it with a tighter cut, a concrete number inside 3 seconds, and a fresh visual grammar.

Implication for V13: short, plain English lines over footage; no essay; no 100-second monologue; a concrete count early; escalation and payoff, not a static lecture.

---

## 7. Editing grammar for the build

- `0:00-0:03`: first clip already in motion, hard cut, captions already on screen.
- Every `3-5 s`: cut / zoom punch / speed ramp / replay / crop change. No static composition held longer than `3-5 s`.
- VO bursts `2.5-4.5 s`; native audio stays audible between bursts.
- Burned-in English captions for muted viewing.
- Lower-third source attribution only, never a full-screen card.
- Three rounds: `ROUND 1 / THE HOOK`, `ROUND 2 / WHAT HAPPENED`, `ROUND 3 / ONE MORE TIME`. Round labels are small overlays over footage, not title cards.
- No full-screen diagrams, no analytics charts, no owner-only retention cards, no phone-shot presentation.
- Final frame is still footage, not a static end card.

External editing heuristics used as non-guaranteed craft guidance, not API facts: first 3 seconds hook, 3-5 s pattern interrupts, captions, no dead space. See `https://opus.pro`, `https://openclip.app`, `https://increditors.com`.

---

## 8. Rights / reuse boundary

Official YouTube channel monetisation policy (`https://support.google.com/youtube/answer/1311392?hl=en`) says reused content can qualify only with significant original commentary, storyline or substantive modifications, and explicitly lists "Short videos you compiled from other social media websites" and "image slideshows ... with minimal or no narrative" as not monetisable. Therefore V13 is built with a narrative spine, original English commentary and substantive editing. **No monetisation claim is made.**

Clip sources are live Wikimedia Commons namespace-6 file pages with PD / CC0 / CC BY commercial-reuse metadata, recorded per clip in `rights_ledger_v13.json`: Commons page, licence, artist, SHA-1, source URL, local SHA-256, 10 s window start/end and score. Unverified Instagram / TikTok / Reddit / Twitter / Dailymotion reposts are NOT downloaded. Per-clip human legal review and a human watch-through remain required; this is not a legal opinion.

The first V13 pool was rejected because generic CCTV queries returned murder, bombing, missile, crash and robbery footage. `clip_safety_v13.py` now hard-blocks those terms across title + description + categories and ranks animal / funny / unexpected / skill titles first. The second pool was safe but low-energy, so twenty curated Commons clips were assembled through `acquire_curated_v13.py` with the same gate: ten V7 social-origin clips plus ten further on-brand Commons clips found by live API search. The generic motion scorer initially drifted into title cards and a `SUBSCRIBE` outro, so `curated_window_overrides_v13.json` now pins all 20 clips to V7 verified runner windows or hand-checked mid-clip action windows, with a hard end-card clamp. `validate_clips_v13.py` re-checks the final 20-clip selection, licence, SHA-256, duration and video stream before a build is allowed; silent sources are recorded, not treated as native audio.

---

## 9. Production blueprint

| Round | Seconds | Clips | Beat | VO density |
|---|---:|---|---|---|
| Cold open | 0-160 | 20 x 8 s | fastest hook of each clip, no context yet | one 3 s line per 2 clips |
| What happened | 160-360 | 20 x 10 s | slow-mo / replay / zoom on the exact surprise | one 4 s line per clip |
| One more time | 360-540 | 20 x 9 s | callback, escalation, final fastest moment | one 3 s line per 2 clips |

Total `540 s`, `120` visual beats, `20` distinct clips, `60` primary segments. Every segment is moving footage. The 20 clips are defined in `selected_windows_v13.json` and resolved against `rights_ledger_curated_v13.json`; `rights_ledger_v13.json` remains a low-energy research record only. Captions SRT is generated from the same English VO text. EDL, captions, credits, QC report and the final MP4 are written under `production/monarch-cam/caught_on_camera_v13/`.

---

## 10. Honest limits

- Technical QC (`duration`, frame count, audio loudness, caption sync, SHA-256, no static hold) is **not** creative approval.
- No YouTube upload, publish, category change, pin, monetisation change, legal clearance or human sign-off.
- No private analytics, no invented retention/CTR/RPM, no invented transcripts, no verified growth ranking.
- No guaranteed views, virality, perfection, family-safety guarantee, NASA endorsement or official status.
- Third-party benchmark videos are studied, not copied into the edit.
- A human must still watch the full motion, native audio and each clip's rights page before any real publication.

Machine-readable metrics: `FORENSIC_METRICS_V13.json`. Full English VO script: `production/monarch-cam/caught_on_camera_v13/VO_SCRIPT_V13.md`. Final clip ledger: `rights_ledger_curated_v13.json`; low-energy research ledger: `rights_ledger_v13.json`. Final selection: `selected_windows_v13.json`. Rejection record for the previous attempt: `production/monarch-cam/replay_files_ep01_v12/REJECTION_V12.md`.
