# V16 plan and honest source boundary

**Goal:** Replace the rejected V14/V15 20-clip pool with 20 entirely new, rights-documented, on-brand clips, then rebuild the 9-minute English compilation with the V15 curiosity intro and audio ducking kept intact.

## What was tried and abandoned

1. **Direct social acquisition (`acquire_social_v16.py`, workflow `social-v16-clips.yml`)** — 20 high-view social candidates were scouted, but `yt-dlp` downloaded only 2/20. Eighteen YouTube downloads failed; the two non-YouTube files had licence-unknown metadata and failed the hard QC. None are in the final pool. Do not retry this path.
2. **Commons broad/fuzzy viral queries** — six automated runs produced 20/20 technically passing clips each, but manual contact-sheet inspection rejected them as off-brand:
   - run 1: HIV / COVID / news / games / lectures;
   - run 2: USDA farm, volcano, silent films (pool only 23);
   - run 3: old films, NASA, USDA ads, Warm Springs horses;
   - run 4: lab-science false positives, whales, AFN TV spot, monastery;
   - run 5: autumn "Fall overlook / drive / leaves" false positives;
   - run 6: old paper print, abstract animation, military training fall.
   Root causes were bare `viral` matching medicine, fuzzy description matches, `fall` meaning autumn, and generic `sports` / `rescue` / `amazing` titles pulling military/institutional footage. Fixes were `intitle:` queries, title-on-brand gates, substring blocks, funny-first ranking, and finally an exact 20-title pin after contact-sheet review.

## Final V16 source

The final 20 are **Wikimedia Commons namespace-6 file pages** with live API-recorded PD / CC0 / CC BY metadata, per-clip Commons page, creator, licence, SHA-1 and local 10-second window SHA-256. They are Commons funny / cute animal / safe stunt moments selected by `intitle:` search and manual contact-sheet inspection.

**Honest boundary:** social / viral keywords were used only as search recall and ranking heuristics. This is **not** a claim that any selected clip went viral, originated on TikTok/Instagram/Reddit/YouTube, or has a view count. No direct social-platform files are used. No legal opinion, human legal review, upload/publish, monetisation, family-safety guarantee, guaranteed views, virality, or perfection claim. A human must still watch the full motion and native audio and review each rights page. Technical QC `ALL_PASS` is not creative approval.

## Reused from V15

- `vo/chunk_00.mp3` — the unchanged 15.14 s curiosity/FOMO intro, `voice-06`.
- Audio ducking — native 0.60 between VO, 0.15 during VO, VO 1.0, `loudnorm I=-14`.
- 120 moving beats of 4.5 s, three rounds, English burned-in captions, small lower-third source/round/counter overlays, frame-1 real footage, 960×540 / 30 fps / H.264 / AAC.

## Rewritten for V16

- `vo/chunk_01.mp3`–`chunk_10.mp3` — `voice-05`, English commentary matching the 20 new clips.
- `vo_script_v13.json` / `VO_SCRIPT_V13.md` — no V14/V15 clip references.
- `build_video_v13.py`, credits, about, QC and manifest — labelled V16 and the new clip pool. Internal `v13` filenames are pipeline identifiers only.

## Final 20 titles

1. Instant karma for treating the drivethru employee
2. Unexpected hatchlings
3. Male Polyphylla fullo beetle slipping from a Zea mays leaf
4. Burmese Kitten Grooming Itself
5. Three orange kittens following their mother
6. Pig race
7. RopeJump 160 m free fall, Aiglun, France
8. FHP trooper rescues kitten stuck in sewer
9. Squirrel Fishing
10. Sleepy short eared owl on Seedskadee NWR
11. Red Squirrel eats a nut
12. Bear inside Mammoth Lakes Library
13. Teen dives on Summersville Lake Cliff Jump
14. Muntjac Deer Barking
15. Base jump
16. Dirt jump biking
17. P-42 and Kittens
18. Red fox pups playing along Owens Bay Nature Trail
19. Young Raccoons Napping
20. Baby tropicbird vocalization

Evidence: `research/caught_on_camera_v13/rights_ledger_curated_v13.json`, `selected_windows_v13.json`, `hook_windows_curated_v13.json`, `review/validation_v13.json`, `review/curated_contact_sheet_v13.jpg`, `review/candidate_pool_v16.json`.
