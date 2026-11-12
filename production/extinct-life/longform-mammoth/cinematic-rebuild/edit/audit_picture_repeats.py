"""Find the same rendered picture at two different points in the cut.

`audit_duplicates.py` works on source file + timecode, so it catches a render being used
twice. It cannot catch two *different* renders that look the same, which is the risk this
film carries: the plain, the herd and the shoreline recur across a dozen scene
directories and the same 3D mammoth is in all of them.

A frame-by-frame scan cannot answer this. Every held shot drifts slowly, so a frame six
seconds into it is nearly identical to a frame one second in - thousands of "matches"
that mean nothing. The real question is whether two *segments* of the cut open on the
same picture, so this compares segment entry frames, which is where a repeat is visible
to a viewer.

Usage:
  python .cache/audit_picture_repeats.py [reel.mp4]
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[5]
DEFAULT = ROOT / '.cache/mammoth-edit/review-reel-continuous.mp4'
THUMB_W, THUMB_H = 96, 54
# Mean absolute difference in 0-255 grey, measured on a 96x54 thumbnail. Two different
# shots of the same herd on the same plain sit well above this; a genuine repeat of the
# same frame sits below it.
MATCH = 6.0
# Segments closer together than this may legitimately continue the same view.
MIN_GAP = 4.0


def segment_list(reel_seconds):
    sys.path.insert(0, str(ROOT / 'production/extinct-life/longform-mammoth'
                             '/cinematic-rebuild/edit'))
    script = (ROOT / 'production/extinct-life/longform-mammoth'
              '/cinematic-rebuild/edit/check_coverage.py')
    out = subprocess.run([sys.executable, str(script)],
                         capture_output=True, text=True).stdout
    data = json.loads(out[out.index('{'):])
    # Only rendered-world segments: every paper plate opens on the same cream field, so
    # comparing plates measures the template, not a repeated shot.
    sys.path.insert(0, str(ROOT / 'production/extinct-life/longform-mammoth'
                             '/cinematic-rebuild/edit'))
    import report_picture_balance as balance
    segs = [s for s in data['segments']
            if s.get('built') and s['name'] not in balance.PLATE]
    return sorted(segs, key=lambda s: s['start_frame']), reel_seconds


def grab(reel, times):
    """One thumbnail per requested time, in a single pass over the reel."""
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    seen = {}
    for i, t in enumerate(times):
        proc = subprocess.run(
            [ff, '-hide_banner', '-loglevel', 'error', '-ss', f'{t:.3f}',
             '-i', str(reel), '-frames:v', '1',
             '-vf', f'scale={THUMB_W}:{THUMB_H},format=gray',
             '-f', 'rawvideo', '-'],
            capture_output=True, check=True)
        if len(proc.stdout) == THUMB_W * THUMB_H:
            seen[i] = np.frombuffer(proc.stdout, dtype=np.uint8).astype(np.float32)
    return seen


def main():
    reel = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    segs, _ = segment_list(0)
    fps = 30
    times, labels = [], []
    for s in segs:
        t = s['start_frame'] / fps + 1.2 if s['frames'] > 45 else s['start_frame'] / fps + 0.05
        times.append(t)
        labels.append((s['name'], round(s['start_frame'] / fps, 2)))
    frames = grab(reel, times)

    pairs = []
    for i, a in frames.items():
        for j, b in frames.items():
            if j <= i:
                continue
            gap = abs(times[i] - times[j])
            if gap < MIN_GAP:
                continue
            d = float(np.abs(a - b).mean())
            if d < MATCH:
                pairs.append({'a': labels[i][0], 'a_time': labels[i][1],
                              'b': labels[j][0], 'b_time': labels[j][1],
                              'gap_seconds': round(gap, 1), 'difference': round(d, 2)})
    pairs.sort(key=lambda p: p['difference'])
    print(json.dumps({
        'reel': str(reel.relative_to(ROOT)),
        'segments_compared': len(frames),
        'thumbnail': f'{THUMB_W}x{THUMB_H} grey',
        'match_threshold_mad': MATCH,
        'near_identical_entry_pairs': len(pairs),
        'pairs': pairs[:25],
    }, indent=2))
    print(f'PICTURE REPEATS: {len(pairs)}')


if __name__ == '__main__':
    main()
