"""Scene builders: cave, bear, skull, props. Pure geometry, no lighting."""
import math
import numpy as np
from engine import (node, merge, nrm, smoothstep, fbm, rotX, rotY, rotZ, clamp01,
                    vnoise, lerp)

# ---------------------------------------------------------------- palette
LIMESTONE = np.array([0.30, 0.286, 0.258], np.float32)
LIMESTONE_DK = np.array([0.155, 0.145, 0.130], np.float32)
BONE = np.array([0.66, 0.605, 0.492], np.float32)
FUR = np.array([0.0345, 0.0270, 0.0210], np.float32)


def _shell(centre, radii, n, rng, jitter=0.030):
    i = np.arange(n, dtype=np.float32) + 0.5
    phi = np.arccos(1 - 2 * i / n)
    theta = math.pi * (1 + 5 ** 0.5) * i
    sx = np.sin(phi) * np.cos(theta)
    sy = np.cos(phi)
    sz = np.sin(phi) * np.sin(theta)
    d = 1.0 + jitter * (rng.random(n, dtype=np.float32) - 0.5)
    p = np.stack([sx * radii[0] * d, sy * radii[1] * d, sz * radii[2] * d], 1) + np.asarray(centre, np.float32)
    nn = nrm(np.stack([sx / radii[0], sy / radii[1], sz / radii[2]], 1))
    return p, nn


# ---------------------------------------------------------------- CAVE

