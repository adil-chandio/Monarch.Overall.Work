#!/usr/bin/env python3
"""Pass 18: expose the clump size so the fleece density/size trade-off can be
measured and judged side by side.

Pass 17 cut the coat to 26,000 clumps of 0.026-0.041 radius and the result
reads as popcorn rather than fleece: the clumps are simply too large. The
trade-off is real and worth measuring — more clumps cost linearly in triangles,
larger clumps cost fill — so the size and the count both need to be adjustable
while the picture is judged.
"""
from pathlib import Path

SCENE = Path(__file__).with_name("scene.mjs")
s = SCENE.read_text()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n}, found {s.count(old)}: {old[:90]!r}"
    s = s.replace(old, new)


sub(
    """  shag: qn('shag', 1),""",
    """  shag: qn('shag', 1),
  clump: qn('clump', 1),
  hideTex: QS.get('hidetex') !== '0',""",
)

# Hide texture can be switched off for comparison.
sub(
    """  const hideMat = new T.MeshStandardMaterial({
    color: 0xffffff, map: WOOL.color, normalMap: WOOL.normal,
    normalScale: new T.Vector2(1.5, 1.5), roughness: 0.96, metalness: 0.0
  });""",
    """  const hideMat = PROF.hideTex
    ? new T.MeshStandardMaterial({
      color: 0xffffff, map: WOOL.color, normalMap: WOOL.normal,
      normalScale: new T.Vector2(1.5, 1.5), roughness: 0.96, metalness: 0.0
    })
    : new T.MeshStandardMaterial({ color: 0x6f5138, roughness: 0.96, metalness: 0.0 });""",
)

# Clump size is a multiplier on the base radius.
sub(
    """    const sc = 0.026 + R() * 0.015;
    dummy.scale.set(sc, sc * (1.5 + R() * 1.3), sc);""",
    """    const sc = (0.021 + R() * 0.012) * PROF.clump;
    dummy.scale.set(sc, sc * (1.5 + R() * 1.3), sc);""",
)

SCENE.write_text(s)
print("scene.mjs patched (pass 18)")
