"""Camera, world and backdrop -- one projection for everything.

Two earlier attempts got this wrong in opposite directions. First the backdrop was
one bitmap that the figure walked off the end of. Then it was a stack of bands
placed by hand, which meant the figure's feet and the horizon were only related
by luck.

So there is exactly one transform here. World space is the character's plane:
y = 0 is the floor, y is negative upward, and distances are in frame pixels at
zoom 1. A point at depth ``z`` (1.0 = the character's plane, larger = further)
projects as

    screen_x = W/2 + (world_x - cam_x) * scale / z
    screen_y = H*0.30 + tilt ... (see Projector)

with ``scale = zoom``. The floor, the ridges, the sun and the figure are the same
equation at different depths, so when the camera pushes in everything separates
at its own rate -- which is the actual definition of parallax, rather than an
effect that is faked per layer.

The horizon is not a composition choice. It is where the floor at infinite depth
projects, which is the camera's eye line. Putting the eye line low in the world
and tilting the frame down is what gets a high horizon while keeping the figure
full height in a 9:16 frame.
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw

# ------------------------------------------------------------------ palettes

PALETTES = {
    # Warm paper, vermillion sun, warm greys: three values and one accent, so the
    # ink figure is always the darkest thing on screen.
    "paper": {
        "sky_top": (0.980, 0.965, 0.935),
        "sky_low": (0.912, 0.863, 0.788),
        "sun": (0.878, 0.298, 0.145),
        "ridges": [(0.796, 0.757, 0.690), (0.561, 0.522, 0.467),
                   (0.318, 0.290, 0.267)],
        "ground_far": (0.890, 0.851, 0.780),
        "ground_near": (0.812, 0.759, 0.671),
        "mark": (0.700, 0.643, 0.545),
        "ink": (0.078, 0.074, 0.090),
        "accent": (0.878, 0.298, 0.145),
        "haze": (0.980, 0.953, 0.912),
    },
    "night": {
        "sky_top": (0.027, 0.038, 0.086),
        "sky_low": (0.117, 0.129, 0.208),
        "sun": (0.906, 0.878, 0.796),
        "ridges": [(0.184, 0.200, 0.290), (0.106, 0.122, 0.200),
                   (0.051, 0.059, 0.114)],
        "ground_far": (0.125, 0.141, 0.216),
        "ground_near": (0.063, 0.075, 0.133),
        "mark": (0.153, 0.173, 0.255),
        "ink": (0.016, 0.018, 0.031),
        "accent": (0.949, 0.443, 0.208),
        "haze": (0.161, 0.176, 0.263),
    },
}


# ----------------------------------------------------------------- the camera

class Projector:
    """World -> screen. One equation, used by the backdrop and the figure alike.

    ``eye`` is the camera's height above the floor (positive up), in the same
    pixels as the figure. ``tilt`` shifts the whole frame vertically, which is
    the difference between a camera pointed at the horizon and one pointed down
    at the ground. ``zoom`` scales about the frame centre; because the projection
    divides by depth, scaling every world offset by zoom and dividing by depth is
    identical to moving the lens, so a push-in gets real parallax for free.
    """

    def __init__(self, width, height, *, cam_x=0.0, cam_y=0.0, eye=0.30,
                 zoom=1.0, tilt=0.0):
        self.W = width
        self.H = height
        self.cam_x = cam_x
        # Vertical follow, in world units: lifting the camera raises the frame's
        # centre, which is what lets a shot track a jump instead of losing it.
        self.cam_y = cam_y
        self.eye = eye          # fraction of frame height
        self.zoom = zoom
        self.tilt = tilt        # fraction of frame height

    # -- scalar convenience -------------------------------------------------

    @property
    def horizon(self):
        """Screen row of the floor at infinite depth: the eye line, tilted."""
        return self.H * 0.5 + self.tilt * self.H

    def feet(self):
        """Screen row of a floor point at the character's own depth.

        The eye sits above the floor, so the floor at the character's depth
        projects *below* the frame centre by exactly the eye height.
        """
        return self.H * 0.5 + (self.eye * self.H) * self.zoom + self.tilt * self.H

    def ground_scale(self):
        """Pixels per world unit at depth 1."""
        return self.zoom

    # -- projection ---------------------------------------------------------

    def sx(self, world_x, z=1.0):
        return self.W * 0.5 + (np.asarray(world_x, float) - self.cam_x) * self.zoom / z

    def sy(self, world_y, z=1.0):
        # The lens sits at world y = -(cam_y + eye*H), so a point's height above
        # the lens is world_y + cam_y + eye*H. Raising the camera therefore pushes
        # the whole world *down* the frame, which is what lets a shot follow a
        # jump upward instead of losing the figure off the top.
        return (self.H * 0.5 + (np.asarray(world_y, float) + self.cam_y
                                + self.eye * self.H)
                * self.zoom / z + self.tilt * self.H)

    def point(self, world_xy, z=1.0):
        wx, wy = world_xy
        return np.array([self.sx(wx, z), self.sy(wy, z)])

    def depth_range(self, z):
        """World-x range that projects into the frame at depth z."""
        half = self.W * 0.5 * z / self.zoom
        return self.cam_x - half, self.cam_x + half


# ------------------------------------------------------------------- backdrop

class World:
    """Backdrop geometry. Every number here is a world-space fact."""

    def __init__(self, palette="paper", *, seed=5,
                 sun_at=(0.775, 0.150), sun_r=0.072, sun_parallax=0.035,
                 ridge_depths=(26.0, 11.0, 4.6),
                 ridge_heights=(0.104, 0.070, 0.044),
                 gaps=()):
        self.pal = PALETTES[palette]
        self.name = palette
        # The sun is a body at effectively infinite depth, so it is defined where
        # it sits in the composition and how much it drifts with the camera --
        # which is what parallax actually means for something that far away.
        self.sun_at = sun_at            # fraction of (width, height)
        self.sun_r = sun_r              # fraction of frame width
        self.sun_parallax = sun_parallax
        self.ridge_depths = ridge_depths
        # Screen height of each ridge at its own depth, as a fraction of frame
        # height. Converting to world is done in ridge_y so the silhouette keeps
        # the size it was composed at no matter what depth it is placed at.
        self.ridge_heights = ridge_heights

        rng = np.random.default_rng(seed)
        self.phases = [rng.uniform(0.0, 2.0 * math.pi, 3) for _ in range(3)]
        # Frequencies in world units: a hill is a few hundred pixels wide.
        self.freqs = [(0.00042, 0.00113, 0.00271),
                      (0.00058, 0.00151, 0.00364),
                      (0.00079, 0.00207, 0.00498)]
        self.amps = [(0.60, 0.28, 0.12), (0.64, 0.30, 0.13), (0.68, 0.32, 0.14)]
        # A gap is a real hole in the floor, not a painted shadow: a list of
        # (x0, x1, depth) in world units. Everything that depends on standing on
        # the ground -- the floor fill, the floor marks, the cast shadow, the
        # dust -- has to agree about where the ground stops, or the figure walks
        # across a hole it should have fallen into.
        self.gaps = list(gaps)

    # -- ground queries -----------------------------------------------------

    def is_solid(self, x):
        """Is there floor at this world x?"""
        for x0, x1, _ in self.gaps:
            if x0 <= x <= x1:
                return False
        return True

    def in_gap(self, x, margin=0.0):
        for x0, x1, _ in self.gaps:
            if x0 - margin <= x <= x1 + margin:
                return True
        return False

    def gap_edges_near(self, x):
        """The nearest solid edge to the left and right of x, if inside a gap."""
        for x0, x1, _ in self.gaps:
            if x0 <= x <= x1:
                return x0, x1
        return None

    # -- geometry -----------------------------------------------------------

    def ridge_y(self, layer, world_x, frame_h):
        """World y of a ridge top at its own depth. Negative is up.

        The profile is authored as a screen-space silhouette and converted to
        world height through the depth it will be drawn at, so ``governing`` the
        composition is enough to place a ridge -- there is no second number to
        keep in sync.
        """
        f = self.freqs[layer]
        a = self.amps[layer]
        p = self.phases[layer]
        wx = np.asarray(world_x, dtype=np.float64)
        s = (a[0] * np.sin(wx * f[0] + p[0])
             + a[1] * np.sin(wx * f[1] + p[1])
             + a[2] * np.sin(wx * f[2] + p[2]))
        screen_h = self.ridge_heights[layer] * frame_h
        world_h = screen_h * self.ridge_depths[layer]
        # abs() so ridges only ever rise above the horizon, never dip below it.
        return -abs(s) * world_h

    def sun_world(self, frame_w, frame_h, z=1.0):
        """Sun position in world units at a nominal depth, for projection."""
        return ((self.sun_at[0] - 0.5) * frame_w * z,
                -(self.sun_at[1] - 0.5) * frame_h * z)


# ----------------------------------------------------------------- the paint

def paint(world, proj):
    """Paint the backdrop for one projector state, as float RGB (H, W, 3)."""
    W, H = proj.W, proj.H
    pal = world.pal
    hz = proj.horizon
    hz = float(np.clip(hz, 1.0, H - 1.0))

    rows = np.arange(H, dtype=np.float32)[:, None]

    # --- sky: a gradient that meets the horizon
    top = np.array(pal["sky_top"], np.float32)
    low = np.array(pal["sky_low"], np.float32)
    u = np.clip(rows / hz, 0.0, 1.0) ** 0.86
    sky = top[None, None, :] + (low - top)[None, None, :] * u[:, :, None]
    frame = np.repeat(sky, W, axis=1)

    # --- floor: one plane, so colour depends only on the row
    gfar = np.array(pal["ground_far"], np.float32)
    gnear = np.array(pal["ground_near"], np.float32)
    v = np.clip((rows - hz) / max(H - hz, 1.0), 0.0, 1.0) ** 0.62
    floor = gfar[None, None, :] + (gnear - gfar)[None, None, :] * v[:, :, None]
    frame = np.where((rows >= hz)[..., None], np.repeat(floor, W, axis=1), frame)

    # --- sun, a flat printed disc, projected like everything else
    img = Image.fromarray(np.clip(frame * 255.0, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    # The sun is placed directly in the frame and drifts with a fixed parallax
    # rate: at its distance, that is the only visible consequence of a camera
    # move, and it keeps the disc the size it was composed at.
    sx = world.sun_at[0] * W - proj.cam_x * world.sun_parallax * proj.zoom
    sy = world.sun_at[1] * H - (proj.tilt - 0.06) * H * 0.6
    sr = world.sun_r * W * proj.zoom
    if -sr * 2 < sx < W + sr * 2 and -sr * 2 < sy < H + sr * 2:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                  fill=tuple(int(255 * q) for q in pal["sun"]))
    frame = np.asarray(img, dtype=np.float32) / 255.0

    # --- floor marks, laid on the plane at world-uniform depth
    frame = _floor_marks(frame, world, proj, hz)

    # --- ridges, far to near, with aerial perspective.
    #
    # Each ridge stands on the ground at its own depth, so its foot projects
    # below the horizon. Painting it from crest to foot is correct; painting it
    # to the horizon would erase every ridge nearer than infinity. The reason
    # the first version read as floating stripes is that all three were the same
    # saturation -- a hill sixteen times further away is not that colour, it is
    # most of the way to the sky.
    cols = np.arange(W, dtype=np.float32) + 0.5
    rows2 = np.arange(H, dtype=np.float32)[:, None]
    for layer in (0, 1, 2):
        z = world.ridge_depths[layer]
        lo, hi = proj.depth_range(z)
        wx = lo + (hi - lo) * (cols / W)
        prof = world.ridge_y(layer, wx, H)
        screen = proj.sy(prof, z)
        base = float(proj.sy(0.0, z))
        mask = (rows2 >= screen[None, :]) & (rows2 <= base + 0.5)

        # Haze toward the sky colour, more of it the further the ridge is.
        haze = float(np.clip((z / 2.2) ** 0.85 * 0.42, 0.0, 0.88))
        sky_col_t = (top + (low - top) * np.clip(rows2 / max(hz, 1.0), 0, 1) ** 0.86)
        sky_here = np.repeat(sky_col_t[:, None, :], W, axis=1)
        ridge_col = (np.array(pal["ridges"][layer], np.float32)[None, None, :]
                     * (1.0 - haze) + sky_here * haze)
        frame = np.where(mask[..., None], ridge_col, frame)

    # The gap goes on last. A hole is nearer to the camera than anything behind
    # it, so painting it before the ridges leaves the hills showing through the
    # void -- which is exactly what happened the first time.
    if world.gaps:
        frame = _paint_gaps(frame, world, proj, pal, hz)

    return frame


def _paint_gaps(frame, world, proj, pal, hz):
    """Cut the floor open and draw what is inside the cut.

    For each gap: the far wall (seen above the far lip, lit from the sky), the
    void itself (nearly black, because almost no light reaches it), and the
    near wall just below the near lip. The lips get a highlight, which is what
    tells the eye that the floor has an edge rather than a shadow.
    """
    Hh, Ww = frame.shape[:2]
    rows = np.arange(Hh, dtype=np.float32)[:, None]
    floor_row = float(proj.sy(0.0))

    for x0, x1, depth in world.gaps:
        sx0 = float(proj.sx(x0))
        sx1 = float(proj.sx(x1))
        if sx1 < -400 or sx0 > Ww + 400:
            continue
        left = int(max(0, min(Ww, sx0)))
        right = int(max(0, min(Ww, sx1)))
        if right <= left:
            continue

        # How deep the hole projects.
        #
        # The camera looks down into a cut whose floor is below and behind the
        # near lip, so the visible void is a wedge: its top edge is the far lip
        # (further away, therefore higher on screen), its bottom edge is the near
        # lip, and the far wall narrows toward the bottom because the wall's base
        # is further away than its rim. Filling a plain rectangle here is what
        # makes a chasm look like a grey box.
        far_y = float(proj.sy(-depth))
        near_y = float(proj.sy(0.0))

        # The far wall's base sits at the same world depth as its rim, but the
        # floor of the cut is further back, so it foreshortens inward.
        base = float(proj.sy(-depth * 1.9))
        top = min(far_y, near_y)
        bot = max(far_y, near_y)
        if bot - top < 2:
            continue

        # Inset at the far lip, as a fraction of the gap's width. A deeper point
        # projects smaller, so the far lip -- which is at depth z, not 1 -- is
        # narrower on screen than the near lip. Narrow at the top, wide at the
        # bottom: that trapezoid is the whole read of a hole in a floor.
        inset = 0.30
        cols_idx = np.arange(left, right, dtype=np.float64)
        u = (cols_idx - left) / max(right - left, 1)

        # The lip is broken, not cut: a small world-space jitter, fixed per x so
        # it does not crawl, makes the edge read as ground that fell away.
        jitter = (proj.cam_x * 0.0)  # keeps the world stable under the camera
        for y in range(max(0, int(round(top))), min(Hh, int(round(bot)))):
            # How far down the void this row is, 0 at the far lip.
            k = (y - top) / max(bot - top, 1.0)
            a = left + inset * (right - left) * (1.0 - k) * 0.5
            b = right - inset * (right - left) * (1.0 - k) * 0.5
            a, b = int(round(a)), int(round(b))
            if b <= a:
                continue
            # Lit at the rim, falling to almost nothing at the base of the wall.
            lit = np.clip(np.array(pal["ridges"][0], np.float32) * 0.66, 0, 1)
            dark = np.array([0.040, 0.034, 0.040], np.float32)
            col = np.asarray(lit, np.float32) + (
                np.asarray(dark, np.float32) - np.asarray(lit, np.float32)) * float(
                max(0.0, k) ** 0.55)

            # Striations: the far wall is rock, and flat gradients read as
            # printed shading. A few vertical ribs, spacing fixed in world units
            # so they scale with the camera like everything else, are enough to
            # suggest strata without turning into noise.
            band = ((np.arange(a, b) + proj.cam_x * 0.35) // 26).astype(np.int64)
            rib = (np.sin(band * 2.4) * 0.5 + 0.5) * 0.10
            col = col * (1.0 - rib[:, None])
            frame[y, a:b] = col

        # Lip highlights: a thin line along each edge, brighter on the near one
        # because it faces the light.
        # Broken lips. The near and far edges are nibbled in world space, with
        # the notch depth varying along the gap, so the opening reads as ground
        # that collapsed rather than a rectangle cut with a knife.
        for lip_y, sign in ((far_y, -1), (near_y, +1)):
            yy = int(round(lip_y))
            idx = np.arange(left, right)
            wx_here = proj.cam_x + (idx - Ww * 0.5) / proj.zoom
            notch = (np.sin(wx_here * 0.021) * 3.4
                     + np.sin(wx_here * 0.057 + 1.7) * 1.6).astype(np.int32)
            for j, xcol in enumerate(idx):
                y0 = yy + sign * int(notch[j])
                y1 = yy
                if y0 > y1:
                    y0, y1 = y1, y0
                if 0 <= y0 < Hh and y1 < Hh:
                    frame[y0:max(y1, y0 + 1), xcol] = np.array(
                        pal["ground_far"], np.float32) * 1.02

        # Lip highlights: the near lip is the one facing the camera and the
        # light, so it gets a crisp bright edge; the far lip gets a dimmer one
        # because it is seen almost edge-on.
        lip_bright = np.clip(np.array(pal["ground_far"], np.float32) * 1.12, 0, 1)
        lip_dim = np.clip(np.array(pal["ground_far"], np.float32) * 0.80, 0, 1)

    return frame


def _floor_marks(frame, world, proj, hz):
    """Marks lying on the floor plane, spaced uniformly in world depth.

    Uniform world spacing projects to geometrically shrinking rows, which is the
    cue that makes a floor read as a plane. Each row is drawn at its projected
    height, its own scale, and its own weight.
    """
    pal = world.pal
    W, H = proj.W, proj.H
    img = Image.fromarray((np.clip(frame, 0, 1) * 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img, "RGBA")

    depth = 1.04
    for _ in range(26):
        sy = float(proj.sy(0.0, depth))
        if sy > H + 40:
            break
        if sy > hz + 2 and 0 < sy:
            s = proj.zoom / depth
            sp = 300.0 * s
            if sp > 2.5:
                ln = max(2.0, 46.0 * s)
                th = max(1, int(round(3.4 * s)))
                alpha = int(np.clip(40 + 1200.0 / depth ** 2.0, 26, 235))
                colour = tuple(int(255 * q) for q in pal["mark"]) + (alpha,)
                ox = (-proj.cam_x * s) % sp
                x = -sp + ox
                while x < W + sp:
                    # Skip marks that fall in the hole: a floor mark floating in
                    # mid-air over a chasm is the most obvious tell there is.
                    wx = proj.cam_x + (x - W * 0.5) * depth / proj.zoom
                    if world.is_solid(wx):
                        d.line([x - ln * 0.5, sy, x + ln * 0.5, sy],
                               fill=colour, width=th)
                    x += sp
        depth *= 1.26

    return np.asarray(img, dtype=np.float32) / 255.0
