"""The character: painted regions cut apart and bound to the armature.

A single drawing cannot be posed, because when an arm swings away it leaves a
hole in the jacket. Real cutout rigs paint the torso without arms and lay the
arms over it. This module gets the same result out of the drawing by itself:

  * the ink lines inside the drawing are used as walls, and a flood fill splits
    the cel into its painted regions (sleeve, forearm, hand, jacket, trouser…),
  * the regions that belong to an arm become that arm's layer,
  * the hole the arm leaves *inside the jacket* is filled by diffusing the
    jacket's own colour inward, and the filled pixels are bound to the torso,
  * each layer gets its own weight map, so an arm cannot drag the jacket.

No colour, texture or shape is invented: the fill is made of jacket pixels.
"""
from __future__ import annotations

from collections import deque

import numpy as np

import skeleton as K


# ------------------------------------------------------------------- utilities
def _box_blur(img, k=2):
    out = np.asarray(img, np.float32)
    for axis in (0, 1):
        acc = np.zeros_like(out)
        for d in range(-k, k + 1):
            acc += np.roll(out, d, axis=axis)
        out = acc / (2 * k + 1)
    return out


def _grid(w, h):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    return np.stack([xx, yy], -1).astype(np.float32)


def inpaint(rgb, hole, iters=70, relax=120, k=2):
    """Fill `hole` (1 = missing) from the surrounding pixels.

    Two stable steps: a normalised convolution blur carries nearby colour
    inward, then a Laplace relaxation smooths the patch until it matches its own
    boundary. No feedback loop, so values cannot run away.
    """
    hole = np.clip(np.asarray(hole, np.float32), 0, 1)
    rgb = np.asarray(rgb, np.float32)
    if hole.max() < 1e-3:
        return rgb

    col = rgb * (1 - hole)[..., None]
    cov = (1 - hole)[..., None].astype(np.float32)
    for _ in range(iters):
        col = _box_blur(col, k)
        cov = _box_blur(cov, k)
    est = np.clip(col / np.maximum(cov, 1e-3), 0, 1)

    out = np.where(hole[..., None] > 0, est, rgb).astype(np.float32)
    m = (hole > 0.02)[..., None]
    for _ in range(relax):
        nb = 0.25 * (np.roll(out, 1, 0) + np.roll(out, -1, 0) +
                     np.roll(out, 1, 1) + np.roll(out, -1, 1))
        out = np.where(m, nb, out)
    return np.clip(out, 0, 1)


def ink_regions(rgb, body, dark=0.22, grad=0.10, min_px=150):
    """Split a cel into painted regions, using its own lines as walls.

    Two kinds of wall are used: the dark contour the artist drew, and any strong
    luminance step. That is what separates a sleeve from the jacket behind it
    when both are the same charcoal.
    """
    lum = np.asarray(rgb, np.float32).mean(2)
    gx = np.abs(np.roll(lum, 1, 1) - np.roll(lum, -1, 1))
    gy = np.abs(np.roll(lum, 1, 0) - np.roll(lum, -1, 0))
    wall = (lum < dark) | (np.hypot(gx, gy) > grad)
    free = body & ~wall
    h, w = free.shape
    lbl = np.zeros((h, w), np.int32)
    cur = 0
    for sy in range(h):
        for sx in np.nonzero(free[sy])[0]:
            if lbl[sy, sx]:
                continue
            cur += 1
            q = deque([(sy, sx)])
            lbl[sy, sx] = cur
            n = 0
            while q:
                y, x = q.popleft()
                n += 1
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w and free[yy, xx] and not lbl[yy, xx]:
                        lbl[yy, xx] = cur
                        q.append((yy, xx))
            if n < min_px:
                lbl[lbl == cur] = 0
    return lbl


