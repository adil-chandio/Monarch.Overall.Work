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
def ownership_regions(w, h):
    s = h / 1000.0
    return [
        ('head',       0, 0, w, 205 * s),
        ('neck',       0, 195 * s, w, 232 * s),
        ('chest',      0, 215 * s, w, 340 * s),
        ('spine',      0, 320 * s, w, 440 * s),
        ('pelvis',     0, 430 * s, w, 520 * s),
        ('shoulder_l', 0, 205 * s, 150 * s, 330 * s),
        ('elbow_l',    0, 300 * s, 145 * s, 470 * s),
        ('wrist_l',    0, 430 * s, 145 * s, 600 * s),
        ('shoulder_r', 170 * s, 205 * s, w, 330 * s),
        ('elbow_r',    175 * s, 300 * s, w, 470 * s),
        ('wrist_r',    175 * s, 430 * s, w, 600 * s),
        ('hip_l',      0, 480 * s, w / 2, 620 * s),
        ('knee_l',     0, 590 * s, w / 2, 800 * s),
        ('ankle_l',    0, 780 * s, w / 2, 950 * s),
        ('toe_l',      0, 920 * s, w / 2, h),
        ('hip_r',      w / 2, 480 * s, w, 620 * s),
        ('knee_r',     w / 2, 590 * s, w, 800 * s),
        ('ankle_r',    w / 2, 780 * s, w, 950 * s),
        ('toe_r',      w / 2, 920 * s, w, h),
    ]


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
    for bone, x0, y0, x1, y1 in _regions_for(skel, w, h):
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
def deform(rgb, alpha, skel, weights, joint_from, joint_to, img_w, img_h):
    """Linear blend skinning of the painted cel.

    Each bone contributes the rigid transform that carries it from its rest
    placement to its posed placement. Pixels are pulled from the source by the
    inverse of that transform, weighted by the pixel's skin weights — the same
    maths a cutout rigger uses.
    """
    n = skel.n
    yy, xx = np.mgrid[0:img_h, 0:img_w].astype(np.float32)
    src_x = xx.copy()
    src_y = yy.copy()

    for i in range(n):
        wi = weights[i]
        if wi.max() < 1e-4:
            continue
        a0, a1 = joint_from[i], joint_to[i]
        p = skel.parents[i]
        if p >= 0:
            b0, b1 = joint_from[p], joint_to[p]
        else:
            # a root bone keeps its position: translate only
            b0, b1 = a0, a0 + (a1 - a0)
        m0 = _frame(b0, a0)
        m1 = _frame(b1, a1)
        try:
            rel = m1 @ np.linalg.inv(m0)
        except np.linalg.LinAlgError:
            continue
        # inverse map: where did this destination pixel come from?
        det = rel[0, 0] * rel[1, 1] - rel[0, 1] * rel[1, 0]
        if abs(det) < 1e-9:
            continue
        inv = np.array([[rel[1, 1], -rel[0, 1]],
                        [-rel[1, 0], rel[0, 0]]], np.float32) / det
        tx = xx - rel[0, 2]
        ty = yy - rel[1, 2]
        sx = inv[0, 0] * tx + inv[0, 1] * ty
        sy = inv[1, 0] * tx + inv[1, 1] * ty
        src_x += (sx - xx) * wi
        src_y += (sy - yy) * wi

    src_x = np.clip(np.round(src_x), 0, img_w - 1).astype(np.int32)
    src_y = np.clip(np.round(src_y), 0, img_h - 1).astype(np.int32)
    return rgb[src_y, src_x], alpha[src_y, src_x]


def _frame(base, tip):
    """2x3 affine frame of a bone, from its base joint to its tip."""
    v = tip - base
    ang = math.atan2(v[1], v[0])
    c, s = math.cos(ang), math.sin(ang)
    return np.array([[c, -s, base[0]],
                     [s, c, base[1]]], np.float32)
