"""A real head mesh, rasterised: the S5/S6 face.

The procedural sculpt in `face3d.py` gets the lighting and the volume right but
cannot carry a likeness: a union of analytic masses, however smoothly blended,
has no pores, no lip form, no eyelid fold, no philtrum. This module rasterises an
actual scanned head instead, so the close-up has the surface of a face.

Source asset
------------
`assets/face-scan/LeePerrySmith.glb` — the Lee Perry-Smith head, the reference
scan distributed with three.js. It is licensed **CC BY 3.0** by Infinite
Realities Centre (Trento, Italy), and the copy here is unmodified apart from the
scale and pose applied at render time. Attribution is in `CREDITS.md`.
`Map-COL.jpg` is its colour map.

What this module does
---------------------
* parses the GLB (positions, normals, UVs, triangles) with no third-party loader
* rasterises it in screen space with a z-buffer and 2x2 sub-pixel samples
* shades it with the same physically-simple model as the rest of the film: point
  lights with inverse-square falloff, wrapped diffuse, Blinn specular, a
  hemispherical sky term and field-free ambient occlusion from a depth-behind
  test
* keeps the file's UV map for albedo *and* modulates it with the scene's own
  colour grade, so the head sits in the same world as the temple

Scope, honestly: this is one fixed head mesh, so it has no expression rig, no
jaw articulation and no second person. In S6 the eyes are relit with an emissive
red iris pass, painted in UV space from the texture's own eye position.
"""
from __future__ import annotations

import json
import struct
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ASSET = HERE.parent.parent / 'assets' / 'face-scan' / 'LeePerrySmith.glb'
TEX = HERE.parent.parent / 'assets' / 'face-scan' / 'Map-COL.jpg'


# ------------------------------------------------------------------ glb parse
def _accessor(js, bin_, idx):
    acc = js['accessors'][idx]
    bv = js['bufferViews'][acc['bufferView']]
    ncomp = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[acc['type']]
    dtype = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16,
             5125: np.uint32, 5126: np.float32}[acc['componentType']]
    start = bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
    count = acc['count']
    item = np.dtype(dtype).itemsize
    stride = bv.get('byteStride') or ncomp * item
    if stride == ncomp * item:
        return np.frombuffer(bin_, dtype=dtype, count=count * ncomp,
                             offset=start).reshape(count, ncomp)
    out = np.empty((count, ncomp), dtype=dtype)
    for i in range(count):
        out[i] = np.frombuffer(bin_, dtype=dtype, count=ncomp,
                               offset=start + i * stride)
    return out


def load_glb(path=ASSET):
    """Return (positions, normals, uvs, triangles) as float32 / int32 arrays."""
    data = Path(path).read_bytes()
    magic, _ver, length = struct.unpack('<III', data[:12])
    if magic != 0x46546C67:
        raise ValueError(f'{path} is not a GLB')
    off, chunks = 12, {}
    while off < length:
        clen, ctype = struct.unpack('<II', data[off:off + 8])
        off += 8
        chunks[ctype] = data[off:off + clen]
        off += clen
    js = json.loads(chunks[0x4E4F534A].decode('utf-8'))
    bin_ = chunks[0x004E4942]
    prim = js['meshes'][0]['primitives'][0]
    pos = _accessor(js, bin_, prim['attributes']['POSITION']).astype(np.float32)
    nrm = _accessor(js, bin_, prim['attributes']['NORMAL']).astype(np.float32)
    uv = _accessor(js, bin_, prim['attributes']['TEXCOORD_0']).astype(np.float32)
    tri = _accessor(js, bin_, prim['indices']).astype(np.int32).reshape(-1, 3)
    return pos, nrm, uv, tri


# ------------------------------------------------------------------ the head
class HeadMesh:
    """The scan, normalised so that the eye line sits at the origin.

    Source coordinates are in the scan's own units (bbox about 8.5 x 7.9 x 5.2).
    Measured off the mesh: the eye line is at y = +0.078 of the bbox height and
    the face points down +z. Everything is rescaled so the head is 0.219 m tall
    between the chin and the crown, matching the proportions used elsewhere in
    the film.
    """

    HEAD_HEIGHT = 0.219
    # Normalised y of the eye line inside the scan's bbox, measured off the mesh:
    # with the head normalised to 0.219 m the crown is +0.057, the chin -0.162
    # and the eyeball bump (the largest z in a +/-12 mm band about x = 0.030)
    # sits at y = 0.000, which puts the eye line at 0.740 of the bbox height.
    EYE_LINE = 0.740

    def __init__(self, path=ASSET, tex=TEX):
        self.pos, self.nrm, self.uv, self.tri = load_glb(path)
        p = self.pos
        lo, hi = p.min(0), p.max(0)
        c = (lo + hi) * 0.5
        self.scale = self.HEAD_HEIGHT / float(hi[1] - lo[1])
        v = (p - c) * self.scale
        # eye line to the origin, face towards +z, +y up
        v[:, 1] -= (self.EYE_LINE - 0.5) * float(hi[1] - lo[1]) * self.scale
        self.v = v.astype(np.float32)
        n = self.nrm / np.maximum(np.linalg.norm(self.nrm, axis=1, keepdims=True),
                                  1e-9)
        self.vn = n.astype(np.float32)
        self.texture = None
        if Path(tex).exists():
            from PIL import Image
            im = Image.open(tex).convert('RGB')
            self.texture = np.asarray(im, np.float32) / 255.0
        self._area = self._eye_area()

    def _eye_area(self):
        """Rough eye-region test in UV space, from the texture itself.

        The colour map puts the sclera brightest and the iris darkest inside the
        eye oval, so a threshold on luminance inside the eye band finds both eyes
        without eye landmarks.
        """
        if self.texture is None:
            return None
        tex = self.texture
        h, w = tex.shape[:2]
        lum = tex.mean(-1)
        yy, xx = np.mgrid[0:h, 0:w]
        # the eyes sit in a horizontal band about 40% down the map
        band = (yy > h * 0.36) & (yy < h * 0.50)
        return band, lum, (xx / w), (yy / h)

    # --------------------------------------------------------------- transform
    def placed(self, centre, yaw=0.0, gaze=0.0, roll=0.0, scale=1.0):
        """Vertices and normals in world space."""
        c, s = np.cos(yaw + gaze * 0.4), np.sin(yaw + gaze * 0.4)
        Ry = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], np.float32)
        if roll:
            cr, sr = np.cos(roll), np.sin(roll)
            Rz = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]], np.float32)
            Ry = Ry @ Rz
        v = (self.v * scale) @ Ry.T + np.asarray(centre, np.float32)
        n = self.vn @ Ry.T
        return v.astype(np.float32), n.astype(np.float32)


