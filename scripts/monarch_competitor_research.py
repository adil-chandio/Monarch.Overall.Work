"""Small, reproducible YouTube Data API search sample; not a census of YouTube."""
import datetime, json, os, pathlib, urllib.parse, urllib.request, urllib.error, sys
key=os.environ.get('YOUTUBE_API_KEY','')
if not key: sys.exit('YouTube API key unavailable')
queries=['satisfying science experiments shorts','optical illusions explained shorts','oddly satisfying experiments shorts','cool gadgets comparison shorts','trick shots challenge shorts','animal facts explained shorts']
def api(resource,**kwargs):
 kwargs['key']=key; url='https://www.googleapis.com/youtube/v3/'+resource+'?'+urllib.parse.urlencode(kwargs)
 try:
  with urllib.request.urlopen(url,timeout=30) as r: return json.load(r)
 except urllib.error.HTTPError as e:
  raise RuntimeError(f'{resource} HTTP {e.code}') from None
now=datetime.datetime.now(datetime.timezone.utc); since=(now-datetime.timedelta(days=90)).isoformat(timespec='seconds').replace('+00:00','Z')
reports=[]
for query in queries:
 try:
  r=api('search',part='snippet',q=query,type='video',videoDuration='short',order='viewCount',publishedAfter=since,maxResults=30)
  ids=[x['id']['videoId'] for x in r.get('items',[])]; videos=api('videos',part='snippet,contentDetails,statistics',id=','.join(ids),maxResults=50).get('items',[]) if ids else []
  channels=list({v['snippet']['channelId'] for v in videos}); channel_data=api('channels',part='snippet,statistics',id=','.join(channels),maxResults=50).get('items',[]) if channels else []
  reports.append({'query':query,'status':'ok','videos':videos,'channels':channel_data})
 except Exception as e: reports.append({'query':query,'status':'error','error':str(e) if isinstance(e,RuntimeError) else type(e).__name__})
out={'generated_at':now.isoformat(),'published_after':since,'queries':reports,'method':'six keyword searches, 90 days, order=viewCount, videoDuration=short (<4m); not a Shorts classification or representative sample; public cumulative views, not velocity; subscriber counts rounded.'}
p=pathlib.Path('audit-output');p.mkdir(exist_ok=True);(p/'competitors.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print('Search results',[(r['query'],r['status'],len(r.get('videos',[]))) for r in reports])
