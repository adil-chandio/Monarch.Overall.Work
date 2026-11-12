#!/usr/bin/env python3
"""Pass 13: the 'strange part' helix is the film's hero graphic - it must be clean.

Defects at frame 510:
  * The helix was built with 2.4 turns, so the two strand ends finished at different
    angles and the top of the graphic pinched into a visible kink.
  * Its colour (0x7fe3ff) is so pale that, after ACES tone mapping, it read as
    washed-out white and the two strands were hard to tell apart.

Fix: integer turns so the strands close cleanly, a saturated cyan, a darker base
colour so the emissive does not blow out, and a soft glow halo behind the helix
so it sits in the frame rather than floating on flat navy.
"""
from pathlib import Path

SCENE = Path(__file__).with_name("scene.mjs")
s = SCENE.read_text()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n}, found {s.count(old)}: {old[:90]!r}"
    s = s.replace(old, new)


# --------------------------------------------------- hero helix, cleaned up
sub(
    """    if (!window.__bigHelix) {
      const big = buildHelix(1.05, 4.0, 2.4, 0x7fe3ff, 0.95);
      big.position.set(0, 0.2, 0);
      graph.add(big);
      window.__bigHelix = big;
    }
    window.__bigHelix.visible = true;
    window.__bigHelix.rotation.y = t * 0.5;""",
    """    if (!window.__bigHelix) {
      // Integer turns so the two strands close without a kink, saturated cyan so
      // the graphic survives ACES tone mapping, and a halo so it sits in frame.
      const big = buildHelix(1.05, 4.0, 3, 0x2fc4f0, 0.92);
      big.position.set(0, 0.2, 0);
      const halo = new T.Mesh(new T.PlaneGeometry(6.4, 7.6), new T.MeshBasicMaterial({
        map: DOT_TEX, color: 0x1c6f96, transparent: true, opacity: 0.30,
        depthWrite: false, blending: T.AdditiveBlending
      }));
      halo.position.set(0, 0.2, -1.1);
      big.add(halo);
      const halo2 = new T.Mesh(new T.PlaneGeometry(4.2, 5.0), new T.MeshBasicMaterial({
        map: DOT_TEX, color: 0x36a9d8, transparent: true, opacity: 0.26,
        depthWrite: false, blending: T.AdditiveBlending
      }));
      halo2.position.set(0, 0.2, -0.9);
      big.add(halo2);
      graph.add(big);
      window.__bigHelix = big;
    }
    window.__bigHelix.visible = true;
    window.__bigHelix.rotation.y = t * 0.5;""",
)

SCENE.write_text(s)
print("scene.mjs patched (pass 13)")
