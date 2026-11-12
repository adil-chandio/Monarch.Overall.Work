#!/usr/bin/env python3
"""Pass 7: make the visible-surface sampler correct AND fast.

Bugs in pass 6:
  * The leg "inside" test used legGeo.attributes.position.array[0] as the leg's x
    coordinate. After translate() that is the first vertex, not the leg centre.
  * The neck capsule ran the wrong way and used the wrong radius.
  * sampleGeometry() rebuilt a Float64Array cumulative-area table on EVERY call, and
    sampleVisible() called it once per sample -> 34k allocations of a multi-thousand
    element table. That is a multi-second stall and a GC storm.
  Fix: build one triangle table per part up front, then draw from it.
"""
from pathlib import Path

SCENE = Path(__file__).with_name("scene.mjs")
s = SCENE.read_text()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, f"expected {n}, found {s.count(old)}: {old[:90]!r}"
    s = s.replace(old, new)


# ------------------------------------------------------------------ sampler
sub(
    """// Area-weighted triangle sampling on one geometry.
function sampleGeometry(geo, count) {
  const index = geo.index.array;
  const P = geo.attributes.position.array;
  const N = geo.attributes.normal.array;
  const tri = index.length / 3;
  const cum = new Float64Array(tri);
  let total = 0;
  const a = new T.Vector3(), b = new T.Vector3(), c = new T.Vector3();
  const ab = new T.Vector3(), ac = new T.Vector3(), cr = new T.Vector3();
  for (let t = 0; t < tri; t++) {
    const i0 = index[t * 3] * 3, i1 = index[t * 3 + 1] * 3, i2 = index[t * 3 + 2] * 3;
    a.set(P[i0], P[i0 + 1], P[i0 + 2]); b.set(P[i1], P[i1 + 1], P[i1 + 2]); c.set(P[i2], P[i2 + 1], P[i2 + 2]);
    ab.subVectors(b, a); ac.subVectors(c, a);
    total += cr.crossVectors(ab, ac).length() * 0.5;
    cum[t] = total;
  }
  const out = [];
  for (let k = 0; k < count; k++) {
    const target = R() * total;
    let lo = 0, hi = tri - 1;
    while (lo < hi) { const mid = (lo + hi) >> 1; if (cum[mid] < target) lo = mid + 1; else hi = mid; }
    const t = lo;
    const i0 = index[t * 3] * 3, i1 = index[t * 3 + 1] * 3, i2 = index[t * 3 + 2] * 3;
    let u = R(), v = R();
    if (u + v > 1) { u = 1 - u; v = 1 - v; }
    const w = 1 - u - v;
    out.push({
      p: new T.Vector3(
        P[i0] * w + P[i1] * u + P[i2] * v,
        P[i0 + 1] * w + P[i1 + 1] * u + P[i2 + 1] * v,
        P[i0 + 2] * w + P[i1 + 2] * u + P[i2 + 2] * v),
      n: new T.Vector3(
        N[i0] * w + N[i1] * u + N[i2] * v,
        N[i0 + 1] * w + N[i1 + 1] * u + N[i2 + 1] * v,
        N[i0 + 2] * w + N[i2 + 2] * u + N[i2 + 2] * v).normalize()
    });
  }
  return out;
}

// Sample the visible hide only: reject any point that lies inside another volume.
function sampleVisible(parts, count) {
  const out = [];
  let guard = 0;
  const maxGuard = count * 14;
  while (out.length < count && guard++ < maxGuard) {
    const part = parts[Math.floor(R() * parts.length)];
    const cand = sampleGeometry(part.geo, 1)[0];
    if (!cand) continue;
    let buried = false;
    for (const other of parts) {
      if (other === part) continue;
      if (other.test && other.test(cand.p)) { buried = true; break; }
    }
    if (buried) continue;
    out.push({ p: cand.p, n: cand.n, part });
  }
  return out;
}""",
    """// Build one cumulative-area triangle table per part, once.
function buildTriTable(geo) {
  const index = geo.index.array;
  const P = geo.attributes.position.array;
  const N = geo.attributes.normal.array;
  const tri = index.length / 3;
  const cum = new Float64Array(tri);
  let total = 0;
  const a = new T.Vector3(), b = new T.Vector3(), c = new T.Vector3();
  const ab = new T.Vector3(), ac = new T.Vector3(), cr = new T.Vector3();
  for (let t = 0; t < tri; t++) {
    const i0 = index[t * 3] * 3, i1 = index[t * 3 + 1] * 3, i2 = index[t * 3 + 2] * 3;
    a.set(P[i0], P[i0 + 1], P[i0 + 2]); b.set(P[i1], P[i1 + 1], P[i1 + 2]); c.set(P[i2], P[i2 + 1], P[i2 + 2]);
    ab.subVectors(b, a); ac.subVectors(c, a);
    total += cr.crossVectors(ab, ac).length() * 0.5;
    cum[t] = total;
  }
  return { index, P, N, cum, total, tri };
}

// Draw one random point (position + normal) from a triangle table.
function drawPoint(tb) {
  const target = R() * tb.total;
  let lo = 0, hi = tb.tri - 1;
  while (lo < hi) { const mid = (lo + hi) >> 1; if (tb.cum[mid] < target) lo = mid + 1; else hi = mid; }
  const t = lo;
  const index = tb.index, P = tb.P, N = tb.N;
  const i0 = index[t * 3] * 3, i1 = index[t * 3 + 1] * 3, i2 = index[t * 3 + 2] * 3;
  let u = R(), v = R();
  if (u + v > 1) { u = 1 - u; v = 1 - v; }
  const w = 1 - u - v;
  return {
    p: new T.Vector3(
      P[i0] * w + P[i1] * u + P[i2] * v,
      P[i0 + 1] * w + P[i1 + 1] * u + P[i2 + 1] * v,
      P[i0 + 2] * w + P[i1 + 2] * u + P[i2 + 2] * v),
    n: new T.Vector3(
      N[i0] * w + N[i1] * u + N[i2] * v,
      N[i0 + 1] * w + N[i1 + 1] * u + N[i2 + 1] * v,
      N[i0 + 2] * w + N[i2 + 2] * u + N[i2 + 2] * v).normalize()
  };
}

// Sample the visible hide only: reject any point that lies inside another volume.
function sampleVisible(parts, count) {
  const tables = parts.map((p) => buildTriTable(p.geo));
  const out = [];
  const maxGuard = count * 40;
  let guard = 0;
  while (out.length < count && guard++ < maxGuard) {
    const pi = Math.floor(R() * parts.length);
    const cand = drawPoint(tables[pi]);
    let buried = false;
    for (let k = 0; k < parts.length; k++) {
      if (k === pi) continue;
      if (parts[k].test && parts[k].test(cand.p)) { buried = true; break; }
    }
    if (buried) continue;
    out.push({ p: cand.p, n: cand.n, part: parts[pi] });
  }
  console.log('[fur] sampled', out.length, 'of', count, 'visible points in', guard, 'draws');
  return out;
}""",
)

