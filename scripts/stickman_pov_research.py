"""Public YouTube Data API snapshot; no authenticated viewer data, playback, or fabricated metrics."""
import datetime as dt, json, os, pathlib, sys, urllib.request, urllib.parse, urllib.error
key=os.environ.get('YOUTUBE_API_KEY','')
if not key:sys.exit('YouTube API key unavailable')
now=dt.datetime.now(dt.timezone.utc);since=(now-dt.timedelta(days=365)).isoformat(timespec='seconds').replace('+00:00','Z')
queries=['stickman animation pov day in the life','stickman animation billionaire millionaire life','animated celebrity day in the life ronaldo','pov you are rich animated story','stickman true story animated shorts','stickman animation story life shorts','stickman animation funny pov shorts','animated footballer ronaldo life','stick figure animation celebrity life','stickman animation rich vs poor story','stick figure animation story','pov billionaire lifestyle animation']
def api(endpoint,**params):
 params['key']=key
 try:
  with urllib.request.urlopen('https://www.googleapis.com/youtube/v3/'+endpoint+'?'+urllib.parse.urlencode(params),timeout=45) as f:return json.load(f)
 except urllib.error.HTTPError as e:raise RuntimeError(f'{endpoint} HTTP {e.code}') from None
rows=[];ids=set();direct=['WB9P8WZtUA4','slY6pQiNcLg','j_pS-Y42zgo','ax7WrLEiXmw','H7htBKfK2AU']
for q in queries:
 try:
  res=api('search',part='snippet',q=q,type='video',regionCode='US',relevanceLanguage='en',order='viewCount',publishedAfter=since,videoDuration='short',maxResults=30)
  found=[x['id']['videoId'] for x in res.get('items',[])];ids.update(found);rows.append({'query':q,'ids':found,'status':'ok'})
 except Exception as e:rows.append({'query':q,'status':'error','error':str(e)})
ids.update(direct); videos=[]
for i in range(0,len(ids),50):
 try:videos+=api('videos',part='snippet,contentDetails,statistics',id=','.join(sorted(ids)[i:i+50]),maxResults=50).get('items',[])
 except Exception as e:print('video fetch error',str(e),file=sys.stderr)
chs=sorted(set(v['snippet']['channelId'] for v in videos));channels=[]
for i in range(0,len(chs),50):
 try:channels+=api('channels',part='snippet,statistics',id=','.join(chs[i:i+50]),maxResults=50).get('items',[])
 except Exception as e:print('channel fetch error',str(e),file=sys.stderr)
report={'generated_at':now.isoformat(),'published_after':since,'method':'12 keyword searches, US region availability bias (not audience geography), English relevance hint, order=viewCount, videoDuration=short (under 4 minutes, not necessarily Shorts), within last 365 days, up to 30 per query. Direct IDs outside window included as requested. Snapshot cumulative views, not velocity or watch-time. Search is non-exhaustive and may contain irrelevant matches. No playback or audience-geography inference.','queries':rows,'videos':videos,'channels':channels}
p=pathlib.Path('audit-output/stickman-pov-public.json');p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(report,indent=2,ensure_ascii=False))
print('queries',len(rows),'successful',sum(r['status']=='ok' for r in rows),'unique videos',len(videos),'channels',len(channels))
