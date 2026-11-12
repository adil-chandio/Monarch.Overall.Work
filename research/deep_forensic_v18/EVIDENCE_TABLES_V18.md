# V18.1 Evidence Tables — real YouTube Data API forensic

Ye machine-generated local appendix hai. Isme koi naya API call nahi; sab kuch `api_evidence/` aur `FORENSIC_EVIDENCE_EXTRACT_V18.json` se aata hai. Roman Urdu report ka har numeric claim yahan trace hota hai.

## 1. Run receipt aur integrity

| Field | Value |
| --- | --- |
| GitHub Actions run | 43249117208 — success, HARD QC PASS, 5m37s |
| Generated UTC | 2026-11-12T15:39:12Z |
| Raw unique videos | 2,347 |
| Run unique videos | 2,347 |
| Manifest unique videos | 2,347 |
| Description records | 717 |
| Description IDs missing from raw | 0 |
| Candidate videos after title safety | 717 |
| Deep teardowns | 40 |
| Comment request records | 40 ({'error': 1, 'ok': 23, 'not_requested': 16}) |
| Transcript attempts | 12 {'error': 12} |
| Thumbnail stats | 40 |
| Quota approx | 2,549 |
| Raw descriptions capped at | 6,000 characters |

## 2. 24 lane definitions aur metrics

`viewCount`-ordered lanes high-view-conditioned hain; `date`-ordered recent lanes freshness-conditioned hain. Median ko expected performance na samjha jaye.

| Lane | Bucket | n | Median views | Total views | Top3 | Winner/median | >=1M | >=10M | Fresh30d | Med dur s | Caption | Like | Comment | Order | Days |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| map_geo_short_all | short | 50 | 6,629,829 | 518,882,555 | 0.22 | 7.0 | 48 | 14 | 0.0 | 59 | 0.14 | 0.02598 | 0.00019 | viewCount |  |
| map_geo_medium_all | medium | 50 | 1,739,746 | 457,514,907 | 0.605 | 94.0 | 39 | 6 | 0.0 | 537 | 0.4 | 0.01213 | 0.00039 | viewCount |  |
| map_geo_long_all | long | 50 | 1,520,173 | 131,080,532 | 0.26 | 10.1 | 32 | 2 | 0.0 | 3962 | 0.08 | 0.02402 | 0.00108 | viewCount |  |
| science_explainer_short_all | short | 50 | 49,787,595 | 4,191,070,041 | 0.362 | 19.0 | 50 | 50 | 0.0 | 55 | 0.08 | 0.01917 | 8e-05 | viewCount |  |
| science_explainer_medium_all | medium | 50 | 3,112,668 | 451,733,926 | 0.285 | 18.6 | 37 | 16 | 0.0 | 627 | 0.3 | 0.00415 | 6e-05 | viewCount |  |
| science_explainer_long_all | long | 42 | 1,049,704 | 381,786,661 | 0.657 | 160.7 | 21 | 7 | 0.095 | 2810 | 0.119 | 0.00241 | 3e-05 | viewCount |  |
| satisfying_restoration_short_all | short | 50 | 22,923,251 | 2,314,323,525 | 0.346 | 14.4 | 49 | 45 | 0.02 | 57 | 0.0 | 0.02065 | 5e-05 | viewCount |  |
| satisfying_restoration_medium_all | medium | 50 | 3,636,834 | 516,994,919 | 0.333 | 21.9 | 50 | 14 | 0.0 | 828 | 0.08 | 0.00828 | 0.00029 | viewCount |  |
| satisfying_restoration_long_all | long | 50 | 3,555,890 | 310,335,220 | 0.447 | 24.0 | 50 | 4 | 0.0 | 2084 | 0.16 | 0.01049 | 0.00038 | viewCount |  |
| animal_rescue_short_all | short | 50 | 7,480,717 | 1,013,558,259 | 0.459 | 30.6 | 49 | 19 | 0.02 | 41 | 0.12 | 0.00822 | 0.00015 | viewCount |  |
| animal_rescue_medium_all | medium | 50 | 73,655 | 207,434,403 | 0.508 | 581.2 | 16 | 6 | 0.0 | 478 | 0.08 | 0.01403 | 0.00063 | viewCount |  |
| animal_rescue_long_all | long | 50 | 330,642 | 162,543,885 | 0.531 | 120.2 | 16 | 6 | 0.04 | 1879 | 0.12 | 0.00877 | 0.00031 | viewCount |  |
| viral_breakdown_short_all | short | 25 | 74,189 | 4,956,482 | 0.54 | 14.7 | 1 | 0 | 0.174 | 51 | 0.16 | 0.0196 | 0.00048 | viewCount |  |
| viral_breakdown_medium_all | medium | 50 | 42,332 | 11,713,796 | 0.568 | 70.8 | 2 | 0 | 0.14 | 593 | 0.02 | 0.02808 | 0.00203 | viewCount |  |
| viral_breakdown_long_all | long | 33 | 1,695 | 3,952,520 | 0.592 | 505.4 | 0 | 0 | 0.062 | 1543 | 0.121 | 0.03283 | 0.00107 | viewCount |  |
| microdrama_short_all | short | 50 | 463,280 | 60,277,276 | 0.517 | 40.2 | 13 | 1 | 0.32 | 105 | 0.0 | 0.01264 | 8e-05 | viewCount |  |
| microdrama_medium_all | medium | 50 | 592,224 | 50,482,157 | 0.231 | 8.1 | 16 | 0 | 0.0 | 527 | 0.04 | 0.0 | 5e-05 | viewCount |  |
| microdrama_long_all | long | 50 | 190,957 | 40,407,888 | 0.546 | 61.8 | 8 | 1 | 0.26 | 3695 | 0.12 | 0.00862 | 0.00018 | viewCount |  |
| map_geo_recent | any | 50 | 35,302 | 11,269,385 | 0.658 | 118.2 | 3 | 0 | 0.489 | 78 | 0.0 | 0.01188 | 0.00061 | date | 365 |
| science_explainer_recent | any | 50 | 1,436 | 373,969,670 | 0.475 | 78309.8 | 18 | 13 | 0.04 | 55 | 0.06 | 0.01523 | 8e-05 | date | 365 |
| satisfying_restoration_recent | any | 50 | 924 | 9,067,712 | 0.99 | 6662.6 | 2 | 0 | 0.949 | 14 | 0.04 | 0.00589 | 0.0 | date | 365 |
| animal_rescue_recent | any | 50 | 6,663 | 11,290,932 | 0.697 | 673.1 | 4 | 0 | 0.652 | 84 | 0.0 | 0.0086 | 0.0 | date | 365 |
| viral_breakdown_recent | any | 22 | 99,855 | 4,122,295 | 0.47 | 8.0 | 0 | 0 | 0.2 | 678 | 0.0 | 0.02985 | 0.00209 | date | 365 |
| microdrama_recent | any | 50 | 1,011 | 1,596,362 | 0.881 | 1316.5 | 1 | 0 | 0.979 | 70 | 0.0 | 0.01422 | 0.0 | date | 365 |

### Lane queries

| Lane | Query | videoDuration |
| --- | --- | --- |
| map_geo_short_all | map animation geography explained | short |
| map_geo_medium_all | map animation geography explained | medium |
| map_geo_long_all | map animation geography explained | long |
| science_explainer_short_all | science experiment explained funny | short |
| science_explainer_medium_all | science experiment explained funny | medium |
| science_explainer_long_all | science experiment explained funny | long |
| satisfying_restoration_short_all | oddly satisfying restoration | short |
| satisfying_restoration_medium_all | oddly satisfying restoration | medium |
| satisfying_restoration_long_all | oddly satisfying restoration | long |
| animal_rescue_short_all | animal rescue caught on camera | short |
| animal_rescue_medium_all | animal rescue caught on camera | medium |
| animal_rescue_long_all | animal rescue caught on camera | long |
| viral_breakdown_short_all | viral video breakdown analysis | short |
| viral_breakdown_medium_all | viral video breakdown analysis | medium |
| viral_breakdown_long_all | viral video breakdown analysis | long |
| microdrama_short_all | microdrama short series | short |
| microdrama_medium_all | microdrama short series | medium |
| microdrama_long_all | microdrama short series | long |
| map_geo_recent | map animation geography explained 2026 | None |
| science_explainer_recent | science experiment explained funny 2026 | None |
| satisfying_restoration_recent | oddly satisfying restoration 2026 | None |
| animal_rescue_recent | animal rescue caught on camera 2026 | None |
| viral_breakdown_recent | viral video breakdown analysis 2026 | None |
| microdrama_recent | microdrama short series 2026 | None |

## 3. Cross-bucket: Short vs Medium vs Long (717 million-view candidates)

| Bucket | n | Median views | Total views | >=10M | Med dur s | Like | Comment | Caption | Synopsis | Chapters>=3 | Desc words | Med tags | Zero tags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| short | 348 | 9,876,994 | 12,021,720,795 | 171 | 58 | 0.01784 | 0.00012 | 0.075 | 0.29 | 0.006 | 44 | 7 | 0.402 |
| medium | 184 | 3,155,452 | 1,798,799,663 | 45 | 610 | 0.00734 | 0.0002 | 0.196 | 0.467 | 0.098 | 112 | 17 | 0.13 |
| long | 185 | 2,540,517 | 1,147,042,230 | 21 | 3147 | 0.0084 | 0.00025 | 0.141 | 0.649 | 0.227 | 146 | 15 | 0.168 |

