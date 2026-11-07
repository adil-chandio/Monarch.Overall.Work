"""Broaden genuine 3D-source discovery; titles are not visual verification."""
import concurrent.futures,json,urllib.parse,urllib.request
from pathlib import Path
B=Path('docs/research/stickman-study/three-d-public-routes');B.mkdir(parents=True,exist_ok=True)
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Monarch public animation reference research'}),timeout=25)as r:return json.load(r)
queries=['mediatype:movies AND (title:stickman OR title:"stick figure") AND (title:3d OR description:3d)','mediatype:movies AND (title:arckon OR description:arckon OR creator:praven)','mediatype:movies AND title:pacman AND (title:home OR title:save)','mediatype:movies AND title:"stick figure" AND (title:war OR title:battle)','mediatype:movies AND title:fury AND title:order']
def search(q):
 try:return {'query':q,'response':get('https://archive.org/advancedsearch.php?'+urllib.parse.urlencode({'q':q,'output':'json','rows':20,'sort[]':'downloads desc'})).get('response',{})}
 except Exception as e:return {'query':q,'error':str(e)}
s=list(concurrent.futures.ThreadPoolExecutor(4).map(search,queries));(B/'search.json').write_text(json.dumps(s,indent=2)+'\n')
ids=list(dict.fromkeys([v['identifier']for r in s for v in r.get('response',{}).get('docs',[])]+['youtube-'+i for i in ['viv47VJHF-w','YoLqQ8yCXSc','OGEL9n3GWc4','9JVF4egvr7I','1t8_eOuKd0Q','tzt_MzfFmEg','TPLXdDn9Kdg','o5koCe2SR6U','4GxrtDErU6I']]))
def metadata(i):
 try:
  d=get('https://archive.org/metadata/'+urllib.parse.quote(i));m=d.get('metadata',{})
  return {'identifier':i,'exists':bool(m),'restricted':bool(d.get('is_dark')or m.get('access-restricted-item')or m.get('is_dark')),'title':m.get('title'),'creator':m.get('creator'),'description':m.get('description'),'source':m.get('source'),'media_files':[{'name':f['name'],'size':f.get('size'),'format':f.get('format')}for f in d.get('files',[])if f['name'].lower().endswith(('.mp4','.mkv','.webm'))],'3d_classification_verified':False,'actually_watched':False}
 except Exception as e:return {'identifier':i,'error':str(e)}
r=list(concurrent.futures.ThreadPoolExecutor(4).map(metadata,ids));(B/'items.json').write_text(json.dumps(r,indent=2)+'\n');print('3D discovery candidates',len(r),'with media',sum(bool(v.get('media_files'))for v in r))
