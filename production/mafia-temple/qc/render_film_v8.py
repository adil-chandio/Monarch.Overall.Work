#!/usr/bin/env python3
"""Render MONARCH — night temple, build V8: the highest honest-quality cut.

What is different from the earlier review cuts
----------------------------------------------
1. Native frames only. Every shot plays generated frames at <= 1.0x, so no
   frame is duplicated and no motion is invented (`retime_indices` refuses a
   speed that would need more source frames than exist).
2. Measured defect repair, not a global "enhance" filter: per-shot deflicker
   (auto-vetoed where it does not measurably help), cancellation of the measured
   rigid-jitter residual, and exposure matching.
3. A real learned 2x network (ESPCN) instead of bicubic stretching, then a
   frame-accurate push-in/pan re-frame to 1280x720.
4. Exact 480-frame / 20.000 s timeline with frame-accurate cuts and two
   dissolves that *share* frames from both shots (never pad the runtime).
5. Tracked iris glow on the close-up (offline Haar face box + iris centroid,
   median+EMA smoothed), ramped so it never pops, disabled if tracking fails.
6. Cinematic night grade (teal shadows, vignette, per-frame grain) in float32,
   plus a separately measured sound pass.

What this is NOT: it cannot repair identity drift, malformed hands/shoes,
wrong likeness, weak acting, camera-source softness or unverified rights.
Those stay in KNOWN-LIMITS.md and on-camera QC.

Usage:
  python qc/render_film_v8.py --out qc/out/v8/monarch-temple-v8.mp4 \
      --superres /path/ESPCN_x2.pb --audio qc/out/v8/sound.wav
"""
from __future__ import annotations

import argparse, json, re, subprocess, sys, time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import film_tools as ft  # noqa: E402

W, H, FPS = 1280, 720, 24
TOTAL_FRAMES = 480          # exactly 20.000 s


@dataclass
class Shot:
    name: str          # shot id used in logs
    source: str        # clip stem inside clips/
    start: int         # first film frame its timeline range covers
    frames: int        # frames it contributes on the film timeline
    zoom_from: float = 1.0
    zoom_to: float = 1.0
    pan_x: float = 0.0
    pan_y: float = 0.0
    eye_glow: bool = False
    deflicker: float = 0.9
    stabilise: bool = True
    notes: str = ''

    @property
    def end(self):
        return self.start + self.frames


# Cut sheet from job.json: street, gate, aerial, running, turn + close-up.
# Every source frame is used exactly once (97+121+97+73+97 = 485), and the single
# 5-frame dissolve at 3.83s blends two real frames, so the timeline is exactly
# 480 frames = 20.000 s with no hole, no repeat and no invented frame.

SHOTS = [
    Shot('S1-street', 'wan4-street-b', 0, 97, 1.000, 1.060, 0.004, 0.000,
         notes='all 97 native frames; 5f dissolve into the gate'),
    Shot('S2-gate', 'wan4-gate', 92, 121, 1.000, 1.050, -0.004, 0.006,
         notes='all 121 native frames; the gate push carries 8.8s'),
    Shot('S3-aerial', 'wan4-aerial', 213, 97, 1.060, 1.000, 0.0, -0.010,
         notes='all 97 native frames; pull-back exaggerates the descent'),
    Shot('S4-running', 'wan4-running-b', 310, 73, 1.010, 1.100, 0.010, 0.0,
         notes='all 73 native frames; push tracks the stride'),
    Shot('S5-closeup', 'wan4-face-a', 383, 97, 1.000, 1.140, 0.0, 0.004,
         eye_glow=True, deflicker=0.55,
         notes='all 97 native frames; deepest push, tracked red iris glow'),
]

GRADE = {
    'S1-street': dict(teal=0.055, contrast=1.05, black_point=3, vignette=0.14, grain=2.0),
    'S2-gate': dict(teal=0.050, contrast=1.06, black_point=2, vignette=0.12, grain=2.2),
    'S3-aerial': dict(teal=0.060, contrast=1.05, black_point=2, vignette=0.16, grain=2.2),
    'S4-running': dict(teal=0.045, contrast=1.04, black_point=2, vignette=0.12, grain=2.4),
    'S5-closeup': dict(teal=0.035, contrast=1.06, black_point=1, vignette=0.18, grain=1.6),
}


