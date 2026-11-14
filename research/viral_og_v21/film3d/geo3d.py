#!/usr/bin/env python3
"""
EP01 — geometry and animation. Everything is procedural 3D. No images.

Cave   : implicit surface (tube + floor + mouth), analytic, so it can be
         raymarched per frame with correct parallax.
Bear   : metaball shell sampled into a dense point cloud; poses are morphable
         (stand <-> rear <-> walk) and the walk cycle is a real cycle with
         hip rotation, body bob and foot contact events.
Skull  : Ursus spelaeus proportions, carved sockets, teeth.
Dust   : particles with gravity, drag and curl-noise turbulence.
Torch  : flame particles + a flickering light with physically-plausible noise.
"""
from __future__ import annotations

import math

import numpy as np

SR = 48000
G = 9.81

# ------------------------------------------------------------------ noise


def _noise_table(seed=7, n=64):
    return np.random.default_rng(seed).random((n, n, n), dtype=np.float32)


_PG = _noise_table()
_N = 64


def vnoise(x, y, z):
    x = np.asarray(x, np.float32); y = np.asarray(y, np.float32); z = np.asarray(z, np.float32)
    fx0 = np.floor(x); fy0 = np.floor(y); fz0 = np.floor(z)
    xi = fx0.astype(np.int32) & (_N - 1)
    yi = fy0.astype(np.int32) & (_N - 1)
    zi = fz0.astype(np.int32) & (_N - 1)
    fx = x - fx0; fy = y - fy0; fz = z - fz0
    fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy); fz = fz * fz * (3 - 2 * fz)
    x1 = (xi + 1) & (_N - 1); y1 = (yi + 1) & (_N - 1); z1 = (zi + 1) & (_N - 1)
    c00 = _PG[xi, yi, zi] + (_PG[x1, yi, zi] - _PG[xi, yi, zi]) * fx
    c10 = _PG[xi, y1, zi] + (_PG[x1, y1, zi] - _PG[xi, y1, zi]) * fx
    c01 = _PG[xi, yi, z1] + (_PG[x1, yi, z1] - _PG[xi, yi, z1]) * fx
    c11 = _PG[xi, y1, z1] + (_PG[x1, y1, z1] - _PG[xi, y1, z1]) * fx
    c0 = c00 + (c10 - c00) * fy
    c1 = c01 + (c11 - c01) * fy
    return c0 + (c1 - c0) * fz


def fbm(x, y, z, oct=3, gain=0.5, lac=2.03):
    tot = np.zeros_like(np.asarray(x, np.float32))
    amp, fr = 1.0, 1.0
    for _ in range(oct):
        tot = tot + amp * vnoise(x * fr, y * fr, z * fr)
        amp *= gain; fr *= lac
    return tot


def nrm(v):
    v = np.asarray(v, np.float32)
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-8)


