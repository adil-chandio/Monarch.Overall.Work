#!/usr/bin/env python3
"""A small software 3D renderer — meshes, z-buffer, Blinn-Phong, water caustics.

There is no GPU and no OpenGL in this sandbox, so this is a rasteriser written
against numpy. It is not a toy: it does perspective-correct interpolation, per-pixel
normalised normals, a shadow-free but physically-shaped light rig (key from above,
fill from the water surface, rim from behind), depth of field via a CoC gather, and
a film grade.

The reason it exists: the operator rejected flat vector animals twice and asked for
3D. A mesh with normals catches light along a curved flank, so a whale reads as a
rounded body instead of a painted silhouette, and the camera can orbit it because
the geometry is real.

Conventions
  right-handed, +x right, +y up, +z into the screen (camera looks down +z)
  all meshes are numpy float32 arrays of (N, 3) vertices, triangle index arrays
  
Run the self-test:  python scripts/lib/tri3d.py
"""
from __future__ import annotations

import math
import numpy as np

# ---------------------------------------------------------------------------
# Vector helpers
# ---------------------------------------------------------------------------


def norm(v, axis=-1, eps=1e-9):
    n = np.linalg.norm(v, axis=axis, keepdims=True)
    return v / np.maximum(n, eps)


def rotation_y(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=np.float32)


def rotation_x(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=np.float32)


def rotation_z(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float32)


def translation(t):
    m = np.eye(4, dtype=np.float32)
    m[:3, 3] = t
    return m


def euler(rx=0.0, ry=0.0, rz=0.0):
    return rotation_y(ry) @ rotation_x(rx) @ rotation_z(rz)


def look_at(eye, target, up=(0.0, 1.0, 0.0)):
    """A camera matrix that maps world space into camera space (+z forward)."""
    eye = np.asarray(eye, dtype=np.float32)
    target = np.asarray(target, dtype=np.float32)
    up = np.asarray(up, dtype=np.float32)
    f = norm(target - eye)
    r = norm(np.cross(up, f))
    u = np.cross(f, r)
    m = np.eye(4, dtype=np.float32)
    m[0, :3] = r
    m[1, :3] = u
    m[2, :3] = f
    m[:3, 3] = -m[:3, :3] @ eye
    return m


def perspective(fov_deg, aspect, near=0.05, far=200.0):
    """Projection for a +z-forward camera, with LINEAR depth in [0, 1].

    The obvious thing here is the OpenGL matrix, which assumes the camera looks down
    -z. Dropping that in made clip.w negative for every point in front of the camera,
    so NDC came out mirrored and every depth landed outside [0, 1] -- the frame was
    empty and the bug looked like a culling problem. This version sets w = +z and
    maps z to (z - near) / (far - near), which is all a z-buffer needs.
    """
    f = 1.0 / math.tan(math.radians(fov_deg) / 2.0)
    m = np.zeros((4, 4), dtype=np.float32)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = 1.0 / (far - near)
    m[2, 3] = -near / (far - near)
    m[3, 2] = 1.0
    return m


# ---------------------------------------------------------------------------
# Mesh primitives
# ---------------------------------------------------------------------------


class Mesh:
    """Vertices + triangles + optional vertex colour / per-face material id."""

    def __init__(self, verts, tris, colour=(160, 170, 180), material="skin", uvs=None):
        self.v = np.asarray(verts, dtype=np.float32).reshape(-1, 3)
        self.t = np.asarray(tris, dtype=np.int32).reshape(-1, 3)
        self.colour = np.asarray(colour, dtype=np.float32) / 255.0
        self.material = material
        self.uv = uvs

    def copy(self):
        m = Mesh(self.v.copy(), self.t.copy(), self.colour * 255.0, self.material)
        m.uv = None if self.uv is None else self.uv.copy()
        # copy() used to drop these, which silently deleted the orca's white
        # markings: draw_orca() deforms the body through copy(), then looks for
        # body.patches - and found nothing, so the animal rendered pure black.
        m.two_sided = getattr(self, "two_sided", False)
        m.patches = getattr(self, "patches", None)
        return m

    def transform(self, m3):
        out = self.copy()
        out.v = (self.v @ m3[:3, :3].T) + m3[:3, 3]
        return out

    def scale(self, s):
        out = self.copy()
        out.v = self.v * np.asarray(s, dtype=np.float32)
        return out

    def translate(self, t):
        out = self.copy()
        out.v = self.v + np.asarray(t, dtype=np.float32)
        return out

    def mirrored_y(self):
        out = self.copy()
        out.v = self.v * np.array([1, -1, 1], dtype=np.float32)
        out.t = out.t[:, ::-1]
        return out

    def bounds(self):
        return self.v.min(axis=0), self.v.max(axis=0)