### Hook types by bucket

| Bucket | Statement | Number | Belief | Question | List | Comparison |
| --- | --- | --- | --- | --- | --- | --- |
| short | 216 | 29 | 53 | 30 | 17 | 3 |
| medium | 102 | 39 | 19 | 10 | 14 | 0 |
| long | 59 | 89 | 17 | 2 | 17 | 1 |

### CTA counts by bucket (regex Boolean, overlapping)

| Bucket | subscribe | comment | follow | link | part2 | credits | chapters | ai | disclaimer | affiliate | newsletter | donate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| short | 64 | 19 | 51 | 100 | 15 | 23 | 0 | 10 | 19 | 0 | 1 | 2 |
| medium | 95 | 16 | 35 | 125 | 13 | 13 | 12 | 1 | 5 | 12 | 2 | 7 |
| long | 115 | 8 | 42 | 122 | 37 | 14 | 16 | 4 | 8 | 8 | 3 | 0 |

### Title pattern rates by bucket

| Bucket | Med chars | Med words | number | question_mark | hashtag | ellipsis | vs | how_to | worlds | levels | part_or_episode | superlative | shorts_word | emoji |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| short | 64 | 9 | 0.195 | 0.106 | 0.503 | 0.034 | 0.034 | 0.04 | 0.014 | 0.003 | 0.014 | 0.072 | 0.181 | 0.328 |
| medium | 56 | 8 | 0.304 | 0.033 | 0.06 | 0.016 | 0.011 | 0.005 | 0.022 | 0.0 | 0.016 | 0.12 | 0.0 | 0.043 |
| long | 66 | 9 | 0.551 | 0.027 | 0.286 | 0.011 | 0.011 | 0.022 | 0.0 | 0.0 | 0.027 | 0.124 | 0.076 | 0.184 |

### Top tags by bucket

- **short**: geography (33), shorts (28), history (28), life hacks (27), jay finds things (26), jayfindsthings (26), cool products (26), life hack (26), maps (25), gadgets (24), asmr (24), learn (23)
- **medium**: restoration (27), science (17), asmr (17), science experiments (16), satisfying (16), relationship drama (13), experiments (12), farrier (12), oddly satisfying (12), episodic tv (12), tv stories (12), serial drama (12)
- **long**: asmr (37), satisfying (36), diy (28), relaxing (26), restoration (25), satisfying video (24), satisfying makeup (17), makeup (17), makeup repair (17), cosmetic repair (17), satifying asmr (17), oddly (16)

### Top title tokens by bucket

- **short**: asmr (74), science (65), experiment (61), satisfying (45), geography (38), funny (36), ashusir (34), scienceandfun (29), oddlysatisfying (25), map (25), rescue (24), restoration (22)
- **medium**: science (41), geography (33), restoration (32), experiments (31), satisfying (26), asmr (22), hoof (21), drama (16), song (15), micro (14), story (14), farrier (13)
- **long**: satisfying (39), granny (38), geography (36), live (35), makeup (29), science (24), repair (24), gta (23), gta5 (21), gtav (21), gaming (21), asmr (19)


## 4. Top 25 million-view candidates (full 717 index in JSON extract)

| # | Views | ID | Sec | Bucket | Channel | Title | Hook | Words | Chap | Tags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 947,286,603 | -xasdJzBVpo | 60 | short | Vlad and Niki | Kids are making a volcano - Cool Science Experiment! | statement | 8 | 0 | 13 |
| 2 | 702,207,930 | F1_aOX0acbY | 150 | short | W Sound | W Sound 05 "LA PLENA" - Beéle, Westcol, Ovy On The Drums | statement | 373 | 0 | 30 |
| 3 | 366,676,533 | jfUU24gaqNg | 36 | short | Mark Rober | 3 Levels of Elephant Toothpaste | statement | 0 | 0 | 0 |
| 4 | 331,133,432 | ZuA1yaHDB_A | 12 | short | Sam Marlow Farrier Life | Horse needs its crunchy chestnut removed by a farrier ! #horse #asmr … | statement | 0 | 0 | 0 |
| 5 | 279,870,018 | huQIyJ1ymEQ | 55 | short | JayFindsThings | The World's Softest Cushion... | belief_challenge | 16 | 0 | 14 |
| 6 | 269,457,699 | qR7vPGcP_ko | 54 | short | JayFindsThings | How To Remove a Stain | belief_challenge | 16 | 0 | 7 |
| 7 | 257,565,435 | HSWrqJTDn8o | 58 | short | JayFindsThings | Money Inside Soap? | belief_challenge | 16 | 0 | 7 |
| 8 | 239,076,269 | GpRLQ-QizQQ | 24 | short | Oddly Satisfying | Hot Metal Balls Video by Oddly Satisfying #asmr #satisfying #satisfyi… | belief_challenge | 34 | 0 | 0 |
| 9 | 230,897,856 | xZco3o0HLZc | 58 | short | Satisfying Shorts | #shorts Fixing Broken Chanel Blush pt1 #cosmeticrepair#satisfying#asm… | belief_challenge | 33 | 0 | 30 |
| 10 | 229,123,816 | T9abiWZZros | 31 | short | The Pet Collective | Cute Armadillo Rescued From Hole! | list | 145 | 0 | 13 |
| 11 | 203,657,158 | 5PTL5N5c4jc | 11 | short | Sick Science! | Square Bubble | question | 89 | 0 | 20 |
| 12 | 188,296,206 | 4aWjjSKAQig | 48 | short | JayFindsThings | How to Make Paper Dart | belief_challenge | 16 | 0 | 9 |
| 13 | 184,725,560 | -FmaF5KnJ4c | 44 | short | TAMU Physics & Astronomy | Water defies gravity. But how?! 💧👍 #shorts #DrTatiana #science | statement | 94 | 0 | 30 |
| 14 | 182,753,889 | 1GDkjZm6coU | 10 | short | Story Arc Paws | Heart-touching Cute Kitten Dance 🐾 #shorts #kittenrescue #animalrescu… | statement | 3 | 0 | 0 |
| 15 | 175,359,996 | Mqx1PUUAAjg | 54 | short | JayFindsThings | African Teeth Whitening Hack... | belief_challenge | 16 | 0 | 13 |
| 16 | 174,636,394 | 7Wx_2kGHqUA | 56 | short | JayFindsThings | Illegal Dice Trick... #lifehacks | belief_challenge | 17 | 0 | 7 |
| 17 | 172,988,074 | yqmmI_NXxEI | 56 | short | JayFindsThings | Small VS Giant Paper Popper | belief_challenge | 16 | 0 | 13 |
| 18 | 172,400,704 | Bt_VZpxWQGU | 43 | short | JayFindsThings | How To Make Mosquito Snapper | statement | 9 | 0 | 13 |
| 19 | 168,635,831 | pFeanxO4-E8 | 1907 | long | Ryan's World | Ryan learns Easy DIY Science Experiment for Kids with how to make a h… | statement | 29 | 0 | 14 |
| 20 | 163,566,319 | B1J6Ou4q8vE | 843 | medium | Alan Becker | Animation vs. Math | question | 62 | 0 | 0 |
| 21 | 154,169,851 | 29v8Da8mhF4 | 14 | short | Ross Smith | Science Experiment Fail #science #fail #bowling | statement | 0 | 0 | 0 |
| 22 | 153,158,880 | qJdp60LGHf8 | 59 | short | JayFindsThings | How To Breath Underwater | statement | 48 | 0 | 11 |
| 23 | 151,521,198 | IpdXfzr0U3c | 51 | short | Dr. Abdom Fora | Indirect dental restoration #satisfying | list | 11 | 0 | 14 |
| 24 | 142,397,726 | gCjA_3umNpg | 60 | short | Science and fun | Concept of Buoyant force I Ashu Sir #scienceexperiment #shorts #physi… | statement | 0 | 0 | 0 |
| 25 | 135,180,871 | VIain9HJZKQ | 55 | short | Satisfying Shorts | #shorts Relaxing Makeup Restoration pt1 #satisfying#oddly#oddlysatisf… | belief_challenge | 33 | 0 | 30 |

## 5. Newer-channel million-view rows by lane (public created-since-2023 proxy)

