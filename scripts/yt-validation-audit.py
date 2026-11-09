#!/usr/bin/env python3
"""Bounded public Data API audit. No downloads, secret exports, or automatic commits."""
import argparse,datetime,json,os,re,time,urllib.request,urllib.parse,urllib.error
from pathlib import Path
ALIASES=('YOUTUBE_API_KEY','YTAP1','YTAPI1','YT_KEY','YT_API_KEY')
class ApiFailure(Exception):
 def __init__(self,status,reason):self.status=status;self.reason=reason;super().__init__(f'API HTTP {status}: {reason}')
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def validate(r):
 if not isinstance(r,dict):raise ValueError('Request must be an object')
 if not isinstance(r.get('queries'),list) or not 1<=len(r['queries'])<=4:raise ValueError('Supply 1–4 queries')
 if any(not isinstance(q,str) or not q.strip() or len(q)>160 for q in r['queries']):raise ValueError('Invalid query')
 if not isinstance(r.get('orders'),list) or not 1<=len(r['orders'])<=3 or any(x not in ('relevance','viewCount','date') for x in r['orders']):raise ValueError('Invalid search orders')
 n=r.get('results_per_query',25)
 if type(n) is not int or not 1<=n<=50:raise ValueError('results_per_query must be 1–50')
 if len(r['queries'])*len(r['orders'])*100+30>1300:raise ValueError('Request exceeds audit quota ceiling')
 return r
class Api:
 def __init__(self,key,opener=None,sleep=time.sleep):self.key=key;self.opener=opener or urllib.request.urlopen;self.sleep=sleep;self.units=0;self.attempts=0
 def get(self,endpoint,**params):
  cost=100 if endpoint=='search' else 1
  for retry in range(3):
   if self.units+cost>1300:raise ApiFailure(0,'localQuotaCeiling')
   self.units+=cost;self.attempts+=1
   url='https://www.googleapis.com/youtube/v3/'+endpoint+'?'+urllib.parse.urlencode({**params,'key':self.key})
   try:
    with self.opener(urllib.request.Request(url,headers={'Accept':'application/json'}),timeout=35) as f:return json.load(f)
   except urllib.error.HTTPError as e:
    reason='httpError'
    try:
     x=json.loads(e.read());reason=x['error']['errors'][0]['reason']
     if not isinstance(reason,str) or not re.fullmatch(r'[a-zA-Z0-9_\-]{1,80}',reason):reason='httpError'
    except Exception:pass
    # Permanent permission/key/quota errors are never retried.
    if e.code in (429,500,502,503,504) and retry<2:self.sleep(2**retry);continue
    raise ApiFailure(e.code,reason) from None
   except (urllib.error.URLError,TimeoutError,OSError):
    if retry<2:self.sleep(2**retry);continue
    raise ApiFailure(0,'networkUnavailable') from None
   except (ValueError,KeyError):raise ApiFailure(0,'invalidJsonResponse') from None

def batches(rows,n=50):
 for i in range(0,len(rows),n):yield rows[i:i+n]
def collect(api,r):
 out={'status':'running','started_at_utc':utc(),'request':r,'searches':[],'videos':[],'channels':[],'limits':['Bounded search sample, not a census of YouTube','No competitor private CTR/retention/search-volume access','No audiovisual or thumbnail-pixel review performed','Duration alone does not establish Shorts format','Lifetime counts do not establish current growth velocity'],'source':'YouTube Data API v3','api_validation_passed':False}
 try:
  api.get('videos',part='id',id='-DF7Ll_2U90');out['api_validation_passed']=True
  ids=[]
  for q in r['queries']:
   for order in r['orders']:
    response=api.get('search',part='snippet',q=q,type='video',order=order,maxResults=r.get('results_per_query',25),relevanceLanguage='en')
    found=[x['id']['videoId'] for x in response.get('items',[]) if x.get('id',{}).get('videoId')]
    out['searches'].append({'query':q,'order':order,'observed_at_utc':utc(),'video_ids':found});ids.extend(found)
  for batch in batches(list(dict.fromkeys(ids))):
   response=api.get('videos',part='snippet,statistics,contentDetails',id=','.join(batch))
   observed=utc()
   for v in response.get('items',[]):
    sn=v.get('snippet',{});out['videos'].append({'id':v['id'],'title':sn.get('title'),'channel_id':sn.get('channelId'),'channel_title':sn.get('channelTitle'),'published_at':sn.get('publishedAt'),'duration':v.get('contentDetails',{}).get('duration'),'statistics':v.get('statistics',{}),'thumbnails':sn.get('thumbnails',{}),'observed_at_utc':observed})
  for batch in batches(list(dict.fromkeys(v['channel_id'] for v in out['videos'] if v['channel_id']))):
   response=api.get('channels',part='snippet,statistics',id=','.join(batch))
   for c in response.get('items',[]):out['channels'].append({'id':c['id'],'title':c.get('snippet',{}).get('title'),'statistics':c.get('statistics',{}),'observed_at_utc':utc()})
  out['status']='measured' if out['videos'] else 'empty_sample'
 except ApiFailure as e:
  out['status']='partial' if out['videos'] or out['searches'] else 'blocked';out['error']={'http_status':e.status,'reason':e.reason}
 out.update(completed_at_utc=utc(),estimated_attempted_quota_units=api.units,request_attempts=api.attempts)
 return out

def main():
 p=argparse.ArgumentParser();p.add_argument('--request',required=True);p.add_argument('--out',required=True);a=p.parse_args();dest=Path(a.out);dest.mkdir(parents=True,exist_ok=True)
 try:r=validate(json.loads(Path(a.request).read_text()))
 except (ValueError,OSError) as e:
  (dest/'report.json').write_text(json.dumps({'status':'invalid_request','detail':str(e)})+'\n');return 2
 key=next((os.environ[n].strip() for n in ALIASES if os.environ.get(n,'').strip()),'')
 result=collect(Api(key),r) if key else {'status':'blocked','error':{'reason':'missingApiSecret'},'api_validation_passed':False,'request':r,'completed_at_utc':utc()}
 result['git_commit']=os.environ.get('GITHUB_SHA');result['git_ref']=os.environ.get('GITHUB_REF');(dest/'report.json').write_text(json.dumps(result,indent=2)+'\n')
 lines=['# YouTube API validation audit','',f"Status: **{result['status']}**",f"API preflight passed: **{result.get('api_validation_passed',False)}**",f"Public videos measured: **{len(result.get('videos',[]))}**",'']
 if result.get('error'):lines+=['Blocker: '+json.dumps(result['error']),'']
 lines+=['Counts are timestamped public API observations, not private analytics or a claim of full-video review.','A blocked/partial/empty result is not a negative verdict on topic demand.']
 text='\n'.join(lines)+'\n';(dest/'SUMMARY.md').write_text(text);print(text)
 if os.environ.get('GITHUB_STEP_SUMMARY'):Path(os.environ['GITHUB_STEP_SUMMARY']).open('a').write(text)
 # A dependency blocker is preserved explicitly; no misleading fallback to stale/web data.
 return 0
if __name__=='__main__':raise SystemExit(main())
