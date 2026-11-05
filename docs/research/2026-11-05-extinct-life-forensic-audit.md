# Extinct Life — evidence-led channel audit

**Audit date:** 2026-11-05. **Channel supplied by owner:** https://youtube.com/@extinct_life

## 1. Evidence and limits

Primary evidence: owner-supplied Drive file `1R68SUE5ld3yV8H59r_ubk8lmEeCWTy3Y`, `Screen_Recording_20261105_215332.mp4`. Drive metadata: 64,161,887 bytes, 720×1600, 164.461 seconds. The recording shows mobile YouTube Studio, not continuous playback of the uploaded Shorts.

Method: extracted 164 frames at one frame per second with FFmpeg; visually reviewed all nine chronological contact sheets, then enlarged selected source frames for metric verification. The timestamp ledger below is a one-second sampling index, not a frame-by-frame review: brief events between samples can be missed and frame timestamps are approximate (around half-second sampling offset). Loading screens and repeated screens are identified rather than treated as additional evidence. Audio was not evaluated. No OCR-generated guesses are used as exact values.

A direct fetch of the supplied YouTube handle returned a page titled Extinct Life but a 401 error shell instead of a usable channel/video inventory. Public upload playback, full descriptions, banner, About page, exact total uploads, and current public totals were therefore not independently verified. All channel metrics below are the recording's snapshot, not a live API query.

Confidence convention: **observed** = visible in recording; **derived** = arithmetic from visible values; **hypothesis** = explanation to test, not proven causality; **proposal** = recommended future experiment.

## 2. Correct channel identity

- Observed channel name: **Extinct Life**.
- Supplied handle: **@extinct_life**.
- Observed total subscribers: **87** (dashboard around 00:00 and 02:03).
- Content visible: prehistoric/extinct animals, ancient giants, evolutionary curiosity, extinction and dinosaur POV concepts, predominantly Shorts in the shown inventory.
- This is one of the owner's three YouTube Automation channels per the conversation. The other two are not established by this evidence.
- Do not substitute the existing `config/channels.json` defaults (Monarch Lab, Mindful Momentum, Curious Miles). The owner explicitly corrected their classification. Application configuration has NOT been changed as part of this audit.

**Working positioning hypothesis:** visually explain strange extinct animals by comparing them with familiar living animals. This is narrower than generic dinosaur entertainment and better aligned with the strongest inspected result. It is a testable direction, not proof that every future comparison will work.

## 3. Inventory visible in the recording

Titles are transcribed only as far as legible; ellipses indicate visible truncation. This is not a confirmed exhaustive public catalogue. Rounded list counts can differ from detail cards.

| Visible upload | Length badge | Visible views | Visible likes | Visible comments | Inspection depth |
|---|---:|---:|---:|---:|---|
| July 16, 2026 | 0:46 | 0 | 0 | 0 | List only; status/icon meaning not established |
| The Last Thing Dinosaurs Ever Saw 💀 | 0:38 | 1,218 exact in overview | 23 | 0 | Overview, Reach, Engagement, Audience |
| Pov: Survived T-rex Attack ☠ | 0:45 | 1,292 exact in overview | 10 | 0 | Overview, Reach, Engagement, Audience |
| Your DNA has a 250 Million Year Old Secret… | 0:30 | 1,524 exact in overview | 11 | 2 | Overview, Reach, Audience; engagement loading |
| Modern Elephant vs. Prehistoric GIANTS!… | 0:24 | 16.7K detail / 16K list | 446 | 2 | Reach, Engagement, Audience; overview loading |
| Imagine seeing this in your backyard… | 0:23 | 1.8K | 36 | 1 | List only |
| Nature's 8-Foot … #shorts #prehistoric… | 1:05 | 1K | 20 | 1 | List only |
| Forget the T-Rex. Meet the “Terminator Pig.”… | 0:50 | 514 | 6 | 1 | List only |
| Why Evolution “Deleted” This Monst… | 1:08 | 2.3K | 55 | 3 | List only |
| January 12, 2026 | 0:30 | 0 | 0 | 0 | List only; status/icon meaning not established |

