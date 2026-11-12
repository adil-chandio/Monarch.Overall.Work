# V18 DEEP 10x Forensic — real-API data appendix (Shorts + Medium + Long)

Generated UTC: `2026-11-12T15:27:40Z`. Key present: `True`. Secret value never printed or stored.

## Honest capability boundary

- Public Data API: views, likes, comments, duration, title, tags, description, category, topic, caption flag, channel stats, recent uploads, top comments.
- Public text: creator-published `snippet.description` (synopsis / chapters / sources) on every >=1M-view video. This is NOT a verbatim VO transcript.
- Public captions: attempted on 12 teardowns; failures are recorded, never filled with invented words.
- Public images: thumbnail pixel statistics only. Not OCR, not face recognition, not video-frame edit analysis.
- NOT observed: competitor video pixels, cuts/sec, transitions, music, sound design, retention curve, CTR, RPM, impressions, subscriber-growth ranking, legal clearance, human watch-through.
- No third-party video/audio is used as source footage. No upload/publish/monetisation/legal/human/guaranteed-views/virality/perfection claim.

## API evidence counts

| Evidence | Count |
| --- | --- |
| secret_value_printed_or_stored | False |
| lanes | 24 |
| short_bucket_lanes | 6 |
| medium_bucket_lanes | 6 |
| long_bucket_lanes | 6 |
| recent_lanes | 6 |
| lane_rows | 1124 |
| unique_videos | 2352 |
| channels_resolved | 801 |
| growing_channels_sampled | 45 |
| recent_upload_channels | 45 |
| most_popular_regions | 4 |
| video_categories | 32 |
| million_view_videos | 720 |
| ten_million_videos | 245 |
| candidate_videos_after_title_safety | 715 |
| description_forensics | 715 |
| deep_teardowns | 40 |
| comments_videos | 23 |
| transcript_attempts | 12 |
| thumbnail_stats | 40 |
| quota_used_approx | 2550 |

## 24 lanes — Shorts / Medium / Long / Recent

