# Problems, causes, fixes and dead ends — do not retry blindly

This is the regression memory. Failed approaches stay visible so a new chat does not waste tokens, time and energy repeating them.

## Creative acceptance and V4/V5

- **Problem:** V4 and V5 were technically validated but the user rejected them.
- **User signals:** V4 “sirf text likh diya”; V5 “NAHI abhi bhi theek se nhi” plus four screenshots.
- **Fix / standing rule:** technical QC, 40/40 checks, 9/9 audio gates and 47/47 flags are **not** creative acceptance. Do not re-present V4/V5 as final. Do not claim human full-motion/native-audio listening, approval, sign-off, perfection, retention, virality or audience results.
- **Dead end:** treating a presented MP4 or commit-pinned link as approval.

## V5 geometry

- **Problem:** `review/cover_hook.jpg` shows V5 hook lines/question occluded by the `1.–7. LIST`.
- **Cause:** `render_ranking_visual_raw_v5.py` uses centered 104pt hook lines `y=300+150i`, question 72pt `y=800`, list `(650,460)-(1040,1186)`, rank burst `(60,1430)`, reaction `(60,1080,540,150)`.
- **Fix / standing rule:** any V6 needs a centered colorful top hook and a fully visible left `1.–7.` black label plate list; no V5 right panel/bottom rank burst. Add safe-area/social-origin checks; `technical_qc_raw_v5.py` has none.
- **Dead end:** reusing V5 geometry unchanged.

## V5 sources and rights

- **Problem:** `verify_sources.py` is strict CC0-only; `technical_qc_raw_v5.py` checks `seven_cc0_originals`/`api_license_verified`; `ranking_short_spec.json` has `seven_cc0_sources=true`. Broad Commons searches mix CC BY/BY-SA/PD/FAL/silent material.
- **Cause:** earlier CC0-only assumption is superseded by the request for rights-verified funny social-platform clips.
- **Fix / standing rule:** rights must be verified per title; revise spec/gates before any V6. Do not use unverified platform reposts/@onlymeamro footage, old Soviet cartoons, FAL Peuple Loup clips requiring attribution, silent/graphic Reddit K9/dog-wolf/pitbull clips, unverified TikTok heroic-cat, Oriental Cat Shorts, `Animals Workout Mix II`, `Adorable Animals...`, `Hutong Meow`, `Most Funny and Cute Baby Elephant...` (YouTube Audio Library music), `African Lion funny video`, `My Chameleon is funny`, or nuanced PD/CC0-fallback Grizzly GoPro as a cleared funny platform-clip substitute.
- **Dead end:** `Category:CC0 videos` empty; `incategory:"CC0 videos" animal` 0. `Lucanus Cervus fighting.webm` has no audio/bogus 63h duration. Grouped Commons API chunk 0 had `hasMore=true`; do not treat it as complete metadata.
- **Exact rights metadata preserved:** `20100424 Peuple Loup - Dis, on joue à chat.webm` pageid `201598741`, 10,517,276 bytes, 512x384, 72.739s, VP9/Opus 48k stereo, sha1 `b7aef4c9fd7e7a448dd7829a392bd99332d89d29`, FAL/`AttributionRequired=true`, Artist `Peuple Loup`, Dailymotion `xd27vi`; `Dog takes the high ground...` PD/silent/Reddit; `African Lion funny video.webm` CC BY-SA 2.0; `My Chameleon is funny.webm` CC BY-SA 4.0; `20140217 Peuple Loup...` FAL Dailymotion `x1ce98c`; `20150705 Peuple Loup...` FAL/Opus; `US Rangers K9 bites...` PD/silent/Reddit; `Heroic Cat Saves Chicken...` pageid `170443826`, 9,240,282 bytes, 2546x1440, 14.528s, PD/attr false, TikTok `wangotangoyaknow`, Newsflare/YouTube credit, Artist `CCTV`, sha1 `a22289513c22a1b89ed7be55075448ab4c43199d`; `Hobsonia florida.webm` pageid `163581211`, 3,203,262 bytes, 1280x720, 13.576s, VP9/Opus, CC BY-SA 4.0, sha1 `968f32a831270e8963fd3393cbabb2beb0e1cf75`. No clip downloaded/probed/cut/selected.

## V4 audio and runner dead ends

- V3 dance renderer/audio/music/SFX/narration/native ambience are not raw moment audio; no generated sound/audio substitution.
- Old silent starfish/octopus/titmouse manifest/spec and `audio_codec:null` must not return.
- `42396617606` LRA/DC `106.33`/`0.05621`; `42397191709` LRA `106.39`; first candidate probe raw-original-first/no-retry caused six HTTP 429s. Transcode-first URLs/retry/backoff/cache/diagnostics/skip worked, but transcodes remain probe-only.
- `Helostoma temminkii kissing.ogv` effectively silent.
- `42399953907` only `-15.25 LUFS`; two-pass/dynamic/linear/TP/limiter variants failed; measured delivered-AAC calibration with `alimiter=0.75` selected.
- `42401006868` bool JSON error; `42401490506` click gate false and `ffmpeg adeclick` hung >5m; bounded interpolation selected.
- `42402744112` upstream `oriental_dove` HTTP 429/robot policy; `7299557` cache/backoff/original CC0 URLs resolved.
- `42403697302` failed because V4 MP4 was ignored; `1abc62d` unignore resolved.

## V3/V2/build dead ends

