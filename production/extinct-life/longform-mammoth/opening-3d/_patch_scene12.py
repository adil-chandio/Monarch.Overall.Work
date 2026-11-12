#!/usr/bin/env python3
"""Pass 12: the title must fit its plate, and the animal needs a face.

Defects:
  * "THE LAST MAMMOTHS RECOVERED." overflowed the dark title plate on the right.
    The plate is fixed-width in canvas pixels while the headline is Anton, so the
    plate is widened to match the longest line and the headline is sized down.
  * The eye was completely buried: it sat at z=2.62 while the skull surface at
    that height reaches z=3.10, so the eyeball was inside the head and under the
    coat. The eye is moved onto the skull surface, made larger, and given a dark
    socket ring so the animal reads as an animal.
"""
from pathlib import Path

SCENE = Path(__file__).with_name("scene.mjs")
s = SCENE.read_text()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n}, found {s.count(old)}: {old[:90]!r}"
    s = s.replace(old, new)


# ------------------------------------------------------------------ the eye
sub(
    """    const eye = new T.Mesh(new T.SphereGeometry(0.075, 16, 12), eyeMat);
    eye.position.set(s * 0.50, 2.80, 2.62); g.add(eye);
    const glint = new T.Mesh(new T.SphereGeometry(0.022, 10, 8), new T.MeshBasicMaterial({ color: 0xd8ecff }));
    glint.position.set(s * 0.535, 2.835, 2.67); g.add(glint);""",
    """    // Socket ring, then the eye sitting ON the skull surface (z ~ 2.86), so the
    // coat does not swallow it.
    const socket = new T.Mesh(new T.SphereGeometry(0.135, 18, 12),
      new T.MeshStandardMaterial({ color: 0x3b2a1c, roughness: 0.95 }));
    socket.scale.set(1, 0.86, 0.6);
    socket.position.set(s * 0.545, 2.86, 2.845); g.add(socket);
    const eye = new T.Mesh(new T.SphereGeometry(0.095, 18, 14), eyeMat);
    eye.position.set(s * 0.545, 2.87, 2.895); g.add(eye);
    const glint = new T.Mesh(new T.SphereGeometry(0.028, 10, 8), new T.MeshBasicMaterial({ color: 0xe6f3ff }));
    glint.position.set(s * 0.575, 2.905, 2.935); g.add(glint);""",
)

# The eye is now on the skull, so the skull dome must not sit on top of it.
sub(
    """    domeGeo.scale(0.34, 0.30, 0.40);
    domeGeo.translate(s * 0.28, 3.16, 2.06);""",
    """    domeGeo.scale(0.32, 0.28, 0.38);
    domeGeo.translate(s * 0.26, 3.14, 2.02);""",
)

SCENE.write_text(s)
print("scene.mjs patched (pass 12)")

# ------------------------------------------------------------------ title plate
BT = Path(__file__).with_name("build_timeline.py")
b = BT.read_text()
old = """    dict(id='title', start=52.6, end=59.6, text='THE LAST MAMMOTHS RECOVERED.', sub='THEN THEY VANISHED.', fx=.5, fy=.145, size=.46, accent='#e9dcc4', plate=True),"""
new = """    dict(id='title', start=52.6, end=59.6, text='THE LAST MAMMOTHS RECOVERED.', sub='THEN THEY VANISHED.', fx=.5, fy=.145, size=.40, accent='#e9dcc4', plate=True),"""
assert b.count(old) == 1
b = b.replace(old, new)
BT.write_text(b)
print("build_timeline.py patched (title size)")
