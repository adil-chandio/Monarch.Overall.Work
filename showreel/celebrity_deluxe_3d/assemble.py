"""Join forty 1.5-second shards, burn safe-area captions, and mix stereo."""
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
from showreel.celebrity_deluxe_3d.soundtrack import mix

FFMPEG = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or story.FF


def captions(cues, path):
    header = '''[Script Info]\nScriptType: v4.00+\nPlayResX: 320\nPlayResY: 568\nWrapStyle: 0\nScaledBorderAndShadow: yes\n[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\nStyle: Caption,DejaVu Sans,13.5,&H00F8FAFF,&H0000FFFF,&H0011171A,&H80000000,-1,0,0,0,100,100,0,0,1,1.35,0.6,2,17,17,49,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''
    lines = []
    for cue, parts, split in zip(cues,story.CAPTIONS,story.SPLITS):
        current=cue['start']
        ends=([current+split, current+cue['duration']] if split else [current+cue['duration']])
        for text,end in zip(parts,ends):
            lines.append(f'Dialogue: 0,{story.ass_time(current)},{story.ass_time(end)},Caption,,0,0,0,,{{\\fad(80,100)}}{text}')
            current=end
    path.write_text(header+'\n'.join(lines)+'\n')


def run(args):
    print(' '.join(map(str,args)),flush=True)
    subprocess.run(list(map(str,args)),check=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('clips',type=Path)
    p.add_argument('sound_assets',type=Path)
    p.add_argument('output',type=Path)
    args=p.parse_args()
    clips=[args.clips/f'{i:02d}.mp4' for i in range(40)]
    missing=[str(x) for x in clips if not x.is_file()]
    if missing:
        raise SystemExit('missing shards: '+', '.join(missing))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='celebrity-deluxe-') as d:
        d=Path(d); concat=d/'list.txt'; audio=d/'mix.wav'; ass=d/'captions.ass'
        concat.write_text(''.join("file '"+str(x.resolve()).replace("'","'\\''")+"'\n" for x in clips))
        cues=json.loads((story.V6/'script.json').read_text())
        captions(cues,ass)
        mix(cues,args.sound_assets,story.V6/'trimmed',audio,FFMPEG)
        vf=f'fade=t=in:st=0:d=0.32,fade=t=out:st=59.25:d=0.75,ass={ass}'
        run([FFMPEG,'-y','-v','error','-f','concat','-safe','0','-i',concat,'-i',audio,
             '-vf',vf,'-af','loudnorm=I=-18:TP=-2:LRA=11',
             '-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p',
             '-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart',
             '-t','60','-metadata','title=Fictional celebrity day - deluxe 3D pass',args.output])
        run([FFMPEG,'-v','error','-i',args.output,'-f','null','-'])
    print('finished',args.output,args.output.stat().st_size,'bytes',flush=True)


if __name__ == '__main__':
    main()
