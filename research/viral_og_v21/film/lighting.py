#!/usr/bin/env python3
"""Cave optics: analytic tube visibility, so light only enters where it can.

The cave is a tube whose radius is R(z). A straight ray from P to a light at L
is "visible" if it never leaves the tube. Marching that test is cheap and it
gives the falloff that makes a cave read as a cave: a bright mouth, a lit
throat, blackness behind you.
"""
from __future__ import annotations

import math

import numpy as np

from engine import nrm, smoothstep, clamp01


def profile(length, radius):
    """R(z) for the tube, matching scenes.cave()."""
    def R(z):
        V = np.clip((z / length) + 0.5, 0.0, 1.0)
        wide = (1.0 + 0.30 * np.sin(V * math.pi * 2.2 + 0.5)
                + 0.16 * np.sin(V * math.pi * 5.7 + 1.7)
                + 0.10 * np.sin(V * math.pi * 11.3 + 4.2))
        flare = 1.0 + 3.1 * smoothstep(0.855, 1.0, V) ** 2.2
        return radius * wide * flare
    return R


def tube_visibility(P, L, length, radius, steps=7, margin=0.90, soft=0.35):
    """Fraction of light from L that reaches each point of P without hitting rock."""
    P = np.asarray(P, np.float32)
    L = np.asarray(L, np.float32)
    R = profile(length, radius)
    d = L[None, :] - P
    dist = np.linalg.norm(d, axis=1)
    vis = np.ones(len(P), np.float32)
    worst = np.full(len(P), 1e3, np.float32)
    for i in range(1, steps + 1):
        t = i / (steps + 1.0)
        p = P + d * t
        ra = np.sqrt(p[:, 0] ** 2 + (p[:, 1] * 1.05) ** 2)
        rr = R(p[:, 2])
        # clearance normalised: 0 at the wall, 1 at the axis
        c = (rr - ra) / np.maximum(rr, 1e-3)
        worst = np.minimum(worst, c)
    # beyond the mouth, the tube opens up: allow rays that exit past the end
    beyond = P[:, 2] > length * 0.47
    vis = smoothstep(-soft, soft, worst)
    vis = np.where(beyond, np.maximum(vis, 0.85), vis)
    return clamp01(vis).astype(np.float32)


def sky_visibility(P, mouth, length, radius, steps=6):
    """Visibility of a distant sky through the mouth (same test, longer ray)."""
    return tube_visibility(P, mouth, length, radius, steps=steps, margin=0.85, soft=0.30)


def rig_mouth(mouth, power=200.0, col=(0.44, 0.62, 1.00), length=30.0, radius=3.6):
    return dict(pos=(mouth + np.array([0.0, 0.5, -0.2], np.float32)).tolist(),
                col=col, pow=float(power), cut=40.0, shadow=False,
                vis=dict(kind="tube", length=length, radius=radius))


def rig_torch(pos, power=15.0, col=(1.00, 0.56, 0.22), length=30.0, radius=3.6, flicker=1.0):
    return dict(pos=list(np.asarray(pos, np.float32)), col=col, pow=float(power),
                cut=26.0, shadow=False, vis=dict(kind="tube", length=length, radius=radius),
                flicker=flicker)


def apply_visibility(nd, lights, length, radius):
    """Attach a per-point, per-light visibility array to the node (shading input)."""
    vis = []
    for L in lights:
        if L.get("vis", {}).get("kind") == "tube":
            v = tube_visibility(nd["P"], np.asarray(L["pos"], np.float32), length, radius)
        else:
            v = np.ones(len(nd["P"]), np.float32)
        vis.append(v)
    return vis
