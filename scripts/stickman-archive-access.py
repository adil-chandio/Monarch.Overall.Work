"""Public archival discovery only: verify source IDs before attaching YouTube statistics.
No login, restricted items, paid media or full-movie republication.
"""
import json,urllib.parse,urllib.request,concurrent.futures
from pathlib import Path
B=Path('docs/research/stickman-study/public-archives');B.mkdir(parents=True,exist_ok=True)
queries=['mediatype:movies AND (creator:S3dV OR title:S3dV OR description:S3dV)','mediatype:movies AND (title:"Stick Empires" OR creator:"Arckon Arts")','mediatype:movies AND (title:"Stick Figure War" OR creator:"SoKrispyMedia")','mediatype:movies AND creator:"Alan Becker"','mediatype:movies AND (title:"Animation vs. Physics" OR title:"Animation vs. Math")','mediatype:movies AND (title:"3D Stickman" OR title:"3D stick figure")']
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Monarch animation research / public archive provenance','Accept':'application/json'})
 with urllib.request.urlopen(req,timeout=30)as r:return json.load(r)
def search(q):
 try:
  d=get('https://archive.org/advancedsearch.php?'+urllib.parse.urlencode({'q':q,'output':'json','rows':25,'fl[]':['identifier','title','creator']},doseq=True));return {'query':q,'status':'ok','response':d.get('response',{})}
 except Exception as e:return {'query':q,'error':str(e)}
rows=list(concurrent.futures.ThreadPoolExecutor(4).map(search,queries));(B/'search.json').write_text(json.dumps(rows,indent=2)+'\n')
ids=list(dict.fromkeys(d['identifier']for r in rows for d in r.get('response',{}).get('docs',[])))[:50]
def metadata(i):
 try:
  d=get('https://archive.org/metadata/'+urllib.parse.quote(i));m=d.get('metadata',{});files=[{'name':f.get('name'),'bytes':f.get('size'),'format':f.get('format')}for f in d.get('files',[])if f.get('name','').lower().endswith(('.mp4','.mkv','.webm'))];return {'identifier':i,'metadata':m,'media_files':files,'restricted':bool(d.get('is_dark')or m.get('access-restricted-item')or m.get('is_dark')),'youtube_view_counts_not_transferred_without_identity_match':True}
 except Exception as e:return {'identifier':i,'error':str(e)}
meta=list(concurrent.futures.ThreadPoolExecutor(4).map(metadata,ids));(B/'items.json').write_text(json.dumps(meta,indent=2)+'\n');print('Public archival metadata records',len(meta),'media files',sum(len(r.get('media_files',[]))for r in meta))