# ------------------------------------------------------------------ volume tests
sub(
    """    { geo: neckGeo, test: capsuleTest([0, 2.60, 1.16], [0, 2.16, 1.48], 0.86) },""",
    """    { geo: neckGeo, test: capsuleTest([0, 1.91, 1.15], [0, 2.85, 1.49], 0.80) },""",
)

sub(
    """  const legGeos = [];
  for (const [x, z, h] of [[-0.60, 1.20, 1.92], [0.60, 1.20, 1.92], [-0.62, -1.25, 1.96], [0.62, -1.25, 1.96]]) {
    const legGeo = new T.CylinderGeometry(0.27, 0.35, h, 20, 1);
    legGeo.translate(x, h / 2 + 0.08, z);
    g.add(new T.Mesh(legGeo, hideMat));
    legGeos.push(legGeo);""",
    """  const legGeos = [];
  for (const [x, z, h] of [[-0.60, 1.20, 1.92], [0.60, 1.20, 1.92], [-0.62, -1.25, 1.96], [0.62, -1.25, 1.96]]) {
    const legGeo = new T.CylinderGeometry(0.27, 0.35, h, 20, 1);
    legGeo.translate(x, h / 2 + 0.08, z);
    g.add(new T.Mesh(legGeo, hideMat));
    legGeos.push({ geo: legGeo, x, z, h });""",
)

sub(
    """  for (const lg of legGeos) {
    const cx = lg.attributes.position.array[0];
    hideParts.push({ geo: lg, test: capsuleTest([cx, 0.05, 0], [cx, 2.05, 0], 0.38) });
  }""",
    """  for (const lg of legGeos) {
    hideParts.push({ geo: lg.geo, test: capsuleTest([lg.x, 0.05, lg.z], [lg.x, lg.h + 0.08, lg.z], 0.37) });
  }""",
)

SCENE.write_text(s)
print("scene.mjs patched (pass 7)")
