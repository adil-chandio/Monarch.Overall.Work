#!/usr/bin/env python3
"""Deterministic helpers for the Monarch night-temple film build.

Everything here is a pure, measurable pixel operation: frame retiming,
flicker correction, global stabilisation, exposure matching, grading and
face/eye localisation. None of it invents detail or motion. These helpers fix
*engineering* defects only (judder, flicker, shake, exposure jumps, softness);
they cannot fix identity drift, bad anatomy, wrong likeness or weak acting.

Conventions: frames are BGR uint8 arrays, shape (h, w, 3). Times are seconds at
the film frame rate. Every helper is unit-tested in test_research_tools.py.
"""
from __future__ import annotations

import numpy as np

try:  # OpenCV is optional for the pure-maths tests
    import cv2
except Exception:  # pragma: no cover
    cv2 = None


# --------------------------------------------------------------------------- #
# retiming
# --------------------------------------------------------------------------- #
def retime_indices(out_frames: int, src_frames: int) -> np.ndarray:
    """Pick `out_frames` strictly increasing source indices.

    Frames are only ever *dropped*, never duplicated and never invented: a
    duplicated frame is visible judder at 24 fps, and an invented (interpolated)
    frame is the ghosting the earlier review cuts were rejected for. Therefore
    an output that needs more frames than the source has is an error, not
    something to pad.
    """
    if out_frames < 1 or src_frames < 1:
        raise ValueError('frame counts must be positive')
    if out_frames > src_frames:
        raise ValueError(f'cannot produce {out_frames} unique frames from {src_frames}')
    idx = np.floor(np.arange(out_frames, dtype=np.float64) * src_frames / out_frames)
    idx = idx.astype(np.int32)
    if out_frames > 1:
        if np.any(np.diff(idx) < 1):                     # defensive: must strictly grow
            raise ValueError('retime produced a repeated frame')
    return np.minimum(idx, src_frames - 1)


def playback_speed(out_frames: int, src_frames: int) -> float:
    """Effective playback rate when `src_frames` are fitted into `out_frames`."""
    if out_frames < 1:
        raise ValueError('out_frames must be positive')
    return float(src_frames) / float(out_frames)


