# PLAN-08 — How to actually hit the reference level

Forensic pass (microscope level) over all 698 REF frames + the full REF soundtrack,
vs our v6-11 build. Evidence: `analysis/v4-build/forensic/cmp1-3.png` (side-by-side,
23 timestamps), `motion.json` (per-shot camera numbers), and `public/demo/v7-preview.mp4`
(8 s proof clip: new camera system + new sound design, built only from our plates).

This is the analysis + the plan. **Nothing here is built into the film yet** — waiting
on approval before touching the render.

---

## 1. What the reference is really doing (measured, not guessed)

### Shot map (REF cut points from frame-diff + stills)
| # | t (s) | content | camera (measured) | notes |
|---|-------|---------|-------------------|-------|
| 1 | 0.00–0.83 | white card, green **TWENTY** | drift 150, jitter 32, flash-in | white flash frames 0.00–0.37 |
| 2 | 0.83–1.30 | **flash → black, lime TWENTY+BILLION** | drift 193, jitter 56 | violent |
| 3 | 1.30–3.00 | **green field + dark BILLION + bag** | crash-zoom, drift 59→619, jitter 13→32 | jump-cut hold at 1.33 |
| 4 | 3.00–9.00 | **gray storm, bag on stool, "HE SAID NO"** | drift 72, jitter 13 | HE pops 2.17, NO 2.63 |
| 5 | 9.00–11.67 | **red room #1** (2008, man) | drift 48, jitter 18, push | 5.9 s |
| 6 | 11.67–12.57 | **flash → card → black TWENTY BILLION** | drift 193, jitter 56 | white flash 11.63–12.0 |
| 7 | 12.57–12.93 | **green field + BILLION + bag (replay)** | zoom-out, drift 619, jitter 32 | 0.36 s |
| 8 | 12.93–14.63 | **gray storm + HE SAID NO (replay)** | drift 72, jitter 13 | 1.66 s |
| 9 | 14.63–20.63 | **red room #2** (long, push) | drift 39, jitter 19 | 6.0 s, incl. phone-hand beat ~16.5 |
| 10 | 20.63–20.73 | **flash cut** | — | white flash frame |
| 11 | 20.73–23.27 | **red room CTA, subscribe pill** | drift 93, jitter 21 | 2.54 s |

### The five techniques that make it feel "pro"
1. **Hard cuts, and white flash on the two big ones** — the REF fades in from a white
   flash (0.00–0.37) and flashes white again into the replay (11.63–12.0); the other
   transitions are hard cuts. We start straight on the card (no white fade-in), and our
   11.7 flash runs a touch long (to 12.13). Matching the two flash moments + tightening
   ours is part of the fix.
2. **Crash-zoom on the money beats** — the field/money shots are fast zooms
   (drift 600–800 px/s, jitter 30–43 px/f), not static holds. Our field/storm shots
   are near-static (drift 25 px/s, jitter <1 px).
3. **Handheld drift + micro-jitter, not orbit** — the red room moves at ~40 px/s with
   ~18 px/f of smooth jitter. Our red room uses a large orbit (jitter 35–39 px/f),
   which reads as *shaky*, not *handheld* — the opposite of "smooth".
4. **Staggered, beat-synced word pops** — "HE" at 2.17 s, "NO" at 2.63 s, each a
   scale-pop that lands on the music. Our words appear but without the pop/settle
   curve tied to a beat.
5. **Subscribe pill** — glass 2-line pill in the red room, not a flat gray box.

### Sound (REF measured)
- Peak **−0.52 dBFS**, RMS −20.8 dB. Ours: peak −1.20, RMS −21.4 (a touch quieter).
- **Sub band avg −42.5 dB** in REF vs **−53.1 dB** in ours → **we are ~10 dB short of
  sub weight.** The REF runs a *continuous* 808/sub bed, and hard sub drops at
  **11.75 s, 12.0 s and 20.75 s**. Ours only has sub in the drop moments.
