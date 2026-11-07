import concurrent.futures,json,re,urllib.request,urllib.parse,hashlib,subprocess
from pathlib import Path
import imageio_ffmpeg
B=Path('docs/research/stickman-study/stickpage');B.mkdir(parents=True,exist_ok=True);C=Path('.cache/stickpage');C.mkdir(parents=True,exist_ok=True)
roots=['https://www.stickpage.com/hyunseries.shtml','https://www.stickpage.com/stickanimations.shtml','https://www.stickpage.com/se3dtrailerplay.shtml','https://www.stickpage.com/residentevilanimationplay.shtml','https://www.stickpage.com/stickdudekillingarena4play.shtml','https://www.stickpage.com/leagueoflegends2play.shtml']
def get(url):
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25)as r:data=r.read(100_000_000)
  return data,None
 except Exception as e:return None,str(e)
def page(url):
 data,error=get(url)
 if not data:return {'url':url,'error':error}
 text=data.decode('utf8','replace');media=re.findall(r'''(?:https?://[^\s"'<>]+\.(?:swf|mp4|webm)(?:\?[^\s"'<>]*)?|[\w/.-]+\.(?:swf|mp4|webm))''',text)
 return {'url':url,'title':re.search(r'<title>(.*?)</title>',text,re.S).group(1)if re.search(r'<title>(.*?)</title>',text,re.S)else'','media':list(dict.fromkeys(urllib.parse.urljoin(url,m.replace('&amp;','&'))for m in media)),'pages':list(dict.fromkeys(urllib.parse.urljoin(url,m)for m in re.findall(r'''href=["']([^"']+\.shtml)["']''',text)))[:100],'public_video_embed_urls':list(dict.fromkeys(re.findall(r'''https?://(?:www\.)?(?:youtube(?:-nocookie)?\.com/embed/|player.vimeo.com/video/)[^\s"'<>]+''',text)))}
rows=list(concurrent.futures.ThreadPoolExecutor(6).map(page,roots));more=[]
for r in rows:
 for p in r.get('pages',[]):
  if 'stickpage.com/'in p and p not in roots and not any(w in p for w in ['game','interview','series','contact','stickanimations']):
   p=p.replace('.shtml','play.shtml')if not p.endswith('play.shtml')else p
   if p not in more:more.append(p)
rows+=list(concurrent.futures.ThreadPoolExecutor(6).map(page,more[:30]));(B/'page-audit.json').write_text(json.dumps(rows,indent=2)+'\n')
media=[]
for r in rows:
 for u in r.get('media',[]):
  if not any(w in u for w in ['nav','advert','logo','flash_nav','banner']):
   if u.startswith('http://'):u='https://'+u[7:]
   if u not in [x[0]for x in media]:media.append((u,r['url'],r.get('title')))
results=[]
for u,p,title in media[:30]:
 data,error=get(u);row={'url':u,'page':p,'title':title,'accessible':bool(data),'error':error,'full_third_party_files_committed':False}
 if data:
  ident=hashlib.sha256(u.encode()).hexdigest()[:12];f=C/(ident+('.swf'if '.swf'in u else'.mp4'));f.write_bytes(data);row.update(bytes=len(data),signature=data[:3].decode('ascii','replace'),sha256=hashlib.sha256(data).hexdigest(),cache_file=str(f));probe=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-i',str(f)],capture_output=True,text=True);row['ffmpeg_probe']=probe.stderr[-2500:]
 results.append(row);(B/'media-audit.json').write_text(json.dumps(results,indent=2)+'\n');print(u,row['accessible'],row.get('signature'),flush=True)
