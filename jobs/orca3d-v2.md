# orca3d-v2

**artifacts-pending** · 1800/1800 frames (100%) · updated 2026-11-14T00:51:51.108Z

> Skill-gated rebuild of the 60s orca film: fix the missing white markings, marine snow, god rays; rebuild the sound bed from the repo DSP engine to pass showreel.audio_qc 9/9 and match the shipped showreel master within 2 dB on all 8 bands

## Resume here

```bash
OUT=/tmp/v2 CHUNK=150 TOTAL=1800 ./scripts/render-orca3d-v2.sh (skips existing parts/), then: ffmpeg mux /tmp/v2/video.mp4 + /tmp/orca-final.m4a -> upload to Drive -> job artifact/uploaded
```

## Artifacts

_none yet_

## Log

- `22:37` started: Skill-gated rebuild of the 60s orca film: fix the missing white markings, marine snow, god rays; rebuild the sound bed from the repo DSP engine to pass showreel.audio_qc 9/9 and match the shipped showreel master within 2 dB on all 8 bands
- `22:41` chunks 0-1 encoded; chunk pipeline fixed (0-based renumber, resume skip)
- `22:53` chunks 0-3 encoded (~11.7MB); chunk 4 running
- `00:51` all 12 chunks final: card 3/4, scan+flock 5/6, carousel 7 re-rendered after fixes
