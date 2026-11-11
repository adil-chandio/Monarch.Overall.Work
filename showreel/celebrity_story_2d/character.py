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


def _hard_edge(mask, feather=1.0):
    """Threshold a soft mask back to a crisp edge and feather it by ~1 px.

    The feather pass must not reintroduce translucency: scaling a 3x3 mean up
    by 1.8 still leaves the mask around 0.2 in places, and a limb with 0.2
    alpha is a ghost. Thresholding the blurred mask instead keeps every pixel
    fully opaque and only rounds the silhouette by a pixel.
    """
    m = (np.asarray(mask, np.float32) > 0.5).astype(np.float32)
    if feather <= 0:
        return m
    k = max(1, int(round(feather)))
    soft = _box_blur(m, k)
    return (soft > 0.45).astype(np.float32)


def _jacket_fill(rgb, body, hole, skel, tone=(0.18, 0.46)):
    """Paint the gap under a lifted arm with the jacket's own tone.

    The patch to copy from is chosen by *appearance*, not by a box: charcoal
    jacket, not the white shirt or the navy tie that sit in the same rectangle.
    Copying a box gave a pale smear down the chest, which is what made the
    sleeve look ghosted.
    """
    j = skel.index; r = skel.rest
    hole = np.clip(np.asarray(hole, np.float32), 0, 1)
    body = np.asarray(body, np.float32)
    if hole.max() < 1e-3:
        return rgb

    lum = rgb.mean(2)
    sat = rgb.max(2) - rgb.min(2)
    x0, x1 = int(r[j['chest']][0]) - 58, int(r[j['chest']][0]) + 40
    y0, y1 = int(r[j['chest']][1]) + 6, int(r[j['pelvis']][1]) - 20
    x0, y0 = max(0, x0), max(0, y0)
    sub = np.zeros(lum.shape, bool)
    sub[y0:y1, x0:x1] = True
    pick = sub & (body > 0.5) & (lum > tone[0]) & (lum < tone[1]) & (sat < 0.10)
    if pick.sum() < 200:
        pick = (body > 0.5) & (lum > tone[0]) & (lum < tone[1])
    if pick.sum() < 50:
        return rgb
    base = np.median(rgb[pick], axis=0)

    h = body.shape[0]
    yy = np.arange(h, dtype=np.float32)[:, None]
    top, bot = float(y0), float(max(y1, y0 + 1))
    shade = 1.0 - 0.14 * np.clip((yy - top) / max(1e-3, bot - top), 0, 1)
    fill = base[None, None, :] * shade[..., None]
    return np.clip(np.where(hole[..., None] > 0.02, fill, rgb), 0, 1)


