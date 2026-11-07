"""Export complete one-second reference-frame bursts after human visual screening.
Research-only extraction of existing public footage, NOT the unapproved creative minute.
No audio listening or complete human review is claimed by these mechanical outputs.
"""
import concurrent.futures,csv,gzip,hashlib,json,math,os,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe();B=Path('docs/research/stickman-study/curated-windows');B.mkdir(parents=True,exist_ok=True);C=Path('.cache/curated-windows');C.mkdir(parents=True,exist_ok=True)
# All intervals chosen from actual opened source images; hypotheses are in the review notes.
WINDOWS={'0cd18ab697e0':[272.0,472.2],'b9e8a291ae3c':[83.2,304.2],'f334cd6120d4':[227.8,668.2],'f4ae200f9b37':[301.6,345.3],'e3b2a006f184':[82.1,174.0],'7326277638ec':[56.3,178.6],'aff391b174ca':[91.7,208.1],'5d952e3a6a3a':[71.0,181.1],'ef60027e9c03':[187.4,243.1],'455465bdfe37':[187.3,247.4],'ce5cb51a4085':[93.1,98.2],'f97d7d8c717c':[14.0,24.8]}
sources={}
for p in Path('docs/research/stickman-study/archive-footage').glob('results-shard-*.json'):
 for r in json.load(open(p)).get('results',[]):
  if r.get('media_acquired'):sources[Path(r['contact_sheet']).name[:12]]=r
shard=int(os.environ.get('STUDY_SHARD','0'));jobs=[(k,sources[k])for i,k in enumerate(WINDOWS)if i%3==shard and k in sources];results=[]
def process(v):
 key,r=v;row={'source_key':key,'source_url':r['source_url'],'source_title':r['archived_filename'],'human_review_completed':False,'audio_actually_heard':False,'windows':[]};src=C/(key+'.mp4');work=C/key;work.mkdir(exist_ok=True)
 try:
  subprocess.run(['curl','--fail','--location','--max-time','390','--speed-time','20','--speed-limit','2000','--output',str(src),r['source_url']],capture_output=True,check=True,timeout=400)
  actual=hashlib.sha256(src.read_bytes()).hexdigest()
  if actual!=r['file_sha256']:raise ValueError('Source SHA mismatch: do not reuse the previous file frame index')
  row['source_sha256_verified']=actual
  with gzip.open(r['frame_forensics']['frame_index'],'rt')as f:index=[{'n':int(v['decoded_frame']),'pts':float(v['actual_pts_seconds'])}for v in csv.DictReader(f)]
  windows=[{'start':start,'end':start+1,'frames':[v for v in index if start<=v['pts']<start+1]}for start in WINDOWS[key]]
  ids=sorted({v['n']for w in windows for v in w['frames']})
  if not ids:raise ValueError('No indexed frames in requested source intervals')
  expr="select='"+'+'.join('between(n,%s,%s)'%(w['frames'][0]['n'],w['frames'][-1]['n'])for w in windows if w['frames'])+"',scale=480:-2"
  subprocess.run([FF,'-v','error','-y','-i',str(src),'-map','0:v:0','-vf',expr,'-fps_mode','passthrough','-q:v','3',str(work/'%05d.jpg')],capture_output=True,check=True,timeout=220)
  images=sorted(work.glob('*.jpg'))
  if len(images)!=len(ids):raise ValueError(('Expected exact burst-frame count',len(ids),len(images)))
  image_map=dict(zip(ids,images))
  for j,w in enumerate(windows):
   count=len(w['frames']);cols=5;rows=math.ceil(count/cols);board=Image.new('RGB',(1600,50+rows*210),'#17282d');d=ImageDraw.Draw(board);d.text((8,8),f'{key} / {w["start"]:.3f}-{w["end"]:.3f}s / every decoded frame in this interval',fill='white');d.text((8,26),r['archived_filename'][:180],fill='white')
   for n,v in enumerate(w['frames']):
    im=Image.open(image_map[v['n']]);im.thumbnail((320,180));x=n%cols*320;y=50+n//cols*210;board.paste(im,(x,y));d.text((x+5,y+183),f'n{v["n"]} / actual PTS {v["pts"]:.6f}s',fill='white')
   sheet=B/(key+f'-burst-{j}.jpg');board.save(sheet,quality=84)
   record={'start_pts':w['start'],'end_pts_exclusive':w['end'],'frame_count':count,'all_decoded_frames_in_interval_exported':True,'frames':w['frames'],'sheet':str(sheet),'human_visual_interpretation_completed':False,'audio_measurement_is_not_listening':True}
   try:
    a=subprocess.run([FF,'-v','error','-ss',str(w['start']),'-i',str(src),'-t','1','-map','0:a:0','-ac','1','-ar','16000','-f','f32le','pipe:1'],capture_output=True,check=True,timeout=30)
    audio=np.frombuffer(a.stdout,dtype='<f4');blocks=[audio[i:i+160]for i in range(0,len(audio),160)if len(audio[i:i+160])==160];record['audio_rms_10ms']=[round(float(np.sqrt(np.mean(v*v))),7)for v in blocks];record['audio_timing_caveat']='Container seek-relative audio; stream-start offset and perceptual event meaning not independently verified.'
   except Exception as e:record['audio_measurement_error']=str(e)
   row['windows'].append(record)
 except Exception as e:row['error']=str(e);row['diagnostic']=(getattr(e,'stderr',b'')or b'').decode('utf8','replace')[-1200:]
 return row
with concurrent.futures.ThreadPoolExecutor(2)as pool:
 for future in concurrent.futures.as_completed([pool.submit(process,v)for v in jobs]):
  row=future.result();results.append(row);(B/f'results-shard-{shard}.json').write_text(json.dumps({'reference_extraction_only':True,'not_a_completed_visual_or_audio_study':True,'results':results},indent=2)+'\n');print(row['source_key'],len(row['windows']),row.get('error','OK'),flush=True)
