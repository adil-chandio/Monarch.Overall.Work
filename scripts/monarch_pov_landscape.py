"""Reproducible non-exhaustive public metadata study; no private analytics or playback."""
import datetime, json, os, pathlib, sys, urllib.parse, urllib.request, urllib.error, math
KEY=os.environ.get('YOUTUBE_API_KEY','')
if not KEY:sys.exit('Missing YouTube API key')
AFTER='2026-07-08T00:00:00Z'; BEFORE='2026-11-06T00:00:00Z'
QUERIES=[
 'pov you wake up as a celebrity animation','pov life as ronaldo animated','pov celebrity day in the life animated',
 'pov you are a billionaire stickman animation','pov you are rich stickman animation','stickman life of a billionaire',
 'stickman animation day in the life','stickman animation pov funny story','stick figure animation funny story',
 'animated celebrity lifestyle shorts','animated football player story shorts','pov you are a celebrity shorts',
 'pov rich person day in the life','what if you were a billionaire animation','animated famous people shorts',
 'stickman storytelling animation shorts','pov you are famous animation','animated athlete daily routine']

def api(resource, **kw):
 kw['key']=KEY
 try:
  with urllib.request.urlopen('https://www.googleapis.com/youtube/v3/'+resource+'?'+urllib.parse.urlencode(kw),timeout=35) as f:return json.load(f)
 except urllib.error.HTTPError as e:raise RuntimeError(resource+' HTTP '+str(e.code)) from None

def batched(resource, ids, part):
 result=[]
 for i in range(0,len(ids),50):result.extend(api(resource,part=part,id=','.join(ids[i:i+50]),maxResults=50).get('items',[]))
 return result
queries=[];ids=set()
for q in QUERIES:
 for order in ['viewCount','date']:
  try:
   d=api('search',part='snippet',q=q,type='video',regionCode='US',relevanceLanguage='en',order=order,publishedAfter=AFTER,publishedBefore=BEFORE,videoDuration='short',maxResults=25)
   found=[x['id']['videoId'] for x in d.get('items',[])];ids.update(found);queries.append({'query':q,'order':order,'ids':found,'status':'ok'})
  except Exception as e:queries.append({'query':q,'order':order,'status':'error','error':str(e)})
print('search',len(ids),'errors',sum(x['status']!='ok' for x in queries),flush=True)
videos=batched('videos',sorted(ids),'snippet,contentDetails,statistics')
channels=batched('channels',sorted({v['snippet']['channelId'] for v in videos}),'snippet,statistics,contentDetails')
channelmap={c['id']:c for c in channels}
# Sample up to 45 candidates with observable <=100k subscribers. Prioritize strong views and
# query match; include exact-query candidates alongside adjacent ones. Selection is NOT a ranking.
exactids=set(i for q in queries if q['query'] in QUERIES[:7]+QUERIES[11:15]+QUERIES[16:] for i in q.get('ids',[]))
candidates=[]
for v in videos:
 c=channelmap.get(v['snippet']['channelId'],{});s=c.get('statistics',{}); sub=int(s.get('subscriberCount',0) or 0); views=int(v.get('statistics',{}).get('viewCount',0) or 0)
 if not s.get('hiddenSubscriberCount',False) and sub<=100000 and views>=1000:
  title=v['snippet']['title'].lower(); relevant=any(x in title for x in ('pov','stick','animation','billionaire','ronaldo','celebrity','rich','famous','football','life','messi','wealth'))
  if relevant:candidates.append((v['id'] in exactids,views,c['id']))
selected=[]
for exact,views,c in sorted(candidates,reverse=True):
 if c not in selected:selected.append(c)
selected=selected[:45]; uploads=[]; upload_ids=set()
for cid in selected:
 playlist=channelmap[cid].get('contentDetails',{}).get('relatedPlaylists',{}).get('uploads')
 if not playlist:continue
 try:
  r=api('playlistItems',part='contentDetails,snippet',playlistId=playlist,maxResults=35)
  recent=[]
  for item in r.get('items',[]):
   pub=item.get('contentDetails',{}).get('videoPublishedAt','');vid=item.get('contentDetails',{}).get('videoId')
   if vid and pub and pub<BEFORE:recent.append(vid);upload_ids.add(vid)
  uploads.append({'channelId':cid,'ids':recent,'status':'ok','method':'Latest 35 available upload playlist entries retrieved; entries after trusted date omitted; may include private/deleted/missing; no pagination.'})
 except Exception as e:uploads.append({'channelId':cid,'status':'error','error':str(e),'ids':[]})
more=batched('videos',sorted(upload_ids-ids),'snippet,contentDetails,statistics'); videos+=more
# Compact to limit noise and eliminate gratuitous descriptions.
def compact_video(v):
 s=v.get('snippet',{});return {'id':v['id'],'title':s.get('title'),'channelId':s.get('channelId'),'channelTitle':s.get('channelTitle'),'publishedAt':s.get('publishedAt'),'defaultAudioLanguage':s.get('defaultAudioLanguage'),'defaultLanguage':s.get('defaultLanguage'),'duration':v.get('contentDetails',{}).get('duration'),'statistics':v.get('statistics',{})}
def compact_channel(c):
 s=c.get('snippet',{});return {'id':c['id'],'title':s.get('title'),'publishedAt':s.get('publishedAt'),'country':s.get('country'),'customUrl':s.get('customUrl'),'statistics':c.get('statistics',{})}
p={'runner_reported_time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'trusted_cutoff':'2026-11-05T23:59:59Z','publishedAfter':AFTER,'publishedBefore':BEFORE,'method':'18 US-region English-relevance keyword searches, each viewCount and date, short duration filter under 4min, max25 each. Snapshot views may reflect runner clock later than cutoff. US is availability, not audience country. Candidate channels: <=100k publicly shown subscribers and >=1000 views on a keyword-selected video, ranked by inclusion in broad exact queries then views. Latest 35 uploads for up to 45 candidates; nonrepresentative, counts only, no growth/velocity or playback. API totalResults ignored, not a census.', 'queries':queries,'videos':[compact_video(v) for v in videos], 'channels':[compact_channel(c) for c in channels], 'uploads':uploads}
out=pathlib.Path('audit-output/monarch-pov-landscape.json');out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(p,ensure_ascii=False,indent=2));print('videos',len(videos),'channels',len(channels),'selected',len(selected),'upload videos',len(more),flush=True)
