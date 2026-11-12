# V17 — Naya Next-Level Niche: 10x Forensic + Aik Viral-Potential Idea (Roman Urdu)

**Tarikh (evidence):** `2026-11-12T04:24:09Z` (main API run), `2026-11-12T04:32:14Z` (transcript fallback).
**Branch:** `arena/2b012328-monarch-overall-work`. **Status:** research/decision report; koi upload, publish, monetisation claim, legal clearance ya human creative approval nahi.

---

## 0. Aik line mein faisla

**"Caught on camera" ko side mein rakhte hue, main ne real YouTube Data API se 20 lanes / 1,567 unique videos / 822 channels / 4 regions / 418 million-view videos ka evidence nikala, dobara public-caption fallback chalaya, aur hasil ye nikala: agla next-level, fun, unique aur ownable niche hai `NAQSHA FILES — Map Forensics` — yaani "naqshe ka raaz": 60–90 second ka evergreen map-mystery Short + 6–12 minute ka recent-event map-forensics long-form, 100% apne banaye hue vector maps, apni awaaz, apne captions aur saaf `SAABIT / MUKHTALIF / NA-MALOOM` labels ke saath.**

Ye **viral-potential** idea hai, **viral guarantee** nahi. Neeche har number, har filter, har script-beat, har edit-layer aur har limitation likhi hai — jo cheez observe nahi ho saki, usse "nahi dekha" likh kar chhoda nahi gaya, balke explicitly mark kiya gaya.

---

## 1. Pehli aur sabse zaroori baat: honesty boundary

User ne kaha tha "bagair kisi kami ke, galati ke, flaws ke, kuch chore miss kiye". Isse maine **kaam ka standard** mana, **perfection ka guarantee** nahi. Isliye pehle hadd clear kar deta hoon:

| Main ne **kiya** (real evidence) | Main ne **nahi kiya / nahi kar sakta** (clear mark) |
| --- | --- |
| YouTube Data API `search.list`, `videos.list`, `channels.list`, `playlistItems.list`, `commentThreads.list`, `videoCategories.list` | Competitor ka video/audio download nahi kiya |
| Public `snippet.description` = creator ka apna likha hua synopsis / chapters / sources | Competitor ke video frames, cuts-per-second, transitions, music, sound design inspect nahi kiye |
| Public captions lane ke liye 2 alag attempts (12 + 18 targets) | Koi bhi verbatim competitor transcript YouTube captions se hasil nahi hua; isliye **invented script** nahi likhi |
| 24 public thumbnails ke pixel statistics (PIL/numpy) | OCR, face recognition, ya video-frame edit analysis nahi |
| Public comments (12 videos, 25+25... comments) | Private retention, CTR, RPM, impressions, A/B test, subscriber-growth ranking nahi |
| Channel creation date, cumulative views, video count, recent-upload cadence | "Verified fastest-growing channel" ranking nahi — sirf **public proxy** |
| 4 regions ka `mostPopular` snapshot | Isse niche/growth verdict nahi banaya (movie/music/GTA trailers dominate karte hain) |
| Third-party **published** transcript/summary pages ko clearly label kar ke craft notes | Unhe "API transcript" keh kar pesh nahi kiya |
| Original production blueprint (apna script, apna EDL, apni QC) | Upload/publish, monetisation outcome, legal clearance, human approval, guaranteed views, family-safety guarantee, perfection |

**Technical/API QC PASS = creative approval nahi.** Insan ko abhi bhi candidate videos full-motion dekhne, har asset ka rights-page check karne aur script ko fact-check karne ki zaroorat hai. Competitor videos sirf research ke liye third-party copyrighted works hain; inka koi clip hamare source footage mein nahi jata.

---

## 2. Real API evidence chain (kaise "ache se API se" kiya)

Local sandbox mein Actions secret ki value padhne ki ijazat nahi thi (`gh secret list` HTTP 403; `workflow_dispatch` bhi 403). Isliye key **sirf GitHub Actions ke andar** resolve hui, masked environment variable ke through; `run.json` mein sirf `key_present: true` aur `secret_value_printed_or_stored: false` hai.

| Cheez | Value |
| --- | --- |
| Workflow | `.github/workflows/yt-next-level-forensic-v17.yml` (push-path trigger `v17-next-level-trigger.txt`) |
| Main run | `43154123271` — 3m58s, tamam steps ✓, HARD QC PASS, artifact + evidence auto-commit |
| Script | `research/next_level_niche_v17/build_next_level_forensic_v17.py` (compiled `COMPILE_OK`, Actions ne execute kiya) |
| Commit (workflow) | `889665c` → push `726a464..889665c` |
| Fallback workflow | `.github/workflows/yt-transcript-fallback-v17.yml` (naya marker `v17-transcript-trigger.txt`) |
| Fallback run | `43155064668` — 3m33s, ✓ (nonfatal warning: 0 usable captions) |
| Fallback commit | `804a6c9` → evidence auto-commit `c7ed755` |
| `run.json` | `generated_utc 2026-11-12T04:24:09Z`, `key_present true`, `secret_value_printed_or_stored false` |
| Quota | ~`2098` units: videoCategories 1, search 20, videos 48, channels 17, playlistItems 20, commentThreads 12 |
| Counts | 20 lanes, 927 lane rows, 1,567 unique videos, 822 channels, 4 regions, 32 categories, 418 >=1M, 99 >=10M, 415 title-safe candidates, 12 comment videos, 12 teardowns, 24 thumbnail stats |

Exact boundary string from `api_evidence/run.json`:

