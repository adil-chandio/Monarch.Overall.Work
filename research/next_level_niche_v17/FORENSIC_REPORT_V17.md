# V17 Next-Level Niche Forensic — real-API data appendix

Generated UTC: `2026-11-12T04:24:09Z`. Key present: `True`. Secret value never printed or stored.

## Roman Urdu summary

Yeh report **research evidence** hai, final creative approval nahi. Isme 20 search lanes, 4 regions ke most-popular snapshots, channel statistics, recent uploads, public comments, jahan captions mile wahan transcript teardowns, aur thumbnail image statistics hain. Competitor video/audio download nahi kiya, video frames inspect nahi kiye, private retention/CTR/RPM nahi liye. Isliye "har ek cheez microscopic" ka claim sirf **public metadata + public text + thumbnail statistics** tak hai; usse aage ka claim honest nahi hoga.

## Honest capability boundary

- Public Data API fields: views, likes, comments, duration, title, tags, description, category, topic, caption flag, channel stats, recent uploads, top comments.
- Public text: transcript **only where captions are actually available**; otherwise the teardown records `no_captions` / `error`.
- Public images: thumbnail pixel statistics only. Not OCR, not face recognition, not a video-frame edit analysis.
- NOT observed: competitor video pixels, cuts per second, music, sound design, retention curve, CTR, RPM, impressions, subscriber growth ranking, legal clearance, human watch-through.
- No third-party video is used as source footage. No upload, publish, monetisation, legal opinion, human approval, guaranteed views, virality or perfection claim.

## Third-party web signals (not our API data)

