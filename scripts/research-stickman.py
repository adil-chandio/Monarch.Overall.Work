#!/usr/bin/env python3
"""Public-metadata discovery and honest AV-access feasibility; NOT a completed visual study.
No credentials, full third-party videos or private reference material are committed.
"""
import datetime as dt,hashlib,json,os,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from yt_intel import client,http
OUT=Path('docs/research/stickman-study');CACHE=Path('.cache/stickman-study')
QUERIES=['3d stickman animation','3d stick figure animation','stickman animation blender','stickman 3d animated story','stickman 3d science animation','stickman 3d funny animation','stickman vs wall animation','stickman animation physics','stick figure animation storytelling','Alan Becker animation vs physics','Alan Becker animation vs math','stickman animation survival story','stickman animation history explained','stickman animation science explained','stickman 3d fight animation','stickman animation noob vs pro']
SEEDS=['WRXPNw6jq_I','gy0A8ixDhHo','3wnE6nVra70','I8bSN1TX8Sc','JlykRhaFAs0']
def stamp():return dt.datetime.now(dt.timezone.utc).isoformat()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def discover():
 report={'checked_at':stamp(),'status':'discovery_only','lane':client.lane(),'queries':[],'videos':[],'errors':[], 'limitations':['Search ranking and lifetime views do not prove quality, retention, geography, RPM or the cause of virality.','True 3D, 2D, 2.5D, gameplay, tutorials and unrelated results require actual visual screening; titles do not establish style.','YouTube Data API supplies metadata, not watchable video frames.','No full visual/sonic forensic review is claimed by this file.']}
 ids=list(SEEDS);hits={}
 if client.API_KEY:
  for query in QUERIES:
   try:
    data=client._api('search',{'part':'snippet','q':query,'type':'video','maxResults':25,'order':'viewCount','relevanceLanguage':'en','regionCode':'US'},'search')
    found=[r['id']['videoId']for r in data.get('items',[])if r.get('id',{}).get('videoId')]
    report['queries'].append({'query':query,'video_ids':found,'status':'ok','additional_results_available':bool(data.get('nextPageToken'))})
    for vid in found:ids.append(vid);hits.setdefault(vid,[]).append(query)
   except Exception as e:report['errors'].append({'query':query,'detail':http.scrub(str(e))});report['status']='partial_discovery'
  ids=list(dict.fromkeys(ids))
  for i in range(0,len(ids),50):
   try:report['videos'].extend(client.videos(ids[i:i+50]).items)
   except Exception as e:report['errors'].append({'batch':i,'detail':http.scrub(str(e))})
 else:
  report['status']='api_key_unavailable';report['errors'].append({'detail':'No existing API secret resolved; no credentials requested or printed.'})
 for v in report['videos']:
  v.update(url='https://www.youtube.com/watch?v='+v['id'],discovered_by=hits.get(v['id'],['web-search seed; not proof of eligibility']),visual_style_verified=False,footage_studied=False,million_view_snapshot=(v.get('views') or 0)>=1000000)
 ranked=sorted(report['videos'],key=lambda v:v.get('views')or 0,reverse=True);selected=[];counts={}
 # Preserve both genuine-3D leads and high-reach adjacent 2D comparators without conflating them.
 for group in [lambda v:'3d' in v['title'].lower() or 'blender' in v['title'].lower(),lambda v:True]:
  for v in ranked:
   if not group(v)or v['id']in selected:continue
   if counts.get(v['channel_id'],0)>=3:continue
   selected.append(v['id']);counts[v['channel_id']]=counts.get(v['channel_id'],0)+1
   if len(selected)>=36:break
  if len(selected)>=36:break
 report['screening_candidates']=selected;report['counts']={'unique_metadata_records':len(report['videos']),'million_view_records':sum(v['million_view_snapshot']for v in report['videos']),'screening_candidates_not_studied':len(selected)}
 save(OUT/'discovery.json',report);print(json.dumps(report['counts']),flush=True);return report

def probe(report):
 CACHE.mkdir(parents=True,exist_ok=True);rows=[];byid={v['id']:v for v in report['videos']}
 # Public, unrestricted playback only. No cookies, private credentials, DRM or access-wall bypass.
 chosen=report.get('screening_candidates',[])[:4]
 for vid in chosen:
  p=CACHE/vid;p.mkdir(exist_ok=True)
  cmd=[sys.executable,'-m','yt_dlp','--no-playlist','--no-progress','--socket-timeout','15','--retries','1','--fragment-retries','1','--max-filesize','120M','--match-filters','duration <= 900','-f','best[height<=480][ext=mp4]/best[height<=480]','-o',str(p/'source.%(ext)s'),'https://www.youtube.com/watch?v='+vid]
  try:
   r=subprocess.run(cmd,capture_output=True,text=True,timeout=105)
   files=[f for f in p.iterdir()if f.suffix in ['.mp4','.webm','.mkv']and f.stat().st_size>10000]
   row={'id':vid,'title':byid[vid]['title'],'attempt_at':stamp(),'download_command_scope':'Public yt-dlp default client, no authentication or access-wall bypass','exit_code':r.returncode,'media_accessible':bool(files),'detail':http.scrub((r.stderr or r.stdout)[-3500:]),'human_visual_review_completed':False}
   if files:
    f=files[0];row.update(bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest())
  except subprocess.TimeoutExpired:row={'id':vid,'media_accessible':False,'detail':'Public acquisition attempt timed out after 105 seconds','human_visual_review_completed':False}
  rows.append(row);save(OUT/'access-probe.json',{'checked_at':stamp(),'results':rows,'completed_study':False,'no_full_third_party_media_committed':True});print(vid,'accessible:',row['media_accessible'],flush=True)
if __name__=='__main__':
 r=discover()
 if '--probe' in sys.argv:probe(r)
