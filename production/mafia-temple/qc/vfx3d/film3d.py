#!/usr/bin/env python3
"""Render MONARCH — night temple, the 3D/VFX edition.

This replaces photographed/generated plates with actual rendered geometry: the
temple, gate, lanterns, ground and the figure are solids intersected by camera
rays; the page (camera) and the performance (skeleton) change per frame; light,
fog, rain and bloom are computed, not overlaid.

Honest scope
------------
* 1 unit = 1 m, 24 fps, 1280x720, 480 frames = 20.000 s.
* The figure is a stylised low-poly capsule character with procedural gait. It
  is NOT a likeness of any real person, and it is not a finished character: no
  skin shading, no cloth sim, no facial rig.
* The architecture is blocky by design (boxes/slabs). It reads as a temple, not
  as a photoreal set.
* No image files are read as plates. Every pixel comes from this renderer.

Usage:
  python qc/vfx3d/film3d.py --out render-3d/monarch-temple-3d.mp4 \
      --width 1280 --height 720 --samples 1
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))       # so `import vfx3d` works
sys.path.insert(0, str(HERE))

from vfx3d import geom, scene, render  # noqa: E402
from vfx3d.scene import Light  # noqa: E402

FPS = 24
W_DEFAULT, H_DEFAULT = 1280, 720

AMBIENT = np.array([0.030, 0.042, 0.068], np.float32)
FOG_TINT = np.array([0.020, 0.028, 0.048], np.float32)


# --------------------------------------------------------------------- shots
class Shot:
    """A camera move plus what happens in front of it."""

    def __init__(self, name, frames, cam_from, cam_to, target_from, target_to,
                 fov=50.0, figure=None, rain=0.5, fog=0.030, exposure=1.15,
                 eye_glow=0.0, god_rays=0.22, bloom=0.6, notes='',
                 fit=None, fit_dir=(0.0, 0.0, 1.0), fit_fill=0.72,
                 fit_slide=0.0, fit_look=0.0):
        self.name = name
        self.frames = frames
        self.cam_from = np.asarray(cam_from, float)
        self.cam_to = np.asarray(cam_to, float)
        self.tgt_from = np.asarray(target_from, float)
        self.tgt_to = np.asarray(target_to, float)
        self.fov = fov
        self.figure = figure or {}
        self.rain = rain
        self.fog = fog
        self.exposure = exposure
        self.eye_glow = eye_glow
        self.god_rays = god_rays
        self.bloom = bloom
        self.notes = notes
        self.fit = fit                 # (lo, hi) world AABB to keep in frame
        self.fit_dir = np.asarray(fit_dir, float)
        self.fit_fill = fit_fill
        self.fit_slide = fit_slide
        self.fit_look = fit_look


def ease(t):
    return t * t * (3 - 2 * t)


def smooth(t):
    """C1 ease with a touch of hold at both ends."""
    t = min(max(t, 0.0), 1.0)
    return t * t * t * (t * (t * 6 - 15) + 10)


def camera_basis(eye, target):
    """right / up / forward for a look-at camera, matching geom.camera_rays."""
    fwd = np.asarray(target, float) - np.asarray(eye, float)
    fwd /= max(np.linalg.norm(fwd), 1e-9)
    world_up = np.array([0.0, 1.0, 0.0])
    if abs(fwd @ world_up) > 0.995:
        world_up = np.array([0.0, 0.0, 1.0])
    right = np.cross(fwd, world_up)
    right /= max(np.linalg.norm(right), 1e-9)
    up = np.cross(right, fwd)
    return right, up, fwd


def fit_distance(lo, hi, fov_deg, aspect, direction, fill=0.72, push=0.0):
    """Exact distance for a world AABB to fill `fill` of the frame.

    Projects all eight corners into the camera frame for a candidate distance
    and solves the constraint directly (|lateral| <= tan(half_fov) * depth).
    A bounding-sphere fit would leave a tall gate marooned in the middle of the
    picture; this one fills the frame the way a storyboard frame wants.
    """
    lo, hi = np.asarray(lo, float), np.asarray(hi, float)
    centre = (lo + hi) * 0.5
    d = np.asarray(direction, float)
    d /= max(np.linalg.norm(d), 1e-9)
    right, up, fwd = camera_basis(centre + d * 10.0, centre)

    corners = np.array([[x, y, z] for x in (lo[0], hi[0])
                        for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    rel = corners - centre
    a = rel @ right          # horizontal offset in the view plane
    b = rel @ up             # vertical offset
    z = rel @ d              # how far in front of the centre (toward the camera)

    ty = math.tan(math.radians(fov_deg) * 0.5)
    tan_h = ty * aspect * fill
    tan_v = ty * fill
    # depth of a corner = distance - z, so distance >= z + |lateral| / tan
    need = np.maximum(np.abs(a) / tan_h, np.abs(b) / tan_v) + z
    dist = float(np.max(need))
    return max(dist, 0.5) * (1.0 + push)


SHOTS = [
    # Framing solved numerically: every landmark below was projected through the
    # camera before the shot was accepted (see NOTES-3D.md, projection table).
    Shot('S1-gate', 96,
         cam_from=(2.2, 2.55, 12.6), cam_to=(1.2, 2.05, 9.6),
         target_from=(-0.3, 2.90, 4.0), target_to=(-0.2, 2.70, 4.0),
         fov=42, rain=0.85, fog=0.034, exposure=1.10, god_rays=0.30,
         figure=dict(root=(-1.4, 6.6), walk=+1.0, yaw=math.pi),
         notes='the approach: torii on the left third, hall behind, figure '
               'walking away from lens at 7 m'),
    Shot('S2-under-gate', 121,
         cam_from=(1.5, 1.78, 9.4), cam_to=(0.35, 1.74, 5.2),
         target_from=(-0.4, 2.55, 3.0), target_to=(0.0, 2.45, -1.0),
         fov=44, rain=0.55, fog=0.030, exposure=1.12, god_rays=0.20,
         figure=dict(root=(-1.1, 4.4), walk=+1.0, yaw=math.pi),
         notes='cranes down and in through the torii as the figure reaches it'),
    Shot('S3-hall', 97,
         cam_from=(4.4, 2.40, 8.4), cam_to=(3.2, 2.05, 6.2),
         target_from=(0.0, 2.70, -2.0), target_to=(0.0, 2.60, -2.5),
         fov=44, rain=0.32, fog=0.024, exposure=1.16, god_rays=0.14,
         figure=dict(root=(0.6, 2.4), walk=+0.7, yaw=math.pi * 0.72),
         notes='three-quarter on the hall: raking lantern light, columns in '
               'perspective, figure crossing the frame'),
    Shot('S4-aerial', 73,
         cam_from=(2.0, 11.0, 11.0), cam_to=(5.0, 6.4, 8.2),
         target_from=(0.0, 2.40, -2.0), target_to=(0.0, 2.10, -2.5),
         fov=50, rain=0.55, fog=0.028, exposure=1.05, god_rays=0.10,
         figure=dict(root=(-1.6, 3.0), walk=+1.0, yaw=math.pi),
         notes='crane down over the roof onto the courtyard plan'),
    Shot('S5-reveal', 93,
         cam_from=(0.12, 1.72, 5.6), cam_to=(0.10, 1.66, 5.0),
         target_from=(0.0, 1.50, 1.4), target_to=(0.0, 1.50, 1.4),
         fov=46, rain=0.30, fog=0.020, exposure=1.16, eye_glow=1.0,
         god_rays=0.10, bloom=0.70,
         figure=dict(root=(0.0, 1.4), walk=+0.0, yaw=0.0, head_turn=1.0),
         notes='medium shot: figure fills ~55% of frame height against the lit '
               'hall, then the head turns into the lens and the eyes light'),
]


# --------------------------------------------------------------------- frame
class Film3D:
    def __init__(self, width, height, samples=1):
        self.w, self.h, self.samples = width, height, samples
        self.F = render.Frame(width, height)

    def render(self, shot, i, out_scale=1.0):
        t = i / FPS
        p = ease(i / max(shot.frames - 1, 1))
        eye = shot.cam_from + (shot.cam_to - shot.cam_from) * p
        tgt = shot.tgt_from + (shot.tgt_to - shot.tgt_from) * p
        if shot.fit is not None:
            lo, hi = np.asarray(shot.fit[0], float), np.asarray(shot.fit[1], float)
            centre = (lo + hi) * 0.5
            direction = shot.fit_dir / np.linalg.norm(shot.fit_dir)
            # the move: the camera steps in and slides across as the shot plays
            drift = 1.0 - p
            d = fit_distance(lo, hi, shot.fov, self.w / self.h, direction,
                             shot.fit_fill, push=0.16 * drift)
            eye = centre + direction * d
            # a lateral slide across the shot (0 = static)
            eye = eye + np.array([shot.fit_slide * (p - 0.5), 0.0, 0.0])
            tgt = centre + np.array([shot.fit_look * (p - 0.5), 0.0, 0.0])
        # a slow hand-held breath, so the camera is never dead still
        eye = eye + np.array([0.010 * math.sin(t * 0.9), 0.006 * math.sin(t * 1.3 + 1.0), 0.0])

        rd, eyev, right, up = geom.camera_rays(self.w, self.h, eye, tgt, shot.fov)
        ro = np.broadcast_to(eyev, rd.shape).copy()

        fig = shot.figure
        dyn = []
        eyes = []
        if fig:
            walk_t = t * fig.get('walk', 0.0)
            segs = scene.pose_at(walk_t, root=fig['root'], yaw=fig.get('yaw', 0.0),
                                 run=fig.get('run', False),
                                 head_turn=fig.get('head_turn', 0.0) * p)
            dyn = [(np.array(a, np.float32), np.array(b, np.float32), r,
                    scene.MAT_ID[m]) for _n, a, b, r, m in segs]
            if shot.eye_glow > 0:
                for _n, a, b, r, m in segs:
                    if _n != 'head':
                        continue
                    fwd = (b - a) / max(np.linalg.norm(b - a), 1e-6)
                    # eye line sits about a third down the face
                    mid = b - fwd * 0.055
                    side = np.array([1.0, 0.0, 0.0]) * 0.034
                    inten = 3.2 * shot.eye_glow * min(1.0, 0.25 + p * 1.4)
                    eyes.append((tuple(mid + side), (1.0, 0.09, 0.05), inten, 0.020))
                    eyes.append((tuple(mid - side), (1.0, 0.09, 0.05), inten, 0.020))

        cam = (eyev, geom.normalise(tgt - eye).astype(np.float32), right, up,
               np.float32(math.tan(math.radians(shot.fov) * 0.5)),
               float(self.w) / float(self.h))
        tt, mat, nrm = self.F.trace(ro, rd, dyn, cam)
        lights = list(self.F.lights)
        col, hit, dist = self.F.shade(ro, rd, tt, mat, nrm, lights, eyes,
                                      shot.fog, FOG_TINT, AMBIENT)
        col = np.where(hit[..., None], col, self.F.sky(rd, FOG_TINT, time=t))
        col = self.F.wet_floor(col, ro, rd, tt, mat, nrm, lights, eyes,
                               shot.fog, FOG_TINT, AMBIENT, strength=0.38, time=t)
        if shot.god_rays > 0:
            col = self.F.god_rays(col, hit, tt, rd, (0.5, 0.22), shot.god_rays)
        if shot.rain > 0:
            col = self.F.rain(col, rd, tt, seed=7, density=shot.rain,
                              frame=i, length=0.5)
        col = self.F.bloom(col, shot.bloom)
        return self.F.finish(col, exposure=shot.exposure, seed=shot.frames * 31 + i)


def _render_range(job):
    """Worker: render a list of (global_frame_index, shot_index, local_index)."""
    width, height, frames_dir, items, shot_specs = job
    import cv2
    film = Film3D(width, height)
    for gi, si, li in items:
        shot = SHOTS[si]
        frame = film.render(shot, li)
        cv2.imwrite(str(Path(frames_dir) / f'f{gi:05d}.jpg'), frame[..., ::-1],
                    [cv2.IMWRITE_JPEG_QUALITY, 96])
    return len(items)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--width', type=int, default=W_DEFAULT)
    ap.add_argument('--height', type=int, default=H_DEFAULT)
    ap.add_argument('--workers', type=int, default=1)
    ap.add_argument('--frames-dir', default='')
    ap.add_argument('--shots', default='', help='comma list of shot name filters')
    ap.add_argument('--audio', default='')
    ap.add_argument('--log', default=str(HERE.parent / 'out/v3d/render_log.json'))
    ap.add_argument('--crf', type=int, default=18)
    ap.add_argument('--preset', default='slow')
    ap.add_argument('--stills', default='')
    ap.add_argument('--limit', type=int, default=0, help='debug: first N frames only')
    a = ap.parse_args()

    shots = [s for s in SHOTS
             if not a.shots or any(k in s.name for k in a.shots.split(','))]
    total = sum(s.frames for s in shots)
    if a.limit:
        keep, left = [], a.limit
        for s in shots:
            take = min(s.frames, left)
            if take <= 0:
                break
            keep.append(s)
            left -= take
        shots, total = keep, sum(s.frames for s in shots)

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    frames_dir = Path(a.frames_dir) if a.frames_dir else out.parent / 'frames'
    frames_dir.mkdir(parents=True, exist_ok=True)

    # ---- work list
    items, gi = [], 0
    shot_frames = []
    for si, shot in enumerate(shots):
        shot_frames.append((gi, gi + shot.frames))
        for li in range(shot.frames):
            items.append((gi, si, li))
            gi += 1

    log = {'renderer': 'qc/vfx3d/film3d.py',
           'kind': 'analytic ray-traced 3D, procedural geometry and lighting',
           'width': a.width, 'height': a.height, 'fps': FPS,
           'frames_total': total, 'seconds': round(total / FPS, 3),
           'workers': a.workers, 'shots': [], 'output': str(out)}
    t_start = time.time()

    if a.workers > 1:
        import multiprocessing as mp
        chunks = [items[i::a.workers] for i in range(a.workers)]
        jobs = [(a.width, a.height, str(frames_dir), c, None) for c in chunks]
        with mp.Pool(a.workers) as pool:
            done = 0
            for n in pool.imap_unordered(_render_range, jobs):
                done += n
                print(f'  {done}/{total} frames', flush=True)
    else:
        _render_range((a.width, a.height, str(frames_dir), items, None))
    render_seconds = time.time() - t_start

    # ---- encode
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    # -start_number 0 and -fps_mode cfr are not optional: without them ffmpeg's
    # image demuxer starts at 1, misses frame 0 and re-times the whole stream,
    # which produced duplicated frames and an undecodable file.
    cmd = [ff, '-hide_banner', '-loglevel', 'error', '-y',
           '-start_number', '0', '-framerate', str(FPS),
           '-i', str(frames_dir / 'f%05d.jpg'), '-fps_mode', 'cfr']
    has_audio = bool(a.audio) and Path(a.audio).exists()
    if has_audio:
        cmd += ['-i', a.audio, '-map', '0:v', '-map', '1:a',
                '-c:a', 'aac', '-b:a', '256k', '-shortest']
    cmd += ['-c:v', 'libx264', '-preset', a.preset, '-crf', str(a.crf),
            '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-tune', 'film',
            '-movflags', '+faststart', str(out)]
    subprocess.run(cmd, check=True)

    for si, shot in enumerate(shots):
        f0, f1 = shot_frames[si]
        log['shots'].append({
            'shot': shot.name, 'frames': f1 - f0,
            'seconds_from': round(f0 / FPS, 3),
            'seconds_to': round(f1 / FPS, 3),
            'camera_from': shot.cam_from.tolist(), 'camera_to': shot.cam_to.tolist(),
            'target_from': shot.tgt_from.tolist(), 'target_to': shot.tgt_to.tolist(),
            'fov': shot.fov, 'figure': shot.figure, 'rain': shot.rain,
            'fog': shot.fog, 'exposure': shot.exposure, 'notes': shot.notes,
        })
    log['render_seconds_total'] = round(render_seconds, 1)
    log['seconds_per_frame'] = round(render_seconds / max(total, 1), 2)
    log['audio'] = a.audio if has_audio else None
    Path(a.log).parent.mkdir(parents=True, exist_ok=True)
    Path(a.log).write_text(json.dumps(log, indent=1))
    size = out.stat().st_size
    print(f'\nWROTE {out}  {total} frames  {total / FPS:.3f}s  {size} bytes')
    print(f'log   {a.log}')


if __name__ == '__main__':
    main()
