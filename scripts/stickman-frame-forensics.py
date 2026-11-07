"""Mechanical every-decoded-frame index + consecutive-frame quotes. Not human visual review.
No source video is committed. Timing is actual decoded PTS, not nominal-FPS inference.
"""
import csv,gzip,json,re,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe()
def inspect(source,key,out,cache):
 out=Path(out);cache=Path(cache);work=cache/(key+'-adjacent');work.mkdir(exist_ok=True)
 r=subprocess.run([FF,'-hide_banner','-loglevel','info','-i',str(source),'-map','0:v:0','-vf','scale=64:36,format=gray,showinfo','-an','-fps_mode','passthrough','-f','rawvideo','pipe:1'],capture_output=True,check=True,timeout=250)
 a=np.frombuffer(r.stdout,np.uint8).reshape(-1,36*64);log=r.stderr.decode('utf8','replace');pts=[float(v)for v in re.findall(r' n:\s*\d+\s+pts:\s*[-\d]+\s+pts_time:([\d.eE+-]+)',log)]
 if len(pts)!=len(a):raise ValueError(('PTS/frame mismatch',len(pts),len(a)))
 diff=np.zeros(len(a),np.float32)
 for start in range(1,len(a),800):
  end=min(len(a),start+800);diff[start:end]=np.abs(a[start:end].astype(np.int16)-a[start-1:end-1].astype(np.int16)).mean(axis=1)
 csvpath=out/(key+'-frame-index.csv.gz')
 with gzip.open(csvpath,'wt',newline='')as f:
  w=csv.writer(f);w.writerow(['decoded_frame','actual_pts_seconds','mean_abs_gray_difference_64x36'])
  for i,t in enumerate(pts):w.writerow([i,t,round(float(diff[i]),5)])
 # These are mechanically chosen change windows, NOT asserted hand/foot contacts or cuts.
 peaks=[]
 for i in np.argsort(diff)[::-1]:
  i=int(i)
  if i<5 or i>=len(a)-5 or pts[i]<min(12,pts[-1]*.10):continue
  if all(abs(pts[i]-pts[j])>max(5,pts[-1]*.08)for j in peaks):peaks.append(i)
  if len(peaks)==2:break
 ids=sorted(set(n for i in peaks for n in [i-3,i-1,i,i+1,i+3]));filt="select='"+'+'.join(f'eq(n,{i})'for i in ids)+"',scale=960:-2"
 if ids:
  subprocess.run([FF,'-v','error','-y','-i',str(source),'-map','0:v:0','-vf',filt,'-fps_mode','passthrough','-q:v','3',str(work/'%03d.jpg')],capture_output=True,check=True,timeout=180)
  images=list(sorted(work.glob('*.jpg')));board=Image.new('RGB',(1600,420),'#17282d');d=ImageDraw.Draw(board)
  for k,(p,index)in enumerate(zip(images,ids)):
   im=Image.open(p);im.thumbnail((320,180));x=k%5*320;y=k//5*210;board.paste(im,(x,y));d.text((x+5,y+183),f'f{index} / {pts[index]:.4f}s',fill='white')
  board.save(out/(key+'-adjacent-quotes.jpg'),quality=84)
  # Two rescaled 960px-wide detail quotations, not native-resolution evidence.
  for k in [2,7]:
   if k<len(images):Image.open(images[k]).save(out/(key+f'-detail-{k}.jpg'),quality=82)
 report={'all_video_frames_indexed':True,'decoded_frames':len(a),'first_pts':pts[0],'last_pts':pts[-1],'low_change_frames_mae_below_0_5':int(sum(diff[1:]<.5)),'mechanical_change_windows':[{'frame':i,'pts':pts[i],'difference':float(diff[i])}for i in peaks],'adjacent_quoted_frames':[{'frame':i,'pts':pts[i]}for i in ids],'frame_index':str(csvpath),'actual_visual_review_completed':False,'every_frame_human_inspected':False,'audio_listening_claimed':False,'change_scores_are_not_rig_or_editing_method_proof':True}
 (out/(key+'-mechanical.json')).write_text(json.dumps(report,indent=2)+'\n');return report
