#!/usr/bin/env python3
"""Pass 11: the resolve title card and the ice surface.

Defects seen in the pass-10 stills:
  * Frame 1600 (resolve): the film title overlapped the mammoth's legs and sat on
    bright white ice with no contrast. The camera also framed the animal dead
    centre, so the title had nowhere to go.
    Fix: the animal is framed in the upper half, the title drops to the lower
    third on a dark plate, and it is set larger.
  * The floe read as a flat white paper cut-out: one uniform colour, one smooth
    silhouette, no surface story.
    Fix: the ice gets a mottled colour/roughness texture, the snow cap is
    toned down, and the slab edge is cooled so it stops flaring white.
  * The breath plume came out at ground level beside the front leg and read as
    fog on the ice. The trunk tip is raised so the vapour leaves the trunk.
"""
from pathlib import Path

SCENE = Path(__file__).with_name("scene.mjs")
s = SCENE.read_text()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n}, found {s.count(old)}: {old[:90]!r}"
    s = s.replace(old, new)


# ------------------------------------------------------------------ ice texture
sub(
    """function buildFloe() {
  const g = new T.Group();""",
    """function buildFloe() {
  const g = new T.Group();
  // Mottled sea-ice texture: without it the floe reads as a sheet of paper.
  const iceTex = canvasTex(512, 512, (g, w, h) => {
    g.fillStyle = '#c9dce8'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 260; i++) {
      const x = R() * w, y = R() * h, r = 8 + R() * 54;
      const grad = g.createRadialGradient(x, y, 0, x, y, r);
      const pale = R() > 0.45;
      grad.addColorStop(0, pale ? 'rgba(255,255,255,0.42)' : 'rgba(96,140,172,0.30)');
      grad.addColorStop(1, 'rgba(255,255,255,0)');
      g.fillStyle = grad; g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
    }
    // pressure cracks
    g.strokeStyle = 'rgba(72,116,150,0.42)';
    for (let i = 0; i < 34; i++) {
      g.lineWidth = 0.6 + R() * 1.8;
      g.beginPath();
      let x = R() * w, y = R() * h;
      g.moveTo(x, y);
      for (let k = 0; k < 5; k++) { x += (R() - 0.5) * 90; y += (R() - 0.5) * 90; g.lineTo(x, y); }
      g.stroke();
    }
    g.fillStyle = 'rgba(255,255,255,0.20)';
    for (let i = 0; i < 900; i++) { g.fillRect(R() * w, R() * h, 1 + R() * 2, 1 + R() * 2); }
  });
  iceTex.wrapS = iceTex.wrapT = T.RepeatWrapping;
  iceTex.repeat.set(3, 3);""",
)

sub(
    """  const ice = new T.Mesh(geo, new T.MeshStandardMaterial({ color: 0xbfd6e4, roughness: 0.42, metalness: 0.06 }));
  g.add(ice);
  const snow = new T.Mesh(geo.clone(), new T.MeshStandardMaterial({ color: 0xeaf2f7, roughness: 0.95, transparent: true, opacity: 0.55 }));
  snow.position.y = 0.05; snow.scale.setScalar(0.985);
  g.add(snow);""",
    """  const ice = new T.Mesh(geo, new T.MeshStandardMaterial({
    color: 0xa8c3d6, map: iceTex, roughness: 0.62, metalness: 0.02
  }));
  g.add(ice);
  const snow = new T.Mesh(geo.clone(), new T.MeshStandardMaterial({
    color: 0xd8e6ef, map: iceTex, roughness: 0.95, transparent: true, opacity: 0.34
  }));
  snow.position.y = 0.05; snow.scale.setScalar(0.985);
  g.add(snow);""",
)

sub(
    """  const edge = new T.Mesh(skirt, new T.MeshStandardMaterial({ color: 0x7ea9c2, roughness: 0.5, metalness: 0.05, transparent: true, opacity: 0.92 }));""",
    """  const edge = new T.Mesh(skirt, new T.MeshStandardMaterial({ color: 0x5f89a4, roughness: 0.78, metalness: 0.0, transparent: true, opacity: 0.94 }));""",
)

# ------------------------------------------------------------------ camera reframe
sub(
    """  'resolve': { from: [[-3.1, 2.15, 13.5], [1.5, 1.95, 9.6]], look: [[-0.45, 2.3, 0.2], [-0.15, 2.15, 0.4]] },""",
    """  'resolve': { from: [[-2.6, 2.30, 13.2], [1.7, 2.15, 10.4]], look: [[-0.35, 1.85, 0.2], [-0.10, 1.60, 0.4]] },""",
)

# ------------------------------------------------------------------ title plate
sub(
    """  const tex = textPlate([o.text, o.sub], {
    w: 1400, h: 460, titleSize: Math.round(150 * (o.size / 0.62)), subSize: 54, accent: o.accent,
    center: true, color: '#f4efe4', subColor: 'rgba(222,233,242,0.78)'
  });""",
    """  const tex = textPlate([o.text, o.sub], {
    w: 1400, h: 460, titleSize: Math.round(150 * (o.size / 0.62)), subSize: 54, accent: o.accent,
    center: true, color: '#f4efe4', subColor: 'rgba(222,233,242,0.78)',
    plate: !!o.plate
  });""",
)

# ------------------------------------------------------------------ breath origin
sub(
    """    [[0, 2.52, 2.58], [0, 2.02, 2.92], [0.02, 1.34, 2.92], [0.04, 0.74, 2.72], [0.02, 0.46, 2.46]],
    (t) => 0.225 - 0.175 * t, 80, 16);""",
    """    [[0, 2.52, 2.58], [0, 2.04, 2.94], [0.02, 1.46, 3.00], [0.04, 0.98, 2.86], [0.03, 0.78, 2.62]],
    (t) => 0.225 - 0.165 * t, 80, 16);""",
)

sub(
    """  g.userData.trunkTip = new T.Vector3(0.02, 0.46, 2.46);""",
    """  g.userData.trunkTip = new T.Vector3(0.03, 0.78, 2.62);""",
)

SCENE.write_text(s)
print("scene.mjs patched (pass 11)")
