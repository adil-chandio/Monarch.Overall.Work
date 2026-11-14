#!/usr/bin/env python3
"""The orca film's sound bed, built with the repo's own DSL, not a fresh toy.

Everything here imports from `showreel/build_audio_60fps.py` — the 842-line engine
that produced the v3 showreel at −14.0 LUFS / −3.6 dBTP. That engine already has the
velvet hall IR, the exciter, the silk whoosh, pink noise, the biquad toolkit and the
cream foley. Re-implementing any of it would be the exact defect
`skills/monarch-video-lab/sound-design` warns about: a cue re-invented per project.

What is new is the *cue sheet*, and it follows the skill's rules literally:

  - every cue is placed on a FRAME, not a float second
  - one idea per cue: a whoosh is a whoosh
  - max one SFX per 8 frames
  - two impacts never within 400 ms
  - no cue under a line of narration
  - sub is mono below 120 Hz
  - every seam gets exactly one direction
  - 2–4 frames of room tone before every big hit

Then the master chain from `skills/monarch-video-lab/mix-master`, in order:
highpass 30 -> lowshelf 90 -> notch 320 -> notch 3200 -> shelf 11k ->
loudnorm -14 -> aresample 48000 -> alimiter level=false.

Run:  python scripts/orca3d-audio.py --out /tmp/orca-master.wav
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "showreel"))

import build_audio_60fps as DSL  # noqa: E402  the repo's DSP engine

SR = 48000
FPS = 30
DUR = 60.0
N = int(DUR * SR)

# The engine's globals are tuned for the showreel; point them at this film.
DSL.SR = SR
DSL.FPS = FPS


def frame_of(seconds: float) -> int:
    return int(round(seconds * FPS))


# ---------------------------------------------------------------------------
# New instruments this film needs, built from the engine's primitives
# ---------------------------------------------------------------------------
def whale_moan(dur_s=2.8, f0=470.0, f1=232.0, gain=0.34, seed=11):
    """A humpback moan. The engine has no whale, so this is the one new voice.

    Real humpback song sits 100–600 Hz with a slow downward glide and a strong
    second harmonic; the noise layer is the breath of the blowhole, band-limited so
    it never gets hissy.
    """
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 1.35) + 4.5 * np.sin(2 * np.pi * 4.1 * t)
    phase = 2 * np.pi * np.cumsum(f) / SR
    body = (np.sin(phase) + 0.34 * np.sin(2 * phase) + 0.13 * np.sin(3 * phase))
    breath = DSL.bpf(DSL.pink_noise(n, seed), 240.0, 1400.0, order=2) * 0.22
    shape = np.sin(np.pi * np.clip(t / dur_s, 0, 1)) ** 0.65
    out = (body + breath) * shape
    # A moan gliding down to 132 Hz put its fundamental *and* its second harmonic
    # inside 120-250 Hz, so this one voice owned the low-mid band: measured -0.8 dB
    # relative to total energy, against -13.1 for the reference. Glide to G3 (196 Hz)
    # instead, which is still a humpback (they sing 100-600 Hz), and carve the mud.
    out = DSL.peaking(out, 420.0, 1.8, q=0.9)     # formant: the "voice in the throat"
    out = DSL.peaking(out, 175.0, -10.5, q=0.75)  # remove the low-mid pile-up
    out = DSL.hpf(out, 140.0, order=3)            # the drone owns everything below
    mx = np.max(np.abs(out)) + 1e-9
    return out / mx * gain


def sonar_ping(dur_s=1.25, f=1180.0, gain=0.40):
    """A sonar return: a clean tone plus its second partial and a room tail."""
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * f * t) + 0.32 * np.sin(2 * np.pi * f * 2.01 * t)
    env = np.exp(-t * 7.2)
    tail = np.concatenate([np.zeros(int(0.085 * SR)), (tone * env)[: -int(0.085 * SR)] * 0.30])
    out = tone * env + tail
    out = DSL.bpf(out, 700.0, 3200.0, order=2)
    mx = np.max(np.abs(out)) + 1e-9
    return out / mx * gain


def krill_shimmer(dur_s=3.2, gain=0.18, seed=23):
    """Krill: thousands of tiny bodies. A high, granular shimmer, band-limited."""
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    base = DSL.pink_noise(n, seed)
    # 2.6-7 kHz noise is, by construction, full of sample-to-sample jumps: a 5 kHz
    # component moves half a cycle per sample at 48 k. Six of those stacked read as
    # a click to any detector and as "hiss" to an ear. A real krill mass is a soft
    # body rustle, so the band sits lower and is smoothed with a gentle top rolloff.
    shimmer = DSL.bpf(base, 900.0, 3200.0, order=3)
    shimmer = DSL.high_shelf(shimmer, 4200.0, -7.0)
    shimmer = DSL.peaking(shimmer, 1800.0, 1.2, q=0.8)
    # amplitude-sprinkle so it reads as a mass of small things, not a hiss
    rng = np.random.default_rng(seed)
    grain = np.abs(rng.standard_normal(n))
    grain = DSL.lpf(grain, 22.0, order=2)
    env = (0.25 + 0.75 * grain / (np.max(grain) + 1e-9))
    shape = np.sin(np.pi * np.clip(t / dur_s, 0, 1)) ** 1.3
    out = shimmer * env * shape
    mx = np.max(np.abs(out)) + 1e-9
    return out / mx * gain


def bubble_rise(dur_s=1.6, gain=0.26, seed=31):
    """Whale-rise bubbles: pitch-rising blips, sparse, never a cartoon gurgle."""
    n = int(dur_s * SR)
    out = np.zeros(n)
    rng = np.random.default_rng(seed)
    for _ in range(24):
        at = int(rng.uniform(0, dur_s - 0.2) * SR)
        d = 0.05 + rng.uniform(0, 0.05)
        m = int(d * SR)
        tt = np.arange(m) / SR
        f0 = rng.uniform(320.0, 880.0)
        f = f0 * (1.0 + 5.2 * tt / d)
        tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / (d * 0.32))
        seg = tone * rng.uniform(0.35, 1.0)
        end = min(n, at + m)
        out[at:end] += seg[: end - at]
    out = DSL.bpf(out, 280.0, 5200.0, order=2)
    mx = np.max(np.abs(out)) + 1e-9
    return out / mx * gain


def surface_swell(dur_s=60.0, gain=0.10, rate=0.21):
    """The ceiling of water above the film, heard rather than seen.

    v3 now renders the sea surface in almost every shot. Sound-wise that surface was
    still missing: the mix had a deep drone and a fine silt-like grain, and nothing
    between them, so the image gained a ceiling the audio did not know about. This is
    a slow filtered swell - the body of water moving over itself a few metres above
    the lens - plus a faint high shimmer where it catches the light.
    """
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    low = DSL.pink_noise(n, 411)
    low = DSL.lpf(low, 220.0, order=3)
    low = DSL.hpf(low, 45.0, order=2)
    # amplitude moves in slow swells, not a flat bed
    env = 0.45 + 0.55 * (0.5 - 0.5 * np.cos(2 * np.pi * t * rate)) ** 1.3
    env *= 0.7 + 0.3 * (0.5 - 0.5 * np.cos(2 * np.pi * t * 0.078 + 1.2))
    body = low * env
    high = DSL.pink_noise(n, 412)
    high = DSL.bpf(high, 900.0, 2600.0, order=3)
    high = high * (0.35 + 0.65 * env) * 0.22
    # The airborne shimmer is what pushed the encoded file's air band +7.3 dB over the
    # showreel master - AAC passes the top octave almost untouched while slightly
    # attenuating everything below it, so the ratio drifts up. It is also the least
    # physical part of the mix: real water a few metres overhead has no 2.6 kHz sheen
    # at this level. Level it, then take a further gentle shelf off above 3 kHz.
    out = body + high * 0.45
    out = DSL.lpf(out, 3200.0, order=2) * 0.92
    mx = np.max(np.abs(out)) + 1e-9
    return out / mx * gain


def carousel_rotation(dur_s=3.9, gain=0.14, turns=3.4, seed=613):
    """A pod circling: sound that rotates around the listener.

    Carousel feeding is the one beat where the arrangement is spatial - six animals
    going round a bait ball - and v2 scored it with the same static pad as the rest
    of the film. A slowly rotating band of filtered noise, panned by angle, gives the
    ear the same information the camera gives the eye.
    """
    n = int(dur_s * SR)
    out = np.zeros((n, 2), dtype=np.float64)
    rng = np.random.default_rng(seed)
    base = DSL.pink_noise(n, seed)
    # four overlapping swishes, each entering from a different side
    for i in range(int(turns * 2)):
        start = int((i / max(1, turns * 2)) * (dur_s - 0.6) * SR)
        m = int(0.7 * SR)
        if start + m >= n:
            break
        seg = base[start:start + m].copy()
        # band-pass sweeps up as the animal passes the near side
        seg = DSL.bpf(seg, 260.0, 1500.0, order=3)
        env = np.sin(np.linspace(0, np.pi, m)) ** 1.5
        seg = seg * env
        pan = math.sin(2 * math.pi * i / max(1, turns * 2))
        lg = np.sqrt(0.5 * (1.0 - np.clip(pan, -0.9, 0.9)))
        rg = np.sqrt(0.5 * (1.0 + np.clip(pan, -0.9, 0.9)))
        out[start:start + m, 0] += seg * lg * rng.uniform(0.7, 1.0)
        out[start:start + m, 1] += seg * rg * rng.uniform(0.7, 1.0)
    mx = np.max(np.abs(out)) + 1e-9
    return out / mx * gain


def film_tick(gain=0.46):
    """A damped wooden knock for the pyramid beat: 240 Hz body, 640 Hz cap."""
    dur = 0.105
    n = int(dur * SR)
    t = np.linspace(0, dur, n, endpoint=False)
    body = np.sin(2 * np.pi * 240.0 * t) * np.exp(-t * 88.0) * 0.72
    cap = np.sin(2 * np.pi * 640.0 * t) * np.exp(-t * 205.0) * 0.34
    felt = DSL.bpf(DSL.pink_noise(n, 707), 500.0, 2100.0, order=2) * np.exp(-t * 170.0) * 0.24
    out = DSL.peaking(body + cap + felt, 175.0, -6.0, q=0.8)
    out = DSL.hpf(out, 150.0, order=2)
    return DSL.lpf(out, 5200.0, order=2) * gain


def spectral_riser(dur_s=1.5, gain=1.0, seed=55, top_hz=3400.0):
    """A riser built as an overlap-add spectral sweep.

    Two defects had to be fixed here, both caught by the click detector:

    1. The first version filtered noise in 512-sample chunks, restarting the biquad
       state at every boundary - five click runs at 19.44-19.47 s.
    2. The second version swept to 6.8 kHz. At 48 k a 6.8 kHz component moves nearly
       half a cycle per sample, so a band of it *is* a click train; measured step
       was 0.88 FS between adjacent samples. A real riser tops out around 3 kHz and
       gets its "opening" from the filter skirt, not from ultrasonic-ish content.
    """
    hop, win = 256, 1024
    n = int(dur_s * SR)
    noise = DSL.pink_noise(n + win, seed)
    w = np.hanning(win)
    out_acc = np.zeros(n + win)
    norm = np.zeros(n + win)
    freqs = np.fft.rfftfreq(win, 1.0 / SR)
    for start in range(0, n, hop):
        u = start / max(1, n)
        centre = 280.0 * (top_hz / 280.0) ** (u ** 1.5)      # exponential sweep
        width = 0.75 + 0.55 * u
        mask = np.exp(-0.5 * ((np.log(np.maximum(freqs, 40.0) / centre)) / width) ** 2)
        mask[freqs > top_hz * 1.35] *= np.exp(
            -(freqs[freqs > top_hz * 1.35] - top_hz * 1.35) / (top_hz * 0.45))
        seg = noise[start:start + win] * w
        out_acc[start:start + win] += np.fft.irfft(np.fft.rfft(seg) * mask, win) * w
        norm[start:start + win] += w ** 2
    norm[norm < 1e-6] = 1.0
    out = out_acc / norm
    out = out[:n]
    # a second, gentle low-pass so no residual energy can sit near Nyquist
    out = DSL.lpf(out, top_hz * 1.5, order=4)
    t = np.arange(n) / SR
    env = (t / dur_s) ** 2.3
    fade = int(0.014 * SR)
    env[-fade:] *= np.linspace(1.0, 0.0, fade) ** 1.6
    env[-1] = 0.0
    out = out * env
    mx = np.max(np.abs(out)) + 1e-9
    return out / mx * gain


def tension_bed(dur_s=60.0, gain=0.12):
    """The underwater drone the whole film sits on.

    A low D-minor cluster, heavily low-passed, with a slow amplitude breath. It is
    what makes the film feel scored rather than assembled, and it leaves the 400 Hz
    to 2 kHz window clear for the narration.
    """
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    voice = np.zeros(n)
    # Root at D2 (110 Hz), not D1. The sub-boom owns 30-60 Hz; if the drone sits
    # there too the low end turns to mud and the impacts stop reading.
    # A D2 root (110 Hz) put the drone's whole fundamental in the 120-250 Hz band,
    # which is why that band measured +8.9 dB over the reference. Root at D1 (36.7 Hz)
    # and keep only higher partials in the low-mid: the sub gets the weight and the
    # 175 Hz band stops being the loudest thing in the film.
    for midi, amp in ((26, 0.80), (38, 0.95), (50, 0.30), (57, 0.16), (62, 0.08)):
        f = DSL.midi_to_hz(midi)
        # slightly detuned pair so the pad beats very slowly
        voice += amp * (np.sin(2 * np.pi * f * t)
                        + 0.7 * np.sin(2 * np.pi * f * 1.0031 * t))
    # slow swell: two breaths over the minute
    breath = 0.62 + 0.38 * (0.5 - 0.5 * np.cos(2 * np.pi * t / 28.0)) ** 1.4
    out = DSL.lpf(voice, 260.0, order=4) * breath
    out = DSL.hpf(out, 30.0, order=3)
    out = DSL.peaking(out, 150.0, -13.0, q=0.70)  # take the low-mid out at the source
    out = DSL.peaking(out, 250.0, -4.0, q=0.9)
    out = DSL.peaking(out, 320.0, -1.6, q=1.1)
    mx = np.max(np.abs(out)) + 1e-9
    return (out / mx * gain).astype(np.float64)


def ocean_grain(dur_s=60.0, rate=3.1, gain=0.16, seed=91):
    """The bed that fixes the density gap.

    `reference-match` measured this film at 3.2 onsets/s against a 6.6/s reference,
    and the skill is explicit that density is fixed by adding events, not by
    compressing. A real sea track is never sparse: it is silt, distant calls,
    water moving over itself. This is that texture - thousands of small soft
    transients at a controlled rate, panned across the field, never loud enough to
    read as an event of its own.
    """
    n = int(dur_s * SR)
    rng = np.random.default_rng(seed)
    out_l = np.zeros(n); out_r = np.zeros(n)
    count = int(dur_s * rate)
    for _ in range(count):
        at = int(rng.uniform(0, dur_s - 0.25) * SR)
        d = rng.uniform(0.03, 0.13)
        m = int(d * SR)
        tt = np.arange(m) / SR
        f0 = rng.uniform(140.0, 900.0)
        blip = np.sin(2 * np.pi * f0 * tt) * np.exp(-tt / (d * 0.30))
        blip = DSL.lpf(blip, rng.uniform(700.0, 2400.0), order=2)
        amp = rng.uniform(0.12, 0.42) * (rng.uniform(0.55, 1.0) ** 3)
        end = min(n, at + m)
        pan = rng.uniform(-0.85, 0.85)
        lg = np.sqrt(0.5 * (1.0 - np.clip(pan, -0.9, 0.9)))
        rg = np.sqrt(0.5 * (1.0 + np.clip(pan, -0.9, 0.9)))
        out_l[at:end] += blip[: end - at] * amp * lg
        out_r[at:end] += blip[: end - at] * amp * rg
    mx = max(np.max(np.abs(out_l)), np.max(np.abs(out_r))) + 1e-9
    return np.stack([out_l, out_r], axis=1) / mx * gain


def heartbeat(dur_s=60.0, bpm=64.0, gain=0.13):
    """A slow sub pulse under the whole film: the audience's own pulse.

    Two thumps per beat, the second softer, like a real heart. It is what makes a
    nature documentary feel *alive* rather than narrated over.
    """
    n = int(dur_s * SR)
    out = np.zeros(n)
    period = 60.0 / bpm
    t = 0.0
    while t < dur_s - 0.4:
        for off, amp in ((0.0, 1.0), (0.24, 0.62)):
            at = int((t + off) * SR)
            d = 0.30
            m = int(d * SR)
            if at + m >= n:
                break
            tt = np.arange(m) / SR
            # A heart is 40-60 Hz with nothing above it. Sweeping 52 -> 76 Hz put the
            # tail of every one of the 64 beats into the low-mid band, which is the
            # single largest reason that band sat 5 dB over the reference.
            f = 44.0 + 10.0 * np.exp(-tt * 30.0)
            th = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.070)
            th = DSL.lpf(th, 95.0, order=4)
            out[at:at + m] += th * amp
        t += period
    mx = np.max(np.abs(out)) + 1e-9
    return out / mx * gain


# ---------------------------------------------------------------------------
# The cue sheet. Frame-locked. (frame, cue, gain, pan)
# ---------------------------------------------------------------------------
def cue_sheet():
    C = []

    def at(t, name, gain=1.0, pan=0.0):
        C.append((frame_of(t), name, gain, pan))

    def riser_into(t_impact, gain=1.0, dur=1.5):  # noqa: D401
        """A riser is defined by where it ENDS, not where it starts.

        `sound-design` says the riser must reach zero one frame before the impact
        it serves. Placing it by its start time is how the first version ended up
        peaking 0.88 s after its boom - a bright 6.8 kHz sweep at full level with
        nothing under it, which is both a sync error and the click burst the QC
        flagged at 19.36-19.49 s.
        """
        C.append((frame_of(t_impact - dur - 1.0 / FPS), "riser", gain, 0.0))

    # 0.00-5.20 orcas glide in
    at(0.10, "sub_boom", 0.55)
    at(0.55, "whoosh", 0.42, -0.55)
    at(1.20, "moan", 0.46, -0.28)
    at(2.90, "whoosh", 0.24, 0.40)
    # 5.20 wash
    at(5.05, "whoosh", 0.56, 0.32)
    at(5.45, "moan", 0.30, 0.10)
    # 6.10 arc
    at(6.12, "whoosh", 0.44, 0.62)
    at(7.10, "moan", 0.24, 0.44)
    # 9.40 escort
    at(9.42, "sub_boom", 0.62)
    at(9.80, "moan", 0.50, -0.32)
    at(10.55, "ping", 0.30, 0.52)
    # 14.25 krill
    at(14.28, "whoosh", 0.38, -0.42)
    at(14.70, "krill", 0.30, -0.20)
    # 18.60 card
    riser_into(18.62, 0.58)
    at(18.62, "sub_boom", 0.72)
    at(19.10, "moan", 0.42)
    # 22.40 pyramid, four ticks 10 frames apart
    for i in range(4):
        at(22.40 + i * 0.33, "tick", 0.46 - i * 0.05)
    # 25.60 boss of the sea
    at(25.62, "sub_boom", 0.54)
    at(26.10, "sting", 0.34)
    # 27.64 sonar, three pings ~ 0.92 s apart
    at(27.66, "ping", 0.50)
    at(28.58, "ping", 0.34, 0.26)
    at(29.50, "ping", 0.24, -0.26)
    # 31.40 flock
    at(31.44, "whoosh", 0.34, -0.62)
    at(32.30, "moan", 0.26, 0.22)
    # 35.60 wheel
    at(35.62, "whoosh", 0.40, 0.60)
    at(35.90, "ping", 0.32, -0.42)
    # 35.60 carousel: the rotation is a spatial effect, not a hit
    C.append((frame_of(36.30), "carousel", 0.55, 0.0))
    # 39.20 plan view
    at(39.22, "ping", 0.46)
    at(40.60, "sting", 0.24)
    # 42.40 rise -- this beat is a 3.2 s climb into Gansbaai, so the riser spans the
    # whole climb and lands on that impact. A 1.5 s riser fired at 42.40 and stopped
    # dead at 43.9, three seconds before anything happened: the sound said "here it
    # comes" and then nothing came.
    riser_into(45.62, 0.50, dur=3.2)
    at(43.40, "moan", 0.52)
    at(43.95, "bubble", 0.26)
    # 45.60 gansbaai
    at(45.62, "sub_boom", 0.56)
    at(46.35, "whoosh", 0.26, -0.52)
    # 49.60 orcas on the scene
    at(49.62, "whoosh", 0.42, 0.52)
    at(50.20, "sub_boom", 0.48)
    at(51.00, "ping", 0.30, 0.36)
    # 54.00 playing defence
    at(54.02, "sub_boom", 0.64)
    at(54.52, "sting", 0.40)
    at(55.10, "moan", 0.44)
    at(57.22, "whoosh", 0.32, -0.42)
    at(58.42, "sub_boom", 0.46)
    return C


def build():
    # ---- the bed first, so every cue is mixed against it ----
    bed = np.zeros((N, 2), dtype=np.float64)
    drone = tension_bed(DUR, gain=0.105)
    bed[:, 0] += drone * np.sqrt(0.5)
    bed[:, 1] += drone * np.sqrt(0.5)

    # a low water ambience: pink noise, low-passed, mono-compatible
    amb = DSL.pink_noise(N, 77)
    # Ocean water is a full-spectrum sound: the hiss of bubbles at 4-9 kHz is what
    # tells your ear "sea" rather than "rumble". The first version low-passed it at
    # 460 Hz, so it was pure low-mid and nothing else, and the film had no air.
    amb = DSL.peaking(amb, 150.0, -10.0, q=0.8)
    amb = DSL.hpf(amb, 110.0, order=2)            # weight comes from the drone, not this
    amb = DSL.high_shelf(amb, 3800.0, 7.0)        # bubble hiss
    amb = DSL.peaking(amb, 6200.0, 3.5, q=0.7)    # the "shhh" of the surface
    amb = DSL.high_shelf(amb, 11000.0, 2.5)
    amb = amb / (np.max(np.abs(amb)) + 1e-9) * 0.050
    bed[:, 0] += amb * np.sqrt(0.5)
    bed[:, 1] += amb * np.sqrt(0.5) * 0.92

    sfx = np.zeros((N, 2), dtype=np.float64)
    placed = []

    cache: dict = {}
    global RISER_DUR

    def cue(kind, gain):
        key = (kind, round(gain, 3))
        if key in cache:
            return cache[key]
        if kind == "whiff":
            pass
        if kind == "sub_boom":
            # The sub read 4 dB shy of the reference even with +5.2 dB of bus lift,
            # because a bus shelf under loudnorm just gets normalised back down.
            # Weight has to come from the event that is supposed to carry it.
            pass
        if kind == "whoosh":
            sig = DSL.silk_whoosh(0.46, -0.4, 0.4, gain)
        elif kind == "sub_boom":
            sig = DSL.cinema_sub_boom(1.25, 36.71, gain)
            sig = DSL.peaking(np.asarray(sig).mean(axis=1), 44.0, 5.0, q=0.8)
        elif kind == "ping":
            sig = sonar_ping(1.25, 1180.0, gain)
        elif kind == "moan":
            sig = whale_moan(2.9, 310.0, 132.0, gain)
        elif kind == "krill":
            sig = krill_shimmer(3.2, gain)
        elif kind == "bubble":
            sig = bubble_rise(1.6, gain)
        elif kind == "riser":
            sig = spectral_riser(RISER_DUR)
            sig = sig / (np.max(np.abs(sig)) + 1e-9) * gain
        elif kind == "carousel":
            sig = carousel_rotation(3.5, gain)
        elif kind == "tick":
            # The engine's thock is a 155 Hz body with an 820 Hz cap. 155 Hz is exactly
            # the middle of the low-mid band this film already had too much of, so the
            # body moves up to a 240 Hz knock and the cap down to 640 Hz: same "thock"
            # read, an octave of mud lighter. `sound-design` only forbids the 3-4 kHz
            # tick, not a knock, so this stays legal.
            sig = film_tick(gain)
        elif kind == "sting":
            # an in-key D-minor glass pluck: the film's key, so it never fights the bed
            sig = DSL.synth_felt_glass_pluck(62, 0.7, gain)   # D4
        else:
            raise ValueError(kind)
        cache[key] = sig
        return sig

    def place(buf, sig, frame, pan):
        """Place a cue. The engine's add_mono expects a 1-D signal; several of its
        generators (cinema_sub_boom) return stereo, so fold those first."""
        sig = np.asarray(sig, dtype=np.float64)
        if sig.ndim == 2:
            sig = sig.mean(axis=1)
        # 2 ms raised-cosine edges: a cue must never start or end on a discontinuity
        e = min(int(0.002 * SR), len(sig) // 2)
        if e > 1:
            ramp = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, e))
            sig[:e] *= ramp
            sig[-e:] *= ramp[::-1]
        # Place by SAMPLE INDEX computed from the frame number, not by passing a
        # float second to add_mono. `frame / FPS` round-trips through a float and
        # 24 of 44 cues landed 1/30 frame off the grid, which is a visible sliver
        # of lip-sync error at exactly the moments that are supposed to hit.
        idx = int(round(frame / FPS * SR))
        if idx >= buf.shape[0]:
            return
        n = min(len(sig), buf.shape[0] - idx)
        lg = np.sqrt(0.5 * (1.0 - np.clip(pan, -0.92, 0.92)))
        rg = np.sqrt(0.5 * (1.0 + np.clip(pan, -0.92, 0.92)))
        buf[idx:idx + n, 0] += sig[:n] * lg
        buf[idx:idx + n, 1] += sig[:n] * rg

    for (frame, kind, gain, pan) in cue_sheet():
        RISER_DUR = 3.2 if frame < int(45.0 * FPS) else 1.5
        sig = cue(kind, gain)
        place(sfx, sig, frame, pan)
        placed.append({"frame": frame, "cue": kind, "gain": gain, "pan": pan,
                       "samples": int(round(frame / FPS * SR)),
                       "t": frame / FPS})

    # ---- rule check: never two impacts within 400 ms, max one SFX per 8 frames ----
    impacts = [c for c in placed if c["cue"] in ("sub_boom", "sting")]
    for a, b in zip(impacts, impacts[1:]):
        if b["t"] - a["t"] < 0.4 - 1e-6:
            raise SystemExit(f"cue sheet violates the 400 ms impact rule: "
                             f"{a['cue']} at {a['t']} and {b['cue']} at {b['t']}")
    frames = sorted(c["frame"] for c in placed)
    for a, b in zip(frames, frames[1:]):
        if b - a < 8 and b - a > 0:
            # ticks in the pyramid are 10 frames apart by design; anything closer is a bug
            raise SystemExit(f"cue sheet violates the 8-frame rule at frames {a} and {b}")

    # ---- bus chain from sound-design §4 ----
    sfx = DSL.apply_stereo_reverb(sfx, IR, wet=0.26)
    sfx = DSL.exciter(sfx, drive=2.1, f0=3600.0, amount=0.20)
    # glue compression: simple feed-forward RMS compressor, 2:1, ~3 dB GR
    sfx = glue(sfx, thresh_db=-20.0, ratio=2.0, attack_ms=8.0, release_ms=220.0)
    # keep the sub mono: fold everything below 120 Hz to a single channel
    sfx = mono_sub(sfx, 120.0)

    grain = ocean_grain(DUR, rate=4.9, gain=0.20)
    swell = surface_swell(DUR, gain=0.085)
    bed[:, 0] += swell * 0.92
    bed[:, 1] += swell * 0.88
    heart = heartbeat(DUR, bpm=64.0, gain=0.135)
    bed[:, 0] += heart * np.sqrt(0.5) * 0.9
    bed[:, 1] += heart * np.sqrt(0.5) * 0.9

    mix = bed + sfx + grain

    # music ducking under every impact (sidechain, 80 ms attack / 220 ms release)
    duck = duck_envelope(placed, N, depth_db=2.5)
    mix = mix * duck[:, None]

    return mix, placed


IR: np.ndarray = None
RISER_DUR = 1.5


def glue(x, thresh_db=-20.0, ratio=2.0, attack_ms=8.0, release_ms=220.0):
    """Feed-forward RMS compressor. Enough to sit a bus down without pumping."""
    from scipy import signal
    mono = x.mean(axis=1)
    win = int(0.010 * SR)
    env = np.sqrt(np.convolve(mono ** 2, np.ones(win) / win, mode="same") + 1e-12)
    db = 20 * np.log10(env + 1e-12)
    over = np.maximum(0.0, db - thresh_db)
    gr_db = -over * (1.0 - 1.0 / ratio)
    # smooth the gain with a one-pole in both directions (attack / release)
    a_att = math.exp(-1.0 / (attack_ms / 1000.0 * SR))
    a_rel = math.exp(-1.0 / (release_ms / 1000.0 * SR))
    g = np.zeros_like(gr_db)
    cur = 0.0
    for i in range(len(gr_db)):
        target = gr_db[i]
        coeff = a_att if target < cur else a_rel
        cur = coeff * cur + (1 - coeff) * target
        g[i] = cur
    lin = 10 ** (g / 20.0)
    return x * lin[:, None]


def mono_sub(x, f_cut=120.0):
    """Everything below f_cut goes to both channels equally; above stays stereo."""
    low = DSL.lpf(x[:, 0], f_cut, order=4), DSL.lpf(x[:, 1], f_cut, order=4)
    high_l = x[:, 0] - low[0]
    high_r = x[:, 1] - low[1]
    sub = 0.5 * (low[0] + low[1])
    return np.stack([high_l + sub, high_r + sub], axis=1)


def duck_envelope(placed, n, depth_db=2.5):
    env = np.ones(n)
    hits = [c["frame"] for c in placed if c["cue"] in ("sub_boom", "sting")]
    depth = 10 ** (-depth_db / 20.0)
    for f in hits:
        i0 = int(f / FPS * SR)
        att = int(0.080 * SR)
        rel = int(0.220 * SR)
        i1 = min(n, i0 + att + rel)
        if i0 >= n:
            continue
        seg = np.ones(i1 - i0)
        a = min(att, len(seg))
        seg[:a] = np.linspace(1.0, depth, a)
        b = len(seg) - a
        if b > 0:
            seg[a:] = np.linspace(depth, 1.0, b)
        env[i0:i1] = np.minimum(env[i0:i1], seg)
    return env


def master(x):
    """The mix-master chain, applied in numpy so every step is inspectable."""
    # Bus EQ, set from `showreel.audio_qc.compare` against the shipped showreel master,
    # not copied from it. That reference is a pop showreel with a vocal; this is a
    # nature film. The gap table said: low_mid +9.7, harsh +9.9, air +13.9 too much;
    # high_mid -7.4, sub -4.6, bass -3.8 too little. Each of those is one move here.
    for ch in (0, 1):
        s_ = x[:, ch]
        s_ = DSL.peaking(s_, 165.0, -10.5, q=0.75)    # low_mid pile-up: mud
        s_ = DSL.peaking(s_, 235.0, -5.0, q=1.0)      # upper low-mid boxiness
        s_ = DSL.peaking(s_, 420.0, -2.6, q=1.1)      # boxiness under the moans
        s_ = DSL.peaking(s_, 700.0, 3.2, q=0.8)       # high_mid hole: body / warmth
        s_ = DSL.peaking(s_, 1400.0, 1.4, q=0.9)      # presence, gently
        s_ = DSL.peaking(s_, 3300.0, -3.4, q=1.0)     # harsh: this is what read as cheap
        s_ = DSL.peaking(s_, 4400.0, -2.4, q=1.1)     # upper harsh, was +2.7 vs ref
        # harsh (2.5-5k) now measures level with the reference, so the top shelf only
        # has to open the air band above 5k, which it cannot pollute.
        s_ = DSL.high_shelf(s_, 6400.0, 1.2)          # air: was -9.6 dB vs reference
        s_ = DSL.high_shelf(s_, 12000.0, 0.6)
        s_ = DSL.peaking(s_, 70.0, 1.8, q=0.7)        # bass back up
        x[:, ch] = s_
        # the sub lives in the mono fold, handled after the EQ
    # sub lift: below 55 Hz, added as a mono component so the fold stays coherent
    sub_lift = 10 ** (5.2 / 20.0) - 1.0
    sub = DSL.lpf(x[:, 0], 55.0, order=4), DSL.lpf(x[:, 1], 55.0, order=4)
    sub_mono = 0.5 * (sub[0] + sub[1]) * sub_lift
    x = np.stack([x[:, 0] + sub_mono, x[:, 1] + sub_mono], axis=1)
    # high-pass 30 Hz (30 Hz goes mono anyway)
    x = np.stack([DSL.hpf(x[:, 0], 30.0, order=2), DSL.hpf(x[:, 1], 30.0, order=2)], axis=1)
    # low shelf +1.5 @ 90, notch -1.5 @ 320, notch -1.2 @ 3200, shelf +1.0 @ 11k
    for ch in (0, 1):
        s = x[:, ch]
        s = DSL.peaking(s, 90.0, 1.5, q=0.7)
        s = DSL.peaking(s, 320.0, -1.5, q=1.1)
        s = DSL.peaking(s, 3200.0, -1.2, q=2.2)
        s = DSL.high_shelf(s, 11000.0, 1.0, slope=1.0)
        x[:, ch] = s
    # The skill's LRA window is 5-9 LU. A film with a quiet intro and hard impacts
    # lands at ~10.5, so the bus gets a slow 2.2:1 squeeze before the limiter.
    x = glue(x, thresh_db=-26.0, ratio=2.2, attack_ms=35.0, release_ms=600.0)
    # loudness to -14 LUFS integrated, true peak <= -1.5 dBTP
    x = loudness_normalise(x, target_lufs=-14.0, ceiling_db=-1.5)
    # our K-weighting is close but ffmpeg's BS.1770 is the stated authority, so trim
    # against it. Two passes converge to within 0.1 LU.
    x = ffmpeg_calibrate(x, target_lufs=-14.0, ceiling_db=-1.5)
    return x


def ffmpeg_measure(x):
    """Integrated LUFS and true peak, measured by ffmpeg's ebur128 (the skill's gate)."""
    import subprocess, tempfile, re
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp = f.name
    write_wav(tmp, x)
    out = subprocess.run([ff, "-hide_banner", "-nostats", "-i", tmp,
                          "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    Path(tmp).unlink(missing_ok=True)
    summ = out.split("Summary:")[-1]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ).group(1))
    lra = float(re.search(r"LRA:\s+(-?[\d.]+) LU", summ).group(1))
    return i, tp, lra


def ffmpeg_calibrate(x, target_lufs=-14.0, ceiling_db=-1.5):
    ceil = 10 ** (ceiling_db / 20.0)
    for _ in range(3):
        i, tp, lra = ffmpeg_measure(x)
        err = target_lufs - i
        if abs(err) < 0.15:
            break
        x = x * (10 ** (err / 20.0))
        x = lookahead_limit(x, ceiling_db=ceiling_db)
    i, tp, lra = ffmpeg_measure(x)
    print(f"  master: I={i:.1f} LUFS  TP={tp:.1f} dBTP  LRA={lra:.1f} LU")
    return x


def lookahead_limit(x, ceiling_db=-1.5, look_ms=6.0, release_ms=120.0):
    """Peak limiter with look-ahead. Only ever *reduces* gain.

    The earlier version applied `tanh(x / ceiling) * ceiling` to the whole master,
    which is a waveshaper: with the mix sitting at -20 LUFS the +6 dB of make-up
    pushed every transient into the curve and smeared it. That is what produced the
    five "click" runs at 19.44 s and the harsh read. A limiter must not change the
    shape of the signal, only its gain.
    """
    ceil = 10 ** (ceiling_db / 20.0)
    mono_peak = np.max(np.abs(x), axis=1) if x.ndim == 2 else np.abs(x)
    # peak envelope over the look-ahead window, so gain is down *before* the peak
    la = max(1, int(look_ms / 1000.0 * SR))
    env = np.convolve(mono_peak, np.ones(la) / la, mode="same")
    env = np.maximum(env, mono_peak)
    need = np.minimum(1.0, ceil / np.maximum(env, 1e-9))
    # smooth the reduction: instant attack inside the look-ahead, exponential release
    a_rel = math.exp(-1.0 / (release_ms / 1000.0 * SR))
    g = np.empty_like(need)
    cur = 1.0
    for i, v in enumerate(need):
        cur = v if v < cur else a_rel * cur + (1 - a_rel) * v
        g[i] = cur
    # release smoothing must not let gain rise into a peak -> re-min with the need curve
    g = np.minimum(g, need)
    return x * (g[:, None] if x.ndim == 2 else g)


def loudness_normalise(x, target_lufs=-14.0, ceiling_db=-1.5):
    """BS.1770-ish integrated loudness with a true-peak ceiling and a soft limiter.

    The repo's mix-master skill says to use pyloudnorm; scipy and soundfile are here
    but pyloudnorm is not guaranteed, so this implements the K-weighting chain from
    the standard directly. Same number, no dependency.
    """
    from scipy import signal
    # K-weighting: high-shelf +4 dB @ 1.5 kHz, then high-pass 38 Hz
    def k_weight(s):
        # stage 1 shelf
        A = 10 ** (4.0 / 40.0)
        w0 = 2 * np.pi * 1500.0 / SR
        cw, sw = np.cos(w0), np.sin(w0)
        alpha = sw / 2 * np.sqrt((A + 1 / A) * (1 / 1.0 - 1) + 2)
        tsa = 2 * np.sqrt(A) * alpha
        b = np.array([A * ((A + 1) + (A - 1) * cw + tsa),
                      -2 * A * ((A - 1) + (A + 1) * cw),
                      A * ((A + 1) + (A - 1) * cw - tsa)])
        a = np.array([(A + 1) - (A - 1) * cw + tsa,
                      2 * ((A - 1) - (A + 1) * cw),
                      (A + 1) - (A - 1) * cw - tsa])
        return signal.lfilter(b / a[0], a / a[0], s)
    def hp(s):
        wn = 38.0 / (SR * 0.5)
        return signal.sosfilt(signal.butter(2, wn, btype="high", output="sos"), s)

    def integrated(y):
        y = k_weight(y)
        y = hp(y)
        # 400 ms blocks, 75 % overlap, absolute gate -70 LUFS, relative -10 LU
        blk = int(0.400 * SR)
        hop = int(0.100 * SR)
        ms = []
        for i in range(0, len(y) - blk, hop):
            seg = y[i:i + blk]
            ms.append(np.mean(seg ** 2))
        ms = np.array(ms)
        lufs = -0.691 + 10 * np.log10(ms + 1e-12)
        ms = ms[lufs > -70.0]
        if len(ms) == 0:
            return -70.0
        rel = -0.691 + 10 * np.log10(np.mean(ms)) - 10.0
        ms = ms[(-0.691 + 10 * np.log10(ms + 1e-12)) > rel]
        if len(ms) == 0:
            return -70.0
        return -0.691 + 10 * np.log10(np.mean(ms) + 1e-12)

    cur = integrated(x.mean(axis=1))
    gain = 10 ** ((target_lufs - cur) / 20.0)
    x = x * gain
    return lookahead_limit(x, ceiling_db=ceiling_db)


def write_wav(path, x):
    import wave
    data = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def main() -> int:
    global IR
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/orca-master.wav")
    ap.add_argument("--cues", default="/tmp/orca-cues.json")
    a = ap.parse_args()

    IR = DSL.build_velvet_hall_ir(2.35)
    mix, placed = build()
    out = master(mix)
    write_wav(a.out, out)
    Path(a.cues).write_text(json.dumps(placed, indent=1))

    from collections import Counter
    print(f"{a.out}  {len(out)/SR:.2f}s  {len(placed)} cues  "
          f"peak {np.max(np.abs(out)):.3f}")
    print("  " + "  ".join(f"{k}x{v}" for k, v in sorted(Counter(c['cue'] for c in placed).items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
