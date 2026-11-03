---
name: monarch-sfx-library
description: Source, synthesise, licence-check and catalogue a reusable SFX library with a machine-readable manifest — SHA-256, licence URL, author, duration, attack/tail, spectral profile. Use when building a house sound kit so cues stop being re-invented per project.
license: MIT
---

# monarch-sfx-library

A sound effect is only reusable if you can prove where it came from and what it measures. This skill builds `sfx/` as **data**, not a folder of mystery wavs.

---

## 1. Folder contract

```
sfx/
├── manifest.json            # the truth: one row per file
├── ui/                      # clicks, thocks, taps, swipes
├── transition/              # whooshes, risers, reverse swells
├── impact/                  # booms, hits, sub drops
├── ambience/                # rooms, air, city, hall
├── musical/                 # stings, chimes, plucks (in-key sets)
└── _raw/                    # untouched download, never referenced directly
```

---

## 2. The manifest row (required fields)

```json
{
  "id": "sfx-ui-thock-001",
  "file": "ui/thock_001.wav",
  "source": "synth",                     // synth | freesound | zzfx | recorded
  "url": "",                              // required when source != synth
  "author": "",
  "license": "CC0",                      // CC0 | CC-BY | MIT | own
  "license_url": "",
  "sha256": "…",
  "downloaded_at": "2026-11-03T06:00:00Z",
  "duration_s": 0.14,
  "sample_rate": 48000,
  "channels": 1,
  "peak_dbfs": -6.1,
  "attack_ms": 2,
  "tail_ms": 120,
  "spectral_centre_hz": 780,
  "band_energy": { "low": 0.31, "mid": 0.62, "high": 0.07 },
  "harsh": false,                        // 2.5–5 kHz > +2 dB over 1 kHz
  "tags": ["ui", "warm", "no-high-click"],
  "changes": ""
}
```

If a field is unknown, keep it `null`. **Never invent a value** — a missing field is honest, a guessed one is a defect.

---

## 3. Sourcing protocol

### 3a. Synthesise first
Most cues in a product film are yours: clicks, thocks, whooshes, risers, sub-booms, ticks, shimmers. See `skills/monarch-video-lab/sound-design` for the generators. Advantages: licence-free, deterministic, tweakable per project.

### 3b. ZzFX for tiny UI cues
`skills/zzfx` gives you one-line procedural sounds. Good for notification, tick, pop. Render offline with node to a wav so it is deterministic:

```js
import { zzfx } from '../zzfx/ZzFX.js';
const samples = zzfx(0.05, 0.05, 1200, 0.02, 0.1, 0.2); // params: vol, randomness, freq, attack, sustain, release
```

### 3c. Freesound when reality is required
Follow the shotcraft flow (`skills/video-shotcraft/references/sfx-sourcing.md`):
1. Describe the **source**: `paper slide`, `felt thock`, `door latch`, not "cinematic whoosh".
2. Filter duration/attack before comparing.
3. Licence gate: **CC0 default**, CC-BY only with attribution recorded and delivered.
4. Reject: NC, Sampling+, unknown, "personal use only", anything without a licence URL.
5. Download to `_raw/`, hash it, copy to the correct family folder, record the row.

**Never** accept an HTML error page as audio — check the file's magic bytes (`RIFF`, `ID3`, `OggS`, `fLaC`).

---

## 4. Naming

```
<family>-<material>-<variant>-<nnn>
ui-thock-warm-001
transition-whoosh-silk-004
impact-boom-sub-002
musical-chime-glass-D-001        # include the key for musical cues
```

Lowercase, hyphens, three-digit counter. A file you cannot name is a file you will re-download.

---

## 5. Analysis pass (automated)

```python
import soundfile as sf, numpy as np, json, hashlib
x, sr = sf.read(path)
mono = x.mean(axis=1)
peak = 20*np.log10(np.abs(x).max() + 1e-12)
attack = np.argmax(np.abs(mono) > np.abs(mono).max()*0.9) / sr * 1000
spec = np.abs(np.fft.rfft(mono)); freqs = np.fft.rfftfreq(len(mono), 1/sr)
centre = float((spec*freqs).sum()/spec.sum())
band = lambda lo, hi: float(spec[(freqs>=lo)&(freqs<hi)].sum()/spec.sum())
harsh = (band(2500,5000) / max(band(900,1100), 1e-9)) > 1.25
```

Anything flagged `harsh: true` is either re-synthesised or re-EQ'd before it can enter a mix.

---

## 6. Rate limits (protects the edit)

- Max **1 SFX per 8 frames** in a 60 fps film.
- Never two impacts within 400 ms.
- No SFX under line-of-dialogue.
- Every cue must have a visual cause within 2 frames.

---

## 7. Acceptance checklist

- [ ] every row has a licence and a SHA-256
- [ ] no file over 6 MB in the library (long ambiences go to Drive, linked)
- [ ] every cue measured (duration, peak, centre, band energy)
- [ ] zero `harsh: true` among files used in a mix
- [ ] `manifest.json` validates (run `node scripts/validate-sfx.mjs` when it exists)
- [ ] attribution file generated for any CC-BY entry: `FREESOUND-CREDITS.md`
