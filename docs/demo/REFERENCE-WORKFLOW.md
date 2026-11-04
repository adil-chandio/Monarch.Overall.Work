# Reference-video workflow

1. Put the reference in `refs/` (gitignored if large).
2. `python3 tools/analyse_ref.py refs/<name>.mp4`
3. Read `analysis/<name>/report.md`, then look at `strip_cuts.png` and the `zoom_*.png` files.
4. Rebuild in `showreel/<vN>/index.html`, then diff the rebuild by running the same script on it:
   `python3 tools/analyse_ref.py public/demo/<vN>.mp4 --out analysis/<vN>_rebuild`
   and comparing `report.json` against the reference (cuts, shot length, palette, loudness).