Dates clearly visible on detail cards: Last Thing = February 27, 2026; POV = February 16, 2026; DNA = February 8, 2026; Elephant = February 6, 2026. The dashboard's latest-published cards are roughly 250–270 days old. Two date-named rows exist, including a July row with zero views: do not infer a confirmed public upload schedule or a complete inactivity period without inspecting their status. The list contains mixed status icons, so do not assume every row is public or unrestricted.

## 4. Four inspected Shorts: like-for-like lifetime comparison

| Metric | Last Thing | T-rex POV | DNA Secret | Elephant / Giants |
|---|---:|---:|---:|---:|
| Views | 1,218 | 1,292 | 1,524 | 16.7K rounded |
| Watch time | 2.9 h | 4.0 h | 2.9 h | 62.0 h |
| Avg view duration | 0:17 | 0:22 | 0:18 | 0:22 |
| Avg percentage viewed | 45.0% | 51.0% | 60.9% | 92.5% |
| Stayed to watch | 48.6% | 45.2% | Not captured | 77.7% |
| Swiped away | 51.4% | 54.8% | Not captured | 22.3% |
| Engaged views | 558 | 576 | Not captured | 9.8K rounded |
| Unique viewers | Not captured | 548 | 501 | 9.5K rounded |
| Subscribers attributed | +13 | +2 | +3 | +17 |
| Shorts feed share | 92.7% | 92.9% | 96.1% | 91.4% |
| YouTube search share | 6.2% | 6.4% | 1.6% | 7.4% |

### What this supports

1. **Elephant is the strongest inspected discovery/consumption result.** It leads the measured videos in views, stay rate and average percentage viewed. Its duration is about 24 seconds versus 38/45/30 seconds for the others. Topic, opening execution and duration are confounded: this is not a controlled test proving which variable caused the difference.
2. **POV's first-impression problem is separate from retention.** 54.8% swiped away; the remaining consumption metric is still only 51.0% average viewed. Improving only the ending would not address the initial skip rate.
3. **Last Thing has lower consumption but comparatively strong subscriber yield.** +13 from 1,218 views versus Elephant's +17 from about 16,700. That is a reason to examine channel-fit and calls to action, not automatically discard the extinction theme.
4. **DNA's 60.9% is between the weaker two and Elephant.** Its stayed-to-watch card was not obtained; do not fill that gap with the channel-wide rate.
5. Lifetime curves show a strong early rise followed by long, relatively flat periods. Exact initial distribution windows cannot be read from these compressed graphs. No shadowban, account penalty or algorithmic cause is established.

### Derived comparisons (approximate)

- Elephant vs Last Thing: **+29.1 percentage points** stayed to watch; **+47.5 pp** average viewed.
- Elephant vs POV: **+32.5 pp** stayed to watch; **+41.5 pp** average viewed.
- Elephant's rounded views are ~13.7× Last Thing and ~12.9× POV.
- Subscribers per 1,000 displayed views: Last Thing **10.7**, POV **1.5**, DNA **2.0**, Elephant **1.0**. These are descriptive ratios, not controlled conversion probabilities or forecasts. Views and subscriber attribution have different analytics limitations.
- Visible likes / displayed views: Last Thing ~1.89%, POV ~0.77%, DNA ~0.72%, Elephant ~2.67%. Rounded totals and potentially different update times limit precision.

**Metric caution:** Shorts views, engaged views, unique viewers, shown-in-feed decisions, and average view duration are not interchangeable denominators. Do not calculate stay rate as engaged views / all views, or use watch time / all displayed views to overwrite YouTube's displayed duration. 92.5% average percentage viewed is NOT a measured 92.5% completion rate; it can include repeat viewing and does not establish how many reached the final frame. The rounded 22-second duration and 24-second badge do not need to reproduce the precise internal percentage exactly.

## 5. Recent channel performance: keep this separate from lifetime

Observed last-28-days channel dashboard/analytics, with chart labels Oct 8–Nov 4:

| Metric | Observed value |
|---|---:|
| Views | 224; 154 more than usual |
| Watch time | 0.6 hours, dashboard |
| Engaged views | 119; card says 113% more than previous 28 days |
| Likes | 4; card says 100% more than previous 28 days |
| Subscribers, Content card | +1 |
| Subscribers, Overview/Audience cards | 0 |
| Monthly audience | 104; audience-behavior card dated Nov 4, 2026 |
| New / casual / regular viewers | 97.1% / 2.9% / <0.1% |
| Stayed / swiped | 70.2% / 29.8% |
| Realtime views, 48 hours | 7, all seven shown against Elephant |
| Top video, recent | Elephant 217 views |
| Next shown entries | Terminator Pig 5; POV 1; Last Thing 1 |

