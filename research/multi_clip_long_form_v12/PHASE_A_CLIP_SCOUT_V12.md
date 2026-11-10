# V12 PHASE A - Real API Clip-Moment Scout (MC-01)

> **Aage kya hua:** live `YOUTUBE_API_KEY` (GitHub Actions secret) se **5 targeted Data API queries** chalayi gayin, jo `MC-01` ke **8 analytic clip slots** par map hoti hain. Har slot ko **asli** million-view benchmarks mile. Lekin — ye **scout candidates** hain, **hamare 8 source clips nahi**. Koi clip download/clear nahi hua, koi render/VO/upload/publish nahi hua.

**Phase:** `A` · **Run:** `42895703914` · **Edition:** `v12_phase_a_clip_scout` · **Winner:** `MC-01` (unchanged) · **Status:** `SCOUT_CANDIDATES_FOUND_NO_CLIP_ACQUIRED`
**Machine-readable:** `phase_a_clip_scout_v12.json`, `api_evidence/phase_a/*.json`, `api_evidence/phase_a/run.json`

---

## 0. Seedha jawab (TL;DR)

- **5/5 real API queries success** — `lane=api`, `status=ok`, **100 real videos** measured, **82 rows 1M+ views**.
- **Sabse bada real number:** `slow motion physics explained` me ek 9-second clip ke **363,151,838 views** (UrDay, 'How lighter works close-up in #macro #slowmo'). Yani replay/slow-motion mechanic ka real audience bohat bara hai.
- **Sabse behtar rights-lane signal:** NASA/agency probe me **20/20 videos 1M+ views**, median **19,234,336**, `top3_share=0.398` → reading: *distributed — no single video owns it, entry is feasible*.
- **Lekin 5/5 topic verdicts = `NO`** (scores 20.4 – 47.2). Ye **topic packaging** ka verdict hai, hamare idea ka nahi. Iska matlab seedha: generic "viral moments / unexpected moments" title se mat jao; `MC-01` ka thesis-driven forensic angle + number-hook hi alag banata hai.
- **Hard stop abhi bhi wahi:** 8 per-clip rights gates, NASA promotional/current-astronaut gate, aur user-reported Short monetization ON. **Is gate ke bina koi clip edit me nahi jayegi.**

---

## 1. Live API run receipt

| Cheez | Value |
| --- | --- |
| Run | `42895703914` (success, 2m24s) |
| Secret | `YOUTUBE_API_KEY` — `key_present=true` |
| Secret value | **kabhi print / store / request nahi** |
| Chat sandbox direct calls | **0** (googleapis.com allowlist me nahi) |
| Bot commit | `6db3924` — 5 reports + `run.json` |

| # | Query | Order | Slots | n | 1M+ | Verdict | Score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | unexpected moment caught on camera | viewCount | [1, 7] | 20 | 20 | NO | 32.4 |
| 2 | slow motion physics explained | viewCount | [2, 3] | 20 | 20 | NO | 47.2 |
| 3 | optical illusion scale size | relevance | [4] | 20 | 15 | NO | 35.5 |
| 4 | viral moment reaction explained | viewCount | [5, 6, 8] | 20 | 7 | NO | 20.4 |
| 5 | nasa official science demonstration | viewCount | rights-lane probe (shared) | 20 | 20 | NO | 41.1 |

---

## 2. Real numbers (poori hisaab-kitaab)

| Report | Total views | Median views | top3_share | fresh_30d | Reading | Top views |
| --- | --- | --- | --- | --- | --- | --- |
| slot-01-07-expectation-violation | 647,165,488 | 14,818,841 | 0.555 | 0.0 | distributed — no single video owns it, entry is feasible | 204,729,002 |
| slot-02-03-physics-timing | 832,427,286 | 11,964,655 | 0.695 | 0.0 | distributed — no single video owns it, entry is feasible | 363,151,838 |
| slot-04-scale-illusion | 192,388,683 | 3,062,858 | 0.691 | 0.0 | distributed — no single video owns it, entry is feasible | 92,776,824 |
| slot-05-06-08-sound-reaction-callback | 170,152,920 | 656,494 | 0.918 | 0.05 | concentrated — a few videos own the topic, a new entrant must out-execute them | 98,022,417 |
| rights-lane-nasa-agency-probe | 494,286,865 | 19,234,336 | 0.398 | 0.0 | distributed — no single video owns it, entry is feasible | 127,067,555 |