def cave(length=30.0, radius=3.6, seed=11, density=1.0):
    """Limestone tube: closed back, mouth at +z. Returns walls/floor nodes + anchors."""
    rng = np.random.default_rng(seed)
    n_ang = int(170 * density)
    n_len = int(330 * density)
    U, V = np.meshgrid(np.linspace(0, 1, n_ang), np.linspace(0, 1, n_len), indexing="ij")
    U = U.ravel().astype(np.float32)
    V = V.ravel().astype(np.float32)
    ang = U * math.pi * 2.0
    z = (V - 0.5) * length

    wide = (1.0 + 0.30 * np.sin(V * math.pi * 2.2 + 0.5)
            + 0.16 * np.sin(V * math.pi * 5.7 + 1.7)
            + 0.10 * np.sin(V * math.pi * 11.3 + 4.2))
    flare = 1.0 + 3.1 * smoothstep(0.855, 1.0, V) ** 2.2
    r = radius * wide * flare
    r = r + 0.42 * (fbm(np.cos(ang) * 2.4, np.sin(ang) * 2.4, V * 11.0, 4) - 0.5)
    r = r + 0.14 * (fbm(np.cos(ang) * 9.0, np.sin(ang) * 9.0, V * 30.0, 3) - 0.5)
    x = np.cos(ang) * r
    y = np.sin(ang) * r * 0.86
    zz = z + 0.30 * (fbm(U * 4.0, V * 9.0, 5.1, 3) - 0.5)
    # clamp floor: no wall below y=-2.55 so it meets the floor
    y = np.maximum(y, -2.55)
    P = np.stack([x, y, zz], 1).astype(np.float32)

    # normals from local surface: central differences on the grid
    Pg = P.reshape(n_ang, n_len, 3)
    du = np.gradient(Pg, axis=0)
    dv = np.gradient(Pg, axis=1)
    Nn = nrm(-np.cross(du.reshape(-1, 3), dv.reshape(-1, 3)))
    # flip so normals point inward (toward the axis)
    inward = -(P * np.array([1, 1, 0], np.float32))
    flip = (Nn * inward).sum(1) < 0
    Nn[flip] *= -1

    band = fbm(P[:, 0] * 0.55 + P[:, 2] * 0.22, P[:, 1] * 3.1, P[:, 2] * 0.55, 4)
    strata = np.sin(P[:, 1] * 7.0 + band * 6.0) * 0.5 + 0.5
    grime = fbm(P[:, 0] * 2.0, P[:, 1] * 2.0, P[:, 2] * 2.0, 3)
    speck = fbm(P[:, 0] * 14.0, P[:, 1] * 14.0, P[:, 2] * 14.0, 2)
    k = (0.66 + 0.52 * band) * (0.86 + 0.26 * grime) * (0.92 + 0.16 * strata) * (0.94 + 0.12 * speck)
    C = np.clip(LIMESTONE[None, :] * k[:, None], 0, 1)
    # damp/wet patches: darker + shinier
    wet = smoothstep(0.55, 0.78, fbm(P[:, 0] * 1.1, P[:, 1] * 1.1, P[:, 2] * 1.1, 3))
    C *= (1.0 - 0.45 * wet[:, None])
    S = 0.10 + 0.55 * wet
    walls = node(P, Nn, C, S=S, R=0.72 - 0.3 * wet, PX=0.045 / density)
    walls["AO"] = (0.30 + 0.70 * smoothstep(-2.6, 1.2, P[:, 1])).astype(np.float32)

    # floor: displaced plane, tighter than the walls
    nf = int(240 * density)
    X, Z = np.meshgrid(np.linspace(-1, 1, nf), np.linspace(-1, 1, nf), indexing="ij")
    X = X.ravel().astype(np.float32) * (radius * 2.0)
    Z = Z.ravel().astype(np.float32) * (length * 0.5)
    def hgt(xx, zz):
        return (0.30 * (fbm(xx * 0.55, 3.3, zz * 0.55, 4) - 0.5)
                + 0.085 * (fbm(xx * 3.4, 7.0, zz * 3.4, 3) - 0.5)
                + 0.022 * (fbm(xx * 12.0, 9.0, zz * 12.0, 2) - 0.5))
    h = hgt(X, Z)
    e = 0.05
    hx = hgt(X + e, Z)
    hz = hgt(X, Z + e)
    Nf = nrm(np.stack([-(hx - h) / e, np.ones_like(X), -(hz - h) / e], 1))
    g = fbm(X * 1.2, 5.5, Z * 1.2, 4)
    gravel = smoothstep(0.35, 0.75, fbm(X * 5.0, 2.0, Z * 5.0, 3))
    base = LIMESTONE_DK[None, :] * (0.60 + 0.80 * g)[:, None]
    base = base * (0.78 + 0.50 * gravel[:, None])
    floor = node(np.stack([X, h - 0.02, Z], 1), Nf, np.clip(base, 0, 1),
                 S=0.07 + 0.25 * gravel, R=0.95, PX=0.05 / density)
    floor["AO"] = (0.25 + 0.75 * (1.0 - smoothstep(0.30, 0.98, np.abs(X) / (radius * 2.0)))).astype(np.float32)
    return dict(walls=walls, floor=floor, length=length, radius=radius,
                mouth=np.array([0.0, 0.15, length * 0.5 - 0.4], np.float32))


# ---------------------------------------------------------------- BEAR

