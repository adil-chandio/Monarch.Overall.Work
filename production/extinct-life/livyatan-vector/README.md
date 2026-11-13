# Livyatan — the whale that fought Megalodon

A 66-second flat-vector documentary short built to match the reference channel's
style, measured frame by frame in `docs/research/competitor-apexmorph/`.

**Delivered:** `Livyatan-The-Whale-That-Fought-Megalodon-66s-720p.mp4`
Drive `12Evyr8qBt4MeIi8LRzhq54MmkRvJaN7b` · 6.2 MB · 1280×720 · 30 fps · 65.8 s

## What is in it, and where each part lives

| Part | File | Note |
|---|---|---|
| Silhouettes | `scripts/lib/creatures.py` | Single continuous bezier contours. NOT ellipse stacks — that was the first attempt and it was rejected on sight. |
| Bezier engine | `scripts/lib/bezier.py` | Cubics flattened at 28 segments per curve, under 1.3 px of error at a 1000 px box. |
| The film | `scripts/livyatan-film.py` | 16 beats, each a pure function of `t`. |
| Narration | generated, `voice-05` | 177 words, 65.81 s across three clips. The text is in `NARRATION.txt`. |
| Ambience | brown noise 40–220 Hz | The bed under the voice. The reference never runs a bare voice track. |

## The five style elements reproduced from the reference

1. **Depth-aware water** — vertical gradient, then soft god-ray shafts drawn
   additively and scrolled, then three parallax layers of matter. This is what
   separates "water" from "a blue rectangle".
2. **Drifting subjects** — every animal moves 6–18 px/s with a slow bob. Nothing
   in the reference ever sits still and neither does anything here.
3. **Label plates** — dark rounded plate, hairline border, white caps. Not bare text.
4. **Gold measurement bars** — `~17 M` on a gold rule with end ticks.
5. **Sonar arcs** — radius-chasing arcs propagating from a subject.

## Honest state of this cut

Built in one pass at 720p. Three things are knowingly unfinished and are recorded
in the job resume command, not hidden here:

- The counting grid, the fake rewind UI, and any water-surface shot are not built.
- The whale silhouette is good at 400 px but its jaw is a stroke, not an opening —
  a close-up would show it.
- Narration is generated speech, not a human VO. It is honest about what it is.

## What it cost, measured

1974 frames, 1 m 59 s on one CPU core at 720p. The Cycles pipeline this repo also
uses needs 30 CI shards for the same minute of footage. That difference is the
reason this route exists at all.
