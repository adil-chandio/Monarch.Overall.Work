#!/usr/bin/env python3
"""Pass 14: make the heavy fleece affordable to render.

The pass-13 scene rendered at ~7.1 s/frame on the software rasteriser, against
~1.05 s/frame for the earlier, sparser coat. At 1800 frames that is a 3.5 hour
render instead of half an hour. Two things caused it, and both are fixed here
without changing what the frame looks like:

  * Triangle count. The coat used IcosahedronGeometry (20 triangles) and there are
    62,000 of them, plus 40,000 more in the underfur layer: about 2.1 million
    triangles before the rest of the animal. OctahedronGeometry has 8 triangles
    and, at these sizes and with the tufts stretched along the surface normal,
    the two are visually indistinguishable.
  * Light count. Eight lights (hemisphere, key, rim, fill, warm, woolKey,
    woolFill, iceBounce) means eight per-fragment light evaluations for every
    clump on screen. The two redundant ones are folded into the rest.

Net: ~0.7 million triangles and six lights, with the same picture.
"""
from pathlib import Path

SCENE = Path(__file__).with_name("scene.mjs")
s = SCENE.read_text()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n}, found {s.count(old)}: {old[:90]!r}"
    s = s.replace(old, new)


# ---------------------------------------------------------------- 1. cheaper tufts
sub(
    """  const clumpGeo = new T.IcosahedronGeometry(1, 0);""",
    """  // Octahedron: 8 triangles against the icosahedron's 20. At tuft size the two
  // are indistinguishable, and this scene is rasterised in software.
  const clumpGeo = new T.OctahedronGeometry(1, 0);""",
)

sub(
    """  const underGeo = new T.IcosahedronGeometry(1, 0);""",
    """  const underGeo = new T.OctahedronGeometry(1, 0);""",
)

# Slightly larger tufts compensate for the cheaper shape and keep the coat dense.
sub(
    """    const sc = 0.017 + R() * 0.010;
    dummy.scale.set(sc, sc * (1.5 + R() * 1.3), sc);""",
    """    const sc = 0.019 + R() * 0.011;
    dummy.scale.set(sc, sc * (1.5 + R() * 1.3), sc);""",
)

sub(
    """    const sc = 0.009 + R() * 0.008;
    dummy.scale.set(sc, sc * (1.3 + R() * 1.1), sc);""",
    """    const sc = 0.010 + R() * 0.009;
    dummy.scale.set(sc, sc * (1.3 + R() * 1.1), sc);""",
)

# ---------------------------------------------------------------- 2. fewer lights
sub(
    """const fill = new T.DirectionalLight(0x4f83ad, 0.78); fill.position.set(5, 4, 12); scene.add(fill);
const warm = new T.PointLight(0xffb070, 5, 22, 2); warm.position.set(-2.2, 2.4, 2.2); scene.add(warm);""",
    """// The cool front fill and the warm bounce are folded into the hemisphere and the
// wool rig: eight lights meant eight per-fragment light evaluations per clump.
const warm = new T.PointLight(0xffb070, 5, 22, 2); warm.position.set(-2.2, 2.4, 2.2); scene.add(warm);""",
)

sub(
    """const woolKey = new T.DirectionalLight(0xffe0bd, 2.35); woolKey.position.set(-9, 5.2, 11); scene.add(woolKey);
const woolFill = new T.DirectionalLight(0x8fb6d8, 0.95); woolFill.position.set(7.5, 1.6, 9); scene.add(woolFill);
const iceBounce = new T.PointLight(0xbcd6ea, 1.5, 11, 2); iceBounce.position.set(-0.6, 1.6, 4.6); scene.add(iceBounce);""",
    """const woolKey = new T.DirectionalLight(0xffe0bd, 2.5); woolKey.position.set(-9, 5.2, 11); scene.add(woolKey);
const woolFill = new T.DirectionalLight(0x8fb6d8, 1.15); woolFill.position.set(7.5, 1.6, 9); scene.add(woolFill);""",
)

# the removed fill light contributed its cool tone to the hemisphere
sub(
    """scene.add(new T.HemisphereLight(0x9cc4e0, 0x101d28, 0.78));""",
    """scene.add(new T.HemisphereLight(0x9cc4e0, 0x16222e, 0.92));""",
)

sub(
    """  // The wool rig leans in as the camera closes on the animal.
  const close = kind === 'shoulder' ? 1 : kind === 'resolve' ? 0.7 : 0.42;
  woolKey.intensity = 2.35 * close;
  woolFill.intensity = 0.95 * close;
  iceBounce.intensity = 1.5 * close;""",
    """  // The wool rig leans in as the camera closes on the animal.
  const close = kind === 'shoulder' ? 1 : kind === 'resolve' ? 0.7 : 0.42;
  woolKey.intensity = 2.5 * close;
  woolFill.intensity = 1.15 * close;""",
)

SCENE.write_text(s)
print("scene.mjs patched (pass 14)")
