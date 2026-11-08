"""Extract traceable contact sheets from public animation examples; no access circumvention."""
import json,pathlib,subprocess,tempfile,urllib.request
items=[
 ('alan-original','https://vimeo.com/17016768','vimeo','Alan Becker, Animator vs. Animation'),
 ('alan-second','https://vimeo.com/17016941','vimeo','Alan Becker, Animator vs. Animation II'),
 ('alan-minecraft','https://vimeo.com/149072131','vimeo','Alan Becker, Animation vs. Minecraft (first 90 seconds)'),
 ('snowball','https://upload.wikimedia.org/wikipedia/commons/4/4e/Snowball_Fight.webm','direct','turkey3, Snowball Fight, CC BY-SA 2.0'),
 ('coconut','https://upload.wikimedia.org/wikipedia/commons/7/7b/Coconut_Mayhem.webm','direct','turkey3, Coconut Mayhem, CC BY-SA 2.0'),
 ('fight','https://upload.wikimedia.org/wikipedia/commons/5/59/FightAnim3.gif','direct','Evar678, FightAnim3, CC BY 4.0'),
 ('walk','https://upload.wikimedia.org/wikipedia/commons/3/32/Stick_figure_walking.gif','direct','Ebaychatter0, Stick figure walking, CC0')]
out=pathlib.Path('docs/repo-intel/open-animation-motion');out.mkdir(parents=True,exist_ok=True);rows=[]
def run(cmd,timeout=200):return subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout)
with tempfile.TemporaryDirectory() as td:
 for name,url,typ,credit in items:
  row={'id':name,'url':url,'credit':credit,'status':'unknown'}
  try:
   p=pathlib.Path(td)/name
   if typ=='direct':
    p=p.with_suffix(pathlib.Path(urllib.parse.urlparse(url).path).suffix)
    req=urllib.request.Request(url,headers={'User-Agent':'MonarchMotionStudy/1.0 (research)'})
    with urllib.request.urlopen(req,timeout=30) as f:p.write_bytes(f.read())
   else:
    cmd=['yt-dlp','--no-warnings','--no-playlist','--no-progress','--socket-timeout','15','--retries','0','-f','best[height<=480]/best','-o',str(p)+'.%(ext)s']
    if name=='alan-minecraft':cmd+=['--download-sections','*0-90','--force-keyframes-at-cuts']
    r=run(cmd+[url],240);files=list(pathlib.Path(td).glob(name+'.*'))
    if r.returncode or not files:row.update(status='unavailable',error=r.stderr[-400:].replace('\n',' '));rows.append(row);print(name,'unavailable',flush=True);continue
    p=files[0]
   probe=run(['ffprobe','-v','error','-show_entries','format=duration:stream=width,height,r_frame_rate','-select_streams','v:0','-of','json',str(p)])
   row.update(status='downloaded',probe=json.loads(probe.stdout));folder=out/name;folder.mkdir(exist_ok=True)
   # 1 fps total coverage; every sample labeled with decoded presentation timestamp.
   vf="fps=1,scale=240:-2,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='%{pts\\:hms}':x=3:y=3:fontsize=14:fontcolor=white:box=1:boxcolor=black@0.7,tile=5x4"
   r=run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(p),'-vf',vf,'-vsync','vfr',str(folder/'seconds-%02d.jpg')])
   row['seconds']=[str(x) for x in sorted(folder.glob('seconds-*.jpg'))];row['seconds_error']=r.stderr[-300:] if r.returncode else None
   # Dense first 8 seconds at 5fps. This does NOT claim all-frame coverage.
   vf="fps=5,scale=200:-2,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='%{pts\\:hms}':x=3:y=3:fontsize=13:fontcolor=white:box=1:boxcolor=black@0.7,tile=5x4"
   r=run(['ffmpeg','-hide_banner','-loglevel','error','-t','8','-i',str(p),'-vf',vf,'-vsync','vfr',str(folder/'detail-%02d.jpg')])
   row['detail']=[str(x) for x in sorted(folder.glob('detail-*.jpg'))];row['detail_error']=r.stderr[-300:] if r.returncode else None
   print(name,row['status'],len(row['seconds']),len(row['detail']),flush=True)
  except Exception as e:row['status']='error';row['error']=str(e)[:200];print(name,'error',str(e)[:100],flush=True)
  rows.append(row)
(out/'probe.json').write_text(json.dumps({'method':'Public creator Vimeo videos, Wikimedia open-license animation. 1fps temporal overview and 5fps first 8 seconds; not every source frame. First Minecraft 90 sec only. No virality or celebrity POV implied.','items':rows},indent=2))
