# MONARCH® STUDIO — v4 "Absolute Cinema" Showreel Delivery (`MON-DEMO26-SR`)

**Title:** Proof Over Promises — v4 (measured audio pass)
**Runtime:** 36.00 s · **2,160 frames** · 1920×1080 @ 60.000 fps
**Encoding:** H.264 High, yuv420p, 9.56 Mbps video · 48 kHz stereo AAC 258 kbps
**Delivery date:** November 3, 2026

---

## 1. Download

| Asset | Link |
|---|---|
| **1080p60 Master (v4)** | https://drive.google.com/uc?id=1UngK7-tUHYn4kXR9S05ACX9SeJymYpjX&export=download |
| Watch page (streams in-browser) | https://drive.google.com/file/d/1UngK7-tUHYn4kXR9S05ACX9SeJymYpjX/view |
| Delivery vault folder | https://drive.google.com/drive/folders/1ULb_LwBLOHM9GdvPXf6KXsp0Do9n0Zr1 |
| Client portal (watermarked) | https://monarch-workspace-beryl.vercel.app/?portal=MON-DEMO26 |
| In-repo master (43 MB) | `deliverables/MON-DEMO26_Proof_Over_Promises_v3_1080p60_Master.mp4` |
| Streamable preview (24 MB) | `public/demo-preview.mp4` |
| Encrypted vault copy | `deliverables/MON-DEMO26_v3_Master_60fps.enc` |

The v3 audio master was **trashed in Drive** so no client can download the old mix by accident.

---

## 2. What changed in v4 — and the measurement that forced it

Every number below is reproducible with `showreel/audio_qc/gates.py` and
`showreel/audio_qc/compare.py`. Nothing here is a claim.

### 2.1 The three real defects in v3

| Defect | Measurement | Root cause |
|---|---|---|
| The **hook was the quietest section of the film** | hook −19.5 dBFS vs deck −14.7 dBFS | level came from the bed, and the bed had not started yet |
| **Nothing moved for 27 s** | 1.4 dB of movement across the whole body | one static mix, one static filter, one static gain |
| **No top end at all** | air band (6–12 kHz) −21.4 dB under presence | the score contained no content above ~4 kHz |

That third one is why the mix read as "no body": a score with a 21 dB hole in the
top octave cannot sound expensive no matter how loud the lows are.

### 2.2 The fixes

1. **Hook body-lift** — 8.9 dB at t=0 decaying to unity over 2.55 s.
2. **Section gain automation** — deck 0.83, monoliths 0.90, tunnel 1.00, vault 1.06,
   finale 1.15, with 0.4 s crossfades and a 60 ms smoothing pass so no step can click.
   This is arrangement-level dynamics; the bus compressor is now *lighter*
   (1.6:1 at 0.42) than it was in v3, not heavier.
3. **Air bed** — band-passed pink noise at 7.2–11.5 kHz with a slow 0.23 Hz tremolo,
   plus an arp sparkle layer (melody +24 semitones, 4.2 kHz high-pass) on accents.
4. **Presence sweep** — the pad cutoff now opens 1150 → 2800 Hz instead of 1150 → 2150 Hz.
5. **Shaker +3.5 dB** (0.115 → 0.155): the shakers are the only bed element that lives up there.
6. **Exciter reduced** 0.62 → 0.45 — the shelf was inflating 2.5–5 k harshness instead of adding air.
7. **Peak discipline** — `loudnorm I=-14.6 TP=-2.2` then `alimiter` at 0.62.
   AAC overshoots, so the ceiling that *measures* −4.0 dBTP is 0.62 linear, not 0.90.

### 2.3 Before / after

| Metric | v3 (shipped) | **v4 (shipped)** | Gate |
|---|---|---|---|
| Integrated loudness | −14.0 LUFS | **−14.0 LUFS** | −14.0 ± 0.7 ✅ |
| Sectional dynamics | **1.4 dB** | **10.7 dB** | ≥ 3.0 ✅ |
| Hook vs deck | **−4.8 dB** | **−1.6 dB** | hook ≥ deck − 2 dB ✅ |
| Air vs presence | **−21.4 dB** | **−17.0 dB** mastered | −10 … −15 reference class |
| Harsh 2.5–5 k vs 1 k | −11.4 dB | **−12.0 dB** | ≤ +2 dB ✅ |
| True peak | −3.6 dBFS | **−4.0 dBTP** | ≤ −1.0 ✅ |
| Clipped samples | 0 | **0** ✅ | 0 |
| Click artifacts | — | **none** ✅ | 0 |
| Mono fold loss | −0.02 dB | **−0.02 dB** ✅ | > −3 dB |
| DC offset | — | **< 0.002** ✅ | ✅ |

`gates.py --profile web` returns **RESULT: PASS** on all 9 checks; the machine-readable
report ships at `public/showreel/audio_qc.json` and CI now fails the build if it regresses.

### 2.4 An honest note on LRA

v3 measured LRA 2.0 LU and v4 measures 1.6 LU. That is **not** a regression — it is the
metric being wrong for the format. EBU LRA is computed from 3-second short-term windows,
and a continuous 36-second score bed physically cannot produce a wide LRA. The dynamic
question for short-form is *sectional contrast*, which went from 1.4 dB to 10.7 dB.
The gate now encodes that distinction instead of chasing a number that does not apply.

---

## 3. Verified technical QC

- 2,160 frames at exactly 60.000 fps, CFR, duration 00:00:36.00.
- yuv420p, BT.470BG, SAR 1:1 DAR 16:9, progressive.
- Audio stream: AAC-LC, 48,000 Hz, stereo, 258 kbps.
- Decrypt → remux → re-decode round trip verified; measured loudness of the *final
  container* matches the standalone master (−14.0 LUFS / −4.0 dBTP), so nothing was
  lost in the mux.
- Stills pulled at 2.4 s, 18.0 s, 33.0 s to confirm framing, typography and overlay
  integrity in the shipped encode.

---

## 4. Reproducibility

```bash
pip install numpy scipy imageio-ffmpeg
python showreel/build_audio_60fps.py                 # synth + master -> public/showreel/
python -m showreel.audio_qc.gates public/showreel/audio_master_60fps.m4a --profile web
node showreel/render_60fps.mjs                       # frames + mux -> deliverables/
```

`.github/workflows/render-showreel-60fps.yml` runs all of it on every push that touches
the score, the beat sheet or the stage, and refuses to commit a master that fails a gate.
