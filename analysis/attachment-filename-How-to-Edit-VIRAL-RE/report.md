# attachment-filename-How-to-Edit-VIRAL-REELS-Animations-in-After-Effects-_-Full-t.mp4

## Container

- **720x1280 (9:16)**, 30.0 fps, 23.35 s, 3,244,599 bytes
- video h264 / yuv420p / 980 kb/s / tv, bt709, progressive
- audio aac / 44100 Hz / stereo / 127 kb/s

## Edit

- **13 cuts** (33.4/min); ffmpeg scene-score second opinion: 11
- shot length median **0.42 s** (p10 0.23, p90 4.97, longest 8.55)
- hook: 4 cut(s) in 3 s, first cut 0.533, first-second motion 0.1079
- detector: changed-px x histogram-distance x cut-shape, Otsu threshold 0.7365 over 699 frame pairs

| # | time | transition | dur | sharpness | changed px |
|---|---|---|---|---|---|
| 1 | 0.533s | hard cut | 0.033s | 1.961 | 0.9805 |
| 2 | 0.833s | dissolve | 0.5s | 1.9407 | 0.9704 |
| 3 | 1.0s | dissolve | 0.43s | 0.977 | 0.8456 |
| 4 | 1.3s | dissolve | 0.27s | 1.244 | 0.7554 |
| 5 | 3.133s | hard cut | 0.033s | 1.9503 | 0.9752 |
| 6 | 9.133s | hard cut | 0.033s | 1.127 | 0.6943 |
| 7 | 11.7s | hard cut | 0.033s | 1.6368 | 0.8184 |
| 8 | 12.167s | hard cut | 0.033s | 1.9847 | 0.9923 |
| 9 | 12.467s | dissolve | 0.5s | 1.9525 | 0.9763 |
| 10 | 12.667s | dissolve | 0.43s | 0.9544 | 0.7945 |
| 11 | 12.967s | dissolve | 0.5s | 1.6671 | 0.8443 |
| 12 | 13.333s | dissolve | 0.37s | 0.7403 | 0.5885 |
| 13 | 14.8s | hard cut | 0.033s | 1.9952 | 0.9976 |

## Look

- saturation 0.5066 · luma 68.17 (σ 68.21) · dark 50% · blown 6%
- motion mean 0.0566 / peak 1.0 · static 92% of frames
- edge density (type proxy) mean 1.6469, peak 2.6927 at 14.53s
- dominant hue bands: 0-30deg 68%, 330-360deg 18%, 60-90deg 7%, 30-60deg 2%
- palette: `#140a0a` 37%, `#bcbbba` 18%, `#480605` 14%, `#710909` 13%, `#453e36` 10%, `#927b5e` 8%

## Sound

- RMS -13.03 dBFS · decoded peak 2.45 dBFS · crest 15.49 dB
- **no stable tempo grid** (best candidate 70.0 BPM at score 0.076) — so: cut to speech, not to a beat

## Loudness — rebuild to this

- integrated **-14.02 LUFS** · true peak -0.31 dBTP · LRA 1.7

## Artifacts

- `sheet_3x3.png` — nine frames, the arc at a glance
- `strip_cuts.png` — frames either side of each cut (±0.48 s): the transition itself
- `zoom_t*.png` — 10x zooms of the four quadrants at 6%, 50%, 94%
- `palette.png`, `waveform.png`, `motion.png` — colour, sound, pacing as pictures
- `report.json` — every number above, for diffing the rebuild

