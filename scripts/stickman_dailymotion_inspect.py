"""Collect small research contact sheets from creator-published public animations.
No cookies, no access-control workarounds, no raw video committed. Contact sheets for commentary only.
"""
import json,pathlib,subprocess,tempfile
sources=[('xaowzzm','Sticky vs Eraser'),('xaopl5y','Sticky vs Pencil'),('xapkx1m',"Sticky's First Skateboard Trick"),('xap9e2u','Sticky Trapped in an Aesthetic Bedroom'),('xap7xj2','Sticky vs a Living Skateboard'),('xaqit86','He Tried the Viral Trend'),('xbslfb6','Stickman vs The Giant Stapler')]
out=pathlib.Path('docs/repo-intel/stickman-motion-evidence');out.mkdir(parents=True,exist_ok=True); rows=[]
def run(cmd,timeout=90):return subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout)
with tempfile.TemporaryDirectory() as d:
 for vid,title in sources:
  row={'source':f'https://www.dailymotion.com/video/{vid}','id':vid,'title':title,'source_account':'InfoTales3D','status':'unknown'}
  try:
   r=run(['yt-dlp','--no-playlist','--no-warnings','--no-progress','--socket-timeout','15','--retries','0','-f','best[height<=720]/best','-o',f'{d}/{vid}.%(ext)s',row['source']],90)
   files=list(pathlib.Path(d).glob(vid+'.*'))
   if r.returncode or not files:
    row.update(status='unavailable',reason=r.stderr[-600:].replace('\n',' '));rows.append(row);print(vid,'unavailable',flush=True);continue
   video=files[0];p=run(['ffprobe','-v','error','-show_entries','format=duration:stream=width,height,r_frame_rate','-select_streams','v:0','-of','json',str(video)])
   row['probe']=json.loads(p.stdout); row['status']='downloaded'
   folder=out/vid;folder.mkdir(exist_ok=True)
   # Timestamped tiles of every second. A partial last tile may be present.
   vf="fps=1,scale=192:-2,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='%{pts\\:hms}':x=4:y=4:fontsize=14:fontcolor=white:box=1:boxcolor=black@0.7,tile=5x4"
   q=run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(video),'-vf',vf,'-vsync','vfr',str(folder/'seconds-%02d.jpg')])
   row['seconds_sheets']=[str(p) for p in sorted(folder.glob('seconds-*.jpg'))];row['seconds_error']=q.stderr[-300:] if q.returncode else None
   # Dense view of opening 12 seconds at 5 samples per second; timecodes in tiles.
   vf5="fps=5,scale=160:-2,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='%{pts\\:hms}':x=3:y=3:fontsize=12:fontcolor=white:box=1:boxcolor=black@0.7,tile=6x5"
   q=run(['ffmpeg','-hide_banner','-loglevel','error','-t','12','-i',str(video),'-vf',vf5,'-vsync','vfr',str(folder/'detail-%02d.jpg')])
   row['detail_sheets']=[str(p) for p in sorted(folder.glob('detail-*.jpg'))];row['detail_error']=q.stderr[-300:] if q.returncode else None
   print(vid,row['status'],len(row['seconds_sheets']),len(row['detail_sheets']),flush=True)
  except Exception as e:row['status']='error';row['reason']=type(e).__name__;print(vid,'error',type(e).__name__,flush=True)
  rows.append(row)
(out/'probe.json').write_text(json.dumps({'method':'Public creator-account Dailymotion playback with no authentication. Sheets sample at 1fps over full duration and 5fps for opening 12s. This is not every source frame; no claims on virality or exact niche. No raw video stored.','videos':rows},indent=2))
