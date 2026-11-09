from pathlib import Path
import json,subprocess,hashlib
import imageio_ffmpeg
from PIL import Image,ImageDraw
import numpy as np
B=Path('production/extinct-life/homotherium-short');C=Path('.cache/homotherium-short');p=Path('deliverables/Homotherium-Cub-This-Saber-Toothed-Cub-Still-Has-Its-Fur-1080x1920.mp4');ff=imageio_ffmpeg.get_ffmpeg_exe()
r=subprocess.run([ff,'-hide_banner','-i',str(p),'-af','loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);(C/'final-ffmpeg-qc.log').write_text(r.stderr);a=r.stderr.rfind('{');loud=json.loads(r.stderr[a:r.stderr.rfind('}')+1]);assert -18<float(loud['input_i'])<-14;assert float(loud['input_tp'])<=-1
r=subprocess.run([ff,'-v','error','-i',str(p),'-map','0:v:0','-f','null','-'],capture_output=True,text=True,check=True);assert not r.stderr
reader=imageio_ffmpeg.read_frames(str(p),pix_fmt='rgb24');meta=next(reader);count=0;mins=[];motion=[];prior=None;samples=[];sheet=Image.new('RGB',(6*180,5*340),'#071419');draw=ImageDraw.Draw(sheet)
for i,b in enumerate(reader):
 count+=1
 if i%60==0:
  x=np.frombuffer(b,dtype=np.uint8).reshape(1920,1080,3);im=Image.fromarray(x);small=np.asarray(im.resize((54,96)));mins.append(float(small.mean()));
  if prior is not None:motion.append(float(np.mean(np.abs(small.astype(float)-prior.astype(float)))))
  prior=small
  thumb=im.resize((180,320));j=len(samples);sheet.paste(thumb,((j%6)*180,(j//6)*340));draw.text(((j%6)*180+5,(j//6)*340+321),f'{i/30:.1f}s',fill='white');samples.append(i)
  if i in [60,300,900,1020,1440]:im.save(C/f'final-{i:04}.jpg',quality=94)
assert count==1530;assert meta['size']==(1080,1920);assert meta['fps']==30;assert min(mins)>3
sheet.save(C/'final-contact.jpg',quality=92)
d={'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'decoded_frames':count,'width':1080,'height':1920,'fps':30,'duration_seconds':51,'complete_decode_errors':r.stderr,'loudness':loud,'every_two_second_samples':samples,'minimum_sampled_rgb_mean':min(mins),'minimum_two_second_image_difference':min(motion),'render':json.loads((C/'render-0-1530.json').read_text()),'review_scope':'Complete automated video decode and audio loudness analysis; native still and two-second contact sampling. Not claimed as continuous human-like audiovisual watching/listening.','youtube_published':False}
(B/'DELIVERY-QC.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items() if k not in ['render']},indent=2))
