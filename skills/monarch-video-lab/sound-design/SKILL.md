---
name: monarch-sound-design
description: Design and synthesise the sound bed for a MONARCH film — SFX cues, whooshes, impacts, UI foley, risers, sub-booms, ambience — with $0 budget, deterministic Python DSP, and a §-level mix discipline that keeps everything smooth and free of harshness. Use for any showreel, reel, ad, explainer, or faceless-channel video that needs cinematic feel without paid sample packs.
license: MIT
---

# monarch-sound-design

The house method for sound in MONARCH films. The default is original synthesis or clearly permissive sources; user-provided but uncleared sounds are a private-draft-only exception until rights are verified. Nothing depends on a paid API.

> **Lineage:** distilled from `storytold/filmcraft` (NLE-grade audio track discipline), `Vincentwei1021/video-shotcraft` §S1/S4 sfx-sourcing, `calesthio/OpenMontage` sound-effects/music orchestration, and the v3 showreel master (`showreel/build_audio_60fps.py`, 755 lines, −14.0 LUFS / −3.6 dBTP).

---

## 0. Non-negotiables

| Rule | Why |
|---|---|
| **No harsh bands.** 2.5–5 kHz peaks above +1.5 dB relative to 1 kHz will read as "irritating" on phone speakers. | The #1 complaint on AI-edged scores. |
| **Every SFX lands on a frame, not a timestamp guess.** | Frame-locked SFX is what makes motion feel connected to picture. |
| **One idea per cue.** A whoosh is a whoosh, not whoosh+click+riser. | Layered clutter is what people hear as "cheap". |
| **Sub is mono below ~120 Hz.** | Stereo sub cancels on phone speakers and phase-smears on headphones. |
| **A cue may be silent.** If a beat does not need sound, do not add sound. | Silence is the cheapest and most under-used effect. |

---

## 1. Cue sheet is a document, not a vibe

Before synthesising anything, write `beat_sheet.json`:

```json
{
  "fps": 60,
  "total_frames": 2160,
  "bpm": 125.0,
  "seams": { "hook_click": 148, "crash_zoom": 516, "finale": 1800 },
  "cues": [
    { "id": "c01", "frame": 148, "type": "ui_click", "source": "synth", "target_lufs": -22, "notes": "warm thock, no high click" },
    { "id": "c02", "frame": 516, "type": "sub_boom", "source": "synth", "target_lufs": -16, "notes": "36.7 Hz, 1.2 s decay" }
  ]
}
```

Then generate — never "add some whooshes".

### Selection protocol (from shotcraft §1, generalised)
1. Describe the **source material**, not the emotion: `paper slide`, `felt thock`, `glass chime`, not `epic whoosh`.
2. Filter by **duration** and **attack/tail** before comparing anything else.
3. Prefer **single-action recordings**; a multi-action take you must cut up is a defect.
4. Rank by match first. Ratings only break ties. Never invent a rating.
5. Record **licence + URL + SHA-256** in `audio-manifest.json` at download time, not later.

---

## 2. The eight cue families (and how to synthesise each)

All snippets assume `numpy` + `scipy.signal`, 48 kHz, float32 in −1..1.

### 2.1 Whoosh — formant-filtered pink noise
```python
def silk_whoosh(dur=0.42, f_start=380, f_end=2400, gain=0.46):
    n = int(dur * SR); t = np.linspace(0, 1, n)
    noise = pink_noise(n)                       # 1/sqrt(f) shaped
    env = np.sin(np.pi * t) ** 2.2              # zero at both ends, no click
    # automatable band-pass: sweep the centre, keep the Q gentle
    out = np.zeros(n)
    chunk = 256
    for i in range(0, n, chunk):
        f = f_start + (f_end - f_start) * (i / n) ** 1.6
        seg = noise[i:i + chunk]
        out[i:i + chunk] = bpf(seg, f / 2.2, f * 2.2, order=2)
    return normalise(out * env) * gain
```
Rules: attack ≥ 20 ms, tail ≥ 120 ms, no band above 6 kHz louder than −18 dB.

### 2.2 Impact / sub-boom
Pitch-swept sine, not a kick sample.
```python
def cinema_sub_boom(dur=1.25, root_hz=36.71, gain=0.68):
    n = int(dur * SR); t = np.arange(n) / SR
    f = root_hz * (1 + 1.4 * np.exp(-t * 18))
    phase = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(phase) * np.exp(-t * 2.6)
    thud = bpf(pink_noise(n), 90, 240, 2) * np.exp(-t * 26) * 0.18
    return normalise(body + thud) * gain
```
Always high-pass the rest of the mix at 30 Hz so the boom is the only thing down there.

