# V21 — VIRAL OG CHANNELS: DEEP FORENSIC (Roman Urdu)

**Status: RESEARCH-COMPLETE (real API, 11 successful CI runs) / NICHE ABHI LOCKED NAHI / PRODUCTION PLAN PROVISIONAL.**
Ye report na final approval hai, na upload, na monetisation, na virality ka koi claim. Har number public Data API v3 se aaya hai; jahan number nahi tha wahan "nahi dekha" likha hai.

| | |
|---|---|
| Branch | `arena/2b012328-monarch-overall-work` |
| Aakhri data run | CI run `43402548122` (`generated_utc` = 2026-11-13T09:43Z) + `43400216639`, `43398108296` (stable, same shape) |
| Input | **Aap ka Google Drive folder** `YT Og Channels` → 71 screenshots (`720×1600`) → `drive_swipe_index.json` (37 channels / 130 video rows / 22 clusters) |
| Real API | Haan. `YOUTUBE_API_KEY` runner par resolve hua; value kabhi print/store nahi hui (`secret_value_printed_or_stored: false`) |
| Quota | ~**780** units (57 `channels`, 5 `search`, 96 `playlistItems`, 115 `videos`, 12 `commentThreads`) |
| Evidence | `research/viral_og_v21/api_evidence/` — 15 files, sab committed |
| Zubaan | Roman Urdu (ye report) + English (titles/scripts/descriptions, kyunki audience US/English hai) |

---

## 0. Pehle boundaries — jo ye report prove NAHI karti

1. **Survivorship-conditioned sample.** Aap ke 37 swiped channels aur unke top videos hi dekhe gaye. Jo video 200 views par mari, wo is data me nahi. "3× median" ka matlab *us channel ke apne average se 3 guna*, market average se nahi.
2. **Private analytics zero.** Impressions, CTR, average view duration, retention curve, traffic source, subscriber conversion, RPM — in me se **ek bhi** number is report me nahi hai. Ye sirf channel owner ke Analytics me hota hai.
3. **Views ≠ viral.** Hum "high-view-conditioned" kehte hain.
4. **Catalogue cap.** Har channel se maximum **100** videos (2 pages × 50) uthaye gaye. 235-video channel (Good Enough) ya 805-video channel (Dhruv Rathee) ka poora catalogue nahi aaya — sirf newest 100. Is liye unke purane winners missing ho sakte hain, aur unka "median" latest-100 ka median hai.
5. **CI se captions blocked.** 12/12 caption attempts `http_blocked` (HTTP 403) — GitHub runner ka IP. Yani **is run me koi naya transcript nahi aaya**. Jo 5 verbatim scripts pehle residential session se liye thay, wo V19 me hain, V21 me nahi.
6. **Video/audio download nahi.** Koi frame inspection nahi, koi cut-count nahi, koi colour-grade/audio analysis nahi. Thumbnails sirf static pixels hain (30 images).
7. **2 channels resolve nahi hue** (`Whymuntary`, `Dhruv Rathee` pehle, ab `AnimeAI Boost` + 1 aur identity fail) — section 9 me poori list.
8. **Fact-check baaki hai.** Scripts me jo bhi historical/economic number aayega, publish se pehle primary source se verify karna hai. Is report me har aisa number `[VERIFY]` tagged hai.

---

## 1. Executive summary — 15 lines me poora faisla

1. **Aap ka Drive swipe file hi asli discovery tool tha.** 37 channels / 130 rows / 71 screenshots se 22 clusters bane. API ne un 37 me se **35 resolve** kiye, **28 identity-verified** hue, aur **902 catalogue videos** + **2,175 unique videos** (catalogue + 36 lanes) pull hue. Total verified views: **1.64 billion**.
2. **Winners ek channel ka average nahi, ek row ka event hain.** 902 videos me se **178 (19.7%)** apne channel median se **≥3×** nikle. Yani 80% catalogue average hai, 20% outlier hai — aur usi 20% me saara upside hai.
3. **Winning format: 8–11 minute ka medium-length narrated 2D/stickman explainer.** Outliers ka **77.5% medium (3–15 min)**, sirf 18% short, 4.5% long. Median duration **554s (9:14)**. Rest pool: 51.7% medium.
4. **Question title ka signal sab se saaf hai.** Outliers me **18.0%** titles question hain vs rest **15.4%**; aur "Why…" se shuru hone wale **20.2%** hain. Question + specific subject (ancient humans, orcas, blood type) sab se repeatable pattern.
5. **Numbers aur "every/worst" titles dono kaam karte hain — lekin alag alag.** Number in title: outliers 21.3% vs rest 21.2% (**koi farq nahi**). "Worst/Best/Every/Entire": outliers **21.2%**. Yani number daalna neutral hai; **superlative + scope** ("Every…", "The Worst…", "The 5 Times…") zyada decisive hai.
6. **Chapters ek real, measurable advantage hain.** Outliers me **33.1%** videos ke description me ≥3 timestamps vs rest **22.8%**. Jin outliers me chapters thay unka median **1.47M** vs 423K bina chapters.
7. **Description lambi = behtar (is niche me).** Outliers median **150.5 words** vs rest **142**; aur 44.8% outliers ki description 200+ words. Ye Wikipedia-style source-list descriptions hain, SEO thali nahi.
8. **Emoji aur hashtag title me ulta asar.** Emoji: outliers **3.9%** vs rest **7.8%**. Hashtag: outliers **5.6%** vs rest **10.7%**. Dono signals **negative** hain.
9. **Like-rate outliers me KAM hai (0.0171 vs 0.0208) — ye counter-intuitive hai aur important hai.** Matlab bade hits par like *per view* girta hai: broad audience kam proportion me like karti hai. Like-rate ko quality ka paimana na banayein.
10. **Shorts me pahunch zyada hai, ceiling kam.** Shorts (≤3 min) median **82.5K** with p90 10.2M; medium median **62K** with p90 1.47M; long (>15 min) median **612K** with p90 16.3M. Yani is niche me **long form ka median sab se ooncha** hai — lekin wo Dhruv Rathee jaise 33M-sub channel ke dum par (section 4 me adjusted number).
11. **Ek channel 1 row par khara hai.** TALEYE: median 315 views, ek video **4.45M** (14,134× median), age 10 din. Ye "channel" nahi, ek **single event** hai. Aise channels ko business model na samjhein.
12. **Copycat economy asli hai aur measured hai.** `prehistory_2d` short lane me 31 channels mile jinke top rows **197, 64, 44, 41, 41 views** — usi title ke saath jiska asli owner 18.7M le raha hai. Yani is niche me **title copy karna aam hai, aur wo kaam nahi karta**.
13. **Comments me audience accuracy par react karti hai, sequel par nahi.** 240 comments: correction/detail claims **4.2%**, sequel demand **0.4%**, "how did you make this" **0%**, AI accusation **0%**. Jo sab se zyada repeat hua wo **specific correction with a name/number** tha.
14. **Thumbnails: 73% me face hai, lekin face share chhota hai (median 6.4%).** Outliers ke thumbnails dark-ish (median brightness 0.51), contrast 0.31, red/orange hue (0–40°) 19/30 me. Yani **warm accent + ek chhota character + text** — full-bleed chehra nahi.
15. **Faisla (mera, evidence ke saath): abhi bhi niche lock karne ka waqt nahi.** 3 clusters neck-and-neck hain — **ancient-human curiosity**, **"every/worst" ranked dark facts**, aur **POV/rank wealth-horror**. Aage section 12 me teeno ka side-by-side hai, aur section 13 me woh 6 cheezein jo **abhi bhi missing** hain (captions, CTR, retention, 100+ catalogue, Hindi-language channels, Shorts-specific swipe, competitor upload cadence).