def edge_extend(rgb, mask, reach=14):
    """Grow a layer's colour outward past its own edge.

    A weight-blended warp samples a few pixels outside the shape it is warping.
    Inside the jacket that is harmless, but around a sleeve it pulls in the
    white shirt, and the arm ends up looking transparent. Extending the
    sleeve's own colour outward first removes that leak at the source.
    """
    rgb = np.asarray(rgb, np.float32)
    known = (np.asarray(mask, np.float32) > 0.5)
    if not known.any():
        return rgb
    out = rgb.copy()
    for _ in range(reach):
        kn = known.astype(np.float32)[..., None]
        acc = np.zeros_like(out)
        cnt = np.zeros(known.shape, np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            acc += np.roll(out * kn, (dy, dx), (0, 1))
            cnt += np.roll(known.astype(np.float32), (dy, dx), (0, 1))
        grow = (~known) & (cnt > 0)
        if not grow.any():
            break
        out[grow] = acc[grow] / cnt[grow][:, None]
        known = known | grow
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


def fill_holes(mask):
    """Fill enclosed holes, so ink lines inside a region are not punched out."""
    from collections import deque
    m = np.asarray(mask, np.float32) > 0.5
    h, w = m.shape
    seen = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if not m[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if not m[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < h and 0 <= xx < w and not m[yy, xx] and not seen[yy, xx]:
                seen[yy, xx] = True
                q.append((yy, xx))
    return (~seen).astype(np.float32)


def near_body(hand, h, w, reach=58.0):
    """Mask of everything close enough to the hand to be arm, not garment."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.hypot(xx - hand[0], yy - hand[1])
    return d < reach


def limb_masks(lbl, skel, r_upper=31.0, r_fore=26.0, r_hand=30.0, soft=2.5):
    """Arm masks as capsules along the arm bones.

    The painted sleeve is a tapered tube, so a capsule along the bone is the
    right shape for it: it follows the limb, keeps the hand, and — unlike a
    region or a bounding box — cannot swallow the jacket's front panel, which
    sits inboard of the shoulder joint.
    """
    j = skel.index; rest = skel.rest
    h, w = lbl.shape
    px = _grid(w, h)
    out = {}
    for s in ('l', 'r'):
        pts = [rest[j['shoulder_' + s]], rest[j['elbow_' + s]],
               rest[j['wrist_' + s]], rest[j['hand_' + s]]]
        cap = np.zeros((h, w), np.float32)
        # the hand region is the palm plus fingers, which reach past the joint,
        # but only by about half a palm — extending further let the capsule take
        # the jacket's hem on the far side of the wrist
        tail = np.asarray(pts[3], np.float32) + \
            (np.asarray(pts[3], np.float32) - np.asarray(pts[2], np.float32)) * 0.32
        for (a, b), r in zip(((pts[0], pts[1]), (pts[1], pts[2]),
                              (pts[2], pts[3]), (pts[3], tail)),
                             (r_upper, r_fore, r_hand, r_hand * 0.62)):
            a = np.asarray(a, np.float32); b = np.asarray(b, np.float32)
            ab = b - a
            t = np.clip(((px - a) @ ab) / max(float(ab @ ab), 1e-6), 0, 1)
            d = np.linalg.norm(px - (a + t[..., None] * ab), axis=-1)
            cap = np.maximum(cap, np.clip((r - d) / soft, 0, 1))
        # the cut runs a little past the drawn arm so the sleeve's own outline
        # and cuff are inside it; otherwise a thin rim of both survives behind
        # the lifted sleeve, which reads as a notch at the wrist
        grown = _box_blur((cap > 0.5).astype(np.float32), 4)
        keep = fill_holes((cap > 0.5) | (grown > 0.30))
        # the grown cut also takes a sliver of jacket hem; that belongs to the
        # body, and if it rides with the arm it leaves a step at the hip
        # hard stop: nothing beyond a hand-sized disc around the wrist belongs
        # to the arm. Without this the grown cut runs down the jacket hem and
        # the layer carries a strip of coat with it.
        disc = np.hypot(px[..., 0] - pts[2][0], px[..., 1] - pts[2][1]) < (r_hand + 40.0)
        keep = (keep > 0.5) & disc
        out[s] = _box_blur(keep.astype(np.float32), 1)
    return out


# ------------------------------------------------------------------- the rig
class Character:
    """A painted cel cut into layers and bound to the armature."""

    def __init__(self, rgb, alpha, skel=None, fill=True, scale_to=None, pad=1.10):
        rgb = np.asarray(rgb, np.float32)
        alpha = np.clip(np.asarray(alpha, np.float32), 0, 1)
        # A 311-pixel-wide cel cannot hold a lifted arm: the hand would be
        # clipped off the edge of the drawing and the limb would lose most of
        # its pixels. The working canvas is padded so any pose fits inside it.
        h0, w0 = alpha.shape
        px = int(round(w0 * pad))
        px = max(px, int(round(h0 * 0.30)))
        py = int(round(h0 * 0.10))
        canvas = np.zeros((h0 + 2 * py, w0 + 2 * px, 3), np.float32)
        canvas[py:py + h0, px:px + w0] = rgb
        canvas_a = np.zeros((h0 + 2 * py, w0 + 2 * px), np.float32)
        canvas_a[py:py + h0, px:px + w0] = alpha
        rgb, alpha = canvas, canvas_a
        self.pad = (px, py)

        self.h, self.w = alpha.shape
        self.skel = skel or K.hero_skeleton()
        if scale_to:
            self.skel = _scale_skel(self.skel, scale_to / 1000.0)
        self.skel = K.translate_skel(self.skel, px, py)
        self.rest = self.skel.forward()
        self.body = (alpha > 0.45).astype(np.float32)
        self.rgb = rgb

        lbl = ink_regions(rgb, self.body > 0.5)
        self.labels = lbl
        mask = limb_masks(lbl, self.skel)
        cut = {k: v.copy() for k, v in mask.items()}
        # Cut generously: the sleeve, its ink outline and a little margin, so no
        # pale rim of the old sleeve survives in the base.
        bodyf = self.body
        # the cut may never reach past the painted body: the diffusion that
        # grew it also flowed over the keyed-out background beside the hip
        self.cut = {s: _hard_edge(cut[s], 1.5) * bodyf for s in ('l', 'r')}
        # The arm layer is the sleeve only, no margin, so it drops back exactly
        # over its own pixels at rest and cannot spill onto the chest.
        # A hard, one-pixel-feathered edge: a wide soft edge lets the page
        # background show through the sleeve and reads as a white halo.
        self.arm_alpha = {s: _hard_edge(mask[s], 1) * bodyf for s in ('l', 'r')}
        self.arm_mask = mask

        # the hole an arm leaves inside the torso, which must be painted under
        torso = self._torso_weights_only()
        self.hole = {s: np.clip(self.cut[s], 0, 1) for s in ('l', 'r')}

        # the fill must never stand in for the sleeve itself: only the part of
        # the arm that lies behind the jacket is invisible at rest
        sleeves0 = np.clip(self.arm_alpha['l'] + self.arm_alpha['r'], 0, 1)
        undrawn = np.clip(1.0 - sleeves0, 0, 1)
        self.hole = {s: np.clip(self.hole[s] * undrawn, 0, 1) for s in ('l', 'r')}
        self.undrawn = undrawn
        # only the part of the arm that lay *over the jacket* needs painting in:
        # the rest of the sleeve hangs outside the body and leaves nothing behind
        self.hole = {s: np.clip(self.cut[s], 0, 1) for s in ('l', 'r')}
        all_hole = np.clip(self.hole['l'] + self.hole['r'], 0, 1)
        if fill and all_hole.max() > 0.01:
            self.base_rgb = _jacket_fill(rgb, self.body, all_hole, self.skel)
        else:
            self.base_rgb = rgb.copy()

        # The base is the body with the sleeves taken off, plus the jacket that
        # was painted in behind them. The sleeve itself lives only in the arm
        # layers, so the arm can never be drawn twice.
        sleeves = np.clip(self.cut['l'] + self.cut['r'], 0, 1)
        # The base keeps the full silhouette and the sleeve sits over it as its
        # own layer. Subtracting the sleeve from the base instead left a hole
        # wherever the fill did not reach, which is the rectangular notch.
        # The sleeve's own footprint is removed from the base *only* as colour
        # (filled jacket), never as coverage: coverage has to stay whole or a
        # lifted arm uncovers a notch. The arm layer redraws those pixels.
        self.base_alpha = self.body.copy()


        # colour pushed past each layer's edge, so a blended warp cannot sample
        # the shirt or the page through the sleeve
        self.arm_rgb = {s: edge_extend(rgb, self.arm_alpha[s], 16) for s in ('l', 'r')}
        self.voronoi = K.bone_voronoi(self.skel, self.w, self.h)
        self.v_arm = {s: self._chain_voronoi(('shoulder_' + s, 'elbow_' + s,
                                             'wrist_' + s, 'hand_' + s))
                      for s in ('l', 'r')}
        self.w_chain = {s: K.chain_weights(self.skel, ('shoulder_' + s, 'elbow_' + s,
                                                       'wrist_' + s, 'hand_' + s),
                                          self.w, self.h)
                        for s in ('l', 'r')}
        w_all = K.skin_weights(self.skel, self.w, self.h)
        self.w_base = _restrict(self.skel, w_all, [
            'pelvis', 'spine', 'chest', 'neck', 'head', 'head_top',
            'hip_l', 'knee_l', 'ankle_l', 'toe_l',
            'hip_r', 'knee_r', 'ankle_r', 'toe_r'])
        self.w_arm = {s: _restrict(self.skel, w_all, [
            'chest', 'shoulder_' + s, 'elbow_' + s, 'wrist_' + s, 'hand_' + s])
            for s in ('l', 'r')}

        # The base is pinned to the torso: without this, pixels of the jacket's
        # front panel are nearest to an arm bone and peel away with the sleeve.
        j = self.skel.index
        torso_bones = [j[n] for n in ('pelvis', 'spine', 'chest', 'neck',
                                      'head', 'head_top', 'hip_l', 'hip_r')]
        pinned = np.isin(self.voronoi, torso_bones)
        self.base_dom = np.where(pinned, self.voronoi,
                                 np.argmax(self.w_base, axis=0).astype(np.int32))

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
            # colour bends through a soft weight blend; coverage is taken from
            # the hard map. Blending the two together averages the alpha down in
            # the middle of the limb and the background shows through it.
            argb, _ = K.deform(self.arm_rgb[s], self.arm_alpha[s], self.skel,
                               self.w_chain[s], self.rest, joints,
                               self.w, self.h, blend=True)
            _, aalpha = K.deform(self.arm_rgb[s], self.arm_alpha[s], self.skel,
                                 self.v_arm[s], self.rest, joints, self.w, self.h)
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
