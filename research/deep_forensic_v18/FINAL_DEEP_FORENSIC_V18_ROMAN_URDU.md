# FINAL DEEP FORENSIC V18.1 — Roman Urdu (10x / microscope)

**Report ID:** `FINAL_DEEP_FORENSIC_V18_ROMAN_URDU`
**Data run:** GitHub Actions `43249117208` — **SUCCESS 5m37s**, “V18 HARD QC PASS (raw dump matches in-memory corpus)”
**API evidence timestamp:** `2026-11-12T15:39:12Z`
**Repo:** `adil-chandio/Monarch.Overall.Work`, branch `arena/2b012328-monarch-overall-work`
**Ye report kis cheez ki jagah hai:** `DEEP_FORENSIC_V18.md` (auto-generated Actions appendix) aur `EVIDENCE_TABLES_V18.md` (machine tables) ki jagah **yehi final user-facing Roman Urdu report** hai. Wo dono reh gaye hain as raw appendix.

---

## 1. SAB SE PEHLE: status, boundary aur aap ka faisla

### 1.1 Aap ka faisla abhi **NAHI** hua

Aap ne saaf kaha tha: **"pehle ham Kya karenge abhi decide NAHI hua"**. Is liye:

- Ye report **koi final niche announce nahi** kar rahi.
- `VISUAL PROOF LAB` sirf **provisional recommendation / tajweez** hai — **APPROVED NAHI**.
- V17 ka `NAQSHA FILES / Map Forensics` bhi **approved/decided nahi**; wo is report me sirf **ranked alternative #2** hai.
- V16 `caught-on-camera` **set aside** hai (V15 me owner ne V14 clip reuse reject kiya tha; wo raasta band hai).
- Aage kuch bhi produce/upload karne se pehle **aap ka A / B / C** faisla chahiye — Section 21.

### 1.2 Is report ne kya **nahi** kiya (aur kyun)

| Cheez | Status | Wajah / proof |
|---|---|---|
| Competitor video/audio download | **nahi kiya** | sirf public Data API metadata + public thumbnails |
| Video frames dekhe / cuts-per-second naape | **nahi** | 40/40 `deep_teardowns_v18.json` me `editing_observation.status = not_observed` |
| Competitor ka verbatim spoken script / transcript | **nahi** | public caption attempts **12/12 error** (bot-check), **0 usable transcript words** |
| Private retention / CTR / RPM / revenue / demographics | **nahi** | YouTube Data API public fields me nahi hote |
| Verified subscriber-growth ranking | **nahi** | sirf public proxies (cumulative views ÷ channel age) |
| Causal claim (“ye cheez ne views diye”) | **nahi** | viewCount + metadata co-occurrence hai, experiment nahi |
| Legal clearance / human approval / creative sign-off | **nahi** | ye research + production draft hai |
| Upload / publish / schedule | **nahi** | koi connected app upload nahi hua |
| Monetisation outcome / guaranteed views / virality / perfection | **nahi claim** | boundary |

**Ye boundary kamzori nahi — ye is report ki honesty hai.** Jo cheez public API se observe nahi hoti, usay hum **“not observed”** likhte hain, apni pasand se bhar nahi dete. Isi liye neeche har section me teen cheezein alag likhi hain: **(a) kya observe hua, (b) iska matlab, (c) kya nahi keh sakte.**

### 1.3 Aaj ka corpus ek line me

**24 lanes · 1,122 lane rows · 2,347 unique public videos · 804 channels · 726 million-view videos · 240 ten-million videos · 717 title-safe candidates · 40 deep teardowns · 23 comment-mined videos (575 comments) · 40 thumbnails · 12 transcript attempts (0 pass) · ~2,549 quota units.**

---

## 2. Executive summary — 12 findings jo sach me maayne rakhte hain

1. **Short lane hi sab se zyada high-view-conditioned evidence rakhta hai.** 717 candidates me short bucket (n=348) ka median **9,876,994** views hai; medium (n=184) **3,155,452**; long (n=185) **2,540,517**. Ye 3.9× aur 3.9× ka farq hai — lekin ye `order=viewCount` se aaye hue top-50 samples hain, is liye **expected performance nahi, selection-conditioned signal** hai.
2. **Short me sab se upar science-visual-test aur satisfying-restoration lanes hain.** `science_explainer_short_all`: median **49.79M**, **50/50 videos ≥10M**, median duration **55s**. `satisfying_restoration_short_all`: median **22.92M**, **45/50 ≥10M**, **57s**.
3. **Medium aur long me bhi wahi do themes sab se upar hain**, lekin kam median par: medium satisfying **3.64M** (828s) / science **3.11M** (627s); long satisfying **3.56M** (2084s) / science **1.05M** (2810s). Yani **same theme teeno formats me survive karta hai**, sirf payoff ka density badalta hai.
4. **Duration curve non-linear hai.** Short ke andar: 0–15s median **23.10M**, 15–30s **6.36M**, 30–45s **9.13M**, **45–60s 25.95M (n=83)**, 60–120s **5.46M**, 120–240s **3.89M**. Medium 780–960s ka median **5.97M** hai jabke 420–600s ka **2.37M** — yani duration akela predictor nahi, **theme × payoff density** maayne rakhti hai.
5. **Hook type me short ka “statement” aur “belief challenge” sab se aage hain** (statement n=216 median **11.74M**; belief-challenge n=53 median **12.16M**), jabke “number” hook short me kamzor (n=29, **3.30M**). Long me ulta: number hook sab se zyada common (n=89) lekin median sirf **2.27M**. **Hook ka best type format ke saath badalta hai.**
6. **Chapters sirf long me normal hain** (long chapter≥3 rate **22.7%**, medium **9.8%**, short **0.6%**). Short me chapters daalna data ke against hai; long me daalna normal hai. Lekin chapter presence ka median-views se clean rishta nahi (long: ch≥3 **2.73M** vs ch<3 **2.53M** — practically flat).
7. **Tags ka counter-intuitive result:** zero-tag videos ka median **10.81M** (n=195) vs tags-wale **~3–5M**. Iska matlab “tags se views aate hain” **nahi**; bade creators bina tags ke bhi jeet rahe hain. Tags **discovery metadata** hain, **ranking lever nahi**.
8. **Description length par bhi ulta pattern:** 0-word descriptions ka median **22.92M** (n=87), 151+ words ka **3.62M** (n=240). Short me chhoti description normal hai (median 44 words), long me lambi (146 words) — lekin **lambi description views nahi laati**.
9. **Audience ka sab se repeatable sawal “sequel / next part” hai** (fetched comments me 9 hits; per-video 12% tak `qR7vPGcP_ko` me), uske baad **cost objection** (3 hits, `xZco3o0HLZc` me 8%) aur **“kaam nahi kiya”** (2 hits). Yani audience **agla test** maangti hai, theory nahi.
10. **Naye channels ka public proxy strong hai map aur microdrama me, lekin microdrama ki quality signal kamzor hai.** `map_geo_short_all` me **17** newer-channel ≥1M rows; `microdrama_medium_all` me **16** (magar 14 sirf Story TV se, aur microdrama long median **191k** — yani ek channel ka outlier, lane ki health nahi).
11. **Public transcripts ka raasta band hai.** 12/12 bot-check error, V17 fallback me 18/18 blocked. Is liye **koi competitor script, joke timing, VO cadence ya exact wording** is report me nahi hai — aur nahi honi chahiye.
12. **Is liye sab se honest tajweez:** ek **short-first, original, safe, falsifiable visual-test format** — jismein har episode ka apna sawal, apna failure aur apna mechanism ho. Iska naam `VISUAL PROOF LAB` rakha gaya hai. **Ye approved nahi**, sirf evidence-backed recommendation hai.

---

## 3. Method — asal me kya chalaya gaya (reproducible)

### 3.1 Run receipt

| Field | Value |
|---|---|
| Workflow | `.github/workflows/yt-deep-forensic-v18.yml` (trigger marker `v18-deep-trigger.txt`) |
| Run | `43249117208` — **success, 5m37s**, all steps ✓ |
| Evidence commit | `e5242c4` (auto-commit, `[skip ci]`) |
| API key | `key_present: true`, `secret_value_printed_or_stored: false` (masked) |
| Generated | `2026-11-12T15:39:12Z` |
| Quota | ~**2,549** units: `search 24 · videos 63 · channels 17 · playlistItems 45 · commentThreads 23 · videoCategories 1` |
| HARD QC | raw dump `2347` = in-memory `2347` = manifest `2347`; description IDs missing **0**; teardown IDs missing **0**; candidate IDs missing **0** |

### 3.2 24 lanes ka design

Har theme ke **teen duration buckets** (`videoDuration=short|medium|long`) + ek **recent lane** (`order=date`, `publishedAfter=365d`):

| Theme | Query | Recent lane |
|---|---|---|
| Map / geography explainer | `map animation geography explained` | ✅ |
| Science explainer / humor | `science experiment explained funny` | ✅ |
| Oddly satisfying / restoration | `oddly satisfying restoration` | ✅ |
| Animal rescue | `animal rescue caught on camera` | ✅ |
| Viral breakdown / analysis | `viral video breakdown analysis` | ✅ |
| Microdrama / vertical series | `microdrama short series` | ✅ |

Common parameters: `regionCode=US`, `relevanceLanguage=en`, `safeSearch=moderate`, `maxResults=50`, `type=video`.

### 3.3 Sample ka asli nature — ye sab se important caveat hai

- **All-time lanes `order=viewCount` hain.** Yani hum ne **sab se zyada views wale 50** uthaye, random sample nahi. Is liye lane ka “median” **high-view-conditioned median** hai. 717 candidates ka median 4.33M hona is baat ka saboot hai ke ye sample **selection-biased** hai, channel ki aam performance nahi.
- **Recent lanes `order=date` hain** — yani **freshness-conditioned**, growth ranking nahi. Isi liye `microdrama_recent` ka median sirf **1,011** views hai (naye videos, abhi views nahi) aur `fresh_30d_share` **0.979**.
- **Har lane max 50 rows**, is liye chhote farq (jaise 3.1M vs 3.6M) ko “winner” kehna galat hoga. Sirf **bade, repeated** farq par bharosa kiya gaya.
- **Search-based sampling** ka matlab: jo videos search me nahi aaye wo corpus me nahi. Ye **YouTube ki poori niche** nahi, **ek query ke top results** hain.

### 3.4 Derived corpus aur integrity