| Lane | Bucket | Order | Window | n | Total | Median | Top3 | Win/med | >=1M | >=10M | Fresh30 | Med dur s | Short share | Caption |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| map_geo_short_all | short | viewCount | all | 50 | 571,602,667 | 8,196,396 | 19.6% | 5.6 | 49 | 19 | 0.0% | 59 | 100.0% | 8.0% |
| map_geo_medium_all | medium | viewCount | all | 50 | 394,546,097 | 1,739,743 | 63.6% | 94.0 | 38 | 5 | 0.0% | 535 | 0.0% | 38.0% |
| map_geo_long_all | long | viewCount | all | 50 | 131,079,256 | 1,520,132 | 26.0% | 10.1 | 32 | 2 | 0.0% | 3962 | 0.0% | 8.0% |
| science_explainer_short_all | short | viewCount | all | 50 | 4,191,046,786 | 49,786,593 | 36.2% | 19.0 | 50 | 50 | 0.0% | 55 | 100.0% | 8.0% |
| science_explainer_medium_all | medium | viewCount | all | 50 | 529,442,698 | 4,351,801 | 24.3% | 13.3 | 41 | 19 | 0.0% | 563 | 0.0% | 40.0% |
| science_explainer_long_all | long | viewCount | all | 43 | 357,538,254 | 946,185 | 66.4% | 178.2 | 21 | 7 | 9.3% | 3339 | 0.0% | 9.3% |
| satisfying_restoration_short_all | short | viewCount | all | 50 | 1,993,983,250 | 21,405,942 | 31.2% | 11.2 | 49 | 45 | 2.0% | 58 | 100.0% | 0.0% |
| satisfying_restoration_medium_all | medium | viewCount | all | 50 | 516,994,347 | 3,636,801 | 33.3% | 21.9 | 50 | 14 | 0.0% | 828 | 0.0% | 8.0% |
| satisfying_restoration_long_all | long | viewCount | all | 50 | 310,758,589 | 3,694,385 | 44.6% | 23.1 | 50 | 3 | 0.0% | 2030 | 0.0% | 16.0% |
| animal_rescue_short_all | short | viewCount | all | 50 | 1,013,541,542 | 7,480,700 | 45.9% | 30.6 | 49 | 19 | 2.0% | 41 | 100.0% | 12.0% |
| animal_rescue_medium_all | medium | viewCount | all | 50 | 245,413,801 | 83,153 | 47.0% | 514.8 | 17 | 7 | 0.0% | 478 | 0.0% | 8.0% |
| animal_rescue_long_all | long | viewCount | all | 50 | 162,543,723 | 330,641 | 53.1% | 120.2 | 16 | 6 | 4.0% | 1879 | 0.0% | 12.0% |
| viral_breakdown_short_all | short | viewCount | all | 25 | 4,956,268 | 74,189 | 54.0% | 14.7 | 1 | 0 | 17.4% | 51 | 100.0% | 16.0% |
| viral_breakdown_medium_all | medium | viewCount | all | 50 | 11,713,653 | 42,332 | 56.8% | 70.8 | 2 | 0 | 14.0% | 593 | 0.0% | 2.0% |
| viral_breakdown_long_all | long | viewCount | all | 33 | 3,952,504 | 1,695 | 59.2% | 505.4 | 0 | 0 | 6.2% | 1543 | 0.0% | 12.1% |
| microdrama_short_all | short | viewCount | all | 50 | 59,254,884 | 452,601 | 52.6% | 41.2 | 12 | 1 | 32.0% | 103 | 100.0% | 0.0% |
| microdrama_medium_all | medium | viewCount | all | 50 | 50,480,610 | 592,224 | 23.1% | 8.1 | 16 | 0 | 0.0% | 527 | 0.0% | 4.0% |
| microdrama_long_all | long | viewCount | all | 50 | 40,405,905 | 190,945 | 54.6% | 61.8 | 8 | 1 | 26.0% | 3695 | 0.0% | 12.0% |
| map_geo_recent | any | date | 365 | 50 | 12,281,278 | 64,677 | 60.4% | 64.5 | 3 | 0 | 45.8% | 81 | 60.0% | 0.0% |
| science_explainer_recent | any | date | 365 | 50 | 373,959,170 | 1,436 | 47.5% | 78306.7 | 18 | 13 | 4.0% | 55 | 90.0% | 6.0% |
| satisfying_restoration_recent | any | date | 365 | 50 | 2,909,143 | 994 | 97.4% | 2799.4 | 1 | 0 | 97.5% | 11 | 98.0% | 4.0% |
| animal_rescue_recent | any | date | 365 | 50 | 11,278,367 | 6,528 | 69.7% | 687.1 | 4 | 0 | 65.2% | 84 | 94.0% | 0.0% |
| viral_breakdown_recent | any | date | 365 | 23 | 4,200,392 | 90,884 | 46.1% | 8.8 | 0 | 0 | 23.8% | 661 | 26.1% | 0.0% |
| microdrama_recent | any | date | 365 | 50 | 572,125 | 1,199 | 56.4% | 135.2 | 0 | 0 | 89.6% | 76 | 80.0% | 0.0% |

`short` = <4 min, `medium` = 4–20 min, `long` = >20 min (YouTube `videoDuration`). Corpus-shape signals, not growth ranking or promise.

## Shorts vs Medium vs Long — million-view cross-tab

| Bucket | n(>=1M) | Total views | Median views | >=10M | Med dur s | Med like rate | Med comment rate | Caption | Script-like synopsis | Chapters>=3 | Med desc words | Med numbers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| short | 343 | 11,770,042,001 | 11,294,218 | 177 | 59 | 0.01876 | 0.00013 | 6.7% | 29.7% | 0.0% | 47 | 0 |
| medium | 187 | 1,833,109,728 | 3,209,092 | 47 | 601 | 0.00741 | 0.0002 | 19.8% | 47.1% | 9.6% | 113 | 1 |
| long | 185 | 1,121,545,636 | 2,635,459 | 20 | 3200 | 0.00822 | 0.00021 | 14.1% | 63.8% | 21.1% | 146 | 3 |

## Description / script forensics on every >=1M-view video