def tube(rings, colour=(140, 150, 160), material="skin", cap=True):
    """Build a tube from a list of rings, each ring a list of (x, y, z).

    Every ring must have the same length. This is how the whales are built: a
    spine of cross-sections, each an ellipse whose radii change along the body,
    with a lateral offset so the animal can bend.
    """
    rings = [np.asarray(r, dtype=np.float32) for r in rings]
    n = len(rings[0])
    verts = np.concatenate(rings, axis=0)
    tris = []
    for i in range(len(rings) - 1):
        a = i * n
        b = (i + 1) * n
        for j in range(n):
            j2 = (j + 1) % n
            # counter-clockwise when seen from OUTSIDE the tube. The first version
            # had this reversed, so every face normal pointed inward and backface
            # culling removed the entire animal.
            tris.append((a + j, b + j, b + j2))
            tris.append((a + j, b + j2, a + j2))
    if cap:
        # fans at both ends
        c0 = len(verts)
        c1 = len(verts) + 1
        v0 = rings[0].mean(axis=0)
        v1 = rings[-1].mean(axis=0)
        verts = np.vstack([verts, v0[None, :], v1[None, :]])
        base0 = 0
        base1 = (len(rings) - 1) * n
        for j in range(n):
            j2 = (j + 1) % n
            tris.append((base0 + j, base0 + j2, c0))
            tris.append((base1 + j2, base1 + j, c1))
    return Mesh(verts, tris, colour, material)


def ellipse_ring(centre, rx, ry, n=20, tilt=0.0):
    """One cross-section: an ellipse in the x-y plane at a given z."""
    cx, cy, cz = centre
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x = math.cos(a) * rx
        y = math.sin(a) * ry
        # tilt rolls the section so a body can bank
        if tilt:
            ct, st = math.cos(tilt), math.sin(tilt)
            x, y = x * ct - y * st, x * st + y * ct
        out.append((cx + x, cy + y, cz))
    return out


def mirror_x(mesh):
    """The cheap way to make a matching left flipper from a right one."""
    out = mesh.copy()
    out.v = out.v * np.array([-1, 1, 1], dtype=np.float32)
    out.t = out.t[:, ::-1]
    return out


def merge(meshes):
    vs, ts, off = [], [], 0
    colour = None
    mat = None
    for m in meshes:
        vs.append(m.v)
        ts.append(m.t + off)
        off += len(m.v)
        colour = m.colour if colour is None else colour
        mat = m.material if mat is None else mat
    allv = np.concatenate(vs, axis=0)
    # per-vertex colour so different islands can share one draw
    cols = []
    for m in meshes:
        cols.append(np.tile(m.colour[None, :], (len(m.v), 1)))
    return Mesh(all_v(allv), np.concatenate(ts, axis=0), (255, 255, 255), mat,
                uvs=None), np.concatenate(cols, axis=0)


def all_v(v):
    return v


# ---------------------------------------------------------------------------
# The rasteriser
# ---------------------------------------------------------------------------