def limb_masks(lbl, skel, tol=20.0, max_px=20000):
    """Arm masks from the cel's own regions.

    A region belongs to an arm when it lies wholly on that side of the shoulder
    and inside the arm's vertical span. That test alone rejects the jacket (it
    crosses the chest), the trousers (they run below the hand) and the head.
    """
    j = skel.index; rest = skel.rest
    h, w = lbl.shape
    out = {}
    full = {}
    for s in ('l', 'r'):
        sh = rest[j['shoulder_' + s]]
        hand = rest[j['hand_' + s]]
        y0 = min(sh[1], hand[1]) - 44
        y1 = max(sh[1], hand[1]) + 58
        keep = np.zeros((h, w), np.float32)
        for rid in np.unique(lbl):
            if rid <= 0:
                continue
            m = lbl == rid
            ys, xs = np.nonzero(m)
            if xs.size > max_px or xs.size == 0:
                continue
            if ys.min() < y0 or ys.max() > y1:
                continue
            if s == 'l' and xs.max() > rest[j['shoulder_l']][0] + tol:
                continue
            if s == 'r' and xs.min() < rest[j['shoulder_r']][0] - tol:
                continue
            keep[m] = 1.0
        full[s] = keep.copy()
        # a region can run down the jacket's front panel; only the part of it
        # that actually lies over the arm belongs to the arm
        px = _grid(w, h)
        pts = [rest[j['shoulder_' + s]], rest[j['elbow_' + s]],
               rest[j['wrist_' + s]], rest[j['hand_' + s]]]
        d = np.full((h, w), 1e9, np.float32)
        for a, b in ((pts[0], pts[1]), (pts[1], pts[2]), (pts[2], pts[3])):
            a = np.asarray(a, np.float32); b = np.asarray(b, np.float32)
            ab = b - a
            t = np.clip(((px - a) @ ab) / max(float(ab @ ab), 1e-6), 0, 1)
            d = np.minimum(d, np.linalg.norm(px - (a + t[..., None] * ab), axis=-1))
        keep *= np.clip((44.0 - d) / 5.0, 0, 1)
        out[s] = _box_blur(keep, 1)
    return out, {k: _box_blur(v, 1) for k, v in full.items()}