def _bear_parts(pose):
    if pose == "rear":
        return [((0.0, 1.00, 0.00), (0.64, 0.78, 0.54), 1.00),
                ((0.0, 1.72, 0.06), (0.46, 0.42, 0.44), 1.00),
                ((0.0, 2.10, 0.30), (0.35, 0.32, 0.36), 0.95),
                ((0.0, 2.02, 0.58), (0.20, 0.18, 0.22), 0.90),
                ((0.0, 2.26, 0.26), (0.32, 0.10, 0.26), 0.55),
                ((0.62, 1.52, 0.06), (0.23, 0.58, 0.25), 0.80),
                ((-0.62, 1.52, 0.06), (0.23, 0.58, 0.25), 0.80),
                ((0.31, 0.44, 0.04), (0.27, 0.46, 0.29), 0.80),
                ((-0.31, 0.44, 0.04), (0.27, 0.46, 0.29), 0.80)]
    if pose == "walk":
        return [((0.0, 0.94, 0.00), (0.47, 0.47, 0.96), 1.00),
                ((0.0, 1.06, 0.74), (0.37, 0.38, 0.38), 1.00),
                ((0.0, 1.06, 1.16), (0.31, 0.29, 0.32), 0.95),
                ((0.0, 0.98, 1.40), (0.18, 0.16, 0.19), 0.90),
                ((0.0, 1.20, 1.13), (0.27, 0.09, 0.21), 0.55),
                ((0.35, 0.58, 0.80), (0.13, 0.44, 0.15), 0.80),
                ((-0.35, 0.58, 0.66), (0.13, 0.44, 0.15), 0.80),
                ((0.27, 0.54, -0.66), (0.16, 0.44, 0.18), 0.80),
                ((-0.27, 0.54, -0.52), (0.16, 0.44, 0.18), 0.80)]
    if pose == "sleep":
        return [((0.0, 0.48, 0.00), (0.62, 0.44, 0.98), 1.00),
                ((0.0, 0.50, 0.88), (0.35, 0.31, 0.34), 0.95),
                ((0.0, 0.42, 1.10), (0.19, 0.16, 0.19), 0.90),
                ((0.52, 0.36, 0.74), (0.17, 0.17, 0.36), 0.70),
                ((-0.52, 0.36, 0.74), (0.17, 0.17, 0.32), 0.70)]
    if pose == "crawl":
        return [((0.0, 0.64, 0.00), (0.43, 0.37, 0.88), 1.00),
                ((0.0, 0.66, 0.82), (0.33, 0.29, 0.32), 0.95),
                ((0.0, 0.60, 1.05), (0.18, 0.15, 0.18), 0.90)]
    return [((0.0, 0.99, 0.00), (0.48, 0.51, 0.97), 1.00),
            ((0.0, 1.09, 0.75), (0.38, 0.39, 0.37), 1.00),
            ((0.0, 1.08, 1.16), (0.32, 0.30, 0.32), 0.95),
            ((0.0, 0.99, 1.40), (0.18, 0.16, 0.19), 0.90),
            ((0.0, 1.21, 1.13), (0.27, 0.09, 0.21), 0.55),
            ((0.34, 0.57, 0.80), (0.14, 0.45, 0.15), 0.80),
            ((-0.34, 0.57, 0.64), (0.14, 0.45, 0.15), 0.80),
            ((0.28, 0.53, -0.68), (0.16, 0.43, 0.17), 0.80),
            ((-0.28, 0.53, -0.52), (0.16, 0.43, 0.17), 0.80)]


