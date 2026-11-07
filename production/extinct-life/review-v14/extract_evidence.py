"""Evidence from the released encoded MP4, not source re-renders. No creative pass/fail inferred."""
import csv,hashlib,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
R=Path(__file__).resolve().parents[3]; B=Path(__file__).resolve().parent; C=R/'.cache/v14-review';C.mkdir(parents=True,exist_ok=True)
F=imageio_ffmpeg.get_ffmpeg_exe(); movie=R/'.cache/extinct-v14/Extinct_Life_V14_Directed_English_1080p.mp4'
assert hashlib.sha256(movie.read_bytes()).hexdigest()==json.loads((B.parent/'film-v14-directed/QC.json').read_text())['sha256']
def run(a):return subprocess.run([F,'-y','-v','error',*map(str,a)],check=True,capture_output=True)
small=C/'seconds';small.mkdir(exist_ok=True)
run(['-i',movie,'-vf',"select='not(mod(n,30))',scale=384:216",'-fps_mode','passthrough','-q:v','3',small/'%04d.jpg'])
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
def sheet(paths,labels,out,cols=4):
 rows=(len(paths)+cols-1)//cols;im=Image.new('RGB',(384*cols,242*rows),'#10232a');d=ImageDraw.Draw(im)
 for i,(p,label) in enumerate(zip(paths,labels)):
  x=i%cols*384;y=i//cols*242;im.paste(Image.open(p).resize((384,216)),(x,y+26));d.text((x+8,y+4),label,font=font,fill='#f0e4bd')
 im.save(out,quality=89)
(B/'seconds').mkdir(exist_ok=True)
paths=sorted(small.glob('*.jpg'));assert len(paths)==439
for i in range(0,len(paths),20):sheet(paths[i:i+20],[f'{j//60:02}:{j%60:02} | frame {j*30}' for j in range(i,min(i+20,439))],B/'seconds'/f'{i:03}-{min(i+19,438):03}.jpg')
# Every decoded frame: low-resolution numerical diagnostics, not an artistic inspection.
p=subprocess.Popen([F,'-v','error','-i',str(movie),'-an','-vf','scale=160:90','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
metrics=[];previous=None;size=160*90*3
while True:
 raw=p.stdout.read(size)
 if not raw:break
 assert len(raw)==size
 a=np.frombuffer(raw,np.uint8).reshape(90,160,3).astype(np.float32);lum=a.mean(2);delta=0 if previous is None else float(np.abs(a-previous).mean());changed=0 if previous is None else float((np.abs(a-previous).mean(2)>4).mean())
 metrics.append([len(metrics),len(metrics)/30,float(lum.mean()),float(lum.std()),float((lum<5).mean()),float((lum>250).mean()),delta,changed]);previous=a
assert p.wait()==0 and len(metrics)==13163
with (B/'every-frame-metrics.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['frame','seconds','mean_rgb_luma_proxy','spatial_std','near_black_fraction','near_white_fraction','rgb_MAE_from_previous','changed_fraction_over_4']);w.writerows(metrics)
(B/'full-resolution').mkdir(exist_ok=True)
chosen=[0,5,6,17,26,33,38,42,53,57,60,63,65,74,86,90,98,103,108,112,119,124,132,138,141,146,153,160,167,174,179,190,200,205,216,219,220,221,222,225,232,241,250,257,269,278,281,286,294,302,310,318,325,336,339,346,352,358,362,370,377,387,393,400,407,412,416,425,435,438]
for sec in chosen:run(['-ss',sec,'-i',movie,'-frames:v',1,'-q:v',2,B/'full-resolution'/f'{sec:03}.jpg'])
(B/'motion').mkdir(exist_ok=True)
for start in [5,28,142,164,219,222,285,303,343,414]:
 tmp=C/f'motion-{start}';tmp.mkdir(exist_ok=True);run(['-ss',start,'-i',movie,'-t','3','-vf','fps=10,scale=384:216','-q:v','3',tmp/'%03d.jpg']);pp=sorted(tmp.glob('*.jpg'));sheet(pp,[f'{start+j/10:07.2f}s' for j in range(len(pp))],B/'motion'/f'{start:03}.jpg',5)
# Encoded stereo waveform windows. Measurements are not a listening review.
a=C/'audio.f32';run(['-i',movie,'-vn','-ac','2','-ar','48000','-f','f32le',a]);audio=np.fromfile(a,dtype='<f4').reshape(-1,2)
with (B/'audio-per-second.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['second','rms_dbfs','sample_peak_dbfs','stereo_correlation'])
 for i in range(439):
  v=audio[i*48000:(i+1)*48000];r=float(np.sqrt(np.mean(v*v)));peak=float(np.max(np.abs(v)));corr=float(np.corrcoef(v.T)[0,1]) if np.std(v[:,0])*np.std(v[:,1])>1e-10 else None;w.writerow([i,20*np.log10(max(r,1e-10)),20*np.log10(max(peak,1e-10)),corr])
summary={'asset_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'asset_bytes':movie.stat().st_size,'decoded_frames_measured':len(metrics),'analysis_resolution':[160,90],'seconds_sampled_visually_available':len(paths),'second_sample_frames':'0,30,...,13140','full_resolution_samples':chosen,'temporal_strips':{'starts': [5,28,142,164,219,222,285,303,343,414],'duration':3,'fps':10},'manual_every_frame_review_claimed':False,'continuous_human_watch_listen_claimed':False,'warning':'Low-resolution MAE/nonblack tests do not prove absence of anatomy, clipping, continuity, scientific or editorial flaws.'}
(B/'EVIDENCE.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