| Lane | Bucket | Lane n | >=1M rows | Newer-channel >=1M | Top newer channels |
| --- | --- | --- | --- | --- | --- |
| map_geo_short_all | short | 50 | 48 | 17 | GeoGlobeTales (4), Geo All Day (2), Mini Maps (1), Howtown (1), Aaj_K… |
| microdrama_medium_all | medium | 50 | 16 | 16 | Story TV (14), Wow TV - Hindi (1), Jaldi Jaldi Productions (1) |
| animal_rescue_short_all | short | 50 | 49 | 14 | Nature Global (2), Vivid Venture (2), Story Arc Paws (1), Tarazai (1)… |
| satisfying_restoration_short_all | short | 50 | 49 | 13 | Cosmetic Plus (3), FPS (2), FuFu Squishy (1), FUFUSQUISHY_PACKINGORDE… |
| satisfying_restoration_long_all | long | 50 | 50 | 5 | Cleaning Vibe (2), Cosmetic Lab (1), UNSORTED (1), Needs Detail (1) |
| satisfying_restoration_medium_all | medium | 50 | 50 | 4 | Cleaning Vibe (2), Make It Clean (1), Polina Yasinsky (1) |
| microdrama_short_all | short | 50 | 13 | 4 | Casey’s Journey (2), Story TV (2) |
| microdrama_long_all | long | 50 | 8 | 4 | Kuku TV (2), Circuit Dramas (1), ShortMax - Watch Dramas & Show (1) |
| map_geo_long_all | long | 50 | 32 | 2 | SSC Guru Talks (1), The Study Zone (1) |
| science_explainer_short_all | short | 50 | 50 | 2 | Tusher ABC (1), JayFindsThings (1) |
| animal_rescue_medium_all | medium | 50 | 16 | 1 | 𝐅𝐨𝐫𝐞𝐯𝐞𝐫 𝐏𝐚𝐰𝐬. (1) |
| viral_breakdown_medium_all | medium | 50 | 2 | 1 | The Internet Stamp (1) |
| map_geo_recent | any | 50 | 3 | 1 | GeoGlobeTales (1) |
| map_geo_medium_all | medium | 50 | 39 | 0 |  |
| science_explainer_medium_all | medium | 50 | 37 | 0 |  |
| science_explainer_long_all | long | 42 | 21 | 0 |  |
| animal_rescue_long_all | long | 50 | 16 | 0 |  |
| viral_breakdown_short_all | short | 25 | 1 | 0 |  |
| viral_breakdown_long_all | long | 33 | 0 | 0 |  |
| science_explainer_recent | any | 50 | 18 | 0 |  |
| satisfying_restoration_recent | any | 50 | 2 | 0 |  |
| animal_rescue_recent | any | 50 | 4 | 0 |  |
| viral_breakdown_recent | any | 22 | 0 | 0 |  |
| microdrama_recent | any | 50 | 1 | 0 |  |

## 6. Newer channels by million-view corpus hits

| Channel | Created | Subs | Channel views | Videos | >=1M hits | Recent median views |
| --- | --- | --- | --- | --- | --- | --- |
| Story TV | 2025-05-2… | 1,000,000 | 273,065,119 | 743 | 16 | 21,012 |
| GeoGlobeTales | 2023-11-2… | 2,090,000 | 1,645,458,617 | 169 | 5 | 2,889,645 |
| Cleaning Vibe | 2024-02-2… | 88,300 | 16,945,525 | 105 | 4 | — |
| Cosmetic Plus | 2025-05-1… | 559,000 | 496,810,092 | 1,305 | 3 | 5,826 |
| Nature Global | 2024-03-0… | 2,390,000 | 748,076,834 | 882 | 2 | 31,761 |
| FPS | 2024-10-3… | 138,000 | 481,442,880 | 789 | 2 | 32,816 |
| Kuku TV | 2024-11-0… | 1,410,000 | 310,733,779 | 1,603 | 2 | 27,706 |
| Geo All Day | 2023-11-2… | 392,000 | 296,667,877 | 237 | 2 | 244,989 |
| Vivid Venture | 2024-05-1… | 3,250,000 | 252,814,937 | 289 | 2 | 34,938 |
| Casey’s Journey | 2024-08-1… | 50,000 | 47,070,289 | 417 | 2 | — |
| FuFu Squishy | 2023-12-3… | 11,900,000 | 20,861,510,878 | 4,862 | 1 | 414,950 |
| JayFindsThings | 2024-06-0… | 7,760,000 | 6,412,218,292 | 72 | 1 | 44,154,290 |
| FUFUSQUISHY_PACKINGORDER | 2024-04-1… | 3,260,000 | 6,278,709,520 | 3,501 | 1 | 88,112 |
| Street Dog Revival | 2025-02-2… | 378,000 | 974,082,930 | 1,104 | 1 | 23,990 |
| Devi Gausuta Anjali Ji | 2024-04-0… | 722,000 | 527,959,616 | 843 | 1 | 32,502 |
| Tarazai | 2025-01-1… | 257,000 | 506,814,599 | 214 | 1 | 6,432 |
| Marvel Rivals | 2024-02-0… | 1,300,000 | 407,785,409 | 951 | 1 | 169,923 |
| Story Arc Paws | 2024-08-1… | 548,000 | 391,025,327 | 164 | 1 | 475,588 |
| Geo Motion | 2024-09-2… | 213,000 | 274,509,918 | 170 | 1 | 437,777 |
| Howtown | 2024-03-2… | 1,440,000 | 256,016,740 | 119 | 1 | 363,558 |

## 7. Growing-channel public proxies, top 20 of 45

`views_per_channel_day` cumulative views / channel age hai — measured growth nahi.

| Channel | Created | Subs | Channel views | Videos | Views/day proxy | Views/video | Recent n | Recent median | Cadence d | >=1M hits | Newer |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FuFu Squishy | 2023-12-30 | 11,900,000 | 20,861,510,878 | 4,862 | 19,906,021.83 | 4,290,726.22 | 25 | 414,950 | 0.0 | 1 | True |
| JayFindsThings | 2024-06-02 | 7,760,000 | 6,412,218,292 | 72 | 7,180,535.6 | 89,058,587.39 | 25 | 44,154,290 | 7.0 | 1 | True |
| FUFUSQUISHY_PACKINGORDER | 2024-04-15 | 3,260,000 | 6,278,709,520 | 3,501 | 6,672,379.94 | 1,793,404.6 | 25 | 88,112 | 0.0 | 1 | True |
| News Pinch | 2025-04-30 | 2,210,000 | 1,434,333,607 | 6,760 | 2,556,744.4 | 212,179.53 | 25 | 14,189 | 0.0 | 0 | True |
| Street Dog Revival | 2025-02-23 | 378,000 | 974,082,930 | 1,104 | 1,553,561.29 | 882,321.49 | 25 | 23,990 | 0.3 | 1 | True |
| GeoGlobeTales | 2023-11-20 | 2,090,000 | 1,645,458,617 | 169 | 1,512,370.05 | 9,736,441.52 | 24 | 2,889,645 | 5.0 | 5 | True |
| W Sound | 2024-07-19 | 918,000 | 1,165,657,058 | 11 | 1,377,845.22 | 105,968,823.45 | 10 | 15,318,211 | 91.0 | 0 | True |
| Cosmetic Plus | 2025-05-14 | 559,000 | 496,810,092 | 1,305 | 908,245.14 | 380,697.39 | 25 | 5,826 | 0.1 | 3 | True |
| Ashu Ghai Edits | 2024-12-19 | 308,000 | 585,164,249 | 426 | 844,392.86 | 1,373,625.0 | 25 | 36,520 | 2.0 | 0 | True |
| Nature Global | 2024-03-08 | 2,390,000 | 748,076,834 | 882 | 764,123.43 | 848,159.68 | 25 | 31,761 | 1.5 | 2 | True |
| Tarazai | 2025-01-13 | 257,000 | 506,814,599 | 214 | 758,704.49 | 2,368,292.52 | 25 | 6,432 | 1.0 | 1 | True |
| FPS | 2024-10-30 | 138,000 | 481,442,880 | 789 | 647,971.57 | 610,193.76 | 25 | 32,816 | 1.2 | 2 | True |
| Devi Gausuta Anjali Ji | 2024-04-02 | 722,000 | 527,959,616 | 843 | 553,416.79 | 626,286.61 | 25 | 32,502 | 1.0 | 1 | True |
| Mahi daily update | 2026-01-17 | 74,600 | 165,023,424 | 1,882 | 551,917.81 | 87,685.13 | 25 | 4,822 | 0.1 | 0 | True |
| Raajoo Gaming | 2025-09-11 | 214,000 | 219,781,717 | 545 | 514,711.28 | 403,269.21 | 24 | 2,402,878 | 0.8 | 1 | True |
| Story TV | 2025-05-28 | 1,000,000 | 273,065,119 | 743 | 512,317.3 | 367,516.98 | 23 | 21,012 | 0.0 | 16 | True |
| Story Arc Paws | 2024-08-19 | 548,000 | 391,025,327 | 164 | 479,785.68 | 2,384,300.77 | 25 | 475,588 | 2.5 | 1 | True |
| SenpaiUnlimited | 2024-05-29 | 2,010,000 | 387,217,196 | 672 | 431,680.26 | 576,216.07 | 24 | 467,395 | 1.0 | 0 | True |
| Kuku TV | 2024-11-04 | 1,410,000 | 310,733,779 | 1,603 | 421,048.48 | 193,845.15 | 25 | 27,706 | 0.1 | 2 | True |
| Marvel Rivals | 2024-02-05 | 1,300,000 | 407,785,409 | 951 | 403,348.57 | 428,796.43 | 23 | 169,923 | 0.9 | 1 | True |

## 8. Top channels inside 717 title-safe candidates