### 2.1 Decision parts (real, khush-numa nahi)

| Report | demand | winnability | mechanism | reason |
| --- | --- | --- | --- | --- |
| slot-01-07-expectation-violation | 29.7 | 44.49999999999999 | 10.0 | the numbers do not support a day of production |
| slot-02-03-physics-timing | 79.2 | 18.500000000000004 | 35.0 | the numbers do not support a day of production |
| slot-04-scale-illusion | 56.4 | 18.900000000000006 | 25.0 | the numbers do not support a day of production |
| slot-05-06-08-sound-reaction-callback | 49.4 | 1.914285714285711 | 0.0 | the numbers do not support a day of production |
| rights-lane-nasa-agency-probe | 46.0 | 60.199999999999996 | 10.0 | the numbers do not support a day of production |

### 2.2 Teen imaandaar warnings

1. **`fresh_share_30d = 0.0`** 4/5 reports me — ye `order=viewCount` ka **sampling artifact** hai (all-time classics wapas aate hain), iska matlab "naya demand nahi hai" **nahi**. Isko trend ka saboot bana kar pesh nahi kiya gaya.
2. **Number-in-title ka signal aapas me ulta hai:** NASA probe me `has_number_pct = -54.4%`, expectation-violation me -65.4%, lekin scale-illusion me +389.0% (aur uska fit `r2 = 0.093` yani **weak**). Isliye hamare working title ka "8" koi **proven law** nahi — ye ek tested hook variant hai, aur A/B test (Studio Test & Compare) se hi confirm hoga.
3. **`verdict=NO` hamare idea ka verdict nahi.** Ye tool kisi *search topic* ko enter karne ki economics batata hai. Hamara koi video abhi bana hi nahi, isliye isse "idea reject" ya "guaranteed hit" dono nahi nikala ja sakta.

---

## 3. 8 CLIP SLOT CARDS (asli benchmark candidates ke saath)

> Har card me **3 real videos** hain jo us slot ke query me sabse zyada views wale the. Ye **structural benchmarks** hain: dekhne ke liye ki audience kis mechanic par rewatch karti hai. **Inme se koi bhi hamara source clip nahi** — teesre-party copyrighted videos hain. Har card ke neeche rights fields **sab `null` / `pending`** hain.

### SLOT 1 — `expectation violation`

- **Chapter:** `1:40-2:55` · CLIP 1 - expectation violation
- **On-screen:** <= 10s · **VO budget:** 130 words · **Original diagram:** ORIGINAL expected-vs-actual split diagram, our own shapes/text, no source logo
- **Commentary beat:** Show the clip cold, freeze on the exact frame where the expectation breaks, then an ORIGINAL two-column diagram: what the viewer predicted vs what actually happened. One sentence naming the delay between surprise and explanation.
- **Scout query:** `unexpected moment caught on camera` (`order=viewCount`, 20 rows, 20 with 1M+ views)

| Real benchmark (NOT a source clip) | Channel | Views | Duration |
| --- | --- | --- | --- |
| `KT3e_lKrNss` Ranking Unexpected Baby First Words 👶 | Ice Ranks | 204,729,002 | PT49S |
| `JYTg_8Ui1Ho` THE MOST AMAZING SAVES! #shorts | Paul Foisy Facts | 91,496,434 | PT26S |
| `Sy5b_3ZH-rM` This Police Officer is Hilarious - Unexpected Encounter With NYPD! 😂 #shorts | Cop Humor | 62,638,996 | PT20S |

- **Candidate source lanes:** official agency libraries (**DIFFERENT assets only**), CC BY with full attribution, verified public-domain agency originals, own-shot footage, or licensed clips with written permission.
- **Rights gate:** all 18 fields `null` · `clearance_status=pending` · `human_legal_review=false` · `clip_downloaded=false` · `clip_cleared=false`.

### SLOT 2 — `physics / optics surprise`