def bear(pose="stand", scale=1.0, seed=3, detail=1.0, fur=None, head_rot=0.0, leg_phase=0.0):
    rng = np.random.default_rng(seed)
    fur = FUR if fur is None else np.asarray(fur, np.float32)
    parts = _bear_parts(pose)
    Ps, Ns, Ws, part_id = [], [], [], []
    for pi, (c, r, w) in enumerate(parts):
        area = 4 * math.pi * ((r[0] * r[1] + r[1] * r[2] + r[0] * r[2]) / 3.0)
        n = max(140, int(area * 780 * detail * (0.55 + 0.45 * w)))
        p, nn = _shell(c, r, n, rng, 0.045)
        # walk: swing legs around their hip
        if pose == "walk" and pi >= 5:
            front = pi in (5, 6)
            ph = leg_phase + (0.0 if pi in (5, 7) else math.pi)
            ang = math.sin(ph) * 0.42
            piv = (c[0], 1.02 if not front else 0.98, c[2] + (0.10 if front else -0.02))
            p = rotX(p, ang, piv)
            nn = rotX(nn + np.asarray(piv, np.float32), ang, (0, 0, 0)) - np.asarray(rotX(np.array([piv], np.float32), ang, (0, 0, 0))[0], np.float32)
        Ps.append(p); Ns.append(nn); Ws.append(np.full(len(p), w, np.float32))
        part_id.append(np.full(len(p), pi, np.float32))
    P = np.concatenate(Ps, 0)
    N = nrm(np.concatenate(Ns, 0))
    W = np.concatenate(Ws, 0)
    PID = np.concatenate(part_id, 0)

    # head yaw
    if head_rot:
        headmask = PID >= 2
        piv = np.array([0.0, 1.10, 0.90], np.float32)
        P[headmask] = rotY(P[headmask], head_rot, piv)
        N[headmask] = rotY(N[headmask], head_rot, (0, 0, 0))

    # fur: displace + clump, break the silhouette with a few stray strands
    clump = fbm(P[:, 0] * 26, P[:, 1] * 26, P[:, 2] * 26, 2)
    P = P + N * (((0.010 + 0.016 * clump) - 0.006)[:, None])
    stray = rng.random(len(P), dtype=np.float32) < 0.05
    P[stray] = P[stray] + N[stray] * 0.030

    # colour: fur base, lighter muzzle, darker legs, subtle warm variation
    C = np.repeat(fur[None, :], len(P), 0).copy()
    warm = fbm(P[:, 0] * 3.2, P[:, 1] * 3.2, P[:, 2] * 3.2, 3)
    C *= (0.72 + 0.72 * warm)[:, None]
    mz = smoothstep(1.30, 1.48, P[:, 2]) * smoothstep(1.28, 0.88, np.abs(P[:, 0]) + 0.6)
    muzzle = np.array([0.088, 0.062, 0.046], np.float32)
    C = C * (1 - mz[:, None] * 0.9) + muzzle[None, :] * (mz[:, None] * 0.9)
    low = smoothstep(0.65, 0.15, P[:, 1])
    C *= (1.0 - 0.45 * low[:, None])
    # nose leather (shiny black) at the tip
    tip = smoothstep(1.46, 1.52, P[:, 2]) * smoothstep(0.10, 0.03, np.abs(P[:, 0]))
    C = C * (1 - tip[:, None]) + np.array([0.010, 0.010, 0.012], np.float32)[None, :] * tip[:, None]

    # eyes: two emissive-ish dark glossy points (catch the torch as a hot dot)
    ep = []
    for sx in (-1, 1):
        ep.append(np.array([0.088 * sx, 1.14, 1.30], np.float32))
    ep = np.array(ep, np.float32)
    ew = rng.normal(0, 0.0055, (2, 3)).astype(np.float32)
    PE = ep + ew
    NE = nrm(np.stack([ep[:, 0] * 1.6, ep[:, 1] - 1.10, ep[:, 0] * 0 + 0.35], 1))
    nE = 260
    eyeP = np.repeat(PE, nE, 0) + rng.normal(0, 0.0042, (2 * nE, 3)).astype(np.float32)
    eyeN = np.repeat(NE, nE, 0)
    eyeC = np.repeat(np.array([[0.012, 0.010, 0.009]], np.float32), 2 * nE, 0)

    P = np.concatenate([P, eyeP], 0) * scale
    N = np.concatenate([N, eyeN], 0)
    C = np.concatenate([C, eyeC], 0)
    S = np.concatenate([np.full(len(P) - 2 * nE, 0.16, np.float32), np.full(2 * nE, 1.6, np.float32)])
    R = np.concatenate([np.full(len(P) - 2 * nE, 0.62, np.float32), np.full(2 * nE, 0.06, np.float32)])
    PX = np.concatenate([np.full(len(P) - 2 * nE, 0.020, np.float32), np.full(2 * nE, 0.006, np.float32)])
    out = node(P, N, C, S=S, R=R, PX=PX)
    return out


# ---------------------------------------------------------------- SKULL