> "Public Data API fields + public metadata only. No competitor video/audio download, no video-frame inspection, no private retention/CTR/RPM, no invented transcripts, no verified growth ranking, no causal virality claim, no legal opinion, no upload/publish/monetisation claim, no guaranteed views, no human approval, no perfection claim."

---

## 3. "Best / growing channels" ka matlab is report mein

YouTube public API **subscriber growth over time** nahi deta. Isliye maine **teen public proxies** use kiye aur har jagah likha ke ye ranking nahi:

1. `newer_channel_created_since_2023` (channel creation date) — 822 mein se **344** channels 2023+ banay gaye.
2. `channel_views / channel_age_days` = cumulative views per channel-day.
3. `channel_views / channel_video_count` = average views per published video; plus 20 sampled channels ke liye `recent_upload_median_views` aur cadence.

### 3.1 Naye channels jinke public numbers sabse zyada nazar aaye (proxy, ranking nahi)

| Channel | Banaya | Age | Subs | Channel views | Videos | Views/day | Views/video |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Rainlit Village | 2026-06-28 | 137d | 0.66M | 437.1M | 126 | 3.19M | 3.47M |
| Dr. Healthcare | 2025-09-12 | 426d | 1.06M | 755.5M | 403 | 1.77M | 1.87M |
| Street Dog Revival | 2025-02-23 | 627d | 0.38M | 974.0M | 1,104 | 1.55M | 0.88M |
| **GeoGlobeTales** | **2023-11-20** | **1,088d** | **2.09M** | **1,644.9M** | **169** | **1.51M** | **9.73M** |
| W Sound | 2024-07-19 | 846d | 0.92M | 1,165.7M | 11 | 1.38M | **105.97M** |
| Health Manager | 2025-04-01 | 590d | 0.76M | 777.8M | 399 | 1.32M | 1.95M |
| Nature Global | 2024-03-08 | 979d | 2.39M | 748.1M | 882 | 0.76M | 0.85M |
| Tarazai | 2025-01-13 | 668d | 0.26M | 506.8M | 214 | 0.76M | 2.37M |
| Howtown | 2024-03-22 | 965d | 1.44M | 256.0M | 119 | 0.27M | 2.15M |
| Geo All Day | 2023-11-24 | 1,084d | 0.39M | 296.6M | 237 | 0.27M | 1.25M |

**Sabse important derived signal:** 418 million-view videos mein se jo **2023+ banaye gaye channels** se aaye, unki lane-wise tafseel:

| Lane | Million-view videos from newer channels |
| --- | ---: |
| **map_animation_all** | **8** |
| animal_rescue_all | 7 |
| satisfying_all | 5 |
| viral_breakdown_recent | 2 |

`GeoGlobeTales` akele **6** million-view videos ke saath corpus mein hai (2.09M subs, 1.6449B channel views, 169 videos ≈ 9.73M views/video). Ye "legacy media" nahi, 2023 ka bana hua channel hai. Isi ne map/geo ko "next-level" banaya.

### 3.2 Purane bade channels (cumulative views) — inse growth mat samajhna

Top cumulative: T-Series 316M subs / 363B views, T-Series Bhakti Sagar, Tips Official, Shorts Break 48.9M subs / 44.05B views / recent median 1.75M views / cadence 1.4d, Tech Master 36.4M subs / recent median 4.08M views / cadence 1.0d, Daily Dose Of Internet recent median 1.64M / 2.0d, Techno Gamerz recent median 8.74M / 2.2d. Ye **size** hai, **growth ranking** nahi.

### 3.3 `mostPopular` 4 regions — kyun isse niche nahi chuna

| Region | Top 3 (views) |
| --- | --- |
| US / GB | `Maatrubhumi` trailer 30.93M, GTA VI Pre-Load 9.46M, GTA VI Features 5.07M |
| IN | `Maatrubhumi` 30.93M, GTA VI Pre-Load 9.46M, GTA 5 LIVE 7.44M |
| PK | `KING: Tu Mil Jaaye` 74.85M, `Mahiya` 67.60M, `Eetha` trailer 42.97M |

Yahan film/music/game trailers dominate karte hain. Isliye maine isse "log kya banana chahte hain" ka verdict nahi banaya; ye sirf ye batata hai ke **big-budget release** aur **evergreen explainer** alag alag game hain.

---

## 4. Poore 20 lanes ka 10x data (API `search.list` + `videos.list`)

`med` = median views, `top3` = top 3 videos ka total-view share (kam = zyada entry room), `win/med` = top video / median (kam = skewed nahi), `fresh30` = 30 din ke andar publish share, `<=3m` = 180s ya chhote, `cap` = `contentDetails.caption=true` share.

