---
name: monarch-mix-master
description: Measure, mix and master a film's audio to a delivery spec in Python — BS.1770 loudness, true peak, spectral balance, mono compatibility, click detection — with hard pass/fail gates. Use before delivering any master, and whenever someone says the audio "isn't at the level yet".
license: MIT
---

# monarch-mix-master

Objective audio QC. No opinions, numbers only. If the file passes, the conversation is over; if it fails, the failing band tells you what to change.

> **Lineage:** the v3 mastering chain (`loudnorm → aresample → alimiter`), `skills/pyloudnorm` (ITU-R BS.1770), `skills/video-shotcraft/references/final-review.md`, `skills/filmcraft` audio discipline.

---

## 0. The chain, in order, every time

```bash
ffmpeg -i mix.wav \
  -af "highpass=f=30:poles=2,\
       lowshelf=f=90:g=1.5,\
       equalizer=f=320:width_type=q:w=1.1:g=-1.5,\
       equalizer=f=3200:width_type=q:w=2.2:g=-1.2,\
       highshelf=f=11000:g=1.0,\
       loudnorm=I=-14:TP=-1.5:LRA=7,\
       aresample=48000,\
       alimiter=limit=0.66:level=false" \
  -c:a aac -b:a 256k master.m4a
```

Two non-negotiable details:
1. `loudnorm` **upsamples to 192 kHz**. Without `aresample=48000` the file ships at the wrong rate.
2. `alimiter` defaults to auto-levelling (`level=true`), which silently re-adds gain. Always `level=false`.

---

## 1. Measurement first

```python
# Loudness (BS.1770-4) — use the vendored pyloudnorm, not a guess
import pyloudnorm as pyln, soundfile as sf
x, sr = sf.read('master.wav')
meter = pyln.Meter(sr)
print('integrated LUFS:', meter.integrated_loudness(x))
print('loudness range:', meter.loudness_range(x))
```

```bash
# True peak + integrated, authoritative (EBU R128)
ffmpeg -i master.wav -af ebur128=peak=true -f null - 2>&1 | tail -14
```

```python
# Spectral balance — 8 bands, reference-normalised
bands = [(20,60),(60,120),(120,250),(250,500),(500,1000),(1000,2500),(2500,5000),(5000,12000)]
# target slope: each band roughly -1.5 dB relative to the one below it, ±2 dB tolerance
```

```python
# Mono compatibility — fold to mono, measure low-band loss
mono = x.mean(axis=1)
low_loss_db = 10*np.log10(energy(x[:,0], 60, 150) / energy(mono, 60, 150))
# reject if > 3 dB
```

```python
# Click detector
d = np.abs(np.diff(x, axis=0)).max(axis=1)
clicks = np.where(d > 0.3)[0]
# reject if any run of consecutive clicks exists (a single sample jump at a cut point is fine)
```

---

## 2. Pass/fail gates

| Gate | Threshold | Action on fail |
|---|---|---|
| Integrated loudness | target ±0.5 LU | adjust `loudnorm` I, re-render |
| True peak | ≤ target dBTP | lower limiter ceiling by 0.5 dB steps |
| LRA | 5–9 LU for a 36 s film | compress more / less |
| Band balance | each band within ±2 dB of the slope | fix in the mix, not the master |
| Mono low-band loss | ≤ 3 dB | collapse the sub to mono at source |
| Clicks | none | find the cue, add a 2 ms fade |
| DC offset | < 0.002 | high-pass at 20 Hz |

**Never** "fix" a failed band with a master EQ boost. Master EQ is ±1.5 dB maximum; anything bigger is a mix problem wearing a master's clothes.

---

## 3. Target table

| Deliverable | I | TP | LRA |
|---|---|---|---|
| Web / YouTube master | −14.0 LUFS | −1.0 dBTP | 7 |
| Reels / Shorts | −14.0 LUFS | −1.0 dBTP | 5 |
| Broadcast | −23.0 LUFS | −1.0 dBTP | 9 |
| Showreel / cinema | −18.0 LUFS | −2.0 dBTP | 9 |

Document the actual measured values in the delivery notes. The v3 master measured **−14.0 LUFS / −3.6 dBTP** and that is the number that appears on the client page — not a rounded-up claim.

---

## 4. Stem hygiene before mastering

Mastering cannot rescue a bad stem balance. Check each stem:

- **Sub** mono, low-passed at 135 Hz, no content above 200 Hz.
- **Pad** no content below 150 Hz (high-pass it) — otherwise it fights the sub.
- **Arp/pluck** high-passed at 300 Hz; if it sounds thin, add a body layer, not volume.
- **Drums** kick and sub must not both live at 50 Hz — pitch the kick to 45–55 Hz and let the sub own 30–45 Hz.
- **FX** high-passed at 200 Hz except booms.

Every stem bounced with **no master bus processing** so the master stage has clean input.

---

## 5. Reporting

Write `audio_qc.json` next to the master:

```json
{
  "file": "master.m4a",
  "integrated_lufs": -14.02,
  "true_peak_dbtp": -3.61,
  "lra_lu": 6.8,
  "band_slope_ok": true,
  "mono_low_loss_db": 0.4,
  "clicks": 0,
  "dc_offset": 0.0003,
  "pass": true,
  "measured_at": "2026-11-03T06:40:00Z"
}
```

This file is what the client portal reads. If it says `pass: false`, the master does not ship.

---

## 6. Common failures and their real cause

| Symptom | Real cause | Wrong fix |
|---|---|---|
| Sounds quiet next to other videos | LRA too wide, transients eating headroom | turning everything up (kills dynamics) |
| Sounds harsh | 2.5–5 kHz stack from plucks + exciter | master EQ cut (fix the arp) |
| Sounds small | no sub, no room, mix too centred | reverb on everything (makes it worse) |
| Pumps weirdly | sidechain release too short | removing the sidechain (loses the groove) |
| Distorts on phones | true peak over −1.0 dBTP after AAC encode | re-encode at higher bitrate, lower ceiling |
| Cuts click | missing 2 ms fade on a cue | limiter (cannot fix a click) |
