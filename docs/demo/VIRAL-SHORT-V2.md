# Viral short v2 — rebuilt with the repo's own video skills

**42.3 s · 1920×1080 · 30 fps · Urdu-English VO · −14.2 LUFS**
`public/demo/viral-short-v2.mp4` — 20.4 MB

This replaces v1 (`viral-short.mp4`). v1 was rejected twice as a text-card slideshow. v2 is a
different renderer, not a polish pass.

## What changed, and which skill demanded it

| Was (v1) | Now (v2) | Skill / source |
|---|---|---|
| Pillow frames, no filters | **Skia canvas** (`@napi-rs/canvas`): gradients, `ctx.filter` blur, `lighter`/`overlay` blend modes, shadow glow, paths, particles | — |
| No transitions | **Cut-the-curve** seams: `power4.in` exit → `power4.out` entry, ±230 px partial travel (12 % of frame), **10 px blur on the wrapper**, hard swap at peak velocity | `skills/hyperframes/cut-the-curve` §3, §blur logic |
| Two scenes crossfaded | **Zero overlap** — one scene composited per frame; exit occupies `[b−CUT, b)`, entry occupies `[b, b+CUT)` | `motion-doctrine` Seam Gate, `seam-craft` |
| White-flash risk | Stage painted once; the per-scene ground that washed every seam was **removed** (that was a real bug in the first v2 pass) | `seam-craft` §stage-ground |
| Fade killed at 28 % of the clock | Fade completes at 28 % of **travel** (q ≈ 0.73) — otherwise the exit is invisible for the whole acceleration | `cut-the-curve` §3 fade trick |
| Scenes froze after 1.5 s | Beat clock re-timed so the **tail plays at 2.2×** — every beat is still moving into its cut | `motion-doctrine` (no idle wobble / no dead air) |
| Static camera | **Camera with intent**: 8.5 % push + 78 px pan per beat, alternating direction | `motion-doctrine` §performance |
| No inserts | **Two full-frame insert shots** (`36×`, `1/29`) with radial speed-line bursts | `cut-the-curve` arrival beats |
| Sine-tone "music" | **Arrangement** in A minor, 120 BPM: Am–F–C–G, stereo-detuned pad, panned arpeggio fan, gated drums (enter bar 2, out on the last bar), sub-bass, **sidechain pump** on every kick | `monarch-sound-design` §2.6–2.8 |
| No SFX | **Every cue frame-locked**: seam whoosh (peaks on the cut), thock on each cut, sub-boom on the three heavy beats, riser into two arrivals, kliks on every counter tick | `monarch-sound-design` §1, §2.1–2.4 |
| Mono bed | Real stereo: side channel −49 dB against mid −17.5 dB; sub folded mono below 120 Hz | `monarch-sound-design` §0 |
| No lower-third | **Data ribbon**: moving waveform, per-beat ticks, playhead — a motion-graphic element owned by the film, plus a live `BEAT 0n / 07` chip | — |

## Measured

```
duration      42.30 s      loudness  -14.17 LUFS   true peak  -1.47 dBFS
video         h264 1920x1080 @30 fps, 3660 kb/s  ·  20,414,166 bytes
audio         aac 48 kHz stereo 196 kb/s
music bed     -22.3 dB rms   ·  sfx -27.9 dB  ·  voice -11.7 dB  (voice is the clock)
cuts          6 detected (8.51 / min); shots median 5.0 s, p10 1.5 s
motion mean   0.0223 (v1 was 0.0113), peak 0.1207
pacing        "measured — essay/documentary rhythm"   (v1: "quiet 98 %")
```

## Checks

- Seam sheet reviewed frame-by-frame at every boundary (exit → blur peak → hard swap → entry).
- Audio verified by band energy, per-4 s level, and mid/side — not by trusting the mix.
- `python -m yt_intel style` on the finished file: cuts 6 / 8.51 per min, motion 0.0223.

## Rebuild

```bash
node showreel/v2/engine.mjs          # frames → ffmpeg pipe → public/demo/v2-silent.mp4  (~80 s)
.venv/bin/python showreel/v2/audio.py # → public/demo/v2-mix.wav                        (~7 s)
ffmpeg -i public/demo/v2-silent.mp4 -i public/demo/v2-mix.wav -c:v copy -c:a aac \
       -b:a 192k -shortest public/demo/a.mp4
ffmpeg -i public/demo/a.mp4 -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 \
       -c:a aac -b:a 192k -movflags +faststart public/demo/viral-short-v2.mp4
```

Beats come from `public/demo/vo/timing.json` (the measured VO timestamps). Re-record the VO and
both `engine.mjs` and `audio.py` follow it — neither file contains a hand-typed beat time.
