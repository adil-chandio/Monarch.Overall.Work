"""Manual relevance sample of channels and videos discovered in the broad public snapshot."""
import datetime,json,os,pathlib,urllib.request,urllib.parse,urllib.error
K=os.environ['YOUTUBE_API_KEY']; cutoff='2026-11-06T00:00:00Z'
channels=['UCdcJDQafWwwCyDiaYcehm0w','UCqLSt_CKF-D6UQF8Npu94ZA','UCc9J-nAU57iFkurEFcNmamQ','UC7bO2owvsDOJ_14vqL4ys1Q','UCLgzNX8OGekeI53OOBI2R9g','UCXvEHaiROPpsyyc6JShPXdg','UCucoJ5yVEEQlUnGHfiQIPQA','UC_EY0v8qbaEBTzYNNxC9qkQ','UCRFkq3gsy0-wfFUSdvkui6Q','UCz9KHX5VTJYPtUKIDVFR1ng']
comment_ids=['aWHX5Awe_TI','jhC85CjxF4E','5vmyWV9-hXg','8wtQAI_ZZlQ','nrXj8rlwzsI','doyWajAr2lg','HDYkNKZmqLI','GHT3RyE9wGI','LJemKQcxYRE','WB9P8WZtUA4','VE4GMIi39uQ','Tgopx8TcaiM']
def api(r,**params):
 params['key']=K
 try:
  with urllib.request.urlopen('https://www.googleapis.com/youtube/v3/'+r+'?'+urllib.parse.urlencode(params),timeout=30) as f:return json.load(f)
 except urllib.error.HTTPError as e:raise RuntimeError(r+' HTTP '+str(e.code)) from None
cs=api('channels',part='snippet,statistics,contentDetails',id=','.join(channels),maxResults=50).get('items',[]); uploads=[]; ids=set()
for c in cs:
 try:
  res=api('playlistItems',part='snippet,contentDetails',playlistId=c['contentDetails']['relatedPlaylists']['uploads'],maxResults=50)
  items=[{'id':v['contentDetails'].get('videoId'),'publishedAt':v['contentDetails'].get('videoPublishedAt','')} for v in res.get('items',[]) if v['contentDetails'].get('videoPublishedAt','')<cutoff];ids.update(i['id'] for i in items if i['id']);uploads.append({'channelId':c['id'],'status':'ok','items':items})
 except Exception as e:uploads.append({'channelId':c['id'],'status':'error','error':str(e),'items':[]})
ids.update(comment_ids);ids=sorted(ids);videos=[]
for i in range(0,len(ids),50):videos+=api('videos',part='snippet,contentDetails,statistics',id=','.join(ids[i:i+50]),maxResults=50).get('items',[])
comments=[]
for vid in comment_ids:
 try:
  r=api('commentThreads',part='snippet',videoId=vid,maxResults=20,order='relevance',textFormat='plainText')
  items=[{'text':x['snippet']['topLevelComment']['snippet']['textDisplay'],'likes':x['snippet']['topLevelComment']['snippet']['likeCount']} for x in r.get('items',[])];comments.append({'videoId':vid,'status':'ok','items':items})
 except Exception as e:comments.append({'videoId':vid,'status':'unavailable','error':str(e),'items':[]})
p={'runner_reported_time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'trusted_cutoff':cutoff,'method':'Ten manually selected channels, up to 50 most-recent available upload playlist entries, omit publications after trusted cutoff; one page only and missing/private deletions excluded. Public cumulative metrics, no growth, retention, geographies, verified execution, or as-of cutoff claim. Twelve purposefully selected videos; up to 20 relevance-ranked public top-level comments. Some may be disabled. Non-random; descriptive only.','channels':cs,'uploads':uploads,'videos':videos,'comments':comments}
out=pathlib.Path('audit-output/monarch-pov-focus.json');out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(p,ensure_ascii=False,indent=2));print('channels',len(cs),'videos',len(videos),'comments',sum(len(c['items']) for c in comments))