| Channel | Candidate videos | Newer proxy |
| --- | --- | --- |
| Science and fun | 36 | False |
| GeoGlobeTales | 27 | True |
| JayFindsThings | 26 | True |
| Raajoo Gaming | 20 | True |
| KLT | 16 | False |
| Cosmetic Up | 16 | False |
| Story TV | 16 | True |
| BOBIislive | 12 | True |
| FuFu Squishy | 11 | True |
| Geo Study | 11 | False |
| W Sound | 10 | True |
| Satisfying Shorts | 10 | False |
| Maupin Farrier Co | 10 | False |
| TysyTube Restoration | 10 | False |
| Howtown | 9 | True |
| Elite Restore | 8 | True |
| WD Detailing | 8 | False |
| RESTORED | 8 | False |
| Amit Ashik Personal | 8 | True |
| Ryan's World | 7 | False |
| The Dodo | 7 | False |
| Earthstic | 7 | True |
| Fun Science | 6 | False |
| Geo All Day | 6 | True |
| Sunlike study | 6 | False |

## 9. Description / chapter leaders

Chapter regex time-like lines bhi pakad sakta hai; isliye ye creator-published metadata signal hai, verified spoken structure nahi.

| ID | Chap | Words | Numbers | Bucket | Channel | Title | First chapters |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 26ml5dfmQ4I | 91 | 840 | 185 | long | Daily Dose Of Internet | When People Get Too Close To Animals (Special) | 0:00 Intro; 0:03 bison flings man; 0:15 Suddenly crocodile; 0:20 People Scream in Fear as… |
| t8pcKyc3XbM | 50 | 457 | 106 | long | Fun Science | 100 EASY SCIENCE EXPERIMENTS with Explanation - PART 1… | 0:00 Superabsorbent polymer powder (SAP powder); 0:58 Why is an Alcohol Flame Hard to See… |
| qSuoNeeFjbs | 36 | 479 | 89 | long | The Graphic Earth | Incredible Geography of South India \| India's Most Va… | 0:00 = Intro; 1:46 = Indian Subcontinent Geography; 2:32 = North India's Geographical Wea… |
| pVDqiYIxvdA | 31 | 371 | 78 | medium | Fun Science | 33 AMAZING SCIENCE EXPERIMENTS! Compilation \| Best of… | 0:00 Instantly freeze water trick with HOT-ICE; 0:13 Instantly freeze water trick Freeze … |
| ZADsAhZysqw | 25 | 1466 | 97 | long | The Study Zone | One shot : भारत का भूगोल \| Complete Indian geography … | 0:19 भारत की स्थिति एवं विस्तार; 10:28 भारत का भौतिक विभाजन; 11:32 हिमालय; 18:49 पहाड़ी; … |
| H8uhyuGPQJM | 22 | 249 | 48 | medium | VisioNil | Best 21 Science Experiments Compilation From VisioNil | 00:02 Air Experiment; 00:33 Invisible Flame; 01:10 Candle Powered Fan; 01:38 Colgate Expe… |
| s87FhnwMcD0 | 21 | 222 | 49 | medium | VisioNil | 20 AMAZING SCIENCE EXPERIMENTS Compilation At Home | 00:00 Intro With Magic; 00:44 Candle Tricks; 01:18 Orange Peel Experiment; 01:40 Coanda E… |
| 0ZYhyewNQMo | 20 | 417 | 41 | long | Howtown | What do other animals think of human music? | 00:00 the song; 00:56 the fox; 02:09 what’s music?; 02:56 pitch = rhythm; 05:57 incogni; … |
| JTVxuCGTxE8 | 20 | 141 | 48 | medium | Sunlike study | Drainage Class 9 full chapter (Animation) \| Class 9 G… | 00:00 Drainage; 00:16 Drainage Basin; 00:30 Water Divide; 01:03 Drainage System in India;… |
| ZTimVStLZh0 | 18 | 369 | 45 | medium | MW Restoration | Restoration Gumball Machine Stahlberg 1980s | 00:00 Gumball Machine Restoration/Restore; 00:12 Disassemble Gumball Machine; 00:52 Make … |
| pTDKkOy2KcA | 17 | 477 | 39 | long | Howtown | How to catch an arsonist | 00:00 how do they know?; 01:42 🔥 behavior 101; 03:41 clues!; 05:00 troubling history; 7:0… |
| RRDC1RUTBDw | 16 | 397 | 34 | long | Satisfying Restoration | Restoration - Antique Radium Clock | 0:00 Intro; 0:42 Disassembly; 3:50 Sand Blasting; 5:00 Dent Repair and Polishing; 8:28 Po… |
| 0icCbK1IT2g | 16 | 185 | 44 | long | Sunlike study | Water Resources Class 10 cbse full chapter (Animation)… | 00:00 Introduction; 03:18 Water Scarcity and the need for Water Conservation and Manageme… |
| ghW7BEC0byg | 15 | 402 | 33 | long | Howtown | The Moon's origin story doesn't add up | 00:00 intro; 01:04 where is the moon; 02:43 the moon is weird; 04:20 4 hypotheses; 06:08 … |
| dqLM65HfVEw | 14 | 403 | 29 | long | Howtown | Why is this one spot not warming? | 0:00 cold blob; 1:01 side quest to turkey; 3:00 a bucket meets the deep; 5:10 deutsche at… |
| mZqSH58nM7Y | 14 | 265 | 29 | medium | Satisfying Restoration | Gamecube Keyboard Restoration - Yellowed Plastic Retro… | 0:00 Intro; 0:06 unboxing; 0:33 please help me translate this note into English; 0:42 con… |
| EOgLOnCRsKM | 13 | 312 | 40 | long | Cosmetic Up | Satisfying Makeup Repair ASMR💄DIY Lip Balm & Luxury Ma… | 00:00:00 Highlights; 00:00:19 DIY Jelly Lip Balm; 00:01:58 Depotting Dior Forever Glow Lu… |
| xT10kTnYLDQ | 13 | 146 | 38 | long | Sunlike study | Climate class 9 full chapter (Animation) \| Class 9 ge… | 00:00 Introduction; 00:51 Difference between weather and climate; 02:27 Climate of India;… |
| JRAF320GsaI | 13 | 130 | 27 | long | Vlad and Niki | Cool Science Experiments with inflatable toys | 00:00 Inflating toys until they blow - Fun Experiments for kids; 05:20 Kids built a Lego … |
| y7GXR4kSswY | 12 | 326 | 25 | long | Cosmetic Up | Satisfying Makeup Repair ASMR💄Cosmetic Comeback Restor… | 00:00 Highlights; 00:10 DIY color-changing lip balm; 01:37 Fix NYX Makeup SFX Face & Body… |

## 10. Comments: status, phrase rates, per-video patterns

Fetched comments: 575; status {'error': 1, 'ok': 23, 'not_requested': 16}; max 25 per video; relevance order; mining needs >=20 comments; 2.5% floor.

| Phrase | n | Rate of fetched comments |
| --- | --- | --- |
| asked_for_a_sequel | 9 | 0.016 |
| asked_for_sibling_topic | 1 | 0.002 |
| asked_which_tool | 0 | 0.0 |
| said_it_did_not_work | 2 | 0.003 |
| objected_to_cost | 3 | 0.005 |
| objected_to_pacing_clarity | 1 | 0.002 |
| wants_asset | 1 | 0.002 |
| wants_teaching | 0 | 0.0 |

| Video | n | Patterns >=2.5% | Reading |
| --- | --- | --- | --- |
| F1_aOX0acbY | 25 | none | nothing cleared the 2.5% floor — this comment field cannot brief a video. That is a real finding: choose a vi… |
| jfUU24gaqNg | 25 | objected to cost 4% | the loudest objection is objected to cost (4%) — fix that in the remake |
| ZuA1yaHDB_A | 25 | said it did not work 4% | the loudest objection is said it did not work (4%) — fix that in the remake |
| huQIyJ1ymEQ | 25 | asked for a sequel 4% | the audience is asking for more: asked for a sequel (4%) |
| qR7vPGcP_ko | 25 | asked for a sequel 12%; said it did not work 4% | the audience is asking for more: asked for a sequel (12%); the loudest objection is said it did not work (4%)… |
| HSWrqJTDn8o | 25 | none | nothing cleared the 2.5% floor — this comment field cannot brief a video. That is a real finding: choose a vi… |
| GpRLQ-QizQQ | 25 | none | nothing cleared the 2.5% floor — this comment field cannot brief a video. That is a real finding: choose a vi… |
| xZco3o0HLZc | 25 | asked for a sequel 4%; objected to cost 8% | the audience is asking for more: asked for a sequel (4%); the loudest objection is objected to cost (8%) — fi… |
| T9abiWZZros | 25 | none | nothing cleared the 2.5% floor — this comment field cannot brief a video. That is a real finding: choose a vi… |
| 5PTL5N5c4jc | 25 | asked for a sibling topic 4%; objected to pacing/clarity 4% | the audience is asking for more: asked for a sibling topic (4%); the loudest objection is objected to pacing/… |
| 4aWjjSKAQig | 25 | none | nothing cleared the 2.5% floor — this comment field cannot brief a video. That is a real finding: choose a vi… |
| fA8-gXDoAk8 | 25 | none | nothing cleared the 2.5% floor — this comment field cannot brief a video. That is a real finding: choose a vi… |
| EgXkduRe9ZU | 25 | none | nothing cleared the 2.5% floor — this comment field cannot brief a video. That is a real finding: choose a vi… |
| BPZkZpGMpXA | 25 | none | nothing cleared the 2.5% floor — this comment field cannot brief a video. That is a real finding: choose a vi… |
| uwL2o2GnCrg | 25 | none | nothing cleared the 2.5% floor — this comment field cannot brief a video. That is a real finding: choose a vi… |
| _yl5ELcmugI | 25 | none | nothing cleared the 2.5% floor — this comment field cannot brief a video. That is a real finding: choose a vi… |
| pvMPaYHwGVw | 25 | asked for a sequel 4%; wants the asset 4% | the audience is asking for more: asked for a sequel (4%); wants the asset (4%) is the conversion surface |
| nCa4BGy3MJ8 | 25 | none | nothing cleared the 2.5% floor — this comment field cannot brief a video. That is a real finding: choose a vi… |
| XO1h5G6xytU | 25 | none | nothing cleared the 2.5% floor — this comment field cannot brief a video. That is a real finding: choose a vi… |
| 1GDkjZm6coU | 25 | none | nothing cleared the 2.5% floor — this comment field cannot brief a video. That is a real finding: choose a vi… |
| Mqx1PUUAAjg | 25 | none | nothing cleared the 2.5% floor — this comment field cannot brief a video. That is a real finding: choose a vi… |
| 7Wx_2kGHqUA | 25 | asked for a sequel 12% | the audience is asking for more: asked for a sequel (12%) |
| yqmmI_NXxEI | 25 | none | nothing cleared the 2.5% floor — this comment field cannot brief a video. That is a real finding: choose a vi… |

