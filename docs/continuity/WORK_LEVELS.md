# Work levels — everything preserved, level by level

This file is the human-readable map of every known work level. Exact source files, commits, runs, hashes, screenshots and external IDs are in `EVIDENCE_MANIFEST.json`, `evidence/github/`, `external/APP_SNAPSHOT.json` and `sessions/`.

## Level 0 — repo structure and operating model

`README.md`, `docs/architecture/`, `config/spaces.json`, `config/channels.json`, `config/repos.json`:

- One core repo, one deploy, five spaces: `yt-automation`, `monarch-studio`, `personal-brand`, `portfolio`, `ops`.
- `config/spaces.json` version 1, updated 2026-11-03.
- Channels: `ch-01 Monarch Lab @monarchlab` (AI/tools/making, long-form, 2/week, 8–12 min + 3 shorts), `ch-02 Mindful Momentum` (motivation shorts, 1/day, 30–45s), `ch-03 Curious Miles` (exploration/learning, 1/week, 6–10 min). `ch-02` has `conflict_flag`.
- `docs/architecture/02-REPO-REGISTRY.md`: 22 repos, core `Monarch.Overall.Work`, satellites (`Monarch-Studio`, `Monarch.Stickman`, `portfolio`, `Monarch-Agent`, `Maya`), asset stores (`Social-media-Ref-Content-`, `World-Channel-`), archive candidates; “satellite referenced, never merged”.
- Root README says Arena history is not auto-imported and YouTube/social publishing is not connected. This continuity archive addresses the repo-backed part; it does not claim auto-import of future chats.

## Level 1 — earlier V2/V3 ranking Short work

- Original → premium → CLEAN → V2 built, QC'd and delivered. Runs `42264831336/12c8b22`, `26e0afe45`, `42309370914/7131c49`, `42315606019/4bda159`; docs `[skip ci] e2452e3`; 20s run `42234615251` rejected; cancel/dispatch 403.
- V3 audited reference `08-ocSDpt7o`; user answers `build_v3/new_cleared_animal/subtle_rank/35s_ent`; five CC0 Commons sources; docs `[skip ci] 4ac2be2…`, build `410095112`; recon runs `42341799221/128310881335`, `42343517075`; failed/hung `42376100464`, `42377948163`, `42382694165`; gates `221b897…`; `gh run watch 42383560080 --exit-status` rc0 in 7m52s; ff-only `221b897..2ec2671`; artifact `13579076898`; V3 MP4 presented.
- Preserved deliverable: `deliverables/MONARCH_CAM_5_..._CLEAN_PREMIUM_V3.mp4`.

## Level 2 — V4 ranking Short (rejected)

- User choices: `new_v4/raw_only/rank_title`, `dynamic_cover/shorten/keep_35`, `replace_silent_sources`.
- `/tmp/make_v4.py` wrote 15 files plus `.gitignore` at `12a005f…`; diagnostics via `/tmp/simvenv`, `/tmp/yamlvenv5`, FFmpeg tests.
- Commits/runs: `170ad45…/42398535407`, `b6fdc7f…/42398946091`, `50669b8…/42399953907`, `9984d7e…/42401006868`, `46c3118…`, `216635e…`, `7299557…`, `1abc62d…`; failures `42396617606`, `42397191709`, `42401490506`, `42402744112`, `42403697302` resolved.
- Final run `42404195062/128498253881` rc0, artifact `13587220215`, ff-only `1abc62d..331eafb`; MP4/QC/nine gates/audit/visual QC/preservation verified and presented.
- V4 MP4 `57,405,096` bytes, SHA-256 `2bc12b0bc0422c93b401b0af67499dba3a034584abbe15e3712f51f7f994af28`.
- **Rejected:** “sirf text likh diya”. Technical completion is not creative acceptance.

## Level 3 — V5 ranking Short (rejected)

