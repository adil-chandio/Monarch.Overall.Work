#!/usr/bin/env python3
"""Pass 15: restore the fleece silhouette and open a measurement hook.

Pass 14 swapped the wool clumps from icosahedra (20 triangles) to octahedra
(8 triangles) to cut the triangle bill. The stills show the octahedron reads as
a spiky lollipop rather than a fleece: a scaled octahedron is a bipyramid, so
stretching it along the surface normal makes a spike. The icosahedron is the
shape that actually reads as wool, so it goes back.

Pass 14 also dropped two lights. That is kept, but the scene now exposes a
debug handle so the cost of the fleece can be measured instead of guessed at.
"""
from pathlib import Path

SCENE = Path(__file__).with_name("scene.mjs")
s = SCENE.read_text()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n}, found {s.count(old)}: {old[:90]!r}"
    s = s.replace(old, new)


# ---------------------------------------------------------------- wool shape back
sub(
    """  // Octahedron: 8 triangles against the icosahedron's 20. At tuft size the two
  // are indistinguishable, and this scene is rasterised in software.
  const clumpGeo = new T.OctahedronGeometry(1, 0);""",
    """  // Icosahedron: 20 triangles. A scaled octahedron is a bipyramid and reads as
  // a spike, not a wool curl, so the rounder primitive stays.
  const clumpGeo = new T.IcosahedronGeometry(1, 0);""",
)

sub(
    """  const underGeo = new T.OctahedronGeometry(1, 0);""",
    """  const underGeo = new T.IcosahedronGeometry(1, 0);""",
)

# ---------------------------------------------------------------- debug handle
sub(
    """window.__seek = paint;
window.__ready = true;""",
    """window.__seek = paint;
window.__ready = true;
// Measurement handle for the render-cost bench (see _bench.mjs). Read-only
// pointers; nothing in the film path depends on it.
window.__dbg = { scene, renderer, camera, T };""",
)

SCENE.write_text(s)
print("scene.mjs patched (pass 15)")