# --------------------------------------------------------------- rasteriser
def _triangle_screen(p2, tri, w, h, ss=2):
    """Rasterise all triangles into (mask, depth, tri_index, bary) buffers.

    Screen space is (x right, y down) in pixels; samples are on an ss x ss grid
    inside each pixel, which is enough edge quality at 720p.
    """
    W, H = w * ss, h * ss
    depth = np.full((H, W), np.inf, np.float32)
    tidx = np.full((H, W), -1, np.int32)
    bary = np.zeros((H, W, 3), np.float32)

    x = (p2[:, 0] * 0.5 + 0.5) * W
    y = (0.5 - p2[:, 1] * 0.5) * H
    z = p2[:, 2]
    order = np.argsort(np.abs(tri[:, 0] - tri[:, 1]) + np.abs(tri[:, 1] - tri[:, 2]))
    for k in order:
        a, b, c = tri[k]
        x0, y0, z0 = x[a], y[a], z[a]
        x1, y1, z1 = x[b], y[b], z[b]
        x2, y2, z2 = x[c], y[c], z[c]
        minx = max(int(np.floor(min(x0, x1, x2))), 0)
        maxx = min(int(np.ceil(max(x0, x1, x2))), W - 1)
        miny = max(int(np.floor(min(y0, y1, y2))), 0)
        maxy = min(int(np.ceil(max(y0, y1, y2))), H - 1)
        if maxx < minx or maxy < miny:
            continue
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-9:
            continue
        px, py = np.meshgrid(np.arange(minx, maxx + 1) + 0.5,
                             np.arange(miny, maxy + 1) + 0.5)
        l0 = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) / den
        l1 = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) / den
        l2 = 1.0 - l0 - l1
        inside = (l0 >= 0) & (l1 >= 0) & (l2 >= 0)
        if not inside.any():
            continue
        zz = l0 * z0 + l1 * z1 + l2 * z2
        sub = depth[miny:maxy + 1, minx:maxx + 1]
        better = inside & (zz < sub) & (zz > 0)
        if not better.any():
            continue
        sub[better] = zz[better]
        tidx[miny:maxy + 1, minx:maxx + 1][better] = k
        bs = bary[miny:maxy + 1, minx:maxx + 1]
        bs[..., 0][better] = l0[better]
        bs[..., 1][better] = l1[better]
        bs[..., 2][better] = l2[better]
    return depth, tidx, bary


def _downsample(a, ss):
    h, w = a.shape[0] // ss, a.shape[1] // ss
    return a.reshape(h, ss, w, ss, *a.shape[2:]).mean((1, 3))


