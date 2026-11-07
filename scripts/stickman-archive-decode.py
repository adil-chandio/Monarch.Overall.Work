import concurrent.futures,importlib.util,json,urllib.parse,urllib.request,hashlib,re
from pathlib import Path
spec=importlib.util.spec_from_file_location('quotes',Path(__file__).parent/'stickman-alternate-access.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
B=Path('docs/research/stickman-study/archive-footage');B.mkdir(parents=True,exist_ok=True);C=Path('.cache/stickman-archives');C.mkdir(parents=True,exist_ok=True);mod.BASE=B
items=json.load(open('docs/research/stickman-study/public-archives/items.json'));chosen=[];seen=set();families={}
def add(r,f,family):
 base=re.sub(r'\.ia(?=\.mp4$)','',f['name']);identity=(r['identifier'],base)
 if identity in seen or r.get('restricted') or int(f.get('bytes')or 0)>230_000_000:return
 seen.add(identity);chosen.append((r,f,family));families[family]=families.get(family,0)+1
# Quotas prevent an accessible single creator from silently dominating the study.
for r in items:
 ident=r['identifier'];title=str(r.get('metadata',{}).get('title',''));low=title.lower()
 fs=sorted(r.get('media_files',[]),key=lambda f:('.ia.'in f['name'],not f['name'].endswith('.mp4'),int(f.get('bytes')or 0)))
 if ident=='gildedguy':
  for f in fs:
   if any(f['name'].startswith(n+' - ')for n in ['024','028','044','072','078','084','089','102']):add(r,f,'Gildedguy collection — identity pending')
 elif ident=='Newgrounds-598272':
  if fs:add(r,fs[0],'Hyun original-portal archive — identity pending')
 elif ident=='rushed-4-hosted-by-terkoiz':
  if fs:add(r,fs[0],'Terkoiz collection — identity pending')
 elif ident=='four-tanks-and-the-bird':
  for f in fs:
   if f['name'] in ['Four Tanks and the Bird.mp4','4th of July.mp4','Happy Thanksgiving!.mp4']:add(r,f,'Terkoiz collection — identity pending')
 elif ident=='stickman-vs-terraria-bosses':
  for f in fs:
   if any(f['name'].lower().startswith('stickman vs terraria bosses-episode '+str(n)+'-')for n in [1,4,9]):add(r,f,'JzBoy collection — identity pending')
 elif ident=='stickman-vs-games':
  for f in fs:
   if 'baldi' in f['name'] or 'castle crashers' in f['name']:add(r,f,'JzBoy collection — identity pending')
# Select independent Alan Becker movies; avoid dubbing, TikTok watermarks,
# compilations, channel documentaries, duplicate archives and unrelated VFX.
for r in items:
 if families.get('Alan Becker archive — identity pending',0)>=13:break
 title=str(r.get('metadata',{}).get('title',''));low=title.lower();ident=r['identifier']
 if any(x in low for x in ['dub','tiktok','no watermark','compilation','all episodes','sneak','otamatone','anniversary','beast games','bulletproof','chalk warfare']):continue
 if not any(x in low for x in ['animation vs','animator vs','animation shorts','pink army']):continue
 tkey=re.sub(r'[^a-z0-9]','',low).replace('alanbecker','')
 if tkey in seen:continue
 fs=sorted([f for f in r.get('media_files',[])if int(f.get('bytes')or 0)<230_000_000],key=lambda f:('.ia.'in f['name'],not f['name'].endswith('.mp4'),int(f.get('bytes')or 0)))
 if fs:add(r,fs[0],'Alan Becker archive — identity pending');seen.add(tkey)
chosen=chosen[:32]
(B/'selection.json').write_text(json.dumps({'quota_families_provisional':families,'selected':[{'identifier':r['identifier'],'filename':f['name'],'provisional_family':family}for r,f,family in chosen],'not_yet_style_or_reach_verified':True},indent=2)+'\n')
results=[]
def process(v):
 r,f,family=v;identifier=r['identifier'];url='https://archive.org/download/'+urllib.parse.quote(identifier,safe='')+'/'+urllib.parse.quote(f['name'],safe='/');key=hashlib.sha256((identifier+'/'+f['name']).encode()).hexdigest()[:12];p=C/(key+'.'+f['name'].rsplit('.',1)[-1]);row={'archive_identifier':identifier,'archived_filename':f['name'],'provisional_family':family,'archive_title':r.get('metadata',{}).get('title'),'source_url':url,'original_source_metadata':r.get('metadata',{}),'canonical_movie_identity_verified_by_human':False,'actual_visual_review_completed':False}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Monarch animation study / public footage research'}),timeout=80)as resp:p.write_bytes(resp.read(230_000_001))
  if p.stat().st_size>230_000_000:raise ValueError('Research size cap exceeded')
  row.update(mod.quote(p,key,url));row['media_acquired']=True
  spec2=importlib.util.spec_from_file_location('frame_forensics',Path(__file__).parent/'stickman-frame-forensics.py');fm=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(fm);inspect=fm.inspect
  try:row['frame_forensics']=inspect(p,key,B,C)
  except Exception as e:row['frame_forensics_error']=str(e)
 except Exception as e:row.update(media_acquired=False,error=str(e))
 return row
with concurrent.futures.ThreadPoolExecutor(2)as pool:
 for row in pool.map(process,chosen):
  results.append(row);(B/'results.json').write_text(json.dumps({'results':results,'study_complete':False,'full_third_party_movies_committed':False},indent=2)+'\n');print(row['archive_identifier'],row['media_acquired'],row.get('decoded_frames'),flush=True)
