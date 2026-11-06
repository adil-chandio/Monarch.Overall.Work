#!/usr/bin/env python3
"""Expand bounded API evidence and public publisher-caption coverage. No video downloads.
Only derived caption features are persisted; no third-party complete scripts/descriptions.
"""
import concurrent.futures, csv, datetime, importlib.util, json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from yt_intel import client,http
spec=importlib.util.spec_from_file_location('caption_research',ROOT/'scripts/research-extinct-scripts.py');cap=importlib.util.module_from_spec(spec);spec.loader.exec_module(cap)
OUT=ROOT/'docs/research/data/extinct-expanded-study';OUT.mkdir(parents=True,exist_ok=True)
PUBLISHERS=[
('dodo','We Were Wrong About The Dodo','we-were-wrong-about-the-dodo-w98vvk'),
('sponges','The Second Time Sponges Took Over The World','the-second-time-sponges-took-over-the-world-igqybm'),
('cousins','Our Most Mysterious Extinct Cousins','our-most-mysterious-extinct-cousins-jj1kmf'),
('neandertals','When Neandertals Became Apex Predators','when-neandertals-became-apex-predators-bhaih8'),
('rainforests','When the Rainforests Collapsed','when-the-rainforests-collapsed-tholej'),
('oxygen','That Time Oxygen Almost Killed Everything','that-time-oxygen-almost-killed-everything-cnzweg'),
('pangea-formation','How The Formation of Pangea Changed The World','how-the-formation-of-pangea-changed-the-world-life-and-death-on-pangea-ga6jxx'),
('pangea-herbivores','How Eating Plants Shaped Life on Land','how-eating-plants-shaped-life-on-land-life-and-death-on-pangea-lwgxlg'),
('pangea-reef','The Rise and Fall of an Ancient Reef','the-rise-and-fall-of-an-ancient-reef-twowy2'),
('pangea-dying','That Time Almost Everything Died','that-time-almost-everything-died-life-and-death-on-pangea-zvm6ak'),
('pangea-survivors','Who Survived the Great Dying','who-survived-the-great-dying-and-why-life-and-death-on-pangea-pzs3ev')]
# These IDs were observed in public pages or the existing API catalogue, not guessed.
EXPLICIT=['nAWpLtG-kNs','SDs41Ke3v4Q','qrfhhZ-Wvmk','eWu92oXtxsw','fKizW6NlnoA','G2qpBEmUOYk','SpoqgjauXSg','aGKCeCchZWw','dz63YADXAJ4','5QExdZCvdgE','B5Lmnh_BHOU','lVV5ztC3CtI','VFXOF3GM6Go','cNjiOB99U1A','U1DedLVjeE0','s17TVVfv2IU','tRPu5u_Pizk','XEzEW8VUmMM','W3nIbDgLRV8','aIXEjUl57jE','BUR23SvWuYc','8ReyfUpnJIA']
QUERIES=['prehistoric animals documentary','prehistoric ocean','mass extinction documentary','ancient DNA Greenland','Fossil prehistoric survival','ExtinctZoo prehistoric']
cap.TERMS=sorted(set(cap.TERMS+('extinction oxygen carbon climate volcano volcanic traps reef ocean forests plants pollen spores mammal mammals reptiles dinosaurs asteroid impact acidification anoxia survival predator predators prey size giant teeth skull jaws shell limbs lineage ancestors burrow burrows competition diet hypothesis hypotheses evidence fossils model uncertainty damage minerals extraction crocodile alligator isopods worms bones whale food water land sea tree fungi survivor survivors mutation drought warming').split()))
def duration(s):
 m=re.fullmatch(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',s or '')
 return sum(int(x or 0)*f for x,f in zip(m.groups(),[3600,60,1])) if m else 0

def collect():
 now=datetime.datetime.now(datetime.timezone.utc).isoformat();report={'checked_at':now,'selection':'Purposive API discovery plus explicit public-source leads, not representative or exhaustive.','retention_access':False,'playback_reviewed':False,'queries':[],'publisher_matches':[],'videos':[],'channels':[],'errors':[]}
 ids=list(EXPLICIT)
 for q in QUERIES+[title+' PBS Eons' for _,title,_ in PUBLISHERS]:
  if not client.API_KEY:break
  try:
   d=client._api('search',{'part':'snippet','q':q,'type':'video','maxResults':10,'order':'relevance','relevanceLanguage':'en'},'search')
   hits=[{'id':x['id']['videoId'],'title':x['snippet']['title'],'channel':x['snippet']['channelTitle'],'channel_id':x['snippet']['channelId']} for x in d.get('items',[]) if 'videoId' in x.get('id',{})]
   ids.extend(x['id'] for x in hits);report['queries'].append({'query':q,'hits':hits,'has_more':bool(d.get('nextPageToken'))})
   if q.endswith(' PBS Eons'):report['publisher_matches'].append({'publisher_title':q[:-9],'candidate_hits':hits,'edition_identity_verified':False})
  except Exception as e:report['errors'].append(cap.scrub(e))
 # Retain a broader refresh frame, including less-successful long-form controls.
 with (ROOT/'docs/research/data/extinct-market-video-index.csv').open() as f:
  old=[r for r in csv.DictReader(f) if duration(r['duration_iso'])>=480]
 ids.extend(r['video_id'] for r in old[:100]);ids=list(dict.fromkeys(ids))
 fields=['id','title','channel','channel_id','published','duration','views','likes','comments']
 if client.API_KEY:
  for i in range(0,len(ids),50):
   try:report['videos'].extend({k:v.get(k) for k in fields} for v in client.videos(ids[i:i+50]).items)
   except Exception as e:report['errors'].append(cap.scrub(e))
  channels=list(dict.fromkeys(v['channel_id'] for v in report['videos']))
  for i in range(0,len(channels),50):
   try:
    rows=client._api('channels',{'part':'snippet,statistics','id':','.join(channels[i:i+50])},'channels').get('items',[])
    report['channels'].extend({'id':c['id'],'title':c.get('snippet',{}).get('title'),'statistics':c.get('statistics',{})} for c in rows)
   except Exception as e:report['errors'].append(cap.scrub(e))
 report['api_status']='retrieved' if report['videos'] else 'unavailable'
 (OUT/'api-snapshot.json').write_text(json.dumps(report,indent=2)+'\n')
 previous_path=OUT/'publisher-captions.json';previous=json.loads(previous_path.read_text()) if previous_path.exists() else {};prior={c['key']:c for c in previous.get('cases',[])}
 def fetch_case(entry):
  key,title,slug=entry
  if key in prior:return prior[key]
  url='https://www.pbs.org/video/'+slug+'/'
  try:r=cap.captions((key,title,'PBS Eons',url))
  except Exception as e:r={'key':key,'title':title,'public_url':url,'status':'unavailable','diagnostic':cap.scrub(e)}
  r['caption_source_checked_at']=now
  print(key,r['status'],flush=True);return r
 # Two concurrent normal requests, no repeated blocked extractor attempts.
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:cases=list(pool.map(fetch_case,PUBLISHERS))
 previous_path.write_text(json.dumps({'checked_at':now,'raw_captions_published':False,'cases':cases},indent=2)+'\n')
 print('API videos',len(report['videos']),'timed publishers',sum(c['status']=='timed_captions_retrieved' for c in cases),flush=True)
if __name__=='__main__':collect()
