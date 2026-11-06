#!/usr/bin/env python3
"""Public caption/metadata research. No login cookies, access bypass or video downloads.
Raw third-party captions stay temporary. Publish hashes, timings, word counts and
small controlled vocabulary tags, NOT full competing scripts.
"""
import datetime,hashlib,html,json,re,subprocess,sys,tempfile,urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from yt_intel import client,http
OUT=Path('docs/research/data/extinct-script-study');OUT.mkdir(parents=True,exist_ok=True)
CASES=[
 ('eons-dna','Can We Get DNA From Fossils?','PBS Eons','https://www.pbs.org/video/can-we-get-dna-from-fossils-zjwrun/'),
 ('eons-whales','When Whales Walked','PBS Eons','https://www.pbs.org/video/when-whales-walked-jjfimk/'),
 ('scishow-resurrection','Resurrection Biology: How to Bring Animals Back From Extinction','SciShow','https://www.youtube.com/watch?v=y-0mT4oQH3o'),
 ('scishow-nematode',"The Most Important Animal You've Never Seen",'SciShow','https://www.youtube.com/watch?v=vBWzrlCBhCM')]
TERMS='dna amber weevil quagga fossil fossils contamination fungus pcr amplification half-life water bone bones horse dinosaur dinosaurs mammoth mammoths cloning cell cells nucleus egg genome neanderthals population habitat whales whale sea land ambulocetus indohyus involucrum ankle artiodactyls hippos food predators million years nematodes scientists arctic permafrost'.split()
CONNECTORS=['but','because','however','yet','so','instead','for example','what if','imagine','maybe','not','sort of']
def scrub(e):return re.sub(r'https?://\S+','[URL]',http.scrub(str(e)))[:800]
def seconds(s):
 s=s.strip().replace(',','.');parts=s.split(':');return sum(float(x)*60**i for i,x in enumerate(reversed(parts)))
def parse(text,ext):
 rows=[]
 if ext in ('ttml','dfxp'):
  root=ET.fromstring(text)
  for p in root.iter():
   if p.tag.split('}')[-1]=='p' and p.get('begin') and p.get('end'):rows.append((seconds(p.get('begin')),seconds(p.get('end')),' '.join(p.itertext())))
 elif ext=='json3':
  for event in json.loads(text).get('events',[]):
   if 'segs' in event:rows.append((event['tStartMs']/1000,(event['tStartMs']+event.get('dDurationMs',0))/1000,''.join(x.get('utf8','') for x in event['segs'])))
 else:
  matches=list(re.finditer(r'(?m)^((?:\d+:)?\d{2}:\d{2}[.,]\d+)\s*-->\s*((?:\d+:)?\d{2}:\d{2}[.,]\d+).*$',text))
  for i,m in enumerate(matches):
   segment=text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)]
   segment=re.sub(r'(?m)^\s*\d+\s*$','',segment).strip();rows.append((seconds(m[1]),seconds(m[2]),segment))
 clean=[]
 for start,end,body in rows:
  body=html.unescape(re.sub(r'<[^>]+>','',body));body=re.sub(r'\s+',' ',body).strip()
  if body and (not clean or body!=clean[-1][2]):clean.append((start,end,body))
 return clean

