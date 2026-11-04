# v4 build notes — a shot-for-shot rebuild of REF-01

The reference is analysed in `docs/reference/REF-01-nvidia-reel.md`; the numeric
comparison of this build against it is regenerated on every render into
`docs/reference/REF-01-DIFF.md`. This file records the decisions, including the
ones that were wrong first.

## What it is

720×1280, 30 fps, 23.35 s, no voice-over, −14.02 LUFS. Fourteen scenes, thirteen
cuts, on the reference's own measured timecodes:

```
0.000  0.533  0.833  1.000  1.300  3.133  9.133  11.700
12.167 12.467 12.667 12.967 13.333 14.800
```

Those times are not a mood board. They are the output of `tools/analyse_ref.py` on
the reference file, and every one of them is a scene boundary in `showreel/v4/index.html`.

## Structure (the reference's, not a generic short)

    motif      0.00 – 3.13   TWENTY → slam → macro → bag → stool + "HE SAID NO"
    reveal     3.13 – 9.13   red plate, logo, hands + note, 2008, subject rises
    grade      9.13 – 11.70  same frame, red eyes, subscribe pill
    loop      11.70 – 14.80  the same five shots again, tighter
    CTA       14.80 – 23.35  red reveal → pill → 2-frame flash → glass card

36 % of the film is the CTA. That is the format.

## Things that were wrong first, and why

1. **The dissolve went the wrong way.** I faded the incoming plate in over its
   window, so at the cut frame it was only ~17 % visible and the cut measured 0.12
   against the reference's 1.33. The reference's alpha profile at 0.833 is
   `0 → 0.757` in a single frame: a jolt, then a settle. The scene table now lands
   each plate at 0.66 *on* the cut frame and finishes over the span, while the
   outgoing plate holds full opacity at the cut and fades underneath.
2. **Animation was louder than the edit.** Type slams took 0.30 s, so the detector
   raised its threshold above the cuts and three of them vanished. Slams are now
   0.09–0.11 s of blur-assisted arrival; the cut is the biggest change in its own
   window.
3. **Locked plates.** The reference measures 92 % static frames and ≤ 0.56 %W drift.
   A full-frame plate that travels is its own cut, which is how a phantom cut
   appeared at 3.5 s. Plates arrive in place; only the type moves.
4. **A scene left out of the table still painted.** When the loop was re-cut, the
   old `#s11` section stayed in the markup with nothing managing its opacity, and it
   composited over the CTA for the last 8.5 s. `.scene` is now `opacity:0` by
   default, and the gate fails if any `section.scene` is missing from the table.
5. **Frame 0 was black, and the encode was 2 frames short.** The first capture
   landed before the CSS background plates were composited; the frame dir was also
   stale between runs and would have to be re-checked. There is a warm pass, an
   explicit `-start_number 0` / `-frames:v`, CFR at the film rate, and
   `tools/check_render.py` verifies the finished pixels frame by frame.

## Proof

Every render runs, in order:

- `tools/verify_v4.mjs` — the composition's own timeline under jsdom (43 targets,
  12/12 cuts change the picture, no two plates layered outside a dissolve window,
  the flash on 20.633 s, the glass card holding to the last frame)
- `tools/render_v4.mjs` — real Chromium, timeline seeked per frame, exact frame count
- `tools/check_render.py` — pixels against the scene table, frame count, and a
  per-scene colour signature it writes out so the check can be audited
- `tools/analyse_ref.py` + `tools/ref_shots.py` + `tools/ref_deep.py` — the same rig
  that measured the reference, run on the rebuild
- `tools/ref_diff.py` — 24 rows against the reference with explicit tolerances

## Current diff

21 of 24 rows pass. What does not, and why:

| row | reference | rebuild | why |
|---|---|---|---|
| edge_density | 1.65 | ~3.1 | the reference is a 980 kb/s **AI-upscaled** delivery with visible upscaler mush; generated plates are clean 2.7K detail. Plate blur is at 3 px; matching it exactly would mean deliberately destroying the plate |
| palette_distance | — | ~35 rgb | the green/red families differ (my bag green `#2f8f22` vs its `#446f02`) because the plates are mine |
| cut_alignment | 13 cuts | 13 cuts, recall 12/13 | one loop cut reads 2 frames late: two adjacent shots in the loop both cut to a plate of the same bag, so the detector finds the boundary one frame off |

