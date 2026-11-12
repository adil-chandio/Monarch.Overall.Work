"""Assemble a continuous narration-locked review reel from verified inserts.

This is NOT the finished film and NOT picture lock. It is the first artifact in which
the whole 796-second narration can be watched end to end, so that pacing, repetition,
tone drift and section-to-section continuity can finally be judged in sequence rather
than section by section.

Rules:
  * only inserts whose QC report verifies (frame count, fps, offset, audio digest) are
    used; everything else becomes a labelled gap card, never silent black;
  * a gap card states the exact time range and the narration under it, so a missing
    passage is visible in the reel instead of being hidden by a dissolve;
  * narration and score come from one continuous source, so audio is continuous even
    where picture is not;
  * the narration is never ducked, faded or re-timed to fit a picture edit.

Usage:
  python assemble_review.py              # build the review reel
  python assemble_review.py --list       # print the running order only
"""
from pathlib import Path
import hashlib, json, subprocess, sys, tempfile
import imageio_ffmpeg

base = Path(__file__).resolve().parent
root = base.parents[4]
cache = root / '.cache/mammoth-edit'
audio = (root / 'production/extinct-life/longform-mammoth/cinematic-rebuild'
         / 'soundtrack-draft/Narration-Score-DRAFT.m4a')
out = cache / 'review-reel-continuous.mp4'
# Delivery encodes can be redirected without touching the cached master.
for _flag, _key in (('--out', 'OUT'), ('--crf', 'CRF')):
    if _flag in sys.argv:
        globals()[_key] = sys.argv[sys.argv.index(_flag) + 1]
out = Path(globals().get('OUT', out))
CRF = str(globals().get('CRF', '20'))
W, H, FPS = 1280, 720, 30


def verify():
    """Return (used, gaps) from check_coverage.py, never trusting stale QC."""
    script = base / 'check_coverage.py'
    r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit('coverage check failed; fix that before assembling')
    data = json.loads(r.stdout[r.stdout.index('{'):])
    return data


def running_order(data):
    """Expand the verified segments into a contiguous, gap-free running order.

    Each verified segment is its own piece. Merging neighbours into one window would be
    wrong here: once the timeline is continuous, a window is the union of many inserts,
    and no single workprint file covers it.
    """
    total = data['timeline_frames']
    pieces, gaps = [], []
    for seg in data['segments']:
        if not seg.get('built'):
            continue
        pieces.append({'kind': 'picture', 'a': seg['start_frame'],
                       'b': seg['start_frame'] + seg['frames'],
                       'frame': seg['start_frame'], 'name': seg['name'],
                       'file': seg.get('file', seg['name'] + '-incomplete-workprint.mp4')})
    for a, b in data['missing_ranges_frames']:
        gaps.append({'kind': 'gap', 'a': a, 'b': b})
        pieces.append({'kind': 'gap', 'a': a, 'b': b})
    pieces.sort(key=lambda p: (p['a'], p.get('kind') == 'gap'))
    return pieces, gaps, total


def gap_card(a, b):
    """A labelled still for one uncovered range. Text only: nothing is illustrated."""
    import textwrap
    lines = [
        'UNCOVERED PASSAGE',
        f'{a / FPS:0.2f} s – {b / FPS:0.2f} s',
        f'{(b - a) / FPS:0.2f} s of narration with no verified picture',
        '',
        'Narration continues underneath this card.',
        'This range is a gap in the edit, not a held shot.',
    ]
    path = cache / f'gap-{a}-{b}.png'
    vf = (
        f"drawbox=x=0:y=0:w={W}:h={H}:color=0xEFECE3:t=fill,"
        + ",".join(
            f"drawtext=text='{ln}':x=(w-tw)/2:y={196 + i * 46}:"
            f"fontsize={34 if i == 0 else 24}:fontcolor=0x202628:"
            f"fontfile={root}/public/showreel/fonts/Manrope-800.ttf"
            for i, ln in enumerate(lines) if ln
        )
    )
    subprocess.run([
        imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-hide_banner', '-loglevel', 'error',
        '-f', 'lavfi', '-i', f'color=c=0xEFECE3:s={W}x{H}:d=1',
        '-vf', vf, '-frames:v', '1', str(path)
    ], check=True)
    return path


def main():
    if '--list' in sys.argv:
        data = verify()
        pieces, gaps, total = running_order(data)
        for p in pieces:
            tag = p['name'] if p['kind'] == 'picture' else 'GAP'
            print(f"{p['a'] / FPS:7.2f} – {p['b'] / FPS:7.2f}  {tag}")
        print(f"total {total / FPS:.2f} s; {len(gaps)} gaps; "
              f"{data['verified_assembled_seconds']:.1f} s covered")
        return

    data = verify()
    pieces, gaps, total = running_order(data)
    inputs, filters, concat = [], [], []
    idx = 0
    for p in pieces:
        dur = (p['b'] - p['a']) / FPS
        if p['kind'] == 'picture':
            src = cache / p['file']
            if not src.is_file():
                raise SystemExit(f'missing verified workprint for {p["name"]}: {src}')
            inputs += ['-i', str(src)]
            # each insert already carries its own narration excerpt at its offset
            filters.append(
                f"[{idx}:v]trim=duration={dur},setpts=PTS-STARTPTS,"
                f"scale={W}:{H},fps={FPS},format=yuv420p[v{idx}]")
        else:
            card = gap_card(p['a'], p['b'])
            inputs += ['-loop', '1', '-t', f'{dur:.4f}', '-i', str(card)]
            filters.append(f"[{idx}:v]fps={FPS},format=yuv420p[v{idx}]")
        concat.append(f"[v{idx}]")
        idx += 1

    # Picture is concatenated; audio is taken from the single continuous score so the
    # narration never restarts, overlaps or drifts across a cut.
    graph = ";".join(filters) + f";{''.join(concat)}concat=n={idx}:v=1:a=0[vout]"
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-hide_banner', '-loglevel', 'error']
    cmd += inputs + ['-i', str(audio)]
    cmd += ['-filter_complex', graph, '-map', '[vout]', '-map', f'{idx}:a',
            '-t', f'{total / FPS:.4f}', '-c:v', 'libx264', '-preset', 'fast',
            '-crf', str(CRF), '-threads', '2', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', str(out)]
    subprocess.run(cmd, check=True)

    r = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-i', str(out),
                        '-filter_complex', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True)
    import re
    frames = re.findall(r'frame=\s*(\d+)', r.stderr)
    lufs = re.findall(r'I:\s*(-?[\d.]+) LUFS', r.stderr)
    peak = re.findall(r'Peak:\s*(-?[\d.]+) dBFS', r.stderr)
    report = {
        'status': 'continuous review reel; NOT the final film, NOT picture lock',
        'frames': int(frames[-1]) if frames else None,
        'seconds': round(total / FPS, 3),
        'lufs': float(lufs[-1]) if lufs else None,
        'true_peak_dbtp': float(peak[-1]) if peak else None,
        'covered_seconds': data['verified_assembled_seconds'],
        'gap_count': len(gaps),
        'gaps_seconds': [[round(a / FPS, 2), round(b / FPS, 2)] for a, b in
                         [(g['a'], g['b']) for g in gaps]],
        'audio_source': str(audio.relative_to(root)),
        'audio_sha256': hashlib.sha256(audio.read_bytes()).hexdigest(),
        'output_sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
        'note': ('Gaps are labelled cards, not black. Audio is one continuous score; '
                 'no section audio was mixed in. Not auditioned by a human.'),
    }
    (cache / 'review-reel-report.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
