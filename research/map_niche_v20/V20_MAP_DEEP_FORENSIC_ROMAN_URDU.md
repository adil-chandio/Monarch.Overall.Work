# MAP / GEOGRAPHY — V20 DEEP FORENSIC REPORT (Roman Urdu)

**Status: RESEARCH-COMPLETE / NICHE-LOCKED / PRODUCTION-PLAN PROVISIONAL. Ye report na final approval hai, na upload, na monetisation, na virality ka koi claim.**

Ye report sirf **ek niche** par hai: **map / geography, English, US-first audience**. V18.1 me Map aur Visual Proof Lab **4.20 / 4.20** par tie the; aap ne kaha niche abhi decide nahi hua. Is liye V20 me maine general sampling band kar ke **poora budget isi niche** par kharch kiya — taake aap ke paas tie todne ke liye asli, taza numbers hon.

| | |
|---|---|
| Branch | `arena/2b012328-monarch-overall-work` |
| Run | `43295569449` (V20 map niche, 12 lanes + 25 catalogues + comments) |
| Real API | Haan. `YOUTUBE_API_KEY` runner par resolve hua, value kabhi print/store nahi hui (`secret_value_printed_or_stored: false`) |
| Quota | ~**1,345** units (12 search + 60 videos + 25 channels + 49 playlistItems + 11 commentThreads) |
| Evidence folder | `research/map_niche_v20/api_evidence/` (10 JSON files, sab committed) |
| Machine-readable plan | `EPISODE_01_PLAN_V20.json` (isi folder me) |
| Zubaan | Roman Urdu (ye report) + English (saare scripts, titles, descriptions — kyunki audience US/English hai) |

---

## 0. Pehle boundaries — kya prove nahi hota

1. **Ye "top 50 by view count" lanes hain.** Yani har lane me wahi videos aayi jo pehle se bahut zyada views le chuki hain. Ye **expected performance** nahi, **survivorship-conditioned** sample hai. Jo video 200 views par mari, wo is data me nahi.
2. **Private analytics hamare paas nahi**: impressions, CTR, average view duration, retention curve, traffic source, subscriber conversions, RPM — inme se **ek bhi** number is report me nahi hai, kyunki ye sirf channel owner ke Analytics me hota hai.
3. **Views se "viral" prove nahi hota.** Hum "high-view-conditioned" kehte hain, "viral" nahi.
4. **Competitor ke asli cuts/sec, transitions, colour grade, music, SFX, motion-graphics style observe nahi kiye gaye.** Main video/audio download nahi karta. Thumbnails static pixels hain; video frames nahi.
5. **Transcripts**: CI runner ka IP renderer se 403 block hai (12/12 attempts `blocked_or_error`). 5 transcripts **residential browser session** se public caption page par capture kiye — wo verbatim hain, source ke saath store hain, lekin **poori 520-video corpus ki script coverage nahi** hain. Sirf 5.
6. **Fact-check ka zimma abhi baaki hai.** Jo bhi historical/geographic number scripts me aaya, wo **public captions se liya gaya reference** hai — publish se pehle treaty text / IBC / USGS / Natural Earth se verify karna zaroori hai. Report me har aisa number `[VERIFY]` tag ke saath hai.
7. **Monetisation, legal clearance, human approval, guaranteed views** — inme se kisi ka bhi claim nahi.

---

## 1. Executive summary — 12 lines me poora faisla

1. Niche me **520 unique videos** mile (12 lanes, 273 channels), in me se **334 (64.2%) ≥1M**, **54 (10.4%) ≥10M**, **1 ≥100M**. Yani is niche ke top-of-search me million views **exception nahi, norm** hain — lekin ye selection bias hai, isay base-rate na samjhein.
2. **25 channels** ki poori catalogue khenchi: **2,377 videos**. In me se sirf **20** videos apne channel median se **≥3x** nikle — yani is niche me bhi "winner" **1% ke qareeb** phenomenon hai, poore channel ka average nahi.
3. **Winners ki median 12.61M** views vs baaki **2.08M**; views-per-day **12,311 vs 1,546** (8x). Yani jeet sirf total me nahi, **raftaar** me bhi hai.
4. **Duration**: winners me **70% short** (median 85s), baaki corpus me 33.8%. Is niche ka jeetne wala format **60–100 second ka map explainer** hai; long form jeetta hai lekin **kam frequency** par (20%).
5. **Numbers in title**: winners **60%** vs baaki **36.4%**. Is niche me "specific number" (5,525 miles / 85 metres / 20 feet / 27 years) title ka sab se repeatable pattern hai.
6. **Description**: winners ka median **83 words**, baaki ka **152 words** — yani jeetne wale **chhoti description** likhte hain, lambi SEO-thali nahi.
7. **Captions**: winners me **0%** caption flag, baaki me **20.8%**. Captions na hona jeet ka sabab nahi — lekin "captions zaroori hain" wali advice is niche ke data se **support nahi hoti**.
8. **Script structure** (5 verbatim transcripts): teen me **contradiction hook** hai ("map kuch kehta hai, asliyat kuch aur"), do me **self-correction hook**. Pacing 185–219 wpm short me, 67 wpm CGP Grey ke 282s video me — yani **wpm format ka nateeja hai, quality ka paimana nahi**.
9. **Place names hi demand hain**: autocomplete me "map borders explained" par **zero** suggestions aayi, lekin "point roberts" par **10** (map, population, usa), "weird borders" par **10** (including "weird borders canada us", "weird borders in the us"). Log abstract topic nahi, **thikana** search karte hain.
10. **Comments (220 fetched)**: sab se zyada repeat hone wali cheez **map-nerd corrections/details (10)** aur **"actually…" corrections (8)** hain; "part 2" ka demand **0**. Yani is niche me audience **accuracy** par react karti hai, sequel par nahi — is liye accuracy hamara differentiator hai, na ke cliffhanger.
11. **Music/sound nahi, mechanism chahiye**: 220 comments me "how did you animate" **0**, "which software" **0** — audience ko *kaise banaya* se matlab nahi, *kya sach hai* se hai.
12. **Decision**: is niche ka sab se strong, US-audience-safe, 3D-friendly subject **US–Canada border** hai — kyunki (a) demand signal US locale me live hai, (b) teen mukhtalif channels par 18M–37.5M views ka verified public proof hai, (c) 3D map animation ke liye iska structure (line, monuments, enclaves, lake) **visually literal** hai. Is liye Episode 01 isi par bana hai — magar **final niche approval aap ka faisla hai**, main sirf evidence + plan de raha hoon.

---

## 2. Method — jo kiya, jis tarah kiya

### 2.1 Lanes (12)

4 sub-themes × 3 duration buckets. Har call: `search` with `order=viewCount`, `regionCode=US`, `relevanceLanguage=en`, `safeSearch=moderate`, `maxResults=50`.

| # | Lane | Query | Bucket | Rows |
|---|---|---|---|---|
| 1 | `geo_explainer_short_all` | geography explained animation | short | 50 |
| 2 | `geo_explainer_medium_all` | geography explained animation | medium | 50 |
| 3 | `geo_explainer_long_all` | geography explained animation | long | 50 |
| 4 | `map_animation_short_all` | map animation country facts | short | 50 |
| 5 | `map_animation_medium_all` | map animation country facts | medium | 50 |
| 6 | `map_animation_long_all` | map animation country facts | long | **10** |
| 7 | `borders_geo_short_all` | why borders look like this map | short | 50 |
| 8 | `borders_geo_medium_all` | why borders look like this map | medium | 50 |
| 9 | `borders_geo_long_all` | why borders look like this map | long | **32** |
| 10 | `history_map_short_all` | history map animation explained | short | 50 |
| 11 | `history_map_medium_all` | history map animation explained | medium | 50 |
| 12 | `history_map_long_all` | history map animation explained | long | 50 |

**Note (honesty):** lane 6 sirf 10 aur lane 9 sirf 32 rows de payi — YouTube ke paas un exact queries × long-duration combination me itne results nahi the. Ye data ki kami hai, code ki galti nahi; report me isay waise hi dikhaya gaya hai.

### 2.2 Phir kya hua

1. 542 row-slots → **520 unique videos** (dedupe) → har video ka `snippet, statistics, contentDetails, status` (ek `videos` call per 50 ids).
2. In 520 videos ke **273 channels** me se top 25 (total views ke hisaab se) chune → har channel ka `channels` call + **2 pages** uploads playlist (100 tak) + un videos ke full stats = **2,377 videos**.
3. Har channel ka median, **≥3x outlier** (har channel ke top 12 tak listed = 238 rows), aur short/medium/long ladder.
4. **20 thumbnails** (maxres) par pixel-level static analysis.
5. **12 comment threads** (relevance, max 20 each) — 11 successful, **220 comments**.
6. **12 caption attempts** (CI se) — sab blocked; **5 transcripts** residential browser se capture hue aur verbatim store hue.

### 2.3 Bucket definitions (poori report me yahi)

- **short** < 240s (4 min)
- **medium** 240–1200s (4–20 min)
- **long** > 1200s (20 min+)

`chapter_count` = description me time-like lines ka regex count (`M:SS` / `H:MM:SS`). Ye **exact chapter structure ka proof nahi** — description me likha koi timestamp bhi pakda ja sakta hai. Is liye report me "chapters" ko **proxy** kaha gaya hai.

---

## 3. Lane-level results — kahan paisa hai

