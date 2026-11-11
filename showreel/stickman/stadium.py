"""The stadium: a pitch, four stands, a goal, and the light that makes it read.

Everything here is world geometry projected through the same ``Projector`` the
rig uses, so the hero stands on the pitch rather than in front of a picture of
one. Three conventions make that possible:

**The world is in body units.** One metre is 400 units, because the figure is 700
units tall and 1.75 m. A goal is 7.32 m wide, which is 2928 units, and the
crossbar is 2.44 m, which is 976.

**Depth is metres, converted once.** ``Projector.z`` divides, so a point ``d``
metres from the camera is drawn at ``z = d / D0`` with ``D0 = 14``. The hero's
plane is therefore always ``z = 1`` when the hero is 14 m away -- and when a shot
wants him at 40 m it passes ``z = 40/14`` and he shrinks correctly against a goal
that shrinks a little less.

**The pitch is solved per row, not per polygon.** A floor point's screen row
determines its depth exactly, so the mown stripes, the haze and the floodlight
pool are all functions of one column vector. That is why this painter costs about
a tenth of a second instead of a second: nothing is repeated across the frame.

The one deliberate departure from realism: the pitch is lit and the crowd is dark.
An ink figure is the darkest thing in any frame it appears in, so putting him in
front of a bright pitch and a dark stand is what makes him readable. A
photographically correct night stadium -- crowd lit, pitch dim -- would swallow
him, so the stadium is lit the way a *drawing* of a stadium is lit.
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .stage import Projector

UPERM = 400.0          # world units per metre
D0 = 14.0              # metres at which z = 1


def z_of(metres):
    """Depth ratio for a distance in metres from the camera."""
    return metres / D0


# ------------------------------------------------------------------- palettes

STADIUM_PALETTES = {
    # A floodlit evening, drawn the way a drawing of one is lit: the crowd is the
    # brightest thing in the upper frame and the structure is the darkest. That
    # inversion is not stylisation for its own sake -- an ink figure is the
    # darkest object in any frame it is in, so a dark crowd makes him disappear
    # exactly where the film spends most of its time. A photographically correct
    # stand (dark seats, lit pitch) would swallow him.
    "floodlit": {
        "sky_top": (0.043, 0.059, 0.129),
        "sky_low": (0.176, 0.196, 0.290),
        "glow": (0.968, 0.902, 0.752),
        "pitch_far": (0.396, 0.518, 0.302),
        "pitch_near": (0.588, 0.686, 0.420),
        "stripe": 0.095,
        "line": (0.945, 0.953, 0.906),
        "stand": (0.055, 0.055, 0.078),
        "stand_far": (0.098, 0.098, 0.129),
        "roof": (0.031, 0.031, 0.047),
        "board": (0.184, 0.196, 0.259),
        "crowd": (0.412, 0.373, 0.353),
        "crowd_lit": (0.741, 0.686, 0.616),
        # Keys the shared grade expects. `sun` is the colour of the light that
        # catches an edge, and here that is the floodlight, not a sun.
        "sun": (0.968, 0.902, 0.752),
        "haze": (0.176, 0.196, 0.290),
        "lamp": (1.0, 0.976, 0.902),
        "ink": (0.035, 0.035, 0.047),
    },
    # The silence. Same people, same place; the colour has gone out of the light
    # and the whole ground has dropped a stop. The crowd stays pale on purpose --
    # people do not stop existing when a stadium goes quiet, they stop moving.
    "hush": {
        "sky_top": (0.031, 0.039, 0.086),
        "sky_low": (0.129, 0.145, 0.216),
        "glow": (0.690, 0.706, 0.749),
        "pitch_far": (0.278, 0.349, 0.235),
        "pitch_near": (0.408, 0.478, 0.325),
        "stripe": 0.070,
        "line": (0.729, 0.745, 0.706),
        "stand": (0.043, 0.043, 0.063),
        "stand_far": (0.075, 0.075, 0.102),
        "roof": (0.024, 0.024, 0.039),
        "board": (0.145, 0.157, 0.208),
        "crowd": (0.310, 0.290, 0.290),
        "crowd_lit": (0.576, 0.557, 0.522),
        "sun": (0.690, 0.706, 0.749),
        "haze": (0.129, 0.145, 0.216),
        "lamp": (0.812, 0.804, 0.780),
        "ink": (0.035, 0.035, 0.047),
    },
}


# ------------------------------------------------------------------- geometry

class Stadium:
    """The set. Every number is a fact about a football ground, in metres.

    ``goal_d`` is how far the goal line is from the camera. Everything on the far
    side -- the stands, the pylons -- is placed relative to it, so moving the goal
    moves the whole ground and nothing can end up floating free.
    """

    PITCH_HALF_W = 34.0        # metres from the centre line to a touchline
    GOAL_W = 7.32
    GOAL_H = 2.44
    BOX_D = 16.5               # penalty area depth
    BOX_HALF_W = 20.16
    SIX_D = 5.5
    SIX_HALF_W = 9.16
    PEN_D = 11.0

    def __init__(self, palette="floodlit", *, goal_d=25.0, seed=11,
                 stand_rise=16.0, tiers=26, crowd_gap=0.30,
                 stand_back=70.0, origin_x=0.0, show_goal=True,
                 show_pylons=True):
        self.pal = STADIUM_PALETTES[palette]
        self.name = palette
        self.goal_d = goal_d
        # Lateral placement of the whole ground. The projection has depth and one
        # lateral axis, so the only way to put the goal off to one side of the
        # frame -- rather than directly behind the hero -- is to slide the entire
        # set along x. Shifting the origin moves the goal, the boards, the crowd
        # and the pylons together, so nothing can drift out of register.
        self.origin_x = origin_x
        self.stand_back = stand_back
        # A goal that a shot has framed out of view must be off, not merely off to
        # one side. A 7.32 m goal eleven metres away is wider than the frame, so
        # sliding it sideways just slides its net across the whole picture.
        self.show_goal = show_goal
        self.show_pylons = show_pylons
        self.stand_rise = stand_rise
        self.tiers = tiers
        self.crowd_gap = crowd_gap

        rng = np.random.default_rng(seed)
        self.rng = rng

        # The crowd is a fixed point cloud in world units, generated once. It is
        # not re-randomised per frame -- a stand that flickers is the single most
        # obvious tell that a background is procedural.
        self.crowd = self._make_crowd(rng)
        # A fixed per-spectator jitter, applied only when the crowd is churning.
        # Freezing it is how the film shows silence: the sound stops and the stand
        # becomes a photograph, which no amount of dimming achieves.
        self.churn_jitter = rng.normal(0.0, 1.0, (len(self.crowd[0]), 2))
        # Advertising boards run along the back of the goal at a fixed depth.
        self.boards = self._make_boards(rng)

    # -- depth helpers ------------------------------------------------------

    def set_palette(self, name):
        """Swap the light without rebuilding the geometry or the crowd."""
        self.pal = STADIUM_PALETTES[name]
        self.name = name

    def z_stand(self):
        return z_of(self.goal_d + self.stand_back)

    def z_boards(self):
        return z_of(self.goal_d + 12.0)

    def z_goal(self):
        return z_of(self.goal_d)

    # -- crowd --------------------------------------------------------------

    def _make_crowd(self, rng):
        """(x, y, tier) for every spectator, in world units.

        Rows are stacked up the stand. Each tier is slightly further back as well
        as higher, which is what a raked stand is -- and it means the tiers
        separate properly when the camera moves instead of sliding as one slab.
        """
        pts = []
        span = (self.PITCH_HALF_W + 22.0) * UPERM
        n_x = int(2.0 * span / (self.crowd_gap * UPERM))
        for t in range(self.tiers):
            rise = self.stand_rise * (t + 0.55) / self.tiers
            # Uniform random, not a lattice. A stand is packed people, and a fixed
            # pitch with a jitter is still a lattice -- it reads as an LED matrix
            # at the exact distance where the crowd matters most.
            xs = rng.uniform(-span, span, n_x)
            # World y is negative upward. Getting this sign wrong put the entire
            # crowd underground, where it projected onto the pitch as a field of
            # evenly spaced dots -- which is exactly what a mis-signed crowd looks
            # like, and almost plausible enough to miss.
            ys = np.full(n_x, -rise * UPERM) + rng.uniform(-0.16, 0.16, n_x) * UPERM
            pts.append(np.stack([xs, ys], axis=1))
        arr = np.concatenate(pts, axis=0)
        # A per-spectator brightness band: three values, so the stand has texture
        # rather than a uniform stipple.
        band = rng.integers(0, 3, len(arr))
        return arr, band

    def _make_boards(self, rng):
        """Positions and lengths of the advertising boards behind the goal."""
        out = []
        x = -(self.PITCH_HALF_W + 6.0) * UPERM
        end = (self.PITCH_HALF_W + 6.0) * UPERM
        while x < end:
            w = rng.uniform(4.0, 8.0) * UPERM
            out.append((x, x + w))
            x += w
        return out


# ---------------------------------------------------------------------- paint

def _rows_and_depth(proj):
    """Screen row -> depth, for the floor plane. Only valid below the horizon."""
    rows = np.arange(proj.H, dtype=np.float32) + 0.5
    hz = np.float32(proj.H * 0.5 + proj.tilt * proj.H)
    A = proj.cam_y + proj.eye * proj.H
    denom = rows - hz
    with np.errstate(divide="ignore", invalid="ignore"):
        z = A * proj.zoom / denom
    z = np.where(denom > 1e-6, z, np.inf)
    return rows, hz, z


def paint(stad, proj, *, churn=0.0, wobble=0.0):
    """Paint the whole ground for one camera. Returns float RGB (H, W, 3)."""
    if stad.origin_x:
        # Sliding the set is exactly the same operation as sliding the camera the
        # other way, so it is done here once rather than at forty call sites.
        shifted = Projector(proj.W, proj.H, cam_x=proj.cam_x - stad.origin_x,
                            cam_y=proj.cam_y, eye=proj.eye, zoom=proj.zoom,
                            tilt=proj.tilt)
        proj = shifted
    W, H = proj.W, proj.H
    pal = stad.pal
    rows, hz, z_row = _rows_and_depth(proj)
    cols = np.arange(W, dtype=np.float32) + 0.5

    # ---- sky ------------------------------------------------------------
    top = np.array(pal["sky_top"], np.float32)
    low = np.array(pal["sky_low"], np.float32)
    u = np.clip(rows / max(hz, 1.0), 0.0, 1.0)[:, None] ** 0.85
    sky = top[None, :] + (low - top)[None, :] * u
    frame = np.repeat(sky[:, None, :], W, axis=1)

    # ---- pitch ----------------------------------------------------------
    # Below the horizon every row has one depth, so the stripes are a function of
    # the row and the whole plane costs one vector op.
    zb = np.where(np.isfinite(z_row), z_row, 1e9)[:, None]
    t = np.clip((zb - 0.35) / 6.0, 0.0, 1.0) ** 0.55
    near = np.array(pal["pitch_near"], np.float32)[None, :]
    far = np.array(pal["pitch_far"], np.float32)[None, :]
    pitch = far + (near - far) * t

    # Mown stripes, keyed to depth in metres so they run across the pitch.
    metres = zb * D0
    period = 5.6
    phase = (metres / period) % 2.0
    stripe = np.where(phase < 1.0, 1.0, 1.0 - pal["stripe"])
    # Fade the stripes out at distance: they alias into noise long before the
    # horizon otherwise.
    fade = np.clip((metres - 30.0) / 40.0, 0.0, 1.0)
    stripe = 1.0 + (stripe - 1.0) * (1.0 - fade)
    pitch = pitch * stripe

    # Floodlight pool: brighter near the goal mouth, falling off at the edges.
    # `metres` is already a column (H, 1); adding another axis here turns the
    # multiply into (H, 3) * (H, 1, 1), which broadcasts to an (H, H, 3) frame.
    pool = np.clip(1.0 - ((metres - 26.0) / 46.0) ** 2, 0.0, 1.0)
    pitch = pitch * (0.86 + 0.26 * pool)

    # Aerial perspective on the grass: distance washes toward the haze.
    haze_c = np.array(pal["sky_low"], np.float32)[None, :]
    haze = np.clip((metres - 24.0) / 70.0, 0.0, 1.0) * 0.55
    pitch = pitch * (1.0 - haze) + haze_c * haze

    ground = np.repeat(pitch[:, None, :], W, axis=1)
    frame = np.where((rows >= hz)[:, None, None], ground, frame)

    # ---- markings -------------------------------------------------------
    frame = _markings(frame, stad, proj, cols, rows, z_row, hz)

    # ---- stands, boards, goal ------------------------------------------
    # Far to near, so each object occludes what is behind it.
    # Painter's order is depth order, back to front: pylons, the stand, the people
    # in it, the boards, and the goal. Any other order lets a far object show
    # through the gaps in a near one -- the first version drew the goal behind the
    # crowd, and the net hung in the air among the spectators.
    if stad.show_pylons:
        frame = _pylons(frame, stad, proj, cols, rows)
    frame = _stand_back(frame, stad, proj, cols, rows)
    frame = _crowd(frame, stad, proj, churn=churn)
    frame = _boards(frame, stad, proj, cols, rows)
    if stad.show_goal:
        frame = _goal(frame, stad, proj, cols, rows, wobble=wobble)

    # The light pool. Floodlights are over the pitch, so the stand falls off
    # toward the corners of the frame. This is a lighting decision that happens to
    # be a legibility decision: the part of the stand the figure stands in front of
    # is the part that is lit, and the rest of it stops competing with him.
    above = rows[:, None] < hz
    fal = 1.0 - 0.62 * np.clip(np.abs(cols[None, :] - W * 0.5) / (W * 0.58),
                               0.0, 1.0) ** 1.5
    frame = np.where(above[:, :, None], frame * fal[:, :, None], frame)

    return frame


def _seg_mask(rows, cols, p0, p1, z, proj, width_px):
    """A thick screen-space segment into a boolean mask (rows, cols)."""
    x0, y0 = float(p0[0]), float(p0[1])
    x1, y1 = float(p1[0]), float(p1[1])
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    if L2 < 1e-9:
        return np.zeros((len(rows), len(cols)), bool)
    X = cols[None, :] - x0
    Y = rows[:, None] - y0
    tt = np.clip((X * dx + Y * dy) / L2, 0.0, 1.0)
    ddx = X - tt * dx
    ddy = Y - tt * dy
    return (ddx * ddx + ddy * ddy) <= (width_px * 0.5) ** 2


def _markings(frame, stad, proj, cols, rows, z_row, hz):
    """White paint on the grass, drawn as screen-space bands.

    Lines are constant-width in the world, so their screen width shrinks with
    depth; that is handled by scaling the band by ``1/z``. Everything else is a
    screen-space mask, which is cheap and exact because the camera is level.
    """
    W, H = proj.W, proj.H
    line = np.array(stad.pal["line"], np.float32)
    ink = np.array(stad.pal["ink"], np.float32)
    zg = stad.z_goal()

    def blend(mask, colour, alpha=1.0):
        nonlocal frame
        # In-place: `frame = frame*(1-a) + c*a` allocates two full frames per
        # call and this is called thirteen times. `frame += (c - frame) * a`
        # allocates one, and is the same arithmetic.
        a = mask[:, :, None].astype(np.float32) * np.float32(alpha)
        frame += (colour[None, None, :] - frame) * a

    # -- lines that run across the pitch ---------------------------------
    # A depth line is horizontal on screen, so it is a band of rows. Solving the
    # band in *rows* rather than in metres matters: at 50 m, one metre of depth is
    # about two rows, so a 0.16 m wide line lands between rows and disappears. An
    # earlier version did exactly that and drew a pitch with no markings at all.
    for d_m in (0.0, stad.SIX_D, stad.BOX_D, 52.5):
        dist = stad.goal_d + d_m
        r0 = float(proj.sy(0.0, z_of(dist)))
        r1 = float(proj.sy(0.0, z_of(dist + 0.25)))
        thick = max(1.5, abs(r1 - r0))
        m = (np.abs(rows[:, None] - r0) <= thick) & (rows > hz)[:, None]
        blend(m, line, 0.82)

    # -- lines that run along the pitch (constant world x): converge
    for wx, thick in ((0.0, 0.16),
                      (stad.BOX_HALF_W * UPERM, 0.16),
                      (-stad.BOX_HALF_W * UPERM, 0.16),
                      (stad.SIX_HALF_W * UPERM, 0.16),
                      (-stad.SIX_HALF_W * UPERM, 0.16),
                      (stad.PITCH_HALF_W * UPERM, 0.20),
                      (-stad.PITCH_HALF_W * UPERM, 0.20)):
        zz = np.maximum(z_row, 1e-3)[:, None]
        sx = W * 0.5 + (wx - proj.cam_x) * proj.zoom / zz
        half = (thick * UPERM * 0.5) * proj.zoom / zz
        m = (np.abs(cols[None, :] - sx) <= np.maximum(half, 0.7))
        # Only where the pitch exists: between the goal line and the halfway.
        # Every term here is already a (H, 1) column. Indexing one of them with
        # [:, None] a second time makes it (H, 1, 1), and the `&` then broadcasts
        # to (H, W, W) -- 2 GB for one boolean mask.
        m = m & ((z_row * D0)[:, None] < 53.0) & (rows > hz)[:, None] \
            & ((z_row * D0)[:, None] > stad.goal_d - 0.4)
        blend(m, line, 0.80)

    # -- penalty spot
    zs = z_of(stad.goal_d + stad.PEN_D)
    sp = proj.point((0.0, 0.0), zs)
    r = max(1.2, 0.16 * UPERM * 0.5 * proj.zoom / zs)
    m = ((cols[None, :] - sp[0]) ** 2 + (rows[:, None] - sp[1]) ** 2) <= r * r
    blend(m, line, 0.90)

    # -- the mouth of the goal, in shadow on the grass
    zg_ = zg
    y0 = float(proj.sy(0.0, zg_))
    x0 = float(proj.sx(-stad.GOAL_W * 0.5 * UPERM, zg_))
    x1 = float(proj.sx(stad.GOAL_W * 0.5 * UPERM, zg_))
    band = (np.abs(rows - y0) < 3.0)[:, None] & (cols[None, :] > x0) & (cols[None, :] < x1)
    blend(band, ink, 0.22)
    return frame


def _stand_back(frame, stad, proj, cols, rows):
    """The far stand: one dark mass rising above the horizon, with a lit roof.

    Not a box in 3D -- the stand is far enough away that its silhouette is the
    only thing that reads, so it is authored as a silhouette: a curved top edge,
    a vertical face, and a roof band. The crowd dots are placed on it afterwards.
    """
    W, H = proj.W, proj.H
    pal = stad.pal
    z = stad.z_stand()
    base = float(proj.sy(0.0, z))
    rise = stad.stand_rise * UPERM
    top = float(proj.sy(-rise, z))

    # The top edge bows up slightly toward the middle of the ground, which is
    # what a curved stand looks like from pitch level.
    x_mid = float(proj.sx(0.0, z))
    half = W * 0.5 * z / proj.zoom
    u = np.clip((cols - x_mid) / max(half, 1.0), -1.0, 1.0)
    bow = (1.0 - u * u) * (rise * 0.05 * proj.zoom / z)
    top_edge = top + bow

    body = (rows[:, None] >= top_edge[None, :]) & (rows[:, None] <= base)
    stand = np.array(pal["stand"], np.float32)
    far = np.array(pal["stand_far"], np.float32)
    # Lighter at the top where the floodlights graze it.
    v = np.clip((rows - top) / max(base - top, 1.0), 0.0, 1.0)[:, None, None]
    col = far[None, None, :] * (1.0 - v) + stand[None, None, :] * v
    frame = np.where(body[:, :, None], col, frame)

    # Tier edges: the horizontal lip of each row of seats, plus a soft shadow
    # under it. Both are full-width horizontal bands, so they are accumulated as
    # one column vector and applied once. Doing it per tier -- 26 comparisons and
    # 26 full-frame multiplies -- was two thirds of this function's cost and
    # produced exactly the same picture.
    lip = max(1.0, (rise * 0.004) * proj.zoom / z)
    lip_w = np.zeros((len(rows), 1), np.float32)
    for t in range(stad.tiers):
        wy = -(stad.stand_rise * (t + 0.55) / stad.tiers) * UPERM
        r = float(proj.sy(wy, z))
        d = rows - r
        lip_w[:, 0] += np.where(np.abs(d) < lip, 0.55, 0.0)
        lip_w[:, 0] += np.where((d > 0) & (d < lip * 5.0), 0.22, 0.0)
    lip_w = np.clip(lip_w, 0.0, 0.80)
    frame = frame * (1.0 - lip_w[:, :, None] * body[:, :1, None].astype(np.float32))

    # Roof: a hard band along the top edge.
    roof_t = max(2.0, (rise * 0.030) * proj.zoom / z)
    roof = (rows[:, None] >= top_edge[None, :] - roof_t) & \
           (rows[:, None] <= top_edge[None, :])
    frame = np.where(roof[:, :, None], np.array(pal["roof"], np.float32)[None, None, :],
                     frame)
    return frame


def _boards(frame, stad, proj, cols, rows):
    """Advertising boards at the back of the goal, as one lit band."""
    W = proj.W
    pal = stad.pal
    z = stad.z_boards()
    y0 = float(proj.sy(-1.1 * UPERM, z))
    y1 = float(proj.sy(0.0, z))
    band = ((rows[:, None] >= y0) & (rows[:, None] <= y1)).astype(np.float32)
    frame += (np.array(pal["board"], np.float32)[None, None, :] - frame) * band[:, :, None]
    # Vertical seams every few metres: a lit board is a row of panels, and a band
    # without seams reads as a letterbox bar pasted over the pitch.
    z0 = z
    for a, b in stad.boards:
        gx = float(proj.sx(a, z0))
        col = (np.abs(cols[None, :] - gx) < 1.2) & \
              (rows[:, None] >= y0) & (rows[:, None] <= y1)
        frame *= (1.0 - 0.45 * col[:, :, None].astype(np.float32))

    # A single bright line along the top edge sells them as lit panels.
    edge = ((rows[:, None] >= y0) & (rows[:, None] <= y0 + 1.6)).astype(np.float32)
    lit = np.array(pal["crowd_lit"], np.float32)[None, None, :] * 1.25
    frame += (lit - frame) * edge[:, :, None]
    return frame


def _goal(frame, stad, proj, cols, rows, *, wobble=0.0):
    """The goal: two posts, a crossbar, and a net drawn as a sparse lattice.

    The net is a line grid in *world* space on the goal plane, so its cells get
    smaller toward the far post and the whole thing has real perspective. A
    screen-space grid would be half the cost and would look printed on.
    """
    pal = stad.pal
    z = stad.z_goal()
    ink = np.array(pal["ink"], np.float32)
    hw = stad.GOAL_W * 0.5 * UPERM
    h = stad.GOAL_H * UPERM
    post_w = max(1.6, 0.12 * UPERM * proj.zoom / z)

    # The net is a real object and it moves when something hits it. `wobble` is
    # the displacement in world units, applied to the *net only* -- the frame and
    # the posts do not move, which is what makes it read as fabric rather than as
    # the whole goal shaking.
    p_bl = proj.point((-hw, 0.0), z)
    p_br = proj.point((hw, 0.0), z)
    p_tl = proj.point((-hw, -h), z)
    p_tr = proj.point((hw, -h), z)

    m = np.zeros((len(rows), len(cols)), bool)
    for a, b in ((p_bl, p_tl), (p_br, p_tr), (p_tl, p_tr)):
        m |= _seg_mask(rows, cols, a, b, z, proj, post_w * 1.35)

    a = m[:, :, None].astype(np.float32)
    frame = frame * (1.0 - a) + ink[None, None, :] * a

    # -- net: verticals and horizontals on the goal plane, thin and pale.
    # Every strand is either a constant world x (a column on screen) or a constant
    # world y (a row), because the goal plane is a plane of constant depth. So the
    # whole net is a set of 1-D bands and costs two comparisons per strand instead
    # of six full-frame arrays.
    net = np.zeros((len(rows), len(cols)), bool)
    x0s = float(p_bl[0])
    x1s = float(p_br[0])
    ytop = float(p_tl[1])
    ybot = float(p_bl[1])
    n_v = int(stad.GOAL_W / 0.22)
    n_h = int(stad.GOAL_H / 0.22)
    if x1s > x0s:
        for i in range(1, n_v):
            gx = x0s + (x1s - x0s) * i / n_v
            net |= (np.abs(cols[None, :] - gx) < 0.9) & \
                   (rows[:, None] >= ytop) & (rows[:, None] <= ybot)
    if ybot > ytop:
        for j in range(1, n_h):
            gy = ytop + (ybot - ytop) * j / n_h
            net |= (np.abs(rows[:, None] - gy) < 0.9) & \
                   (cols[None, :] >= x0s) & (cols[None, :] <= x1s)

    na = net[:, :, None].astype(np.float32) * np.float32(0.22)
    frame = frame * (1.0 - na) + np.array(pal["line"], np.float32)[None, None, :] * na

    # The goal mouth is darker than the pitch behind it: the net shades it.
    mouth = (rows[:, None] >= p_tl[1]) & (rows[:, None] <= p_bl[1]) & \
            (cols[None, :] >= p_bl[0]) & (cols[None, :] <= p_br[0])
    frame *= (1.0 - np.float32(0.26) * mouth[:, :, None].astype(np.float32))
    return frame


def _crowd(frame, stad, proj, *, churn=0.0):
    """Project every spectator once and draw the ones inside the frame.

    Drawn as a raster pass rather than a loop of rectangles because the count is
    what sells it: a stand with 300 marks reads as empty, and one with 2,500
    reads as a crowd. The projection is one vector op; only the marks are looped.
    """
    W, H = proj.W, proj.H
    pts, band = stad.crowd
    if churn > 0.0:
        # A moving crowd: each spectator drifts a fraction of a metre. Amplitude
        # is deliberately below the spacing, or the stand turns into boiling noise
        # instead of people shifting their weight.
        pts = pts + stad.churn_jitter * (churn * 0.16 * UPERM)
    z = stad.z_stand()
    sx = W * 0.5 + (pts[:, 0] - proj.cam_x) * proj.zoom / z
    sy = proj.H * 0.5 + (pts[:, 1] + proj.cam_y + proj.eye * proj.H) * proj.zoom / z \
        + proj.tilt * proj.H
    keep = (sx > -6) & (sx < W + 6) & (sy > -6) & (sy < H + 6)
    if not np.any(keep):
        return frame

    sx, sy, band = sx[keep], sy[keep], band[keep]
    # A mark is a head and a pair of shoulders, sized by the projection: 14 cm
    # wide and 46 cm tall in world units. Getting this wrong is what makes a
    # stadium look like a blackboard covered in chalk dust -- at 78 m a seated
    # spectator is about 22 px tall on screen, not three.
    # A seated spectator is a head and a pair of shoulders: about 40 cm across and
    # 50 cm tall. Drawn taller than wide they read as falling rain, which is what
    # the first version of this looked like.
    r = max(1.0, 0.135 * UPERM * proj.zoom / z)
    h = max(2.0, 0.34 * UPERM * proj.zoom / z)

    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    order = np.argsort(band)
    # Three passes, dimmest first, so a lighter spectator can sit in front of a
    # darker neighbour the way a lit face does in a real stand.
    for b, val in ((0, 150), (1, 205), (2, 255)):
        sel = order[band[order] == b]
        for i in sel:
            cx, cy = sx[i], sy[i]
            d.ellipse([cx - r, cy - h * 0.5, cx + r, cy + h * 0.5], fill=val)

    a = np.asarray(mask, np.float32)[:, :, None] / 255.0
    base = np.array(stad.pal["crowd"], np.float32)[None, None, :]
    lit = np.array(stad.pal["crowd_lit"], np.float32)[None, None, :]
    col = base * (1.0 - a * 0.55) + lit * (a * 0.55)
    return frame * (1.0 - a * 0.85) + col * (a * 0.85)


def _pylons(frame, stad, proj, cols, rows):
    """Two floodlight masts behind the stand, plus the glow they throw.

    The masts are placed just past the back of the stand and tall enough to clear
    it, so their heads are in the sky above the roof line. That is the whole
    reason they work: they are the only thing in the frame that says *night
    match*, and they say it with a silhouette against the sky.
    """
    W, H = proj.W, proj.H
    pal = stad.pal
    z = stad.z_stand() * 1.22
    m_top = (stad.stand_rise + 13.0) * UPERM
    heads = []
    # Narrow enough to sit inside a vertical frame. A real pylon is at the corner
    # of the ground, which is outside a 9:16 crop at this distance -- so the two
    # that flank the goal are the ones the shot can actually see.
    for wx in (-13.0, 13.0):
        base_x = wx * UPERM
        p0 = proj.point((base_x, 0.0), z)
        p1 = proj.point((base_x, -m_top), z)
        if p0[0] < -30 or p0[0] > W + 30:
            continue
        w = max(2.0, 0.55 * UPERM * proj.zoom / z * 0.40)
        m = _seg_mask(rows, cols, p0, p1, z, proj, w)
        a = m[:, :, None].astype(np.float32) * 0.95
        frame = frame * (1.0 - a) + np.array(pal["ink"], np.float32)[None, None, :] * a
        heads.append((p1, w))

    if not heads:
        return frame

    lamp = np.array(pal["lamp"], np.float32)
    glow = Image.new("L", (W, H), 0)
    hard = Image.new("L", (W, H), 0)
    dg = ImageDraw.Draw(glow)
    dh = ImageDraw.Draw(hard)
    for (hx, hy), w in heads:
        bw = max(11.0, w * 9.0)
        bh = max(7.0, w * 4.0)
        box = [hx - bw, hy - bh, hx + bw, hy + bh]
        dg.rectangle(box, fill=255)
        dh.rectangle(box, fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(max(6.0, 34.0 * proj.zoom)))
    g = np.asarray(glow, np.float32)[:, :, None] / np.float32(255.0)
    hm = np.asarray(hard, np.float32)[:, :, None] / np.float32(255.0)

    frame = frame * (1.0 - g * 0.42) + lamp[None, None, :] * (g * 0.42)
    frame = frame * (1.0 - hm * 0.96) + lamp[None, None, :] * (hm * 0.96)
    return frame


# ------------------------------------------------------------------- overlays

def tunnel(frame, proj, *, openness=1.0):
    """The tunnel mouth, as a foreground matte over the finished stadium.

    A tunnel shot is not a different set. It is the same ground seen through a
    corridor, so the matte sits in front of the pitch and the stands and simply
    uncovers them as it opens -- which is what walking out of a tunnel does. The
    alternative, a separate "tunnel room" scene, would cut rather than open, and
    a cut loses the one thing the shot is for: the moment the noise arrives.
    """
    H, W = frame.shape[:2]
    open_ = 0.0 if openness < 0.0 else 1.0 if openness > 1.0 else openness
    if open_ >= 0.995:
        return frame

    yy = np.arange(H, dtype=np.float32)[:, None]
    xx = np.arange(W, dtype=np.float32)[None, :]
    cx = W * 0.5

    # The aperture: a slit that grows into the mouth of the tunnel.
    half_w = W * (0.040 + 0.90 * open_)
    top = H * (0.70 - 0.78 * open_)
    u = np.clip((xx - cx) / half_w, -1.0, 1.0)
    arch = top + (1.0 - np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))) * half_w * 0.50
    inside = (yy > arch) & (np.abs(xx - cx) < half_w)

    a = inside.astype(np.float32)
    # Feather by a pixel and a half so the aperture is not a vector cut-out.
    m = Image.fromarray((a * 255).astype(np.uint8), "L")
    m = m.filter(ImageFilter.GaussianBlur(1.6))
    a = np.asarray(m, np.float32)[:, :, None] / np.float32(255.0)

    # The wall: a corridor, darker at the frame edge and near-black at the
    # corners, lit only by what spills out of the opening.
    dist_from_axis = np.abs(xx - cx) / max(half_w, 1.0)
    spill = np.clip(1.0 - dist_from_axis * 0.62, 0.0, 1.0)
    spill = spill * np.clip((yy - top) / max(H - top, 1.0), 0.0, 1.0) ** 0.5
    wall_in = np.array([0.145, 0.141, 0.176], np.float32)[None, None, :]
    wall_out = np.array([0.020, 0.020, 0.031], np.float32)[None, None, :]
    wall = wall_out + (wall_in - wall_out) * spill[:, :, None] * (1.0 - open_ * 0.35)

    return frame * a + wall * (1.0 - a)
