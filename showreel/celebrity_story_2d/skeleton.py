"""Skeleton, skinning and motion for the painted 2D character.

This is real cutout character animation, the way Toon Boom Harmony, Spine and
DragonBones do it: the painted art supplies the texture, and a skeleton supplies
the motion. Bones are placed on the drawing's actual anatomy, pixels are weighted
to bones, and every frame is produced by posing that skeleton and re-skinning.

Nothing here draws a new character. It deforms the painted one, which is why the
face, the fabric folds and the line work stay exactly as painted while the body
moves.

Coordinates: cel space, y down, origin at the top-left of the trimmed cel, with
the figure normalised to 1000 px tall.
"""
from __future__ import annotations

import math

import numpy as np


# --------------------------------------------------------------------- bones
class Skeleton:
    """A 2D armature: joints in parent-relative rest positions."""

    def __init__(self, joints, parents):
        self.names = list(joints.keys())
        self.index = {n: i for i, n in enumerate(self.names)}
        self.rest = np.array([joints[n] for n in self.names], np.float32)
        self.parents = np.array([self.index.get(parents.get(n), -1)
                                 for n in self.names], np.int32)
        self.n = len(self.names)

    def forward(self, angles=None, offsets=None):
        """World positions of every joint for a set of local bone angles."""
        if angles is None:
            angles = np.zeros(self.n, np.float32)
        out = np.zeros((self.n, 2), np.float32)
        out[0] = self.rest[0]
        for i in range(1, self.n):
            p = self.parents[i]
            # rest offset, rotated by the accumulated rotation of the chain
            off = self.rest[i] - self.rest[p]
            world = out[p] + off
            out[i] = world
        if offsets is not None:
            out += np.asarray(offsets, np.float32)
        return out


def hero_skeleton():
    """Joints measured off the painted standing cel (311 x 1000).

    Values were read from the drawing, not guessed: shoulders at the suit's
    shoulder line, elbows where the sleeve breaks, wrists where the cuff ends,
    knees at the trouser crease, ankles at the shoe opening.
    """
    j = {
        'pelvis':      (160.0, 486.0),
        'spine':       (160.0, 400.0),
        'chest':       (160.0, 292.0),
        'neck':        (161.0, 212.0),
        'head':        (162.0, 120.0),
        'head_top':    (162.0, 22.0),
        'shoulder_l':  (96.0, 236.0),
        'elbow_l':     (76.0, 372.0),
        'wrist_l':     (70.0, 512.0),
        'hand_l':      (68.0, 556.0),
        'shoulder_r':  (232.0, 236.0),
        'elbow_r':     (250.0, 372.0),
        'wrist_r':     (256.0, 512.0),
        'hand_r':      (258.0, 556.0),
        'hip_l':       (140.0, 496.0),
        'knee_l':      (136.0, 700.0),
        'ankle_l':     (132.0, 934.0),
        'toe_l':       (150.0, 972.0),
        'hip_r':       (182.0, 496.0),
        'knee_r':      (188.0, 700.0),
        'ankle_r':     (192.0, 934.0),
        'toe_r':       (210.0, 972.0),
    }
    parents = {
        'spine': 'pelvis', 'chest': 'spine', 'neck': 'chest', 'head': 'neck',
        'head_top': 'head',
        'shoulder_l': 'chest', 'elbow_l': 'shoulder_l', 'wrist_l': 'elbow_l',
        'hand_l': 'wrist_l',
        'shoulder_r': 'chest', 'elbow_r': 'shoulder_r', 'wrist_r': 'elbow_r',
        'hand_r': 'wrist_r',
        'hip_l': 'pelvis', 'knee_l': 'hip_l', 'ankle_l': 'knee_l', 'toe_l': 'ankle_l',
        'hip_r': 'pelvis', 'knee_r': 'hip_r', 'ankle_r': 'knee_r', 'toe_r': 'ankle_r',
    }
    return Skeleton(j, parents)