| Lane | n | Median views | Total views | Median duration | Number in title | Question | Emoji | Hashtag | Median desc words | Chapters ≥3 | Median tags | Median like-rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| geo_explainer **short** | 50 | **4,506,384** | 418.8M | 63s | 32% | 18% | 18% | 32% | 94 | 2% | 21 | 2.27% |
| geo_explainer **medium** | 50 | 2,433,246 | 463.7M | 506s | 40% | 10% | 4% | 2% | 192 | 20% | 19 | 1.42% |
| geo_explainer **long** | 50 | 2,293,619 | 150.4M | 4540s | 66% | 0% | 2% | 2% | 235 | 32% | 18 | 2.00% |
| map_animation **short** | 50 | 2,802,780 | 266.2M | 50s | 20% | 12% | **26%** | **60%** | 37 | 0% | 8 | 1.67% |
| map_animation **medium** | 50 | **52,494** | 11.0M | 537s | 28% | 20% | 10% | 10% | 224 | 32% | 18 | 1.73% |
| map_animation **long** | 10 | **11,366** | 1.7M | 1633s | 40% | 0% | 20% | 0% | 196 | 40% | 11 | 0.33% |
| borders_geo **short** | 50 | 122,373 | 151.3M | 60s | 14% | **36%** | 32% | 38% | 92 | 2% | 8 | 1.51% |
| borders_geo **medium** | 50 | 10,969 | 75.2M | 650s | 30% | 32% | 4% | 4% | 187 | **34%** | 17 | 1.68% |
| borders_geo **long** | 32 | 61,317 | 33.0M | 1964s | 59% | 12% | 0% | 0% | 184 | 34% | 21 | 1.82% |
| history_map **short** | 50 | **6,011,775** | 395.9M | 59s | 16% | 18% | 22% | 38% | 61 | 0% | 8 | **2.62%** |
| history_map **medium** | 50 | 3,895,919 | 426.0M | 529s | 42% | 2% | 2% | 2% | 95 | 14% | 11 | 1.42% |
| history_map **long** | 50 | 3,332,559 | 280.5M | 2182s | 50% | 0% | 0% | 0% | 277 | **42%** | 17 | 2.14% |

### 3.1 Lane insights (jo numbers ke andar se nikle)

- **"map animation" wali query medium/long me dead hai** (median 52,494 / 11,366). Iski wajah data me dikh rahi hai: us query par jo results aaye wo **UPSC/competitive-exam Indian coaching** content aur **"map animation kaise banaye" tutorials** hain — yani query ka intent **tool/tutorial/exam** hai, **story** nahi. Hum aisi query par nahi jaate.
- **"why borders look like this map" ka short bucket** median sirf **122,373** hai lekin **median question-rate 36%** — yahi wo lane hai jahan sawal-pattern common hai magar views kam. Iska matlab: sawal likhna kaafi nahi, **kaunsa sawal** maayne rakhta hai.
- **history_map short** ka median **6.01M** aur like-rate **2.62%** — sab se zyada. Yani "history + map" ke 60-second visual me audience **emotionally** engage hoti hai (like-rate se pata chalta hai, magar like-rate ko engagement ka complete paimana na samjhein).
- **Chapters** ka rate long me 32–42%, short me 0–2% — yani format ke saath chapters aate hain, videos ko chapters "banane" se views nahi aate.
- **Hashtags**: map_animation short me 60%, baaki lanes me 0–38%. Hashtags ka istemal **format-specific habit** hai, ranking lever nahi.

---

## 4. Corpus anatomy — 520 videos

| Measure | Value |
|---|---|
| Unique videos | 520 |
| ≥1M views | **334 (64.2%)** |
| ≥10M views | **54 (10.4%)** |
| ≥100M views | **1 (0.19%)** — Alan Becker, `Animation vs. Math`, 163.65M, 843s |
| Channels represented | 273 |
| Median duration | 552s (poora corpus) |

**Language tags (`defaultAudioLanguage`)** — 520 videos:

`en 176` · `unset 145` · `hi 83` · `en-US 52` · `en-GB 36` · `en-IN 7` · `zxx 7` (music/no speech) · `es 4` · `en-AU 3` · `ur 2` · `en-CA 1` · `hi-Latn 1` · `fr 1` · `ml 1` · `te 1`

**≥5M wali 127 videos me:** `unset 42` · `en 42` · **`hi 21` (16.5%)** · `en-US 11` · `en-GB 5` · `en-IN 2` · `en-AU 2` · `zxx 2`.

Iska seedha matlab: Hindi map/geography content is niche ke top me **asli competitor** hai (Professor Of How 16.2M subs, Sunlike study, StudyIQ, Geo Study). Lekin **US-first English audience** ke liye ye competition relevant nahi — ye ek **alag market** hai jo same search queries me ghus aata hai. Hum English me US audience ke liye banate hain, is liye Hindi channels ko benchmark (format) ke tor par dekha, **target** ke tor par nahi.

**Ek aur honesty note:** 145 videos (27.9%) ka language tag **set hi nahi** hai. Yani "English content ka share" ko exact number ke tor par nahi likha ja sakta — sirf tag-based floor diya ja sakta hai.

---

## 5. Top 25 winners (poore niche corpus se, views ke hisaab se)

| # | Views | Dur | Published | Channel | Title |
|---|---|---|---|---|---|
| 1 | 163,650,508 | 843s | 2023-06 | Alan Becker | Animation vs. Math |
| 2 | 50,867,169 | 31s | 2024-05 | Zack D. Films | How Fossilization Works 🤔 |
| 3 | 47,520,729 | 298s | 2016-01 | KLT | 50 States Song — USA States and Capitals (Geography Explained) |
| 4 | 47,081,328 | 97s | 2025-09 | GeoGlobeTales | Spain's Strangest Borders 🤯 Unexpected Hidden Neighbors 👀 |
| 5 | 46,287,579 | 17s | 2022-06 | MinuteMinis | Why do Rivers Curve? |
| 6 | 39,801,924 | 251s | 2017-08 | National Geographic | Solar System 101 |
| 7 | 37,483,831 | 282s | 2013-06 | CGP Grey | The US-Canada Border Is 5,500 Miles of Pure Nonsense |
| 8 | 33,319,271 | 1337s | 2020-09 | Cordova Joyful Learning | Prithviraj Chauhan \| 3D Animation Movie |
| 9 | 32,867,019 | 542s | 2024-06 | Alan Becker | Animation vs. Geometry |
| 10 | 32,034,328 | 61s | 2024-07 | GeoGlobeTales | Why Do Time Zones Look So Strange 🌍 How They Work 🕒 |
| 11 | 31,910,079 | 299s | 2020-01 | National Geographic | Volcanoes 101 |
| 12 | 30,746,240 | 30s | 2025-10 | GrowBig | Where is INDIA? 🔥 #shorts #india #fyp #geography |
| 13 | 28,537,025 | 90s | 2025-10 | Historically | What if Germany won WW2 #shorts #4k #history |
| 14 | 26,075,568 | 43s | 2025-04 | Raj's SnapFusion | Safest Countries to Survive World War 3 #shorts #map |
| 15 | 25,826,068 | 74s | 2025-04 | Howtown | 1.8 billion years in 60 seconds |
| 16 | 23,881,287 | 156s | 2015-07 | Business Insider | Animated map shows how religion spread around the world |
| 17 | 23,734,445 | 2125s | 2022-05 | Sunlike study | The Rise of Nationalism in Europe (Class 10, Animation) |
| 18 | 22,557,645 | 1301s | 2022-11 | SypherPK | The ENTIRE History of Fortnite: Animated! |
| 19 | 21,709,633 | 60s | 2023-11 | Reed Schultz Geo | What does the shortest border in the world really look like? #geography |
| 20 | 18,619,965 | 514s | 2016-11 | PlatigeImage | Animated History of Poland |
| 21 | 18,025,997 | 175s | 2018-05 | Tom Scott | The US-Canada border splits this road down the middle |
| 22 | 17,172,333 | 41s | 2023-07 | KK Create | Physical features of India 😍 #shorts #geography #map |
| 23 | 17,124,675 | 1759s | 2017-03 | illacertus | The 48 Laws of Power (Animated) |
| 24 | 16,932,906 | 81s | 2026-08 | Professor Of How | Nepal Floods (3D Animation) |
| 25 | 16,484,749 | 16s | 2025-03 | War map animation | Indian-Portuguese War 1961, Annexation of Goa |

**Read this table carefully:** is "map/geography" niche ke top me aadhi cheezein **actual map content nahi** hain — animation art (Alan Becker), song (KLT), gaming history (SypherPK), film (PlatigeImage), self-help (illacertus). Search query ka **intent drift** ye hai: "animation" + "map" likhne se YouTube animation wali cheezein bhi le aata hai.

Is liye niche ka **core** (jo asal me border/geography ka kaam hai) ye 9 hain: GeoGlobeTales, Reed Schultz Geo, CGP Grey, Tom Scott, Howtown, MinuteMinis, Historically, Business Insider (animated map), National Geographic.

---

## 6. 25 channel deep dive — catalogue-level sach

Har channel ki **poori recent catalogue** (100 uploads tak) khenchi, taake pata chale "ek video chal gayi" vs "channel ka pattern chalta hai".

