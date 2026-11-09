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

## Staged whitespace / raw-evidence fix

- **Problem:** `git diff --cached --check` failed on the first commit attempt because raw Google Docs / satellite-repo evidence contains original CRLF and trailing spaces, and generated `*.md` ledgers had an extra blank line at EOF.
- **Cause:** `render_outputs()` ended several generated lists with an empty string, and `git` treats preserved CRLF/trailing spaces in imported text as whitespace errors.
- **Fix:** `render()` now normalizes generated Markdown to a single trailing newline. Root `.gitattributes` sets `docs/continuity/** -text -whitespace` so raw bytes are preserved byte-for-byte without EOL conversion or staged whitespace warnings. `refresh()` builds the manifest twice so `COVERAGE.json` hash covers its final bytes. `checkpoint()` now calls `refresh()` before `render()`.
- **Standing rule:** do not “clean” raw Drive/Docs/satellite evidence to silence whitespace warnings; the hashes in `EVIDENCE_MANIFEST.json` are authoritative. Staged whitespace check passed after these fixes.

## Evidence-honesty dead ends

- No full chat transcript/JSON is in the workspace. Screenshots/session memory/Drive session logs/Linear project descriptions/Notion pages are not proof of complete Arena chat preservation.
- Drive WF‑02/WF‑05 startup docs explicitly say chat memory does not magically transfer and missing messages must not be claimed. Notion legacy WF‑02 says old chat sandbox files were not uploaded to Drive and Gofile/Litterbox links may have expired.
- Supabase `public.saved_conversations` has 0 rows; Dropbox/Gmail/Vercel/Google Docs searches found no chat export.
- `EMS-20261011-001-history-archive.tar.gz` contains a real `CHAT_TRANSCRIPT.jsonl`, but it has only 3 user messages and no assistant messages; `JOURNAL.jsonl` is a hash-chained event log, not a transcript. Mark both `partial`.
- Do not fabricate “everything” or claim exact all-chat archive until real exports are imported. `COVERAGE.json`, `GAPS.md` and `STATE.json.claims` exist to enforce this.

## Stale checkout / missing continuity files

- **Problem:** the workspace was restored to old commit `ac3a5295903b1a625acd4923882d68064204128a` with a modified `.gitignore` and untracked V3/dance-clean drafts, while `AGENTS.md`, `tools/continuity.py` and `docs/continuity/` were missing. This is the exact "restarts from the beginning" failure the user complained about.
- **Cause:** local snapshot stale relative to remote branch `arena/390292fc-monarch-overall-work`; remote head was `4b3574c1c936e47cf2a68d719bae0e9fe6a2380a`.
- **Fix:** backed up 7 untracked paths plus `.gitignore` diff to `/tmp/arena_stale_backup_1794159448`, restored `.gitignore`, ran `git clean -fd -e deliverables`, used explicit-refspec `git fetch`, then `git merge --ff-only` to `4b3574c1`. `python3 tools/continuity.py validate` passed.
- **Permanent mitigation:** root `RECOVER.md`, `python3 tools/continuity.py recover`, root `MONARCH_CAM.md`, and active-channel capsule embedded in `resume`/`bootstrap`. CI also runs `python3 tools/continuity.py channel`.
- **Standing rule:** never restart work from a stale checkout; recover the branch head first. Do not delete `deliverables/` or `.git`.

## V6 audio-gate invocation — 2026-11-08

- Failed run: `42516794773`, job `128841464088`, step `Nine web audio gates`, exit code `2`.
- Cause: the V6 workflow invoked `python -m showreel.audio_qc.gates` with no positional audio path. `showreel/audio_qc/gates.py main()` returns `2` when no args are supplied. The step also relied on env vars that the module does not read.
- Fix: install `scipy` in the V6 Python-tools step and invoke the gates with the delivered V6 MP4 path, `--profile web`, `--json .../audio_qc.json`, and `tee .../audio_qc.log`, matching the V5 workflow. Add `audio_qc.log` to the V6 artifact list.
- V5/V4/V3 packages remain untouched. Re-run `42517651544` succeeded after the fix; V6 MP4, 49/49 technical checks, 9/9 audio gates, safe-area and social-origin checks were committed by workflow commit `5559b52`. No human creative acceptance is claimed.

