# V11 - Long-Form Viral Idea: 10x Forensic Selection Study

> **Roman Urdu note:** Aapne kaha tha *"abhi viral idea choose Karna ha 1"* aur *"ach ese video nhi banani abhi"*. Isliye ye file **sirf 1 idea ka final selection + uski microscope-level forensic** hai. Koi video nahi bani, koi upload/publish nahi hua, koi YouTube Data API call nahi hua. Neeche har claim ka source hai aur har missing cheez ko "pending / unverified" likha hai.

**Edition:** `v11_long_form_viral_idea_selection_2026-11-05`  
**Branch:** `arena/2b012328-monarch-overall-work` · **HEAD at selection:** `e0f8e1cfb959fc38da5a1b60634d2cd29d0ef6d4`  
**Status:** `idea_selected_video_not_built`  
**Deliverable:** 1 chosen long-form idea + evidence, scoring, blueprint, risk ledger  
**Machine-readable:** `long_form_viral_idea_v11.json`, `candidate_scoring_v11.json`, `sources_v11.json`, `api_capability_audit_v11.json`

---

## 0. Pehle seedha jawab (TL;DR)

### ✅ Chosen idea (1 hi)

**`REPLAY LAB Ep.1 - The Upside-Down Face: 42.7 Seconds of NASA Footage, Explained Frame by Frame`**

> One official NASA clip. Eight replay passes. Ten-plus minutes of optics, microgravity, native audio, edit anatomy and myth-vs-fact - without ever claiming CGI, endorsement or a guaranteed result.