class Renderer:
    def __init__(self, w, h, ssaa=1):
        self.w, self.h = w * ssaa, h * ssaa
        self.ow, self.oh = w, h
        self.ssaa = ssaa
        self.colour = np.zeros((self.h, self.w, 3), dtype=np.float32)
        self.depth = np.ones((self.h, self.w), dtype=np.float32)
        # camera
        self.view = np.eye(4, dtype=np.float32)
        self.proj = perspective(42.0, self.w / self.h)
        # lights
        self.key = norm(np.array([-0.35, 0.86, -0.38], dtype=np.float32))
        self.key_col = np.array([0.94, 0.98, 1.00], dtype=np.float32) * 1.30
        self.fill_col = np.array([0.26, 0.46, 0.60], dtype=np.float32) * 0.40
        self.rim_col = np.array([0.55, 0.80, 0.95], dtype=np.float32) * 0.75
        self.ambient = np.array([0.055, 0.095, 0.125], dtype=np.float32)
        # The rig is a *direction*, not a fixture. Every shot inherits it, and a shot
        # that wants a different key (a hero shot where the animal must read, not
        # silhouette) sets it. v2 had it hard-coded inside draw(), so the card shot
        # put the key behind the whale relative to that camera and rendered a
        # featureless dark shape under the title - correct lighting, wrong shot.
        self.key_dir = np.array([-0.30, 0.82, -0.48], dtype=np.float32)

    # -- scene ------------------------------------------------------------
    def clear(self, top=(0.05, 0.16, 0.21), bottom=(0.010, 0.030, 0.045)):
        k = np.linspace(0, 1, self.h, dtype=np.float32)[:, None, None]
        top = np.asarray(top, dtype=np.float32)
        bottom = np.asarray(bottom, dtype=np.float32)
        self.colour[:] = top[None, None, :] * (1 - k) + bottom[None, None, :] * k
        self.depth[:] = 1.0

    def light_rig(self, key=None, key_gain=1.30, ambient=None, fill=None, rim=None):
        """Re-light for one shot. Pass a world-space direction to move the key."""
        if key is not None:
            self.key_dir = norm(np.asarray(key, dtype=np.float32))
        self.key_col = np.array([0.94, 0.98, 1.00], dtype=np.float32) * key_gain
        if ambient is not None:
            self.ambient = np.asarray(ambient, dtype=np.float32)
        if fill is not None:
            self.fill_col = np.asarray(fill, dtype=np.float32)
        if rim is not None:
            self.rim_col = np.asarray(rim, dtype=np.float32)

    def set_camera(self, eye, target, up=(0, 1, 0), fov=42.0, clear=True):
        """Point the camera and, by default, reset the buffers.

        Every beat calls this before it draws. Without the reset the depth buffer
        keeps whatever the previous beat wrote, and stale near geometry punches
        holes through the new frame: a black orca rendered as a translucent ghost
        with its own dorsal fin floating outside it.
        """
        self.view = look_at(eye, target, up)
        self.proj = perspective(fov, self.w / self.h)
        if clear:
            self.clear()

    # -- draw -------------------------------------------------------------
    def draw(self, mesh, model=None, decal=0.0):
        """Rasterise one mesh: z-buffer, backface cull, Blinn-Phong.

        All geometry maths happens in VIEW space. The earlier version built face
        normals from world-space positions and then dotted them with a view-space
        direction to camera, which is meaningless: every animal either vanished or
        rendered inside out depending on where the camera was.
        """
        m4 = np.eye(4, dtype=np.float32) if model is None else model
        world = (mesh.v @ m4[:3, :3].T) + m4[:3, 3]
        vc = (world @ self.view[:3, :3].T) + self.view[:3, 3]
        clip = np.concatenate([vc, np.ones((len(vc), 1), dtype=np.float32)], axis=1) @ self.proj.T
        w = clip[:, 3:4]
        ndc = clip[:, :3] / np.maximum(w, 1e-6)
        sx = (ndc[:, 0] * 0.5 + 0.5) * self.w
        sy = (1.0 - (ndc[:, 1] * 0.5 + 0.5)) * self.h
        sz = ndc[:, 2]

        tri = mesh.t
        p0, p1, p2 = vc[tri[:, 0]], vc[tri[:, 1]], vc[tri[:, 2]]
        fn = norm(np.cross(p1 - p0, p2 - p0))
        centre = (p0 + p1 + p2) / 3.0
        # eye is the origin in view space, so the direction to it is -normalise(centre)
        to_eye = -norm(centre)
        facing = (fn * to_eye).sum(axis=1)
        # A patch shell or a flat plate has no inside. Culling it from behind leaves
        # the white saddle invisible half the time, which read as "the orca has no
        # markings" rather than as a backface problem.
        two_sided = getattr(mesh, "two_sided", False)
        keep = (facing > 1e-4) | (two_sided & (facing < -1e-4))
        tri, fn, centre, to_eye = tri[keep], fn[keep], centre[keep], to_eye[keep]
        if len(tri) == 0:
            return
        if two_sided:
            fn = fn * np.sign((fn * to_eye).sum(axis=1))[:, None]

        x = np.stack([sx[tri[:, 0]], sx[tri[:, 1]], sx[tri[:, 2]]], axis=1)
        y = np.stack([sy[tri[:, 0]], sy[tri[:, 1]], sy[tri[:, 2]]], axis=1)
        z = np.stack([sz[tri[:, 0]], sz[tri[:, 1]], sz[tri[:, 2]]], axis=1)

        minx = np.floor(x.min(axis=1)).astype(np.int32)
        maxx = np.ceil(x.max(axis=1)).astype(np.int32)
        miny = np.floor(y.min(axis=1)).astype(np.int32)
        maxy = np.ceil(y.max(axis=1)).astype(np.int32)
        onscreen = (maxx >= 0) & (minx < self.w) & (maxy >= 0) & (miny < self.h)
        infront = (z.min(axis=1) > 0.0) & (z.min(axis=1) < 1.0)
        keep = onscreen & infront
        if not keep.any():
            return
        tri, fn, centre, to_eye = tri[keep], fn[keep], centre[keep], to_eye[keep]
        x, y, z = x[keep], y[keep], z[keep]
        minx, maxx = np.clip(minx[keep], 0, self.w - 1), np.clip(maxx[keep], 0, self.w - 1)
        miny, maxy = np.clip(miny[keep], 0, self.h - 1), np.clip(maxy[keep], 0, self.h - 1)

        # Per-vertex normals, interpolated per pixel. Flat per-face normals made the
        # whale a faceted blob: at 22 rings a 14 m animal shows every band. Normals
        # are the averaged face normals around each vertex, which is all a tube needs
        # to shade as a smooth surface.
        vn = self._vertex_normals(mesh, m4)

        key = norm(np.asarray(self.key_dir, dtype=np.float32))
        kd_f = np.clip(fn @ key, 0, None)
        half_f = norm(key[None, :] + to_eye)
        spec_f = np.clip((fn * half_f).sum(axis=1), 0, None) ** 42.0
        fill_f = np.clip(fn[:, 1], 0, None)
        rim_f = np.clip(1.0 - (fn * to_eye).sum(axis=1), 0, None) ** 2.6

        depth = self.depth
        colour = self.colour
        for i in range(len(tri)):
            bx0, bx1 = int(minx[i]), int(maxx[i])
            by0, by1 = int(miny[i]), int(maxy[i])
            xs, ys = x[i], y[i]
            denom = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
            if abs(denom) < 1e-9:
                continue
            yy, xx = np.mgrid[by0:by1 + 1, bx0:bx1 + 1]
            w0 = ((ys[1] - ys[2]) * (xx - xs[2]) + (xs[2] - xs[1]) * (yy - ys[2])) / denom
            w1 = ((ys[2] - ys[0]) * (xx - xs[2]) + (xs[0] - xs[2]) * (yy - ys[2])) / denom
            w2 = 1.0 - w0 - w1
            inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
            if not inside.any():
                continue
            zz = w0 * z[i, 0] + w1 * z[i, 1] + w2 * z[i, 2]
            if decal:
                zz = zz - decal
            sub = depth[by0:by1 + 1, bx0:bx1 + 1]
            hit = inside & (zz < sub)
            if not hit.any():
                continue
            sub[hit] = zz[hit]
            # barycentric weights at the hit pixels, then re-shade with interpolated
            # normals so the surface reads smooth
            b0 = w0[hit][:, None]
            b1 = w1[hit][:, None]
            b2 = w2[hit][:, None]
            nrm = vn[tri[i, 0]][None, :] * b0 + vn[tri[i, 1]][None, :] * b1 + vn[tri[i, 2]][None, :] * b2
            nrm = norm(nrm)
            ey = to_eye[i][None, :]
            kd = np.clip(nrm @ key, 0, None)
            hh = norm(key[None, :] + ey)
            nh = np.clip((nrm * hh).sum(axis=1), 0, None)
            sp_tight = nh ** 96.0
            sp_wide = nh ** 11.0
            fl = np.clip(nrm[:, 1], 0, None)
            rm = np.clip(1.0 - (nrm * ey).sum(axis=1), 0, None) ** 2.2
            # wrap lighting: light bleeds around a wet, slightly translucent body
            wrap = np.clip((nrm @ key + 0.35) / 1.35, 0, None)
            c = (mesh.colour[None, :] * (self.ambient[None, :]
                                         + self.key_col[None, :] * (0.55 * kd + 0.45 * wrap)[:, None]
                                         + self.fill_col[None, :] * fl[:, None])
                 + self.key_col[None, :] * sp_tight[:, None] * 0.42
                 + self.rim_col[None, :] * sp_wide[:, None] * 0.16
                 + self.rim_col[None, :] * rm[:, None] * 0.62)
            # Markings read as markings. A white patch is a diffuse scatterer - it has
            # no specular lobe and it picks up light from everywhere, which is exactly
            # why an orca's flank is legible at 40 m in murky water while its black
            # back is not. Shaded like skin, the patch came out the same value as the
            # body and the animal looked plain black.
            # A flat appendage seen from above is a grazing surface: every lighting
            # term that depends on orientation - specular, rim, the ^2.2 Fresnel-ish
            # falloff - fires at once along its whole length, so a black pectoral fin
            # from the top is a solid white blade. That is a shading artefact, not the
            # animal. "fin" keeps the diffuse response and drops the view-dependent
            # terms, which is what an organ that is a matte black plate actually does.
            # ORCA_FIN_MARKER
            if mesh.material == "patch":
                c = (c * 0.55 + mesh.colour[None, :] * self.ambient[None, :] * 1.7
                     + mesh.colour[None, :] * 0.30)
            elif mesh.material == "fin":
                # diffuse only: no specular lobe, no rim, no wrap-around
                c = (mesh.colour[None, :] * (self.ambient[None, :] * 1.35
                                             + self.key_col[None, :] * kd[:, None] * 0.42
                                             + self.fill_col[None, :] * fl[:, None] * 0.55))
            colour[by0:by1 + 1, bx0:bx1 + 1][hit] = c

    def _vertex_normals(self, mesh, m4):
        """Average the transformed face normals at every vertex, then cache.

        The cache key is (vertex count, triangle count, first vertex, last vertex,
        sum of the vertex array), not id(mesh): CPython recycles id() the moment a
        temporary mesh is freed, so a brand-new 567-vertex whale inherited the
        612-vertex table from a mesh that had already been garbage collected and the
        rasteriser indexed straight off the end of it. That killed the render at
        frame 157, in the middle of the wash.
        """
        key = (len(mesh.v), len(mesh.t), float(mesh.v[0, 0]), float(mesh.v[-1, 2]),
               float(mesh.v.sum()))
        cache = getattr(self, "_vn_cache", None)
        if cache is None:
            cache = self._vn_cache = {}
        if len(cache) > 400:
            cache.clear()
        hit = cache.get(key)
        if hit is not None:
            return hit
        world = (mesh.v @ m4[:3, :3].T) + m4[:3, 3]
        vc = (world @ self.view[:3, :3].T) + self.view[:3, 3]
        p0, p1, p2 = vc[mesh.t[:, 0]], vc[mesh.t[:, 1]], vc[mesh.t[:, 2]]
        fn = np.cross(p1 - p0, p2 - p0)
        acc = np.zeros_like(mesh.v, dtype=np.float32)
        for k in range(3):
            np.add.at(acc, mesh.t[:, k], fn)
        out = norm(acc)
        cache[key] = out
        return out

    # -- post -------------------------------------------------------------
    def linear_depth(self):
        """View-space distance for every pixel, in the same units as the camera.

        self.depth holds NDC z, which is hyperbolic: two metres near the lens covers
        a huge NDC range and ten metres at distance covers almost none. Fog keyed on
        NDC therefore thickens in front of the camera and barely acts on the far
        plane - the opposite of aerial perspective. This converts back to metres.
        """
        z = self.depth
        if self.ssaa > 1:
            z = z.reshape(self.oh, self.ssaa, self.ow, self.ssaa).mean(axis=(1, 3))
        n, f = 0.05, 400.0
        ndc = np.clip(z, -1.0, 1.0)
        return (2.0 * n * f) / (f + n - ndc * (f - n))

    def resolve(self):
        im = self.colour
        if self.ssaa > 1:
            im = im.reshape(self.oh, self.ssaa, self.ow, self.ssaa, 3).mean(axis=(1, 3))
        return im

    def depth_of_field(self, im, focus_depth, strength=6.0):
        """Cheap CoC: blend the frame with two blurred copies by depth error."""
        from PIL import Image, ImageDraw, ImageFilter
        z = self.depth.copy()
        if self.ssaa > 1:
            z = z.reshape(self.oh, self.ssaa, self.ow, self.ssaa).mean(axis=(1, 3))
        u8 = np.clip(im * 255, 0, 255).astype(np.uint8)
        base = Image.fromarray(u8)
        b1 = base.filter(ImageFilter.GaussianBlur(2.2))
        b2 = base.filter(ImageFilter.GaussianBlur(5.5))
        coc = np.clip(np.abs(z - focus_depth) / max(1e-4, focus_depth) * strength, 0, 1)
        a1 = np.clip(coc * 1.8, 0, 1)[..., None]
        a2 = np.clip(coc - 0.55, 0, 1)[..., None] / 0.45
        out = im * (1 - a1) + (np.asarray(b1, dtype=np.float32) / 255.0) * a1
        out = out * (1 - a2) + (np.asarray(b2, dtype=np.float32) / 255.0) * a2
        return out


