# monarch-video-lab

Four house skills plus a licensed-library map, written from a forensic read of four repos you pointed at:

| Problem | Skill | Fix it encodes |
|---|---|---|
| "the music isn't at the level" | [`music-score`](./music-score/SKILL.md) | form, harmony, stem arc, tempo solved from seam frames |
| "sfx are not there yet" | [`sound-design`](./sound-design/SKILL.md) | 8 cue families synthesised in numpy, harshness bans, cue-sheet protocol |
| "audio isn't clean/loud enough" | [`mix-master`](./mix-master/SKILL.md) | BS.1770 measurement, pass/fail gates, the loudnorm→aresample→limiter chain |
| "motion should move more" | [`motion-graphics`](./motion-graphics/SKILL.md) | five laws, frame-exact timing maths, 8 shot recipes, still-QC before render |
| "we keep re-downloading sounds" | [`sfx-library`](./sfx-library/SKILL.md) | folder contract, manifest schema, licence gate, analysis pass |

## Where these came from

| Upstream | Licence | What we took | What we did not |
|---|---|---|---|
| `yihui-dev/awesome-opus5-5-videos` | MIT | 703 prompt specs + `data/videos.json` catalogue → `skills/opus55-video-vault` | no media, no Skillry links vendored |
| `Vincentwei1021/video-shotcraft` | Apache-2.0 | already vendored: 125 shot recipes, sfx-sourcing, music-beat-sync | no `node_modules`, no demo assets |
| `calesthio/OpenMontage` | **AGPL-3.0** | skills **read as reference** → `skills/openmontage` (147 SKILL.md) | no code copied, nothing linked into the app |
| `storytold/filmcraft` | Apache-2.0 | NLE/audio discipline docs read → folded into `mix-master` | it is a Rust desktop app; not vendored |
| `KilledByAPixel/ZzFX` | MIT | procedural SFX engine → `skills/zzfx` | — |
| `csteinmetz1/pyloudnorm` | MIT | BS.1770 measurement → `skills/pyloudnorm` | — |
| `Tonejs/Tone.js` | MIT | web audio scheduling reference → `skills/tonejs` | build not vendored |

## The one rule

These skills are the **method**. The code that runs is `showreel/build_audio_60fps.py` and `public/showreel/index.html`. If a skill and the code disagree, the code is wrong — fix it there, then update the skill.