def skull(scale=1.0, seed=2, detail=1.0, with_teeth=True):
    rng = np.random.default_rng(seed)
    parts = [((0.000, 0.000, -0.020), (0.118, 0.101, 0.138), 1.00),
             ((0.000, 0.030, -0.062), (0.076, 0.056, 0.100), 0.90),
             ((0.000, -0.006, 0.135), (0.071, 0.059, 0.096), 1.00),
             ((0.000, -0.012, 0.206), (0.047, 0.041, 0.056), 1.00),
             ((0.000, 0.052, 0.076), (0.100, 0.030, 0.066), 0.80),
             ((0.076, -0.020, 0.076), (0.030, 0.041, 0.071), 0.70),
             ((-0.076, -0.020, 0.076), (0.030, 0.041, 0.071), 0.70),
             ((0.000, 0.087, -0.010), (0.021, 0.025, 0.116), 0.55)]
    Ps, Ns = [], []
    for (c, r, w) in parts:
        area = 4 * math.pi * ((r[0] * r[1] + r[1] * r[2] + r[0] * r[2]) / 3.0)
        n = max(190, int(area * 6200 * detail * w))
        p, nn = _shell(c, r, n, rng, 0.020)
        Ps.append(p); Ns.append(nn)
    P = np.concatenate(Ps, 0)
    N = nrm(np.concatenate(Ns, 0))

    # eye sockets carved
    for sx in (-1, 1):
        eye = np.array([0.056 * sx, 0.018, 0.146], np.float32)
        d = np.linalg.norm(P - eye, axis=1)
        P = P - N * (smoothstep(0.055, 0.020, d)[:, None] * 0.032)
    # nasal aperture
    nas = np.array([0.0, -0.004, 0.234], np.float32)
    d = np.linalg.norm(P - nas, axis=1)
    P = P - N * (smoothstep(0.030, 0.008, d)[:, None] * 0.052)
    # occipital hole at the back
    occ = np.array([0.0, -0.010, -0.150], np.float32)
    d = np.linalg.norm(P - occ, axis=1)
    P = P - N * (smoothstep(0.040, 0.012, d)[:, None] * 0.030)

    P = P * scale
    N = N
    # bone colour with age stain, darkest inside cavities
    cav = 1.0 - smoothstep(0.015, 0.11, np.linalg.norm(P[:, :2], axis=1))
    stain = 0.78 + 0.28 * fbm(P[:, 0] * 9, P[:, 1] * 9, P[:, 2] * 9, 3)
    dirt = smoothstep(0.55, 0.85, fbm(P[:, 0] * 3.1, P[:, 1] * 3.1, P[:, 2] * 3.1, 3))
    C = (BONE[None, :] * stain[:, None]) * (0.52 + 0.48 * cav[:, None] ** 0.7)
    C *= (1.0 - 0.45 * dirt[:, None])
    S = 0.26 - 0.18 * dirt
    R = 0.40 + 0.25 * dirt
    PX = np.full(len(P), 0.0032 * scale, np.float32)

    if with_teeth:
        tp, tn = [], []
        for sx in (-1, 1):
            for k in range(10):
                tz = 0.082 + k * 0.0175
                ty = -0.050 - 0.012 * math.sin(k / 9.0 * math.pi)
                tx = sx * (0.042 - 0.0045 * k)
                tp.append((tx, ty, tz)); tn.append((0.0, 1.0, 0.14))
        TP = np.array(tp, np.float32)
        TN = nrm(np.array(tn, np.float32))
        cp, cn = [], []
        for c, nd in zip(TP, TN):
            i = np.arange(80, dtype=np.float32) + 0.5
            phi = np.arccos(1 - 2 * i / 80)
            th = math.pi * (1 + 5 ** 0.5) * i
            ex, ey, ez = np.sin(phi) * np.cos(th), np.cos(phi), np.sin(phi) * np.sin(th)
            blade = np.stack([ex * 0.0105, ey * 0.021 + 0.021, ez * 0.0085], 1)
            cp.append((blade + c) * scale)
            cn.append(nrm(np.stack([ex, ey * 2.6, ez], 1)))
        P = np.concatenate([P, np.concatenate(cp, 0)], 0)
        N = np.concatenate([N, np.concatenate(cn, 0)], 0)
        nt = 20 * 80
        C = np.concatenate([C, np.repeat(np.array([[0.58, 0.53, 0.40]], np.float32), nt, 0)], 0)
        S = np.concatenate([S, np.full(nt, 0.34, np.float32)])
        R = np.concatenate([R, np.full(nt, 0.26, np.float32)])
        PX = np.concatenate([PX, np.full(nt, 0.0016 * scale, np.float32)])

    return node(P, N, np.clip(C, 0, 1), S=S, R=R, PX=PX)


# ---------------------------------------------------------------- PROPS

