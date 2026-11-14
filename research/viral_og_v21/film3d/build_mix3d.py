#!/usr/bin/env python3
"""Mix the 60 s cut: VO + repo score + repo SFX cues (kit levels) + synthesized ambience."""
import math, os, subprocess, sys
import numpy as np
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sfx_cues

SR = 48000
FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
OUT = os.path.join(HERE, "out")
VO = os.path.abspath(os.path.join(HERE, "..", "film", "out", "vo_master.wav"))
DUR = 60.0
BED_DB = -26.0


def wav_read(p):
    with wave.open(p) as w:
        n = w.getnframes(); ch = w.getnchannels()
        x = np.frombuffer(w.readframes(n), dtype="<i2").astype(np.float32) / 32768.0
    if ch > 1:
        x = x.reshape(-1, ch).mean(1)
    return x


def wav_write(p, st):
    st = np.clip(st, -1, 1)
    with wave.open(p, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())


def pink(n, rng):
    w = rng.normal(0, 1, n).astype(np.float32)
    F = np.fft.rfft(w)
    f = np.fft.rfftfreq(n, 1 / SR)
    return np.fft.irfft(F / np.maximum(f, 18.0) ** 0.5, n).astype(np.float32)


def bp(x, lo, hi, order=2):
    n = len(x); F = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
    m = np.ones_like(f)
    if lo: m *= 1 / (1 + (lo / np.maximum(f, 1e-6)) ** (2 * order))
    if hi: m *= 1 / (1 + (f / hi) ** (2 * order))
    return np.fft.irfft(F * m, n).astype(np.float32)


def ambience(n, rng):
    """Cave room tone + fire + a cold wind at the mouth."""
    t = np.arange(n, dtype=np.float32) / SR
    rumble = (np.sin(2 * np.pi * 42 * t) * 0.6 + np.sin(2 * np.pi * 61.5 * t) * 0.25)
    rumble = bp(rumble, 18, 110, 2) * 0.055
    air = bp(pink(n, rng), 260, 5200, 1) * 0.035
    wind = bp(pink(n, rng), 90, 900, 2)
    wind *= (0.55 + 0.45 * np.sin(2 * np.pi * 0.06 * t)) * 0.030
    fire = bp(pink(n, rng), 120, 6200, 2) * 0.020
    cr = np.zeros(n, np.float32)
    for _ in range(int(DUR * 13)):
        i = int(rng.integers(0, max(1, n - 2000)))
        L = int(rng.integers(80, 700))
        b = rng.normal(0, 1, L).astype(np.float32) * np.exp(-np.arange(L) / (L * 0.25))
        b = bp(b, 900, 7000, 1) * float(rng.uniform(0.02, 0.13))
        cr[i:i + L] += b[:max(0, min(L, n - i))]
    # the fire is next to camera for the first 27 s only
    fade = np.ones(n, np.float32)
    fade[int(27 * SR):] = np.linspace(1.0, 0.25, n - int(27 * SR))
    return (rumble + air + wind + (fire + cr) * fade)


def footsteps(n, rng):
    """Boots and claws on wet gravel, placed on the animal's own gait clock."""
    import film1min as F
    _, sh = F.film()
    starts, acc = [], 0.0
    for s in sh:
        starts.append(acc); acc += s.dur
    out = np.zeros(n, np.float32)
    for i, s in enumerate(sh):
        act = s.act(0.5)
        if act.get("kind") != "bear" or act.get("walk", 0.0) < 0.5:
            continue
        t0, dur = starts[i], s.dur
        f = F.BEAR_WALK["freq"]
        for k in range(int(dur * f * 2)):
            t = t0 + k / (2.0 * f)
            heavy = (k % 4 == 0)
            L = int(0.20 * SR) if heavy else int(0.12 * SR)
            tt = np.arange(L, dtype=np.float32) / SR
            # thump: filtered noise burst with a fast decay, plus a low body
            b = rng.normal(0, 1, L).astype(np.float32) * np.exp(-tt * (34 if heavy else 60))
            b = bp(b, 180, 2600 if heavy else 5200, 1)
            b *= (0.55 if heavy else 0.30) * (0.7 + 0.6 * rng.random())
            body = np.sin(2 * np.pi * 78 * tt) * np.exp(-tt * 26) * (0.22 if heavy else 0.07)
            g = b + body
            j = int(t * SR)
            if 0 <= j < n:
                m = min(L, n - j)
                out[j:j + m] += g[:m]
    return out


def main():
    n = int(DUR * SR)
    rng = np.random.default_rng(3)
    # --- VO: first 60 s of the fitted master
    vo = wav_read(VO)[:n]
    if len(vo) < n:
        vo = np.pad(vo, (0, n - len(vo)))
    vo = vo / (np.abs(vo).max() + 1e-9) * 0.72
    # a touch of room so the narration sits in the cave, not on top of it
    ir_n = int(1.6 * SR)
    ir = rng.normal(0, 1, ir_n).astype(np.float32) * np.exp(-np.arange(ir_n) / (0.30 * SR))
    ir = bp(ir, 180, 5200, 1); ir /= np.abs(ir).sum() + 1e-9
    wet = np.fft.irfft(np.fft.rfft(vo, n + ir_n) * np.fft.rfft(ir, n + ir_n), n + ir_n)[:n].astype(np.float32)
    vo_mix = vo * 0.92 + wet * 0.9
    # --- score
    with wave.open(os.path.join(OUT, "score60.wav")) as w:
        s = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768.0
    score = s.reshape(-1, 2)[:n]
    if len(score) < n:
        score = np.pad(score, ((0, n - len(score)), (0, 0)))
    # --- SFX from the repo kit
    bus = sfx_cues.build(DUR, bed_db=BED_DB)
    sfx = bus.stereo()[:n]
    pk = np.abs(sfx).max()
    if pk > 0:
        sfx = sfx / pk * 0.62
    # --- ambience + footfall foley
    amb = ambience(n, rng) + footsteps(n, rng)
    amb_st = np.stack([amb, np.roll(amb, 480)], 1)
    # --- mix: music steps down under the SFX transients, VO stays on top
    bed = score * 0.85 + amb_st * 0.9
    st = vo_mix[:, None] * np.array([0.98, 0.98])[None, :] + bed * 0.55 + sfx * 0.55
    # soft knee, then loudness
    st = np.tanh(st * 1.08) * 0.95
    tmp = os.path.join(OUT, "mix60_raw.wav")
    wav_write(tmp, st)
    fin = os.path.join(OUT, "mix60.wav")
    subprocess.run([FF, "-y", "-i", tmp, "-af",
                    "highpass=f=28,loudnorm=I=-16:TP=-1.5:LRA=9", "-ar", str(SR), "-ac", "2", fin],
                   check=True, capture_output=True)
    print("wrote", fin, st.shape, "peak %.3f" % np.abs(st).max())


if __name__ == "__main__":
    main()