def captions(case):
 key,title,channel,url=case;row={'key':key,'title':title,'channel':channel,'public_url':url,'status':'unavailable','playback_reviewed':False}
 with tempfile.TemporaryDirectory() as tmp:
  p=subprocess.run([sys.executable,'-m','yt_dlp','--no-playlist','--skip-download','--dump-single-json','--socket-timeout','15','--retries','0','--extractor-retries','0','--no-warnings',url],capture_output=True,text=True,timeout=150)
  if p.returncode:row['diagnostic']=scrub(p.stderr);return row
  info=json.loads(p.stdout);row['publisher_media_id']=info.get('id');row['publisher_duration_seconds']=info.get('duration')
  options=[]
  for kind in ['subtitles','automatic_captions']:
   for lang,formats in info.get(kind,{}).items():
    if lang.startswith('en'):
     for f in formats:
      if f.get('ext') in ['vtt','srt','ttml','dfxp','json3']:options.append((kind,lang,f))
  options.sort(key=lambda x:(x[0]!='subtitles',x[2].get('ext')!='vtt'))
  if not options:row['diagnostic']='No public English timed caption track exposed by the normal extractor';return row
  kind,lang,f=options[0];req=urllib.request.Request(f['url'],headers={'User-Agent':'Mozilla/5.0'})
  raw=urllib.request.urlopen(req,timeout=25).read();data=raw.decode('utf-8-sig');cues=parse(data,f['ext'])
  if not cues:raise ValueError('Caption track parsed to zero cues')
  row.update(status='timed_captions_retrieved',caption_type=kind,language=lang,caption_format=f['ext'],caption_sha256=hashlib.sha256(raw).hexdigest(),cue_count=len(cues),last_cue_end=max(x[1] for x in cues),timing_scope='Caption cue timestamps for this publisher edition; not word onsets, shot boundaries, or verified YouTube-edition timing.')
  row['brief_opening_excerpt']=' '.join(' '.join(c[2] for c in cues[:3]).split()[:13])
  derived=[]
  for i,(start,end,body) in enumerate(cues):
   lower=body.lower();words=re.findall(r"[\w'-]+",lower);derived.append({'cue':i,'start':start,'end':end,'word_count':len(words),'text_sha256':hashlib.sha256(body.encode()).hexdigest(),'question':bool(re.search(r'[?？]',body)),'terms':[w for w in TERMS if re.search(r'\b'+re.escape(w)+r'\b',lower)],'connectors':[w for w in CONNECTORS if re.search(r'\b'+re.escape(w)+r'\b',lower)]})
  row['cues']=derived;row['caption_word_count']=sum(x['word_count'] for x in derived)
 return row

def metadata():
 report={'status':'no_api_key','videos':[],'title_searches':[]}
 if not client.API_KEY:return report
 ids=['y-0mT4oQH3o','vBWzrlCBhCM','nAWpLtG-kNs','SDs41Ke3v4Q','qrfhhZ-Wvmk','td2GgN6lrWE']
 for _,title,channel,_ in CASES[:2]:
  try:
   data=client._api('search',{'part':'snippet','q':title+' '+channel,'type':'video','maxResults':5,'relevanceLanguage':'en'},'search')
   hits=[{'id':x['id']['videoId'],'title':x['snippet']['title'],'channel':x['snippet']['channelTitle']} for x in data.get('items',[]) if x.get('id',{}).get('videoId')];report['title_searches'].append({'query':title,'hits':hits});ids.extend(x['id'] for x in hits)
  except Exception as e:report.setdefault('errors',[]).append(scrub(e))
 try:
  raw=client.videos(list(dict.fromkeys(ids))).items;fields=['id','title','channel','channel_id','published','duration','views','likes','comments'];report['videos']=[{k:v.get(k) for k in fields} for v in raw];report['status']='retrieved'
  channels=list(dict.fromkeys(v['channel_id'] for v in report['videos']));channel_rows=client._api('channels',{'part':'snippet,statistics','id':','.join(channels)},'channels').get('items',[]);report['channels']=[{'id':c['id'],'title':c.get('snippet',{}).get('title'),'publishedAt':c.get('snippet',{}).get('publishedAt'),'statistics':c.get('statistics',{})} for c in channel_rows]
 except Exception as e:report['status']='partial';report.setdefault('errors',[]).append(scrub(e))
 return report

def cached_case(case,previous,refresh=False):
 """Reuse prior attempts; a code-only push must not retry blocked extraction.
 Refresh is opt-in and only applies to previously successful public tracks.
 """
 prior=next((r for r in previous.get('cases',[]) if r['key']==case[0]),None)
 if prior and (prior.get('status')!='timed_captions_retrieved' or not refresh):
  row=dict(prior);row.setdefault('caption_source_checked_at',previous.get('checked_at'))
  row['reused_prior_attempt']=True
  return row
 return None

if __name__=='__main__':
 path=OUT/'retrieval.json';previous=json.loads(path.read_text()) if path.exists() else {}
 report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Purposive public script-study sample, not an exhaustive or causal viral-performance study. No retention analytics or audience-geography access.','raw_captions_published':False,'cases':[]}
 for c in CASES:
  try:
   r=cached_case(c,previous,refresh='--refresh-public-captions' in sys.argv)
   if r is None:r=captions(c);r['caption_source_checked_at']=report['checked_at']
  except Exception as e:r={'key':c[0],'public_url':c[3],'status':'unavailable','diagnostic':scrub(e),'caption_source_checked_at':report['checked_at']}
  report['cases'].append(r);print(c[0],r['status'],flush=True);(OUT/'retrieval.json').write_text(json.dumps(report,indent=2)+'\n')
 report['metadata']=metadata();(OUT/'retrieval.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Timed-caption cases:',sum(c['status']=='timed_captions_retrieved' for c in report['cases']))