def rock(centre, size=(0.4, 0.3, 0.35), seed=4, detail=1.0, tone=1.0):
    rng = np.random.default_rng(seed)
    n = int(650 * detail)
    p, nn = _shell((0, 0, 0), size, n, rng, 0.35)
    lump = fbm(p[:, 0] * 3.4, p[:, 1] * 3.4, p[:, 2] * 3.4, 4)
    p = p * (0.82 + 0.55 * lump[:, None])
    # re-derive normals from the displaced surface (approximate: keep + add lump bias)
    nn = nrm(nn + (lump[:, None] - 0.5) * 0.9 * nrm(p))
    p = p + np.asarray(centre, np.float32)
    g = fbm(p[:, 0] * 7, p[:, 1] * 7, p[:, 2] * 7, 3)
    C = np.clip((LIMESTONE * 1.35 * (0.7 + 0.7 * g)[:, None]) * tone, 0, 1)
    return node(p, nn, C, S=0.10, R=0.86, PX=0.02)


def bone_speck(centre, spread=(0.5, 0.12, 0.5), count=140, seed=9, size=1.0):
    rng = np.random.default_rng(seed)
    p = np.asarray(centre, np.float32) + rng.normal(0, 1, (count, 3)).astype(np.float32) * np.asarray(spread, np.float32)
    n = nrm(rng.normal(0, 1, (count, 3)))
    C = np.repeat((BONE * 0.62)[None, :], count, 0) * rng.uniform(0.6, 1.1, (count, 1)).astype(np.float32)
    return node(p, n, np.clip(C, 0, 1), S=0.18, R=0.6, PX=0.012 * size)


def dust(volume_centre, volume_size, count=900, seed=13, bright=1.0):
    rng = np.random.default_rng(seed)
    p = np.asarray(volume_centre, np.float32) + (rng.random((count, 3)).astype(np.float32) - 0.5) * np.asarray(volume_size, np.float32)
    n = nrm(rng.normal(0, 1, (count, 3)))
    C = np.repeat(np.array([[0.75, 0.72, 0.66]], np.float32) * bright, count, 0)
    return node(p, n, C, S=0.9, R=0.4, PX=0.0030, EM=0.10)


def wall_art(centre, normal, scale=1.0, seed=21):
    """Red ochre bear on a wall: points painted onto a plane patch."""
    rng = np.random.default_rng(seed)
    body = bear(pose="walk", scale=scale * 0.55, seed=seed, detail=0.55)
    P = body["P"]
    # flatten onto the wall plane, project along the wall normal
    nn = nrm(np.asarray(normal, np.float32))
    c = np.asarray(centre, np.float32)
    # rotate so +Z of the bear lies along the wall's horizontal axis
    side = nrm(np.cross(nn, np.array([0, 1, 0], np.float32)))
    up = np.cross(nn, side) * -1
    x = P @ side
    y = P @ np.array([0, 1, 0], np.float32)
    PP = c[None, :] + side[None, :] * (x - x.mean())[:, None] * 1.0 + np.array([0, 1, 0], np.float32)[None, :] * (y - y.mean())[:, None]
    PP = PP + nn[None, :] * 0.035
    # ochre: red, uneven, with negative space
    base = np.array([0.50, 0.115, 0.052], np.float32)
    wear = fbm(PP[:, 0] * 16, PP[:, 1] * 16, PP[:, 2] * 16, 3)
    keep = wear > 0.30
    PP = PP[keep]
    C = np.repeat(base[None, :], len(PP), 0) * (0.55 + 0.85 * wear[keep])[:, None]
    Nn = np.repeat(nn[None, :], len(PP), 0)
    return node(PP, Nn, np.clip(C, 0, 1), S=0.02, R=0.95, PX=0.008)


