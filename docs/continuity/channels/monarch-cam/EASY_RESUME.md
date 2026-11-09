# Monarch Cam — copy-paste capsule for a new Arena chat

Branch: `{{BRANCH}}` · Exact HEAD: `{{HEAD}}` · Tree: {{TREE_URL}} · Active channel: `{{ACTIVE_CHANNEL}}` · Channel start: `{{CHANNEL_START}}` · Recovery: `{{RECOVERY_COMMAND}}`

You are resuming **Monarch Cam**, one of the three channels, inside `adil-chandio/Monarch.Overall.Work`. The user must not have to explain the channel, workflow, style, decisions, rejections or next action again. Everything is already in the repo.

First run:

```bash
python3 tools/continuity.py resume
```

If continuity files are missing, run `{{RECOVERY_COMMAND}}` (or raw git command in `RECOVER.md`), then `resume`. Do not switch, rename, or push another branch.

Read, in order: `docs/continuity/channels/monarch-cam/00_START_HERE.md`, `CHANNEL_STATE.json`, `NEXT_ACTION.md`, `PLAYBOOK.md`, `WORKFLOW.md`, `REJECTIONS.md`, `EVIDENCE.md`, then root `AGENTS.md`, `docs/continuity/00_START_HERE.md`, `STATE.json`, `MINDSET.md`, `WORK_LEVELS.md`, `PROBLEMS_FIXES.md`, `COVERAGE.json`, `GAPS.md`.

Inherit this exact state:

- Identity: **Real wildlife moments, explained through original behaviour-led storytelling.** Primary series `Too Close: Wildlife in Human Space`; secondary `Nature's Hidden Tricks` only after the primary cluster is coherent. YouTube: https://www.youtube.com/@Monarch-Cam · `@Monarch-Cam`.
- Owner says Monarch Cam is one of the 3 channels. `config/channels.json` still lists 3 legacy slots `Monarch Lab`, `Mindful Momentum`, `Curious Miles`. Until explicitly renamed, treat Monarch Cam as the active channel workstream; preserve legacy config; do not claim reconciliation.
- Live audit: do not delete the channel, do not mass-delete old videos, do not re-upload the 25-view ranking repeatedly, do not start random niche experiments. Old bear winner still active; new-release system stalled/incoherent. Rebuild around two organised wildlife promises.
- November plan: 4 long videos, 8 connected Shorts, one primary cluster, two playlists, 100% clip-rights/factual-source records, old-winner bridge, Studio RPM baseline. Viral-quality chain: high-demand concept → readable real thumbnail → accurate standalone title → proof in first 3 seconds → payoff by 0:25 → fresh evidence/explanation → satisfying final answer → related next video.
- Rights: no direct permission outreach. Use verified PD / suitably licensed CC or stock material plus original Monarch Cam narration/graphics/production. Clip ledger required before edit. CPW is research only (CC BY-NC-ND 4.0). Credit, crop, mirror, disclaimers and fair-use paragraphs are not clearance. AI must not fabricate wildlife events as real evidence.
- V4 ranking Short rejected: “sirf text likh diya”. V5 ranking Short rejected: “NAHI abhi bhi theek se nhi” plus four screenshots. V6 ranking Short rejected after its GitHub upload/link: “Yeh Kya chutiyapa banaya ha NAHI abhi bhi theek se nhi ...” plus six screenshots. Technical QC, 40/40 or 49/49 checks, 9/9 audio gates, CI success and download links are **not** creative acceptance. V5 stays untouched. A separate V7 task is active.
- V5 geometry dead end: hook/question occluded by right `1.–7. LIST`. V6 dead end: black empty upper half, boxed tiny list, oversized hook, crop routine and CC0 animal-only clips. V7 uses a blurred full-frame background plus a sharp uncut source frame, a centered two-line color-split hook, all seven visible rank plates/labels, right UI, comment bubble, Subscribe and bottom chrome; no V6 crop, no zoom, no black bars. Only native per-window source audio; no generated sound or added layers.
- Continuity archive is delivered and validated, but no complete Arena chat export/JSON exists; `full_arena_export_available=false`. Connected apps are snapshots, not live mirrors. Hourly automation is a protocol, not proven cron.
- No human full-motion/native-audio listening, approval, sign-off, perfection, retention, virality, revenue or audience-result claim. Historical YouTube Studio analytics are historical metrics only.

Exact next action: inherit `CHANNEL_STATE.json` and continue the single active Monarch Cam lane without asking the user to explain how to do it. Build the separate V7 60s ranking Short from rights-cleared social-origin Commons mirrors, upload the new V7 MP4 to GitHub and give only its own download link. Do not re-present V4/V5/V6 or claim creative acceptance. V5 untouched. If the lane is the broader channel rebuild, continue `PLAYBOOK.md` from the latest recorded state, not from scratch.

After every meaningful step: `python3 tools/continuity.py checkpoint ...`, update `CHANNEL_STATE.json` / `STATE.json`, then `refresh`, `render`, `validate`, `render --check`, commit and push on `{{BRANCH}}`.

Now acknowledge the exact resumed Monarch Cam state in one short paragraph and tell the single next action. Do not ask the user to repeat history or explain the workflow.

## V6 rejection / V7 active task — 2026-11-05

- V6 was rejected after its GitHub upload/download-link answer: `Yeh Kya chutiyapa banaya ha NAHI abhi bhi theek se nhi ...` plus six reference screenshots. Technical QC, 49/49 checks, 9/9 audio gates, CI success and V6 links are **not** creative acceptance.
- The user wants `📈 trending viral videos` / social-platform clips, `viral ke sath sath purani bhi chalenge`, `bas clips mazedar next level honi chaiye`, the best hooked/engaging scenes extracted, and a full 60s ranking built on them. The reference screenshots show `ranking list kese lagi ha sab kuch visible horha ha main hamra kuch kat nhi rha`: full-screen uncut clip, visible hook, all 1.-7. list items, right UI, caption bubble, Subscribe and bottom chrome.
- V7 is a separate package at `production/monarch-cam/short_ranking_raw_v7/` with workflow `.github/workflows/monarch-cam-short-ranking-viral-v7.yml` and deliverable `deliverables/MONARCH_CAM_7_Most_Unexpected_Internet_Moments_Ranked_60s_Short_VIRALSTYLE_V7.mp4`.
- Rights boundary: ten rights-cleared social-origin Commons mirrors; per-title Commons API extmetadata, original SHA-1, Credit/Categories social origin and CC BY attribution; no unverified currently trending TikTok/Instagram/Reddit/Dailymotion/YouTube reposts, no current-trending claim, no legal opinion.
- Visual boundary: blurred full-frame background plus sharp uncut source frame; no V6 crop routine, no zoom, no black empty top, no letterbox; all seven labels visible from the first frame.
- No V7 MP4, QC, download link, human full-motion/native-audio listening, creative approval, sign-off, perfection, retention, virality or audience result is claimed yet. V4/V5/V6 stay rejected; V5 untouched.