| Signal | Value |
| --- | --- |
| Videos analysed | 715 |
| Hook types | {"statement": 366, "belief_challenge": 91, "list": 48, "question": 49, "number": 155, "comparison": 6} |
| Median description words | 94 |
| Median numbers in description | 0 |
| Median hashtags | 3 |
| Median URLs | 0 |
| Script-like synopsis rate | 43.1% |
| Chapter rate (>=3 markers) | 8.0% |
| Emoji present rate | 42.5% |
| CTA counts | {"subscribe": 273, "comment": 41, "follow": 129, "link": 350, "part2": 66, "credits": 41, "chapters": 28, "ai": 15, "disclaimer": 25, "affiliate": 20, "newsletter": 8, "donate": 8} |
| Top title tokens | [["science", 129], ["asmr", 118], ["satisfying", 109], ["geography", 102], ["experiment", 72], ["restoration", 70], ["experiments", 49], ["funny", 38], ["granny", 38], ["makeup", 36], ["map", 35], ["live", 35], ["ashusir", 34], ["rescue", 34], ["full", 34], ["caught", 34], ["camera", 32], ["india", 32], ["kids", 31], ["oddly", 30]] |
| Top tags | [["asmr", 77], ["satisfying", 66], ["restoration", 60], ["geography", 56], ["science", 42], ["relaxing", 38], ["diy", 38], ["shorts", 34], ["history", 34], ["learn", 32], ["science experiments", 32], ["maps", 32], ["repair", 31], ["animals", 31], ["life hacks", 30], ["makeup", 27], ["makeup repair", 27], ["satisfying video", 27], ["jay finds things", 26], ["jayfindsthings", 26]] |

`script_like_synopsis` means the creator's own description is >=50 words and carries >=2 numbers, >=3 chapters, or a question/comparison/belief-challenge hook. It is a public synopsis, not a spoken transcript.

## Growing-channel public proxies (NOT a verified growth ranking)

| Channel | Created | Age d | Subs | Channel views | Videos | Views/day | Views/video | >=1M in corpus | Recent med views | Since 2023 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FuFu Squishy | 2023-12-30 | 1048 | 11,900,000 | 20,861,510,878 | 4862 | 19,906,021 | 4,290,726 | 1 | 414855 | True |
| JayFindsThings | 2024-06-02 | 893 | 7,760,000 | 6,412,218,292 | 72 | 7,180,535 | 89,058,587 | 1 | 44153875 | True |
| FUFUSQUISHY_PACKINGORDER | 2024-04-15 | 941 | 3,260,000 | 6,278,709,520 | 3501 | 6,672,379 | 1,793,404 | 1 | 87934 | True |
| News Pinch | 2025-04-30 | 561 | 2,210,000 | 1,434,333,607 | 6760 | 2,556,744 | 212,179 | 0 | 14112 | True |
| Street Dog Revival  | 2025-02-23 | 627 | 378,000 | 974,064,727 | 1104 | 1,553,532 | 882,305 | 1 | 23969 | True |
| GeoGlobeTales | 2023-11-20 | 1088 | 2,090,000 | 1,645,458,617 | 169 | 1,512,370 | 9,736,441 | 8 | 2889300 | True |
| W Sound | 2024-07-19 | 846 | 918,000 | 1,165,657,058 | 11 | 1,377,845 | 105,968,823 | 0 | 15318132 | True |
| Cosmetic Plus | 2025-05-14 | 547 | 559,000 | 496,810,092 | 1305 | 908,245 | 380,697 | 3 | 5809 | True |
| Ashu Ghai Edits | 2024-12-19 | 693 | 308,000 | 585,149,143 | 426 | 844,371 | 1,373,589 | 0 | 36520 | True |
| Nature Global | 2024-03-08 | 979 | 2,390,000 | 748,076,834 | 882 | 764,123 | 848,159 | 2 | 31757 | True |
| Tarazai | 2025-01-13 | 668 | 257,000 | 506,813,463 | 214 | 758,702 | 2,368,287 | 1 | 6432 | True |
| FPS | 2024-10-30 | 743 | 138,000 | 481,442,880 | 789 | 647,971 | 610,193 | 2 | 32818 | True |
|  Devi Gausuta Anjali Ji | 2024-04-02 | 954 | 722,000 | 527,959,616 | 843 | 553,416 | 626,286 | 1 | 32500 | True |
| Mahi daily update | 2026-01-17 | 299 | 74,600 | 165,023,424 | 1882 | 551,917 | 87,685 | 0 | 4822 | True |
| Raajoo Gaming | 2025-09-11 | 427 | 214,000 | 219,781,717 | 545 | 514,711 | 403,269 | 1 | 2402878 | True |
| Story TV | 2025-05-28 | 533 | 1,000,000 | 273,065,119 | 743 | 512,317 | 367,516 | 16 | 21012 | True |
| Story Arc Paws | 2024-08-19 | 815 | 548,000 | 391,025,327 | 164 | 479,785 | 2,384,300 | 1 | 475598 | True |
| SenpaiUnlimited | 2024-05-29 | 897 | 2,010,000 | 387,217,196 | 672 | 431,680 | 576,216 | 0 | 467376 | True |
| Kuku TV | 2024-11-04 | 738 | 1,410,000 | 310,733,779 | 1603 | 421,048 | 193,845 | 2 | 27607 | True |
| Marvel Rivals | 2024-02-05 | 1011 | 1,300,000 | 407,785,409 | 951 | 403,348 | 428,796 | 1 | 169899 | True |
| Elite Restore  | 2026-01-23 | 293 | 192,000 | 115,872,637 | 71 | 395,469 | 1,632,008 | 1 | 202588 | True |
| জানার বাইরে | 2025-11-17 | 360 | 158,000 | 129,956,447 | 296 | 360,990 | 439,042 | 0 | 17769 | True |
| Adda247 World News | 2025-03-07 | 615 | 927,000 | 219,267,528 | 617 | 356,532 | 355,376 | 0 | 4818 | True |
| Geo Motion | 2024-09-29 | 774 | 213,000 | 274,509,918 | 170 | 354,663 | 1,614,764 | 2 | 437741 | True |
| I am Khaleel 2 | 2025-05-14 | 547 | 229,000 | 172,949,957 | 250 | 316,179 | 691,799 | 0 | 444682 | True |

