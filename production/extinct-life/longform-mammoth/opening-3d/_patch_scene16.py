#!/usr/bin/env python3
"""Pass 16: make the render cost configurable so it can be measured, then priced.

The bench (_bench.mjs, _bench2.mjs, _microbench.mjs) showed the opening's wall
cost is dominated by the wool coat: about 81% of every frame, and about 90% of
that is fill (fragment) cost rather than vertex cost. 113,000 instanced clumps,
each shaded by a full PBR MeshStandardMaterial under six lights, is simply too
much for a software rasteriser on two cores.

This pass does not change the picture on its own. It exposes the knobs that
control cost — anti-aliasing, fur material, light count, fur density — behind
URL parameters so each combination can be rendered and measured for real, in
the actual scene, before anything is committed as the production default.

  ?aa=0            disable MSAA
  ?furmat=basic    MeshBasicMaterial for the coat (lambert|standard also allowed)
  ?lights=N        keep only the first N lights
  ?coat=0.5        halve the coat density (underfur scales with it)
  ?under=0         drop the underfur layer entirely
  ?shag=0          drop the guard-hair layer entirely
"""
from pathlib import Path

SCENE = Path(__file__).with_name("scene.mjs")
s = SCENE.read_text()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n}, found {s.count(old)}: {old[:90]!r}"
    s = s.replace(old, new)


# ---------------------------------------------------------------- perf profile
sub(
    """const S = await (await fetch('/timeline.json')).json();
const W = S.width, H = S.height, FPS = S.fps;""",
    """const S = await (await fetch('/timeline.json')).json();
const W = S.width, H = S.height, FPS = S.fps;

// Render-cost profile. Defaults are the production values; the query string
// only exists so the cost of each option can be measured in the real scene
// before it is adopted. See _bench3.mjs.
const QS = new URLSearchParams(location.search);
const qn = (k, d) => (QS.has(k) ? parseFloat(QS.get(k)) : d);
const PROF = {
  aa: QS.get('aa') !== '0',
  furMat: QS.get('furmat') || 'standard',
  lights: qn('lights', 6),
  coat: qn('coat', 1),
  under: qn('under', 1),
  shag: qn('shag', 1),
  dropUnder: QS.get('under') === '0',
  dropShag: QS.get('shag') === '0',
};""",
)

# ---------------------------------------------------------------- renderer
sub(
    """const renderer = new T.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true, powerPreference: 'high-performance' });""",
    """const renderer = new T.WebGLRenderer({ antialias: PROF.aa, preserveDrawingBuffer: true, powerPreference: 'high-performance' });""",
)

# ---------------------------------------------------------------- lights
sub(
    """scene.add(new T.HemisphereLight(0x9cc4e0, 0x16222e, 0.92));""",
    """const lightRig = [];
lightRig.push(new T.HemisphereLight(0x9cc4e0, 0x16222e, 0.92));
scene.add(lightRig[0]);""",
)

sub(
    """const key = new T.DirectionalLight(0xffcf9c, 3.1); key.position.set(9, 3.4, -26); scene.add(key);""",
    """const key = new T.DirectionalLight(0xffcf9c, 3.1); key.position.set(9, 3.4, -26); lightRig.push(key); scene.add(key);""",
)

sub(
    """const rim = new T.DirectionalLight(0x9fd4ff, 1.9); rim.position.set(-13, 7, -14); scene.add(rim);""",
    """const rim = new T.DirectionalLight(0x9fd4ff, 1.9); rim.position.set(-13, 7, -14); lightRig.push(rim); scene.add(rim);""",
)

sub(
    """const warm = new T.PointLight(0xffb070, 5, 22, 2); warm.position.set(-2.2, 2.4, 2.2); scene.add(warm);""",
    """const warm = new T.PointLight(0xffb070, 5, 22, 2); warm.position.set(-2.2, 2.4, 2.2); lightRig.push(warm); scene.add(warm);""",
)

sub(
    """const woolKey = new T.DirectionalLight(0xffe0bd, 2.5); woolKey.position.set(-9, 5.2, 11); scene.add(woolKey);""",
    """const woolKey = new T.DirectionalLight(0xffe0bd, 2.5); woolKey.position.set(-9, 5.2, 11); lightRig.push(woolKey); scene.add(woolKey);""",
)

sub(
    """const woolFill = new T.DirectionalLight(0x8fb6d8, 1.15); woolFill.position.set(7.5, 1.6, 9); scene.add(woolFill);""",
    """const woolFill = new T.DirectionalLight(0x8fb6d8, 1.15); woolFill.position.set(7.5, 1.6, 9); lightRig.push(woolFill); scene.add(woolFill);""",
)

# Apply the light budget once the rig is complete.
sub(
    """/* ---------- DNA helix ---------- */""",
    """// Light budget: only the first PROF.lights lights are switched on.
lightRig.forEach((l, i) => { l.visible = i < PROF.lights; });

/* ---------- DNA helix ---------- */""",
)

# ---------------------------------------------------------------- fur material
sub(
    """  const furMat = new T.MeshStandardMaterial({ color: 0x9a7550, roughness: 0.92, metalness: 0.0 });
  const shagMat = new T.MeshStandardMaterial({ color: 0x8e6b47, roughness: 0.95, metalness: 0.0, transparent: true });""",
    """  // Wool is matte. Under a software rasteriser the PBR branch (roughness,
  // metalness, IBL) costs far more than it adds on a diffuse fleece, so the
  // material class is a measured choice, not a default.
  const furMat = PROF.furMat === 'basic'
    ? new T.MeshBasicMaterial({ color: 0x9a7550 })
    : PROF.furMat === 'lambert'
      ? new T.MeshLambertMaterial({ color: 0x9a7550 })
      : new T.MeshStandardMaterial({ color: 0x9a7550, roughness: 0.92, metalness: 0.0 });
  const shagMat = PROF.furMat === 'basic'
    ? new T.MeshBasicMaterial({ color: 0x8e6b47, transparent: true })
    : PROF.furMat === 'lambert'
      ? new T.MeshLambertMaterial({ color: 0x8e6b47, transparent: true })
      : new T.MeshStandardMaterial({ color: 0x8e6b47, roughness: 0.95, metalness: 0.0, transparent: true });""",
)

# ---------------------------------------------------------------- fur density
sub(
    """  const surface = sampleVisible(hideParts, 62000);""",
    """  const surface = sampleVisible(hideParts, Math.round(62000 * PROF.coat));""",
)

sub(
    """  const underSurface = sampleVisible(hideParts, 40000);""",
    """  const underSurface = PROF.dropUnder ? [] : sampleVisible(hideParts, Math.round(40000 * PROF.under));""",
)

sub(
    """  const shagSurface = sampleVisible(hideParts, 11000);""",
    """  const shagSurface = PROF.dropShag ? [] : sampleVisible(hideParts, Math.round(11000 * PROF.shag));""",
)

SCENE.write_text(s)
print("scene.mjs patched (pass 16)")
