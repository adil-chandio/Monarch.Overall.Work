"""Bounded channel context, not age-matched causal performance estimation."""
import importlib.util,json,os,statistics,datetime,re
from pathlib import Path
spec=importlib.util.spec_from_file_location('audit',Path(__file__).with_name('yt-validation-audit.py'));a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
r=json.loads(Path('production/extinct-life/research/longform-001/baseline-request.json').read_text());assert 1<=len(r['channel_ids'])<=3;assert all(re.fullmatch(r'UC[\w-]{22}',x) for x in r['channel_ids']);assert all(re.fullmatch(r'[\w-]{11}',x) for x in r['target_video_ids']);assert r['uploads_per_channel']==50
out={'status':'running','request':r,'started_at_utc':a.utc(),'source_commit':os.getenv('GITHUB_SHA'),'channels':[],'targets':[],'limits':['Latest 50 uploads only, not entire channel history','4-minute minimum is an analytical proxy, not a platform format label','30–365-day mixed-age median, not an age-matched comparison to older target videos','Counts retrieved now; not historical view counts at analysis cutoff','Runner clock may differ from session date; preserve raw timestamps, do not date-certify views']};dest=Path('.cache/longform-baseline');dest.mkdir(parents=True,exist_ok=True)
try:
 key=next((os.environ[x].strip() for x in a.ALIASES if os.getenv(x,'').strip()),'')
 if not key:raise a.ApiFailure(0,'missingApiSecret')
 api=a.Api(key);response=api.get('channels',part='snippet,statistics,contentDetails',id=','.join(r['channel_ids']));cutoff=datetime.datetime.fromisoformat(r['analysis_cutoff'])
 def seconds(s):
  m=re.fullmatch(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',s or '');return sum(int(n or 0)*v for n,v in zip(m.groups(),[3600,60,1])) if m else 0
 def simplify(v):
  p=v['snippet'];return {'id':v['id'],'title':p['title'],'channel_id':p['channelId'],'published_at':p['publishedAt'],'duration':v['contentDetails']['duration'],'seconds':seconds(v['contentDetails']['duration']),'statistics':v.get('statistics',{}),'observed_at_utc':a.utc()}
 for c in response.get('items',[]):
  playlist=c['contentDetails']['relatedPlaylists']['uploads'];items=api.get('playlistItems',part='contentDetails',playlistId=playlist,maxResults=50);ids=[v['contentDetails']['videoId'] for v in items.get('items',[])];videos=api.get('videos',part='snippet,statistics,contentDetails',id=','.join(ids));rows=[simplify(v) for v in videos.get('items',[])];eligible=[]
  for v in rows:
   age=(cutoff-datetime.datetime.fromisoformat(v['published_at'].replace('Z','+00:00'))).total_seconds()/86400
   if v['seconds']>=240 and 30<=age<=365 and 'viewCount' in v['statistics']:eligible.append(v)
  counts=[int(v['statistics']['viewCount']) for v in eligible];out['channels'].append({'id':c['id'],'title':c['snippet']['title'],'statistics':c.get('statistics',{}),'uploads':rows,'eligible_ids':[v['id'] for v in eligible],'eligible_count':len(eligible),'mixed_age_median_views':statistics.median(counts) if counts else None,'eligible_min_views':min(counts) if counts else None,'eligible_max_views':max(counts) if counts else None})
 out['targets']=[simplify(v) for v in api.get('videos',part='snippet,statistics,contentDetails',id=','.join(r['target_video_ids'])).get('items',[])];out['status']='measured';out['estimated_quota_units']=api.units
except a.ApiFailure as e:out['status']='partial' if out['channels'] else 'blocked';out['error']={'status':e.status,'reason':e.reason}
out['completed_at_utc']=a.utc();(dest/'report.json').write_text(json.dumps(out,indent=2)+'\n');print('status',out['status'],'channels',len(out['channels']))