- User choices: `new_v5_both/full/seven_60`; reference screenshots and YouTube Short `08-ocSDpt7o`; V4/V3 scripts, workflows, specs, manifests, QC and gates inspected.
- Seven per-title Commons `prop=imageinfo` calls verified CC0 for Uluwatu 3/4, Berlin mov09/mov01, Bois begging/bowing, oriental dove. No emoji/symbola/noto fonts; local `PIL` missing; V4 35s/1050f hard-codes identified; silent/bogus-duration `Lucanus Cervus fighting.webm` rejected.
- Local drafts backed to `/tmp/monarch_stale_backup` and `/tmp/v5_local_backup`; stale `.gitignore` restored; `git clean`; explicit-refspec fetch; ff-only `ac3a529..331eafb` and later `99f4548..8fc1dcd`.
- `/tmp/make_v5_static.py` created manifest/spec/metadata/docs/trigger/review upload text; `validate_raw_v5.py`, `verify_v5_sources.py`, `source_recon_ranking.py`, `probe_v5_candidates.py`, audio/render/QC scripts and `.github/workflows/monarch-cam-short-ranking-raw-v5.yml`.
- Commits/runs: `ff52bd9` build, diagnostics `f5c1c6f`, `f0a92fb`, `14ef4a2`, fixes `27b0a44`, `ff8aa55`, `99f4548349ee6213315d01d97587673c204f9c20`; successful run `42430602404` rc0; `[skip ci] 8fc1dcd` returned MP4/QC; docs `[skip ci] 393edd6` corrected static wording; artifact `13597706464`, `37,855,740` bytes, `expired=false`; failures `42429961015`, `42429256832`, `42427990187`.
- V5 deliverable `deliverables/MONARCH_CAM_7_Unexpected_Animal_Moments_Ranked_60s_Short_RAW_FULLSCREEN_V5.mp4`: `28,043,097` bytes, SHA-256 `8948f67f4ab0fb419fd1d53a10f1db68a0c6848347aa80961a1a607f9806306a`; `60.0s`, `1080x1920`, `30fps`, `1800` frames; seven moments; `review/qc_summary.json` matches sha/bytes/duration/frames.
- Static durations `[9,9,9,9,9,4,11]`s; frames `[270,270,270,270,270,120,330]`; ranks `[7,6,5,4,3,2,1]`; exact in/out/labels in `review/selected_windows.json` and `ranking_short_spec.json`.
- Visual spec: `full_screen=true`, `cover_mode=dynamic_subject_safe_cover`, source aspect preserved, no letterbox/black bars/blurred background/action window, colorful hook, persistent list, progressive labels, payoff cuts/zoom, reaction/emoji pops, seven moments only, hard cuts only, native color, `light_contrast_lift=1.02`; `hook_seconds=1.5`; hook lines `["RANKING","7 UNEXPECTED","ANIMAL MOMENTS"]`; question `WHICH ONE IS #1?`; list `x=650,y=460,w=390,row_h=96`; `label_reveal_at=0.12`, `payoff_at=0.7`, `reaction_at=0.72`, `payoff_zoom=1.22`; `seven_cc0_sources=true` needs revision for any V6.
- Audio policy: raw per-window native audio only, seven audible segments, zero silent. `showreel/audio_qc/gates.py`: `lufs=-14.0`, `tol=0.7`, `tp=-1.0`, `lra=(1.0,10.0)`, movement `>=3.0`, no clipping/clicks, mono low-band loss `>-3.0`, `dc_offset<0.002`, not harsh.
- QC: `review/technical_qc.json` `passed=true` 40 checks no failures; `review/audio_qc.json` `pass=true` 9/9 web gates; `qc_summary.json` 47/47 flags true. Human/full-motion/listening/sign-off and human/outcome/AI/audio-layer false flags remain false. Runner/visual records show `runner_probe_passed=true`, `runner_audio_visual_probe_passed=true`, `runner_visual_motion_probe=true`, `contact_sheets_written=true`, `source_review_recorded=true`, `visual_lock_written=true`; `visual_review_lock.json` `LOCKED_FOR_V5_RENDER`.
- `candidate_sources.json`: 11 CC0 assets (`uluwatu_heist`, `uluwatu_bag`, `berlin_crow_bath`, `berlin_squirrel_monkey`, `bois_crow_follow`, `cape_squirrel`, `oriental_dove`, `malaga_animals`, `tidepool_worm`, `sasana_squirrel`, `berlin_gorilla`). `verify_sources.py` strict CC0-only; `candidate_audio_probe.py` `SR=48000`, `WINDOW_S=0.5`, `SEGMENT_S=8.6`, `AUDIBLE_DBFS=-70.0`, `SELECTABLE_DBFS=-55.0`, `MIN_MOTION=0.4`; `select_moments.py` `FRAME_DURATIONS=[257]*6+[258]`, `eligible[:7][::-1]`.
- **Rejected:** “NAHI abhi bhi theek se nhi” plus four screenshots. `review/cover_hook.jpg` shows V5 hook lines/question occluded by the `1.–7. LIST`; `render_ranking_visual_raw_v5.py` uses centered 104pt hook lines `y=300+150i`, question 72pt `y=800`, list `(650,460)-(1040,1186)`, rank burst `(60,1430)`, reaction `(60,1080,540,150)`. Do not reuse unchanged. `technical_qc_raw_v5.py` has no safe-area/social-origin check.
- No human full-motion/native-audio listening, approval, sign-off, perfection, retention, virality or audience-result claim exists.

