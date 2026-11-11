"""A parametric 2D character: joint angles in, painted figure out.

Built from tapered limb capsules grouped by material, then each material group is
shaded as one form with a single light direction and a global rim. Two views are
supported: 'front' and 'side' (profile, used for walking and silhouette shots).

Angles are measured from "straight down": 0 = hanging, +90 = out to the
character's right, -90 = out to their left.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import core2d as C

H = 1000.0
ANKLE_Y = -40.0
KNEE_Y = -286.0
HIP_Y = -518.0
WAIST_Y = -612.0
SHOULDER_Y = -812.0
NECK_Y = -852.0
HEAD_C_Y = -930.0
HEAD_RY = 72.0
HEAD_RX = 54.0
SHOULDER_X = 92.0
HIP_X = 40.0
UPPER_ARM = 172.0
FOREARM = 156.0
THIGH = 240.0
SHIN = 240.0


def d(angle):
    a = math.radians(angle)
    return (math.sin(a), math.cos(a))


def step(p, angle, length):
    dx, dy = d(angle)
    return (p[0] + dx * length, p[1] + dy * length)


def rot_about(p, origin, deg):
    a = math.radians(deg)
    x, y = p[0] - origin[0], p[1] - origin[1]
    return (origin[0] + x * math.cos(a) - y * math.sin(a),
            origin[1] + x * math.sin(a) + y * math.cos(a))


# ------------------------------------------------------------------- poses
def base_pose():
    return dict(
        pelvis=(0.0, 0.0), lean=0.0, head_turn=0.0, head_tilt=0.0, head_nod=0.0,
        arm_l=(5.0, 7.0), arm_r=(-5.0, -7.0),
        leg_l=(2.5, -3.0), leg_r=(-2.5, 3.0),
        foot_l=0.0, foot_r=0.0, breathe=0.0, hop=0.0,
    )


def blend(a, b, k):
    out = {}
    for key in a:
        va, vb = a[key], b[key]
        if isinstance(va, tuple):
            out[key] = tuple(x + (y - x) * k for x, y in zip(va, vb))
        else:
            out[key] = va + (vb - va) * k
    return out


def pose_idle(t, seed=0.0, mood=0.0):
    p = base_pose()
    p['breathe'] = math.sin((t + seed) * 1.35) * 0.5 + 0.5
    p['arm_l'] = (5.0 + math.sin(t * .8 + seed) * 1.4, 8.0)
    p['arm_r'] = (-5.0 - math.sin(t * 1.02 + seed) * 1.4, -8.0)
    p['head_turn'] = math.sin(t * .33 + seed) * .40
    p['head_tilt'] = math.sin(t * .27 + seed * 2) * 1.1
    p['lean'] = 1.2 + p['breathe'] * 0.6
    return p


def pose_walk(phase, stride=26.0, view='side'):
    p = base_pose()
    s, c = math.sin(phase), math.cos(phase)
    lift = max(0.0, 40 * math.sin(phase - 0.7))
    lift_r = max(0.0, 40 * math.sin(phase + math.pi - 0.7))
    if view == 'side':
        p['leg_l'] = (stride * s, -max(0.0, lift * .9))
        p['leg_r'] = (-stride * s, -max(0.0, lift_r * .9))
        p['arm_l'] = (-stride * 0.85 * s, 14 + 8 * max(0, s))
        p['arm_r'] = (stride * 0.85 * s, -(14 + 8 * max(0, -s)))
        p['foot_l'] = 12 * max(0, math.sin(phase + .4))
        p['foot_r'] = 12 * max(0, math.sin(phase + math.pi + .4))
    else:
        p['leg_l'] = (10 * s, -lift * .5)
        p['leg_r'] = (-10 * s, -lift_r * .5)
        p['arm_l'] = (-12 * s, 10)
        p['arm_r'] = (12 * s, -10)
    p['pelvis'] = (0.0, -abs(math.sin(phase)) * 6.0)
    p['hop'] = -abs(math.sin(phase)) * 7.0
    p['lean'] = 3.0
    p['breathe'] = 0.5
    return p


def pose_arm_to(p, side, target_local, elbow_bend=26.0):
    key = f'arm_{side}'
    sx = SHOULDER_X if side == 'r' else -SHOULDER_X
    shoulder = (sx, SHOULDER_Y)
    vx, vy = target_local[0] - shoulder[0], target_local[1] - shoulder[1]
    ang = math.degrees(math.atan2(vx, vy))
    p[key] = (ang, -elbow_bend if side == 'r' else elbow_bend)
    return p


# --------------------------------------------------------------- geometry
def figure_points(pose):
    pel = (pose['pelvis'][0], HIP_Y + pose['pelvis'][1] + pose['hop'])
    lean = pose['lean']
    neck = (pel[0] + math.sin(math.radians(lean)) * -294.0,
            pel[1] - 294.0 * math.cos(math.radians(lean)))
    shoulder_c = (neck[0], neck[1] + 40.0)
    head_ang = math.radians(lean + pose['head_nod'])
    head_c = (neck[0] + math.sin(head_ang) * 78.0, neck[1] - 78.0 * math.cos(head_ang))

    pts = dict(pelvis=pel, neck=neck, shoulder_c=shoulder_c, head=head_c,
               shoulder_l=(shoulder_c[0] - SHOULDER_X, shoulder_c[1]),
               shoulder_r=(shoulder_c[0] + SHOULDER_X, shoulder_c[1]),
               hip_l=(pel[0] - HIP_X, pel[1]), hip_r=(pel[0] + HIP_X, pel[1]),
               waist=(pel[0], WAIST_Y + pose['pelvis'][1] + pose['hop']))

    for side, sx in (('l', -1), ('r', 1)):
        au, af = pose[f'arm_{side}']
        sh = (shoulder_c[0] + sx * SHOULDER_X, shoulder_c[1] + 4)
        el = step(sh, au, UPPER_ARM)
        wr = step(el, au + af, FOREARM)
        pts[f'sh_{side}'] = sh
        pts[f'el_{side}'] = el
        pts[f'wr_{side}'] = wr
        pts[f'hand_{side}'] = step(wr, au + af, 14.0)

        th, sh_rel = pose[f'leg_{side}']
        hip = pts[f'hip_{side}']
        kn = step(hip, th, THIGH)
        an = step(kn, th + sh_rel, SHIN)
        pts[f'kn_{side}'] = kn
        pts[f'an_{side}'] = an
        pts[f'toe_{side}'] = step(an, 88 + pose[f'foot_{side}'], 50.0)
    return pts


# ---------------------------------------------------------------- drawing
class Style:
    def __init__(self, skin=(0.855, 0.700, 0.590), hair=(0.115, 0.092, 0.085),
                 shirt=(0.905, 0.905, 0.915), trousers=(0.225, 0.245, 0.305),
                 shoes=(0.085, 0.085, 0.105), jacket=None, accent=(0.545, 0.160, 0.195),
                 shirt_style='tee', hair_style='short'):
        self.skin, self.hair = skin, hair
        self.shirt, self.trousers = shirt, trousers
        self.shoes, self.jacket, self.accent = shoes, jacket, accent
        self.shirt_style, self.hair_style = shirt_style, hair_style


def _capsule(draw, p0, p1, r0, r1, flat=1.0):
    x0, y0 = p0
    x1, y1 = p1
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    draw.ellipse([x0 - r0, y0 - r0 * flat, x0 + r0, y0 + r0 * flat], fill=255)
    draw.ellipse([x1 - r1, y1 - r1 * flat, x1 + r1, y1 + r1 * flat], fill=255)
    n = 10
    left, right = [], []
    for i in range(n + 1):
        k = i / n
        px, py = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
        r = r0 + (r1 - r0) * k
        nx, ny = math.cos(math.radians(ang + 90)), math.sin(math.radians(ang + 90))
        left.append((px + nx * r, py + ny * r * flat))
        right.append((px - nx * r, py - ny * r * flat))
    draw.polygon(left + right[::-1], fill=255)


def draw_figure(size, pose, style: Style, scale=1.0, origin=(0.5, 0.97),
                light=(-0.55, -0.84), key=1.0, rim=(0.85, 0.92, 1.0),
                rim_strength=0.42, detail=True, view='front', extra=None,
                contact=(0.0, 0.0, 0.0)):
    """Render one figure. Returns (rgb, mask) float arrays at `size`."""
    w, h = size
    pts = figure_points(pose)
    ox, oy = origin[0] * w, origin[1] * h

    def T(p):
        return (ox + p[0] * scale, oy + p[1] * scale)

    def S(v):
        return v * scale

    side = (view == 'side')
    masks = {}

    def mask(name):
        if name not in masks:
            masks[name] = Image.new('L', size, 0)
        return masks[name]

    def d_of(name):
        return ImageDraw.Draw(mask(name))

    # ---------------------------------------------------------- limbs
    for name, sgn in (('far', -1), ('near', 1)):
        a_side = 'l' if name == 'far' else 'r'
        m_arm, m_leg = mask(f'arm_{name}'), mask(f'leg_{name}')
        da, dl = d_of(f'arm_{name}'), d_of(f'leg_{name}')
        sh, el, wr = T(pts[f'sh_{a_side}']), T(pts[f'el_{a_side}']), T(pts[f'wr_{a_side}'])
        off = S(-11) if side else 0.0
        if side:
            sh = (sh[0] + S(6), sh[1]); el = (el[0], el[1]); wr = (wr[0], wr[1])
        _capsule(da, sh, el, S(27), S(22))
        _capsule(da, el, wr, S(22), S(17))
        # shoulder cap blends the sleeve into the torso
        da.ellipse([sh[0] - S(30), sh[1] - S(30), sh[0] + S(30), sh[1] + S(30)], fill=255)

        hip, kn, an = T(pts[f'hip_{a_side}']), T(pts[f'kn_{a_side}']), T(pts[f'an_{a_side}'])
        if side:
            hip = (hip[0] + S(-6 if name == 'far' else 4), hip[1])
            kn = (kn[0], kn[1])
            an = (an[0], an[1])
        _capsule(dl, hip, kn, S(37), S(27))
        _capsule(dl, kn, an, S(27), S(19))

        ds = d_of(f'shoe_{name}')
        toe = T(pts[f'toe_{a_side}'])
        if side:
            ds.ellipse([an[0] - S(30), an[1] - S(20), an[0] + S(52), an[1] + S(26)], fill=255)
            ds.polygon([(an[0] - S(26), an[1] + S(4)), (an[0] + S(46), an[1] - S(6)),
                        (an[0] + S(52), an[1] + S(24)), (an[0] - S(24), an[1] + S(26))], fill=255)
        else:
            _capsule(ds, an, toe, S(23), S(17))
            ds.ellipse([an[0] - S(25), an[1] - S(18), an[0] + S(25), an[1] + S(24)], fill=255)

        dh = d_of(f'hand_{name}')
        hx, hy = T(pts[f'hand_{a_side}'])
        ang = pose[f'arm_{"l" if name == "far" else "r"}'][0] + pose[f'arm_{"l" if name == "far" else "r"}'][1]
        dh.ellipse([hx - S(20), hy - S(17), hx + S(20), hy + S(19)], fill=255)
        if detail:
            # thumb
            tx, ty = step((hx, hy), ang - 55, S(19))
            dh.ellipse([tx - S(9), ty - S(9), tx + S(9), ty + S(9)], fill=255)

    # ---------------------------------------------------------- torso
    dt = d_of('torso')
    sc, pelvis, waist = pts['shoulder_c'], pts['pelvis'], pts['waist']
    top, mid, bot = T((sc[0], sc[1] + 8)), T(waist), T((pelvis[0], pelvis[1] + 34))
    half_top = S(58 if side else 96)
    half_mid = S(52 if side else 74)
    half_bot = S(50 if side else 60)
    dt.polygon([
        (top[0] - half_top, top[1] - S(14)), (top[0] + half_top, top[1] - S(14)),
        (mid[0] + half_mid, mid[1]), (bot[0] + half_bot, bot[1]),
        (bot[0] - half_bot, bot[1]), (mid[0] - half_mid, mid[1]),
    ], fill=255)
    dt.ellipse([top[0] - half_top, top[1] - half_top * .62, top[0] + half_top, top[1] + half_top * .40], fill=255)
    dt.ellipse([bot[0] - half_bot, bot[1] - half_bot * .8, bot[0] + half_bot, bot[1] + half_bot * .55], fill=255)

    # ---------------------------------------------------------- neck+head
    nx, ny = pts['neck']
    dn = d_of('skin')
    _capsule(dn, T((nx, ny + 46)), T((nx + (S(6) if side else 0), ny - 18)), S(21), S(24))

    hc = T(pts['head'])
    hx0 = hc[0] + (pose['head_turn'] * S(7) if not side else 0)
    rx, ry = S(HEAD_RX), S(HEAD_RY)
    dh = d_of('head')
    if side:
        # profile: cranium, brow, nose, lips, chin
        dh.ellipse([hx0 - rx * .96, hc[1] - ry, hx0 + rx * .92, hc[1] + ry * .52], fill=255)
        dh.polygon([(hx0 - rx * .86, hc[1] + ry * .12), (hx0 + rx * .96, hc[1] + ry * .10),
                    (hx0 + rx * .80, hc[1] + ry * .62), (hx0 + rx * .30, hc[1] + ry * .88),
                    (hx0 - rx * .34, hc[1] + ry * .90), (hx0 - rx * .90, hc[1] + ry * .48)], fill=255)
        # nose
        dh.polygon([(hx0 + rx * .52, hc[1] - ry * .10), (hx0 + rx * 1.02, hc[1] + ry * .26),
                    (hx0 + rx * .94, hc[1] + ry * .40), (hx0 + rx * .50, hc[1] + ry * .38)], fill=255)
        # chin
        dh.ellipse([hx0 + rx * .18, hc[1] + ry * .60, hx0 + rx * .86, hc[1] + ry * .96], fill=255)
    else:
        dh.ellipse([hx0 - rx, hc[1] - ry, hx0 + rx, hc[1] + ry * .26], fill=255)
        dh.polygon([(hx0 - rx * .93, hc[1] + ry * .02), (hx0 + rx * .93, hc[1] + ry * .02),
                    (hx0 + rx * .62, hc[1] + ry * .74), (hx0 + rx * .38, hc[1] + ry * .95),
                    (hx0 - rx * .38, hc[1] + ry * .95), (hx0 - rx * .62, hc[1] + ry * .74)], fill=255)
        dh.ellipse([hx0 - rx * 1.02, hc[1] - ry * .10, hx0 - rx * .74, hc[1] + ry * .34], fill=255)
        dh.ellipse([hx0 + rx * .74, hc[1] - ry * .10, hx0 + rx * 1.02, hc[1] + ry * .34], fill=255)

    # ---------------------------------------------------------- hair
    dhb = d_of('hair_back')
    dhh = d_of('hair')
    if side:
        dhb.ellipse([hx0 - rx * 1.16, hc[1] - ry * 1.10, hx0 + rx * .80, hc[1] + ry * .44], fill=255)
        dhh.ellipse([hx0 - rx * 1.10, hc[1] - ry * 1.08, hx0 + rx * .46, hc[1] + ry * .06], fill=255)
        dhh.ellipse([hx0 - rx * 1.14, hc[1] - ry * .10, hx0 - rx * .30, hc[1] + ry * .52], fill=255)
    else:
        dhb.ellipse([hx0 - rx * 1.12, hc[1] - ry * 1.12, hx0 + rx * 1.12, hc[1] + ry * .10], fill=255)
        dhh.ellipse([hx0 - rx * 1.06, hc[1] - ry * 1.06, hx0 + rx * 1.06, hc[1] - ry * .18], fill=255)
        dhh.polygon([(hx0 - rx * 1.04, hc[1] - ry * .22), (hx0 + rx * .28, hc[1] - ry * .40),
                     (hx0 + rx * 1.02, hc[1] - ry * .05), (hx0 + rx * .96, hc[1] - ry * .34),
                     (hx0 - rx * .60, hc[1] - ry * .62)], fill=255)
        dhh.ellipse([hx0 - rx * 1.10, hc[1] - ry * .30, hx0 - rx * .78, hc[1] + ry * .30], fill=255)
        dhh.ellipse([hx0 + rx * .78, hc[1] - ry * .30, hx0 + rx * 1.10, hc[1] + ry * .30], fill=255)

    # ---------------------------------------------------------- shading
    out = np.zeros((h, w, 3), np.float32)
    alpha = np.zeros((h, w), np.float32)

    def put(name, colour, **kw):
        nonlocal out, alpha
        rgb, m = C.paint_mask(mask(name), colour, light=light, key=key,
                              rim=rim, rim_strength=rim_strength, **kw)
        out = out * (1 - m[..., None]) + rgb
        alpha = np.clip(alpha + m, 0, 1)

    trouser = style.trousers
    shirt = style.jacket if style.jacket else style.shirt
    far_shade = 0.60

    put('leg_far', (trouser[0] * far_shade, trouser[1] * far_shade, trouser[2] * far_shade * 1.06))
    put('arm_far', (shirt[0] * far_shade, shirt[1] * far_shade, shirt[2] * far_shade * 1.06))
    put('shoe_far', (style.shoes[0] * .7, style.shoes[1] * .7, style.shoes[2] * .8), shade=.5)
    put('leg_near', trouser)
    put('torso', shirt, texture=_cloth_texture(size, max(3.0, S(13))))
    put('hair_back', (style.hair[0] * .74, style.hair[1] * .74, style.hair[2] * .84), shade=.5)
    put('arm_near', shirt)
    put('shoe_near', style.shoes, shade=.5)
    put('skin', style.skin, shade=.36)

    m_head = np.asarray(mask('head')).astype(np.float32) / 255.0
    head_rgb, _ = C.paint_mask(mask('head'), style.skin, light=light, key=key,
                               rim=rim, rim_strength=rim_strength * .85, shade=.32)
    out = out * (1 - m_head[..., None]) + head_rgb
    alpha = np.clip(alpha + m_head, 0, 1)

    m_hair = np.asarray(mask('hair')).astype(np.float32) / 255.0
    hair_rgb, _ = C.paint_mask(mask('hair'), style.hair, light=light,
                               key=key * .95, rim=rim, rim_strength=rim_strength * .75, shade=.5)
    out = out * (1 - m_hair[..., None]) + hair_rgb
    alpha = np.clip(alpha + m_hair, 0, 1)

    if detail and S(HEAD_RY) > 13:
        out = _face(out, alpha, size, pose, style, T, S, side, hx0, hc)
        out = _garment_details(out, alpha, size, pose, style, T, S, side, shirt)
    if extra:
        out, alpha = extra(out, alpha, T, S)
    if contact[2] > 0:
        out = contact_shadow_at(out, T(pts['pelvis'])[0], origin[1] * h, alpha, contact)
    return out, alpha


def _cloth_texture(size, period):
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    weave = (np.sin(xx / max(period, 1e-3) * 2.1) * np.sin(yy / max(period, 1e-3) * 2.4)) * 0.016
    return weave[..., None]


def _px(fill):
    """Colour tuple with 0..1 floats -> 0..255 ints."""
    if len(fill) == 4:
        return tuple(int(round(max(0.0, min(1.0, c)) * 255)) for c in fill)
    return fill


def _draw_soft(size, layers, blur=1.2):
    """layers: list of (kind, coords, fill, width)."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for kind, coords, fill, width in layers:
        fill = _px(fill)
        if kind == 'line':
            d.line(coords, fill=fill, width=max(1, int(width)), joint='curve')
        elif kind == 'ellipse':
            d.ellipse(coords, fill=fill)
        elif kind == 'poly':
            d.polygon(coords, fill=fill)
        elif kind == 'arc':
            d.arc(coords, fill=fill, width=max(1, int(width)), start=180, end=360)
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    return img


