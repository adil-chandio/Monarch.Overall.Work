# No-stock 2.5D cut

This 43.6-second cut uses **no stock footage, A-roll or B-roll**. All visual frames are assembled from a procedural animated ocean, keyed AI-generated ship, toy and container layers, independently animated particles, kinetic text, and a map drawn from Natural Earth geographical data. The cutouts are reused across shots, and motion is 2.5D compositing, not full 3D simulation. All shipping and toy imagery is stylized reconstruction. Ocean-current lines are conceptual, not verified toy trajectories. Approximately 29,000 toys included types other than ducks.

Narration and the original synthesized musical bed are extracted from the audio stream of the previous first cut; that cut's visual stream is not used. Additional transition cues are procedurally synthesized. Source narration is AI-generated; verify commercial-use terms and applicable platform disclosure requirements before publishing. Primary story source: https://sanctuaries.noaa.gov/education/teachers/ocean-mysteries/mapping-floatees.html . Map geography: Natural Earth, public domain, https://www.naturalearthdata.com/about/terms-of-use/ .

## Render

```
python -m pip install pillow numpy imageio-ffmpeg
python showreel/duck_parallax/render_no_stock.py --output deliverables/monarch-ducks-25d-original.mp4
```

Requires the three cutout files under `showreel/duck_parallax/assets`, the map data under `showreel/duck_documentary`, DejaVu fonts, and an audio source (default is the previous original cut). Output: 720x1280, 30 fps, 1308 frames. The audio mix measured -16.3 LUFS integrated / -1.4 dBTP using FFmpeg EBU R128; it is below the repo's -14 LUFS target. The file is a draft, not a claim of flawless or publication-ready quality; a further full visual review, audio mastering and rights check remain necessary.
