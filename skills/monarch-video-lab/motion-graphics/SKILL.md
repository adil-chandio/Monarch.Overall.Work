---
name: monarch-motion-graphics
description: Build cinematic motion graphics for MONARCH films — kinetic typography, stat count-ups, logo stings, lower thirds, chart hits, 3D camera moves — as deterministic code (HTML/Canvas/SVG/GSAP/Three) rendered to frame-accurate video. Use when a reel needs motion that actually moves, not fades over stock.
license: MIT
---

# monarch-motion-graphics

The MONARCH way to build a moving image: **code is the animation**, so every frame is reproducible, adjustable and free.

> **Lineage:** `skills/hyperframes` (motion-doctrine, cut-the-curve, oversized-cursor, seam-craft), `skills/video-shotcraft` (125 shot recipes), `skills/openmontage/.agents/skills/{motion-graphics,canvas-procedural-animation,gsap-*,threejs-*}`, and the v3 showreel stage (`public/showreel/index.html`, 2,160 frames).

---

## 0. The five laws

1. **One protagonist per beat.** Exactly one element owns attention at any frame. Everything else yields: lower opacity, smaller scale, blurred, or off-stage.
2. **Velocity-matched seams.** A cut lands when outgoing and incoming motion share a direction and speed. Cut mid-motion, never after a hold.
3. **No idle wobble.** Nothing moves without a reason. Ambient drift is banned; breathing is not the same as shaking.
4. **Oversized causal cursor.** When a click matters, the cursor is 7cqw and its click causes the change — visible cause before visible effect.
5. **Never a flash-frame.** Seams are opaque; a white gap between two scenes is a defect, not a transition.

---

## 1. Shot vocabulary you actually need

| Beat | Recipe | Duration |
|---|---|---|
| Hook | kinetic slam + oversized cursor click | 0–2.5 s |
| Proof | stat count-up + SVG stroke-draw of a curve | 2–5 s |
| Product | 3D UI flyover, elements entering on z | 4–8 s |
| Parallel | quad-split, four scenes breathing in sync | 6–10 s |
| Punch | crash-zoom on a hard cut + 2-frame freeze | 0.5–1 s |
| Morph | UI → brand lockup, shared-element transition | 1–2 s |
| Rhythm | speed-ramp: 0.5× → 2× → freeze | 1–3 s |
| Close | signature draw-on + lockup | 2–3 s |

The full 125-recipe set lives in `skills/video-shotcraft/references/shots/` — read the specific file, do not improvise a recipe.

---

## 2. Timing maths (frame-exact, non-negotiable)

```js
const FPS = 60, TOTAL = 2160;
const frameToT = (f) => f / FPS;
const tToFrame = (t) => Math.round(t * FPS);

// every animation must be a pure function of t, never of wall-clock
const scene = (t) => ({ x: ease(t / 0.6) * 400 });
```

- Render with `--deterministic-frames`, pausing the clock between frames (`window.__seek(frame)`).
- Any use of `Date.now()`, `performance.now()`, `requestAnimationFrame` inside a scene = non-reproducible render = reject.
- Set `document.timeline` or your engine's seek to the exact frame; verify frames 0, 1, mid, last are pixel-identical across two runs (hash them).

### Easing library
```js
const expoOut = (x) => 1 - Math.pow(2, -10 * x);
const power4Out = (x) => 1 - Math.pow(1 - x, 4);
const springOut = (x) => 1 - Math.exp(-6 * x) * Math.cos(10 * x);
// nudge curve used across MONARCH: 10 / 65 / 25 percent segments
```

---

## 3. Typography

| Rule | Value |
|---|---|
| Display size | ≥ 12% of frame height for a hero word |
| Tracking | tight for display (−2%), normal for body |
| Line height | 0.92–1.0 for stacked display type |
| Line breaks | break at the word that carries the idea, not at the width limit |
| Reveal | mask-lift per line, 80–140 ms stagger, 0.45 s duration |
| Colour | one accent maximum per frame |

Banned: centred paragraphs, three-line stacks that read as a paragraph, drop shadows on display type, more than two typefaces.

---

## 4. Composition

- **Rule of thirds is a starting point, not a law.** Overlap is allowed when it creates depth (foreground type over background scene).
- **Negative space is a subject.** Leave 25–40% of the frame empty on a hero beat.
- **Depth = 3 planes minimum** (background plate, mid subject, foreground grain/vignette).
- **Never let two text blocks touch.** 24 px minimum on a 1920 frame.
- **Grain/vignette at 4–8% opacity** on every frame — it is what separates "HTML screenshot" from "film".

---

## 5. Render pipeline

```bash
# deterministic frame capture (headless chrome, frame by frame)
node showreel/render_60fps.mjs         # in this repo: 2160 frames, crf 16

# verify before shipping
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 out.mp4
# must equal 2160. If it is 2159 or 2161 the seek is off by one.
```

Rules:
- `crf 16` for a master, `crf 20` for a preview. Never `crf 23+` for anything public.
- 60 fps even if the source motion is 30 — the extra frames carry the sub-frame easing.
- Audio muxed in a **second pass** so a re-render never re-encodes audio.

---

## 6. QC a still before rendering 2,160 frames

Pull 8 stills at the seams plus the middle of every beat:

```bash
python3 - <<'PY'
import imageio_ffmpeg, subprocess
for f in [0,148,516,1050,1428,1800,2100,2159]:
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-ss',str(f/60),
                    '-i','master.mp4','-frames:v','1',f'/tmp/qc_{f}.jpg','-y'])
PY
```

Look for: overlapping text, clipped type at frame edges, empty frame (missing layer), misaligned equaliser bars, watermark overlaps, and stale copy strings. **Five of the seven v3 showreel fixes came from this check, not from a full render.**

---

## 7. Anti-patterns

- **Fade-in cards on a static background** — that is a slideshow, not motion.
- **Conic "god rays" without blur/mask** — reads as a harsh X.
- **Stock B-roll as the hero** — banned by `03_VISUAL_OS.md`.
- **Reset `el.style.display = ''`** — reintroduces hidden layout; set explicit values.
- **rgba() radial layers without a solid base colour** — shows the page background through the frame.
- **Animating `top/left`** — use transforms; layout thrash drops frames.
- **A `window.onload` timer** — non-deterministic; the render will differ run to run.

---

## 8. Where to look in this repo

| Need | File |
|---|---|
| The working 60 fps stage | `public/showreel/index.html` |
| Frame capture | `showreel/render_60fps.mjs` |
| 125 shot recipes | `skills/video-shotcraft/references/shots/` |
| Motion doctrine, seams, cursor | `skills/hyperframes/` |
| GSAP / Three / Lottie / Manim patterns | `skills/openmontage/.agents/skills/` |
| 703 catalogue prompt specs | `skills/opus55-video-vault/prompts/` |
