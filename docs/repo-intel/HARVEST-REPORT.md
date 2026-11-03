# Repo Harvest Report — what came in, what it changes

**Date:** 2026-11-03 · **Method:** GitHub topic sweep → score → license gate → sparse vendor → index.
**Cost:** $0. No paid API, no model credits.

---

## 1. Honest status of the sources you named

| Source | Reachable from this sandbox | Action taken |
|---|---|---|
| **GitHub** | ✅ yes (API + git clone) | swept, scored, vendored |
| **PyPI / npm** | ✅ yes | used for install instructions, not vendored |
| **Hugging Face** | ❌ **blocked** (TLS handshake dies at this sandbox's egress proxy) | catalogued via `fetch_page` + pinned in `models.lock.json` for GitHub Actions to pull |
| **Google Drive** | ⚠️ connector only | not used for skills |
| **Arbitrary websites** | ⚠️ via `fetch_page` only | used for research, nothing vendored from a non-GitHub source |

**Why Hugging Face matters here anyway:** model weights are 0.5–30 GB. They must never enter a git repo. The correct pattern is: repo holds a **lockfile** (exact model + revision + file size), CI downloads, cache keeps it. That is what `models.lock.json` is for.

---

## 2. The sweep

```
28 topics scanned → 1,235 unique live repos
  ├─ license-clean (MIT/Apache/BSD/MPL/CC0/ISC)   814
  ├─ pushed in last ~6 months                     936
  └─ composite score ≥ 60                         925

by space:  yt-automation 417 · monarch-studio 432 · personal-brand 42 · ops 344
```

Scoring: stars (log-scaled, max 40) + license clean (20) + recent (15) + topic fit (15) + repo size sane (10).
Full data: `docs/repo-intel/candidates.json` (1,235 rows). Re-run: `node scripts/harvest-candidates.mjs`.

---

## 3. What was actually vendored (16 packs, 786 skills)

| Pack | Upstream | License | SKILL.md | Why |
|---|---|---|---|---|
| `claude-skills` | alirezarezvani/claude-skills | MIT | 408 | the big library: video content strategist, marketing ops, finance, docs |
| `wshobson-agents` | wshobson/agents | MIT | 185 | plugin-per-domain agent set, 186 skills |
| `marketingskills` | coreyhaines31/marketingskills | MIT | 53 | hooks, positioning, copy — feeds YT + personal brand |
| `baoyu-skills` | JimLiu/baoyu-skills | MIT | 22 | transcript extraction, content repurposing |
| `planning-with-files` | OthmanAdi/planning-with-files | MIT | 18 | the file-based planning method (ops backbone) |
| `ffmpeg-skill` | kajisho5/ffmpeg-skill | MIT | 14 | frame-accurate ffmpeg recipes |
| `html-video` | nexu-io/html-video | Apache-2.0 | 14 | code → video, same family as our showreel pipeline |
| `elephant-goldfish` | google/elephant-goldfish-model | Apache-2.0 | 14 | long-context agent patterns |
| `ponytail` | DietrichGebert/ponytail | MIT | 12 | cross-tool skill surface (13 skills, multi-editor) |
| `skill-seekers` | yusufkaraaslan/Skill_Seekers | MIT | 26 | turns docs/PDFs into skills — how we ingest future knowledge |
| `prompt-master` | nidhinjs/prompt-master | MIT | 1 | prompt architecture reference |
| `book-to-skill` | virgiliojr94/book-to-skill | MIT | 1 | books → skills |
| `distilly` | titanwings/distilly | MIT | 1 | distillation of long sources |
| `website-cloner` | JCodesMore/ai-website-cloner-template | MIT | 1 | client-site reconstruction |
| `html-anything` | nexu-io/html-anything | Apache-2.0 | 0 (README only) | kept for reference; thin payload |
| `awesome-agent-skills` | VoltAgent/awesome-agent-skills | MIT | 0 (README only) | link index only |

**Total on disk: 26 MB.** No media, no `node_modules`, no weights. Each pack carries `MONARCH-PROVENANCE.md` with upstream URL + exact commit.

Regenerate the index any time:

```bash
node scripts/build-skill-index.mjs     # → skills/INDEX.md + docs/repo-intel/skills-index.json
./scripts/find-skills.sh thumbnail      # name search, falls back to body search
node scripts/vendor-skill.mjs owner/repo slug LICENSE
```

---

## 4. Gaps this sweep exposed (the important part)

1. **`yt-automation` has 5 skills and 417 candidate repos.** The biggest business area is the least tooled. The repos that would fix it are Python/ML engines (`Pixelle-Video`, `VidBee`, `VideoLingo`, `GPT-SoVITS`, `VoxCPM`) — they belong in a **satellite workflow repo**, not in this control plane.
2. **No thumbnail skill exists anywhere** in 786 skills. Real gap, real money (CTR). Needs to be authored, not cloned.
3. **`portfolio` has 10 skills, all generic design.** No case-study or client-proof skill exists.
4. **Hugging Face is unreachable here.** Any model-dependent pipeline (TTS, ASR, upscale, music) must run in CI or on Kaggle, driven by a lockfile — never interactively in this sandbox.
5. **Vendoring is a licence risk if we get lazy.** Every pack is one of MIT/Apache-2.0/BSD/MPL. Nothing GPL/AGPL was copied — `MoneyPrinterTurbo` (MIT but stock-spam), `jub0t/Concat` (AGPL), `OpenMontage` (AGPL) were deliberately **not** vendored.

---

## 5. What happens next (needs your call)

**Option A — Model layer lockfile (my recommendation).**
`models.lock.json`: Whisper large-v3 (ASR, exact word timings), Kokoro-82M (TTS, Apache/MIT, 82 MB), a music model, an upscaler. CI pulls with `huggingface_hub`, caches, and the studio space gets "generate voice / align captions / upscale" as real buttons. This is what makes the YT factory actually run.

**Option B — Build the YT factory satellite.**
New repo `monarch-yt-factory` (Python): script → voice → visual → assembly → upload-pack, driven by `config/channels.json` from this repo. This repo stays the control plane and only shows status.

**Option C — Close the skill gaps.**
Author the three missing skills: `thumbnail-craft` (CTR-driven), `case-study-proof`, `hook-lab`. Small, high leverage, no licence questions.

Nothing above is started yet — all three cost decisions, and you said you want no guessing.
