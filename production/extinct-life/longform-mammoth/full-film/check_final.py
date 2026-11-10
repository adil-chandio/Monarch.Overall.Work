"""Full-film automated delivery QC. Does not claim human listening or viewing."""
import hashlib,json,re,subprocess
from pathlib import Path
import imageio_ffmpeg,numpy as np
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[3];C=R/'.cache/longform-mammoth-full';P=json.loads((B/'timeline.json').read_text());v=R/'deliverables/Last-Mammoths-Full-Film-3D-1080p.mp4';ff=imageio_ffmpeg.get_ffmpeg_exe()
assert v.exists() and v.stat().st_size>1000000
# Full decode of video AND audio, aborting on decoding errors.
q=subprocess.run([ff,'-v','error','-i',str(v),'-f','null','-'],capture_output=True,text=True,check=True)
if q.stderr.strip():raise RuntimeError(q.stderr)
r=subprocess.run([ff,'-hide_banner','-i',str(v),'-af','loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json','-vn','-f','null','-'],capture_output=True,text=True,check=True)
s=r.stderr;i=s.rfind('{');loud=json.loads(s[i:s.rfind('}')+1])
assert -19<float(loud['input_i'])<-13,loud
assert float(loud['input_tp'])<=-0.8,loud
# One sampled frame every 10 seconds; output downscaled raw frames to avoid
# transmitting gigabytes of pixel buffers from a 12 minute 1080p decode.
proc=subprocess.Popen([ff,'-v','error','-i',str(v),'-vf','fps=1/10,scale=320:180','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
frames=[]
while True:
 b=proc.stdout.read(320*180*3)
 if not b:break
 if len(b)!=320*180*3:raise RuntimeError('Truncated QC sample')
 frames.append(np.frombuffer(b,dtype=np.uint8).reshape(180,320,3).copy())
err=proc.stderr.read().decode();code=proc.wait()
if code or err.strip():raise RuntimeError(err)
assert len(frames)>=int(P['duration']//10)
mins=[float(f.mean()) for f in frames];assert min(mins)>3.0,min(mins)
cols=6;rows=(len(frames)+cols-1)//cols;sheet=Image.new('RGB',(cols*320,rows*180));draw=ImageDraw.Draw(sheet)
for i,f in enumerate(frames):
 x=(i%cols)*320;y=(i//cols)*180;sheet.paste(Image.fromarray(f),(x,y));draw.text((x+5,y+162),f'{5+i*10}s',fill='white')
sheet.save(C/'contact.jpg',quality=88)
reader=imageio_ffmpeg.read_frames(str(v),pix_fmt='rgb24');meta=next(reader);reader.close()
assert meta['size']==(1920,1080),meta
assert abs(meta['fps']-30)<.02,meta
assert abs(meta['duration']-P['duration'])<.5,(meta['duration'],P['duration'])
report={'file':str(v.relative_to(R)),'bytes':v.stat().st_size,'sha256':hashlib.sha256(v.read_bytes()).hexdigest(),'duration_seconds':meta['duration'],'size':meta['size'],'fps':meta['fps'],'loudness':loud,'full_decode_errors':q.stderr,'samples':len(frames),'sample_interval_seconds':10,'first_sample_seconds':5,'minimum_sampled_rgb_mean':round(min(mins),2),'coverage':'Full decode and audio loudness measurement; one frame sampled every 10 seconds. Not continuous viewing or listening.','youtube_published':False}
(B/'DELIVERY-QC.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