- `video_details_v18.json`: **2,347** videos (V18.1 ne recent-upload resolution ke baad poora resolved corpus dobara save kiya — yehi V18 ki integrity bug ka fix tha).
- `analysis_manifest_v18.json`: in-memory corpus, raw dump, derived count — teeno match.
- `description_forensics_v18.json`: **717** (title-safe million-view candidates, `snippet.description` max **6,000 chars** tak).
- `deep_teardowns_v18.json`: **40**; `comments_v18.json`: **23 ok / 1 error / 16 not_requested**; `thumbnail_forensics_v18.json`: **40**; `transcript_teardowns`: **12, sab error**.
- 717 candidates me se: `category_id` 22 (People & Blogs) 390, 24 (Entertainment) 311, 27 (Education) 243, 28 (Science & Tech) 107, 10 (Music) 102, 1 (Film) 63.
- `default_language`: `en 1028 + en-US 162` short lane me; medium `en 410`; long `en 352 + en-IN 55`. Yani corpus **English-heavy** hai — Roman Urdu audience ke liye direct mapping nahi, sirf **format/pattern** ka signal.
- `made_for_kids`: sirf **63/2347**; candidates me **0**. Yani ye corpus **kids content nahi** — family-safe claim bhi nahi.
- `dimension/projection`: raw dump me **sab `2d / rectangular`** store hua, jabke actual short videos vertical hote hain. **Ye API field ka artifact hai, video ka asli aspect nahi.** Is liye is report me “9:16 vs 16:9” ka claim **data se nahi**, hamari production choice se hai. (V18.1 ne isay invent nahi kiya — hum ne ise explicitly likh diya.)

---

## 4. Lane-by-lane deep read — 24 lanes, poora table

`med` = median views, `m1` = videos ≥1M, `m10` = ≥10M, `dur` = median seconds, `like`/`com` = median like/comment rate, `top3` = top-3 videos ka share of lane views, `win` = max ÷ median, `fresh` = last 30 din ka share, `vpd` = median views/day.

| Lane | n | med | total | m1 | m10 | dur | like | com | vpd | top3 | win | fresh |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| map_geo_short_all | 50 | 6,629,829 | 518.88M | 48 | 14 | 59 | .02598 | .00019 | 9,163 | .220 | 7.0 | 0 |
| map_geo_medium_all | 50 | 1,739,746 | 457.51M | 39 | 6 | 537 | .01213 | .00039 | 1,427 | .605 | 94.0 | 0 |
| map_geo_long_all | 50 | 1,520,173 | 131.08M | 32 | 2 | 3962 | .02402 | .00108 | 2,064 | .260 | 10.1 | 0 |
| science_explainer_short_all | 50 | 49,787,595 | 4.19B | 50 | 50 | 55 | .01917 | .00008 | 88,858 | .362 | 19.0 | 0 |
| science_explainer_medium_all | 50 | 3,112,668 | 451.73M | 37 | 16 | 627 | .00415 | .00006 | 2,089 | .285 | 18.6 | 0 |
| science_explainer_long_all | 42 | 1,049,704 | 381.79M | 21 | 7 | 2810 | .00241 | .00003 | 1,040 | .657 | 160.7 | .095 |
| satisfying_restoration_short_all | 50 | 22,923,251 | 2.31B | 49 | 45 | 57 | .02065 | .00005 | 35,735 | .346 | 14.4 | .02 |
| satisfying_restoration_medium_all | 50 | 3,636,834 | 516.99M | 50 | 14 | 828 | .00828 | .00029 | 4,585 | .333 | 21.9 | 0 |
| satisfying_restoration_long_all | 50 | 3,555,890 | 310.34M | 50 | 4 | 2084 | .01049 | .00038 | 3,810 | .447 | 24.0 | 0 |
| animal_rescue_short_all | 50 | 7,480,717 | 1.01B | 49 | 19 | 41 | .00822 | .00015 | 13,992 | .459 | 30.6 | .02 |
| animal_rescue_medium_all | 50 | 73,655 | 207.43M | 16 | 6 | 478 | .01403 | .00063 | 115 | .508 | 581.2 | 0 |
| animal_rescue_long_all | 50 | 330,642 | 162.54M | 16 | 6 | 1879 | .00877 | .00031 | 615 | .531 | 120.2 | .04 |
| viral_breakdown_short_all | 25 | 74,189 | 4.96M | 1 | 0 | 51 | .01960 | .00048 | 262 | .540 | 14.7 | .174 |
| viral_breakdown_medium_all | 50 | 42,332 | 11.71M | 2 | 0 | 593 | .02808 | .00203 | 147 | .568 | 70.8 | .14 |
| viral_breakdown_long_all | 33 | 1,695 | 3.95M | 0 | 0 | 1543 | .03283 | .00107 | 8.6 | .592 | 505.4 | .062 |
| microdrama_short_all | 50 | 463,280 | 60.28M | 13 | 1 | 105 | .01264 | .00008 | 9,645 | .517 | 40.2 | .32 |
| microdrama_medium_all | 50 | 592,224 | 50.48M | 16 | 0 | 527 | .00000* | .00005 | 2,783 | .231 | 8.1 | 0 |
| microdrama_long_all | 50 | 190,957 | 40.41M | 8 | 1 | 3695 | .00862 | .00018 | 2,925 | .546 | 61.8 | .26 |
| map_geo_recent | 50 | 35,302 | 11.27M | 3 | 0 | 78 | .01188 | .00061 | 1,745 | .658 | 118.2 | .489 |
| science_explainer_recent | 50 | 1,436 | 373.97M | 18 | 13 | 55 | .01523 | .00008 | 174 | .475 | 78,309.8 | .04 |
| satisfying_restoration_recent | 50 | 924 | 9.07M | 2 | 0 | 14 | .00589 | 0 | 1,122 | .990 | 6,662.6 | .949 |
| animal_rescue_recent | 50 | 6,663 | 11.29M | 4 | 0 | 84 | .00860 | 0 | 439 | .697 | 673.1 | .652 |
| viral_breakdown_recent | 22 | 99,855 | 4.12M | 0 | 0 | 678 | .02985 | .00209 | 942 | .470 | 8.0 | .20 |
| microdrama_recent | 50 | 1,011 | 1.60M | 1 | 0 | 70 | .01422 | 0 | 80 | .881 | 1,316.5 | .979 |

\* `microdrama_medium_all` ka like-rate median `0.0` — kyunki us lane ke bahut se rows me `likeCount` disabled/zero hai. Ye “like nazarandaz karte hain” ka proof nahi, **data limitation** hai.

### 4.1 Har theme ka microscope

**A) Science explainer / humour — sab se strong short signal**
- Short: median 49.79M, **50/50 ≥10M**, 55s, like .01917, `top3_share .362`, winner ratio 19×.
- Top 3: `-xasdJzBVpo` Vlad and Niki “Kids are making a volcano” **947M** (60s); `jfUU24gaqNg` Mark Rober “3 Levels of Elephant Toothpaste” **366M** (36s); `5PTL5N5c4jc` “Square Bubble” **203M** (11s).
- Medium: 3.11M / 627s / 16 videos ≥10M. Long: 1.05M / 2810s / 7 ≥10M / **top3 .657** — yani long me ek do video poora lane kheench rahe hain (`pFeanxO4-E8` 168M, `IXqBm15EZYA` 42.8M, `_ZizKQqHNgI` 39.2M).
- Recent lane me: total **373.97M** but median **1,436** — kyunki 18 ≥1M rows (13 ≥10M) hain aur baaki naye hain. Winner `hDleig-iA_g` **112.49M** (“New Dhanda Khol Le?” — Science and fun, **61s** Hindi science experiment). Yani **naya science-short abhi bhi 100M+ kar raha hai**, lekin distribution **extreme** hai (`winner_ratio 78,309`).
- **Reading:** short science = “ek visual, ek sawal, ek payoff, 11–60s”. **Lekin** science ke andar chemical stunts (elephant toothpaste) safety-wise risky hain; is liye hamara pilot **mechanical** (kaagaz + weight) hai, chemical nahi.

**B) Satisfying / restoration — sab se consistent**
- Short 22.92M / 57s / 45 ≥10M; Medium 3.64M / 828s / 14; Long 3.56M / 2084s / 4. **Teeno buckets me ≥22M/3.5M/3.5M** — yani theme **format-agnostic** hai.
- Lekin: is lane ke top hits **farrier hoof, cosmetic repair, hot metal balls** hain — yani **kisi aur ka kaam, kisi aur ki craft**. Aap ke paas ye craft/asset nahi hai. Copy karna na ethical hai na feasible.
- Recent lane me median **924** (`fresh_30d .949`) — yani naye satisfying shorts **bina traction** ke bhi bahut hain. Ye lane **zero-sum saturated** lagti hai.
- **Reading:** theme strong hai, lekin **entry barrier = asli craft/skill**, aur saturation high. Hamare liye ye **#3 ranked option** hai, #1 nahi.

**C) Map / geography — sab se strong newer-channel signal (V17 ka base)**
- Short 6.63M / 59s / 14 ≥10M / **top3 .220** (yani views top-3 me nahi thuse — distribution healthy); Medium 1.74M / 537s / 6, magar **top3 .605** (ek video 94× median — `B1J6Ou4q8vE` 163M); Long 1.52M / 3962s / 2.
- Recent: median 35.3k, **top3 .658**, fresh .489, **3 videos ≥1M**, winner 4.17M (`J_sNJjrN4J4` El Niño). Yani **naya map short abhi bhi 1–4M kar raha hai** — realistic, na 100M ka sapna, na zero.
- Newer-channel ≥1M rows: **17** (GeoGlobeTales 4, Geo All Day 2, Mini Maps, Howtown, Aaj_Ki_Research...). Ye **sab se zyada** hai kisi bhi lane me.
- Top video: `HKdjIFjYZ40` “Why do Rivers Curve?” **46.29M** (17s, channel “MinuteMinis”). Dhyan dein: **17s me poora concept** — is liye hamara **56s** target isi lane ke median 59s ke qareeb hai.
- **Ek ahem caveat:** “Why do Rivers Curve?” originally **MinuteEarth** ka ~2:38 explainer hai (`8a3r-cG8Wic`), jiska public transcript PSU/ESLvideo par milta hai. Jo 17s version corpus me hai wo **alag channel (MinuteMinis)** ka **short re-cut** lagta hai. Yani map lane ke top hit me **re-upload / re-cut** ka pattern bhi maujood hai. Hum aisa nahi karenge: map lane choose karne par **original animation + original research**, kisi ka re-cut nahi.
- **Reading:** map = **knowledge + visual + newer channels ke liye realistic ceiling**. V17 ne isi ko `NAQSHA FILES` bola tha; wo **approved nahi**, lekin evidence **strong** hai.

**D) Animal rescue — emotional, lekin sensitive aur inconsistent**
- Short 7.48M / 41s / 19 ≥10M / top3 .459. Medium **73.7k** / 478s (yani medium me log rescue nahi dekhte). Long 330.6k / 1879s, top3 .531.
- Recent: median 6,663, 4 ≥1M, fresh .652.
- **Reading:** sirf short me chalta hai, aur **animal distress / reupload / rights** ke masle hain. Owner ne V15–V16 me already is raaste ko chhoda. **#4 ranked, sensitive.**

