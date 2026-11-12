"""Join 20 loss-controlled render shards and add the existing story mix."""
from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from showreel.celebrity_recovery_3d import render as source

FFMPEG = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or source.FF


def run(args):
    print(' '.join(map(str, args)), flush=True)
    subprocess.run(list(map(str, args)), check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('clips', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    clips = [args.clips / f'{i:02d}.mp4' for i in range(20)]
    missing = [str(p) for p in clips if not p.is_file()]
    if missing:
        raise SystemExit('missing shards: ' + ', '.join(missing))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='celebrity-premium-') as tmp:
        tmp = Path(tmp)
        concat = tmp / 'list.txt'
        concat.write_text(''.join("file '" + str(p.resolve()).replace("'", "'\\''") + "'\n" for p in clips))
        sound = tmp / 'mix.wav'
        subtitles = tmp / 'captions.ass'
        cues = json.loads((source.V6 / 'script.json').read_text())
        if len(cues) != 10:
            raise ValueError('the ten-cue narration is required')
        source.audio(cues, sound)
        source.captions(cues, subtitles)
        vf = f'fade=t=in:st=0:d=0.3,fade=t=out:st=59.45:d=0.55,ass={subtitles}'
        run([FFMPEG, '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', concat,
             '-i', sound, '-vf', vf, '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
             '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000',
             '-movflags', '+faststart', '-t', '60', '-metadata',
             'title=Fictional celebrity day - 3D upgrade', args.output])
        run([FFMPEG, '-v', 'error', '-i', args.output, '-f', 'null', '-'])
    print('finished', args.output, args.output.stat().st_size, 'bytes', flush=True)


if __name__ == '__main__':
    main()