def _blend_layer(out, alpha, layer):
    arr = np.asarray(layer).astype(np.float32) / 255.0
    a = arr[..., 3:4] * alpha[..., None]
    return out * (1 - a) + arr[..., :3] * a


def _face(out, alpha, size, pose, style, T, S, side, hx0, hc):
    ry, rx = S(HEAD_RY), S(HEAD_RX)
    turn = pose['head_turn']
    layers = []
    if side:
        eye_x = hx0 + rx * .52
        eye_y = hc[1] - ry * .02
        layers.append(('ellipse', [eye_x - rx * .15, eye_y - ry * .055,
                                   eye_x + rx * .19, eye_y + ry * .045], (248, 245, 242, 235), 0))
        layers.append(('ellipse', [eye_x + rx * .02, eye_y - ry * .045,
                                   eye_x + rx * .135, eye_y + ry * .035], (74, 62, 50, 255), 0))
        layers.append(('line', [(eye_x - rx * .16, eye_y - ry * .035),
                                (eye_x + rx * .10, eye_y - ry * .065),
                                (eye_x + rx * .19, eye_y - ry * .02)],
                       (34, 24, 20, 240), max(2, int(S(4.5)))))
        # brow
        layers.append(('line', [(hx0 + rx * .28, hc[1] - ry * .30),
                                (hx0 + rx * .66, hc[1] - ry * .34),
                                (hx0 + rx * .86, hc[1] - ry * .26)],
                       (32, 22, 18, 235), max(3, int(S(6)))))
        # lips
        layers.append(('line', [(hx0 + rx * .66, hc[1] + ry * .44), (hx0 + rx * .88, hc[1] + ry * .42)],
                       (140, 82, 72, 205), max(2, int(S(4)))))
        # ear + jaw shadow
        layers.append(('ellipse', [hx0 - rx * .92, hc[1] - ry * .04, hx0 - rx * .58, hc[1] + ry * .26],
                       (150, 108, 86, 45), 0))
    else:
        eye_y = hc[1] + ry * .02
        eye_dx = rx * .40
        squash = 1.0 - 0.26 * abs(turn)
        for sx in (-1, 1):
            ex = hx0 + sx * eye_dx * squash + turn * rx * .18
            ew, eh = rx * .27 * squash, ry * .085
            layers.append(('ellipse', [ex - ew, eye_y - eh, ex + ew, eye_y + eh], (250, 248, 245, 240), 0))
            ir = eh * 1.15
            layers.append(('ellipse', [ex - ir * .82, eye_y - ir, ex + ir * .82, eye_y + ir], (92, 76, 60, 255), 0))
            layers.append(('ellipse', [ex - ir * .34, eye_y - ir * .40, ex + ir * .34, eye_y + ir * .48], (28, 24, 22, 255), 0))
            layers.append(('ellipse', [ex - ir * .30, eye_y - ir * .52, ex + ir * .02, eye_y - ir * .12], (255, 255, 255, 190), 0))
            layers.append(('arc', [ex - ew * 1.06, eye_y - eh * 2.0, ex + ew * 1.06, eye_y + eh * 1.0],
                           (44, 32, 27, 225), max(2, int(S(3.2)))))
            by = eye_y - eh * 4.0
            layers.append(('line', [(ex - ew * 1.2, by + eh * .7), (ex + ew * .1, by - eh * .5),
                                    (ex + ew * 1.12, by + eh * .35)],
                           (36, 26, 21, 235), max(3, int(S(5.4)))))
        nose_x = hx0 + turn * rx * .46
        layers.append(('poly', [(nose_x - rx * .12, eye_y + ry * .10),
                                (nose_x + rx * .13, eye_y + ry * .34),
                                (nose_x - rx * .10, eye_y + ry * .36)], (128, 92, 74, 95), 0))
        layers.append(('line', [(nose_x - rx * .20, eye_y + ry * .42), (nose_x + rx * .20, eye_y + ry * .42)],
                       (104, 70, 56, 130), max(1, int(S(2.6)))))
        my = hc[1] + ry * .52
        mw = rx * .38 * squash
        layers.append(('line', [(hx0 - mw, my), (hx0, my + ry * .05), (hx0 + mw, my - ry * .01)],
                       (128, 74, 64, 220), max(2, int(S(4.6)))))
        layers.append(('line', [(hx0 - mw * .8, my + ry * .085), (hx0 + mw * .72, my + ry * .075)],
                       (198, 152, 142, 85), max(1, int(S(2.2)))))
    layer = _draw_soft(size, layers, blur=S(0.8))
    return _blend_layer(out, alpha, layer)