## V6 rejection / V7 active task — 2026-11-09

- V6 was rejected after its GitHub upload/download-link answer: `Yeh Kya chutiyapa banaya ha NAHI abhi bhi theek se nhi ...` plus six reference screenshots. Technical QC, 49/49 checks, 9/9 audio gates, CI success and V6 links are **not** creative acceptance.
- The user wants `📈 trending viral videos` / social-platform clips, `viral ke sath sath purani bhi chalenge`, `bas clips mazedar next level honi chaiye`, the best hooked/engaging scenes extracted, and a full 60s ranking built on them. The reference screenshots show `ranking list kese lagi ha sab kuch visible horha ha main hamra kuch kat nhi rha`: full-screen uncut clip, visible hook, all 1.-7. list items, right UI, caption bubble, Subscribe and bottom chrome.
- V7 is a separate package at `production/monarch-cam/short_ranking_raw_v7/` with workflow `.github/workflows/monarch-cam-short-ranking-viral-v7.yml` and deliverable `deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_VIRALSTYLE_V7.mp4`.
- Rights boundary: ten rights-cleared social-origin Commons mirrors; per-title Commons API extmetadata, original SHA-1, Credit/Categories social origin and CC BY attribution; no unverified currently trending TikTok/Instagram/Reddit/Dailymotion/YouTube reposts, no current-trending claim, no legal opinion.
- Visual boundary: blurred full-frame background plus sharp uncut source frame; no V6 crop routine, no zoom, no black empty top, no letterbox; all seven labels visible from the first frame.
- No V7 MP4, QC, download link, human full-motion/native-audio listening, creative approval, sign-off, perfection, retention, virality or audience result is claimed yet. V4/V5/V6 stay rejected; V5 untouched.


## V6 creative mismatch — 2026-11-09

- **Problem:** V6 passed technical/audio gates and was uploaded to GitHub with a download link, but the user rejected it with six reference screenshots and `Yeh Kya chutiyapa banaya ha NAHI abhi bhi theek se nhi ...`. Screenshots showed full-screen human viral clips and a visible ranking UI; V6 showed a large black empty upper half, a boxed tiny list and CC0 animal-only clips.
- **Cause:** strict CC0-only gates and geometric/technical QC measured file integrity, not the requested viral social-origin clips, hooked scene selection or reference-style full-frame composition. V6 `cover_crop()` cropped the main clip and created black/empty areas.
- **Fix:** separate V7 package with rights-cleared social-origin Commons mirrors, per-title API licence/Credit/Categories/original-SHA-1 verification, CC BY attribution, runner audio/motion best-window selection, blurred full-frame background plus sharp uncut source frame, no crop/zoom, all seven labels visible, sampled-frame QC for black empty areas, and a narrow V7 workflow with `[skip ci]` commit-back.
- **Standing rule:** technical QC, audio gates, CI success and GitHub links are not creative approval. Do not claim human listening, sign-off, current trending status, full legal compliance or audience results.

## V7 render throughput — 2026-11-09

- **Problem:** the first V7 render step ran full-canvas Gaussian-blurred text shadows on every one of 1800 frames; a local benchmark measured about `5.6 s/frame`, projecting more than the 120-minute CI timeout.
- **Cause:** `compose_frame()` rebuilt the static reference-style UI and full-frame blur for each frame.
- **Fix:** cache the static gradient/UI/reaction overlay once per scene and payoff state, use a cheap dark offset shadow for cached text, downsample the full-frame blur, and composite only the cached overlay plus a short transition flash per frame. Local benchmark dropped to about `0.13 s/frame` (~4 minutes for 1800 frames). The visible hook, all seven rank labels, right UI, handle, comment bubble, Subscribe and bottom chrome remain present; no crop, zoom or black empty top was introduced.
- **CI:** workflow concurrency now uses `cancel-in-progress: true` so the optimized retry supersedes the slow in-progress render instead of running both.