- **Chapter:** `2:55-4:05` · CLIP 2 - the physics surprise
- **On-screen:** <= 10s · **VO budget:** 135 words · **Original diagram:** ORIGINAL optics / force diagram, no stock b-roll as hero
- **Commentary beat:** Play <=10s, replay at 0.5x, then explain the mechanism with an original ray/force diagram. Factual claim anchored to a first-party official source; state the source on screen.
- **Scout query:** `slow motion physics explained` (`order=viewCount`, 20 rows, 20 with 1M+ views)

| Real benchmark (NOT a source clip) | Channel | Views | Duration |
| --- | --- | --- | --- |
| `ro-vkofFP3E` How lighter works close-up in #macro #slowmo | UrDay | 363,151,838 | PT9S |
| `LgtQ3NL01As` REALITY vs SLOW MOTION! 🎥 | Legendary Shots | 155,827,569 | PT30S |
| `fgLf_dcZy9Q` Visualizing Magnetic Fields with Slow Mo #shorts #slowmoguys | The Slow Mo Guys | 59,568,824 | PT54S |

- **Candidate source lanes:** official agency libraries (**DIFFERENT assets only**), CC BY with full attribution, verified public-domain agency originals, own-shot footage, or licensed clips with written permission.
- **Rights gate:** all 18 fields `null` · `clearance_status=pending` · `human_legal_review=false` · `clip_downloaded=false` · `clip_cleared=false`.

### SLOT 3 — `timing / slow-motion frame`

- **Chapter:** `4:05-5:10` · CLIP 3 - timing / slow motion
- **On-screen:** <= 10s · **VO budget:** 120 words · **Original diagram:** ORIGINAL frame-timeline with 3 labelled speed bands
- **Commentary beat:** Show the same moment at 1x, 0.5x, 0.25x in three labelled passes. Identify which single frame carries the surprise; do not claim the creator intended it.
- **Scout query:** `slow motion physics explained` (`order=viewCount`, 20 rows, 20 with 1M+ views)

| Real benchmark (NOT a source clip) | Channel | Views | Duration |
| --- | --- | --- | --- |
| `ro-vkofFP3E` How lighter works close-up in #macro #slowmo | UrDay | 363,151,838 | PT9S |
| `LgtQ3NL01As` REALITY vs SLOW MOTION! 🎥 | Legendary Shots | 155,827,569 | PT30S |
| `fgLf_dcZy9Q` Visualizing Magnetic Fields with Slow Mo #shorts #slowmoguys | The Slow Mo Guys | 59,568,824 | PT54S |

- **Candidate source lanes:** official agency libraries (**DIFFERENT assets only**), CC BY with full attribution, verified public-domain agency originals, own-shot footage, or licensed clips with written permission.
- **Rights gate:** all 18 fields `null` · `clearance_status=pending` · `human_legal_review=false` · `clip_downloaded=false` · `clip_cleared=false`.

### SLOT 4 — `scale / size illusion`

- **Chapter:** `5:10-6:15` · CLIP 4 - scale / size illusion
- **On-screen:** <= 10s · **VO budget:** 120 words · **Original diagram:** ORIGINAL scale comparison with a stated reference length
- **Commentary beat:** Clip <=10s, then an original scale diagram with a labelled reference object. Explain the missing reference cue, not 'the camera tricks you'.
- **Scout query:** `optical illusion scale size` (`order=relevance`, 20 rows, 15 with 1M+ views)

| Real benchmark (NOT a source clip) | Channel | Views | Duration |
| --- | --- | --- | --- |
| `FHJ3CMWnVxY` Furniture Optical Illusions - Zach King Magic | Zach King | 92,776,824 | PT3M55S |
| `jBEEsLeKoUM` Dogs funny reaction to entering optical illusion rug! #shorts | My Mountain Husky | 21,364,400 | PT17S |
| `-IWk5NkxQF8` 10 Mind Blowing Optical Illusions | TheRichest | 18,835,155 | PT3M59S |

- **Candidate source lanes:** official agency libraries (**DIFFERENT assets only**), CC BY with full attribution, verified public-domain agency originals, own-shot footage, or licensed clips with written permission.
- **Rights gate:** all 18 fields `null` · `clearance_status=pending` · `human_legal_review=false` · `clip_downloaded=false` · `clip_cleared=false`.

### SLOT 5 — `native sound vs silence`

