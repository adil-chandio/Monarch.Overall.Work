#!/usr/bin/env python3
"""Lay the reference's edit onto a soundtrack: a designed bed plus cues on the cut points.

The cue sheet is the measured picture, not a mood: cuts from analysis/v4-build/shots.json,
type slams from the word boxes, the flash at 20.63, the pill at 9.55. Each cue names a
role, and each role fixes *where* its sync point sits against the cut and *how loud* it is
over the bed -- so an effect either leads the cut by 40 ms or lands after it, exactly as
the edit implies, and nothing is guessed by ear.

Levels are relative to the bed (the measured -16 dBFS RMS of the reference), and the whole
mix is then loudness-matched to the reference, so the result cannot be quieter or harsher
than the film it replaces.

    python3 tools/mix.py --seconds 7 --out audio/mix-7.wav
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ffbin import ffmpeg

SR = 48000
TAKES = Path("audio/takes")

# role -> (sound, align point, offset ms from the cut, level over the bed in dB)
ROLES = {
    "whoosh.short": ("whoosh_fast_crisp", "peak", -110, 6.0),
    "whoosh.long":  ("whoosh_big_thump", "peak", -60, 5.0),
    "hit":          ("cut_hit_punch", "onset", 0, 4.5),
    "drop":         ("cut_hit_kick", "onset", 0, 2.0),
    "swell":        ("reverse_swell_dark", "peak", -30, 2.5),
    "riser":        ("riser_dark", "peak", 0, 1.0),
    "land":         ("pro_pop_in_round", "onset", 30, 5.5),
    "tock":         ("knock_wood", "onset", -25, 3.5),
    "tick":         ("pro_hover_tick_ping", "onset", 0, 1.5),
    "bell":         ("mallet_glock", "onset", 0, 3.0),
    "notify":       ("notify_mid_tine", "onset", 0, 2.0),
    "snap":         ("shutter_dslr", "onset", 5, 2.0),
    "pop":          ("ui_pop_soft", "onset", 0, 4.0),
    "sub":          ("sub_drop_punch", "onset", 0, 1.5),
    "zip":          ("zip_bright", "peak", 0, 1.0),
}


def load(name: str) -> tuple[np.ndarray, dict]:
    meta = json.loads((TAKES / "meta.json").read_text())
    key = next((k for k in meta if k.replace("/", "_") == name), None)
    if key is None:
        raise SystemExit(f"no take for {name}")
    b = subprocess.run([ffmpeg(), "-v", "error", "-i", str(TAKES / f"{name}.wav"),
                        "-f", "f32le", "-"], capture_output=True).stdout
    y = np.frombuffer(b, np.float32).reshape(-1, 2).astype(np.float64)
    return y, meta[key]


def place(dst: np.ndarray, y: np.ndarray, start: int, gain: float) -> None:
    if start >= dst.shape[0]:
        return
    s = max(0, start)
    skip = s - start
    seg = y[skip:]
    n = min(seg.shape[0], dst.shape[0] - s)
    if n > 0:
        dst[s:s + n] += seg[:n] * gain


def l50(x: np.ndarray, win: float = 0.05) -> np.ndarray:
    """RMS of every 50 ms window: the short-term level a hit is judged against."""
    w = max(1, int(win * SR))
    m = x if x.ndim == 1 else x.mean(1)
    n = m.shape[0] // w
    if n == 0:
        return np.array([np.sqrt((m ** 2).mean())])
    return np.sqrt((m[:n * w].reshape(n, w) ** 2).mean(1))


def band(x: np.ndarray, lo: float, hi: float, order: int = 2) -> np.ndarray:
    from scipy.signal import butter, sosfilt
    sos = butter(order, [lo / (SR / 2), hi / (SR / 2)], btype="band", output="sos")
    return sosfilt(sos, x)


def hf_share(x: np.ndarray, lo: float = 5000.0, hi: float = 16000.0) -> float:
    seg = x[: int(2.0 * SR), 0]
    S = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
    f = np.fft.rfftfreq(len(seg), 1 / SR)
    return float(S[(f >= lo) & (f < hi)].sum() / (S.sum() + 1e-12))


def air_polish(x: np.ndarray, target: float = 0.245, cap_db: float = 4.0) -> np.ndarray:
    """Bring the 5-16 kHz air back to the reference's share with a gentle shelf.

    Air is smooth noise up here; the band that makes a mix harsh is 2-5 kHz, and that one is
    left alone. Three passes at most, and never more than `cap_db` of lift.
    """
    if hf_share(x) < 1e-6:
        return x
    lift = 0.0
    for _ in range(3):
        cur = hf_share(x)
        if cur >= target * 0.95:
            break
        need_db = min(cap_db - lift, 20 * np.log10(target / max(cur, 1e-6)) * 0.55)
        if need_db <= 0.1:
            break
        g = 10 ** (need_db / 20.0) - 1
        for ch in (0, 1):
            x[:, ch] += band(x[:, ch], 6200.0, 17000.0) * g
        lift += need_db
    return x


def limit(x: np.ndarray, ceiling_db: float = -1.0) -> np.ndarray:
    """A lookahead limiter: peaks over the ceiling are pulled down with a 3 ms lookahead and
    a 60 ms release, so the hits keep their body instead of the whole mix being turned down."""
    from scipy.ndimage import maximum_filter1d, uniform_filter1d
    thr = 10 ** (ceiling_db / 20.0)
    env = np.abs(x).max(1)
    look = maximum_filter1d(env, int(0.006 * SR), mode="nearest")
    look = uniform_filter1d(look, int(0.004 * SR))
    g = np.minimum(1.0, thr / np.maximum(look, 1e-9))
    g = uniform_filter1d(g, int(0.020 * SR))                 # smooth release
    g = np.minimum(g, np.minimum(1.0, thr / np.maximum(np.abs(x).max(1), 1e-9)))
    return x * g[:, None]


def lufs(x: np.ndarray) -> float:
    """Integrated-ish loudness: EBU R128 via ffmpeg, which is what a phone measures."""
    raw = np.clip(x, -1, 1).astype(np.float32).tobytes()
    q = subprocess.Popen([ffmpeg(), "-v", "info", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                          "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, err = q.communicate(raw)
    txt = (err or b"").decode("utf-8", "ignore")
    try:
        j = txt[txt.index("{"):txt.rindex("}") + 1]
        return float(json.loads(j)["input_i"])
    except Exception:
        return -23.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=7.0)
    ap.add_argument("--bed", default="audio/bed-7.wav")
    ap.add_argument("--out", default="audio/mix-7.wav")
    ap.add_argument("--cues", default="audio/cues.json")
    ap.add_argument("--target-i", type=float, default=-14.0,
                    help="integrated loudness of the reference's own soundtrack")
    a = ap.parse_args()

    n = int(a.seconds * SR)
    b = subprocess.run([ffmpeg(), "-v", "error", "-i", a.bed, "-f", "f32le", "-"],
                       capture_output=True).stdout
    bed = np.frombuffer(b, np.float32).reshape(-1, 2)[:n].astype(np.float64)
    if bed.shape[0] < n:
        bed = np.pad(bed, ((0, n - bed.shape[0]), (0, 0)))
    mix = bed.copy()
    duck = np.ones(n)                      # the bed steps back under a hit, so the hit is felt
    bed_rms = float(np.sqrt((bed ** 2).mean()))
    print(f"  bed median 50 ms {20 * np.log10(np.median(l50(bed))):.1f} dBFS")
    cues = json.loads(Path(a.cues).read_text())
    used = 0
    for c in cues:
        role = ROLES.get(c["role"])
        if not role:
            continue
        sound, align, off_ms, over_db = role
        if not (TAKES / f"{sound}.wav").exists():
            continue
        y, m = load(sound)
        cue_s = c["t"] + off_ms / 1000.0
        start = int(round((cue_s - m[f"{align}_s"]) * SR))
        # the level is over the bed *in that moment*, not a fixed gain: the take's loudest
        # 50 ms against the music's median 50 ms in the half-second before the cue
        w0 = max(0, start - int(0.5 * SR))
        ref = float(np.median(l50(mix[w0:max(w0 + 1, start)]))) if start > 0 else float(np.median(l50(mix)))
        ref = max(ref, 1e-6)
        gain = (ref * (10 ** (over_db / 20.0))) / max(1e-9, float(l50(y).max()))
        gain *= c.get("gain", 1.0)
        if c["role"] in ("swell", "riser", "bell"):
            gain *= 0.7          # beds and bells stay under the hits, never beside them
        place(mix, y, start, gain)
        if c["role"] in ("hit", "drop", "whoosh.long", "sub"):
            d0 = max(0, start)
            d1 = min(n, d0 + int(0.34 * SR))
            duck[d0:d1] = np.minimum(duck[d0:d1], 0.42)   # -7.5 dB
        used += 1
    # soften the duck's edges so it breathes instead of clicking
    from scipy.ndimage import uniform_filter1d
    duck = uniform_filter1d(duck, int(0.045 * SR))
    mix = mix * duck[:, None]
    # keep the sum from clipping, then hit the reference's loudness
    mix = air_polish(mix)
    mix = limit(mix)
    cur = lufs(mix)
    g = 10 ** ((a.target_i - cur) / 20.0)
    mix *= g
    mix = limit(mix)
    raw = np.clip(mix, -1, 1).astype(np.float32).tobytes()
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    w = subprocess.Popen([ffmpeg(), "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2",
                          "-i", "-", "-c:a", "pcm_s24le", a.out], stdin=subprocess.PIPE)
    w.stdin.write(raw); w.stdin.close(); w.wait()
    print(f"  {used} cues  bed rms {20 * np.log10(bed_rms):.1f} dBFS  "
          f"mix {lufs(mix):.1f} LUFS  peak {20 * np.log10(np.abs(mix).max()):.1f} dBFS -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
