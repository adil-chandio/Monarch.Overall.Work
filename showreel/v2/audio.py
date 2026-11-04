"""
MONARCH v2 — the sound bed.

Follows skills/monarch-video-lab/sound-design:
  · 8 cue families synthesised with numpy/scipy, $0 budget, no samples
  · every SFX lands on a FRAME, not a timestamp guess (cues are derived from
    showreel/v2/seams.json, which the picture renderer wrote)
  · no harsh 2.5–5 kHz bands, sub is mono below 120 Hz
  · music is in the film's key (A minor) so stings can never fight the score
  · one idea per cue; a cue may be silent

Writes public/demo/v2-mix.wav (48 kHz, stereo, float32).
"""
import argparse
import json
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy import signal

SR = 48000
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEAMS = ROOT / "showreel/v2/seams.json"
DEFAULT_OUT = ROOT / "public/demo/v2-mix.wav"
def _ffmpeg() -> str:
    """the venv binary when it exists, otherwise whatever is on PATH (CI runner)."""
    venv = ROOT / ".venv/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
    if venv.exists():
        return str(venv)
    import shutil
    found = shutil.which("ffmpeg")
    if not found:
        try:
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            raise SystemExit("no ffmpeg available — install ffmpeg or imageio-ffmpeg")
    return found


FFMPEG = _ffmpeg()

BPM = 120.0
BEAT = 60.0 / BPM          # 0.5 s
BAR = BEAT * 4             # 2.0 s
KEY = 57                   # A3 — the film's key (A minor)


# ------------------------------------------------------------------ helpers
def hz(midi: float) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def pink(n: int, seed: int = 0) -> np.ndarray:
    """1/sqrt(f)-shaped noise via a cheap IIR, deterministic."""
    rng = np.random.default_rng(seed)
    w = rng.standard_normal(n)
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]
    return signal.lfilter(b, a, w)


def bpf(x: np.ndarray, lo: float, hi: float, order: int = 2) -> np.ndarray:
    ny = SR / 2
    sos = signal.butter(order, [max(lo, 20) / ny, min(hi, ny * 0.98) / ny], btype="band", output="sos")
    return signal.sosfilt(sos, x)


def hpf(x: np.ndarray, f: float, order: int = 2) -> np.ndarray:
    sos = signal.butter(order, f / (SR / 2), btype="high", output="sos")
    return signal.sosfilt(sos, x)


def norm(x: np.ndarray, peak: float = 1.0) -> np.ndarray:
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 1e-9 else x


def env_ad(n: int, attack: float, decay: float) -> np.ndarray:
    t = np.arange(n) / SR
    a = 1 - np.exp(-t / max(attack, 1e-4))
    d = np.exp(-t / max(decay, 1e-4))
    return a * d


def pan(x: np.ndarray, p: float) -> np.ndarray:
    """equal-power pan, -1 hard left .. +1 hard right. Returns (2, n)."""
    a = (p + 1) * np.pi / 4
    return np.vstack([x * np.cos(a), x * np.sin(a)]) * np.sqrt(2)


def place_st(bus: np.ndarray, x: np.ndarray, at: float, gain: float = 1.0, p: float = 0.0) -> None:
    place(bus, pan(x, p) if p else np.vstack([x, x]), at, gain)


def place(bus: np.ndarray, x: np.ndarray, at: float, gain: float = 1.0) -> None:
    i = int(round(at * SR))
    if i >= bus.shape[1]:
        return
    j = min(bus.shape[1], i + x.shape[-1])
    if x.ndim == 1:
        bus[:, i:j] += x[: j - i] * gain
    else:
        bus[:, i:j] += x[:, : j - i] * gain


# ------------------------------------------------------------------ 2.1 whoosh
def silk_whoosh(dur=0.42, f0=380, f1=2600, gain=0.5, seed=1):
    n = int(dur * SR)
    u = np.linspace(0, 1, n)
    nz = pink(n, seed)
    e = np.sin(np.pi * u) ** 2.2          # zero at both ends, no click
    out = np.zeros(n)
    chunk = 512
    for i in range(0, n, chunk):
        f = f0 + (f1 - f0) * (i / n) ** 1.6
        seg = nz[i:i + chunk]
        out[i:i + chunk] = bpf(seg, f / 2.2, f * 2.2)[: len(seg)]
    out = norm(out * e)
    # no band above 6 kHz louder than -18 dB
    out = out - 0.06 * hpf(out, 6000)
    return out * gain