### 2.3 UI click / thock (the "product feel" cue)
Two layers: a warm wooden body + a damped keycap tap.
```python
def thock_click(gain=0.44):
    n = int(0.14 * SR); t = np.arange(n) / SR
    body = np.sin(2*np.pi*155*t) * np.exp(-t*38)
    cap  = np.sin(2*np.pi*820*t) * np.exp(-t*110) * 0.45
    return normalise(body + cap) * gain
```
Never add a 3–4 kHz "tick" — that is exactly the sound people call cheap and irritating.

### 2.4 Riser / tension
Noise + rising resonant filter + slow pitch-up sine, then **cut** at the drop frame.
```python
# envelope must reach zero 1 frame before the impact, not on it
env = np.linspace(0, 1, n) ** 2
env[-int(0.012*SR):] = 0
```

### 2.5 Musical sting (in-key, so it never fights the score)
```python
def felt_glass_pluck(midi, dur=0.55, vel=0.8):
    f = midi_to_hz(midi)
    n = int(dur * SR); t = np.arange(n) / SR
    att = 1 - np.exp(-t / 0.004)          # 4 ms felt attack
    body = np.sin(2*np.pi*f*t) * np.exp(-t*3.2)
    bell = np.sin(2*np.pi*f*2.01*t) * np.exp(-t*7) * 0.22
    return normalise(body + bell) * att * vel
```
Carry the film's key. A sting outside the scale sounds like an error.

### 2.6 Ambience bed
Loopable noise, low-passed and slowly modulated. Keep it ≥ −34 LUFS under dialogue and duck it by 3 dB under every impact.

### 2.7 Transition "seam" sounds
One direction per seam. A whoosh that goes out must land somewhere; a reverse-swell must resolve on the cut. **Never both.**

### 2.8 Silence + room tone
Every cut is not a sound. Leave 2–4 frames of pure room tone before big hits so the hit has contrast.

---

## 3. Free sound libraries (licence-checked)

| Source | Licence | Notes |
|---|---|---|
| **Freesound** | CC0 preferred, CC BY acceptable | Use the shotcraft `sfx-source.py` flow; record author + licence URL + hash |
| **ZzFX** (`skills/zzfx`) | MIT | Procedural JS sound generator — great for UI/notification cues, zero assets |
| **BBC Sound Effects** | RemArc licence — **not** for commercial client work without checking | research only |
| **zapsplat / pixabay / mixkit** | free tiers exist but terms vary | verify per file, log it |
| **Self-synthesised** | yours | the default; this skill is mostly about making it yourself |

**Banned for commercial delivery:** anything marked NC, Sampling+, unknown, or "free for personal use".

---

## 4. Mix discipline

```
1. Gain-stage to −18 dBFS RMS per cue before any processing.
2. High-pass everything except sub/boom at 30–40 Hz (12 dB/oct).
3. Cut, don't boost: if it is muddy, notch 200–400 Hz by 2–3 dB.
4. De-ess the mid-high: dynamic EQ dip of 2 dB at 3.2 kHz at every transient.
5. Bus structure: SFX bus → glue comp (2:1, 3 dB GR) → hall reverb send (0.22 wet).
6. Sidechain music −2.5 dB under every impact, 80 ms attack, 220 ms release.
7. Master: loudnorm to the target below, then a limiter with `level=false`.
```

### Loudness targets

| Deliverable | Integrated | True peak | Notes |
|---|---|---|---|
| YouTube / web master | **−14.0 LUFS** | ≤ −1.0 dBTP | platform ceiling |
| Broadcast / client TV | −23.0 LUFS | ≤ −1.0 dBTP | EBU R128 |
| Reels / Shorts / TikTok | −14.0 LUFS | ≤ −1.0 dBTP | same as web; phone speakers need the mid-band intact |
| Cinema / showreel | −18.0 LUFS | ≤ −2.0 dBTP | more headroom for subs |

**Never** run `loudnorm` without `,aresample=48000,alimiter=limit=0.64:level=false` after it (it upsamples to 192 kHz).

---

## 5. QC gate (run before any render)

```bash
# 1. loudness + true peak
ffmpeg -i master.wav -af ebur128=peak=true -f null - 2>&1 | tail -12

# 2. harshness check — spectral balance per band
python3 - <<'PY'
import numpy as np, soundfile as sf
x, sr = sf.read('master.wav'); x = x.mean(axis=1) if x.ndim > 1 else x
f, p = np.fft.rfft(x), None
PY

# 3. click detector — any sample-to-sample jump over 0.3 in 1 ms
# 4. phase check — mono compatibility at 100 Hz
```