- **Chapter:** `6:15-7:10` · CLIP 5 - sound and silence
- **On-screen:** <= 10s · **VO budget:** 105 words · **Original diagram:** ORIGINAL two-row A/B waveform/beat diagram (drawn, not sampled audio)
- **Commentary beat:** Two passes: native audio, then muted with our commentary. Retain the source's native audio; no music or SFX substitution. Compare what the sound contributed to the replay impulse.
- **Scout query:** `viral moment reaction explained` (`order=viewCount`, 20 rows, 7 with 1M+ views)

| Real benchmark (NOT a source clip) | Channel | Views | Duration |
| --- | --- | --- | --- |
| `cU5uVnWL1Us` Lil Durk - Viral Moment (Official Music Video) | Lil Durk | 98,022,417 | PT3M26S |
| `FfFsz9TvXeI` Bradford goes viral for being #GrumpyCop! or #TheRookie (SPOILERS!) | The Rookie (Fan Page) | 54,311,920 | PT57S |
| `3gJbBnLyUBI` Akanksha Choudhary 😂🔥 Talks About That Viral Dance Everyone’s Talking About  #shorts #splitsvilla | PINKVILLA | 3,802,491 | PT50S |

- **Candidate source lanes:** official agency libraries (**DIFFERENT assets only**), CC BY with full attribution, verified public-domain agency originals, own-shot footage, or licensed clips with written permission.
- **Rights gate:** all 18 fields `null` · `clearance_status=pending` · `human_legal_review=false` · `clip_downloaded=false` · `clip_cleared=false`.

### SLOT 6 — `human reaction beat`

- **Chapter:** `7:10-8:00` · CLIP 6 - the human reaction
- **On-screen:** <= 10s · **VO budget:** 95 words · **Original diagram:** ORIGINAL attention-reset timeline, no face crop reused as thumbnail
- **Commentary beat:** Clip <=10s, then explain why a face or laugh resets attention. No astronaut/person name used promotionally; no endorsement implied; identifiable-person check is a hard gate.
- **Scout query:** `viral moment reaction explained` (`order=viewCount`, 20 rows, 7 with 1M+ views)

| Real benchmark (NOT a source clip) | Channel | Views | Duration |
| --- | --- | --- | --- |
| `cU5uVnWL1Us` Lil Durk - Viral Moment (Official Music Video) | Lil Durk | 98,022,417 | PT3M26S |
| `FfFsz9TvXeI` Bradford goes viral for being #GrumpyCop! or #TheRookie (SPOILERS!) | The Rookie (Fan Page) | 54,311,920 | PT57S |
| `3gJbBnLyUBI` Akanksha Choudhary 😂🔥 Talks About That Viral Dance Everyone’s Talking About  #shorts #splitsvilla | PINKVILLA | 3,802,491 | PT50S |

- **Candidate source lanes:** official agency libraries (**DIFFERENT assets only**), CC BY with full attribution, verified public-domain agency originals, own-shot footage, or licensed clips with written permission.
- **Rights gate:** all 18 fields `null` · `clearance_status=pending` · `human_legal_review=false` · `clip_downloaded=false` · `clip_cleared=false`.

### SLOT 7 — `near-miss / coincidence`

- **Chapter:** `8:00-8:45` · CLIP 7 - the near-miss / coincidence
- **On-screen:** <= 10s · **VO budget:** 85 words · **Original diagram:** ORIGINAL two-track converging timeline, sourced only from verified facts
- **Commentary beat:** Clip <=10s, then an original timeline graphic of the two converging events. No invented date, injury, outcome or quote.
- **Scout query:** `unexpected moment caught on camera` (`order=viewCount`, 20 rows, 20 with 1M+ views)

| Real benchmark (NOT a source clip) | Channel | Views | Duration |
| --- | --- | --- | --- |
| `KT3e_lKrNss` Ranking Unexpected Baby First Words 👶 | Ice Ranks | 204,729,002 | PT49S |
| `JYTg_8Ui1Ho` THE MOST AMAZING SAVES! #shorts | Paul Foisy Facts | 91,496,434 | PT26S |
| `Sy5b_3ZH-rM` This Police Officer is Hilarious - Unexpected Encounter With NYPD! 😂 #shorts | Cop Humor | 62,638,996 | PT20S |

