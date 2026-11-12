#!/usr/bin/env python3
"""Pass 20: a light budget with priority, and a material choice for the hide.

Two things the render-cost bench settled:

  * Light count is a real cost, but dropping lights blindly changes the
    picture. The rig now has a priority order, so a budget of N keeps the N
    most important lights and compensates the survivors with extra intensity
    rather than just going dark.
  * Wool is matte. The PBR branch (roughness, metalness, IBL, GGX) costs far
    more than it adds on a diffuse fleece under six lights, so the fur and
    hide material class is a measured choice exposed as ?furmat=.
"""
from pathlib import Path

SCENE = Path(__file__).with_name("scene.mjs")
s = SCENE.read_text()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n}, found {s.count(old)}: {old[:90]!r}"
    s = s.replace(old, new)


# ---------------------------------------------------------------- profile
sub(
    """  hideTex: QS.get('hidetex') !== '0',
  dropShag: QS.get('shag') === '0',
};""",
    """  hideTex: QS.get('hidetex') !== '0',
  dropShag: QS.get('shag') === '0',
  hideMat: QS.get('hidemat') || 'standard',
};""",
)

# ---------------------------------------------------------------- light rig
sub(
    """const lightRig = [];
lightRig.push(new T.HemisphereLight(0x9cc4e0, 0x16222e, 0.92));
scene.add(lightRig[0]);""",
    """// Light rig with a priority order. A budget of N keeps the N most important
// lights and brightens the survivors, so cutting the count costs triangles
// and fill, not exposure.
const lightRig = [];
const rigBase = [];
const rigPush = (light, priority) => {
  light.userData.priority = priority;
  lightRig.push(light); rigBase.push(light.intensity);
  scene.add(light);
};
rigPush(new T.HemisphereLight(0x9cc4e0, 0x16222e, 0.92), 1);""",
)

sub(
    """const key = new T.DirectionalLight(0xffcf9c, 3.1); key.position.set(9, 3.4, -26); lightRig.push(key); scene.add(key);""",
    """const key = new T.DirectionalLight(0xffcf9c, 3.1); key.position.set(9, 3.4, -26); rigPush(key, 2);""",
)

sub(
    """const rim = new T.DirectionalLight(0x9fd4ff, 1.9); rim.position.set(-13, 7, -14); lightRig.push(rim); scene.add(rim);""",
    """const rim = new T.DirectionalLight(0x9fd4ff, 1.9); rim.position.set(-13, 7, -14); rigPush(rim, 4);""",
)

sub(
    """const warm = new T.PointLight(0xffb070, 5, 22, 2); warm.position.set(-2.2, 2.4, 2.2); lightRig.push(warm); scene.add(warm);""",
    """const warm = new T.PointLight(0xffb070, 5, 22, 2); warm.position.set(-2.2, 2.4, 2.2); rigPush(warm, 5);""",
)

sub(
    """const woolKey = new T.DirectionalLight(0xffe0bd, 2.5); woolKey.position.set(-9, 5.2, 11); lightRig.push(woolKey); scene.add(woolKey);""",
    """const woolKey = new T.DirectionalLight(0xffe0bd, 2.5); woolKey.position.set(-9, 5.2, 11); rigPush(woolKey, 3);""",
)

sub(
    """const woolFill = new T.DirectionalLight(0x8fb6d8, 1.15); woolFill.position.set(7.5, 1.6, 9); lightRig.push(woolFill); scene.add(woolFill);""",
    """const woolFill = new T.DirectionalLight(0x8fb6d8, 1.15); woolFill.position.set(7.5, 1.6, 9); rigPush(woolFill, 6);""",
)

# Apply the budget: keep the highest-priority lights, brighten the survivors.
sub(
    """// Light budget: only the first PROF.lights lights are switched on.
lightRig.forEach((l, i) => { l.visible = i < PROF.lights; });""",
    """// Light budget. The most important lights are kept; the rest are switched
// off and the survivors are brightened to keep the exposure roughly where it
// was, so the picture changes far less than the frame time does.
{
  const order = lightRig
    .map((l, i) => ({ l, i, p: l.userData.priority }))
    .sort((a, b) => a.p - b.p);
  const keep = new Set(order.slice(0, Math.max(1, Math.round(PROF.lights))).map((o) => o.i));
  lightRig.forEach((l, i) => {
    l.visible = keep.has(i);
    l.userData.gain = keep.has(i) ? Math.pow(2, (order.length - keep.size) / order.length * 0.42) : 0;
  });
}""",
)

# The per-shot wool rig now scales the boosted intensity.
sub(
    """  woolKey.intensity = 2.5 * close;
  woolFill.intensity = 1.15 * close;""",
    """  woolKey.intensity = 2.5 * close * (woolKey.userData.gain || 1);
  woolFill.intensity = 1.15 * close * (woolFill.userData.gain || 1);""",
)

# ---------------------------------------------------------------- hide material
sub(
    """  const hideMat = PROF.hideTex
    ? new T.MeshStandardMaterial({
      color: 0xffffff, map: WOOL.color, normalMap: WOOL.normal,
      normalScale: new T.Vector2(1.5, 1.5), roughness: 0.96, metalness: 0.0
    })
    : new T.MeshStandardMaterial({ color: 0x6f5138, roughness: 0.96, metalness: 0.0 });""",
    """  const hideMat = PROF.hideMat === 'lambert'
    ? new T.MeshLambertMaterial({ color: 0xffffff, map: WOOL.color, normalMap: WOOL.normal })
    : PROF.hideMat === 'basic'
      ? new T.MeshBasicMaterial({ color: 0xffffff, map: WOOL.color })
      : PROF.hideTex
        ? new T.MeshStandardMaterial({
          color: 0xffffff, map: WOOL.color, normalMap: WOOL.normal,
          normalScale: new T.Vector2(1.5, 1.5), roughness: 0.96, metalness: 0.0
        })
        : new T.MeshStandardMaterial({ color: 0x6f5138, roughness: 0.96, metalness: 0.0 });""",
)

SCENE.write_text(s)
print("scene.mjs patched (pass 20)")