- **Hook:** *"That is not a lens. Watch the face inside that floating water sphere flip upside down - then stay, because every replay hides a different layer."*
- **Format:** long-form landscape 16:9, 10-12 min target (11:00 including teaser), 30fps, H.264 + AAC
- **Weighted score:** `93.3 / 100` (runner-up `AN-01` = `82.4`; minimum pass = `75.0`)
- **Source:** ONE locked NASA asset `art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman` [13](https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman) + V10 ledgers [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10)
- **Kyun:** YouTube khud "spikes" ko *rewatched or shared moments* kehta hai [3](https://support.google.com/youtube/answer/9314415?hl=en) - aur ye idea poora replay-first hai. Short se long-form funnel official 2026 direction se match karta hai [1](https://blog.youtube/inside-youtube/the-future-of-youtube-2026/) [2](https://blog.youtube/news-and-events/made-on-youtube-creators-shorts-series-tv-features/) [9](https://blog.youtube/news-and-events/youtube-monetization-qualified-watch-hours-shorts-views/).

### ⚠️ Do line jo main jhooth nahi bolunga

- **"API se live best viral channels dekha"** - nahi. Is workspace me YouTube Data API key nahi hai, isliye `videos.list` / `search.list` / `channels.list` **0 calls** kiye. Official API docs [6](https://developers.google.com/youtube/v3/docs/videos/list) [7](https://developers.google.com/youtube/v3/docs/search/list) [8](https://developers.google.com/youtube/v3/docs/videoCategories/list) + public/official pages + committed workspace evidence use kiye. §1 me poora audit hai.
- **"Millions of views pakke"** - nahi. Wikipedia ke top-30 me children's songs aur music videos hain, science explainers nahi [10](https://en.wikipedia.org/wiki/List_of_most-viewed_YouTube_videos). Hum idea ko depth, replay craft aur evidence integrity ke liye chun rahe hain, guaranteed reach ke liye nahi.

---

## 1. Honest evidence boundary - "API se" ka sach

Aapne bola *"research karo api se ... best viral growing channels ... millions views laane wali videos ko dekho"*. Maine ye check kiya, aur result khul ke likh raha hoon:

| Check | Result |
| --- | --- |
| Env me YouTube/Google API key variable | **NOT PRESENT** (value kabhi print/store nahi kiya) |
| `config/youtube.json` / `config/api_keys.json` / `.env` | absent |
| `config/channels.json` | present [27](workspace://config/channels.json) |
| Bash outbound allowlist | github.com, codeload, api.github.com, npm, pypi, files.pythonhosted.org |
| YouTube Data API calls actually made | **0** |
| Official API docs fetched | videos.list [6](https://developers.google.com/youtube/v3/docs/videos/list), search.list [7](https://developers.google.com/youtube/v3/docs/search/list), videoCategories.list [8](https://developers.google.com/youtube/v3/docs/videoCategories/list) |
| Web research actually done | 10 queries (depth 2), 50 results, plus official pages fetched directly (YouTube Blog, Help, API docs, NASA guidance, Wikipedia) |

### 1.1 API kya de sakta tha (aur kya nahi)

| Method | Kya milta | Quota | Doc |
| --- | --- | --- | --- |
| videos.list | title, channelId, categoryId, publishedAt, viewCount, likeCount, commentCount, duration | 1 unit per call | [6](https://developers.google.com/youtube/v3/docs/videos/list) |
| search.list | videoId + snippet only; statistics require a follow-up videos.list | 100 calls per day in the Search Queries bucket (1 unit in that bucket) | [7](https://developers.google.com/youtube/v3/docs/search/list) |
| channels.list | subscriberCount, viewCount, videoCount, channel title | 1 unit per call | [29](https://developers.google.com/youtube/v3/docs/channels/list) |
| videoCategories.list | assignable category IDs and labels | 1 unit per call | [8](https://developers.google.com/youtube/v3/docs/videoCategories/list) |

**Ready-to-run queries (execute NAHI kiye; key placeholder `REDACTED`):**

```text
GET https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&chart=mostPopular&regionCode=PK&videoCategoryId=28&maxResults=50&key=REDACTED
GET https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&order=viewCount&videoDuration=long&publishedAfter=2026-01-01T00:00:00Z&maxResults=50&key=REDACTED
GET https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id=REDACTED&key=REDACTED
GET https://www.googleapis.com/youtube/v3/videoCategories?part=snippet&regionCode=PK&key=REDACTED
```

**API ki hard limits (key ho tab bhi):**

- No breakout / outlier detection vs a channel baseline; must be built manually [25](https://outlierkit.com/resources/how-to-get-youtube-api-key/)
- No transcripts for arbitrary videos; captions.download requires OAuth + ownership [25](https://outlierkit.com/resources/how-to-get-youtube-api-key/)
- No keyword search-volume or competition data; the API returns videos, not demand [25](https://outlierkit.com/resources/how-to-get-youtube-api-key/)
- No semantic look-alike channel search; search.list matches keywords only [25](https://outlierkit.com/resources/how-to-get-youtube-api-key/)
- Impressions, CTR, watch time, average view duration, retention and revenue are OWNER-ONLY Studio / Analytics API data, not public Data API fields [4](https://support.google.com/youtube/answer/9313698?hl=en) [5](https://support.google.com/youtube/answer/12220281?hl=en) [25](https://outlierkit.com/resources/how-to-get-youtube-api-key/)
- Public view counts are a snapshot, not a forecast and not a guarantee of a future video's reach [10](https://en.wikipedia.org/wiki/List_of_most-viewed_YouTube_videos)

> **Bottom line:** live "best growing channels" ranking, verified competitor view counts, keyword volume, retention graphs, CTR/RPM - inme se koi bhi is session me available nahi tha. Jo third-party numbers niche dikhte hain, unhe **directional / unverified** label diya gaya hai, target ya proof nahi banaya gaya.

---

## 2. Research log (10 queries, microscope mode)

| # | Query | Kept refs | Takeaway |
| --- | --- | --- | --- |
| 1 | YouTube 2026 long-form video trends creators watch time official YouTube blog | 20, 21 | Third-party 2026 trend write-ups claim long-form/TV resurgence and multi-format advantage; all numeric growth multipliers in those posts are unverified and were NOT used as evidence. |
| 2 | Wikipedia list of most-viewed YouTube videos 2026 billions views | 10 | Fetched Wikipedia directly: top 30 = children's songs, music videos, one ad. Reality check: a science forensic long-form video is NOT in the billion-view genre, so 'millions of views' cannot be promised. |
| 3 | fastest growing YouTube channels 2026 science space documentary millions views | 22, 23 | Aggregator sites list large science channels and million-view science videos; subscriber/view figures are directional only, not verified by us and not used as targets. |
| 4 | YouTube viral video replay breakdown format hook retention rewatch wait what science explainer | 24 | Self-described manual analysis of 500 videos over 1M views reports curiosity-gap / pattern-interrupt / listicle hook patterns. Unofficial sample; used only as pattern vocabulary. |
| 5 | YouTube Data API videos.list search.list requires API key quota official documentation | 6, 25 | Confirmed official quota model and the API's hard limits; also fetched videos.list and search.list docs directly. |
| 6 | NASA Artemis II Fun with Water Bubbles upside down face viral 2026 | 14, 15, 16 | Multiple independent reports describe the same playful water sphere, refraction-inverted face, straw catch and 'uniquely human' public reaction. That is public interest evidence, NOT a YouTube view count. |
| 7 | site:blog.youtube 2026 long-form TV viewing creators official YouTube | 1, 2, 9 | Official first-party 2026 direction: every format on every screen, TV as top interface for over half of top-100 creators, episodic/series structures, qualified long-form watch hours. |
| 8 | YouTube official help watch time average view duration audience retention analytics | 3, 4, 5 | Official metric definitions. Critical: 'spikes' are moments viewers rewatched or shared - a replay-first idea is aligned with a documented retention signal, not a guessed algorithm hack. |
| 9 | NASA Artemis II water bubble video millions views social media viral May 2026 | 17, 18, 19 | Public reaction, a viewer safety question and a fact-check about a broadcast glitch being misused for 'staged' claims. Supplies myth-vs-fact material and a misinformation guardrail. |
| 10 | long-form science documentary YouTube millions views 2026 space physics explainer | 22 | Directional curiosity-gap documentary titles with reported million-view examples; unverified, used only to name the format family. |

### 2.1 Source-reliability ladder

| Tier | Kya hai | Kaise use kiya |
| --- | --- | --- |
| A - official first-party | YouTube Blog / Help / Developer docs, NASA guidance [1](https://blog.youtube/inside-youtube/the-future-of-youtube-2026/) [3](https://support.google.com/youtube/answer/9314415?hl=en) [12](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/) | Factual claims, metric definitions, policy guardrails |
| B - public snapshot | Wikipedia most-viewed list [10](https://en.wikipedia.org/wiki/List_of_most-viewed_YouTube_videos) | Reality check only; page khud kehta hai dynamic list kabhi complete na ho |
| C - public reporting | Orbital Today, Yahoo, Daily Mail, Gazeta, AFP, Nautilus [14](https://orbitaltoday.com/2026/05/12/a-tiny-water-droplet-became-the-star-of-artemis-ii-video/) [18](https://factcheck.afp.com/doc.afp.com.A6WV668) [19](https://nautil.us/astronauts-as-influencers-1279855) | Public interest / reaction / myth-vs-fact material; NOT YouTube analytics |
| D - directional third-party | TVREV/Tubular, vidIQ, TubeStats, FalconVid, Fluxnote, OutlierKit [20](https://www.tvrev.com/news/tube-trends-how-youtube-creators-are-using-longer-videos-to-compete-with-tv) [24](https://fluxnote.io/blog/short-form-hook-library-500-viral-videos) [25](https://outlierkit.com/resources/how-to-get-youtube-api-key/) | Format vocabulary only; har number par 'unverified' label |
| E - workspace evidence | V10 ledgers, config, prior forensic study [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10) [27](workspace://config/channels.json) [28](workspace://research/caught_on_camera_commentary_v10/CAUGHT_ON_CAMERA_FORENSIC_STUDY.md) | Locked source, rubric, kill switches, existing assets |

---

## 3. Official findings - idea ko inhone shape diya

1. Every format on every screen; long-form, Shorts, podcasts, livestreams; Shorts 200B daily views; YouTube #1 US streaming watchtime nearly 3 years. [1](https://blog.youtube/inside-youtube/the-future-of-youtube-2026/)
2. Over half of top-100 creators have TV as most watched interface; episodic Shorts series; 6.5B microdrama views H1 2026. [2](https://blog.youtube/news-and-events/made-on-youtube-creators-shorts-series-tv-features/)
3. Intro = % watching after 30s; spikes = rewatched/shared; dips = skips; typical retention compares 10 similar-length videos. [3](https://support.google.com/youtube/answer/9314415?hl=en)
4. Qualified YPP watch hours come from public long-form / archived livestreams, not Shorts watch hours. [9](https://blog.youtube/news-and-events/youtube-monetization-qualified-watch-hours-shorts-views/)
5. Top-30 most-viewed videos are children's songs, music videos and one ad - not science explainers. [10](https://en.wikipedia.org/wiki/List_of_most-viewed_YouTube_videos)
6. 93% of US 18-27 year olds and 79% of US teachers say YouTube helps learning. [1](https://blog.youtube/inside-youtube/the-future-of-youtube-2026/)

**Sabse important inference:** YouTube Help kehta hai *"Spikes are moments in your video that were rewatched or shared"* [3](https://support.google.com/youtube/answer/9314415?hl=en). V10 Short me pehle se 1.5s payoff flash + 44.24s loop-back + 8-beat replay structure hai [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10). To "replay" koi andaza nahi, ek **documented retention signal** hai. Isliye winner idea ka naam hi `REPLAY LAB` hai.

**Reality check:** all-time top videos music/kids hain [10](https://en.wikipedia.org/wiki/List_of_most-viewed_YouTube_videos); 20+ minute uploads badh rahe hain (directional) [20](https://www.tvrev.com/news/tube-trends-how-youtube-creators-are-using-longer-videos-to-compete-with-tv); science channels bade hain (unverified aggregates) [22](https://falconvid.ai/blog/science-youtube-channels-that-make-money) [23](https://tubestats.io/channels/science). Inse hum **format direction** lete hain, **view-count promise** nahi.

---

## 4. 8 candidates - weighted 10-axis scoring

Weights sum = `10.0`, max = `100.0`, minimum pass = `75.0`. Har axis evidence-linked hai; koi bhi score measured audience result nahi hai.

| Axis | Weight | Kyun |
| --- | --- | --- |
| Hook / first-30s stop power | 1.2 | Official 'Intro' metric = % still watching after 30s [3](https://support.google.com/youtube/answer/9314415?hl=en) |
| Replay / rewatch signal | 1.2 | Official 'Spikes' = moments rewatched or shared [3](https://support.google.com/youtube/answer/9314415?hl=en) |
| Source chain certainty | 1.3 | Prior V10 rubric's rights-chain axis, escalated for long-form [28](workspace://research/caught_on_camera_commentary_v10/CAUGHT_ON_CAMERA_FORENSIC_STUDY.md) |
| Fun / emotional spike | 1.0 | User's 'mazedar / next level' requirement; config bans reaction-only and clickbait-with-no-payoff [27](workspace://config/channels.json) |
| Depth runway for 8-12 min | 1.2 | User's 'microscope / 10x think / detailed forensic' requirement; config long-form target 8-12 min [27](workspace://config/channels.json) |
| Long-form / TV / multi-format fit | 0.9 | Official 2026 direction [1](https://blog.youtube/inside-youtube/the-future-of-youtube-2026/) [2](https://blog.youtube/news-and-events/made-on-youtube-creators-shorts-series-tv-features/) [9](https://blog.youtube/news-and-events/youtube-monetization-qualified-watch-hours-shorts-views/) |
| Feasibility with existing assets | 0.9 | One locked NASA master + V10 WAVs, PNGs and ledgers already in the repo [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10) |
| Series / repeatability | 0.7 | Official Shorts series / episodic push [2](https://blog.youtube/news-and-events/made-on-youtube-creators-shorts-series-tv-features/); config 'one concept, one demo' [27](workspace://config/channels.json) |
| Rights / legal risk (10 = low risk) | 0.8 | NASA promotional-content and current-astronaut imagery gate [12](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/) |
| Claim integrity | 0.8 | No guaranteed virality, no legal clearance, no human approval, no perfection [12](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/) [10](https://en.wikipedia.org/wiki/List_of_most-viewed_YouTube_videos) |

### 4.1 Score table

| ID | Idea | hook stop power | replay rewatch signal | source chain certainty | fun emotional spike | depth runway 10min | long form tv multiformat fit | production feasibility existing assets | series scalability | rights legal risk inverse | claim integrity | Total | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RL-01 | REPLAY LAB Ep.1 - The Upside-Down Face | 10 | 10 | 10 | 9 | 10 | 10 | 9 | 10 | 4 | 10 | 93.3 | WINNER |
| AN-01 | One Clip, 8 Beats - anatomy of a 49-second Short | 7 | 8 | 10 | 6 | 9 | 8 | 9 | 7 | 8 | 10 | 82.4 | strong_second_folded_into_winner |
| AF-01 | How We Fixed a 'Buffering Glitch' - audio forensics behind the scenes | 6 | 5 | 10 | 6 | 9 | 7 | 8 | 5 | 8 | 9 | 73.6 | runner_up_narrow |
| EX-01 | Why Water Becomes a Crystal Ball in Space (straight explainer) | 6 | 5 | 9 | 6 | 7 | 8 | 8 | 6 | 5 | 9 | 69.1 | reject_generic |
| MS-01 | Artemis II: the 10-day mission that got weirdly funny | 8 | 7 | 5 | 9 | 8 | 9 | 4 | 7 | 3 | 6 | 66.9 | reject_source_scope |
| DY-01 | I Tried to Recreate the NASA Water Bubble on Earth | 8 | 7 | 6 | 9 | 6 | 8 | 3 | 6 | 4 | 5 | 63.3 | reject_scope |
| RL-02 | 7 Real Space Moments That Look Fake (ranked compilation) | 9 | 9 | 3 | 9 | 7 | 8 | 3 | 8 | 2 | 4 | 63.2 | reject |
| CG-01 | 'Is It CGI?' Court - 10 internet claims judged frame by frame | 9 | 8 | 2 | 8 | 7 | 7 | 2 | 8 | 1 | 2 | 55.5 | reject_high_risk |

### 4.2 Har candidate ka forensic verdict

#### `RL-01` - REPLAY LAB Ep.1 - The Upside-Down Face — **93.3**

*42.7 seconds of NASA footage, explained frame by frame in a 10-12 minute forensic replay documentary built on the ONE locked Artemis II water-bubble master.*

Evidence: V10 already has 8 beats / 118 words / loop-back at 44.24s [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10) · Official spikes = rewatched or shared moments [3](https://support.google.com/youtube/answer/9314415?hl=en) · Official every-format / TV / long-form watch-hours direction [1](https://blog.youtube/inside-youtube/the-future-of-youtube-2026/) [2](https://blog.youtube/news-and-events/made-on-youtube-creators-shorts-series-tv-features/) [9](https://blog.youtube/news-and-events/youtube-monetization-qualified-watch-hours-shorts-views/) · Single official NASA asset with recorded ID and SHA [13](https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman) [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10) · Public reporting supplies the 'uniquely human' playfulness and the safety question [16](https://www.dailymail.com/sciencetech/article-15807427/Incredible-video-shows-water-floating-space.html) [17](https://www.gazetaexpress.com/en/Artemis-II-astronauts-experiment-with-a-drop-of-water-in-space--NASA-footage-amazes-the-web/)

**Kill switches hit:** none

**Open gates / weaknesses:** NASA promotional / current-astronaut imagery clearance gate remains OPEN [12](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/) · human legal review and human creative approval remain false

#### `AN-01` - One Clip, 8 Beats - anatomy of a 49-second Short — **82.4**

*Meta breakdown of V10's own edit ledger: hook, 118 words, captions, payoff flash, loop-back.*

Evidence: Complete edit ledger, caption timings and QC already committed [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10)

**Kill switches hit:** none

**Open gates / weaknesses:** meta/creator-facing; less visceral than the actual footage · best used as a CHAPTER inside RL-01 rather than a standalone flagship

#### `AF-01` - How We Fixed a 'Buffering Glitch' - audio forensics behind the scenes — **73.6**

*A 10-minute technical documentary on the V10 VO glitch diagnosis, waveform/spectrum evidence and continuous slope conditioner.*

Evidence: All audio WAVs, PNGs and QC JSONs already exist [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10) · Strong 'build in public' fit for the legacy Monarch Lab slot [27](workspace://config/channels.json)

**Kill switches hit:** none

**Open gates / weaknesses:** narrow creator/tools audience; weaker 'mazedar' general appeal · still lacks human listening sign-off [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10)

#### `EX-01` - Why Water Becomes a Crystal Ball in Space (straight explainer) — **69.1**

*A conventional 8-minute science explainer on surface tension and refraction in microgravity.*

Evidence: Science-explainer format family is well populated [22](https://falconvid.ai/blog/science-youtube-channels-that-make-money) [23](https://tubestats.io/channels/science)

**Kill switches hit:** none

**Open gates / weaknesses:** generic; weak differentiation; 'voice-over stock documentary' is explicitly banned in the legacy config [27](workspace://config/channels.json)

#### `MS-01` - Artemis II: the 10-day mission that got weirdly funny — **66.9**

*Mission narrative with the water bubble as the human-interest centerpiece.*

Evidence: Cross-platform Artemis II exposure documented [19](https://nautil.us/astronauts-as-influencers-1279855) · Mission context reported alongside the bubble [15](https://www.yahoo.com/news/articles/watch-artemis-ii-astronauts-fun-193852742.html) [16](https://www.dailymail.com/sciencetech/article-15807427/Incredible-video-shows-water-floating-space.html)

**Kill switches hit:** `multiple_unverified_or_unlicensed_clips`

**Open gates / weaknesses:** needs additional official clips and mission-fact verification · broadcast/stream audience figures must not be recast as YouTube views [19](https://nautil.us/astronauts-as-influencers-1279855)

#### `DY-01` - I Tried to Recreate the NASA Water Bubble on Earth — **63.3**

*DIY challenge attempting the liquid-lens effect with household materials.*

Evidence: DIY experiment format is popular in the science family [23](https://tubestats.io/channels/science)

**Kill switches hit:** `nasa_endorsement_or_official_status_claim`

**Open gates / weaknesses:** requires original filming not present in this workspace · physics of a ground-based sphere is not equivalent to microgravity; high inaccuracy risk

#### `RL-02` - 7 Real Space Moments That Look Fake (ranked compilation) — **63.2**

*A ranked long-form compilation of multiple NASA/space clips, each with replay and explanation.*

Evidence: Only ONE clip is actually sourced and QC'd in this workspace [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10) · NASA promotional gate multiplies with each additional current-astronaut clip [12](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/)

**Kill switches hit:** `multiple_unverified_or_unlicensed_clips`, `current_astronaut_imagery_in_promotional_content_without_written_clearance`, `fabricated_analytics_or_view_counts`

**Open gates / weaknesses:** would require a full new rights-clearance pass for 6 more clips

#### `CG-01` - 'Is It CGI?' Court - 10 internet claims judged frame by frame — **55.5**

*Myth-busting courtroom format judging viral clips as real or fake.*

Evidence: AFP documents how an Artemis II broadcast glitch was already misused for false 'staged' claims [18](https://factcheck.afp.com/doc.afp.com.A6WV668)

**Kill switches hit:** `multiple_unverified_or_unlicensed_clips`, `staged_or_conspiracy_amplification`, `ai_free_imagery_or_no_cgi_claim_without_verification`, `fabricated_analytics_or_view_counts`

**Open gates / weaknesses:** defamation / misinformation risk; rights nightmare


**Winner:** `RL-01` at `93.3`. Runner-up `AN-01` ko reject nahi kiya - usse winner ke Chapter 9 ("Microscope on the edit") me fold kiya gaya, kyunki uski sabse badi strength (committed edit ledger) exactly wahan fit baithti hai [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10).

---

## 5. 10x microscope - winner ka forensic dissection

**L1 - Hook physics.** First 30s = official 'Intro' metric [3](https://support.google.com/youtube/answer/9314415?hl=en). Cold open me 3 silent replays, koi text nahi, sirf ulta chehra + native audio. Pattern interrupt [24](https://fluxnote.io/blog/short-form-hook-library-500-viral-videos) without clickbait-with-no-payoff [27](workspace://config/channels.json).

**L2 - Replay mechanics.** 'Spikes' = rewatched/shared [3](https://support.google.com/youtube/answer/9314415?hl=en). Har chapter ek naya replay pass (0.25x / 0.5x / 1x / freeze) with a NEW question - isliye rewatch ka reason badalta hai, same clip baar baar nahi lagta.

**L3 - Source chain.** ONE NASA ID, page, 2026-04-04 date, original SHA, vertical master SHA, rights ledger [13](https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman) [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10). Koi doosra clip add nahi - yahi sabse bada competitor-killer hai.

**L4 - Physics depth.** Surface tension -> sphere; curved interface -> refraction -> image inversion [15](https://www.yahoo.com/news/articles/watch-artemis-ii-astronauts-fun-193852742.html) [16](https://www.dailymail.com/sciencetech/article-15807427/Incredible-video-shows-water-floating-space.html). Simple ORIGINAL diagram, koi stock b-roll hero nahi [27](workspace://config/channels.json).

**L5 - Brain / misinformation.** 'CGI lagta hai' = expectation violation [24](https://fluxnote.io/blog/short-form-hook-library-500-viral-videos); lekin AFP-documented broadcast-glitch conspiracy ko amplify nahi karna [18](https://factcheck.afp.com/doc.afp.com.A6WV668). Koi 'No CGI' / '100% real' claim nahi.

**L6 - Audio forensics.** NASA native crew audio retained; V10 chain me no music/SFX/bed/substitution [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10). 9/9 gates objective evidence hain, human listening abhi false hai.

**L7 - Edit forensics.** 8 beats, 118 words, word-by-word captions, REFRACTION 23.42-29.90s, credit 44.24-49.40s, loop-back [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10).

**L8 - Rights / legal.** NASA: short-form social generally promotional; current-astronaut imagery promotional content me 'may not be used' [12](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/). Ye idea-selection gate OPEN hai; commercial publish se pehle written clearance + human legal review.

**L9 - Metrics honesty.** Impressions/CTR/watch time/retention owner-only Studio data hain [4](https://support.google.com/youtube/answer/9313698?hl=en) [5](https://support.google.com/youtube/answer/12220281?hl=en) [25](https://outlierkit.com/resources/how-to-get-youtube-api-key/). Hum inhe predict nahi karte; sirf official definitions ke mutabiq structure banate hain.

**L10 - Failure modes.** Thin 42.7s source ko 10 min tak kheenchna sabse bada risk. Isliye 12 chapters alag-alag *lenses* hain (physics, audio, edit, myth, mission), na ki same clip ko 12 baar chipkaya gaya. Phir bhi human pacing review pending hai.

---

## 6. Chosen idea - full blueprint (proposal ONLY)

**Working title:** `The Upside-Down Face: 42.7 Seconds of NASA Footage, Explained Frame by Frame` (76 chars, limit 100 [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10))

**Alt titles:**

- `Replay Lab Ep.1 - Why NASA's Water Bubble Flipped an Astronaut's Face`
- `That Is Not a Lens: The Forensic Story of Artemis II's Floating Water Ball`
- `10 Minutes on 42 Seconds: What Really Happened Inside That NASA Water Bubble`

**Logline:** One official NASA clip. Eight replay passes. Ten-plus minutes of optics, microgravity, native audio, edit anatomy and myth-vs-fact - without ever claiming CGI, endorsement or a guaranteed result.

**Hook line:** *"That is not a lens. Watch the face inside that floating water sphere flip upside down - then stay, because every replay hides a different layer."*

**Runtime / format:** long-form landscape 16:9, 10-12 min target (11:00 including teaser), 30fps, H.264 + AAC

### 6.1 Chapter ledger (11:00 including teaser)

| Time | Chapter | Content |
| --- | --- | --- |
| 0:00-0:20 | Cold open: three silent replays | The upside-down face, no text, native crew audio only. Then the line: 'That is not a lens.' |
| 0:20-1:00 | The promise | 42.7 seconds of NASA footage, ten-plus minutes of 'how did that happen?'. State plainly: one source, no re-enactment, no outcome promise. |
| 1:00-2:10 | The mission in 60 seconds | Artemis II lunar flyby, 10-day mission, record distance, NASA credit, 'no endorsement implied'. Use only officially recorded facts [13](https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman) [15](https://www.yahoo.com/news/articles/watch-artemis-ii-astronauts-fun-193852742.html). |
| 2:10-3:30 | Why water becomes a sphere | Surface tension in microgravity; one simple ORIGINAL diagram, not stock b-roll as hero [27](workspace://config/channels.json). |
| 3:30-5:00 | The liquid lens | Refraction through a curved interface, image inversion; freeze at 23.42s, REFRACTION label, slow-motion replay [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10) [15](https://www.yahoo.com/news/articles/watch-artemis-ii-astronauts-fun-193852742.html). |
| 5:00-6:20 | Why your brain says 'CGI' | Expectation violation and pattern interrupt [24](https://fluxnote.io/blog/short-form-hook-library-500-viral-videos); explicitly do NOT amplify the broadcast-glitch 'staged' conspiracy [18](https://factcheck.afp.com/doc.afp.com.A6WV668). No 'No CGI' claim. |
| 6:20-7:30 | The crew's reaction | Native audio retained, laughter, straw catch and release, the 'uniquely human' public framing [16](https://www.dailymail.com/sciencetech/article-15807427/Incredible-video-shows-water-floating-space.html) [17](https://www.gazetaexpress.com/en/Artemis-II-astronauts-experiment-with-a-drop-of-water-in-space--NASA-footage-amazes-the-web/). |
| 7:30-8:40 | Microscope on the audio | Native crew audio kept; no music, SFX, procedural bed or audio substitution. Reference V10's 9/9 audio gates as OBJECTIVE evidence only, with human listening still pending [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10). |
| 8:40-9:40 | Microscope on the edit (AN-01 folded in) | 8 beats, 118 words, word-by-word captions, 1.5s payoff flash, loop-back at 44.24s. This is where the runner-up idea becomes a chapter [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10). |
| 9:40-10:20 | Myth vs fact | Not CGI / not a lens / not official NASA / no invented date / no endorsement / no safety verdict. Include the viewer water-near-electronics question as an open question, not an answer [17](https://www.gazetaexpress.com/en/Artemis-II-astronauts-experiment-with-a-drop-of-water-in-space--NASA-footage-amazes-the-web/). |
| 10:20-10:50 | Final clean replay + loop-back | One uninterrupted pass, then the loop-back; on-screen credit 'Source: NASA / Artemis II' [11](https://www.nasa.gov/nasa-brand-center/images-and-media/) [13](https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman). |
| 10:50-11:00 | Genuine question + series teaser | One specific question and 'Replay Lab' next-episode teaser. No like/subscribe incentive, no reward, no coercion. |

### 6.2 Kyun ye idea jeeta

- It is built around REPLAYS, which YouTube's own Help defines as 'spikes' - moments viewers rewatched or shared [3](https://support.google.com/youtube/answer/9314415?hl=en). This is a documented retention signal, not an invented algorithm trick.
- It converts the already-locked V10 Short into a long-form depth layer, matching the official 2026 every-format / TV / qualified-watch-hours direction [1](https://blog.youtube/inside-youtube/the-future-of-youtube-2026/) [2](https://blog.youtube/news-and-events/made-on-youtube-creators-shorts-series-tv-features/) [9](https://blog.youtube/news-and-events/youtube-monetization-qualified-watch-hours-shorts-views/).
- Source certainty is maximal: ONE official NASA asset with a recorded ID, page and SHA, plus 12 committed V10 evidence files [13](https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman) [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10). Every rejected multi-clip competitor fails here.
- The 'microscope / 10x' demand is literally the structure: optics, audio, edit ledger, myth-vs-fact, frame-level replay - enough honest runway for 10-12 minutes without padding.
- It is a SERIES pilot, not a one-off: 'one concept, one demo' [27](workspace://config/channels.json) plus the official episodic/Shorts-series push [2](https://blog.youtube/news-and-events/made-on-youtube-creators-shorts-series-tv-features/). Each future episode would still need its own cleared source.
- Reality check from the most-viewed list: billion-view videos are children's songs and music videos [10](https://en.wikipedia.org/wiki/List_of_most-viewed_YouTube_videos). We therefore choose this idea for depth, replay craft and evidence integrity - NOT because it guarantees millions of views.

### 6.3 Kaise banayenge (abhi NAHI banaya - phases ready hain)

| Phase | Detail |
| --- | --- |
| A - source audit | Re-verify the locked NASA asset ID, SHA and vertical master; re-read rights_ledger_v10.json; DO NOT add any second clip without a new clearance pass [12](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/) [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10). |
| B - script | Write a timed 10-12 min script with 3 hook variants; every factual line mapped to a source ledger entry; word-by-word caption timing generated from the script. |
| C - voice | Generic synthetic VO, user-selected voice-01 from the V10 lane; no real-person clone; no time-stretch; no music/SFX/procedural bed; NASA native audio retained [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10). |
| D - edit | 16:9 master, replay passes at 0.25x / 0.5x / 1x, original diagrams, on-screen credit, no baked platform UI, no clickbait overlays, safe areas maintained. |
| E - QC | Run the same nine audio gates + technical QC harness as V10; objective pass recorded separately from human listening / creative approval [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10). |
| F - metadata | Separate long-form title/description/tags/category/pinned-comment pack; no unrelated tags, no NASA official status, no endorsement, no guaranteed reach. |

### 6.4 Hard guardrails

- One official NASA source only; credit 'Source: NASA / Artemis II' and 'no endorsement implied' [11](https://www.nasa.gov/nasa-brand-center/images-and-media/) [12](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/).
- No 'No CGI', no '100% real', no AI-free imagery claim, no invented date or mission detail.
- No NASA insignia, no 'official NASA', no astronaut names used promotionally, no co-branding [12](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/).
- No music, SFX, procedural bed or substitution of NASA native audio [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10).
- No unrelated/misleading tags, no engagement coercion, no guaranteed virality/retention/views/RPM.
- No human approval, legal clearance, perfection or zero-omission claim.

---

## 7. Risk ledger / open gates

| Item | Status |
| --- | --- |
| Rights gate severity | HIGH |
| Finding | NASA states short-form social content is generally promotional and imagery with current astronauts may not be used in promotional content; identifiable current astronauts / possible CSA personnel appear in this footage [12](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/). |
| Consequence | A commercial, monetized, sponsored or otherwise promotional long-form publish must NOT proceed without written clearance and human legal review. This idea-selection pack does not resolve that gate. |
| human_legal_review | False |
| commercial_monetization_clearance | False |
| publicity_or_privacy_permission_obtained | False |
| not_a_legal_opinion | True |
| YouTube Data API key | NOT PRESENT - 0 calls |
| Live competitor analytics | NOT ACCESSED |
| Human creative / listening / full-motion approval | FALSE |
| Video rendered / published | FALSE |

---

## 8. "Bagair kisi kami ke" - jawaab imaandaari se

- Aapne 'bagair kisi kami / galati / flaws ke, kuch chhore miss kiye bagair' manga. Main ye claim nahi kar sakta: is workspace me YouTube Data API key nahi hai, live analytics nahi, channel ka private Studio data nahi, human listening / full-motion review nahi, aur na hi kisi future audience result ka pata hai [6](https://developers.google.com/youtube/v3/docs/videos/list) [25](https://outlierkit.com/resources/how-to-get-youtube-api-key/) [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10).
- Jo verify ho saka usse source ledger, reliability tier aur citation ke saath rakha hai; jo verify nahi ho saka usse 'unverified / directional / pending' likha hai. Ye honesty hi asli 'flaw-free' approach hai - chhupaana nahi.
- Official documentation bhi legal opinion nahi hai; NASA promotional gate khula hai [12](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/).
- Technical QC (jab bhi banega) objective record hoga; creative approval, legal clearance aur listening sign-off alag human gates rahenge [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10).

**Non-claim register (sab `false`):** `video_rendered`, `upload_or_publish_performed`, `youtube_data_api_called`, `api_key_available_in_workspace`, `live_channel_analytics_accessed`, `verified_current_trending_ranking`, `verified_competitor_view_counts`, `keyword_search_volume_data`, `retention_or_ctr_or_rpm_data`, `millions_of_views_guaranteed`, `virality_guaranteed`, `audience_result_guaranteed`, `human_creative_approval`, `human_native_audio_listening`, `human_full_motion_review`, `human_legal_review`, `commercial_monetization_clearance`, `written_astronaut_or_csa_permission`, `legal_opinion`, `perfection_or_zero_omission`, `nasa_endorsement`, `official_nasa_status`, `exact_reference_match`, `technical_qc_pass_for_new_video`

---

## 9. Exact next action

**Aapka agla faisla:** kya `REPLAY LAB Ep.1 - The Upside-Down Face` idea approve hai? 
Agar haan, to tab Phase A (source audit) se shuru hoga - aur tab bhi **pehle** NASA promotional clearance / human legal review ka gate, aur human creative approval, alag se record karna hoga. Is turn me maine **sirf idea choose kiya hai**: na render, na VO, na API call, na upload, na publish, na clearance claim.

Agar aap apne Google Cloud project me YouTube Data API enable karte hain, to §1.1 ki queries ready hain (key chat me mangi ya store nahi ki gayi). Tab live `mostPopular` / channel statistics verify kar ke is study ko ek addendum se update kiya ja sakta hai - bina kisi guarantee ke.

---

## 10. Source ledger

| Ref | Source | Authority | Reliability | Used for |
| --- | --- | --- | --- | --- |
| [1](https://blog.youtube/inside-youtube/the-future-of-youtube-2026/) | From the CEO: What's coming to YouTube in 2026 (Neal Mohan) | official_youtube_blog | official_first_party | Every format on every screen; long-form, Shorts, music, livestreams, podcasts; Shorts averages 200B daily views; YouTube #1 in US streaming watchtime nearly 3 years (Nielsen); 93% of US 18-27 year olds and 79% of US teachers say YouTube helps learning (2025 Kantar / Oxford Economics); creators as new studios; $100B paid to creators in 4 years. |
| [2](https://blog.youtube/news-and-events/made-on-youtube-creators-shorts-series-tv-features/) | Connect with creators on the biggest screen (Made On YouTube 2026) | official_youtube_blog | official_first_party | Over half of YouTube's top 100 creators have TV as their most watched interface; Shorts series / seasons / episodes; microdramas surpassed 6.5B views in H1 2026 with watch time +50% YoY and TV views +90% YoY; 300M users engage with posts daily. |
| [3](https://support.google.com/youtube/answer/9314415?hl=en) | Measure key moments for audience retention - YouTube Help | official_youtube_help | official_first_party | Intro = % still watching after first 30s; spikes = moments rewatched or shared; dips = skipped/abandoned; flat = watched start to finish; typical retention compares 10 latest videos of similar length; retention data takes 1-2 days; key moments need video >=60s and >=100 views. |
| [4](https://support.google.com/youtube/answer/9313698?hl=en) | Understand your YouTube engagement - YouTube Help | official_youtube_help | official_first_party | Engagement tab snapshot: watch time (hours), average view duration, views; audience retention report. |
| [5](https://support.google.com/youtube/answer/12220281?hl=en) | Understand your YouTube content performance - YouTube Help | official_youtube_help | official_first_party | Impressions, impressions CTR, views, average view duration, average percentage viewed, engaged views, unique viewers, regular viewers. |
| [6](https://developers.google.com/youtube/v3/docs/videos/list) | Videos: list - YouTube Data API v3 | official_developer_docs | official_first_party | chart=mostPopular returns most popular videos for a content region and video category; part=snippet,statistics returns categoryId, title, viewCount, likeCount; quota cost 1 unit; up to 50 IDs per call. |
| [7](https://developers.google.com/youtube/v3/docs/search/list) | Search: list - YouTube Data API v3 | official_developer_docs | official_first_party | Keyword search; 100 calls per day in the Search Queries quota bucket (1 unit in that bucket); default 25 results; type=video, order, publishedAfter, videoDuration filters exist. |
| [8](https://developers.google.com/youtube/v3/docs/videoCategories/list) | VideoCategories: list - YouTube Data API v3 | official_developer_docs | official_first_party | Returns categories associable with videos; regionCode makes the list region-specific; quota cost 1 unit. |
| [9](https://blog.youtube/news-and-events/youtube-monetization-qualified-watch-hours-shorts-views/) | Qualified watch hours and Shorts views (YPP) - YouTube Blog | official_youtube_blog | official_first_party | Qualified watch hours come from public long-form videos including podcasts and archived livestreams; Shorts watch hours do NOT count as qualified long-form watch hours. |
| [10](https://en.wikipedia.org/wiki/List_of_most-viewed_YouTube_videos) | List of most-viewed YouTube videos - Wikipedia | community_maintained | public_snapshot_not_authoritative | Top 30 most-viewed are children's songs, music videos and one advertisement; Baby Shark Dance 17.28B; since Bad Romance (2010) every #1 most-viewed video has been a music video; page self-describes as a dynamic list that may never satisfy completeness. |
| [11](https://www.nasa.gov/nasa-brand-center/images-and-media/) | NASA Brand Center - Images and Media | official_nasa_guidance | official_first_party | Acknowledge NASA as source; no implied endorsement; insignia / identifiable-person restrictions. |
| [12](https://www.nasa.gov/collaborating-with-nasa/strategic-partnerships/) | NASA Strategic Partnerships - Promotional Content | official_nasa_guidance | official_first_party | Exact wording: 'Short-form social media content generally is considered promotional content' and 'Imagery with ... current astronauts ... may not be used in promotional content'; NASA cannot endorse or appear to endorse; no co-branding/sponsorship. |
| [13](https://images.nasa.gov/details/art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman) | NASA image detail - Fun with Water Bubbles (Artemis II) | official_nasa_asset | official_first_party | Locked source ID, title 'Fun with Water Bubbles', 2026-04-04; the one clip already sourced and QC'd in V10. |
| [14](https://orbitaltoday.com/2026/05/12/a-tiny-water-droplet-became-the-star-of-artemis-ii-video/) | A Tiny Water Droplet Became the Star of Artemis II | third_party_reporting | reporting_not_analytics | Public-interest framing: 'star of Artemis II', Hansen leaning in, face upside down and warped, straw catch, light bending like a glass lens. |
| [15](https://www.yahoo.com/news/articles/watch-artemis-ii-astronauts-fun-193852742.html) | Watch the Artemis II astronauts have fun with bubbles | third_party_reporting | reporting_not_analytics | Surface tension forms the sphere; light bends and inverts images; retired astronaut Karen Nyberg's 'what you see depends on how we look' lesson; playful tone. |
| [16](https://www.dailymail.com/sciencetech/article-15807427/Incredible-video-shows-water-floating-space.html) | 'Like a crystal clear ball!' NASA water-in-space video | third_party_reporting | reporting_not_analytics | Jeremy Hansen upside-down through the orb; straw catch and release; 'uniquely human' audience reaction; NASA statement that crew had fun with water in weightlessness. |
| [17](https://www.gazetaexpress.com/en/Artemis-II-astronauts-experiment-with-a-drop-of-water-in-space--NASA-footage-amazes-the-web/) | Artemis II water drop footage amazes the network | third_party_reporting | reporting_not_analytics | Social reactions and a viewer safety question about water near electronics - useful raw material for a myth-vs-fact chapter, NOT a verdict. |
| [18](https://factcheck.afp.com/doc.afp.com.A6WV668) | Artemis II broadcast error used to stoke false 'staged' claims - AFP Fact Check | third_party_factcheck | factcheck_reporting | A broadcast text-overlay glitch was misused to claim the mission was staged; the glitch clip drew over 1.5M views. Guardrail for the 'why your brain says CGI' chapter: do not amplify or invent conspiracy claims. |
| [19](https://nautil.us/astronauts-as-influencers-1279855) | Astronauts as Influencers - Nautilus | third_party_reporting | reporting_not_analytics | Artemis II cross-platform exposure: 27.3M TV news viewers for return, 18.1M for launch, 650k splashdown stream, 22M archived video. These are broadcast/stream figures, NOT YouTube views of our clip and NOT a forecast. |
| [20](https://www.tvrev.com/news/tube-trends-how-youtube-creators-are-using-longer-videos-to-compete-with-tv) | Tube Trends: longer videos to compete with TV (Tubular Labs data) | third_party_industry_reporting | directional_unverified_by_us | Q1 2026 US creators uploaded 6.6M videos of 20+ minutes, 80.3% at least 30 min; MrBeast 628M long-form views in Q1; 44 creators above 100M views on longer content. |
| [21](https://vidiq.com/blog/post/future-youtube-trends/) | 9 YouTube Trends Creators Need to Watch in 2026 - vidIQ | third_party_creator_tool | directional_unverified_by_us | Long-form viewing on TVs, video podcasts, multi-format channels, stronger title/thumbnail testing, community revenue. |
| [22](https://falconvid.ai/blog/science-youtube-channels-that-make-money) | Faceless science channels and reusable hooks - FalconVid | third_party_aggregator | unverified_aggregator | Directional examples of curiosity-gap long-form science titles with reported million-view videos (Nebula Prophecy, GoDocs, OctoLab). Numbers NOT verified by us. |
| [23](https://tubestats.io/channels/science) | Best Science YouTube Channels 2026 - TubeStats | third_party_aggregator | unverified_aggregator | Directional channel-scale context (Kurzgesagt, Vsauce, Veritasium, NASA). Subscriber/view numbers NOT verified by us. |
| [24](https://fluxnote.io/blog/short-form-hook-library-500-viral-videos) | Short-Form Hook Library: 500 viral videos (2026 manual analysis) | third_party_analysis | unverified_sample | Pattern frequencies in a self-described manual sample: direct claim with specific number 14%, POV 11%, contradictory pattern interrupt 10%, curiosity gap 9%, listicle preamble 7%. NOT an official YouTube statistic. |
| [25](https://outlierkit.com/resources/how-to-get-youtube-api-key/) | How to Get a YouTube API Key in 2026 - OutlierKit | third_party_guide | third_party_guide_cross_checked_with_official_docs | API key is free within a 10,000-unit/day default quota; what the Data API cannot do: breakout/outlier detection vs channel baseline, arbitrary-video transcripts, keyword search volume, semantic look-alike channels, derived audience intelligence. |
| [26](workspace://production/monarch-cam/caught_on_camera_commentary_v10) | V10 workspace evidence (locked NASA Short + ledgers) | workspace_evidence | verified_workspace | Single locked 1080x1920 master (SHA 11395618...), 49.4s V10 deliverable SHA 608aa065cd3c53894b96df1ebb6fa74dd3ce1e846366e40a940426b4823586a7, 8 beats / 118 words, 9/9 audio gates, 33/33 technical checks, rights_ledger, edit_ledger, native_audio_ledger, qc_summary, category/pinned-comment pack. |
| [27](workspace://config/channels.json) | config/channels.json | workspace_evidence | verified_workspace | Legacy slots: Monarch Lab long-form 8-12 min with 'one concept, one demo' and banned 'stock b-roll as hero' / 'reaction-only' / 'clickbait with no payoff'; Curious Miles long-form 6-10 min with 'how it actually works' / 'myth vs measured'. Monarch Cam is a separate active workstream per the continuity note. |
| [28](workspace://research/caught_on_camera_commentary_v10/CAUGHT_ON_CAMERA_FORENSIC_STUDY.md) | Caught-on-camera single-clip commentary - V10 forensic study | workspace_evidence | verified_workspace | Prior evidence ladder, 10-axis one-clip rubric (min 78), 12 kill switches, honest evidence boundary, channel ecosystem tiers and long-form anatomy template. |
| [29](https://developers.google.com/youtube/v3/docs/channels/list) | Channels: list - YouTube Data API v3 | official_developer_docs | official_first_party_reference_only | Endpoint identity for public channel statistics (subscriberCount, viewCount, videoCount, snippet). Referenced for the ready-to-run query; NOT fetched this session and NOT called. |

> Citation numbers upar is study ke source-ledger IDs hain. `sources_v11.json` me har entry ke saath original `search_result_id` bhi hai, taake har web_search-derived claim apne `[id](url)` tak trace ho. Workspace claims local paths se cite hote hain, URLs se nahi.

---

## 11. Final position

**1 idea:** `REPLAY LAB Ep.1 - The Upside-Down Face: 42.7 Seconds of NASA Footage, Explained Frame by Frame`. **Score:** 93.3/100. **Basis:** official replay/retention + long-form/TV signals, ek locked NASA source, 10x forensic runway, series scalability. **Not basis:** guaranteed millions of views, live API analytics, legal clearance, human approval ya perfection. Video abhi nahi bani - ye idea-selection turn hai.