- **Candidate source lanes:** official agency libraries (**DIFFERENT assets only**), CC BY with full attribution, verified public-domain agency originals, own-shot footage, or licensed clips with written permission.
- **Rights gate:** all 18 fields `null` · `clearance_status=pending` · `human_legal_review=false` · `clip_downloaded=false` · `clip_cleared=false`.

### SLOT 8 — `prediction test / callback`

- **Chapter:** `8:45-9:25` · CLIP 8 + the prediction test (MC-02 folded in)
- **On-screen:** <= 10s · **VO budget:** 75 words · **Original diagram:** ORIGINAL 8-slot callback grid, one cell per DIFFERENT clip
- **Commentary beat:** Play the 8th clip WITHOUT explanation, ask the viewer to predict the replay point, then reveal how the earlier 7 clips set up the rule. Closes the thesis loop; no outcome promise.
- **Scout query:** `viral moment reaction explained` (`order=viewCount`, 20 rows, 7 with 1M+ views)

| Real benchmark (NOT a source clip) | Channel | Views | Duration |
| --- | --- | --- | --- |
| `cU5uVnWL1Us` Lil Durk - Viral Moment (Official Music Video) | Lil Durk | 98,022,417 | PT3M26S |
| `FfFsz9TvXeI` Bradford goes viral for being #GrumpyCop! or #TheRookie (SPOILERS!) | The Rookie (Fan Page) | 54,311,920 | PT57S |
| `3gJbBnLyUBI` Akanksha Choudhary 😂🔥 Talks About That Viral Dance Everyone’s Talking About  #shorts #splitsvilla | PINKVILLA | 3,802,491 | PT50S |

- **Candidate source lanes:** official agency libraries (**DIFFERENT assets only**), CC BY with full attribution, verified public-domain agency originals, own-shot footage, or licensed clips with written permission.
- **Rights gate:** all 18 fields `null` · `clearance_status=pending` · `human_legal_review=false` · `clip_downloaded=false` · `clip_cleared=false`.

---

## 4. NASA / agency rights-lane probe — aur uske exclusions

API ne agency-owned channels ke **10 real videos** diye. Ye sabse qareebi **rights-lane** hai (official source URL mil sakta hai), lekin **abhi koi cleared source nahi**: NASA brand/insignia, current astronauts, promotional use, native audio, endorsement wording — sab per-clip check aur **human legal review** maangte hain.

