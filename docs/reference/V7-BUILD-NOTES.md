# V7 build and verification

A+B+C+D were approved together, with reference-weight sound and opening/replay flashes.
The candidate is `public/demo/v7-01.mp4`. It is assembled from our own image layers and
procedurally generated audio, not reference pixels or samples.

## What changed

- `spec/v7-01.json` revises the cut timings, removes dissolves at the cut points, and
  replaces the replay's unrelated macro with the green field and bag.
- `tools/v7.py` is a separate renderer: crop-camera punches, jitter, layered room,
  retimed words, and rounded translucent CTA. Room orbit is reduced. The unsuitable
  floating hands/cash cutout was removed after full-size review.
- `tools/v7_audio.py` generates an original deterministic 120 BPM score: 808, kick,
  hats, snare, separate ducked bed and impacts, sub drops and sweeps. The mastered AAC
  is normalized via the explicit gain in the instructions below.

## Checks performed

- 720x1280 H.264, 30 fps, **698 frames**, 23.267 s; 48 kHz stereo AAC. Full decode
  completed without errors. Final encoded-audio true peak measured **−0.6 dBTP** with
  FFmpeg ebur128 (target was −0.5 dBTP).
- Full-resolution frames reviewed at 1.05, 1.90, 12.85, 16.5, 18.0 and 21.95 s;
  after removing the floating hands, 4.9 and 16.5 s were checked again. CTA does not
  cover the face. This is not a substitute for judging motion and sound by playback.
- Optical-flow spot check on the finished render (same downscaled LK method as the
  forensic pass): field 0.93–1.30: ~259 px/s; storm 1.8–2.9: ~30 px/s, jitter
  ~7 px/frame; room 3.2–8.9: ~8 px/s, jitter ~4 px/frame; replay field 12.6–12.9:
  ~452 px/s; storm 13.0–14.5: ~26 px/s. These estimates depend on shot boundaries
  and tracking; **they do not demonstrate a match to REF motion**. In particular the
  room and storm remain substantially less dynamic than the earlier REF estimates.
- The room uses layered 2.5D compositing, not a true 3D scene. The reference's phone
  beat has no suitable original plate here and is not reproduced. The score is an
  original approximation, not the REF music. These remain quality limitations, not
  verified matches.

## Reproduce

Requires NumPy, SciPy, OpenCV, the repository assets/fonts, and the FFmpeg located by
`tools/ffbin.py`. The paths under `/tmp` are intermediates, not source assets.

```sh
python3 tools/v7.py --spec spec/v7-01.json --out /tmp/v7-video.mp4 --crf 17
python3 tools/v7_audio.py --out /tmp/v7-score.wav
FF=$(python3 -c 'import sys;sys.path.insert(0,"tools");from ffbin import ffmpeg;print(ffmpeg())')
"$FF" -v error -y -i /tmp/v7-score.wav -af volume=0.8dB -c:a aac -b:a 192k /tmp/v7-audio.m4a
"$FF" -v error -y -i /tmp/v7-video.mp4 -i /tmp/v7-audio.m4a -map 0:v:0 -map 1:a:0 -c copy -movflags +faststart public/demo/v7-01.mp4
"$FF" -v error -i public/demo/v7-01.mp4 -f null -
"$FF" -hide_banner -i public/demo/v7-01.mp4 -filter_complex ebur128=peak=true -f null -
```