## Level 4 — V6 intent (not built)

- V5 stays untouched. A new separate V6 package was intended, but **no V6 `.gitignore` exception, workflow, source ledger, rights-verified social-platform clips, extracted scenes, renderer, QC contract, MP4, run or final delivery exists**.
- Reference screenshots require centered top hook and left `1.`–`7.` black label plates fully on-screen, progressive labels (`Backflip combo`, `That was quick`, `Bro charge it up 😭`, `Wind turbine hit:`, `That’s unexpected 🤯`, `Bro made his day`), cone/ball and shoe/street payoffs, white “Bro made sure Someone saw it 😭”, black `WHAT!!`, right platform UI and bottom comment/Subscribe. No V5 right panel/bottom rank burst.
- Broad Commons searches returned mixed PD/CC BY/CC BY-SA/FAL/silent leads. Platform totals `1160/186/287/7456`; newer `TikTok cat 10`, `Instagram cat 169`, `Reddit cat 1`, `Reddit dog 5`, `"YouTube" "funny animals" 30`. `Category:CC0 videos` empty; `incategory:"CC0 videos" animal` 0.
- Rejected/unselected: unverified platform reposts/@onlymeamro footage, old Soviet cartoons, FAL Peuple Loup clips, silent/graphic Reddit K9/dog-wolf/pitbull clips, unverified TikTok heroic-cat, Oriental Cat Shorts, `Animals Workout Mix II`, `Adorable Animals...`, `Hutong Meow`, `Most Funny and Cute Baby Elephant...` (YouTube Audio Library music), `African Lion funny video`, `My Chameleon is funny`, nuanced PD/CC0-fallback Grizzly GoPro. Exact rights metadata for `20100424 Peuple Loup`, `Dog takes the high ground`, `Heroic Cat Saves Chicken`, `Hobsonia florida` is in `sessions/arena-390292fc-current.md` and `PROBLEMS_FIXES.md`.
- No rights-cleared funny social-platform clip has been selected.

## Level 5 — other Arena chats visible in screenshots