## V7 native-audio LRA gate failure — 2026-11-09

- **Failed run:** `42547437901`, job `128935444230`, step `Build raw per-window native audio track and mux MP4`. Steps 1-12 succeeded; the cached-UI visual render finished in 2m22s. Steps 14-19 were skipped and no artifact or committed MP4 was produced.
- **Cause:** all 16 measured per-window gain / mastering-chain attempts failed only `lra_in_range` against the unchanged nine web gates. Measured LRA was about `87-89 LU` and movement about `225-229 dB`. A short runner-only audio-window diagnostic showed long `-120 dBFS` digital-silence blocks inside the selected `caption_fail` and `nose_wheelie` windows, even though their aggregate 8.6-second RMS passed the old `-65 dBFS` segment gate.
- **Fix:** strengthen the source contract instead of weakening or faking the gates. The candidate probe now scores only 8.6-second windows in which **all seventeen complete 0.5-second blocks** exceed the unchanged `-65 dBFS` native-audible threshold. Window selection, the selected-window audit, the native-audio builder ledger and technical QC record and enforce continuous native audio. No VO, music, SFX, bed, generated calls, audio substitution or added layer is introduced, and the web profile remains `LRA 1-10 LU` with the other eight gates unchanged.
- **Diagnostics:** a temporary `V7 audio-window diagnostic` workflow uploads compact per-candidate continuous-window measurements and a runner-only selected-window audit. It is not a deliverable and is not creative acceptance.
- **Status:** fix implemented locally; short diagnostic and full V7 CI verification are pending. No successful V7 CI, committed MP4, QC evidence, artifact, hash, download link, human full-motion/native-audio listening, creative approval or sign-off exists yet.

## V7 continuous-audio diagnostic — 2026-11-09

- **Diagnostic run:** `42559696919`, job `128973180485`, all 12 steps `success`; artifact `13648638723` (`66149` bytes, zip SHA-256 `a6821c30d37e6c1c425f0099931077dfe9e26920db01621afd4bfa8b997aabce`).
- **Result:** eight candidates passed the audio/visual probe. All seven selected windows had `17` complete 0.5-second blocks, `0` quiet blocks and all block RMS values above `-65 dBFS`. The selected `caption_fail` window moved from `source_start 4.0` to `75.5`; `nose_wheelie` moved from `0.0` to `1.0`, avoiding the long `-120 dBFS` silence runs that caused the previous LRA failure.
- **Meaning:** continuous native source audio is now measured and enforced before mastering. This is runner-only objective evidence, not a V7 MP4, human listening, creative approval or sign-off. The unchanged nine web gates still have to pass on the delivered AAC stream in the full V7 CI run.

## V7 full CI reached nine-gate audio pass, then failed QC ledger contract — 2026-11-09

- **Run:** `42560161988`, job `128974608119`, `failure` in 6m17s. Steps 1-14 succeeded: probe, selection, per-title rights, recon, continuous-audio audit, full-frame render, native-audio mux, and the unchanged nine web audio gates. Step 15 `Technical QC with sampled-frame and rights checks` raised `KeyError: 'blurred_background_fill'` at `technical_qc_v7.py:185`; steps 16-19 were skipped.
- **Objective runner-only result:** MP4 `21916389` bytes, `60.000000s`, `1080x1920`, `30/1`, `h264/aac`; nine web gates `PASS` with `I -14.39 LUFS`, `LRA 9.14 LU`, `peak -2.19 dBFS`, `movement 26.46 dB`, `clicks 0`; eight rights-ledger flags true. This file was not committed, uploaded as a deliverable artifact, or reviewed by a human.
- **Cause:** the renderer's `visual_v7_qc.json` recorded `full_screen_blur_background` but omitted the parallel `blurred_background_fill` key that `layout_manifest.json`, `visual_edit_ledger.json` and `technical_qc_v7.py` already used. It was a ledger-key mismatch, not a visual, audio or rights failure.
- **Fix:** `write_visual_qc()` now writes `blurred_background_fill=True` alongside `full_screen_blur_background=True`. The technical QC logs sampled-frame metrics, and a failure-only artifact can upload the runner MP4/sampled frames/ledgers for inspection. No web gate, threshold, audio policy or rights check was weakened; no audio was added or substituted.
- **Status:** clean full V7 CI verification is pending. No successful main V7 CI, committed MP4, QC evidence, artifact, hash, download link, human full-motion/native-audio listening, creative approval or sign-off exists yet.