**Scope discrepancy:** Content shows +1 subscriber while Overview/Audience show 0. Possible attribution, gross/net, filter or reporting differences need a Studio export; the recording does not establish the explanation. Preserve both rather than silently choose one.

Derived: **217/224 = 96.875%** of recent channel views came from Elephant. Its recent audience is effectively dominated by that one asset. The 70.2% stay rate is therefore not proof that every concept on the channel performs that well.

### A crucial shift: lifetime feed discovery vs recent search discovery

Recent Shorts sources, around 02:33–02:34:
- **YouTube search 84.8%**.
- **Shorts feed 10.3%**.
- **Hashtag pages 2.7%**.

Recent YouTube search terms, around 02:35:
- **platybelodon 61.6%**.
- **deinotherium elephant 1.6%**.
- **elephant evolution 0.5%**.

These search-term percentages are shares within the search-term report, NOT shares of every channel view. Sources are rounded and only the visible leading rows were captured.

**Interpretation:** the snapshot supports an old feed-distributed winner retaining a small search-driven tail, particularly around Platybelodon. This is not evidence of a current viral Shorts-feed surge. Search-led sequels are justified as an experiment; this small sample does not establish market size, future revenue or RPM.

## 6. Audience evidence and restrictions

### Elephant lifetime audience
- Geography: India **63.6%**, Pakistan **7.0%**, Bangladesh **2.5%**.
- Gender: male **89.8%**, female **10.2%**, user-specified **0.0%**.
- Visible ages: 13–17 **3.5%**, 18–24 **26.8%**, 25–34 **46.3%**, 35–44 **19.0%**, 45–54 **3.8%**. Lower rows show zero in the sampled screen; do not force displayed rounded percentages to sum exactly to 100.
- Devices, watch-time share: mobile **88.9%**, TV **5.4%**, tablet **3.4%**, computer **2.2%**.
- No subtitles/CC: **98.7%**.

### Other videos differ materially
- Last Thing: US **22.1%**, India **9.8%**, Philippines **9.3%**; no CC **97.1%**, English CC **2.9%**; unsubscribed watch time **99.6%**.
- POV: Brazil **8.6%**, Mexico **7.6%**, Pakistan **7.5%**; gender male **47.7%**, female **52.3%**; age 25–34 displayed **100%**. Mobile **83.7%**, TV **9.6%**, tablet **4.9%**, computer **1.8%**. No CC and unsubscribed watch time both **100%**.
- DNA: US **39.6%**, UK **8.7%**, Canada **5.7%**; male **100%**; ages 45–54 **7.7%**, 55–64 **31.7%**, 65+ **60.6%**.

**Do not infer:** “the entire channel targets elderly US males” from DNA, or “all viewers are 25–34” from POV. Small eligible demographic subsets can look extreme; their denominators and coverage are not shown. Also geography does not establish language or purchasing power.

### Recent channel audience
- Devices: mobile **68.0%**, tablet **16.6%**, TV **9.7%**, computer **5.7%** (watch-time share).
- No subtitles/CC **97.8%**; Czech auto-translated **0.9%**; Portuguese **0.5%**.
- Unsubscribed watch time **100%**.
- Age, gender, geography, viewer-online times, other watched channels/content and formats often show insufficient data.

No CC usage does not prove the actual videos have no burned-in captions. Viewer-online times are unavailable: an exact best posting hour cannot be derived.

## 7. Packaging, retention and content diagnosis

### What is visible

The inventory mixes recognizable-versus-ancient comparisons, threat/POV stories, extinction spectacle, DNA curiosity and unusual-creature reveals. Thumbnails show portrait creature imagery, dramatic scale or threatening compositions. The Last Thing thumbnail is fiery orange/red with multiple dinosaurs; POV shows a close threatening creature scene; DNA shows a creature against an outdoor backdrop. These observations do not establish the production model, AI tools, licensing or factual accuracy.

### What the retention shapes suggest

