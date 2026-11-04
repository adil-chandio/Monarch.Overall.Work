# v3 — HyperFrames render (real browser, real GSAP)

`public/demo/viral-short-v3.mp4` · rendered by [HyperFrames](https://github.com/heygen-com/hyperframes)
on the GitHub runner, not painted by a CPU loop.

## Why v3 exists

v2 was a Skia painter driven by a hand-rolled frame loop. It passed its own checks, but it
was still **one process drawing rectangles**: no browser layout, no real CSS, no plugin
ecosystem, no shader transitions, and no way to use the two hundred motion blocks the
HyperFrames registry ships.

v3 replaces the painter with the thing the whole ecosystem uses:

```
showreel/v3/index.html   →  chrome-headless-shell  →  GSAP timeline seeked per frame  →  ffmpeg
```

## The composition

| | |
|---|---|
| file | `showreel/v3/index.html` (one file, self-contained) |
| runtime | GSAP 3.14 — vendored at `showreel/v3/vendor/gsap.min.js`, **no CDN** |
| fonts | Anton + Poppins, vendored at `showreel/v3/vendor/fonts/` (the runner has no internet fonts) |
| protocol | `window.__timelines["main"] = gsap.timeline({paused:true})`, the contract HyperFrames seeks |
| length | 42.24 s — derived from the measured VO timestamps in `public/demo/vo/timing.json` |
| scenes | 7 beats + 2 full-frame inserts |
| tweens | 506 |

### Seams (cut-the-curve §3)

- exit `x: 0 → −230` over 0.24 s on `power4.in`, blur `0 → 10px`
- the exit holds at **0.92 opacity** into the overlap window instead of fading early:
  a 0.28 × CUT fade is 0.28 of the *clock* but only **0.06 % of the travel** on a quartic
  curve, which blacks the frame out through the whole acceleration
- entry `x: +230 → 0` on `power4.out`, igniting at **0.45**, same 0.24 s
- 2.5 frames of overlap (pulled entry start), so the summed scene opacity never dips below
  **0.92** — measured on every frame, not assumed

### Motion

- camera push **1.0 → 1.045** across every beat
- waterfall entry on the hook: word-by-word, gaps decaying ×0.84, `expo.out`
- inverse zoom-through arrival on the 36× and CONCENTRATED beats (`1.25 → 1.0`)
- 29-spoke lattice that opens and keeps drifting; 100-cell grid with a scan column
- two insert shots with radial speed-line bursts
- a data ribbon (waveform + beat ticks + playhead) and a live `BEAT 0n / 07` chip belong to
  the film, not to a beat

## The gate

`node tools/verify_v3.mjs` — runs the composition's real inline script against the real
GSAP build inside **jsdom**, then drives the timeline frame by frame:

```
1267 frames · NaN/undefined style values: 0
seam @ 4.89s  min summed opacity 0.92  max scenes 2  settled:[s2]
...
PASS — timeline, seams, exit velocities and beat activity all check out
```

It fails the build on: a NaN transform, all seven scenes composited at once, a seam that
blinks black, an exit that is too still to be a cut, or a beat where nothing changes.
CI runs it **before** the render, so a broken film never reaches the encoder.

## Sound

`showreel/v2/audio.py --seams showreel/v3/seams.json --out public/demo/v3-mix.wav`

Same score engine as v2 (A minor, 120 BPM, Am–F–C–G, sidechain pump, real stereo, mono sub
below 120 Hz) plus insert cues. Every SFX is derived from `seams.json`, so it is
frame-locked by construction rather than by ear.

## Rebuild

Push anything under `showreel/v3/` — that is the render button:

```bash
git add showreel/v3 && git commit -m "tweak" && git push
```

`.github/workflows/hyperframes-v3.yml` then, on `ubuntu-24.04` with a real
`chrome-headless-shell`:

1. `npx hyperframes lint` + `validate`
2. `node tools/verify_v3.mjs` — the composition gate
3. `npx hyperframes render … --fps 30 --quality delivery`
4. builds the mix, measures it, masters to −14 LUFS / −1.5 dBTP / 48 kHz
5. commits `public/demo/viral-short-v3.mp4` back to the branch

## Honest limits

- The sandbox that authored this has **no working Chromium** (`libnspr4`/`nss3` missing, no
  root, no apt) and no GPU, so it cannot render here. That is exactly why the render lives
  on the runner — not a workaround, the correct place for it.
- HyperFrames' shader transitions need WebGL, which `chrome-headless-shell` on a CPU runner
  supplies through SwiftShader at reduced speed. They are available; v3 does not use them
  yet because they cost render time the current runner budget does not have.
