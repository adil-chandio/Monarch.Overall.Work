"""Narration + a synthesised sound bed for the Gatun piece.

Everything is made from the repo's own DSP kit (audio/takes/*.wav, generated for this
repo) plus numpy synthesis: no third-party audio, nothing sampled from a film.
Cues come from the same timeline as the visuals (state(t), caption ids).
"""
import json, os, subprocess, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/user/Monarch.Overall.Work"
SR = 48000
DUR = 47.0
N = int(DUR * SR)
FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"


def load_vo():
    raw = subprocess.run([FF, "-v", "quiet", "-i", os.path.join(HERE, "audio", "vo.wav"),
                          "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.float32).astype(np.float32)
    out = np.zeros(N, np.float32)
    out[:min(len(a), N)] = a[:N]
    return out


def load_take(name):
    p = os.path.join(REPO, "audio", "takes", name + ".wav")
    raw = subprocess.run([FF, "-v", "quiet", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float32)


def place(buf, x, t, gain=1.0):
    i = int(t * SR)
    if i >= len(buf):
        return
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n] * gain


def env_adsr(n, a=0.01, d=0.1, s=0.7, r=0.3):
    t = np.arange(n) / SR
    e = np.ones(n, np.float32)
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nd and na + nd < n:
        e[na:na + nd] = np.linspace(1, s, nd)
        e[na + nd:] = s
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def sine_bed():
    """A low, slow bed: two detuned sines an octave apart, filtered noise for air,
    swelling with the two lockages instead of looping a tune."""
    t = np.arange(N) / SR
    bed = (0.050 * np.sin(2 * np.pi * 55.0 * t + 0.4 * np.sin(2 * np.pi * 0.07 * t))
           + 0.034 * np.sin(2 * np.pi * 82.5 * t + 0.9)
           + 0.022 * np.sin(2 * np.pi * 110.0 * t + 1.7 * np.sin(2 * np.pi * 0.05 * t)))
    # air: filtered noise, slowly breathing
    rng = np.random.default_rng(11)
    nz = rng.standard_normal(N).astype(np.float32)
    k = 400                                   # crude one-pole low pass
    b = np.zeros(N, np.float32)
    acc = 0.0
    for i in range(0, N, 1):
        acc += (nz[i] - acc) * (k / SR)
        b[i] = acc
    b = b / (np.abs(b).max() + 1e-9)
    bed = bed + 0.030 * b * (0.55 + 0.45 * np.sin(2 * np.pi * 0.045 * t - 1.2))
    # slow build: quiet under the hook, fuller under the mechanism, opens at the end
    shape = np.interp(t, [0, 3, 12, 19, 26, 34, 40, 43.9, 46.2, 47],
                      [0.45, 0.55, 0.70, 0.85, 1.00, 0.95, 1.05, 0.95, 0.30, 0.0])
    return bed * shape


def water_layer(level_curve, t_grid):
    """Water movement: a filtered noise bed whose gain follows the fill rate."""
    rng = np.random.default_rng(23)
    nz = rng.standard_normal(N).astype(np.float32)
    # band-pass around 500 Hz with a simple biquad
    from math import sin, cos, pi, sqrt
    f0, q = 520.0, 0.8
    w0 = 2 * pi * f0 / SR
    alpha = sin(w0) / (2 * q)
    b0, b1, b2 = alpha, 0.0, -alpha
    a0, a1, a2 = 1 + alpha, -2 * cos(w0), 1 - alpha
    y = np.zeros(N, np.float32)
    x1 = x2 = y1 = y2 = 0.0
    for i in range(N):
        x0 = nz[i]
        acc = (b0 * x0 + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2) / a0
        y[i] = acc
        x2, x1 = x1, x0
        y2, y1 = y1, acc
    y = y / (np.abs(y).max() + 1e-9)
    gain = np.interp(np.arange(N) / SR, t_grid[0], t_grid[1])
    return y * gain


def main():
    import sys
    sys.path.insert(0, HERE)
    import build_video as B          # for the shared timeline
    caps = json.load(open(os.path.join(HERE, "audio", "align.json")))["captions"]

    vo = load_vo()
    music = sine_bed()

    # --- water movement follows the fill rate; valves open with the fill
    ts = np.arange(0, DUR, 0.05)
    lvl = np.array([B.state(t)["level"] for t in ts])
    rate = np.gradient(lvl, ts)
    rate = np.clip(rate / max(rate.max(), 1e-6), 0, 1)
    gains = 0.16 + 0.75 * rate
    water = water_layer(None, (ts, gains))

    sfx = np.zeros(N, np.float32)
    sfx_bright = np.zeros(N, np.float32)

    # --- gate machinery: a low motor hum while a gate is moving
    gate_curve = np.array([max(B.state(t)["gate_low"], B.state(t)["gate_mid"], B.state(t)["gate_up"]) for t in ts])
    dgate = np.abs(np.gradient(gate_curve, ts))
    dgate = dgate / (dgate.max() + 1e-9)
    t_all = np.arange(N) / SR
    hum = (0.35 * np.sin(2 * np.pi * 58 * t_all) + 0.22 * np.sin(2 * np.pi * 116 * t_all + 0.7)
           + 0.10 * np.sin(2 * np.pi * 174 * t_all + 2.1))
    hum = hum * np.interp(t_all, ts, dgate * 0.9 + 0.02)

    # --- cue list, tied to the narration beats
    take = lambda n: load_take(n)
    knock = take("knock_wood")
    pop = take("ui_pop_soft")
    tick = take("pro_hover_tick_ping")
    swish = take("swish_bright")
    hit = take("cut_hit_punch")
    thump = take("whoosh_big_thump")
    riser = take("riser_dark")
    swell = take("reverse_swell_dark")
    mallet = take("mallet_glock")

    def cap_t(i, word=None):
        """Start time of caption i (or of the first caption containing `word`)."""
        if word is not None:
            for c in caps:
                if word.lower() in c["text"].lower():
                    return c["start"]
        return caps[min(i, len(caps) - 1)]["start"]

    # the ship arriving and entering
    place(sfx, knock, 0.05, 0.55)
    place(sfx, swish, cap_t(2) - 0.05, 0.42)          # "climb a mountain"
    place(sfx, pop, cap_t(3) - 0.02, 0.50)            # "No crane."
    place(sfx, pop, cap_t(4) - 0.02, 0.56)            # "No elevator."
    place(sfx, thump, 12.6, 0.55)                     # gate begins to open
    place(sfx, knock, 14.35, 0.70)                    # miter leaves seat
    place(sfx, knock, 15.10, 0.55)
    place(sfx, tick, cap_t(10), 0.40)
    # water arriving through the floor
    place(sfx, swell, 18.35, 0.75)
    place(sfx, thump, 18.75, 0.60)
    place(sfx, swish, cap_t(19) - 0.10, 0.55)         # "rises through a hundred"
    place(sfx, swish, cap_t(20) - 0.05, 0.50)
    place(sfx, mallet, cap_t(0, "Buoyancy does"), 0.34)     # "buoyancy does"
    # the second lift and the gates again
    place(sfx, thump, 26.9, 0.60)
    place(sfx, knock, 27.45, 0.65)
    place(sfx, tick, cap_t(27), 0.35)
    place(sfx, swell, 31.0, 0.55)
    place(sfx, pop, cap_t(30), 0.40)                  # "Three steps."
    place(sfx, pop, cap_t(31), 0.44)                  # "Eighty-five feet."
    # gravity: the culvert and the valves
    place(sfx, riser, 34.55, 0.55)
    place(sfx, thump, 36.55, 0.55)
    place(sfx, knock, 37.2, 0.45)
    place(sfx, pop, cap_t(0, "No pumps") - 0.02, 0.42)      # "No pumps."
    place(sfx, pop, cap_t(0, "No engines") - 0.02, 0.40)    # "No engines."
    place(sfx_bright, hit, cap_t(0, "Engineering hiding") - 0.05, 0.45)   # closing line
    place(sfx, hit, 43.9, 0.40)

    # --- gentle ducking of the bed under the voice, and a low cut on the voice
    venv = np.convolve(np.abs(vo), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
    venv = np.clip(venv / (np.percentile(venv, 92) + 1e-9), 0, 1)
    duck = 1.0 - 0.55 * venv

    mix = (vo * 1.0 + music * duck * 0.55 + water * duck * 0.30
           + hum * duck * 0.35 + sfx * 0.85 + sfx_bright * 0.55)

    # --- tail: let the bed ring out, fade the last half second to true silence
    fade_start = int(45.4 * SR)
    mix[fade_start:] *= np.linspace(1, 0, N - fade_start) ** 1.5
    # soft clip and normalise to -1 dBFS peak, then a gentle limiter slope
    mix = np.tanh(mix * 1.15) * 0.92
    mix = mix / max(np.abs(mix).max(), 1e-6) * 0.89

    out = os.path.join(HERE, "audio", "mix.wav")
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    p = subprocess.Popen([FF, "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-",
                          "-c:a", "pcm_s24le", out], stdin=subprocess.PIPE,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    p.stdin.write(pcm.tobytes())
    p.stdin.close()
    p.wait()
    print("wrote", out, "%.2f s" % (len(mix) / SR))


if __name__ == "__main__":
    main()