## 11. Thumbnail pixel statistics

| Metric | Aggregate value |
| --- | --- |
| face_rate | 0.825 |
| avg_contrast | 0.226 |
| avg_brightness | 0.325 |
| avg_busy | 2.335 |
| avg_accent_share | 0.508 |
| avg_lower_text_energy | 2.111 |
| hue_families | [[0, 22], [3, 15], [5, 1], [4, 1], [1, 1]] |
| note | image statistics only; not OCR, not face recognition, not video-frame edit analysis |

| Bucket | n | Face heuristic | Contrast | Brightness | Busy | Accent | Lower text energy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| short | 26 | 0.885 | 0.209 | 0.272 | 1.7 | 0.518 | 1.55 |
| medium | 8 | 0.625 | 0.25 | 0.354 | 3.734 | 0.546 | 3.312 |
| long | 6 | 0.833 | 0.265 | 0.513 | 3.225 | 0.412 | 2.938 |

`face_present` skin-tone pixel heuristic hai; face recognition/OCR nahi. 40 thumbnails ki full rows JSON extract me hain.

## 12. Transcript blocker ledger — 12/12 errors

| Video | Teardown | Transcript | Words | Detail |
| --- | --- | --- | --- | --- |
| -xasdJzBVpo | ok | error | 0 | ERROR: [youtube] -xasdJzBVpo: Sign in to confirm you’re not a bot. This helps protect our community. Use --cookies-from-browser or --cookies for the … |
| F1_aOX0acbY | ok | error | 0 | ERROR: [youtube] F1_aOX0acbY: Sign in to confirm you’re not a bot. This helps protect our community. Use --cookies-from-browser or --cookies for the … |
| jfUU24gaqNg | ok | error | 0 | ERROR: [youtube] jfUU24gaqNg: Sign in to confirm you’re not a bot. This helps protect our community. Use --cookies-from-browser or --cookies for the … |
| ZuA1yaHDB_A | ok | error | 0 | ERROR: [youtube] ZuA1yaHDB_A: Sign in to confirm you’re not a bot. This helps protect our community. Use --cookies-from-browser or --cookies for the … |
| huQIyJ1ymEQ | ok | error | 0 | ERROR: [youtube] huQIyJ1ymEQ: Sign in to confirm you’re not a bot. This helps protect our community. Use --cookies-from-browser or --cookies for the … |
| qR7vPGcP_ko | ok | error | 0 | ERROR: [youtube] qR7vPGcP_ko: Sign in to confirm you’re not a bot. This helps protect our community. Use --cookies-from-browser or --cookies for the … |
| HSWrqJTDn8o | ok | error | 0 | ERROR: [youtube] HSWrqJTDn8o: Sign in to confirm you’re not a bot. This helps protect our community. Use --cookies-from-browser or --cookies for the … |
| GpRLQ-QizQQ | ok | error | 0 | ERROR: [youtube] GpRLQ-QizQQ: Sign in to confirm you’re not a bot. This helps protect our community. Use --cookies-from-browser or --cookies for the … |
| xZco3o0HLZc | ok | error | 0 | ERROR: [youtube] xZco3o0HLZc: Sign in to confirm you’re not a bot. This helps protect our community. Use --cookies-from-browser or --cookies for the … |
| T9abiWZZros | ok | error | 0 | ERROR: [youtube] T9abiWZZros: Sign in to confirm you’re not a bot. This helps protect our community. Use --cookies-from-browser or --cookies for the … |
| 5PTL5N5c4jc | ok | error | 0 | ERROR: [youtube] 5PTL5N5c4jc: Sign in to confirm you’re not a bot. This helps protect our community. Use --cookies-from-browser or --cookies for the … |
| 4aWjjSKAQig | ok | error | 0 | ERROR: [youtube] 4aWjjSKAQig: Sign in to confirm you’re not a bot. This helps protect our community. Use --cookies-from-browser or --cookies for the … |

## 13. All 40 deep teardowns — public receipt + metadata + not-observed ledger