**E) Microdrama — high volume, low quality signal**
- Short 463k / 105s / 13 ≥1M (magar 1 ≥10M); Medium 592k / 527s / **0 ≥10M**; Long 191k / 3695s / 1.
- Newer rows: 16 in medium — **lekin 14 sirf Story TV**; Story TV ke 743 videos me 16 hits, recent median **21,012** — yani **volume game**, consistent hit nahi.
- Recent median **1,011**, fresh .979.
- **Reading:** ye **factory model** hai (casting, writers, daily episodes). Ek banda/ek studio ke liye **sab se mehnga aur sab se risky**. **#5.**

**F) Viral breakdown / analysis — meta-trap**
- Short 74k (1 ≥1M), Medium 42k (2 ≥1M), Long **1,695** median, **0 ≥1M**.
- Yani “viral videos par video banane wale” khud viral nahi ho rahe. `dIKsEhX-vyU` “Why every Johnny Harris video goes viral” sirf **859k**; `Xqy9L-88wcw` “I Studied 1,000 Hooks” **856k**.
- **Reading:** is lane ko **content niche** ke tor par choose karna evidence ke khilaf hai. Hum isay sirf **research method** ke tor par use kar sakte hain. **#6, not recommended.**

---

## 5. Distribution microscope — 717 candidates ka asli shape

### 5.1 Quantiles (717 title-safe million-view candidates)

| Percentile | Views |
|---|---|
| min | 1,001,572 |
| p10 | 1,267,992 |
| p25 | 1,880,921 |
| **p50** | **4,332,245** |
| p75 | 16,315,859 |
| p90 | 44,142,276 |
| p99 | 237,767,723 |
| max | 947,286,603 |

**Total views:** 14.97B. **Top 1% (7 videos) = 21.1% of all views. Top 10% (72 videos) = 64.1% of all views.**

**Iska matlab:** “million views” corpus bhi **power-law** hai. Median 4.3M ka matlab ye **nahi** ke aam video 4.3M karti hai — matlab ye ke **is filtered sample** ka beech ka video 4.3M par hai. Aap ka pehla video 4.3M karega, iska koi guarantee nahi.

### 5.2 Bucket-wise quantiles

| Bucket | n | p25 | p50 | p75 | p90 | max |
|---|---|---|---|---|---|---|
| short | 348 | 2,954,465 | 9,917,133 | 33,364,144 | 73,891,631 | 947,286,603 |
| medium | 184 | 1,809,114 | 3,159,463 | 9,877,963 | 30,490,192 | 163,566,319 |
| long | 185 | 1,599,030 | 2,540,517 | 5,010,416 | 11,066,186 | 168,635,831 |

**Reading:** short ka p90 (73.9M) medium ke max (163.6M) se kam hai, lekin medium ka p90 (30.5M) short ke p75 (33.4M) se kam. Yani **short ka “aam top” medium ke “best” se bhi upar** hai is sample me. Lekin p25 me farq kam (2.95M vs 1.81M) — yani **short ki lower half bhi utni hi kamzor hai**. Short ka fayda **upper tail** me hai, guarantee me nahi.

### 5.3 Duration sub-buckets (n aur median)

| Duration | n | Median views |
|---|---|---|
| short 0–15s | 34 | **23,102,284** |
| short 15–30s | 41 | 6,357,526 |
| short 30–45s | 35 | 9,134,884 |
| **short 45–60s** | **83** | **25,946,818** |
| short 60–120s | 92 | 5,459,518 |
| short 120–240s | 63 | 3,885,438 |
| med 240–420s | 53 | 3,131,842 |
| med 420–600s | 36 | 2,366,629 |
| med 600–780s | 34 | 3,017,375 |
| med 780–960s | 29 | 5,971,508 |
| med 960–1201s | 32 | 3,222,291 |
| long 1200–1800s | 47 | 2,467,090 |
| long 1800–2400s | 33 | 3,809,040 |
| long 2400–3600s | 27 | 1,873,214 |
| long 3600s+ | 78 | 2,402,878 |

**Teen observations:**
1. **0–15s aur 45–60s do spikes hain.** 0–15s me mostly single-gag/satisfying clips (12s chestnut, 11s bubble, 10s kitten). 45–60s me “ek chhota test + payoff” wale clips. Hamara **56s** target isi 45–60s bucket me padta hai — **n=83, sab se bada short sub-bucket**.
2. **60–120s me drop** (5.46M) — yani “short” ka label lagane ke baad bhi 1–2 minute me retention pressure aata hai. Short ko 56s par rakhna data ke saath consistent hai.
3. **Long 3600s+ (1 hour+) ka median 2.40M** hai, jo 1200–1800s se **behtar** hai — yani long me “compilation / 1-hour” format zinda hai. Lekin wo **volume + library** ka game hai, single original episode ka nahi. Hamara 28 min long **1200–1800s bucket** me padta hai (median 2.47M).

### 5.4 Hook type × bucket

| Hook | Global n / median | Short n / median | Medium n / median | Long n / median |
|---|---|---|---|---|
| statement | 377 / 5,267,356 | 216 / **11,742,251** | 102 / 3,102,895 | 59 / 2,479,425 |
| belief_challenge | 89 / 5,593,687 | 53 / **12,161,023** | 19 / 2,999,217 | 17 / 3,434,570 |
| list | 48 / 4,927,435 | 17 / **18,209,048** | 14 / 2,786,608 | 17 / 3,938,021 |
| question | 42 / 5,108,424 | 30 / 6,125,426 | 10 / **9,999,250** | 2 / 2,213,913 |
| number | 157 / 2,824,826 | 29 / 3,302,376 | 39 / 3,389,374 | 89 / 2,269,079 |
| comparison | 4 / 3,579,763 | 3 / 5,108,016 | — | 1 / 1,059,724 |

**Reading:** short me **statement / belief-challenge / list** sab 11–18M par hain; **number hook short me sab se kamzor**. Medium me **question** sab se upar (10.0M, lekin n=10 — chhota sample). Long me **number** sab se common (89) magar median sab se kam — yani long me numbers **common** hain, **differentiating nahi**.

Hamara pilot hook: **"Kya kaagaz ek kilo utha sakta hai?"** = question + implicit belief-challenge. Question short me 6.1M (n=30) par hai, belief-challenge 12.2M par. Is liye script me **question + prediction + statement payoff** mix rakha gaya hai — sirf question par nahi.

### 5.5 Chapters

| Bucket | ch=0 | ch≥3 rate |
|---|---|---|
| short | 346/348 | **0.6%** |
| medium | 166/184 | 9.8% |
| long | 143/185 | **22.7%** |

Global ch≥3: **62/717 = 8.6%**. Chapter presence ka median par asar: global ch≥3 **3.07M** vs ch0 **4.52M**; medium me **5.05M vs 3.13M** (chapters wale behtar); long me **2.73M vs 2.53M** (flat). Yani chapters **medium me** thoda positive, **short me bekaar**, long me **neutral-but-normal**.

### 5.6 Tags

| Bucket | median tags | zero-tag rate | zero-tag median | has-tag median |
|---|---|---|---|---|
| short | 7 | **40.2%** | **16,724,278** | 7,097,987 |
| medium | 17 | 13.0% | 3,405,198 | 3,141,641 |
| long | 15 | 16.8% | 1,599,030 | 2,950,418 |

Global median **13 tags**, zero-tag **27.2%**, zero-tag median **10,813,309** vs 1–5 tags **2,705,192**, 6–15 **5,105,024**, 16+ **3,852,646**.

**Counter-evidence examples:** `jfUU24gaqNg` (366.7M), `ZuA1yaHDB_A` (331.1M), `GpRLQ-QizQQ` (239.1M), `B1J6Ou4q8vE` (163.6M) — **sab ke 0 tags**. Is liye tags ko **“zaroori” ya “views ka cause”** kehna galat hoga. Hamare tags **relevance + spelling variants** ke liye hain, ranking ke liye nahi.

### 5.7 Description length

| Desc words | n | Median views |
|---|---|---|
| 0 | 87 | **22,917,770** |
| 1–25 | 90 | 12,039,388 |
| 26–75 | 142 | 3,939,674 |
| 76–150 | 158 | 3,224,087 |
| 151+ | 240 | 3,615,182 |

