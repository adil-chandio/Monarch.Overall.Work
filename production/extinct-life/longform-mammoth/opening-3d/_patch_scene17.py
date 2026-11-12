#!/usr/bin/env python3
"""Pass 17: stop making 113,000 solid clumps responsible for 100% of the wool.

The render-cost bench found the truth about this scene. On the software
rasteriser the wall cost is close to linear in triangle count — roughly 1.3 us
per triangle — and the fleece alone accounted for about 81% of every frame at
2.1 million triangles. Underfur was 40,000 clumps of the 113,000, and its only
job was to hide the gaps between the coat clumps so that the smooth hide would
not show through.

That is the wrong division of labour. A hide surface that is itself textured
as dense wool does not need a second layer of geometry to hide it, and the
coat only has to do what the coat is actually for: the shaggy silhouette and
the surface relief.

So:

  * The hide gets a procedural wool texture (mottled fibre colour plus a
    matching normal map), so any gap between clumps reads as shadowed wool
    rather than bare skin.
  * The underfur layer goes away by default.
  * The coat gets a little larger per clump so coverage is roughly preserved
    with fewer of them.

The wool texture is generated here, in code, from a hash-based value noise —
no image files, nothing imported.
"""
from pathlib import Path

SCENE = Path(__file__).with_name("scene.mjs")
s = SCENE.read_text()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n}, found {s.count(old)}: {old[:90]!r}"
    s = s.replace(old, new)


# ---------------------------------------------------------------- wool texture
sub(
    """const DOT_TEX = softDot();""",
    """const DOT_TEX = softDot();

/* ---------- procedural wool ---------- */
// A hide that is itself wool. Two textures come out of this: a mottled fibre
// colour map and a matching normal map, so the gaps between coat clumps read
// as shadowed wool instead of bare skin. That is what lets the coat be much
// sparser without the animal going bald.
function hash2(x, y) {
  let h = x * 374761393 + y * 668265263;
  h = (h ^ (h >> 13)) * 1274126177;
  return ((h ^ (h >> 16)) >>> 0) / 4294967296;
}
function vnoise(x, y) {
  const xi = Math.floor(x), yi = Math.floor(y);
  const xf = x - xi, yf = y - yi;
  const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
  const a = hash2(xi, yi), b = hash2(xi + 1, yi), c = hash2(xi, yi + 1), d = hash2(xi + 1, yi + 1);
  return (a * (1 - u) + b * u) * (1 - v) + (c * (1 - u) + d * u) * v;
}
function fbm(x, y, oct) {
  let sum = 0, amp = 0.5, f = 1;
  for (let i = 0; i < oct; i++) { sum += amp * vnoise(x * f, y * f); f *= 2.03; amp *= 0.5; }
  return sum;
}
function woolTextures(size = 512) {
  const HGT = new Float32Array(size * size);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      // Stretched noise reads as fibres lying along one direction.
      const fib = fbm(x * 0.09, y * 0.30, 4);
      const clump = fbm(x * 0.045, y * 0.045, 3);
      HGT[y * size + x] = fib * 0.68 + clump * 0.32;
    }
  }
  const col = canvasTex(size, size, (g, w, h) => {
    const img = g.createImageData(w, h);
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const i = y * w + x;
        const n = HGT[i];
        // Dark chocolate brown with warm and cool fibre variation.
        const warm = fbm(x * 0.13, y * 0.13, 3);
        const r = 74 + n * 52 + warm * 26;
        const gg = 50 + n * 38 + warm * 12;
        const b = 33 + n * 24;
        img.data[i * 4] = Math.min(255, r);
        img.data[i * 4 + 1] = Math.min(255, gg);
        img.data[i * 4 + 2] = Math.min(255, b);
        img.data[i * 4 + 3] = 255;
      }
    }
    g.putImageData(img, 0, 0);
  });
  col.wrapS = col.wrapT = T.RepeatWrapping;
  col.repeat.set(3, 3);
  const nrm = canvasTex(size, size, (g, w, h) => {
    const img = g.createImageData(w, h);
    const at = (x, y) => HGT[((y + h) % h) * w + ((x + w) % w)];
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const i = y * w + x;
        const dx = (at(x + 1, y) - at(x - 1, y)) * 2.4;
        const dy = (at(x, y + 1) - at(x, y - 1)) * 2.4;
        const len = Math.hypot(dx, dy, 1);
        img.data[i * 4] = ((-dx / len) * 0.5 + 0.5) * 255;
        img.data[i * 4 + 1] = ((-dy / len) * 0.5 + 0.5) * 255;
        img.data[i * 4 + 2] = ((1 / len) * 0.5 + 0.5) * 255;
        img.data[i * 4 + 3] = 255;
      }
    }
    g.putImageData(img, 0, 0);
  });
  nrm.wrapS = nrm.wrapT = T.RepeatWrapping;
  nrm.repeat.set(3, 3);
  return { color: col, normal: nrm };
}
const WOOL = woolTextures(512);""",
)

# ---------------------------------------------------------------- hide material
sub(
    """  const hideMat = new T.MeshStandardMaterial({ color: 0x6f5138, roughness: 0.96, metalness: 0.0 });""",
    """  // The hide is wool in its own right, so a gap between coat clumps shows
  // shadowed fibre rather than bare skin.
  const hideMat = new T.MeshStandardMaterial({
    color: 0xffffff, map: WOOL.color, normalMap: WOOL.normal,
    normalScale: new T.Vector2(1.5, 1.5), roughness: 0.96, metalness: 0.0
  });""",
)

# ---------------------------------------------------------------- coat density
sub(
    """  const surface = sampleVisible(hideParts, Math.round(62000 * PROF.coat));""",
    """  const surface = sampleVisible(hideParts, Math.round(26000 * PROF.coat));""",
)

sub(
    """  const underSurface = PROF.dropUnder ? [] : sampleVisible(hideParts, Math.round(40000 * PROF.under));""",
    """  // The underfur layer is off by default: the wool-textured hide now covers
  // the gaps that layer existed to cover, and it cost 40,000 clumps.
  const underSurface = PROF.dropUnder || PROF.under === 0
    ? []
    : sampleVisible(hideParts, Math.round(40000 * PROF.under));""",
)

# Bigger clumps so the sparser coat still reads as a full fleece.
sub(
    """    const sc = 0.019 + R() * 0.011;
    dummy.scale.set(sc, sc * (1.5 + R() * 1.3), sc);""",
    """    const sc = 0.026 + R() * 0.015;
    dummy.scale.set(sc, sc * (1.5 + R() * 1.3), sc);""",
)

SCENE.write_text(s)
print("scene.mjs patched (pass 17)")