Reject the render if:
- any band 2.5–5 kHz exceeds the 1 kHz band by **+2 dB** while normalised,
- true peak above target,
- any click larger than 0.3 FS in < 1 ms,
- mono fold-down loses more than 3 dB of the 60–150 Hz region.

---

## 6. Anti-patterns (learned the hard way)

- **Reese sub + stereo widening** → cancels. Keep sub mono.
- **Pink-noise "air" shelf alone** never lifts 3–8 kHz; you need a harmonic exciter + coherent bells.
- **Full-frame reverb on everything** = wash. Send only, 0.2–0.35.
- **SFX on every cut** = noise. Keep to at most one foreground accent per 8 frames. Closely spaced low-level texture is allowed only when it follows a visible motion cluster and stays tucked under dialogue; never pad a placement target with arbitrary hits.
- **A 20-minute reverb IR** on a 36-second film smears the transients that create the impact.
- **Loudness war** — pushing to −9 LUFS sounds louder for 3 seconds and worse forever.

---

## 7. References in this repo

- `showreel/build_audio_60fps.py` — the working 7-voice + foley engine (DSP helpers, velvet hall IR, exciter, FFT telemetry export)
- `skills/zzfx` — procedural one-liner SFX (MIT)
- `skills/pyloudnorm` — ITU-R BS.1770 loudness measurement (MIT)
- `skills/video-shotcraft/references/sfx-sourcing.md` — the sourcing protocol this file generalises
- `skills/openmontage/.agents/skills/sound-effects` — paid-API alternative (ElevenLabs), do not use on $0 projects

---

## 8. Repository-wide frame-synced SFX workflow

Use this for **every video build in every MONARCH space**, not only Monarch Cam or the animated-short style. The current user's standing preference is 100+ carefully timed SFX placements across a full video when the picture can support that density. A placement is not a unique source recording. Preserve pauses and silence; never hit a count by adding random ticks or putting a cue on every cut.

### Shared assets and licensing

- Canonical catalog: `production/audio-library/catalog.json`.
- Future user-provided assets: `production/audio-library/inbox/` (local-only; Git ignores audio/video payloads).
- Inventory new sources with `python3 tools/sfx_sync.py scan --root production/audio-library/inbox --output .cache/sfx-inbox-scan.json`. Scanning is not rights clearance or semantic audio review.
- For each asset, log provenance, precise source excerpt bounds, cue tags, vibe tags and rights status in the catalog. Never label a source as licensed because the user supplied it.
- The four current SFX demo reels are tagged `user_provided_unverified` and `private_review_only`. Use them only for private review with `--private-review`; do not commit their audio excerpts or release them publicly until rights are verified. A demo's visible label can guide audition/cue semantics but is not proof of what its audio contains.
- Add later user-provided sounds to this shared catalog so every space can use them. Existing project-specific stricter source-audio / rights rules take precedence; do not overwrite native-source-audio-only or intentional-silence requirements.

### Per-video cue/mix steps

1. Read the active project's shot/edit manifest, render constants and narration timing. Establish exact `fps`, total frames, motion/transition start and landing frames, visible actions, voice phrases, and the mood arc. Do not infer real-world foley for actions not shown.
2. Write a project-local cue sheet with one record per audible event: frame, visual action, effect family, intended vibe, cue ID (or tags for catalog matching), gain/ducking and any intentional-silence span. Cluster low-level tactile texture only around actual depicted motion.
3. Resolve and render the stem using the shared engine, e.g.:
   ```bash
python3 tools/sfx_sync.py render --catalog production/audio-library/catalog.json --events path/to/project/sfx-events.json --output path/to/project/audio/sfx.wav
```
   Add `--private-review` only for private drafts containing the current unverified user-provided reels. Frame starts are derived from integer video frames, not guessed wall-clock timestamps. Review the generated `*.resolved-cues.json` for source, rights, frame and trim evidence.
4. Mix SFX under VO with voice-reactive ducking; add music/ambience only when the visual/story arc benefits. Use the shared `mix` command or the project's existing calibrated mixer. Final mux must explicitly map the chosen video stream and finished audio stream so raw source/demo audio cannot leak through.
5. QC frame count/duration, cue density and exact frame starts, narration intelligibility, clipping/true peak, loudness, stereo/mono behavior, and the delivered AAC stream. Listen to the complete render when playback is available; technical checks alone are not creative acceptance. Keep source credits and rights status with the project.

The helper creates/reuses placement; it does **not** watch every render or perform semantic vision without a shot/event map. Repository-wide automatic use means every video workflow invokes this standard and supplies its actual shot events. “Perfect” sound remains subjective; report measured sync/QC honestly and let the user review the draft.