**Reading:** short-form hits ki description **khaali ya 16 words** hoti hai (JayFindsThings ke saare 16 words: “#shorts All of my finds are linked in my bio and in the video for you!”). **Lambi description = bada channel** ka pattern hai (long bucket median 146 words, 3 numbers, links 122), **views ka cause nahi**. Hamari description **format ke hisaab se** hogi: short ~60, medium ~100, long ~130 words — **jitna kaam ka hai, utna**.

### 5.8 Engagement rates

Global median like **.01155**, comment **.00016**. Bucket: short like **.01784** / comment **.00012**; medium **.00734 / .00020**; long **.00840 / .00025**.

**Reading:** short me **like zyada, comment kam** (fast swipe, low friction). Long me **comment zyada** (investment). Is liye short par “comment army” build karna mushkil hai; **pinned vote** hi sab se realistic CTA hai.

### 5.9 mostPopular (4 regions) — kyun ye niche verdict nahi

| Region | #1 | #2 | #3 |
|---|---|---|---|
| US | `fA8-gXDoAk8` Salman Khan trailer 37.5M / 275s | `_yl5ELcmugI` GTA VI Pre-Load 10.4M / 30s | `8L0CzL2V72c` GTA VI features 5.4M / 49s |
| PK | `BPZkZpGMpXA` T-Series “KING” 76.0M / 223s | `EgXkduRe9ZU` Badshah “Mahiya” 68.95M / 155s | `nCa4BGy3MJ8` “Eetha” trailer 44.1M / 183s |
| GB | `fA8-gXDoAk8` 37.5M | `_yl5ELcmugI` 10.4M | `uwL2o2GnCrg` Gunmaaster G9 trailer 5.98M |
| IN | `fA8-gXDoAk8` 37.5M | `dB_4TiBSLFk` GTA 5 LIVE 10.5M / 3859s | `yTSDTmdLb0k` Himesh music 8.82M |

**Reading:** chaaron regions me **music, trailers, gaming livestreams** top par hain. Yani “aaj kya trending hai” ka jawab **films/music/GTA** hai — **hamari 6 lanes ka koi lane nahi**. Isi liye `mostPopular` ko **niche verdict** banana galat hoga; ye sirf **platform-wide attention** dikhata hai. Ye 20 rows 40 deep teardowns me se **7** me overlap karte hain (trailer/music/gaming IDs), baaki 6 selected nahi hue — kyunki unka niche relevance kam tha.

**Ek aur note:** `fA8-gXDoAk8` **chaar regions me #1** hai — yani ek hi video multiple regions me top par ho sakta hai. Iska matlab regional lists **independent nahi** hain, aur unse “Pakistan me kya chalta hai” ka clean signal nahi milta.

---

## 6. Title forensics — 717 titles

### 6.1 Length aur pattern rates

| Bucket | Med chars | Med words | number | question | hashtag | ellipsis | vs | how_to | worlds | levels | part/ep | superlative | “shorts” | emoji |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| short | 64 | 9 | .195 | .106 | **.503** | .034 | .034 | .040 | .014 | .003 | .014 | .072 | .181 | **.328** |
| medium | 56 | 8 | .304 | .033 | .060 | .016 | .011 | .005 | .022 | 0 | .016 | .120 | 0 | .043 |
| long | 66 | 9 | **.551** | .027 | .286 | .011 | .011 | .022 | 0 | 0 | .027 | .124 | .076 | .184 |

Global: number **226/717 = 31.5%**, question mark **48 = 6.7%**, hashtag **239 = 33.3%**, emoji **156 = 21.8%**, superlative **70 = 9.8%**.

### 6.2 Top title tokens

Global: `science 130 · asmr 115 · satisfying 110 · geography 107 · restoration 72 · experiment 71 · experiments 49 · funny 38 · granny 38 · makeup 37 · live 35 · ashusir 34 · rescue 34 · map 34 · full 33 · caught 33 · repair 32 · camera 31 · india 30 · kids 29`.

Short: `asmr 74 · science 65 · experiment 61 · satisfying 45 · geography 38 · funny 36 · ashusir 34 · scienceandfun 29 · oddlysatisfying 25 · map 25 · rescue 24 · restoration 22`.
Medium: `science 41 · geography 33 · restoration 32 · experiments 31 · satisfying 26 · asmr 22 · hoof 21 · drama 16 · song 15 · micro 14 · story 14 · farrier 13`.
Long: `satisfying 39 · granny 38 · geography 36 · live 35 · makeup 29 · science 24 · repair 24 · gta 23 · gta5 21 · gtav 21 · gaming 21 · asmr 19`.

### 6.3 Title shape observations (co-occurrence, causal nahi)

- **Short titles hashtag-heavy aur emoji-heavy** (.503 / .328) — kyunki Shorts feed me hashtag/emoji thumbnail-style kaam karte hain; medium me ye almost gayab (.060 / .043).
- **Long titles number-heavy** (.551) — “40 Science Experiments”, “Level 1 to 100”, “50 States”, “1871 Candy Drop Roller”. Long me numbers **topic + scope** batate hain.
- **`World's` sirf 6/717 (~0.8%)** — yani “World's biggest/softest” pattern **kam** hai, bhale hi usme se ek 279M kar gaya. Isay formula samajhna galat hoga.
- **`Levels` 0.4%** — sirf Mark Rober type. Copy na karein.
- **Question mark short me 10.6%** — common, magar **median par bara faida nahi** (question hook short median 6.13M vs statement 11.74M). Yani question **click** ke liye kaam karta hai, **retention** ka proof nahi.

### 6.4 Hamare titles ka design rule (evidence se, copy se nahi)

1. **Format ke hisaab se**: short me 1 hashtag + 1 emoji max, 8–10 words, 60–65 chars; medium me saaf 8 words, koi hashtag nahi; long me number + scope + “full/poora”.
2. **Measurable specificity**: `1 Kilo`, `3 Designs`, `5 Tests` — yani number **sach** ho aur video me **dikhe**.
3. **Koi superlative jhoot nahi**: `World's`, `Best`, `100%`, `Guaranteed` avoid — kyunki (a) claim verify nahi hota, (b) official policy misleading metadata se bachne ko kehti hai.
4. **Koi competitor title copy nahi**: `3 Levels of Elephant Toothpaste` ka **structure idea** (number + levels) hai, **words nahi**.

---

## 7. Description, chapters aur CTA — 717 descriptions

### 7.1 Core numbers

| Metric | Global | Short | Medium | Long |
|---|---|---|---|---|
| Median words | 91 | 44 | 112 | 146 |
| Median numbers | 0 | 0 | 1 | 3 |
| Median hashtags | 3 | 1 | 3 | 3 |
| Median URLs | 0 | 0 | 3 | 3 |
| Emoji present | 41.8% | 38.2% | 37.0% | — |
| Script-like synopsis | **42.8%** | 29.0% | 46.7% | **64.9%** |
| Chapters ≥3 | 8.6% | 0.6% | 9.8% | 22.7% |
| Caption flag | 12.3% | 7.5% | 19.6% | 14.1% |
| HD definition | 99.9% | 99.7% | 100% | — |

### 7.2 CTA counts (regex, overlapping — ek description me multiple ho sakte hain)

| Bucket | subscribe | comment | follow | link | part2 | credits | chapters | ai | disclaimer | affiliate | newsletter | donate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| short | 64 | 19 | 51 | 100 | 15 | 23 | 0 | 10 | 19 | 0 | 1 | 2 |
| medium | 95 | 16 | 35 | 125 | 13 | 13 | 12 | 1 | 5 | 12 | 2 | 7 |
| long | 115 | 8 | 42 | 122 | 37 | 14 | 16 | 4 | 8 | 8 | 3 | 0 |
| **global** | **274** | 43 | 128 | **347** | 65 | 50 | 28 | 15 | 32 | 20 | 6 | 9 |

**Reading:** link sab se common CTA (347/717 = 48.4%) — mostly affiliate/social. `subscribe` 38.2%, `follow` 17.9%. **`part2` long me 37** — yani long me “next part” ka promise common hai. Lekin **`comment` sirf 43 (6.0%)** — matlab **comment CTA under-used** hai. Ye hamare liye asli gap hai: comment/vote ko explicit banana.

### 7.3 Chapter leaders (creator-published metadata, spoken script nahi)

| ID | Words | Numbers | Chapters | Views |
|---|---|---|---|---|
| `26ml5dfmQ4I` | 840 | 185 | **91** | — |
| `t8pcKyc3XbM` | 457 | 106 | 50 | — |
| `qSuoNeeFjbs` | 479 | 89 | 36 | — |
| `pVDqiYIxvdA` | 371 | 78 | 31 | — |
| `ZADsAhZysqw` | 1466 | 97 | 25 | — |

**Boundary:** chapter regex time-like lines bhi pakad sakta hai; aur 6,000-char cap ki wajah se lambi descriptions **truncate** ho sakti hain. Is liye “91 chapters” ko **exact structure** na samjhein — ye **published text ka parse** hai.

### 7.4 Description design rule (hamara)

- **Short:** ~60 words. Pehle sawal, phir teen designs, hidden failure, safety boundary, ek vote, 3 hashtags. Link nahi (jab tak asli source na ho).
- **Medium:** ~100 words + **11 chapters** (`0:00` se). Material list + limitations + vote.
- **Long:** ~130 words + **11 chapters** + results/limitations + “compilation nahi” line.
- **Har format me:** koi misleading claim nahi, koi fake “part 2” nahi, AI disclosure sirf agar synthetic use ho.

---

## 8. Comments — 575 fetched comments ka microscope

### 8.1 Request ledger

- 40 deep IDs me se **pehle 24** par commentThreads call: **23 ok, 1 error (403 on `-xasdJzBVpo`), 16 not_requested**.
- **575 comments** total, max **25 per video**, `order=relevance`. Mining floor **2.5%**, minimum **20 comments** per video.
- Ye **sab comments nahi** hain. Relevance-ordered top 25 hain. **Silent majority invisible** hai.

### 8.2 Global phrase counts (of 575)

| Pattern | n | Share |
|---|---|---|
| Asked for a sequel | **9** | 1.6% |
| Objected to cost | **3** | 0.5% |
| Said it did not work | **2** | 0.3% |
| Asked for sibling topic | 1 | 0.2% |
| Objected to pacing/clarity | 1 | 0.2% |
| Wants the asset | 1 | 0.2% |
| Asked which tool | 0 | 0% |
| Wants teaching | 0 | 0% |

### 8.3 Per-video patterns (sirf wahan jahan ≥2.5% floor clear hua)

| Video | Comment n | Pattern | Share | Iska matlab |
|---|---|---|---|---|
| `qR7vPGcP_ko` (JayFindsThings, stain) | 25 | sequel **12%** + did-not-work 4% | **sab se strong** | audience ne agla test maanga; kuch ne “kaam nahi kiya” kaha |
| `7Wx_2kGHqUA` | 25 | sequel **12%** | strong | sequel demand |
| `xZco3o0HLZc` (Chanel blush repair) | 25 | cost **8%** + sequel 4% | moderate | “ye mehnga hai” objection |
| `jfUU24gaqNg` (Mark Rober) | 25 | cost 4% | weak | cost objection |
| `ZuA1yaHDB_A` (farrier) | 25 | did-not-work 4% | weak | “aisa nahi hota” |
| `5PTL5N5c4jc` (Square Bubble) | 25 | sibling topic 4% + pacing 4% | weak | agla experiment + clarity |
| `pvMPaYHwGVw` | 25 | sequel 4% + asset 4% | weak | sequel + file demand |
| `huQIyJ1ymEQ` (softest cushion) | 25 | sequel 4% | weak | sequel |
| `F1_aOX0acbY` (music) | 25 | **koi pattern nahi** | — | music comments sentiment hain, brief nahi |
| `HSWrqJTDn8o`, `GpRLQ-QizQQ`, `T9abiWZZros`, `4aWjjSKAQig` | 25 each | **koi pattern nahi** | — | comment field brief nahi de sakta |

### 8.4 Sab se zyada liked comments (jo asli audience language dikhate hain)

- `huQIyJ1ymEQ`: **“World's softest cushion ❌ World's strongest chair ✅”** (27,401 likes) — audience **test ko aage badhana** chahti hai.
- `qR7vPGcP_ko`: **“I love this guy. No part two, no lies and no beg for likes. Respect! This is refreshing”** (70,630 likes) — **anti-clickbait / no-fake-sequel** sentiment sab se zyada liked.
- `ZuA1yaHDB_A`: **“What is it called?”** (1,481) — **tool/mechanism** curiosity.
- `jfUU24gaqNg`: Mark vs Speed jokes — entertainment, niche signal nahi.

**Ye teen comments hamare design ke liye asli brief hain:**
1. **Fake “part 2” na karo** — audience us se thak chuki hai (70k likes wala comment).
2. **Test ko aage badhao** — sequel/sibling demand real hai.
3. **Naam/mechanism batao** — “ye kaise kaam karta hai” wala sawal common hai.

---

## 9. Thumbnails — 40 images ka pixel-level read (aur uski limit)

### 9.1 Aggregate

| Metric | All (n=40) | Short (n=26) | Medium (n=8) | Long (n=6) |
|---|---|---|---|---|
| face heuristic | .825 | .885 | .625 | .833 |
| contrast | .226 | .209 | .250 | .265 |
| brightness | .325 | .272 | .354 | .513 |
| busy (edge density) | 2.335 | **1.70** | 3.734 | 3.225 |
| accent share | .508 | .518 | .546 | .412 |
| lower text energy | 2.111 | **1.55** | 3.312 | 2.938 |
| dominant hue | red 22, teal 15 | red 14, teal 10 | teal 4, red 4 | red 4 |

### 9.2 Iska matlab — aur jo nahi hai

- **Short thumbnails sab se “saaf” hain**: busy 1.70 (lowest), lower text energy 1.55 (lowest), face .885 (highest). Yani short me **chehra + kam text + kam clutter**.
- **Medium/long zyada busy** (3.73 / 3.23) — kyunki unme title text, arrows, multiple elements hote hain; aur **long sab se bright** (.513) — studio/education look.
- **Red/teal dominant** hai (22+15 = 37/40) — yani thumbnail palette corpus me **warm-vs-cool contrast** common hai. Hamara “ek accent” rule isi se consistent hai.
- **Jo NAHI hai:** `face_present` **permissive skin-tone pixel heuristic** hai — **face recognition nahi**. `lower_text_energy` **OCR nahi** — hum nahi jaante thumbnail par kya likha tha. 40 **static thumbnails** hain — **video frames nahi**. Aur **CTR/impressions private** hain, is liye “is thumbnail ne views diye” **causal claim** hoga. **Hum wo claim nahi kar rahe.**

### 9.3 Hamara thumbnail spec (teeno formats)

| Format | Text | Composition | Kyun |
|---|---|---|---|
| Short | `1 KG?` | 1 kg weight + visibly thin paper bridge; hands optional; one accent | short me text kam (lower text energy 1.55), subject clear |
| Medium | `1 KG / 3 TESTS` | left flat failure, right tube hold, ek arrow | medium me text zyada normal (3.31), magar clutter control |
| Long | `5 TESTS / 1 KG` | bridge silhouette + five-test strip | long me brightness/contrast zyada (0.513/0.265) |

**Safe zones:** text top 12% ke andar, bottom 18% UI ke liye khaali, subject par overlap nahi.

---

## 10. Channel-level microscope — naye channels, proxies, aur unki limit

### 10.1 Proxy ka definition (pehle ye samajhna zaroori hai)

`views_per_channel_day = cumulative channel views ÷ channel age in days`. Ye **measured growth nahi** hai — ye **lifetime average** hai. Purana viral video ise hamesha upar rakhega. Isi liye hum ne **recent median** aur **≥1M hits** bhi saath dekha.

### 10.2 Top public proxies (45 me se top 12)

| Channel | Created | Subs | Channel views | Videos | Views/day proxy | Views/video | Recent median | ≥1M hits |
|---|---|---|---|---|---|---|---|---|
| FuFu Squishy | 2023-12-30 | 11.9M | 20.86B | 4,862 | 19,906,022 | 4,290,726 | 414,950 | 1 |
| **JayFindsThings** | **2024-06-02** | 7.76M | 6.41B | **72** | 7,180,536 | **89,058,587** | **44,154,290** | 1 |
| FUFUSQUISHY_PACKINGORDER | 2024-04-15 | 3.26M | 6.28B | 3,501 | 6,672,380 | 1,793,405 | 88,112 | 1 |
| News Pinch | 2025-04-30 | 2.21M | 1.43B | 6,760 | 2,556,744 | 212,180 | 14,189 | 0 |
| Street Dog Revival | 2025-02-23 | 378k | 974.1M | 1,104 | 1,553,561 | 882,321 | 23,990 | 1 |
| **GeoGlobeTales** | 2023-11-20 | 2.09M | 1.65B | 169 | 1,512,370 | 9,736,442 | 2,889,645 | **5** |
| W Sound | 2024-07-19 | 918k | 1.17B | **11** | 1,377,845 | 105,968,823 | 15,318,211 | 0 |
| Cosmetic Plus | 2025-05-14 | 559k | 496.8M | 1,305 | 908,245 | 380,697 | 5,826 | 3 |
| Ashu Ghai Edits | 2024-12-19 | 308k | 585.2M | 426 | 844,393 | 1,373,625 | 36,520 | 0 |
| Nature Global | 2024-03-08 | 2.39M | 748.1M | 882 | 764,123 | 848,160 | 31,761 | 2 |
| Tarazai | 2025-01-13 | 257k | 506.8M | 214 | 758,704 | 2,368,293 | 6,432 | 1 |
| Story TV | 2025-05-28 | 1.0M | 273.1M | 743 | 512,317 | 367,517 | 21,012 | **16** |

### 10.3 JayFindsThings — sab se instructive case (aur uski limit)

- **72 videos, 6.412B channel views, 7.76M subs, created 2024-06-02, US.** Views/video **89.06M**. Recent median **44.15M**.
- Top videos: **V18 API corpus** me `huQIyJ1ymEQ` 279.9M, `qR7vPGcP_ko` 269.5M, `HSWrqJTDn8o` 257.6M. **External vidIQ public-count page** par `dIvVlU2Cgv8` 412.5M, `9ivdSY-KQb0` 414.5M, `-D_6wWKA3Do` 267.8M bhi listed hain — wo **external benchmark** hai, is run ka API data nahi.
- Corpus me uske **26 title-safe candidates** — yani ek channel 717 candidates ka **3.6%** hai.
- **Kya seekhna hai:** kam uploads, high per-video payoff, **short visual test + product/experiment payoff**, description 16 words, tags 7–14, **koi long-form dependency nahi**. Audience comment: “no part two, no lies, no beg for likes”.
- **Kya seekhna NAHI hai:** uske clips **product + uski awaaz + uske assets** hain; copy karna **copyright + originality** dono ke khilaf. Aur **views/video 89M** ka matlab ye **nahi** ke naya channel bhi 89M karega — ye ek **outlier channel** hai, distribution ka mean nahi.
- **Important:** external vidIQ public-count page (7.76M subs / 6.412B views / 72 videos) is corpus ke **channelStatistics** se match karta hai; monthly history aur revenue estimates **modelled** hain, observed daily counts nahi.

### 10.4 GeoGlobeTales — map lane ka naya champion

- Created **2023-11-20**, 2.09M subs, **1.65B views**, **169 videos**, views/video **9.74M**, recent median **2.89M**, **5** corpus hits, **27** title-safe candidates.
- Recent uploads: “The Difference Between the House and Senate”, “Why Time Zones Got So Weird”, “The Difference Between Asia's Regions” — yani **comparison + geography + explainer**, 40–60s.
- **Kya seekhna hai:** chhota channel, **narrow geography topic**, consistent comparison format, 2M subs tak pahuncha. Ye map lane ka **naya evidence** hai (V17 ke baad).
- **Limit:** 169 videos me 27 candidates — yani **hit-rate high** hai, lekin **median recent 2.89M** (44M nahi). Map lane ki ceiling **realistic** hai, JayFindsThings jaisi nahi.

### 10.5 Newer-channel ≥1M rows by lane

| Lane | Lane n | ≥1M rows | Newer ≥1M | Top newer channels |
|---|---|---|---|---|
| map_geo_short_all | 50 | 48 | **17** | GeoGlobeTales 4, Geo All Day 2, Mini Maps, Howtown, Aaj_Ki_Research |
| microdrama_medium_all | 50 | 16 | **16** | Story TV 14, Wow TV 1, Jaldi Jaldi 1 |
| animal_rescue_short_all | 50 | 49 | 14 | Nature Global 2, Vivid Venture 2, Story Arc Paws 1 |
| satisfying_restoration_short_all | 50 | 49 | 13 | Cosmetic Plus 3, FPS 2, FuFu Squishy 1 |
| satisfying_restoration_long_all | 50 | 50 | 5 | Cleaning Vibe 2 |
| satisfying_restoration_medium_all | 50 | 50 | 4 | Cleaning Vibe 2 |
| microdrama_short_all | 50 | 13 | 4 | Casey's Journey 2, Story TV 2 |
| microdrama_long_all | 50 | 8 | 4 | Kuku TV 2 |
| map_geo_long_all | 50 | 32 | 2 | SSC Guru Talks 1 |
| science_explainer_short_all | 50 | 50 | 2 | Tusher ABC 1, JayFindsThings 1 |
| science_explainer_recent | 50 | 18 | 0 | — |
| map_geo_recent | 50 | 3 | 1 | GeoGlobeTales 1 |

**Reading:** **map short (17)** aur **microdrama medium (16)** naye channels ke liye sab se zyada “≥1M” rows dete hain. Lekin microdrama ke 16 me se **14 ek hi channel (Story TV)** ka hai, aur uska recent median **21k** — yani **ek factory**, ecosystem nahi. **Map ka 17 alag-alag channels me phaila hua hai** — ye zyada healthy signal hai.

### 10.6 Top channels inside 717 candidates

`Science and fun 36 · GeoGlobeTales 27 · JayFindsThings 26 · Raajoo Gaming 20 · KLT 16 · Cosmetic Up 16 · Story TV 16 · BOBIislive 12 · FuFu Squishy 11 · Geo Study 11 · W Sound 10 · Satisfying Shorts 10 · Maupin Farrier Co 10 · TysyTube Restoration 10 · Howtown 9 · Elite Restore 8 · WD Detailing 8 · RESTORED 8 · Amit Ashik Personal 8 · Ryan's World 7 · The Dodo 7 · Earthstic 7 · Fun Science 6 · Geo All Day 6 · Sunlike study 6`.

**Reading:** corpus me **science aur geography dono ke multiple channels** hain (Science and fun 36, GeoGlobeTales 27, KLT 16, Geo Study 11, Howtown 9, Earthstic 7, Geo All Day 6, Sunlike study 6) — yani ye **ek channel ka fluke nahi**, **lane** hai. Isi liye science-visual-test + map dono top par hain.

---

## 11. Transcript blocker — jo hum ne try kiya, jo fail hua, aur us se kya sekha

### 11.1 Ledger

| Attempt | Tool | Result |
|---|---|---|
| V18 deep teardowns | `yt-dlp` subtitles | **12/12 error** — “Sign in to confirm you're not a bot” |
| V17 fallback (run `43155064668`) | `youtube-transcript-api` + alternate yt-dlp clients | **18/18 RequestBlocked / bot-check**; `usable_transcripts 0` |
| Public `timedtext` endpoints | `HKdjIFjYZ40`, `Xqy9L-88wcw`, `dIKsEhX-vyU` | **HTTP 500** |
| Secondary pages | PSU Earth111, ESLvideo, StudioLayerOne | transcript **original MinuteEarth `8a3r-cG8Wic`** aur **StudioLayerOne ka secondary summary** — target shorts ka caption nahi |

### 11.2 Iska matlab

- **Koi bhi competitor ka verbatim script, joke timing, VO cadence, ya exact wording** is report me **nahi** hai — aur hona bhi nahi chahiye.
- Jo hum keh sakte hain: **public metadata** (title, description synopsis, chapters, tags, duration, views, likes, comments, thumbnail pixels).
- Jo hum **nahi** keh sakte: “is video me pehle 3 second me ye line bolti hai”, “ye hook use karo”, “inka pacing 2.3 cuts/sec hai”.
- Jo secondary sources se mila (MinuteEarth ka meander transcript, StudioLayerOne ka hook breakdown, Mark Rober ka long-form safety review, Alan Becker ka no-dialogue art) — wo **benchmark** hai, **API proof nahi**, aur **koi line copy nahi** ki gayi.

### 11.3 Kyun ye report phir bhi useful hai

Kyunki **format, duration, title, description, chapters, tags, comments, thumbnails, lane economics** — ye sab **public** hain aur **asli** hain. Script ke bina bhi aap **kya banana hai, kitna lamba, kis format me, kis hook type se, kis CTA se** decide kar sakte hain. **Script ka final draft aap ki apni original writing hogi** — jo is report ne `EPISODE_00_EDL_V18.json` me draft ki hai.

---

## 12. Short vs Medium vs Long — alag-alag poora comparison

### 12.1 Ek nazar me

| Dimension | SHORT | MEDIUM | LONG |
|---|---|---|---|
| Candidate n | 348 | 184 | 185 |
| Median views | **9.92M** | 3.16M | 2.54M |
| p75 | 33.36M | 9.88M | 5.01M |
| ≥10M share | **49.1%** | 24.5% | 11.4% |
| Median duration | 58s | 610s | 3147s |
| Median like rate | **.01784** | .00734 | .00840 |
| Median comment rate | .00012 | .00020 | **.00025** |
| Caption flag | 7.5% | **19.6%** | 14.1% |
| Description words | 44 | 112 | **146** |
| Chapters ≥3 | 0.6% | 9.8% | **22.7%** |
| Median tags | 7 | **17** | 15 |
| Zero tags | **40.2%** | 13.0% | 16.8% |
| Strongest hook | statement / belief | question / number | number / list |
| Production load | **lowest** | medium | **highest** |
| Rights risk | medium (assets/music) | medium | high (licensing, compilations) |
| Monetisation relevance | Shorts RPM lower | **best for long-form ads** | best for watch time |

### 12.2 SHORT — kya kaam karta hai, kya nahi

**Kaam karta hai:**
- **45–60s ya 0–15s** — do clear spikes (25.95M / 23.10M).
- **Ek visual test, ek payoff, ek hidden detail** — science short lane ke top hits (volcano 60s, elephant toothpaste 36s, square bubble 11s, paper dart 48s).
- **Kam text, kam description** — 44 words median, 40% zero tags, 16-word descriptions.
- **Like-heavy, comment-light** — .01784 vs .00012.
- **Statement/belief hook** — 11.74M / 12.16M medians.

**Kaam nahi karta:**
- **Chapters** (0.6%) — short me bekaar.
- **Lambi description** — 0-word descriptions ka median 22.9M, 151+ ka 3.62M.
- **Number-only hook** — 3.30M median, sab se kamzor.
- **60–120s** — median 5.46M, sharp drop.
- **Sirf tags par bharosa** — zero-tag videos 16.72M median par hain.

**Hamara short plan:** 56s, 11 shots, question→prediction→3 tests→hidden failure→mechanism→vote. Description ~60 words, 0 chapters, 10 tags, `1 KG?` thumbnail.

### 12.3 MEDIUM — “depth ka sab se efficient format”

**Kaam karta hai:**
- **612s–960s** (10–16 min) — 780–960s ka median 5.97M, sab se zyada.
- **Chapters** — 9.8% videos me hain, aur chapters-wale ka median 5.05M vs 3.13M (positive, lekin causal nahi).
- **Question hook** — 10.0M median (n=10, chhota sample).
- **Satisfying (3.64M, 828s)** aur **science (3.11M, 627s)** — dono stable.
- **Caption flag 19.6%** — sab se zyada; yani medium me captions/subtitles zyada common.

**Kaam nahi karta:**
- **Animal rescue** (73.7k median) — log medium me rescue nahi dekhte.
- **Viral breakdown** (42.3k) — meta-niche medium me mar chuka hai.
- **Microdrama medium** (592k, **0 ≥10M**) — factory content, organic nahi.

**Hamara medium plan:** 10m30s, 11 chapters, control + 3 designs + hidden failure + mechanism + cost objection + rematch + results/limits.

### 12.4 LONG — “library + trust” ka format, “viral” ka nahi

**Kaam karta hai:**
- **Satisfying long 3.56M / 2084s** — sab se strong long lane (50/50 ≥1M).
- **Numbers in title** (55.1% long titles me) — scope batate hain: “40 Science Experiments”, “50 States”, “Level 1 to 100”.
- **Chapters 22.7%** — long me normal.
- **Comment rate .00025** — sab se zyada; long me log baat karte hain.
- **1-hour+ compilations** ka median 2.40M — library model chalta hai.

**Kaam nahi karta:**
- **Viral breakdown long** — 1,695 median, **0 ≥1M**. Sab se bara red flag.
- **Animal long** — 330.6k, top3 .531 (ek do video par depend).
- **Microdrama long** — 191k, 3695s, 1 ≥10M.
- **Science long** — 1.05M, top3 .657 (outlier-dependent: 168M + 42.8M + 39.2M).

**Hamara long plan:** 28m, **single-session original arc** (compilation nahi), 5 designs, load ramp, failure analysis, rematch, results/limits. Ye 1200–1800s bucket me padta hai (median 2.47M) — realistic, “1 hour compilation” ka sapna nahi.

### 12.5 Format ka faisla — ek line me

- **Agar goal = reach / naya audience:** **Short first** (56s).
- **Agar goal = depth / trust / watch time:** **Medium** (10–11 min, chapters).
- **Agar goal = library / search / binge:** **Long** (28 min, single arc), **compilation nahi**.
- **Teeno ek saath** sirf tab jab **har format ka apna promise** ho. Warna wahi clip teen baar = **repetitive/template** ka khatra, jo official policy ke against hai.

---

## 13. Niche ranking — transparent scoring

Scoring **qualitative tiers** me hai (0–5), evidence se:

| Criterion (weight) | Visual Proof Lab | Map/Geography | Satisfying/Restoration | Animal Rescue | Microdrama | Viral Breakdown |
|---|---|---|---|---|---|---|
| Short-lane high-view evidence (25%) | 5 (science 49.8M) | 4 (6.63M) | 5 (22.92M) | 4 (7.48M) | 2 (463k) | 2 (74k) |
| Medium/long depth viability (20%) | 4 (3.11M / 1.05M) | 4 (1.74M / 1.52M) | 5 (3.64M / 3.56M) | 2 (73.7k / 331k) | 2 (592k / 191k) | 1 (42k / 1.7k) |
| Newer-channel entry signal (20%) | 3 (2 rows, but JayFindsThings 26 cands) | **5** (17 rows / 8+ channels) | 4 (13 rows) | 5 (14 rows) | 2 (16 → 14 one channel) | 1 (1 row) |
| Feasibility for small team (15%) | **5** (paper, weight, phone) | 4 (research + simple animation) | 1 (needs craft/asset) | 2 (needs animals/rights) | 1 (casting/writers) | 3 (needs research) |
| Rights / originality safety (10%) | **5** (100% self-shot) | 4 (self-made maps) | 2 (process footage ownership) | 2 (animal welfare/reupload) | 3 (scripted original) | 4 |
| Saturation risk (10%) | 3 (science crowded but varied) | 4 | 1 (very saturated) | 2 | 2 | 1 |
| **Weighted total /5** | **4.20** | **4.20** | **3.50** | **3.10** | **1.95** | **1.85** |

**Reading:** Asli arithmetic se Visual Proof Lab aur Map/Geography **bilkul barabar** hain (**4.20 vs 4.20**). Yani score se koi winner nahi nikalta — is liye maine isay tie rakha hai, kisi ek ko "winner" nahi banaya. Farq sirf profile ka hai:
- **Visual Proof Lab** = science lane ka high ceiling + zero rights risk + ek banda kar sakta hai.
- **Map/Geography** = newer channels ka sab se strong, sab se phaila hua signal + V17 me already research hua + realistic ceiling (1–4M recent), lekin animation/research load zyada.

**Tie ka faisla aap ke paas hai:** agar aap ke paas **craft/asset** ya **animation skill** hai, ya aap **Pakistani/Urdu current-affairs** audience ko target karte hain, to map lane zyada natural hai. Agar aap **ek phone, ek table, zero assets** se shuru karna chahte hain, to Visual Proof Lab zyada natural hai.

**Ye scoring meri judgment hai, aap ka faisla nahi.** Weights badalne se ranking badal sakti hai — is liye maine weights likh diye hain, takay aap disagree kar sakein.

---

## 14. Provisional recommendation — `VISUAL PROOF LAB`

### 14.1 Kya hai

**Naam:** `VISUAL PROOF LAB — Kya Ye Sach Mein Kaam Karega?`
**Pilot:** `Kaagaz Ka Bridge: 1 Kilo, 3 Designs, 1 Hidden Failure`
**Sawal:** *Kya sirf kaagaz ka bana pull 1 kilo wazan sambhal sakta hai, aur kaunsa design sab se pehle fail hoga?*
**Format:** short-first (56s) → medium (10m30s) → long (28m) — **teen alag promises**, ek hi clip ka re-cut nahi.
**Materials:** printer paper, ruler, 1 kg calibrated weight / sealed bottle, flat table, phone, soft tray. **Koi chemical, aag, animal, minor, sharp load nahi.**

### 14.2 Kyun ye (evidence-backed reasons)

1. **Science short lane sab se strong hai** (median 49.79M, 50/50 ≥10M) aur medium/long me bhi zinda hai (3.11M / 1.05M).
2. **45–60s bucket (n=83, median 25.95M)** hamare 56s target ke saath match karta hai.
3. **Zero rights risk** — sab kuch self-shot; koi competitor clip/audio/music nahi. (Animal/map/satisfying me rights ya asset dependency hai.)
4. **Originality guard** — har episode ka naya sawal/failure/mechanism, is liye policy ke “generic/template/mass-produced” wale khatre se bachav.
5. **Audience ka asli sawal** — “sequel”, “kaam nahi kiya”, “naam kya hai” — teeno ka jawab design me hai (vote, visible failure, mechanism).
6. **Ek banda + ek phone** se shuru ho sakta hai — yani pehla test **mehnga nahi**, aur fail ho to nuksan kam.

### 14.3 Risks / kya galat ho sakta hai

| Risk | Mitigation |
|---|---|
| Science shorts me saturation high hai | Alag sawal + hidden failure + mechanism; generic “5 experiments” nahi |
| “Paper bridge” boring lag sakta hai | 2s hook, prediction, hidden failure close-up, vote |
| AI/TTS voice audience reject kar sakti hai | Own voice default; TTS sirf disclosure ke saath |
| 1 kg test “staged” lage | Calibrated weight, side camera, no cuts during load, timer visible |
| Short se medium/long me audience nahi aayegi | Har format ka apna hook/title/thumbnail; “part 2” ka jhoota promise nahi |
| Policy: repetitive content | Har episode naya; template sirf **format** ka, **content** ka nahi |
| Monetisation expectation | Shorts RPM long-form se kaafi kam; is report me koi revenue claim nahi |

### 14.4 Kya is recommendation ko **falsify** karega

- Agar aap ke paas **craft/asset** hai (e.g. restoration, farrier, makeup) → satisfying lane **behtar** ho sakti hai.
- Agar aap **geography/current affairs** me comfortable hain aur animation kar sakte hain → **map lane** barabar score (4.20 vs 4.20) par hai, aur newer-channel evidence (17 vs 3 rows) uske haq me zyada hai.
- Agar aap **Urdu/Pakistani audience** ko target kar rahe hain → corpus **English-heavy** hai; Roman Urdu me hook/retention **test karna padega**, ye data us par khamosh hai.
- Agar aap ka goal **long-form watch time / ads** hai → medium/long pehle karein, short sirf funnel.

---

## 15. Pilot ka poora production plan (teeno formats)

Detail `PRODUCTION_BLUEPRINT_V18_ROMAN_URDU.md` aur machine-readable `EPISODE_00_EDL_V18.json` me hai. Yahan summary:

### 15.1 Scripts (original, competitor se nahi)

- **Short (56s, 11 lines):** “Kya kaagaz ek kilo utha sakta hai?” → guess → flat fail → fold → edge load → tubes → 1 kg hold → hidden failure → bend vs compression → vote.
- **Medium (10m30s, 11 chapters):** cold open → prediction → control → fold → tubes → hidden failure → mechanism → cost objection → rematch → results → next.
- **Long (28m, 11 chapters):** cold open → rules → safety → test 1 → test 2 → test 3 → test 4 → test 5 load ramp → mechanism → rematch → limits.

Har line Roman Urdu me, ~110–130 words short, ~700–900 medium, poora arc long. **Koi competitor line copy nahi.**

### 15.2 Titles

- Short: `Kya Kaagaz 1 Kilo Utha Sakta Hai? 3 Designs Test`
- Medium: `Kaagaz Ka Bridge: 1 Kilo, 3 Designs Aur Ek Chhupa Failure`
- Long: `Kaagaz Se Pull Tak: 1 Kilo Ka Poora Visual Proof Test`

### 15.3 Descriptions + chapters

- Short ~60 words, **0 chapters**, 3 hashtags.
- Medium ~100 words + **11 chapters**, material list, limitations.
- Long ~130 words + **11 chapters**, results table, “compilation nahi” line.

### 15.4 Tags

10 focused tags per format (short/medium/long lists blueprint me). **Keyword stuffing nahi, celebrity/game tags nahi.**

### 15.5 Comments

- Pinned: “Har claim ka visible test, har failure ka close-up, agla sawal audience se. Vote: 2 kg / naya design / mechanism detail?”
- Har format ka end **vote** par.
- “Part 2” sirf tab jab sach me banega.

### 15.6 Thumbnails

- Short `1 KG?`; Medium `1 KG / 3 TESTS`; Long `5 TESTS / 1 KG`.
- Ek accent, kam text, subject par overlap nahi, top 12% / bottom 18% safe.

### 15.7 Editing

- Short: 11 shots / 56s, 4–7s me naya proof, straight cuts, natural test sound, burned-in short captions.
- Medium: 11 chapters, har 60–90s me naya test/failure, recap.
- Long: 11 chapters, har 2–3 min me measurable change, results table.
- **Competitor ke cuts/sec, transitions, music, colour grade, caption animation — not observed; ye hamare design decisions hain.**

### 15.8 QC (upload se pehle)

User approval → original footage → rights ledger → safety review → claim/test match → no competitor media → AI disclosure if any → title/desc/chapters/tags/thumbnail match → technical QC (duration/aspect/audio/captions/safe zones) → human creative review. **Is report ne koi upload nahi kiya.**

---

## 16. Safety, rights, originality, policy

### 16.1 Safety

- **Allowed:** paper, ruler, tape (disclosed), 1 kg calibrated weight/bottle, flat table, phone, soft tray.
- **Excluded:** fire, concentrated peroxide, chemicals, glass under load, sharp tools, minors as spectacle, animals, competitor clips, unverified life hacks, dangerous replication.
- **Kyun:** Mark Rober ke **10:33 long-form** elephant toothpaste experiment ki external safety review high-concentration chemical, ~200°F foam heat aur adult/professional planning batati hai. Hamara pilot **mechanical** hai. **Ye legal clearance nahi.**

### 16.2 Rights

- Footage: 100% self-shot (abhi shoot nahi hua).
- Voice: own / disclosed TTS; competitor voice clone nahi.
- Music/SFX: original ya licence-documented.
- Graphics/maps: self-made; third-party tiles sirf rights verify hone par.
- AI: agar synthetic use ho to disclose.

### 16.3 Originality / policy

Official YouTube Help (July 2025, “repetitious” → “inauthentic content”) ke mutabiq monetised channels ko original/authentic hona chahiye, aur mass-produced, generic, repetitive, manipulative ya generic AI-template content se bachna chahiye. Is liye:

- Har episode: naya sawal, naya failure, naya mechanism.
- Short/medium/long: alag promise, alag proof — sirf re-cut nahi.
- Long: compilation nahi, single arc.
- Title/tag/hashtag stuffing nahi.

**Ye policy reading hai, legal advice ya channel clearance nahi.**

---

## 17. Measurement — sirf future upload ke baad

- **Public:** apne views/likes/comments 24h / 7d / 28d (Data API ya creator analytics).
- **Private:** retention/CTR/RPM sirf apne creator analytics me — is report me nahi.
- **Comparison:** apne channel baseline se, **high-view-conditioned competitor medians se nahi**.
- **Koi claim nahi:** guaranteed views, virality, RPM, monetisation outcome, perfection.

---

## 18. Not-observed / not-available / not-claimed ledger (repeat, takay koi bhoolay na)

| Item | Status | Proof |
|---|---|---|
| Verbatim competitor scripts/captions | **not_observed** | 12/12 bot-check; 0 words |
| Competitor frames, cuts/sec, transitions, music, SFX, colour, caption animation, retention | **not_observed** | 40/40 teardowns `not_observed`; no media download |
| Private retention/impressions/CTR/RPM/revenue/demographics | **not_available** | public API only |
| Verified subscriber-growth ranking | **not_observed** | cumulative views ÷ age proxy |
| Thumbnail OCR / face recognition / text content | **not_observed** | pixel stats + permissive skin-tone heuristic |
| All public comments | **partial** | 23 ok / 1 error / 16 not_requested; 575 comments, 25/video |
| Full untruncated descriptions | **partial** | 6,000-char cap |
| “Asli” 9:16 vs 16:9 | **not_observed** | raw dump me sab `2d/rectangular` (API artifact) — aspect hamari choice hai |
| Causal reason a video won | **not_observable** | co-occurrence, not experiment |
| Legal clearance / human approval / upload / monetisation | **not_done** | research only |
| Guaranteed views / virality / perfection / family-safety | **not_claimed** | boundary |

---

## 19. Source files (sab workspace me)

| File | Kya hai |
|---|---|
| `research/deep_forensic_v18/FINAL_DEEP_FORENSIC_V18_ROMAN_URDU.md` | **ye report** |
| `research/deep_forensic_v18/EVIDENCE_TABLES_V18.md` | 24 lanes, cross-bucket, 40 teardowns, comments, thumbnails, transcript ledger, not-observed ledger (machine tables) |
| `research/deep_forensic_v18/FORENSIC_EVIDENCE_EXTRACT_V18.json` | 717-candidate index, 40 teardown cards, derived tables |
| `research/deep_forensic_v18/RECOMMENDATION_V18.json` | ranked options, evidence, pending decision, boundaries |
| `research/deep_forensic_v18/EPISODE_00_EDL_V18.json` | teeno formats ke scripts, EDL, descriptions, chapters, titles, tags, comments, thumbnails, QC |
| `research/deep_forensic_v18/PRODUCTION_BLUEPRINT_V18_ROMAN_URDU.md` | production blueprint (same content, alag structure) |
| `research/deep_forensic_v18/DEEP_FORENSIC_V18.md` | auto-generated Actions appendix (raw, is report ka replacement nahi) |
| `research/deep_forensic_v18/api_evidence/*.json` | asli API dump: `run_v18.json`, `analysis_manifest_v18.json`, `lanes_v18.json`, `lane_metrics_v18.json`, `video_details_v18.json` (2347), `description_forensics_v18.json` (717), `deep_teardowns_v18.json` (40), `comments_v18.json`, `thumbnail_forensics_v18.json`, etc. |
| `research/next_level_niche_v17/*` | V17 ka pura forensic + `NAQSHA FILES` (approved nahi) |
| `.github/workflows/yt-deep-forensic-v18.yml` | reproducible run (marker `v18-deep-trigger.txt`) |

**Reproduce:** workflow push marker ke saath chalta hai; secret `YOUTUBE_API_KEY` already configured hai; HARD QC raw dump = in-memory corpus assert karta hai. Local derive: `python3 research/deep_forensic_v18/build_v18_evidence_extract.py` (no network).

---

## 20. Aakhri sach — ek paragraph

Is corpus me **2,347 public videos, 717 million-view candidates, 40 deep teardowns, 575 comments, 40 thumbnails** hain — aur **0 competitor scripts, 0 frames, 0 private analytics, 0 verified growth numbers**. Is liye ye report **pattern evidence** deti hai, **guarantee nahi**: short 45–60s visual proof sab se zyada high-view-conditioned signal rakhta hai, science aur geography dono me naye channels kamyab ho rahe hain, audience sequel + visible proof maangti hai, aur tags/description length views ka cause nahi. Sab se honest tajweez **`VISUAL PROOF LAB`** hai — lekin **aap ne decide nahi kiya**, aur jab tak aap A/B/C nahi choose karte, ye sirf **provisional recommendation** hai.

---

## 21. Aap ka faisla chahiye — A / B / C

| Option | Kya hoga |
|---|---|
| **A) `VISUAL PROOF LAB` approve** | Pilot `Kaagaz Ka Bridge` ka script/EDL final, shoot plan, safety checklist, thumbnail draft — human review ke liye ready |
| **B) Map / Geography deeper** | `NAQSHA FILES` ko approved maane baghair naya map plan: 8 episode ideas, research workflow, animation pipeline, realistic 1–4M target |
| **C) Aap ka apna niche/idea** | V18.1 evidence us idea ke against re-score hoga (short/medium/long, hook, title, tags, comments, thumbnails) |