# ------------------------------------------------------------------ skinning
# which bone owns which part of the drawing, as a painted region prior. Each
# entry is (bone, x0, y0, x1, y1) in cel space; overlaps are blended by weight.
def ownership_regions(skel, w, h):
    """Which strip of the drawing each bone is allowed to influence.

    These are measured from the drawing, not invented: the sleeve runs from
    x=18 to x=113, so nothing right of 118 can belong to a left-arm bone. That
    limit is what stops the jacket's edge being dragged along when the arm lifts.
    """
    j = skel.index
    r = skel.rest
    sl = r[j['shoulder_l']]; sr = r[j['shoulder_r']]
    hd = r[j['head']]; nk = r[j['neck']]; ch = r[j['chest']]
    pv = r[j['pelvis']]
    regions = [
        ('head',       0, 0, w, nk[1] + 34),
        ('head_top',  hd[0] - 40, 0, hd[0] + 40, hd[1] + 40),
        ('neck',       0, nk[1] - 34, w, ch[1] - 20),
        ('chest',      sl[0] + 4, ch[1] - 40, sr[0] - 4, pv[1] - 30),
        ('spine',      sl[0] + 4, ch[1] + 20, sr[0] - 4, pv[1] + 10),
        ('pelvis',     sl[0] + 4, pv[1] - 30, sr[0] - 4, pv[1] + 46),
        ('shoulder_l', 0, sl[1] - 40, sl[0] + 26, sl[1] + 90),
        ('elbow_l',    0, sl[1] + 60, r[j['elbow_l']][0] + 16, r[j['wrist_l']][1] - 10),
        ('wrist_l',    0, r[j['wrist_l']][1] - 40, r[j['wrist_l']][0] + 18, r[j['hand_l']][1] + 10),
        ('hand_l',     0, r[j['hand_l']][1] - 50, r[j['hand_l']][0] + 22, h),
        ('shoulder_r', sr[0] - 26, sr[1] - 40, w, sr[1] + 90),
        ('elbow_r',    r[j['elbow_r']][0] - 16, sr[1] + 60, w, r[j['wrist_r']][1] - 10),
        ('wrist_r',    r[j['wrist_r']][0] - 18, r[j['wrist_r']][1] - 40, w, r[j['hand_r']][1] + 10),
        ('hand_r',     r[j['hand_r']][0] - 22, r[j['hand_r']][1] - 50, w, h),
        ('hip_l',      0, pv[1], (sl[0] + sr[0]) / 2, r[j['knee_l']][1] + 40),
        ('knee_l',     0, r[j['knee_l']][1] - 60, (sl[0] + sr[0]) / 2, r[j['ankle_l']][1] - 30),
        ('ankle_l',    0, r[j['ankle_l']][1] - 70, (sl[0] + sr[0]) / 2, h),
        ('toe_l',      0, r[j['ankle_l']][1] - 20, (sl[0] + sr[0]) / 2, h),
        ('hip_r',      (sl[0] + sr[0]) / 2, pv[1], w, r[j['knee_r']][1] + 40),
        ('knee_r',     (sl[0] + sr[0]) / 2, r[j['knee_r']][1] - 60, w, r[j['ankle_r']][1] - 30),
        ('ankle_r',    (sl[0] + sr[0]) / 2, r[j['ankle_r']][1] - 70, w, h),
        ('toe_r',      (sl[0] + sr[0]) / 2, r[j['ankle_r']][1] - 20, w, h),
    ]
    # every bone needs a region: an unlisted bone is unpenalised everywhere and
    # silently steals pixels from the limb it happens to be nearest to
    listed = {b for b, *_ in regions}
    for i, name in enumerate(skel.names):
        if name in listed:
            continue
        p = int(skel.parents[i])
        a = r[i]
        b = r[p] if p >= 0 else a
        regions.append((name, min(a[0], b[0]) - 34, min(a[1], b[1]) - 34,
                        max(a[0], b[0]) + 34, max(a[1], b[1]) + 34))
    return regions


def bone_voronoi(skel, w, h):
    """Hard nearest-bone assignment: contiguous cells, no checkerboard.

    Blurred weights are right for deformable skin but wrong for choosing which
    bone carries a pixel: where two weights are nearly equal the argmax flips
    from pixel to pixel and the limb shatters. This computes the plain nearest
    segment instead, whose cells are connected by construction.
    """
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    pts = np.stack([xx, yy], -1)
    dist = np.zeros((skel.n, h, w), np.float32)
    for i in range(skel.n):
        p = int(skel.parents[i])
        a = skel.rest[i]
        b = skel.rest[p] if p >= 0 else a
        d = _seg_dist(pts, b, a)
        for bone, x0, y0, x1, y1 in ownership_regions(skel, w, h):
            if skel.index[bone] == i:
                xi0, yi0 = max(0, int(x0)), max(0, int(y0))
                xi1, yi1 = min(w, int(x1)), min(h, int(y1))
                inside = np.zeros((h, w), bool)
                inside[yi0:yi1, xi0:xi1] = True
                d = d + np.where(inside, 0.0, 400.0)
                break
        dist[i] = d
    return np.argmax(-dist, axis=0).astype(np.int32)