Last Thing drops substantially early and then trends toward roughly the lower quarter of the graph by the end. POV similarly declines through the video, ending low. DNA's line falls through the middle and toward the bottom near the finish. Elephant holds materially better through much of its shorter runtime, then drops near the ending. Exact second-by-second retention values and causes cannot be read reliably from these screenshots; no tooltip sequence is shown.

### Hypotheses worth testing

- Recognizable reference animal + surprising extinct relative may communicate the premise faster than a broad extinction or cinematic threat premise.
- A short, concrete comparison may deliver its promise more efficiently than 38–45-second narrative setups.
- Naming the specific animal may align packaging with existing search intent.
- A clearer recurring series could help convert one-off curiosity into return visits.

None proves that the thumbnail, voiceover, music, first frame or narration pacing caused the outcome. Uploaded-video playback is needed to audit those assets.

### Risks to inspect, not assumed violations

- Elephant detail card has **Other notices**. That is not enough to call it a strike, copyright claim, age restriction or monetization block. Open the notice details.
- DNA title makes a precise “250 Million Year” claim. The title alone does not show what is asserted in narration. Check the actual biological claim, timeframe and citations before repeating it.
- Titles such as “evolution deleted” can imply intent; a scientific script should explain real mechanisms rather than treat the metaphor literally.
- AI reconstruction, if used, should not be mistaken for footage or certainty about unknown anatomy/behavior. Tool provenance was not established here.
- No revenue, Earn eligibility, RPM, CTR, impressions, production costs or copyright detail was shown. No monetization conclusion is justified.

## 8. Recommended next production experiment

**Goal:** find out whether the Elephant result is repeatable while retaining a clear, scientifically defensible channel identity.

Do not mass-produce 30 near-identical clips or delete older uploads from this evidence. Start with a small logged batch:

1. **Three 20–30-second ancient-relative comparisons:** proposed topics Platybelodon vs modern elephant, Deinotherium vs modern elephant, and one researched third relative. Check taxonomy, dates, range and scale before scripting. No invented measurements.
2. **Two 20–30-second single-creature explanations:** same visual/voice style and similar production quality, but one clear question/answer rather than comparison. This gives directional evidence about the format, not a randomized experiment.
3. **One shorter extinction-story follow-up:** retain the thematic appeal of Last Thing but get to a concrete fact sooner; examine subscriber yield alongside reach.

Suggested structure, not a reconstruction of the existing successful video:
- 0–2 s: identifiable modern reference + strange prehistoric contrast; say the premise immediately.
- 2–7 s: name the animal and one well-sourced distinction.
- 7–17 s: two clear visual comparisons with readable scale/context.
- 17–24 s: answer the opening question and correct a likely misconception.
- Optional last moment: a relevant next-episode cue, not an unrelated engagement demand.

Use accurate natural-language titles including the animal name when relevant. Example proposal: **“Platybelodon vs Modern Elephant: Why the Strange Jaw?”** This is an editorial concept, not a verified anatomical explanation. Avoid keyword stuffing and unrelated trends.

### Measurement protocol

For each upload, log title/version, animal, format, duration, language, opening visual, upload time, sources, cost and any content notice. Capture **24 h / 72 h / 7 d / 28 d** snapshots separately:
- Views and engaged views.
- Stayed-to-watch / swiped-away.
- Average duration and average percentage viewed.
- Retention screenshots with readable time axis.
- Feed vs search share and actual source volumes where available.
- Likes, comments, attributed subscribers and unsubscribed watch time.
- Geographic coverage and demographic sample caveats.

Compare new uploads at the same age and distinguish search from feed. The existing 77.7% stay and 92.5% average-viewed result is a **reference**, not a guaranteed threshold or universal benchmark. With only a handful of uploads, use results directionally; do not claim statistical causality. Avoid changing topic, duration, language and visual style simultaneously if the objective is to learn which factor matters.

## 9. What is needed for a genuine creative/operational deep audit

The supplied recording is excellent analytics evidence, but it cannot expose every production detail. Needed next:
- Actual playable exports or watch links for the four inspected Shorts, especially Elephant and Last Thing.
- Full title, description, tags and language settings; subtitles and source/licensing records.
- Studio CSV exports with date ranges and exact totals, source counts and subscriber scopes.
- Elephant **Other notices** details.
- Retention views with tooltip timestamps, not only a compressed curve.
- Channel Home/About/branding screenshots; public inventory and status of the zero-view date-named rows.
- Production workflow/tool list and cost/time per upload if automation efficiency is to be assessed.

