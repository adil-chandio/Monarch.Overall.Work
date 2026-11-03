---
name: monarch-music-score
description: Compose and synthesise original background music in Python — key, tempo, chord progression, arrangement arc, instrument design — so a film has a real score instead of a loop. Use when the brief says "the music isn't at the level" and the answer must be composed, not licensed.
license: MIT
---

# monarch-music-score

A score is a **structure**, not a texture. This skill is the order of decisions that makes a 36-second film feel scored rather than looped.

> **Lineage:** the v3 showreel engine (`showreel/build_audio_60fps.py` — 125 BPM, Dm9→B♭maj9→Gm9→A7sus(♭9)→Dmaj9 Picardy), plus arrangement patterns from `skills/openmontage/.agents/skills/music` and `music-to-video`.

---

## 0. Decide these before writing a note

| Decision | Default | Why |
|---|---|---|
| **Key** | D minor for drama, A minor for warmth, F minor for cinematic weight | minor keys carry tension without volume |
| **Tempo** | 90–125 BPM for scores, 120–140 for energy | must match the edit, not the vibe |
| **Form** | intro → build → lift → climax → resolve | a score without a lift is a loop |
| **Cadence** | end on a **Picardy third** (minor → parallel major) | the single cheapest emotional upgrade |
| **Length** | locked to `total_frames / fps`, with the last 1.5 s reserved for decay | never cut music mid-note |

Golden rule: **the picture decides the form.** Count the beats in the edit, pick a tempo where bar lines land on your seams.

```python
frames_per_bar = (60 / BPM) * 4 * FPS     # 125 BPM @ 60fps = 115.2 frames/bar
# choose BPM so that frames_per_bar divides the distance between your biggest seams
```

---

## 1. Harmony that always works

### The dependable minor progression
```
i9  →  VI maj9  →  iv9  →  V7sus(♭9)  →  I maj9  (Picardy)
Dm9 →  B♭maj9  →  Gm9  →  A7sus(♭9)  →  Dmaj9
```
- Each chord gets **8–9 beats** at 125 BPM (one bar).
- The final major chord is the whole trick: the audience does not know why the ending feels resolved.
- Alternative for longer pieces: add `III maj7` before `VI` for lift, or `iv → ♭VII → i` for a modal, folk weight.

### Voicing rules
1. Root + 3rd + 7th + 9th. Drop the 5th — it adds mud and nothing else.
2. Keep the top voice **smooth**: no leap larger than a 4th in the melody line.
3. Spread below C3 across at least an octave, or thin it to root+fifth.

---

## 2. Instrument design in Python

Each instrument is 15–40 lines. Design them in this order: **sub → body → air**, never the reverse.

```python
# A. Pad — 7 detuned voices per note, low-passed, slow attack
def pad_chord(midis, dur, cutoff=1350, gain=0.22, detune_cents=(-9,-5,-2,0,2,5,9)):
    voices = []
    for m in midis:
        for c in detune_cents:
            f = midi_to_hz(m) * 2 ** (c / 1200)
            voices.append(saw_bandlimited(f, dur, harmonics=6))
    sig = np.mean(voices, axis=0)
    sig = lpf(sig, cutoff, order=4)
    env = adsr(len(sig), a=0.35, d=0.4, s=0.75, r=0.9)   # slow attack = no click, no "stab"
    return normalise(sig * env) * gain
```

```python
# B. Pluck — Karplus-Strong or additive felt-glass
def karplus(f, dur, damp=0.996, bright=0.5):
    n = int(SR / f); buf = np.random.uniform(-1, 1, n)
    out = np.zeros(int(dur * SR))
    for i in range(len(out)):
        out[i] = buf[i % n]
        buf[i % n] = damp * bright * (buf[i % n] + buf[(i + 1) % n])
    return out
```

```python
# C. Bass — mono, fundamental + one octave, nothing else
def reese_sub(midi, dur, gain=0.34):
    f = midi_to_hz(midi)
    t = np.arange(int(dur * SR)) / SR
    sig = np.sin(2*np.pi*f*t) + 0.35*np.sin(2*np.pi*f*2*t) + 0.12*np.sin(2*np.pi*f*3*t)
    return lpf(sig, 135, order=4) * gain
```