**Aur ye bhi pending:** language (Roman Urdu / Urdu / English), voice (own / TTS), face vs hands-only, cadence, safety/rights review, human creative approval.

**Jab tak aap choose nahi karte — koi upload, koi publish, koi “final niche” claim nahi.**

---

## 22. ADDENDUM (user-directed): English + USA audience, aur 3D animation ka sawal

Ye section user ke saaf direction par add hua: **"hamara target audience USA se zyada hai, content English me hai"**. Yani niche choice ka scoring ab **English / US-first** lens se dobara padha gaya hai. **Purana data wahi hai** — sirf interpretation badla hai.

### 22.1 Language: corpus pehle se English-heavy hai — ye hamare haq me hai

717 candidates ka `default_language`:

| Language | n | Share |
|---|---|---|
| `en` | 562 | 78.4% |
| `en-US` | 80 | 11.2% |
| `en-IN` | 30 | 4.2% |
| `en-GB` | 12 | 1.7% |
| `hi` | 12 | 1.7% |
| `es` / `es-419` | 12 | 1.7% |
| `id` / `ml` / `bn-IN` | 6 | 0.8% |

**English total: 684/717 = 95.4%.** Yani pehle jo maine likha tha ke “Roman Urdu me test karna padega, corpus English-heavy hai” — **wo aap ke liye masla nahi tha, wo aap ke liye fit tha.** Ab language change nahi karni: **English hi rakhein**, Roman Urdu sirf aap ke liye samjhane ke liye.