| Channel | Country | Joined | Subs | Videos (total) | Catalogue n | Median views | ≥3x outliers | Short | Med | Long | Median dur |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Alan Becker | US | 2006-07 | 34.4M | 271 | 100 | 18,052,035 | 8 | 69% | 24% | 7% | 48s |
| Zack D. Films | — | 2021-06 | 29.7M | 4212 | 100 | 8,499,768 | 1 | 100% | 0% | 0% | 34s |
| GeoGlobeTales | CA | 2023-11 | 2.09M | 169 | 100 | 4,290,031 | **12** | 100% | 0% | 0% | 70s |
| CGP Grey | GB | 2010-08 | 7.05M | 195 | 100 | 6,711,882 | 9 | 23% | 72% | 5% | 385s |
| Professor Of How | IN | 2017-05 | 16.2M | 655 | 100 | 5,244,465 | 10 | 90% | 0% | 10% | 86s |
| Historically | NL | 2023-03 | 1.64M | 85 | 83 | 3,574,072 | **11** | 73% | 16% | 11% | 79s |
| Reed Schultz Geo | US | 2022-11 | 571K | 84 | 84 | 2,759,232 | 10 | 98% | 2% | 0% | 57s |
| Sunlike study | IN | 2021-06 | 2.29M | 96 | 96 | 1,622,110 | 12 | 0% | 65% | 35% | 721s |
| Howtown | US | 2024-03 | 1.44M | 119 | 100 | 601,159 | 12 | 75% | 8% | 17% | 91s |
| History Matters | GB | 2015-08 | 1.92M | 398 | 100 | 988,934 | **0** | 65% | 35% | 0% | 217s |
| GrowBig | IN | 2023-03 | 137K | 83 | 83 | 169,615 | 12 | 98% | 2% | 0% | 31s |
| Geo Study | IN | 2023-09 | 862K | 221 | 100 | 278,153 | 12 | 73% | 20% | 7% | 88s |
| TED-Ed | US | 2011-03 | 23.0M | 2397 | 100 | 408,127 | 12 | 2% | 97% | 1% | 351s |
| KLT | US | 2015-01 | 2.76M | 937 | 100 | 404,995 | 9 | 85% | 6% | 9% | 122s |
| The Operations Room | GB | 2019-04 | 1.45M | 213 | 100 | 424,016 | 7 | 32% | 15% | 53% | 1296s |
| The Armchair Historian | US | 2016-06 | 2.54M | 337 | 100 | 438,251 | 2 | 10% | 57% | 33% | 1108s |
| Animation gyaan hub | IN | 2025-09 | 61.8K | 142 | 100 | 52,164 | 12 | 100% | 0% | 0% | 48s |
| National Geographic | US | 2006-05 | 26.6M | 11580 | 100 | 150,862 | 12 | 52% | 7% | 41% | 104s |
| Geo All Day | US | 2023-11 | 392K | 237 | 100 | 123,365 | 12 | 88% | 12% | 0% | 71s |
| MinuteMinis | US | 2022-02 | 423K | 304 | 100 | 22,461 | 12 | 100% | 0% | 0% | 54s |
| Business Insider | US | 2009-10 | 10.6M | 8267 | 100 | 12,392 | 12 | 89% | 7% | 4% | 95s |
| StudyIQ IAS | IN | 2015-06 | 20.6M | 67630 | 100 | 20,151 | 12 | 20% | 40% | 40% | 916s |
| BibleProject | US | 2013-11 | 5.51M | 558 | 100 | 45,614 | 9 | 80% | 19% | 1% | 67s |
| Raj's SnapFusion | IN | 2023-12 | 38.3K | 303 | 100 | 18,743 | 12 | 100% | 0% | 0% | 43s |
| Cordova Joyful Learning | IN | 2017-03 | 505K | 160 | 100 | 4,517 | 12 | 93% | 3% | 4% | 55s |

**Countries:** US 9 · IN 8 · GB 3 · CA 2 · NL 1 · unknown 2.

### 6.1 Naye channels ka asli signal — jo mujhe sab se ahem laga

Is table ka sab se zyada valuable hissa **joined date + subs + median** ka combination hai:

| Channel | Joined | Subs | Median views | Median duration | Matlab |
|---|---|---|---|---|---|
| **GeoGlobeTales** (CA) | 2023-11 | 2.09M | **4.29M** | **70s** | 2 saal me 2M subs, **100% short**, har video ka median 4.29M — yani ye kismat nahi, **system** hai |
| **Reed Schultz Geo** (US) | 2022-11 | 571K | 2.76M | 57s | 571K subs par **2.76M median** — yani views subs se 4.8x zyada, distribution-led channel |
| **Historically** (NL) | 2023-03 | 1.64M | 3.57M | 79s | 85 videos, 11 outliers, **zero tags, 6-word descriptions** — metadata par bilkul invest nahi |
| **Howtown** (US) | 2024-03 | 1.44M | 601K | 91s | 2 saal, 119 videos, aur ek 44.8M outlier — **hit-driven**, median kam |
| **Geo All Day** (US) | 2023-11 | 392K | 123K | 71s | 392K subs par median sirf 123K — yani "map shorts" bana lena kaafi nahi |

**Sab se ahem observation:** GeoGlobeTales aur Reed Schultz dono **US/Canada se, short-only, 57–70s, aur naye (2022–2023)** hain — inki median apne subs se **zyada** hai. Ye woh exact shape hai jo aap ke case me fit hoti hai: naya channel, English, US audience, 3D map animation. **Professor Of How** (16.2M subs, 90% short, 86s median) yahi shape Hindi me chala raha hai — yani format language-agnostic hai, audience ni.

### 6.2 Har channel ke actual winners (≥3x median) — pattern kya kehta hai

**GeoGlobeTales** (12 outliers, 100% short, median 70s):

| Views | Dur | Title |
|---|---|---|
| 61,179,108 | 103s | 27 Years to Walk Around the World 😱 The Longest Distance in History🚶‍♂️ |
| 47,081,328 | 97s | Spain's Strangest Borders 🤯 Unexpected Hidden Neighbors 👀 |
| 34,864,465 | 81s | Why Chile Is So Long & So Thin 🇨🇱 🌶️ |
| 34,768,009 | 95s | Why USA Built a Giant Wall from Canada to Texas 😱🇺🇸 |
| 31,552,984 | 99s | The Strangest Border Between Sweden & Finland 🇸🇪🇫🇮 Märket Island 🤯 |
| 30,573,224 | 85s | Which Country Is Closest to Space? 🚀 |
| 29,002,124 | 73s | The Difference Between UAE, Dubai & Abu Dhabi 🇦🇪 |
| 27,179,418 | 89s | Why North and South Korea Are Still at War 🇰🇷 |

Pattern: **"sab se ajeeb / sab se lamba / sab se chhota" + asli jagah ka naam + emoji flag**. Har video me ek **contradiction**: map par kuch, asliyat me kuch aur. Description 174–212 words (in outliers ki), tags 12–32, chapters 0.

**Reed Schultz Geo** (10 outliers, median 57s):

| Views | Dur | Title |
|---|---|---|
| 21,709,637 | 60s | What does the shortest border in the world really look like? #geography |
| 13,195,289 | 50s | I never knew that every map lied to us..😦 #shorts |
| 12,866,190 | 57s | The one place in the US where EVERYTHING is legal… |
| 12,708,055 | 57s | The weirdest country border situation in the entire world… |
| 12,029,158 | 57s | I always thought that Alaska was the largest 😭 #shorts |
| 11,620,719 | 52s | The true answer really surprised me lol #shorts |
| 10,814,950 | 60s | Why doesn't any country want to own this piece of land?? #geography |

Pattern: **personal doubt hook** ("I never knew", "I always thought", "the true answer really surprised me") + US angle jab possible ho ("the one place in the US"). Ye **audience ke andar ka sawal** hai, presenter ka lecture nahi.

**Similarly:** Historically (NL) 28.5M "What if Germany won WW2", 28.4M "60s before NUKE", 21.7M "Why the 🇫🇷 hate Potatoes" — **zero tags, 6-word description**, sirf hook + 70–90s animation. Howtown (US) 44.8M "Noah Lyles won the 100m by point zero zero five seconds" — **number-as-hook**. CGP Grey 44.6M "Traffic Has a Perfect Solution. Humans Are the Problem." — **claim + blame**, 270s.

### 6.3 Channel-level lesson

- **Median duration 48–103s** un channels me jo consistent hain; **385–1296s** un me jo long-form authority hain (CGP Grey, Operations Room, Armchair Historian).
- **Metadata invest vs performance ka koi seedha rishta nahi**: Historically (zero tags, 6-word desc) ka median 3.57M; Business Insider (8,267 videos, full SEO) ka 12,392. Yani **metadata se jeet nahi aati** — hook aur clarity se aati hai; metadata sirf **kaam ko support** karta hai.
- **History Matters ke 0 outliers** (100 videos, median 988K) sab se zyada instructive failure hai: channel stable hai, koi video median se 3x nahi gayi. Yani "achha channel" aur "hit" do alag cheezein hain; hit ke liye **specific escalation** chahiye.

---

## 7. Outlier cross-tab — kya cheez winners ko alag karti hai

Niche ke andar: **20 outliers (≥3x channel median), jo niche corpus (520 videos) me bhi mojood hain** vs **500 baaki**. (25 catalogues me total **238** outlier rows mile — magar un me se sirf 20 niche ke apne 520-video corpus me aaye; baaki catalogue-only hain. Dono ko mix karna galat hoga, is liye cross-tab sirf 20 par hai.)

| Measure | Outliers (n=20) | Rest (n=500) | Farq |
|---|---|---|---|
| Median views | **12,613,808** | 2,084,235 | **6.1x** |
| Median views/day | **12,311** | 1,546 | **8.0x** |
| Median duration | **85s** | 515s | 6x chhota |
| Short share | **70%** | 33.8% | 2.1x |
| Medium share | 10% | 39.0% | 0.26x |
| Long share | 20% | 27.2% | 0.74x |
| Number in title | **60%** | 36.4% | 1.65x |
| Question in title | 10% | 15.0% | 0.67x |
| Emoji in title | 15% | 11.0% | 1.36x |
| Hashtag in title | 30% | 15.6% | 1.92x |
| Median title words | 9.5 | 10 | barabar |
| Median desc words | **83.5** | 152.5 | **0.55x** |
| Chapters ≥3 | 20% | 19.6% | barabar |
| Has captions | **0%** | 20.8% | — |
| Median tags | 13.5 | 17 | 0.79x |
| Median like-rate | 1.83% | 1.79% | barabar |

### 7.1 Teen ahem nateeje

1. **"Chhota + number + chhoti description" = is niche ka jeetne wala signature.** Winners 85s, title me number, description 83 words. Ye teeno mil kar kehte hain: **video ek hi cheez promise karti hai aur jaldi de deti hai**.
2. **Captions ka 0% "captions buri hain" ka proof nahi.** Iska matlab ye hai ke jeetne wale creator apni video ke liye captions upload nahi karte (kyunki shorts me auto-captions chalti hain). Lekin hamare liye **burned-in on-screen text** zaroori hai — kyunki mobile par sound off dekha jata hai. Ye **production decision** hai, evidence ka naate nahi.
3. **Like-rate me farq nahi** (1.83% vs 1.79%). Yani outliers ko **zyada pasand nahi kiya jata** — unhe **zyada dikhaya jata hai** ya wo **zyada click hote hain**. Is se sirf itna keh sakta hoon: like-rate is niche me **quality ka discriminant nahi** hai. Aur ye bhi ho sakta hai ke bade videos par like-rate dilute ho jaye (casual viewers). **Is par koi causal claim nahi.**

---

## 8. Script forensics — 5 verbatim transcripts

Ye 5 transcripts **public caption text** se verbatim capture kiye (source: `youtubetotranscript.com/transcript?v=<ID>`), workspace me `map_scripts_v20.json` me poori tarah mojood hain. Ye **competitor ki lines hain, hamari nahi** — sirf structure padhne ke liye.

