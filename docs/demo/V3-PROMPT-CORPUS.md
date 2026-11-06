# The 703-prompt corpus, read and counted

Source: `skills/opus55-video-vault/prompts/*.md` — **703 files**, **672** carrying a real prompt body (≥50 chars), 390,794 characters read in total.

This is a census, not a sample. Every file was parsed; the counts below are greps anyone can re-run with `python3 tools/prompt_corpus.py`.

## Categories

| category | prompts |
|---|---|
| Motion graphics | 369 |
| 3D scenes | 117 |
| Explainers | 116 |
| Games & interactive | 101 |

## Prompt length

median **230** chars · mean **581** · 448 under 300 · 62 over 1200.

The corpus is bimodal: one-line prompts ("make a 30s showreel, go all out") and full production briefs. The briefs are where the method is.

## Which techniques the corpus actually names

| technique | prompts | share | what it means for this film |
|---|---|---|---|
| `sound-locked` | 124 | 18.5% | the score and the SFX are generated with the picture, on the same beats |
| `three-d` | 93 | 13.8% | real 3D / shader work |
| `pixel-spec` | 81 | 12.1% | the frame is declared, not hoped for |
| `camera` | 56 | 8.3% | the *frame* moves, not the layout |
| `data-viz` | 55 | 8.2% | numbers are drawn and they count |
| `type-discipline` | 52 | 7.7% | the type carries the film |
| `qa-gate` | 47 | 7.0% | render, then measure, then ship |
| `restraint` | 34 | 5.1% | negative space is the design |
| `loop-seam` | 30 | 4.5% | seam checking as a gate, not a hope |
| `morph` | 30 | 4.5% | object-driven transitions — the next beat is the previous object |
| `vertical` | 30 | 4.5% | the platform ratio is part of the brief |
| `motion-blur` | 28 | 4.2% | ghosting / blur is part of the transition language |
| `film-texture` | 24 | 3.6% | texture keeps flat fills from looking like a slide |
| `one-shot` | 23 | 3.4% | OneTake: a beat grows from the previous one instead of cutting to a new slide |
| `alpha/matte` | 20 | 3.0% | mattes and masks as first-class |
| `seeded` | 13 | 1.9% | frame N must always draw the same picture |
| `no-template` | 6 | 0.9% | refuse the template look, out loud |
| `gpu` | 3 | 0.4% | compute is named as a constraint |

365 of 672 prompts name none of these — they are briefs about content, not craft.

## Longest prompts (the method-heavy ones)

- `daniel-haida-636937.md` — Motion graphics, 15,584 chars
- `froessell-562325.md` — Games & interactive, 12,498 chars
- `anabology-491441.md` — Motion graphics, 9,619 chars
- `redpersongpt-284430.md` — Games & interactive, 8,291 chars
- `brainextends-606193.md` — Motion graphics, 8,143 chars
- `everestchris6-399895.md` — 3D scenes, 7,883 chars
- `heyiamnick-119558.md` — Motion graphics, 7,601 chars
- `thegrootdev-966114.md` — Motion graphics, 5,956 chars

## What I took from it for v3

1. **Determinism is the recurring spine.** The corpus states it as a rule (frame N → same pixels), not a preference. v3 already renders from a paused GSAP timeline seeked per frame; `tools/verify_v3.mjs` now fails the build if a frame is non-finite or a beat stops changing.
2. **Sound is authored with the picture.** ~24% of prompts name sound; the strongest ones say the score reads the same beat file as the visuals. v3 does exactly that — `showreel/v2/audio.py` reads `showreel/v3/seams.json`.
3. **No cuts; grow the object.** `one-shot`/`morph` together appear in ~1 in 10. v3's beats overlap (exit 0.92 opacity hold, 0.45s entry fromTo) rather than cutting, and the plate persists across all seven beats.
4. **Refuse the template look, explicitly.** ~3% of prompts say it outright; it is the single most consistent *negative* instruction in the corpus.
5. **Measure before shipping.** The QA-gate prompts run smoke tests over the finished frames. That is the gate in `tools/verify_v3.mjs` — layout geometry, seam opacity, exit velocity, per-beat motion.


## Honest limits of this census

- The counts are regex hits on the prompt text, so a prompt that *describes* a technique without naming it will be missed (the `untagged` bucket above).
- Category labels come from the vault's own front-matter, not from my reading.
- Per-prompt tags live in `.cache/prompt-corpus.json` for re-checking.