def skin_weights(skel, w, h, softness=28.0):
    """Per-pixel bone weights from distance to each bone segment.

    A pixel belongs to whichever bone is closest, with a soft transition at the
    boundary. This is what keeps a painted sleeve attached to the arm instead of
    tearing when the elbow bends.
    """
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    pts = np.stack([xx, yy], -1)
    n = skel.n
    dist = np.full((n, h, w), 1e9, np.float32)

    for i in range(n):
        a = skel.rest[i]
        p = skel.parents[i]
        if p < 0:
            seg_a = a
            seg_b = a
        else:
            seg_a = skel.rest[p]
            seg_b = a
        d = _seg_dist(pts, seg_a, seg_b)
        dist[i] = d

    # limit a bone's reach so an arm cannot pull the opposite leg: soft, so the
    # weight map stays smooth and the skin does not tear at region borders
    for bone, x0, y0, x1, y1 in ownership_regions(skel, w, h):
        idx = skel.index[bone]
        inside = np.zeros((h, w), bool)
        xi0, yi0 = max(0, int(x0)), max(0, int(y0))
        xi1, yi1 = min(w, int(x1)), min(h, int(y1))
        inside[yi0:yi1, xi0:xi1] = True
        dist[idx] = dist[idx] + np.where(inside, 0.0, 70.0)

    best = dist.min(axis=0)
    wts = np.exp(-((dist - best[None]) / softness) ** 2)
    wts[dist > 1e8] = 0.0
    tot = wts.sum(axis=0, keepdims=True)
    wts = wts / np.maximum(tot, 1e-6)
    # one light blur pass so neighbouring pixels do not jump between bones
    wts = np.stack([_blur(wts[i], 3.0) for i in range(wts.shape[0])])
    wts = wts / np.maximum(wts.sum(axis=0, keepdims=True), 1e-6)
    return wts


def _blur(a, radius):
    from PIL import Image, ImageFilter
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    im = im.filter(ImageFilter.GaussianBlur(radius))
    return np.asarray(im).astype(np.float32) / 255.0


def _regions_for(skel, w, h):
    """Ownership regions, mapped to whatever the skeleton is called."""
    out = []
    for bone, x0, y0, x1, y1 in ownership_regions(w, h):
        if bone in skel.index:
            out.append((bone, x0, y0, x1, y1))
    return out


def _seg_dist(pts, a, b):
    ab = b - a
    L2 = float(ab @ ab)
    if L2 < 1e-6:
        return np.sqrt(((pts - a[None, None, :]) ** 2).sum(-1))
    ap = pts - a[None, None, :]
    t = np.clip((ap[..., 0] * ab[0] + ap[..., 1] * ab[1]) / L2, 0, 1)
    proj = a[None, None, :] + t[..., None] * ab[None, None, :]
    return np.sqrt(((pts - proj) ** 2).sum(-1))


# ---------------------------------------------------------------- deformation
def joint_rotations(rest, posed, skel):
    """Accumulated world rotation of every joint, recovered from positions."""
    cum = np.zeros(skel.n, np.float32)
    for i in range(skel.n):
        p = int(skel.parents[i])
        if p < 0:
            continue
        vr = np.asarray(rest[i], np.float32) - np.asarray(rest[p], np.float32)
        vp = np.asarray(posed[i], np.float32) - np.asarray(posed[p], np.float32)
        cum[i] = math.atan2(vp[1], vp[0]) - math.atan2(vr[1], vr[0])
    for i in range(skel.n):
        p = int(skel.parents[i])
        if p >= 0:
            while cum[i] - cum[p] > math.pi:
                cum[i] -= math.tau
            while cum[i] - cum[p] < -math.pi:
                cum[i] += math.tau
    return cum


def _rigid(rest_p, posed_p, ang):
    """2x3 affine: rotate by ang about rest_p, then translate to posed_p."""
    c, s = math.cos(ang), math.sin(ang)
    R = np.array([[c, -s], [s, c]], np.float32)
    t = np.asarray(posed_p, np.float32) - R @ np.asarray(rest_p, np.float32)
    return np.array([[c, -s, t[0]], [s, c, t[1]]], np.float32)