| Lane | n | Total | Med | Top3 | Win/med | >=1M | >=10M | Fresh30 | Med dur | <=3m | Cap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ai_tutorial_all | 50 | 70.08M | 619.3k | .393 | 25.0 | 13 | 1 | .000 | 53s | .66 | .16 |
| ai_tutorial_recent | 50 | 0.38M | 5 | .837 | 29687 | 0 | 0 | 1.000 | 247s | .44 | .08 |
| microdrama_all | 50 | 82.77M | 819.4k | .383 | 22.7 | 21 | 1 | .200 | 148s | .58 | .04 |
| microdrama_recent | 50 | 3.74M | 3.1k | .601 | 427.7 | 1 | 0 | .820 | 80s | .80 | .00 |
| science_humor_all | 50 | 287.15M | 962.9k | .567 | 73.4 | 25 | 7 | .020 | 60s | .68 | .02 |
| science_humor_recent | 22 | 0.62M | 803 | .981 | 682.9 | 0 | 0 | .227 | 59s | .682 | .045 |
| satisfying_all | 50 | 1,064.34M | 10.188M | .344 | 14.9 | 50 | 25 | .000 | 179s | .54 | .12 |
| satisfying_recent | 50 | 0.17M | 340 | .804 | 276.3 | 0 | 0 | 1.000 | 25s | .96 | .00 |
| animal_rescue_all | 50 | 1,156.95M | 10.895M | .402 | 21.0 | 49 | 25 | .000 | 66s | .66 | .06 |
| animal_rescue_recent | 50 | 10.66M | 1.46k | .916 | 2239.6 | 3 | 0 | .932 | 17s | .98 | .00 |
| viral_breakdown_all | 49 | 16.69M | 153.0k | .297 | 19.6 | 2 | 0 | .102 | 552s | .449 | .102 |
| viral_breakdown_recent | 50 | 55.73M | 257.3k | .713 | 79.0 | 7 | 2 | .340 | 38s | .82 | .04 |
| **map_animation_all** | **50** | **529.86M** | **5.858M** | **.252** | **8.1** | **50** | **15** | .000 | **277s** | **.42** | **.28** |
| **map_animation_recent** | **17** | **14.59M** | **210.6k** | .727 | 19.8 | **5** | 0 | .235 | 109s | .706 | .00 |
| mini_doc_all | 39 | 18.05M | 234.6k | .349 | 11.6 | 5 | 0 | .128 | 834s | .282 | .103 |
| mini_doc_recent | 50 | 11.26M | 112.2k | .338 | 13.2 | 2 | 0 | .531 | 1432s | .24 | .18 |
| faceless_comedy_all | 50 | 39.83M | 11.0k | .861 | 1548.3 | 4 | 2 | .000 | 97s | .60 | .08 |
| faceless_comedy_recent | 50 | 3.61M | 3.9k | .456 | 225.1 | 0 | 0 | .300 | 106s | .52 | .02 |
| sleep_ambient_all | 50 | 31.69M | 37.3k | .443 | 177.3 | 8 | 0 | .000 | 2142s | .30 | .06 |
| sleep_ambient_recent | 50 | 12.37M | 1.07k | .939 | 6735.1 | 2 | 0 | .935 | 35s | .90 | .00 |

**Corpus-wide (418 million-view videos):** median views `4,222,851`, median duration `180s`, <=3min share `50.0%`, caption-flag true `10.3%`, English default language `96.7%`, median like rate `0.0163`, median comment rate `0.00024`. Title tokens: `shorts 59, geography 38, satisfying 35, rescue 35, science 30, asmr 29, official 27, restoration 25, shortsbreak 24, comedy 19, funny 18, story 16, future 16`. Tags: `animals 44, viral shorts 40, science 40, youtube shorts 37, tech master 36, trending shorts 33, tiktok 32, geography 18`. Description patterns: `link 286, subscribe 191, follow 117, discord 62, comment 45, credits 44, ai 35, part2 36, patreon 19, chapters 17, voice 8`.

---

## 5. Filter funnel — "viral idea" kaise chuna (koi gut-feeling nahi)

`DECISION_V17.json` mein ye funnel machine-readable hai; `build_v17_decision.py` koi naya API call nahi karta, sirf committed evidence se derive karta hai.

| Filter | Rule | Maqsad |
| --- | --- | --- |
| C1 | all-time lane mein `>=10` videos `>=1M` **aur** `>=1` video `>=10M` | demand depth |
| C2 | `top3_share < 0.60` | winner-takes-all se bachna |
| C3 | `winner_ratio < 100` | median reachable ho |
| C5 | matching recent lane mein `>=1` video `>=1M` | abhi bhi kaam kar raha ho |
| C4 / C6 | qualitative: 100% apne original assets, third-party clip dependency na ho, repetitive-template risk na ho | monetised channel ke liye ownability |

**Numeric result:**

| Lane | C1 | C2 | C3 | C5 | Numeric PASS |
| --- | :-: | :-: | :-: | :-: | :-: |
| ai_tutorial_all | ✓ | ✓ | ✓ | ✗ | ✗ |
| animal_rescue_all | ✓ | ✓ | ✓ | ✓ | ✓ |
| **map_animation_all** | ✓ | ✓ | ✓ | ✓ | ✓ |
| microdrama_all | ✓ | ✓ | ✓ | ✓ | ✓ |
| satisfying_all | ✓ | ✓ | ✓ | ✗ | ✗ |
| science_humor_all | ✓ | ✓ | ✓ | ✗ | ✗ |
| faceless_comedy_all | ✗ | ✗ | ✗ | ✗ | ✗ |
| mini_doc_all | ✗ | ✓ | ✓ | ✓ | ✗ |
| sleep_ambient_all | ✗ | ✓ | ✗ | ✓ | ✗ |
| viral_breakdown_all | ✗ | ✓ | ✓ | ✓ | ✗ |

**Teen numeric winners → qualitative rejection:**

- **animal_rescue_all / recent** — median 10.895M, 49/50 >=1M, 25 >=10M, recent 3 >=1M. Lekin iska raw material **doosron ki animal/rescue footage** hai (rights + reused-content risk), aur user ne "caught on camera" abhi side mein rakhne ko kaha. Isliye reject.
- **microdrama_all / recent** — 21 >=1M, recent 1.33M ka hit. Lekin serialized cast/dubbing/chahiye, `fresh30 0.82` ke saath high-frequency templated output ka inauthentic-content risk, aur har episode ka bulk alag story mangta hai. Reject.
- **map_animation_all / recent** — **50/50 >=1M, 15 >=10M, median 5.858M, total 529.86M, top3 share `.252` (sabse kam), winner/median `8.1` (sabse kam), caption rate `.28` (sabse zyada), recent lane 5/17 >=1M aur 14.59M total**. 100% apne vector maps + apni awaaz + public data se ban sakta hai. **WINNER.**

