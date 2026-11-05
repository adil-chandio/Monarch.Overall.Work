# 43-second re-edit: credits and verification

## Wave footage

“Overhead view of waves on the shore” by MGA Photography, https://commons.wikimedia.org/wiki/File:Overhead_view_of_waves_on_the_shore.webm — Creative Commons Attribution 3.0 Unported, https://creativecommons.org/licenses/by/3.0/ . Changes: excerpted, cropped to vertical, color-adjusted and combined with titles and audio. The footage was shot at Manly Beach, Sydney, Australia; it is illustrative only, not footage of the spill or Alaska. Attribution also appears on screen at the end. Include this complete credit in any publishing description.

Narration and music come from the prior 43-second first cut. Synthetic speech rights should be checked against the provider's terms before publication. Remaining motion graphics are stylized reconstructions / conceptual diagrams, not archival footage or precise tracks. Primary factual reference: https://sanctuaries.noaa.gov/education/teachers/ocean-mysteries/mapping-floatees.html

## Output / limitations

720x1280 at 30 fps, 43.6 seconds; this revision replaces four sections with actual moving wave footage, adds color treatment, animates on-screen text and remasters the existing mixed audio. It still uses much of the simplistic vector animation from the earlier cut, and does not constitute a premium fully rebuilt film. The mixed track measured approximately -17.3 LUFS integrated, -1.5 dBTP; it has not passed the repository's -14 LUFS target. Review and master before publishing.

## Reproduce

```
python -m pip install imageio-ffmpeg
python showreel/duck_cinema/reedit.py
```

Inputs are `deliverables/monarch-invisible-thread-animated.mp4` and `showreel/duck_cinema/assets/mga-waves-excerpt.mp4`. DejaVu Sans fonts are expected in `/usr/share/fonts/truetype/dejavu/`. The different NOAA asset in the assets folder is not used in this edit.