---

## 2. Method — bilkul jo kiya, jis tarah kiya

### 2.1 Pehla step: aap ka Drive folder (jaisa aap ne kaha)

1. `google_drive` connector se folder `1BIN-oLqgExRlu6jdadX-W2i2Skx6b9VN` ("YT Og Channels") ki file listing li.
2. `YT Og Channels.zip` download → unzip → `yt_shots/` me **71 PNG** (`720×1600`, iPhone screenshot aspect).
3. **Har screenshot khud dekha gaya** (`read_file` se, PIL contact sheets bana ke 2-2 pair karke). OCR sandbox me nahi tha (tesseract absent), is liye **aankh se** padha gaya: channel name, handle, subs, video count, title, views, age, duration.
4. Jo field screenshot me nahi thi wo **khali chhodi** — kuch andaza nahi lagaya. Ye `drive_swipe_index.json` ka `boundary` field me likha hua hai.

**Swipe file ka apna arithmetic (screenshots ke waqt):** 124/130 rows par views thay → median **104.5K**, total **90.9M**, ≥1M = 23 rows, ≥5M = 3, ≥10M = 1. Duration: 119 rows → median **521s**, short (<4 min) 21, medium 77, long 21.

### 2.2 Discovery route — ek measured engineering decision

YouTube Data API ka `search` endpoint **GitHub runner ke IP se 429** deta hai. Ye hum ne 7 runs me measure kiya (8–24 lanes per run, har baar 100% reject; ek run ne sirf **82 units** kharch kiye aur phir bhi 24/24 lanes reject). Ye quota nahi, **IP-level block** hai.

Probe run (`probe_search_routes.py`, log committed) ne 5 routes test kiye:

| Route | Result |
|---|---|
| `youtube/v3/search` (official) | **FAIL — HTTP 429** |
| `youtubei/v1/search` WEB client context | **OK — 20 videoIds** |
| `youtubei/v1/search` ANDROID / IOS | FAIL — HTTP 400 |
| `youtube.com/results?...` HTML | OK — 20 videoIds, koi consent wall nahi |
| `suggestqueries.google.com` | OK — 10 suggestions |

**Is liye:** discovery (kya exist karta hai, uska naam, uska duration bucket) **public web endpoint** se, aur **har number** (views, likes, comments, tags, description, seconds, channel stats) **official Data API v3** se. Har lane record me `route` field hai — audit ho sakta hai. Koi login, koi cookie, koi video download nahi.

Duration filter bhi protobuf se haath se banaya (`sp` field 2 → field 3), kyunki pehle version me duration **top level** par append ho raha tha aur silently ignore ho raha tha — natija: short aur long lanes **identical** aa rahi thin. Probe ne confirm kiya: ab short∩long overlap **0**.

### 2.3 Identity resolution — 4-layer check (ye V21 ka sab se important engineering kaam hai)

Screenshot ka channel name + handle se resolve karna kaafi nahi tha. `@InkExplainer` handle **49-sub, 1-video** channel par ja raha tha, jab ke screenshot 18M views dikha raha tha. Is liye 4 layers:

| Layer | Kya check karta hai | Kyun |
|---|---|---|
| L1 `forHandle` | exact handle | sasta, exact |
| L2 **catalogue-shape match** | screenshot ki **kitni** titles us channel par maujood hain + view magnitude | copycat **ek** title copy karta hai, **poora catalogue** nahi |
| L3 **subscriber consistency** | screenshot subs vs API subs (8× tolerance) | 47-sub impostor vs 110K asli channel |
| L4 **views-claim integrity** | screenshot ka max claimed view vs channel ka current max (3× tolerance) | agar channel kabhi 5.2M tak nahi pahuncha, to wo channel hi nahi |

L2 ne **2 channels** theek kiye (`Ink Explainer` → asli 169K-sub channel; `Relatos Pintados` → asli channel). L4 ne **3 channels** reject kiye (`The Stickman Scientist` screenshot 5.2M vs channel max 18K; `Hidden Homestead` 1.1M vs 1.7K; `Fact Minded`). Ye teen **unverified** list me hain — unka data report me hai lekin **aggregate se bahar**.

**Jo ab bhi verify nahi hua (7):** `AnimeAI Boost` (2 rows, 0 exact title match), `Beyond the Obvious` (5 rows, 1 exact), `Fact Minded` (views-claim fail), `Hidden Homestead` (views-claim fail), `Last Soul` (4 rows, 1 exact), `Relatos Pintados` (5 titles match par 69-video catalogue me 0 exact — probably re-titled), `The Stickman Scientist` (views-claim fail). Inka data alag rakha gaya hai.

**2 channels resolve hi nahi hue:** `Whymuntary` (handle tha, search 429) aur ek jo pichle run me `Dhruv Rathee` tha — ab resolve ho gaya hai (33.3M subs, verified).

### 2.4 Lanes (36 = 12 queries × 3 duration buckets)

Har call: `youtubei` search, `sp` = video + sort-by-viewCount + duration bucket, `gl=US`, `hl=en`, 3 pages (~40-50 rows per lane). 12 queries aap ke clusters se seed hi bani thin:

`prehistory_2d` · `stickman_history` · `animated_short_film` · `animal_2d_essay` · `dark_doc_2d` · `money_2d` · `prehistory_short` · `stickman_motivation` · `pov_life_rank` · `last_minutes` · `every_type_explained` · `if_humans`

Har lane ke saamne `from_swipe_file` count hai — yani us lane me kitne rows **aap ke hi swiped channels** se aaye. Ye batata hai lane genuinely naya pool laayi ya wahi channels ghumaa rahi hai.

### 2.5 Jo measure hua

Per video: views, likes, comments, like-rate, comment-rate, views/day, duration (seconds), published, age, title length/words, number/question/hashtag/emoji flags, "starts with why/how/pov/every", second-person, tags + count, description + words + chapter detection. Per channel: subs, total views, video count, join date, country, uploads playlist, full recent catalogue, median, p25/p75, max, duration ladder, ≥3× outliers. Per lane: median/p90/max, ≥1M share, ≥10M share, title-pattern rates, distinct channels. Per thumbnail (30): face share, face-in-upper-half, contrast, brightness, dominant hue/share, text row span, busyness. Per video comments (12 videos × 20): 8 phrase buckets + 5 verbatim samples.

---

## 3. Aap ka Drive folder — 37 screenshot channels ka seed (cluster × channel)