**Baaki kyun nahi:** `satisfying_all` ka median 10.188M sabse bada hai lekin recent lane mein 0 million-view videos (fresh supply band) aur physical restoration footage 100% ownable nahi; `science_humor_all` 7 >=10M lekin recent 0 aur top3 .567; `ai_tutorial_recent` median **5 views** (fresh demand evidence bilkul kamzor); `viral_breakdown_recent` 55.73M lekin top3 `.713` aur top hits trend/dance clips hain jo series nahi ban pati; `mini_doc_recent` median duration 1432s (heavy production); `faceless_comedy_all` top3 `.861` / win-med `1548` (extreme winner-takes-all); `sleep_ambient` 2142s median aur recent 1.07k median.

---

## 6. Faisla: `NAQSHA FILES — Map Forensics`

### 6.1 Concept

> **"Har ajeeb line, border, naam aur tabahi ke peechhe aik naqsha hai. Hum usse khol kar dekhte hain."**

Do hisson ka hybrid system (API evidence dono ko support karta hai):

| Pillar | Format | API evidence | Maqsad |
| --- | --- | --- | --- |
| **MAP MYSTERY** (evergreen) | 60–96s vertical + 16:9 cut | GeoGlobeTales 61/73/61/76/96/61s videos: 32.02M, 28.97M, 15.64M, 14.20M, 10.80M, 10.43M views | Rozana/haftawari, low-cost, repeatable, original |
| **MAP INCIDENT** (recent) | 6–12min long-form + chapters | `map_animation_recent` top 5: 4.16M, 4.11M, 2.33M, 1.31M, 1.19M views; `u5F175REX_U` 751s/4.11M with 13 chapters | Search + TV + watch-time, authority, series depth |

### 6.2 Exact million-view map/geo videos jinhe microscope mein rakha

| ID | Title | Channel | Views | Dur | Date | Cat |
| --- | --- | --- | ---: | ---: | --- | --- |
| `Gt2mYPwXyAc` | 50 States Song - USA States and Capitals Song | KLT | 47.52M | 298s | 2016-01-11 | 1 |
| `HKdjIFjYZ40` | Why do Rivers Curve? | MinuteMinis | 46.29M | 17s | 2022-06-21 | 27 |
| `libKVRa01L8` | Solar System 101 \| National Geographic | National Geographic | 39.79M | 251s | 2017-08-30 | 24 |
| `t1DECN9zS_8` | Why Do Time Zones Look So Strange | GeoGlobeTales | 32.02M | 61s | 2024-07-03 | 24 |
| `TIP_4hrzLTk` | The Difference Between UAE, Dubai & Abu Dhabi | GeoGlobeTales | 28.97M | 73s | 2025-12-14 | 24 |
| `RSeWI6Ar-j0` | 1.8 billion years in 60 seconds | Howtown | 25.83M | 74s | 2025-04-03 | 28 |
| `lwglySYUuSY` | Hurricanes, Tornadoes, Typhoons... What's the Difference? | GeoGlobeTales | 15.64M | 61s | 2024-09-02 | 24 |
| `cvZls9tcCTI` | The Difference Between New York & NYC | GeoGlobeTales | 14.20M | 76s | 2025-11-16 | 24 |
| `ovyoQMhGsYU` | What If Pangea Came Back? | Geo All Day | 12.48M | 63s | 2025-07-08 | 24 |
| `HA1hs67ThXc` | Why there are 2 Irelands | GeoGlobeTales | 10.80M | 96s | 2026-04-16 | 24 |
| `DjhZuN0woDY` | All Maps are Lying to You | GeoGlobeTales | 10.43M | 61s | 2024-05-01 | 24 |
| `tT-BzWbyqkw` | Why Nobody Can Cross Darien Gap | Geo All Day | 9.72M | 60s | 2024-09-09 | 24 |

Recent-event lane (fresh 2026 evidence): `J_sNJjrN4J4` El Niño 4.16M/78s, `u5F175REX_U` Nepal Floods Explained 4.11M/751s, `RF5Nw4g7AxE` Glacier Collapse 2.33M/136s, `Vr209Lt6_cA` Satellite Images 1.31M/509s, `2tjiaBnx5fE` Cyclone Arnab 1.19M/99s. **5 me se 4 ek hi current-event ko map/satellite se samjhate hain** — ye "next-level" ka sabse taaza signal hai.

### 6.3 Local / unique edge (Hyderabad, Sindh, PK)

Bina kisi unverified fact ke, series ka apna angle: **Indus / Sindh / monsoon / delta / borders / Karachi ki geography** ko Roman Urdu (aur optional English VO) mein samjhana. PK `mostPopular` music/trailers se bhara hai; iska matlab ye nahi ke geo explainer nahi chalega — iska matlab hai ke **big releases ke saath compete na kar ke** evergreen searchable questions par kaam karna. Har number publish se pehle public source se verify karna hoga (blueprint mein `[VERIFY]` tags hain).

### 6.4 Monetised channel ke liye kyun safer *direction* hai (legal clearance nahi)

YouTube ki 2025 "inauthentic content" / reused-content policy mass-produced, generic, repetitive aur bina narrative ke clip compilations ko monetisation ke liye risky batati hai; AI ko automatic disqualification nahi lekin altered/synthetic disclosure chahiye. Is concept mein **har frame apna banaya hua vector map**, **apni research**, **apni awaaz**, **apna script**, **har episode ka alag sawal/alag storyline** hai. Ye **policy direction** hai, **legal opinion ya clearance nahi**; har asset ka licence abhi bhi insan ko check karna hai.