def _garment_details(out, alpha, size, pose, style, T, S, side, shirt):
    """Collar, placket, cuffs and belt: the details that stop it reading as a blob."""
    pts = figure_points(pose)
    sc, pelvis = pts['shoulder_c'], pts['pelvis']
    layers = []
    top = T((sc[0], sc[1] + 10))
    dx = S(52 if side else 84)
    # collar
    collar = (max(0.0, shirt[0] - .16), max(0.0, shirt[1] - .16), max(0.0, shirt[2] - .15), 210)
    if side:
        layers.append(('line', [(top[0] - S(20), top[1] - S(2)), (top[0] + S(6), top[1] + S(10)),
                                (top[0] - S(16), top[1] + S(22))], collar, max(2, int(S(5)))))
    else:
        layers.append(('poly', [(top[0] - S(26), top[1] - S(12)), (top[0], top[1] + S(26)),
                                (top[0] + S(26), top[1] - S(12)), (top[0] + S(18), top[1] - S(18)),
                                (top[0], top[1] + S(6)), (top[0] - S(18), top[1] - S(18))],
                       (max(0, shirt[0] - .10), max(0, shirt[1] - .10), max(0, shirt[2] - .09), 190), 0))
        layers.append(('line', [(top[0], top[1] + S(18)), (top[0], top[1] + S(150))],
                       (max(0, shirt[0] - .12), max(0, shirt[1] - .12), max(0, shirt[2] - .11), 150),
                       max(1, int(S(3)))))
    # belt
    belt_y = T((pelvis[0], pelvis[1] - S(6) / max(S(1), 1e-3)))[1]
    bl = (max(0, style.trousers[0] * .55), max(0, style.trousers[1] * .55), max(0, style.trousers[2] * .58), 235)
    layers.append(('line', [(top[0] - dx, belt_y + S(2)), (top[0] + dx, belt_y + S(2))], bl,
                   max(2, int(S(7)))))
    if not side:
        layers.append(('ellipse', [top[0] - S(7), belt_y - S(6), top[0] + S(7), belt_y + S(8)],
                       (0.62, 0.55, 0.30, 235), 0))
    # cuffs on the near arm
    wr = T(pts['wr_r'])
    layers.append(('line', [(wr[0] - S(20), wr[1] - S(16)), (wr[0] + S(20), wr[1] + S(14))],
                   (max(0, shirt[0] - .10), max(0, shirt[1] - .10), max(0, shirt[2] - .10), 170),
                   max(2, int(S(5)))))
    layer = _draw_soft(size, layers, blur=S(0.9))
    return _blend_layer(out, alpha, layer)


def contact_shadow_at(canvas, x, ground_y, alpha, contact):
    strength, rx, ry = contact[0], contact[1], contact[2]
    h, w = canvas.shape[:2]
    m = C.soft_ellipse((w, h), (x, ground_y), rx, ry, softness=1.0)
    return canvas * (1 - (m * strength)[..., None])


def contact_shadow(canvas, x, y, rx, ry, strength=0.5):
    h, w = canvas.shape[:2]
    m = C.soft_ellipse((w, h), (x, y), rx, ry, softness=1.1)
    return canvas * (1 - (m * strength)[..., None])