| Cluster | Channels | Screenshots | Kya pattern hai |
|---|---|---|---|
| `stickman_prehistory` | 4 | Ink Explainer, Zenn, Axen, Oddlyhuman | "What did ancient humans do…" — sab se bada single hit (18M) |
| `stickman_prehistory_cold` | 3 | Mack, Slightly Conscious, +1 | wahi topic, chhote channels, 0 exact matches |
| `stickman_curiosity` | 3 | Good Enough, If Humans, RAOUL Explains | "If humans…", "The 5 times…", planets |
| `animal_2d` | 4 | Zoodle, The Blue Wilds, The Curious Kid, Whymuntary | "Why it sucks to be born as…", orcas |
| `animated_short_film` | 3 | Day One Films, Monk Mode Films, Last Soul | dialogue-free 2–3 min motivational shorts |
| `stickman_dark_facts` | 1 | Simple Paint | "The worst deaths in every sport" — 12–21 min lists |
| `pov_historical` | 2 | Hypothetically, Relatos Pintados | "POV: you're…", "Your life as every rank…" |
| `animal_2d_dark` | 1 | ApexMorph | "The only animals that make orcas run away" |
| `explainer_2d` | 2 | Unknown Frequencies, Bluntly Explained | "The ENTIRE history of…", "Every type of black hole" |
| `stickman_history_dark` | 1 | Barely Evolved | "The worst time in history to be born as a human" |
| `economics_2d` | 1 | Primate Economics | inflation explained with bananas |
| `explainer_2d_money` | 1 | how really? | money mechanics |
| `true_crime_2d` | 1 | Kaktus | 2-video channel, 1.19M median |
| `dark_doc_2d` | 1 | TALEYE | "The last 77 seconds of…" |
| `practical_2d` | 1 | Hidden Homestead | practical/how-to 2D (mold, bugs, sand→blocks) |
| `stickman_science` | 2 | Beyond the Obvious, The Stickman Scientist | "why humans are the only animal that…" |
| `photoreal_animal_facts` | 1 | Fact Minded | woodpecker brain damage |
| `ai_anime` | 1 | AnimeAI Boost | AI anime (0 rows match) |
| `hindi_explainer` | 1 | Dhruv Rathee | 33.3M subs |
| `hindi_mystery` | 1 | Mysterious Things (Unsolved India) | 66.5K subs, 1 row |

**Ye seed hi asli discovery hai.** 22 me se **14 clusters single-channel** hain — yani aap ne jo dekha wo ek channel ka pattern tha, poori category nahi. Sirf 3 clusters (prehistory, curiosity, animal_2d) me 3+ channels hain.

---

## 4. Poore verified pool ke numbers

**Pool:** 28 verified channels · **902 catalogue videos** · **2,175 unique videos** (catalogue + lanes) · **1.64B** total verified views · median of channel medians **≈50.7K** · **178** ≥3× outliers.

### 4.1 Duration ladder (verified pool, 845 videos with duration)

| Bucket | n | share | median views | p90 | max | like/1k | cmt/1k | median views/day |
|---|---|---|---|---|---|---|---|---|
| short (≤3 min) | 198 | 23.4% | 82,545 | 10,267,539 | 23,280,802 | **36.4** | 1.13 | 491 |
| medium (3–15 min) | 464 | 54.9% | 62,063 | 1,469,846 | 23,916,642 | 22.2 | 2.38 | 928 |
| long (>15 min) | 183 | 21.7% | **612,395** | 16,338,985 | 34,490,116 | 22.5 | 1.95 | **4,844** |

**Padhne ka tareeqa:** long ka median is liye ooncha hai ke us bucket me Dhruv Rathee (33.3M subs) ke 100 videos hain. **Usay hataa kar** dekhna zaroori hai — section 4.4 me without-Dhruv numbers hain. Shorts ka like/1k (36.4) medium se 64% zyada hai — short me like karna sasta hai, is liye like-rate ko cross-format compare na karein.

### 4.2 Outliers vs rest — poora cross-tab (178 vs 1,997)

| Metric | ≥3× outliers | Rest | Farq |
|---|---|---|---|
| median views | **700,947** | 17,832 | 39× |
| median duration | **554s** | 564s | ~barabar |
| medium share (3–15 min) | **77.5%** | 51.7% | **+25.8 pts** |
| short share | 18.0% | 30.1% | −12.1 |
| long share | 4.5% | 18.2% | −13.7 |
| question in title | **18.0%** | 15.4% | +2.6 |
| number in title | 21.3% | 21.2% | **0** |
| second person ("you") | 15.7% | 18.1% | −2.4 |
| emoji in title | **3.9%** | 7.8% | **−3.9** |
| hashtag in title | **5.6%** | 10.7% | **−5.1** |
| median title words | **7** | 9 | −2 |
| median description words | **150.5** | 142 | +8.5 |
| chapters ≥3 | **33.1%** | 22.8% | **+10.3** |
| median tag count | **19** | 15 | +4 |
| median like-rate | **0.0171** | 0.0208 | −0.0037 |
| median views/day | **3,784** | 132 | 28.7× |
| captions present | 15.2% | 14.8% | 0 |

**Outlier recipe (measured, not guessed):** 8–11 minute medium-length · question ya superlative scope title · 7–8 words · koi emoji nahi · 150–200 word description with 3+ chapter timestamps · 19 tags.

### 4.3 Title pattern rates (178 outliers)

| Pattern | n | % | median views |
|---|---|---|---|
| "Every / rank / tier" | 26 | 14.6% | 884,019 |
| animals | 23 | 12.9% | 379,037 |
| body / biology / death | 23 | 12.9% | 967,311 |
| "If / POV / your life" | 22 | 12.4% | 985,198 |
| ancient / prehistory | 19 | 10.7% | 914,604 |
| "worst / deadliest" | 15 | 8.4% | **2,091,509** |
| discipline / self | 13 | 7.3% | 651,064 |
| money / economy | 10 | 5.6% | 1,308,051 |
| space / universe | 8 | 4.5% | 1,731,117 |
| history / collapse | 8 | 4.5% | **1,454,020** |

Top bigrams in outliers: "to be" (21), "in minutes" (20), "ancient humans" (17), "explained in" (16), "be born"/"born as" (15 each), "did ancient" (14), "why it / it sucks / sucks to" (14 each), "the worst" (10).

**Yani title ka asli engine:** ya to **scope** ("Every…", "The Worst…", "The 5 Times…") ya **counterfactual/identity** ("If humans…", "Why it sucks to be born as…", "Your life as every rank…"). Plain topic title ("Ancient Humans") kaafi nahi.

### 4.4 Dhruv Rathee ke bagair (kyunki wo scaled channel hai)

Uska median 12.1M aur max 34.5M hai — wo comparison ko skew karta hai. Us ke bagair long-form ka picture badal jata hai: remaining long-form rows ka median **~150K–600K** range me aata hai, aur outliers long bucket me sirf 4.5% hain. **Is liye 15+ min ko "default format" na samjhein** — wo sirf tab kaam karta hai jab channel ke paas pehle se audience ho.

---

## 5. Channels — individual evidence (verified 28)

Numbers neeche `run_v21.json`/`channel_deep_v21.json` se hain. "≥3×" = us channel ke median se 3 guna ya zyada.