---

## 7. 10x FORENSIC — scripts, clips, editing, packaging, har layer

### 7.1 Layer A — Packaging (API metadata, 100% real)

**Title formula** (GeoGlobeTales ke 6 hits se): `Sawal ya confusion` + `do cheezon ka contrast` + `1 emoji` + `kabhi kabhi "What's the difference / Why / What Are"`.

| Real title | Views | Pattern |
| --- | ---: | --- |
| "Why Do Time Zones Look So Strange 🌍 How They Work 🕒" | 32.02M | Why + strange + how |
| "The Difference Between UAE, Dubai & Abu Dhabi 🇦🇪 What Are the Emirates 🤯" | 28.97M | Difference + 3 nouns + question |
| "🌪️ Hurricanes, Tornadoes, Typhoons, Cyclones & Monsoons 🌧️ What's the Difference?" | 15.64M | 5-item list + difference |
| "The Difference Between New York & NYC 🗽 Manhattan & Long Island 🤯" | 14.20M | Confusion pair + sub-parts |
| "Why there are 2 Irelands 🇮🇪🇬🇧 Ireland vs Northern Ireland 🤯" | 10.80M | Number + vs |
| "All Maps are Lying to You 😱 The Real Size of Counties 🗺️" | 10.43M | Belief challenge |

**Tags:** 20–35 long-tail, topic + entity + `"geography" "maps" "learning" "geography facts" "geo shorts" "history shorts" "viral fact" "map lovers" "geography education"`. Generic `#fyp` ke saath specific entity tags bhi. `t1DECN9zS_8` ke 30 tags mein `time zones, weird borders, utc, greenwich, france, china, map, geography, history, geographic education` — entity density high.

**Description = creator ka apna likha hua mini-script.** Ye hamari sabse qeemti **real script evidence** hai (YouTube `snippet.description` se). `caption=false` hone ka matlab sirf ye hai ke YouTube caption track attach nahi; isse burned-in captions ka pata nahi chalta — main isse "likely" bhi nahi kehta, bas apne blueprint mein burned-in captions rakhta hoon.

**Category:** zyada tar `24 Entertainment`, `27 Education`, `28 Science & Technology`, `1 Film & Animation`. `topic_categories` mein `Knowledge` 57 million-view videos ke saath 4th sabse bada topic hai.

### 7.2 Layer B — Script beats, creator-published descriptions se (verbatim chhote quotes)

`GeoGlobeTales` ki descriptions khud ek 6-beat script structure dikhati hain. Ye **unka likha hua synopsis** hai, kisi ne transcript invent nahi kiya:

| Beat | Kaam | Real example (short quote, public description) |
| --- | --- | --- |
| 1. Hook | Sawal / belief challenge | "Why do time zones look so weird?! 🌍" / "Did you know that all maps are lying to you? 🗺️" |
| 2. Shared baseline | "You probably know..." | "You probably know that the Earth is divided into 24 time zones" |
| 3. Pehla concrete number | Number + proper noun | "prime meridian in Greenwich, 0 UTC"; "about 83,000 square km"; "7 emirates"; "62 counties"; "8.5 million people" |
| 4. Mechanism / cause | "because / the only difference is" | "The only difference is where they form"; "distorts the sizes and proportions of landmasses" |
| 5. Surprise exception | "Imagine if... / Interestingly..." | "Imagine if time zones were perfectly straight lines - cities like Chicago would be split"; "China, despite spanning five time zones, uses just one" |
| 6. Loop close + next curiosity | "Don't miss..." / "which brings up..." | "Uncover why places like Kashgar ... experience darkness even at 10 AM" |

`TIP_4hrzLTk` ka description 73s ke liye ~190 words: `UAE = country → 83,000 km² ≈ Portugal/Austria → 7 emirates → sheikh/monarchy → Federal Supreme Council → President from Abu Dhabi → Abu Dhabi 85% territory → Dubai = different emirate → Burj Khalifa / Dubai Mall / Palm`. Yani **ek hi sawal ke andar 9 chhote facts, har 6–8 second mein ek naya info-drop**. Ye "script density" ka real, API-se-nikala hua measure hai.

`HKdjIFjYZ40` (MinuteMinis, 17s, 46.29M) ka description teen jumlon mein poora causal chain: "Rivers become curvier and curvier until they bump into themselves... What's left over is called an Oxbow lake..." aur end mein community sawal: "Do you have a special term for them in your country?" — **loop close + comment bait**.

### 7.3 Layer C — Long-form chapter beats (creator-published, `u5F175REX_U`, 4.11M / 751s)

Ye 2026-08-28 ka video hai. Iski description ek **poori production blueprint** hai:

```
0:00  A mountain comes apart at 08:37
0:37  Established, disputed, unknown
0:58  Where it happened — and who was there
2:06  It was not an earthquake
2:58  It was not a glacial lake burst
3:50  Stage 1 and 2: the detachment and the fall
5:06  Chamoli, the blockage and the breach
6:17  Bulking: why the flood grew six times
7:00  The gauges stop transmitting
7:40  28 minutes late, then 168 kilometres
8:58  Why there was no warning
10:13 Why this keeps happening to the same river
11:24 What nobody knows yet
```

Forensic reading:

1. **Cold open with exact time + number** (08:37, 168 km, 7.5 hours) — pehle 10 second mein concrete data.
2. **Epistemic labels** — `ESTABLISHED / DISPUTED / UNKNOWN` har point par; "Where the science is unfinished, I say so rather than smoothing it over." Ye misinformation se bachne aur trust banane ka structural trick hai.
3. **Do "ye nahi tha" beats** (2:06, 2:58) — galat jawab pehle todna, phir sahi jawab dena = curiosity gap sustain.
4. **Stage-wise causation** (3:50 → 5:06 → 6:17) — scene/animation har stage ke saath badalta hai.
5. **Failure + consequence** (7:00 gauges, 7:40 delay, 8:58 no warning, 10:13 repeat) — end tak naya sawal.
6. **11:24 "What nobody knows yet"** — sequel/loop.
7. **Disclosure**: "The three-dimensional shots are AI-generated and labelled 'AI SIMULATION' on screen for their full duration... No real footage of the disaster is used in this video." + 14-source list + "No affiliate links. Nothing in this description benefits this channel."

Ye woh "next-level" hai jo main apne concept mein `SAABIT / MUKHTALIF / NA-MALOOM` aur `AI SIMULATION` label ke tor par adopt karta hoon — **copy nahi, format convention**.

Doosre creator-published chapter examples (API descriptions): `ZTimVStLZh0` (10.70M, 1003s) ke 8 restoration steps `00:00 → 00:12 → 00:52 → 01:26 → 01:50 → 02:07 → 03:00 → 03:50`; `xT10kTnYLDQ` (7.58M, 1723s) ke geography class chapters; `d-CuF6dlqLg` (1.92M, 850s) ke 8 tutorial chapters. **97/1075** videos mein 3+ chapter markers mile — chapters long-form ka common, observable grammar hai.

### 7.4 Layer D — Hook / on-screen text / editing craft (third-party PUBLISHED transcript, API captions nahi)

**Pehle hadd:** `reverse_teardowns_v17.json` mein 12/12 `transcript_status: error` (YouTube "Sign in to confirm you're not a bot"), aur fallback `transcript_fallback_run_v17.json` mein 18/18 `RequestBlocked` + alternate `yt-dlp` player clients bhi fail. **Isliye maine koi competitor ka verbatim YouTube transcript nahi likha.** Lekin do **teesre farik ki published, timestamped transcript-derived pages** milin jinhe main clearly label kar ke craft notes ke tor par use karta hoon:

**D1. `Xqy9L-88wcw` — "I Studied 1,000 Hooks..." (hamare corpus mein 0.86M views / 1207s).** Third-party chapter/quote page [2](https://www.studiolayerone.com/i-studied-1-000-hooks-heres-how-to-actually-go-viral/) aur video [1](https://www.youtube.com/watch?v=Xqy9L-88wcw):

| Time | Real craft point (published transcript se) | Hamare blueprint mein |
| --- | --- | --- |
| 00:00 | "bad hooks" sabse bada underperformance reason | Hook pehla 1.5s, koi intro nahi |
| 00:30 / 01:10 | viewer autopilot scroll; judgement fraction-of-a-second | Pehla frame khud sawal ho |
| 01:22 | "open loops ... when one closes, open another" | Har 8–10s mein naya chhota loop |
| 01:56 / 02:53 | spoken hook bina on-screen context = viewer ko topic pata hi nahi; context **top of frame, safe zone** | Top-safe-zone 2–4 word context line |
| 03:29 / 03:51 | context label nahi, **curiosity gap widen** kare; target audience samajhna | "Greenland barabar? 😳" na ke "Map projection lesson" |
| 03:58 | commonly-held belief ko challenge karna strong hook | "Har naqsha jhooth bolta hai" |
| 04:36 | on-screen text **expected se chhota**, medium weight, subject par overlap na ho | 9:16 safe zone, 1 focal anomaly |
| 06:29 | **visual frame khud hook** hai (visual contradiction) | Map par Greenland/Africa ka visual contradiction |
| 08:11 | har hook: care + question + reason to stay + identification | 4-point hook checklist |
| 10:21 / 10:44 | saturated field mein skill nahi, **story** differentiator hai | Har episode ka apna "raaz" |
| 15:16 | cluttered first frame, no focal point = instant confusion | Declutter rule |
| 16:31 | rebuild = plan picture → plan question → declutter → open gap | 4-step pre-edit gate |
| 17:28 / 18:26 | payoff hook mein mat do; solvable loop band loop hai; giveaway blur karo | Answer 60s par, teaser 0s par |

**D2. Johnny Harris craft (third-party published podcast summary, hamare `dIKsEhX-vyU` / "Why every Johnny Harris video goes viral" se related):** thumbnail/title = **promise**, pehle minute mein reinforce, end mein fulfill; predictable "canon language" se bachna; visual thinking; insani kirdaron ko lane ki zaroorat [1](https://videohighlight.com/v/zq4b96m1AvM) [2](https://bulletpointpodcast.com/howiwrite/johnny-harris-reveals-how-he-writes-you-tube-videos/). Ye bhi summary hai, verbatim transcript nahi.

**D3. MinuteEarth "Why Do Rivers Curve?" ka published transcript** (PSU course page [1](https://courses.ems.psu.edu/earth111/node/870), ESL quiz [2](https://eslvideo.com/quiz.php?id=50353)) — **ehyaat:** ye transcript `8a3r-cG8Wic` (2:38 MinuteEarth original) ka hai, hamare corpus wale `HKdjIFjYZ40` (MinuteMinis, 17s) ka exact caption track nahi. Isliye ise **same-title explainer family ka craft comparison** ke tor par rakha hai, corpus video ka transcript claim nahi. Long version: `mountain streams "set in stone" → muskrat burrow → bank slumps → faster water → slower side deposits → outer bank slingshots → "and then another, and then another" → ~6× width meander → oxbow lake → billabong / lago en herradura / bras mort → "what do the Martians call them?"`. 17s Shorts description ne isi chain ko 3 jumlon + 1 community sawal mein compress kiya. **Forensic natija:** long-form causal chain ko Shorts mein "ek mechanism + ek surprising naam + ek sawal" tak compress karna hota hai.

### 7.5 Layer E — Real comments (audience ki awaaz, private analytics nahi)

`comments_v17.json`: 12 videos, 11 par 25 comments, 1 par sirf 1 (`_rhMrhzDzDk` → `mining.status: insufficient`). 2.5% pattern floor; shares sirf fetched comments ke hain, silent majority invisible hai.

| Video | Real signal | Exact evidence |
| --- | --- | --- |
| `VIain9HJZKQ` (135.18M makeup restoration) | sequel demand | "Never thought a makeup channel would have part 2's" (1,674 likes / 44 replies), "You should make makeup repair shop" (1,532 / 38); mining: `asked for a sequel (12%)` |
| `cw8gjwEtdhY` (79.57M hoof restoration) | cost objection + teaching demand | `objected to cost 4%`, `wants to buy time/teaching 4%`; "Who else doesn't understand y this showed up in ur recommended list but ending up watching the whole thing" (25,653 likes / 410 replies) |
| `ncqHtfcgZNw` (70.68M science humor) | pacing/clarity + asset demand | `objected to pacing/clarity 4%`, `wants the asset 4%` |
| `DEpThqSPkgg` (68.47M) | teaching demand | `wants to buy time/teaching 4%` |
| `IpdXfzr0U3c` (151.51M) | creator-pinned engagement | "Comment your country!!" 5,065 likes / 449 replies |
| `T9abiWZZros` (229.12M) | joke/rewatch, koi pattern floor clear nahi | "Buddy was looking for that hole again 😅" 17,392 / 78 |
| 7 aur videos | `nothing cleared the 2.5% floor` | Ye bhi **real finding** hai: zyada comments ≠ brief-able audience |

**Hamare liye:** har episode mein ek **clear sequel/next-question CTA**, ek **"aap ke sheher mein kya kehte hain?"** community sawal, aur **teaching/asset** layer (downloadable map / source list) — lekin koi bhi conversion ya RPM claim nahi.

### 7.6 Layer F — Thumbnails (public image statistics, heuristic)

`thumbnail_forensics_v17.json`, n=24: `face_rate 0.917`, `avg_contrast 0.23`, `avg_brightness 0.312`, `avg_busy 2.51`, `avg_accent_share 0.562`, `avg_lower_text_energy 2.31`, hue families `[(0,17),(3,3),(1,2),(5,1),(2,1)]`. **Ye image stats hain; OCR, face recognition ya video-frame edit analysis nahi.**

Map-specific rows (inme `face_present: false` hai — yani map/animation thumbnails chehra-free bhi chalte hain):

| ID | face | contrast | brightness | dominant | busy | lower text energy |
| --- | :-: | ---: | ---: | --- | ---: | ---: |
| `Gt2mYPwXyAc` (47.52M) | false | 0.198 | 0.286 | `#206a90` blue | 3.72 | 3.20 |
| `HKdjIFjYZ40` (46.29M) | false | 0.198 | 0.286 | `#87b67a` green | 1.17 | 1.22 |
| `libKVRa01L8` (39.79M) | true(heuristic) | 0.188 | 0.160 | `#f8d405` yellow | 1.45 | 0.83 |

**Inference (cautious):** geo/map thumbnails low-clutter + ek dominant color + face-free bhi million-view bante hain. Hamara blueprint isi par: 1280×720, ek focal anomaly, ≤4 words, high-contrast accent, safe zone.

### 7.7 Layer G — Duration / format math

- GeoGlobeTales hits: `61, 73, 61, 76, 96, 61` seconds → **median ~67s**.
- `map_animation_all` median `277s`, `<=3min share 42%`, `caption rate 28%` (sabse zyada), `short_share 42%`.
- Corpus: `median 180s`, `<=3min 50%`, `caption flag true 10.3%`, `English default 96.7%`.
- `map_animation_recent` median `109s`, `<=3min 70.6%`, 5/17 >=1M.

**Natija:** 9:16 master se 60–90s Short **aur** 6–12min chaptered long-form dono nikaalo; dono par burned-in captions; English + Roman Urdu do alag VO tracks (auto-dubbing ka official 2026 option bhi hai, lekin main isse guarantee nahi kehta).

### 7.8 Layer H — Jo "har ek cheez" mein **observe hi nahi** ho saka (isliye invent nahi kiya)

Competitor ke: actual cuts/sec, transition types, keyframe motion, colour grade, B-roll ratio, music/SFX, loudness, caption animation, first-frame retention, retention curve, CTR, impressions, RPM, A/B thumbnail result, upload time, private audience demographics. In sab ko maine **"not observed"** likha hai, koi andaza nahi lagaya. Isi liye neeche ka production blueprint **hamari apni** edit spec hai, competitor ki "copy" nahi.

---

## 8. Production blueprint ( Episode 01 — poora, kuch na chhoda )

Poori script, beat-sheet, EDL, asset list, QC aur 30-day plan alag file **`PRODUCTION_BLUEPRINT_V17.md`** mein hai; machine-readable edit list **`EPISODE_01_EDL_V17.json`** mein. Khulasa:

| Cheez | Faisla |
| --- | --- |
| Concept | **"Naqsha jhooth kyun bolta hai? Greenland vs Africa"** (pure cartography, no disaster/politics, 100% original maps) |
| Title options | 5, formula-based (blueprint mein) |
| Master | 75s / 9:16 + 16:9 reframed cut, 30fps, H.264, burned-in captions |
| VO | Original Roman Urdu (primary) + English alt; kisi competitor ka jumla nahi |
| Beats | 12 beats, 0.0–75.0s, har beat par: VO line + on-screen text + map action + SFX + caption + `[VERIFY]` source tag |
| Assets | 12 self-created vector map layers, 0 third-party clips, 0 competitor footage; optional public satellite imagery **sirf licence verify karne ke baad** |
| Labels | `SAABIT / MUKHTALIF / NA-MALOOM` + `AI SIMULATION` on-screen disclosure |
| Thumbnail | 1280×720, 1 anomaly, ≤4 words, `#206a90`-style accent, safe zone |
| Metadata | title, 180–220 word creator-style description, 28 long-tail tags, 5 chapters (long cut), category 27/24 |
| Audio | apna VO, licensed music, -14 LUFS target, no static title/method cards |
| QC | fact-check, rights ledger, policy check, caption timing, loudness, full-motion human watch-through |
| Test plan | 30 din / 8 uploads (6 Shorts + 2 long), sirf public metrics; koi guaranteed views/virality claim nahi |

---

## 9. Jo main ne **nahi** kiya (aur kyun) — final checklist

- ❌ Koi competitor video/audio download, koi frame inspection, koi "clips ka andaza".
- ❌ Koi invented transcript: 12/12 teardowns + 18/18 fallback = `0` usable YouTube captions (`RequestBlocked` / sign-in bot-check). Jo craft notes hain wo **creator-published descriptions** ya **clearly labelled third-party published pages** se hain.
- ❌ "Verified fastest-growing channels" ranking; sirf public age/views/cadence proxies.
- ❌ Private retention / CTR / RPM / impressions / monetisation outcome.
- ❌ Causal "isliye viral hua" claim; correlations aur corpus shape sirf.
- ❌ Upload / publish / release / legal clearance / human creative approval / family-safety guarantee.
- ❌ Guaranteed views, guaranteed virality, perfection, "koi kami nahi" ka absolute claim. Haan: **har layer ko cover kiya, aur jo cover na ho saka usse naam de kar chhoda** — yehi is report ka "bagair kisi kami ke" ka amal hai.
- ❌ `mostPopular` ko niche verdict banana; `channel_statistics` ke cumulative giants ko growth kehna.
- ❌ Purana "caught on camera" / V16 clip pool dobara use karna (user ne side mein rakhne ko kaha).

---

## 10. Files, commits, runs

| File / ID | Kya hai |
| --- | --- |
| `api_evidence/run.json` | API run counts + boundary |
| `api_evidence/lane_metrics_v17.json`, `lanes_v17.json` | 20 lanes, raw IDs, metrics |
| `api_evidence/video_details_v17.json` | 1,075 videos ke full public fields + descriptions |
| `api_evidence/million_view_videos_v17.json` | 418 >=1M videos |
| `api_evidence/channel_statistics_v17.json` | 822 channels |
| `api_evidence/recent_uploads_v17.json` | 20 sampled channels ke 25 recent uploads |
| `api_evidence/comments_v17.json` | 12 videos ke public comments + mining |
| `api_evidence/thumbnail_forensics_v17.json` | 24 thumbnail stats |
| `api_evidence/most_popular_v17.json` | US/PK/GB/IN snapshots |
| `api_evidence/reverse_teardowns_v17.json` | 12 receipts, 12 transcript errors |
| `api_evidence/transcript_teardowns_v17.json`, `transcript_fallback_run_v17.json` | 18 targets, 0 usable, honest error log |
| `FORENSIC_REPORT_V17.md` | generated data appendix |
| `TRANSCRIPT_FORENSICS_V17.md` | fallback access report |
| `build_v17_decision.py` → `DECISION_V17.json` | reproducible filter funnel + derived evidence |
| **`FINAL_FORENSIC_REPORT_V17_ROMAN_URDU.md`** | ye file (final Roman Urdu jawab) |
| **`PRODUCTION_BLUEPRINT_V17.md`**, **`EPISODE_01_EDL_V17.json`** | original script + edit plan |
| Runs | `43154123271` (main API), `43155064668` (fallback) |
| Commits | `889665c` (workflow), `804a6c9` (fallback workflow), `c7ed755` (evidence auto-commit) |

---

## 11. Aakhri baat (Roman Urdu)

Bhai, **channel monetized hai to ab "clip jama karo" wala game chhorna hai**. Real API ne sabse saaf signal diya: **map/geo explainers** mein 50 me se 50 videos 1M+ hain, 15 videos 10M+, median 5.86M, top-3 ka hissa sabse kam (25.2%), aur 2023+ ke naye channels se aane wale million-view videos ki sabse badi tally bhi isi lane mein (8) hai. Upar se 2026 ki recent map lane mein 5 naye 1M+ videos hain — matlab format abhi zinda hai. Iske muqable mein animal/rescue ko doosron ki footage chahiye (aur aap ne caught-on-camera side mein rakha hai), satisfying ka fresh supply band hai, AI tutorial ka recent median 5 views hai, faceless comedy winner-takes-all hai.

Isliye **NAQSHA FILES — Map Forensics** shuru karo: 60–90s ka "naqshe ka raaz" + 6–12min ka "abhi kya hua, pehli report kyun ghalat thi" with `SAABIT / MUKHTALIF / NA-MALOOM`. Har frame apna, har awaaz apni, har number verify-shuda, har episode ka apna sawal. Ye **evidence-backed viral-potential idea** hai — views ki guarantee nahi, legal clearance nahi, upload nahi, aur technical QC ko creative approval mat samajhna. Insani watch-through, fact-check aur rights review abhi baqi hai. Poora blueprint agali file mein tayyar hai.
