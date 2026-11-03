# Video / Audio / Motion — forensic harvest #2

**Date:** 2026-11-03 · **Trigger:** "video skills ko next level le jao — sfx, M G, music"
**Spend:** $0 · **Result:** 5 house skills authored + 6 packs vendored + a licence-verified map of what exists.

---

## 1. The four repos you named — what they actually are

| Repo | Real size | Licence | Contents | Verdict |
|---|---|---|---|---|
| `yihui-dev/awesome-opus5-5-videos` | 834 KB | MIT | **703 prompt specs** + an 813 KB `videos.json` catalogue of code-made videos (SVG/CSS/Canvas/Three) | **Vendored** as `skills/opus55-video-vault`. Highest idea density per KB we have found |
| `Vincentwei1021/video-shotcraft` | 201 MB | Apache-2.0 | **125 shot recipe cards** in 10 categories + `sfx-sourcing.md` + `music-beat-sync.md` + a Freesound tool | **Already vendored** — confirmed complete. This is the best single motion asset in the repo |
| `calesthio/OpenMontage` | 77 MB | **AGPL-3.0** | 2,669 files, **140 SKILL.md**, 594 Python, 75 TS — three.js, GSAP, Remotion, HyperFrames, manim, lottie, TTS/STT, music, sfx | **Vendored as reference only.** Copyleft: read it, never link its code into our app or a client deliverable |
| `storytold/filmcraft` | 39 MB | Apache-2.0 | Rust desktop NLE, 1,906 files — codec parity docs, captions, graphics, performance, gaps | **Not vendored as code.** Its docs (codec parity, audio discipline) were read and folded into `mix-master` |

**Shot recipe coverage (shotcraft):** typography 22 · ui-entrance 21 · effects 15 · transition 15 · interaction 11 · opening 11 · camera 10 · rhythm 8 · outro 6 · data 5. That is the complete motion vocabulary — nothing was missing there.

---

## 2. New house skills (authored, MIT, ours)

| Skill | Lines | What it fixes |
|---|---|---|
| `skills/monarch-video-lab/music-score` | 179 | "music isn't at the level" → form before texture: key, tempo solved from seam frames, i9→VImaj9→iv9→V7sus♭9→Imaj9 Picardy, 7-voice pad / Karplus pluck / mono Reese / synthesised drums, a 6-section stem arc, export + stems + beat sheet |
| `skills/monarch-video-lab/sound-design` | 212 | "sfx aren't there" → 8 synthesised cue families with working numpy, a cue-sheet schema, a 5-step selection protocol, loudness targets, and 5 harshness bans |
| `skills/monarch-video-lab/mix-master` | 149 | objective QC → BS.1770 measurement, spectral slope gate, mono-fold check, click detector, and the `loudnorm→aresample→alimiter` chain with the two classic traps |
| `skills/monarch-video-lab/motion-graphics` | 148 | movement → five laws, frame-exact timing maths, 8 beat recipes, typography/composition rules, still-QC before a 2,160-frame render |
| `skills/monarch-video-lab/sfx-library` | 118 | reuse → folder contract, manifest schema (SHA-256 + licence URL + attack/tail + spectral centre + harsh flag), sourcing protocol, naming, analysis pass |

All five are written against **our own** code (`showreel/build_audio_60fps.py`, `public/showreel/index.html`) so they describe what actually runs, not theory.

---

## 3. Packs vendored this round

| Pack | Upstream | Licence | Payload |
|---|---|---|---|
| `opus55-video-vault` | yihui-dev/awesome-opus5-5-videos | MIT | 703 prompts + `data/videos.json` (3.8 MB) |
| `openmontage` | calesthio/OpenMontage | AGPL-3.0 (reference) | 147 SKILL.md across three.js, GSAP, Remotion, HyperFrames, manim, lottie, music, sfx (14 MB) |
| `filmcraft` | storytold/filmcraft | Apache-2.0 | docs + README + 1 skill (Rust app not included) |
| `zzfx` | KilledByAPixel/ZzFX | MIT | procedural SFX generator, 1 file |
| `pyloudnorm` | csteinmetz1/pyloudnorm | MIT | BS.1770 loudness metering |
| `tonejs` | Tonejs/Tone.js | MIT | web-audio scheduling reference |

Repo skills total: **931 skills · 26 packs · 45 MB**.

---

## 4. The gap analysis (what still does not exist anywhere)

Ranked by money impact:

1. **Thumbnail / CTR craft.** Still zero. In 931 skills there is no "design a thumbnail that earns a click" skill. This is the single highest-ROI writing job left for the YT business.
2. **Hook writing / retention engineering.** Shot-level recipes exist; *story*-level hook structure does not. `video-shotcraft` gives you an opening shot, not an opening line.
3. **Reference-matched scoring.** No skill anywhere explains how to analyse a reference track and match its tonal balance and arrangement density. (This is exactly what you asked for and why the music still feels short of the mark.)
4. **Sound-design for Roman-Urdu/Urdu voice.** No TTS+DSP chain tuned for a non-English timbre at −14 LUFS.
5. **Faceless visual identity.** Nothing about building a consistent faceless look (palette, grain, motion signature) across 100 videos.

Items 1–3 are worth writing next. 4–5 depend on the channel names you have not shared yet.

### Reference-matched scoring — the honest answer
It is not on GitHub as a skill because it is a measurement job, not a library. The method is:
```
reference track  →  STFT  →  band-energy curve (8 bands, per second)
your track       →  STFT  →  same curve
difference       →  tells you exactly which band and which section is off
arrangement      →  onset density per section (notes/sec) compared the same way
```
That is buildable in ~120 lines of numpy on top of `librosa` (BSD/ISC) and `pyloudnorm` (already vendored). Ask me for it and it becomes `skills/monarch-video-lab/reference-match` plus a real script that runs on any two files.

---

## 5. Licence ledger (what we may and may not do)

| Vendored | Ship in client work? | Link into app? |
|---|---|---|
| MIT / Apache-2.0 / BSD / ISC packs | yes, with attribution where required | yes |
| `openmontage` (AGPL-3.0) | **read-only reference** | **no** — AGPL would force our source open |
| `filmcraft` (Apache-2.0 docs) | yes | n/a (not code) |
| Freesound CC0 | yes | yes |
| Freesound CC-BY | yes, with credit in the delivery | yes |
| Freesound NC / unknown | **never** | never |

Deliberately **not** vendored: `MoneyPrinterTurbo` (MIT but stock-spam by design — violates `03_VISUAL_OS.md`), `jub0t/Concat` (AGPL), `sergree/matchering` (GPL-3.0 — good tool, wrong licence for a commercial repo; if we want it, it goes in a separate GPL satellite).

---

## 6. What this changes in practice

A 36-second film now has a documented chain instead of a vibe:

```
beat_sheet.json  →  music-score (§0–3)  →  stems
                →  sound-design (§2 cue families, §4 mix)  →  sfx
                →  mix-master (gates)  →  audio_qc.json  →  pass
picture: motion-graphics (5 laws + still QC)  →  2,160 frames  →  mux
```

Every one of those steps has a pass/fail condition. That is the difference between "improved" and "at the level".
