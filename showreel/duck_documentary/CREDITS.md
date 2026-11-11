# Documentary rough cut: credits and production notes

43.6 seconds, 720×1280, 30 fps. Moving video clips and animated geography replace the earlier cartoon edit. All source footage is illustrative, **not** the 1992 spill, the original vessel, toy recovery, or Alaska. The toy footage shows a 2022 event in France. The map's lines are conceptual and do not show individual toy trajectories or actual current measurements. The map uses Natural Earth 1:110m land polygons (public domain): https://www.naturalearthdata.com/about/terms-of-use/ .

## Video footage (cropped, excerpted, color graded, original audio removed)

- Jonathan Fielding, *Container Ship Dashcam Around The World In 70 Days* (2018), https://commons.wikimedia.org/wiki/File:Container_Ship_Dashcam_Around_The_World_In_70_Days_Timelapse,_4k,_60fps.webm, CC BY 3.0 https://creativecommons.org/licenses/by/3.0/ ; original https://www.youtube.com/watch?v=TR3aXzVJTO0 . The Commons license review is automated; third-party issues remain to be checked before publishing.
- La Télé Mobile / Sébastien Corberon, *Duck Race 2022 - Fontainebleau*, https://commons.wikimedia.org/wiki/File:Duck_Race_2022_-_Fontainebleau.webm, CC BY 3.0 https://creativecommons.org/licenses/by/3.0/ ; original https://www.youtube.com/watch?v=buQjLIAZDKg . Event footage is unrelated to the spill.
- MGA Photography, *Overhead view of waves on the shore*, https://commons.wikimedia.org/wiki/File:Overhead_view_of_waves_on_the_shore.webm, CC BY 3.0 https://creativecommons.org/licenses/by/3.0/ . This footage depicts Manly Beach, Sydney, Australia.
- NOAA Ocean Exploration, 2021 North Atlantic Stepping Stones: https://oceanexplorer.noaa.gov/ocean-fact/waves/ . Research ship footage is unrelated to the spill.

Include these credits and licence URLs in any publication description. Source footage rights and synthetic narration commercial-use terms should be reviewed before publication.

## Research

NOAA, *Mapping Friendly Floatees*: https://sanctuaries.noaa.gov/education/teachers/ocean-mysteries/mapping-floatees.html . Nearly 29,000 bath toys were spilled; avoid claiming they alone mapped the ocean.

## Render and limitations

Run `PYTHONPATH=/path/to/deps python3 showreel/duck_documentary/edit.py` with Pillow and imageio-ffmpeg installed, source clips in `showreel/duck_cinema/assets`, and the earlier narrated cut at `deliverables/monarch-invisible-thread-animated.mp4`. The narration/music come from that earlier cut. Samples were checked for visual selection; full creative polish and licensing review are still required. FFmpeg EBU R128 measured approximately -17.3 LUFS integrated and -1.5 dBTP, below the repository's -14 LUFS target. This is an editorial rough cut, not an approved premium master.