- `arena/6101616c-monarch-overall-work`: portrait research, generated cinematic portrait, local running-shot/close-up work, face-recognition model-weight/license search, “Maine running shot ke chehre par ek local test kiya; likeness behtar hui, lekin motion aur ground-contact ke masail abhi baaqi hain. Ab zyada reference-matched close-up par turn animation test kar raha hoon.” Screenshot shows tool-call limit and “Continue”. Evidence: `screenshot_only`.
- `arena/d9c9e65-portfolio`: Vercel/Vercel API deployment checklist, live URL `https://adil-chandio.github.io/portfolio/`, test “MONARCH ke sath kaise kaam karoon?”, “Complete checklist (sab DONE)”, `monarch-concierge-api.vercel.app/api/chat` returning `{"error":"method_not_allowed"}` for GET (POST allowed), Build & Development Settings unchanged, Node.js 26.x, root `concierge-api`, ignored build step Automatic, “Skip deployments when there are no changes to the root directory” Enabled. Evidence: `screenshot_only`; Vercel project metadata also in `external/APP_SNAPSHOT.json`.
- `arena/ba8d901e-monarch-overall-work`: extinct-life wall Short discussion. Exact visible prompts: “Ok ab poori videos”, “Short video hamari”, “Woh poori video banao ab new level ke sath Jo hamne dekha seekha usko next level lejake”; commands “Start New extinct-life Short – native still review” and “native still review”; assistant says V14 full film and selected thumbnail unchanged, research applied, unfinished forensic study not called complete. Evidence: `screenshot_only`.
- `arena/1f352b8e-monarch-overall-work`: animated POV storyboard / one-minute test video. User complaint “Lekin nhi na Tune images me character ghusane ki Koshish ki … poori frame by frame”; assistant says illustrated backgrounds must be removed and scenes/character/props/lighting/movement rendered by code, “simple vector-style test hai, polished 3D animation nahi. Video 60 seconds ki hai”; “Was this task successful? Yes / No / Keep working”. Evidence: `screenshot_only`.
- Sidebar in those screenshots shows many older chats (repo explanation, portfolio, character, WhatsApp assistant, Monarch-World Channel, Stickman Production, clone requests, etc.). Titles are truncated; exact full list is a gap, recorded in `sessions/screenshot-sidebar-20261108.md`.

## Level 6 — other workspaces and workflow libraries

- Drive WF‑02 / Zack d 3D animation: `00_READ_FIRST_NEW_CHAT_WF02.txt`, trigger `WF2 <topic or reference>`, `python3 tools/continuity.py resume`, `AGENTS.md`, `STYLE_DNA.json`, `QUALITY_CONTRACT.json`, `knowledge/PLAYBOOK.md`, V8 baseline, preserve older masters, canonical `adil-chandio/Monarch-Studio`, branch `arena/eba29c7c-monarch-studio`.
- Drive WF‑05 / MOTIONGO: `WF05_FRESH_CHAT_START_HERE.md`, run `python3 tools/continuity.py resume`, read `styles/premium-motion-editing/AGENTS.md`, `FRESH_CHAT.md`, `data/approved-profile.json`, `knowledge/INDEX.md`; preserve V5 clean editorial plus accepted V6 motion/depth/transition/sound; **do not use V6 bottom caption pills or active-word lower strip**; resume existing work before generating; final response leads with artifact and verified link.
- Google Docs WF‑07 start-here: VIPER-1, free/paid routes, 480×832 free base, 960×1664 upscale, H3 paid native 2K/dialogue, estimate-before-paid/verify-before-delivery. H3 prompting grammar: T2VA/I2VA/FL2VA/Ref2VA fields, language limitation for Urdu/Hindi, Monarch locks, shot-list rules.
- Notion WF‑02 legacy page: local root lived in old chat sandbox (`/home/user/START-HERE.md`, `/home/user/crayon/pp-v4.html`, `/home/user/tools/render_v4*.js`, `/home/user/audio_vo/`); “Nothing was uploaded to Drive; deliverables were shared via Gofile/Litterbox links (may have expired)”; resume key `TABAHI ACTIVATE`; Linear `MON-32`; Google Doc HUB `1MVReMbe56MeehNO8Il70qMhuAHNxI01PPE0Vupj0FTc`.
- Linear: 13 projects including `WF-02 · Monarch Stickman Animation — LEGACY` (`a813926c-b2ef-4956-91dd-09e91f08b7d9`, “Complete end-to-end session record — every prompt, response, result, error and fix”), archived `Monarch Stickman Animation` (`be68fa7d-39ea-4d5b-b9c0-f17615d3d04e`, “Complete session archive… Every prompt, response, result, error, file”), `WF-05 · Premium Motion Editing`, `WF-04 Monarch Face`, `Editing Monarch Studio · Continuity & Style Library`, `MONARCH STUDIO · Workflow Registry`, `Monarch YT Automation — Arena Team OS`, `MONARCH® B2B Agency & Client Portal OS`. Issues MON-1…MON-72 and project updates preserve delivered films, WF‑04 v2, NEELAMI WF‑01/WF‑03, WF‑05 foundation and B2B OS.
- Supabase `monarch-workspace` (`oeqeqlgatdlqbuywktnu`, ACTIVE_HEALTHY): 22 public tables, 232 columns; `public.saved_conversations` 0 rows; `knowledge_notes` 0; `workspace_state` 1 row revision 1. Schema includes `channels`, `content_items`, `tasks`, `projects`, `vault_*`, `workspace_state`. No imported conversations.
- Vercel: `monarch-concierge-api`, `whatsapp-ai-saathi`; production `dpl_HJgeUMGy8JYTUkny7fkyEUZ5u3wi` from portfolio PR #14 “wire live brain”. Env keys exist but values are empty/redacted; no secrets copied. No chat transcripts.
- Gmail: 3 B2B outreach drafts plus 1 blank draft; no chat transcript/attachment. Dropbox: `/MONARCH_B2B_DELIVERY` tree and one 783-byte MD; content read blocked by `email_not_verified`; no chat transcript.
- B2B OS: Linear MON-69 shipped Supabase migration `202611020001_monarch_agency_os`, Edge Function `public-intake`, Vercel `https://monarch-workspace-beryl.vercel.app/`, Drive/Dropbox delivery folders; MON-70/71/72 are phone steps. Notion B2B SOP page `40c807e1-e916-8168-9afd-d661acd13046`.