## Top 25 million-view videos (deep-forensic pool)

| Title | Channel | Views | Dur s | Bucket | Published | Like | Comment | ID |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Kids are making a volcano - Cool Science Experiment! | Vlad and Niki | 947,285,220 | 60 | short | 2024-03-19 | 1.0% | 0.0% | -xasdJzBVpo |
| W Sound 05 "LA PLENA" - Beéle, Westcol, Ovy On The Drums | W Sound | 702,203,617 | 150 | short | 2025-02-20 | 0.2% | 0.0% | F1_aOX0acbY |
| 3 Levels of Elephant Toothpaste | Mark Rober | 366,672,053 | 36 | short | 2025-11-22 | 0.9% | 0.0% | jfUU24gaqNg |
| The World's Softest Cushion... | JayFindsThings | 279,869,893 | 55 | short | 2025-06-21 | 1.0% | 0.0% | huQIyJ1ymEQ |
| How To Remove a Stain | JayFindsThings | 269,457,679 | 54 | short | 2025-09-05 | 1.6% | 0.0% | qR7vPGcP_ko |
| Money Inside Soap? | JayFindsThings | 257,565,348 | 58 | short | 2025-10-17 | 1.5% | 0.0% | HSWrqJTDn8o |
| Hot Metal Balls Video by Oddly Satisfying #asmr #satisfying #satisfyingvideo #re | Oddly Satisfying | 239,076,269 | 24 | short | 2024-05-02 | 0.8% | 0.0% | GpRLQ-QizQQ |
| #shorts Fixing Broken Chanel Blush pt1 #cosmeticrepair#satisfying#asmr#oddly#odd | Satisfying Shorts | 230,897,754 | 58 | short | 2023-07-09 | 2.5% | 0.0% | xZco3o0HLZc |
| Cute Armadillo Rescued From Hole! | The Pet Collective | 229,123,812 | 31 | short | 2023-09-16 | 1.1% | 0.0% | T9abiWZZros |
| Square Bubble | Sick Science! | 203,657,045 | 11 | short | 2023-03-01 | 1.1% | 0.0% | 5PTL5N5c4jc |
| How to Make Paper Dart | JayFindsThings | 188,296,134 | 48 | short | 2025-08-08 | 2.2% | 0.0% | 4aWjjSKAQig |
| Water defies gravity. But how?! 💧👍 #shorts #DrTatiana #science | TAMU Physics & Astronomy | 184,725,548 | 44 | short | 2024-08-01 | 4.0% | 0.0% | -FmaF5KnJ4c |
| Heart-touching Cute Kitten Dance 🐾 #shorts #kittenrescue #animalrescue #kittenre | Story Arc Paws | 182,750,533 | 10 | short | 2025-02-23 | 0.7% | 0.0% | 1GDkjZm6coU |
| African Teeth Whitening Hack... | JayFindsThings | 175,359,994 | 54 | short | 2025-08-15 | 1.3% | 0.0% | Mqx1PUUAAjg |
| Illegal Dice Trick... #lifehacks | JayFindsThings | 174,636,394 | 56 | short | 2025-05-16 | 1.8% | 0.0% | 7Wx_2kGHqUA |
| Small VS Giant Paper Popper | JayFindsThings | 172,988,068 | 56 | short | 2025-07-05 | 1.8% | 0.0% | yqmmI_NXxEI |
| How To Make Mosquito Snapper | JayFindsThings | 172,400,704 | 43 | short | 2025-08-22 | 1.5% | 0.0% | Bt_VZpxWQGU |
| Ryan learns Easy DIY Science Experiment for Kids with how to make a homemade Vol | Ryan's World | 168,635,791 | 1907 | long | 2020-05-14 | 0.2% | 0.0% | pFeanxO4-E8 |
| Animation vs. Math | Alan Becker | 163,562,841 | 843 | medium | 2023-06-24 | 1.0% | 0.0% | B1J6Ou4q8vE |
| Science Experiment Fail #science #fail #bowling | Ross Smith | 154,169,850 | 14 | short | 2024-09-25 | 3.0% | 0.0% | 29v8Da8mhF4 |
| How To Breath Underwater | JayFindsThings | 153,158,872 | 59 | short | 2025-08-01 | 1.8% | 0.0% | qJdp60LGHf8 |
| Indirect dental restoration #satisfying | Dr. Abdom Fora | 151,520,992 | 51 | short | 2024-04-10 | 2.2% | 0.0% | IpdXfzr0U3c |
| Concept of Buoyant force I Ashu Sir #scienceexperiment #shorts #physics #funny # | Science and fun | 142,397,659 | 60 | short | 2022-10-06 | 3.4% | 0.0% | gCjA_3umNpg |
| #shorts Relaxing Makeup Restoration pt1 #satisfying#oddly#oddlysatisfying#bts #a | Satisfying Shorts | 135,180,870 | 55 | short | 2022-11-19 | 2.4% | 0.0% | VIain9HJZKQ |
| Newton's Laws of Motion🤔 🔥🔥 #shorts #science #physics #funny 😀 | Class Up Academy | 133,933,086 | 29 | short | 2022-09-28 | 2.2% | 0.0% | _7pWP89C6rg |