| # | ID | Bucket | Views | Sec | Channel | Title | Hook | Desc words | Chap | Tags | Caption | Comments | Transcript | Editing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | -xasdJzBVpo | short | 947,286,603 | 60 | Vlad and Niki | Kids are making a volcano - Cool Science Experiment! | statement | 8 | 0 | 13 | False | error/0 | error | not_observed |
| 2 | F1_aOX0acbY | short | 702,207,930 | 150 | W Sound | W Sound 05 "LA PLENA" - Beéle, Westcol, Ovy On The Drums | statement | 373 | 0 | 30 | True | ok/25 | error | not_observed |
| 3 | jfUU24gaqNg | short | 366,676,533 | 36 | Mark Rober | 3 Levels of Elephant Toothpaste | statement | 0 | 0 | 0 | True | ok/25 | error | not_observed |
| 4 | ZuA1yaHDB_A | short | 331,133,432 | 12 | Sam Marlow Farrier Li… | Horse needs its crunchy chestnut removed by a farrier ! #… | statement | 0 | 0 | 0 | False | ok/25 | error | not_observed |
| 5 | huQIyJ1ymEQ | short | 279,870,018 | 55 | JayFindsThings | The World's Softest Cushion... | belief_challe… | 16 | 0 | 14 | False | ok/25 | error | not_observed |
| 6 | qR7vPGcP_ko | short | 269,457,699 | 54 | JayFindsThings | How To Remove a Stain | belief_challe… | 16 | 0 | 7 | False | ok/25 | error | not_observed |
| 7 | HSWrqJTDn8o | short | 257,565,435 | 58 | JayFindsThings | Money Inside Soap? | belief_challe… | 16 | 0 | 7 | False | ok/25 | error | not_observed |
| 8 | GpRLQ-QizQQ | short | 239,076,269 | 24 | Oddly Satisfying | Hot Metal Balls Video by Oddly Satisfying #asmr #satisfyi… | belief_challe… | 34 | 0 | 0 | False | ok/25 | error | not_observed |
| 9 | xZco3o0HLZc | short | 230,897,856 | 58 | Satisfying Shorts | #shorts Fixing Broken Chanel Blush pt1 #cosmeticrepair#sa… | belief_challe… | 33 | 0 | 30 | False | ok/25 | error | not_observed |
| 10 | T9abiWZZros | short | 229,123,816 | 31 | The Pet Collective | Cute Armadillo Rescued From Hole! | list | 145 | 0 | 13 | False | ok/25 | error | not_observed |
| 11 | 5PTL5N5c4jc | short | 203,657,158 | 11 | Sick Science! | Square Bubble | question | 89 | 0 | 20 | False | ok/25 | error | not_observed |
| 12 | 4aWjjSKAQig | short | 188,296,206 | 48 | JayFindsThings | How to Make Paper Dart | belief_challe… | 16 | 0 | 9 | False | ok/25 | error | not_observed |
| 13 | fA8-gXDoAk8 | medium | 37,517,941 | 275 | Salman Khan Films | Maatrubhumi - Trailer \| Salman Khan, Chitrangda Singh \|… | statement | 168 | 0 | 9 | False | ok/25 | not_requested | not_observed |
| 14 | EgXkduRe9ZU | short | 68,953,240 | 155 | Badshah | Mahiya (Official Music Video) Badshah x Shreya Ghoshal - … | statement | 638 | 0 | 30 | False | ok/25 | not_requested | not_observed |
| 15 | BPZkZpGMpXA | short | 76,017,600 | 223 | T-Series | KING: Tu Mil Jaaye \| Shah Rukh Khan, Deepika \| Sachin-J… | statement | 212 | 0 | 23 | False | ok/25 | not_requested | not_observed |
| 16 | uwL2o2GnCrg | short | 5,980,063 | 162 | Soham Rockstar Entert… | Gunmaaster G9 Trailer l Emraan l Genelia l Aparshakti l D… | statement | 553 | 0 | 24 | True | ok/25 | not_requested | not_observed |
| 17 | _yl5ELcmugI | short | 10,402,102 | 30 | Rockstar Games | Grand Theft Auto VI: Pre-Load Now | statement | 113 | 0 | 15 | True | ok/25 | not_requested | not_observed |
| 18 | pvMPaYHwGVw | short | 7,959,573 | 18 | FuFu Squishy | FUFUSQUISHY ASMR🥟🥟DUMPLING#asmr#satisfying | belief_challe… | 91 | 0 | 0 | False | ok/25 | not_requested | not_observed |
| 19 | nCa4BGy3MJ8 | short | 44,134,186 | 183 | Maddock Films | Eetha \| Official Trailer \| Shraddha Kapoor \| Randeep H… | list | 227 | 0 | 27 | True | ok/25 | not_requested | not_observed |
| 20 | XO1h5G6xytU | medium | 42,704,648 | 248 | Daddy Yankee | Daddy Yankee and Diljit Dosanjh - POKITO (Official Music … | statement | 835 | 0 | 10 | False | ok/25 | not_requested | not_observed |
| 21 | 1GDkjZm6coU | short | 182,753,889 | 10 | Story Arc Paws | Heart-touching Cute Kitten Dance 🐾 #shorts #kittenrescue … | statement | 3 | 0 | 0 | False | ok/25 | not_requested | not_observed |
| 22 | Mqx1PUUAAjg | short | 175,359,996 | 54 | JayFindsThings | African Teeth Whitening Hack... | belief_challe… | 16 | 0 | 13 | False | ok/25 | not_requested | not_observed |
| 23 | 7Wx_2kGHqUA | short | 174,636,394 | 56 | JayFindsThings | Illegal Dice Trick... #lifehacks | belief_challe… | 17 | 0 | 7 | False | ok/25 | not_requested | not_observed |
| 24 | yqmmI_NXxEI | short | 172,988,074 | 56 | JayFindsThings | Small VS Giant Paper Popper | belief_challe… | 16 | 0 | 13 | False | ok/25 | not_requested | not_observed |
| 25 | Bt_VZpxWQGU | short | 172,400,704 | 43 | JayFindsThings | How To Make Mosquito Snapper | statement | 9 | 0 | 13 | False | not_requested/0 | not_requested | not_observed |
| 26 | qJdp60LGHf8 | short | 153,158,880 | 59 | JayFindsThings | How To Breath Underwater | statement | 48 | 0 | 11 | False | not_requested/0 | not_requested | not_observed |
| 27 | LuvaQXZscUc | short | 128,477,074 | 8 | Tusher ABC | #experimentvideoviral #viralexperiment #scienceexperiment… | statement | 10 | 0 | 4 | False | not_requested/0 | not_requested | not_observed |
| 28 | H27TCc-JCWU | short | 125,880,515 | 55 | JayFindsThings | World's Strongest Bottle? | statement | 1 | 0 | 7 | False | not_requested/0 | not_requested | not_observed |
| 29 | B1J6Ou4q8vE | medium | 163,566,319 | 843 | Alan Becker | Animation vs. Math | question | 62 | 0 | 0 | False | not_requested/0 | not_requested | not_observed |
| 30 | cw8gjwEtdhY | medium | 79,575,609 | 962 | Maupin Farrier Co | Farrier-Hoof Restoration-Satisfying | belief_challe… | 19 | 0 | 0 | False | not_requested/0 | not_requested | not_observed |
| 31 | rGcRe4lt4z4 | medium | 65,904,683 | 526 | KLT | All the Countries of the World with Flags \| Countries Of… | belief_challe… | 141 | 0 | 16 | True | not_requested/0 | not_requested | not_observed |
| 32 | z-R3DShHbkA | medium | 58,013,764 | 369 | Fun Science | EASY SCIENCE EXPERIMENTS TO DO AT HOME | statement | 153 | 3 | 17 | False | not_requested/0 | not_requested | not_observed |
| 33 | JHGLnec9Eg4 | medium | 52,241,259 | 777 | Jeffers Farrier Svc. | Very Satisfying - Hoof Restoration - Farrier ASMR | statement | 3 | 0 | 0 | False | not_requested/0 | not_requested | not_observed |
| 34 | Gt2mYPwXyAc | medium | 47,519,981 | 298 | KLT | 50 States Song - USA States and Capitals Song \| Geograph… | number | 697 | 0 | 17 | True | not_requested/0 | not_requested | not_observed |
| 35 | pFeanxO4-E8 | long | 168,635,831 | 1907 | Ryan's World | Ryan learns Easy DIY Science Experiment for Kids with how… | statement | 29 | 0 | 14 | False | not_requested/0 | not_requested | not_observed |
| 36 | ian6CXeFUYc | long | 85,213,193 | 1359 | Rescue & Restore | 1871 Candy Drop Roller Restoration - Thomas Mills | statement | 134 | 0 | 0 | False | not_requested/0 | not_requested | not_observed |
| 37 | IXqBm15EZYA | long | 42,836,541 | 4765 | Ryan's World | DIY Rainbow Science Experiments with 1hr activities for k… | statement | 28 | 0 | 14 | False | not_requested/0 | not_requested | not_observed |
| 38 | ZW27ubHprMo | long | 39,746,754 | 1951 | MAD LAB | Best Moments Of Animals That Asked People for Help in 202… | statement | 76 | 0 | 25 | False | not_requested/0 | not_requested | not_observed |
| 39 | _ZizKQqHNgI | long | 39,200,340 | 1295 | Inventor 101 | 40 Science Experiments - Experiments You Can Do at Home C… | number | 43 | 0 | 21 | False | not_requested/0 | not_requested | not_observed |
| 40 | JH03xu8R7fo | long | 33,787,096 | 1355 | TysyTube Restoration | I Took Polishing This Rusty Cleaver Too Far | statement | 140 | 0 | 15 | False | not_requested/0 | not_requested | not_observed |

Har teardown me `editing_observation.status=not_observed`; koi competitor frame/cut/music/SFX/caption animation inspect nahi kiya gaya.

### 12 detailed teardown cards


#### 1. `-xasdJzBVpo` — Kids are making a volcano - Cool Science Experiment!

| Field | Value |
| --- | --- |
| Channel / published | Vlad and Niki / 2024-03-19T06:00:00Z |
| Public receipt | 947,286,603 views, 60s, like 0.01024, comment 0.0, caption flag False |
| Hook sentence | Kids are making a volcano - Cool Science Experiment! |
| Hook type / description | statement / 8 words, 0 numbers, 0 chapter markers, script-like synopsis False |
| CTA true | none |
| Tags | Vlad and Niki, Alice, Kids, Kids playing, Fun, Family, Video for kids, Shorts, Kids stories, Toys, Kids toys, Baby, Learn |
| Chapters | none |
| Comment mining | error n=None; no pattern >=2.5% |
| Transcript attempt | {'status': 'error', 'lang': None, 'kind': None, 'words': 0, 'detail': 'ERROR: [youtube] -xasdJzBVpo: Sign in to confirm you’re not a bot. This helps protect our community. Use --c… |
| Editing observation | competitor video frames, cuts/sec, transitions, music, sound design, caption animation, colour grade and retention curve were not inspected; no video/audio download was performed |
| Boundary | third-party copyrighted work, research only, not source footage |


#### 2. `F1_aOX0acbY` — W Sound 05 "LA PLENA" - Beéle, Westcol, Ovy On The Drums

| Field | Value |
| --- | --- |
| Channel / published | W Sound / 2025-02-20T00:00:07Z |
| Public receipt | 702,207,930 views, 150s, like 0.00221, comment 6e-05, caption flag True |
| Hook sentence | Stream Aqui: ✅ Siguenos en las Redes: @wsoundwestcol Instagram - www.instagram.com/westcol www.instagram.com/ovyonthedrums www.instagram.com/Beele #wsound #westcol #beele #ovyonth |
| Hook type / description | statement / 373 words, 1 numbers, 0 chapter markers, script-like synopsis False |
| CTA true | link |
| Tags | Ryan castro, W sound, Ovy, Westcol, Awooo, Awo, Lyric video SQ, SQ, Ryan, Cantante del ghetto, Cantante del queso, West col, West, Kick, W sound 04, W sound 03, Raw Alejandro, Sol… |
| Chapters | none |
| Comment mining | ok n=25; no pattern >=2.5% |
| Transcript attempt | {'status': 'error', 'lang': None, 'kind': None, 'words': 0, 'detail': 'ERROR: [youtube] F1_aOX0acbY: Sign in to confirm you’re not a bot. This helps protect our community. Use --c… |
| Editing observation | competitor video frames, cuts/sec, transitions, music, sound design, caption animation, colour grade and retention curve were not inspected; no video/audio download was performed |
| Boundary | third-party copyrighted work, research only, not source footage |


#### 3. `jfUU24gaqNg` — 3 Levels of Elephant Toothpaste

| Field | Value |
| --- | --- |
| Channel / published | Mark Rober / 2025-11-22T17:37:17Z |
| Public receipt | 366,676,533 views, 36s, like 0.00862, comment 2e-05, caption flag True |
| Hook sentence |  |
| Hook type / description | statement / 0 words, 0 numbers, 0 chapter markers, script-like synopsis False |
| CTA true | none |
| Tags | none |
| Chapters | none |
| Comment mining | ok n=25; objected to cost 4% |
| Transcript attempt | {'status': 'error', 'lang': None, 'kind': None, 'words': 0, 'detail': 'ERROR: [youtube] jfUU24gaqNg: Sign in to confirm you’re not a bot. This helps protect our community. Use --c… |
| Editing observation | competitor video frames, cuts/sec, transitions, music, sound design, caption animation, colour grade and retention curve were not inspected; no video/audio download was performed |
| Boundary | third-party copyrighted work, research only, not source footage |


#### 4. `ZuA1yaHDB_A` — Horse needs its crunchy chestnut removed by a farrier ! #horse #asmr #oddlysatisfying #animal

| Field | Value |
| --- | --- |
| Channel / published | Sam Marlow Farrier Life / 2023-07-02T12:38:29Z |
| Public receipt | 331,133,432 views, 12s, like 0.00718, comment 0.0, caption flag False |
| Hook sentence |  |
| Hook type / description | statement / 0 words, 0 numbers, 0 chapter markers, script-like synopsis False |
| CTA true | none |
| Tags | none |
| Chapters | none |
| Comment mining | ok n=25; said it did not work 4% |
| Transcript attempt | {'status': 'error', 'lang': None, 'kind': None, 'words': 0, 'detail': 'ERROR: [youtube] ZuA1yaHDB_A: Sign in to confirm you’re not a bot. This helps protect our community. Use --c… |
| Editing observation | competitor video frames, cuts/sec, transitions, music, sound design, caption animation, colour grade and retention curve were not inspected; no video/audio download was performed |
| Boundary | third-party copyrighted work, research only, not source footage |


#### 5. `huQIyJ1ymEQ` — The World's Softest Cushion...

| Field | Value |
| --- | --- |
| Channel / published | JayFindsThings / 2025-06-21T11:15:05Z |
| Public receipt | 279,870,018 views, 55s, like 0.00997, comment 2e-05, caption flag False |
| Hook sentence | #shorts All of my finds are linked in my bio and in the video for you! |
| Hook type / description | belief_challenge / 16 words, 0 numbers, 0 chapter markers, script-like synopsis False |
| CTA true | none |
| Tags | amazon finds, amazon, terrible amazon finds, jay finds things, jayfindsthings, kitchen, home, gadgets, products, cool products, amazon products, life hacks, life hack, cool gadgets |
| Chapters | none |
| Comment mining | ok n=25; asked for a sequel 4% |
| Transcript attempt | {'status': 'error', 'lang': None, 'kind': None, 'words': 0, 'detail': 'ERROR: [youtube] huQIyJ1ymEQ: Sign in to confirm you’re not a bot. This helps protect our community. Use --c… |
| Editing observation | competitor video frames, cuts/sec, transitions, music, sound design, caption animation, colour grade and retention curve were not inspected; no video/audio download was performed |
| Boundary | third-party copyrighted work, research only, not source footage |


#### 6. `qR7vPGcP_ko` — How To Remove a Stain

| Field | Value |
| --- | --- |
| Channel / published | JayFindsThings / 2025-09-05T11:15:16Z |
| Public receipt | 269,457,699 views, 54s, like 0.01593, comment 5e-05, caption flag False |
| Hook sentence | #shorts All of my finds are linked in my bio and in the video for you! |
| Hook type / description | belief_challenge / 16 words, 0 numbers, 0 chapter markers, script-like synopsis False |
| CTA true | none |
| Tags | jay finds things, jayfindsthings, gadgets, products, cool products, life hacks, life hack |
| Chapters | none |
| Comment mining | ok n=25; asked for a sequel 12%; said it did not work 4% |
| Transcript attempt | {'status': 'error', 'lang': None, 'kind': None, 'words': 0, 'detail': 'ERROR: [youtube] qR7vPGcP_ko: Sign in to confirm you’re not a bot. This helps protect our community. Use --c… |
| Editing observation | competitor video frames, cuts/sec, transitions, music, sound design, caption animation, colour grade and retention curve were not inspected; no video/audio download was performed |
| Boundary | third-party copyrighted work, research only, not source footage |


#### 7. `HSWrqJTDn8o` — Money Inside Soap?

| Field | Value |
| --- | --- |
| Channel / published | JayFindsThings / 2025-10-17T12:00:37Z |
| Public receipt | 257,565,435 views, 58s, like 0.01494, comment 7e-05, caption flag False |
| Hook sentence | #shorts All of my finds are linked in my bio and in the video for you! |
| Hook type / description | belief_challenge / 16 words, 0 numbers, 0 chapter markers, script-like synopsis False |
| CTA true | none |
| Tags | jay finds things, jayfindsthings, gadgets, products, cool products, life hacks, life hack |
| Chapters | none |
| Comment mining | ok n=25; no pattern >=2.5% |
| Transcript attempt | {'status': 'error', 'lang': None, 'kind': None, 'words': 0, 'detail': 'ERROR: [youtube] HSWrqJTDn8o: Sign in to confirm you’re not a bot. This helps protect our community. Use --c… |
| Editing observation | competitor video frames, cuts/sec, transitions, music, sound design, caption animation, colour grade and retention curve were not inspected; no video/audio download was performed |
| Boundary | third-party copyrighted work, research only, not source footage |


#### 8. `GpRLQ-QizQQ` — Hot Metal Balls Video by Oddly Satisfying #asmr #satisfying #satisfyingvideo #relaxing #asmrsounds

| Field | Value |
| --- | --- |
| Channel / published | Oddly Satisfying / 2024-05-02T08:47:09Z |
| Public receipt | 239,076,269 views, 24s, like 0.00849, comment 1e-05, caption flag False |
| Hook sentence | Here is another all original satisfying / asmr / relaxing and smooth video that delights not only your eyeballs but also your ears! |
| Hook type / description | belief_challenge / 34 words, 0 numbers, 0 chapter markers, script-like synopsis False |
| CTA true | none |
| Tags | none |
| Chapters | none |
| Comment mining | ok n=25; no pattern >=2.5% |
| Transcript attempt | {'status': 'error', 'lang': None, 'kind': None, 'words': 0, 'detail': 'ERROR: [youtube] GpRLQ-QizQQ: Sign in to confirm you’re not a bot. This helps protect our community. Use --c… |
| Editing observation | competitor video frames, cuts/sec, transitions, music, sound design, caption animation, colour grade and retention curve were not inspected; no video/audio download was performed |
| Boundary | third-party copyrighted work, research only, not source footage |


#### 9. `xZco3o0HLZc` — #shorts Fixing Broken Chanel Blush pt1 #cosmeticrepair#satisfying#asmr#oddly#oddlysatisfying#fyp

| Field | Value |
| --- | --- |
| Channel / published | Satisfying Shorts / 2023-07-09T20:00:14Z |
| Public receipt | 230,897,856 views, 58s, like 0.02532, comment 3e-05, caption flag False |
| Hook sentence | ASMR Repairing Makeup All content is exclusively owned and created by YumUp CO.,LTD. |
| Hook type / description | belief_challenge / 33 words, 0 numbers, 0 chapter markers, script-like synopsis False |
| CTA true | subscribe, link |
| Tags | shorts, tiktok, cosmetic, cosmetics, makeup, makeup asmr, asmr, asmr makeup, makeup repair, youtube shorts, best shorts, cosmetic asmr, viral, satisfying, fyp, tips, hacks, beauty… |
| Chapters | none |
| Comment mining | ok n=25; asked for a sequel 4%; objected to cost 8% |
| Transcript attempt | {'status': 'error', 'lang': None, 'kind': None, 'words': 0, 'detail': 'ERROR: [youtube] xZco3o0HLZc: Sign in to confirm you’re not a bot. This helps protect our community. Use --c… |
| Editing observation | competitor video frames, cuts/sec, transitions, music, sound design, caption animation, colour grade and retention curve were not inspected; no video/audio download was performed |
| Boundary | third-party copyrighted work, research only, not source footage |


#### 10. `T9abiWZZros` — Cute Armadillo Rescued From Hole!

| Field | Value |
| --- | --- |
| Channel / published | The Pet Collective / 2023-09-16T03:00:11Z |
| Public receipt | 229,123,816 views, 31s, like 0.01078, comment 3e-05, caption flag False |
| Hook sentence | "Thank you for the ride, good sir!" 💕✨❤️ (Via - Anna S.) #Armadillo #Wildlife #CuteAnimals #FunnyAnimals #AnimalLover ✨💕🐶Subscribe to The Scoop for our most entertaining pet videos, helpful pet parenting tips, and exclusive deals delivered |
| Hook type / description | list / 145 words, 0 numbers, 0 chapter markers, script-like synopsis False |
| CTA true | subscribe, link |
| Tags | the pet collective, pet collective, animals, funny, funny videos, cat, cats, dog, dogs, funny animal, try not to laugh, jukin media, funny animal videos |
| Chapters | none |
| Comment mining | ok n=25; no pattern >=2.5% |
| Transcript attempt | {'status': 'error', 'lang': None, 'kind': None, 'words': 0, 'detail': 'ERROR: [youtube] T9abiWZZros: Sign in to confirm you’re not a bot. This helps protect our community. Use --c… |
| Editing observation | competitor video frames, cuts/sec, transitions, music, sound design, caption animation, colour grade and retention curve were not inspected; no video/audio download was performed |
| Boundary | third-party copyrighted work, research only, not source footage |


#### 11. `5PTL5N5c4jc` — Square Bubble

| Field | Value |
| --- | --- |
| Channel / published | Sick Science! / 2023-03-01T20:00:03Z |
| Public receipt | 203,657,158 views, 11s, like 0.01083, comment 1e-05, caption flag False |
| Hook sentence | Full Experiment: Are you a teacher? |
| Hook type / description | question / 89 words, 2 numbers, 0 chapter markers, script-like synopsis True |
| CTA true | follow, link, part2, credits |
| Tags | SteveSpanglerScience, Steve Spangler, SteveSpangler, Cool Science Experiments, Cool Science, At Home Science, Do it Yourself Science, Fun Science Experiments, Science For Kids, Co… |
| Chapters | none |
| Comment mining | ok n=25; asked for a sibling topic 4%; objected to pacing/clarity 4% |
| Transcript attempt | {'status': 'error', 'lang': None, 'kind': None, 'words': 0, 'detail': 'ERROR: [youtube] 5PTL5N5c4jc: Sign in to confirm you’re not a bot. This helps protect our community. Use --c… |
| Editing observation | competitor video frames, cuts/sec, transitions, music, sound design, caption animation, colour grade and retention curve were not inspected; no video/audio download was performed |
| Boundary | third-party copyrighted work, research only, not source footage |


#### 12. `4aWjjSKAQig` — How to Make Paper Dart

| Field | Value |
| --- | --- |
| Channel / published | JayFindsThings / 2025-08-08T11:00:10Z |
| Public receipt | 188,296,206 views, 48s, like 0.02209, comment 5e-05, caption flag False |
| Hook sentence | #shorts All of my finds are linked in my bio and in the video for you! |
| Hook type / description | belief_challenge / 16 words, 0 numbers, 0 chapter markers, script-like synopsis False |
| CTA true | none |
| Tags | jay finds things, jayfindsthings, gadgets, products, cool products, amazon products, life hacks, life hack, how to |
| Chapters | none |
| Comment mining | ok n=25; no pattern >=2.5% |
| Transcript attempt | {'status': 'error', 'lang': None, 'kind': None, 'words': 0, 'detail': 'ERROR: [youtube] 4aWjjSKAQig: Sign in to confirm you’re not a bot. This helps protect our community. Use --c… |
| Editing observation | competitor video frames, cuts/sec, transitions, music, sound design, caption animation, colour grade and retention curve were not inspected; no video/audio download was performed |
| Boundary | third-party copyrighted work, research only, not source footage |

## 14. mostPopular top 5 per region — niche verdict nahi

| Region | ID | Views | Sec | Channel | Title |
| --- | --- | --- | --- | --- | --- |
| US | fA8-gXDoAk8 | 37,517,504 | 275 | Salman Khan Films | Maatrubhumi - Trailer \| Salman Khan, Chitrangda Singh \| Apoorva Lak… |
| US | _yl5ELcmugI | 10,401,475 | 30 | Rockstar Games | Grand Theft Auto VI: Pre-Load Now |
| US | 8L0CzL2V72c | 5,401,684 | 49 | PlayStation | Grand Theft Auto VI - Features Trailer \| PS5 Games |
| US | YJ9Ndcv-ZFE | 2,751,098 | 74 | Marvel Rivals | Nightcrawler: Hope and Brimstone \| Character Reveal Trailer \| Marve… |
| US | kWOjA8mCaXo | 2,540,517 | 2650 | SMii7Yplus | Your Favorite YouTubers Do Crack |
| PK | BPZkZpGMpXA | 76,017,600 | 223 | T-Series | KING: Tu Mil Jaaye \| Shah Rukh Khan, Deepika \| Sachin-Jigar, Arijit… |
| PK | EgXkduRe9ZU | 68,953,240 | 155 | Badshah | Mahiya (Official Music Video) Badshah x Shreya Ghoshal - Mahiya ft. A… |
| PK | nCa4BGy3MJ8 | 44,134,186 | 183 | Maddock Films | Eetha \| Official Trailer \| Shraddha Kapoor \| Randeep H \| Dinesh V… |
| PK | XO1h5G6xytU | 42,704,648 | 248 | Daddy Yankee | Daddy Yankee and Diljit Dosanjh - POKITO (Official Music Video) |
| PK | fA8-gXDoAk8 | 37,517,504 | 275 | Salman Khan Films | Maatrubhumi - Trailer \| Salman Khan, Chitrangda Singh \| Apoorva Lak… |
| GB | fA8-gXDoAk8 | 37,517,504 | 275 | Salman Khan Films | Maatrubhumi - Trailer \| Salman Khan, Chitrangda Singh \| Apoorva Lak… |
| GB | _yl5ELcmugI | 10,401,475 | 30 | Rockstar Games | Grand Theft Auto VI: Pre-Load Now |
| GB | uwL2o2GnCrg | 5,980,046 | 162 | Soham Rockstar Entertain… | Gunmaaster G9 Trailer l Emraan l Genelia l Aparshakti l Deepak M l Ad… |
| GB | 8L0CzL2V72c | 5,401,684 | 49 | PlayStation | Grand Theft Auto VI - Features Trailer \| PS5 Games |
| GB | kWOjA8mCaXo | 2,540,517 | 2650 | SMii7Yplus | Your Favorite YouTubers Do Crack |
| IN | fA8-gXDoAk8 | 37,517,504 | 275 | Salman Khan Films | Maatrubhumi - Trailer \| Salman Khan, Chitrangda Singh \| Apoorva Lak… |
| IN | dB_4TiBSLFk | 10,533,282 | 3859 | PAJI IS LIVE | GTA 5 LIVE #gta5 #gtav #gaming |
| IN | yTSDTmdLb0k | 8,818,002 | 213 | Himesh Reshammiya Melodi… | Bulaye Chhathi Maa\| Yeh Prem Mol Liya \| Ayushmann, Sharvari, Sooraj… |
| IN | Yl-nQ_V-bAA | 6,510,528 | 101 | Kalaippuli S Thanu | Vetri Maaran’s Arasan 'FIRE' Glimpse \| Silambarasan TR \| Anirudh \|… |
| IN | uwL2o2GnCrg | 5,980,046 | 162 | Soham Rockstar Entertain… | Gunmaaster G9 Trailer l Emraan l Genelia l Aparshakti l Deepak M l Ad… |

## 15. Not-observed / not-available / not-claimed ledger

| Item | Status | Proof / boundary |
| --- | --- | --- |
| Full verbatim spoken competitor scripts / captions | not_observed | 12/12 public caption attempts errored with bot-check; 0 usable transcript words; creator descriptions are synopses/chapters only. |
| Competitor video frames, cuts/sec, transitions, music, SFX, colour grade, caption animation | not_observed | deep_teardowns_v18.json editing_observation.status=not_observed on all 40; no competitor media download. |
| Private retention, impressions, CTR, RPM, revenue, audience demographics | not_available | YouTube Data API public fields only. |
| Verified subscriber-growth ranking | not_observed | growing_channels_v18.json uses cumulative channel views / channel age and sampled recent uploads as public proxies. |
| Thumbnail OCR, face identity/recognition, text content | not_observed | thumbnail stats are pixel statistics and a permissive skin-tone heuristic only. |
| All public comments | partial | first 24 deep IDs requested up to 25 relevance-ordered comments; 23 ok, 1 error, 16 not_requested. |
| Full untruncated creator descriptions | partial | parse_video_item caps snippet.description at 6000 characters. |
| Causal reason a video won | not_observable | viewCount and metadata are co-occurrence, not an experiment or private analytics. |
| Legal clearance, human/creative approval, upload/publish, monetisation outcome | not_done | research only; no connected-app upload/send; no release claim. |
| Guaranteed views, virality, perfection, family-safety guarantee | not_claimed | report boundary. |

## 16. Source files

- `research/deep_forensic_v18/api_evidence/analysis_manifest_v18.json`
- `research/deep_forensic_v18/api_evidence/channel_statistics_v18.json`
- `research/deep_forensic_v18/api_evidence/comments_v18.json`
- `research/deep_forensic_v18/api_evidence/deep_teardowns_v18.json`
- `research/deep_forensic_v18/api_evidence/description_forensics_v18.json`
- `research/deep_forensic_v18/api_evidence/growing_channels_v18.json`
- `research/deep_forensic_v18/api_evidence/lane_metrics_v18.json`
- `research/deep_forensic_v18/api_evidence/lanes_v18.json`
- `research/deep_forensic_v18/api_evidence/million_view_videos_v18.json`
- `research/deep_forensic_v18/api_evidence/most_popular_v18.json`
- `research/deep_forensic_v18/api_evidence/pattern_aggregates_v18.json`
- `research/deep_forensic_v18/api_evidence/recent_uploads_v18.json`
- `research/deep_forensic_v18/api_evidence/reverse_teardowns_v18.json`
- `research/deep_forensic_v18/api_evidence/run_v18.json`
- `research/deep_forensic_v18/api_evidence/selected_forensic_ids_v18.json`
- `research/deep_forensic_v18/api_evidence/thumbnail_forensics_v18.json`
- `research/deep_forensic_v18/api_evidence/video_categories_v18.json`
- `research/deep_forensic_v18/api_evidence/video_details_v18.json`
- `research/deep_forensic_v18/FORENSIC_EVIDENCE_EXTRACT_V18.json` — 717-candidate index, 40 teardown records, all derived tables

- `research/deep_forensic_v18/DEEP_FORENSIC_V18.md` — auto-generated data appendix from the Actions builder