```python
# D. Percussion — synthesised, never sampled
kick   = pitch-swept sine 118→43 Hz, ~0.35 s, no click layer above 500 Hz
clap   = 3 micro-layers at 0/11/22 ms of band-passed noise, 1.2 kHz centre
shaker = band-passed pink noise 3–7 kHz, 40 ms decay, alternating accents
```

### The "premium" checklist for every instrument
- attack **never** < 3 ms unless it is percussion,
- no content below 30 Hz except sub/kick,
- no sustained tone above 9 kHz,
- every note ends with a release ≥ 120 ms (a hard stop is a click),
- detune is ±10 cents max — more and it reads as out of tune, not wide.

---

## 3. Arrangement arc (this is what people call "the level")

Map stems on/off to the picture beats:

| Section | Frames (36 s @ 60 fps) | Stems on |
|---|---|---|
| Hook | 0–148 | sub + one pad note + a single impact |
| Establish | 148–516 | + kick, + arp enters at 25% gain |
| Build | 516–1050 | + shaker, + second pad voice, arp to 60% |
| Lift | 1050–1428 | + clap, arp 100%, filter opens to 2.4 kHz |
| Climax | 1428–1800 | all stems, + counter-melody, + riser into the drop |
| Resolve | 1800–2160 | strip to pad + sub, Picardy chord, 1.5 s tail |

**Rule:** something must **enter or leave every 2–4 bars**. A stem list that never changes is what makes music sound like a bed instead of a score.

### Variations that upgrade a repeat
- arp: same notes, different octave or 3-against-2 rhythm
- pad: same chord, different voicing/inversion
- percussion: drop the kick for one bar before a lift (the "hole" makes the return bigger)
- melody: state → fragment → invert → return

---

## 4. Beat-to-frame mapping

Everything must agree on one grid:

```python
BEAT_S = 60 / BPM
def frame_of_beat(b): return round(b * BEAT_S * FPS)
def beat_of_frame(f): return f / FPS / BEAT_S
```

- Quantise every cue to `frame_of_beat(round(beat_of_frame(cue)))` — max 3-frame error, same rule as shotcraft.
- Export `beat_sheet.json` with `bpm`, `fps`, `frames_per_bar`, and every seam frame.
- The visual engine reads the **same** file, so the equaliser cannot drift from the music.

---

## 5. Export

```bash
# stems first, master second
ffmpeg -i mix.wav -af loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000,alimiter=limit=0.66:level=false \
       -c:a aac -b:a 256k audio_master.m4a
```

Deliver:
- `audio_master.m4a` (48 kHz stereo AAC, target loudness)
- `stems/` (pad, arp, sub, drums, fx) — so any future edit can rebalance without re-rendering
- `beat_sheet.json`
- `audio_reactive.json` — per-frame sub/mid/high envelopes + FFT bands for the visual engine

---

## 6. Reference and licensing

- **Never** ship a "royalty-free" track for a client without recording its licence text and URL in `audio-manifest.json`.
- **Never** use an AI music API on a $0 brief (ElevenLabs `music`, Suno, Udio). Costs money and produces unusable stems.
- Local generation options when a model is genuinely wanted: `YuE` (Apache-2.0), `ACE-Step` (see `skills/openmontage/.agents/skills/acestep`) — but they are 6–30 GB and belong in CI, not in this repo.
- The house default is **compose it in Python**. It is deterministic, free, frame-lockable, and stems are separable by construction.

---

## 7. Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| "Sounds like a loop" | no stem entry/exit, no form | add the arc from §3 |
| "Cheap / plasticky" | sawtooth with full harmonics, no filtering | band-limit to 6 harmonics, low-pass 1.2–2.4 kHz |
| "Muddy" | 5th in every voicing, too many voices low | drop the 5th, spread the low end |
| "Irritating" | 3–5 kHz build-up from stacked plucks | thin the arp, dip 3.2 kHz by 2 dB, de-ess transients |
| "Doesn't end" | cut mid-note | reserve 1.5 s decay, end on Picardy |
| "Drifts against picture" | tempo not derived from seam frames | solve BPM from the seams (§0) |