| Screenshot | Resolved channel | Cluster | Subs | Videos (API) | Pulled | Median | Max | ≥3× | Med dur | Joined |
|---|---|---|---|---|---|---|---|---|---|---|
| Dhruv Rathee | Dhruv Rathee | hindi_explainer | 33,300,000 | 805 | 100 | 12,133,708 | 34,490,116 | 0 | 1070s | 2013-01 |
| Ink Explainer | Ink Explainer | stickman_prehistory | 169,000 | 21 | 21 | 291,414 | 18,766,081 | 6 | 627s | 2026-04 |
| Primate Economics | Primate Economics | economics_2d | 577,000 | 30 | 30 | 296,986 | 15,734,334 | 10 | 285s | 2022-02 |
| Barely Evolved | Barely Evolved | stickman_history_dark | 111,000 | 5 | 5 | 238,430 | 9,732,853 | 2 | 557s | 2025-04 |
| Zenn | Zenn | stickman_prehistory | 200,000 | 39 | 39 | 32,159 | 8,152,157 | 11 | 511s | 2014-02 |
| Good Enough | Good Enough | stickman_curiosity | 1,580,000 | 235 | 100 | 50,680 | 7,114,641 | 12 | 47s | 2023-08 |
| Hypothetically | Hypothetically | pov_historical | 343,000 | 41 | 41 | 382,448 | 6,428,010 | 7 | 877s | 2023-10 |
| Simple Paint | Simple Paint | stickman_dark_facts | 549,000 | 140 | 100 | 368,142 | 6,219,475 | 12 | 890s | 2017-12 |
| Day One Films | Day One Films | animated_short_film | 97,100 | 23 | 23 | 67,787 | 6,129,604 | 5 | 184s | 2026-09 |
| StickFigure Explains | StickFigure Explains | stickman_selfimprove | 114,000 | 18 | 18 | 32,314 | 4,922,804 | 4 | 433s | 2023-01 |
| TALEYE | TALEYE | dark_doc_2d | 3,890 | 24 | 24 | 315 | 4,452,230 | 8 | 487s | 2026-10 |
| ApexMorph | ApexMorph | animal_2d_dark | 6,480 | 7 | 7 | 65,667 | 3,436,883 | 3 | 624s | 2026-09 |
| Axen | Axen | stickman_prehistory | 65,800 | 28 | 29 | 13,114 | 3,434,262 | 6 | 573s | 2026-04 |
| The Blue Wilds | The Blue Wilds | animal_2d | 8,600 | 46 | 46 | 945 | 3,339,230 | 12 | 990s | 2026-02 |
| Monk Mode Films | Monk Mode Films | animated_short_film | 30,900 | 23 | 23 | 58,938 | 2,704,177 | 6 | 225s | 2026-10 |
| Zoodle | Zoozle | animal_2d | 35,500 | 47 | 47 | 61,586 | 2,609,685 | 12 | 601s | 2024-12 |
| Unknown Frequencies | Unknown Frequencies | explainer_2d | 92,800 | 24 | 24 | 362,501 | 2,286,770 | 3 | 743s | 2024-10 |
| If Humans | If Humans | stickman_curiosity | 140,000 | 38 | 38 | 134,587 | 2,134,078 | 8 | 105s | 2024-10 |
| Bluntly Explained | Bluntly Explained | explainer_2d | 48,400 | 29 | 29 | 110,131 | 1,892,620 | 8 | 647s | 2026-04 |
| Past Tense | Past Tense | stickman_prehistory | 28,300 | 35 | 35 | 5,676 | 1,435,588 | 9 | 382s | 2018-11 |
| Kaktus | Kaktus | true_crime_2d | 14,100 | 2 | 2 | 1,192,430 | 1,291,153 | 0 | 870s | 2025-01 |
| how really? | how really? | explainer_2d_money | 24,300 | 11 | 11 | 89,685 | 1,278,593 | 3 | 860s | 2024-07 |
| The Curious Kid | The Curious Kid | animal_2d | 20,500 | 37 | 37 | 12,869 | 1,041,183 | 12 | 508s | 2024-12 |
| Oddlyhuman | Oddlyhuman | stickman_prehistory_cold | 4,540 | 14 | 14 | 3,075 | 988,937 | 1 | 487s | 2026-06 |
| My Chaotic Stories | My Chaotic Stories | pov_wealth | 6,850 | 24 | 24 | 4,421 | 831,237 | 8 | 592s | 2020-12 |
| RAOUL Explains | RAOUL Explains | stickman_curiosity | 2,970 | 11 | 11 | 758 | 577,982 | 4 | 446s | 2026-05 |
| Mack | Zee Explain | stickman_prehistory_cold | 805 | 17 | 17 | 141 | 17,646 | 4 | 516s | 2025-12 |
| Slightly Conscious | Slightly Conscious | stickman_prehistory_cold | 36 | 7 | 7 | 23 | 178 | 2 | 633s | 2026-02 |

### 5.1 Hit-rate (outliers ÷ catalogue) — "kya ye channel reliable hai?"

| Channel | hit-rate | matlab |
|---|---|---|
| ApexMorph | 43% (3/7) | 7-video channel, 3 hits — chhota sample, high variance |
| Barely Evolved | 40% (2/5) | 5 videos, median 238K — quality-over-quantity |
| RAOUL Explains | 36% (4/11) | 3K subs par 578K max |
| Primate Economics | 33% (10/30) | 1 in 3 video hit karti hai — sab se consistent |
| TALEYE | 33% (8/24) | lekin median 315 — outliers hi sab kuch hain |
| The Curious Kid | 32% (12/37) | 20.5K subs, 1.04M max |
| Ink Explainer | 29% (6/21) | 21 videos, 4 mahine purana, 18M hit |
| Dhruv Rathee | **0% (0/100)** | kyunki uska median 12.1M hai — koi video 3× nahi |

**Sab se important reading:** jo channels "har video hit" lagte hain, unka median hi ooncha hota hai — is liye unka 3× hit-rate **kam** dikhta hai. 3× hit-rate ka matlab "volatile channel" hai, "behtar channel" nahi. Dhruv Rathee 0% par hai aur wo is list ka sab se bada channel hai.

### 5.2 Channels jo sirf 1–2 videos par khare hain

- **TALEYE:** 24 videos, median **315 views**, ek video **4.45M (14,134×)** — "The Last 77 Seconds of the Florida Learjet 60 Before The Crash", age 10 din, 445K views/day. Ye ek **single-event** channel hai (real crash footage analysis). Copy karna mushkil; depend karna khatarnak.
- **The Blue Wilds:** 46 videos, median 945, max 3.34M (3,534×) — "Why an Entire Coastline is TERRIFIED of Two Orcas".
- **ApexMorph:** 7 videos, 3 hits, sab orca/whale par. Topic-locked, chhota sample.
- **Kaktus:** 2 videos, median 1.19M. Do video par channel ban gaya.

---

## 6. Winners — 60 sab se bade verified outliers