# --------------------------------------------------------------------------- #
# flicker / exposure
# --------------------------------------------------------------------------- #
def deflicker_gains(means: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """Per-frame multiplicative gains that flatten slow luma drift.

    A 5-tap median kills single-frame flicker; the result is blended with the
    original curve by `strength` so intended fades are not erased.
    """
    if strength < 0 or strength > 1:
        raise ValueError('strength must be inside [0,1]')
    m = np.asarray(means, dtype=np.float64)
    if m.ndim != 1 or m.size == 0:
        raise ValueError('means must be a non-empty 1-D array')
    if m.size < 5:
        target = np.full_like(m, m.mean())
    else:
        padded = np.pad(m, 2, mode='edge')
        target = np.array([np.median(padded[i:i + 5]) for i in range(m.size)])
    curve = m * (1 - strength) + target * strength
    curve = np.maximum(curve, 1e-3)
    return float(curve.mean()) / curve


def match_luma(frame: np.ndarray, gain: float, limit: float = 1.35) -> np.ndarray:
    """Apply a server-side gain, clamped so a dark shot cannot be blown out."""
    if not np.isfinite(gain) or gain <= 0:
        raise ValueError('gain must be finite and positive')
    g = float(np.clip(gain, 1.0 / limit, limit))
    out = frame.astype(np.float32) * g
    return np.clip(out, 0, 255).astype(np.uint8)


# --------------------------------------------------------------------------- #
# stabilisation (removes measured jitter, keeps intended travel)
# --------------------------------------------------------------------------- #
def smooth_path(values: np.ndarray, sigma: float) -> np.ndarray:
    """Gaussian smooth a 1-D path (used to separate travel from jitter)."""
    if sigma <= 0:
        return np.asarray(values, dtype=np.float64).copy()
    v = np.asarray(values, dtype=np.float64)
    radius = max(1, int(round(sigma * 3)))
    x = np.arange(-radius, radius + 1)
    k = np.exp(-(x ** 2) / (2 * sigma ** 2))
    k /= k.sum()
    return np.convolve(np.pad(v, radius, mode='edge'), k, mode='valid')


def stabilise_residuals(shifts: np.ndarray, sigma: float = 2.5) -> np.ndarray:
    """Return the jitter component of a global-shift track.

    `shifts` is (n, 2) of per-frame displacement in pixels. The returned array
    is the high-frequency part to be cancelled.
    """
    s = np.asarray(shifts, dtype=np.float64)
    if s.ndim != 2 or s.shape[1] != 2:
        raise ValueError('shifts must be (n, 2)')
    resid = np.empty_like(s)
    for axis in range(2):
        resid[:, axis] = s[:, axis] - smooth_path(s[:, axis], sigma)
    return resid


def jitter_rms(shifts: np.ndarray, sigma: float = 2.5) -> float:
    """Root-mean-square jitter magnitude in pixels — the honest shake metric."""
    r = stabilise_residuals(shifts, sigma)
    return float(np.sqrt((r ** 2).sum(1).mean()))


def best_translation(a: np.ndarray, b: np.ndarray, radius: int = 12):
    """Integer (dx, dy) that best aligns `a` onto `b` inside +/-radius.

    A brute-force search on the phase-correlation surface is used because its
    peak is unambiguous for sub-pixel-accurate integer shifts, which is what
    stabilisation needs. Returns (dx, dy, confidence) in pixels.
    """
    if cv2 is None:
        raise RuntimeError('OpenCV required for best_translation')
    fa = np.float32(a)
    fb = np.float32(b)
    fa = fa - fa.mean()
    fb = fb - fb.mean()
    win = cv2.createHanningWindow((fa.shape[1], fa.shape[0]), cv2.CV_32F)
    (dx, dy), response = cv2.phaseCorrelate(fa * win, fb * win)
    return float(dx), float(dy), float(response)


def track_shifts(gray_frames, work_width: int = 512, radius: int = 10) -> np.ndarray:
    """Cumulative global translation track of a shot, in source pixels.

    Each consecutive pair is aligned by normalised cross-correlation of the
    previous frame's central patch (verified sub-pixel), which is exact for the
    rigid camera shake and slow travel this film has. The cumulative path is
    mean-centred so stabilisation does not drift.
    """
    if cv2 is None:
        raise RuntimeError('OpenCV required for track_shifts')
    scale = work_width / float(gray_frames[0].shape[1])
    small = [cv2.resize(g, (work_width, max(2, int(round(g.shape[0] * scale)))))
             for g in gray_frames]
    h, w = small[0].shape[:2]
    pad = radius + 2
    out = [(0.0, 0.0)]
    for prev, cur in zip(small, small[1:]):
        # template = interior of the previous frame, searched inside the current one
        tmpl = prev[pad:h - pad, pad:w - pad]
        win = cur[2:min(h, h - 0), 2:min(w, w - 0)]
        res = cv2.matchTemplate(win, tmpl, cv2.TM_CCOEFF_NORMED)
        _, _, _, maxloc = cv2.minMaxLoc(res)
        # maxloc is where the template's top-left landed, relative to (2,2)
        dx = maxloc[0] + 2 - pad
        dy = maxloc[1] + 2 - pad
        out.append((-dx / scale, -dy / scale))
    cum = np.cumsum(np.array(out, dtype=np.float64), axis=0)
    cum -= cum.mean(axis=0)
    return cum


# --------------------------------------------------------------------------- #
# camera move + grade
# --------------------------------------------------------------------------- #
def camera_matrix(progress: float, zoom_from: float, zoom_to: float,
                  pan_x: float = 0.0, pan_y: float = 0.0,
                  width: int = 1280, height: int = 720) -> np.ndarray:
    """Affine matrix for a smooth push-in/pan, in source-pixel space."""
    if not 0.0 <= progress <= 1.0:
        raise ValueError('progress must be inside [0,1]')
    e = progress * progress * (3 - 2 * progress)  # smoothstep: no velocity snaps
    zoom = 1.0 + (zoom_to - zoom_from) * e
    zoom = max(zoom, 0.2)
    cx, cy = width / 2.0, height / 2.0
    # pan_x/pan_y are fractions of frame size; convert to the translation part
    tx = pan_x * e * width
    ty = pan_y * e * height
    return np.array([[zoom, 0.0, cx - zoom * cx + tx],
                     [0.0, zoom, cy - zoom * cy + ty]], dtype=np.float32)


def grade_frame(frame: np.ndarray, grain: float = 0.0, vignette: float = 0.0,
                teal: float = 0.0, contrast: float = 1.0,
                black_point: float = 0.0, seed: int = 0) -> np.ndarray:
    """Cinematic night grade: black lift, teal shadows, vignette, film grain.

    Parameters are bounded so a typo cannot silently wreck the image.
    """
    for name, value, lo, hi in (('grain', grain, 0, 12), ('vignette', vignette, 0, .45),
                                ('teal', teal, -0.35, 0.35), ('contrast', contrast, .5, 1.6),
                                ('black_point', black_point, 0, 40)):
        if not lo <= value <= hi:
            raise ValueError(f'{name} must be inside [{lo}, {hi}]')
    img = frame.astype(np.float32)
    if contrast != 1.0:
        img = (img - 127.5) * contrast + 127.5
    img -= black_point
    if teal:
        # push blue/green into shadows, protect highlights
        lum = img.mean(axis=2, keepdims=True) / 255.0
        shadow = np.clip(1.0 - lum * 1.9, 0, 1)[:, :, 0]
        img[:, :, 0] += teal * 255 * shadow * 0.85   # blue
        img[:, :, 1] += teal * 255 * shadow * 0.45   # green
        img[:, :, 2] -= teal * 255 * shadow * 0.30   # red
    if vignette:
        h, w = img.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
        falloff = 1.0 - vignette * np.clip((r - 0.45) / 0.85, 0, 1) ** 1.6
        img *= falloff[:, :, None]
    if grain:
        rng = np.random.default_rng(seed)
        img += rng.normal(0.0, grain, img.shape[:2])[:, :, None]
    return np.clip(img, 0, 255).astype(np.uint8)


# --------------------------------------------------------------------------- #
# subject localisation for the close-up eye glow
# --------------------------------------------------------------------------- #
_CASCADES = {}


def _cascade(name):
    global _CASCADES
    if cv2 is None:
        raise RuntimeError('OpenCV required for cascades')
    if name not in _CASCADES:
        _CASCADES[name] = cv2.CascadeClassifier(cv2.data.haarcascades + name)
    return _CASCADES[name]


def face_box(frame: np.ndarray, min_size: int = 80):
    """Largest frontal face box (x, y, w, h) in source pixels, or None."""
    g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    g = cv2.equalizeHist(g)
    boxes = _cascade('haarcascade_frontalface_default.xml').detectMultiScale(
        g, 1.08, 5, minSize=(min_size, min_size))
    if len(boxes) == 0:
        return None
    x, y, w, h = max(boxes, key=lambda b: b[2] * b[3])
    return (x / 2.0, y / 2.0, w / 2.0, h / 2.0)


def _dark_blob_score(gray: np.ndarray, cx: int, cy: int, radius: int = 2) -> float:
    """How much darker a small disk is than the ring around it (eye-socket score)."""
    h, w = gray.shape
    r_in, r_out = radius, radius * 2 + 2
    y0, y1 = max(cy - r_out, 0), min(cy + r_out + 1, h)
    x0, x1 = max(cx - r_out, 0), min(cx + r_out + 1, w)
    patch = gray[y0:y1, x0:x1]
    if patch.size == 0:
        return -1e9
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d2 = (yy - cy) ** 2 + (xx - cx) ** 2
    inner = d2 <= r_in ** 2
    ring = (d2 > r_in ** 2) & (d2 <= r_out ** 2)
    if inner.sum() < 2 or ring.sum() < 4:
        return -1e9
    return float(patch[ring].mean() - patch[inner].mean())


def eye_points(frame: np.ndarray, box, band: float = 0.18):
    """Locate the two iris centres inside a face box, with a symmetry prior.

    Each eye half is scanned for the pixel whose small dark disk contrasts most
    with its surrounding ring, but only in narrowed windows and with a hard
    pair constraint (same height, plausible separation). If no confident pair
    exists the function returns None, so the caller disables the effect instead
    of drawing light on the wrong feature.
    """
    if box is None:
        return None
    x, y, w, h = [float(v) for v in box]
    x, y = max(x, 0.0), max(y, 0.0)
    if w < 48 or h < 48:
        return None
    gx0, gy0 = int(round(x)), int(round(y))
    gw = min(int(round(w)), frame.shape[1] - gx0)
    gh = min(int(round(h)), frame.shape[0] - gy0)
    if gw < 48 or gh < 48:
        return None
    roi = frame[gy0:gy0 + gh, gx0:gx0 + gw]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY).astype(np.float32)
    y_lo = int(gh * 0.30)
    y_hi = int(gh * 0.30 + gh * band)
    radius = max(2, gw // 26)
    halves = ((int(gw * 0.24), int(gw * 0.47)),
              (int(gw * 0.53), int(gw * 0.76)))
    candidates = []
    for x_lo, x_hi in halves:
        scored = []
        for cy in range(max(y_lo, radius * 3), min(y_hi, gh - radius * 3)):
            for cx in range(max(x_lo, radius * 3), min(x_hi, gw - radius * 3)):
                scored.append((_dark_blob_score(gray, cx, cy, radius), cx, cy))
        scored.sort(reverse=True)
        candidates.append(scored[:40])            # keep the best few per eye
    # anatomical priors: iris spacing is ~0.32 of face width, eyes sit level
    target_sep = 0.32 * gw
    best = None
    for s1, x1, y1 in candidates[0]:
        for s2, x2, y2 in candidates[1]:
            sep = x2 - x1
            if not (0.22 * gw <= sep <= 0.46 * gw):
                continue
            if abs(y1 - y2) > 0.06 * gh:
                continue
            penalty = (abs(sep - target_sep) / gw) * 55.0
            penalty += (abs(y1 - y2) / gh) * 40.0
            score = s1 + s2 - penalty
            if best is None or score > best[0]:
                best = (score, (x1, y1), (x2, y2))
    if best is None or min(best[0] / 2.0, 99) < 1.2:
        return None
    p1 = (gx0 + best[1][0], gy0 + best[1][1])
    p2 = (gx0 + best[2][0], gy0 + best[2][1])
    return [p1, p2]


def track_pair(frames, seed_index: int, points, patch: int = 7, search: int = 5,
               min_score: float = 0.52):
    """Follow two small eye patches through a shot with template matching.

    Anchoring the whole shot to one verified pair removes per-frame landmark
    jitter and stops the glow from sliding onto the nose or brow. Frames whose
    match is weak are returned as None so `smooth_points` can bridge them.
    """
    if points is None or len(points) != 2:
        return [None] * len(frames)
    seq = [None] * len(frames)
    for start, step, stop in ((seed_index, -1, -1), (seed_index, 1, len(frames))):
        pos = [tuple(map(float, p)) for p in points]
        prev_gray = cv2.cvtColor(frames[seed_index], cv2.COLOR_BGR2GRAY)
        idx = start
        while idx != stop:
            cur_gray = cv2.cvtColor(frames[idx], cv2.COLOR_BGR2GRAY)
            out = []
            for (px, py) in pos:
                cx, cy = int(round(px)), int(round(py))
                if (cx - patch < 0 or cy - patch < 0 or cx + patch + 1 > prev_gray.shape[1]
                        or cy + patch + 1 > prev_gray.shape[0]):
                    out.append(None); continue
                tmpl = prev_gray[cy - patch:cy + patch + 1, cx - patch:cx + patch + 1]
                x0, y0 = max(cx - search - patch, 0), max(cy - search - patch, 0)
                x1 = min(cx + search + patch + 1, cur_gray.shape[1])
                y1 = min(cy + search + patch + 1, cur_gray.shape[0])
                win = cur_gray[y0:y1, x0:x1]
                if win.shape[0] < tmpl.shape[0] or win.shape[1] < tmpl.shape[1]:
                    out.append(None); continue
                res = cv2.matchTemplate(win, tmpl, cv2.TM_CCOEFF_NORMED)
                _, maxv, _, maxloc = cv2.minMaxLoc(res)
                if maxv < min_score:
                    out.append(None); continue
                out.append((x0 + maxloc[0] + patch, y0 + maxloc[1] + patch))
            seq[idx] = out if all(o is not None for o in out) else None
            if seq[idx] is not None:
                pos = [tuple(map(float, o)) for o in seq[idx]]
            idx += step
            prev_gray = cur_gray
    return seq


def seed_eyes(frames, max_probe: int = 60):
    """Find one frame whose eye pair is confidently verified, for tracking."""
    order = list(range(len(frames)))
    if len(order) > max_probe:
        # probe the second half first: he faces camera by then
        order = order[len(order) // 3:]
        order = order[:max_probe]
    for i in order:
        box = face_box(frames[i])
        pts = eye_points(frames[i], box)
        if pts is not None:
            return i, pts
    return None, None


def brighten_eyes(frame: np.ndarray, points, strength: float,
                  radius_scale: float = 1.0) -> np.ndarray:
    """Add controlled red wound-light to two tracked iris points.

    The light has three parts so it reads as emission rather than a sticker: a
    small hot core (near-white red), a saturated iris ring, and a wide bloom
    that also tints the surrounding skin.
    """
    if not 0.0 <= strength <= 1.0:
        raise ValueError('strength must be inside [0,1]')
    if points is None or strength <= 0 or len(points) != 2:
        return frame
    h, w = frame.shape[:2]
    k = max(0.6, radius_scale)
    core = np.zeros((h, w), np.float32)
    iris = np.zeros((h, w), np.float32)
    for px, py in points:
        c = (int(round(px)), int(round(py)))
        cv2.circle(iris, c, max(2, int(round(2.4 * k))), 1.0, -1, cv2.LINE_AA)
        cv2.circle(core, c, max(1, int(round(1.0 * k))), 1.0, -1, cv2.LINE_AA)
    core_b = cv2.GaussianBlur(core, (0, 0), 0.55 * k)
    iris_b = cv2.GaussianBlur(iris, (0, 0), 1.1 * k)
    bloom = cv2.GaussianBlur(iris_b, (0, 0), 5.5 * k)
    spill = cv2.GaussianBlur(iris_b, (0, 0), 13.0 * k)
    s = strength
    out = frame.astype(np.float32)
    out[:, :, 2] += s * (core_b * 255 + iris_b * 205 + bloom * 120 + spill * 26)   # red
    out[:, :, 1] += s * (core_b * 150 + iris_b * 26 + bloom * 16)                  # green
    out[:, :, 0] += s * (core_b * 120 + bloom * 30)                                # blue
    return np.clip(out, 0, 255).astype(np.uint8)


def smooth_points(sequence, window: int = 5):
    """Median-then-EMA smoothing of a tracked point sequence; rejects gaps."""
    valid = [p for p in sequence if p is not None]
    if not valid:
        return [None] * len(sequence)
    out, prev = [], None
    for i, p in enumerate(sequence):
        if p is None:
            out.append(prev)
            continue
        lo = max(0, i - window // 2)
        near = [q for q in sequence[lo:i + window // 2 + 1] if q is not None]
        cand = []
        for side in (0, 1):
            xs = sorted(q[side][0] for q in near)
            ys = sorted(q[side][1] for q in near)
            cand.append((xs[len(xs) // 2], ys[len(ys) // 2]))
        if prev is None:
            prev = cand
        else:
            prev = [((0.62 * a[0] + 0.38 * b[0]), (0.62 * a[1] + 0.38 * b[1]))
                    for a, b in zip(cand, prev)]
        out.append(prev)
    return out


# --------------------------------------------------------------------------- #
# higher-resolution pass
# --------------------------------------------------------------------------- #
class SuperRes:
    """ESPCN 2x upsampler (a real learned network, tiny and CPU-viable)."""

    def __init__(self, model_path: str):
        if cv2 is None:
            raise RuntimeError('OpenCV required')
        self.sr = cv2.dnn_superres.DnnSuperResImpl_create()
        self.sr.readModel(str(model_path))
        self.sr.setModel('espcn', 2)

    def __call__(self, frame: np.ndarray) -> np.ndarray:
        return self.sr.upsample(frame)


def detail_gain(before: np.ndarray, after: np.ndarray) -> float:
    """Ratio of high-frequency energy after/before an upscale (softness metric)."""
    def hf(img):
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        return float(cv2.Laplacian(g, cv2.CV_32F).var())
    a = hf(after)
    b = hf(before)
    return float(a / b) if b > 0 else float('nan')