def smoothstep(a, b, x):
    t = np.clip((np.asarray(x, np.float32) - a) / (b - a if b != a else 1e-8), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def ease(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = np.clip(t, 0, 1)
    return 1 - (1 - t) ** 3


# ------------------------------------------------------------------ cave


class Cave:
    """A limestone tube with a floor, closed at the back, open at the mouth."""

    def __init__(self, length=30.0, radius=2.05, floor_y=-1.35, mouth_z=None,
                 chambers=((1.5, 2.4, 2.3), (-9.0, 3.0, 1.1))):
        self.L = length
        self.R0 = radius
        self.floor_y = floor_y
        self.mouth_z = length * 0.5 - 0.5 if mouth_z is None else mouth_z
        # a chamber is where the bore opens out; without one a 2.6 m animal cannot
        # be filmed from the side, because the camera would be inside the wall
        self.chambers = chambers
        self.mouth_z = length * 0.5 - 0.5 if mouth_z is None else mouth_z

    def radius_at(self, z):
        lut = getattr(self, "_lut", None)
        if lut is not None:
            return np.interp(z, self._lutz, lut).astype(np.float32)
        return self._radius_exact(z)

    def _build_lut(self, n=3072):
        z0, z1 = -self.L * 0.5 - 4.0, self.mouth_z + 4.0
        self._lutz = np.linspace(z0, z1, n).astype(np.float32)
        self._lut = self._radius_exact(self._lutz)
        return self

    def _radius_exact(self, z):
        z = np.asarray(z, np.float32)
        V = np.clip(z / self.L + 0.5, -0.3, 1.4)
        wide = (1.0 + 0.26 * np.sin(V * math.pi * 2.1 + 0.55)
                + 0.13 * np.sin(V * math.pi * 5.3 + 1.8)
                + 0.07 * np.sin(V * math.pi * 10.7 + 4.1))
        flare = 1.0 + 0.22 * smoothstep(0.86, 1.00, V) ** 1.5
        r = self.R0 * wide * flare
        for (zc, zh, extra) in self.chambers:
            r = r + extra * np.exp(-((z - zc) / zh) ** 2)
        return r

    def sdf(self, p):
        x = p[..., 0]; y = p[..., 1]; z = p[..., 2]
        th = np.arctan2(y / 0.80, x)
        # angle-dependent irregularity: the bore is not a circle
        wob = (1.0 + 0.20 * np.sin(3.0 * th + 0.7) + 0.12 * np.sin(5.0 * th + 2.1)
               + 0.06 * np.sin(9.0 * th + 4.4))
        r = np.sqrt(x ** 2 + (y / 0.80) ** 2)
        ft = r - self.radius_at(z) * wob
        ff = self.floor_y - p[..., 1]   # positive BELOW the floor = solid rock
        ft = np.where(p[..., 2] > self.mouth_z, -1e3, ft)
        ft = np.where(p[..., 2] < -self.L * 0.5, 1e3, ft)
        return np.minimum(ft, ff)

    def normal(self, p, e=0.012):
        """Surface normal facing the cave air. sdf > 0 is solid, so the gradient
        points into the rock; the visible normal is its negation."""
        gx = self.sdf(p + np.array([e, 0, 0], np.float32)) - self.sdf(p - np.array([e, 0, 0], np.float32))
        gy = self.sdf(p + np.array([0, e, 0], np.float32)) - self.sdf(p - np.array([0, e, 0], np.float32))
        gz = self.sdf(p + np.array([0, 0, e], np.float32)) - self.sdf(p - np.array([0, 0, e], np.float32))
        return nrm(-np.stack([gx, gy, gz], -1))


# ------------------------------------------------------------------ shapes


def _shell(centre, radii, n, rng, jitter=0.03):
    i = np.arange(n, dtype=np.float32) + 0.5
    phi = np.arccos(1 - 2 * i / n)
    th = math.pi * (1 + 5 ** 0.5) * i
    sx, sy, sz = np.sin(phi) * np.cos(th), np.cos(phi), np.sin(phi) * np.sin(th)
    d = 1.0 + jitter * (rng.random(n, dtype=np.float32) - 0.5)
    P = np.stack([sx * radii[0] * d, sy * radii[1] * d, sz * radii[2] * d], 1) + np.asarray(centre, np.float32)
    N = nrm(np.stack([sx / radii[0], sy / radii[1], sz / radii[2]], 1))
    return P, N


def rotX(P, a, pivot):
    p = np.asarray(pivot, np.float32)
    q = P - p
    c, s = math.cos(a), math.sin(a)
    return np.stack([q[:, 0], q[:, 1] * c - q[:, 2] * s, q[:, 1] * s + q[:, 2] * c], 1) + p


def rotY(P, a, pivot):
    p = np.asarray(pivot, np.float32)
    q = P - p
    c, s = math.cos(a), math.sin(a)
    return np.stack([q[:, 0] * c + q[:, 2] * s, q[:, 1], -q[:, 0] * s + q[:, 2] * c], 1) + p


# --- bear: 9 matching parts in both poses, so poses can be morphed ---------

BEAR_PARTS = {
    "stand": [((0.00, 0.99, 0.02), (0.48, 0.50, 0.95)),
              ((0.00, 1.10, 0.76), (0.38, 0.39, 0.37)),
              ((0.00, 1.09, 1.17), (0.32, 0.30, 0.32)),
              ((0.00, 0.99, 1.41), (0.18, 0.16, 0.19)),
              ((0.00, 1.21, 1.14), (0.27, 0.09, 0.21)),
              ((0.34, 0.57, 0.80), (0.14, 0.45, 0.15)),
              ((-0.34, 0.57, 0.64), (0.14, 0.45, 0.15)),
              ((0.28, 0.53, -0.70), (0.16, 0.43, 0.17)),
              ((-0.28, 0.53, -0.52), (0.16, 0.43, 0.17))],
    "rear": [((0.00, 1.02, 0.02), (0.62, 0.76, 0.55)),
             ((0.00, 1.74, 0.06), (0.46, 0.42, 0.44)),
             ((0.00, 2.12, 0.30), (0.35, 0.32, 0.36)),
             ((0.00, 2.04, 0.58), (0.20, 0.18, 0.22)),
             ((0.00, 2.28, 0.26), (0.32, 0.10, 0.26)),
             ((0.60, 1.54, 0.08), (0.23, 0.57, 0.25)),
             ((-0.60, 1.54, 0.08), (0.23, 0.57, 0.25)),
             ((0.30, 0.46, 0.04), (0.27, 0.46, 0.29)),
             ((-0.30, 0.46, 0.04), (0.27, 0.46, 0.29))],
}
LEG_IDX = (5, 6, 7, 8)
HIP = {5: (0.34, 1.02, 0.80), 6: (-0.34, 1.02, 0.64),
       7: (0.28, 1.00, -0.70), 8: (-0.28, 1.00, -0.52)}
PHASE = {5: 0.0, 6: math.pi, 7: math.pi, 8: 0.0}


def _pose_mix(a, b, u):
    A = BEAR_PARTS[a]; B = BEAR_PARTS[b]
    out = []
    for (ca, ra), (cb, rb) in zip(A, B):
        c = tuple(ca[i] + (cb[i] - ca[i]) * u for i in range(3))
        r = tuple(ra[i] + (rb[i] - ra[i]) * u for i in range(3))
        out.append((c, r))
    return out


def bear(t, pose=0.0, walk=0.0, phase=0.0, breathe=0.0, head_yaw=0.0,
         seed=11, density=1.0, fur_steps=1):
    """pose: 0 quadruped .. 1 rearing. walk: 0..1 how much of the gait is active."""
    rng = np.random.default_rng(seed)
    parts = _pose_mix("stand", "rear", pose) if pose > 0 else BEAR_PARTS["stand"]
    Ps, Ns, Ws, IDX = [], [], [], []
    for pi, (c, r) in enumerate(parts):
        w = 1.0 if pi < 5 else 0.82
        area = 4 * math.pi * ((r[0] * r[1] + r[1] * r[2] + r[0] * r[2]) / 3.0)
        n = max(420, int(area * 3000 * density * (0.6 + 0.4 * w)))
        P, N = _shell(c, r, n, rng, 0.045)
        if pi in LEG_IDX and walk > 0:
            ang = math.sin(phase + PHASE[pi]) * 0.40 * walk
            P = rotX(P, ang, HIP[pi])
            N = rotX(N + np.asarray(HIP[pi], np.float32), ang, (0, 0, 0)) - rotX(
                np.array([HIP[pi]], np.float32), ang, (0, 0, 0))[0]
        if pi == 1 and breathe:
            P = P + N * (0.012 * breathe)
        Ps.append(P); Ns.append(N); Ws.append(np.full(len(P), w, np.float32))
        IDX.append(np.full(len(P), pi, np.float32))
    P = np.concatenate(Ps); N = nrm(np.concatenate(Ns))
    W = np.concatenate(Ws); PID = np.concatenate(IDX)

    if head_yaw:
        m = PID >= 2
        piv = np.array([0.0, 1.10, 0.92], np.float32)
        P[m] = rotY(P[m], head_yaw, piv)
        N[m] = rotY(N[m], head_yaw, (0, 0, 0))

    # fur: clumped displacement + a broken silhouette
    cl = fbm(P[:, 0] * 24, P[:, 1] * 24, P[:, 2] * 24, 2)
    P = P + N * ((0.008 + 0.017 * cl) - 0.006)[:, None]
    if fur_steps:
        stray = rng.random(len(P), dtype=np.float32) < 0.055
        P[stray] += N[stray] * (0.022 + 0.02 * rng.random(stray.sum(), dtype=np.float32))[:, None]

    # colour: near-black fur with a warm tip and a lighter muzzle
    base = np.array([0.088, 0.064, 0.046], np.float32)
    C = np.repeat(base[None, :], len(P), 0)
    warm = fbm(P[:, 0] * 3.0, P[:, 1] * 3.0, P[:, 2] * 3.0, 3)
    C *= (0.70 + 0.85 * warm)[:, None]
    muz = smoothstep(1.34, 1.48, P[:, 2]) * smoothstep(0.13, 0.03, np.abs(P[:, 0]))
    C = C * (1 - muz[:, None]) + np.array([0.150, 0.108, 0.078], np.float32)[None, :] * muz[:, None]
    nose = smoothstep(1.50, 1.56, P[:, 2]) * smoothstep(0.075, 0.02, np.abs(P[:, 0]))
    C = C * (1 - nose[:, None]) + np.array([0.006, 0.006, 0.007], np.float32)[None, :] * nose[:, None]

    # eyes: wet black spheres -> the torch makes one hot specular dot
    eyeP, eyeN = [], []
    for sx in (-1, 1):
        c = np.array([0.090 * sx, 1.145, 1.315], np.float32)
        n = 320
        P2, N2 = _shell((0, 0, 0), (0.0125, 0.0125, 0.0125), n, rng, 0.0)
        eyeP.append(P2 + c)
        eyeN.append(N2)
    PE = np.concatenate(eyeP); NE = np.concatenate(eyeN)
    CE = np.repeat(np.array([[0.010, 0.008, 0.007]], np.float32), len(PE), 0)

    P = np.concatenate([P, PE]); N = np.concatenate([N, NE]); C = np.concatenate([C, CE])
    nfur = len(P) - len(PE)
    S = np.concatenate([np.full(nfur, 0.14, np.float32), np.full(len(PE), 2.2, np.float32)])
    Rg = np.concatenate([np.full(nfur, 0.66, np.float32), np.full(len(PE), 0.045, np.float32)])
    PX = np.concatenate([np.full(nfur, 0.0115, np.float32), np.full(len(PE), 0.0035, np.float32)])
    return dict(P=P.astype(np.float32), N=N.astype(np.float32), C=C.astype(np.float32),
                S=S, R=Rg, PX=PX, EM=np.zeros(len(P), np.float32))


def skull(scale=1.0, seed=3, density=1.0):
    rng = np.random.default_rng(seed)
    parts = [((0.000, 0.000, -0.020), (0.118, 0.101, 0.138)),
             ((0.000, 0.030, -0.062), (0.076, 0.056, 0.100)),
             ((0.000, -0.006, 0.135), (0.071, 0.059, 0.096)),
             ((0.000, -0.012, 0.206), (0.047, 0.041, 0.056)),
             ((0.000, 0.052, 0.076), (0.100, 0.030, 0.066)),
             ((0.076, -0.020, 0.076), (0.030, 0.041, 0.071)),
             ((-0.076, -0.020, 0.076), (0.030, 0.041, 0.071)),
             ((0.000, 0.087, -0.010), (0.021, 0.025, 0.116))]
    Ps, Ns = [], []
    for (c, r) in parts:
        area = 4 * math.pi * ((r[0] * r[1] + r[1] * r[2] + r[0] * r[2]) / 3.0)
        n = max(900, int(area * 30000 * density))
        P, N = _shell(c, r, n, rng, 0.02)
        Ps.append(P); Ns.append(N)
    P = np.concatenate(Ps); N = nrm(np.concatenate(Ns))
    for sx in (-1, 1):
        e = np.array([0.056 * sx, 0.018, 0.146], np.float32)
        P = P - N * (smoothstep(0.055, 0.020, np.linalg.norm(P - e, axis=1))[:, None] * 0.032)
    nas = np.array([0.0, -0.004, 0.234], np.float32)
    P = P - N * (smoothstep(0.030, 0.008, np.linalg.norm(P - nas, axis=1))[:, None] * 0.052)
    occ = np.array([0.0, -0.010, -0.150], np.float32)
    P = P - N * (smoothstep(0.040, 0.012, np.linalg.norm(P - occ, axis=1))[:, None] * 0.030)

    cav = 1.0 - smoothstep(0.015, 0.11, np.linalg.norm(P[:, :2], axis=1))
    stain = 0.76 + 0.30 * fbm(P[:, 0] * 9, P[:, 1] * 9, P[:, 2] * 9, 3)
    dirt = smoothstep(0.55, 0.85, fbm(P[:, 0] * 3.1, P[:, 1] * 3.1, P[:, 2] * 3.1, 3))
    bone = np.array([0.62, 0.565, 0.455], np.float32)
    C = (bone[None, :] * stain[:, None]) * (0.80 + 0.20 * cav[:, None] ** 0.7)
    C *= (1.0 - 0.42 * dirt)[:, None]
    S = 0.24 - 0.16 * dirt
    Rg = 0.42 + 0.24 * dirt
    PX = np.full(len(P), 0.0021, np.float32)

    # teeth
    tp = []
    for sx in (-1, 1):
        for k in range(10):
            tz = 0.082 + k * 0.0175
            ty = -0.050 - 0.012 * math.sin(k / 9.0 * math.pi)
            tx = sx * (0.042 - 0.0045 * k)
            tp.append((tx, ty, tz))
    cp, cn = [], []
    for c in np.array(tp, np.float32):
        i = np.arange(190, dtype=np.float32) + 0.5
        phi = np.arccos(1 - 2 * i / 190); th = math.pi * (1 + 5 ** 0.5) * i
        ex, ey, ez = np.sin(phi) * np.cos(th), np.cos(phi), np.sin(phi) * np.sin(th)
        cp.append(np.stack([ex * 0.0105, ey * 0.021 + 0.021, ez * 0.0085], 1) + c)
        cn.append(nrm(np.stack([ex, ey * 2.6, ez], 1)))
    P = np.concatenate([P, np.concatenate(cp)]); N = np.concatenate([N, np.concatenate(cn)])
    nt = 20 * 190
    C = np.concatenate([C, np.repeat(np.array([[0.55, 0.50, 0.38]], np.float32), nt, 0)])
    S = np.concatenate([S, np.full(nt, 0.32, np.float32)])
    Rg = np.concatenate([Rg, np.full(nt, 0.26, np.float32)])
    PX = np.concatenate([PX, np.full(nt, 0.0011, np.float32)])
    return dict(P=(P * scale).astype(np.float32), N=N.astype(np.float32),
                C=np.clip(C, 0, 1), S=S, R=Rg, PX=PX, EM=np.zeros(len(P), np.float32))


def bone_pile(centre, spread=(1.6, 0.28, 2.2), count=2600, seed=5):
    rng = np.random.default_rng(seed)
    P = np.asarray(centre, np.float32) + (rng.random((count, 3)).astype(np.float32) - 0.5) * np.asarray(spread, np.float32)
    P[:, 1] = np.minimum(P[:, 1], -2.35)
    N = nrm(rng.normal(0, 1, (count, 3)))
    C = np.repeat(np.array([[0.30, 0.27, 0.21]], np.float32), count, 0) * rng.uniform(0.5, 1.15, (count, 1)).astype(np.float32)
    S = rng.uniform(0.10, 0.30, count).astype(np.float32)
    return dict(P=P, N=N, C=np.clip(C, 0, 1), S=S, R=np.full(count, 0.55, np.float32),
                PX=np.full(count, 0.016, np.float32), EM=np.zeros(count, np.float32))


def rocks(centre, n=900, radius=0.7, seed=9):
    rng = np.random.default_rng(seed)
    P = np.asarray(centre, np.float32) + (rng.random((n, 3)).astype(np.float32) - 0.5) * np.asarray(radius, np.float32) * 2
    N = nrm(rng.normal(0, 1, (n, 3)))
    g = fbm(P[:, 0] * 6, P[:, 1] * 6, P[:, 2] * 6, 3)
    C = np.repeat(np.array([[0.26, 0.245, 0.22]], np.float32), n, 0) * (0.55 + 0.9 * g)[:, None]
    return dict(P=P, N=N, C=np.clip(C, 0, 1), S=np.full(n, 0.12, np.float32),
                R=np.full(n, 0.8, np.float32), PX=np.full(n, 0.024, np.float32),
                EM=np.zeros(n, np.float32))


def boulder(centre, radii=(0.42, 0.30, 0.42), n=14000, seed=17):
    """A squat dome sitting on the floor: the slab the skull rests on."""
    rng = np.random.default_rng(seed)
    P, N = _shell((0, 0, 0), radii, n, rng, 0.10)
    P[:, 1] = np.abs(P[:, 1])                       # keep the upper half -> dome
    N[:, 1] = np.abs(N[:, 1])
    wob = fbm(P[:, 0] * 5.5, P[:, 1] * 5.5, P[:, 2] * 5.5, 3) - 0.5
    P = P + N * (wob * 0.055)[:, None]
    P = P + np.asarray(centre, np.float32)
    g = fbm(P[:, 0] * 6, P[:, 1] * 6, P[:, 2] * 6, 3)
    C = np.repeat(np.array([[0.215, 0.203, 0.180]], np.float32), len(P), 0) * (0.62 + 0.80 * g)[:, None]
    return dict(P=P.astype(np.float32), N=nrm(N), C=np.clip(C, 0, 1),
                S=np.full(len(P), 0.10, np.float32), R=np.full(len(P), 0.82, np.float32),
                PX=np.full(len(P), 0.0062, np.float32), EM=np.zeros(len(P), np.float32))


# ------------------------------------------------------------------ particles


class Dust:
    """Airborne motes: gravity, drag, curl turbulence, respawn."""

    def __init__(self, n=1400, box=((-3.2, 3.2), (-2.3, 2.2), (-9.0, 9.0)), seed=21):
        self.rng = np.random.default_rng(seed)
        self.n = n
        self.lo = np.array([box[0][0], box[1][0], box[2][0]], np.float32)
        self.hi = np.array([box[0][1], box[1][1], box[2][1]], np.float32)
        self.P = self.lo + self.rng.random((n, 3)).astype(np.float32) * (self.hi - self.lo)
        self.V = (self.rng.normal(0, 0.02, (n, 3))).astype(np.float32)
        self.bright = self.rng.uniform(0.3, 1.0, n).astype(np.float32)

    def step(self, dt, t):
        # curl-ish turbulence from a drifting noise field
        e = 0.22
        fx = fbm(self.P[:, 0] / e + t * 0.35, self.P[:, 1] / e, self.P[:, 2] / e, 2) - 0.5
        fy = fbm(self.P[:, 0] / e, self.P[:, 1] / e + t * 0.3, self.P[:, 2] / e, 2) - 0.5
        fz = fbm(self.P[:, 0] / e, self.P[:, 1] / e, self.P[:, 2] / e + t * 0.4, 2) - 0.5
        self.V += np.stack([fx, fy * 0.4, fz], 1) * 0.22 * dt
        self.V[:, 1] -= 0.020 * dt            # motes are light: near-neutral buoyancy
        self.V *= (1.0 - 0.9 * dt)            # drag
        self.P += self.V * dt
        out = ((self.P < self.lo) | (self.P > self.hi)).any(1)
        if out.any():
            k = int(out.sum())
            self.P[out] = self.lo + self.rng.random((k, 3)).astype(np.float32) * (self.hi - self.lo)
            self.V[out] = self.rng.normal(0, 0.02, (k, 3)).astype(np.float32)
        return self.P.copy()


class Flame:
    """Torch flame: particles rising, cooling, dying, plus the light it casts."""

    def __init__(self, n=170, seed=31):
        self.rng = np.random.default_rng(seed)
        self.n = n
        self.age = self.rng.random(n).astype(np.float32)
        self.life = self.rng.uniform(0.35, 0.85, n).astype(np.float32)
        self.off = (self.rng.normal(0, 0.010, (n, 3))).astype(np.float32)

    def intensity(self, t):
        sn = (fbm(np.array([t * 7.0]), np.array([1.3]), np.array([2.1]), 3)[0]
              + 0.6 * fbm(np.array([t * 19.0]), np.array([4.1]), np.array([0.7]), 2)[0])
        return 0.82 + 0.55 * (sn - 0.5)

    def step(self, dt, base):
        self.age += dt / self.life
        dead = self.age > 1.0
        if dead.any():
            k = int(dead.sum())
            self.age[dead] = 0.0
            self.life[dead] = self.rng.uniform(0.35, 0.85, k).astype(np.float32)
            self.off[dead] = self.rng.normal(0, 0.010, (k, 3)).astype(np.float32)
        a = np.clip(self.age, 0, 1)
        r = (1.0 - a) * 0.055
        th = self.rng.random(self.n).astype(np.float32) * 6.283
        P = np.stack([np.cos(th) * r + self.off[:, 0],
                      np.asarray(base, np.float32)[1] + a * 0.30 + self.off[:, 1],
                      np.sin(th) * r + self.off[:, 2]], 1)
        P[:, 0] += (fbm(P[:, 0] * 12, a * 4, P[:, 2] * 12, 2) - 0.5) * 0.05
        heat = (1.0 - a) ** 1.4
        C = np.stack([np.ones(self.n, np.float32),
                      0.30 + 0.55 * heat,
                      0.04 + 0.20 * heat], 1)
        return P.astype(np.float32), C, heat


class Embers:
    """Sparks that leave the fire, drift, cool and die. Purely additive."""

    def __init__(self, n=120, seed=77):
        self.rng = np.random.default_rng(seed)
        self.n = n
        self.age = self.rng.random(n).astype(np.float32)
        self.life = self.rng.uniform(1.1, 3.0, n).astype(np.float32)
        self.v = np.stack([self.rng.normal(0, 0.18, n), self.rng.uniform(0.35, 0.95, n),
                           self.rng.normal(0, 0.18, n)], 1).astype(np.float32)
        self.ph = self.rng.random(n).astype(np.float32) * 6.283

    def step(self, dt, base, t=0.0):
        self.age += dt / self.life
        dead = self.age > 1.0
        if dead.any():
            k = int(dead.sum())
            self.age[dead] = 0.0
            self.life[dead] = self.rng.uniform(1.1, 3.0, k).astype(np.float32)
            self.v[dead] = np.stack([self.rng.normal(0, 0.18, k), self.rng.uniform(0.35, 0.95, k),
                                     self.rng.normal(0, 0.18, k)], 1)
        a = np.clip(self.age, 0, 1)
        b = np.asarray(base, np.float32)
        swirl = np.stack([np.sin(a * 9 + self.ph) * 0.10 * a,
                          np.zeros(self.n), np.cos(a * 7 + self.ph * 1.3) * 0.10 * a], 1)
        P = b + swirl + self.v * (a * self.life)[:, None] * 0.55
        P[:, 1] += 0.18
        heat = np.clip(1.0 - a, 0, 1) ** 2.2 * self.rng.uniform(0.6, 1.0, self.n).astype(np.float32)
        return P.astype(np.float32), heat.astype(np.float32)


def torch_prop(base, seed=41):
    """A hand torch: charred handle points plus a flame cluster."""
    rng = np.random.default_rng(seed)
    n = 260
    t = rng.random(n).astype(np.float32)
    P = np.stack([(rng.normal(0, 0.008, n)).astype(np.float32),
                  -t * 0.42, (rng.normal(0, 0.008, n)).astype(np.float32)], 1)
    N = nrm(np.stack([np.ones(n), np.zeros(n), np.zeros(n)], 1))
    C = np.repeat(np.array([[0.055, 0.040, 0.028]], np.float32), n, 0) * rng.uniform(0.6, 1.2, (n, 1)).astype(np.float32)
    handle = dict(P=(P + np.asarray(base, np.float32)).astype(np.float32), N=N,
                  C=np.clip(C, 0, 1), S=np.full(n, 0.08, np.float32),
                  R=np.full(n, 0.85, np.float32), PX=np.full(n, 0.010, np.float32),
                  EM=np.zeros(n, np.float32))
    return handle