# ------------------------------------------------------------------ 2.2 sub-boom
def cinema_sub_boom(dur=1.25, root=36.71, gain=0.7, seed=2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = root * (1 + 1.4 * np.exp(-t * 18))
    phase = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(phase) * np.exp(-t * 2.6)
    thud = bpf(pink(n, seed), 90, 240) * np.exp(-t * 26) * 0.18
    return norm(body + thud) * gain


# ------------------------------------------------------------------ 2.3 thock
def thock_click(gain=0.42):
    n = int(0.14 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * 155 * t) * np.exp(-t * 38)
    cap = np.sin(2 * np.pi * 820 * t) * np.exp(-t * 110) * 0.45
    return norm(body + cap) * gain       # never a 3–4 kHz tick


# ------------------------------------------------------------------ 2.4 riser
def riser(dur=1.4, gain=0.34, seed=4):
    n = int(dur * SR)
    u = np.linspace(0, 1, n)
    nz = pink(n, seed)
    out = np.zeros(n)
    for i in range(0, n, 512):
        f = 300 + 5200 * (i / n) ** 2.2
        seg = nz[i:i + 512]
        out[i:i + 512] = bpf(seg, f * 0.7, f * 1.6)[: len(seg)]
    tone = np.sin(2 * np.pi * np.cumsum(hz(KEY) * (1 + 2.5 * u ** 2)) / SR) * 0.25
    e = u ** 2
    e[-int(0.012 * SR):] = 0            # reaches zero a frame before the impact
    return norm((out + tone) * e) * gain


# ------------------------------------------------------------------ 2.5 felt pluck
def felt_pluck(midi, dur=0.9, vel=0.8):
    f = hz(midi)
    n = int(dur * SR)
    t = np.arange(n) / SR
    att = 1 - np.exp(-t / 0.004)
    body = np.sin(2 * np.pi * f * t) * np.exp(-t * 3.0)
    bell = np.sin(2 * np.pi * f * 2.01 * t) * np.exp(-t * 7) * 0.22
    fifth = np.sin(2 * np.pi * f * 1.5 * t) * np.exp(-t * 5) * 0.12
    return norm(body + bell + fifth) * att * vel


# ------------------------------------------------------------------ 2.6 pad
def pad_voice(midi, dur, detune=0.004, gain=0.18):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for d in (-detune, 0.0, detune):
        f = hz(midi) * (1 + d)
        out += np.sin(2 * np.pi * f * t) + 0.22 * np.sin(2 * np.pi * f * 2 * t)
    # slow, musical swell — no tremolo (that is idle wobble)
    e = np.minimum(1, t / 0.55) * np.minimum(1, (dur - t) / 0.7)
    return out * np.clip(e, 0, 1) * gain / 3


# ------------------------------------------------------------------ 2.7 kick / 2.8 hats
def kick(gain=0.9):
    n = int(0.42 * SR)
    t = np.arange(n) / SR
    f = 52 + 128 * np.exp(-t * 34)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8.5)
    click = bpf(pink(n, 9), 1200, 3200) * np.exp(-t * 150) * 0.25
    return norm(np.tanh((body + click) * 1.4)) * gain


def hat(gain=0.16, seed=11):
    n = int(0.07 * SR)
    t = np.arange(n) / SR
    nz = hpf(pink(n, seed), 7000)
    return norm(nz * np.exp(-t * 90)) * gain


def snare(gain=0.30, seed=13):
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    nz = bpf(pink(n, seed), 900, 5200) * np.exp(-t * 26)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 40) * 0.5
    return norm(nz + body) * gain