def _inv_affine(M):
    det = float(M[0, 0] * M[1, 1] - M[0, 1] * M[1, 0])
    if abs(det) < 1e-9:
        return None
    A = np.array([[M[1, 1], -M[0, 1]], [-M[1, 0], M[0, 0]]], np.float32) / det
    return A, -(A @ M[:, 2])


def source_map(skel, weights, rest, posed, w, h):
    """Inverse-skinned source coordinates for every destination pixel.

    Linear blend skinning run backwards: each bone contributes the inverse of
    its rigid transform, blended by the pixel's weights.
    """
    cum = joint_rotations(rest, posed, skel)
    a11 = np.zeros((h, w), np.float32); a12 = np.zeros((h, w), np.float32)
    a21 = np.zeros((h, w), np.float32); a22 = np.zeros((h, w), np.float32)
    tx = np.zeros((h, w), np.float32); ty = np.zeros((h, w), np.float32)

    for i in range(skel.n):
        wi = weights[i]
        if float(wi.max()) < 1e-4:
            continue
        inv = _inv_affine(_rigid(rest[i], posed[i], float(cum[i])))
        if inv is None:
            continue
        A, t = inv
        a11 += wi * A[0, 0]; a12 += wi * A[0, 1]
        a21 += wi * A[1, 0]; a22 += wi * A[1, 1]
        tx += wi * t[0]; ty += wi * t[1]

    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    sx = a11 * xx + a12 * yy + tx
    sy = a21 * xx + a22 * yy + ty
    return sx, sy


def _bilinear(img, sx, sy):
    """Sample img (H,W,C) at fractional coords, clamp to edge."""
    h, w = img.shape[0], img.shape[1]
    x0 = np.floor(sx).astype(np.int32)
    y0 = np.floor(sy).astype(np.int32)
    fx = (sx - x0)[..., None].astype(np.float32)
    fy = (sy - y0)[..., None].astype(np.float32)
    x0c = np.clip(x0, 0, w - 1); x1c = np.clip(x0 + 1, 0, w - 1)
    y0c = np.clip(y0, 0, h - 1); y1c = np.clip(y0 + 1, 0, h - 1)
    p00 = img[y0c, x0c]; p10 = img[y0c, x1c]
    p01 = img[y1c, x0c]; p11 = img[y1c, x1c]
    top = p00 + (p10 - p00) * fx
    bot = p01 + (p11 - p01) * fx
    return top + (bot - top) * fy


def source_map_rigid(skel, weights, rest, posed, w, h):
    """Source coordinates using one rigid transform per pixel.

    Blending two rotations linearly shrinks the limb — the classic
    *candy-wrapper* collapse, which is why an arm pulled to 85 degrees came out
    as a sliver. A painted 2D character is a cutout, so each pixel is carried by
    a single bone: the one it belongs to most. The result is crisp and cannot
    shrink; the only cost is that the boundary between two bones is a seam,
    which the soft weight map already places where the drawing folds.
    """
    cum = joint_rotations(rest, posed, skel)
    dom = weights if weights.dtype == np.int32 else np.argmax(weights, axis=0)
    sx = np.arange(w, dtype=np.float32)[None, :].repeat(h, 0)
    sy = np.arange(h, dtype=np.float32)[:, None].repeat(w, 1)

    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    for i in range(skel.n):
        m = (dom == i)
        if not m.any():
            continue
        inv = _inv_affine(_rigid(rest[i], posed[i], float(cum[i])))
        if inv is None:
            continue
        A, t = inv
        sx = np.where(m, A[0, 0] * xx + A[0, 1] * yy + t[0], sx)
        sy = np.where(m, A[1, 0] * xx + A[1, 1] * yy + t[1], sy)
    return sx, sy


def deform(rgb, alpha, skel, weights, rest, posed, w=None, h=None, blend=False):
    """Warp the painted cel into a pose. Returns (rgb, alpha), same size."""
    h = h if h is not None else rgb.shape[0]
    w = w if w is not None else rgb.shape[1]
    if blend:
        sx, sy = source_map(skel, weights, rest, posed, w, h)
    else:
        sx, sy = source_map_rigid(skel, weights, rest, posed, w, h)
    stack = np.dstack([np.asarray(rgb, np.float32),
                       np.asarray(alpha, np.float32)[..., None]])
    out = _bilinear(stack, sx, sy)
    return out[..., :3], out[..., 3]
