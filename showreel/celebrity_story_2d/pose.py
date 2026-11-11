"""Forward kinematics and inverse kinematics for the 2D armature.

A pose is a dictionary of *local* joint rotations in degrees. Local means
"relative to the parent bone's current direction", which is what makes a
shoulder swing carry the elbow and hand with it — the single most obvious
difference between a rigged character and a rotated picture.

Two-bone IK is included because feet must stay planted while the hips travel:
you place the ankle, and the knee solves itself.
"""
from __future__ import annotations

import math

import numpy as np


def _order(skel):
    """Indices sorted so a parent always comes before its children."""
    cached = getattr(skel, '_order', None)
    if cached is not None:
        return cached
    out, seen = [], set()
    while len(out) < skel.n:
        for i in range(skel.n):
            if i in seen:
                continue
            p = int(skel.parents[i])
            if p < 0 or p in seen:
                out.append(i)
                seen.add(i)
    skel._order = out
    return out


def _rot(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s], [s, c]], np.float32)


def apply_pose(skel, rest, pose, root_offset=(0.0, 0.0)):
    """Return posed joint positions from a dict of local rotations."""
    order = _order(skel)
    posed = np.array(rest, np.float32).copy()
    cum = np.zeros(skel.n, np.float32)

    for i in order:
        p = int(skel.parents[i])
        local = float(pose.get(skel.names[i], 0.0))
        if p < 0:
            cum[i] = local
            posed[i] = posed[i] + np.asarray(root_offset, np.float32)
            continue
        cum[i] = cum[p] + local
        rel = np.asarray(rest[i], np.float32) - np.asarray(rest[p], np.float32)
        posed[i] = posed[p] + rel @ _rot(float(cum[i])).T
    return posed


def two_bone_ik(root, target, l1, l2, bend=1.0):
    """Solve a hip-knee-ankle or shoulder-elbow-wrist chain.

    Returns (mid, end). `bend` is +1 or -1 and picks which side the joint
    pops to: a knee bends backwards, an elbow forwards.
    """
    root = np.asarray(root, np.float32)
    target = np.asarray(target, np.float32)
    d = target - root
    n = float(np.linalg.norm(d))
    n = min(max(n, abs(l1 - l2) + 1e-3), l1 + l2 - 1e-3)
    if n < 1e-6:
        return root.copy(), root.copy()
    u = d / (float(np.linalg.norm(d)) + 1e-9)
    a = (l1 * l1 - l2 * l2 + n * n) / (2 * n)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    side = np.array([-u[1], u[0]], np.float32) * bend
    mid = root + u * a + side * h
    return mid, root + u * n


def subtree(skel, bone):
    idx = skel.index[bone]
    out = []
    for i in range(skel.n):
        j = i
        while j >= 0:
            if j == idx:
                out.append(i)
                break
            j = int(skel.parents[j])
    return out


def rotate_below(skel, posed, bone, deg, pivot=None):
    """World-rotate a bone and everything under it about a pivot."""
    idx = skel.index[bone]
    piv = posed[idx] if pivot is None else np.asarray(posed[pivot], np.float32)
    R = _rot(deg)
    out = posed.copy()
    for i in subtree(skel, bone):
        out[i] = piv + (posed[i] - piv) @ R.T
    return out


def place_chain(skel, posed, a, b, p, q):
    """Rigidly move bone a->b onto the position p->q (used after IK)."""
    out = posed.copy()
    src = np.asarray(posed[skel.index[b]], np.float32) - np.asarray(posed[skel.index[a]], np.float32)
    dst = np.asarray(q, np.float32) - np.asarray(p, np.float32)
    ang = math.degrees(math.atan2(dst[1], dst[0]) - math.atan2(src[1], src[0]))
    R = _rot(ang)
    out = rotate_below(skel, out, a, ang)
    delta = np.asarray(p, np.float32) - out[skel.index[a]]
    for i in subtree(skel, a):
        out[i] = out[i] + delta
    return out


def angle_between(a, b):
    d = np.asarray(b, np.float32) - np.asarray(a, np.float32)
    return math.degrees(math.atan2(d[1], d[0]))


def bone_len(rest, skel, bone):
    i = skel.index[bone]
    p = int(skel.parents[i])
    return float(np.linalg.norm(np.asarray(rest[i]) - np.asarray(rest[p])))
