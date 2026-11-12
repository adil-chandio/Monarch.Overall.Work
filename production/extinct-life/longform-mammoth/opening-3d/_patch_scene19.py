#!/usr/bin/env python3
"""Pass 19 (applied): underfur off by default; clump primitive selectable.

The triangle audit showed 1.42 million triangles per frame, of which 800,000
came from the 40,000-clump underfur layer. Pass 17 meant to drop that layer
but only dropped it when a profile asked for it, so the default render was
still paying for it. It is off now: the hide carries a wool texture, so a gap
between coat clumps shows shadowed fibre rather than bare skin.

The clump primitive is selectable, because it is the biggest lever left and it
has to be judged by eye, not by a number. At the size these clumps occupy on
screen they are a few pixels across, and a low-triangle primitive may read
identically to the 20-triangle icosahedron.

  ?clumpgeom=ico|octa|tetra|cone
"""
from pathlib import Path

SCENE = Path(__file__).with_name("scene.mjs")
s = SCENE.read_text()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n}, found {s.count(old)}: {old[:90]!r}"
    s = s.replace(old, new)


sub(
    """  under: qn('under', 1),""",
    """  under: qn('under', 0),""",
)

sub(
    """  clump: qn('clump', 1),""",
    """  clump: qn('clump', 1),
  clumpGeom: QS.get('clumpgeom') || 'ico',""",
)

sub(
    """  // Icosahedron: 20 triangles. A scaled octahedron is a bipyramid and reads as
  // a spike, not a wool curl, so the rounder primitive stays.
  const clumpGeo = new T.IcosahedronGeometry(1, 0);""",
    """  // Clump primitive. The icosahedron is the shape that reads as a wool curl,
  // but at 20 triangles it is the most expensive thing in the frame, so the
  // alternatives are measured and judged by eye rather than assumed.
  const CLUMP = {
    ico: () => new T.IcosahedronGeometry(1, 0),
    octa: () => new T.OctahedronGeometry(1, 0),
    tetra: () => new T.TetrahedronGeometry(1, 0),
    cone: () => new T.ConeGeometry(0.62, 1.5, 5, 1, true),
  };
  const clumpGeo = (CLUMP[PROF.clumpGeom] || CLUMP.ico)();""",
)

SCENE.write_text(s)
print("scene.mjs patched (pass 19)")