- **Air band −80.8 dB** REF vs **−86.6 dB** ours → REF has more high-end air/hats.
- The REF is a **120 bpm** bed: four-on-the-floor kick, hats, snare on 2 & 4, a
  continuous 808, and a **sidechain pump** (music dips ~0.5–0.8 dB on the 0.5 s grid).

**The `v7-preview.mp4` audio already demonstrates this** (kick + 808 + hats + snare,
sidechain pump, whoosh, sub drop, crash). The gap is that our full-film mix
(`mix-23.wav`) uses a different, thinner bed and no continuous 808/sub.

---

## 2. The concrete gaps (ours vs REF), ranked by visual impact

| Gap | Ours (v6-11) | REF | Fix |
|-----|--------------|-----|-----|
| **Static money/storm shots** | s4 drift 25 px/s, s11 26 px/s, jitter <1 | crash-zoom 600–800 px/s | per-shot crash-zoom keyframes on the money beats |
| **Shaky, not smooth, red room** | jitter 35–39 px/f (orbit) | jitter ~18 px/f (handheld) | replace orbit with smooth drift + seeded micro-jitter |
| **Missing opening flash-in** | no white fade-in | white flash-in 0.00–0.37 | white fade-in on the open (tighten the 11.7 flash) |
| **Flat camera** | zoom ~0% everywhere | push + punch | camera layer (push + beat punch), proven in demo |
| **Thin sub / quiet peak** | sub −53 dB, peak −1.2 | sub −42 dB, peak −0.52 | continuous 808 bed + sub drops + louder master |
| **Flat gray CTA box** | `card_pill` gray rect | glass 2-line pill | glass pill (blur + tint + round) |
| **Words not beat-punched** | static scale | scale-pop on beat | keyframe pop tied to the SFX hits |

---

## 3. The build plan (what I will do, in order)

**Stage A — Camera system (the big one).** Add a `camera()` layer to `tools/v6.py`,
exactly the one proven in `demo_v7.py` (AE "camera on a large layer": render zoomed,
crop the window; no warpAffine — that path collapses to ~15 s/frame on this 2-core
box, the crop path does 240 frames in 53 s). Per-shot keyframes from the table above:
- slow **push-in** on the red room + field holds
- **crash-zoom punches** on every money beat (1.30, 12.57, and the drop at 11.67)
- **smooth drift + seeded multi-sine micro-jitter** (7/11/17 Hz) replacing the orbit
- **white flash-in** on the open + a tightened flash into the replay
This is what makes it "smooth" AND "alive" at once.

**Stage B — Type keyframes.** Staggered scale-pop on TWENTY / BILLION / HE / NO /
2008 / SUBSCRIBE, each landing on its SFX hit, with a settle (the `pop()` back-ease
already in the codebase). Glass 2-line subscribe pill.

**Stage C — Sound redesign.** Rebuild the bed to the REF recipe: 120 bpm,
four-on-the-floor kick, hats, snare, **continuous 808**, sidechain pump, and hard
**sub drops at 11.75 / 12.0 / 20.75 s** + whoosh on each flash cut + crash on the
CTA. Master to **−0.5 dBTP**. (The demo's `build_audio()` is the template.)

**Stage D — Re-render + verify.** Full 698-frame render, re-run the 23-timestamp
forensic grid and the cut-<53 ms audio check, and confirm the per-shot camera numbers
now sit inside the REF's measured range.

**Estimated:** A+B are edits to `v6.py` (~2 h of render to iterate), C is `mix.py`/
`film_score.py` changes, D is one full render + mux.

---

## 4. Proof (watch these)
- `public/demo/v7-preview.mp4` — 8 s, new camera + parallax + beat-punch + new sound.
- `analysis/v4-build/forensic/cmp1-3.png` — REF vs ours, side by side, where it diverges.

**Question for approval:** proceed with **A → B → C → D** as one build (the full
ref-match), or stage it (e.g. A+C first — camera + sound — then type/CTA)?
