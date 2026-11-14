#!/usr/bin/env python3
"""
MONARCH — "Climbing a Mountain" / the original Gatún Locks.
A vertical 3D explainer, rendered as real geometry with a software rasteriser.

Why this renderer and not the reference stack: the reference used Three.js in
headless Chromium with SwiftShader. Here Chromium cannot start (libnspr4/libnss3
missing, apt has no package, repo is read-only), so WebGL is impossible. What is
possible is this: a scanline rasteriser in NumPy with a z-buffer, a proper sky,
a water surface shader with per-pixel Fresnel and specular, cached shadow maps
from the sun, an interior "torch" shadow map for the cutaway, animated gate
leaves on their hinge, rising water, and a ship that floats on that water.

Everything is driven by one clock: SHOTS (camera + labels), STATE(t) (water,
gates, ship, valves) and audio/align.json (captions). Nothing is a still.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------ constants
W, H = int(os.environ.get("VW", 1080)), int(os.environ.get("VH", 1920))   # 9:16
FPS = int(os.environ.get("VFPS", 30))
DUR = 47.0

U = 1.0                 # illustrative world unit (~10.2 ft): the brief requires not-to-scale
LOCK_W = 10.8           # 110 ft
CH_LEN = 34.0           # 1000 ft
STEP = 2.2              # lockage lift, illustrative
KEEL_DZ = -0.30         # keel sits this far below the water surface
SHIP_L, SHIP_W = 26.0, 9.0

CH_Z = [46.0, 0.0, -46.0]          # chamber centres, ship travels -z
GATE_Z = [63.0, 29.0, -17.0, -63.0]
L0 = 4.2                           # starting water level = sea level
WALL_TOP = 11.2
SEC_H = 1.15         # height of the sectioned (near) wall: a kerb you see over


# ------------------------------------------------------------------ math
def clamp(x, a=0.0, b=1.0):
    return a if x < a else (b if x > b else x)


def smoothstep(a, b, x):
    t = clamp((x - a) / (b - a) if b != a else 0.0)
    return t * t * (3 - 2 * t)


def smootherstep(p):
    """quintic S-curve: zero velocity AND zero acceleration at both ends"""
    p = clamp(p)
    return p * p * p * (p * (p * 6 - 15) + 10)


def lerp(a, b, t):
    return a + (b - a) * t


def nrm(v):
    v = np.asarray(v, np.float32)
    return v / max(float(np.linalg.norm(v)), 1e-9)


# ------------------------------------------------------------------ scene state
def level_of_step(k):
    """Water level of the upper chamber when it is at step k (k = 0 is the sea)."""
    return L0 + k * STEP


def state(t):
    """Every animated quantity at time t. One source of truth."""
    s = dict(t=t)
    s["fill_k"] = 0 if t < 18.6 else 1                       # which lockage is filling
    s["fill_p"] = 0.0 if t < 18.6 else clamp((t - 18.6) / 7.6)
    if t < 18.6:                      # before the fill the chamber already holds water
        s["fill"] = level_of_step(0)  # 4.2 m; the fill then lifts it 2.2 m
    else:
        s["fill"] = level_of_step(0) + STEP * smootherstep(s["fill_p"])
    s["fill2_p"] = clamp((t - 31.2) / 4.4)
    s["fill2"] = level_of_step(1) + STEP * smootherstep(s["fill2_p"])
    s["ch1"] = s["fill"]
    s["ch2"] = s["fill2"] if t > 31.2 else level_of_step(1)
    s["ch3"] = level_of_step(2)
    # gate openings (0 closed, 1 open): lower gates for chamber 1, then upper
    s["gate_low"] = smootherstep(clamp((t - 14.2) / 3.6))         # G1 opens, ship enters
    s["gate_mid"] = smootherstep(clamp((t - 27.2) / 3.4))         # G2 opens, ship goes up a step
    s["gate_up"] = smootherstep(clamp((t - 36.6) / 3.2))          # G3 opens, ship leaves
    s["valve"] = smoothstep(0.0, 0.6, s["fill_p"]) * (1 - smoothstep(0.75, 1.0, s["fill_p"]))
    s["valve2"] = smoothstep(0.0, 0.5, s["fill2_p"]) * (1 - smoothstep(0.78, 1.0, s["fill2_p"]))
    # ship: z from the sea (below G1) into chamber 1, then up into chamber 2
    if t < 14.2:
        z = 84.0
    elif t < 18.6:
        z = lerp(84.0, 46.0, smootherstep((t - 14.2) / 4.4))
    elif t < 23.9:
        z = 46.0
    elif t < 27.2:                      # small drift while the chamber fills
        z = 46.0 - 0.6 * smootherstep((t - 23.9) / 3.3)
    elif t < 31.2:
        z = lerp(45.4, 30.0, smootherstep((t - 27.2) / 4.0))
    else:
        z = 30.0
    s["ship_z"] = z
    lvl = s["ch1"] if t < 31.2 else s["ch2"]
    s["ship_y"] = lvl
    s["level"] = lvl
    # heave / roll / pitch: small, driven by the fill rate, not a sine toy
    rate = (STEP * (smootherstep(s["fill_p"] + 0.01) - smootherstep(s["fill_p"] - 0.01)) / 0.02) if t > 18.6 else 0.0
    s["heave"] = 0.010 * math.sin(t * 1.7) + 0.006 * math.sin(t * 0.9 + 1.1)
    s["roll"] = math.radians(0.25) * math.sin(t * 0.83) + math.radians(0.10) * math.sin(t * 1.9 + 2.0)
    s["pitch"] = math.radians(0.10) * math.sin(t * 0.61 + 0.7)
    s["flow"] = 0.35 + 2.2 * clamp(rate / 3.0)
    s["turb"] = 0.15 + 1.6 * s["fill_p"] * (1 - s["fill_p"]) * 4 * 0.35
    return s


# ------------------------------------------------------------------ camera
class Cam:
    def __init__(self, eye, target, fov_deg, roll=0.0):
        self.eye = np.asarray(eye, np.float32)
        self.f = nrm(np.asarray(target, np.float32) - self.eye)
        up = np.array([0, 1, 0], np.float32)
        r = nrm(np.cross(self.f, up))
        if roll:
            c, s = math.cos(roll), math.sin(roll)
            r, up2 = r * c + np.cross(self.f, r) * s, np.cross(r, self.f)
            self.u = nrm(up2)
        else:
            self.u = nrm(np.cross(r, self.f))
        self.r = r
        self.tan = math.tan(math.radians(fov_deg) / 2)
        self.fov = fov_deg

    def project(self, P):
        """P: (N,3) world -> (sx, sy, depth, visible) in pixels, and view dirs."""
        d = np.asarray(P, np.float32) - self.eye[None, :]
        z = d @ self.f
        x = d @ self.r
        y = d @ self.u
        zz = np.maximum(z, 1e-4)
        aspect = W / H
        sx = (x / (zz * self.tan * aspect)) * 0.5 * W + W / 2
        sy = H / 2 - (y / (zz * self.tan)) * 0.5 * H
        return sx, sy, z, (z > 0.05)


def bbox_pts(cmin, cmax):
    """The eight corners of an axis-aligned box, as fit points."""
    cmin = np.asarray(cmin, np.float32); cmax = np.asarray(cmax, np.float32)
    return np.array([[x, y, z] for x in (cmin[0], cmax[0])
                     for y in (cmin[1], cmax[1]) for z in (cmin[2], cmax[2])], np.float32)


def fit_cam(pts, direction, fov=42.0, margin=0.90, dist=None):
    """Distance the camera along `direction` until every fit point lands inside the
    frame with the given margin (fraction of half-width/half-height). Exact, so a
    beat cannot crop its subject when the aspect or the resolution changes."""
    pts = np.asarray(pts, np.float32).reshape(-1, 3)
    target = pts.mean(0)
    direction = nrm(np.asarray(direction, np.float32))
    if dist is not None:
        return Cam(target + direction * dist, target, fov)
    tv = math.tan(math.radians(fov) / 2)
    th = tv * (W / H)
    lo, hi = 1.0, 1200.0
    for _ in range(48):
        d = 0.5 * (lo + hi)
        cam = Cam(target + direction * d, target, fov)
        dv = pts - cam.eye[None, :]
        z = dv @ cam.f
        if (z <= 0.4).any():
            lo = d
            continue
        x = (dv @ cam.r) / (z * th)
        y = (dv @ cam.u) / (z * tv)
        if np.abs(x).max() <= margin and np.abs(y).max() <= margin:
            hi = d
        else:
            lo = d
    return Cam(target + direction * hi, target, fov)


def shot_camera(t):
    """Beats, all shot from outside the sectioned near wall (cut to 2.2 m for exactly
    this reason) or from above the flight. Every camera is placed over the canal, so
    the walls frame the subject instead of hiding it.

    Axes: +z downstream (sea), -z upstream (lake), +y up. The ship climbs +z -> -z."""
    s = state(t)
    sb = float(s["ship_y"])
    sz = float(s["ship_z"])

    def E(a, b, p):
        return np.array(a, np.float32) * (1 - p) + np.array(b, np.float32) * p

    if t < 3.3:      # HOOK: the whole flight from the sea side, a crane starting up
        p = smootherstep(t / 3.3)
        return Cam(E((6.5, 11.0, 124.0), (5.4, 12.4, 122.0), p), (0.0, 4.4, 66.0), 42.0)
    if t < 5.55:     # continue the crane: the ship at the lower gate, the steps behind
        p = smootherstep((t - 3.3) / 2.25)
        return Cam(E((5.4, 12.4, 122.0), (2.4, 14.0, 116.0), p), (0.0, 4.4, 62.0), lerp(42.0, 40.0, p))
    if t < 11.85:    # AT GATUN: up over the flight, three steps climbing away
        p = smootherstep((t - 5.55) / 6.3)
        return Cam(E((2.4, 14.0, 116.0), (-1.2, 30.0, 126.0), p), (0.0, 4.0, 46.0), lerp(40.0, 36.0, p))
    if t < 18.6:     # GATE + FILL: low outside the kerb, the gate across the channel
        p = smootherstep((t - 11.85) / 6.75)
        return Cam(E((-1.2, 30.0, 126.0), (8.4, 4.6, 78.0), p), (-1.0, 5.2, 66.0), 44.0)
    if t < 25.0:     # HOLES: close over the chamber floor, water rising off the openings
        p = smootherstep((t - 18.6) / 6.4)
        return Cam(E((8.4, 4.6, 78.0), (8.0, 8.6, 58.0), p), (0.0, sb + 0.4, 48.0), 46.0)
    if t < 30.5:     # LIFT: side-on, the hull and the waterline climbing the wall
        p = smootherstep((t - 25.0) / 5.5)
        return Cam(E((8.0, 8.6, 58.0), (9.2, 10.4, 50.0), p), (0.0, sb + 2.6, 42.0), 46.0)
    if t < 34.6:     # THREE STEPS: out and up, three water levels stacked up
        p = smootherstep((t - 30.5) / 4.1)
        return Cam(E((9.2, 10.4, 50.0), (10.0, 30.0, 118.0), p), (0.0, 4.0, 40.0), lerp(46.0, 38.0, p))
    if t < 39.45:    # GRAVITY: into the culvert gallery, then the valves in the wall
        p = (t - 34.6) / 4.85
        if p < 0.55:
            q = smootherstep(p / 0.55)
            return Cam(E((10.0, 30.0, 118.0), (3.2, 2.4, 66.0), q), (0.0, -1.6, 48.0), lerp(38.0, 46.0, q))
        q = smootherstep((p - 0.55) / 0.45)
        return Cam(E((3.2, 2.4, 66.0), (6.0, 12.0, 44.0), q), (-5.4, 10.0, 34.0), lerp(46.0, 42.0, q))
    # CLOSE: out and up, the whole flight with the lake beyond it
    p = smootherstep((t - 39.45) / (DUR - 39.45))
    return Cam(E((6.0, 12.0, 44.0), (4.0, 44.0, 140.0), p), (0.0, 4.0, 20.0), lerp(42.0, 36.0, p))


# ------------------------------------------------------------------ geometry
class Mesh:
    """Triangle soup with flat-ish normals, built once."""

    def __init__(self):
        self.v = []
        self.n = []
        self.c = []
        self.kind = []          # 0 = matte, 1 = steel, 2 = emissive-ish

    def quad(self, a, b, c, d, n, col, kind=0):
        a, b, c, d = (np.asarray(x, np.float32) for x in (a, b, c, d))
        n = nrm(n)
        for tri in ((a, b, c), (a, c, d)):
            self.v.extend(tri)
            self.n.extend([n, n, n])
            self.c.extend([col, col, col])
            self.kind.extend([kind, kind, kind])

    def box(self, cmin, cmax, col, kind=0, skip=()):
        x0, y0, z0 = cmin
        x1, y1, z1 = cmax
        if "front" not in skip:
            self.quad((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1), (0, 0, 1), col, kind)
        if "back" not in skip:
            self.quad((x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0), (0, 0, -1), col, kind)
        if "left" not in skip:
            self.quad((x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0), (-1, 0, 0), col, kind)
        if "right" not in skip:
            self.quad((x1, y0, z1), (x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (1, 0, 0), col, kind)
        if "top" not in skip:
            self.quad((x0, y1, z1), (x1, y1, z1), (x1, y1, z0), (x0, y1, z0), (0, 1, 0), col, kind)
        if "bottom" not in skip:
            self.quad((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1), (0, -1, 0), col, kind)

    def arrays(self):
        return (np.array(self.v, np.float32).reshape(-1, 3), np.array(self.n, np.float32).reshape(-1, 3),
                np.array(self.c, np.float32).reshape(-1, 3), np.array(self.kind, np.int8).reshape(-1))


CONCRETE = np.array([0.600, 0.575, 0.520], np.float32)
CONCRETE_D = np.array([0.430, 0.410, 0.375], np.float32)
STEEL = np.array([0.205, 0.220, 0.240], np.float32)
HULL = np.array([0.130, 0.145, 0.170], np.float32)
DECK = np.array([0.34, 0.33, 0.315], np.float32)
# container colours, desaturated: a working port, not a toy box
BOXCOLS = [np.array(c, np.float32) for c in
           [(0.31, 0.16, 0.12), (0.13, 0.21, 0.28), (0.22, 0.23, 0.19),
            (0.30, 0.25, 0.12), (0.16, 0.18, 0.21), (0.27, 0.27, 0.25),
            (0.25, 0.13, 0.13), (0.11, 0.16, 0.18)]]


def build_static():
    """Walls, floors, gate piers, culverts, service buildings, terrain, trees."""
    m = Mesh()
    hw = LOCK_W / 2
    wall_h = WALL_TOP
    z_start, z_end = 92.0, -92.0

    # --- chamber floor with the 100 openings (20 cross culverts x 5 holes)
    for k, zc in enumerate(CH_Z):
        z0, z1 = zc + CH_LEN / 2, zc - CH_LEN / 2
        m.box((-hw, -0.9, z0), (hw, 0.0, z1), CONCRETE * np.array([0.62, 0.66, 0.70], np.float32))
        for i in range(20):
            zz = z0 - 1.2 - i * 1.65
            for j in range(5):
                xx = -3.2 + j * 1.6
                m.box((xx - 0.24, -0.02, zz - 0.34), (xx + 0.24, 0.03, zz + 0.34),
                      np.array([0.16, 0.17, 0.18], np.float32), kind=1)
    # --- main culverts inside each wall (18 ft tunnels), cutaway-visible
    for sx in (-1, 1):
        x = sx * (hw - 0.55)
        m.box((x - 0.42, -0.85, z_end), (x + 0.42, -0.05, z_start), np.array([0.22, 0.235, 0.245], np.float32))
    # --- cross culverts under each chamber floor
    for zc in CH_Z:
        for i in range(20):
            zz = zc + CH_LEN / 2 - 1.2 - i * 1.65
            m.box((-hw + 0.5, -0.8, zz - 0.16), (hw - 0.5, -0.1, zz + 0.16),
                  np.array([0.20, 0.215, 0.225], np.float32))
    # --- side walls (thick, with coping) and the guide rails on top
    for sx in (-1, 1):
        # the sectioned near wall is a slim kerb; the intact far wall is the full mass
        wid = 2.0 if sx > 0 else 9.0
        x0, x1 = (hw, hw + wid) if sx > 0 else (-hw - wid, -hw)
        outer = hw + wid
        wh = wall_h if sx < 0 else SEC_H
        m.box((x0, -2.2, z_end), (x1, wh, z_start), CONCRETE)          # main mass
        cop = CONCRETE_D if sx < 0 else np.array([0.250, 0.250, 0.235], np.float32)
        m.box((sx * hw, wh, z_end), (sx * outer, wh + 0.18, z_start), cop)          # coping
        # batter: a slightly wider base, the way a lock wall actually sits
        m.box((sx * hw, -2.2, z_end), (sx * (hw + 0.55), 0.9, z_start), CONCRETE_D)
        for zt in np.arange(z_start, z_end, 6.0):      # construction seams, flush
            m.box((sx * (hw + 0.004), -0.8, zt), (sx * (hw + 0.02), wh - 0.33, zt + 0.05),
                  CONCRETE_D * 0.82)
        if sx < 0:            # everything on top only exists on the intact wall
            m.box((x0 + 1.1, wh + 0.14, z_end), (x0 + 1.2, wh + 0.20, z_start), STEEL, kind=1)
            m.box((x1 - 1.2, wh + 0.14, z_end), (x1 - 1.1, wh + 0.20, z_start), STEEL, kind=1)
            for zt in np.arange(z_start - 6, z_end, 26.0):
                m.box((x0 + 1.9, wh + 0.14, zt - 0.12), (x0 + 2.14, wh + 0.5, zt + 0.12), STEEL, kind=1)

    # --- gate piers between chambers
    for gz in GATE_Z:
        for sx in (-1, 1):
            x0 = (hw - 0.2) if sx > 0 else (-hw - 2.4)
            ph = wall_h + 1.5 if sx < 0 else SEC_H
            m.box((x0, -0.9, gz - 1.5), (x0 + 2.6, ph, gz + 1.5), CONCRETE)
        # sill
        m.box((-hw, -0.95, gz - 1.4), (hw, -0.05, gz + 1.4), CONCRETE_D)

    # --- miter gate leaves (geometry built closed; the renderer rotates them)
    for gz in GATE_Z:
        for sx in (-1, 1):
            leaf = Mesh()
            w = hw - 0.15
            # a leaf that closes from the pier towards the centre: its hinge is at x = sx*hw
            gh = wall_h - 0.6
            leaf.box((0, -0.7, -0.5), (w, gh, 0.5), STEEL, kind=1)
            for yy in np.arange(0.2, wall_h - 1.0, 1.6):   # horizontal girders
                leaf.box((0, yy, -0.54), (w, yy + 0.14, 0.54), np.array([0.190, 0.205, 0.225], np.float32), kind=1)
            for xx in np.arange(1.1, w, 2.6):              # vertical ribs
                leaf.box((xx, -0.6, -0.52), (xx + 0.12, wall_h - 0.7, 0.52), np.array([0.175, 0.190, 0.210], np.float32), kind=1)
            # local +x runs along the leaf from the hinge. Right pier: base angle 180
            # so the leaf points across the canal; the swing adds to that.
            GATE_LEAVES.append(dict(mesh=leaf, hinge=np.array([sx * hw, 0, gz], np.float32),
                                    base=0.0 if sx < 0 else math.pi, swing=-sx, w=w, gz=gz))

    # --- electric mules: the little locomotives that keep the hull off the walls.
    #     They are the best scale cue on the whole structure, so they are everywhere.
    for sx in (-1,):
        for zt in np.arange(z_start - 10, z_end + 10, 9.0):
            xc = sx * (hw + 1.35)
            m.box((xc - 1.05, wall_h + 0.18, zt - 1.5), (xc + 1.05, wall_h + 0.85, zt + 1.5),
                  np.array([0.520, 0.400, 0.075], np.float32))          # yellow body
            m.box((xc - 0.95, wall_h + 0.85, zt - 1.25), (xc + 0.95, wall_h + 1.05, zt + 0.55),
                  np.array([0.240, 0.245, 0.250], np.float32), kind=1)  # cab roof
            m.box((xc - 0.8, wall_h + 0.30, zt - 1.55), (xc + 0.8, wall_h + 0.62, zt - 1.45),
                  np.array([0.140, 0.140, 0.145], np.float32), kind=1)
    # --- ladders and recesses down the inside faces, another scale cue
    for sx in (-1,):
        for zt in np.arange(z_start - 14, z_end + 10, 16.0):
            xin = sx * (hw + 0.03)
            m.box((xin - sx * 0.03, 1.2, zt - 0.5), (xin + sx * 0.12, wall_h - 0.16, zt + 0.5),
                  np.array([0.185, 0.205, 0.190], np.float32), kind=1)

    # --- service buildings on the walls, with windows
    for sx in (-1,):
        for zt in (60.0, 12.0, -40.0):
            x0 = (hw + 0.5) if sx > 0 else (-hw - 3.0)
            m.box((x0, wall_h + 0.14, zt - 3.0), (x0 + 2.4, wall_h + 1.8, zt + 3.0), CONCRETE_D)
            m.box((x0 - 0.04, wall_h + 1.7, zt - 2.8), (x0 + 2.44, wall_h + 1.95, zt + 2.8),
                  np.array([0.24, 0.255, 0.27], np.float32))
            for wzt in np.arange(zt - 2.2, zt + 2.2, 1.5):
                m.box((x0 - 0.06, wall_h + 0.75, wzt), (x0 - 0.02, wall_h + 1.35, wzt + 0.7),
                      np.array([0.055, 0.07, 0.09], np.float32), kind=1)

    # --- gate machinery houses beside each gate
    for gz in GATE_Z:
        for sx in (-1, 1):
            x0 = (hw - 0.1) if sx > 0 else (-hw - 2.0)
            m.box((x0 + 0.3, wall_h + 0.14, gz - 1.2), (x0 + 1.9, wall_h + 1.1, gz + 1.2),
                  np.array([0.30, 0.29, 0.27], np.float32))
            m.box((x0 + 0.8, wall_h + 1.1, gz - 0.4), (x0 + 1.4, wall_h + 1.5, gz + 0.4), STEEL, kind=1)

    # --- terrain: one ground plane; the banks sit well outside the walls and low,
    #     so they read as ground instead of a wall in front of the lens
    # --- the land the lock is cut through. Gatun is a channel cut through the
    #     isthmus: low ground either side of the walls, jungle beyond it, and the lake
    #     the flight ends in. Without this the lock floats on a blue plane.
    rng = np.random.default_rng(7)
    for sx in (-1, 1):
        xin = sx * (hw + 9.02)
        xo = sx * 260.0
        m.box((min(xin, xo), -3.0, -330.0), (max(xin, xo), 2.4, 190.0),
              np.array([0.150, 0.180, 0.125], np.float32))
        # the mown maintenance strip that runs along every lock wall
        xs0 = sx * (hw + 9.02); xs1 = sx * (hw + 16.0)
        m.box((min(xs0, xs1), 2.4, -330.0), (max(xs0, xs1), 2.55, 190.0),
              np.array([0.300, 0.315, 0.250], np.float32))
        # jungle: a dense canopy band that starts just behind the maintenance strip,
        # so the lock sits in forest instead of on a lawn
        for zt in np.arange(-330.0, 190.0, 9.0):
            for xi in (0.0, 9.0, 20.0, 34.0, 52.0, 74.0):
                if rng.random() < 0.22:
                    continue
                xc = sx * (hw + 9.0 + 16.5 + xi + rng.random() * 6.0)
                ww = 5.5 + rng.random() * 5.0
                hh = 6.0 + rng.random() * 9.0 + xi * 0.06
                m.box((xc - ww, 2.3, zt + rng.random() * 4.0),
                      (xc + ww, 2.3 + hh, zt + ww * 1.9),
                      np.array([0.095 + rng.random() * 0.045, 0.150 + rng.random() * 0.070,
                                0.085 + rng.random() * 0.040], np.float32))
    # --- Gatun Lake upstream: wide water at the top level, past the last gate
    m.box((-260.0, level_of_step(2) - 0.55, -430.0), (260.0, level_of_step(2), -100.0),
          np.array([0.075, 0.155, 0.185], np.float32))
    # --- a hazy ridge on the far shore of the lake
    m.box((-320.0, -2.0, -520.0), (320.0, 22.0, -420.0), np.array([0.240, 0.265, 0.230], np.float32))

    verts, norms, cols, kinds = m.arrays()
    # gate leaves are separate, so keep them out of the static buffer
    return dict(v=verts, n=norms, c=cols, k=kinds)


GATE_LEAVES = []


def ship_mesh(s):
    """Hull, deckhouse, container stacks. One mesh, moved by the ship state."""
    m = Mesh()
    y = s["ship_y"]
    z = s["ship_z"]
    dz = KEEL_DZ
    L, Wd = SHIP_L, SHIP_W
    # hull: three boxes (belt, upper, bow taper) keep it readable at 9:16
    m.box((-Wd / 2, y + dz, z - L / 2), (Wd / 2, y + 1.75, z + L / 2), HULL)
    m.box((-Wd / 2 + 0.25, y + 1.75, z - L / 2 + 0.5), (Wd / 2 - 0.25, y + 2.05, z + L / 2 - 2.6), DECK)
    # bow: a wedge made of two quads
    bl = z + L / 2
    m.quad((-Wd / 2, y + dz, bl), (Wd / 2, y + dz, bl), (0.0, y + dz, bl + 2.6), (0.0, y + dz, bl + 2.6),
           (0, -1, 0), HULL)
    for sx in (-1, 1):
        m.quad((sx * Wd / 2, y + dz, bl), (0, y + dz, bl + 2.6), (0, y + 1.75, bl + 2.6),
               (sx * Wd / 2, y + 1.75, bl), (sx * 0.45, 0, 0.9), HULL)
    # bulwark: the low wall round the deck edge that makes a ship read as a ship
    for sx in (-1, 1):
        m.box((sx * (Wd / 2) - sx * 0.22, y + 1.75, z - L / 2), (sx * (Wd / 2), y + 2.55, z + L / 2 - 1.2),
              np.array([0.175, 0.190, 0.215], np.float32))
    m.box((-Wd / 2, y + 1.75, z - L / 2), (Wd / 2, y + 2.55, z - L / 2 + 0.22),
          np.array([0.175, 0.190, 0.215], np.float32))
    # deckhouse aft
    m.box((-Wd / 2 + 1.0, y + 2.05, z - L / 2 + 1.2), (Wd / 2 - 1.0, y + 4.2, z - L / 2 + 6.2),
          np.array([0.60, 0.60, 0.58], np.float32))
    m.box((-Wd / 2 + 1.4, y + 4.2, z - L / 2 + 1.6), (Wd / 2 - 1.4, y + 4.6, z - L / 2 + 3.0),
          np.array([0.30, 0.31, 0.32], np.float32), kind=1)
    # container stacks: 8 bays x 2 rows x 3 high, deterministic colouring
    rng = np.random.default_rng(20261114)
    for bi in range(7):
        bz0 = z - L / 2 + 8.4 + bi * 2.35
        for row, sx in enumerate((-1, 1)):
            for lvl in range(2):
                if rng.random() < 0.10:
                    continue
                col = BOXCOLS[(bi * 3 + lvl + row) % len(BOXCOLS)]
                xc = sx * (Wd / 2 - 1.75)
                m.box((xc - 1.24, y + 2.55 + lvl * 0.80, bz0), (xc + 1.24, y + 3.30 + lvl * 0.80, bz0 + 2.20),
                      np.asarray(col, np.float32))
    return m


# ------------------------------------------------------------------ water
def water_height(x, z, t, s, turb=1.0):
    """Layered sine ripples (the reference's shader family, retuned for our scale),
    plus a wake behind the hull and turbulence that follows the fill rate."""
    dy = (0.020 * np.sin(4.1 * x + 0.38 * z + 0.80 * t)
          + 0.013 * np.sin(2.6 * z - 0.7 * x - 0.63 * t)
          + 0.006 * np.sin(7.2 * x + 3.8 * z + 1.12 * t))
    # wake: a V trailing the ship, amplitude falling with distance
    sz = s["ship_z"]
    behind = np.clip((z - (sz - SHIP_L / 2)), 0, 40) * (z > sz - SHIP_L / 2)
    lat = np.abs(x) / (1.0 + behind * 0.35)
    wake = 0.055 * np.exp(-behind * 0.06) * np.exp(-(lat ** 2) * 2.2) * np.sin(behind * 1.6 - t * 3.0)
    churn = 0.0
    if s.get("valve", 0) > 0.02:            # water welling up through the floor
        edge = np.clip(1.0 - np.abs(z - (s["ship_z"] - 12.0)) / 16.0, 0, 1)
        churn = 0.10 * s["valve"] * edge * np.sin(9.0 * x + 5.0 * z - 7.0 * t)
    return dy * (0.55 + 0.45 * turb) + wake + churn


def render_water(cam, t, s):
    """Water as a projected grid: channel water inside the walls, plus the lake
    beyond them, so the flight reads as sitting in a landscape, not in a box."""
    hw = LOCK_W / 2 + 0.05         # the canal itself, wall to wall
    z0, z1 = 200.0, -104.0
    nx, nz = 10, 110
    xs = np.linspace(-hw, hw, nx)
    zs = np.linspace(z0, z1, nz)
    XX, ZZ = np.meshgrid(xs, zs, indexing="ij")
    lvl = s["level"]
    YY = lvl + water_height(XX, ZZ, t, s)
    P = np.stack([XX, YY, ZZ], -1).reshape(-1, 3)
    sx, sy, depth, vis = cam.project(P)
    # per-cell normal from the height field
    dYdx = (np.roll(YY, -1, 0) - np.roll(YY, 1, 0)) / (2 * (xs[1] - xs[0]))
    dYdz = (np.roll(YY, -1, 1) - np.roll(YY, 1, 1)) / (2 * (zs[1] - zs[0]))
    N = np.stack([-dYdx, np.ones_like(dYdx), -dYdz], -1).reshape(-1, 3)
    N = N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-8)

    vdir = nrm(P - cam.eye[None, :])
    f0 = 0.02
    fres = f0 + (1 - f0) * (1 - np.abs((N * -vdir).sum(1))) ** 5
    sun = nrm(SUN_DIR)
    ndl = np.clip(N @ sun, 0, 1)
    h = N * -1
    hv = N - vdir
    hv = hv / np.maximum(np.linalg.norm(hv, axis=1, keepdims=True), 1e-8)
    ndh = np.clip((hv * sun).sum(1), 0, 1)
    spec = ndh ** 340 * 4.2
    # reflection: mirror the view vector about the surface and sample the sky
    R = vdir - 2.0 * (N * vdir).sum(1, keepdims=True) * N
    refl = sky_color(R, t) * 0.70
    deep = np.array([0.022, 0.105, 0.115], np.float32)
    col = deep * (0.90 + 0.28 * ndl)[:, None] + refl * (fres ** 1.5)[:, None] + spec[:, None]
    # shadows from the walls and gates, and a dark halo right under the hull
    sh = sun_shadow(P, s)
    col = col * (1.0 - 0.38 * sh)[:, None]
    cx, cz = s.get("ship_x", 0.0), s["ship_z"]
    ex = ((P[:, 0] - cx) / (SHIP_W / 2 + 1.6)) ** 2 + ((P[:, 2] - cz) / (SHIP_L / 2 + 2.2)) ** 2
    col = col * (1.0 - 0.45 * np.clip(1.0 - ex, 0, 1))[:, None]
    col = np.clip(col, 0, 3)

    idx = np.arange(nx * nz).reshape(nx, nz)
    quads = np.stack([idx[:-1, :-1].ravel(), idx[1:, :-1].ravel(),
                      idx[1:, 1:].ravel(), idx[:-1, 1:].ravel()], 1)
    SX, SY, D = sx.reshape(nx, nz), sy.reshape(nx, nz), depth.reshape(nx, nz)
    qx = np.stack([SX[:-1, :-1].ravel(), SX[1:, :-1].ravel(), SX[1:, 1:].ravel(), SX[:-1, 1:].ravel()], 1)
    qy = np.stack([SY[:-1, :-1].ravel(), SY[1:, :-1].ravel(), SY[1:, 1:].ravel(), SY[:-1, 1:].ravel()], 1)
    qz = np.stack([D[:-1, :-1].ravel(), D[1:, :-1].ravel(), D[1:, 1:].ravel(), D[:-1, 1:].ravel()], 1)
    # opacity: shallow/grazing water hides the floor, looking down you see through it
    alpha = np.clip(0.998 - 0.05 * fres, 0.985, 0.998).reshape(nx, nz)
    on = ((qx.max(1) > 0) & (qx.min(1) < W) & (qy.max(1) > 0) & (qy.min(1) < H)
          & (qz.min(1) > 0.06) & (qz.min(1) < 320.0))
    quads = quads[on]
    return dict(quads=quads, sx=sx, sy=sy, depth=depth, col=col, alpha=alpha.reshape(-1),
                albedo=None, kind=np.full(len(P), 3, np.int8), normals=N, pts=P)


SUN_DIR = np.array([0.26, 0.84, 0.48], np.float32)


# ------------------------------------------------------------------ shaders
def sky_color(dirv, t):
    """Soft tropical daylight; no texture, so no seam and no fake footage claim."""
    d = dirv / np.maximum(np.linalg.norm(dirv, axis=1, keepdims=True), 1e-8)
    h = np.clip(d[:, 1], -1, 1)
    zen = np.array([0.080, 0.215, 0.500], np.float32)
    hor = np.array([0.700, 0.760, 0.790], np.float32)
    ground = np.array([0.190, 0.205, 0.175], np.float32)
    k = np.clip(h, 0, 1) ** 0.50
    col = hor[None, :] * (1 - k)[:, None] + zen[None, :] * k[:, None]
    col = np.where(h[:, None] < 0, ground[None, :], col)
    sun = nrm(SUN_DIR)
    cs = np.clip(d @ sun, -1, 1)
    glow = np.clip(cs, 0, 1) ** 9 * 0.60 + np.clip(cs, 0, 1) ** 160 * 2.6
    col = col + np.array([1.0, 0.90, 0.74], np.float32)[None, :] * glow[:, None]
    return col.astype(np.float32)


def vnoise(p, scale=0.6, seed=0.0):
    """Cheap deterministic value noise from position; used for surface variation."""
    q = p * scale
    i = np.floor(q)
    f = q - i
    f = f * f * (3 - 2 * f)
    def h(a, b, c):
        return np.modf(np.sin(a * 12.9898 + b * 78.233 + c * 37.719 + seed) * 43758.5453)[0]
    n000 = h(i[:, 0], i[:, 1], i[:, 2])
    n100 = h(i[:, 0] + 1, i[:, 1], i[:, 2])
    n010 = h(i[:, 0], i[:, 1] + 1, i[:, 2])
    n110 = h(i[:, 0] + 1, i[:, 1] + 1, i[:, 2])
    n001 = h(i[:, 0], i[:, 1], i[:, 2] + 1)
    n101 = h(i[:, 0] + 1, i[:, 1], i[:, 2] + 1)
    n011 = h(i[:, 0], i[:, 1] + 1, i[:, 2] + 1)
    n111 = h(i[:, 0] + 1, i[:, 1] + 1, i[:, 2] + 1)
    x, y, z = f[:, 0], f[:, 1], f[:, 2]
    return ((n000 * (1 - x) + n100 * x) * (1 - y) + (n010 * (1 - x) + n110 * x) * y) * (1 - z) + \
           ((n001 * (1 - x) + n101 * x) * (1 - y) + (n011 * (1 - x) + n111 * x) * y) * z


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


def sun_shadow(P, s, wall_h=None, soft=1.1):
    """Cheap analytic shadows: the sun is low enough that the tall lock walls and the
    gate leaves throw long shadows across the water. That is most of what makes a
    lock look like a lock, so it is worth the few lines of maths."""
    wall_h = WALL_TOP if wall_h is None else wall_h
    hw = LOCK_W / 2
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    k = SUN_DIR[1] / max(SUN_DIR[0], 1e-3)          # rise per metre of travel
    sh = np.zeros(len(P), np.float32)
    # right-hand wall (sun side), shadows fall left across the channel
    dx = hw - x
    in_chan = (dx > -0.2) & (dx < hw * 2)
    h_edge = wall_h - k * np.clip(dx, 0, None)
    sh = np.maximum(sh, in_chan.astype(np.float32) * smoothstep(h_edge + soft, h_edge - soft, y))
    # gate leaves: each gate is a wall across the channel, shadow falls to -z
    kz = SUN_DIR[1] / max(SUN_DIR[2], 1e-3)
    for gz in GATE_Z:
        dz = z - gz
        h_g = wall_h - 0.4 - kz * np.clip(dz, 0, None)
        band = ((dz > -0.2) & (dz < 26)).astype(np.float32)
        sh = np.maximum(sh, band * smoothstep(h_g + soft, h_g - soft, y))
    return np.clip(sh, 0, 1)


def shade(points, normals, albedo, kinds, cam, t, s, fog_k=0.0009):
    """Sun + hemisphere + rim, with a tiny distance haze. No texture reads."""
    sun = nrm(SUN_DIR)
    ndl = np.clip(normals @ sun, 0, 1)
    # the waterline: everything just above the water is wet, dark and streaked
    lvl = s.get("level", 0.0)
    wet = smoothstep(lvl + 1.15, lvl + 0.05, points[:, 1])
    # two octaves of variation: concrete mottling and grime, not a flat laminate
    var = 0.80 + 0.30 * vnoise(points, 0.55, 1.0) + 0.13 * vnoise(points, 2.7, 7.0)
    albedo = albedo * var[:, None]
    albedo = albedo * (1.0 - 0.22 * wet)[:, None]
    lit = 1.0 - 0.50 * sun_shadow(points, s)
    vdir = nrm(cam.eye[None, :] - points)
    ndv = np.clip((normals * vdir).sum(1), 0, 1)
    hemi_up = np.clip(normals[:, 1] * 0.5 + 0.5, 0, 1)
    sky = np.array([0.46, 0.56, 0.70], np.float32)
    grd = np.array([0.26, 0.26, 0.21], np.float32)
    amb = (sky[None, :] * hemi_up[:, None] + grd[None, :] * (1 - hemi_up)[:, None]) * 1.55
    amb = amb + np.array([0.075, 0.085, 0.095], np.float32)[None, :]      # bounce from the water
    sunc = np.array([1.00, 0.905, 0.780], np.float32)
    # ambient occlusion: tight in the chamber, open above the coping
    ao = np.clip(0.52 + 0.48 * np.clip((points[:, 1] - s.get("level", 0.0)) / 4.2, 0, 1), 0.52, 1.0)
    col = albedo * (amb * 0.80 * ao[:, None] + sunc[None, :] * (ndl * 2.05 * lit)[:, None])
    # steel gets a tighter specular and a cool rim
    is_steel = kinds == 1
    if is_steel.any():
        hv = sun[None, :] + vdir
        hv = hv / np.maximum(np.linalg.norm(hv, axis=1, keepdims=True), 1e-8)
        ndh = np.clip((normals[is_steel] * hv[is_steel]).sum(1), 0, 1)
        col[is_steel] = col[is_steel] + (ndh ** 90 * 1.5)[:, None] * sunc[None, :]
        col[is_steel] = col[is_steel] + ((1 - ndv[is_steel]) ** 3 * 0.16)[:, None] * sky[None, :]
    rim = ((1 - ndv) ** 4 * 0.35)[:, None] * np.array([0.55, 0.68, 0.85], np.float32)[None, :]
    col = col + rim * ndl[:, None]
    # distance haze towards the sky colour at the same view direction
    dist = np.linalg.norm(points - cam.eye[None, :], axis=1)
    f = 1 - np.exp(-fog_k * np.maximum(dist - 45, 0))
    atm = np.array([0.655, 0.715, 0.745], np.float32)      # horizon air
    zen = np.array([0.230, 0.345, 0.480], np.float32)
    up = np.clip((points[:, 1] + 2.0) / 60.0, 0, 1)[:, None]
    sk = atm[None, :] * (1 - up) + zen[None, :] * up
    return col * (1 - f[:, None] * 0.85) + sk * (f[:, None] * 0.85)


# ------------------------------------------------------------------ raster
class Frame:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.col = np.zeros((h, w, 3), np.float32)
        self.z = np.full((h, w), np.inf, np.float32)

    def raster(self, sx, sy, z, tris, colors):
        """Filled triangle rasterisation with a z-buffer, vectorised per scanline band."""
        x0 = np.minimum(np.minimum(sx[tris[:, 0]], sx[tris[:, 1]]), sx[tris[:, 2]])
        x1 = np.maximum(np.maximum(sx[tris[:, 0]], sx[tris[:, 1]]), sx[tris[:, 2]])
        y0 = np.minimum(np.minimum(sy[tris[:, 0]], sy[tris[:, 1]]), sy[tris[:, 2]])
        y1 = np.maximum(np.maximum(sy[tris[:, 0]], sy[tris[:, 1]]), sy[tris[:, 2]])
        keep = (x1 >= 0) & (x0 < self.w) & (y1 >= 0) & (y0 < self.h) & np.isfinite(z[tris[:, 0]])
        tris = tris[keep]
        if tris.size == 0:
            return
        ax, ay = sx[tris[:, 0]], sy[tris[:, 0]]
        bx, by = sx[tris[:, 1]], sy[tris[:, 1]]
        cx, cy = sx[tris[:, 2]], sy[tris[:, 2]]
        az, bz, cz = z[tris[:, 0]], z[tris[:, 1]], z[tris[:, 2]]
        area = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
        ok = np.abs(area) > 1e-9
        tris, ax, ay, bx, by, cx, cy, az, bz, cz, area = (
            tris[ok], ax[ok], ay[ok], bx[ok], by[ok], cx[ok], cy[ok], az[ok], bz[ok], cz[ok], area[ok])
        cols = colors[tris[:, 0]]
        rad, g, b = cols[:, 0], cols[:, 1], cols[:, 2]
        ymin = np.floor(np.minimum(np.minimum(ay, by), cy)).astype(np.int64)
        ymax = np.ceil(np.maximum(np.maximum(ay, by), cy)).astype(np.int64)
        ymin = np.clip(ymin, 0, self.h - 1)
        ymax = np.clip(ymax, 0, self.h - 1)
        # expand to scanline work items
        counts = np.maximum(ymax - ymin + 1, 0)
        total = int(counts.sum())
        if total == 0:
            return
        tid = np.repeat(np.arange(len(tris)), counts)
        ystart = np.repeat(ymin, counts)
        off = np.arange(total) - np.repeat(np.cumsum(counts) - counts, counts)
        yy = ystart + off
        py = yy.astype(np.float32) + 0.5
        inv = 1.0 / area[tid]
        # barycentric at the left/right ends: solve the edge functions across the span
        w0a = ((bx[tid] - ax[tid]) * (py - ay[tid]) - (by[tid] - ay[tid]) * (0 - ax[tid]))
        # cheaper: compute edge functions at x=0 then step
        e0x = -(cy[tid] - by[tid]); e0c = (cy[tid] - by[tid]) * (0 - bx[tid]) + (bx[tid] - cx[tid]) * (py - by[tid])
        e1x = -(ay[tid] - cy[tid]); e1c = (ay[tid] - cy[tid]) * (0 - cx[tid]) + (cx[tid] - ax[tid]) * (py - cy[tid])
        e2x = -(by[tid] - ay[tid]); e2c = (by[tid] - ay[tid]) * (0 - ax[tid]) + (ax[tid] - bx[tid]) * (py - ay[tid])
        # x range for this scanline
        xs0 = np.minimum(np.minimum(ax[tid], bx[tid]), cx[tid])
        xs1 = np.maximum(np.maximum(ax[tid], bx[tid]), cx[tid])
        xa = np.clip(np.floor(xs0), 0, self.w - 1).astype(np.int64)
        xb = np.clip(np.ceil(xs1), 0, self.w - 1).astype(np.int64)
        span = np.maximum(xb - xa + 1, 0)
        tot2 = int(span.sum())
        if tot2 == 0:
            return
        wid = np.repeat(np.arange(total), span)
        ptr = np.repeat(xa, span) + (np.arange(tot2) - np.repeat(np.cumsum(span) - span, span))
        pxx = ptr.astype(np.float32) + 0.5
        t_ = tid[wid]
        iA = 1.0 / area[t_]
        l0 = (e0x[wid] * pxx + e0c[wid]) * iA
        l1 = (e1x[wid] * pxx + e1c[wid]) * iA
        l2 = (e2x[wid] * pxx + e2c[wid]) * iA
        inside = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6) & (ptr >= 0) & (ptr < self.w)
        if not inside.any():
            return
        t_, ptr, l0, l1, l2, py2 = t_[inside], ptr[inside], l0[inside], l1[inside], l2[inside], py[wid][inside]
        zz = l0 / az[t_] + l1 / bz[t_] + l2 / cz[t_]
        zz = 1.0 / np.maximum(zz, 1e-9)
        pix = py2.astype(np.int64) * self.w + ptr
        zi = self.z.reshape(-1)
        nearer = zz < zi[pix]
        pix, zz = pix[nearer], zz[nearer]
        if pix.size == 0:
            return
        zi[pix] = zz
        cf = self.col.reshape(-1, 3)
        # per-pixel colour: interpolate the three vertex colours
        cf[pix, 0] = rad[t_][nearer]  # flat-ish: vertex colours are similar within a tri
        cf[pix] = cols[t_][nearer]
        # keep proper attribute interpolation for smooth water
        self.col = cf.reshape(self.h, self.w, 3)


def clip_near(tris, sx, sy, z, attr, znear=0.06):
    """Clip triangles against the near plane (z > znear), in camera space.

    Only the triangles that actually cross the plane go through the Python loop; the
    rest are kept vectorised. (Looping over every triangle here was the single biggest
    cost in the whole renderer.)
    """
    zt = z[tris]
    need = (zt <= znear).any(1)
    if not need.any():
        return tris, sx, sy, z, attr
    keep = ~need
    SX, SY, Z, AT = list(sx), list(sy), list(z), list(attr)
    out = tris[keep].tolist()
    for T in tris[need]:
        zs = z[T]
        if (zs <= znear).all():
            continue
        poly = []
        for i in range(3):
            a, b = T[i], T[(i + 1) % 3]
            za, zb = z[a], z[b]
            if za > znear:
                poly.append(int(a))
            if (za > znear) != (zb > znear):
                t = (znear - za) / (zb - za)
                SX.append(sx[a] + (sx[b] - sx[a]) * t)
                SY.append(sy[a] + (sy[b] - sy[a]) * t)
                Z.append(znear)
                AT.append(attr[a] + (attr[b] - attr[a]) * t)
                poly.append(len(SX) - 1)
        for k in range(1, len(poly) - 1):
            out.append([poly[0], poly[k], poly[k + 1]])
    tris2 = np.asarray(out, np.int32) if len(out) else np.zeros((0, 3), np.int32)
    return tris2, np.asarray(SX, np.float32), np.asarray(SY, np.float32), \
           np.asarray(Z, np.float32), np.asarray(AT, np.float32)


def _raster_band(fr, sx, sy, z, tris, attr, blend, y0, y1, alpha=None):
    """Rasterise the part of the given triangles that falls inside rows [y0, y1)."""
    ax, ay = sx[tris[:, 0]], sy[tris[:, 0]]
    bx, by = sx[tris[:, 1]], sy[tris[:, 1]]
    cx, cy = sx[tris[:, 2]], sy[tris[:, 2]]
    az, bz, cz = z[tris[:, 0]], z[tris[:, 1]], z[tris[:, 2]]
    area = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)

    zmin, zmax = np.minimum(np.minimum(az, bz), cz), np.maximum(np.maximum(az, bz), cz)
    ok = ((np.abs(area) > 1e-7) & np.isfinite(ax) & np.isfinite(bx) & np.isfinite(cx)
          & np.isfinite(ay) & np.isfinite(by) & np.isfinite(cy)
          & (zmin > 0.06) & (zmax < 900.0)
          & (np.maximum(np.maximum(ay, by), cy) >= y0) & (np.minimum(np.minimum(ay, by), cy) < y1)
          & (np.maximum(np.maximum(ax, bx), cx) > 0) & (np.minimum(np.minimum(ax, bx), cx) < fr.w))
    if not ok.any():
        return
    tris = tris[ok]
    ax, ay, bx, by, cx, cy = ax[ok], ay[ok], bx[ok], by[ok], cx[ok], cy[ok]
    az, bz, cz = az[ok], bz[ok], cz[ok]
    inv_area = 1.0 / area[ok]

    ymin = np.clip(np.floor(np.minimum(np.minimum(ay, by), cy)), y0, y1 - 1).astype(np.int64)
    ymax = np.clip(np.ceil(np.maximum(np.maximum(ay, by), cy)), y0, y1 - 1).astype(np.int64)
    counts = np.maximum(ymax - ymin + 1, 0)
    total = int(counts.sum())
    if total == 0:
        return
    tid = np.repeat(np.arange(len(tris)), counts)
    rowstart = np.repeat(np.cumsum(counts) - counts, counts)
    py = (np.repeat(ymin, counts) + (np.arange(total) - rowstart)).astype(np.float32) + 0.5

    Ax, Ay, Bx, By, Cx, Cy = ax[tid], ay[tid], bx[tid], by[tid], cx[tid], cy[tid]
    e0x = -(Cy - By)                                   # edge BC, weight of A
    e0c = (Cy - By) * Bx + (Cx - Bx) * (py - By)
    e1x = -(Ay - Cy)                                   # edge CA, weight of B
    e1c = (Ay - Cy) * Cx + (Ax - Cx) * (py - Cy)
    e2x = -(By - Ay)                                   # edge AB, weight of C
    e2c = (By - Ay) * Ax + (Bx - Ax) * (py - Ay)

    # a triangle seen edge-on has a huge bbox but a thin row span: take the span from
    # where the edges actually cross this scanline, which is both correct and much
    # cheaper than evaluating the whole bounding box
    def cross(x0, y0, x1, y1):
        dy = y1 - y0
        safe = np.where(np.abs(dy) < 1e-6, 1.0, dy)
        xe = x0 + (py - y0) * (x1 - x0) / safe
        return np.where(np.abs(dy) < 1e-6, np.nan, xe)
    e_ab = cross(Ax, Ay, Bx, By)
    e_bc = cross(Bx, By, Cx, Cy)
    e_ca = cross(Cx, Cy, Ax, Ay)
    X = np.stack([e_ab, e_bc, e_ca], 1)
    with np.errstate(invalid="ignore"):
        xa = np.nanmin(X, axis=1)
        xb = np.nanmax(X, axis=1)
    bad = ~np.isfinite(xa) | ~np.isfinite(xb)
    xa = np.where(bad, np.minimum(np.minimum(Ax, Bx), Cx), xa)
    xb = np.where(bad, np.maximum(np.maximum(Ax, Bx), Cx), xb)
    xa = np.clip(np.floor(xa), 0, fr.w - 1).astype(np.int64)
    xb = np.clip(np.ceil(xb), 0, fr.w - 1).astype(np.int64)
    span = np.maximum(xb - xa + 1, 0)
    tot2 = int(span.sum())
    if tot2 == 0:
        return
    wid = np.repeat(np.arange(total), span)
    off = np.arange(tot2) - np.repeat(np.cumsum(span) - span, span)
    pix_x = np.repeat(xa, span) + off
    px = pix_x.astype(np.float32) + 0.5

    ia = inv_area[tid[wid]]
    l0 = (e0x[wid] * px + e0c[wid]) * ia
    l1 = (e1x[wid] * px + e1c[wid]) * ia
    l2 = (e2x[wid] * px + e2c[wid]) * ia
    ins = (l0 >= -1e-5) & (l1 >= -1e-5) & (l2 >= -1e-5)
    if not ins.any():
        return

    w = wid[ins]
    l0i, l1i, l2i = l0[ins], l1[ins], l2[ins]
    za, zb, zc = az[tid][w], bz[tid][w], cz[tid][w]
    zz = 1.0 / np.maximum(l0i / za + l1i / zb + l2i / zc, 1e-9)
    pix = py[w].astype(np.int64) * fr.w + pix_x[ins]
    zi = fr.z.reshape(-1)
    nearer = zz < zi[pix]
    if not nearer.any():
        return
    pix, zz = pix[nearer], zz[nearer]
    tri = tris[tid[w[nearer]]]
    L = np.stack([l0i[nearer], l1i[nearer], l2i[nearer]], 1)
    a_c = attr[tri[:, 0]] * L[:, :1] + attr[tri[:, 1]] * L[:, 1:2] + attr[tri[:, 2]] * L[:, 2:3]
    zi[pix] = zz
    if alpha is not None:
        at = alpha[tri[:, 0]] * L[:, 0] + alpha[tri[:, 1]] * L[:, 1] + alpha[tri[:, 2]] * L[:, 2]
        cf = fr.col.reshape(-1, 3)
        cf[pix] = cf[pix] * (1.0 - at[:, None]) + a_c * at[:, None]
    elif blend is None:
        fr.col.reshape(-1, 3)[pix] = a_c
    else:
        blend(fr, pix, a_c)


def cull_back(v, tris, normals, cam, centroid=None):
    """Drop triangles whose face points away from the camera.

    Works off the stored per-vertex normals (which point outward), so it is a plain
    half-space test and costs one dot product per triangle. It removes about half of
    the geometry before anything is rasterised.
    """
    tri = tris if tris.shape[1] == 3 else np.concatenate([tris[:, [0, 1, 2]], tris[:, [0, 2, 3]]], 0)
    P = v[tri].mean(1) if centroid is None else centroid
    view = cam.eye[None, :] - P
    nn = normals[tri[:, 0]]
    keep = (nn * view).sum(1) > 1e-4
    return tri[keep]


def raster_attr(fr, sx, sy, z, tris, attr, blend=None, band=160, alpha=None):
    """Near-plane clip, then rasterise in horizontal bands.

    Bands keep peak memory bounded: a handful of triangles that cover the whole
    frame would otherwise allocate a screen-worth of scratch per triangle at once.
    """
    if tris.shape[1] == 4:                     # a quad is two triangles
        tris = np.concatenate([tris[:, [0, 1, 2]], tris[:, [0, 2, 3]]], 0)
    if (z[tris] <= 0.06).any():
        tris, sx, sy, z, attr = clip_near(tris, sx, sy, z, attr)
        if len(tris) == 0:
            return
    for y0 in range(0, fr.h, band):
        _raster_band(fr, sx, sy, z, tris, attr, blend, y0, min(y0 + band, fr.h), alpha)


# ------------------------------------------------------------------ post
def aces(x):
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    return np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)


def blur(img, r):
    if r <= 0:
        return img
    k = int(r * 2 + 1)
    ker = np.exp(-0.5 * (np.arange(k) - r) ** 2 / max(r, 0.6) ** 2)
    ker /= ker.sum()
    out = img
    for ax in (0, 1):
        pad = [(0, 0)] * img.ndim
        pad[ax] = (r, r)
        z = np.pad(out, pad, mode="edge")
        acc = np.zeros_like(out)
        for i in range(k):
            acc += np.take(z, np.arange(i, i + out.shape[ax]), axis=ax) * ker[i]
        out = acc
    return out


def post(img, t, exposure=1.02, bloom=0.12, vign=0.30, grain=0.005, sat=1.26):
    x = aces(np.maximum(img, 0) * exposure)
    lum = x.mean(2, keepdims=True)
    hi = np.clip(lum - 0.72, 0, None)
    if bloom > 0:
        x = x + blur(hi * x, 5) * bloom * 2.2
    # subtle contrast S-curve, then tasteful saturation
    x = np.clip((x - 0.5) * 1.12 + 0.5, 0, 1)
    l = x.mean(2, keepdims=True)
    x = np.clip(l + (x - l) * sat, 0, 1)
    # split tone: cool the shadows, warm the highlights (a film grade, not a filter)
    sh_w = np.clip(0.62 - l, 0, 1)
    hi_w = np.clip(l - 0.55, 0, 1) * 1.6
    x = x + sh_w * np.array([-0.020, 0.004, 0.030], np.float32) + hi_w * np.array([0.035, 0.014, -0.020], np.float32)
    # vignette
    yy, xx = np.mgrid[0:x.shape[0], 0:x.shape[1]].astype(np.float32)
    cx, cy = x.shape[1] / 2, x.shape[0] / 2
    r = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2) / 1.414
    x = x * (1 - vign * np.clip(r, 0, 1) ** 2.1)[..., None]
    if grain:
        rng = np.random.default_rng(int(t * 1000) & 0xFFFF)
        x = x + (rng.standard_normal(x.shape[:2]).astype(np.float32) * grain)[..., None]
    return np.clip(x, 0, 1)


# ------------------------------------------------------------------ captions
FONT_PATHS = [
    os.path.join(HERE, "fonts", "Manrope-800.ttf"),
    "/home/user/Monarch.Overall.Work/public/showreel/fonts/Manrope-800.ttf",
]


def font(size):
    for p in FONT_PATHS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def wrap_caption(txt, fnt, maxw, draw):
    words = txt.split()
    lines, cur = [], ""
    for w in words:
        cand = (cur + " " + w).strip()
        if draw.textlength(cand, font=fnt) <= maxw or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_caption(img, txt, alpha, t):
    """Kinetic caption card: Manrope 800, uppercase, soft shadow, a slow 1.5 % push-in
    and a 6 px rise as it lands. Nothing else is ever drawn on the frame."""
    if not txt or alpha <= 0.01:
        return img
    H_, W_ = img.shape[:2]
    fnt = font(int(W_ * 0.072))
    pil = Image.fromarray((img * 255).astype(np.uint8))
    d = ImageDraw.Draw(pil)
    lines = wrap_caption(txt.upper(), fnt, int(W_ * 0.86), d)
    lh = int(fnt.size * 1.22)
    total = lh * len(lines)
    y0 = int(H_ * 0.795) - total // 2
    rise = (1.0 - min(1.0, alpha * 1.6)) * 6.0
    for i, ln in enumerate(lines):
        tw = d.textlength(ln, font=fnt)
        x = (W_ - tw) / 2
        y = y0 + i * lh + rise
        col = tuple(int(255 * (0.55 + 0.45 * alpha)) for _ in range(3))
        d.text((x + 2, y + 4), ln, font=fnt, fill=(0, 0, 0, 255))
        d.text((x, y), ln, font=fnt, fill=col)
    return np.asarray(pil, np.float32) / 255.0


def caption_at(caps, t):
    for c in caps:
        if c["start"] <= t < c["end"]:
            # 0.12 s fade in / out, and a 0.06 s cross-fade feel
            a = min(1.0, (t - c["start"]) / 0.12 + 0.15, (c["end"] - t) / 0.10)
            return c["text"], clamp(a)
    return None, 0.0


# ------------------------------------------------------------------ frame
def render_frame(t, static, caps):
    s = state(t)
    cam = shot_camera(t)
    fr = Frame(W, H)
    # --- sky
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ray = (cam.f[None, :] + cam.r[None, :] * ((xx - W / 2) / (0.5 * W) * cam.tan * (W / H))[..., None]
           + cam.u[None, :] * (-(yy - H / 2) / (0.5 * H) * cam.tan)[..., None])
    fr.col = sky_color(ray.reshape(-1, 3), t).reshape(H, W, 3)

    # --- static geometry
    v, n, c, k = static["v"], static["n"], static["c"], static["k"]
    sx, sy, z, vis = cam.project(v)
    shade_c = shade(v, n, c, k, cam, t, s)
    tri = cull_back(v, np.arange(len(v)).reshape(-1, 3), n, cam)
    raster_attr(fr, sx, sy, z, tri, shade_c)

    # --- gate leaves (animated on their hinges)
    for gz_i, gz in enumerate(GATE_Z):
        op = [s["gate_low"], s["gate_mid"], s["gate_up"], s["gate_up"]][gz_i]
        for leaf in GATE_LEAVES[gz_i * 2:gz_i * 2 + 2]:
            lv, ln, lc, lk = leaf["mesh"].arrays()
            th = leaf["base"] + math.radians(64.0) * smootherstep(op) * leaf["swing"]
            ct, st = math.cos(th), math.sin(th)
            P = lv.copy()
            P[:, 0] = leaf["hinge"][0] + lv[:, 0] * ct - lv[:, 2] * st
            P[:, 2] = leaf["hinge"][2] + lv[:, 0] * st + lv[:, 2] * ct
            NN = ln.copy()
            NN[:, 0] = ln[:, 0] * ct - ln[:, 2] * st
            NN[:, 2] = ln[:, 0] * st + ln[:, 2] * ct
            gsx, gsy, gz_, _ = cam.project(P)
            gc = shade(P, NN, lc, lk, cam, t, s)
            raster_attr(fr, gsx, gsy, gz_, np.arange(len(P)).reshape(-1, 3), gc)

    # --- ship
    sm = ship_mesh(s)
    sv, sn, sc, sk = sm.arrays()
    # heave / roll / pitch about the ship's own centre
    cz = s["ship_z"]
    piv = np.array([0, s["ship_y"], cz], np.float32)
    P = sv - piv
    rx, ry, rz = s["roll"], s["pitch"], 0.0
    cx, sxn = math.cos(rx), math.sin(rx)
    P = np.stack([P[:, 0], P[:, 1] * cx - P[:, 2] * sxn, P[:, 1] * sxn + P[:, 2] * cx], -1)
    cy, sy_ = math.cos(ry), math.sin(ry)
    P = np.stack([P[:, 0] * cy + P[:, 2] * sy_, P[:, 1], -P[:, 0] * sy_ + P[:, 2] * cy], -1)
    P = P + piv + np.array([0, s["heave"], 0], np.float32)
    NN = sn.copy()
    NN = np.stack([NN[:, 0], NN[:, 1] * cx - NN[:, 2] * sxn, NN[:, 1] * sxn + NN[:, 2] * cx], -1)
    NN = np.stack([NN[:, 0] * cy + NN[:, 2] * sy_, NN[:, 1], -NN[:, 0] * sy_ + NN[:, 2] * cy], -1)
    ssx, ssy, sz_, _ = cam.project(P)
    shc = shade(P, NN, sc, sk, cam, t, s)
    raster_attr(fr, ssx, ssy, sz_, np.arange(len(P)).reshape(-1, 3), shc)

    # --- water (drawn last among geometry: it is the surface we see through)
    w = render_water(cam, t, s)
    raster_attr(fr, w["sx"], w["sy"], w["depth"], w["quads"], w["col"], alpha=w["alpha"])

    # --- composite + grade + captions
    img = post(fr.col, t)
    txt, alpha = caption_at(caps, t)
    if txt:
        img = draw_caption(img, txt, alpha, t)
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


def main():
    align = json.load(open(os.path.join(HERE, "audio", "align.json")))
    caps = align["captions"]
    t0 = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    t1 = float(sys.argv[2]) if len(sys.argv) > 2 else DUR
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(OUT, "part.mp4")
    static = build_static()
    FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
    n = int(round((t1 - t0) * FPS))
    p = subprocess.Popen([FF, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                          "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
                         stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import time
    tstart = time.time()
    for i in range(n):
        t = t0 + i / FPS
        frame = render_frame(t, static, caps)
        p.stdin.write(frame.tobytes())
        if i % 15 == 0:
            el = time.time() - tstart
            print("frame %d/%d  %.2fs/frame" % (i, n, el / max(i, 1)), flush=True)
    p.stdin.close()
    p.wait()
    print("wrote", out, "%.1f s total" % (time.time() - tstart))


if __name__ == "__main__":
    main()
