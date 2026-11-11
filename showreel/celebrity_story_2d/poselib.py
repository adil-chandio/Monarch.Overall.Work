"""A library of *painted* poses, each on its own skeleton, blended by warp.

This is how hand-drawn animation is actually made. An animator does not rotate
one drawing until the joints give out; they draw the extremes and then draw the
frames between them. A rig is only ever used for the in-betweens, and a rig can
only be trusted over a small arc.

So the poses here are painted, not deformed. Each one gets its own skeleton,
registered to that drawing, and a transition between two poses is made by
warping *both* drawings onto one intermediate skeleton and dissolving:

    pose A --warp--> S(t) <--warp-- pose B

Warping both sides is the part that matters. Dissolving two un-warped drawings
ghosts, because a hand in one place cross-fades with a hand somewhere else.
Putting both through the same skeleton first means the difference the dissolve
has to hide is only shading, and the silhouette stays where the skeleton says
it is.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

import numpy as np
from PIL import Image

import skeleton as K

HERE = os.path.dirname(os.path.abspath(__file__))


# ----------------------------------------------------------------- keying
def key_green(rgb, tol=0.30, soft=0.06):
    """Alpha for a cel photographed on chroma-key green.

    The sheet is drawn on a flat green field, so the key is a distance in RGB
    rather than a colour pick. A soft band keeps the ink outline from being
    eaten, which is what makes a keyed character look chewed at the edges.
    """
    # measured from the sheet's own corners, not guessed from the hex swatch:
    # the render is not exactly #00b140 and a few hundredths of a shift leaves
    # a green halo on every edge
    key = np.array([0.018, 0.689, 0.293], np.float32)
    d = np.linalg.norm(rgb - key[None, None, :], axis=-1)
    a = np.clip((d - tol) / max(soft, 1e-6), 0, 1)
    # a green spill fringe: cheap despill so the outline does not glow
    g = rgb[..., 1]
    excess = np.clip(g - np.maximum(rgb[..., 0], rgb[..., 2]), 0, 1)
    rgb = rgb.copy()
    rgb[..., 1] = g - excess * 0.8
    return a.astype(np.float32), np.clip(rgb, 0, 1)


def trim(rgb, alpha, pad=6):
    ys, xs = np.nonzero(alpha > 0.35)
    if ys.size == 0:
        return rgb, alpha
    y0, y1 = max(0, ys.min() - pad), min(alpha.shape[0], ys.max() + pad)
    x0, x1 = max(0, xs.min() - pad), min(alpha.shape[1], xs.max() + pad)
    return rgb[y0:y1, x0:x1], alpha[y0:y1, x0:x1]


def fit_height(rgb, alpha, h, mode='contour'):
    """Scale a cel so the *figure* is h pixels tall, not the trimmed box.

    Trimming includes a little margin, so scaling by the box would make every
    pose a slightly different size — and a pose that is 3 % too tall pops when
    the dissolve starts.
    """
    ys, xs = np.nonzero(alpha > 0.5)
    if ys.size == 0:
        return rgb, alpha
    fh = float(ys.max() - ys.min() + 1)
    s = h / fh
    nw = max(1, int(round(rgb.shape[1] * s)))
    nh = max(1, int(round(rgb.shape[0] * s)))
    rgb_i = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))
    a_i = Image.fromarray((np.clip(alpha, 0, 1) * 255).astype(np.uint8))
    rgb = np.asarray(rgb_i.resize((nw, nh), Image.LANCZOS), np.float32) / 255.0
    alpha = np.asarray(a_i.resize((nw, nh), Image.LANCZOS), np.float32) / 255.0
    return rgb, alpha


# -------------------------------------------------------------- skeleton fit
# The rig, in fractions of figure height, for a standing figure whose top of
# head is y=0. These are the same proportions the painted model sheet was drawn
# to, so registering a pose is mostly a matter of finding the feet and the head.
PROPORTIONS = {
    'head_top':   (0.500, 0.030),
    'head':       (0.505, 0.105),
    'neck':       (0.520, 0.165),
    'chest':      (0.560, 0.270),
    'spine':      (0.545, 0.390),
    'pelvis':     (0.530, 0.500),
    'shoulder_l': (0.400, 0.200),
    'elbow_l':    (0.345, 0.360),
    'wrist_l':    (0.300, 0.505),
    'hand_l':     (0.285, 0.545),
    'shoulder_r': (0.640, 0.205),
    'elbow_r':    (0.690, 0.362),
    'wrist_r':    (0.720, 0.505),
    'hand_r':     (0.735, 0.545),
    'hip_l':      (0.435, 0.525),
    'knee_l':     (0.420, 0.720),
    'ankle_l':    (0.415, 0.930),
    'toe_l':      (0.450, 0.975),
    'hip_r':      (0.610, 0.525),
    'knee_r':     (0.625, 0.720),
    'ankle_r':    (0.635, 0.930),
    'toe_r':      (0.670, 0.975),
}

PARENTS = {
    'spine': 'pelvis', 'chest': 'spine', 'neck': 'chest', 'head': 'neck',
    'head_top': 'head',
    'shoulder_l': 'chest', 'elbow_l': 'shoulder_l', 'wrist_l': 'elbow_l',
    'hand_l': 'wrist_l',
    'shoulder_r': 'chest', 'elbow_r': 'shoulder_r', 'wrist_r': 'elbow_r',
    'hand_r': 'wrist_r',
    'hip_l': 'pelvis', 'knee_l': 'hip_l', 'ankle_l': 'knee_l', 'toe_l': 'ankle_l',
    'hip_r': 'pelvis', 'knee_r': 'hip_r', 'ankle_r': 'knee_r', 'toe_r': 'ankle_r',
}


def register_skeleton(alpha, lower_only=False):
    """Place the rig on a painted pose by measuring the drawing.

    The figure's own bounding box gives the height and its centre-line gives
    the horizontal placement, so two poses drawn at different sizes on the
    sheet still end up with the same rig proportions.
    """
    ys, xs = np.nonzero(alpha > 0.5)
    if ys.size == 0:
        raise ValueError('empty cel')
    h = float(ys.max() - ys.min() + 1)
    cy_top = float(ys.min())
    cx_l, cx_r = float(xs.min()), float(xs.max())
    w = cx_r - cx_l + 1
    joints = {}
    for name, (fx, fy) in PROPORTIONS.items():
        joints[name] = (cx_l + fx * w, cy_top + fy * h)
    sk = K.Skeleton(joints, PARENTS)
    return sk


# ---------------------------------------------------------------- the library
POSE_SHEET = os.path.join(HERE, 'assets', 'pose_sheet.png')
POSES = [
    # (name, sheet x0, x1) — measured from the column profile of the sheet
    ('stand',  26,  234),
    ('three_q', 260, 463),
    ('walk',   483, 713),
    ('raise',  717, 961),
    ('profile', 977, 1098),
    ('sit',    1120, 1390),
]


@dataclass
class Pose:
    name: str
    rgb: np.ndarray
    alpha: np.ndarray
    skel: K.Skeleton
    rest: np.ndarray

    @property
    def size(self):
        return self.alpha.shape[1], self.alpha.shape[0]


def load_poses(path=POSE_SHEET, target_h=1000, cache={}):
    """Cut the sheet into its six painted poses, each with its own rig."""
    key = (path, target_h)
    if key in cache:
        return cache[key]
    rgb = np.asarray(Image.open(path).convert('RGB'), np.float32) / 255.0
    alpha, rgb = key_green(rgb)
    out = {}
    for name, x0, x1 in POSES:
        r = rgb[:, x0:x1].copy()
        a = alpha[:, x0:x1].copy()
        r, a = trim(r, a)
        r, a = fit_height(r, a, target_h)
        sk = register_skeleton(a)
        out[name] = Pose(name, r, a, sk, sk.forward())
    cache[key] = out
    return out


def draw_rig(pose, path=None):
    """Overlay the registered joints on the drawing, for eyeballing a fit."""
    from PIL import ImageDraw
    im = Image.fromarray(np.dstack([(np.clip(pose.rgb, 0, 1) * 255).astype(np.uint8),
                                    (np.clip(pose.alpha, 0, 1) * 255).astype(np.uint8)]),
                         'RGBA')
    bg = Image.new('RGBA', im.size, (248, 248, 248, 255))
    bg.alpha_composite(im)
    d = ImageDraw.Draw(bg)
    sk = pose.skel
    for i in range(sk.n):
        p = int(sk.parents[i])
        if p >= 0:
            d.line([tuple(sk.rest[p]), tuple(sk.rest[i])], fill=(230, 40, 40), width=2)
        x, y = sk.rest[i]
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(20, 120, 240))
    if path:
        bg.convert('RGB').save(path)
    return bg


# --------------------------------------------------------------- retargeting
def retarget(pose, target, root=None):
    """Pose `target`'s joints back onto `pose`'s drawing.

    Walks the hierarchy parents-first. At each joint the drawing's own bone
    length is kept, but its direction is taken from the target, so the result
    has the target's gesture in the drawing's proportions. The root is placed
    at `root` (default: the drawing's own pelvis) — without that anchor the
    whole figure slides, which is what made the first attempt look random.
    """
    sk = pose.skel
    rest = np.asarray(pose.rest, np.float32)
    out = np.zeros_like(rest)
    order = []
    seen = set()
    while len(order) < sk.n:
        for i in range(sk.n):
            if i in seen:
                continue
            p = int(sk.parents[i])
            if p < 0 or p in seen:
                order.append(i)
                seen.add(i)
    anchor = rest[sk.index['pelvis']] if root is None else np.asarray(root, np.float32)
    for i in order:
        p = int(sk.parents[i])
        if p < 0:
            out[i] = rest[i] - rest[sk.index['pelvis']] + anchor
            continue
        tgt = np.asarray(target[i], np.float32) - np.asarray(target[p], np.float32)
        n = float(np.linalg.norm(tgt))
        cur_len = float(np.linalg.norm(rest[i] - rest[p]))
        if n < 1e-6:
            out[i] = out[p] + (rest[i] - rest[p])
            continue
        out[i] = out[p] + (tgt / n) * cur_len
    return out


def fit_to_slot(w, h=1000):
    """Target rig in a common slot: x across `w`, y down `h`, centred."""
    joints = {n: (fx * w, fy * h) for n, (fx, fy) in PROPORTIONS.items()}
    return K.Skeleton(joints, PARENTS)


# ------------------------------------------------------------------- blending
def _pad(rgb, alpha, pad):
    h, w = alpha.shape
    c = np.zeros((h + 2 * pad, w + 2 * pad, 3), np.float32)
    c[pad:pad + h, pad:pad + w] = rgb
    a = np.zeros((h + 2 * pad, w + 2 * pad), np.float32)
    a[pad:pad + h, pad:pad + w] = alpha
    return c, a


def _canvas_size(poses, pad):
    h = max(p.alpha.shape[0] for p in poses) + 2 * pad
    w = max(p.alpha.shape[1] for p in poses) + 2 * pad
    return w, h


def blend_poses(a, b, u, slot_w=340, slot_h=1000, pad=170):
    """One frame between two painted poses.

    Both drawings are retargeted onto the same skeleton for this instant, so
    the only difference the dissolve has to hide is shading — not the position
    of a hand. That is what stops the ghosting a plain cross-fade gives.
    """
    CW, CH = _canvas_size((a, b), pad)
    tgt = fit_to_slot(slot_w, slot_h).forward() + np.array([pad, pad], np.float32)

    out = None
    for pose, wgt in ((a, 1.0 - u), (b, u)):
        if wgt <= 0.001:
            continue
        rgb, alpha = _pad(pose.rgb, pose.alpha, pad)
        if alpha.shape[1] != CW or alpha.shape[0] != CH:
            rr = np.zeros((CH, CW, 3), np.float32)
            aa = np.zeros((CH, CW), np.float32)
            h, w = alpha.shape
            rr[:h, :w] = rgb
            aa[:h, :w] = alpha
            rgb, alpha = rr, aa
        posed = retarget(pose, tgt - np.array([pad, pad], np.float32),
                         root=tgt[pose.skel.index['pelvis']] - np.array([pad, pad], np.float32))
        vor = K.bone_voronoi(pose.skel, alpha.shape[1], alpha.shape[0])
        wrgb, walpha = K.deform(rgb, alpha, pose.skel, vor, pose.rest, posed,
                                alpha.shape[1], alpha.shape[0])
        wrgb = np.clip(wrgb, 0, 1)
        walpha = np.clip(walpha, 0, 1)[..., None]
        if out is None:
            out = [wrgb * wgt, walpha * wgt, wgt]
        else:
            out[0] += wrgb * wgt
            out[1] += walpha * wgt
            out[2] += wgt

    rgb_acc, a_acc, wsum = out
    wsum = max(wsum, 1e-6)
    # premultiplied average: dividing colour by the same weight as coverage
    # keeps a pixel that is opaque in only one drawing from turning see-through
    rgb = rgb_acc / np.maximum(a_acc, 1e-6)
    alpha = np.clip(a_acc / (wsum if wsum > 1 else 1.0), 0, 1)
    return np.clip(rgb, 0, 1), alpha[..., 0]