## Level 7 — this continuity archive

- Active branch HEAD at capture `393edd658e8336780e1cd4aea4cf5b5261c2d1e3`; `git rev-list --all --count` was 991 before the latest fetch, then 998 reachable commits indexed in `evidence/github/commits.jsonl`.
- GitHub evidence at capture: 11 remote heads, 16 tags, 4 PRs, 452 workflow runs, 18 local workflows, 22 repos, 120 imported satellite continuity-like files. Exact heads/tags/runs/commits are in `evidence/github/`.
- Drive evidence: 11 `MONARCH_STICKMAN_ANIMATION_SESSION_LOG.md` snapshots, 13 `RESUME_STATE.md` snapshots, WF‑02/WF‑05 codexes, failures/fixes JSON, start-here docs, recovery hubs, receipts, and one `EMS-20261011-001-history-archive.tar.gz` containing a partial `CHAT_TRANSCRIPT.jsonl` and hash-chained `JOURNAL.jsonl`. Indexed in `external/DRIVE_INDEX.md`; imported text under `evidence/external/drive_text/`.
- 29 attached PNGs copied into `evidence/screenshots/` with hashes and descriptions.
- Machine ledgers: `STATE.json`, `COVERAGE.json`, `SESSION_INDEX.json`, `EVENTS.jsonl`, `DECISION_LOG.jsonl`, `PROMPT_RESULT_LOG.jsonl`, `EVIDENCE_MANIFEST.json`.
- Tooling: `tools/continuity.py` (`resume`, `validate`, `refresh`, `render`, `import-chat`, `checkpoint`, `bootstrap`) and `.github/workflows/continuity-validate.yml`.
- Root `AGENTS.md` and README continuity section make the archive discoverable to new agents.
- **Honest limit:** no complete Arena chat export/JSON is available in the workspace or connected apps. One partial older transcript is imported; everything else is `repo_evidence`, `connected_app_record`, `screenshot_only`, `session_memory`, or an explicit `gap`. Exact all-chat preservation becomes true only after real exports are imported.