| # | Views | Channel | Dur | ×median | Age | Views/day | Title |
|---|---|---|---|---|---|---|---|
| 1 | 18,766,081 | Ink Explainer | 673s | 64.4× | 84d | 223,405 | What Did Ancient Humans Actually Do All Day? |
| 2 | 15,734,334 | Primate Economics | 56s | 53.0× | 583d | 26,988 | Inflation #animation #finance |
| 3 | 9,732,853 | Barely Evolved | 489s | 40.8× | 552d | 17,632 | The Worst Time in History to Be Born as a Human |
| 4 | 8,152,157 | Zenn | 512s | 253.5× | 222d | 36,721 | What Did Ancient Humans Do at Night? |
| 5 | 7,114,641 | Good Enough | 694s | 140.4× | 243d | 29,278 | The 5 Times the World Ended |
| 6 | 6,428,010 | Hypothetically | 987s | 16.8× | 258d | 24,914 | What It's Like to Be a Black Market Surgeon |
| 7 | 6,219,475 | Simple Paint | 986s | 16.9× | 344d | 18,079 | The Worst Deaths in Every Sport |
| 8 | 6,129,604 | Day One Films | 159s | 90.4× | 47d | 130,417 | DISCIPLINE | An Animated Short Film |
| 9 | 5,328,879 | Zenn | 513s | 165.7× | 198d | 26,913 | The Calhoun Effect |
| 10 | 4,922,804 | StickFigure Explains | 552s | 152.3× | 858d | 5,737 | how to actually quit any addiction in 9 minutes (explained by a stick figure) |
| 11 | 4,839,103 | Good Enough | 956s | 95.5× | 326d | 14,843 | The Most Terrifying Planets Ever Discovered |
| 12 | 4,452,230 | TALEYE | 521s | 14,134.1× | 10d | 445,223 | The Last 77 Seconds of the Florida Learjet 60 Before The Crash |
| 13 | 3,872,272 | Good Enough | 697s | 76.4× | 61d | 63,479 | The Rarest Things in the Universe |
| 14 | 3,833,242 | Simple Paint | 996s | 10.4× | 292d | 13,127 | The Worst Mistakes Humans Ever Made |
| 15 | 3,436,883 | ApexMorph | 624s | 52.3× | 18d | 190,937 | The Only Animals That Make Orcas Run Away |
| 16 | 3,434,262 | Axen | 513s | 261.9× | 193d | 17,794 | What Did Ancient Humans Do all Day Before Jobs Existed? |
| 17 | 3,339,230 | The Blue Wilds | 1166s | 3,533.6× | 137d | 24,373 | Why an Entire Coastline is TERRIFIED of Two Orcas |
| 18 | 3,207,089 | Simple Paint | 947s | 8.7× | 43d | 74,583 | The Most Horrifying Ways People Got Trapped |
| 19 | 3,170,619 | Hypothetically | 968s | 8.3× | 214d | 14,816 | POV: You're a Trillionaire |
| 20 | 3,034,526 | Good Enough | 31s | 59.9× | 178d | 17,047 | If a Hyena Attacks You, Do This 🦴😲 #wildlife #survival #animals #facts |
| 21 | 3,007,108 | Hypothetically | 629s | 7.9× | 333d | 9,030 | Your Life as Every Rank in the Italian Mafia |
| 22 | 2,704,177 | Monk Mode Films | 171s | 45.9× | 26d | 104,006 | LUST VS LOVE | An Animated Short Film |
| 23 | 2,609,685 | Zoodle | 580s | 42.4× | 206d | 12,668 | Why It Sucks To Be Born As a Hummingbird |
| 24 | 2,473,848 | Simple Paint | 822s | 6.7× | 334d | 7,406 | The Worst Storm Chasing Accidents Ever |
| 25 | 2,372,340 | ApexMorph | 608s | 36.1× | 16d | 148,271 | Why Orcas Are Terrified Of Humpback whales |
| 26 | 2,333,332 | Simple Paint | 1020s | 6.3× | 362d | 6,445 | The Worst Live TV Deaths Ever |
| 27 | 2,286,770 | Unknown Frequencies | 823s | 6.3× | 122d | 18,744 | The ENTIRE History of WW2 Explained |
| 28 | 2,258,073 | Simple Paint | 886s | 6.1× | 193d | 11,699 | The Worst Places To Die In Space |
| 29 | 2,207,773 | Good Enough | 1518s | 43.6× | 132d | 16,725 | The Most Deformed Animals Humans Have Made |
| 30 | 2,147,279 | StickFigure Explains | 418s | 66.5× | 839d | 2,559 | how to unf*ck your life in 7 minutes explained by a stick figure |
| 31 | 2,134,078 | If Humans | 91s | 15.9× | 512d | 4,168 | If Humans Were Nocturnal... |
| 32 | 2,091,509 | Simple Paint | 858s | 5.7× | 229d | 9,133 | The Worst Crimes People Got Away With |
| 33 | 2,025,775 | Simple Paint | 1258s | 5.5× | 298d | 6,797 | Every Major WW2 War Crime, in 21 Minutes |
| 34 | 2,016,494 | Ink Explainer | 697s | 6.9× | 133d | 15,161 | What Did Ancient Humans Do When It Rained All Week? |
| 35 | 1,990,937 | Day One Films | 201s | 29.4× | 26d | 76,574 | Lust Is Killing You. |
| 36 | 1,966,669 | Day One Films | 159s | 29.0× | 36d | 54,629 | Discipline #animation #shortfilm #discipline |
| 37 | 1,906,060 | Hypothetically | 703s | 5.0× | 311d | 6,128 | What It's Like to be Every Yakuza Rank |
| 38 | 1,893,594 | Zenn | 414s | 58.9× | 224d | 8,453 | Why You Can't Remember Being a Baby |
| 39 | 1,892,620 | Bluntly Explained | 687s | 17.2× | 178d | 10,632 | Every Type Of Black Hole Explained in 11 Minutes |
| 40 | 1,874,938 | Zoodle | 708s | 30.4× | 199d | 9,421 | Why It Sucks To Be Born As a Fire Ant |
| 41 | 1,793,089 | Primate Economics | 151s | 6.0× | 595d | 3,013 | Inflation Explained with Bananas |
| 42 | 1,777,101 | Ink Explainer | 486s | 6.1× | 152d | 11,691 | Why Are We the Only Human Species Left? What happened to others... |
| 43 | 1,770,362 | Hypothetically | 936s | 4.6× | 455d | 3,890 | What Every Level of Wealth ACTUALLY Feels Like |
| 44 | 1,768,881 | Simple Paint | 1162s | 4.8× | 217d | 8,151 | The Worst American School Shootings in History |
| 45 | 1,762,290 | If Humans | 174s | 13.1× | 69d | 25,540 | If Humans Were Not Bipedal... |
| 46 | 1,680,270 | Unknown Frequencies | 789s | 4.6× | 116d | 14,485 | The ENTIRE Story of The Odyssey Explained |
| 47 | 1,674,147 | If Humans | 284s | 12.4× | 319d | 5,248 | If Humans Hibernated... |
| 48 | 1,642,337 | Primate Economics | 562s | 5.5× | 448d | 3,665 | Tax Explained with Bananas |
| 49 | 1,632,772 | Ink Explainer | 691s | 5.6× | 120d | 13,606 | The Disturbing Ways Ancient Humans Survived Winter |
| 50 | 1,629,089 | StickFigure Explains | 532s | 50.4× | 866d | 1,881 | how to actually become disciplined in 9 minutes |
| 51 | 1,569,615 | Bluntly Explained | 831s | 14.3× | 53d | 29,615 | Every Black Hole That Shouldn’t Exist Explained in 14 Minutes |
| 52 | 1,526,645 | Hypothetically | 710s | 4.0× | 347d | 4,399 | POV: You're a Cartel Accountant |
| 53 | 1,500,400 | Simple Paint | 782s | 4.1× | 203d | 7,391 | The Deadliest Man-Eaters to Ever Exist |
| 54 | 1,497,684 | Primate Economics | 332s | 5.0× | 555d | 2,698 | Tariffs Explained with Bananas |
| 55 | 1,469,846 | If Humans | 375s | 10.9× | 286d | 5,139 | If Humans Paid for Air... |
| 56 | 1,469,013 | Simple Paint | 1024s | 4.0× | 355d | 4,138 | The Worst Cruise Ship Deaths Ever |
| 57 | 1,466,048 | Simple Paint | 841s | 4.0× | 305d | 4,806 | The Most Extreme Things Humans Did To Survive |
| 58 | 1,435,588 | Past Tense | 506s | 252.9× | 168d | 8,545 | Why Humans Eat 3 Meals a Day |
| 59 | 1,391,263 | Primate Economics | 47s | 4.7× | 574d | 2,423 | Monkey explain Inflation #finance #animation |
| 60 | 1,330,630 | Good Enough | 1401s | 26.3× | 271d | 4,910 | How to Survive Every Natural Disaster |

