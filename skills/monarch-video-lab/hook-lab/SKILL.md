---
name: monarch-hook-lab
description: Write and score the first three seconds of a video — the script, the on-screen text and the measured audio lift — so the open is the loudest, clearest part instead of a slow build. Use before editing, not after.
license: MIT
---

# monarch-hook-lab

Retention is decided before the viewer decides anything. What decides it is four
mechanical facts about the first ~120 frames:

1. **Motion at frame 0.** A static open reads as a banner ad and gets swiped.
2. **A claim in words within ~1.5 s.** Silence is not intrigue; it is a reason to leave.
3. **Specificity in the claim.** A number, a named thing, a receipt.
4. **No ramp.** Second 1 must already be at body energy.

Point 4 is the one everybody gets wrong, and it is measurable.

```bash
python -m showreel.ctr        # scores the script + on-screen text
python -m showreel.audio_qc.gates public/showreel/audio_master_60fps.m4a --profile web
```

---

## 1. Script scoring

`showreel/ctr/hook.py::score_hook` measures:

| Metric | Weight | What it catches |
|---|---|---|
| `claim_in_1_5s` | 0.30 | openers that set a scene instead of making a claim |
| `specificity` | 0.25 | "we did great" instead of "583,290 views" |
| `onscreen_adds_info` | 0.15 | on-screen text that repeats the narration (wasted second channel) |
| `spoken_fits_window` | 0.15 | a 3-second hook that needs 5 seconds to say |
| `motion_at_frame0` | 0.15 | static openings |

Speech budget: **165 wpm**, so a 3 s hook is ≈ 8 words. Anything longer is a different
video. Hard fails: vague openers ("welcome", "in today's video", "let me"), overruns,
static frame 0.

Grade bands: A ≥ 85, B ≥ 72, C ≥ 58.

---

## 2. Audio side — the v3 lesson

v3 shipped with the **hook as the quietest section of the film**:

```
hook        -19.5 dBFS
deck        -14.7 dBFS     <- 4.8 dB louder than the thing meant to stop the scroll
```

That is a fade-in, and no amount of editing fixes it. The fix was a **body-lift curve**
(8.9 dB at t=0 decaying to unity over 2.55 s) plus section gain automation, which landed
the hook at **−1.6 dB** relative to the deck. `hook_plan_score()` in `hook.py` folds the
measured numbers into the verdict and refuses to call a hook good if the gap exceeds 2 dB.

**Rule: hook ≥ body energy − 2 dB. Always. Measure it, never assume it.**

---

## 3. Four openers that are structurally different

| Variant | Script | Bet |
|---|---|---|
| **A · number slam** | "583,290 views. Zero bought numbers." | the receipt is the hook |
| **B · contradiction** | "Everybody pitches. Nobody ships." | tension, no number needed |
| **C · spec flex** | "36 seconds. 2,160 frames. One take." | craft audience |
| **D · receipt** | "Here's the Studio screenshot. Unedited." | proof-of-work audience |

All four fit inside 2.2–2.5 s at 165 wpm. Never stack two bets in one hook — a number and
a contradiction and a spec list is a trailer, not an opening.

---

## 4. The 3-second build (what actually goes on the timeline)

| Frames (60 fps) | Picture | Sound | Text |
|---|---|---|---|
| 000–015 | hard cut in, already moving | full-level body, lifted +8 dB | the number, huge |
| 016–060 | one deliberate move (push or whip) | impact on the cut | 2–3 words, mono |
| 061–120 | subject established | bed at body level | claim resolved |
| 121–150 | first beat of the real film | lift decays to 0 dB | — |
| 151+ | normal film | normal film | normal film |

The lift **decays**, it does not step. A step is audible as a dropout.

---

## 5. Pre-flight checklist

- [ ] frame 0 is not a logo, a fade, or black
- [ ] the claim is spoken by 1.5 s
- [ ] the claim contains something verifiable
- [ ] on-screen text adds a fact the narration does not say
- [ ] hook measured within 2 dB of body energy (`audio_qc`)
- [ ] no "welcome", no "in today's video", no "let me"
- [ ] 8-word budget respected

---

## 6. Files

| Purpose | Path |
|---|---|
| Script scoring + variants | `showreel/ctr/hook.py` |
| Measured audio numbers | `public/showreel/audio_qc.json` |
| Hook lift implementation | `showreel/build_audio_60fps.py` (`hook lift` block) |
| Delivery gate that would have caught v3 | `showreel/audio_qc/gates.py` → `has_dynamics` |