| Agency video (real ID) | Channel | Views | Status | Kyun |
| --- | --- | --- | --- | --- |
| `Riauw5UTnW8` NASA or Sarychev Volcano Eruption from the International Space Station | NASA Goddard | 127,067,555 | PROBE_ONLY_NOT_A_SOURCE_CLIP | Agency-owned channel found by the API; still needs per-clip licence, insignia, native-audio, endorsement and promotional-use checks. |
| `z-j1uxBmis0` NASA’s Artemis II Crew Flies Around the Moon (Official Broadcast) | NASA | 28,162,374 | EXCLUDED_PENDING_HUMAN_LEGAL_REVIEW | Current named crew / official mission broadcast: NASA promotional + current-astronaut + identifiable-person gate is OPEN. |
| `o8TssbmY-GM` Wringing out Water on the ISS - for Science! | Canadian Space Agency | 21,675,484 | REJECT_FOR_NOW | DIFFERENT asset from the V10/Short (different agency, different video ID), but the SAME water-bubble physics family - not a fresh 'different moment' for this episode. |
| `S9HdPi9Ikhk` Restored Apollo 11 Moonwalk - Original NASA EVA Mission Video - Walking on the Moon | NASA | 20,440,041 | PROBE_ONLY_NOT_A_SOURCE_CLIP | Agency-owned channel found by the API; still needs per-clip licence, insignia, native-audio, endorsement and promotional-use checks. |
| `Tf_UjBMIzNo` NASA's Artemis II Crew Launches To The Moon (Official Broadcast) | NASA | 19,297,600 | EXCLUDED_PENDING_HUMAN_LEGAL_REVIEW | Current named crew / official mission broadcast: NASA promotional + current-astronaut + identifiable-person gate is OPEN. |
| `pMsvr55cTZ0` Making History: NASA and SpaceX Launch Astronauts to Space! (#LaunchAmerica Success May 30, 2020) | NASA | 19,234,336 | PROBE_ONLY_NOT_A_SOURCE_CLIP | Agency-owned channel found by the API; still needs per-clip licence, insignia, native-audio, endorsement and promotional-use checks. |
| `4czjS9h4Fpg` Perseverance Rover’s Descent and Touchdown on Mars (Official NASA Video) | NASA | 17,976,193 | PROBE_ONLY_NOT_A_SOURCE_CLIP | Agency-owned channel found by the API; still needs per-clip licence, insignia, native-audio, endorsement and promotional-use checks. |
| `2MJY_ptQW1o` 2024 Total Solar Eclipse: Through the Eyes of NASA (Official Broadcast) | NASA | 11,927,486 | PROBE_ONLY_NOT_A_SOURCE_CLIP | Agency-owned channel found by the API; still needs per-clip licence, insignia, native-audio, endorsement and promotional-use checks. |
| `_T8cn2J13-4` How We Are Going to the Moon - 4K | NASA | 11,861,385 | PROBE_ONLY_NOT_A_SOURCE_CLIP | Agency-owned channel found by the API; still needs per-clip licence, insignia, native-audio, endorsement and promotional-use checks. |
| `7nT7JGZMbtM` James Webb Space Telescope Launch — Official NASA Broadcast | NASA | 11,460,738 | PROBE_ONLY_NOT_A_SOURCE_CLIP | Agency-owned channel found by the API; still needs per-clip licence, insignia, native-audio, endorsement and promotional-use checks. |

> 🔴 **V10/Short clip abhi bhi EXCLUDED** (`art002m1200950026_SHARED_Returned_0025_Z9_019_Wiseman`) — hero, callback, montage filler ya poore video ka subject, kisi bhi 8 slot me nahi. Aur upar wala Canadian Space Agency water-bubble video **alag asset** hone ke bawajood **REJECT FOR NOW** hai kyunki wohi physics family dohrata hai — aapne "DUSRI bohat saari best clips/moments" manga tha, wahi paani wala moment nahi.

---

## 5. Production blueprint (SPEC ONLY — kuch execute nahi hua)

**VO budget:** 1150 words / 13 chapters · **Runtime:** 600s · **Source footage:** <=80s (**<=13.3%**) · **Har clip:** <=10s on screen + 35-45s hamari apni analysis + 1 original diagram.

| # | Time | Chapter | VO words | Beat |
| --- | --- | --- | --- | --- |
| 1 | 0:00-0:20 | Cold open: 3-second montage of 8 different moments | 25 | One fast cut from each of 8 DIFFERENT clips (0.8-1.2s each), no logo, no greeting, native audio only. Then the one-line hook. |
| 2 | 0:20-0:55 | The promise and the rule | 75 | Name the thesis plainly: a rewatch happens when an expectation breaks and the explanation arrives one beat late. Promise 8 proofs. No outcome promise. |
| 3 | 0:55-1:40 | Why 'rewatched or shared' is a real signal | 110 | YouTube's own Help calls those moments Spikes; Intro is % still watching after 30s; Dips are skips. State the metric source, then say our own Analytics is not available. |
| 4 | 1:40-2:55 | CLIP 1 - expectation violation | 130 | See slot 1 card. |
| 5 | 2:55-4:05 | CLIP 2 - the physics surprise | 135 | See slot 2 card. |
| 6 | 4:05-5:10 | CLIP 3 - timing / slow motion | 120 | See slot 3 card. |
| 7 | 5:10-6:15 | CLIP 4 - scale / size illusion | 120 | See slot 4 card. |
| 8 | 6:15-7:10 | CLIP 5 - sound and silence | 105 | See slot 5 card. |
| 9 | 7:10-8:00 | CLIP 6 - the human reaction | 95 | See slot 6 card. |
| 10 | 8:00-8:45 | CLIP 7 - the near-miss / coincidence | 85 | See slot 7 card. |
| 11 | 8:45-9:25 | CLIP 8 + the prediction test (MC-02 folded in) | 75 | See slot 8 card. |
| 12 | 9:25-9:50 | The rule, restated + honest limits | 55 | One screen with the 6-step rule; say plainly what we could not verify (no owner-only competitor retention/CTR/RPM, no arbitrary competitor transcripts, no human review, no per-clip clearance). Public Data API view counts were used for scouting, not as proof of our own result. |
| 13 | 9:50-10:00 | Genuine question + series teaser | 20 | One specific question, one next-episode teaser. No like/subscribe coercion or reward. |

**Edit spec:** `canvas`=16:9 landscape, 30fps, H.264 + AAC; `runtime_seconds`=600; `chapters`=13; `source_footage_max_seconds`=80; `source_share_max_pct`=13.3; `per_clip_max_on_screen_seconds`=10; `replay_passes`=1x, 0.5x, 0.25x; `audio`=retain native audio of each verified source; no music/SFX substitution; original VO only after rights gate; `pattern`=one original diagram + one labelled replay after each clip; no clip strung together with little narrative; `loudness_target`=-14 LUFS (spec copied from V10 QC, NOT a V12 measurement); `status`=SPEC_ONLY_NOT_RENDERED

> Ye **beat sheet + word budget** hai, **final VO script nahi**. Script/voice/edit ka kaam **Phase B rights gate ke baad** hoga — kyunki bina clear kiye clip par script likhna us clip ko edit me le jane jaisa hi hai. Koi MP4, koi WAV, koi VO audio nahi bana.

---

## 6. Hard stop — Phase B

> **NO clip enters the edit until** har slot ke liye ye 18 fields verified values se bharein aur `human_legal_review=true` ho:

`official_source_url`, `nasa_or_agency_asset_id`, `licence_basis`, `third_party_copyrighted_material_check`, `identifiable_persons_check`, `current_astronaut_or_employee_check`, `promotional_or_cover_art_use`, `native_audio_rights`, `attribution_string`, `no_endorsement_implied_wording`, `no_insignia_confirmed`, `sha256_after_download`, `duration_seconds`, `scout_score_out_of_100`, `scout_min_pass_78`, `clearance_status`, `human_legal_review`, `not_a_legal_opinion`

**Open gates (unchanged):** NASA promotional / current-astronaut imagery; 8 per-clip rights chains; user-reported Short monetization ON; render toolchain; AI-use toggle; human listening / creative approval / legal review.

---

## 7. Jo main nahi bolunga

- `clip_downloaded` = **False**
- `clip_cleared` = **False**
- `legal_opinion` = **False**
- `human_legal_review` = **False**
- `commercial_monetization_clearance` = **False**
- `render_done` = **False**
- `vo_generated` = **False**
- `final_script_written` = **False**
- `upload_done` = **False**
- `publish_done` = **False**
- `monetization_changed` = **False**
- `human_creative_approval` = **False**
- `guaranteed_views` = **False**
- `guaranteed_retention` = **False**
- `guaranteed_virality` = **False**
- `perfection` = **False**
- `flawlessness` = **False**
- `nasa_endorsement` = **False**
- `verified_growth_ranking` = **False**
- `competitor_transcripts_obtained` = **False**
- `owner_only_analytics_obtained` = **False**
- `api_secret_value_read` = **False**

**Seedha:** NO legal clearance, NO guaranteed views, NO guaranteed retention, NO guaranteed virality, NO human creative approval, NO monetization change, NO upload, NO publish, NO render, NO final VO script or audio.

Koi verified "best growing channels" ranking, competitor retention/CTR/RPM graph, arbitrary competitor transcript, guaranteed views, legal opinion, NASA endorsement ya perfection ka dawa nahi. Jo figures hain wo **public Data API view counts** hain, jo kisi ke bhi dekhne ke liye available hain — private analytics nahi.

---

## 8. Agla qadam

1. **Phase B (hard stop):** in 8 slots me se har clip ka `official_source_url` + licence basis + SHA-256 + identifiable-person / promotional / native-audio checks + **human legal review**. Ye main khud complete nahi kar sakta — aapki / reviewer ki zarurat hai.
2. Uske baad final VO script → voice → edit → QC → metadata.
3. Pending safety: uploaded V10 Short ka monetization OFF (aapne ON bataya tha).
4. Chahein to aur targeted API queries chalayein (`yt-intel topic` / `reverse`) — key ab available hai, workflow `yt-phase-a-scout-v12.yml` tayyar hai.