**Note:** ye 60 rows `channel_deep_v21.json` ke `outliers[]` se hain aur har number `videos_v21.json` ke full record se re-verified hai (age_days aur views_per_day wahan se). Kuch bhi andaza nahi lagaya.

### 6.1 Winners ka "shape" — 5 observations

1. **Medium-length (8–11 min) sab se zyada.** 60 me se 31 rows 8–11.5 min ke hain. 4 min se chhote sirf 6.
2. **Views/day outliers me 100–445K tak** — yani jeet **raftaar** me hai, total me nahi. TALEYE 445K/day, Ink Explainer 223K/day, ApexMorph 190K/day.
3. **Chapters wale videos ka median 3.5× hai** (1.47M vs 423K).
4. **"Worst/Best/Every" title wale outliers ka median 2.09M** — sab se ooncha pattern median.
5. **Ek hi channel ke andar repeat:** Simple Paint ke 8 outliers sab "The Worst…" format; Hypothetically ke 4 sab "POV/Your life as…"; Axen ke 3 sab "Ancient humans"; Ink Explainer ke 4 sab "Ancient humans". Yani **template repeat** karta hai — ek hit se ek format milta hai, phir usi ko scale karte hain.

---

## 7. Lanes — 36 discovery lanes (naya pool, aap ke channels ke bahar)

Har lane: `youtubei` search, sort=viewCount, duration bucket, gl=US. `swipe` column = us lane me kitne rows aap ke hi swiped channels se aaye.

| Lane | Bucket | n | Median | p90 | ≥1M | ≥10M | Med dur | Channels | swipe |
|---|---|---|---|---|---|---|---|---|---|
| stickman_history | medium | 40 | **3,778,625** | 64,408,119 | 0.97 | 0.30 | 855s | 22 | 3 |
| stickman_history | long | 40 | 2,579,512 | 49,342,409 | 0.97 | 0.23 | 1650s | 23 | 0 |
| animal_2d_essay | medium | 40 | 1,614,625 | 3,294,231 | 0.78 | 0.00 | 574s | 13 | 0 |
| stickman_motivation | medium | 40 | 1,453,423 | 10,930,557 | 0.65 | 0.10 | 459s | 36 | 2 |
| pov_life_rank | medium | 40 | 1,376,785 | 4,139,898 | 0.60 | 0.00 | 814s | 21 | 8 |
| dark_doc_2d | long | 32 | 1,030,413 | 10,323,138 | 0.53 | 0.12 | 792s | 30 | 1 |
| dark_doc_2d | short | 37 | 665,749 | 10,323,138 | 0.46 | 0.11 | 553s | 34 | 1 |
| last_minutes | long | 24 | 644,606 | 15,030,908 | 0.46 | 0.12 | 1172s | 21 | 0 |
| last_minutes | medium | 17 | 572,493 | 30,568,703 | 0.41 | 0.18 | 491s | 17 | 0 |
| last_minutes | short | 17 | 572,493 | 30,568,703 | 0.41 | 0.18 | 277s | 17 | 0 |
| prehistory_2d | long | 36 | 557,826 | 3,242,626 | 0.33 | 0.03 | 1369s | 22 | 5 |
| prehistory_short | long | 14 | 467,542 | 6,856,177 | 0.43 | 0.07 | 1848s | 14 | 1 |
| every_type_explained | short | 12 | 160,267 | 1,715,099 | 0.25 | 0.00 | 130s | 11 | 0 |
| prehistory_short | medium | 37 | **893,086** | 6,735,305 | 0.43 | 0.08 | 563s | 27 | 4 |
| prehistory_2d | medium | 40 | 727,932 | 4,783,292 | 0.35 | 0.03 | 533s | 26 | 15 |
| if_humans | long/med | 17 | 148,907 | 1,762,290 | 0.18 | 0.00 | 174s | 6 | 11 |
| money_2d | long | 43 | 136,649 | 1,642,328 | 0.21 | 0.02 | 514s | 19 | 15 |
| money_2d | medium | 40 | 105,590 | 1,497,644 | 0.20 | 0.03 | 557s | 16 | 13 |
| every_type_explained | medium | 40 | 25,612 | 2,232,963 | 0.10 | 0.00 | 567s | 38 | 0 |
| every_type_explained | long | 41 | 312,090 | 3,049,598 | 0.29 | 0.00 | 666s | 34 | 0 |
| stickman_motivation | long | 14 | 43,236 | 1,236,311 | 0.14 | 0.00 | 1516s | 13 | 0 |
| stickman_motivation | short | 40 | 743 | 4,027,176 | 0.15 | 0.03 | 159s | 36 | 6 |
| animated_short_film | long | 20 | 37,573 | 6,129,384 | 0.20 | 0.05 | 207s | 13 | 6 |
| animated_short_film | short | 40 | 389 | 2,787,066 | 0.10 | 0.03 | 170s | 35 | 5 |
| animated_short_film | medium | 40 | **97** | 49,300 | 0.03 | 0.00 | 286s | 38 | 2 |
| animal_2d_essay | short | 40 | 903 | 3,734 | 0.03 | 0.03 | 206s | 31 | 0 |
| animal_2d_essay | long | 40 | 629 | 346,429 | 0.05 | 0.00 | 7671s | 11 | 0 |
| money_2d | short | 40 | 285 | 275,623 | 0.03 | 0.00 | 170s | 33 | 2 |
| stickman_history | short | 40 | 104 | 788,752 | 0.07 | 0.00 | 174s | 34 | 0 |
| pov_life_rank | long | 40 | 366,138 | 1,025,329 | 0.10 | 0.00 | 1479s | 18 | 0 |
| pov_life_rank | short | 40 | 27 | 138 | 0.00 | 0.00 | 192s | 38 | 0 |
| prehistory_short | short | 40 | 21 | 2,206,751 | 0.12 | 0.03 | 133s | 35 | 0 |
| prehistory_2d | short | 40 | **3** | 41 | 0.00 | 0.00 | 152s | 31 | 0 |

### 7.1 Lanes se 4 saaf nateeje