## V7 sampled-frame black-background QC failure — 2026-11-09

- **Run:** `42561159698`, job `128977659206`, `failure` in 7m5s. Steps 1-14 succeeded, including the unchanged nine web audio gates (`PASS`, `LRA 9.14 LU`, `movement 26.46 dB`, `clicks 0`). Technical QC then raised `RuntimeError: V7 technical QC failed: {"no_black_empty_top": false, "no_black_bars": false, "no_hook_black_fill": false}`. Steps 16-20 were skipped; no committed MP4 or delivery artifact exists.
- **Evidence:** the completed job log printed sampled-frame metrics. Frames `630`, `810` and `990` had `top_black_fraction 0.445/0.437/0.666`, `bottom_black_fraction` up to `0.477` and `hook_black_fraction` up to `0.493`. Failure artifact `13649543217` was uploaded, but its signed zip was not downloadable in this environment (`EOF`/HTTP 500); the compact metrics in the log were sufficient to diagnose the failure.
- **Cause:** the full-frame blurred fill was derived directly from the source frame. Dark night/CCTV/title windows made the top, hook and bottom background regions near-black even though the sharp source frame remained uncut and the layout overlays were present. This was a real visual-policy failure, not a ledger-key mismatch.
- **Fix:** `compose_frame()` now applies a soft dark ambient-blue luminance floor and `1.12x` brightness to the **blurred background only**, preserving its color/motion. The sharp aspect-preserving uncut source frame, all UI, the nine web gates and all QC thresholds are unchanged. A local fully black source-frame simulation produced `top_black_fraction 0.0186`, `bottom 0.0757`, `hook 0.0459` with `top_mean 46.39`, `top_std 58.19`, `hook_std 83.86`, so the objective sampled-frame checks pass on the worst case.
- **Status:** clean full V7 CI verification is pending. No successful main V7 CI, committed MP4, QC evidence, artifact, hash, download link, human full-motion/native-audio listening, creative approval or sign-off exists yet.

## V7 successful CI delivery — 2026-11-09

- **Run:** `42562287554`, job `128981122857`, `success` in 7m57s; all build steps passed. Artifact `13650013062`; workflow commit `47012a5dcfc7f2fa07107878a3bcf61f5349daf5`.
- **Committed deliverable:** `deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_VIRALSTYLE_V7.mp4`, `21986563` bytes, SHA-256 `4f76a4e102d6c20a655157c955e076bc6a54d34ba86914b334897c8ce249b8f4`, `60.0s`, `1080x1920`, `30fps`, `1800` frames, `h264/aac`.
- **QC:** `technical_qc.json` `65/65` checks pass; `audio_qc.json` `9/9` unchanged web gates pass; `native_audio_ledger.json` records `final_web_gate_pass=true`, `final_technical_click_runs=0`, `all_seven_native_audio_continuous=true`, `quiet_full_block_count=0`. `source_audio_audit.json` records seven continuously audible windows with 17 complete 0.5s blocks each and zero quiet blocks. `social_origin_ledger.json` records eight objective per-title rights flags true.
- **Evidence:** committed sampled frames, payoff frames, covers, seven selected-window contact sheets, ten candidate contact sheets, `qc_summary.json`, `review-manifest.json`, `selected_windows.json`, `verified_sources.json`, `source_video_ledger.json`, `source_audio_audit.json`, `visual_v7_qc.json`, `layout_manifest.json` and audio/technical QC. Committed sampled frames show the blurred full-frame background, sharp uncut source, visible two-line hook, all seven rank labels, right UI, `@Monarch-Cam`, comment bubble, Subscribe and bottom chrome.
- **Cleanup:** temporary `v7-audio-window-diagnostic.yml`, `DIAGNOSTIC_TRIGGER.md` and their continuity scan entry were removed.
- **Boundary:** this is a technical build for human review. No human full-motion/native-audio listening, creative approval, sign-off, perfection, retention, virality, 3x, likes/subscribes, same-path replacement or audience result is claimed. Exact rights-cleared currently trending TikTok/Instagram/YouTube/Reddit/Dailymotion clips remain unmet; V7 uses older rights-cleared Commons social-origin mirrors with attribution/restrictions. Commons metadata is a rights record, not a legal opinion, and no full legal compliance or current-trending claim is made. V4/V5/V6 remain rejected.