def torch(centre, scale=1.0, seed=31):
    """Burning torch: guttering flame particles + a hot core."""
    rng = np.random.default_rng(seed)
    n = 900
    t = rng.random(n).astype(np.float32)
    r = np.sqrt(rng.random(n).astype(np.float32)) * 0.030 * (1 - t * 0.55)
    a = rng.random(n).astype(np.float32) * math.pi * 2
    p = np.stack([np.cos(a) * r, t * 0.22, np.sin(a) * r], 1)
    p[:, 1] += (fbm(p[:, 0] * 40, p[:, 1] * 12, p[:, 2] * 40, 3) - 0.5) * 0.05
    p = p + np.asarray(centre, np.float32)
    C = np.stack([np.full(n, 1.0), 0.42 + 0.5 * (1 - t), 0.10 + 0.22 * (1 - t)], 1)
    Nn = nrm(rng.normal(0, 1, (n, 3)))
    d = node(p * np.array([1, 1, 1], np.float32), Nn, C, S=0.0, R=1.0, PX=0.010 * scale, EM=3.4)
    return d


def wall_torch(pos, seed=31):
    rng = np.random.default_rng(seed)
    stick = node(
        (np.asarray(pos, np.float32)[None, :] + np.array([0, -0.30, 0], np.float32)[None, :])
        + rng.normal(0, 0.02, (90, 3)).astype(np.float32) * np.array([1, 6, 1], np.float32),
        nrm(rng.normal(0, 1, (90, 3))), np.repeat(np.array([[0.055, 0.040, 0.028]], np.float32), 90, 0),
        S=0.1, R=0.8, PX=0.012)
    return stick


# ---------------------------------------------------------------- SKY / OUTSIDE

def sky_plate(cam, W, H, seed=7, snow=True, dawn=0.35):
    """Distant exterior plate: dusk sky, ridge line, falling snow. Linear light."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = yy / H
    u = xx / W
    d = cam.dir_of(xx.ravel(), yy.ravel()).reshape(H, W, 3)
    # sky gradient: cold blue above, warmer at the horizon
    horizon = 0.55 + 0.10 * np.sin(u * 4.0)
    t = np.clip((v - horizon) / 0.55, 0, 1)
    top = np.array([0.070, 0.135, 0.290], np.float32)
    mid = np.array([0.230, 0.330, 0.470], np.float32)
    low = np.array([0.520, 0.470, 0.400], np.float32)
    sky = lerp(mid[None, None, :], top[None, None, :], t[..., None] ** 0.8)
    below = np.clip((horizon - v) / 0.10, 0, 1)[..., None]
    sky = sky * (1 - below) + low[None, None, :] * below * 0.55
    # thin cloud bands
    cl = fbm(u * 5.0 + 3.0, v * 9.0, 1.7, 4)
    sky = sky * (1.0 + 0.35 * (cl - 0.5)[..., None])
    # ridge: silhouette of a limestone cliff, darker than the sky
    ridge = 0.62 + 0.045 * np.sin(u * 11.0 + 1.2) + 0.030 * np.sin(u * 27.0 + 0.4) + 0.05 * (fbm(u * 18, 2.2, 6.1, 4) - 0.5)
    m = (v > ridge)[..., None]
    land = np.array([0.030, 0.036, 0.044], np.float32)[None, None, :] * (0.7 + 0.6 * fbm(u * 30, v * 30, 3.0, 3)[..., None])
    out = sky * (1 - m) + land * m
    # a low sun/moon glow
    gx, gy = 0.72, ridge.min() - 0.10
    r = np.sqrt(((u - gx) * 1.6) ** 2 + (v - gy) ** 2)
    glow = np.exp(-(r ** 2) / 0.010)[..., None] * np.array([0.90, 0.72, 0.55], np.float32)
    out = out + glow * 0.55
    if snow:
        n = 520
        sx = rng.random(n) * W
        sy = rng.random(n) * H
        sz = rng.random(n)
        rad = 0.7 + sz * 1.5
        for i in range(n):
            r0 = int(max(0, sy[i] - rad[i])); r1 = int(min(H, sy[i] + rad[i] + 1))
            c0 = int(max(0, sx[i] - rad[i])); c1 = int(min(W, sx[i] + rad[i] + 1))
            if r1 <= r0 or c1 <= c0:
                continue
            out[r0:r1, c0:c1] += 0.55 * (1.0 - abs(sz[i] - 0.5))
    return out.astype(np.float32)
