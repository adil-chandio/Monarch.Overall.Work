# The Invisible Thread: ocean-toy motion study

Original, code-drawn 2D motion-graphics prototype and a complete 43.6-second first cut. It does not use the previous AI still plates. The ship, toy and current sequences are visual reconstructions; the current diagram and chart are conceptual, not actual tracks or observations. This is a rough first cut, not a premium finished master.

## Render

Python 3, Pillow, imageio-ffmpeg and DejaVu Sans fonts are required. The 4 narration files are deliberately not checked in; supply `vo1.wav` through `vo4.wav` with commercial-use clearance. Their timing in the full cut assumes durations of approximately 9.64, 12.46, 10.27 and 9.89 seconds respectively. A different recording may require editing the offsets and scene timings.

```sh
python -m pip install Pillow imageio-ffmpeg
python showreel/duck_pilot/render_film.py --voice-dir /path/to/narration --output /path/to/film.mp4
python showreel/duck_pilot/render.py --voice /path/to/narration/vo1.wav --output /path/to/proof.mp4
```

The renderer uses the FFmpeg executable supplied by imageio-ffmpeg. Original score and thud cues are synthesized at render time. Output is vertical 720x1280 at 30 fps. Font paths currently target Debian's `/usr/share/fonts/truetype/dejavu/`. The film is not committed as a generated binary.

## Editorial and quality notes

- [NOAA: Mapping Friendly Floatees](https://sanctuaries.noaa.gov/education/teachers/ocean-mysteries/mapping-floatees.html): 1992 North Pacific spill, approximately 29,000 bath toys, and using recovered-object locations to learn about ocean forces. The toys did not map the whole ocean.
- First cut measured at approximately -19.3 LUFS integrated / -0.9 dBTP using FFmpeg EBU R128; it has **not** passed the repo's -14 LUFS mastering target. Review and master before publication.
- Synthetic narration is supplied separately; verify the chosen provider's commercial terms and any platform disclosure requirements before publishing.
- This rough vector cut is not a 3D reconstruction and should not be represented as archival footage. Frame-by-frame competitor footage analysis was not available during research.