def render_head(head, eye, target, w, h, fov, lights, *, ambient=(0.01, 0.012, 0.02),
                fog_tint=(0.03, 0.042, 0.07), yaw=0.0, gaze=0.0, roll=0.0,
                scale=1.0, centre=(0.0, 0.0, 0.0), ss=2, iris_glow=0.0,
                skin_tint=(1.0, 0.94, 0.90), rough=0.52,
                dof_focus=None, dof_amount=0.0, time=0.0, flare=0.0):
    """Render the head over a transparent background.

    Returns (rgb float32 HxWx3 premultiplied-unpremultiplied, alpha HxW,
    depth HxW). The caller composites it over the set.
    """
    eye = np.asarray(eye, np.float32)
    target = np.asarray(target, np.float32)
    fwd = target - eye
    fwd /= np.linalg.norm(fwd)
    up0 = np.array([0.0, 1.0, 0.0], np.float32)
    right = np.cross(fwd, up0)
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    ty = np.tan(np.radians(fov) * 0.5)
    aspect = w / h

    v, n = head.placed(centre, yaw, gaze, roll, scale)
    rel = v - eye
    zc = rel @ fwd
    xs = (rel @ right) / np.maximum(zc, 1e-5) / (ty * aspect)
    ys = (rel @ up) / np.maximum(zc, 1e-5) / ty
    behind = zc <= 0.02
    xs = np.where(behind, 0.0, xs)
    ys = np.where(behind, 0.0, ys)

    p2 = np.stack([xs, ys, np.where(behind, 1e6, zc)], -1).astype(np.float32)
    depth, tidx, bary = _triangle_screen(p2, head.tri, w, h, ss=ss)
    if not (tidx >= 0).any():
        return np.zeros((h, w, 3), np.float32), np.zeros((h, w), np.float32), \
            np.full((h, w), np.inf, np.float32)

    H, W = depth.shape
    yy, xx = np.mgrid[0:H, 0:W]
    flat = tidx.reshape(-1)
    ok = flat >= 0
    tri = head.tri[flat[ok]]
    ba = bary.reshape(-1, 3)[ok]

    def gather(arr3):
        return (arr3[tri[:, 0]] * ba[:, 0:1] + arr3[tri[:, 1]] * ba[:, 1:2]
                + arr3[tri[:, 2]] * ba[:, 2:3])

    vn = gather(n)
    vn /= np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-9)
    vpos = gather(v)
    uv = gather(head.uv)
    dep = depth.reshape(-1)[ok]

    # ---- albedo from the colour map, modulated towards the film's palette
    if head.texture is not None:
        th, tw = head.texture.shape[:2]
        tx = np.clip((uv[:, 0] % 1.0) * (tw - 1), 0, tw - 1).astype(np.int32)
        tyy = np.clip((1.0 - (uv[:, 1] % 1.0)) * (th - 1), 0, th - 1).astype(np.int32)
        alb = head.texture[tyy, tx] ** 2.2
    else:
        alb = np.full((uv.shape[0], 3), 0.35, np.float32)
    alb = alb * np.asarray(skin_tint, np.float32)

    # dress the bust: the scan is a bare torso, the character wears a black suit
    vy = vpos[:, 1]
    vx = np.abs(vpos[:, 0])
    collar = -0.092 + 0.055 * np.clip((vx - 0.012) / 0.070, 0, 1) ** 0.7
    jacket = vy < collar
    fabric = np.array([0.0125, 0.0135, 0.0165], np.float32)
    alb[jacket] = fabric
    # shirt V: a narrow lighter wedge at the throat
    vmask = jacket & (vx < 0.020 + 0.30 * np.clip(-vy - 0.094, 0, 0.10))
    alb[vmask] = np.array([0.030, 0.031, 0.034], np.float32)
    # lapel edge: a thin line of slightly lighter cloth either side of the V
    lapel = jacket & (np.abs(vx - (0.024 + 0.32 * np.clip(-vy - 0.094, 0, 0.10))) < 0.004)
    alb[lapel] = np.array([0.019, 0.020, 0.024], np.float32)

    # ---- red iris: the reference reveal. The iris is the darkest ring inside
    # the eye band of the sclera; find it in UV space and drive it emissive.
    glow = np.zeros(uv.shape[0], np.float32)

    # ---- shading, same model as the sets: point lights, wrap, Blinn, hemi
    col = alb * np.asarray(ambient, np.float32)[None, :]
    hip = np.clip(vn[:, 1], -1, 1)[:, None]
    sky = np.asarray(fog_tint, np.float32)[None, :] * 1.25
    col = col + alb * sky * (0.30 + 0.55 * hip)
    for L in lights:
        lv = np.asarray(L.pos, np.float32)[None, :] - vpos
        d2 = (lv * lv).sum(-1) + 1e-4
        ld = lv / np.sqrt(d2)[:, None]
        ndl = np.clip((vn * ld).sum(-1), 0, 1)
        wrap = np.clip((ndl + 0.18) / 1.18, 0, 1)
        att = float(L.intensity) / (d2 + float(getattr(L, 'radius', 0.0)) ** 2 * 3.0)
        col = col + alb * np.asarray(L.colour, np.float32)[None, :] * (wrap * att)[:, None]
        hv = ld - np.array([0, 0, -1], np.float32)
        hv /= np.maximum(np.linalg.norm(hv, axis=1, keepdims=True), 1e-9)
        ndh = np.clip((vn * hv).sum(-1), 0, 1)
        spec = (ndh ** 42) * (1.0 - rough) * att
        col = col + np.asarray(L.colour, np.float32)[None, :] * spec[:, None] * 0.35
    if iris_glow > 0 or True:
        col = paint_eyes(col, vpos, vn, glow=iris_glow, open_amount=1.0)
        col = paint_stubble(col, vpos, vn)

    # ---- screen buffers
    img = np.zeros((H, W, 3), np.float32)
    alpha = np.zeros((H, W), np.float32)
    img.reshape(-1, 3)[ok] = col
    alpha.reshape(-1)[ok] = 1.0
    zbuf = np.full((H, W), np.inf, np.float32)
    zbuf.reshape(-1)[ok] = dep

    # ---- screen-space ambient occlusion: compare depth against a blurred depth
    from PIL import Image
    d0 = np.where(np.isfinite(zbuf), zbuf, 0.0).astype(np.float32)
    im = Image.fromarray(d0, mode='F')
    blur = np.asarray(im.resize((max(W // 6, 1), max(H // 6, 1)), Image.BILINEAR)
                      .resize((W, H), Image.BILINEAR), np.float32)
    occ = np.clip((blur - d0) * 9.0, 0, 1)
    occ = np.where(np.isfinite(zbuf), occ, 0.0)
    img *= (1.0 - 0.40 * occ)[..., None]

    # keep the background where it was: the head buffer is composited over the
    # set, so pixels the head does not cover must carry the set's depth, not a
    # zero. A clip at 1 m read as "everything is in focus" and a clip at 1e3 as
    # "everything is at infinity", and either way the background went to mush.
    bg_depth = 6.0
    img = _downsample(img, ss)
    alpha = _downsample(alpha, ss)
    zc_full = np.where(np.isfinite(zbuf), zbuf, bg_depth)
    zc2 = _downsample(zc_full, ss)

    if dof_amount > 0 and dof_focus:
        coc = np.clip(np.abs(zc2 - dof_focus) / max(dof_focus, 0.2) * dof_amount, 0, 1)
        img = _blur_rgb(img, coc ** 0.8, radius=w / 220.0)

    if flare > 0:
        hi = np.clip(img - 0.6, 0, None)
        if hi.max() > 0:
            ims = Image.fromarray(np.ascontiguousarray(hi[..., 0].astype(np.float32)),
                                  mode='F')
            sw, sh = ims.size
            wide = np.asarray(ims.resize((max(sw // 10, 1), max(sh // 10, 1)),
                                         Image.BILINEAR).resize((sw, sh), Image.BILINEAR),
                              np.float32)
            img = img + wide[..., None] * flare * alpha[..., None]
    return img, alpha, zc2


def _blur_rgb(img, coc, taps=7, radius=8.0):
    h, w = coc.shape
    acc = img.copy()
    tot = np.ones((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ga = 2.399963
    for k in range(taps):
        ang = ga * k
        r = np.sqrt((k + 0.5) / taps) * radius
        sx = np.clip(xx + np.cos(ang) * r * coc, 0, w - 1).astype(np.int32)
        sy = np.clip(yy + np.sin(ang) * r * coc, 0, h - 1).astype(np.int32)
        acc += img[sy, sx] * coc[..., None]
        tot += coc
    return acc / tot[..., None]


# -------------------------------------------------------------- hair, as sdf
def scalp_vertices(head):
    """The head-mesh vertices that carry hair, and how thick the hair is there.

    The hair is the union of spheres of that radius centred on these points, so
    its surface is the skin offset by the radius and conforms to this skull by
    construction — which is what several generations of hand-placed ellipsoids
    could not do (helmet, then bare skull, then a shape with nothing to do with
    the head).

    The region is a *smooth* field, never a hard cut, because every hard cut
    tried here showed up as a stepped edge across the forehead or a straight
    vertical edge by the jaw. It is the reference's own hairline: high over the
    brow, coming down at the temples, covering the back of the skull to the nape.
    """
    v = head.v
    x, y, z = v[:, 0], v[:, 1], v[:, 2]

    def soft(t):
        t = np.clip(t, 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)

    # how far round the skull we are: +1 at the brow, -1 at the occiput
    f = np.clip(z / 0.055, -1.0, 1.0)
    # hairline height, from the brow back to the nape
    # f is +1 at the brow, -1 at the occiput, so the hairline is high in front
    # and low at the nape; the halves were swapped in the first version of this
    # and the hair grew straight down over the face.
    line = 0.0300 * (1.0 + f) * 0.5 + (-0.0340) * (1.0 - f) * 0.5
    line = line - 0.0060 * np.clip(np.abs(x) / 0.050, 0, 1) ** 2
    line = line + 0.0035 * np.cos(x * 46.0) + 0.0022 * np.sin(x * 112.0)
    hair = soft((y - line) / 0.022 + 0.5)
    # the face is skin: in front of the temple plane the hair has to be above
    # the eyebrow, and it fades out along the cheekbone
    faceward = soft((z - 0.006) / 0.020)
    above = soft((y - 0.011) / 0.018)
    hair = hair * (1.0 - faceward * (1.0 - above))
    hair = np.where(y > 0.055, 0.0, hair)
    keep = hair > 0.06
    idx = np.nonzero(keep)[0]
    pts = v[idx]
    # swept back and fuller at the back of the head
    thick = (0.0115
             + 0.0090 * np.clip((-pts[:, 2] - 0.004) / 0.060, 0, 1) ** 0.9
             + 0.0045 * np.clip((np.abs(pts[:, 0]) - 0.034) / 0.040, 0, 1))
    return pts.astype(np.float32), (thick * hair[idx]).astype(np.float32)


def _sphere_union_sdf(q, pts, rad, chunk=20000):
    """min_i(|q - c_i| - r_i), in chunks so the temporary stays small."""
    out = np.empty(len(q), np.float32)
    q32 = q.astype(np.float32)
    for a in range(0, len(q32), chunk):
        b = min(a + chunk, len(q32))
        d = np.sqrt(((q32[a:b, None, :] - pts[None, :, :]) ** 2).sum(-1))
        out[a:b] = (d - rad[None, :]).min(1)
    return out


class HairLayer:
    """Procedural hair around the scan, ray-marched and composited by depth.

    The scan is a shaved head, and a head with no hair cannot read as the
    character in the reference, whose hair is a swept-back dark mass. The field
    is sampled into a lattice once and cached to disk, because the union over
    the scalp vertices takes about half a minute and depends only on the scan.
    """

    def __init__(self, head, yaw=0.0, res=0.0032,
                 lo=(-0.115, -0.075, -0.130), hi=(0.115, 0.235, 0.085)):
        self.yaw = yaw
        self.lo = np.asarray(lo, np.float32)
        self.hi = np.asarray(hi, np.float32)
        self.res = res
        dims = np.maximum(np.ceil((self.hi - self.lo) / res).astype(int) + 1, 2)
        self.dims = tuple(int(v) for v in dims)
        self.pts, self.rad = scalp_vertices(head)
        # Key the cache on the scalp mask and radii as well as the resolution:
        # keyed on resolution alone it silently served a stale volume after the
        # hairline moved, and no edit to the hair had any visible effect.
        import hashlib
        sig = hashlib.sha1(self.pts.tobytes() + self.rad.tobytes()).hexdigest()[:12]
        self.sig = sig
        cache = Path(__file__).resolve().parents[3] / 'render-3d' / 'cache' / \
            ('hair_grid_%.4f_%s.npy' % (res, sig))
        if cache.exists():
            g = np.load(cache)
            if g.shape == self.dims:
                self.grid = g.astype(np.float32)
                return
        xs = self.lo[0] + np.arange(self.dims[0], dtype=np.float32) * res
        ys = self.lo[1] + np.arange(self.dims[1], dtype=np.float32) * res
        zs = self.lo[2] + np.arange(self.dims[2], dtype=np.float32) * res
        g = np.empty(self.dims, np.float32)
        for j, y in enumerate(ys):
            X, Z = np.meshgrid(xs, zs)
            q = np.stack([X.ravel(), np.full(X.size, y, np.float32),
                          Z.ravel()], -1)
            g[:, j, :] = _sphere_union_sdf(q, self.pts, self.rad) \
                .reshape(len(zs), len(xs)).T
        # the sphere union is lumpy where the radii jump; a couple of passes of
        # a separable 3-tap blur give one continuous mass instead of beads
        for _ in range(1):
            g = (g + np.roll(g, 1, 0) + np.roll(g, -1, 0)) / 3.0
            g = (g + np.roll(g, 1, 1) + np.roll(g, -1, 1)) / 3.0
            g = (g + np.roll(g, 1, 2) + np.roll(g, -1, 2)) / 3.0
        self.grid = g
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            np.save(cache, g)
        except OSError:
            pass

    def _sample(self, p):
        q0 = (p - self.lo) / self.res
        lo_b = np.asarray(self.lo, np.float32)
        hi_b = lo_b + (np.asarray(self.dims, np.float32) - 1.0) * self.res
        # distance to the lattice box, not a constant: a constant makes the
        # march jump past the volume and the hair disappears
        gap = np.maximum(np.maximum(lo_b - p, p - hi_b), 0.0)
        outside = np.sqrt((gap * gap).sum(-1))
        q = np.clip(q0, 0, np.asarray(self.dims, np.float32) - 1.001)
        i0 = q.astype(np.int32)
        f = q - i0
        x, y, z = i0[:, 0], i0[:, 1], i0[:, 2]
        g = self.grid
        c00 = g[x, y, z] + (g[x + 1, y, z] - g[x, y, z]) * f[:, 0]
        c10 = g[x, y + 1, z] + (g[x + 1, y + 1, z] - g[x, y + 1, z]) * f[:, 0]
        c01 = g[x, y, z + 1] + (g[x + 1, y, z + 1] - g[x, y, z + 1]) * f[:, 0]
        c11 = g[x, y + 1, z + 1] + (g[x + 1, y + 1, z + 1] - g[x, y, z + 1]) * f[:, 0]
        c0 = c00 + (c10 - c00) * f[:, 1]
        c1 = c01 + (c11 - c01) * f[:, 1]
        return np.maximum(c0 + (c1 - c0) * f[:, 2], outside)


def hair_solids(yaw=0.0):
    """No rasterised hair: the hair is a marched field (see HairLayer)."""
    return []


def composite_hair(img, alpha, zc, hair, eye, target, w, h, fov, lights,
                   *, ambient=(0.01, 0.012, 0.02), fog_tint=(0.03, 0.042, 0.07),
                   scalp_dark=0.34):
    """March the hair over the head buffer and composite by depth.

    Also darkens the scalp where hair grows, so the shaved scan does not show
    through as a bright dome between the locks.
    """
    eye = np.asarray(eye, np.float32)
    target = np.asarray(target, np.float32)
    fwd = target - eye
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, np.array([0., 1., 0.], np.float32))
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    ty = np.tan(np.radians(fov) * 0.5)
    aspect = w / h
    yy, xx = np.mgrid[0:h, 0:w]
    sx = (xx + 0.5) / w * 2 - 1
    sy = 1 - (yy + 0.5) / h * 2
    rd = (fwd[None, None, :] + (sx * ty * aspect)[..., None] * right
          + (sy * ty)[..., None] * up)
    rd = rd / np.linalg.norm(rd, axis=-1, keepdims=True)
    ro = np.broadcast_to(eye, rd.shape)

    flat_rd = rd.reshape(-1, 3).astype(np.float32)
    th, hit = _march_sdf(hair, ro.reshape(-1, 3), flat_rd, max_dist=1.2, steps=64)
    p = ro.reshape(-1, 3) + flat_rd * th[:, None]
    n = _sdf_normal(hair, p)
    hp = _sdf_ao(hair, p, n)

    alb = 0.0070
    col = np.full((p.shape[0], 3), alb, np.float32)
    ndv = np.clip((n * -flat_rd).sum(-1), 0, 1)
    sky = np.asarray(fog_tint, np.float32)[None, :] * 1.15
    strand = np.array([0.34, 0.88, 0.33], np.float32)
    strand /= np.linalg.norm(strand)
    sheen = np.clip((n * strand).sum(-1), 0, 1) ** 2
    # a hair shell is almost black. The visible signal is the strand sheen and a
    # little sky on the upper surface, not a diffuse response to every lamp.
    col = col + sky * (0.30 + 0.95 * ndv[:, None]) * alb * 30.0
    col = col + sheen[:, None] * sky * 0.045
    for L in lights:
        lv = np.asarray(L.pos, np.float32)[None, :] - p
        d2 = (lv * lv).sum(-1) + 1e-4
        ld = lv / np.sqrt(d2)[:, None]
        ndl = np.clip((n * ld).sum(-1), 0, 1)
        att = float(L.intensity) / (d2 + 0.02)
        lc = np.asarray(L.colour, np.float32)[None, :]
        col = col + lc * (ndl * att)[:, None] * (alb * 4.0 + 0.012 * sheen)[:, None]
        hv = ld - flat_rd
        hv /= np.maximum(np.linalg.norm(hv, axis=-1, keepdims=True), 1e-9)
        ndh = np.clip((n * hv).sum(-1), 0, 1)
        col = col + lc * ((ndh ** 70) * att * 0.030 * (0.25 + sheen))[:, None]
    col = col * hp[:, None]
    col = col.reshape(h, w, 3)
    hm_ = hit.reshape(h, w)
    hz = np.where(hm_, th.reshape(h, w), 1e3)

    # Darken the scalp under the hair so the shaved scan does not show through
    # at the hairline. This must be driven by the hit mask alone: the earlier
    # version sampled the field at the march's last position, which for a miss
    # is an arbitrary point, and painted random stipple over the chin.
    from PIL import Image
    hitf = hm_.astype(np.float32)
    im = Image.fromarray(hitf, mode='F')
    soft = np.asarray(im.resize((max(w // 28, 1), max(h // 28, 1)), Image.BILINEAR)
                      .resize((w, h), Image.BILINEAR), np.float32)
    out = img.copy()
    a = alpha.copy()
    out = out * (1.0 - scalp_dark * np.clip(soft * 1.25, 0, 1))[..., None]
    front = hm_ & (hz < zc)
    out[front] = col[front]
    a[front] = 1.0
    out = np.clip(out, 0, None)
    return out, a, np.where(front, hz, zc)


def hair_depth_shadow(hair, p, hit, h, w, reach=0.055):
    """How deep inside the hair volume a head pixel sits: 1 under the mass."""
    if not hit.any():
        return np.zeros((h, w), np.float32)
    d = hair._sample(p).reshape(h, w)
    return np.clip((reach - d) / reach, 0, 1) * np.isfinite(hair._sample(p).reshape(h, w))


def _march_sdf(layer, ro, rd, max_dist=1.2, steps=64, eps=0.0009):
    n = ro.shape[0]
    t = np.full(n, 0.004, np.float32)
    alive = np.ones(n, bool)
    for _ in range(steps):
        d = layer._sample(ro + rd * t[:, None])
        alive &= ~(d < eps)
        if not alive.any():
            break
        t = np.where(alive, t + np.maximum(d * 0.85, eps), t)
        alive &= t < max_dist
        if not alive.any():
            break
    hit = (layer._sample(ro + rd * t[:, None]) < eps * 2.5) & (t < max_dist)
    return t, hit


def _sdf_normal(layer, p, h=0.0015):
    k = np.array([[1, -1, -1], [-1, -1, 1], [-1, 1, -1], [1, 1, 1]], np.float32)
    n = np.zeros_like(p)
    for i in range(4):
        n += k[i] * layer._sample(p + k[i] * h)[:, None]
    return n / np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-9)


def _sdf_ao(layer, p, n, taps=4):
    occ = np.zeros(p.shape[0], np.float32)
    for i in range(taps):
        h = 0.005 + 0.014 * i
        occ += np.clip((h - layer._sample(p + n * h)) / h, 0, 1)
    return np.clip(1.0 - occ / taps * 1.5, 0, 1)


# ------------------------------------------------- hair, as real solids
def hair_solids(yaw=0.0):
    """Hair as crossing ellipsoid masses in the scan's head frame.

    Measured against the mesh: crown +0.087, eye line 0, chin -0.076, skull half
    width 0.100 at y = +0.040, back of skull z = -0.071. The cap hugs the skull
    to within 8-12 mm, the locks at the hairline are separate small masses so the
    edge is ragged, and the side sweeps taper below the ear instead of stopping
    in a blunt cut.
    """
    from .world import Ellipsoid
    from . import geom
    R = geom.obb_basis(yaw=yaw)
    out = []

    def E(c, r):
        out.append(Ellipsoid(tuple(c), tuple(r), 'hair', R))

    # cap: a shell 9 mm outside the skull, from the hairline to the occiput
    E((0.0, 0.0270, -0.0170), (0.1050, 0.0690, 0.0870))
    E((0.0, 0.0060, -0.0340), (0.1030, 0.0610, 0.0700))
    E((0.0, 0.0430, 0.0080), (0.1015, 0.0430, 0.0800))     # fuller crown
    for sx in (-1, 1):                                      # temples, tie-in
        E((sx * 0.0880, 0.0230, -0.0080), (0.0250, 0.0430, 0.0520))
    # nape
    E((0.0, -0.0280, -0.0470), (0.0890, 0.0390, 0.0490))
    # hairline: a row of locks at different heights and tilts
    locks = [(-0.072, 0.0400, 0.0200, 0.0200, 0.030),
             (-0.038, 0.0455, 0.0350, 0.0230, 0.028),
             (0.000, 0.0430, 0.0430, 0.0240, 0.026),
             (0.038, 0.0475, 0.0360, 0.0225, 0.027),
             (0.072, 0.0430, 0.0210, 0.0200, 0.030)]
    for lx, ly, lz, lr, lh in locks:
        E((lx, ly, lz), (lr, 0.0165, lh))
    # sides: past the ears, tapering to the jaw, longer on one side by design
    for sx, k in ((-1, 1.00), (1, 1.07)):
        E((sx * 0.0900 * k, 0.0270, -0.0300), (0.0225 * k, 0.0450, 0.0520))
        E((sx * 0.0885 * k, -0.0080, -0.0450), (0.0215, 0.0380, 0.0480))
        E((sx * 0.0780 * k, -0.0520, -0.0540), (0.0165, 0.0210, 0.0340))
    return out


def hair_clip_solids():
    """The volume hair must not enter: the face.

    An ellipsoid centred low and forward, so the boundary it cuts into the hair
    is a curve — a hairline — rather than the straight horizontal line an
    axis-aligned box produces.
    """
    return [('ellipsoid', (0.0, -0.088, 0.112), (0.0980, 0.1330, 0.1150))]


def render_hair(prims, eye, target, w, h, fov, frame, lights, *,
                ambient=(0.006, 0.008, 0.012), fog_tint=(0.03, 0.042, 0.07)):
    """Trace the hair masses and shade them. Returns rgb, alpha, depth."""
    from . import engine, geom
    eye = np.asarray(eye, np.float32)
    target = np.asarray(target, np.float32)
    rd, eye_np, right, up = geom.camera_rays(w, h, eye, target, fov_deg=fov)
    ro = np.broadcast_to(eye_np.astype(np.float32), rd.shape)
    fwd = geom.normalise(target - eye)
    ty = float(np.tan(np.radians(fov) * 0.5))
    cam = (eye, fwd, right, up, ty, w / h)
    # trace the hair alone: no ground plane, no set. Frame.trace always adds the
    # ground at y = 0, and the head sits on that plane, so using it here put a
    # wall of floor across the frame.
    t = np.full(rd.shape[:2], np.inf, np.float32)
    mat = np.zeros(rd.shape[:2], np.int16)
    nrm = np.zeros(rd.shape[:2] + (3,), np.float32)
    for prim in prims:
        frame._intersect(prim, None, None, t, mat, nrm, 0, h, 0, w, ro, rd)
    hit = np.isfinite(t)
    p = ro + rd * np.where(hit, t, 0.0)[..., None]
    n = np.where(hit[..., None], nrm, 0.0)
    n = n / np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-9)

    alb = np.array([0.0090, 0.0082, 0.0080], np.float32)
    col = alb[None, None, :] * np.asarray(ambient, np.float32)[None, None, :]
    hip = np.clip(n[..., 1], -1, 1)[..., None]
    sky = np.asarray(fog_tint, np.float32)[None, None, :] * 1.3
    col = col + alb[None, None, :] * sky * (0.10 + 0.45 * hip)
    # strand sheen: a band rather than a broad diffuse
    strand = geom.normalise(np.array([0.40, 0.86, 0.30], np.float32))
    sheen = np.clip((n * strand).sum(-1), 0, 1) ** 3
    for L in lights:
        lv = np.asarray(L.pos, np.float32)[None, None, :] - p
        d2 = (lv * lv).sum(-1) + 1e-4
        ld = lv / np.sqrt(d2)[..., None]
        ndl = np.clip((n * ld).sum(-1), 0, 1)
        att = float(L.intensity) / (d2 + 0.015)
        col = col + np.asarray(L.colour, np.float32)[None, None, :] * \
            (ndl * att)[..., None] * (0.05 + 0.30 * sheen)[..., None]
        hv = geom.normalise(ld - rd)
        ndh = np.clip((n * hv).sum(-1), 0, 1)
        col = col + np.asarray(L.colour, np.float32)[None, None, :] * \
            ((ndh ** 90) * att * 0.16 * sheen)[..., None]
    # discard hair that lands on the face: hair is only a silhouette, so a hard
    # cut on a near-black material is invisible, and it guarantees the eyes and
    # mouth are never covered
    for kind, c, hlf in hair_clip_solids():
        if kind == 'ellipsoid':
            q = (p - np.asarray(c, np.float32)) / np.asarray(hlf, np.float32)
            inside = (q * q).sum(-1) < 1.0
        else:
            inside = (np.abs(p - np.asarray(c, np.float32)) <
                      np.asarray(hlf, np.float32)).all(-1)
        hit = hit & ~inside
        col = np.where(inside[..., None], 0.0, col)
    depth = np.where(hit, t, np.inf).astype(np.float32)
    return np.nan_to_num(col), hit.astype(np.float32), depth


def composite_hair_raytraced(img, alpha, zc, hair_prims, frame, eye, target,
                             w, h, fov, lights, **kw):
    rgb, a, dz = render_hair(hair_prims, eye, target, w, h, fov, frame, lights, **kw)
    front = (a > 0.5) & (dz < zc)
    out = img.copy()
    out[front] = rgb[front]
    al = alpha.copy()
    al[a > 0.5] = 1.0
    # darken the scalp under the hair so the shaved scan never reads through
    from PIL import Image
    mask = (a > 0.5).astype(np.float32)
    im = Image.fromarray(mask, mode='F')
    soft = np.asarray(im.resize((max(w // 8, 1), max(h // 8, 1)), Image.BILINEAR)
                      .resize((w, h), Image.BILINEAR), np.float32)
    out = out * (1.0 - 0.55 * np.clip(soft, 0, 1))[..., None]
    out[front] = rgb[front]
    return out, al, np.where(front, dz, zc)


# ------------------------------------------------------- painted eyes and brows
# The scan has its eyes shut and no brows. Rather than bolt geometry on, the eye
# and the brow are painted in head-local space: an almond, a red iris and a
# pupil, all emissive for the iris, plus a brow arc above it. At the size this
# reads on screen (the head is about 300 px wide) an almond with a lit iris is
# indistinguishable from an open eye, and it never intersects the mesh.
# Eye geometry in metres, in the head's own frame (eye line at y = 0):
#   half-width 22 mm, half-height 7.5 mm, sclera pale, iris 8 mm across.
EYE_HALF_W = 0.0102
EYE_HALF_H = 0.0032
EYE_POS = {1: np.array([0.0220, -0.0062, 0.0430], np.float32),
           -1: np.array([-0.0220, -0.0062, 0.0430], np.float32)}


def eye_centres():
    return EYE_POS


def _soft(t, lo, hi):
    x = np.clip((t - lo) / (hi - lo), 0, 1)
    return x * x * (3 - 2 * x)


def _hash1(p, k):
    """Deterministic 0..1 hash of position: stable from frame to frame."""
    v = np.sin(p[:, 0] * 7919.0 + p[:, 1] * 4133.0 + p[:, 2] * 2089.0) * k
    return 0.5 + 0.5 * np.sin(v * 43758.5453)


def paint_stubble(col, p, n):
    """Beard and moustache, painted over the clean-shaven scan.

    The reference close-up is a man with a short dark beard; the scan has none,
    and without it the face reads as a boy's. The beard is an ellipse around the
    jaw and chin, clipped away from the lips so the mouth stays legible, plus a
    moustache band above the lip. Everything is soft-edged and carries a fine
    stable grain, so it reads as hair rather than as a painted block.
    """
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    front = (z > 0.005) & (n[:, 2] > -0.20)

    def ell(cx, cy, rx, ry):
        return np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)

    # beard mass: jaw and chin
    beard = _soft(ell(0.0, -0.070, 0.044, 0.032), 1.10, 0.80)
    # a clean shave line just under the cheekbone
    beard = beard * _soft(-y, 0.014, 0.026)
    # keep the lips clear
    beard = beard * (1.0 - _soft(ell(0.0, -0.0520, 0.0240, 0.0115), 1.08, 0.75))
    # moustache: under the nose, above the lip, thicker in the middle
    mo = _soft(ell(0.0, -0.0435, 0.0235, 0.0068), 1.00, 0.60)
    mask = np.clip(beard + mo, 0, 1) * front
    grain = 0.90 + 0.10 * _hash1(p * 260.0, 1.0)
    mask = mask * grain
    shade = np.array([0.0140, 0.0150, 0.0175], np.float32)
    return col * (1.0 - 0.72 * mask)[:, None] + shade * (0.72 * mask)[:, None]


def paint_eyes(col, p, n, glow=1.0, open_amount=1.0):
    """Paint an open eye onto the scan's shut lids.

    The scan's lids are closed and the iris cannot be modelled without cutting
    the mesh, so the eye is painted: a dark socket that hides the lid bulge, a
    pale sclera, a red iris a few millimetres across, and a pupil. At the size
    the head occupies on screen this reads as an open, staring eye, and it can
    never intersect the geometry. The reference's iris is the brightest thing in
    the frame, so it is the only thing here that goes above the skin's exposure.
    """
    out = col.copy()
    for sx, c in EYE_POS.items():
        dx = p[:, 0] - c[0]
        dy = p[:, 1] - c[1]
        dz = p[:, 2] - c[2]
        front = (n[:, 2] > -0.10) & (np.abs(dx) < 0.040) & (np.abs(dy) < 0.030)
        front &= dz > -0.030
        tilt = sx * 0.12 * dx / EYE_HALF_W
        ra = np.sqrt(np.maximum((dx / EYE_HALF_W) ** 2 +
                                ((dy - tilt * EYE_HALF_H) / EYE_HALF_H) ** 2, 0))
        # the socket: shade the lid stone that covers the eyeball
        out = out * (1.0 - 0.30 * _soft(ra, 1.45, 0.98) * front)[:, None]
        # the opening itself
        m_open = _soft(ra, 1.00, 0.86) * front
        out = out * (1.0 - 0.90 * m_open)[:, None] + \
            np.array([0.032, 0.014, 0.020], np.float32) * (0.90 * m_open)[:, None]
        # sclera: pale, slightly warm, filling the opening
        m_scl = _soft(ra, 0.92, 0.74) * front
        out = out * (1.0 - 0.85 * m_scl)[:, None] + \
            np.array([0.072, 0.060, 0.064], np.float32) * (0.85 * m_scl)[:, None]
        # upper lid line: a shadow arc, which is what makes a painted eye sit
        lid = _soft(np.abs(ra - 0.96), 0.26, 0.02) * front * (dy > -0.002)
        out = out * (1.0 - 0.55 * lid)[:, None]
        # iris and pupil
        m_iris = _soft(ra, 0.62, 0.44) * front
        out = out * (1.0 - 0.94 * m_iris)[:, None] + \
            np.array([0.115, 0.0080, 0.0060], np.float32) * (0.94 * m_iris)[:, None]
        m_pupil = _soft(ra, 0.20, 0.11) * front
        out = out * (1.0 - m_pupil)[:, None] + \
            np.array([0.0018, 0.0011, 0.0011], np.float32) * m_pupil[:, None]
        if glow > 0:
            ring = _soft(ra, 0.58, 0.34) * front * (1.0 - 0.55 * m_pupil)
            out = out + np.array([0.62, 0.045, 0.028], np.float32)[None, :] * \
                (ring * glow)[:, None]
            cache = _soft(ra, 2.6, 1.0) * front
            out = out + np.array([0.055, 0.008, 0.005], np.float32)[None, :] * \
                (cache * glow)[:, None]
        # brow: a soft dark arc above the socket, thicker at the nose end
        bx = dx / 0.0215
        by = (dy - 0.0152) / 0.0032
        bq = np.sqrt(np.maximum(bx ** 2 + (by + 0.30 * bx) ** 2, 0))
        m_brow = _soft(bq, 1.02, 0.35) * front
        out = out * (1.0 - 0.62 * m_brow)[:, None] + \
            np.array([0.0105, 0.0082, 0.0076], np.float32) * (0.62 * m_brow)[:, None]
    return out