## V7 rejected after delivery — 2026-11-09

- **Rejection:** after the V7 GitHub link was given, the user attached a phone screenshot of the delivered MP4 and said the "clean" video is still stuffed with overlays; the main content is not visible. They want all that removed and every element rebuilt to match the referenced 60s YouTube Short `08-ocSDpt7o` exactly.
- **What succeeded technically:** V7 CI `42562287554` passed 65/65 technical QC and 9/9 unchanged web audio gates; MP4, sampled frames, contact sheets and ledgers were committed at `47012a5`. Technical QC, CI success and the GitHub link are **not** creative acceptance.
- **What failed creatively:** the V7 reference-style overlay (two-line hook, seven-row list, right UI, handle, comment bubble, Subscribe, bottom chrome) covered the centered sharp source frame. The user explicitly wants a clean presentation where the main clip is visible. Sampled-frame QC measured black-area/geometry, not overlay obstruction or creative match.
- **Reference metadata retrieved:** `Ranking Most Impressive Moments Ever #shorts` by `onlymeamro`, 60s, ~89.97M views, ~2.88M likes, uploaded 2026-01-05; TikTok original by `thatoneamro` video `7592066346708454686`. oEmbed/watch metadata and thumbnail URLs are accessible, but the video frames are not playable/extractable in this environment.
- **Next:** request 2-3 screenshots or a short clip from the reference, then create a separate V8 clean lane. Do not modify or re-present V4/V5/V6/V7 as accepted. Exact reference clips are not rights-cleared; no current-trending, full-compliance, human-review, perfection, retention, virality or audience-result claim exists.

## Clean V8 — built, not approved — 2026-11-09

- **Status:** `v8_clean_build_committed_human_review_pending`.
- **CI:** `42653605976` / job `129286160076` succeeded; commit-back `9b18446`.
- **Deliverable:** `deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_CLEAN_V8.mp4` (`22,459,082` bytes, SHA-256 `1c44fb345f3f8582ee22b6c333c39050968669b8f6fc0012d9a5b56b3d03e1e7`).
- **Direct link:** `https://github.com/adil-chandio/Monarch.Overall.Work/raw/arena/2b012328-monarch-overall-work/deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_CLEAN_V8.mp4`
- **Visual:** V7 overlay clutter removed; only a slim `7→1` rank strip, small moment badge and thin progress line remain outside the central unobstructed content region. Sharp uncut source on ambient-lifted blurred full-frame background. Two cuts were moved off a black fade-in and a static title card after committed contact-sheet review.
- **Objective records:** `68/68` technical checks, `9/9` unchanged web audio gates, seven continuous raw native-audio windows, zero quiet half-second blocks, per-title Commons API rights/social-origin/SHA-1 ledgers.
- **Limits:** exact reference frames/full motion/audio were not obtainable; the user refused further frame requests; no exact-reference-match claim. Exact rights-cleared currently trending named-platform clips remain unmet; older verified Commons social-origin mirrors used. No full legal compliance, human full-motion/native-audio listening, creative approval, sign-off, perfection, retention, virality, 3x, likes/subscribes, same-path replacement or audience result is claimed.
- **Rule:** V4/V5/V6/V7 are rejected. V8 CI success, QC and link are objective records, not creative acceptance.
