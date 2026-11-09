"""Measure every 30th source frame and 1-second audio RMS; no media copied into Git.
Requires ffmpeg, numpy and Pillow. This is sampled analysis, not shot detection.
"""
import argparse, json, math, re, subprocess, hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('out');p.add_argument('--ffmpeg',default='ffmpeg');a=p.parse_args()
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
# For the audited CFR-30 source, select frame indices 0,30,...; showinfo records actual PTS.
log=out/'selected-showinfo.txt';vid=[];thumb=[]
with log.open('wb') as err:
 proc=subprocess.Popen([a.ffmpeg,'-v','info','-i',a.source,'-map','0:v:0','-an','-vf','select=not(mod(n\\,30)),showinfo,scale=160:90','-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE,stderr=err)
 previous=None;n=0
 while True:
  data=proc.stdout.read(160*90*3)
  if not data:break
  if len(data)!=160*90*3:raise RuntimeError('incomplete raw frame')
  image=np.frombuffer(data,dtype=np.uint8).reshape(90,160,3)
  small=image.astype(np.int16);diff=None if previous is None else float(np.mean(np.abs(small-previous)));previous=small
  vid.append({'frame_index':n*30,'mean_rgb':[round(float(x),2) for x in image.mean(axis=(0,1))],'difference_from_previous_sample':round(diff,3) if diff is not None else None})
  if n%10==0:thumb.append((n,Image.fromarray(image.copy())))
  n+=1
 if proc.wait()!=0:raise RuntimeError('video decode failed')
pts=[float(x) for x in re.findall(r'\bn:\s*\d+\s+pts:\s*-?\d+\s+pts_time:([\d.]+)',log.read_text())]
if len(pts)!=len(vid):raise RuntimeError(f'PTS count {len(pts)} != frames {len(vid)}')
for entry,t in zip(vid,pts):entry['pts_seconds']=t
for base in range(0,len(thumb),49):
 batch=thumb[base:base+49];sheet=Image.new('RGB',(7*160,7*110),'white');d=ImageDraw.Draw(sheet)
 for j,(idx,im) in enumerate(batch):
  x=(j%7)*160;y=(j//7)*110;sheet.paste(im,(x,y+20));t=pts[idx];d.text((x+2,y+2),f'{int(t//60):02d}:{int(t%60):02d} / {t:.2f}s',fill='black')
 sheet.save(out/f'overview-{base//49+1:02}.jpg',quality=86)
# PCM is downmixed to mono, 8kHz; energy is numerical only, not source identification.
proc=subprocess.Popen([a.ffmpeg,'-v','error','-i',a.source,'-vn','-ac','1','-ar','8000','-f','f32le','-'],stdout=subprocess.PIPE)
audio=[]
while True:
 data=proc.stdout.read(8000*4)
 if not data:break
 v=np.frombuffer(data,dtype='<f4');r=float(np.sqrt(np.mean(v.astype(np.float64)**2)));peak=float(np.max(np.abs(v)))
 audio.append({'start_seconds':len(audio),'samples':len(v),'mono_rms_dbfs':round(20*math.log10(max(r,1e-12)),2),'mono_sample_peak_dbfs':round(20*math.log10(max(peak,1e-12)),2)})
if proc.wait()!=0:raise RuntimeError('audio decode failed')
# Downmix coefficients may produce >0 dBFS floating-point values; these are not true peak.
result={'source_sha256':hashlib.sha256(Path(a.source).read_bytes()).hexdigest(),'method':'Every 30th decoded frame with FFmpeg PTS, 160x90 sample; mono 8kHz RMS and sample peak per second, not LUFS/true peak, no source classification. Differences are sample differences, not verified edits.','video_sample_count':len(vid),'audio_sample_seconds':len(audio),'video':vid,'audio':audio}
(out/'metrics.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
print('video samples',len(vid),'audio bins',len(audio),'overview sheets',math.ceil(len(thumb)/49),'last pts',pts[-1],flush=True)
