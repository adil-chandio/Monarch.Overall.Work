---
name: monarch-reference-match
description: Measure a reference track against ours and get a numeric fix list — loudness, dynamics, density, and per-band movement per section. Use when someone says "the music isn't at the level" because it turns a taste argument into dB.
license: MIT
---

# monarch-reference-match

Taste is not measurable. The **gap to a reference** is.

You bring a track you think is right. The tool measures it, measures ours, and prints what to change — band by band, section by section. No adjectives.

```bash
python -m showreel.audio_qc.compare reference.mp3 ours.m4a --sections 8 --json gap.json
```

---

## 1. What it measures

| Dimension | Method | What it tells you |
|---|---|---|
| **Integrated loudness** | BS.1770-4 K-weighting, gated 400 ms blocks (channel power **summed**, G=1.0 per channel) | how loud it actually is |
| **LRA** | 10th/95th percentile of gated short-term loudness | how much the dynamics move |
| **Spectrum** | Welch PSD, 8 fixed bands, dB relative to total energy | which band the reference has that we do not |
| **Band movement** | STFT per band, normalised to each band's own mean, cut into N sections | *when* the reference moves and we sit still |
| **Onset density** | Hilbert envelope peak pick → events/second | how busy the arrangement is |
| **True peak** | sample peak of the decoded file | headroom |

Bands are fixed so two files always compare on the same grid:
`sub 20-60 · bass 60-120 · low_mid 120-250 · mid 250-500 · high_mid 500-1000 · presence 1000-2500 · harsh 2500-5000 · air 5000-12000`

---

## 2. Reading the report

```
LOUDNESS GAP : -2.40 LU   (negative = ours is quieter)
DYNAMICS GAP : -3.10 LU   (negative = ours is flatter)
DENSITY GAP  : -2.60 onsets/s  (negative = ours is emptier)
```

- **Loudness gap** — fix in the master (`loudnorm I`), never by raising every stem.
- **Dynamics gap** — fix in the arrangement. Section gains and stem entries/exits, not a compressor.
- **Density gap** — count notes/events. If the reference has 9/s and we have 6/s, adding a counter-melody or doubling the shaker is the fix, not a new instrument.

Then the band table:

```
      sub: +1.20
     bass: +0.80
  low_mid: +3.40   <-- fix
      mid: +0.20
 high_mid: -0.40
 presence: -1.10
    harsh: -0.90
      air: -6.50   <-- fix
```

Anything ≥ ±2.5 dB is a real difference; ±1 dB is noise across two different recordings.

Finally the **section grid** shows whether the reference builds where ours is flat. A row of near-zeros across sections 1–6 means our arrangement never changes; that is the single most common cause of "it sounds like a loop".

---

## 3. The fix order (never skip a step)

1. **Density** — is the arrangement as busy as the reference? Add/remove events first; nothing else matters while the part count is wrong.
2. **Movement** — do the sections go anywhere? Section gains, stem entries, filter opening over time.
3. **Bands** — correct the spectrum at stem level (thin the pluck, lift the air bed), not on the master bus.
4. **Loudness** — only now set `loudnorm` to the target.
5. **Peak** — limiter ceiling last, and re-measure after AAC because the encoder overshoots.

Master EQ is ±1.5 dB maximum. Anything bigger is a mix problem wearing a master's clothes.

---

## 4. Real example: MONARCH v3 → v4

| Metric | v3 | v4 | Reference-class target |
|---|---|---|---|
| Integrated | −14.0 LUFS | −14.0 LUFS | −14.0 |
| LRA | **2.0 LU** | **1.6 LU** | 2–6 for a 36 s score |
| Sectional movement | **~1.4 dB** | **10.7 dB** | ≥ 6 dB |
| Hook vs body | **−4.8 dB** (quietest part was the hook) | **−1.6 dB** | hook ≥ body − 2 dB |
| Air band vs presence | **−21.4 dB** | **−17.0 dB** (full chain) | −10 to −15 dB |
| Harsh 2.5–5 k vs 1 k | −11.4 dB | −12.0 dB | ≤ +2 dB |

Findings that mattered more than any EQ move:
1. The **hook was the quietest section of the film** — fixed with a 2.55 s lift.
2. **Nothing moved for 30 seconds** — fixed with section gain automation (0.4 s crossfades), not compression.
3. The top octave was **21 dB down** because the bed had no 6–12 kHz content at all — fixed with an air bed + arp sparkle layer.
4. The AAC encoder **overshoots ~1.5 dB**, so the limiter ceiling that lands −3.9 dBTP is ~0.62, not 0.90.

---

## 5. Honest limits

- A 36-second piece **cannot** have a wide EBU LRA: LRA is built from 3 s windows over a continuous score bed, so anything under ~60 s lands around 2 LU. Judge short-form dynamics by **sectional movement**, not LRA. (`showreel/audio_qc/gates.py` encodes this.)
- Two different recordings will always differ by ~1 dB per band. Chase ≥2.5 dB differences only.
- The tool cannot hear arrangement *taste* — it measures density, not whether the melody is good.
- Never match a reference's loudness if the reference is a phone-mic upload. Match a commercial master only.

---

## 6. Files

| Purpose | Path |
|---|---|
| Measurement core | `showreel/audio_qc/core.py` |
| Reference compare + report | `showreel/audio_qc/compare.py` |
| Delivery gates | `showreel/audio_qc/gates.py` |
| Machine-readable result | `public/showreel/audio_qc.json` |
| CI step | `.github/workflows/render-showreel-60fps.yml` → "Audio delivery gates" |