| Channel | Video | Views | Dur | Words | WPM | Numbers | Sentences | Words/sentence | Unique places |
|---|---|---|---|---|---|---|---|---|---|
| GeoGlobeTales | 27 Years to Walk Around the World | 61,179,108 | 103s | 318 | **185** | 20 | 15 | 21.2 | 6 |
| GeoGlobeTales | Spain's Strangest Borders | 47,081,328 | 97s | 320 | **198** | **8** | 17 | 18.8 | **9** |
| Howtown | Noah Lyles won by 0.005s | 44,837,676 | 59s | 202 | **205** | 6 | 1* | — | 2 |
| CGP Grey | The US-Canada Border… | 37,483,831 | 282s | 316 | **67** | 7 | 22 | **14.4** | 3 |
| Reed Schultz Geo | Shortest border in the world | 21,709,633 | 60s | 219 | **219** | 6 | 1* | — | 2 |

\* ASR/caption punctuation nahi rakhta, is liye sentence-count unreliable hai. Isi wajah se `reading_grade` bhi (Howtown 83.0, Reed Schultz 88.1) **noise** hai — unpunctuated text par grade ka koi matlab nahi. Main in numbers ko **evidence ke tor par use nahi kar raha**, sirf sharam ke saath dikha raha hoon.

### 8.1 Spain's Strangest Borders — beat-by-beat decode (97s, 320 words)

| Time (approx) | Beat | Kaam |
|---|---|---|
| 0–8s | "Did you know Spain is the country with the strangest borders?" | **Sawal + superlative**, audience ko challenge |
| 8–14s | "On the map, it looks like Spain has only two land neighbors… but in reality, there are many more" | **Map vs reality contradiction** — poore niche ka core engine |
| 14–30s | Llivia: town inside France, 2 km from border, Spanish territory → "This is called an enclave" | **Pehla example + naam** (terminology deta hai, taake viewer seekhne ka feel kare) |
| 30–50s | Pheasant Island: border island, 6 months Spain, 6 months France | **Escalation**: enclave se aage — "ye to aur ajeeb hai" |
| 50–65s | Andorra: 80,000 log, "half the size of New York City" | **US anchor** (New York) — audience ko scale samjhane ke liye |
| 65–80s | Gibraltar: UK ka overseas territory, Strait ka control, Europe/Africa divide | **Geopolitics ka teaser**, bina politics me ghuse |
| 80–97s | Ceuta, Melilla + "shortest land border in the world, just 85 m" | **Payoff + record** — video ka promise poora |

**Structure formula:** *ek sawal → ek contradiction → 3–4 escalating examples (har example me: naam + ek line geography + ek line consequence) → ek record/payoff.* Har example ~15–20s. Koi intro nahi, koi "subscribe" nahi, koi channel branding nahi.

### 8.2 Reed Schultz — "shortest border" (60s, 219 words)

Beat 1: **apni purani video ko correct karta hai** — "in one of my older videos I said the shortest was this 150 m border from Botswana to Zambia but I kind of lied". Ye ek **self-correction hook** hai: curiosity + trust, dono ek saath. Beat 2: sawal ("how could they possibly share a border?"). Beat 3: history (Spain ne northern Morocco chhoda, kuch hisse reh gaye). Beat 4: concrete detail — "this small rock inhabited only by a couple dozen Spanish soldiers… supplies brought in through helicopter". Beat 5: payoff — "85 m, the shortest border in the world".

**Lesson:** ek hi fact (85 m) ko **teen channels** ne alag-alag angle se 21M–47M views dilwaye. Yani is niche me **fact naya nahi hota, framing nayi hoti hai** — aur wo framing **ek chhoti si insani detail** se banti hai (soldiers, helicopter, "eight steps as a kid", "four border crossings to school").

### 8.3 27 Years to Walk Around the World (103s, 318 words, 20 numbers)

Ek hi insaan (Carl Bushby) ke 27 saal, magar har 10 second me ek **naya obstruction + number**: Darién Gap 50 din, Panama 18 din arrest, 6 saal North America, Bering Strait 80 km off course, Russia visa 90 din, Siberia −50°C / 11 saal, Kazakhstan 4 saal, Caspian 30 din swim, 25 countries, 47,000 km. Ye **number-stacking narrative** hai — audience ko "kitna mushkil tha" ka ehsaas numbers se hota hai, adjectives se nahi.

### 8.4 CGP Grey (282s, 316 words, 67 wpm)

Slow, dense, **14.4 words per sentence** (baaki sab 18–21). Mechanism: "straight" claim ko **torne** se shuru karta hai ("Sure it looks straight… but the official border is 900 lines that zig-zag"). Phir **counterfactual immersion**: "imagine you're back in North America in the 1800s… you're handed a compass and a ball of string… Good luck." Phir **human consequence**: Point Roberts ke bachche din me 4 dafa international border cross karte hain school jaane ke liye.

**Lesson:** long-form me wpm **kam** hota hai kyunki har sentence me **idea** hota hai. Hum 67 wpm copy nahi karenge (wo 7M-sub channel ka established rhythm hai) — hamara target 150–165 wpm hai, lekin **sentence length 14–17 words** rakhenge.

---

## 9. Title forensics — 520 titles + 25 catalogues

### 9.1 Openers (pehla lafz)

**≥5M wale 125 videos:** `the 19` · `why 9` · `india 4` · `how 3` · `animation 3` · `what 3` · `history 3` · `50 2` · `solar 2` · `most 2` · `animated 2`
**<5M wale 392 videos:** `why 39` · `the 32` · `how 28` · `indian 13` · `what 12` · `complete 11` · `geography 10` · `india 8` · `book 8` · `map 6`

**Ye ulta lagta hai, aur ye ahem hai:** "why" se shuru hone wali videos **chhoti** bucket me zyada hain (39 vs 9). Yani **"Why…" likhna guarantee nahi** — bade winners me "the" (definite article) zyada hai: *The* US-Canada Border, *The* Strangest Borders, *The* Longest Distance.

**≥5M vs <5M share:**

| Signal | ≥5M (n=125) | <5M (n=392) |
|---|---|---|
| "why" opener | 7.2% | 9.9% |
| "how" opener | 2.4% | 7.1% |
| Country name in title | **34.4%** | 31.1% |
| Emoji | **20.8%** | 7.9% |
| Hashtag | 17.6% | 15.6% |
| Number | **41.6%** | 34.9% |
| Median duration | 209s | 552s |

**Reading:** winners me **emoji (2.6x)** aur **number (1.2x)** zyada; "how" kam (kyunki "how to make map animation" wali tutorial videos chhoti hoti hain). Country name dono me ~1/3 — yani **desh ka naam zaroori nahi, magar common hai**; farq **specificity** ka hai (Spain, Point Roberts, Chile) vs generic ("geography", "map").

### 9.2 Hashtags (≥10M wali videos ki descriptions + titles se)

`geography 18` · `shorts 14` · `history 12` · `map 11` · `fyp 6` · `learning 6` · `usa 5` · `unitedstates 5` · `maps 5` · `facts 5` · `geoshorts 5` · `uniquegeography 5` · `viral 5` · `viralmap 5` · `cbse 5` · `ncert 5` · `upsc 4` · `india 4` · `border 4` · `learn 4`

**Note:** `cbse/ncert/upsc` (Indian exam tags) 4–5 dafa aaye — yani Hindi/exam market same hashtag space me hai. US audience ke liye hum `geography`, `map`, `maps`, `border`, `usa`, `history`, `facts`, `geoshorts`, `uniquegeography` use karenge — `fyp/viral` jaise **empty-reach tags nahi** (in ka koi measurable matlab nahi).

### 9.3 Hamare titles (evidence-pattern se banaye, copy nahi)

Long-form (Ep 01) — 3 options:
- **A)** `The US–Canada Border Is Not Actually Straight`
- **B)** `5,525 Miles of Border, 900 Kinks: Why the US–Canada Line Is Broken`
- **C)** `The Map Mistake That Put 1,000 Americans Behind Canada`

Short 1 (Point Roberts): `The US Town You Can Only Reach Through Canada`
Short 2 (20-foot gap): `America's Border Has a 20-Foot Gap. All 5,525 Miles of It.`
Short 3 (49th parallel): `The "Straight" Border That Zig-Zags 900 Times`