Top science shorts ka `default_audio_language`: `-xasdJzBVpo` **en**, `jfUU24gaqNg` **en-US**, `5PTL5N5c4jc` **en-US**, `4aWjjSKAQig` **en-US**, `-FmaF5KnJ4c` **en-US**, `huQIyJ1ymEQ` **en-US**, `qR7vPGcP_ko` **en-US**. Yani **US-English audio hi is lane ka standard hai** — accent American rakhein, British nahi.

### 22.2 US-first channels ka real record

| Channel | Country | Created | Channel views | Views/day proxy | Note |
|---|---|---|---|---|---|
| JayFindsThings | **US** | 2024-06-02 | 6.41B | 7.18M | 72 videos, views/video 89.06M |
| Geo All Day | **US** | 2023-11-24 | 296.7M | 273.7k | map short |
| Howtown | **US** | 2024-03-22 | 256.0M | 265.3k | map explainer |
| GeoGlobeTales | **CA** | 2023-11-20 | 1.65B | 1.51M | map short, 27 candidates |
| Earthstic | **PK** | 2025-04-30 | 81.2M | 144.7k | Pakistani channel, English map shorts |

**Ahem baat:** **Earthstic ek Pakistani channel hai (created 2025-04-30), 81.2M views, English map shorts** — yani Pakistan se English content **US/global audience** le raha hai. Ye aap ke case ka sab se qareeb ka real example hai: **Pakistan se, English me, US audience ko**. Ye “Pakistan se English me US audience” ka **proof of concept** hai (verified growth nahi, sirf public proxy).

