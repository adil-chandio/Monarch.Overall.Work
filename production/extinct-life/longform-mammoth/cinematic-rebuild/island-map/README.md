# Wrangel region 3D map — present-day outline only

This is an unintegrated scene/asset, **not the completed film**. The coastlines are modern. They must not be shown as a precise reconstruction of the shoreline at isolation ~10,000 years ago. The sea, flat land extrusion, colours, camera, relief and labels are an illustrative design, not measured bathymetry or topography. The map uses a local equirectangular approximation around 70°N, so distances elsewhere are distorted; it has not had geographic or scientific expert review. It still needs an actual storytelling edit, contextual geography, sound, integration and quality review.

`wrangel-modern-land.geojson` is a clipped/simplified derivative of [Natural Earth 1:10m land](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_10m_land.geojson), Git blob `2d76878175b8054acd9c5a52917ee9ea59a36fc5`, downloaded source SHA-256 `1ac90796408bc6ad6911d69448485d3c4dbf2190370080368a09976e1c9f7416`. Natural Earth calls its vector data public domain: https://www.naturalearthdata.com/about/terms-of-use/ . The map joins the two pieces of Wrangel split by the 180° meridian and displays longitudes as 0–360°. “Made with Natural Earth.”

Recreate the extract with Python/Shapely and the exact source file:

```
.venv/bin/python production/extinct-life/longform-mammoth/cinematic-rebuild/island-map/extract.py /path/to/ne_10m_land.geojson
node production/extinct-life/longform-mammoth/cinematic-rebuild/island-map/inspect.mjs
```

Inspection images go to ignored `.cache/mammoth-island-map`. Deterministic rendering tests do not confirm the map's science or creative suitability.

A provisional 360-frame silent review clip can be rendered with `node production/extinct-life/longform-mammoth/cinematic-rebuild/island-map/render-preview.mjs 360`. It remains modern-coastline-only and is not an approved film shot.
