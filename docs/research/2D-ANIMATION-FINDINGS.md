# 2D animation on YouTube — what the measured winners do

**Measured, not remembered.** 146 videos across 8 animation queries, pulled from the
public YouTube search results (`docs/research/anim-research.json`), then 5 of them
opened and read for script signals (`docs/research/anim-deep.json`).

---

## 1. The sample

| Measure | Value |
|---|---|
| videos sampled | **146** |
| median views (all) | **~1.0 M** |
| long-form only (≥ 120 s), n | **72** |
| long-form median views | **1.21 M** |
| long-form p90 views | **12.8 M** |
| long-form median length | **~408 s (6:48)** |
| like-rate, long-form median | **3.98 %** |

**Length matters.** Split by runtime:

| runtime band | n | median views |
|---|---|---|
| ≥ 120 s | 74 | **1,376,653** |
| 60–120 s | 15 | 653,508 |
| < 60 s | 57 | 843,369 |

The 60–120 s band is the **weakest** of the three. A 60-second piece has to survive on
being a short; a 6–7 minute piece earns watch time and gets pushed. Our current film is
60 s, which sits in the worst-performing band of the sample.

## 2. What the winners actually are

Top long-form by views, with the thing each one sells:

| channel | secs | views | what it actually is |
|---|---|---|---|
| Sony Pictures Animation | 408 | 121.2 M | *Hair Love* — **Oscar-winning**, character-first, near-wordless |
| Ashley Yeajee Lee | 195 | 62.1 M | SVA student film, **black-and-white**, high-contrast, emotional reveal |
| Tomoki Misato | 451 | 43.7 M | stop-motion + 2D hybrid, **no dialogue**, visual storytelling |
| Vancouver Film School | 168 | 23.9 M | student film, simple shapes, **one clear idea** |
| Sr Pelo | 736 | 17.3 M | parody/genre, **exaggerated acting**, meme-native pacing |
| Shingo Tamagawa | 180 | 12.8 M | *Puparia* — **one person, years of work**, hand-drawn density |
| Gothfrog | 353 | 11.9 M | SVA thesis, painted, atmospheric |
| Aaron Blaise | 706 | 10.6 M | **ex-Disney animator** — craft demo is the draw |
| GOBELINS Paris | 402 | 2.96 M | school reel, ensemble staging |

Two patterns dominate the top of the list, and neither is "a 60-second narrated
portrait":

1. **Emotional, nearly wordless, character-first short films** (Hair Love, Puparia,
   Wings, Piece of Cake, Last Summer). The animation *is* the storytelling.
2. **Craft/expertise as the draw** (Aaron Blaise, BaM Animation, Gabe Hordos). The
   audience comes to watch somebody who can really animate.

## 3. The script finding that matters most

Five long-form winners could be transcribed. Measured over the whole runtime:

| measure | median |
|---|---|
| words | **342** |
| words per minute | **40.1** |
| words per second | **0.67** |
| runtime | **408 s** |
| auto-captions (i.e. no scripted VO) | **40 %** |

**40 words per minute.** Normal narration runs 140–160 wpm; audiobook is ~150. These
films talk at roughly a quarter of that. They are not narrated — they are *scored*,
with sparse dialogue over animation that carries the meaning.

Our delivered 60-second film runs **≈ 158 wpm** (10 narration cues, ~1,400 words/min
density in the spoken windows). That is not a small stylistic gap. It means the
current film **asks the viewer to listen to a narrator for a full minute**, while the
videos that get a million views ask the viewer to watch.

Fixing this is not a matter of re-recording faster or slower. It changes the script,
the shot count, the acting, and the length.

## 4. What this means for this project — stated plainly

| the sample says | where we are | delta |
|---|---|---|
| ~6:48 runtime, 72 % of the long-form sample ≥ 120 s | 60 s | **7× shorter** |
| ~40 wpm, 40 % with no scripted VO at all | ~158 wpm | **4× too talky** |
| character acting carries the film (Hair Love, Puparia) | 9 held cels, cuts between poses | **not yet animation** |
| craft authority is the draw when there is no story engine | pipeline demo | **no human craft story** |
| like-rate 3.98 % | not yet measurable | — |

The honest summary: **the current film is technically real animation but formally the
wrong film.** It is a 60-second narrated portrait in a market that rewards 7-minute,
near-wordless character pieces or obvious craft mastery.

## 5. What a rebuild has to do

Not "more polish on the same film". The measured requirements:

1. **Length: go to 4–7 minutes.** The 60 s band is measurably the weakest.
2. **Script: cut narration by ~4×.** Roughly 300–400 words total for a 5–6 minute
   piece, and give the film wordless stretches where acting carries a beat.
3. **Acting: real keyframed character animation.** A hold-and-cut cel library cannot
   carry 6 minutes. This needs actual motion — walk cycles with breakdowns, hands,
   weight, timing — on a skeleton, not pose swapping.
4. **Physics and camera: continuous.** Gravity, momentum, follow-through, overlapping
   action; a camera with motivated movement, not a drift.
5. **Lighting: motivated per shot**, with consistent direction, colour and falloff
   across a cut, not a per-shot grade filter.

## 6. What was NOT measured (and so is not claimed)

- Watch time and retention curves — not available without channel access.
- Thumbnail A/B performance — the thumbnails were fetched but not tested against CTR.
- Which specific animation technique each winner used, frame by frame — 5 transcripts
  and metadata were read; the films themselves were not decoded here.
- Comment sentiment on why viewers liked them.

These are the next probes, and they are listed so nobody mistakes this document for a
complete forensic.
