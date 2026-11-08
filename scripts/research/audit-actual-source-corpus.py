"""Actual-file evidence, not metadata-only or generated animation. Offline.
All frames decoded at source cadence, numerical frame metrics + PTS indexed;
visual review sampling is explicitly separate from all-frame decoding.
"""
import argparse,concurrent.futures,csv,hashlib,json,math,re,subprocess
from pathlib import Path
import imageio_ffmpeg,numpy as np
from PIL import Image,ImageDraw
FF=imageio_ffmpeg.get_ffmpeg_exe()
def run(args,timeout=160):return subprocess.run(args,capture_output=True,timeout=timeout,check=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--sources',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 manifest=json.loads((a.sources/'local-source-manifest.json').read_text());a.out.mkdir(parents=True,exist_ok=True)
 def audit(row):
  source=a.sources/row['file'];folder=a.out/row['key'];folder.mkdir(parents=True,exist_ok=True)
  if hashlib.file_digest(source.open('rb'),'sha256').hexdigest()!=row['sha256']:raise ValueError('Source hash changed')
  # showinfo precedes scaling: timestamps/indices describe actual decoded source frames.
  p=run([FF,'-y','-hide_banner','-i',str(source),'-map','0:v:0','-vf','showinfo,scale=90:160,format=rgb24','-fps_mode','passthrough','-an','-f','rawvideo','-'])
  log=p.stderr.decode('utf-8','replace');(folder/'full-decode-timestamps.log').write_text(log)
  pts=[float(x) for x in re.findall(r' n:\s*\d+\s+pts:\s*[-\d]+\s+pts_time:([-.\d]+)',log)]
  rgb=np.frombuffer(p.stdout,dtype=np.uint8).reshape(-1,160,90,3)
  if len(rgb)!=len(pts) or not len(pts):raise ValueError('Frame/timestamp coverage mismatch')
  if any(b<=c for c,b in zip(pts,pts[1:])):raise ValueError('Nonmonotonic source timestamps')
  delta=np.mean(np.abs(rgb[1:].astype(np.float32)-rgb[:-1].astype(np.float32)),axis=(1,2,3));delta=np.r_[0,delta]
  durations=np.diff(pts);step=float(np.median(durations)) if len(durations) else 1/30;start=pts[0];end=pts[-1]+step;duration=end-start
  with (folder/'every-frame.csv').open('w',newline='') as f:
   w=csv.writer(f);w.writerow(['frame','source_pts_seconds','relative_pts_seconds','mean_rgb_change_90x160'])
   w.writerows((i,t,t-start,float(delta[i])) for i,t in enumerate(pts))
  # Exact frame-number extraction. One-second samples are not a claim of all-frame visual review.
  sample_ids=sorted(set([min(len(pts)-1,int(np.searchsorted(pts,start+t))) for t in range(math.ceil(duration))]+[len(pts)-1]))
  select='+'.join('eq(n,'+str(i)+')' for i in sample_ids)
  run([FF,'-y','-v','error','-i',str(source),'-vf',"select='"+select+"'",'-fps_mode','passthrough','-q:v','2',str(folder/'native-sample-%03d.jpg')])
  gridpaths=[]
  for block in range(0,len(sample_ids),20):
   ids=sample_ids[block:block+20];board=Image.new('RGB',(1000,4*382),'#15222c');draw=ImageDraw.Draw(board)
   for j,idx in enumerate(ids):
    im=Image.open(folder/f'native-sample-{block+j+1:03d}.jpg').convert('RGB');im.thumbnail((200,356))
    x=(j%5)*200;y=(j//5)*382;board.paste(im,(x,y));draw.text((x+3,y+358),f'{pts[idx]-start:.3f}s f{idx}',fill='white')
   filename=f'timeline-{block//20+1:02d}.jpg';board.save(folder/filename,quality=90);gridpaths.append(filename)
  audio=run([FF,'-y','-v','error','-i',str(source),'-vn','-ac','2','-ar','48000','-f','f32le','-']).stdout
  (folder/'mixed-audio.f32').write_bytes(audio);pcm=np.frombuffer(audio,dtype='<f4').reshape(-1,2)
  with (folder/'second-by-second.csv').open('w',newline='') as f:
   w=csv.writer(f);w.writerow(['start_relative_seconds','end_relative_seconds','first_frame','last_frame','frame_count','mixed_audio_rms_dbfs','visual_review_status','audio_listening_status'])
   rel=np.array(pts)-start
   for sec in range(math.ceil(duration)):
    stop=min(sec+1,duration);ids=np.where((rel>=sec)&(rel<stop))[0];segment=pcm[round(sec*48000):round(stop*48000)].astype(np.float64)
    rms=20*math.log10(max(float(np.sqrt(np.mean(segment*segment))),1e-12)) if len(segment) else None
    w.writerow([sec,stop,int(ids[0]) if len(ids) else '',int(ids[-1]) if len(ids) else '',len(ids),rms,'not_yet_manually_annotated','not_perceptually_listened'])
  p=subprocess.run([FF,'-y','-hide_banner','-i',str(source),'-vn','-af','loudnorm=I=-16:TP=-2:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True,timeout=160,check=True)
  levels=json.loads(p.stderr[p.stderr.rfind('{'):p.stderr.rfind('}')+1])
  threshold=max(12,float(np.median(delta)+4*np.median(np.abs(delta-np.median(delta)))))
  candidates=[{'frame':int(i),'time_seconds':pts[i]-start,'mean_change':float(delta[i])} for i in np.argsort(delta)[::-1][:24] if delta[i]>threshold]
  candidates.sort(key=lambda x:x['frame'])
  summary={**row,'decoded_frame_count':len(pts),'source_video_seconds_from_pts':duration,'source_first_video_pts':start,'source_last_video_pts':pts[-1],
   'decoded_audio_seconds':len(pcm)/48000,'native_frame_size_from_decode_log':re.search(r' s:(\d+x\d+)',log).group(1),
   'sampled_source_frame_ids':sample_ids,'timeline_sheets':gridpaths,'high_change_candidates_NOT_verified_cuts':candidates,
   'integrated_lufs':levels['input_i'],'true_peak_dbtp':levels['input_tp'],'reported_short_clip_lra':levels['input_lra'],
   'all_frames_decoded_and_indexed':True,'every_frame_visually_inspected':False,'continuous_audio_listened':False,
   'limits':['RGB change is not camera-motion estimation or a verified cut list','One-second image sampling misses subsecond events',
    'Mixed PCM energy does not separate voice/music/SFX','Nominal decoded cadence does not establish authored animation cadence',
    'Sample PNG/JPEG exports are not source project files; exact renderer/lens/rig unavailable'],'production_hold':True}
  (folder/'evidence.json').write_text(json.dumps(summary,indent=2)+'\n');print(row['key'],len(pts),'frames indexed',flush=True);return summary
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(audit,manifest['sources']))
 (a.out/'corpus-evidence.json').write_text(json.dumps({'production_hold':True,'actual_sources_audited_numerically':len(results),'cases':results,'fully_manually_reviewed_sources':0},indent=2)+'\n')
if __name__=='__main__':main()
