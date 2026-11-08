#!/usr/bin/env python3
"""Loudness-normalize a provisional research mix; this is not listening QA."""
import argparse,json,re,subprocess
from pathlib import Path
import imageio_ffmpeg

p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path);p.add_argument('output',type=Path);p.add_argument('--target',type=float,default=-20.0);a=p.parse_args()
if not -30<=a.target<=-14:raise ValueError('Target out of research range')
if not a.input.is_file():raise FileNotFoundError(a.input)
ff=imageio_ffmpeg.get_ffmpeg_exe();af=f'loudnorm=I={a.target}:TP=-2:LRA=10'
analysis=subprocess.run([ff,'-hide_banner','-nostats','-i',str(a.input),'-af',af+':print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
matches=re.findall(r'\{[^{}]*"input_i"[^{}]*\}',analysis.stderr,re.S)
if not matches:raise RuntimeError('Loudness analysis did not report measurements')
measure=json.loads(matches[-1])
keys=['input_i','input_tp','input_lra','input_thresh','target_offset']
for key in keys:
 try: val=float(measure[key])
 except (KeyError,ValueError):raise ValueError(f'Invalid loudness measurement {key}')
 if not -100<val<100:raise ValueError(f'Unsafe loudness measurement {key}')
a.output.parent.mkdir(parents=True,exist_ok=True)
second=af+':measured_I='+measure['input_i']+':measured_TP='+measure['input_tp']+':measured_LRA='+measure['input_lra']+':measured_thresh='+measure['input_thresh']+':offset='+measure['target_offset']+':linear=true:print_format=summary'
subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-i',str(a.input),'-af',second,'-ar','48000','-c:a','pcm_s16le',str(a.output)],check=True)
print('Two-pass provisional loudness normalization; creative listening and sync QA still required.')
