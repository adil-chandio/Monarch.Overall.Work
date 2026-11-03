# Provenance — self-media-workflow

| field | value |
|---|---|
| source | https://github.com/yanhua1010/self-media-content-workflow |
| commit | `eb1550ac565e350e9c8900f42df528ed9355783d` |
| licence | MIT |
| vendored | 2026-11-03 via `scripts/vendor-skill.mjs` |
| files | 75 (11 SKILL.md + assets/templates + references) |
| role | templates + review cadence |

## What it contributes to Monarch

| asset | used for |
|---|---|
| `topic-pool-template.md` | shape of the yt-automation idea pool (`config/channels.json` pillars) |
| `content-calendar-template.md` | cadence maths for CH-01/02/03 slots |
| `metrics-ledger-template.md` | the ledger `yt_intel` writes its measurements into |
| `content-registry-template.md` | one row per shipped video, with its gate results |
| `weekly-review-template.md` | the Ops space's weekly loop |

## What Monarch deliberately does not take

- **Platform-native copy advice for Chinese platforms** (Xiaohongshu/Douyin/WeChat) —
  out of scope for CH-01/02/03.
- **Its metric definitions.** Monarch computes loudness, CTR and retention from its own
  measurements (`showreel/audio_qc`, `showreel/ctr`, `yt_intel`); importing a second,
  differently-defined metric set would produce two numbers for one question.