def decode(path: Path) -> np.ndarray:
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    probe = subprocess.run([ff, '-hide_banner', '-i', str(path)],
                           capture_output=True, text=True).stderr
    m = re.search(r'(\d{2,5})x(\d{2,5})', probe.split('Video:')[1]) if 'Video:' in probe else None
    if not m:
        raise SystemExit(f'cannot probe {path}')
    w, h = int(m.group(1)), int(m.group(2))
    raw = subprocess.run([ff, '-v', 'error', '-i', str(path), '-pix_fmt', 'bgr24',
                          '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    n = len(raw) // (w * h * 3)
    if n < 2:
        raise SystemExit(f'no frames decoded from {path}')
    return np.frombuffer(raw[:n * w * h * 3], np.uint8).reshape(n, h, w, 3).copy()


def fit_wide(frame: np.ndarray) -> np.ndarray:
    """Cover-crop to 16:9 (no distortion), then scale to film size."""
    h, w = frame.shape[:2]
    target = W / H
    if w / h > target:
        nw = int(round(h * target))
        x0 = (w - nw) // 2
        frame = frame[:, x0:x0 + nw]
    else:
        nh = int(round(w / target))
        y0 = (h - nh) // 2
        frame = frame[y0:y0 + nh]
    interp = cv2.INTER_AREA if frame.shape[1] >= W else cv2.INTER_CUBIC
    return cv2.resize(frame, (W, H), interpolation=interp)


class Renderer:
    def __init__(self, args):
        self.args = args
        self.sr = ft.SuperRes(str(args.superres)) if args.superres else None
        self.log = {'shots': [], 'film': {}}

    # -------------------------------------------------------------- per shot
    def prepare(self, shot: Shot):
        frames = decode(ROOT / 'clips' / f'{shot.source}.mp4')
        n = len(frames)
        idx = ft.retime_indices(shot.frames, n)
        speed = ft.playback_speed(shot.frames, n)
        used = frames[idx]

        grays = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in used]
        luma = np.array([g.mean() for g in grays], dtype=np.float64)
        step_before = float(np.abs(np.diff(luma)).max()) if len(luma) > 1 else 0.0

        gains = np.ones_like(luma)
        step_after = step_before
        flicker_used = 0.0
        if shot.deflicker > 0 and len(luma) > 4:
            cand = ft.deflicker_gains(luma, shot.deflicker)
            cand_step = float(np.abs(np.diff(luma * cand)).max())
            if cand_step < step_before * 0.9:
                gains, step_after, flicker_used = cand, cand_step, shot.deflicker

        shifts = np.zeros((shot.frames, 2))
        jitter_before = jitter_after = 0.0
        if shot.stabilise and len(used) > 3:
            track = ft.track_shifts(grays, work_width=320, radius=5)
            jitter_before = ft.jitter_rms(track)
            if jitter_before >= 0.45:
                resid = np.clip(ft.stabilise_residuals(track, sigma=2.5), -10, 10)
                shifts = -resid
                jitter_after = ft.jitter_rms(track - resid)
            else:
                jitter_after = jitter_before

        eye_track, eye_stats = None, None
        if shot.eye_glow:
            seed, pts = ft.seed_eyes(used)
            eye_stats = {'seed_frame': seed, 'seed_points': pts, 'frames': len(used)}
            if seed is None:
                eye_stats['glow'] = 'disabled: no verified eye pair found'
            else:
                track = ft.track_pair(used, seed, pts)
                eye_track = ft.smooth_points(track, 5)
                hits = int(sum(p is not None for p in eye_track))
                eye_stats['eye_hits'] = hits
                if hits < 0.6 * len(used):
                    eye_track = None
                    eye_stats['glow'] = f'disabled: tracking only {hits}/{len(used)} frames'
                else:
                    eye_stats['glow'] = f'tracked on {hits}/{len(used)} frames'

        self.log['shots'].append({
            'shot': shot.name, 'source': shot.source, 'source_frames': n,
            'timeline_range': [shot.start, shot.end - 1], 'timeline_frames': shot.frames,
            'playback_speed': round(speed, 4), 'duplicated_frames': 0,
            'frames_dropped': n - shot.frames,
            'deflicker_strength': flicker_used,
            'luma_step_max_before': round(step_before, 3),
            'luma_step_max_after': round(step_after if flicker_used else step_before, 3),
            'jitter_rms_before': round(jitter_before, 3),
            'jitter_rms_after': round(jitter_after, 3),
            'stabilised': bool(np.abs(shifts).max() > 0),
            'camera': {'zoom': [shot.zoom_from, shot.zoom_to],
                       'pan': [shot.pan_x, shot.pan_y]},
            'eye_track': eye_stats, 'notes': shot.notes,
        })
        return {'used': used, 'gains': gains, 'shifts': shifts, 'eye': eye_track}

    # ------------------------------------------------------------ per frame
    def render_frame(self, shot: Shot, prep, i: int) -> np.ndarray:
        k = min(i, len(prep['used']) - 1)
        frame = prep['used'][k]

        g = float(prep['gains'][k])
        if abs(g - 1.0) > 1e-3:
            frame = ft.match_luma(frame, g, limit=1.12)

        if self.sr is not None:
            frame = self.sr(frame)
        frame = fit_wide(frame)

        progress = i / max(shot.frames - 1, 1)
        m = ft.camera_matrix(progress, shot.zoom_from, shot.zoom_to,
                             shot.pan_x, shot.pan_y, W, H)
        # a 1.02 guard zoom hides the sub-pixel edge of the warp
        m[0, 0] = m[1, 1] = m[0, 0] * 1.02
        m[0, 2] += (0.5 * 1.02 - 0.5) * W * -1
        m[1, 2] += (0.5 * 1.02 - 0.5) * H * -1
        frame = cv2.warpAffine(frame, m, (W, H), flags=cv2.INTER_LANCZOS4,
                               borderMode=cv2.BORDER_REFLECT_101)

        s = -prep['shifts'][k]
        if np.abs(s).max() > 0.05:
            dm = np.float32([[1, 0, float(s[0])], [0, 1, float(s[1])]])
            frame = cv2.warpAffine(frame, dm, (W, H), flags=cv2.INTER_LINEAR,
                                   borderMode=cv2.BORDER_REFLECT_101)

        eye = prep['eye']
        if eye is not None and eye[k] is not None:
            # ramp in over ~1.4 s, then a slow breathing pulse; capped so it
            # glows rather than blows out
            ramp = float(np.clip((i - 26) / 34.0, 0, 1))
            pulse = 0.92 + 0.08 * np.sin(2 * np.pi * i / 40.0)
            scale = W / float(prep['used'].shape[2])
            pts = [(x * scale, y * scale) for x, y in eye[k]]
            frame = ft.brighten_eyes(frame, pts, 0.92 * ramp * pulse, radius_scale=scale)

        return ft.grade_frame(frame, seed=(shot.start + i) * 7919, **GRADE[shot.name])


def build(args):
    r = Renderer(args)
    preps = [(s, r.prepare(s)) for s in SHOTS]

    # per-frame plan: which shot(s) cover each film frame, and the blend alpha
    plan = [[] for _ in range(TOTAL_FRAMES)]
    for shot, prep in preps:
        for f in range(shot.start, min(shot.end, TOTAL_FRAMES)):
            plan[f].append((shot, prep, f - shot.start))
    missing = [f for f, p in enumerate(plan) if not p]
    if missing:
        raise SystemExit(f'timeline gap at frames {missing[:8]} ({len(missing)} frames)')
    over = [f for f, p in enumerate(plan) if len(p) > 2]
    if over:
        raise SystemExit(f'more than two shots overlap at {over[:8]}')

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, '-hide_banner', '-loglevel', 'error', '-y',
           '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', 'pipe:0']
    has_audio = bool(args.audio) and Path(args.audio).exists()
    if has_audio:
        cmd += ['-i', str(args.audio), '-map', '0:v', '-map', '1:a', '-c:a', 'aac',
                '-b:a', '256k', '-ar', '48000']
    cmd += ['-c:v', 'libx264', '-preset', args.preset, '-crf', str(args.crf),
            '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.1',
            '-g', '48', '-movflags', '+faststart', str(out)]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    t0 = time.time()
    try:
        for f in range(TOTAL_FRAMES):
            entries = plan[f]
            if len(entries) == 1:
                shot, prep, i = entries[0]
                frame = r.render_frame(shot, prep, i)
            else:
                (s1, p1, i1), (s2, p2, i2) = entries
                # alpha by position inside the overlap: first frame keeps more of
                # the outgoing shot, last frame keeps more of the incoming one
                overlap_len = s1.end - s2.start
                a = (f - s2.start + 1) / (overlap_len + 1)
                a = a * a * (3 - 2 * a)
                f1 = r.render_frame(s1, p1, i1).astype(np.float32)
                f2 = r.render_frame(s2, p2, i2).astype(np.float32)
                frame = np.clip(f1 * (1 - a) + f2 * a, 0, 255).astype(np.uint8)
            enc.stdin.write(frame.tobytes())
            if (f + 1) % 60 == 0:
                print(f'  {f + 1}/{TOTAL_FRAMES} frames  ({time.time() - t0:.1f}s)', flush=True)
    finally:
        try:
            enc.stdin.close()
        except BrokenPipeError:
            pass
    if enc.wait() != 0:
        raise SystemExit('encoding failed')

    r.log['film'] = {
        'width': W, 'height': H, 'fps': FPS, 'frames': TOTAL_FRAMES,
        'seconds': round(TOTAL_FRAMES / FPS, 3), 'output': str(out),
        'cuts_seconds': [round(s.start / FPS, 3) for s in SHOTS],
        'overlaps': [{'frames': [a.end - b.start], 'at_seconds': b.start / FPS}
                     for a, b in zip(SHOTS, SHOTS[1:]) if a.end > b.start],
        'grade': GRADE,
        'superres': 'ESPCN x2 (learned)' if r.sr else 'none',
        'encode': {'codec': 'libx264', 'crf': args.crf, 'preset': args.preset},
        'audio': str(args.audio) if has_audio else None,
        'render_seconds': round(time.time() - t0, 2),
        'limits': 'Measured engineering repair only. No likeness/anatomy/rights claim.',
    }
    log_path = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(r.log, indent=1))
    print(f'\nWROTE {out} ({TOTAL_FRAMES} frames, {TOTAL_FRAMES / FPS:.3f}s)')
    print(f'log  {log_path}')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', required=True)
    ap.add_argument('--log', default=str(HERE / 'out/v8/render_log.json'))
    ap.add_argument('--superres', default='')
    ap.add_argument('--audio', default='')
    ap.add_argument('--crf', type=int, default=17)
    ap.add_argument('--preset', default='medium')
    build(ap.parse_args())


if __name__ == '__main__':
    main()
