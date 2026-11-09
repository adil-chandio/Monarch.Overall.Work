# Monarch Cam production workflow — already decided, do not ask the user

This is the exact workflow a new chat inherits. The user must not have to say “yeh aise karna hai”. Read `00_START_HERE.md`, `CHANNEL_STATE.json` and `NEXT_ACTION.md` first, then execute.

## 0. Recover if the workspace is stale

If `AGENTS.md`, `tools/continuity.py` or `docs/continuity/` are missing, use root `RECOVER.md`. After files exist:

```bash
python3 tools/continuity.py recover
python3 tools/continuity.py resume
```

Never switch, rename, or push another branch. Work only on `arena/2b012328-monarch-overall-work`.

## 1. Resume with channel context

```bash
python3 tools/continuity.py resume
# or channel-only:
python3 tools/continuity.py channel
```

`resume` validates the archive and prints the commit-pinned bootstrap with `EASY_RESUME.md` embedded. Do not ask the user to re-explain old work.

## 2. Inherit the single active lane

Read:

1. `docs/continuity/channels/monarch-cam/00_START_HERE.md`
2. `docs/continuity/channels/monarch-cam/CHANNEL_STATE.json`
3. `docs/continuity/channels/monarch-cam/NEXT_ACTION.md`
4. `docs/continuity/channels/monarch-cam/PLAYBOOK.md`
5. `docs/continuity/channels/monarch-cam/REJECTIONS.md`
6. `docs/continuity/channels/monarch-cam/EVIDENCE.md`

The active lane is either the broader channel rebuild (`PLAYBOOK.md`) or the unresolved ranking-Short V6 intent. Do not silently switch to an older task. V4/V5 are rejected; V5 stays untouched.

## 3. Before any new edit: rights gate

- No unverified platform reposts, no arbitrary copyrighted clips, no “credit only” clearance.
- Verify each title's rights basis, commercial-use permission, edit permission, exact declaration/licence, verification date and required credit.
- Keep a clip ledger before the edit.
- For the first bear episode, use the NPS public-domain source pack from `docs/MONARCH_CAM_PERMISSION_FREE_BEAR_FOOTAGE_PLAN_2026-11.md`.
- CPW is research only (CC BY-NC-ND 4.0, no commercial use / modification).
- No generated wildlife event presented as real evidence. Disclose realistic altered/generated material where applicable.

## 4. Build in a separate package

For the ranking-Short lane, **never modify V5**. Create a new V6 package with:

- new source ledger with per-title rights verification;
- extracted scenes and native per-window audio;
- visible centered colorful top hook;
- fully visible left `1.–7.` black label plates with progressive labels;
- payoff cuts/zoom, reaction bubbles, emojis;
- safe-area / social-origin checks;
- renderer, audio policy, QC contract, workflow, MP4 and run;
- no silent segments, no generated sound substitution, no strict CC0-only assumption without revised gates.

For the channel-rebuild lane, follow `PLAYBOOK.md`: two series, viral-quality chain, November calendar, two Shorts per long, old-winner bridge, About/home cleanup, Studio review. Do not mass-delete old videos.

## 5. Validate, render, commit, push

```bash
python3 tools/continuity.py validate
python3 tools/continuity.py render --check
python3 -m py_compile tools/continuity.py
git diff --check
git add AGENTS.md README.md RECOVER.md MONARCH_CAM.md .gitattributes .gitignore \
  config/continuity.json config/channels.json tools/continuity.py \
  .github/workflows/continuity-validate.yml \
  .github/workflows/monarch-cam-short-ranking-raw-v6.yml docs/continuity \
  docs/MONARCH_CAM_*.md production/monarch-cam/short_ranking_raw_v5 \
  production/monarch-cam/short_ranking_raw_v6 \
  deliverables/MONARCH_CAM_7_Unexpected_Animal_Moments_Ranked_60s_Short_RAW_FULLSCREEN_V6.mp4
git commit -m "chore(monarch-cam): advance active channel lane"
git push origin arena/2b012328-monarch-overall-work
```

CI runs `py_compile`, `validate`, `render --check` and the channel capsule command.

## 6. Checkpoint before ending