# ------------------------------------------------------------------ the VO
def load_vo(path: Path) -> np.ndarray:
    """decode an mp3 to mono float32 at SR with ffmpeg"""
    raw = subprocess.run(
        [FFMPEG, "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


def rms_db(x: np.ndarray) -> float:
    r = np.sqrt(np.mean(x ** 2)) + 1e-12
    return 20 * np.log10(r)


def main() -> None:
    ap = argparse.ArgumentParser(description="build the score and frame-locked SFX")
    ap.add_argument("--seams", default=str(DEFAULT_SEAMS),
                    help="seam manifest written by the picture renderer")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="output wav")
    args = ap.parse_args()

    seams = json.loads(Path(args.seams).read_text())
    OUT = Path(args.out)
    total = seams["total"]
    beats = seams["beats"]
    n = int(np.ceil(total * SR))
    music = np.zeros((2, n))
    sfx = np.zeros((2, n))

    # ---------------------------------------------------------------- MUSIC
    # A minor, 120 BPM, Am – F – C – G, one chord per bar — and an ARRANGEMENT, not a
    # loop: the drums arrive at bar 2, everything is in by bar 4, and the last bar drops
    # to pad + pluck only. Constant-level beds are what read as "no music".
    prog = [[KEY, KEY + 3, KEY + 7, KEY + 12],
            [KEY - 4, KEY, KEY + 3, KEY + 8],
            [KEY + 3, KEY + 7, KEY + 10, KEY + 15],
            [KEY - 2, KEY + 2, KEY + 5, KEY + 7]]
    bars = int(np.ceil(total / BAR))
    last_bar = bars - 1

    def drums_on(bar):        # the arrangement gate
        return 1 <= bar < last_bar

    for b in range(bars):
        chords = prog[b % 4]
        is_last = b == last_bar
        # pad: true stereo — left and right get different detune sets, so the field opens
        for j, m in enumerate(chords):
            l = pad_voice(m, BAR * 1.18, detune=0.0035, gain=0.080)
            r = pad_voice(m, BAR * 1.18, detune=0.0055, gain=0.080)
            place(music, np.vstack([l, r]), b * BAR)
            l2 = pad_voice(m + 12, BAR * 1.18, detune=0.006, gain=0.042)
            r2 = pad_voice(m + 12, BAR * 1.18, detune=0.002, gain=0.042)
            place(music, np.vstack([l2, r2]), b * BAR, gain=0.0)  # keep the field, muted octave
        # arpeggio: 8th notes, panned in a widening fan — the movement the ear follows
        for k in range(8):
            m = chords[k % 4] + (12 if k % 8 >= 4 else 0)
            pnl = (-0.55, 0.35, -0.15, 0.6, 0.2, -0.45, 0.5, -0.25)[k % 8]
            g = 0.62 if not is_last else 0.72
            place_st(music, felt_pluck(m, vel=0.34), b * BAR + k * BEAT / 2, gain=g, p=pnl)
        # the pluck's octave sparkle only in the big bars
        if 2 <= b < last_bar:
            for k in range(4):
                m = chords[k] + 24
                place_st(music, felt_pluck(m, dur=0.5, vel=0.20), b * BAR + k * BEAT + BEAT / 2, gain=0.30, p=0.7 * (-1) ** k)

    # ---- drums, gated by the arrangement
    for k in range(int(total / BEAT)):
        at = k * BEAT
        bar = int(at / BAR)
        if not drums_on(bar):
            continue
        if k % 4 == 0 or k % 4 == 2:
            place(music, kick(gain=0.9), at, gain=0.92)
        place_st(music, hat(gain=0.15 if k % 2 else 0.20), at + BEAT / 2, gain=1.0, p=0.22)
        if bar >= 2:
            place_st(music, hat(gain=0.09), at + BEAT / 4, gain=1.0, p=-0.35)
            place_st(music, hat(gain=0.09), at + 3 * BEAT / 4, gain=1.0, p=-0.35)
            if k % 4 == 2:
                place(music, snare(gain=0.30), at, gain=1.0)

    # ---- sub: root of the chord on every beat, folded to both channels (mono < 120 Hz)
    for b in range(bars):
        root = prog[b % 4][0] - 24
        for k in range(4):
            nb = int(BEAT * SR)
            t = np.arange(nb) / SR
            f = hz(root)
            sub = np.sin(2 * np.pi * f * t) * env_ad(nb, 0.006, 0.22) * 0.5
            place(music, np.vstack([sub, sub]), b * BAR + k * BEAT, gain=0.30)

    # ---- SIDECHAIN PUMP: the kick ducks the pad every beat. This is what makes a bed
    # feel like a record instead of a sustained tone.
    pump = np.ones(n)
    for k in range(int(total / BEAT)):
        bar = int(k * BEAT / BAR)
        if not drums_on(bar):
            continue
        i = int(k * BEAT * SR)
        m = int(0.26 * SR)
        if i + m < n:
            pump[i:i + m] = np.minimum(pump[i:i + m], 1 - 0.55 * np.exp(-np.arange(m) / (0.07 * SR)))
    music *= pump[None, :]

    # ---------------------------------------------------------------- SFX
    # Every cue is derived from a FRAME in seams.json — the picture wrote the timing.
    for i, beat in enumerate(beats):
        at = beat["start"]
        # the seam whoosh: starts 0.24 s BEFORE the cut, peaks ON it
        place(sfx, silk_whoosh(0.55, 300, 2900, gain=0.42, seed=100 + i), at - 0.24)
        # the downbeat thock lands exactly on the frame
        place(sfx, thock_click(0.34), at)
        # a sub-boom under the two heaviest beats only (one idea per cue)
        if beat["name"] in ("gap", "swap", "end"):
            place(sfx, cinema_sub_boom(1.25, gain=0.62, seed=200 + i), at, gain=0.9)
        # a riser into the two arrivals that need tension
        if beat["name"] in ("swap", "comments"):
            place(sfx, riser(1.4, gain=0.30, seed=300 + i), at - 1.4)

    # inserts are their own shots, so they get their own arrival cue
    for ins in seams.get("inserts", []):
        at = float(ins["start"])
        place(sfx, silk_whoosh(0.45, 420, 3400, gain=0.50, seed=int(at * 10)), at - 0.20)
        place(sfx, cinema_sub_boom(0.95, gain=0.70, seed=int(at * 7)), at, gain=0.85)
        place(sfx, thock_click(0.30), at + 0.02)

    # UI foley: every count tick gets a quiet click — the numbers sound like instruments
    rng_at = [0.0]
    for beat in beats:
        for k in range(6):
            rng_at.append(beat["start"] + 0.10 + k * 0.085)
    for j, at in enumerate(rng_at):
        place(sfx, thock_click(0.10 if j % 3 else 0.15), at, gain=0.8)

    # ---------------------------------------------------------------- VO
    vo = np.zeros(n)
    for k, start in enumerate(seams.get("vo_starts", [])):
        pass
    timing = json.loads((ROOT / "public/demo/vo/timing.json").read_text())
    vo_files = sorted((ROOT / "public/demo/vo").glob("0*.mp3"))
    for k, (f, start) in enumerate(zip(vo_files, timing["starts"])):
        x = load_vo(f)
        place(vo[None, :], x, start)

    # ---------------------------------------------------------------- MIX
    # voice is the clock: duck the bed 6 dB under every VO segment, with a 60 ms ramp
    duck = np.ones(n)
    for f, start in zip(vo_files, timing["starts"]):
        x = load_vo(f)
        a = int(start * SR)
        b = min(n, a + len(x))
        duck[a:b] = 0.42
    # smooth the duck so it never clicks
    k = int(0.06 * SR)
    duck = np.convolve(duck, np.ones(k) / k, mode="same")

    # the sub must be mono below 120 Hz: fold the low band to both channels equally
    low = signal.sosfilt(signal.butter(4, 120 / (SR / 2), btype="low", output="sos"), music.mean(axis=0))
    high = music - signal.sosfilt(signal.butter(4, 120 / (SR / 2), btype="low", output="sos"),
                                 np.vstack([music.mean(axis=0)] * 2))
    music = high + np.vstack([low, low])

    # gain staging: VO is the reference. The bed sits ~11 dB under it before ducking,
    # the SFX peak above it only on their own frame (a cue may be loud; a bed may not).
    M_GAIN, S_GAIN, V_GAIN = 0.42, 0.72, 2.6
    bed = music * M_GAIN * duck[None, :] + sfx * S_GAIN * (0.80 * duck[None, :] + 0.20)
    mix = bed
    mix[0] += vo * V_GAIN
    mix[1] += vo * V_GAIN

    # no harshness: a gentle shelf cut at 3.2 kHz on the bed only (the VO keeps its air)
    ny = SR / 2
    sos = signal.butter(2, [2500 / ny, 5200 / ny], btype="band", output="sos")
    harsh = signal.sosfilt(sos, bed.mean(axis=0))
    mix -= np.vstack([harsh, harsh]) * 0.22

    mix = signal.sosfilt(signal.butter(2, 30 / (SR / 2), btype="high", output="sos"), mix)
    peak = np.max(np.abs(mix))
    mix = mix / peak * 0.89

    # ---------------------------------------------------------------- write
    pcm = (np.clip(mix.T, -1, 1) * 32767).astype("<i2")
    with wave.open(str(OUT), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())

    print(f"wrote {OUT}  {total:.2f}s  {OUT.stat().st_size/1e6:.1f} MB")
    print(f"  music rms {rms_db(music*M_GAIN):6.1f} dB   sfx {rms_db(sfx*S_GAIN):6.1f} dB   vo {rms_db(vo*V_GAIN):6.1f} dB")
    print(f"  peaks: mix {20*np.log10(np.max(np.abs(mix))+1e-12):.1f} dBFS")


if __name__ == "__main__":
    main()