The audio rows all pass: −14.37 LUFS against −14.02, true peak −0.10 against −0.31,
LRA 2.2 against 1.7, and the pre-cut transients land 17–110 ms before their cuts,
which is what the reference's own transient table shows.

## Pass 5 — the scene that never left

The picture at 19 s was a portrait sitting on a khaki field, with a rotated
BILLION in the corner and a fan of bills behind his head. None of those layers
belong to the CTA. They belong to `s4` (1.00–1.30 s) and `s15` (12.67–12.97 s).

`s15`'s layer was a red herring: on its own it is correct. The real fault was
`s4`, and it was arithmetic, not design:

```
s4 window      1.000 → 1.300 s          (0.300 s long)
entrance       duration = max(0.43 * 0.75, 2/30) = 0.3225 s, starting at 1.000
               so it finishes at 1.3225 s
hide           tl.set(s4, {opacity: 0}, 1.300)
```

The hide fires at 1.300 s, and then the still-running entrance writes
`opacity: 1` back at its next tick. GSAP keeps rendering the last inserted tween
on a property, so `s4` stood at full opacity from **1.33 s to the end of the
film** — 22 seconds under every later scene, and in front of them wherever a
later scene has a transparent or `backdrop-filter` layer.

That is why the CTA measured `[118,101,70]` khaki instead of the reference's
`[59,26,23]` maroon, and why it turned *green* after the flash: `#s14red`
(`mix-blend-mode: screen`) screen-blends with what is underneath it, and what
was underneath it was a green money bag.

Two fixes:

1. An entrance tween may never outlive its own window:
   `entDur = min(max(dis*0.75, 2/FPS), max(outT - inT, 1/FPS))`.
2. Frame 0 is authored in the markup, not by the timeline. A zero-duration set at
   exactly `t = 0` is never applied — GSAP has not inserted it yet when the
   timeline sits on 0 — so `s1` stays `opacity:1` inline and the timeline only
   ever hides it.

`tools/timeline_probe.mjs` now samples the real timeline headlessly and fails the
build, by scene name and by second, if any scene outlives its window or if frame 0
is unpainted. It runs before the render, so this class of fault costs two seconds
instead of a seven-minute render.

## Measured before/after (master at 19 s, right-hand background)

| | before | after | REF-01 |
|---|---|---|---|
| CTA background | `[118,101,70]` | — | `[59,26,23]` |
| CTA background after flash | `[100,135,92]` green | — | `[49,6,7]` |

The flash was also re-measured off the reference frame by frame: it is **three**
frames — 145, 139, 139 luma — building through 61 and decaying through 48. The
build had it as two frames flat at 217, which is shorter and harder than the
reference.

## Pass 6 — the pill, and the gate that was asserting my own number

Two things were left, both now measured rather than described:

- The CTA's yellow pill arrived at 18.72 and popped in. REF-01's own frames put the
  start at **19.03** and it is still growing at 19.9 (yellow share 0.8 → 3.1 → 4.5 →
  6.0 → 7.5 %). It also cleared on the flash frame, stacking a second full change on
  the flash — the reference's detector finds no cut at 20.633, and that stacking was
  the "1 extra cut" in the diff. Now springs in over 0.92 s from 19.03 and clears at
  20.750 into the glass card.
- `tools/verify_v4.mjs` required `flash >= 0.9` because an earlier build ran it at
  0.9. The reference measures 145 luma over a ~40 base, i.e. ~0.5. The gate was
  asserting my first attempt, not the reference. It now asserts a band around the
  measurement.

`edge_density` and `palette_distance` are still failing and the fix for each is known
and written down in `docs/v4-KYA-KIYA.md`, including the measured price of the cheap
version and why it was not taken: an extra 2 px of global blur would pass edge_density
at 1.59 against 1.65 and blur all 701 frames.