# ------------------------------------------------------------------- the rig
class Character:
    """A painted cel cut into layers and bound to the armature."""

    def __init__(self, rgb, alpha, skel=None, fill=True, scale_to=None):
        rgb = np.asarray(rgb, np.float32)
        alpha = np.clip(np.asarray(alpha, np.float32), 0, 1)
        self.h, self.w = alpha.shape
        self.skel = skel or K.hero_skeleton()
        if scale_to:
            self.skel = _scale_skel(self.skel, scale_to / 1000.0)
        self.rest = self.skel.forward()
        self.body = (alpha > 0.45).astype(np.float32)
        self.rgb = rgb

        lbl = ink_regions(rgb, self.body > 0.5)
        self.labels = lbl
        mask, cut = limb_masks(lbl, self.skel)
        # Cut generously: the sleeve, its ink outline and a little margin, so no
        # pale rim of the old sleeve survives in the base.
        self.cut = {s: np.clip(_box_blur(cut[s], 4) * 1.6, 0, 1) for s in ('l', 'r')}
        # The arm layer is the sleeve only, no margin, so it drops back exactly
        # over its own pixels at rest and cannot spill onto the chest.
        self.arm_alpha = {s: np.clip(_box_blur(mask[s], 1) * 1.2, 0, 1) for s in ('l', 'r')}
        self.arm_mask = mask

        # the hole an arm leaves inside the torso, which must be painted under
        torso = self._torso_weights_only()
        self.hole = {s: np.clip(self.cut[s] * torso, 0, 1) for s in ('l', 'r')}

        # the fill must never stand in for the sleeve itself: only the part of
        # the arm that lies behind the jacket is invisible at rest
        sleeves0 = np.clip(self.arm_alpha['l'] + self.arm_alpha['r'], 0, 1)
        undrawn = np.clip(1.0 - sleeves0, 0, 1)
        self.hole = {s: np.clip(self.hole[s] * undrawn, 0, 1) for s in ('l', 'r')}
        self.undrawn = undrawn
        all_hole = np.clip(self.cut['l'] + self.cut['r'], 0, 1)
        if fill and all_hole.max() > 0.01:
            self.base_rgb = np.where(all_hole[..., None] > 0.02,
                                     inpaint(rgb, all_hole), rgb)
        else:
            self.base_rgb = rgb.copy()

        # The base is the body with the sleeves taken off, plus the jacket that
        # was painted in behind them. The sleeve itself lives only in the arm
        # layers, so the arm can never be drawn twice.
        sleeves = np.clip(self.cut['l'] + self.cut['r'], 0, 1)
        self.base_alpha = np.clip(self.body - sleeves, 0, 1)


        self.voronoi = K.bone_voronoi(self.skel, self.w, self.h)
        self.v_arm = {s: self._chain_voronoi(('shoulder_' + s, 'elbow_' + s,
                                             'wrist_' + s, 'hand_' + s))
                      for s in ('l', 'r')}
        w_all = K.skin_weights(self.skel, self.w, self.h)
        self.w_base = _restrict(self.skel, w_all, [
            'pelvis', 'spine', 'chest', 'neck', 'head', 'head_top',
            'hip_l', 'knee_l', 'ankle_l', 'toe_l',
            'hip_r', 'knee_r', 'ankle_r', 'toe_r'])
        self.w_arm = {s: _restrict(self.skel, w_all, [
            'chest', 'shoulder_' + s, 'elbow_' + s, 'wrist_' + s, 'hand_' + s])
            for s in ('l', 'r')}

    # ------------------------------------------------------------------
    def _chain_voronoi(self, names):
        """Nearest bone *within one chain*, so a limb can never grab a far bone."""
        sk = self.skel
        idx = [sk.index[n] for n in names]
        h, w = self.h, self.w
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        pts = np.stack([xx, yy], -1)
        d = np.full((len(idx), h, w), 1e9, np.float32)
        for k, i in enumerate(idx):
            p = int(sk.parents[i])
            a = sk.rest[i]
            b = sk.rest[p] if p >= 0 else a
            d[k] = K._seg_dist(pts, b, a)
        return np.array(idx, np.int32)[np.argmin(d, 0)]

    def _torso_weights_only(self):
        """A soft body mask that excludes anything outside the jacket box."""
        j = self.skel.index; r = self.skel.rest
        x0 = float(r[j['shoulder_l']][0]) - 6
        x1 = float(r[j['shoulder_r']][0]) + 6
        y0 = float(r[j['neck']][1]) - 10
        y1 = float(r[j['pelvis']][1]) + 34
        px = _grid(self.w, self.h)
        inside = ((px[..., 0] >= x0) & (px[..., 0] <= x1) &
                  (px[..., 1] >= y0) & (px[..., 1] <= y1)).astype(np.float32)
        return _box_blur(inside, 2)

    def posed(self, angles, root=(0.0, 0.0)):
        from pose import apply_pose
        return apply_pose(self.skel, self.rest, angles, root)

    def render(self, joints):
        def warp(rgb, alpha, weights):
            return K.deform(rgb, alpha, self.skel, weights, self.rest, joints,
                            self.w, self.h)

        brgb, balpha = warp(self.base_rgb, self.base_alpha, self.voronoi)
        brgb = np.clip(brgb, 0, 1)
        balpha = np.clip(balpha, 0, 1)

        for s in ('r', 'l'):     # far arm, then near arm
            argb, aalpha = warp(self.rgb, self.arm_alpha[s], self.v_arm[s])
            argb = np.clip(argb, 0, 1)
            a = np.clip(aalpha, 0, 1)[..., None]
            brgb = argb * a + brgb * (1 - a)
            balpha = np.maximum(balpha, a[..., 0])
        return brgb, np.clip(balpha, 0, 1)


def _restrict(skel, weights, names):
    keep = [skel.index[n] for n in names if n in skel.index]
    w = np.zeros_like(weights)
    w[keep] = weights[keep]
    tot = w.sum(0)
    dead = tot < 1e-4
    if dead.any():
        w[keep[0]][dead] = 1.0
        tot = w.sum(0)
    return (w / np.maximum(tot, 1e-6)[None]).astype(np.float32)


def _scale_skel(skel, s):
    if abs(s - 1.0) < 1e-6:
        return skel
    names = skel.names
    joints = {n: tuple(np.asarray(p, np.float32) * s) for n, p in zip(names, skel.rest)}
    par = {n: names[int(skel.parents[i])] for i, n in enumerate(names)
           if int(skel.parents[i]) >= 0}
    return K.Skeleton(joints, par)