```bash
python3 tools/continuity.py checkpoint \
  --title "Exact short title" \
  --details "What changed, result, problems/fixes, exact IDs" \
  --kind result --space yt-automation --evidence-level repo_evidence \
  --ref path/to/evidence \
  --status "..." --next-action "..."
```

Then update `docs/continuity/channels/monarch-cam/CHANNEL_STATE.json` and `docs/continuity/STATE.json` if the active lane/status/next action changed, run `refresh`, `render`, `validate`, `render --check`, commit and push.

## 7. Non-negotiable

- Do not ask answered questions or request the old explanation again.
- Do not re-present V4/V5/V6 as final.
- Do not reuse V5 occluding geometry or dead-end sources.
- Do not claim human approval, native-audio listening, sign-off, perfection, retention, virality, revenue or audience results.
- Do not claim all Arena chats are preserved while `COVERAGE.json` says `full_arena_export_available=false`.
- Do not leave unimported files in `chat_exports/inbox/`.
- Do not restart from the beginning.

## V6 rejection / V7 active task — 2026-11-09

- V6 was rejected after its GitHub upload/download-link answer: `Yeh Kya chutiyapa banaya ha NAHI abhi bhi theek se nhi ...` plus six reference screenshots. Technical QC, 49/49 checks, 9/9 audio gates, CI success and V6 links are **not** creative acceptance.
- The user wants `📈 trending viral videos` / social-platform clips, `viral ke sath sath purani bhi chalenge`, `bas clips mazedar next level honi chaiye`, the best hooked/engaging scenes extracted, and a full 60s ranking built on them. The reference screenshots show `ranking list kese lagi ha sab kuch visible horha ha main hamra kuch kat nhi rha`: full-screen uncut clip, visible hook, all 1.-7. list items, right UI, caption bubble, Subscribe and bottom chrome.
- V7 is a separate package at `production/monarch-cam/short_ranking_raw_v7/` with workflow `.github/workflows/monarch-cam-short-ranking-viral-v7.yml` and deliverable `deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_VIRALSTYLE_V7.mp4`.
- Rights boundary: ten rights-cleared social-origin Commons mirrors; per-title Commons API extmetadata, original SHA-1, Credit/Categories social origin and CC BY attribution; no unverified currently trending TikTok/Instagram/Reddit/Dailymotion/YouTube reposts, no current-trending claim, no legal opinion.
- Visual boundary: blurred full-frame background plus sharp uncut source frame; no V6 crop routine, no zoom, no black empty top, no letterbox; all seven labels visible from the first frame.
- No V7 MP4, QC, download link, human full-motion/native-audio listening, creative approval, sign-off, perfection, retention, virality or audience result is claimed yet. V4/V5/V6 stay rejected; V5 untouched.

## Clean V8 — built, not approved — 2026-11-09

- **Status:** `v8_clean_build_committed_human_review_pending`.
- **CI:** `42653605976` / job `129286160076` succeeded; commit-back `9b18446`.
- **Deliverable:** `deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_CLEAN_V8.mp4` (`22,459,082` bytes, SHA-256 `1c44fb345f3f8582ee22b6c333c39050968669b8f6fc0012d9a5b56b3d03e1e7`).
- **Direct link:** `https://github.com/adil-chandio/Monarch.Overall.Work/raw/arena/2b012328-monarch-overall-work/deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_CLEAN_V8.mp4`
- **Visual:** V7 overlay clutter removed; only a slim `7→1` rank strip, small moment badge and thin progress line remain outside the central unobstructed content region. Sharp uncut source on ambient-lifted blurred full-frame background. Two cuts were moved off a black fade-in and a static title card after committed contact-sheet review.
- **Objective records:** `68/68` technical checks, `9/9` unchanged web audio gates, seven continuous raw native-audio windows, zero quiet half-second blocks, per-title Commons API rights/social-origin/SHA-1 ledgers.
- **Limits:** exact reference frames/full motion/audio were not obtainable; the user refused further frame requests; no exact-reference-match claim. Exact rights-cleared currently trending named-platform clips remain unmet; older verified Commons social-origin mirrors used. No full legal compliance, human full-motion/native-audio listening, creative approval, sign-off, perfection, retention, virality, 3x, likes/subscribes, same-path replacement or audience result is claimed.
- **Rule:** V4/V5/V6/V7 are rejected. V8 CI success, QC and link are objective records, not creative acceptance.