### 22.3 USA/English lens se niche ranking dobara

| Niche | English/global fit | US audience fit | Verdict |
|---|---|---|---|
| **Map / Geography explainer** | **5/5** (95% corpus English; GeoGlobeTales CA, Geo All Day US, Howtown US, Earthstic PK) | **5/5** (US states, time zones, Congress, world geography = US search demand) | **#1 US-first** |
| **Visual Proof Lab (science)** | 5/5 (science shorts en-US audio) | 4/5 (science US me strong, magar kids/family skew) | **#2** |
| Satisfying / restoration | 4/5 | 3/5 (global, US me bhi) | craft chahiye |
| Animal rescue | 4/5 | 3/5 | sensitive |
| Microdrama | 2/5 (IN/ID-heavy, Hindi/Telugu) | 1/5 | nahi |
| Viral breakdown | 4/5 | 2/5 (US meta-niche already served by big names) | nahi |

**Naya nateeja:** **aap ki direction ke saath map/geography #1 par chala jata hai**, Visual Proof Lab #2 par. Pehle dono **4.20 / 4.20 tie** the — tie toot gaya **aap ke audience decision se**, naye data se nahi. Ye farq zaroori hai: score same hai, **fit badal gaya**.

**Kyun map US-first me jeetta hai:**
1. **US audience geography me curious hai** — “50 States Song” 47.5M, “All the Countries with Flags” 65.9M, GeoGlobeTales ke “House vs Senate”, “Why Time Zones Got So Weird”, “Asia's Regions” — ye **US civic/geography** topics hain.
2. **English default** — corpus me map lane ke top channels US/CA hain.
3. **Realistic ceiling** — map recent lane median 35.3k, winner 4.17M, 3 videos ≥1M. Ye **naye channel ke liye believable** hai. Science ka recent lane median 1,436 hai magar winner 112M — yani **lottery**.
4. **Animation-driven** — map lane me animation **already norm** hai (`Geo Study`, `Sunlike study`, `Animation gyaan hub`, `Beyond Borders`, `Geoview`), is liye aap ka 3D skill **yahan direct convert** hota hai.