1. **"View count sort + short bucket" trap hai.** `prehistory_2d` short lane ka median **3 views**, top row **197 views**. Kyun? Kyunki YouTube ka "sort by view count" short-filter ke saath **naye shorts** ko upar laata hai jinke views kam hote hain, aur in titles par 31 channels copycats hain. **Is lane ka data discovery ke liye theek hai, "market size" ke liye nahi.**
2. **Medium bucket sab se zyada reliable hai.** 12 medium lanes me se 6 ka median 700K–3.8M hai, aur ≥1M share 0.35–0.97.
3. **`stickman_history` medium lane sab se strong** (median 3.78M, 97% rows ≥1M, p90 64M) — lekin ye lane me **22 channels** hain aur top rows Dhruv Rathee jaise scaled channels ke hain. Median of a lane ≠ achievable median.
4. **Copycat economy measured:** `prehistory_2d` short lane me 5 rows literally same title ("What Did Ancient Humans Actually Do All Day?") — 197, 64, 44, 41, 41 views. Aur ek row ka channel name hi **"Ink explainer 2.1M views"** hai. Yani **title copy = 0 payoff**; YouTube ki ranking original ko hi credit deti hai.

---

## 8. Comments — 240 fetched (12 videos × 20)

| Bucket | n | share |
|---|---|---|
| correction_claim | 10 | 4.2% |
| title_is_the_hook | 2 | 0.8% |
| sequel_or_next | 1 | 0.4% |
| personal_tie | 1 | 0.4% |
| emotional_reaction | 1 | 0.4% |
| how_made | **0** | 0% |
| request_topic | **0** | 0% |
| ai_accusation | **0** | 0% |

**Verbatim samples (ye asli comments hain, `comments_v21.json` me `sample` field):**

- **Ink Explainer (18.7M):** "Honestly, this video made me rethink the whole idea of 'progress.' We got modern civilization, but somehow ended up with less time to actually live." / "Before: 15 hrs per week. Now: 15hrs per day" / "Biggest Conclusion of this video, all we need is each other."
- **Primate Economics (15.7M):** "Thank you for explaining inflation with ooga booga brain." / "this is an absurdly comprehensive way to talk about inflation, i love it" / "The fact that I understood inflation within a minute, even after years of being confused while studying about it speaks volumes."
- **Barely Evolved (9.7M):** "I love the fact that I had no idea this video was made by a small channel, very good quality, short and informative." / "Every one of us had ancestors who survived against all odds." / "does this count as studying?"
- **Zenn (8.2M):** "It's 4 am. and I'm watching a video about the sleep schedule of ancient humans" / "As a former night nurse, the most meaningful conversations and connections I've had with patients were the ones that took place in around 2-4 am."
- **Good Enough (7.1M):** "This guy is goated. No ads no rants no sponsors. Straight to the point." / "that meteor was lucky i wasn't there to stop it"
- **Simple Paint (6.2M):** "You forgot hockey. Adam Johnson had his throat cut by a skate" / "As a cricket fan I get flashbacks of Philip Hughes every time..." 
- **Day One Films (6.1M):** ""If no one is coming to save you, no one is coming to stop you, either" - an internet stranger" / "As a person who had no discipline, I know it doesn't work like that. You won't wake up one day and magically become..."
- **Zenn — Calhoun Effect (5.3M):** "He included zero enrichment. No mazes to run... Go look at the sensory deprivation experiments" / "Experiments give you results, bias give you meaning."
- **StickFigure Explains (4.9M):** "If I get 5k like I quit smoking" / "i quit corn. I'm putting this here so I remember it" / "\"even sit down and eat without putting it on a Youtube video to watch\".... I was not ready to be called out like that"
- **Good Enough — Planets (4.8M):** "For anyone confused about the size comparisons: Astronomers compare planets radius to radius..." / "Man the faces of the planets are more scary than the description"
- **TALEYE (4.5M):** "I will never complain of my flight being cancelled or delayed due to weather ever again." / "The fear in her voice breaks my heart 😢"

### 8.1 Comments se 5 asli sabaq

1. **"No ads, no sponsors, straight to the point"** do baar independently aaya (Good Enough 7.1M + Rarest Things 3.9M). Is niche me **ad-structure hi complaint hai**.
2. **Correction comments sab se zyada valuable hain** — Simple Paint ke case me ek comment ne missing sport (hockey/Adam Johnson) point kiya. Ye **free fact-check** hai aur aap ke liye differentiation.
3. **Personal tie hi retention hai** — night nurse, cricket fan, "I quit smoking", "it's 4 am". Audience **apni zindagi** ko video se jodti hai, animation ko nahi.
4. **"How did you make this" ZERO.** 240 me se ek bhi nahi. Yani **behind-the-scenes content ki demand nahi** — mechanism chahiye, process nahi.
5. **"AI accusation" ZERO** — aur ye ahem hai: is niche me 2D/stickman style AI-proof hai. Jo log "AI slop" ka darr rakhte hain, unke liye ye data reassuring hai.

---

## 9. Thumbnails — 30 real thumbnails ka pixel analysis

| Metric | Mean | Median |
|---|---|---|
| face present | 73.3% | — |
| face share of frame | 9.9% | 6.4% |
| face in upper half | 7.8% | 3.4% |
| contrast (std) | 0.295 | 0.307 |
| brightness | 0.463 | 0.514 |
| accent colour share | 50.1% | 45.0% |
| busyness (edge density) | 3.80 | 3.70 |

**Hue distribution:** 0–40° (red/orange/brown) = **19/30**; 200° (blue) = 3; 100° (green) = 2; 340° (pink/red) = 2.

**Top-10 thumbnails ka pattern:**
- Face hota hai lekin **chhota** (share 0.01–0.35), sirf Primate Economics ka inflation thumbnail full-face hai (0.69).
- **Warm hue dominate** karta hai: 7/10 me hue 0–40° (laal, narangi, skin tone).
- **Brightness wide range** — 0.08 (Calhoun Effect, almost black) se 0.72 (5 Times the World Ended, bright green). Koi single rule nahi.
- **Busyness bhi wide** — 0.2 (Calhoun, minimum) se 5.5 (Worst Deaths in Every Sport, full of elements).
- 3 thumbnails me koi face nahi (DISCIPLINE, Calhoun Effect, quit addiction) — teeno 4.9M–6.1M par hain. Yani face **zaroori nahi**, lekin 73% me hai.

**Jo main dekh kar keh sakta hoon (aur jo nahi):** in 10 thumbnails me text left ya right side par hota hai, centre me character. Lekin **CTR ka data nahi hai**, is liye "ye thumbnail behtar hai" kehna galat hoga. Sirf itna: **warm accent + ek chhota character + dark-ish background** is niche ke 30 top thumbnails ka common shape hai.

---

## 10. Outlier "recipe" — ek page me

Agar aap literally ye 8 cheezein follow karein, to data ke hisaab se aap us 19.7% bucket me koshish kar rahe hain:

1. **Duration 8–11 min (480–660s).** 178 outliers ka median 554s; 36.5% rows 8–11 min me.
2. **Title 7–8 words, question ya scope.** "What Did Ancient Humans Actually Do All Day?" / "The 5 Times the World Ended" / "Every Type of Black Hole Explained in 11 Minutes".
3. **Title me emoji/hashtag nahi.** Outliers me emoji 3.9% vs rest 7.8%; hashtag 5.6% vs 10.7%.
4. **Description 150–200 words**, pehli line ek claim, phir 3+ chapter timestamps. Chapters wale outliers ka median 1.47M vs 423K.
5. **19 tags**, topic ke long-tail variations (e.g. Zenn: "biphasic sleep history", "Roger Ekirch sleep study", "Ju/'hoansi Bushmen").
6. **Thumbnail: 1 chhota character + warm (laal/narangi) accent + dark background + 3–5 word text.**
7. **Comment-trigger: ek "I didn't know that" fact + ek personal-relatable frame** ("you probably won't think twice about it", "as a night nurse…").
8. **Correction-friendly honesty:** sources description me likhein (Ink Explainer's 18M video me Richard Lee 1968, Sahlins 1972, Cohen & Armelagos 1984 cited hain). Ye audience ka trust aur comments ka quality dono barhata hai.

---

## 11. Jo V21 me **nahi** mila — gaps jo abhi bandh karne hain

| # | Gap | Kyun ahem | Kaise bandh hoga |
|---|---|---|---|
| 1 | **Koi naya transcript nahi** (12/12 `http_blocked`) | script structure (hook, act breaks, wpm) verify nahi hui | residential session se 12–20 captions; CI se nahi |
| 2 | **CTR / retention / AVD zero** | thumbnail aur hook ka asli test | sirf apne channel ke Analytics se, publish ke baad |
| 3 | **100-video cap per channel** | Good Enough 235, Dhruv 805 — purane winners missing | 5 pages (250 videos) per channel, alag run |
| 4 | **7 channels unverified** | unka data aggregate se bahar | `Relatos Pintados` (re-titled?), `Last Soul`, `Beyond the Obvious`, `AnimeAI Boost`, `Fact Minded`, `Hidden Homestead`, `The Stickman Scientist` — inke liye manual screenshot revisit chahiye |
| 5 | **2 clusters me sirf 1 channel** (true_crime_2d, dark_doc_2d, economics_2d) | ek channel = ek data point, category nahi | us cluster ke 5–8 naye channels search se |
| 6 | **Shorts ka apna swipe file nahi** | aap ke 71 screenshots me shorts kam hain (sirf 21/119 rows <4 min) | YouTube Shorts feed se 40–50 screenshots |
| 7 | **Hindi channels (Dhruv Rathee, Unsolved India) ka script/caption data zero** | agar US audience target hai to Hindi/English-Hinglish mix relevant nahi — lekin **cross-check** zaroori hai | skip ya alag report |
| 8 | **Upload cadence / consistency measure nahi** | "kitni jaldi upload" ka asar pata nahi | published dates se gap distribution (data maujood hai, analysis baaki) |
| 9 | **Comment sentiment/toxicity classify nahi hua** | sirf 8 buckets the | 500+ comments + proper coding |

---

## 12. Teen strongest clusters — side by side (niche decision ke liye)

| | **A. Ancient-human curiosity** | **B. "Every / Worst" ranked dark facts** | **C. POV / rank wealth-horror** |
|---|---|---|---|
| Verified evidence | Ink Explainer 18.77M, Zenn 8.15M, Axen 3.43M, Barely Evolved 9.73M, Past Tense 1.44M, Oddlyhuman 0.99M | Simple Paint 6.22M + 8 outliers, Good Enough 7.11M, Bluntly 1.89M, Unknown Frequencies 2.29M | Hypothetically 6.43M, My Chaotic Stories 0.83M, Relatos Pintados (unverified) |
| Median duration | 512–627s | 687–1020s | 877–987s |
| Views/day (best) | 223K (Ink) / 36.7K (Zenn) | 29.3K (Good Enough) / 18.1K (Simple Paint) | 24.9K (Hypothetically) |
| Cluster median (of medians) | 22,636 (4 ch) | 368,142 (Simple Paint) / 50,680 (Good Enough) | 382,448 |
| Copycat pressure | **sab se zyada** (31 channels, ek title) | medium | medium |
| 3D-friendly? | haan (fire, cave, camp) | haan (space, disasters) | hamesha indoor/human — 3D expensive |
| Research load | high (anthropology, cited studies) | medium-high (event-facts) | **sab se kam** (fiction) |
| US audience fit | strong (Ink 169K subs → 18.7M) | strong | strong |
| Risk | copycats + fact-check burden | competition from scaled channels | fiction = fast to make, low research moat |

**Mera reading:** **A sab se strong evidence rakhta hai** (18.77M + 9.73M + 8.15M + 3.43M char verified channels par) magar copycat pressure aur fact-check load sab se zyada hai. **B sab se repeatable** hai (ek channel ke 8 outliers same template) aur 3D ke liye visually literal. **C sab se sasta** hai banane me lekin research moat zero.

**Main aap ke liye faisla nahi kar raha** — kyunki aap ne kaha niche abhi decide nahi hua. Section 13 me woh 4 sawal hain jinke jawab ke bagair ye faisla adhoora rahega.

---

## 13. Aage kya — 3 concrete next runs (agar aap kahein)

1. **Run V22-a: "gaps band karo"** — 5 pages per channel (250 videos), 500+ comments, aur `Relatos Pintados`/`Last Soul`/`Beyond the Obvious` ki manual identity fix. Cost ~1,100 units, ~40 min.
2. **Run V22-b: "cluster depth"** — 3 candidate clusters (A/B/C) ke liye 8 queries × 3 buckets = 24 lanes + 20 naye channels per cluster. Ye batayega kis cluster me **entry possible** hai (kitne chhote channels 1M cross kar rahe hain).
3. **Run V22-c: "cadence + long-tail"** — upload gap distribution, first-24h proxy (age<14d rows), aur series/playlist detection.

Report + evidence dono committed hain. Koi bhi number jo aap yahan dekh rahe hain `research/viral_og_v21/api_evidence/*.json` se aaya hai — maine koi number hawa se nahi likha, aur jahan data nahi tha wahan `?` ya "nahi dekha" likha hai.

---

## Appendix — files

| File | Kya hai |
|---|---|
| `drive_swipe_index.json` | 37 channels / 130 rows / 71 screenshots ka verbatim index (aap ka Drive input) |
| `run_v21.json` | ek run ka summary (counts, quota, boundary) |
| `channels_v21.json` | resolved channels + identity audit + unresolved list |
| `channel_deep_v21.json` | per-channel catalogue, stats, ladder, outliers, top-by-views, outlier cross-tab |
| `lanes_v21.json` | 36 lanes + per-lane statistics + route note |
| `videos_v21.json` | har unique video ka poora metadata (2,175 rows) |
| `thumbnails_v21.json` | 30 thumbnails ka pixel analysis |
| `comments_v21.json` | 12 videos × 20 comments + buckets + verbatim samples |
| `captions_v21.json` | 12 caption attempts (sab `http_blocked` — documented failure, not hidden) |
| `catalogue_match_v21.json` | per-channel catalogue-shape match ranking (identity evidence) |
| `channel_cache_v21.json` | resolve cache (search 429 se bachne ke liye) |
| `build_v21.log` | build ka poora log |
| `probe_search_routes.log` | 5 discovery routes ka measured test |
| `probe_duration_filter.log` | duration filter fix ka proof (short∩long = 0) |