- Historical peak/loudness/clicks, font, `api.load("onnx")`, 20s/timeout/manual-cancel 403 resolved/rejected.
- Do not reuse failed runner MP4s, weaken gates, reintroduce `load()`, old cue schema, handle/food-reward claims, `source_recon.py`/`short_next`, or claim human approval/virality.
- Base local lacks FFmpeg/ffprobe/media deps/Ruby; global `pip install pyyaml` fails externally-managed; `/tmp/simvenv` missing; `/tmp/yamlvenv5` worked; `static-ffmpeg` there failed SSL, use imageio-ffmpeg/runner apt FFmpeg.
- PyYAML converts `on` → `True`; `read_file` offset `0` invalid; `grep --exclude` after `--` errors; `gh workflow list --json` unsupported; `gh run view --log-failed`/job-log/artifact downloads often EOF; `gh workflow run`/API dispatch/manual cancels 403; trigger by normal push.
- Node20→24/cache-save annotations nonfatal. Plain fetch may set only `FETCH_HEAD`; explicit refspec required. `present_file` failed original/premium MP4s but succeeded CLEAN/V2/V3/V4/V5.
- V3 nested-quote SyntaxError, source-check AssertionError, duplicate `edition`/`native_audio`, `AssertionError: handle`, missing `cartoon_boing`/`comedy_tick`, `vo1 needs excessive tempo 1.159`, local Edge TTS failure, cue `KeyError`, failed runs `42376100464`, `42377948163`, `42382694165` resolved. Do not retry unpatched 15-min recon, deprecated `actions/cache@v4 save-always`, multiplicative sound fix, stale V3/V4 push overlap, FWS/Flickr/Facebook/Freesound/Openverse/Pixabay/guessed URLs, `thumb.wikimedia.org` SSL.

## Chat-archive and workspace dead ends

- Local checkout initially stale/grafted at `ac3a529` with modified `.gitignore` and untracked old V3/dance-clean drafts. Remote tracked equivalents were restored by fast-forward; `/tmp/arena_local_untracked_backup_1794150197` is a nonpersistent backup only, not source of truth.
- `git merge --ff-only` timed out at 120s while printing a huge file list, but later checks proved success. Do not repeat the same verbose fetch/merge.
- Other chats remain active: remote-tracking/`git ls-remote` heads for other branches change. Use exact GitHub API/`git ls-remote` values captured in `evidence/github/branch_heads.json` and cite the capture timestamp.
- `gh api 'repos/.../pulls?state=all&per_page=100' --jq ...` wrote NDJSON to `/tmp/monarch_prs.json`; `json.load` failed `JSONDecodeError: Extra data`. Fix: use `--jq '[.[] | {...}]'` to produce one array, or parse JSONL. This archive uses the array form.
- `multi_tool_use.parallel` attempts to call `google_drive__search_files`, `dropbox__search_files`, `notion__search` can return “Model tried to call unavailable tool” if the connector was not loaded in that reply. Call `list_connector_tools` first, then call connectors directly.
- `google_drive__download_file` writes files into `google_drive/`. Duplicate filenames (e.g. 11 `MONARCH_STICKMAN_ANIMATION_SESSION_LOG.md`, 13 `RESUME_STATE.md`) overwrite unless each download is immediately renamed. Canonical copies are under `evidence/external/drive/session_logs/`; `google_drive/` is ignored scratch.
- Three stale Drive IDs from session memory returned 404 (`1PhCjQp...`, `1Dcf7dVj...`, `1tQws_3...`). Correct IDs were found by exact-name search: `1xqBx2wiyOTmoZe_OvVXePmlgZ8vu2MOj`, `1L9uUfrhAPiw9f5JMKB3kx4fTifvwlTWF`, `1IP1ykbtg6Hvk3SqiZGkF_uRsj8v9vRje`. A legacy Notion Google Doc HUB ID `1MVReMbe56MeehNO8Il70qMhuAHNxI01PPE0Vupj0FTc` also 404s; do not claim that doc was imported.
- `dropbox__get_file_content` for `/MONARCH_B2B_DELIVERY/.../MON-DEMO26_Final_Delivery_Pack.md` returned `email_not_verified`; leave that as an explicit gap. Do not change the path or retry the identical blocked call.
- Local Python had `PIL`, `yaml`, `pytesseract` missing; `tesseract` command absent; `file` command missing in an earlier screenshot-copy pass. Do not rely on OCR being installed. `cp`, `ls`, `read_file`, `hashlib` and `json` worked.
- `curl` to `www.googleapis.com` from bash fails SSL/network; use connector tools, not direct HTTP from the sandbox.
- `google_drive__download_file` does not accept a custom `file_path`; extra properties are rejected. Rename after download instead.
- `google_drive__export_file` with `text/plain` writes native Docs text into `google_drive/`; canonical copies are copied into `evidence/external/drive_text/`.

## Evidence-honesty dead ends

- No full chat transcript/JSON is in the workspace. Screenshots/session memory/Drive session logs/Linear project descriptions/Notion pages are not proof of complete Arena chat preservation.
- Drive WF‑02/WF‑05 startup docs explicitly say chat memory does not magically transfer and missing messages must not be claimed. Notion legacy WF‑02 says old chat sandbox files were not uploaded to Drive and Gofile/Litterbox links may have expired.
- Supabase `public.saved_conversations` has 0 rows; Dropbox/Gmail/Vercel/Google Docs searches found no chat export.
- `EMS-20261011-001-history-archive.tar.gz` contains a real `CHAT_TRANSCRIPT.jsonl`, but it has only 3 user messages and no assistant messages; `JOURNAL.jsonl` is a hash-chained event log, not a transcript. Mark both `partial`.
- Do not fabricate “everything” or claim exact all-chat archive until real exports are imported. `COVERAGE.json`, `GAPS.md` and `STATE.json.claims` exist to enforce this.