### 22.4 3D animation — kya aap aage ja sakte hain? (seedha jawab: HAAN, lekin ek shart ke saath)

**Haan — kyunki data me animation wale channels ka record maujood hai:**

| Animation-type channel | Candidates | Median views | Max | Duration profile |
|---|---|---|---|---|
| **Alan Becker** (`Animation vs. Math`) | 1 | **163.57M** | 163.57M | 843s (14m) — **no dialogue** |
| **KLT** (kids geography songs) | 16 | **5.06M** | 65.90M | 207–257s |
| **GeoGlobeTales** (map animation) | 27 | **3.45M** | 28.99M | 42–68s shorts |
| **Howtown** (map explainer) | 9 | 2.47M | 25.83M | 64s shorts + 20–25m long |
| Sunlike study (2D animation, CBSE) | 6 | ~5.0M | 7.58M | 1700–2900s |
| Geo Study (map animation, Hindi) | 6+ | 3.0–5.1M | 18.2M | 34–60s shorts |
| **Earthstic** (PK, English) | 7 | 1.42M | 7.39M | 12–27s + long |

**Sab se important do misaal:**
1. **Alan Becker — `Animation vs. Math`: 163.57M views, 14m3s, koi dialogue nahi.** Stick figure + equations. Ye **pure visual animation** ka sab se bara proof hai corpus me. Iska matlab: **3D/2D animation long-form me bhi 163M kar sakti hai** — agar **visual storytelling** ho, VO nahi.
2. **KLT — 16 candidates, median 5.06M, max 65.9M, 3–4 minute geography songs.** Ye **educational animation ka repeatable model** hai: geography + song + simple animation, **bina cinematic 3D ke**.

**Shart (jo aap ko maan ni hogi):**
- **3D = cost + time.** 56s short ke liye bhi modelling, lighting, render — ek banda hafte me 1 video kar sakta hai, daily nahi. Is liye 3D me **short-first weekly cadence** realistic hai, **daily nahi**.
- **3D khud views nahi deti.** `Animation vs. Math` 163M is liye hai ke **concept (math) + visual gag + pacing** hai, 3D quality ki wajah se nahi. `Geo Study` ke 34–60s map animations 3–5M karte hain **simple 2D** me.
- **Pipeline:** script → storyboard → blockout → animation → sound → thumbnail. Har step me **ek rukavat** = ek hafta. Is liye pehla 3D short **2 hafte** target karein, 2 din nahi.
- **Render cost:** 1080p 30fps 60s me bhi Blender me GPU hours lagte hain; is liye **stylised/low-poly** style choose karein, photorealism nahi.
- **3D me bhi transcript/caption block wahi hai** — koi competitor script nahi milega.

### 22.5 Recommendation update — 3D + English + USA ke saath

**Naya #1: `MAP ANIMATION` niche (English, US-first, 3D-friendly)**
- **Short:** 45–60s, ek geography sawal, **3D map camera move** + ek label + ek answer. (Map lane ka median 59s short; top hit 17s; hamara 50s sweet spot.)
- **Medium:** 8–12 min, 3D map + timeline + comparisons (e.g. “Why 90% of Canada lives near the border”).
- **Long:** 20–30 min, deep geography arc.
- **Kyun:** English 95% corpus, US/CA/PK channels sab isme hain, newer-channel rows **17**, realistic ceiling 1–4M, aur **aap ka 3D skill direct asset hai**.
- **Risk:** animation load; “map + text” generic ban sakta hai; **research quality** hi differentiator hai.

**#2: `VISUAL PROOF LAB` — 3D ke saath**
- 3D me **test ko simulate** karke phir **real test** dikhana (simulation vs reality) — ye ek **naya angle** hai jo abhi corpus me nahi hai. Lekin ye **experimental** hai, data iska proof nahi.
- Agar 3D aap ka strength hai, to Visual Proof Lab ko **“3D prediction → real test”** format me badla ja sakta hai. Ye original hoga, magar **pehle test karna padega**.

**#3: KLT-style educational animation** — geography/science songs, 3–4 min, kids/family. Median 5.06M, max 65.9M. **Magar** ye **kids content** hai: `made_for_kids` compliance, COPPA-style rules, aur “kids content” me monetisation limits. Corpus me `made_for_kids` sirf 63/2347 — yani ye mainstream nahi, **alag compliance track** hai. Isay tab choose karein jab aap **specifically kids** karna chahein.

### 22.6 Jo abhi bhi nahi pata (aur 3D se nahi badlega)

- **US audience ka apna retention/CTR** — public API me nahi.
- **3D vs 2D ka performance farq** — corpus me dono hain, lekin **koi controlled comparison nahi**. Main ye nahi keh sakta “3D zyada views deti hai”. Main sirf ye keh sakta hoon: **animation wale channels is corpus me 1.4M se 163M tak hain**.
- **Aap ka render pipeline kitna fast hai** — ye aap ka operational sawal hai, data ka nahi.
- **Aap ka US audience kaise aayega** — Shorts feed geography-based hota hai, channel location US/CA/PK ka farq **public data me nahi dikhta**. Earthstic (PK) ka example dikhata hai ke **possible hai**, guaranteed nahi.

### 22.7 Ek line ka faisla

**Aap English + USA + 3D kar rahe hain → `MAP ANIMATION` ab #1 hai, `VISUAL PROOF LAB` #2.** 3D aap ko **map lane me sab se zyada faida** degi (kynki wahan animation already norm hai aur US search demand hai), aur **Visual Proof Lab me** 3D sirf tab useful hai jab aap “simulation vs real test” ka naya format banana chahein. **Dono me se ek chunein, dono ek saath nahi** — pehla episode ek lane me karein, warna dono adhoore rahenge.