## Deep teardown ledger (what was and was not observed)

Every one of the 40 deep teardowns stores: full public receipt, description-forensics record, creator-published chapter beats, comment mining (first 24), public-caption attempt (first 12), thumbnail statistics, and an explicit `editing_observation.status = not_observed` for frames/cuts/music/retention. See `api_evidence/deep_teardowns_v18.json`.

## Thumbnail aggregate (image statistics only)

| Signal | Value |
| --- | --- |
| face_rate | 0.85 |
| avg_contrast | 0.222 |
| avg_brightness | 0.327 |
| avg_busy | 2.448 |
| avg_accent_share | 0.508 |
| avg_lower_text_energy | 2.237 |
| hue_families | [(0, 22), (3, 15), (5, 1), (4, 1), (1, 1)] |
| note | image statistics only; not OCR, not face recognition, not video-frame edit analysis |

## Files

- `run_v18.json`
- `lanes_v18.json`
- `lane_metrics_v18.json`
- `video_details_v18.json`
- `channel_statistics_v18.json`
- `growing_channels_v18.json`
- `recent_uploads_v18.json`
- `million_view_videos_v18.json`
- `description_forensics_v18.json`
- `pattern_aggregates_v18.json`
- `selected_forensic_ids_v18.json`
- `deep_teardowns_v18.json`
- `comments_v18.json`
- `reverse_teardowns_v18.json`
- `thumbnail_forensics_v18.json`
- `most_popular_v18.json`
- `video_categories_v18.json`

---

**NOT claimed:** upload/publish, monetisation, legal clearance, human creative approval, guaranteed views, virality, perfection, private retention/CTR/RPM, invented transcripts, verified growth ranking, causal claim, video-frame editing analysis. Technical/API evidence is not creative approval.
