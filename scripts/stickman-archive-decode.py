import concurrent.futures,importlib.util,json,urllib.parse,urllib.request,hashlib,re
from pathlib import Path
spec=importlib.util.spec_from_file_location('quotes',Path(__file__).parent/'stickman-alternate-access.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
B=Path('docs/research/stickman-study/archive-footage');B.mkdir(parents=True,exist_ok=True);C=Path('.cache/stickman-archives');C.mkdir(parents=True,exist_ok=True);mod.BASE=B
items=json.load(open('docs/research/stickman-study/public-archives/items.json'));chosen=[];seen=set()
for r in items:
 if r.get('restricted'):continue
 title=str(r.get('metadata',{}).get('title',''));low=title.lower()
 if any(s in low for s in ['dub','tiktok','no watermark','no-watermark','compilation','all episodes','sneak','squid','otamatone','anniversary','beast games','bulletproof','chalk warfare']):continue
 files=sorted([f for f in r.get('media_files',[])if int(f.get('bytes')or 0)<230_000_000],key=lambda f:(not f['name'].endswith('.mp4'),int(f.get('bytes')or 0)))
 if not files:continue
 f=files[0];idmatch=re.search(r'youtube-([A-Za-z0-9_-]{11})(?:$|/)',r['identifier']);identity=idmatch[1]if idmatch else re.sub(r'[^a-z0-9]','',low)
 if identity in seen:continue
 # Normalized title dedup as well as source-ID dedup.
 tkey=re.sub(r'[^a-z0-9]','',low).replace('alanbecker','');
 if tkey in seen:continue
 seen.update([identity,tkey]);chosen.append((r,f))
chosen=chosen[:32]
results=[]
def process(v):
 r,f=v;identifier=r['identifier'];url='https://archive.org/download/'+urllib.parse.quote(identifier,safe='')+'/'+urllib.parse.quote(f['name'],safe='/');key=hashlib.sha256(identifier.encode()).hexdigest()[:12];p=C/(key+'.'+f['name'].rsplit('.',1)[-1]);row={'archive_identifier':identifier,'archive_title':r.get('metadata',{}).get('title'),'source_url':url,'original_source_metadata':r.get('metadata',{}),'canonical_movie_identity_verified_by_human':False,'actual_visual_review_completed':False}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Monarch animation study / public footage research'}),timeout=80)as resp:p.write_bytes(resp.read(230_000_001))
  if p.stat().st_size>230_000_000:raise ValueError('Research size cap exceeded')
  row.update(mod.quote(p,key,url));row['media_acquired']=True
 except Exception as e:row.update(media_acquired=False,error=str(e))
 return row
with concurrent.futures.ThreadPoolExecutor(4)as pool:
 for row in pool.map(process,chosen):
  results.append(row);(B/'results.json').write_text(json.dumps({'results':results,'study_complete':False,'full_third_party_movies_committed':False},indent=2)+'\n');print(row['archive_identifier'],row['media_acquired'],row.get('decoded_frames'),flush=True)
