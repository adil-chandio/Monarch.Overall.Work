"""Bounded real-file verification. Small public movies only, not metadata masquerading as viewing."""
import hashlib,importlib.util,json,subprocess,urllib.parse
from pathlib import Path
B=Path('docs/research/stickman-study/quick-footage');B.mkdir(parents=True,exist_ok=True);C=Path('.cache/quick-footage');C.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('quote',Path(__file__).parent/'stickman-alternate-access.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.BASE=B
items=json.load(open('docs/research/stickman-study/three-d-public-routes/items.json'));rows=[]
for r in items:
 if r.get('restricted'):continue
 fs=[f for f in r.get('media_files',[])if int(f.get('size')or 0)<4_000_000 and f['name'].endswith('.mp4')]
 if not fs:continue
 f=fs[0];ident=r['identifier'];key=hashlib.sha256(ident.encode()).hexdigest()[:12];url='https://archive.org/download/'+urllib.parse.quote(ident,safe='')+'/'+urllib.parse.quote(f['name'],safe='/');p=C/(key+'.mp4');row={'identifier':ident,'title':r.get('title'),'url':url,'media_acquired':False,'actual_visual_review_completed':False,'million_views_not_claimed':True}
 try:
  subprocess.run(['curl','--fail','--location','--max-time','35','--speed-time','12','--speed-limit','1000','--output',str(p),url],check=True,capture_output=True,timeout=40)
  row.update(m.quote(p,key,url));row['media_acquired']=True
  spec2=importlib.util.spec_from_file_location('frames',Path(__file__).parent/'stickman-frame-forensics.py');fm=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(fm)
  try:row['frame_forensics']=fm.inspect(p,key,B,C)
  except Exception as e:row['frame_forensics_error']=str(e)
 except Exception as e:row['error']=str(e)
 rows.append(row);(B/'results.json').write_text(json.dumps({'results':rows,'not_a_completed_corpus_study':True},indent=2)+'\n');print(ident,row['media_acquired'],row.get('decoded_frames'),flush=True)