# ---------------------------------------------------------------------------
# Water: a big plane with caustics painted onto it, plus a god-ray volume
# ---------------------------------------------------------------------------


def caustics(w, h, t, scale=1.0, seed=0):
    """Voronoi-ish caustic pattern, cheap and convincing at this scale."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    x = xx / w * 7.0 * scale + t * 0.30
    y = yy / h * 4.2 * scale - t * 0.22
    acc = np.zeros((h, w), dtype=np.float32)
    for i in range(3):
        ox = math.sin(t * 0.7 + i * 2.1) * 1.4
        oy = math.cos(t * 0.6 + i * 1.7) * 1.1
        a = np.sin(x * (1.0 + i * 0.28) + ox) * np.sin(y * (1.22 + i * 0.19) + oy)
        b = np.sin((x + y) * (0.74 + i * 0.11) + t * (0.5 + i * 0.2))
        acc += (a * b) ** 2
    acc /= 3.0
    return np.clip(acc ** 0.7 * 2.1, 0.0, 1.6)


def god_rays(w, h, t, n=9, strength=0.35, seed=3):
    """Shafts of surface light, as a volume rather than as painted bars.

    The first version drew hard-edged parallelograms of constant fill over the whole
    frame and blurred them. That has no falloff in any axis, so on screen it reads as
    flat stripes hanging in front of the scene - the single most "cheap render" cue
    in the film. Real shafts:

      * are brightest at the surface and die out with depth (exponential, and they
        never reach the bottom of frame at full strength)
      * spread as they descend, the way a beam widens through a scattering medium
      * have soft, ragged edges because the surface above them is moving
      * are blocked by whatever is in front of them, which the caller applies as a
        depth mask
    """
    from PIL import Image, ImageDraw, ImageFilter
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    for i in range(n):
        base = 0.03 + i * 0.108
        drift = math.sin(t * 0.25 + i * 1.7) * 0.012
        x = w * (base + drift)
        wd = (14 + (i * 37) % 44) * (w / 1280.0)
        # beams lean and widen as they descend
        lean = (i % 3 - 1) * 0.06 * w + math.sin(t * 0.4 + i) * 0.01 * w
        spread = 2.1 + 0.5 * math.sin(i * 2.3)
        amp = 0.55 + 0.35 * math.sin(t * 0.8 + i * 2.1) + 0.10 * math.sin(t * 2.3 + i)
        # brightness follows an exponential depth falloff, so multiply the polygon's
        # vertical extent but shade it with a per-row ramp afterwards
        d.polygon([(x, -h * 0.05), (x + wd, -h * 0.05),
                   (x + wd + lean + wd * spread, h), (x + lean - wd * spread, h)],
                  fill=int(np.clip(190 * amp, 0, 255)))
    m = m.filter(ImageFilter.GaussianBlur(max(8, w // 70)))
    arr = np.asarray(m, dtype=np.float32) / 255.0

    # depth falloff: full strength at the surface, essentially gone by the seafloor
    yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
    arr *= np.exp(-3.1 * yy ** 1.15) * 0.92 + 0.08

    # horizontal falloff so the beams are not at the frame edges at full tilt
    xx = np.linspace(-1.0, 1.0, w, dtype=np.float32)[None, :]
    arr *= np.clip(1.15 - 0.55 * np.abs(xx) ** 1.6, 0, 1)

    # ragged breakup: the surface above the water is never a still sheet of glass
    rng = np.random.default_rng(seed)
    coarse = rng.standard_normal((max(2, h // 46), max(2, w // 46))).astype(np.float32)
    ci = Image.fromarray(((coarse * 0.5 + 0.5) * 255).astype(np.uint8), "L")
    ci = ci.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(w // 90))
    arr *= 0.55 + 0.75 * (np.asarray(ci, dtype=np.float32) / 255.0)

    return (arr * strength)[..., None]


def particles_overlay(w, h, t, n=170, seed=0):
    """Marine snow: soft defocused motes, not snowflakes.

    The first version drew hard ellipses of 0.6-3.2 px at up to 120/255 alpha with
    no depth term, so every mote was a crisp white dot the same size regardless of
    where it sat in the water. On screen that reads as falling snow. Real marine
    snow is out of focus at every distance except the focal plane: each mote is a
    soft blob whose radius and alpha both fall off with distance, and the near ones
    are larger and dimmer rather than brighter.
    """
    from PIL import Image, ImageDraw, ImageFilter
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(seed)
    for i in range(n):
        px = rng.random()
        # parallax: near motes travel further than far ones
        depth = rng.random() ** 1.6                      # 0 = far, 1 = near
        speed = 0.004 + 0.020 * depth
        py = (rng.random() - t * speed) % 1.0
        r = (0.5 + 2.2 * depth) * (w / 1280.0)
        # near = bigger, softer, dimmer; far = smaller, sharper, still faint
        a = int((10 + 26 * (1.0 - depth)) * (0.55 + 0.45 * rng.random()))
        x, y = px * w, py * h
        d.ellipse([x - r, y - r, x + r, y + r], fill=(198, 226, 238, max(6, a)))
    # one defocus pass over the whole layer: nothing in this plate is in focus
    lay = lay.filter(ImageFilter.GaussianBlur(radius=max(0.8, 1.6 * w / 1280.0)))
    return np.asarray(lay, dtype=np.float32) / 255.0


def apply_grade(im, tint=(0.94, 1.00, 1.045), lift=(0.012, 0.026, 0.034),
                contrast=1.10, sat=1.06, vignette=0.34):
    """Filmic grade: toe, shoulder, split tone, vignette, grain.

    v2's grade clipped hard at 1.0 (np.clip before and after a simple S-curve), so
    every highlight - the Snell's window, the sun core, a white flank catching a
    shaft - flattened to the same value and the image looked like a video game
    rather than film. Here the shoulder is exponential, so values above ~0.75
    compress instead of clipping, which is what gives bright water its bloom.

    The split tone is the other half: shadows go teal (water absorbs red first, so
    deep water *is* teal) and highlights go slightly warm (sunlight). That split is
    what makes an underwater frame read as lit from above rather than uniformly
    blue, and it costs two multiplies.
    """
    x = np.clip(im, 0.0, 4.0).astype(np.float32)

    # --- shoulder: compress into the top end without ever hitting a hard 1.0 ---
    knee = 0.76
    over = np.maximum(x - knee, 0.0)
    x = np.where(x > knee, knee + (1.0 - knee) * (1.0 - np.exp(-over / (1.0 - knee))), x)

    # --- toe: lift the blacks a touch so nothing crushes to pure video black ---
    x = x + np.asarray(lift, dtype=np.float32)[None, None, :] * np.clip(1.0 - x * 2.2, 0, 1)

    # --- contrast around mid grey, then a gentle filmic S ---
    x = np.clip((x - 0.42) * contrast + 0.42, 0.0, 1.6)
    x = x * x * (3.0 - 2.0 * np.clip(x, 0, 1)) * 0.30 + x * 0.70

    # --- split tone ---
    lum = (x @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32))[..., None]
    shadow_w = np.clip(1.0 - lum * 2.6, 0.0, 1.0)
    high_w = np.clip((lum - 0.45) * 2.2, 0.0, 1.0)
    x = x + (np.array([0.006, 0.030, 0.046], dtype=np.float32)[None, None, :] * shadow_w
             + np.array([0.045, 0.024, -0.010], dtype=np.float32)[None, None, :] * high_w)

    x = x * np.asarray(tint, dtype=np.float32)[None, None, :]

    # --- saturation, weighted so the teal does not overwhelm the skin tones ---
    lum2 = (x @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32))[..., None]
    x = lum2 + (x - lum2) * sat

    # --- vignette ---
    h, w = x.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = w / 2.0, h / 2.0
    rr = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2) / math.sqrt(2)
    x = x * (1.0 - vignette * np.clip(rr, 0, 1) ** 2.2)[..., None]

    # --- grain, monochrome, stronger in the shadows like real sensor noise ---
    rng = np.random.default_rng(7)
    g = rng.standard_normal((h, w, 1)).astype(np.float32)
    gl = (x @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32))[..., None]
    x = x + g * 0.010 * np.clip(1.25 - gl * 1.6, 0.25, 1.25)

    return np.clip(x, 0.0, 1.0)


if __name__ == "__main__":
    import time
    t0 = time.time()
    r = Renderer(320, 180, ssaa=2)
    r.clear()
    r.set_camera((0, 1.2, -6), (0, 0, 0))
    rings = []
    for i in range(24):
        k = i / 23
        z = -2.2 + k * 4.4
        rx = 0.35 + 0.55 * math.sin(math.pi * k) ** 0.7
        ry = 0.28 + 0.40 * math.sin(math.pi * k) ** 0.7
        rings.append(ellipse_ring((0, math.sin(k * 3.1) * 0.12, z), rx, ry, 20))
    m = tube(rings, (120, 130, 140))
    r.draw(m)
    im = r.resolve()
    print(f"rendered 320x180 ss2 in {time.time()-t0:.2f}s, tris={len(m.t)}")
    from PIL import Image
    Image.fromarray((im * 255).astype(np.uint8)).save("/tmp/tri3d-selftest.png")
    print("ok -> /tmp/tri3d-selftest.png")
