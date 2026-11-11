# Final crossing — closing landscape, unfinished 3D

A 13-second closing sequence: four instances of the third-party rigged mammoth
(see `../mammoth-rig/README.md`) cross a snow plain at low sun and walk out of
frame; the camera descends and settles on a single footprint they left. It is an
illustrative motif returning to the opening landscape, **not** a specific herd,
season, weather or documented event, and not a reconstruction of Wrangel.

## What is real and what is invented

- **Ground, ridge, snowbanks and sea:** generated geometry with a shader water
  strip. Shapes, distances and the horizon are invented; there is no bathymetry,
  sea-level reconstruction or measured coastline.
- **Animals:** one shared mesh at four scales and headings, driven by the
  hand-authored in-place walk cycle and translated along a straight path. The
  stated speed is an approximation; it is not gait analysis, and there is no
  terrain conforming, foot sinking, fur physics or herd behaviour simulation.
- **Footprint:** a painted impression decal (pale pressed sole, four toe lobes, a
  lit pushed-up rim and a cool interior). It is **stylised and oversized for
  legibility**; it is not a measured specimen, a cast, or simulated snow
  deformation. It does not claim to be a real print from Wrangel.
- **Light and grade:** a low warm key, cool hemisphere fill, a soft vignette and
  a warm soft-light pass are applied in the page. The result is a stylised render.

## Review status

Four stills were inspected and the framing was revised repeatedly (footprint
legibility, herd spacing, horizon seam, light direction). The **full 13 seconds
has not been continuously viewed**, and the crossing has not been checked frame by
frame for foot sliding, ground contact or animal-to-animal collision. The closing
composition, the print's scale and the herd's apparent speed all need human review.

```
node production/extinct-life/longform-mammoth/cinematic-rebuild/final-crossing/inspect.mjs
node production/extinct-life/longform-mammoth/cinematic-rebuild/final-crossing/render-preview.mjs 390
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/edit/build_insert.py final-crossing
```

`inspect.mjs` checks deterministic seeks, page errors, four animals with the
expected triangle count, six print decals, and that the lead animal moves to the
right across the sequence. Those are structural checks, not art or science review.
Renders and workprints live in `.cache/` and are not deliverables.
