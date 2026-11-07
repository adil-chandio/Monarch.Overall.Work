#!/usr/bin/env python3
"""Find actual public creator-hosted animation. No authentication-wall bypass.
Caches full media only ephemerally. Research quotes are small timestamped contact sheets.
"""
import concurrent.futures,hashlib,json,math,re,subprocess,sys,urllib.request
from pathlib import Path
from datetime import datetime,timezone
import imageio_ffmpeg
from PIL import Image,ImageDraw
BASE=Path('docs/research/stickman-study/alternate-access');BASE.mkdir(parents=True,exist_ok=True)
CACHE=Path('.cache/stickman-alternates');CACHE.mkdir(parents=True,exist_ok=True)
FF=imageio_ffmpeg.get_ffmpeg_exe()
PAGES=['https://noogai.newgrounds.com/movies','https://gildedguy.newgrounds.com/movies','https://terkoiz.newgrounds.com/movies','https://hyun1990.newgrounds.com/movies','https://www.arckonarts.com/','https://www.sokrispymedia.com/','https://www.stickpage.com/hyunseries.shtml','https://vimeo.com/130462764','https://vimeo.com/212518562']
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def get(url):
 try:
  q=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept-Language':'en-US,en;q=0.9'})
  with urllib.request.urlopen(q,timeout=25)as r:data=r.read(5_000_000).decode('utf-8','replace');status=r.status
  return {'url':url,'status':status,'title':re.search(r'<title[^>]*>(.*?)</title>',data,re.S).group(1).strip()if re.search(r'<title[^>]*>(.*?)</title>',data,re.S)else'', 'portals':list(dict.fromkeys(re.findall(r'(?:https?://www.newgrounds.com)?/portal/view/\d+',data))),'direct_media':list(dict.fromkeys(re.findall(r'https?[^\s<>"\']+\.(?:mp4|webm)(?:\?[^\s<>"\']*)?',data))), 'video_links':list(dict.fromkeys(re.findall(r'https?://(?:player\.)?vimeo.com/(?:video/)?\d+',data)))}
 except Exception as e:return {'url':url,'error':str(e),'portals':[],'direct_media':[],'video_links':[]}
def quote(f,ident,source):
 probe=subprocess.run([FF,'-hide_banner','-i',str(f)],capture_output=True,text=True).stderr
 m=re.search(r'Duration: (\d+):(\d+):([\d.]+)',probe)
 if not m:raise ValueError('No decodable duration')
 duration=int(m[1])*3600+int(m[2])*60+float(m[3]);d=CACHE/ident;d.mkdir(exist_ok=True)
 # Full decode/progress, not a claim of human viewing every frame.
 full=subprocess.run([FF,'-v','error','-i',str(f),'-map','0:v:0','-progress','pipe:1','-an','-f','null','-'],capture_output=True,text=True,timeout=220,check=True)
 counts=re.findall(r'^frame=(\d+)',full.stdout,re.M)
 images=[]
 for i in range(24):
  t=max(0,min(duration-.05,(i+.5)*duration/24));p=d/f'{i:02}.jpg'
  subprocess.run([FF,'-v','error','-y','-ss',str(t),'-i',str(f),'-frames:v','1','-vf','scale=320:180:force_original_aspect_ratio=decrease,pad=320:180:(ow-iw)/2:(oh-ih)/2',str(p)],check=True,capture_output=True,timeout=30);images.append((p,t))
 board=Image.new('RGB',(1280,1260),'#17282d');draw=ImageDraw.Draw(board)
 for i,(p,t)in enumerate(images):
  x=i%4*320;y=i//4*210;board.paste(Image.open(p),(x,y));draw.text((x+5,y+184),f'{ident}  {t:.2f}s',fill='white')
 out=BASE/(ident+'-research-quotes.jpg');board.save(out,quality=82)
 return {'source':source,'file_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'seconds':duration,'full_decode':True,'decoded_frames':int(counts[-1])if counts else None,'quoted_frame_timestamps':[t for _,t in images],'contact_sheet':str(out),'every_frame_human_inspected':False,'visual_style_verified':False,'view_counts_not_inferred_from_alternate_site':True}
def main():
 pages=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(get,PAGES));write(BASE/'public-page-audit.json',pages)
 urls=[]
 for p in pages:
  # Limited, diverse creator sampling; do not confuse alternate platform reach with YouTube reach.
  for u in p.get('portals',[])[:7]:urls.append(('https://www.newgrounds.com'+u if u.startswith('/')else u,p['url']))
  for u in p.get('direct_media',[])[:3]:urls.append((u,p['url']))
  for u in p.get('video_links',[])[:3]:urls.append((u,p['url']))
 urls.extend([(u,u)for u in PAGES if 'vimeo.com/'in u]);urls=list(dict.fromkeys(urls))[:32]
 write(BASE/'candidate-public-routes.json',[{'url':u,'discovered_on':s}for u,s in urls]);results=[]
 def acquire(item):
  u,source=item;ident=hashlib.sha256(u.encode()).hexdigest()[:12];folder=CACHE/ident;folder.mkdir(exist_ok=True)
  try:
   r=subprocess.run([sys.executable,'-m','yt_dlp','--no-playlist','--no-progress','--socket-timeout','15','--retries','0','--fragment-retries','0','--js-runtimes','node','--max-filesize','160M','--match-filters','duration <= 1000','-f','best[height<=720]/best','-o',str(folder/'source.%(ext)s'),u],capture_output=True,text=True,timeout=100)
   files=[f for f in folder.iterdir()if f.suffix in ['.mp4','.webm','.mkv']and f.stat().st_size>10000]
   row={'url':u,'discovered_on':source,'media_acquired':bool(files),'detail':r.stderr[-2000:],'visual_review_completed':False}
   if files:row.update(quote(files[0],ident,u))
   return row
  except Exception as e:return {'url':u,'media_acquired':False,'error':str(e)}
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
  for row in pool.map(acquire,urls):results.append(row);write(BASE/'results.json',{'checked_at':datetime.now(timezone.utc).isoformat(),'results':results,'full_third_party_movies_committed':False,'study_complete':False});print(row['url'],row.get('media_acquired'),flush=True)
 if not urls:write(BASE/'results.json',{'results':[],'study_complete':False,'reason':'No direct public media routes discovered'})
if __name__=='__main__':main()
