# orca3d-v2

**running** · 0/1800 frames (0%) · updated 2026-11-13T22:37:14.600Z

> Skill-gated rebuild of the 60s orca film: fix the missing white markings, marine snow, god rays; rebuild the sound bed from the repo DSP engine to pass showreel.audio_qc 9/9 and match the shipped showreel master within 2 dB on all 8 bands

## Resume here

```bash
OUT=/tmp/v2 CHUNK=150 TOTAL=1800 ./scripts/render-orca3d-v2.sh (skips existing parts/), then: ffmpeg mux /tmp/v2/video.mp4 + /tmp/orca-final.m4a -> upload to Drive -> job artifact/uploaded
```

## Artifacts

_none yet_

## Log

- `22:37` started: Skill-gated rebuild of the 60s orca film: fix the missing white markings, marine snow, god rays; rebuild the sound bed from the repo DSP engine to pass showreel.audio_qc 9/9 and match the shipped showreel master within 2 dB on all 8 bands