- AIR Media-Tech / TubeAI's 144,370-channel study reports Sep 2026 median subscriber growth of 0.97%/month for 10K–100K-subscriber channels; kids 1.59%, ASMR 1.56%, creator economy 1.50%, AI/ML 1.44%, education 1.30%. AIR's 300-channel Studio data puts education/science median RPM at $10.22 vs $2.43 entertainment and $0.33 kids. Six of the ten fastest-growing channels in their Social Blade check grew mainly on Shorts; microdramas passed 6.5B views in H1 2026 with watch time up over 50% YoY. [1](https://air.io/en/audience-growth/whos-growing-fastest-on-youtube-and-which-niches-are-hot-in-2025)
- vidIQ frames AI tools/workflow tutorials as a fastest-growing cluster and says to show AI as a tool with real screen recordings and original commentary, not as fully generated filler. [2](https://vidiq.com/blog/post/best-youtube-niches/)
- OpusClip's 13.5M-clip dataset reports captions in 80.2% and caption animation in 78.6% of analysed viral clips; `Expert Explainer` is the top storyline pattern; conversational delivery is 59.4%; authority/credibility hooks averaged 6,706 views in their hook subset. This is a vendor dataset, not official YouTube data. [5](https://www.opus.pro/research/how-to-go-viral-youtube)
- Revid's 176,367-TikTok study found faceless videos median 113.9K views vs 67.4K for one person on camera, and faceless tutorials 155.6K vs 52.5K on-camera tutorials. This is TikTok data from videos that already did well, so it is correlational, not a YouTube growth guarantee. [8](https://www.revid.ai/blog/best-faceless-youtube-niches)
- YouTube's 2026 CEO letter says Shorts averages 200 billion daily views and more than 1M channels used its AI creation tools daily in December 2025, while framing AI as a tool for expression, not a replacement. [1](https://blog.youtube/inside-youtube/the-future-of-youtube-2026/)
- YouTube's Aug 2026 YPP update says that from Feb 1 2027, Shorts ads/subscription revenue sharing requires 10M qualified Shorts views in 90 days, and new YPP applicants need 8,000 watch hours or 20M qualified Shorts views. Existing YPP channels are not impacted by the entry-threshold change. [2](https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn/)
- YouTube's monetisation policy says mass-produced, generic, repetitive or templated content and reused compilations without substantive original commentary/narrative can be ineligible for monetisation. A monetised channel should therefore avoid template compilations and add visible original research, voice and structure. [1](https://support.google.com/youtube/answer/1311392?hl=en)

## API evidence counts

| Evidence | Count |
| --- | --- |
| Search lanes | 20 |
| Lane video rows | 927 |
| Unique videos resolved | 1567 |
| Channels resolved | 822 |
| mostPopular regions | 4 |
| Video categories | 32 |
| Videos >= 1M views | 418 |
| Videos >= 10M views | 99 |
| Candidate videos after title safety | 415 |
| Videos with comments fetched | 12 |
| Teardowns attempted | 12 |
| Usable transcript statuses | {"error": 12} |
| Thumbnails analysed | 24 |
| Approx. quota units used | 2098 |

## Lane demand table (API `search.list` + `videos.list`)

| Lane | Order | Window | n | Total views | Median views | Top3 share | Winner/median | >=1M | >=10M | Fresh 30d | Med dur s | <=3min | Captions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ai_tutorial_all | viewCount | all | 50 | 70,076,489 | 619,324 | 39.3% | 25.0 | 13 | 1 | 0.0% | 53 | 66.0% | 16.0% |
| ai_tutorial_recent | date | 365 | 50 | 377,765 | 5 | 83.7% | 29687.0 | 0 | 0 | 100.0% | 247 | 44.0% | 8.0% |
| microdrama_all | viewCount | all | 50 | 82,769,888 | 819,359 | 38.3% | 22.7 | 21 | 1 | 20.0% | 148 | 58.0% | 4.0% |
| microdrama_recent | date | 365 | 50 | 3,737,649 | 3,101 | 60.1% | 427.7 | 1 | 0 | 82.0% | 80 | 80.0% | 0.0% |
| science_humor_all | viewCount | all | 50 | 287,153,732 | 962,939 | 56.7% | 73.4 | 25 | 7 | 2.0% | 60 | 68.0% | 2.0% |
| science_humor_recent | date | 365 | 22 | 620,322 | 803 | 98.1% | 682.9 | 0 | 0 | 22.7% | 59 | 68.2% | 4.5% |
| satisfying_all | viewCount | all | 50 | 1,064,343,605 | 10,188,173 | 34.4% | 14.9 | 50 | 25 | 0.0% | 179 | 54.0% | 12.0% |
| satisfying_recent | date | 365 | 50 | 173,945 | 340 | 80.4% | 276.3 | 0 | 0 | 100.0% | 25 | 96.0% | 0.0% |
| animal_rescue_all | viewCount | all | 50 | 1,156,953,568 | 10,894,898 | 40.2% | 21.0 | 49 | 25 | 0.0% | 66 | 66.0% | 6.0% |
| animal_rescue_recent | date | 365 | 50 | 10,659,331 | 1,458 | 91.6% | 2239.6 | 3 | 0 | 93.2% | 17 | 98.0% | 0.0% |
| viral_breakdown_all | viewCount | all | 49 | 16,688,881 | 152,960 | 29.7% | 19.6 | 2 | 0 | 10.2% | 552 | 44.9% | 10.2% |
| viral_breakdown_recent | date | 365 | 50 | 55,726,231 | 257,279 | 71.3% | 79.0 | 7 | 2 | 34.0% | 38 | 82.0% | 4.0% |
| map_animation_all | viewCount | all | 50 | 529,862,279 | 5,858,000 | 25.2% | 8.1 | 50 | 15 | 0.0% | 277 | 42.0% | 28.0% |
| map_animation_recent | date | 365 | 17 | 14,592,457 | 210,562 | 72.7% | 19.8 | 5 | 0 | 23.5% | 109 | 70.6% | 0.0% |
| mini_doc_all | viewCount | all | 39 | 18,045,572 | 234,638 | 34.9% | 11.6 | 5 | 0 | 12.8% | 834 | 28.2% | 10.3% |
| mini_doc_recent | date | 365 | 50 | 11,257,605 | 112,196 | 33.8% | 13.2 | 2 | 0 | 53.1% | 1432 | 24.0% | 18.0% |
| faceless_comedy_all | viewCount | all | 50 | 39,826,366 | 10,987 | 86.1% | 1548.3 | 4 | 2 | 0.0% | 97 | 60.0% | 8.0% |
| faceless_comedy_recent | date | 365 | 50 | 3,611,018 | 3,881 | 45.6% | 225.1 | 0 | 0 | 30.0% | 106 | 52.0% | 2.0% |
| sleep_ambient_all | viewCount | all | 50 | 31,690,794 | 37,282 | 44.3% | 177.3 | 8 | 0 | 0.0% | 2142 | 30.0% | 6.0% |
| sleep_ambient_recent | date | 365 | 50 | 12,371,490 | 1,072 | 93.9% | 6735.1 | 2 | 0 | 93.5% | 35 | 90.0% | 0.0% |

`Top3 share` lower = less winner-takes-all. `Winner/median` lower = easier entry. These are corpus-shape signals, not a growth ranking or a promise.

## Corpus-wide million-view signals

| Signal | Value |
| --- | --- |
| Median views | 4,222,851 |
| Median duration (s) | 180 |
| <=3 min share | 50.0% |
| Caption flag true | 10.3% |
| English default language | 96.7% |
| Median like rate | 0.0163 |
| Median comment rate | 0.00024 |
| Top title tokens | shorts(59), geography(38), satisfying(35), rescue(35), science(30), asmr(29), official(27), restoration(25), shortsbreak(24), comedyvideos(20), comedy(19), full(18), funny(18), story(16), future(16), oddly(15), chapter(15), oddlysatisfying(14), animals(14), camera(14) |
| Top tags | animals(44), viral shorts(40), science(40), youtube shorts(37), tech master(36), trending shorts(33), tiktok(32), funny shorts(29), daily dose of internet(29), comedy shorts(26), funny videos(25), tech(25), short videos(24), internet(24), internet videos(24), daily dose(24), technology(24), techno gamerz(24), gadgets(24), shorts(23) |
| Top topic categories | Entertainment(118), Lifestyle (sociology)(96), Film(76), Knowledge(57), Video game culture(48), Action-adventure game(45), Music(44), Action game(39), Pet(36), Role-playing video game(32), Television program(27), Music of Asia(26) |
| Description patterns | subscribe=191, link=286, follow=117, part2=36, comment=45, discord=62, patreon=19, ai=35, voice=8, credits=44, chapters=17 |

## Top 25 million-view videos in this API snapshot

| Title | Channel | Views | Likes | Comments | Dur s | Age d | Views/day | Cap | Lang | Category |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Cute Armadillo Rescued From Hole! | The Pet Collective | 229,123,695 | 2,470,192 | 6,316 | 31 | 1153 | 198,719.5 | N | en | Pets & Animals |
| Heart-touching Cute Kitten Dance 🐾 #shorts #kittenrescue #animalrescue #… | Story Arc Paws | 182,606,544 | 1,355,349 | 3,907 | 10 | 627 | 291,238.6 | N | en | Entertainment |
| Indirect dental restoration #satisfying | Dr. Abdom Fora | 151,511,110 | 3,338,265 | 13,904 | 51 | 946 | 160,159.7 | N | es-419 | Howto & Style |
| #shorts Relaxing Makeup Restoration pt1 #satisfying#oddly#oddlysatisfyin… | Satisfying Shorts | 135,180,786 | 3,285,329 | 1,867 | 55 | 1454 | 92,971.7 | N | en | Entertainment |
| Farrier-Hoof Restoration-Satisfying | Maupin Farrier Co | 79,574,050 | 382,307 | 17,305 | 962 | 1890 | 42,102.7 | N | en | People & Blogs |
| KING: Tu Mil Jaaye \| Shah Rukh Khan, Deepika \| Sachin-Jigar, Arijit, E… | T-Series | 74,846,365 | 739,357 | 46,333 | 223 | 11 | 6,804,215.0 | N | en | Music |
| Shocking results 😲 #science #ashortaday #funny #comedy #ashusir #science… | Science and fun | 70,675,575 | 4,652,375 | 3,780 | 60 | 1637 | 43,173.8 | N | en | Science & Technolo… |
| #funny #but #scientific #momentum #conservation #science #physics #vyase… | VYAS EDIFICATION | 68,469,217 | 1,692,092 | 2,802 | 19 | 941 | 72,762.2 | N | en-IN | Education |
| Mahiya (Official Music Video) Badshah x Shreya Ghoshal - Mahiya ft. Avne… | Badshah | 67,595,869 | 290,589 | 20,994 | 155 | 8 | 8,449,483.7 | N | en | Music |
| 🙃 ASMR \| nail day #asmr #asmrvideos #satisfying #relax #relaxing #tingl… | Nail’s | 65,451,520 | 341,710 | 2,399 | 27 | 499 | 131,165.3 | N | en | Music |
| #shorts YSL Lipstick Restoration #satisfying #oddly #oddlysatisfying #as… | Satisfying Shorts | 56,015,897 | 2,425,700 | 1,158 | 59 | 1443 | 38,819.0 | N | en | Entertainment |
| Zookeepers Break Concrete to Save Trapped Giraffe | Wisdom Pouchannel | 53,127,472 | 96,392 | 364 | 8 | 393 | 135,184.3 | N | en | Science & Technolo… |
| Angry elephant and deer rescue #shortvideo #Elephant #Leopard #Deer #Ani… | Tarazai | 49,468,762 | 122,716 | 254 | 11 | 391 | 126,518.6 | N | en | Entertainment |
| How to clean a dirty coin #cleaningdirtycoins #shorts #oddlysatisfying #… | ICONIC COINS | 47,890,416 | 1,549,152 | 40,912 | 55 | 1396 | 34,305.4 | N | en | Entertainment |
| SICK TIGER RESCUE! #animals #animalrescue #animalstories #cute #animals … | Nature Global | 47,827,365 | 1,697,405 | 10,735 | 25 | 931 | 51,372.0 | N | en | People & Blogs |
| 50 States Song - USA States and Capitals Song \| Geography Explained by … | KLT | 47,518,465 | 96,312 | 0 | 298 | 3958 | 12,005.8 | Y | en | Film & Animation |
| Why do Rivers Curve? | MinuteMinis | 46,287,002 | 2,003,299 | 10,005 | 17 | 1605 | 28,839.4 | Y | en | Education |
| Eetha \| Official Trailer \| Shraddha Kapoor \| Randeep H \| Dinesh V \|… | Maddock Films | 42,969,365 | 265,546 | 23,314 | 183 | 13 | 3,305,335.7 | Y | en | Entertainment |
| Daddy Yankee and Diljit Dosanjh - POKITO (Official Music Video) | Daddy Yankee | 42,407,333 | 493,321 | 25,839 | 248 | 13 | 3,262,102.6 | N | es-419 | Music |
| 100-Year-Old Rusty Motorcycle Restored to Brand New! \| Most Satisfying … | Revival Workshop | 40,974,369 | 436,766 | 1,858 | 33 | 98 | 418,105.9 | N | en | Sports |
| Solar System 101 \| National Geographic | National Geographic | 39,793,568 | 231,071 | 7,724 | 251 | 3361 | 11,839.9 | Y | en | Entertainment |
| Best Moments Of Animals That Asked People for Help in 2022 ! | MAD LAB | 39,745,656 | 400,015 | 13,197 | 1951 | 1434 | 27,716.6 | N | en | People & Blogs |
| ASMR cleaning this paintbrush is so satisfying | FPS | 38,069,649 | 222,502 | 966 | 11 | 639 | 59,576.9 | N | en-US | Entertainment |
| KAALI HOODIE (MUSIC VIDEO) SIDHU MOOSE WALA FT BOHEMIA \| THE KIDD | Sidhu Moose Wala | 35,974,206 | 994,097 | 160,170 | 170 | 27 | 1,332,378.0 | N | en | Music |
| This woman rescued a baby deer that was trapped under her car and then | DEKoyle | 35,337,954 | 751,629 | 7,566 | 60 | 578 | 61,138.3 | N | en | People & Blogs |

`Views/day` is a public velocity proxy from views and publish date only. It is NOT retention, CTR, RPM, or a growth ranking.

## Channel snapshot (top 20 by cumulative channel views)

| Channel | Handle | Country | Created | Age d | Subs | Channel views | Videos | Recent n | Recent med views | Cadence d | Since 2023 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T-Series | @tseries | IN | 2006-03-13 | 7549 | 316,000,000 | 363,379,839,477 | 27,522 | 25 | 134,836 | 0.1 | N |
| Tips Official | @tipsofficial | IN | 2007-05-22 | 7114 | 82,800,000 | 60,520,762,178 | 10,760 | 24 | 46,419 | 0.1 | N |
| T-Series Bhakti Sagar | @tseriesbhaktisaga… | IN | 2011-02-13 | 5751 | 83,600,000 | 51,959,344,441 | 33,207 | 24 | 47,239 | 0.3 | N |
| Shorts Break | @shortsbreak_offic… | IN | 2021-07-07 | 1954 | 48,900,000 | 44,051,776,949 | 1,093 | 25 | 1,754,922 | 1.4 | N |
| Aditya Music | @adityamusic | IN | 2008-05-01 | 6769 | 37,000,000 | 41,187,120,131 | 33,725 | 24 | 6,423 | 0.0 | N |
| Daddy Yankee | @daddyyankee | US | 2011-05-16 | 5659 | 41,800,000 | 29,696,255,216 | 640 | 25 | 145,057 | 0.0 | N |
| Fox News | @foxnews | US | 2006-09-19 | 7359 | 15,600,000 | 27,473,744,281 | 147,393 | 25 | 23,891 | 0.0 | N |
| Inside Edition | @insideedition | US | 2012-10-09 | 5147 | 13,800,000 | 26,009,029,592 | 37,716 | 25 | 30,359 | 0.0 | N |
| Ishtar Music | @ishtarmusic | IN | 2005-09-22 | 7721 | 54,100,000 | 24,777,245,053 | 7,290 | 25 | 20,365 | 0.2 | N |
| Tech Master | @techmasterhq | IN | 2021-07-24 | 1937 | 36,400,000 | 23,750,730,045 | 1,652 | 25 | 4,075,535 | 1.0 | N |
| ★ Kids Roma Show | @kidsromashow | US | 2015-05-12 | 4202 | 45,800,000 | 23,366,135,407 | 1,132 | 25 | 557,682 | 2.0 | N |
| ABC News | @abcnews | US | 2006-08-07 | 7402 | 19,900,000 | 19,383,335,906 | 123,215 | 25 | 6,871 | 0.0 | N |
| Wisdom Pouchannel | @wisdompouchannel | US | 2017-05-20 | 3463 | 10,000,000 | 18,155,964,450 | 2,581 | 25 | 123,601 | 0.1 | N |
| Daily Dose Of Internet | @dailydoseofintern… | US | 2015-07-15 | 4138 | 20,700,000 | 17,646,709,785 | 2,023 | 25 | 1,641,926 | 2.0 | N |
| The Dodo | @thedodo | US | 2014-03-21 | 4619 | 18,900,000 | 17,258,151,101 | 15,170 | 25 | 109,749 | 0.1 | N |
| Techno Gamerz | @technogamerzoffic… | IN | 2017-08-13 | 3378 | 53,600,000 | 16,823,449,278 | 1,199 | 24 | 8,738,847 | 2.2 | N |
| T-Series Hamaar Bhojpuri | @hamaarbhojpuri | IN | 2011-11-01 | 5490 | 24,700,000 | 15,390,323,965 | 12,286 | 24 | 16,878 | 0.3 | N |
| Future | @officialfuturevid… | - | 2011-11-14 | 5477 | 15,100,000 | 15,301,974,934 | 81 | 1 | 53,284 | None | N |
| LatinHype | @latinhype. | MX | 2018-08-05 | 3021 | 12,000,000 | 12,613,785,127 | 2,152 | 24 | 16,159 | 1.0 | N |
| Netflix | @netflix | US | 2012-07-17 | 5231 | 33,800,000 | 11,939,171,402 | 9,583 | 24 | 50,087 | 0.1 | N |

`Since 2023` only means the channel's public creation date is within ~3 years of this run. It is NOT a verified fastest-growing ranking.

## mostPopular snapshots

| Region | Status | n | Top 3 by views |
| --- | --- | --- | --- |
| US | ok | 50 | Maatrubhumi - Trailer \| Salman Khan, Chit… (30,927,248) | Grand Theft Auto VI: Pre-Load Now (9,463,778) | Grand Theft Auto VI - Features Trailer \| … (5,072,820) |
| PK | ok | 50 | KING: Tu Mil Jaaye \| Shah Rukh Khan, Deep… (74,846,365) | Mahiya (Official Music Video) Badshah x Sh… (67,595,869) | Eetha \| Official Trailer \| Shraddha Kapo… (42,969,365) |
| GB | ok | 50 | Maatrubhumi - Trailer \| Salman Khan, Chit… (30,927,248) | Grand Theft Auto VI: Pre-Load Now (9,463,778) | Grand Theft Auto VI - Features Trailer \| … (5,072,820) |
| IN | ok | 48 | Maatrubhumi - Trailer \| Salman Khan, Chit… (30,927,248) | Grand Theft Auto VI: Pre-Load Now (9,463,778) | GTA 5 LIVE #gta5 #gtav #gaming (7,441,689) |

## Transcript / script / hook teardowns

| Video | Transcript | Kind | Words | WPM | Grade | CTAs | First 30 words | Claim type | You | Number | Keep |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T9abiWZZros | error | None | - | - | - | - |  | - | N | N |  |
| 1GDkjZm6coU | error | None | - | - | - | - |  | - | N | N |  |
| IpdXfzr0U3c | error | None | - | - | - | - |  | - | N | N |  |
| VIain9HJZKQ | error | None | - | - | - | - |  | - | N | N |  |
| cw8gjwEtdhY | error | None | - | - | - | - |  | - | N | N |  |
| BPZkZpGMpXA | error | None | - | - | - | - |  | - | N | N |  |
| ncqHtfcgZNw | error | None | - | - | - | - |  | - | N | N |  |
| DEpThqSPkgg | error | None | - | - | - | - |  | - | N | N |  |
| fA8-gXDoAk8 | error | None | - | - | - | - |  | - | N | N |  |
| EgXkduRe9ZU | error | None | - | - | - | - |  | - | N | N |  |
| _rhMrhzDzDk | error | None | - | - | - | - |  | - | N | N |  |
| _yl5ELcmugI | error | None | - | - | - | - |  | - | N | N |  |

Only short excerpts and computed metrics are stored. No full competitor transcript is reproduced. `no_captions` is a real result, not a gap filled with invented text.

## Structure / psychology / replication (where a transcript existed)

The teardown maps co-occurrence only. It does NOT claim the video won because of any one feature.

## Top-comment mining

| Bucket | Label | Hits across sampled comment fields |
| --- | --- | --- |
| asks | asked for a sequel | 3 |
| wants | wants to buy time/teaching | 2 |
| objections | objected to cost | 1 |
| objections | objected to pacing/clarity | 1 |
| wants | wants the asset | 1 |

Most-liked comment snippets (short excerpts, not full comment threads):

- `_yl5ELcmugI` · 54027 likes · They added a backflip to counter accusations of poor animation in Jason in the extended look. Geniuses.
- `DEpThqSPkgg` · 41996 likes · That's why women live longer😂
- `_yl5ELcmugI` · 26634 likes · We made it brothers. RIP to those who didn’t
- `cw8gjwEtdhY` · 25653 likes · *Who else doesn't understand y this showed up in ur recommended list but ending up watching the whole thing*
- `ncqHtfcgZNw` · 21472 likes · Plz recognize him with president awards for teacher ....he is really giving a lot efforts
- `T9abiWZZros` · 17392 likes · Buddy was looking for that hole again 😅
- `IpdXfzr0U3c` · 15714 likes · The clean: 😎 The pain: 💀 Edit: TYSM btw u could use anesthesia to but still and its a joke Edit: y'all 15k LIKES OMG
- `DEpThqSPkgg` · 13450 likes · Who created this insane good game? Where the level up or some storms? Where 🐢🐢🐢 Thanks for 👍 It's to dumb way to death 😂😂 EDIT: WOW never have like for comment …

Caveat: shares are of the comments fetched, not of everyone who watched; a silent majority is invisible here by construction.

## Thumbnail image statistics

| Metric | Value |
| --- | --- |
| Thumbnails analysed | 24 |
| Face-present rate | 91.7% |
| Avg contrast | 0.23 |
| Avg brightness | 0.312 |
| Avg busy/edge energy | 2.51 |
| Avg accent share | 0.562 |
| Avg lower text-band energy | 2.31 |
| Hue families | [(0, 17), (3, 3), (1, 2), (5, 1), (2, 1)] |
| Note | image statistics only; not OCR, not face recognition, not video-frame editing analysis |

Per-thumbnail rows are in `thumbnail_forensics_v17.json`. These are crude image statistics with a stated purpose, not OCR and not a model's opinion.

## Files

- `channel_statistics_v17.json`
- `comments_v17.json`
- `corpus_signals_v17.json`
- `lane_metrics_v17.json`
- `lanes_v17.json`
- `million_view_videos_v17.json`
- `most_popular_v17.json`
- `recent_uploads_v17.json`
- `reverse_teardowns_v17.json`
- `run.json`
- `selected_forensic_ids_v17.json`
- `thumbnail_forensics_v17.json`
- `video_categories_v17.json`
- `video_details_v17.json`

---

**NOT claimed:** YouTube upload/publish, monetisation, legal clearance, human creative approval, family-safety guarantee, guaranteed views, virality, perfection, private retention/CTR/RPM, invented transcripts, verified growth ranking, social-platform origin, view-count causation, NASA endorsement, official status. Technical/API evidence is not creative approval. A human must still watch candidate videos and review rights before any publication.
