"""Read ordinary public creator pages for canonical video links. No private API,
GraphQL session extraction, cookies, proxying, authentication or anti-bot bypass.
"""
import datetime,html,json,re,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/research/zack-original-access';OUT.mkdir(parents=True,exist_ok=True)
URLS=['https://www.facebook.com/zackdfilms/videos/','https://www.facebook.com/zackdfilms/reels/','https://www.facebook.com/zackdfilms/videos/what-is-a-jerboa-/2330611454420496/']
report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'production_hold':True,'route':'Ordinary unauthenticated public creator HTML only','pages':[],'candidates':[]}
seen=set()
def candidate(vid,origin,url=None,title=None,kind='public_html_link'):
 if not re.fullmatch(r'\d{8,25}',str(vid)) or vid in seen:return
 seen.add(vid);report['candidates'].append({'id':vid,'url':url or 'https://www.facebook.com/watch/?v='+str(vid),'discovered_on':origin,'title_hint':title,'kind':kind,'publisher_identity_verified':False})
def walk(obj,origin):
 if isinstance(obj,dict):
  typename=obj.get('__typename','')
  if typename in ['Video','VideoStory','VideoReel'] or obj.get('__isVideo'):
   title=obj.get('title');title=title.get('text') if isinstance(title,dict) else title
   candidate(obj.get('id',''),origin,obj.get('permalink_url') or obj.get('url'),title,'public_video_json')
  for k,v in obj.items():
   if k in ['permalink_url','url'] and isinstance(v,str):
    match=re.search(r'facebook\.com/(?:[^/?#]+/)?(?:videos|reel)/(?:[^/?#]+/)?(\d{8,25})',v)
    if match:candidate(match.group(1),origin,v)
   if isinstance(v,(dict,list)):walk(v,origin)
 elif isinstance(obj,list):
  for x in obj:walk(x,origin)
for url in URLS:
 row={'url':url}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=25) as r:
   body=r.read(12_000_000).decode('utf-8','replace');row['http_status']=r.status
  row['html_bytes']=len(body);before=len(seen)
  normalized=html.unescape(body.replace('\\/','/'))
  for match in re.finditer(r'https?://(?:www\.)?facebook\.com/(?:[^/"\\\s<>]+/)?(?:videos|reel)/(?:[^/"\\\s<>]+/)?(\d{8,25})[^"\\\s<>]*',normalized):candidate(match.group(1),url,match.group(0))
  count=0
  for script in re.findall(r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>',body,re.S):
   try:walk(json.loads(script),url);count+=1
   except (ValueError,RecursionError):continue
  row['json_scripts_parsed']=count;row['new_candidate_count']=len(seen)-before
 except urllib.error.HTTPError as e:row['http_status']=e.code
 except Exception as e:row['error_type']=type(e).__name__
 report['pages'].append(row)
report['candidate_count']=len(report['candidates'])
(OUT/'facebook-public-discovery.json').write_text(json.dumps(report,indent=2)+'\n')
print('Public video candidates:',len(report['candidates']))
