# The Invisible Thread — 2.5D rough cut

A frame-driven 43.6-second vertical reconstruction, not a finished premium master. The ship, floating toys, foreground wave lines, camera-relative positioning, headline entrance and map flow are independently animated layers. The ship and duck are AI-generated cutout assets; they are not archival footage. The approximate toy count includes other types of bath toy. Current lines and particles are conceptual and do **not** depict verified toy tracks.

## Credits / publication

Ocean background: MGA Photography, “Overhead view of waves on the shore”, https://commons.wikimedia.org/wiki/File:Overhead_view_of_waves_on_the_shore.webm, https://creativecommons.org/licenses/by/3.0/ . Changed: excerpted, cropped, recolored and combined with other animation/audio. It depicts Manly Beach, Australia, and is only a visual texture; it is not the spill site. Include this complete attribution and licence URL in the video description on publication.

Geography: Natural Earth 1:110m land, https://www.naturalearthdata.com/about/terms-of-use/ (public domain). Primary story reference: NOAA, https://sanctuaries.noaa.gov/education/teachers/ocean-mysteries/mapping-floatees.html . Generated imagery and synthetic speech: confirm their provider's terms and relevant platform disclosure rules before publication. Narration/music reuse the prior first cut.

## Render

```
python -m pip install pillow numpy imageio-ffmpeg
python showreel/duck_parallax/render.py --output deliverables/monarch-ducks-25d-preview.mp4
```

Inputs: `assets/duck.png`, `assets/ship.png`, `showreel/duck_cinema/assets/mga-waves-excerpt.mp4`, `showreel/duck_documentary/natural_earth_110m_land.geojson` and `deliverables/monarch-invisible-thread-animated.mp4`. The renderer uses Linux DejaVu fonts. Source video and narration are required separately, and multiple scenes deliberately reuse their visual assets.

## Quality / limitations

720×1280, 30 fps; one background texture and recurring cutouts, not a full 3D simulation. The actual preview measures approximately -17.3 LUFS integrated and -1.5 dBTP (FFmpeg EBU R128), short of the repo's -14 LUFS target. Further sound mastering, detailed shot-by-shot creative review and rights checks are needed before publishing. This is a rough visual treatment and does not establish any retention or performance result.
