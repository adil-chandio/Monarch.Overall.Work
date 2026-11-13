#!/usr/bin/env python3
"""VO fit + synthesized bed + 5.1-safe stereo master. Writes out/mix.wav."""
import os, sys, subprocess
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_build import (build_vo, torch_loop, wind_loop, drone_score, reverb,
                         whoosh, sub_boom, riser, place, bp, SR)
from beats import timeline, cues, CHORD
import json
def _rows():
    return json.load(open(os.path.join(OUT,'timeline_ext.json')))

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
OUT = "out"
PIC_LEN = 515.0

def wav_write(path, x):
    """x: (n,) or (n,2) float32 in -1..1"""
    import wave, struct
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    x = np.clip(x, -1, 1)
    pcm = (x * 32767.0).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())

def main():
    reels = sorted(os.path.join("vo", f) for f in os.listdir("vo") if f.endswith(".mp3"))
    print("reels", len(reels))
    vo_path, raw_d, fit_d, ratio = build_vo(PIC_LEN, reels)
    print("VO raw %.1fs -> fitted %.1fs (ratio %.4f)" % (raw_d, fit_d, ratio))
    # decode VO to float
    tmp = os.path.join(OUT, "tmp", "vo_f32.wav")
    subprocess.run([FF, "-y", "-i", vo_path, "-f", "f32le", "-ac", "1",
                    "-ar", str(SR), tmp], check=True, capture_output=True)
    vo = np.fromfile(tmp, dtype="<f4").astype(np.float32)
    if len(vo) < int(PIC_LEN * SR):
        vo = np.pad(vo, (0, int(PIC_LEN * SR) - len(vo)))
    vo = vo[:int(PIC_LEN * SR)]
    n = len(vo)
    print("vo samples", n)

    rows = _rows()
    t = 0.0
    for r in rows:
        r['start'] = round(t, 3); t += r['sec']
    total = round(t, 3)
    # ids were suffixed during the stretch; cue on the base id
    for r in rows:
        r['id'] = r['id'].split('.')[0]
    rng = np.random.default_rng(20261105)

    # ---- bed: ambience
    torch = torch_loop(n, rng) * 0.5
    wind = wind_loop(n, rng)
    # cave tone: very low room rumble
    t = np.arange(n, dtype=np.float32) / SR
    rumble = (np.sin(2 * np.pi * 41 * t) * 0.5 + np.sin(2 * np.pi * 57.3 * t) * 0.25)
    rumble = bp(rumble.astype(np.float32), 20, 120, 2) * 0.10
    amb = torch*0.9 + wind*0.8 + rumble

    # ---- score: one chord per chapter, mastered under speech
    chords = [CHORD[r["ch"]] for r in rows]
    # collapse to chapter changes only
    seq, last = [], None
    for r in rows:
        if r["ch"] != last:
            seq.append(CHORD[r["ch"]]); last = r["ch"]
    score = drone_score(n, seq, rng)

    # ---- transitions
    fx = np.zeros(n, np.float32)
    for c in cues(rows):
        if c["kind"] == "whoosh":
            clip = whoosh(0.55, 300, 3000, gain=c["gain"], rng=rng)
            place(fx, clip, c["t"])
        elif c["kind"] == "boom":
            clip = sub_boom(1.6, 64, 32, gain=c["gain"])
            place(fx, clip, c["t"])
        elif c["kind"] == "riser":
            clip = riser(2.2, gain=c["gain"], rng=rng)
            place(fx, clip, c["t"])
        elif c["kind"] == "tick":
            m = int(0.05 * SR); tt = np.arange(m) / SR
            clip = (np.sin(2 * np.pi * 2400 * tt) * np.exp(-tt * 90) * c["gain"]).astype(np.float32)
            place(fx, clip, c["t"])

    # ---- silence window: 8:27 -> end, drop the score to a floor so the last lines land
    duck = np.ones(n, np.float32)
    a, b = 8.30*60, PIC_LEN
    if a < PIC_LEN:
        duck[int(a*SR):] = np.linspace(1.0, 0.22, n - int(a*SR))
    score = score * duck
    amb = amb * (0.55 + 0.45 * duck)

    # ---- mix (all in -1..1 linear, VO loudest)
    vo_g = vo / (np.abs(vo).max() + 1e-9) * 0.78
    bed = (score + amb) * 0.30 + fx * 0.40
    bed = reverb(bed, mix=0.26, t60=2.6, rng=rng)
    mix = vo_g * 1.0 + bed * 0.55
    # gentle bus comp + soft clip
    mix = np.tanh(mix * 1.12) * 0.92
    # stereo: VO centre, bed wide via a short decorrelation
    d = int(0.011 * SR)
    bedL = bed * 0.98
    bedR = np.concatenate([np.zeros(d, np.float32), bed[:-d]]) * 0.98
    L = vo_g * 0.98 + bedL * 0.55
    R = vo_g * 0.98 + bedR * 0.55
    st = np.stack([np.tanh(L * 1.12), np.tanh(R * 1.12)], 1) * 0.92
    wav_write(os.path.join(OUT, "mix.wav"), st)
    print("wrote out/mix.wav", st.shape)

if __name__ == "__main__":
    main()