Without those, sound design, spoken hooks, factual accuracy of full scripts, scene cadence, upload compliance, production profitability and end-to-end automation remain unverified.

## 10. Bottom line

**Observed:** Extinct Life has a real standout inspected asset, not uniformly strong performance across its tested themes. That asset dominates the small recent traffic base, which is currently search-led in this snapshot. **Hypothesis:** ancient-elephant / recognizable-relative explanations are the most defensible first replication lane. **Proposal:** run a small controlled-style production batch, retain factual sourcing and measure source-specific outcomes before scaling.

The report does not establish that the channel is dead, shadowbanned, monetized, or guaranteed to grow. It also does not establish the other two automation channels. No application configuration or cloud settings were changed.

## Appendix A — chronological one-second evidence ledger

The ledger is appended below. Times refer to the screen recording, NOT to retention timestamps inside an uploaded Short. Entries summarize the sampled visible screen; repeated screens and loading states are intentionally retained.

| Recording time | Sampled screen / evidence |
|---|---|
| 00:00 | Dashboard: Extinct Life, 87 subscribers; 224 views / 0.6 h last 28 days; latest-published cards. |
| 00:01 | Dashboard: Extinct Life, 87 subscribers; 224 views / 0.6 h last 28 days; latest-published cards. |
| 00:02 | Content tab loading placeholders. |
| 00:03 | Content tab loading placeholders. |
| 00:04 | Content inventory scrolling: upload titles, portrait thumbnails, duration badges, view/like/comment counts. |
| 00:05 | Content inventory scrolling: upload titles, portrait thumbnails, duration badges, view/like/comment counts. |
| 00:06 | Content inventory scrolling: upload titles, portrait thumbnails, duration badges, view/like/comment counts. |
| 00:07 | Content inventory scrolling: upload titles, portrait thumbnails, duration badges, view/like/comment counts. |
| 00:08 | Content inventory scrolling: upload titles, portrait thumbnails, duration badges, view/like/comment counts. |
| 00:09 | Content inventory scrolling: upload titles, portrait thumbnails, duration badges, view/like/comment counts. |
| 00:10 | Content inventory scrolling: upload titles, portrait thumbnails, duration badges, view/like/comment counts. |
| 00:11 | Opening Last Thing; transition/loading. |
| 00:12 | Opening Last Thing; transition/loading. |
| 00:13 | Last Thing detail: 0:38, Feb 27 2026, Public, 1.2K views, 2.9 h. |
| 00:14 | Last Thing analytics loading. |
| 00:15 | Last Thing analytics loading. |
| 00:16 | Last Thing Overview: exact 1,218 views; retention 0:17 / 45.0%. |
| 00:17 | Last Thing Overview carousel: subscribers +13; same retention graph. |
| 00:18 | Last Thing Reach loading. |
| 00:19 | Last Thing Reach: Shorts feed 92.7%, search 6.2%, other features 0.4%, channel pages 0.3%, other 0.3%. |
| 00:20 | Last Thing Engagement loading. |
| 00:21 | Last Thing Engagement: engaged views 558; Hype 0; stay/swipe card. |
| 00:22 | Last Thing Engagement: stayed 48.6%, swiped 51.4%; retention 0:17 / 45.0%. |
| 00:23 | Last Thing Reach: lifetime curve and traffic sources. |
| 00:24 | Last Thing search terms: dahlia flower 4.0%, dinosaurs on youtube 2.6%, horror shorts 2.6%; insufficient suggesting/playlist data. |
| 00:25 | Last Thing Reach: sources; insufficient external-site data. |
| 00:26 | Last Thing Reach: sources; insufficient external-site data. |
| 00:27 | Last Thing Audience loading. |
| 00:28 | Last Thing Audience: US 22.1%, India 9.8%, Philippines 9.3%; no CC 97.1%, English 2.9%; unsubscribed 99.6%. |
| 00:29 | Last Thing Audience: US 22.1%, India 9.8%, Philippines 9.3%; no CC 97.1%, English 2.9%; unsubscribed 99.6%. |
| 00:30 | Last Thing Audience: gender unavailable; geography/CC repeated. |
| 00:31 | Back to Last Thing detail. |
| 00:32 | Content inventory; moving to T-rex POV. |
| 00:33 | Content inventory; moving to T-rex POV. |
| 00:34 | T-rex POV opening/loading. |
| 00:35 | T-rex POV opening/loading. |
| 00:36 | POV detail: 0:45, Feb 16 2026, Public; 1.2K views, 4.0 h. |
| 00:37 | POV analytics loading. |
| 00:38 | POV Overview: exact 1,292 views; retention 0:22 / 51.0%; realtime 0. |
| 00:39 | POV Overview scrolled: retention curve / zero realtime. |
| 00:40 | POV Reach loading. |
| 00:41 | POV Reach: feed 92.9%, search 6.4%, other features 0.3%, browse 0.2%, other 0.2%. |
| 00:42 | POV search terms: dinosaurs 4.9%, spider-man game 3.7%, dinosaur 2.4%; insufficient suggesting/playlist data. |
| 00:43 | POV Engagement loading. |
| 00:44 | POV engaged views 576; stayed 45.2%, swiped 54.8%; Hype 0. |
| 00:45 | POV carousel: unique viewers 548; stay/swipe repeated. |
| 00:46 | POV carousel: watch time 4.0 h; stay/swipe repeated. |
| 00:47 | POV carousel: watch time 4.0 h; stay/swipe repeated. |
| 00:48 | POV carousel: average view duration 0:22. |
| 00:49 | POV retention curve: 0:22 / 51.0%, declining toward end. |
| 00:50 | POV retention curve: 0:22 / 51.0%, declining toward end. |
| 00:51 | POV Audience loading. |
| 00:52 | POV unique viewers 548; insufficient watch-behavior/other-content data. |
| 00:53 | POV Audience carousel: subscribers +2. |
| 00:54 | POV age 25–34 100%; gender card entering view. |
| 00:55 | POV devices: mobile 83.7%, TV 9.6%, tablet 4.9%, computer 1.8%. |
| 00:56 | POV age/gender: male 47.7%, female 52.3%, user-specified 0%. |
| 00:57 | POV geography: Brazil 8.6%, Mexico 7.6%, Pakistan 7.5%; no CC 100%; unsubscribed 100%. |
| 00:58 | POV geography: Brazil 8.6%, Mexico 7.6%, Pakistan 7.5%; no CC 100%; unsubscribed 100%. |
| 00:59 | Back to POV detail. |
| 01:00 | Content inventory; moving to DNA Secret. |
| 01:01 | Content inventory; moving to DNA Secret. |
| 01:02 | DNA detail loading. |
| 01:03 | DNA detail: 0:30, Feb 8 2026, Public; 1.5K views, 2.9 h. |
| 01:04 | DNA detail/comments: visible yes comment with one reply; no unresponded comments. |
| 01:05 | DNA detail/comments: visible yes comment with one reply; no unresponded comments. |
| 01:06 | DNA analytics loading. |
| 01:07 | DNA Overview: exact 1,524 views; retention 0:18 / 60.9%. |
| 01:08 | DNA Reach loading. |
| 01:09 | DNA Reach: feed 96.1%, other features 2.0%, search 1.6%, channel pages 0.2%, other 0.1%. |
| 01:10 | DNA Engagement/Audience navigation and loading; no reliable engagement values captured. |
| 01:11 | DNA Engagement/Audience navigation and loading; no reliable engagement values captured. |
| 01:12 | DNA Engagement/Audience navigation and loading; no reliable engagement values captured. |
| 01:13 | DNA Engagement/Audience navigation and loading; no reliable engagement values captured. |
| 01:14 | DNA Audience: unique viewers 501; insufficient behavior data; own uploads listed below. |
| 01:15 | DNA ages: 45–54 7.7%, 55–64 31.7%, 65+ 60.6%; male 100%. |
| 01:16 | DNA geography: US 39.6%, UK 8.7%, Canada 5.7%. |
| 01:17 | DNA Audience scroll: TV 3.3% visible; age/gender repeated. |
| 01:18 | DNA Reach curve/source card repeated. |
| 01:19 | DNA search terms: dna 8.0%, buffalo meat 4.0%, con ma 4.0%; insufficient suggesting/playlist data. |
| 01:20 | DNA Overview retention curve repeated. |
| 01:21 | DNA Overview retention curve repeated. |
| 01:22 | DNA Overview carousel: subscribers +3; then navigation transition. |
| 01:23 | DNA detail and brief navigation overlap. |
| 01:24 | Content inventory; moving to Elephant / Giants. |
| 01:25 | Content inventory; moving to Elephant / Giants. |
| 01:26 | Opening Elephant detail; loading/transition. |
| 01:27 | Elephant detail: 0:24, Feb 6 2026, Public; Other notices; 16.7K views, 62.0 h. |
| 01:28 | Elephant detail: 0:24, Feb 6 2026, Public; Other notices; 16.7K views, 62.0 h. |
| 01:29 | Elephant detail/comments: creator question about scariest ancient giant, with reply. |
| 01:30 | Elephant analytics opening/Overview loading; no overview values established. |
| 01:31 | Elephant analytics opening/Overview loading; no overview values established. |
| 01:32 | Elephant analytics opening/Overview loading; no overview values established. |
| 01:33 | Elephant Reach opening/partially loaded. |
| 01:34 | Elephant Reach: feed 91.4%, search 7.4%, hashtags 0.5%, other features 0.3%, other 0.4%; platybelodon search 13.4%, elephant 1.7%, honey badger 0.7%; external Creator Studio 50.0%, WhatsApp 33.3% (external subset). |
| 01:35 | Elephant Reach: feed 91.4%, search 7.4%, hashtags 0.5%, other features 0.3%, other 0.4%; platybelodon search 13.4%, elephant 1.7%, honey badger 0.7%; external Creator Studio 50.0%, WhatsApp 33.3% (external subset). |
| 01:36 | Elephant Reach: feed 91.4%, search 7.4%, hashtags 0.5%, other features 0.3%, other 0.4%; platybelodon search 13.4%, elephant 1.7%, honey badger 0.7%; external Creator Studio 50.0%, WhatsApp 33.3% (external subset). |
| 01:37 | Elephant Engagement loading. |
| 01:38 | Elephant Engagement: 9.8K engaged views; Hype 0; stayed 77.7%, swiped 22.3%. |
| 01:39 | Elephant retention: 0:22 / 92.5%; stay/swipe repeated. |
| 01:40 | Elephant engaged views curve: 9.8K, rapid early rise and long tail. |
| 01:41 | Elephant carousel: 9.5K unique viewers. |
| 01:42 | Elephant carousel: 62.0 hours watch time. |
| 01:43 | Elephant carousel: average view duration 0:22. |
| 01:44 | Elephant carousel: average view duration 0:22. |
| 01:45 | Elephant Audience navigation/loading. |
| 01:46 | Elephant Audience navigation/loading. |
| 01:47 | Elephant Audience: insufficient behavior data; other watched uploads listed. |
| 01:48 | Elephant Audience carousel: subscribers +17. |
| 01:49 | Elephant devices: mobile 88.9%, TV 5.4%, tablet 3.4%, computer 2.2%; ages below. |
| 01:50 | Elephant age distribution and male 89.8% / female 10.2% entering view. |
| 01:51 | Elephant geography: India 63.6%, Pakistan 7.0%, Bangladesh 2.5%; no CC 98.7%. |
| 01:52 | Returning to inventory; brief UI overlap. |
| 01:53 | Content inventory scrolling through same uploads; date-named zero-view rows visible. |
| 01:54 | Content inventory scrolling through same uploads; date-named zero-view rows visible. |
| 01:55 | Content inventory scrolling through same uploads; date-named zero-view rows visible. |
| 01:56 | Content inventory scrolling through same uploads; date-named zero-view rows visible. |
| 01:57 | Content inventory scrolling through same uploads; date-named zero-view rows visible. |
| 01:58 | Content inventory scrolling through same uploads; date-named zero-view rows visible. |
| 01:59 | Content inventory scrolling through same uploads; date-named zero-view rows visible. |
| 02:00 | Content inventory scrolling through same uploads; date-named zero-view rows visible. |
| 02:01 | Content inventory scrolling through same uploads; date-named zero-view rows visible. |
| 02:02 | Dashboard return, partially scrolled. |
| 02:03 | Dashboard: 87 subscribers; recent 224 views / 0.6 h; latest-published cards. |
| 02:04 | Dashboard: 87 subscribers; recent 224 views / 0.6 h; latest-published cards. |
| 02:05 | Dashboard: 87 subscribers; recent 224 views / 0.6 h; latest-published cards. |
| 02:06 | Dashboard: 87 subscribers; recent 224 views / 0.6 h; latest-published cards. |
| 02:07 | Channel analytics loading. |
| 02:08 | Channel Overview: 224 views last 28 days, 154 above usual; top content Elephant 217, Terminator Pig 5, POV 1, Last Thing 1. |
| 02:09 | Channel Overview: 224 views last 28 days, 154 above usual; top content Elephant 217, Terminator Pig 5, POV 1, Last Thing 1. |
| 02:10 | Channel Overview: 224 views last 28 days, 154 above usual; top content Elephant 217, Terminator Pig 5, POV 1, Last Thing 1. |
| 02:11 | Channel Overview: 224 views last 28 days, 154 above usual; top content Elephant 217, Terminator Pig 5, POV 1, Last Thing 1. |
| 02:12 | Channel Overview: 224 views last 28 days, 154 above usual; top content Elephant 217, Terminator Pig 5, POV 1, Last Thing 1. |
| 02:13 | Channel Overview scrolled: same top content; realtime 7 views / 48 h. |
| 02:14 | Channel Overview scrolled: same top content; realtime 7 views / 48 h. |
| 02:15 | Channel Overview repeated before Audience navigation. |
| 02:16 | Channel Audience loading. |
| 02:17 | Channel Audience: monthly audience 104; new 97.1%, casual 2.9%, regular <0.1%. |
| 02:18 | Channel Audience: monthly audience 104; new 97.1%, casual 2.9%, regular <0.1%. |
| 02:19 | Audience carousel: subscribers 0; viewer-behavior shares repeated. |
| 02:20 | Audience carousel: subscribers 0; viewer-behavior shares repeated. |
| 02:21 | Popular with new viewers: Elephant 211, Terminator Pig 5, POV 1, Last Thing 1. |
| 02:22 | Viewer-online times insufficient; recent device shares entering view. |
| 02:23 | Recent devices: mobile 68.0%, tablet 16.6%, TV 9.7%, computer 5.7%; age/gender/geography unavailable. |
| 02:24 | Recent CC: none 97.8%, Czech auto-translated 0.9%, Portuguese 0.5%; unsubscribed watch time 100%; other audience reports insufficient. |
| 02:25 | Recent CC: none 97.8%, Czech auto-translated 0.9%, Portuguese 0.5%; unsubscribed watch time 100%; other audience reports insufficient. |
| 02:26 | Audience carousel repeated: subscribers 0. |
| 02:27 | Trends / Explore topics screen: example chips, not established channel-specific demand. |
| 02:28 | Back to Audience: subscribers 0; behavior and popular-with-new-viewers repeated. |
| 02:29 | Back to Audience: subscribers 0; behavior and popular-with-new-viewers repeated. |
| 02:30 | Back to Audience: subscribers 0; behavior and popular-with-new-viewers repeated. |
| 02:31 | Back to Audience: subscribers 0; behavior and popular-with-new-viewers repeated. |
| 02:32 | Channel Content analytics loading. |
| 02:33 | Recent Shorts sources: search 84.8%, feed 10.3%, hashtag pages 2.7%; remixes unavailable. |
| 02:34 | Recent Shorts sources: search 84.8%, feed 10.3%, hashtag pages 2.7%; remixes unavailable. |
| 02:35 | Recent search terms: platybelodon 61.6%, deinotherium elephant 1.6%, elephant evolution 0.5%. |
| 02:36 | Content carousel: views 224; stayed 70.2%, swiped 29.8%. |
| 02:37 | Content carousel: engaged views 119; 113% above previous 28 days; stay/swipe repeated. |
| 02:38 | Content carousel: likes 4; 100% above previous 28 days. |
| 02:39 | Content carousel: subscribers +1; stay/swipe repeated. |
| 02:40 | Back to Overview: 224 views. |
| 02:41 | Overview subscriber card: 0; discrepancy with Content +1 preserved. |
| 02:42 | Content subscriber card +1 repeated. |
| 02:43 | Overview top content repeated; realtime 7, all shown against Elephant. |

**02:44–02:44.461:** final fractional segment is not separately represented in the one-Hz sample set; no additional finding claimed.
