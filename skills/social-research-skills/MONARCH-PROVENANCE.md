# Provenance — social-research-skills

| field | value |
|---|---|
| source | https://github.com/ScrapeCreators/social-media-research-skills |
| commit | `64ba7b4dea71e130d2712ffb6c1c1024b3b7c4b2` |
| licence | MIT (per-skill `license: MIT` in front-matter; repo LICENSE present) |
| vendored | 2026-11-03 via `scripts/vendor-skill.mjs` |
| files | 18 (14 SKILL.md + LICENSE + README) |
| role | **methodology reference only** |

## How Monarch uses this

The 14 skills are *methods* — outlier-post finding, comment mining, creator teardowns,
audience research, transcript intelligence, trend discovery. They are instruction
documents, not code.

**They describe calls to the ScrapeCreators API** (a paid third-party service) in their
`references/` examples. Monarch does **not** call that API and does not require it. The
same jobs are implemented locally, keyless and free, in `yt_intel/`:

| these skills describe | Monarch implements it as |
|---|---|
| trend discovery | `python -m yt_intel demand "<topic>"` (autocomplete position/spread/expansion) |
| competitor teardown | `python -m yt_intel channel @handle` + `topic` saturation |
| transcript intelligence | `python -m yt_intel reverse <video_id>` (wpm, CTA density, reading grade) |
| outlier post finding | `yt_intel.forensic.saturation` (top-3 share, winner ratio, views/hour) |
| comment mining | **not implemented** — needs the API or comment HTML; see gap list |

## Rules carried over

- the outlier rule: judge a video against its channel's median, never against the platform
- label the evidence class (observed / proxy / inferred) on anything published
- never quote an engagement number without its capture date
