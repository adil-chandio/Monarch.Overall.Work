"""Assemble the full 24 fps render with the ten existing narration takes."""
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
from showreel.celebrity_recovery_3d import render as story

FFMPEG = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or story.FF


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
    with tempfile.TemporaryDirectory(prefix='celebrity-cinematic-') as temp:
        temp = Path(temp)
        concat, audio, captions = temp / 'list.txt', temp / 'mix.wav', temp / 'captions.ass'
        concat.write_text(''.join("file '" + str(p.resolve()).replace("'", "'\\''") + "'\n" for p in clips))
        cues = json.loads((story.V6 / 'script.json').read_text())
        if len(cues) != 10:
            raise ValueError('all ten original narration cues are required')
        story.audio(cues, audio)
        story.captions(cues, captions)
        # Use a slightly finer outline than the previous heavy black border.
        ass = captions.read_text().replace(',1,2.2,0.7,2,18,18,30,1', ',1,1.6,0.8,2,18,18,30,1')
        captions.write_text(ass)
        vf = f'fade=t=in:st=0:d=0.3,fade=t=out:st=59.45:d=0.55,ass={captions}'
        run([FFMPEG, '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', concat,
             '-i', audio, '-vf', vf, '-af', 'loudnorm=I=-18:TP=-2:LRA=11',
             '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
             '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-movflags', '+faststart',
             '-t', '60', '-metadata', 'title=Fictional celebrity day - cinematic 3D pass', args.output])
        run([FFMPEG, '-v', 'error', '-i', args.output, '-f', 'null', '-'])
    print('finished', args.output, args.output.stat().st_size, 'bytes', flush=True)


if __name__ == '__main__':
    main()