**Kyun ye:** har title me **number** (5,525 / 20 / 900 / 1,000), **contradiction** (straight/not straight, you can only reach/it's in the US), aur **specific place** hai — teeno V20 ke winners me upar thay. Koi "shocking", "you won't believe", "100%" nahi.

---

## 10. Description, chapters, tags — forensics

| Measure | Outliers (n=20) | Rest (n=500) | Lane extremes |
|---|---|---|---|
| Median desc words | **83.5** | 152.5 | geo_explainer long 235 · map_animation short **37** |
| Chapters ≥3 | 20% | 19.6% | history_map long **42%** · short lanes **0–2%** |
| Median tags | 13.5 | 17 | map_animation short **8** · borders_geo long 21 |
| Captions | 0% | 20.8% | geo_explainer long / borders_geo medium high |

**Description ka asli kaam** (jo outliers se dikhta hai): (1) ek do line me promise repeat, (2) sources/credits, (3) 1–2 related links, (4) 3 hashtags. Bas. 83 words kaafi hain. `Historically` to 6 words me kaam chala raha hai.

**Tags ka kaam:** 8–21 tags; outliers me 13.5 median. Winners me zero-tag examples bhi hain (Historically, Howtown ke kai videos) — yani tags **discovery ka primary lever nahi**. Hum 12–14 focused tags rakhenge (brand-safe, relevant), keyword stuffing nahi.

---

## 11. Thumbnail statistics — 20 images par pixel analysis

**Boundary pehle:** ye **static image analysis** hai. `face_present` ek permissive skin-tone pixel heuristic hai, **chehra pehchan nahi**; `text_row_span`/`text_edge_energy` **OCR nahi**; `busy` ek edge-density proxy hai. Aur CTR/impressions **private** hain — is liye "ye thumbnail views laya" kehna **causal claim** hoga. Hum nahi kehte.

| Bucket | n | Face present | Face share | Contrast | Brightness | Accent share | Busy |
|---|---|---|---|---|---|---|---|
| Short | 15 | 86.7% | 15.7% | 0.192 | 0.221 | 0.381 | 2.24 |
| Medium | 2 | 100% | 22.8% | 0.301 | 0.679 | 0.709 | 4.64 |
| Long | 4 | 50% | 21.8% | 0.262 | 0.504 | 0.651 | 3.45 |
| **All** | **20** | **81%** | 17.6% | 0.216 | 0.319 | 0.464 | 2.70 |

**Dominant hue families:** blue-ish `#276092` / `#2b5c76` (share up to 0.94), amber/gold `#f6d860` / `#e3b873`, olive/green `#4b5837` / `#648b22`, terracotta `#ae5a49`. Yani **map ka natural palette** (blue water, land beige/olive, red accent).

**Reading (careful):**
- Short thumbnails me face 86.7% par **face share sirf 15.7%** — yani chehra **chhota** hota hai (map ke corner me), thumbnail face-led nahi hai. Ye `Reed Schultz Geo` ke thumbnails se match karta hai (face 0.089–0.16 par share).
- `Geo Study` (Hindi) ke thumbnails me face share **0.29–0.49** — yani face-led style wahan zyada hai. Do **alag visual languages** hain, aur hum English/US style choose karte hain.
- Busy metric short me 2.24 vs medium 4.64 — yani short thumbnail **saaf** rehta hai. 70–100s video ke liye ye logical hai.

**Hamara thumbnail spec (proposal):**

| Format | Text | Composition | Safe zone |
|---|---|---|---|
| Short | 2–4 words max (`85 METRES`, `20 FEET`, `NOT IN CANADA`) | ek zoomed map crop + ek red line/pin, ek accent colour | text top 18%, bottom 20% clear (UI) |
| Long | `NOT STRAIGHT` / `900 KINKS` | left: map line ka kink close-up; right: **Point Roberts** ka tiny enclave highlighted | same |
| Rule | Koi misleading arrow/red circle nahi. Har text jo thumbnail me hai, video me **sach me** cover hota hai. | | |

---

## 12. Comments — 220 fetched comments, 12 videos

`commentThreads`: 11/12 requests ok (KLT `50 States Song` par error), `order=relevance`, `maxResults=20`.

| Bucket | Count | Share of fetched |
|---|---|---|
| `map_nerd` (border / enclave / parallel / projection / cartography) | **10** | 4.5% |
| `correction_claim` (actually / wrong / not true / you forgot) | **8** | 3.6% |
| `personal_tie` (I live / my country / here in) | 3 | 1.4% |
| `did_not_know` (I never knew / TIL) | 1 | 0.5% |
| `sequel_or_next` (part 2 / next video / do more) | **0** | 0% |
| `ask_how_made` (how did you animate / which software) | **0** | 0% |
| `country_request` | 0 | 0% |

**Per video:** CGP Grey US-Canada par **6 map-nerd** comments (sab se zyada) + 1 correction; GeoGlobeTales Spain par 3 corrections + 2 personal ties + 2 map-nerd.

**Verbatim examples** (public comments, sirf pattern dikhane ke liye — ye logon ki apni zubaan hai):

- CGP Grey par: *"I, with my Canadian father and American mother, am living proof that the 'no touching zone' thing doesn't always work."*
- CGP Grey par: *"Person: I think I found oil on the no-touching zone. USA: who said that was a no-touching zone?"*
- CGP Grey par: *"I accidently crossed into Canada during a hunting trip and the Canadian trooper I ran into was super nice…"*
- GeoGlobeTales Spain par: *"You've opened Andorra's box by bringing up all these territorial oddities."*
- GeoGlobeTales Spain par: *"'Where do you live?' 'What month is it?' 'what'"* (Pheasant Island ka joke)
- GeoGlobeTales Time Zones par: *"Imagine waking up at 10am and it's dark 😂. Us Americans will go back to sleep"* — **US identity** comments aate hain jab subject US ko touch kare

**Comment strategy (evidence se, guess se nahi):**
1. **Correction ko welcome karo, chhupao nahi.** 8/220 correction-type hain — ye is niche me **normal** hai. Hamara pinned comment: *"Har number ka source description me hai. Koi ghalti mile to likhein — next video me correction card aayega."* Ye invite **trust** banata hai aur echo-chamber ke "actually" bombs ko productive bana deta hai.
2. **Personal-tie comments ko pin karo** (3/220): "I grew up in Point Roberts…" type comment sab se zyada engaging hota hai.
3. **"Part 2" ka demand 0 hai** — is liye **cliffhanger par video khatam mat karo**. Har video **self-contained** honi chahiye, aakhir me ek **agla sawal** (vote) chhodo.
4. **"How did you animate" 0** — is liye behind-the-scenes/making-of content is audience ke liye priority nahi. (Shorts me wo alag audience ho sakti hai, magar is data me nahi.)

---

## 13. Public demand signal — autocomplete (honest read)

Method: Google/YouTube autocomplete via `suggestqueries` (gl=us). Ye **ordered demand signal** hai — suggestion ka aana matlab koi na koi real query volume hai; position matlab wo baaki completions se aage hai. **Ye search volume ya trend nahi hai.**

| Probe | Suggestions mili | Kya dikha |
|---|---|---|
| `point roberts` | 10 | map · population · `point roberts usa` · real estate · tides — **yani log is jagah ko search karte hain** |
| `weird borders` | 10 | `weird borders in the world` · `weird borders in europe` · **`weird borders canada us`** · **`weird borders in the us`** · `belgium weird borders` |
| `us canada border` | 9 | `map` · `length` · `latitude` · `parallel` · `wait times` · `crossing` — yani **line ki geometry** ka intent asli hai |
| `why does the us border` | 10 | security/patrol/phones — yani **politics/policy** ka intent bhi andar hai (hum isay avoid karenge) |
| `darién gap map` | 9 | `map` · `route` · `google earth` · `topographic` — **map-first** intent |
| `map borders explained` | **0** | abstract topic par **koi demand nahi** |
| `why is there a town` | 8 | US town-name curiosity (Chevy Chase, Hell, Intercourse, Truth or Consequences) — **"why is this town here"** wala format chalta hai |

**Sab se ahem nateeja:** `map borders explained` par **zero**. Yani log **abstract geography topic** search nahi karte; wo **ek jagah ka naam** search karte hain. Hamari discovery strategy isi liye **topic-led nahi, place-led** hogi: har video ka title ek jagah ka naam rakhega.

**Aur ek honest warning:** `why does the us border` ki suggestions me **border patrol / phone search / illegal crossing** jaisa policy intent hai. Us intent par video banane ka matlab politics me ghusna hai — is niche me woh **sab se zyada polarizing** content hai. Hum **map/history** par rahenge, policy par nahi. (Ye ek **editorial** decision hai, legal advice nahi.)

---

## 14. 3D animation ka asli hisaab — cost aur waqt

Aap ne 3D allow kiya hai, is liye main ise **production reality** ke saath likh raha hoon. Ye numbers **estimates** hain (kisi vendor quote ya internal data se nahi — sirf shot-count × typical per-shot time). Inhe **budget commitment na samjhein**.

### 14.1 Shot math

| Cheez | Value |
|---|---|
| Target length (Ep 01 long) | **17 min = 1,020s** |
| Avg shot length (map explainer) | **6–9s** (visual change har 6–9s; winners ka 60–100s short me har 4–7s change hota hai) |
| Shots needed | **128** (assigned, `SHOTLIST_EP01_V20.csv`) — range 130–170 agar shots chhote hon |
| Unique 3D "sets" | 6 (globe, continent plane, 49th parallel strip, Point Roberts close-up, Northwest Angle lake, monument/obelisk detail) |
| Reusable assets | continent mesh (Natural Earth, public domain), border polyline, monument model, compass/chain props |
| Per-shot cost (estimate) | **2.5–4 ghante** (layout → camera → light → render → comp), agar asset ready ho |
| Total 3D hours (estimate) | **325–680 ghante** |
| Agar per-shot reuse ho (10 sets ko 130 shots me reuse) | **180–320 ghante** |

### 14.2 Do raste (aur meri tajweez)

| Route | Kya | Waqt (estimate) | Risk |
|---|---|---|---|
| **A. Full 3D (Blender)** | Asli 3D continent, extruded border, camera fly-throughs, depth of field, volumetric light | 325–680 ghante | Zyada slow; ek insaan ke liye 3–4 mahine |
| **A' — hamara shotlist** | 128 shots, jismein **16 hero shots 3D** aur **112 2.5D** | ~**200–260 ghante** | Ye hybrid hi `SHOTLIST_EP01_V20.csv` me likha hai |
| **B. 2.5D map-first (recommended)** | Orthographic map plane + layered parallax + depth-extruded borders + 3D props sirf 6–8 hero shots me | **120–200 ghante** | Kam cinematic, lekin **GeoGlobeTales/Reed Schultz ka exact look** isi route se banta hai |
| **C. Hybrid (mera pick)** | Shorts = B (2.5D, tez), Long = A ke 8–10 hero shots + B ke baaki | 200–280 ghante | Balance |

**Kyun B/C:** niche ke winners me se koi bhi full-CGI cinematic nahi hai — GeoGlobeTales, Reed Schultz, Howtown, Historically sab **flat map + text + fast cuts** hain. Sirf Professor Of How (Hindi) aur Cordova (story) full 3D karte hain. Yani **3D "allowed" hai, magar is niche ka jeetne wala look 3D nahi hai** — wo **saaf map + ek red line + tez awaaz** hai.

**Iska matlab ye nahi ke 3D se bachein:** 3D hamare liye **differentiator** hai *agar* wo **clarity** barhaye (e.g. border line ko 3D me uthana, monument ko scale me dikhana). 3D ko **show-off** banane se wahi 325–680 ghante jal jayenge.

---

## 15. Episode slate — is niche ke liye 5 deliverables

| # | Format | Title | Length | Kyun (evidence) |
|---|---|---|---|---|
| **E1** | Long (flagship) | The US–Canada Border Is Not Actually Straight | 17 min | CGP Grey 37.5M @282s + Tom Scott 18.0M @175s + Reed Schultz 21.7M @60s: **same subject, 3 formats, verified public views**. US audience ke liye sab se seedha fit. |
| **S1** | Short (cut from E1) | The US Town You Can Only Reach Through Canada | 55–60s | Point Roberts ka autocomplete demand (10 suggestions) + CGP Grey ke comments me sab se zyada map-nerd reaction isi hisse par |
| **S2** | Short (cut from E1) | America's Border Has a 20-Foot Gap | 45–50s | GeoGlobeTales/Reed Schultz ka proven "ek ajeeb fact + map" format |
| **S3** | Short (cut from E1) | The "Straight" Border That Zig-Zags 900 Times | 55–60s | 900 monuments ka number + "map jhoot bolta hai" contradiction — niche ka core engine |
| **M1** | Medium | Why the 49th Parallel Isn't a Straight Line | 9–10 min | `borders_geo_medium` lane me CGP Grey 37.5M/282s aur JackSucksAtGeography 6.8M/424s — medium bucket is subject par zinda hai |

**Is slate ki logic:** ek long-form "mother" video, uske 3 shorts (jo **uske hi 3 sab se strong beats** hain), aur ek medium jo **ek hi sawal** (49th parallel) ko gehrai se kholta hai. Ye **compilation nahi** — teeno shorts **apne dam par** khadi hain, aur long unka **poora context** deta hai.

---

## 16. EPISODE 01 — poora long-form script (English VO, 17 min)

**SERIES:** *Lines on a Map* (working title — aap change kar sakte hain)
**EPISODE 01:** *The US–Canada Border Is Not Actually Straight*
**Format:** 16:9, 1920×1080, 24fps (motion graphics), VO 150–165 wpm, 9 chapters
**Language:** English (US audience). **Har number `[VERIFY]` hai** — publish se pehle treaty text/IBC/USGS se confirm karna hai.

### 16.1 Cold open (0:00–0:50)

**[VISUAL: Black. A single white line. It starts perfectly straight, then at 6s a kink appears — small, 3 frames. Camera pulls back; the line becomes a 5,525-mile strip across a continent. Text: `NOT STRAIGHT`]**

> **VO:** This is the border between the United States and Canada.
> It is 5,525 miles long. It is the longest international border on Earth. `[VERIFY]`
> And for about two hundred years, everyone has described it with the same word: straight.
> It is not straight.
> Not because of politics. Not because of a dispute.
> Because of a map that had a hole in it, a compass, and a ball of string.
> This is the story of a line that nobody could actually draw — and the 1,000 Americans who live on the wrong side of it.

**[VISUAL: title card — `LINES ON A MAP · EP 01`]**

### 16.2 Chapter 1 — The word "straight" (0:50–2:40)

> **VO:** Start with the claim. On almost every map, the western half of this border is a horizontal line. It looks like someone took a ruler to a continent.
> And the treaties do say that. The Treaty of 1818 set the boundary at the 49th parallel — a line of latitude — from Lake of the Woods to the Rocky Mountains. `[VERIFY]`
> A line of latitude is, mathematically, a perfect circle around the planet. So on paper, the border really is a clean curve.
> Here's the problem. A treaty line is an idea. A border is a thing that has to exist on the ground — through forest, through muskeg, through lakes, through mountains nobody had surveyed.
> So between 1872 and 1876, surveyors went out to make the idea real. `[VERIFY]`
> They didn't have GPS. They had a compass, a chain, and the best astronomy of the 1870s.
> And when you do that for hundreds of miles, small errors accumulate.

**[VISUAL: 2.5D — the 49th parallel line drawn onto a continent plane; then the line is "surveyed" in segments, each segment slightly off; end with a zoom showing the zig-zag]**

> **VO:** The result is a border made of roughly 900 straight segments `[VERIFY]` — a line that zig-zags above and below the 49th parallel by as much as a few hundred feet. `[VERIFY]`
> On a globe, you cannot see it.
> At ground level, it decides which country a tree is standing in.

### 16.3 Chapter 2 — The 20-foot gap (2:40–5:00)

> **VO:** Here's what most people have never seen: this border is not just a line. It is a physical gap.
> A cleared strip, about 20 feet wide, running the entire length of the land border. `[VERIFY]`
> Six metres. Both countries agreed to keep it clear — no trees, no buildings, no touching. `[VERIFY]`
> Which means if you fly over the northern United States, you can see the border. Not a fence. Not a wall. A mowed line through a forest, 3,000 miles long.
> And here is the detail that tells you how serious this is: in the middle of one of the most remote stretches of North America — the Alaska–Yukon wilderness — the two countries still send people out to cut the trees down. `[VERIFY]`

**[VISUAL: aerial-style camera over a forest plane; the 20-ft strip is a bright cut; then a close-up of a fallen tree on the line; text `20 FEET`]**

> **VO:** Now hold that image, because it becomes important later. A line that is 6 metres wide and 5,525 miles long is a very strange thing to build.
> And it exists because two countries wanted it to be *completely obvious* which side of the continent is whose.
> Which is ironic — because in about a dozen places, it is not obvious at all.

### 16.4 Chapter 3 — 1783: the map with a hole in it (5:00–8:00)

> **VO:** To understand the weird parts, you have to go back to the end of the American Revolution.
> In 1783, American and British negotiators sat down to draw a border across a continent that neither side had fully mapped. `[VERIFY]`
> They had a map. It was the best available. And in the northwest, that map had an **inset** — a small box drawn over the corner of the map, covering the exact area they were arguing about.
> So they negotiated blind. `[VERIFY]`
> They wrote that the border would run from the northwest corner of a lake, west, until it met the Mississippi River.
> There was one problem. The Mississippi doesn't go that far north.
> The line ran west, and kept running, and hit nothing.

**[VISUAL: the 1783 map plane; an inset box slides in and covers the northwest; the described line is drawn; it stops in empty space; text `SOMEWHERE` then `NOWHERE`]**

> **VO:** So the border was vague. It stayed vague for 35 years. `[VERIFY]`
> In 1818, the two sides tried again, and this time they used a line of latitude: the 49th parallel.
> But the lake they were measuring from turned out to be **higher and less round** than the map showed. So the new line had to jump north to meet the lake, then drop straight down to the 49th parallel — cutting off a small piece of Canada in the process. `[VERIFY]`
> That piece of Canada is called the Northwest Angle. `[VERIFY]`
> It is part of the United States. And you cannot drive to it from the United States.

**[VISUAL: the lake; a small polygon highlighted; a road route drawn that leaves the US, enters Canada, and comes back — 3 crossings; text `YOU CANNOT DRIVE HERE FROM HERE`]**

> **VO:** To get there by road, you leave the United States, drive through Canada, and come back into the United States. `[VERIFY]`
> There is a sign at the border. People take photos of it.

### 16.5 Chapter 4 — Point Roberts (8:00–11:30)

> **VO:** Which brings us to the strangest result of that same line.
> In 1846, Britain and the United States agreed to extend the 49th parallel west, all the way to the sea. `[VERIFY]`
> They were careful about one thing: Vancouver Island. The line would have cut straight through it. Both sides agreed that would be ridiculous, so the border was routed around the island, through the water. `[VERIFY]`
> What nobody noticed was a small peninsula just south of the line.

**[VISUAL: the peninsula; the 49th parallel drawn across it; the land below the line turns blue (US); the peninsula is isolated — water on three sides, Canada on the fourth]**

> **VO:** The line crossed it. Everything below the line became the United States. Everything above became Canada.
> And because the peninsula was attached to Canada on its north side, and surrounded by water on the other three — the American part became an island. Not by water. By **line**.
> It is called Point Roberts. `[VERIFY]`
> About 1,000 people live there. `[VERIFY]`
> There is a primary school. There is no high school.
> Which means, every school day, teenagers who live in the United States get in a car, drive north across an international border into Canada, drive east, and cross back into the United States to go to school. `[VERIFY]`

**[VISUAL: the route; 4 crossings counted on screen; a clock ticking; text `4 BORDER CROSSINGS, ONE SCHOOL DAY`]**

> **VO:** Their school is in their own state. They just can't get there without leaving their country.
> Think about what that means practically. A dentist appointment. A hardware store. A hospital. Anything that isn't in that small triangle of land requires a passport. `[VERIFY]`
> And the reverse is also true: if you're a Canadian in that area, the shortest way to parts of your own country can take you through the United States. `[VERIFY]`
> This is not a war. Nobody is fighting. It's just a line that was drawn on a map by people who couldn't see the ground.

### 16.6 Chapter 5 — The other side of the line (11:30–13:30)

> **VO:** Point Roberts is one of a family. Once you know what to look for, you find these places everywhere on this border.
> There is a lake where the border runs through the water and cuts off a small Canadian peninsula — about 100 Americans live inside it. `[VERIFY]`
> There is an island in the Atlantic that both countries claim, where Canada built a lighthouse and the United States, for years, simply ignored the lighthouse. `[VERIFY]`
> There is a Canadian island whose only road connection is a bridge into the United States. `[VERIFY]`
> And there are places where the two countries' borders have been re-surveyed so many times that a property line can technically be in the wrong country.

**[VISUAL: 4 small map vignettes, each 15–20s, one after another; each with a single label; no clutter]**

> **VO:** The pattern is always the same: an old survey, a bad map, or a line that had to be adjusted for something practical — a road, a lake, a farm — and a community that ended up on the wrong side of a decision made two hundred years before they were born.

### 16.7 Chapter 6 — Why it matters now (13:30–15:30)

> **VO:** So why does a 200-year-old surveying error matter in 2026?
> Three reasons.
> **One:** it shows you that a border is not a natural object. It is a decision, made by people, with tools that were imperfect, and every imperfection became somebody's daily life.
> **Two:** it explains a whole genre of geography content — the "weird border" video — which is not really about weirdness. It's about the gap between the map in your head and the ground under your feet.
> **Three:** it's a reminder that the most interesting thing on a map is usually not the country. It's the line.

### 16.8 Chapter 7 — What we could not verify (15:30–16:40)

> **VO:** A note on sources, because this video makes a lot of specific claims.
> Every number in this video is in the description, with where it came from. The treaty dates, the length of the border, the size of the gap, the survey count, the population of Point Roberts.
> If any of them is wrong, the correction goes in the description and — if it's big enough — in a pinned comment.
> And there's one thing I want to be clear about: this video is about geometry and history. It is not about immigration policy, border enforcement, or who should be allowed where. That's a different conversation, and it isn't this one.

### 16.9 Chapter 8 — Close + vote (16:40–17:00)

> **VO:** There are about a dozen places on this border where the line does something a line shouldn't do. I've shown you three.
> The next one is a lake, a piece of Canada that sticks into the United States, and a town where the border runs through the main street.
> Vote in the comments: **the lake, the peninsula, or the main street.**
> I'll build whichever one wins.

**[END CARD: `LINES ON A MAP` — 3 vote cards; no subscribe-beg, one line: "New map, every two weeks."]**

**Script length (measured, na ke andaza):** poora VO **1,397 words** hai → 155 wpm par **~9.0 min** speech. 17 min runtime ka matlab **~8 min visual/silence/chapter-card breathing room**. Ye ratio **jaan boojh kar** hai: map explainer me har chapter ke beech map par **khamoshi** chahiye, warna 155 wpm par 17 min me 2,600+ words chahiye hote jo is format me bharkeela lagta hai. Exact word counts `EPISODE_01_PLAN_V20.json` ke `vo_blocks` me hain.

---

## 17. SHORTS scripts (English, cut from Ep 01, magar standalone)

### 17.1 S1 — "The US Town You Can Only Reach Through Canada" (58s, ~195 words)

**[0–3s] VISUAL: map of the peninsula. Text: `THIS IS THE US`**
> **VO:** This is Point Roberts. It's in the United States. You cannot drive to it from the United States.

**[3–12s] VISUAL: the 49th parallel drawn across the peninsula; land below turns blue**
> **VO:** In 1846, Britain and America drew the border along the 49th parallel. Straight through this peninsula. Everything below the line became America. Everything above stayed Canada.

**[12–22s] VISUAL: water on three sides, Canada on the fourth**
> **VO:** But the peninsula is attached to Canada on the north, and surrounded by water everywhere else. So the American part became an island — made of a line, not water.

**[22–38s] VISUAL: the school route; 4 crossings**
> **VO:** About a thousand people live there. There's a primary school. No high school. So every school day, American teenagers drive into Canada, then back into America, to get to a school in their own state. Four border crossings a day.

**[38–50s] VISUAL: dentist, hardware store, hospital icons**
> **VO:** A dentist. A hardware store. A hospital. All of it means leaving the country and coming back.

**[50–58s] VISUAL: title card `LINES ON A MAP`**
> **VO:** Nobody fought a war over this. Someone just drew a line they couldn't see the ground under.

### 17.2 S2 — "America's Border Has a 20-Foot Gap" (47s, ~160 words)

**[0–4s] VISUAL: forest plane from above; a bright strip appears**
> **VO:** There is a 20-foot gap running through North America. It's 5,525 miles long.

**[4–16s] VISUAL: strip continues through forest, lake, mountain**
> **VO:** It's the US–Canada border. Both countries agreed to keep a cleared strip — about six metres wide — with no trees, no buildings, nothing on it. From the air, you can see the border as a mowed line through a forest.

**[16–30s] VISUAL: Alaska/Yukon wilderness; a tree falls**
> **VO:** And in the most remote parts — hundreds of miles of Alaskan and Yukon wilderness — they still send people out to cut the trees down. Because the point isn't the trees. The point is that you can never be confused about which country you're in.

**[30–40s] VISUAL: zoom out; the line looks straight, then kinks appear**
> **VO:** Except the line isn't straight. It's about 900 separate segments that zig-zag by hundreds of feet.

**[40–47s] VISUAL: `NOT STRAIGHT`**
> **VO:** Which means the clearest border on Earth is also one of the most crooked.

### 17.3 S3 — "The 'Straight' Border That Zig-Zags 900 Times" (60s, ~200 words)

**[0–4s] VISUAL: perfect straight line; text `STRAIGHT`**
> **VO:** This is called the longest straight border in the world.

**[4–10s] VISUAL: line zooms in; kinks appear one by one; counter climbs to 900**
> **VO:** It isn't straight. It's about 900 separate straight segments, each one slightly off from the last.

**[10–24s] VISUAL: 19th century surveyors, compass, chain**
> **VO:** Why? In the 1800s, surveyors had to turn a treaty line into a real line on the ground. No GPS. A compass, a chain, and astronomy. Over hundreds of miles, small errors add up.

**[24–38s] VISUAL: the zig-zag on a globe vs on the ground**
> **VO:** On a globe, a line of latitude is a perfect circle. On the ground, it's a zig-zag that decides which country a tree is standing in.

**[38–50s] VISUAL: the 20-ft gap**
> **VO:** And because nobody wanted to be confused, both countries cleared a 20-foot strip along the whole thing. So you can see the mistake from space.

**[50–60s] VISUAL: `NOT STRAIGHT` + `LINES ON A MAP`**
> **VO:** A border is not a natural fact. It's a decision someone made with the tools they had.

---

## 18. MEDIUM (M1) — "Why the 49th Parallel Isn't a Straight Line" (9–10 min)

**Structure (9 chapters, no cold-open gimmick):**

| Time | Chapter | Beat |
|---|---|---|
| 0:00 | The claim | "Straight" ka claim + globe par perfect dikhne ka proof |
| 0:45 | What a treaty line is | Latitude = math; border = physical object. Do cheezein alag |
| 2:00 | 1818 | Treaty of 1818, 49th parallel, Lake of the Woods problem `[VERIFY]` |
| 3:30 | The survey (1872–1876) | Compass, chain, astronomy, 900 monuments `[VERIFY]` |
| 5:00 | Error accumulation | 3 reasons: instrument drift, terrain, astronomy limits `[VERIFY]` |
| 6:15 | The 20-foot strip | Clear-cut ka logic aur uski cost |
| 7:15 | Consequences | Northwest Angle, Point Roberts, lake peninsula — 3 mini cases |
| 8:30 | Why it still matters | Map vs ground; current relevance bina politics |
| 9:20 | Sources + next | Description me sources; next video vote |

**Medium ka farq long se:** long me **insani kahani** (Point Roberts ke bachche) emotional core hai; medium me **method** (surveying kaise kaam karta hai) core hai. Same research, **alag sawal**.

---

## 19. Copy-paste metadata (Ep 01 long)

### 19.1 Description

```
The US–Canada border is 5,525 miles long and is usually described as straight.
It isn't. This is the story of the map with a hole in it, the surveyors who
made the line real, and the ~1,000 Americans who live on the wrong side of it.

CHAPTERS
0:00 A line that isn't straight
0:50 The word "straight"
2:40 The 20-foot gap
5:00 1783: the map with a hole in it
8:00 Point Roberts
11:30 The other side of the line
13:30 Why it matters
15:30 What we could not verify
16:40 Next map

SOURCES & NUMBERS  [VERIFY before publish — replace with exact citations]
• Border length, 49th parallel, treaty dates: Treaty of 1818 / Oregon Treaty 1846
• Survey period and monument count: International Boundary Commission records
• Point Roberts population and school situation: local/county sources
• 20-foot cleared strip: International Boundary Commission maintenance policy

CORRECTIONS
If a number in this video is wrong, we'll note it here and pin a comment.
Corrections are not embarrassing. Hiding them is.

This video is about geography and history. It is not about immigration
policy or border enforcement.

#geography #map #bordercrossing
```

### 19.2 Tags (13)

`us canada border, 49th parallel, point roberts, border geography, map animation, geography explained, weird borders, northwest angle, international boundary, cartography, map facts, north america geography, lines on a map`

### 19.3 Pinned comment

```
Every number in this video is in the description with its source. If you find
a mistake, reply here — corrections go in the description, not down the memory hole.

Next map: the lake, the peninsula, or the main street? Vote.
```

### 19.4 Thumbnail brief

- Background: dark blue land/water split (`#1b2a41` / `#276092`), one accent red `#e0473c`.
- Left: zoomed border line with visible kinks, a white 20-ft strip.
- Right: tiny enclave polygon with a pin and text `US`.
- Text: **`NOT STRAIGHT`** (upper-left, heavy sans, 2 lines max).
- No arrows pointing at nothing. No fake red circles. No shocked face.

---

## 20. Editing & animation blueprint

**Style test mojood hai:** `s1_animatic_v20.mp4` (58s, 9:16, 15fps) — ye ek **layout/pace animatic** hai jo sirf teen cheezein lock karta hai: (a) 9:16 me text kahan baithta hai bina UI ke neeche dabne, (b) 4–7s ka cut rhythm, (c) headline vs caption ka size ratio. Isme **na VO hai, na music, na asli geography** — shapes schematic blocks hain, Natural Earth geometry nahi. Yani ye "video" nahi, **graphic system ka test** hai. Jab asli map data aayega, wahi layout us par baithega.

| Element | Spec | Kyun (evidence) |
|---|---|---|
| Aspect | 16:9 long/medium, 9:16 shorts | lane data |
| Shot length | long **6–9s**, short **4–7s** | winners me visual change tez |
| VO pace | long **150–165 wpm**, short **180–210 wpm** | 5 transcripts: short 185–219, long 67 (CGP Grey outlier) |
| Sentence length | **14–18 words** | CGP Grey 14.4 (dense, slow) vs GeoGlobeTales 18.8–21.2 (fast, list-like) |
| Numbers on screen | har number **bada, screen par** likho, VO ke saath sync | winners me title+script number density high (60% title) |
| Camera | orthographic map + slow push-in; 3D sirf 8–10 hero shots me | 2.5D route = 120–200 ghante vs 325–680 |
| Transitions | hard cut; koi zoom-blur/spin nahi | is niche me saaf map style |
| On-screen text | max 4 words per card; top 18% / bottom 20% safe | thumbnail + shorts UI overlap |
| Music | low, 70–85 BPM, no drops | (ye **hamari choice** hai — competitor ke audio ka analysis nahi kiya) |
| SFX | ek "tick" jab number aaye, ek "whoosh" jab map change ho | attention anchors |
| Captions | **burned-in** on shorts (sound-off), YouTube captions on long | 0% outliers me caption flag — par mobile silent viewing ke liye burned-in zaroori |
| Colour | land beige `#d8cbb4`, water `#276092`, accent red `#e0473c`, border white | thumbnail hue analysis + map readability |
| Chapter cards | text-only, 1.2s, no music sting | long-form me 32–42% chapters |

---

## 21. Risks, boundaries, aur jo cheezein galat ho sakti hain

1. **Fact risk (sab se bara).** Ye script ke numbers public captions se aaye reference hain. Treaty dates, 900 monuments, 20-ft strip, Point Roberts ki population — in me se **koi bhi** galat ho sakta hai. Publish se pehle **primary source** se verify karna hai. Report me `[VERIFY]` isi liye laga hai.
2. **Legal / policy risk.** Border enforcement, immigration, indigenous land rights — in par **koi claim nahi**. Script me ye explicitly door kiya gaya hai. Ye **legal advice nahi**, sirf editorial boundary hai.
3. **Copyright.** Koi competitor footage, audio, music, ya frame use nahi. Map data **Natural Earth (public domain)** se aayega. Har asset ka license check karna hai.
4. **"Mass-produced" risk.** Ek hi template se 20 videos = YouTube ki original/authentic content policy ke against ja sakta hai. Is liye har episode me **naya research + naya visual** hoga. (Ye **policy context** hai, legal clearance nahi.)
5. **3D scope risk.** Full 3D = 325–680 ghante (estimate). Pehla episode **2.5D** route par banao; 3D sirf hero shots me.
6. **Sample bias.** Sab lanes `order=viewCount` hain — yani successful videos. Is data se "aisa karo to chalega" nahi, "aisa jeeta hai" kaha ja sakta hai.
7. **Comment bias.** 220 comments, relevance order, max 20 per video. Silent majority invisible. Koi sentiment score nahi.
8. **Caption block.** CI IP 403. 5 transcripts residential se. Yani **script-level evidence 5 videos par** hai, 520 par nahi.

---

## 22. Jo main observe nahi kar saka (aur isay chhupana nahi chahiye)

| Cheez | Status |
|---|---|
| Retention curves / average view duration | **not observed** (private) |
| CTR / impressions | **not observed** (private) |
| Traffic sources (browse vs search vs suggested) | **not observed** (private) |
| Subscriber conversion per video | **not observed** (private) |
| Revenue / RPM | **not observed** (private) |
| Cuts per second, transitions, music cues, colour grade | **not observed** (no video download) |
| 515 of 520 scripts | **not observed** (captions blocked) |
| Competitor thumbnails beyond 20 | **not observed** |
| Audience demographics / age / geography | **not observed** (private) |
| Hindi-market performance vs English for same topic | **partially observed** (language tags + channel country only) |
| Whether any of this causes views | **never claimed** |

**Jo cheez is decision ko badal sakti hai:** agar aap ke paas **apne** channel ka Analytics ho (CTR, retention, traffic source) to woh is poori report se zyada valuable hai — kyunki woh aap ke audience ka asli data hai, aur ye public proxy hai.

---

## 23. Agle 7 din — checklist

| Din | Kaam | Output |
|---|---|---|
| 1 | **Niche confirm** (Map vs Visual Proof Lab) — aap ka faisla | ek line ka decision |
| 1 | Sources list banao (treaty text, IBC, county data) aur har `[VERIFY]` number ko primary source se replace karo | `SOURCES.md` |
| 2 | Ep 01 ka **VO record** (155 wpm target, 1,610 words) | audio + transcript |
| 2 | Shot list review (128 shots, 16 3D hero, 6 sets) | `SHOTLIST_EP01_V20.csv` |
| 3 | Map assets: Natural Earth continent, border polyline, 49th parallel, Point Roberts polygon, Northwest Angle polygon | `.blend` / `.svg` |
| 4 | **S1 (Point Roberts)** ka 2.5D animation — 58s, 12 shots | MP4 |
| 5 | S1 publish-ready package (title/desc/tags/thumb 3 variants) | folder |
| 6 | Ep 01 chapters 1–3 animate | preview |
| 7 | Review: kya 3D add karne se clarity barhi ya sirf time gaya? | decision note |

---

## 24. Faislay jo aap ke hain (mera kaam sirf evidence + plan hai)

1. **Niche**: Map/Geography final hai, ya Visual Proof Lab ke saath A/B karna hai? (V20 ke baad mera evidence-backed jhukav: **Map**, kyunki 520-video corpus me 64.2% ≥1M hai aur demand signal place-led hai — magar ye **tie-breaker evidence** hai, guarantee nahi.)
2. **Series ka naam**: `Lines on a Map` rakhein ya aap ka apna?
3. **Episode 01 subject**: US–Canada border (recommended) ya koi aur place?
4. **3D scope**: Route B (2.5D, 120–200 ghante) se shuru karein, ya Route A (full 3D, 325–680 ghante) — kyunki ye aap ke time/budget ka faisla hai, mera nahi.
5. **Shorts ka order**: S1 (Point Roberts) pehle, ya S2 (20-foot gap) — S2 chhota aur tez hai, S1 zyada emotional.

Main in paanch me se kisi par bhi **aap ke bina** aage nahi barhunga — kyunki inka taluq aap ke time, budget aur creative taste se hai.

---

## 25. Evidence index (sab committed)

| File | Kya hai |
|---|---|
| `research/map_niche_v20/build_map_niche_v20.py` | poora reproducible pipeline (12 lanes → 25 catalogues → thumbs → captions → comments) |
| `api_evidence/run_v20.json` | run summary, quota, boundary |
| `api_evidence/lanes_v20.json` | 12 lanes, exact queries, ids |
| `api_evidence/lane_stats_v20.json` | per-lane stats (table §3) |
| `api_evidence/videos_v20.json` | 520 videos, full metadata |
| `api_evidence/channels_v20.json` | 25 channels, aggregate |
| `api_evidence/channel_deep_v20.json` | catalogues (2,377 videos), ladders, outliers, cross-tab |
| `api_evidence/thumbnails_v20.json` + `thumbnail_aggregates_v20.json` | 20 thumbnails, pixel stats |
| `api_evidence/captions_v20.json` | 12 caption attempts, sab blocked (honest record) |
| `api_evidence/comments_v20.json` | 220 comments, phrase buckets |
| `api_evidence/map_scripts_v20.json` | **5 verbatim transcripts** (public captions) |
| `api_evidence/map_script_metrics_v20.json` | wpm / numbers / structure metrics |
| `api_evidence/google_suggest_v20.json` | autocomplete probes (ordered demand signal) |
| `EPISODE_01_PLAN_V20.json` | machine-readable episode plan (9 chapters, VO blocks, metadata, shorts, medium) |
| `SHOTLIST_EP01_V20.csv` | **128 timed shots** for Ep 01 (in/out, set, camera, 2.5D vs 3D hero, text, SFX) |
| `render_s1_animatic_v20.py` | S1 ka layout/pace test renderer (PIL frames → ffmpeg). Reproducible, no third-party assets |
| `s1_animatic_v20.mp4` | **58s, 9:16, style-test animatic** — composition/pacing/text-size lock (South: schematic shapes, no VO, not final art) |
| `s1_poster.png` · `qa_contact_sheet.png` | animatic ke key frames (poster + 9-scene contact sheet) |
| `thumb_v2_A.png` · `thumb_v2_B.png` | thumbnail layout mocks (A = kink close-up, B = enclave emphasis) |

---

## 26. Ek aakhri baat — jo is report ka sab se ahem nateeja hai

Main ne apne hi khayal ko check kiya, aur wo **ghalat** nikla. Is liye ye section poora honest hai.

**Pehla khayal:** "is niche ke outliers me se zyada tar titles me jagah ka naam hota hai." Main ne title-token check chalaya (`outlier_title_tokens_v20.json`), aur nateeja aaya:

| Signal (20 outliers ke titles me) | Count | Share |
|---|---|---|
| Jagah / desh ka naam | **6** | 30% |
| Koi number | **12** | **60%** |
| Dono me se kam az kam ek | 14 | 70% |

Yani **jagah ka naam 30% me hai, number 60% me**. Mera "13/20 place-name" wala andaza **galat** tha; sahih number **6/20** hai. Isi tarah "7 me number" bhi galat tha — **12** hai.

**Doosra khayal:** "chhote outliers sab US/Europe ke geography channels ke hain." Ye bhi adhoora tha. Asal 20 outliers me **6 Hindi/Indian-exam channels** ke hain (Sunlike study ×4, Geo Study ×3, Professor Of How, War map animation ×3, AlternativeGeopolitics ×2, GrowBig) — yani is niche ke winners me **Hindi market ki hissa dari barhi** hai.

**Teesra (aur ye asli nateeja hai):** outliers me do **bilkul alag genres** hain, aur unhe ek saath dekhna ghalat hai:

| Genre | Kis ne | Kitne outliers | Median views | Format |
|---|---|---|---|---|
| **Map/border explainer** | GeoGlobeTales, Reed Schultz Geo, CGP Grey, Historically, Howtown | 5 channels ka core kaam | 12M–61M (channel median ke hisaab se) | 60–100s, ek contradiction, ek record |
| **Exam-cram animation** | Sunlike study, Geo Study, StudyIQ, OnlyIAS | 6+ (upar wali list me) | 7M–23M | 12–47 min, "class 10 full chapter" |
| **War/battle map** | War map animation, AlternativeGeopolitics, Operations Room | 3+ | 4M–24M | 14–52s, timberlapse |
| **History-short** | Historically, GrowBig, Raj's SnapFusion | 3+ | 1M–28M | 45–90s, "what if" |

Iska matlab: **"map/geography" ek niche nahi, teen markets hain** — (a) US/English map explainer, (b) Indian exam cram, (c) war map timelapse. Hamara target sirf **(a)** hai. Ye tafseel is liye zaroori hai ke koi ye na samjhe ke "Sunlike study ka 23M pakad kar hum wahi bana lein" — wo **alag audience, alag zubaan, alag monetisation** hai.

**Aur asli production rule jo bacha:** winners me sab se repeatable cheez **ek measurable claim** hai (60% titles me number, aur 5 verbatim scripts me 4–20 numbers per 100 words) — **jagah ka naam optional hai, number optional nahi**. Ek video "Spain" par nahi chalti; wo **"85 metres"** par chalti hai, jise Spain ke ek chhote se rock par dikhaya gaya ho.

Is liye hamara rule ye hai: **pehle wo number dhoondo jo screen par ajeeb lage (85 m, 20 ft, 900 kinks, 5,525 miles). Phir us number ke peeche ki jagah dhoondo. Phir likho.**
